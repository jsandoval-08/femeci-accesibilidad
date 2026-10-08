"""Puntajes de conformidad automática a partir de axe.json (Fase 2B).

Dos medidas, ambas documentadas, porque el puntaje por reglas esconde la magnitud:

  - Por reglas:    reglas aprobadas / (aprobadas + violadas).
  - Por elementos: nodos que pasan  / (nodos que pasan + nodos que fallan).

Criterios:
  - Una regla con al menos un nodo que falla cuenta como VIOLADA, aunque otros nodos
    suyos pasen (axe la lista en `violations` y en `passes`). Es "aprobada" solo si no
    tiene ningún nodo que falle.
  - Las incompletas (axe no pudo decidir; requieren revisión manual) NO entran a ningún
    puntaje y se reportan aparte. Las no aplicables tampoco; solo se cuentan.
  - Sin denominador (nada evaluado) el puntaje es None, nunca 1.0: no se inventa un dato.
  - Puntaje CONSERVADOR (cota inferior): igual, pero las incompletas cuentan como fallas
    (regla incompleta = violada; nodo incompleto = nodo que falla). Se reporta junto al normal
    porque axe deja sin decidir una parte que el normal ignora; el verdadero queda entre ambos.
  - Esto mide solo lo que axe revisa automáticamente. No es "conformidad WCAG".
"""

import json
from pathlib import Path


def _proporcion(a: int, b: int):
    """a / (a + b), o None si no hay nada evaluado."""
    return a / (a + b) if (a + b) else None


def calcular_puntajes(axe: dict) -> dict:
    """Devuelve ambos puntajes y los conteos que los respaldan (para poder auditarlos)."""
    if "error" in axe:
        raise ValueError(f"axe no corrió: {axe['error']}")

    violadas = {r["id"] for r in axe["violations"]}
    aprobadas = {r["id"] for r in axe["passes"]} - violadas
    nodos_fallan = sum(len(r["nodes"]) for r in axe["violations"])
    nodos_pasan = sum(len(r["nodes"]) for r in axe["passes"])

    # Conservador: lo que axe no pudo decidir se trata como falla.
    incompletas = {r["id"] for r in axe["incomplete"]}
    nodos_incompletos = sum(len(r["nodes"]) for r in axe["incomplete"])
    violadas_cons = violadas | incompletas
    aprobadas_cons = aprobadas - incompletas

    return {
        "reglas": _proporcion(len(aprobadas), len(violadas)),
        "elementos": _proporcion(nodos_pasan, nodos_fallan),
        "reglas_conservador": _proporcion(len(aprobadas_cons), len(violadas_cons)),
        "elementos_conservador": _proporcion(nodos_pasan, nodos_fallan + nodos_incompletos),
        "reglas_aprobadas": len(aprobadas),
        "reglas_violadas": len(violadas),
        "nodos_pasan": nodos_pasan,
        "nodos_fallan": nodos_fallan,
        "incompletas_reglas": len(axe["incomplete"]),
        "incompletas_nodos": nodos_incompletos,
        "no_aplicables_reglas": len(axe["inapplicable"]),
    }


def puntajes_de_captura(carpeta: Path) -> dict:
    """Lee <carpeta>/axe.json y calcula los puntajes."""
    axe = json.loads((Path(carpeta) / "axe.json").read_text(encoding="utf-8"))
    return calcular_puntajes(axe)
