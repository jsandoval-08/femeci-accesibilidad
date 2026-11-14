"""Fase 3E.1: regla de resultados oficiales (fijada el 13-nov antes de la segunda corrida) y datos de la
interfaz. Datos a mano; no tocan ningún sitio."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import generar_datos_interfaz as g  # noqa: E402

F1, F2 = "2026-11-08T20:00:00-07:00", "2026-11-13T23:00:00-07:00"


def _t(estado="no_completable", tipo_falla="no_encontrado", friccion=None, consumidas=12,
       motivo="ninguna estrategia encontró el objetivo", trayectoria="leer×12", pasos=True, puntajes=0.8):
    t = {"tarea": "A", "entrada": "https://x.mx/", "pagina_axe": "https://x.mx/", "estado": estado,
         "tipo_falla": tipo_falla, "friccion": friccion, "consumidas": consumidas, "motivo": motivo,
         "trayectoria": trayectoria, "falsas_llegadas": [], "error_axe": None,
         "puntajes": {"reglas": puntajes} if puntajes is not None else None}
    if pasos:
        t["pasos"] = [{"tecla": "leer", "anuncio": "x", "pulsaciones": i + 1, "url": "https://x.mx/",
                       "no_evaluable": None} for i in range(consumidas or friccion or 0)]
        t["encontro"] = None
    return t


def test_falla_tecnica_del_8nov_toma_la_segunda_corrida():
    primera = _t("no_evaluable", None, None, 0, "no resuelta dentro del presupuesto: timeout",
                 "entrada×1", pasos=False, puntajes=None)
    segunda = _t("con_dificultad", None, 20, None, None, "H×20", puntajes=0.9)
    o = g.elegir_oficial(primera, F1, segunda, F2)
    assert o["estado"] == "con_dificultad" and o["puntajes"] == {"reglas": 0.9}
    assert o["corrida"] == "segunda corrida, 2026-11-13" and o["fecha"] == F2
    assert len(o["pasos"]) == 20 and "timeout" in o["nota_corrida"]


def test_falla_tecnica_que_se_repite_queda_no_evaluable():
    primera = _t("no_evaluable", None, None, 0, "no resuelta dentro del presupuesto: timeout",
                 "entrada×1", pasos=False, puntajes=None)
    segunda = _t("no_evaluable", None, None, 0, "no resuelta dentro del presupuesto: timeout",
                 "entrada×1", puntajes=None)
    o = g.elegir_oficial(primera, F1, segunda, F2)
    assert o["estado"] == "no_evaluable" and o["corrida"].startswith("segunda corrida")


def test_tope_no_es_falla_tecnica():
    t = _t("no_evaluable", None, None, 508, "no resuelta dentro del presupuesto: tope_pulsaciones")
    assert not g.falla_tecnica(t)
    assert g.falla_tecnica(_t("no_evaluable", None, None, 0,
                              "no resuelta dentro del presupuesto: falla_tecnica"))


def test_manda_el_8nov_y_la_segunda_solo_aporta_pasos_si_coincide():
    primera = _t(pasos=False, puntajes=0.7)
    o = g.elegir_oficial(primera, F1, _t(puntajes=0.75), F2)
    assert o["puntajes"] == {"reglas": 0.7} and o["corrida"] == "corrida del 2026-11-08"
    assert len(o["pasos"]) == 12 and "mismo resultado" in o["nota_corrida"]


def test_si_no_coincide_los_pasos_quedan_pendientes():
    primera = _t(pasos=False)
    segunda = _t(consumidas=13, trayectoria="leer×13")
    o = g.elegir_oficial(primera, F1, segunda, F2)
    assert o["pasos"] is None and o["consumidas"] == 12
    assert "13 pulsaciones" in o["nota_corrida"] and "no la reemplaza" in o["nota_corrida"]


def test_sin_segunda_corrida_y_tarea_nueva():
    o = g.elegir_oficial(_t(pasos=False), F1, None, None)
    assert o["pasos"] is None and o["nota_corrida"] is None
    nueva = g.elegir_oficial(None, None, _t(), F2)
    assert nueva["corrida"] == "corrida del 2026-11-13" and len(nueva["pasos"]) == 12


def test_sitio_ciego_no_muestra_trayectorias():
    t = g._para_interfaz(_t(), "https://x.mx/", 15, ciego=True)
    assert t["pasos"] is None and t["trayectoria"] is None and t["falsas_llegadas"] is None
    assert t["ciego"] is True and t["estado"] == "no_completable"


def test_marcas():
    t = g._para_interfaz(_t("con_dificultad", None, 20, None, None, "leer×20"), "https://x.mx/", 15, False)
    assert {m["tipo"]: m["paso"] for m in t["marcas"]} == {"umbral": 15, "llego": 19}
    assert t["pasos"][0]["pagina"] == "/"
    t = g._para_interfaz(_t(), "https://x.mx/", 15, False)
    assert [m["tipo"] for m in t["marcas"]] == ["detenido"]
    t = g._para_interfaz(_t("no_evaluable", None, None, 1, "no resuelta dentro del presupuesto: timeout"),
                         "https://x.mx/", 15, False)
    assert "timeout" in t["marcas"][0]["texto"]
