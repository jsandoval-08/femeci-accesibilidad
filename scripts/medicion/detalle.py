"""Medición (solo lectura): detalle de los nodos de ciertos roles en una captura, con las
paradas que genera hoy el emulador en el subárbol de cada uno. Complementa a
roles_fuera.py: sirve para ver QUÉ hace el emulador con un rol (p. ej. si una pestaña queda
como texto suelto, o si un landmark no genera ninguna parada).

Ojo: lista TODOS los nodos de esos roles, también los que están dentro de una parada (ya
fundidos); roles_fuera.py, en cambio, solo cuenta los de afuera.

Capturas usadas el 20-oct: las del 5-oct-2026 de www.culiacan.gob.mx (tab, tabpanel,
group, tablist) y atencionciudadana.sinaloa.gob.mx (generic, complementary). Ver la lista
completa en roles_fuera.py (CAPTURAS_5_OCT); capturas/ no está en el repositorio.

Uso: python scripts/medicion/detalle.py <arbol_ax.json> <rol1,rol2,...>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.emulador import _propiedad, aplanar, normalizar  # noqa: E402


def main() -> None:
    ruta, roles = Path(sys.argv[1]), set(sys.argv[2].split(","))
    arbol = json.loads(ruta.read_text(encoding="utf-8"))
    nodos = {n["nodeId"]: n for n in arbol["nodes"]}
    paradas = {p.id_nodo: p for p in aplanar(arbol)}

    def bajo(n):
        salida = [paradas[n["nodeId"]]] if n["nodeId"] in paradas else []
        for h in n.get("childIds", []):
            if h in nodos:
                salida += bajo(nodos[h])
        return salida

    for n in arbol["nodes"]:
        if n.get("ignored") or n["role"]["value"] not in roles:
            continue
        nombre = normalizar(n.get("name", {}).get("value") or "")
        sub = bajo(n)
        print(f"{n['role']['value']} {nombre!r} enfocable={bool(_propiedad(n, 'focusable'))} "
              f"selected={_propiedad(n, 'selected')} -> {len(sub)} paradas: "
              + "; ".join(f"{p.rol}:{p.nombre[:30]!r}" for p in sub[:4])
              + (" ..." if len(sub) > 4 else ""))


if __name__ == "__main__":
    main()
