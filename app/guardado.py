"""Lo que guarda el modo exploración (Fase 3F): una carpeta por evaluación dentro de exploracion/.

exploracion/<AAAAMMDD-HHMMSS>_<host>_<tarea>/
    exploracion.json   todo lo corrido: intentos, pasos, opciones a confirmar, estimaciones, axe
    capturas/          la captura de axe (como en el estudio)
    reporte.md         solo si se exporta

Nada de aquí entra a estudio/, al análisis ni a interfaz/datos.js. Es una estimación experimental,
no verificada con NVDA.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from app.motor import Exploracion, estimaciones, hallazgos
from src.reporte import _paso, resumir_trayectoria
from src.sitio import PUNTAJES, TOPE_NAVEGACIONES, TOPE_PULSACIONES
from src.veredicto import UMBRAL, UMBRALES_SENSIBILIDAD, _describir

ARCHIVO = "exploracion.json"
AVISO = ("Modo exploración: estimación experimental, no verificada con NVDA. Fuera del estudio: sin "
         "objetivo correcto fijado de antemano; lo encontrado lo confirma la persona. El puntaje de "
         "conformidad automática mide solo lo que axe-core revisa.")
_ID = re.compile(r"^\d{8}-\d{6}(-\d+)?_[a-z0-9.-]+_[ABCD]$")
TAREAS = {"A": "Contacto", "B": "Requisitos de un trámite", "C": "Abrir un documento descargable",
          "D": "Llegar a un formulario e identificar sus campos"}
ESTADOS = {"completable": "Completable", "con_dificultad": "Con dificultad",
           "no_completable": "No completable", "no_evaluable": "No evaluable"}
FALLAS = {"no_encontrado": "no se encontró", "no_identificable": "no se puede identificar",
          "cierre_roto": "el cierre no funciona"}


def formato_duracion(segundos) -> str:
    """mm:ss (los minutos pueden pasar de 59). None = una evaluación guardada antes de medir el tiempo."""
    if segundos is None:
        return "no medida"
    total = int(round(segundos))
    return f"{total // 60:02d}:{total % 60:02d}"


def es_id(texto: str) -> bool:
    """¿Es un nombre de carpeta de evaluación? Evita que una petición salga de exploracion/."""
    return bool(_ID.match(texto or ""))


def nueva_carpeta(base: Path, url: str, letra: str) -> Path:
    host = re.sub(r"[^a-z0-9.-]", "-", (urlparse(url).hostname or "sitio").lower())
    sello = datetime.now().strftime("%Y%m%d-%H%M%S")
    carpeta, n = Path(base) / f"{sello}_{host}_{letra}", 1
    while carpeta.exists():
        n += 1
        carpeta = Path(base) / f"{sello}-{n}_{host}_{letra}"
    carpeta.mkdir(parents=True)
    return carpeta


def a_diccionario(ex: Exploracion) -> dict:
    r = ex.resultado
    opciones = hallazgos(r)
    return {
        "modo": "exploracion", "aviso": AVISO, "url": ex.url, "tarea": ex.tarea.letra,
        "tramite": ex.tarea.tramite, "fecha": ex.fecha, "palabras_version": ex.palabras_version,
        "umbral": UMBRAL, "umbrales": list(UMBRALES_SENSIBILIDAD), "pausa_s": ex.pausa_s,
        "topes": {"pulsaciones": TOPE_PULSACIONES, "navegaciones": TOPE_NAVEGACIONES},
        "duracion_s": ex.duracion_s,
        "intentos": [{"estrategia": i.estrategia, "llego": i.llego, "pulsaciones": i.pulsaciones,
                      "duracion_s": ex.duraciones_s[n] if n < len(ex.duraciones_s) else None,
                      "motivo": i.motivo, "encontro": _describir(i.hallazgo) if i.hallazgo else None,
                      "trayectoria": resumir_trayectoria(i.trayectoria),
                      "pasos": [_paso(p) for p in i.trayectoria]} for n, i in enumerate(r.intentos)],
        "opciones": [{k: o[k] for k in ("estrategia", "pulsaciones", "encontro")} for o in opciones],
        "requiere_confirmacion": bool(opciones),
        "estimaciones": estimaciones(r),
        "confirmacion": None,  # o {"eleccion": "0" | "1" | ... | "ninguna", "fecha": ...}
        "captcha": list(r.captcha), "puntajes": ex.puntajes, "error_axe": ex.error_axe,
        "bloqueadas": list(ex.bloqueadas),
    }


def guardar(carpeta: Path, datos: dict) -> None:
    (Path(carpeta) / ARCHIVO).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def leer(carpeta: Path) -> dict:
    return json.loads((Path(carpeta) / ARCHIVO).read_text(encoding="utf-8"))


def confirmar(carpeta: Path, eleccion: str) -> dict:
    """La persona dice qué era lo que buscaba: una opción ("0", "1", ...) o "ninguna". Es una
    confirmación humana, no un veredicto NVDA."""
    datos = leer(carpeta)
    if eleccion not in datos["estimaciones"]:
        raise ValueError(f"opción desconocida: {eleccion}")
    datos["confirmacion"] = {"eleccion": eleccion,
                             "fecha": datetime.now().astimezone().isoformat(timespec="seconds")}
    guardar(carpeta, datos)
    return datos


def vigente(datos: dict) -> dict | None:
    """La estimación que vale ahora: None si falta que la persona confirme."""
    if not datos["requiere_confirmacion"]:
        return datos["estimaciones"]["ninguna"]
    if datos["confirmacion"]:
        return datos["estimaciones"][datos["confirmacion"]["eleccion"]]
    return None


def historial(base: Path) -> list[dict]:
    """Las evaluaciones guardadas, de la más reciente a la más antigua."""
    filas = []
    for carpeta in sorted(Path(base).glob("*/" + ARCHIVO), reverse=True):
        try:
            d = leer(carpeta.parent)
        except (OSError, ValueError):
            continue
        v = vigente(d)
        filas.append({"id": carpeta.parent.name, "url": d["url"], "tarea": d["tarea"],
                      "tramite": d["tramite"], "fecha": d["fecha"],
                      "estado": v["estado"] if v else None, "por_confirmar": v is None})
    return filas


# ---------- Reporte en Markdown ----------

def _pct(valor) -> str:
    return "no medido" if valor is None else f"{valor * 100:.1f} %"


def _estado(v: dict) -> str:
    texto = ESTADOS[v["estado"]]
    if v["tipo_falla"]:
        texto += f" ({FALLAS[v['tipo_falla']]})"
    if v["friccion"] is not None:
        texto += f" · fricción {v['friccion']} pulsaciones (umbral {UMBRAL})"
    elif v["consumidas"] is not None:
        texto += f" · {v['consumidas']} pulsaciones consumidas sin resolver"
    return texto


def markdown(datos: dict) -> str:
    host = urlparse(datos["url"]).hostname
    v = vigente(datos)
    l = [f"# Atorapp · modo exploración: {host} · Tarea {datos['tarea']}", "",
         f"> **{datos['aviso']}**", "",
         f"- Dirección: {datos['url']}",
         f"- Tarea: {datos['tarea']} · {TAREAS[datos['tarea']]}"
         + (f" · Trámite buscado: {datos['tramite']}" if datos["tramite"] else ""),
         f"- Fecha: {datos['fecha']} · Palabras clave: versión {datos['palabras_version']}",
         f"- Duración total: {formato_duracion(datos.get('duracion_s'))} (mm:ss, axe incluido)",
         f"- Límites: pausa de {datos['pausa_s']:g} s entre páginas, tope de {datos['topes']['pulsaciones']} "
         f"pulsaciones y {datos['topes']['navegaciones']} páginas por estrategia; nunca envía formularios.",
         "", "## Lo que estima Atorapp", ""]
    if v is None:
        primera = datos["opciones"][0]
        condicional = datos["estimaciones"]["0"]
        l += [f"Llegué a esto: «{primera['encontro']}», en {primera['pulsaciones']} pulsaciones "
              f"({primera['estrategia']}).", "",
              f"**Por confirmar.** Si es lo que buscabas: {_estado(condicional)}. Nadie lo ha confirmado.", ""]
    else:
        eleccion = (datos["confirmacion"] or {}).get("eleccion")
        if eleccion and eleccion != "ninguna":
            l += [f"Confirmado por la persona (no por NVDA): «{datos['opciones'][int(eleccion)]['encontro']}».", ""]
        elif eleccion == "ninguna":
            l += ["La persona indicó que nada de lo encontrado era lo que buscaba.", ""]
        l += [f"**{_estado(v)}**", ""]
        if v["estrategia"]:
            l.append(f"- Estrategia: {v['estrategia']}")
        if v["motivo"]:
            l.append(f"- Motivo: {v['motivo']}")
        l.append("- Con otros umbrales: " + ", ".join(f"{u}: {ESTADOS[e]}" for u, e in v["sensibilidad"].items()))
        if v["falsas_llegadas"]:
            l.append("- Llegó primero a otra cosa: " + "; ".join(
                f"{x['estrategia']} en {x['pulsaciones']} («{x['encontro']}»)" for x in v["falsas_llegadas"]))
        l.append("")
    if datos["captcha"]:
        l += [f"CAPTCHA detectado en la ruta: {', '.join(datos['captcha'])}.", ""]
    l += ["## Estrategias", "", "| Estrategia | ¿Cree que llegó? | Pulsaciones | Duración | Encontró o motivo |",
          "|---|---|---|---|---|"]
    for i in datos["intentos"]:
        detalle = (i["encontro"] if i["llego"] else i["motivo"]) or "—"
        l.append(f"| {i['estrategia']} | {'sí' if i['llego'] else 'no'} | {i['pulsaciones']} | "
                 f"{formato_duracion(i.get('duracion_s'))} | {detalle.replace('|', '/')} |")
    pasos = v["pasos"] if v else datos["estimaciones"]["0"]["pasos"]
    l += ["", "## Recorrido paso a paso", ""]
    l += [f"{n}. {p['tecla']} — {p['anuncio']}" for n, p in enumerate(pasos, 1)] or ["Sin pulsaciones."]
    l += ["", "## Puntajes de axe-core", ""]
    if datos["puntajes"] is None:
        l.append(f"No medido ({datos['error_axe']}).")
    else:
        l += [f"- {k.replace('_', ' ').capitalize()}: {_pct(datos['puntajes'][k])}" for k in PUNTAJES]
        l += ["", "Un puntaje alto no garantiza que la tarea se pueda completar."]
    l += ["", "## Límites", "",
          "Emulador simplificado inspirado en los comandos de NVDA; no equivale a NVDA. No reproduce modo "
          "foco, no lee iframes ni anuncia aria-live. La fricción es esfuerzo de navegación (pulsaciones), "
          "no dificultad humana completa. Sin objetivo fijado de antemano, la opción más barata puede ser "
          "una falsa llegada: por eso se pide confirmar."]
    return "\n".join(l) + "\n"


def exportar(carpeta: Path) -> Path:
    ruta = Path(carpeta) / "reporte.md"
    ruta.write_text(markdown(leer(carpeta)), encoding="utf-8")
    return ruta
