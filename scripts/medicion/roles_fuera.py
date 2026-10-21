"""Medición (solo lectura): nodos con roles FUERA de ROLES_PARADA que tienen nombre o son
enfocables, por sitio y por rol. Sirvió para decidir, el 20-oct, qué roles interactivos
(tab, menuitem, switch...) entran como parada en la Fase 3B.

Qué cuenta: nodos no ignorados, fuera de una parada (lo de adentro ya está fundido) y fuera
de aria-hidden, con la misma regla de recorrido que src/emulador.aplanar. Por cada rol:
  n           nodos encontrados
  nombre      cuántos tienen nombre
  enfocable   cuántos tienen focusable=true en el árbol
  sin_paradas cuántos no generan NINGUNA parada en su subárbol (el emulador no los ve)

Capturas usadas el 20-oct: las 5 portadas capturadas en vivo el 5-oct-2026 (estado inicial
de cada página, sin expandir menús). capturas/ no está en el repositorio (.gitignore); para
repetir la medición hay que volver a capturar con src/captura.py, y el resultado puede
cambiar si los sitios cambiaron.

Uso: python scripts/medicion/roles_fuera.py [arbol_ax.json ...]
     (sin argumentos usa las 5 capturas del 5-oct, si existen)
"""

import collections
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.emulador import (ROLES_DESCARTADOS, ROLES_PARADA, TEXTO,  # noqa: E402
                          _es_aria_hidden, _propiedad, aplanar, normalizar)

CAPTURAS_5_OCT = [
    "atencionciudadana.sinaloa.gob.mx_a59e8774/20261005-123407",
    "retys.sinaloa.gob.mx_Portal_Inicio_Index_385de576/20261005-123324",
    "sinaloa.gob.mx_89e2ea75/20261005-123304",
    "www.ahome.gob.mx_53bc984a/20261005-123345",
    "www.culiacan.gob.mx_6a1357dd/20261005-123243",
]


def medir(ruta: Path) -> dict:
    arbol = json.loads(ruta.read_text(encoding="utf-8"))
    nodos = {n["nodeId"]: n for n in arbol["nodes"]}
    raiz = next(n for n in arbol["nodes"] if "parentId" not in n)
    ids_parada = {p.id_nodo for p in aplanar(arbol)}
    por_rol = collections.defaultdict(lambda: {"n": 0, "nombre": 0, "enfocable": 0,
                                               "sin_paradas": 0, "ej": ""})

    def paradas_bajo(n):
        k = 1 if n["nodeId"] in ids_parada else 0
        return k + sum(paradas_bajo(nodos[h]) for h in n.get("childIds", []) if h in nodos)

    def visitar(n):
        if n.get("ignored"):
            if _es_aria_hidden(n):
                return
        else:
            rol = n["role"]["value"]
            if rol in ROLES_PARADA or rol in ROLES_DESCARTADOS or rol == TEXTO:
                return
            nombre = normalizar(n.get("name", {}).get("value") or "")
            enfocable = bool(_propiedad(n, "focusable"))
            if (nombre or enfocable) and rol != "RootWebArea":
                d = por_rol[rol]
                d["n"] += 1
                d["nombre"] += bool(nombre)
                d["enfocable"] += enfocable
                d["sin_paradas"] += paradas_bajo(n) == 0
                if nombre and not d["ej"]:
                    d["ej"] = nombre[:40]
        for h in n.get("childIds", []):
            if h in nodos:
                visitar(nodos[h])

    visitar(raiz)
    return por_rol


def main() -> None:
    rutas = [Path(a) for a in sys.argv[1:]] or [
        RAIZ / "capturas" / c / "arbol_ax.json" for c in CAPTURAS_5_OCT]
    for ruta in rutas:
        if not ruta.exists():
            print(f"### NO EXISTE: {ruta}")
            continue
        sitio = ruta.parts[-3].rsplit("_", 1)[0]
        print(f"### {sitio}  ({ruta.parts[-2]})")
        for rol, d in sorted(medir(ruta).items(), key=lambda x: -x[1]["n"]):
            print(f"  {rol:20} n={d['n']:3} nombre={d['nombre']:3} enfocable={d['enfocable']:3} "
                  f"sin_paradas={d['sin_paradas']:3}  ej={d['ej']!r}")


if __name__ == "__main__":
    main()
