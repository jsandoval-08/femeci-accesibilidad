"""Fixtures compartidas de la Fase 3B: servidor local, Chromium y emuladores en vivo.

Las páginas de prueba se sirven por http (no file://) desde un servidor levantado aquí en
un puerto libre: es más parecido a un sitio real (historial, redirecciones, códigos HTTP) y
permite simular fallas. SOLO páginas locales: nada de sitios reales.

Rutas especiales del servidor (además de los archivos de tests/paginas):
  /lento/<archivo>     espera LENTO_S segundos y sirve <archivo> (simula timeout)
  /redirige/<archivo>  302 a /<archivo>
"""

import functools
import http.server
import threading
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

PAGINAS = Path(__file__).parent / "paginas"
LENTO_S = 3  # más que el timeout que usan las pruebas de falla (1 s)


class _Manejador(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # sin ruido en la salida de pytest
        pass

    def do_GET(self):
        if self.path.startswith("/lento/"):
            time.sleep(LENTO_S)
            self.path = self.path.removeprefix("/lento")
        elif self.path.startswith("/redirige/"):
            self.send_response(302)
            self.send_header("Location", self.path.removeprefix("/redirige"))
            self.end_headers()
            return
        super().do_GET()


@pytest.fixture(scope="session")
def servidor():
    """URL base (termina en /) del servidor local sobre tests/paginas."""
    manejador = functools.partial(_Manejador, directory=str(PAGINAS))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    srv.daemon_threads = True  # una petición lenta no bloquea el cierre
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/"
    srv.shutdown()
    srv.server_close()


@pytest.fixture(scope="module")
def chromium():
    """Un Chromium por módulo. No de sesión: capturar() abre su propio Playwright y la API
    síncrona no admite dos abiertos a la vez en el mismo hilo."""
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()


@pytest.fixture
def vivo(servidor, chromium):
    """Fábrica de emuladores en vivo sobre el servidor local; cierra todo al terminar.
    vivo("pagina.html", tope=None, **opciones de NavegadorEnVivo)."""
    from src.emulador import Emulador
    from src.navegador import NavegadorEnVivo

    abiertos = []

    def abrir(pagina, tope=None, **opciones):
        opciones = {"timeout_ms": 5_000, "espera_ms": 0, "pausa_s": 0, **opciones}
        nav = NavegadorEnVivo(chromium, **opciones)
        abiertos.append(nav)
        return Emulador.en_vivo(nav, servidor + pagina, tope_pulsaciones=tope)

    yield abrir
    for nav in abiertos:
        nav.cerrar()
