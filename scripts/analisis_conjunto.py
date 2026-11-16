"""Fase 4: análisis conjunto de los sitios reales contra la auditoría NVDA.

Usa las fórmulas de src/analisis.py, fijadas en 3D ANTES de ver datos (matriz, acuerdo de 3 clases y
binario, falsas llegadas). Agrega la sensibilidad del acuerdo al umbral (10, 15, 25) con el estado
que el propio reporte ya calcula para cada umbral, y las notas del auditor (notas_nvda.csv).

AUC: no se reporta como resultado si hay muy pocas tareas (MIN_TAREAS_AUC). Con 1 tarea de una clase
y 2 de la otra, el AUC solo puede valer 0, 0.5 o 1: un número así no dice nada de axe. Se escribe el
motivo en lugar del número.

Uso: python scripts/analisis_conjunto.py [--resultados estudio/resultados] [--notas ...]
"""

import argparse
import csv
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.analisis import (CLASES, NO_COMPLETABLE, NO_EVALUABLE, acuerdo_observado,  # noqa: E402
                          cargar_registros, falsas_llegadas, matriz_confusion)
from src.sitio import PUNTAJES  # noqa: E402
from src.veredicto import UMBRALES_SENSIBILIDAD  # noqa: E402

RESULTADOS = RAIZ / "estudio" / "resultados"
NOTAS = RAIZ / "estudio" / "auditoria" / "notas_nvda.csv"
# Fijado antes de ver los datos de la Fase 4: por debajo de esto el AUC no se interpreta.
MIN_TAREAS_AUC = 10


def _acuerdo_por_umbral(tareas) -> dict:
    """Acuerdo de 3 clases con cada umbral: el estado de Atorapp sale de 'sensibilidad' del reporte;
    NVDA no cambia (el auditor juzgó con ~15). Mismas exclusiones que el análisis principal."""
    salida = {}
    for u in UMBRALES_SENSIBILIDAD:
        comparables = [t for t in tareas if t["veredicto_nvda"] not in (None, NO_EVALUABLE)
                       and t["sensibilidad"][str(u)] != NO_EVALUABLE]
        iguales = sum(t["sensibilidad"][str(u)] == t["veredicto_nvda"] for t in comparables)
        salida[u] = {"n": len(comparables), "iguales": iguales}
    return salida


def _leer_notas(ruta) -> dict:
    if not Path(ruta).exists():
        return {}
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return {(n["sitio"], n["tarea"]): n for n in csv.DictReader(f)}


def _referencia_original(registros, tareas) -> dict | None:
    """Si alguna referencia NVDA se corrigió DESPUÉS de correr Atorapp ('veredicto_nvda_corrida' en el
    reporte oficial, 15-nov: atención A), el acuerdo también se reporta con la referencia original.
    Así se ve cuánto depende el resultado de una corrección hecha viendo a Atorapp."""
    originales = {(t["sitio"], t["tarea"]): t["veredicto_nvda_corrida"] for t in tareas
                  if t.get("veredicto_nvda_corrida") is not None}
    if not originales:
        return None
    regs = [replace(r, nvda=originales.get((r.sitio, r.tarea), r.nvda)) for r in registros]
    tars = [{**t, "veredicto_nvda": originales.get((t["sitio"], t["tarea"]), t["veredicto_nvda"])}
            for t in tareas]
    return {"corregidas": [{"sitio": s, "tarea": k, "original": o,
                            "vigente": next(t["veredicto_nvda"] for t in tareas
                                            if (t["sitio"], t["tarea"]) == (s, k))}
                           for (s, k), o in originales.items()],
            "acuerdo": acuerdo_observado(regs), "acuerdo_por_umbral": _acuerdo_por_umbral(tars)}


def _lineas_acuerdo(acuerdo, por_umbral) -> list[str]:
    if not acuerdo["n"]:
        return ["- No hay tareas comparables."]
    return ([f"- 3 clases (principal): {round(acuerdo['tres_clases'] * acuerdo['n'])} de {acuerdo['n']}",
             f"- Binario (secundario; se logró / {NO_COMPLETABLE}): {round(acuerdo['binario'] * acuerdo['n'])} "
             f"de {acuerdo['n']}"]
            + [f"- Umbral {u} (3 clases): {v['iguales']} de {v['n']}" for u, v in por_umbral.items()])


def _pct(v) -> str:
    return "no medido" if v is None else f"{100 * v:.1f} %"


