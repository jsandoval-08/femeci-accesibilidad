"""Navegador en vivo (Fase 3B): ejecuta lo que el emulador decide. No cuenta nada.

El emulador (src/emulador.py) decide qué hace cada tecla y cuenta pulsaciones; este módulo
solo hace lo que necesita red, con Playwright sobre el sitio EN VIVO:
  - abrir el punto de entrada y navegar: cada nivel en una pestaña NUEVA del mismo contexto
    (mismas cookies, con referer). Así la página anterior queda viva e intacta y volver es
    cerrar la pestaña de arriba: se reusa el árbol guardado y los id del DOM siguen sirviendo
    para hacer clic después. Limitación declarada: se navega a la URL del enlace, no se
    ejecuta su onclick (medido el 20-oct: 150 de 164 enlaces de las 5 portadas tienen URL
    navegable y ninguno usa javascript:).
  - recapturar el árbol de accesibilidad (CDP) de cada página nueva.
  - descargar los documentos (PDF) sin abrir visor y medir si tienen capa de texto.
  - hacer clic en la misma página (expandir, pestañas) y ubicar el destino de un "#id".
No se corre axe aquí: las páginas que puntúa axe están fijas de antemano (CLAUDE.md).
Nunca envía formularios: el emulador no le pide activar campos ni botones de envío.

Uso típico (las pruebas comparten un mismo Chromium):
    with sync_playwright() as p:
        nav = NavegadorEnVivo(p.chromium.launch())
        emu = Emulador.en_vivo(nav, url_entrada)
"""

import io
import json
import mimetypes
import time
from pathlib import Path
from urllib.parse import urldefrag

from playwright.sync_api import Error as ErrorPlaywright
from playwright.sync_api import TimeoutError as TimeoutPlaywright
from pypdf import PdfReader

from src.captura import VIEWPORT, arbol_ax
from src.emulador import Documento, Falla, Pagina, Parada

TIEMPO_LIMITE_MS = 30_000  # carga de cada página
ESPERA_EXTRA_MS = 2_000  # tras el evento load, para el JS tardío (igual que la captura)
ESPERA_CLIC_MS = 500  # tras un clic en la misma página, para que el JS actualice el DOM
PAUSA_S = 1.0  # antes de cada petición al sitio (cortesía); no antes de volver


