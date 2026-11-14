"""Fase 3E.1: corre las 24 tareas de las páginas de prueba y guarda sus reportes.

Las pruebas (pytest) ya verifican estas tareas, pero sus reportes quedan en carpetas temporales. Este
script los deja en estudio/resultados_prueba/<pagina>/ para que la interfaz los muestre.

SOLO páginas locales: levanta un servidor http en 127.0.0.1 sobre tests/paginas (como conftest.py; no
file://). Compara cada tarea con su .esperado.yaml (estado, tipo_falla, fricción, estrategia) y
termina con error si una sola difiere: lo que se muestra es exactamente lo que las pruebas exigen.

Uso: python scripts/correr_paginas_prueba.py [--carpeta estudio/resultados_prueba]
"""

import argparse
import functools
import http.server
import sys
import threading
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.reporte import a_diccionario, escribir_reporte  # noqa: E402
from src.sitio import correr_sitio  # noqa: E402

PAGINAS = RAIZ / "tests" / "paginas"
CARPETA = RAIZ / "estudio" / "resultados_prueba"
NOMBRES = ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
           "formulario_sin_etiquetas", "pdf_escaneado"]


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def _servidor():
    manejador = functools.partial(_Silencioso, directory=str(PAGINAS))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def diferencias(tarea: dict, esperado: dict) -> list[str]:
    """Lo que no coincide entre una tarea del reporte y su yaml. Vacío = igual."""
    friccion = tarea["friccion"] if tarea["friccion"] is not None else tarea["consumidas"]
    pares = [("estado", tarea["estado"], esperado["estado"]),
             ("tipo_falla", tarea["tipo_falla"], esperado["tipo_falla"]),
             ("friccion", friccion, esperado["friccion_esperada"]),
             ("estrategia", tarea["estrategia"], esperado["estrategia"])]
    return [f"{campo}: {obtenido!r} (esperado {esperado_!r})"
            for campo, obtenido, esperado_ in pares if obtenido != esperado_]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Reportes de las 24 tareas de prueba.")
    ap.add_argument("--carpeta", default=CARPETA)
    args = ap.parse_args(argv)
    srv, base = _servidor()
    errores = []
    try:
        for nombre in NOMBRES:
            reporte = correr_sitio(PAGINAS / f"{nombre}.auditoria.csv", base,
                                   Path(args.carpeta) / nombre, timeout_ms=5_000, espera_ms=0,
                                   pausa_s=0)
            escribir_reporte(reporte, Path(args.carpeta) / nombre)
            esperado = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))
            for t in a_diccionario(reporte)["tareas"]:
                for d in diferencias(t, esperado["tareas"][t["tarea"]]):
                    errores.append(f"{nombre} {t['tarea']}: {d}")
            print(f"{nombre}: listo")
    finally:
        srv.shutdown()
        srv.server_close()
    if errores:
        print("DIFERENCIAS con los .esperado.yaml:", *errores, sep="\n  ", file=sys.stderr)
        return 1
    print(f"Las {len(NOMBRES) * 4} tareas coinciden con sus .esperado.yaml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
