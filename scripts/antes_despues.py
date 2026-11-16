"""Experimento antes/después (sección 6.8 del Anexo): atención ciudadana, tarea A, página /asistencia-digital/.
Prerregistro en BITACORA.md (16-nov). No cambia src/, umbrales, topes, palabras clave ni estrategias.

  python scripts/antes_despues.py preparar   genera original/ (desde la captura del 15-nov) y corregida/
  python scripts/antes_despues.py validar    ¿el árbol de original/ coincide con el capturado el 15-nov?
  python scripts/antes_despues.py medir      axe (4 índices) + Atorapp (todas las estrategias), una corrida por versión

Las reproducciones son EXPERIMENTALES: la captura del 15-nov con
  (1) un comentario que la rotula,
  (2) un <meta> Content-Security-Policy que impide cualquier carga fuera de la propia carpeta (ni CSS ni JS ni
      imágenes del sitio, tampoco al abrirla a mano para NVDA: no toca el sitio), y
  (3) las 6 tarjetas de main apuntando a las PNG locales (tarjetas/), sin srcset, y
  (4) una regla de CSS reconstruido (no viene del sitio; ver CSS_RECONSTRUIDO).
corregida/ = original/ con el alt de las 4 tarjetas sin enlace cambiado por su texto visible literal. Nada más.

Sin red: se sirven en 127.0.0.1 y todo contexto de Playwright aborta cualquier petición a otro host (se registra).
axe se inyecta con evaluate (no le afecta la CSP), así que no hace falta bypass_csp: los scripts de la página no corren.
"""
import argparse
import difflib
import functools
import http.server
import json
import re
import sys
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from playwright.sync_api import sync_playwright  # noqa: E402

from src.captura import AXE_ETIQUETAS, AXE_JS, AXE_OPCIONES, ESPERA_EXTRA_MS, VIEWPORT, arbol_ax  # noqa: E402
from src.emulador import Emulador, aplanar  # noqa: E402
from src.estrategias import Tarea, cargar_palabras, mejor_estrategia  # noqa: E402
from src.navegador import NavegadorEnVivo  # noqa: E402
from src.puntajes import calcular_puntajes  # noqa: E402
from src.reporte import escribir_reporte, resumir_trayectoria  # noqa: E402
from src.sitio import (HOSTS_LOCALES, PUNTAJES, TOPE_NAVEGACIONES, TOPE_PULSACIONES, FilaAuditoria,  # noqa: E402
                       ReporteSitio, ResultadoFila)
from src.veredicto import clasificar, hallazgo_correcto  # noqa: E402

CAPTURA = (RAIZ / "estudio/corridas/2026-11-15/atencion/capturas/"
           "atencionciudadana.sinaloa.gob.mx_asistencia-digital_492f6948/20261115-192802")
URL_CAPTURA = "https://atencionciudadana.sinaloa.gob.mx/asistencia-digital/"
BASE = RAIZ / "estudio/antes_despues/atencion"
OBJETIVO = "asistencia@sinaloa.gob.mx|(667) 7587123|(667) 5027665"  # el de atencion.auditoria.csv
VERSIONES = ("original", "corregida")

# Las 6 tarjetas de main (las 2 del pie no se tocan ni se bajaron).
TARJETAS = ("2024/08/Card-linea-telefonica.png", "2024/07/Tarjeta-whatsapp-dorada.png",
            "2024/07/Tarjeta-facebook-dorada.png", "2024/07/Tarjeta-correo-L-dorada.png",
            "2024/07/Tarjeta-chat-L-dorada.png", "2024/09/Tarjeta-video-L-dorada2-1.png")