class NavegadorEnVivo:
    def __init__(self, navegador, timeout_ms: int = TIEMPO_LIMITE_MS,
                 espera_ms: int = ESPERA_EXTRA_MS, espera_clic_ms: int = ESPERA_CLIC_MS,
                 pausa_s: float = PAUSA_S, carpeta: Path | None = None):
        """navegador: un Browser de Playwright (Chromium). carpeta: si se da, ahí se guarda
        el árbol de cada página cargada (NN_arbol_ax.json), como evidencia reproducible."""
        self.contexto = navegador.new_context(viewport=VIEWPORT, accept_downloads=True)
        self.timeout_ms = timeout_ms
        self.espera_ms = espera_ms
        self.espera_clic_ms = espera_clic_ms
        self.pausa_s = pausa_s
        self.carpeta = Path(carpeta) if carpeta else None
        self._pestanas = []  # pila: una pestaña por nivel (entrada = la primera)
        self.capturas = 0  # árboles capturados (volver no captura)

    def cerrar(self) -> None:
        self.contexto.close()

    # ---------- Acciones que pide el emulador ----------

    def abrir(self, url: str) -> Pagina | Documento | Falla:
        """Punto de entrada (nivel 0)."""
        return self._cargar(url, referer=None)

    def navegar(self, parada: Parada) -> Pagina | Documento | Falla:
        """Enter en un enlace: abre su URL en una pestaña nueva. Si el árbol no trae url
        (menuitem), se lee el href del elemento en el DOM."""
        url = parada.url or self._href_dom(parada)
        if not url:  # menuitem sin href: se activa como cualquier control de la página
            return self.activar_en_sitio(parada)
        return self._cargar(url, referer=self._pestanas[-1].url)

    def volver(self) -> None:
        """Alt+←: cierra la pestaña del nivel actual. No recaptura nada."""
        self._pestanas.pop().close()

    def activar_en_sitio(self, parada: Parada) -> Pagina | Falla:
        """Enter que no cambia de página (expandir, colapsar, seleccionar pestaña, href="#"):
        clic en el elemento del DOM (la acción por omisión, que es lo que hace NVDA en modo
        exploración) y recaptura en la MISMA pestaña. Si el clic termina navegando a otro
        documento, se reporta como falla técnica: no está modelado en 3B (al volver, la página
        anterior ya no estaría viva). Medido el 20-oct: 7 de 164 enlaces son href="#"."""
        pestana = self._pestanas[-1]
        antes = urldefrag(pestana.url)[0]
        try:
            self._en_dom(parada, "function () { this.click(); }")
            pestana.wait_for_timeout(self.espera_clic_ms)
            if urldefrag(pestana.url)[0] != antes:
                return Falla("falla_tecnica",
                             f"el clic en '{parada.nombre}' navegó a {pestana.url} (no modelado)")
            arbol = self._capturar(pestana)
        except ErrorPlaywright as e:
            return Falla("falla_tecnica", _primera_linea(e))
        return Pagina(url_pedida=pestana.url, url=pestana.url, estado_http=None,
                      titulo=pestana.title(), arbol=arbol, nueva_pestana=False)

    def ubicar_fragmento(self, fragmento: str, paradas: list[Parada]) -> int | None:
        """Enter en "#id" de la misma página: índice de la primera parada que está dentro
        del elemento destino o después de él, en orden del documento. None si la página no
        tiene ese id (p. ej. rutas de SPA con "#/..."): entonces el emulador hace clic."""
        pestana = self._pestanas[-1]
        cdp = self.contexto.new_cdp_session(pestana)
        try:
            destino = cdp.send("Runtime.evaluate", {"expression": (
                f"document.getElementById({json.dumps(fragmento)}) || "
                f"document.getElementsByName({json.dumps(fragmento)})[0] || null")})["result"]
            if "objectId" not in destino:
                return None
            for p in paradas:
                if p.id_dom is None:
                    continue
                nodo = cdp.send("DOM.resolveNode", {"backendNodeId": p.id_dom})["object"]
                r = cdp.send("Runtime.callFunctionOn", {
                    "objectId": nodo["objectId"], "returnByValue": True,
                    "arguments": [{"objectId": destino["objectId"]}],
                    "functionDeclaration": (
                        "function (d) { return d === this || d.contains(this) || "
                        "!!(d.compareDocumentPosition(this) & Node.DOCUMENT_POSITION_FOLLOWING); }"),
                })
                if r["result"].get("value"):
                    return p.indice
            return None
        finally:
            cdp.detach()

    # ---------- Interno ----------

    def _cargar(self, url: str, referer: str | None) -> Pagina | Documento | Falla:
        time.sleep(self.pausa_s)
        pestana = self.contexto.new_page()
        descargas = []
        pestana.on("download", lambda d: descargas.append(d))
        try:
            respuesta = pestana.goto(url, wait_until="load", timeout=self.timeout_ms,
                                     referer=referer)
        except TimeoutPlaywright as e:
            pestana.close()
            return Falla("timeout", _primera_linea(e))
        except ErrorPlaywright as e:
            # Un PDF (o cualquier archivo que el navegador descarga) no abre visor: Chromium
            # sin interfaz lo descarga y goto falla con "Download is starting" (comprobado
            # 20-oct). Los bytes llegan por la misma sesión (mismas cookies).
            if descargas or "Download is starting" in str(e):
                try:
                    descarga = descargas[0] if descargas else pestana.wait_for_event(
                        "download", timeout=self.timeout_ms)
                    return self._documento(descarga)
                except ErrorPlaywright as e2:
                    return Falla("falla_tecnica", _primera_linea(e2))
                finally:
                    pestana.close()
            pestana.close()
            return Falla("falla_tecnica", _primera_linea(e))
        if self.espera_ms:
            pestana.wait_for_timeout(self.espera_ms)
        self._pestanas.append(pestana)
        arbol = self._capturar(pestana)
        return Pagina(url_pedida=url, url=pestana.url,
                      estado_http=respuesta.status if respuesta else None,
                      titulo=pestana.title(), arbol=arbol)

    def _documento(self, descarga) -> Documento:
        datos = Path(descarga.path()).read_bytes()  # espera a que termine la descarga
        nombre = descarga.suggested_filename
        if self.carpeta:  # evidencia: el archivo tal como llegó
            self.carpeta.mkdir(parents=True, exist_ok=True)
            (self.carpeta / f"{self.capturas:02d}_{nombre}").write_bytes(datos)
        return leer_documento(descarga.url, nombre, datos)

    def _capturar(self, pestana) -> dict:
        arbol = arbol_ax(pestana)
        if self.carpeta:
            self.carpeta.mkdir(parents=True, exist_ok=True)
            ruta = self.carpeta / f"{self.capturas:02d}_arbol_ax.json"
            ruta.write_text(json.dumps(arbol, ensure_ascii=False), encoding="utf-8")
        self.capturas += 1
        return arbol

    def _en_dom(self, parada: Parada, funcion: str):
        """Ejecuta `funcion` (JS, con this = el elemento) sobre el nodo del DOM de la parada,
        en la pestaña actual, y devuelve su resultado."""
        cdp = self.contexto.new_cdp_session(self._pestanas[-1])
        try:
            objeto = cdp.send("DOM.resolveNode", {"backendNodeId": parada.id_dom})["object"]
            r = cdp.send("Runtime.callFunctionOn", {
                "objectId": objeto["objectId"], "functionDeclaration": funcion,
                "returnByValue": True})
            return r["result"].get("value")
        finally:
            cdp.detach()

    def _href_dom(self, parada: Parada) -> str | None:
        return self._en_dom(parada, "function () { return this.href || null; }")


