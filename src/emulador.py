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
# Roles interactivos que no son enlace (decidido 20-oct, Fase 3B): parada propia con su texto
# fundido, pero K NO se detiene en ellos (si una tarea depende de ellos con K, es barrera real
# del sitio). "option" suelta: Chromium no la expone como option (comprobado 20-oct); dentro
# de un listbox o un select ya queda fundida en el campo.
ROLES_INTERACTIVOS = {"tab", "menuitem", "menuitemcheckbox", "menuitemradio", "switch",
                      "option", "treeitem"}
# Paradas cuyo subárbol se funde en su nombre (no se baja a sus hijos).
ROLES_PARADA = {"heading", "link", "button", "image"} | ROLES_CAMPO | ROLES_INTERACTIVOS
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
    # Fase 3B. De estos, solo los estados van en el anuncio (la url nunca: el agente no ve
    # URLs).
    id_dom: int | None = None  # backendDOMNodeId: para hacer clic y reubicar el cursor
    url: str | None = None  # propiedad url del árbol (enlaces; menuitem no la trae)
    expandido: bool | None = None  # aria-expanded
    seleccionado: bool | None = None  # aria-selected (pestañas, elementos de árbol)


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
    """Paradas de la página en orden del documento (ver aplanar_pagina)."""
    return aplanar_pagina(arbol)[0]


