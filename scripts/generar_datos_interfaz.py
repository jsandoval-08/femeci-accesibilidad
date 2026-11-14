"""Fase 3E.1: arma los resultados oficiales y escribe interfaz/datos.js para la interfaz estática.

1. Resultados oficiales (regla fijada el 13-nov ANTES de ver la segunda corrida; ver BITACORA.md):
   - Si la corrida del 8-nov de una tarea fue no_evaluable por falla técnica (timeout, error de carga),
     el resultado oficial es el de la segunda corrida: veredicto, puntajes de axe y pasos.
   - En las demás manda la corrida del 8-nov; la segunda solo aporta los pasos, y solo si coinciden
     estado, tipo de falla, fricción, consumidas y trayectoria resumida. Si no, pasos = None
     ("pendiente") y una nota con lo que dio.
   - Una tarea que no estaba el 8-nov se toma de su primera corrida.
   Se escriben en estudio/oficial/<sitio>/ y el análisis (scripts/analisis_conjunto.py, con las
   fórmulas de src/analisis.py) se recalcula ahí. estudio/resultados/ no se toca.
2. interfaz/datos.js: window.ATORAPP = {...}. Sin fetch(): Chrome lo bloquea en file://.
   Lo que no está en los reportes queda null; la interfaz lo muestra como "pendiente" o "no medido".

--ciego <sitio>: sitio con auditoría NVDA a ciegas en curso. Sus pasos, trayectoria y falsas llegadas
no entran a datos.js hasta que se quite la opción.

Uso: python scripts/generar_datos_interfaz.py [--ciego ciudadano]
Se vuelve a correr cuando haya filas o corridas nuevas.
"""

import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from analisis_conjunto import analizar  # noqa: E402
from correr_paginas_prueba import NOMBRES, diferencias  # noqa: E402

RESULTADOS = RAIZ / "estudio" / "resultados"  # corrida del 8-nov (no se toca)
CORRIDAS = RAIZ / "estudio" / "corridas"  # corridas posteriores: corridas/<AAAA-MM-DD>/<sitio>/
OFICIAL = RAIZ / "estudio" / "oficial"
PRUEBA = RAIZ / "estudio" / "resultados_prueba"
NOTAS = RAIZ / "estudio" / "auditoria" / "notas_nvda.csv"
PAGINAS = RAIZ / "tests" / "paginas"
SALIDA = RAIZ / "interfaz" / "datos.js"
# Motivos de No evaluable que son falla técnica (src/emulador.py, NoEvaluable). Los topes y la
# profundidad no lo son: son el presupuesto de exploración, y el CAPTCHA tampoco.
MOTIVOS_TECNICOS = ("timeout", "falla_tecnica")
COMPARAR = ("estado", "tipo_falla", "friccion", "consumidas", "trayectoria")


def _dia(fecha_iso: str) -> str:
    return fecha_iso[:10]


def falla_tecnica(tarea: dict) -> bool:
    motivo = tarea.get("motivo") or ""
    return tarea["estado"] == "no_evaluable" and motivo.split(": ")[-1] in MOTIVOS_TECNICOS


def coincide(a: dict, b: dict) -> bool:
    return all(a.get(c) == b.get(c) for c in COMPARAR)


def _resumen(t: dict) -> str:
    falla = f", {t['tipo_falla'].replace('_', ' ')}" if t["tipo_falla"] else ""
    cuenta = (f"fricción {t['friccion']}" if t["friccion"] is not None
              else f"{t['consumidas']} pulsaciones consumidas")
    return f"{t['estado'].replace('_', ' ')}{falla}, {cuenta}" + (f" ({t['motivo']})" if t["motivo"] else "")


def elegir_oficial(primera: dict | None, fecha_primera: str | None,
                   segunda: dict | None, fecha_segunda: str | None) -> dict:
    """Aplica la regla a UNA tarea. Devuelve la tarea oficial con 'corrida', 'fecha' y
    'nota_corrida'; 'pasos' es None si no hay pasos válidos."""
    if primera is None:  # la tarea no estaba el 8-nov: su primera corrida
        oficial = copy.deepcopy(segunda)
        oficial.update(corrida=f"corrida del {_dia(fecha_segunda)}", fecha=fecha_segunda,
                       nota_corrida=None)
        return oficial
    oficial = copy.deepcopy(primera)
    oficial.update(corrida=f"corrida del {_dia(fecha_primera)}", fecha=fecha_primera,
                   nota_corrida=None)
    oficial.setdefault("pasos", None)  # los reportes del 8-nov no los guardaron
    oficial.setdefault("encontro", None)
    if segunda is None:
        return oficial
    if falla_tecnica(primera):
        oficial = copy.deepcopy(segunda)
        oficial.update(corrida=f"segunda corrida, {_dia(fecha_segunda)}", fecha=fecha_segunda,
                       nota_corrida=(f"La corrida del {_dia(fecha_primera)} fue {_resumen(primera)}. "
                                     "Por la regla del 13-nov, el resultado oficial es el de la "
                                     "segunda corrida (único reintento)."))
        return oficial
    if coincide(primera, segunda):
        oficial["pasos"] = segunda["pasos"]
        oficial["encontro"] = segunda.get("encontro")
        oficial["falsas_llegadas"] = segunda["falsas_llegadas"]
        oficial["nota_corrida"] = (f"Pasos de la segunda corrida ({_dia(fecha_segunda)}), que dio el "
                                   "mismo resultado; el veredicto es el de la primera.")
    else:
        oficial["nota_corrida"] = (f"La segunda corrida ({_dia(fecha_segunda)}) dio {_resumen(segunda)}, "
                                   "distinto de la primera: no la reemplaza y sus pasos no se muestran.")
    return oficial


