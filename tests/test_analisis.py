"""Fase 3D: análisis contra NVDA. Valores a mano, antes del código.

LOS DATOS DE ESTE ARCHIVO SON INVENTADOS y existen SOLO para probar las fórmulas. No son resultados
de ningún sitio, nunca se reportan y el módulo de análisis no los escribe en ningún lado.
"""

import json

import pytest

analisis = pytest.importorskip("src.analisis")

C, D, N, E = "completable", "con_dificultad", "no_completable", "no_evaluable"


def _reg(nvda, atorapp=C, puntaje=0.5, sitio="s1", tarea="A", falsas=0, vidente=None):
    puntajes = None if puntaje is None else {
        "reglas": puntaje, "elementos": puntaje, "reglas_conservador": puntaje,
        "elementos_conservador": puntaje}
    return analisis.RegistroTarea(sitio, tarea, atorapp, nvda, vidente, puntajes, falsas)


# Inventado. 5 comparables: (C,C), (C,C), (C,N), (N,N), (D,C). 3 excluidas.
REGISTROS = [_reg(C, C), _reg(C, C), _reg(C, N), _reg(N, N), _reg(D, C),
             _reg(None, C), _reg(E, C), _reg(C, E)]


def test_matriz_confusion():
    m = analisis.matriz_confusion(REGISTROS)
    assert m["clases"] == [C, D, N] and m["n"] == 5
    assert m["matriz"][C] == {C: 2, D: 0, N: 1}
    assert m["matriz"][D] == {C: 1, D: 0, N: 0}
    assert m["matriz"][N] == {C: 0, D: 0, N: 1}
    assert m["excluidas"] == {"sin_nvda": 1, "no_evaluable_nvda": 1, "no_evaluable_atorapp": 1}


def test_acuerdo_observado():
    a = analisis.acuerdo_observado(REGISTROS)
    assert a["n"] == 5
    assert a["tres_clases"] == pytest.approx(3 / 5)  # (C,C) ×2 y (N,N)
    assert a["binario"] == pytest.approx(4 / 5)  # además (D,C): ambos se lograron


def test_acuerdo_sin_datos_es_none():
    a = analisis.acuerdo_observado([_reg(None), _reg(E)])
    assert a == {"n": 0, "tres_clases": None, "binario": None}


@pytest.mark.parametrize("positivos,negativos,auc", [
    ([0.9, 0.8], [0.2, 0.1], 1.0),  # el puntaje separa perfecto
    ([0.2, 0.1], [0.9, 0.8], 0.0),  # al revés
    ([0.5, 0.5], [0.5, 0.5], 0.5),  # no distingue
    ([0.9, 0.3], [0.8, 0.2], 0.75),  # 3 de 4 pares bien ordenados
])
def test_auc(positivos, negativos, auc):
    registros = [_reg(C, puntaje=p) for p in positivos] + [_reg(N, puntaje=p) for p in negativos]
    r = analisis.auc_axe(registros)
    assert r["referencia"] == "nvda" and r["exploratorio"] is False
    assert set(r["principal"]) == set(analisis.PUNTAJES)
    for fila in r["principal"].values():
        assert fila["auc"] == pytest.approx(auc)
        assert fila["n_tareas"] == 4 and fila["motivo"] is None


def test_auc_principal_excluye_con_dificultad_y_secundario_lo_cuenta():
    """Principal: (0.9 C) contra (0.5 N) = 1.0. Secundario: 0.1 D cuenta como logrado:
    pares (0.9, 0.5) bien y (0.1, 0.5) mal = 0.5."""
    r = analisis.auc_axe([_reg(C, puntaje=0.9), _reg(N, puntaje=0.5), _reg(D, puntaje=0.1)])
    assert r["principal"]["reglas"]["auc"] == pytest.approx(1.0)
    assert r["principal"]["reglas"]["n_tareas"] == 2
    assert r["secundario"]["reglas"]["auc"] == pytest.approx(0.5)
    assert r["secundario"]["reglas"]["n_tareas"] == 3


