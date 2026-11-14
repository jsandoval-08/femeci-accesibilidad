"""Motor del modo exploración (Fase 3F): corre las estrategias de src/ sobre cualquier URL y avisa de
cada paso conforme sale. NO cambia ninguna decisión: reúsa mejor_estrategia() y clasificar() tal cual.

Cómo se ve cada paso sin tocar el emulador: Emulador._anotar() hace `self.trayectoria.append(paso)` y
correr() solo lee `tuple(emu.trayectoria)`. La fábrica de aquí reemplaza esa lista por una
ListaObservada cuyo append avisa. Las estrategias no se enteran.

Sin objetivo correcto (no hay auditoría): el veredicto se pide a clasificar() con el hallazgo que la
PERSONA confirma como objetivo, o con NO_EXISTE si nadie llegó o si dice que nada de lo encontrado era
lo que buscaba. Así las reglas son exactamente las del estudio. Es una estimación experimental, no
verificada con NVDA.
"""

import json
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from app.seguridad import HostBloqueado, NavegadorConBloqueo, host_bloqueado, validar_entrada
from src.captura import TIEMPO_LIMITE_MS as TIEMPO_CARGA_MS  # el mismo tope de 60 s que la captura de axe
from src.emulador import Emulador, Falla, NoEvaluable, Paso
from src.estrategias import (ESTRATEGIAS, ETIQUETAS, SOLO_TAREA_D, Intento, ResultadoTarea, Tarea,
                             cargar_palabras, mejor_estrategia)
from src.navegador import ESPERA_EXTRA_MS, PAUSA_S, TIEMPO_LIMITE_MS, NavegadorEnVivo
from src.reporte import _paso
from src.sitio import HOSTS_LOCALES, TOPE_NAVEGACIONES, TOPE_PULSACIONES, _puntuar
from src.veredicto import NO_EXISTE, _describir, clasificar


class Detenida(Exception):
    """La persona pulsó Detener. No es SesionTerminada: correr() no la atrapa y sube hasta aquí."""


class ListaObservada(list):
    """La trayectoria del emulador, con aviso en cada append. Solo observa: guarda lo mismo."""

    def __init__(self, previos, al_agregar):
        super().__init__(previos)
        self._al_agregar = al_agregar

    def append(self, paso):
        super().append(paso)
        self._al_agregar(paso)


def estrategias_de(letra: str) -> list[str]:
    """Las estrategias en el orden en que mejor_estrategia() las corre (y llama a la fábrica)."""
    return [c for c in ESTRATEGIAS if c not in SOLO_TAREA_D or letra == "D"]


@dataclass(frozen=True)
class Exploracion:
    url: str
    tarea: Tarea
    fecha: str
    palabras_version: int
    pausa_s: float
    resultado: ResultadoTarea
    puntajes: dict | None  # los 4 puntajes; None = no medido
    error_axe: str | None
    bloqueadas: tuple[str, ...]  # peticiones abortadas por la barrera 2
    duracion_s: float | None = None  # de principio a fin, axe incluido; None = no medida
    duraciones_s: tuple[float, ...] = ()  # una por estrategia, en el orden de resultado.intentos
    # Si la carga de prueba falló: {"tipo": "timeout" | "falla_tecnica", "motivo": texto para la
    # persona, "detalle": el error del navegador (solo para exploracion.json)}. None = cargó.
    no_cargo: dict | None = None


def motivo_no_cargo(tipo: str, timeout_ms: int) -> str:
    """El texto que ve la persona cuando la página de entrada no abrió."""
    if tipo == "timeout":
        return f"No cargó en el navegador de Atorapp en {round(timeout_ms / 1000)} s"
    return "No cargó en el navegador de Atorapp (falla técnica al abrir la página)"


def _sin_cargar(tarea: Tarea, url: str, no_cargo: dict) -> ResultadoTarea:
    """El resultado cuando la entrada no abre: ninguna estrategia corrió. Es un No evaluable con 0
    pulsaciones, como el que arma el emulador cuando falla su entrada (clasificar() lo trata igual)."""
    tipo = no_cargo["tipo"]
    paso = Paso("entrada", f"no evaluable: {tipo}", None, False, 0, url=url, no_evaluable=tipo)
    ne = NoEvaluable(tipo, no_cargo["detalle"], 0)
    intento = Intento("entrada", False, 0, (paso,), no_cargo["motivo"], ne, None, ())
    return ResultadoTarea(tarea, "entrada", None, None, 0, no_cargo["motivo"], ne, (), (intento,))