def _leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def _primera_corrida_posterior(sitio: str, carpeta_corridas: Path) -> dict | None:
    """La segunda corrida de un sitio: la más antigua de estudio/corridas/ (cada corrida es única)."""
    reportes = [_leer(r) for r in carpeta_corridas.glob(f"*/{sitio}/{sitio}.reporte.json")]
    return min(reportes, key=lambda d: d["fecha"]) if reportes else None


def armar_oficial(carpeta_resultados=RESULTADOS, carpeta_corridas=CORRIDAS,
                  carpeta_oficial=OFICIAL) -> list[dict]:
    """Escribe estudio/oficial/<sitio>/<sitio>.reporte.json y devuelve los reportes oficiales."""
    oficiales = []
    sitios = sorted({r.parent.name for r in Path(carpeta_resultados).glob("*/*.reporte.json")}
                    | {r.parent.name for r in Path(carpeta_corridas).glob("*/*/*.reporte.json")})
    for sitio in sitios:
        ruta1 = Path(carpeta_resultados) / sitio / f"{sitio}.reporte.json"
        r1 = _leer(ruta1) if ruta1.exists() else None
        r2 = _primera_corrida_posterior(sitio, Path(carpeta_corridas))
        t1 = {t["tarea"]: t for t in r1["tareas"]} if r1 else {}
        t2 = {t["tarea"]: t for t in r2["tareas"]} if r2 else {}
        tareas = [elegir_oficial(t1.get(k), r1 and r1["fecha"], t2.get(k), r2 and r2["fecha"])
                  for k in sorted(t1.keys() | t2.keys())]
        base = r1 or r2
        reporte = {k: base[k] for k in ("sitio", "url_base", "palabras_version", "umbral", "nota")}
        reporte.update(fecha=base["fecha"], tareas=tareas,
                       regla=("Resultados oficiales según la regla del 13-nov (BITACORA.md): cada "
                              "tarea dice de qué corrida sale."))
        carpeta = Path(carpeta_oficial) / sitio
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / f"{sitio}.reporte.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2),
                                                       encoding="utf-8")
        oficiales.append(reporte)
    return oficiales


def _pagina(url: str | None, base: str) -> str | None:
    """Ruta legible de una URL: relativa a la base del sitio cuando es del mismo sitio."""
    if not url:
        return None
    if url.startswith(base):
        return "/" + url[len(base):]
    return url


def marcas(t: dict, umbral: int) -> list[dict]:
    """Dónde marcar el recorrido: se pasó del umbral, llegó, o se detuvo. Solo a partir de los datos."""
    pasos = t.get("pasos")
    if not pasos:
        return []
    salida = []
    cruce = next((i for i, p in enumerate(pasos) if p["pulsaciones"] > umbral), None)
    if cruce is not None:
        salida.append({"paso": cruce, "tipo": "umbral",
                       "texto": f"Aquí pasa de {umbral} pulsaciones (umbral)"})
    ultimo = len(pasos) - 1
    detenido = next((i for i, p in enumerate(pasos) if p.get("no_evaluable")), None)
    if t["estado"] in ("completable", "con_dificultad"):
        salida.append({"paso": ultimo, "tipo": "llego", "texto": "Llegó al objetivo correcto"})
    elif t["tipo_falla"] == "cierre_roto":
        salida.append({"paso": ultimo, "tipo": "detenido",
                       "texto": "Llegó al documento, pero no se puede leer"})
    elif t["tipo_falla"] == "no_identificable":
        salida.append({"paso": ultimo, "tipo": "detenido",
                       "texto": "Llegó a los campos, pero alguno no tiene nombre"})
    elif t.get("no_cargo"):
        salida.append({"paso": 0, "tipo": "detenido",
                       "texto": f"Aquí se detuvo: la página de entrada no cargó ({t['no_cargo']['tipo']})"})
    elif t["estado"] == "no_evaluable":
        salida.append({"paso": detenido if detenido is not None else ultimo, "tipo": "detenido",
                       "texto": f"Aquí se detuvo sin poder evaluar: {t['motivo']}"})
    else:
        salida.append({"paso": detenido if detenido is not None else ultimo, "tipo": "detenido",
                       "texto": "Aquí se detuvo sin encontrar el objetivo correcto"})
    return salida


