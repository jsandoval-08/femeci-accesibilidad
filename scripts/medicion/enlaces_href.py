"""Medición (solo lectura): ¿a dónde lleva cada enlace que el emulador ve como parada?

Sirvió para decidir, el 20-oct (antes del paso 4 de la Fase 3B), si Enter en enlace puede
navegar abriendo la URL del enlace en una pestaña nueva (una por nivel) en vez de hacer clic.
Ese diseño solo funciona con enlaces que tienen una URL navegable; los que dependen de
JavaScript (javascript:, "#" solo, sin URL) caen en "clic en la misma página".

Qué cuenta, por sitio, sobre las paradas de rol link y menuitem (src/emulador.aplanar: fuera
de aria-hidden y solo lo visible en el estado inicial, sin expandir menús):
  navegable        http(s) a OTRO documento
  frag_destino     "#id" de la misma página y el id existe (p. ej. "Saltar al contenido")
  frag_sin_dest    "#algo" de la misma página sin ese id (rutas de SPA con "#/..." o roto)
  solo_#           href="#" (la url termina en "#"): depende de JavaScript
  misma_pagina     la misma página sin "#" (logo o "Inicio" en la portada): recarga, es
                   navegación real
  javascript       javascript:...
  otro_esquema     mailto:, tel:, etc. (Enter abriría otra aplicación)
  sin_url          el árbol no trae url (role="link" sin href, o menuitem)
  con_expanded     de todos los anteriores, cuántos tienen aria-expanded (Enter los expande)
Aparte, en el HTML renderizado: <a> sin href (no son enlaces en el árbol: K no los ve).

Capturas usadas: las mismas 5 portadas del 5-oct que roles_fuera.py (capturas/ no está en el
repositorio; para repetir hay que volver a capturar y el resultado puede cambiar).

Uso: python scripts/medicion/enlaces_href.py [carpeta_de_captura ...]
"""

import collections
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from scripts.medicion.roles_fuera import CAPTURAS_5_OCT  # noqa: E402
from src.emulador import aplanar  # noqa: E402

COLUMNAS = ["navegable", "misma_pagina", "frag_destino", "frag_sin_dest", "solo_#",
            "javascript", "otro_esquema", "sin_url"]


class _Html(HTMLParser):
    """Junta los id/name del documento y cuenta los <a> sin href."""

    def __init__(self):
        super().__init__()
        self.ids = set()
        self.a_sin_href = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for clave in ("id", "name"):
            if attrs.get(clave):
                self.ids.add(attrs[clave])
        if tag == "a" and "href" not in attrs:
            self.a_sin_href += 1


def clasificar(url: str | None, url_pagina: str, ids: set) -> str:
    if not url:
        return "sin_url"
    esquema = urlparse(url).scheme.lower()
    if esquema == "javascript":
        return "javascript"
    if esquema not in ("http", "https"):
        return "otro_esquema"
    destino, fragmento = urldefrag(url)
    if destino != urldefrag(url_pagina)[0]:
        return "navegable"
    if not fragmento:
        # urldefrag no distingue "pagina#" de "pagina": se mira el texto de la url.
        return "solo_#" if url.endswith("#") else "misma_pagina"
    return "frag_destino" if fragmento in ids else "frag_sin_dest"


def medir(carpeta: Path) -> dict:
    arbol = json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8"))
    meta = json.loads((carpeta / "metadatos.json").read_text(encoding="utf-8"))
    html = _Html()
    html.feed((carpeta / "pagina.html").read_text(encoding="utf-8"))
    cuenta = collections.Counter()
    ejemplos = {}
    for p in aplanar(arbol):
        if p.rol not in ("link", "menuitem"):
            continue
        clase = clasificar(p.url, meta["url_final"], html.ids)
        cuenta[clase] += 1
        cuenta["total"] += 1
        cuenta["con_expanded"] += p.expandido is not None
        if clase != "navegable" and clase not in ejemplos:
            ejemplos[clase] = f"{p.nombre[:30]!r} -> {(p.url or '')[:50]}"
    cuenta["a_sin_href"] = html.a_sin_href
    return {"cuenta": cuenta, "ejemplos": ejemplos}


def main() -> None:
    carpetas = [Path(a) for a in sys.argv[1:]] or [RAIZ / "capturas" / c for c in CAPTURAS_5_OCT]
    cabecera = ["sitio", "total"] + COLUMNAS + ["con_expanded", "a_sin_href"]
    print(" | ".join(cabecera))
    todos = collections.Counter()
    ejemplos = []
    for carpeta in carpetas:
        if not (carpeta / "arbol_ax.json").exists():
            print(f"### NO EXISTE: {carpeta}")
            continue
        sitio = carpeta.parts[-2].rsplit("_", 1)[0]
        r = medir(carpeta)
        todos.update(r["cuenta"])
        print(" | ".join([sitio] + [str(r["cuenta"][c]) for c in cabecera[1:]]))
        ejemplos += [f"  {sitio} {clase}: {ej}" for clase, ej in r["ejemplos"].items()]
    print(" | ".join(["TOTAL"] + [str(todos[c]) for c in cabecera[1:]]))
    print("Ejemplos (primer caso no navegable de cada clase):")
    print("\n".join(ejemplos))


if __name__ == "__main__":
    main()
