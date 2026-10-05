"""Fase 2: axe-core dentro de capturar() y módulo de puntajes (respuesta conocida)."""

import json
from pathlib import Path

import pytest

from src.captura import capturar
from src.puntajes import calcular_puntajes, puntajes_de_captura

PAGINAS = Path(__file__).parent / "paginas"
SEIS = ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
        "formulario_sin_etiquetas", "pdf_escaneado"]


def _capturar(nombre, base):
    return capturar((PAGINAS / f"{nombre}.html").resolve().as_uri(), base=base)


def _axe(carpeta):
    return json.loads((carpeta / "axe.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def capturas(tmp_path_factory):
    base = tmp_path_factory.mktemp("capturas_axe")
    return {n: _capturar(n, base) for n in ["basica", "csp_estricta"] + SEIS}


# ---------- 2A: axe dentro de capturar() ----------

def test_basica_violaciones(capturas):
    axe = _axe(capturas["basica"])
    violadas = {r["id"] for r in axe["violations"]}
    assert {"image-alt", "link-name"} <= violadas
    for lista in ("violations", "passes", "incomplete", "inapplicable"):
        assert lista in axe
    # los nodos vienen completos (no recortados)
    assert all(r["nodes"] for r in axe["passes"])


def test_metadatos_axe(capturas):
    meta = json.loads((capturas["basica"] / "metadatos.json").read_text(encoding="utf-8"))
    axe = _axe(capturas["basica"])
    assert meta["axe_version"] == axe["testEngine"]["version"]
    assert meta["axe_etiquetas"] == ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
    assert meta["bypass_csp"] is True and meta["axe_error"] is None
    # solo se corrieron reglas de esas etiquetas
    etiquetas = {"wcag2a", "wcag2aa", "wcag21a", "wcag21aa"}
    for lista in ("violations", "passes", "incomplete"):
        assert all(etiquetas & set(r["tags"]) for r in axe[lista])


def test_axe_corre_con_csp_estricta(capturas):
    meta = json.loads((capturas["csp_estricta"] / "metadatos.json").read_text(encoding="utf-8"))
    assert meta["axe_error"] is None and meta["axe_version"]
    assert "image-alt" in {r["id"] for r in _axe(capturas["csp_estricta"])["violations"]}


# ---------- Páginas de prueba ----------

def test_perfecta_cero_violaciones(capturas):
    """Si falla, la PÁGINA está mal y se corrige (no la prueba)."""
    axe = _axe(capturas["perfecta"])
    detalle = [(r["id"], [n["target"] for n in r["nodes"]]) for r in axe["violations"]]
    assert detalle == []
    p = puntajes_de_captura(capturas["perfecta"])
    assert p["reglas"] == 1.0 and p["elementos"] == 1.0


@pytest.mark.parametrize("nombre", SEIS)
def test_seis_paginas_puntajes_validos(nombre, capturas):
    p = puntajes_de_captura(capturas[nombre])
    assert 0 <= p["reglas"] <= 1 and 0 <= p["elementos"] <= 1


# ---------- 2B: módulo de puntajes (axe armado a mano) ----------

def _regla(id_, n):
    return {"id": id_, "nodes": [{}] * n}


def test_puntajes_cuentas_conocidas():
    axe = {
        "violations": [_regla("a", 2), _regla("b", 1)],
        "passes": [_regla("b", 4), _regla("c", 3), _regla("d", 1)],  # b también falla en 1 nodo
        "incomplete": [_regla("e", 5)],
        "inapplicable": [_regla("f", 0), _regla("g", 0)],
    }
    p = calcular_puntajes(axe)
    # b se cuenta como violada; aprobadas = c, d
    assert (p["reglas_aprobadas"], p["reglas_violadas"]) == (2, 2)
    assert p["reglas"] == 2 / 4
    assert (p["nodos_pasan"], p["nodos_fallan"]) == (8, 3)
    assert p["elementos"] == 8 / 11
    # las incompletas no entran al puntaje y se reportan aparte
    assert (p["incompletas_reglas"], p["incompletas_nodos"]) == (1, 5)
    assert p["no_aplicables_reglas"] == 2


def test_puntaje_sin_denominador_es_none():
    p = calcular_puntajes({"violations": [], "passes": [], "incomplete": [], "inapplicable": []})
    assert p["reglas"] is None and p["elementos"] is None


def test_axe_con_error_no_da_puntaje():
    with pytest.raises(ValueError):
        calcular_puntajes({"error": "falló"})
