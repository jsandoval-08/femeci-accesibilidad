"""Captura de una página EN VIVO con Playwright (Fase 1A).

Guarda, en capturas/<nombre_seguro>_<hash8>/<AAAAMMDD-HHMMSS>/:
  - pagina.html          HTML ya renderizado (con JS y CSS aplicados)
  - arbol_ax.json        árbol de accesibilidad completo (CDP Accessibility.getFullAXTree)
  - aria_snapshot.txt    aria snapshot de Playwright
  - metadatos.json       URL, URL final, estado HTTP, fecha y hora, versión de Chromium, etc.

Uso: python -m src.captura <url>
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from importlib.metadata import version as version_paquete

from playwright.sync_api import sync_playwright

CARPETA_CAPTURAS = Path("capturas")
VIEWPORT = {"width": 1366, "height": 768}
TIEMPO_LIMITE_MS = 60_000  # tope para cargar la página
ESPERA_EXTRA_MS = 2_000  # tras el evento load, para que termine el JS tardío
MAX_NOMBRE = 80

# Caracteres inválidos en nombres de archivo de Windows, más espacios y control
_INVALIDOS = re.compile(r'[?&=:/\\*"<>|\s\x00-\x1f]+')


def nombre_carpeta(url: str) -> str:
    """Nombre seguro para Windows: legible + hash de la URL completa (evita choques)."""
    partes = urlparse(url)
    if partes.scheme == "file":
        # Solo el nombre del archivo: la ruta local completa no aporta y es larga
        base = Path(unquote(partes.path)).name
    else:
        base = partes.netloc + partes.path + ("?" + partes.query if partes.query else "")
    limpio = _INVALIDOS.sub("_", base).strip("._")[:MAX_NOMBRE].strip("._") or "pagina"
    hash8 = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    return f"{limpio}_{hash8}"


def _guardar_json(ruta: Path, datos) -> None:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def capturar(url: str, base: Path = CARPETA_CAPTURAS) -> Path:
    """Captura `url` y devuelve la carpeta donde quedó todo.

    Estructura: <base>/<nombre_seguro>_<hash8>/<AAAAMMDD-HHMMSS>/. Capturar la misma URL
    otra vez crea una subcarpeta nueva; nunca sobrescribe (falla si coincide el segundo).
    """
    ahora = datetime.now().astimezone()
    carpeta = base / nombre_carpeta(url) / ahora.strftime("%Y%m%d-%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=False)

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport=VIEWPORT)
        pagina = contexto.new_page()

        respuesta = pagina.goto(url, wait_until="load", timeout=TIEMPO_LIMITE_MS)
        pagina.wait_for_timeout(ESPERA_EXTRA_MS)

        # HTML renderizado
        (carpeta / "pagina.html").write_text(pagina.content(), encoding="utf-8")

        # Árbol de accesibilidad completo vía CDP (incluye nodos ignorados; no se filtra aquí)
        cdp = contexto.new_cdp_session(pagina)
        cdp.send("Accessibility.enable")
        arbol = cdp.send("Accessibility.getFullAXTree")
        _guardar_json(carpeta / "arbol_ax.json", arbol)

        # Aria snapshot de Playwright
        snapshot = pagina.locator("body").aria_snapshot()
        (carpeta / "aria_snapshot.txt").write_text(snapshot, encoding="utf-8")

        # Metadatos. En file:// Playwright reporta un 200 sintético (no es HTTP real);
        # solo es null si no hubo respuesta (p. ej. navegación a about:blank).
        metadatos = {
            "url": url,
            "url_final": pagina.url,
            "estado_http": respuesta.status if respuesta else None,
            "fecha_hora": ahora.isoformat(timespec="seconds"),
            "chromium_version": navegador.version,
            "playwright_version": version_paquete("playwright"),
            "viewport": VIEWPORT,
            "num_iframes": len(pagina.frames) - 1,  # el primer frame es la página principal
            "num_nodos_ax": len(arbol["nodes"]),
        }
        _guardar_json(carpeta / "metadatos.json", metadatos)

        navegador.close()

    return carpeta


def main() -> None:
    ap = argparse.ArgumentParser(description="Captura una página con Playwright.")
    ap.add_argument("url", help="URL a capturar (http, https o file)")
    args = ap.parse_args()
    carpeta = capturar(args.url)
    print(f"Captura guardada en: {carpeta}")


if __name__ == "__main__":
    sys.exit(main())