def analizar(carpeta_resultados, ruta_notas) -> tuple[dict, str]:
    rutas = sorted(Path(carpeta_resultados).glob("*/*.reporte.json"))
    registros = cargar_registros(rutas)
    tareas = []
    for ruta in rutas:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        tareas += [{"sitio": datos["sitio"], "fecha": datos["fecha"], **t} for t in datos["tareas"]]
    notas = _leer_notas(ruta_notas)
    matriz = matriz_confusion(registros)
    acuerdo = acuerdo_observado(registros)
    por_umbral = _acuerdo_por_umbral(tareas)
    falsas = falsas_llegadas(registros)
    n_auc = matriz["n"]
    auc = {"calculado": False,
           "motivo": (f"hay {n_auc} tareas comparables (de {len(registros)} tareas en "
                      f"{len({r.sitio for r in registros})} sitios); con menos de {MIN_TAREAS_AUC} el AUC "
                      "no es interpretable: solo puede tomar unos cuantos valores (con 1 tarea de cada "
                      "clase, 0 o 1) y no dice nada de axe")}
    original = _referencia_original(registros, tareas)
    datos = {"tareas": tareas, "notas_nvda": list(notas.values()), "matriz": matriz,
             "acuerdo": acuerdo, "acuerdo_por_umbral": por_umbral, "falsas_llegadas": falsas,
             "auc": auc, "referencia_original": original}

    l = ["# Análisis conjunto: Atorapp contra la auditoría NVDA", "",
         "Atorapp es una estimación; la referencia es la auditoría manual con NVDA, hecha a ciegas "
         "y antes de correr Atorapp. Las tareas de un mismo sitio no son independientes: no hay "
         "p-valores ni intervalos.", "",
         f"Tareas: {len(tareas)} · sitios: {len({t['sitio'] for t in tareas})}", "",
         "## Por tarea", "",
         "| Sitio | Tarea | NVDA | Atorapp | Falla | Fricción | Mejor estrategia | Falsas llegadas "
         "| Atorapp con 10 / 15 / 25 | axe reglas | axe elementos | reglas cons. | elementos cons. "
         "| NVDA pulsaciones aprox. |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in tareas:
        friccion = (str(t["friccion"]) if t["friccion"] is not None
                    else f"{t['consumidas']} consumidas" if t["consumidas"] is not None else "—")
        sens = " / ".join(t["sensibilidad"][str(u)] for u in UMBRALES_SENSIBILIDAD)
        p = t["puntajes"] or {}
        nota = notas.get((t["sitio"], t["tarea"]), {})
        l.append(f"| {t['sitio']} | {t['tarea']} | {t['veredicto_nvda'] or 'no medido'} | {t['estado']} "
                 f"| {t['tipo_falla'] or '—'} | {friccion} | {t['estrategia'] or '—'} "
                 f"| {len(t['falsas_llegadas'])} | {sens} | "
                 + " | ".join(_pct(p.get(k)) for k in PUNTAJES)
                 + f" | {nota.get('pulsaciones_aprox') or 'no medido'} |")
    l += ["", "## Matriz NVDA (filas) contra Atorapp (columnas)", "",
          "| NVDA \\ Atorapp | " + " | ".join(CLASES) + " |", "|---" * (len(CLASES) + 1) + "|"]
    for n in CLASES:
        l.append(f"| {n} | " + " | ".join(str(matriz["matriz"][n][a]) for a in CLASES) + " |")
    ex = matriz["excluidas"]
    l += ["", f"Comparables: {matriz['n']}. Excluidas: sin NVDA {ex['sin_nvda']}, no evaluable en NVDA "
          f"{ex['no_evaluable_nvda']}, no evaluable en Atorapp {ex['no_evaluable_atorapp']}.", "",
          "## Acuerdo observado", "",
          "Principal: acuerdo de 3 clases (la meta de la Tabla 4 del Anexo 2 dice «acuerdo de los "
          "veredictos»; decidido el 15-nov, antes de correr navolato). Binario: secundario.", ""]
    if acuerdo["n"]:
        l += [f"- 3 clases (principal): {round(acuerdo['tres_clases'] * acuerdo['n'])} de {acuerdo['n']}",
              f"- Binario (secundario; se logró / {NO_COMPLETABLE}): {round(acuerdo['binario'] * acuerdo['n'])} "
              f"de {acuerdo['n']}"]
    else:
        l.append("- No hay tareas comparables.")
    l += ["", "## Sensibilidad al umbral (acuerdo de 3 clases)", ""]
    l += [f"- Umbral {u}: {v['iguales']} de {v['n']}" for u, v in por_umbral.items()]
    if original:
        l += ["", "## Referencia corregida después de la corrida", "",
              "Estas referencias NVDA se corrigieron DESPUÉS de ver el resultado de Atorapp, al aplicar "
              "una regla que ya existía (ver BITACORA.md). Atorapp no se volvió a correr. Las secciones "
              "de arriba usan la referencia vigente; aquí, el acuerdo con la referencia original.", ""]
        l += [f"- {c['sitio']} {c['tarea']}: {c['original']} → {c['vigente']}" for c in original["corregidas"]]
        l += ["", "Acuerdo con la referencia original:", ""]
        l += _lineas_acuerdo(original["acuerdo"], original["acuerdo_por_umbral"])
    l += ["", "## Falsas llegadas", "",
          f"Tareas con al menos una: {falsas['tareas_con_falsa']} de {falsas['n_tareas']}.", "",
          "## AUC de los puntajes de axe", "", f"No se calcula: {auc['motivo']}.", ""]
    if notas:
        l += ["## Notas del auditor (no las lee Atorapp)", ""]
        for n in notas.values():
            l.append(f"- **{n['sitio']} {n['tarea']}** ({n['fecha_auditoria']}): ruta: {n['ruta_nvda']} "
                     f"· dónde se atoró: {n['que_me_atoro']}")
        l.append("")
    return datos, "\n".join(l)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Análisis conjunto de los reportes por sitio.")
    ap.add_argument("--resultados", default=RESULTADOS)
    ap.add_argument("--notas", default=NOTAS)
    args = ap.parse_args(argv)
    datos, md = analizar(args.resultados, args.notas)
    carpeta = Path(args.resultados)
    (carpeta / "analisis.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    (carpeta / "analisis.md").write_text(md, encoding="utf-8")
    print(carpeta / "analisis.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