def explorar(url: str, letra: str, tramite: str | None, carpeta, hosts, al_evento=None,
             detener: threading.Event | None = None, pausa_s: float = PAUSA_S,
             timeout_ms: int = TIEMPO_LIMITE_MS, espera_ms: int = ESPERA_EXTRA_MS,
             tope: int = TOPE_PULSACIONES, tope_nav: int = TOPE_NAVEGACIONES,
             timeout_carga_ms: int = TIEMPO_CARGA_MS) -> Exploracion:
    """Antes de las estrategias hace UNA carga de prueba de la URL de entrada (timeout_carga_ms, 60 s).
    Si no abre, termina en No evaluable sin correr estrategias ni axe. Si abre, todo sigue igual.
    Corre todas las estrategias de la tarea sobre `url` y luego axe sobre la misma página.
    al_evento(tipo, datos): "estrategia", "paso", "fase". Lanza Detenida, HostBloqueado o ValueError."""
    t0 = time.monotonic()
    url = validar_entrada(url, hosts)  # barrera 1: antes de tocar la red
    tarea = Tarea(letra, url, (tramite or "").strip() or None)  # B sin trámite: ValueError
    if pausa_s < PAUSA_S and urlparse(url).hostname not in HOSTS_LOCALES:
        raise ValueError(f"fuera de 127.0.0.1 la pausa no baja de {PAUSA_S} s: {pausa_s}")
    emitir = al_evento or (lambda tipo, datos: None)
    carpeta = Path(carpeta)
    palabras = cargar_palabras()
    claves = estrategias_de(letra)
    llamadas = []  # una por estrategia: así se sabe cuál corre
    inicios = []  # reloj al arrancar cada estrategia; la duración de una termina donde empieza la siguiente

    def detenida():
        if detener is not None and detener.is_set():
            raise Detenida()

    def revisar(vista: str | None):  # barrera 3: una redirección que termina en un host bloqueado
        if vista and (h := host_bloqueado(vista, hosts)):
            raise HostBloqueado(vista, h)

    abiertos = []
    no_cargo = None
    with sync_playwright() as p:
        navegador = NavegadorConBloqueo(p.chromium.launch(), hosts)  # barrera 2
        try:
            # Carga de prueba: pasa por la barrera 2 (route del contexto) y la barrera 3 (redirección).
            prueba = NavegadorEnVivo(navegador, timeout_ms=timeout_carga_ms, espera_ms=0, pausa_s=pausa_s)
            abiertos.append(prueba)
            detenida()
            abierta = prueba.abrir(url)
            if isinstance(abierta, Falla):
                tipo = "timeout" if abierta.motivo == "timeout" else "falla_tecnica"
                no_cargo = {"tipo": tipo, "motivo": motivo_no_cargo(tipo, timeout_carga_ms),
                            "detalle": abierta.detalle}
            else:
                revisar(getattr(abierta, "url", None))
            detenida()

            def fabrica(entrada):
                clave = claves[len(llamadas)]
                llamadas.append(clave)
                inicios.append(time.monotonic())
                nombre = ETIQUETAS.get(clave, clave)
                detenida()
                emitir("estrategia", {"indice": len(llamadas), "total": len(claves), "estrategia": nombre})
                nav = NavegadorEnVivo(navegador, timeout_ms=timeout_ms, espera_ms=espera_ms, pausa_s=pausa_s)
                abiertos.append(nav)
                emu = Emulador.en_vivo(nav, entrada, tope_pulsaciones=tope, tope_navegaciones=tope_nav)
                revisar(emu.url)

                def al_agregar(paso):
                    revisar(paso.url)
                    if paso.documento:
                        revisar(paso.documento.url)
                    emitir("paso", {"estrategia": nombre, **_paso(paso)})
                    detenida()

                previos = list(emu.trayectoria)  # p. ej. la falla de la entrada
                emu.trayectoria = ListaObservada(previos, al_agregar)
                for paso in previos:
                    emitir("paso", {"estrategia": nombre, **_paso(paso)})
                return emu

            if no_cargo:
                resultado = _sin_cargar(tarea, url, no_cargo)
            else:
                resultado = mejor_estrategia(fabrica, tarea, palabras)
            fin_estrategias = time.monotonic()
        finally:
            for nav in abiertos:
                try:
                    nav.cerrar()
                except Exception:  # noqa: BLE001 - cerrar lo que se pueda; el error real ya subió
                    pass
            navegador.close()
    detenida()
    if no_cargo:  # sin estrategias ni axe: el error del navegador queda solo en no_cargo["detalle"]
        return Exploracion(url, tarea, datetime.now().astimezone().isoformat(timespec="seconds"),
                           palabras.version, pausa_s, resultado, None, "la página no cargó",
                           tuple(navegador.bloqueadas), round(time.monotonic() - t0, 1), (), no_cargo)
    emitir("fase", {"fase": "axe"})
    puntajes, error_axe = _puntuar(url, carpeta / "capturas")  # abre su propio Playwright
    if final := _url_final_bloqueada(carpeta / "capturas", hosts):  # barrera 4
        shutil.rmtree(carpeta / "capturas", ignore_errors=True)
        puntajes, error_axe = None, f"la captura de axe terminó en un host bloqueado ({final}); no se reporta"
    cortes = inicios + [fin_estrategias]
    duraciones = tuple(round(b - a, 1) for a, b in zip(cortes, cortes[1:]))
    return Exploracion(url, tarea, datetime.now().astimezone().isoformat(timespec="seconds"),
                       palabras.version, pausa_s, resultado, puntajes, error_axe,
                       tuple(navegador.bloqueadas), round(time.monotonic() - t0, 1), duraciones)


