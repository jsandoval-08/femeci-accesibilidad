"""Prueba de la captura sobre tests/paginas/basica.html (respuesta conocida)."""

import json
from pathlib import Path

from src.captura import capturar, nombre_carpeta

PAGINA = Path(__file__).parent / "paginas" / "basica.html"


def _nodos_visibles(carpeta):
    arbol = json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8"))
    return [
        (n["role"]["value"], n.get("name", {}).get("value", ""))
        for n in arbol["nodes"]
        if not n.get("ignored")
    ]


def test_captura_basica(tmp_path):
    carpeta = capturar(PAGINA.resolve().as_uri(), base=tmp_path)
    for archivo in ("pagina.html", "arbol_ax.json", "aria_snapshot.txt", "metadatos.json"):
        assert (carpeta / archivo).exists()

    nodos = _nodos_visibles(carpeta)
    assert ("heading", "Trámites de ejemplo") in nodos  # h1
    assert ("link", "Contacto") in nodos  # enlace con nombre
    assert ("link", "") in nodos  # enlace sin nombre
    assert ("image", "") in nodos  # imagen sin alt
    assert ("StaticText", "Para dudas llame al 667 123 4567.") in nodos  # teléfono

    meta = json.loads((carpeta / "metadatos.json").read_text(encoding="utf-8"))
    assert meta["viewport"] == {"width": 1366, "height": 768}
    assert meta["num_iframes"] == 0
    assert meta["chromium_version"]


def test_nombre_carpeta_seguro():
    url = 'https://ejemplo.gob.mx/a/b?x=1&y="2"|<c>*' + "z" * 200
    nombre = nombre_carpeta(url)
    assert not any(c in nombre for c in '?&=:/\\*"<>|')
    assert len(nombre) <= 80 + 1 + 8
    # URLs distintas que se limpian igual no deben chocar
    assert nombre_carpeta("https://a.mx/x?y=1") != nombre_carpeta("https://a.mx/x?y&1")
