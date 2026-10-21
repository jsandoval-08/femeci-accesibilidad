"""Emulador simplificado de lector de pantalla (Fase 3A): determinista, sin IA y sin red.

Opera sobre un arbol_ax.json ya capturado (CDP Accessibility.getFullAXTree). Está INSPIRADO
en los comandos de NVDA en modo exploración, pero NO es equivalente a NVDA. Límites
declarados (ver CLAUDE.md): no reproduce modo foco/exploración, no lee iframes, no anuncia
aria-live, no lee contenido de PDFs, no modela el control de foco de modales.

Parada = cada parada de flecha abajo: encabezado, enlace, botón, campo de formulario,
imagen (con o sin nombre) y texto suelto. El texto dentro de una parada se funde en su
nombre. Limitación D3: 1 StaticText = 1 parada (un párrafo con un enlace en medio son 3
paradas; un párrafo largo es 1 aunque NVDA lo parta en varias líneas).
"""

import json
from dataclasses import dataclass
from pathlib import Path

# Campos de formulario (CLAUDE.md). Roles tal como los nombra Chromium en el árbol CDP.
ROLES_CAMPO = {"textbox", "searchbox", "combobox", "checkbox", "radio", "listbox",
               "spinbutton", "date", "DateTime", "InputTime"}
# Tecla F (D2): cualquier campo de formulario, incluidos los botones, como en NVDA
# (por verificar en NVDA). Configurable.
ROLES_F = ROLES_CAMPO | {"button"}
# Paradas cuyo subárbol se funde en su nombre (no se baja a sus hijos).
ROLES_PARADA = {"heading", "link", "button", "image"} | ROLES_CAMPO
TEXTO = "StaticText"
# Nodos que nunca son parada ni aportan texto propio: las cajas de texto internas de
# Chromium y la viñeta de los elementos de lista (se lee junto con su elemento).
ROLES_DESCARTADOS = {"InlineTextBox", "ListMarker"}

# Landmarks (tecla D). region y form solo cuentan si tienen nombre (regla de ARIA).
LANDMARKS = {"banner", "navigation", "main", "contentinfo", "complementary", "search"}
LANDMARKS_CON_NOMBRE = {"region", "form"}

# Chromium marca así los nodos ocultos con aria-hidden (el propio y su subárbol).
RAZONES_ARIA_HIDDEN = {"ariaHiddenElement", "ariaHiddenSubtree"}


@dataclass(frozen=True)
class Parada:
    indice: int  # posición en orden del documento (0 = primera)
    rol: str  # rol CDP: heading, link, button, textbox, image, StaticText...
    nombre: str  # normalizado; "" si no tiene
    nivel: int | None  # solo en encabezados
    enfocable: bool  # propiedad focusable del árbol
    # Landmarks (rol, nombre) que EMPIEZAN en esta parada, de afuera hacia adentro. Es una
    # tupla y no un sí/no porque dos landmarks pueden empezar en la misma parada (main y la
    # primera región), y en NVDA eso son dos pulsaciones de D.
    landmarks: tuple[tuple[str, str], ...]
    id_nodo: str  # nodeId CDP, para rastrear la parada en el árbol


def normalizar(texto: str) -> str:
    """Quita espacios al inicio y al final y colapsa los repetidos (incluye tabuladores y
    espacios no separables, que str.split() también reconoce como espacio)."""
    return " ".join(texto.split())


def _propiedad(nodo: dict, nombre: str):
    for p in nodo.get("properties", []):
        if p["name"] == nombre:
            return p["value"].get("value")
    return None


def _es_aria_hidden(nodo: dict) -> bool:
    return any(r["name"] in RAZONES_ARIA_HIDDEN for r in nodo.get("ignoredReasons", []))


def _landmark(rol: str, nombre: str) -> tuple[str, str] | None:
    if rol in LANDMARKS or (rol in LANDMARKS_CON_NOMBRE and nombre):
        return (rol, nombre)
    return None


def aplanar(arbol: dict) -> list[Parada]:
    """Lineariza el árbol CDP en paradas, en orden del documento (orden de childIds).

    - Nodo ignorado: no es parada, pero se baja a sus hijos (Chromium envuelve el contenido
      visible en nodos ignorados). Excepción: si lo oculta aria-hidden, se poda todo.
    - Rol de parada (ROLES_PARADA): una parada con el nombre que calculó Chromium; no se baja
      a sus hijos (el texto de adentro ya está en el nombre; las opciones de un select no
      son paradas aparte).
    - StaticText fuera de una parada, con nombre no vacío tras normalizar: texto suelto.
    - InlineTextBox y ListMarker: se descartan.
    - Cualquier otro rol (generic, paragraph, list, listitem, LabelText, form...): contenedor;
      si es landmark se anota en su primera parada.
    Limitación: un landmark sin ninguna parada adentro no se registra (D no llega a él).
    """
    nodos = {n["nodeId"]: n for n in arbol["nodes"]}
    raiz = next(n for n in arbol["nodes"] if "parentId" not in n)
    paradas: list[Parada] = []
    pendientes: list[tuple[str, str]] = []  # landmarks abiertos que aún no tienen parada

    def nueva(nodo, rol, nombre):
        nivel = _propiedad(nodo, "level") if rol == "heading" else None
        paradas.append(Parada(
            indice=len(paradas), rol=rol, nombre=nombre, nivel=nivel,
            enfocable=bool(_propiedad(nodo, "focusable")),
            landmarks=tuple(pendientes), id_nodo=nodo["nodeId"],
        ))
        pendientes.clear()

    def visitar(nodo):
        if nodo.get("ignored"):
            if _es_aria_hidden(nodo):
                return
        else:
            rol = nodo["role"]["value"]
            nombre = normalizar(nodo.get("name", {}).get("value") or "")
            if rol in ROLES_DESCARTADOS:
                return
            if rol in ROLES_PARADA:
                nueva(nodo, rol, nombre)
                return
            if rol == TEXTO:
                if nombre:
                    nueva(nodo, rol, nombre)
                return
            marca = _landmark(rol, nombre)
            if marca:
                pendientes.append(marca)
                visitar_hijos(nodo)
                if marca in pendientes:  # landmark vacío: no se arrastra a la parada siguiente
                    pendientes.remove(marca)
                return
        visitar_hijos(nodo)

    def visitar_hijos(nodo):
        for hijo in nodo.get("childIds", []):
            if hijo in nodos:
                visitar(nodos[hijo])

    visitar(raiz)
    return paradas


class Emulador:
    """Entorno: un cursor sobre las paradas de una página ya capturada."""

    def __init__(self, paradas: list[Parada]):
        self.paradas = paradas
        self.cursor = -1  # antes de la primera parada

    @classmethod
    def desde_archivo(cls, ruta_arbol: Path) -> "Emulador":
        arbol = json.loads(Path(ruta_arbol).read_text(encoding="utf-8"))
        return cls(aplanar(arbol))
