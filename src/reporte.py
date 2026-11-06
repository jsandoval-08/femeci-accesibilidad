"""Reporte por sitio (Fase 3D): un JSON para el análisis y un Markdown para leer.

Es una ESTIMACIÓN de Atorapp: la referencia es la auditoría manual con NVDA. Lo que no se midió
se dice como no medido. Los puntajes de axe miden solo lo que axe revisa automáticamente.
"""

import json
from itertools import groupby
from pathlib import Path

from src.sitio import PUNTAJES, ReporteSitio
from src.veredicto import UMBRAL

NOTA = ("Esta es una estimación de Atorapp sobre lo que un lector de pantalla anunciaría; la referencia es la "
        "auditoría manual con NVDA. El puntaje de conformidad automática mide solo lo que axe-core "
        "revisa, sobre la página fijada de antemano para cada tarea.")


def resumir_trayectoria(pasos) -> str:
    """Teclas seguidas agrupadas: "H×6, leer×1". El detalle completo es reproducible."""
    grupos = [f"{tecla}×{sum(1 for _ in g)}" for tecla, g in groupby(p.tecla for p in pasos)]
    return ", ".join(grupos) or "sin pulsaciones"


def _tarea(r) -> dict:
    v, f = r.veredicto, r.fila
    return {
        "tarea": f.tarea, "entrada": f.entrada, "tramite": f.tramite,
        "objetivo_correcto": f.objetivo_correcto, "pagina_axe": f.pagina_axe,
        "estado": v.estado, "tipo_falla": v.tipo_falla, "estrategia": v.estrategia,
        "friccion": v.friccion, "consumidas": v.consumidas, "motivo": v.motivo,
        "sensibilidad": {str(u): e for u, e in v.sensibilidad.items()},
        "trayectoria": resumir_trayectoria(v.intento.trayectoria),
        "falsas_llegadas": [{"estrategia": x.estrategia, "pulsaciones": x.pulsaciones,
                             "encontro": x.encontro} for x in v.falsas_llegadas],
        "captcha": list(r.captcha), "puntajes": r.puntajes, "error_axe": r.error_axe,
        "veredicto_nvda": f.veredicto_nvda, "vidente_lo_encuentra": f.vidente_lo_encuentra,
    }


def a_diccionario(reporte: ReporteSitio) -> dict:
    return {"sitio": reporte.sitio, "url_base": reporte.url_base, "fecha": reporte.fecha,
            "palabras_version": reporte.palabras_version, "umbral": UMBRAL, "nota": NOTA,
            "tareas": [_tarea(r) for r in reporte.tareas]}


def _pct(valor) -> str:
    return "no medido" if valor is None else f"{valor * 100:.1f} %"


def _sn(valor) -> str:
    return "no medido" if valor is None else ("sí" if valor is True else valor if valor else "no")


def _markdown(datos: dict) -> str:
    lineas = [f"# Reporte de Atorapp: {datos['sitio']}", "", datos["nota"], "",
              f"Fecha: {datos['fecha']} · Umbral: {datos['umbral']} pulsaciones · "
              f"Palabras clave: versión {datos['palabras_version']}", "", "## Resumen", "",
              "| Tarea | Estado | Falla | Estrategia | Fricción | Trayectoria |",
              "|---|---|---|---|---|---|"]
    for t in datos["tareas"]:
        friccion = t["friccion"] if t["friccion"] is not None else f"{t['consumidas']} consumidas"
        lineas.append(f"| {t['tarea']} | {t['estado']} | {t['tipo_falla'] or '—'} | "
                      f"{t['estrategia'] or '—'} | {friccion} | {t['trayectoria']} |")
    lineas += ["", "## Llegó primero a otra cosa", "",
               "Estrategias que creyeron llegar, pero no al objetivo correcto. No cambian el estado; "
               "en un sitio real eso también le puede pasar a una persona.", ""]
    falsas = [(t["tarea"], x) for t in datos["tareas"] for x in t["falsas_llegadas"]]
    lineas += [f"- Tarea {tarea}: {x['estrategia']}, en {x['pulsaciones']} pulsaciones, encontró "
               f"\"{x['encontro']}\"." for tarea, x in falsas] or ["Ninguna."]
    lineas += ["", "## Detalle por tarea"]
    for t in datos["tareas"]:
        sens = ", ".join(f"{u}: {e}" for u, e in t["sensibilidad"].items())
        lineas += ["", f"### Tarea {t['tarea']}", "",
                   f"- Entrada: {t['entrada']}" + (f" · Trámite: {t['tramite']}" if t["tramite"] else ""),
                   f"- Objetivo correcto: {t['objetivo_correcto']}",
                   f"- Motivo: {t['motivo'] or 'se llegó al objetivo correcto'}",
                   f"- Con otros umbrales: {sens}"]
        if t["captcha"]:
            lineas.append(f"- CAPTCHA detectado: {', '.join(t['captcha'])}")
        lineas.append(f"- Veredicto NVDA: {_sn(t['veredicto_nvda'])} · "
                      f"¿Lo encuentra un usuario vidente?: {_sn(t['vidente_lo_encuentra'])}")
        puntajes = t["puntajes"]
        if puntajes is None:
            lineas.append(f"- Puntajes de axe en {t['pagina_axe']}: no medido ({t['error_axe']})")
        else:
            texto = " · ".join(f"{k.replace('_', ' ')}: {_pct(puntajes[k])}" for k in PUNTAJES)
            lineas.append(f"- Puntajes de axe en {t['pagina_axe']}: {texto}")
    return "\n".join(lineas) + "\n"


def escribir_reporte(reporte: ReporteSitio, carpeta) -> tuple[Path, Path]:
    """Escribe <sitio>.reporte.json y <sitio>.reporte.md; devuelve sus rutas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = a_diccionario(reporte)
    ruta_json = carpeta / f"{reporte.sitio}.reporte.json"
    ruta_md = carpeta / f"{reporte.sitio}.reporte.md"
    ruta_json.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    ruta_md.write_text(_markdown(datos), encoding="utf-8")
    return ruta_json, ruta_md
