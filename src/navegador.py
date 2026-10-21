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
No se corre axe aquí: las páginas que puntúa axe están fijas de antemano (CLAUDE.md).
Nunca envía formularios: el emulador no le pide activar campos ni botones de envío.

Uso típico (las pruebas comparten un mismo Chromium):
    with sync_playwright() as p:
        nav = NavegadorEnVivo(p.chromium.launch())
        emu = Emulador.en_vivo(nav, url_entrada)
"""

import json
import time
from pathlib import Path

from playwright.sync_api import Error as ErrorPlaywright
from playwright.sync_api import TimeoutError as TimeoutPlaywright

from src.captura import VIEWPORT, arbol_ax
from src.emulador import Falla, Pagina, Parada

TIEMPO_LIMITE_MS = 30_000  # carga de cada página
ESPERA_EXTRA_MS = 2_000  # tras el evento load, para el JS tardío (igual que la captura)
PAUSA_S = 1.0  # antes de cada petición al sitio (cortesía); no antes de volver


class NavegadorEnVivo:
    def __init__(self, navegador, timeout_ms: int = TIEMPO_LIMITE_MS,
                 espera_ms: int = ESPERA_EXTRA_MS, pausa_s: float = PAUSA_S,
                 carpeta: Path | None = None):
        """navegador: un Browser de Playwright (Chromium). carpeta: si se da, ahí se guarda
        el árbol de cada página cargada (NN_arbol_ax.json), como evidencia reproducible."""
        self.contexto = navegador.new_context(viewport=VIEWPORT, accept_downloads=True)
        self.timeout_ms = timeout_ms
        self.espera_ms = espera_ms
        self.pausa_s = pausa_s
        self.carpeta = Path(carpeta) if carpeta else None
        self._pestanas = []  # pila: una pestaña por nivel (entrada = la primera)
        self.capturas = 0  # árboles capturados (volver no captura)

    def cerrar(self) -> None:
        self.contexto.close()

    # ---------- Acciones que pide el emulador ----------

    def abrir(self, url: str) -> Pagina | Falla:
        """Punto de entrada (nivel 0)."""
        return self._cargar(url, referer=None)

    def navegar(self, parada: Parada) -> Pagina | Falla:
        """Enter en un enlace: abre su URL en una pestaña nueva. Si el árbol no trae url
        (menuitem), se lee el href del elemento en el DOM."""
        url = parada.url or self._href_dom(parada)
        if not url:
            return Falla("falla_tecnica", f"'{parada.nombre}' no tiene URL a dónde navegar")
        return self._cargar(url, referer=self._pestanas[-1].url)

    def volver(self) -> None:
        """Alt+←: cierra la pestaña del nivel actual. No recaptura nada."""
        self._pestanas.pop().close()

    # ---------- Interno ----------

    def _cargar(self, url: str, referer: str | None) -> Pagina | Falla:
        time.sleep(self.pausa_s)
        pestana = self.contexto.new_page()
        try:
            respuesta = pestana.goto(url, wait_until="load", timeout=self.timeout_ms,
                                     referer=referer)
        except TimeoutPlaywright as e:
            pestana.close()
            return Falla("timeout", _primera_linea(e))
        except ErrorPlaywright as e:
            pestana.close()
            return Falla("falla_tecnica", _primera_linea(e))
        if self.espera_ms:
            pestana.wait_for_timeout(self.espera_ms)
        self._pestanas.append(pestana)
        arbol = self._capturar(pestana)
        return Pagina(url_pedida=url, url=pestana.url,
                      estado_http=respuesta.status if respuesta else None,
                      titulo=pestana.title(), arbol=arbol)

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


def _primera_linea(error: Exception) -> str:
    return str(error).strip().splitlines()[0] if str(error).strip() else type(error).__name__