def _url_final_bloqueada(capturas: Path, hosts) -> str | None:
    for meta in capturas.glob("*/*/metadatos.json"):
        final = json.loads(meta.read_text(encoding="utf-8")).get("url_final") or ""
        if host_bloqueado(final, hosts):
            return final
    return None


# ---------- Estimación: clasificar() con el objetivo que confirma la persona ----------

def objetivo_de(letra: str, hallazgo: dict) -> str:
    """El hallazgo confirmado escrito como objetivo_correcto, en el formato de las auditorías
    ("|" separa valores). Si no queda nada que comparar (p. ej. todos los campos sin nombre), es
    NO_EXISTE: un objetivo vacío coincidiría con cualquier cosa."""
    def limpio(texto):
        return " ".join(str(texto or "").replace("|", " ").split())

    if letra == "A":
        partes = [limpio(hallazgo.get("contacto")) or limpio(hallazgo.get("url"))]
    elif letra == "C":
        partes = [limpio(hallazgo["documento"].url)]
    else:
        partes = [limpio(t) for t in hallazgo["requisitos" if letra == "B" else "campos"]]
    partes = [p for p in partes if p]
    return "|".join(partes) if partes else NO_EXISTE


def hallazgos(resultado: ResultadoTarea) -> list[dict]:
    """Lo distinto que encontraron las estrategias que creen llegar, de menor a mayor fricción (en
    empate, en el orden declarado). Son las opciones que la persona puede confirmar."""
    vistos, opciones = set(), []
    for i in sorted((i for i in resultado.intentos if i.llego), key=lambda i: i.pulsaciones):
        encontro = _describir(i.hallazgo)
        if encontro in vistos:
            continue
        vistos.add(encontro)
        opciones.append({"estrategia": i.estrategia, "pulsaciones": i.pulsaciones, "encontro": encontro,
                         "objetivo": objetivo_de(resultado.tarea.letra, i.hallazgo)})
    return opciones


def estimar(resultado: ResultadoTarea, objetivo: str, motivo_carga: str | None = None) -> dict:
    """El veredicto de clasificar() como datos para guardar y mostrar. Con motivo_carga (la entrada
    no abrió) el estado sigue siendo el de clasificar(); solo se dice el motivo real, sin estrategia."""
    v = clasificar(resultado, objetivo)
    intento = v.intento
    return {
        "estado": v.estado, "tipo_falla": v.tipo_falla,
        "estrategia": None if motivo_carga else v.estrategia,
        "friccion": v.friccion, "consumidas": v.consumidas, "motivo": motivo_carga or v.motivo,
        "sensibilidad": {str(u): e for u, e in v.sensibilidad.items()},
        "encontro": _describir(intento.hallazgo) if intento and intento.hallazgo else None,
        "pasos": [_paso(p) for p in intento.trayectoria] if intento else [],
        "falsas_llegadas": [{"estrategia": x.estrategia, "pulsaciones": x.pulsaciones,
                             "encontro": x.encontro} for x in v.falsas_llegadas],
    }


def estimaciones(resultado: ResultadoTarea, motivo_carga: str | None = None) -> dict:
    """Todas las respuestas posibles, calculadas de una vez: "ninguna" (nadie llegó, o nada de lo
    encontrado era lo buscado) y una por opción ("0", "1", ...). Así confirmar solo elige; también
    desde el historial."""
    todas = {"ninguna": estimar(resultado, NO_EXISTE, motivo_carga)}
    for n, opcion in enumerate(hallazgos(resultado)):
        todas[str(n)] = estimar(resultado, opcion["objetivo"], motivo_carga)
    return todas
