"""Diagnóstico POSTERIOR a las corridas: reproduce cada estrategia SIN RED sobre una captura guardada
(árbol de axe de la entrada), para explicar dónde se detuvo cada una. No altera veredictos ni
resultados oficiales: no escribe nada, no cambia src/ ni las palabras clave, y lo que imprime no entra
a estudio/, al análisis ni a interfaz/datos.js.

Uso: python scripts/reproducir.py <carpeta_captura> <tarea> <tramite o -> [objetivo_correcto]
Ejemplo: python scripts/reproducir.py estudio/corridas/2026-11-15/culiacan/capturas/<host>/<fecha> A - "info@culiacan.gob.mx|(667) 7580101"
Validado el 15-nov: Culiacán A Tab_inicio = 41 y navolato A no_dirigida = 138, igual que en vivo.

Navegador sustituto: abrir() sirve el árbol guardado; cualquier otra cosa que pediría red
(Enter que navega, clic en la misma página, "#id") devuelve Falla("no_capturada"): esa estrategia
termina ahí. Es un artefacto de la reproducción, no un resultado del sitio. La captura es la de axe,
no la que vieron las estrategias en vivo: puede diferir si la página cambia entre cargas.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emulador import Emulador, Falla, Pagina  # noqa: E402
from src.estrategias import ESTRATEGIAS, SOLO_TAREA_D, Tarea, cargar_palabras, correr  # noqa: E402
from src.sitio import TOPE_NAVEGACIONES, TOPE_PULSACIONES  # noqa: E402
from src.veredicto import hallazgo_correcto  # noqa: E402


class NavegadorSinRed:
    def __init__(self, carpeta: Path):
        meta = json.loads((carpeta / "metadatos.json").read_text(encoding="utf-8"))
        html = (carpeta / "pagina.html").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        self.pagina = Pagina(meta["url"], meta["url_final"], meta["estado_http"],
                             (m.group(1).strip() if m else ""),
                             json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8")))
        self.pedidas = []

    def abrir(self, url):
        return self.pagina

    def navegar(self, parada):
        self.pedidas.append(("navegar", parada.nombre, parada.url))
        return Falla("no_capturada", f"Enter en '{parada.nombre}' -> {parada.url} (sin red)")

    def activar_en_sitio(self, parada):
        self.pedidas.append(("clic", parada.nombre, parada.url))
        return Falla("no_capturada", f"clic en '{parada.nombre}' (sin red)")

    def ubicar_fragmento(self, fragmento, paradas):
        return None  # sin DOM vivo: cae en activar_en_sitio -> no_capturada

    def volver(self):
        pass


def main():
    carpeta, letra = Path(sys.argv[1]), sys.argv[2]
    tramite = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    objetivo = sys.argv[4] if len(sys.argv) > 4 else None
    palabras = cargar_palabras()
    navs = []

    def fabrica(entrada):
        nav = NavegadorSinRed(carpeta)
        navs.append(nav)
        return Emulador.en_vivo(nav, entrada, tope_pulsaciones=TOPE_PULSACIONES,
                                tope_navegaciones=TOPE_NAVEGACIONES)

    nav0 = NavegadorSinRed(carpeta)
    emu0 = Emulador.en_vivo(nav0, nav0.pagina.url)
    print(f"Página: {nav0.pagina.url} · título: {nav0.pagina.titulo!r} · paradas: {len(emu0.paradas)}")
    for p in emu0.paradas:
        if p.landmarks:
            print(f"  landmark(s) en parada {p.indice + 1}: {p.landmarks}")
    tarea = Tarea(letra, nav0.pagina.url, tramite)
    print()
    for clave in ESTRATEGIAS:
        if clave in SOLO_TAREA_D and letra != "D":
            continue
        i = correr(clave, fabrica, tarea, palabras)
        ultimo = i.trayectoria[-1] if i.trayectoria else None
        correcto = (hallazgo_correcto(letra, i.hallazgo, objetivo)
                    if (i.hallazgo and objetivo) else None)
        print(f"{clave:24s} llegó={i.llego!s:5s} correcto={correcto!s:5s} pulsaciones={i.pulsaciones:4d}"
              f" motivo={i.motivo}")
        print(f"   último paso: {ultimo.tecla if ultimo else '-'} -> "
              f"{(ultimo.anuncio if ultimo else '')[:110]!r}")
        if i.hallazgo:
            print(f"   hallazgo: {str(i.hallazgo)[:160]}")
        if navs[-1].pedidas:
            print(f"   pediría red: {navs[-1].pedidas}")


if __name__ == "__main__":
    main()
