"""Corre las tareas de un CSV de auditoría y escribe su reporte (Fase 3D.1).

Sin --sitio-real solo acepta páginas locales. Un sitio real exige escribir su host y que el CSV
tenga veredicto_nvda en todas las filas; si no, se niega antes de tocar la red.

Uso: python -m src.correr_sitio auditoria.csv http://127.0.0.1:8000/ --carpeta salida
     python -m src.correr_sitio auditoria.csv https://ejemplo.gob.mx/ --carpeta salida --sitio-real ejemplo.gob.mx
"""

import argparse
import sys

from src.reporte import escribir_reporte
from src.sitio import correr_sitio


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Corre las tareas de un sitio y escribe su reporte.")
    ap.add_argument("csv", help="CSV exportado de la hoja de auditoría")
    ap.add_argument("url_base", help="URL base contra la que se resuelven las entradas")
    ap.add_argument("--carpeta", required=True, help="dónde guardar capturas y reporte")
    ap.add_argument("--sitio-real", help="host autorizado; exige veredicto_nvda en todas las filas")
    args = ap.parse_args(argv)
    try:
        reporte = correr_sitio(args.csv, args.url_base, args.carpeta, sitio_real=args.sitio_real)
    except (ValueError, OSError) as e:
        print(f"No se corrió: {e}", file=sys.stderr)
        return 2
    ruta_json, ruta_md = escribir_reporte(reporte, args.carpeta)
    print(f"Reporte: {ruta_md} y {ruta_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
