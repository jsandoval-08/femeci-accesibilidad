"""Análisis contra la referencia (Fase 3D). Listo para datos reales; todavía NO hay ninguno.

Sin auditoría NVDA no hay resultados que reportar: este módulo solo define las fórmulas, fijadas
ANTES de ver datos para no elegir después la versión que más convenga.

  - Matriz de confusión y acuerdo observado: Atorapp vs NVDA. Quedan fuera, con su conteo, las tareas
    sin dato de NVDA y las no evaluables. El acuerdo binario ("se logró" contra no_completable) va
    junto al de 3 clases porque "con dificultad" se decide por pulsaciones, y un auditor humano no
    necesariamente lo mide igual.
  - AUC del puntaje de axe: ¿separa completables de no completables, según NVDA? Principal: excluye
    con_dificultad. Secundario: lo cuenta como logrado. referencia="atorapp" es solo exploratorio: mide
    cuánto se parece axe a Atorapp, no si axe distingue tareas realmente completables.
  - Sin p-valores ni intervalos: las tareas de un sitio no son independientes y comparten puntaje.
    Se reporta el AUC con su número de tareas y de sitios.
  - Falsas llegadas: conteo aparte; no cambian el estado.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from sklearn.metrics import roc_auc_score

from src.sitio import PUNTAJES

COMPLETABLE, CON_DIFICULTAD = "completable", "con_dificultad"
NO_COMPLETABLE, NO_EVALUABLE = "no_completable", "no_evaluable"
CLASES = [COMPLETABLE, CON_DIFICULTAD, NO_COMPLETABLE]


@dataclass(frozen=True)
class RegistroTarea:
    sitio: str
    tarea: str
    atorapp: str
    nvda: str | None  # None = no medido
    vidente: bool | None
    puntajes: dict | None
    falsas_llegadas: int


def cargar_registros(rutas_json) -> list[RegistroTarea]:
    """Lee los <sitio>.reporte.json."""
    registros = []
    for ruta in rutas_json:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
        for t in datos["tareas"]:
            registros.append(RegistroTarea(datos["sitio"], t["tarea"], t["estado"], t["veredicto_nvda"],
                                           t["vidente_lo_encuentra"], t["puntajes"],
                                           len(t["falsas_llegadas"])))
    return registros


def _comparables(registros) -> tuple[list[RegistroTarea], dict]:
    excluidas = {"sin_nvda": 0, "no_evaluable_nvda": 0, "no_evaluable_atorapp": 0}
    comparables = []
    for r in registros:
        if r.nvda is None:
            excluidas["sin_nvda"] += 1
        elif r.nvda == NO_EVALUABLE:
            excluidas["no_evaluable_nvda"] += 1
        elif r.atorapp == NO_EVALUABLE:
            excluidas["no_evaluable_atorapp"] += 1
        else:
            comparables.append(r)
    return comparables, excluidas


def matriz_confusion(registros) -> dict:
    """matriz[nvda][atorapp] = número de tareas."""
    comparables, excluidas = _comparables(registros)
    matriz = {n: {a: 0 for a in CLASES} for n in CLASES}
    for r in comparables:
        matriz[r.nvda][r.atorapp] += 1
    return {"clases": list(CLASES), "matriz": matriz, "n": len(comparables), "excluidas": excluidas}


def acuerdo_observado(registros) -> dict:
    comparables, _ = _comparables(registros)
    n = len(comparables)
    if not n:
        return {"n": 0, "tres_clases": None, "binario": None}
    iguales = sum(r.nvda == r.atorapp for r in comparables)
    binario = sum((r.nvda == NO_COMPLETABLE) == (r.atorapp == NO_COMPLETABLE) for r in comparables)
    return {"n": n, "tres_clases": iguales / n, "binario": binario / n}


def _auc(registros, puntaje: str, atributo: str, positivas: set) -> dict:
    grupo = [r for r in registros if getattr(r, atributo) in positivas | {NO_COMPLETABLE}]
    con_puntaje = [r for r in grupo if r.puntajes and r.puntajes.get(puntaje) is not None]
    etiquetas = [int(getattr(r, atributo) in positivas) for r in con_puntaje]
    fila = {"auc": None, "n_tareas": len(con_puntaje), "n_sitios": len({r.sitio for r in con_puntaje}),
            "sin_puntaje": len(grupo) - len(con_puntaje), "motivo": None}
    if not con_puntaje:
        fila["motivo"] = "no hay tareas comparables con puntaje"
    elif len(set(etiquetas)) < 2:
        fila["motivo"] = "se necesitan tareas de las dos clases"
    else:
        fila["auc"] = float(roc_auc_score(etiquetas, [r.puntajes[puntaje] for r in con_puntaje]))
    return fila


def auc_axe(registros, referencia: str = "nvda") -> dict:
    """AUC de cada puntaje. 0.5 = no distingue; 1 = un puntaje más alto siempre va con completable.
    None con motivo si no se puede calcular: nunca un valor engañoso."""
    if referencia not in ("nvda", "atorapp"):
        raise ValueError(f"Referencia desconocida: {referencia}")
    return {
        "referencia": referencia,
        "exploratorio": referencia != "nvda",
        "principal": {p: _auc(registros, p, referencia, {COMPLETABLE}) for p in PUNTAJES},
        "secundario": {p: _auc(registros, p, referencia, {COMPLETABLE, CON_DIFICULTAD})
                       for p in PUNTAJES},
    }


def falsas_llegadas(registros) -> dict:
    """Cuántas tareas tienen al menos una falsa llegada (tareas, no estrategias)."""
    por_sitio: dict[str, int] = {}
    for r in registros:
        por_sitio[r.sitio] = por_sitio.get(r.sitio, 0) + (r.falsas_llegadas > 0)
    return {"tareas_con_falsa": sum(por_sitio.values()), "n_tareas": len(registros),
            "por_sitio": por_sitio}