def leer_documento(url: str, nombre: str, datos: bytes) -> Documento:
    """Hechos medidos de un archivo descargado (tarea C). Es PDF si los bytes empiezan con
    %PDF- (no se confía en la extensión). Capa de texto = pypdf extrae al menos un carácter no
    blanco; sin capa = escaneado (CLAUDE.md). El veredicto completable / cierre roto es de 3D.
    tipo_contenido se deduce del nombre del archivo (la descarga no trae la cabecera)."""
    tipo = mimetypes.guess_type(nombre)[0] or "desconocido"
    if not datos.startswith(b"%PDF-"):
        return Documento(url, tipo, es_pdf=False, capa_texto=None, paginas=None,
                         caracteres=None)
    try:
        lector = PdfReader(io.BytesIO(datos))
        if lector.is_encrypted:
            lector.decrypt("")  # muchos PDF públicos están "cifrados" con contraseña vacía
        texto = "".join(pagina.extract_text() or "" for pagina in lector.pages)
    except Exception as e:  # noqa: BLE001 - se registra como no medido, no se oculta
        return Documento(url, tipo, es_pdf=True, capa_texto=None, paginas=None,
                         caracteres=None, error=f"{type(e).__name__}: {e}")
    caracteres = len("".join(texto.split()))
    return Documento(url, tipo, es_pdf=True, capa_texto=caracteres > 0,
                     paginas=len(lector.pages), caracteres=caracteres)


def _primera_linea(error: Exception) -> str:
    return str(error).strip().splitlines()[0] if str(error).strip() else type(error).__name__