# Texto visible literal (validado por Javier el 16-nov). Solo las 4 sin enlace.
ALT = {
    "Card-linea-telefonica.png": "Línea telefónica Atención ciudadana (667) 7587123",
    "Tarjeta-whatsapp-dorada.png": "Whatsapp (667) 5027665",
    "Tarjeta-correo-L-dorada.png": "Correo electrónico asistencia@sinaloa.gob.mx",
    "Tarjeta-video-L-dorada2-1.png": "Videollamada en LSM (667) 5027665",  # un solo espacio (declarado)
}
ROTULO = ("<!-- REPRODUCCIÓN EXPERIMENTAL (Atorapp, FEMECI 2026). No es el sitio oficial. Copia local de "
          "https://atencionciudadana.sinaloa.gob.mx/asistencia-digital/ capturada el 15-nov-2026 19:28, para el "
          "experimento antes/después. Ver estudio/antes_despues/atencion/README.md. -->")
CSP = ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; "
       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'none'\">")
# CSS RECONSTRUIDO (enmienda del prerregistro, 16-nov): NO viene del sitio. En vivo, la hoja externa de Elementor
# le pone content:"desktop" a <span id="elementor-device-mode" class="elementor-screen-only">, y el lector lo oye
# como la última parada. Sin esa hoja faltaba esa parada (31 de 32). Se justifica porque deja el árbol idéntico
# al capturado el 15-nov (32 de 32). Va igual en las dos versiones.
CSS_RECONSTRUIDO = '<style>#elementor-device-mode::after{content:"desktop"}</style>'


# ---------- preparar ----------

def _tag_tarjeta(html: str, ruta: str) -> re.Match:
    encontrados = list(re.finditer(r"<img\b[^>]*src=\"[^\"]*/uploads/" + re.escape(ruta) + r"\"[^>]*>", html))
    assert len(encontrados) == 1, f"{ruta}: {len(encontrados)} etiquetas"
    return encontrados[0]


def _reemplazar(html: str, m: re.Match, nuevo: str) -> str:
    return html[:m.start()] + nuevo + html[m.end():]


def preparar() -> None:
    html = (CAPTURA / "pagina.html").read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>") and html.count('<meta charset="UTF-8">') == 1
    html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>" + ROTULO, 1)
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + CSP + CSS_RECONSTRUIDO, 1)
    for ruta in TARJETAS:
        m = _tag_tarjeta(html, ruta)
        nombre = Path(ruta).name
        tag = re.sub(r"\s(srcset|sizes)=\"[^\"]*\"", "", m.group(0))
        tag = re.sub(r"src=\"[^\"]*\"", f'src="../tarjetas/{nombre}"', tag)
        html = _reemplazar(html, m, tag)
    original = html
    for nombre, alt in ALT.items():
        encontrados = list(re.finditer(r"<img\b[^>]*src=\"\.\./tarjetas/" + re.escape(nombre) + r"\"[^>]*>", html))
        assert len(encontrados) == 1, nombre
        m = encontrados[0]
        assert m.group(0).count(' alt=""') == 1
        html = _reemplazar(html, m, m.group(0).replace(' alt=""', f' alt="{alt}"'))
    corregida = html
    for version, texto in (("original", original), ("corregida", corregida)):
        (BASE / version).mkdir(parents=True, exist_ok=True)
        (BASE / version / "index.html").write_text(texto, encoding="utf-8", newline="")
    diff = difflib.unified_diff(original.splitlines(keepends=True), corregida.splitlines(keepends=True),
                                "original/index.html", "corregida/index.html", n=0)
    (BASE / "correccion.diff").write_text("".join(diff), encoding="utf-8", newline="")
    print("original/ y corregida/ generadas; diff en correccion.diff")


# ---------- red: servidor local y bloqueo ----------

class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servir():
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                               functools.partial(_Silencioso, directory=str(BASE)))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor, f"http://127.0.0.1:{servidor.server_address[1]}"


class SoloLocal:
    """Envuelve el Browser: cada contexto aborta toda petición fuera de 127.0.0.1 y la registra."""

    def __init__(self, navegador):
        self._navegador = navegador
        self.bloqueadas: list[tuple[str, str]] = []

    def new_context(self, **opciones):
        contexto = self._navegador.new_context(**opciones)
        contexto.route(lambda url: urlparse(url).hostname not in HOSTS_LOCALES, self._abortar)
        return contexto

    def _abortar(self, ruta):
        self.bloqueadas.append((ruta.request.resource_type, ruta.request.url))
        ruta.abort("blockedbyclient")

    def __getattr__(self, nombre):
        return getattr(self._navegador, nombre)