def aplanar_pagina(arbol: dict) -> tuple[list[Parada], tuple[tuple[str, str], ...]]:
    """Lineariza el árbol CDP en paradas, en orden del documento (orden de childIds).
    Devuelve también los landmarks finales: los que quedaron sin ninguna parada después.

    - Nodo ignorado: no es parada, pero se baja a sus hijos (Chromium envuelve el contenido
      visible en nodos ignorados). Excepción: si lo oculta aria-hidden, se poda todo.
    - Rol de parada (ROLES_PARADA): una parada con el nombre que calculó Chromium; no se baja
      a sus hijos (el texto de adentro ya está en el nombre; las opciones de un select no
      son paradas aparte).
    - StaticText fuera de una parada, con nombre no vacío tras normalizar: texto suelto.
    - InlineTextBox y ListMarker: se descartan.
    - Cualquier otro rol (generic, paragraph, list, listitem, LabelText, form...): contenedor;
      si es landmark se anota en su primera parada.
    Landmark sin paradas adentro (3B): se anota en la SIGUIENTE parada, para que D lo cuente
    (limitación declarada: el anuncio lo combina con una parada que está fuera de él). Si es
    lo último del documento, queda en los landmarks finales. No se crea una parada vacía
    porque inflaría la fricción de flecha.
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
            id_dom=nodo.get("backendDOMNodeId"), url=_propiedad(nodo, "url"),
            expandido=_propiedad(nodo, "expanded"),
            seleccionado=_propiedad(nodo, "selected"),
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
                pendientes.append(marca)  # si queda vacío, pasa a la parada siguiente
                visitar_hijos(nodo)
                return
        visitar_hijos(nodo)

    def visitar_hijos(nodo):
        for hijo in nodo.get("childIds", []):
            if hijo in nodos:
                visitar(nodos[hijo])

    visitar(raiz)
    return paradas, tuple(pendientes)


# ---------- Anuncio ----------
# Redacción propia, inspirada en NVDA en español; no es su texto literal.
ROTULOS = {
    "link": "enlace", "button": "botón", "image": "gráfico", "textbox": "edición",
    "searchbox": "cuadro de búsqueda", "combobox": "cuadro combinado",
    "checkbox": "casilla de verificación", "radio": "botón de opción", "listbox": "lista",
    "spinbutton": "selector numérico", "date": "campo de fecha",
    "DateTime": "campo de fecha y hora", "InputTime": "campo de hora",
    "tab": "pestaña", "menuitem": "elemento de menú",
    "menuitemcheckbox": "elemento de menú de verificación",
    "menuitemradio": "elemento de menú de opción", "switch": "conmutador",
    "option": "opción", "treeitem": "elemento de árbol",
}
# Roles en los que se anuncia "contraído" / "expandido" (los que Enter expande en la misma
# página). No combobox: NVDA sí lo diría, pero Enter no abre campos y así no cambia el
# anuncio de 3A. Limitación: no se anuncia el estado marcado de switch ni de menuitemcheckbox.
ROLES_EXPANDIBLES = {"button", "link", "menuitem"}
ROTULOS_LANDMARK = {
    "banner": "banner", "navigation": "navegación", "main": "principal",
    "contentinfo": "información de contenido", "complementary": "complementario",
    "search": "búsqueda", "region": "región", "form": "formulario",
}
# Decisión D1 (aprobada 20-oct): si no hay siguiente, el cursor no se mueve ni da la vuelta
# al inicio (NVDA por omisión no da la vuelta; JAWS sí), se anuncia esto y la pulsación
# CUENTA: la persona sí presionó la tecla y así descubre que no hay más.
SIN_SIGUIENTE = {
    "H": "no hay más encabezados", "K": "no hay más enlaces",
    "D": "no hay más puntos de referencia", "F": "no hay más campos de formulario",
    "Tab": "fin de los elementos enfocables", "flecha": "fin del documento",
    "leer": "fin del documento",
}
# Qué paradas alcanza cada tecla de salto (D va aparte: salta por landmarks).
FILTROS = {
    "H": lambda p: p.rol == "heading",
    "K": lambda p: p.rol == "link",
    "F": lambda p: p.rol in ROLES_F,
    # Tab solo llega a enfocables. Limitación: el árbol marca enfocable también lo que
    # tiene tabindex="-1", al que el Tab real no llega (comprobado en casos_emulador).
    # Pestañas (patrón ARIA): Tab solo se detiene en la seleccionada; las demás, con flecha.
    "Tab": lambda p: p.enfocable and (p.rol != "tab" or p.seleccionado is True),
    "flecha": lambda p: True,
    "leer": lambda p: True,
}
ELEMENTOS = {"enlaces": "link", "encabezados": "heading"}


def anuncio(parada: Parada | None, landmark: tuple[str, str] | None = None) -> str:
    """Rol + nombre (+ estado) de la parada; el texto suelto se anuncia solo con su texto.
    Con D se antepone el landmark al que se llegó. parada=None: landmark final vacío, se
    anuncia solo el landmark."""
    base = None
    if parada is not None and parada.rol == TEXTO:
        base = parada.nombre
    elif parada is not None:
        if parada.rol == "heading":
            rotulo = f"encabezado nivel {parada.nivel}" if parada.nivel else "encabezado"
        else:
            rotulo = ROTULOS.get(parada.rol, parada.rol)
        partes = [rotulo] + ([parada.nombre] if parada.nombre else [])
        if parada.rol == "tab" and parada.seleccionado:
            partes.append("seleccionada")
        if parada.rol in ROLES_EXPANDIBLES and parada.expandido is not None:
            partes.append("expandido" if parada.expandido else "contraído")
        base = ", ".join(partes)
    if landmark:
        rol, nombre = landmark
        marca = ROTULOS_LANDMARK[rol] + (f" {nombre}" if nombre else "")
        return f"{marca}, punto de referencia" + (f"; {base}" if base is not None else "")
    return base


@dataclass(frozen=True)
class Paso:
    tecla: str  # "H", "K", "D", "F", "Tab", "flecha" o "leer"
    anuncio: str  # lo que se anunciaría
    parada: int | None  # dónde quedó el cursor (None = sigue antes de la primera)
    se_movio: bool  # False si no había siguiente (D1)
    pulsaciones: int  # acumuladas después de este paso
    landmark: tuple[str, str] | None = None  # solo con D: landmark al que se llegó


# ---------- Fase 3B: límites y errores ----------

# Profundidad máxima desde el punto de entrada (nivel 0). Es el tamaño de la pila de páginas,
# no el número de páginas visitadas: ir y volver no acumula.
PROFUNDIDAD_MAX = 3


class AccionNoPermitida(Exception):
    """Enter sobre algo que no se debe activar (campo, botón que podría enviar un formulario,
    encabezado, texto) o con el cursor antes de la primera parada. No se ejecuta ni cuenta:
    es un error de quien llama (estrategia o agente), no una pulsación de la persona."""


class SesionTerminada(Exception):
    """Se pulsó una tecla después de que la tarea quedó No evaluable."""


# ---------- Entorno ----------

class Emulador:
    """Entorno: un cursor sobre las paradas de una página ya capturada.

    Cada tecla cuesta 1 pulsación y queda en la trayectoria (reproducible: mismas teclas
    sobre el mismo árbol dan la misma trayectoria). Enter, volver y la navegación entre
    páginas son de la Fase 3B; el costo de la lista de elementos y de elegir en ella, de 3C.
    """

    def __init__(self, paradas: list[Parada], landmarks_finales=()):
        self.paradas = paradas
        self.cursor = -1  # antes de la primera parada
        self.pulsaciones = 0
        self.trayectoria: list[Paso] = []
        # Para D: todos los pares (parada, landmark) en orden. Varios pueden compartir parada.
        # Los landmarks finales vacíos van con índice len(paradas): D los anuncia sin mover.
        self._marcas = [(p.indice, lm) for p in paradas for lm in p.landmarks]
        self._marcas += [(len(paradas), lm) for lm in landmarks_finales]
        self._marca = -1  # último par al que llegó D (-1 si el cursor se movió con otra tecla)

    @classmethod
    def desde_archivo(cls, ruta_arbol: Path) -> "Emulador":
        arbol = json.loads(Path(ruta_arbol).read_text(encoding="utf-8"))
        return cls(*aplanar_pagina(arbol))

    def _registrar(self, tecla, texto, se_movio, landmark=None) -> Paso:
        self.pulsaciones += 1
        paso = Paso(tecla, texto, self.cursor if self.cursor >= 0 else None,
                    se_movio, self.pulsaciones, landmark)
        self.trayectoria.append(paso)
        return paso

    def pulsar(self, tecla: str) -> Paso:
        """Una pulsación: H, K, D, F, Tab o flecha (abajo). Siempre avanza hacia adelante."""
        if tecla == "D":
            return self._pulsar_D()
        if tecla not in FILTROS or tecla == "leer":
            raise ValueError(f"Tecla no soportada en 3A: {tecla}")
        return self._saltar(tecla)

    def _saltar(self, tecla) -> Paso:
        filtro = FILTROS[tecla]
        destino = next((p for p in self.paradas[self.cursor + 1:] if filtro(p)), None)
        if destino is None:
            return self._registrar(tecla, SIN_SIGUIENTE[tecla], se_movio=False)
        self.cursor = destino.indice
        self._marca = -1
        return self._registrar(tecla, anuncio(destino), se_movio=True)

    def _pulsar_D(self) -> Paso:
        # Si el cursor sigue donde lo dejó D (ninguna otra tecla lo movió), se continúa desde
        # ese par (así los landmarks que empiezan en la misma parada cuestan una pulsación
        # cada uno); si no, desde el primer landmark que empieza después del cursor.
        if self._marca >= 0:
            inicio = self._marca + 1
        else:
            inicio = next((i for i, (j, _) in enumerate(self._marcas) if j > self.cursor),
                          len(self._marcas))
        if inicio >= len(self._marcas):
            return self._registrar("D", SIN_SIGUIENTE["D"], se_movio=False)
        self._marca = inicio
        indice, landmark = self._marcas[inicio]
        if indice == len(self.paradas):
            # Landmark final vacío: se anuncia sin mover el cursor y la pulsación cuenta 1.
            return self._registrar("D", anuncio(None, landmark), se_movio=False,
                                   landmark=landmark)
        self.cursor = indice
        return self._registrar("D", anuncio(self.paradas[indice], landmark),
                               se_movio=True, landmark=landmark)

    def leer_de_corrido(self, n: int | None = None) -> list[Paso]:
        """Lee n paradas desde el cursor; cada una cuesta 1 (como flecha abajo). Con n=None
        lee hasta la última parada, sin pulsar de más. Si n pasa del final, las pulsaciones
        sobrantes cuentan y no mueven (D1)."""
        if n is None:
            n = len(self.paradas) - 1 - self.cursor
        return [self._saltar("leer") for _ in range(n)]

    def lista_elementos(self, tipo: str) -> list[Parada]:
        """Lista de elementos (NVDA+F7): "enlaces" o "encabezados", en orden del documento.
        No mueve el cursor ni suma pulsaciones: su costo se define en la Fase 3C."""
        rol = ELEMENTOS[tipo]
        return [p for p in self.paradas if p.rol == rol]
