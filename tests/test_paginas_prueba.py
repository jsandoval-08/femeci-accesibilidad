"""Fase 1B: las páginas de prueba se abren con capturar() y el árbol muestra la falla prevista.

No hay lógica de tareas aquí: solo se confirma que cada página tiene la estructura (o la falla)
con la que fue diseñada y que su .esperado.yaml es coherente.
"""

import json
import re
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

from src.captura import capturar

PAGINAS = Path(__file__).parent / "paginas"
NOMBRES = [
    "perfecta",
    "sin_encabezados",
    "sin_contacto",
    "enlaces_ambiguos",
    "formulario_sin_etiquetas",
    "pdf_escaneado",
]
LANDMARKS = {"banner", "navigation", "main", "contentinfo", "region", "complementary", "search"}
ESTADOS = {"completable", "con_dificultad", "no_completable"}
TIPOS_FALLA = {"no_encontrado", "no_identificable", "cierre_roto"}
ESTRATEGIAS = {"H_a_seccion", "F_a_campos", "enlace_por_nombre", "no_dirigida"}


@pytest.fixture(scope="module")
def capturas(tmp_path_factory):
    """Captura cada página una vez; devuelve {nombre: lista de (rol, nombre) visibles}."""
    base = tmp_path_factory.mktemp("capturas")
    salida = {}
    for nombre in NOMBRES + ["enlaces_ambiguos_tramite"]:
        carpeta = capturar((PAGINAS / f"{nombre}.html").resolve().as_uri(), base=base)
        meta = json.loads((carpeta / "metadatos.json").read_text(encoding="utf-8"))
        assert meta["estado_http"] == 200 and meta["num_iframes"] == 0
        arbol = json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8"))
        salida[nombre] = [
            (n["role"]["value"], n.get("name", {}).get("value", ""))
            for n in arbol["nodes"]
            if not n.get("ignored")
        ]
    return salida


def _roles(nodos):
    return [r for r, _ in nodos]


def test_perfecta(capturas):
    nodos = capturas["perfecta"]
    assert [n for r, n in nodos if r == "heading"][:3] == [
        "Ayuntamiento de Villa Ejemplo", "Trámites", "Licencia de construcción menor",
    ]
    assert {"banner", "navigation", "main", "contentinfo"} <= set(_roles(nodos))
    assert ("heading", "Contacto") in nodos
    assert ("StaticText", "Teléfono: 667 555 0142") in nodos
    campos = [n for r, n in nodos if r == "textbox"]
    assert len(campos) == 3 and all(campos)


def test_sin_encabezados(capturas):
    nodos = capturas["sin_encabezados"]
    assert "heading" not in _roles(nodos)
    assert not LANDMARKS & set(_roles(nodos))
    assert ("StaticText", "Teléfono: 667 555 0142") in nodos


def test_sin_contacto(capturas):
    nodos = capturas["sin_contacto"]
    textos = " ".join(n for _, n in nodos).lower()
    assert "contacto" not in textos and "tel" not in textos and "@" not in textos
    assert not re.search(r"\d{3}\s?\d{3}", textos)  # ningún número de teléfono
    html = (PAGINAS / "sin_contacto.html").read_text(encoding="utf-8")
    assert "tel:" not in html and "mailto:" not in html
    # El formulario existe y sus campos sí tienen nombre
    campos = [n for r, n in nodos if r in ("textbox", "combobox")]
    assert len(campos) >= 3 and all(campos)


def test_enlaces_ambiguos(capturas):
    nodos = capturas["enlaces_ambiguos"]
    enlaces = [n for r, n in nodos if r == "link"]
    assert enlaces.count("Leer más") == 8
    assert enlaces.count("clic aquí") == 4
    assert enlaces.count("") == 3  # íconos-enlace sin nombre

    # El enlace correcto es la tarjeta 9 de 12 y queda lejos del salto (encabezado "Trámites"):
    # cuenta de elementos (párrafos y enlaces) hasta él > 25, el umbral mayor de sensibilidad.
    html = (PAGINAS / "enlaces_ambiguos.html").read_text(encoding="utf-8")
    destinos = re.findall(r'<div class="tarjeta">.*?<a href="([^"]+)"', html, flags=re.S)
    assert len(destinos) == 12 and destinos[8] == "enlaces_ambiguos_tramite.html"
    despues = nodos[nodos.index(("heading", "Trámites")) + 1:]
    contados, enlaces_vistos = 0, 0
    for rol, _ in despues:
        if rol in ("paragraph", "link"):
            contados += 1
        if rol == "link":
            enlaces_vistos += 1
            if enlaces_vistos == 9:
                break
    assert contados == 27

    destino = capturas["enlaces_ambiguos_tramite"]
    assert ("heading", "Requisitos") in destino


def test_formulario_sin_etiquetas(capturas):
    nodos = capturas["formulario_sin_etiquetas"]
    campos = [n for r, n in nodos if r == "textbox"]
    assert len(campos) == 3 and all(n == "" for n in campos)
    # Ningún mecanismo que pueda darles nombre
    html = (PAGINAS / "formulario_sin_etiquetas.html").read_text(encoding="utf-8").lower()
    formulario = re.search(r"<form.*?</form>", html, flags=re.S).group(0)
    for prohibido in ("<label", "placeholder", "title=", "aria-label", "aria-labelledby", "aria-describedby"):
        assert prohibido not in formulario, prohibido


def test_pdf_escaneado(capturas):
    nodos = capturas["pdf_escaneado"]
    assert ("link", "Requisitos de licencia de construcción (PDF)") in nodos


def _texto_pdf(nombre):
    lector = PdfReader(PAGINAS / "docs" / nombre)
    return "".join(p.extract_text() or "" for p in lector.pages).strip()


def test_pdfs():
    assert "Identificación oficial vigente" in _texto_pdf("requisitos_licencia.pdf")
    assert _texto_pdf("requisitos_escaneado.pdf") == ""


@pytest.mark.parametrize("nombre", NOMBRES)
def test_esperado_yaml(nombre):
    datos = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))
    assert datos["pagina"] == f"{nombre}.html"
    assert set(datos["tareas"]) == {"A", "B", "C", "D"}
    for clave, t in datos["tareas"].items():
        assert (PAGINAS / t["entrada"]).exists(), f"{nombre} {clave}: entrada inexistente"
        assert t["estado"] in ESTADOS
        assert t["estrategia"] in ESTRATEGIAS
        assert t["razon"]
        # tipo_falla: null salvo en no_completable
        if t["estado"] == "no_completable":
            assert t["tipo_falla"] in TIPOS_FALLA
        else:
            assert t["tipo_falla"] is None
        # no_dirigida solo cuando no hay salto dirigido, y viceversa
        if t["estado"] == "completable":
            assert t["estrategia"] != "no_dirigida" and t["ruta"]
        if t["estado"] == "con_dificultad":
            assert t["estrategia"] == "no_dirigida" and t["ruta"]
    # Los enlaces a PDF de cada página apuntan a archivos que existen
    html = (PAGINAS / f"{nombre}.html").read_text(encoding="utf-8")
    for pdf in re.findall(r'href="(docs/[^"]+\.pdf)"', html):
        assert (PAGINAS / pdf).exists()