def capturar_local(navegador: SoloLocal, url: str, carpeta: Path | None) -> dict:
    """Como src.captura.capturar, sin red y sin bypass_csp; axe por evaluate."""
    contexto = navegador.new_context(viewport=VIEWPORT)
    pagina = contexto.new_page()
    respuesta = pagina.goto(url, wait_until="load")
    pagina.wait_for_timeout(ESPERA_EXTRA_MS)
    datos = {"html": pagina.content(), "arbol": arbol_ax(pagina),
             "snapshot": pagina.locator("body").aria_snapshot(), "estado": respuesta.status if respuesta else None,
             "titulo": pagina.title()}
    if carpeta is not None:
        pagina.evaluate(AXE_JS.read_text(encoding="utf-8"))
        datos["axe"] = pagina.evaluate("opciones => axe.run(document, opciones)", AXE_OPCIONES)
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "pagina.html").write_text(datos["html"], encoding="utf-8")
        (carpeta / "arbol_ax.json").write_text(json.dumps(datos["arbol"], ensure_ascii=False, indent=2), "utf-8")
        (carpeta / "aria_snapshot.txt").write_text(datos["snapshot"], encoding="utf-8")
        (carpeta / "axe.json").write_text(json.dumps(datos["axe"], ensure_ascii=False, indent=2), "utf-8")
        meta = {"url": url, "url_final": pagina.url, "estado_http": datos["estado"],
                "fecha_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
                "chromium_version": navegador.version, "viewport": VIEWPORT, "bypass_csp": False,
                "axe_version": datos["axe"].get("testEngine", {}).get("version"), "axe_etiquetas": AXE_ETIQUETAS,
                "num_iframes": len(pagina.frames) - 1, "num_nodos_ax": len(datos["arbol"]["nodes"])}
        (carpeta / "metadatos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), "utf-8")
    contexto.close()
    return datos


# ---------- validar ----------

def _paradas(arbol: dict, base_local: str | None):
    filas = []
    for p in aplanar(arbol):
        url = p.url
        if url and base_local and url.startswith(base_local):
            url = URL_CAPTURA + url[len(base_local):]  # mismo destino relativo (p. ej. #content)
        filas.append(f"{p.rol} | {p.nombre!r} | nivel={p.nivel} | foco={p.enfocable} | "
                     f"landmarks={list(p.landmarks)} | url={url}")
    return filas


def _rango_main(filas):
    """Índices [ini, fin) de las paradas de main: desde la que abre main hasta la que abre contentinfo."""
    ini = next(i for i, f in enumerate(filas) if "('main'," in f)
    fin = next((i for i, f in enumerate(filas) if "('contentinfo'," in f), len(filas))
    return ini, fin


def validar() -> int:
    servidor, raiz = servir()
    try:
        with sync_playwright() as p:
            nav = SoloLocal(p.chromium.launch())
            datos = capturar_local(nav, f"{raiz}/original/", None)
            nav.close()
    finally:
        servidor.shutdown()
    capturado = json.loads((CAPTURA / "arbol_ax.json").read_text(encoding="utf-8"))
    a = _paradas(capturado, None)
    b = _paradas(datos["arbol"], f"{raiz}/original/")
    print(f"paradas: capturado {len(a)} · reproducción {len(b)} · título {datos['titulo']!r}")
    (ai, af), (bi, bf) = _rango_main(a), _rango_main(b)
    print(f"main: capturado paradas {ai + 1}-{af} · reproducción {bi + 1}-{bf}")
    main_igual = a[ai:af] == b[bi:bf]
    todo_igual = a == b
    print(f"main idéntico: {main_igual} · todo idéntico: {todo_igual}")
    for linea in difflib.unified_diff(a, b, "capturado 15-nov", "reproducción original", n=1, lineterm=""):
        print("  " + linea)
    snap_a = (CAPTURA / "aria_snapshot.txt").read_text(encoding="utf-8").splitlines()
    snap_b = datos["snapshot"].replace(f"{raiz}/original/", URL_CAPTURA).splitlines()
    print(f"aria snapshot idéntico (url local normalizada): {snap_a == snap_b}")
    for linea in difflib.unified_diff(snap_a, snap_b, "capturado", "reproducción", n=1, lineterm=""):
        print("  " + linea)
    return 0 if main_igual else 1


# ---------- medir ----------

def medir() -> None:
    palabras = cargar_palabras()
    servidor, raiz = servir()
    resumen = {}
    try:
        with sync_playwright() as p:
            for version in VERSIONES:
                url = f"{raiz}/{version}/"
                carpeta = BASE / "mediciones" / version
                nav = SoloLocal(p.chromium.launch())
                datos = capturar_local(nav, url, carpeta / "captura")
                todos = calcular_puntajes(datos["axe"])
                puntajes = {k: todos[k] for k in PUNTAJES}
                bloqueadas_axe = list(nav.bloqueadas)
                nav.bloqueadas.clear()
                abiertos = []

                def fabrica(entrada, nav=nav, abiertos=abiertos):
                    n = NavegadorEnVivo(nav)  # tiempos y pausa por omisión, como correr_sitio
                    abiertos.append(n)
                    return Emulador.en_vivo(n, entrada, tope_pulsaciones=TOPE_PULSACIONES,
                                            tope_navegaciones=TOPE_NAVEGACIONES)

                resultado = mejor_estrategia(fabrica, Tarea("A", url, None), palabras)
                for n in abiertos:
                    n.cerrar()
                veredicto = clasificar(resultado, OBJETIVO)
                fila = FilaAuditoria("A", url, None, OBJETIVO, None, True, url)
                reporte = ReporteSitio(f"atencion_{version}", raiz, datetime.now().astimezone().isoformat(
                    timespec="seconds"), palabras.version, (ResultadoFila(fila, veredicto, puntajes, None,
                                                                           resultado.captcha),))
                escribir_reporte(reporte, carpeta)
                estrategias = []
                for i in resultado.intentos:
                    ultimo = i.trayectoria[-1] if i.trayectoria else None
                    estrategias.append({
                        "estrategia": i.estrategia, "llego": i.llego, "pulsaciones": i.pulsaciones,
                        "correcto": hallazgo_correcto("A", i.hallazgo, OBJETIVO) if i.hallazgo else None,
                        "motivo": i.motivo, "no_evaluable": str(i.no_evaluable) if i.no_evaluable else None,
                        "trayectoria": resumir_trayectoria(i.trayectoria),
                        "ultimo_anuncio": ultimo.anuncio if ultimo else None,
                        "hallazgo": i.hallazgo})
                resumen[version] = {
                    "url": url, "titulo": datos["titulo"], "paradas": len(aplanar(datos["arbol"])),
                    "puntajes": puntajes, "conteos_axe": {k: v for k, v in todos.items() if k not in PUNTAJES},
                    "violaciones": sorted((r["id"], len(r["nodes"])) for r in datos["axe"]["violations"]),
                    "estado": veredicto.estado, "tipo_falla": veredicto.tipo_falla,
                    "mejor_estrategia": veredicto.estrategia, "friccion": veredicto.friccion,
                    "consumidas": veredicto.consumidas, "motivo": veredicto.motivo,
                    "sensibilidad": {str(u): e for u, e in veredicto.sensibilidad.items()},
                    "falsas_llegadas": [(x.estrategia, x.pulsaciones, x.encontro) for x in veredicto.falsas_llegadas],
                    "estrategias": estrategias,
                    "bloqueadas_axe": bloqueadas_axe, "bloqueadas_estrategias": list(nav.bloqueadas)}
                nav.close()
    finally:
        servidor.shutdown()
    (BASE / "mediciones" / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2,
                                                                 default=str), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paso", choices=("preparar", "validar", "medir"))
    paso = ap.parse_args().paso
    sys.exit({"preparar": preparar, "validar": validar, "medir": medir}[paso]() or 0)
