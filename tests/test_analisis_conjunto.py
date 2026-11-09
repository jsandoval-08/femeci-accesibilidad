"""Fase 4: análisis conjunto. Reportes inventados: viven solo en esta prueba y nunca se reportan."""

import importlib.util
import json
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "scripts" / "analisis_conjunto.py"
_spec = importlib.util.spec_from_file_location("analisis_conjunto", RUTA)
analisis_conjunto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analisis_conjunto)

PUNTAJES = {"reglas": 0.9, "elementos": 0.8, "reglas_conservador": 0.7, "elementos_conservador": 0.6}


def _tarea(letra, estado, nvda, friccion=None, consumidas=None, sens=None, falsas=0):
    return {"tarea": letra, "entrada": "https://x.gob.mx/", "tramite": None, "objetivo_correcto": "x",
            "pagina_axe": "https://x.gob.mx/", "estado": estado, "tipo_falla": None,
            "estrategia": "H_a_seccion", "friccion": friccion, "consumidas": consumidas, "motivo": None,
            "sensibilidad": sens or {"10": estado, "15": estado, "25": estado}, "trayectoria": "H×1",
            "falsas_llegadas": [{"estrategia": "x", "pulsaciones": 1, "encontro": "y"}] * falsas,
            "captcha": [], "puntajes": PUNTAJES, "error_axe": None, "veredicto_nvda": nvda,
            "vidente_lo_encuentra": True}


def _reporte(carpeta, sitio, *tareas):
    (carpeta / sitio).mkdir(parents=True)
    datos = {"sitio": sitio, "url_base": "https://x.gob.mx/", "fecha": "2026-11-08",
             "palabras_version": 2, "tareas": list(tareas)}
    (carpeta / sitio / f"{sitio}.reporte.json").write_text(json.dumps(datos), encoding="utf-8")


def test_matriz_sensibilidad_y_auc_no_calculado(tmp_path):
    # s1 A: fricción 12 → con_dificultad con 10, completable con 15 y 25; NVDA completable.
    _reporte(tmp_path, "s1", _tarea("A", "completable", "completable", friccion=12,
                                    sens={"10": "con_dificultad", "15": "completable",
                                          "25": "completable"}, falsas=1))
    _reporte(tmp_path, "s2", _tarea("B", "no_completable", "con_dificultad", consumidas=73),
             _tarea("A", "no_evaluable", "completable"))  # excluida del acuerdo
    datos, md = analisis_conjunto.analizar(tmp_path, tmp_path / "no_hay_notas.csv")
    assert datos["matriz"]["n"] == 2
    assert datos["matriz"]["excluidas"]["no_evaluable_atorapp"] == 1
    assert datos["matriz"]["matriz"]["con_dificultad"]["no_completable"] == 1
    assert datos["acuerdo_por_umbral"] == {10: {"n": 2, "iguales": 0}, 15: {"n": 2, "iguales": 1},
                                           25: {"n": 2, "iguales": 1}}
    assert datos["auc"]["calculado"] is False and "no es interpretable" in md
    assert datos["falsas_llegadas"]["tareas_con_falsa"] == 1
    assert "73 consumidas" in md and "90.0 %" in md
