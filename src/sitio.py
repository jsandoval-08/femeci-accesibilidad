"""Entrada por sitio (Fase 3D): lee el CSV exportado de la hoja de auditoría y corre sus tareas.

Columnas: tarea, entrada, tramite, objetivo_correcto, veredicto_nvda, vidente_lo_encuentra y, opcional,
pagina_axe (vacía = la entrada). Las páginas que puntúa axe se fijan de antemano por tarea, nunca
son las que visiten las estrategias. objetivo_correcto: varios valores se separan con "|"; si la
referencia dice que el sitio no lo tiene, se escribe NO_EXISTE (vacío es un error: no se distingue
de un olvido). veredicto_nvda y vidente_lo_encuentra vacíos = no medido.

Seguro: correr_sitio() rechaza por omisión cualquier URL que no sea local. Un sitio real solo corre
con sitio_real=<su host> y con veredicto_nvda lleno en TODAS las filas: así la regla "auditoría antes
de Atorapp" queda en el código. Comprueba que hay veredictos, no que se hicieron a ciegas ni antes:
eso sigue siendo disciplina del auditor. Limitación declarada: una estrategia puede seguir un enlace
con palabra clave a otro dominio (bloquearlo daría no_encontrado falso con PDF oficiales en otro host).
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

from src.captura import capturar
from src.emulador import Emulador
from src.estrategias import Tarea, cargar_palabras, mejor_estrategia
from src.navegador import ESPERA_EXTRA_MS, PAUSA_S, TIEMPO_LIMITE_MS, NavegadorEnVivo
from src.puntajes import puntajes_de_captura
from src.veredicto import Veredicto, clasificar

COLUMNAS = ("tarea", "entrada", "tramite", "objetivo_correcto", "veredicto_nvda",
            "vidente_lo_encuentra")
ESTADOS = {"completable", "con_dificultad", "no_completable", "no_evaluable"}
VIDENTE = {"si": True, "sí": True, "no": False}
PUNTAJES = ("reglas", "elementos", "reglas_conservador", "elementos_conservador")
HOSTS_LOCALES = {"127.0.0.1", "localhost"}
# Topes por estrategia y por tarea, fijados por escrito el 6-nov ANTES de ver datos (CLAUDE.md).
# Agotar cualquiera sin resolver = No evaluable. No se cambian al ver resultados.
# Pulsaciones: 4 niveles que permite la profundidad × 127 paradas, la portada más larga medida
# (scripts/medicion/paradas.py). Alto a propósito: uno bajo volvería No evaluable un "no existe" real.
TOPE_PULSACIONES = 508
# Navegaciones: acota peticiones al sitio y tiempo de corrida. enlaces_ambiguos B usa 9.
TOPE_NAVEGACIONES = 30


class ErrorAuditoria(ValueError):
    """El CSV de auditoría no es válido. El mensaje dice en qué línea."""


class AuditoriaIncompleta(ValueError):
    """Modo sitio real sin veredicto_nvda en todas las filas: se niega a correr."""


@dataclass(frozen=True)
class FilaAuditoria:
    tarea: str
    entrada: str
    tramite: str | None
    objetivo_correcto: str
    veredicto_nvda: str | None  # None = no medido
    vidente_lo_encuentra: bool | None  # None = no medido
    pagina_axe: str
    linea: int = 0  # línea del CSV, para los mensajes


@dataclass(frozen=True)
class ResultadoFila:
    fila: FilaAuditoria
    veredicto: Veredicto
    puntajes: dict | None  # los 4 puntajes; None = no medido
    error_axe: str | None
    captcha: tuple[str, ...]


@dataclass(frozen=True)
class ReporteSitio:
    sitio: str
    url_base: str
    fecha: str
    palabras_version: int
    tareas: tuple[ResultadoFila, ...]


def leer_auditoria(ruta) -> list[FilaAuditoria]:
    # utf-8-sig: Excel y Google Sheets exportan con o sin BOM; así se leen ambos.
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        faltan = [c for c in COLUMNAS if c not in (lector.fieldnames or ())]
        if faltan:
            raise ErrorAuditoria(f"{ruta}: faltan columnas: {', '.join(faltan)}")
        filas, vistas = [], set()
        for fila in lector:
            filas.append(_fila(fila, lector.line_num, vistas))
    return filas


def _fila(datos: dict, linea: int, vistas: set) -> FilaAuditoria:
    def error(mensaje):
        return ErrorAuditoria(f"línea {linea}: {mensaje}")

    valor = {k: (v or "").strip() for k, v in datos.items() if k}
    tarea = valor["tarea"]
    if tarea not in ("A", "B", "C", "D"):
        raise error(f"tarea desconocida: '{tarea}'")
    if tarea in vistas:
        raise error(f"tarea repetida: {tarea}")
    vistas.add(tarea)
    if not valor["entrada"]:
        raise error("falta la entrada")
    if tarea == "B" and not valor["tramite"]:
        raise error("la tarea B se define con el trámite que la persona busca")
    if not valor["objetivo_correcto"]:
        raise error("objetivo vacío; si el sitio no lo tiene, escribe NO_EXISTE")
    nvda = valor["veredicto_nvda"]
    if nvda and nvda not in ESTADOS:
        raise error(f"veredicto_nvda desconocido: '{nvda}'")
    vidente = valor["vidente_lo_encuentra"].lower()
    if vidente and vidente not in VIDENTE:
        raise error(f"vidente_lo_encuentra debe ser sí, no o vacío: '{vidente}'")
    return FilaAuditoria(tarea, valor["entrada"], valor["tramite"] or None,
                         valor["objetivo_correcto"], nvda or None, VIDENTE.get(vidente),
                         valor.get("pagina_axe") or valor["entrada"], linea)


def _exigir_local(url: str) -> None:
    if urlparse(url).hostname not in HOSTS_LOCALES:
        raise ValueError(f"solo se permiten páginas locales; se rechazó: {url}")


def faltan_veredictos(filas) -> list[FilaAuditoria]:
    """Filas sin veredicto_nvda. "no_evaluable" cuenta como lleno: la auditoría sí se hizo."""
    return [f for f in filas if f.veredicto_nvda is None]


def _exigir_sitio_real(sitio_real: str, url_base: str, urls: list[str], filas, pausa_s: float) -> None:
    """Todo lo que debe cumplirse para tocar un sitio real, antes de tocar la red."""
    if urlparse(url_base).hostname != sitio_real:
        raise ValueError(f"el host de {url_base} no es el autorizado: {sitio_real}")
    for url in urls:
        if urlparse(url).hostname != sitio_real:
            raise ValueError(f"{url} está en otro host; solo se autorizó {sitio_real}")
    if faltan := faltan_veredictos(filas):
        tareas = ", ".join(f"{f.tarea} (línea {f.linea})" for f in faltan)
        raise AuditoriaIncompleta(f"falta veredicto_nvda en: {tareas}. La auditoría va antes de Atorapp.")
    if pausa_s < PAUSA_S:
        raise ValueError(f"en un sitio real la pausa no baja de {PAUSA_S} s: {pausa_s}")


def _puntuar(url: str, carpeta: Path) -> tuple[dict | None, str | None]:
    """Los 4 puntajes de axe de la página. Si axe falla, queda como no medido: no se inventa."""
    try:
        todos = puntajes_de_captura(capturar(url, base=carpeta))
    except Exception as e:  # noqa: BLE001 - se reporta como no medido, no se oculta
        return None, f"{type(e).__name__}: {e}"
    return {k: todos[k] for k in PUNTAJES}, None


def correr_sitio(ruta_csv, url_base: str, carpeta, sitio_real: str | None = None,
                 timeout_ms: int = TIEMPO_LIMITE_MS, espera_ms: int = ESPERA_EXTRA_MS,
                 pausa_s: float = PAUSA_S, tope: int = TOPE_PULSACIONES,
                 tope_nav: int = TOPE_NAVEGACIONES) -> ReporteSitio:
    """Corre todas las tareas del CSV. sitio_real: el host autorizado; sin él, solo páginas locales.
    axe corre primero: capturar() abre su propio Playwright y la API síncrona no admite dos
    abiertos en el mismo hilo."""
    filas = leer_auditoria(ruta_csv)
    urls = {f: (urljoin(url_base, f.entrada), urljoin(url_base, f.pagina_axe)) for f in filas}
    todas = [u for par in urls.values() for u in par]
    if sitio_real is not None:  # todo antes de tocar la red
        _exigir_sitio_real(sitio_real, url_base, todas, filas, pausa_s)
    else:
        for url in [url_base, *todas]:
            _exigir_local(url)
    carpeta = Path(carpeta)
    axe = {}  # una sola medición por página, aunque la compartan varias tareas
    for _, pagina_axe in urls.values():
        if pagina_axe not in axe:
            axe[pagina_axe] = _puntuar(pagina_axe, carpeta / "capturas")

    palabras = cargar_palabras()
    resultados = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        for fila in filas:
            abiertos = []

            def fabrica(entrada):
                nav = NavegadorEnVivo(navegador, timeout_ms=timeout_ms, espera_ms=espera_ms,
                                      pausa_s=pausa_s)
                abiertos.append(nav)
                return Emulador.en_vivo(nav, entrada, tope_pulsaciones=tope,
                                        tope_navegaciones=tope_nav)

            entrada, pagina_axe = urls[fila]
            resultado = mejor_estrategia(fabrica, Tarea(fila.tarea, entrada, fila.tramite), palabras)
            for nav in abiertos:
                nav.cerrar()
            puntajes, error_axe = axe[pagina_axe]
            resultados.append(ResultadoFila(fila, clasificar(resultado, fila.objetivo_correcto),
                                            puntajes, error_axe, resultado.captcha))
        navegador.close()
    nombre = Path(ruta_csv).name.removesuffix(".csv").removesuffix(".auditoria")
    return ReporteSitio(nombre, url_base, datetime.now().astimezone().isoformat(timespec="seconds"),
                        palabras.version, tuple(resultados))