def no_cargo(t: dict) -> dict | None:
    """Presentación: ¿la tarea quedó No evaluable porque la página de entrada no abrió? Se sabe porque su
    única parada es la "entrada" con el motivo técnico (src/emulador.py la anota así cuando falla la
    carga inicial). No cambia ningún veredicto: solo decide cómo se cuenta."""
    pasos = t.get("pasos") or []
    if t["estado"] == "no_evaluable" and len(pasos) == 1 and pasos[0]["tecla"] == "entrada":
        return {"tipo": pasos[0].get("no_evaluable") or "falla_tecnica"}
    return None


def _texto_no_cargo(tipo: str) -> str:
    causa = ("la página de entrada agotó el tiempo de espera (timeout)" if tipo == "timeout"
             else "falla técnica al abrir la página de entrada")
    return (f"No cargó en el navegador de Atorapp: {causa}. Ninguna estrategia pudo empezar, así que "
            "no se evaluó nada. Esto no es «no completable».")


def _para_interfaz(t: dict, base: str, umbral: int, ciego: bool) -> dict:
    t = copy.deepcopy(t)
    # En un sitio con auditoría a ciegas no se toca nada: su recorrido no entra a la interfaz.
    t["no_cargo"] = None if ciego else no_cargo(t)
    if t["no_cargo"]:
        t["motivo_texto"] = _texto_no_cargo(t["no_cargo"]["tipo"])  # `motivo` (dato de src/) queda intacto
        if t.get("nota_corrida"):
            t["nota_corrida"] = t["nota_corrida"].replace(
                f"({t['motivo']})", "(la página de entrada no cargó)")
    t.pop("error_axe", None) if t.get("puntajes") else None
    if ciego:
        t.update(pasos=None, trayectoria=None, falsas_llegadas=None, encontro=None,
                 ciego=True, nota_corrida="Pendiente: auditoría NVDA a ciegas en curso en este sitio.")
    else:
        t["ciego"] = False
    for p in (t.get("pasos") or []):
        p["pagina"] = _pagina(p.pop("url"), base)
    for f in (t.get("falsas_llegadas") or []):
        for p in f.get("pasos") or []:
            p["pagina"] = _pagina(p.pop("url"), base)
    t["entrada"] = _pagina(t["entrada"], base) if base else t["entrada"]
    t["pagina_axe"] = _pagina(t["pagina_axe"], base) if base else t["pagina_axe"]
    t["marcas"] = marcas(t, umbral)
    return t


def datos_interfaz(oficiales, analisis: dict, carpeta_prueba=PRUEBA, ciegos=()) -> dict:
    umbral = None
    reales = []
    for r in oficiales:
        umbral = r["umbral"]
        for t in r["tareas"]:
            reales.append({"sitio": r["sitio"], "url_base": r["url_base"],
                           **_para_interfaz(t, r["url_base"], r["umbral"], r["sitio"] in ciegos)})
    prueba = []
    for nombre in NOMBRES:
        r = _leer(Path(carpeta_prueba) / nombre / f"{nombre}.reporte.json")
        esperado = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))
        for t in r["tareas"]:
            e = esperado["tareas"][t["tarea"]]
            fila = _para_interfaz(t, r["url_base"], r["umbral"], False)
            fila.update(sitio=nombre, url_base=None, fecha=r["fecha"], corrida=f"corrida del {_dia(r['fecha'])}",
                        esperado={"estado": e["estado"], "tipo_falla": e["tipo_falla"],
                                  "friccion": e["friccion_esperada"], "estrategia": e["estrategia"],
                                  "razon": e.get("razon")},
                        coincide_esperado=not diferencias(t, e))
            prueba.append(fila)
    return {
        "generado": datetime.now().astimezone().isoformat(timespec="seconds"),
        "umbral": umbral or 15,
        "nota": oficiales[0]["nota"] if oficiales else None,
        "reales": reales,
        "prueba": prueba,
        "analisis": {k: analisis[k] for k in ("matriz", "acuerdo", "acuerdo_por_umbral",
                                              "falsas_llegadas", "auc")},
        "notas_nvda": analisis["notas_nvda"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Resultados oficiales y datos de la interfaz.")
    ap.add_argument("--ciego", action="append", default=[],
                    help="sitio con auditoría a ciegas en curso: sin trayectorias en la interfaz")
    args = ap.parse_args(argv)
    oficiales = armar_oficial()
    analisis, md = analizar(OFICIAL, NOTAS)
    md = md.replace("\n\nAtorapp es una estimación",
                    "\n\nResultados oficiales según la regla del 13-nov (BITACORA.md); la corrida del "
                    "8-nov sigue intacta en estudio/resultados/.\n\nAtorapp es una estimación", 1)
    (OFICIAL / "analisis.json").write_text(json.dumps(analisis, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    (OFICIAL / "analisis.md").write_text(md, encoding="utf-8")
    datos = datos_interfaz(oficiales, analisis, ciegos=set(args.ciego))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("// Generado por scripts/generar_datos_interfaz.py. No editar a mano.\n"
                      "window.ATORAPP = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n",
                      encoding="utf-8")
    print(f"{SALIDA} · oficiales en {OFICIAL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
