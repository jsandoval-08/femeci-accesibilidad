"""Fase 4: convierte el Excel de la auditoría NVDA en un CSV por sitio, el que lee src/sitio.py.

Reproducible: siempre se corre sobre la COPIA del Excel guardada en el repositorio (evidencia de lo
que se auditó; git guarda cada versión). Reglas:
- Una pestaña = un sitio; el CSV se llama <pestaña>.auditoria.csv. Se ignoran las pestañas sin el
  encabezado de auditoría (Instrucciones, Por verificar NVDA) y la de "ejemplo" (no es dato).
- Solo filas con veredicto_nvda: las demás no se auditaron y no se usan. Una pestaña sin ninguna
  no produce CSV. Las filas cuya tarea no es A-D (notas al pie) se ignoran.
- Las 7 columnas de Atorapp, en utf-8-sig. Las notas del auditor (ruta_nvda, pulsaciones_aprox,
  que_me_atoro, fecha_auditoria) van aparte, a notas_nvda.csv, para el análisis: Atorapp no las lee.
- Todo se valida con el mismo lector de Atorapp ANTES de escribir: si una fila no sirve, no se
  escribe ningún CSV (así no queda uno a medias que alguien pudiera correr).

Uso: python scripts/excel_a_csv.py [excel] [--salida carpeta]
"""

import argparse
import csv
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import openpyxl  # noqa: E402

from src.sitio import COLUMNAS, ErrorAuditoria, leer_auditoria  # noqa: E402

COLUMNAS_CSV = (*COLUMNAS, "pagina_axe")
COLUMNAS_NOTAS = ("ruta_nvda", "pulsaciones_aprox", "que_me_atoro", "fecha_auditoria")
HOJAS_IGNORADAS = {"ejemplo"}
EXCEL = RAIZ / "estudio" / "auditoria" / "Auditoria_NVDA_Atorapp.xlsx"


def _texto(valor) -> str:
    """Celda a texto: vacía = "", 20.0 = "20" (un teléfono escrito como número no lleva ".0"),
    fecha = AAAA-MM-DD."""
    if valor is None:
        return ""
    if isinstance(valor, (datetime, date)):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _filas_auditadas(hoja) -> list[dict] | None:
    """Filas con veredicto de una pestaña; None si la pestaña no es de auditoría."""
    filas = hoja.iter_rows(values_only=True)
    encabezado = [_texto(c) for c in next(filas, ())]
    if any(c not in encabezado for c in COLUMNAS_CSV):
        return None
    datos = [dict(zip(encabezado, map(_texto, fila))) for fila in filas]
    return [d for d in datos if d["tarea"] in ("A", "B", "C", "D") and d["veredicto_nvda"]]


def _escribir(ruta: Path, columnas, filas) -> None:
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(filas)


def convertir(ruta_excel, carpeta) -> list[Path]:
    """Escribe <sitio>.auditoria.csv y notas_nvda.csv en `carpeta`; devuelve los CSV de sitio."""
    libro = openpyxl.load_workbook(ruta_excel, data_only=True, read_only=True)
    por_sitio = {}
    for hoja in libro.worksheets:
        if hoja.title.lower() in HOJAS_IGNORADAS:
            continue
        filas = _filas_auditadas(hoja)
        if filas:
            por_sitio[hoja.title] = filas
    libro.close()

    with tempfile.TemporaryDirectory() as tmp:  # validar todo antes de escribir nada
        for nombre, filas in por_sitio.items():
            prueba = Path(tmp) / f"{nombre}.auditoria.csv"
            _escribir(prueba, COLUMNAS_CSV, filas)
            try:
                leer_auditoria(prueba)
            except ErrorAuditoria as e:
                raise ErrorAuditoria(f"pestaña '{nombre}': {e}") from None

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    escritos = []
    for nombre, filas in por_sitio.items():
        escritos.append(carpeta / f"{nombre}.auditoria.csv")
        _escribir(escritos[-1], COLUMNAS_CSV, filas)
    notas = [{"sitio": nombre, **f} for nombre, filas in por_sitio.items() for f in filas]
    _escribir(carpeta / "notas_nvda.csv", ("sitio", "tarea", *COLUMNAS_NOTAS), notas)
    return escritos


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Excel de auditoría NVDA → un CSV por sitio.")
    ap.add_argument("excel", nargs="?", default=EXCEL, help="copia del Excel en el repositorio")
    ap.add_argument("--salida", default=EXCEL.parent, help="carpeta de los CSV")
    args = ap.parse_args(argv)
    try:
        escritos = convertir(args.excel, args.salida)
    except ErrorAuditoria as e:
        print(f"No se escribió ningún CSV: {e}", file=sys.stderr)
        return 2
    for ruta in escritos:
        print(ruta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
