"""Fase 4: del Excel de auditoría NVDA a un CSV por sitio. Valores a mano, antes del código.

El Excel se arma aquí con la misma forma que la hoja real (pestañas de instrucciones y de
ejemplo, filas sin veredicto, una nota al pie). Datos inventados: viven solo en esta prueba.
"""

import csv
import importlib.util
from datetime import datetime
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")
sitio = pytest.importorskip("src.sitio")

RUTA_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "excel_a_csv.py"
_spec = importlib.util.spec_from_file_location("excel_a_csv", RUTA_SCRIPT)
excel_a_csv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(excel_a_csv)

ENCABEZADO = ["tarea", "entrada", "tramite", "objetivo_correcto", "veredicto_nvda",
              "vidente_lo_encuentra", "pagina_axe", "ruta_nvda", "pulsaciones_aprox",
              "que_me_atoro", "fecha_auditoria"]
NOTA = "En la fila A deja 'tramite' vacío (gris). Celdas amarillas: las llenas tú."


def _excel(tmp_path, hojas: dict) -> Path:
    libro = openpyxl.Workbook()
    libro.active.title = "Instrucciones"
    libro.active.append(["Auditoría manual NVDA"])
    for nombre, filas in hojas.items():
        hoja = libro.create_sheet(nombre)
        hoja.append(ENCABEZADO)
        for fila in filas:
            hoja.append(fila)
    ruta = tmp_path / "auditoria.xlsx"
    libro.save(ruta)
    return ruta


def _leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


HOJAS = {
    "ejemplo": [["A", "https://www.ejemplo.gob.mx/", None, "667 123 4567", "completable", "si",
                 None, "D al pie", 8, "nada", "07/11/2026"]],
    "sitio1": [
        ["A", "https://sitio1.gob.mx/", None, "contacto@sitio1.gob.mx", "con_dificultad", "si",
         "https://sitio1.gob.mx/", "H, D y K", 35, "cuesta", "2026-11-08"],
        ["B", "https://sitio1.gob.mx/", None, None, None, None, None, None, None, None, None],
        [NOTA] + [None] * 10,
    ],
    "sitio2": [
        ["A", "https://sitio2.gob.mx/", None, None, None, None, None, None, None, None, None],
        # Celda numérica (teléfono escrito como número) y fecha como fecha de Excel.
        ["B", "https://sitio2.gob.mx/", "Acta de nacimiento", 6675550142, "completable", "no",
         None, "flechas", 20.0, "tarjetas", datetime(2026, 11, 8)],
    ],
    "sitio3": [  # nada auditado: no produce CSV
        ["A", "https://sitio3.gob.mx/", None, None, None, None, None, None, None, None, None],
    ],
}


def test_un_csv_por_sitio_solo_con_filas_auditadas(tmp_path):
    salida = tmp_path / "salida"
    escritos = excel_a_csv.convertir(_excel(tmp_path, HOJAS), salida)
    assert sorted(p.name for p in escritos) == ["sitio1.auditoria.csv", "sitio2.auditoria.csv"]
    assert not (salida / "ejemplo.auditoria.csv").exists()  # la pestaña de ejemplo no es dato
    assert not (salida / "sitio3.auditoria.csv").exists()

    filas1 = _leer(salida / "sitio1.auditoria.csv")
    assert list(filas1[0]) == list(sitio.COLUMNAS) + ["pagina_axe"]  # solo las 7 columnas
    assert [f["tarea"] for f in filas1] == ["A"]  # B sin veredicto y la nota quedan fuera
    assert filas1[0]["objetivo_correcto"] == "contacto@sitio1.gob.mx"
    assert filas1[0]["tramite"] == ""

    (b,) = _leer(salida / "sitio2.auditoria.csv")
    assert b["objetivo_correcto"] == "6675550142"  # número entero, sin ".0"
    assert b["pagina_axe"] == ""  # vacía: correr_sitio usa la entrada

    # Lo que sale lo acepta el lector de Atorapp tal cual.
    assert sitio.leer_auditoria(salida / "sitio2.auditoria.csv")[0].tramite == "Acta de nacimiento"


def test_utf8_con_bom(tmp_path):
    salida = tmp_path / "salida"
    excel_a_csv.convertir(_excel(tmp_path, HOJAS), salida)
    assert (salida / "sitio2.auditoria.csv").read_bytes().startswith(b"\xef\xbb\xbf")


def test_notas_aparte_con_sitio_y_tarea(tmp_path):
    salida = tmp_path / "salida"
    excel_a_csv.convertir(_excel(tmp_path, HOJAS), salida)
    notas = _leer(salida / "notas_nvda.csv")
    assert list(notas[0]) == ["sitio", "tarea", "ruta_nvda", "pulsaciones_aprox", "que_me_atoro",
                              "fecha_auditoria"]
    assert [(n["sitio"], n["tarea"]) for n in notas] == [("sitio1", "A"), ("sitio2", "B")]
    assert notas[0]["pulsaciones_aprox"] == "35"
    assert notas[1]["pulsaciones_aprox"] == "20" and notas[1]["fecha_auditoria"] == "2026-11-08"


def test_fila_invalida_no_escribe_nada(tmp_path):
    """Un objetivo con forma de URL en A daría no_completable fijo: se rechaza y no queda ningún
    CSV a medias que alguien pudiera correr."""
    hojas = {"malo": [["A", "https://malo.gob.mx/", None, "https://malo.gob.mx/", "completable",
                       "si", None, None, None, None, None]],
             "sitio1": HOJAS["sitio1"]}
    salida = tmp_path / "salida"
    with pytest.raises(sitio.ErrorAuditoria, match="malo"):
        excel_a_csv.convertir(_excel(tmp_path, hojas), salida)
    assert not salida.exists() or not any(salida.iterdir())
