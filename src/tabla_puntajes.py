"""Tabla de las páginas de prueba: puntajes de axe junto a la fricción esperada.

Uso: python -m src.tabla_puntajes
Captura cada página en una carpeta temporal; los números salen de axe.json y de los
.esperado.yaml, nunca se escriben a mano.
"""

import tempfile
from pathlib import Path

import yaml

from src.captura import capturar
from src.puntajes import puntajes_de_captura

PAGINAS = Path(__file__).resolve().parent.parent / "tests" / "paginas"
NOMBRES = ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
           "formulario_sin_etiquetas", "pdf_escaneado"]


def _pct(x):
    return "n/d" if x is None else f"{x * 100:.1f}%"


def main() -> None:
    print("| Página | Reglas | Reglas cons. | Elementos | Elementos cons. | Aprob/Viol | Nodos pasan/fallan | Incompl. (reglas/nodos) "
          "| Fricción A | B | C | D |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    with tempfile.TemporaryDirectory() as tmp:
        for n in NOMBRES:
            carpeta = capturar((PAGINAS / f"{n}.html").as_uri(), base=Path(tmp))
            p = puntajes_de_captura(carpeta)
            t = yaml.safe_load((PAGINAS / f"{n}.esperado.yaml").read_text(encoding="utf-8"))["tareas"]
            fr = " | ".join(str(t[k]["friccion_esperada"]) + ("*" if t[k]["estado"] == "no_completable" else "")
                            for k in "ABCD")
            print(f"| {n} | {_pct(p['reglas'])} | {_pct(p['reglas_conservador'])} "
                  f"| {_pct(p['elementos'])} | {_pct(p['elementos_conservador'])} "
                  f"| {p['reglas_aprobadas']}/{p['reglas_violadas']} | {p['nodos_pasan']}/{p['nodos_fallan']} "
                  f"| {p['incompletas_reglas']}/{p['incompletas_nodos']} | {fr} |")
    print("\n* = no completable (la fricción declarada no decide el estado)")


if __name__ == "__main__":
    main()
