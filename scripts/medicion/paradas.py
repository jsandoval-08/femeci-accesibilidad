"""Medición (solo lectura): NÚMERO DE PARADAS de las 5 portadas capturadas el 5-oct-2026. No corre
estrategias ni veredictos. Sirvió para fijar por escrito, el 6-nov, TOPE_PULSACIONES = 4 × el máximo
medido (ver CLAUDE.md). Resultado de esa fecha: 104, 71, 123, 127 y 87 (máximo 127).

Límites: portadas, estado inicial sin expandir menús, sin iframes. capturas/ no está en el
repositorio (.gitignore); para repetirla hay que volver a capturar, y puede cambiar.

Uso: python scripts/medicion/paradas.py
"""

import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.emulador import aplanar  # noqa: E402

CAPTURAS_5_OCT = [
    "atencionciudadana.sinaloa.gob.mx_a59e8774/20261005-123407",
    "retys.sinaloa.gob.mx_Portal_Inicio_Index_385de576/20261005-123324",
    "sinaloa.gob.mx_89e2ea75/20261005-123304",
    "www.ahome.gob.mx_53bc984a/20261005-123345",
    "www.culiacan.gob.mx_6a1357dd/20261005-123243",
]


def main() -> None:
    totales = []
    for captura in CAPTURAS_5_OCT:
        ruta = RAIZ / "capturas" / captura / "arbol_ax.json"
        totales.append(len(aplanar(json.loads(ruta.read_text(encoding="utf-8")))))
        print(f"{totales[-1]:5d}  {captura.split('/')[0]}")
    print(f"mín {min(totales)}  mediana {statistics.median(totales)}  máx {max(totales)}")


if __name__ == "__main__":
    main()
