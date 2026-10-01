"""Genera los dos PDFs de prueba de la tarea C (con Playwright, sin dependencias extra).

  docs/plan_municipal.pdf            texto real (con capa de texto)
  docs/plan_municipal_escaneado.pdf  solo una imagen del mismo texto (sin capa de texto)

El escaneado se logra fotografiando el documento y metiendo la imagen en un PDF:
queda una página-imagen, igual que un papel escaneado sin OCR.

Uso (desde la raíz del proyecto): python tests/paginas/generar_pdfs.py
"""

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

DOCS = Path(__file__).parent / "docs"

DOCUMENTO = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Plan Municipal de Desarrollo</title>
<style>body{font-family:Arial,sans-serif;font-size:20px;margin:40px;width:680px}</style>
</head><body>
<h1>Plan Municipal de Desarrollo 2024-2027</h1>
<p>Ayuntamiento de Villa Ejemplo</p>
<ul>
<li>Eje 1. Servicios públicos de calidad</li>
<li>Eje 2. Desarrollo económico local</li>
<li>Eje 3. Medio ambiente y espacios públicos</li>
<li>Eje 4. Gobierno abierto</li>
</ul>
</body></html>"""


def generar() -> None:
    DOCS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": 760, "height": 500})

        # 1) PDF con texto real
        pagina.set_content(DOCUMENTO)
        pagina.pdf(path=str(DOCS / "plan_municipal.pdf"), format="Letter")

        # 2) Foto del documento -> PDF que contiene solo la imagen
        png = pagina.screenshot(full_page=True)
        datos = base64.b64encode(png).decode("ascii")
        pagina.set_content(
            f'<html><body style="margin:0"><img src="data:image/png;base64,{datos}" '
            f'style="width:100%"></body></html>'
        )
        pagina.pdf(path=str(DOCS / "plan_municipal_escaneado.pdf"), format="Letter")

        navegador.close()


if __name__ == "__main__":
    generar()
    print(f"PDFs generados en {DOCS}")