def test_auc_por_puntaje_es_independiente():
    a = analisis.RegistroTarea("s", "A", C, C, None, {"reglas": 0.9, "elementos": 0.1,
                               "reglas_conservador": 0.9, "elementos_conservador": 0.1}, 0)
    b = analisis.RegistroTarea("s", "B", N, N, None, {"reglas": 0.2, "elementos": 0.8,
                               "reglas_conservador": 0.2, "elementos_conservador": 0.8}, 0)
    r = analisis.auc_axe([a, b])["principal"]
    assert r["reglas"]["auc"] == pytest.approx(1.0) and r["elementos"]["auc"] == pytest.approx(0.0)


@pytest.mark.parametrize("registros", [
    [],  # sin datos
    [_reg(C), _reg(C)],  # una sola clase
    [_reg(None), _reg(E)],  # nada comparable
    [_reg(C, puntaje=None), _reg(N, puntaje=None)],  # sin puntajes
])
def test_auc_no_calculable_es_none_con_motivo(registros):
    for fila in analisis.auc_axe(registros)["principal"].values():
        assert fila["auc"] is None and fila["motivo"]


def test_auc_cuenta_tareas_y_sitios_y_excluidas():
    registros = [_reg(C, puntaje=0.9, sitio="s1"), _reg(N, puntaje=0.1, sitio="s1"),
                 _reg(C, puntaje=0.8, sitio="s2"), _reg(N, puntaje=None, sitio="s3"),
                 _reg(E, puntaje=0.5, sitio="s4")]
    fila = analisis.auc_axe(registros)["principal"]["reglas"]
    assert fila["n_tareas"] == 3 and fila["n_sitios"] == 2 and fila["sin_puntaje"] == 1


def test_auc_contra_atorapp_es_exploratorio():
    registros = [_reg(None, C, puntaje=0.9), _reg(None, N, puntaje=0.1)]
    r = analisis.auc_axe(registros, referencia="atorapp")
    assert r["exploratorio"] is True and r["principal"]["reglas"]["auc"] == pytest.approx(1.0)
    with pytest.raises(ValueError):
        analisis.auc_axe(registros, referencia="otra")


def test_falsas_llegadas():
    registros = [_reg(C, sitio="s1", falsas=2), _reg(C, sitio="s1", falsas=0),
                 _reg(None, sitio="s2", falsas=1), _reg(N, sitio="s3", falsas=0)]
    r = analisis.falsas_llegadas(registros)
    assert r["tareas_con_falsa"] == 2 and r["n_tareas"] == 4  # cuenta tareas, no estrategias
    assert r["por_sitio"] == {"s1": 1, "s2": 1, "s3": 0}


def test_cargar_registros(tmp_path):
    datos = {"sitio": "s1", "tareas": [
        {"tarea": "A", "estado": C, "veredicto_nvda": N, "vidente_lo_encuentra": True,
         "puntajes": {"reglas": 0.9, "elementos": 0.8, "reglas_conservador": 0.7,
                      "elementos_conservador": 0.6},
         "falsas_llegadas": [{"estrategia": "H_a_seccion", "pulsaciones": 3, "encontro": "x"}]},
        {"tarea": "B", "estado": N, "veredicto_nvda": None, "vidente_lo_encuentra": None,
         "puntajes": None, "falsas_llegadas": []},
    ]}
    ruta = tmp_path / "s1.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    a, b = analisis.cargar_registros([ruta])
    assert (a.sitio, a.tarea, a.atorapp, a.nvda, a.vidente) == ("s1", "A", C, N, True)
    assert a.puntajes["reglas"] == 0.9 and a.falsas_llegadas == 1
    assert b.nvda is None and b.puntajes is None and b.falsas_llegadas == 0
