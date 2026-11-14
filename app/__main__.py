"""Abre la app del modo exploración: python -m app [--navegador]

Levanta el servidor en 127.0.0.1 (puerto libre, nunca expuesto a la red) y lo muestra en una ventana
propia con pywebview (WebView2, ya incluido en Windows 11). Si pywebview no está o no arranca, abre el
navegador por defecto. Cerrar la ventana (o esta consola) cierra la app.
"""

import argparse
import socket
import sys
import threading
import time
import webbrowser

import uvicorn

from app.seguridad import cargar_config
from app.servidor import crear_app


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Atorapp, modo exploración (estimación experimental).")
    ap.add_argument("--navegador", action="store_true", help="abrir en el navegador, sin ventana propia")
    args = ap.parse_args(argv)

    config = cargar_config()
    servidor = uvicorn.Server(uvicorn.Config(crear_app(config), host="127.0.0.1", port=_puerto_libre(),
                                             log_level="warning"))
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    while not servidor.started:
        if not hilo.is_alive():
            print("No se pudo iniciar el servidor local.", file=sys.stderr)
            return 1
        time.sleep(0.05)
    url = f"http://127.0.0.1:{servidor.config.port}/"
    print(f"Atorapp (modo exploración) en {url}")
    print(f"Lo que corra se guarda en {config.carpeta}")
    if config.hosts_bloqueados:
        print("Hosts bloqueados: " + ", ".join(config.hosts_bloqueados))

    if not args.navegador:
        try:
            import webview
            webview.create_window("Atorapp", url, width=1360, height=900, min_size=(900, 640),
                                  background_color="#FAF7F2")
            webview.start()  # bloquea hasta que se cierra la ventana
            servidor.should_exit = True
            hilo.join(5)
            return 0
        except Exception as e:  # noqa: BLE001 - sin ventana propia, se usa el navegador
            print(f"No se pudo abrir la ventana propia ({type(e).__name__}: {e}); uso el navegador.")
    webbrowser.open(url)
    print("Cierra esta ventana para salir.")
    try:
        while hilo.is_alive():
            hilo.join(0.5)
    except KeyboardInterrupt:
        servidor.should_exit = True
    return 0


if __name__ == "__main__":
    sys.exit(main())
