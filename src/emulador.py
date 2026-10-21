"""Emulador simplificado de lector de pantalla (Fases 3A y 3B): determinista y sin IA.

Opera sobre árboles de accesibilidad (CDP Accessibility.getFullAXTree): uno ya capturado
(3A, sin red) o los que va recapturando un navegador en vivo (3B, src/navegador.py; el
emulador decide y cuenta, el navegador solo ejecuta). Está INSPIRADO
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
from urllib.parse import urldefrag, urlparse

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
    # "H", "K", "D", "F", "Tab", "flecha", "leer", "Enter", "volver", "lista_enlaces",
    # "lista_encabezados", "flecha_lista" o "entrada" (solo si falla la carga inicial)
    tecla: str
    anuncio: str  # lo que se anunciaría
    parada: int | None  # dónde quedó el cursor (None = sigue antes de la primera)
    se_movio: bool  # False si no había siguiente (D1) o si el cursor no cambió de lugar
    pulsaciones: int  # acumuladas después de este paso
    landmark: tuple[str, str] | None = None  # solo con D: landmark al que se llegó
    # Fase 3B (para la evidencia y el veredicto de 3D):
    profundidad: int = 0  # nivel de la página donde quedó el cursor (entrada = 0)
    url: str | None = None  # página donde quedó el cursor (nunca se le da al agente)
    estado_http: int | None = None  # solo al llegar a una página
    captcha: tuple[str, ...] = ()  # marcadores de CAPTCHA de la página a la que se llegó
    documento: "Documento | None" = None  # solo si Enter descargó un documento
    no_evaluable: str | None = None  # motivo, si este paso dejó la tarea No evaluable


# ---------- Fase 3B: límites, errores y resultados del navegador ----------

# Profundidad máxima desde el punto de entrada (nivel 0). Es el tamaño de la pila de páginas,
# no el número de páginas visitadas: ir y volver no acumula.
PROFUNDIDAD_MAX = 3


class AccionNoPermitida(Exception):
    """Enter sobre algo que no se debe activar (campo, botón que podría enviar un formulario,
    encabezado, texto) o con el cursor antes de la primera parada. No se ejecuta ni cuenta:
    es un error de quien llama (estrategia o agente), no una pulsación de la persona."""


class SesionTerminada(Exception):
    """Se pulsó una tecla después de que la tarea quedó No evaluable."""


@dataclass(frozen=True)
class NoEvaluable:
    """Por qué la tarea no se pudo evaluar. NUNCA cuenta como no completable (CLAUDE.md).
    motivo: timeout | profundidad | tope_pulsaciones | falla_tecnica. El CAPTCHA no detiene
    la sesión (decisión 20-oct): se registra y la regla se aplica en 3D."""
    motivo: str
    detalle: str
    pulsaciones: int  # consumidas hasta detenerse


@dataclass(frozen=True)
class Documento:
    """Lo que se descargó al activar un enlace (tarea C). Hechos medidos, no veredicto."""
    url: str
    tipo_contenido: str
    es_pdf: bool  # los bytes empiezan con %PDF-
    capa_texto: bool | None  # None = no medido (no es PDF o no se pudo leer)
    paginas: int | None
    caracteres: int | None  # caracteres no blancos del texto extraído
    error: str | None = None


@dataclass(frozen=True)
class Pagina:
    """Una página cargada por el navegador: su árbol recién capturado y datos de la carga."""
    url_pedida: str
    url: str  # URL final (después de redirecciones)
    estado_http: int | None
    titulo: str
    arbol: dict
    captcha: tuple[str, ...] = ()  # marcadores de CAPTCHA detectados (heurística)
    nueva_pestana: bool = True  # False si el navegador tuvo que hacer clic en la misma pestaña


@dataclass(frozen=True)
class Falla:
    """El navegador no pudo cargar: motivo = timeout | falla_tecnica."""
    motivo: str
    detalle: str


# Enter en un enlace (rol link o menuitem) según su URL. Medido el 20-oct en las 5 portadas
# (scripts/medicion/enlaces_href.py): 150 de 164 enlaces tienen URL navegable.
ESQUEMAS_NAVEGABLES = {"http", "https", "file"}
ROLES_ENLACE = {"link", "menuitem"}


@dataclass
class Vista:
    """Una página del historial: su árbol aplanado y dónde estaba el cursor. Al volver se
    reusa tal cual (no se recaptura)."""
    paradas: list[Parada]
    landmarks_finales: tuple = ()
    url: str | None = None
    titulo: str = ""
    estado_http: int | None = None
    captcha: tuple[str, ...] = ()
    cursor: int = -1  # antes de la primera parada
    marca: int = -1  # último par (parada, landmark) al que llegó D; -1 si otra tecla movió
    marcas: list = None  # todos los pares (parada, landmark) en orden, para D

    def __post_init__(self):
        # Varios landmarks pueden compartir parada. Los finales vacíos van con índice
        # len(paradas): D los anuncia sin mover el cursor.
        self.marcas = [(p.indice, lm) for p in self.paradas for lm in p.landmarks]
        self.marcas += [(len(self.paradas), lm) for lm in self.landmarks_finales]


TECLAS = {"H", "K", "D", "F", "Tab", "flecha", "Enter", "volver"}


# ---------- Entorno ----------

class Emulador:
    """Entorno: un cursor sobre las paradas de una página, con historial de páginas.

    Cada tecla cuesta 1 pulsación y queda en la trayectoria (reproducible: mismas teclas
    sobre el mismo árbol dan la misma trayectoria). El emulador decide qué hace cada tecla y
    cuenta; un navegador (src/navegador.py) solo ejecuta lo que necesita red. Sin navegador
    funciona sobre un árbol ya capturado (Fase 3A).

    Tope de pulsaciones (opcional): con tope N se ejecutan N pulsaciones; la N+1 no se
    ejecuta y la tarea queda No evaluable con N consumidas. No tiene valor por omisión: se
    fija con criterio escrito antes del estudio (CLAUDE.md).
    """

    def __init__(self, paradas: list[Parada], landmarks_finales=(), navegador=None,
                 url=None, titulo="", estado_http=None, captcha=(),
                 tope_pulsaciones: int | None = None):
        self.navegador = navegador
        self.tope_pulsaciones = tope_pulsaciones
        self.pulsaciones = 0
        self.trayectoria: list[Paso] = []
        self.no_evaluable: NoEvaluable | None = None
        # Pila de páginas: [entrada, ..., actual]. La profundidad es su tamaño menos 1.
        self._historial = [Vista(paradas, tuple(landmarks_finales), url, titulo,
                                 estado_http, tuple(captcha))]

    @classmethod
    def desde_archivo(cls, ruta_arbol: Path) -> "Emulador":
        arbol = json.loads(Path(ruta_arbol).read_text(encoding="utf-8"))
        return cls(*aplanar_pagina(arbol))

    # La página actual es la última de la pila; estas propiedades conservan la interfaz de 3A.
    @property
    def vista(self) -> Vista:
        return self._historial[-1]

    @property
    def paradas(self) -> list[Parada]:
        return self.vista.paradas

    @property
    def cursor(self) -> int:
        return self.vista.cursor

    @cursor.setter
    def cursor(self, valor: int):
        self.vista.cursor = valor

    @property
    def _marcas(self) -> list:
        return self.vista.marcas

    @property
    def _marca(self) -> int:
        return self.vista.marca

    @_marca.setter
    def _marca(self, valor: int):
        self.vista.marca = valor

    @property
    def profundidad(self) -> int:
        return len(self._historial) - 1

    @property
    def url(self) -> str | None:
        return self.vista.url

    @property
    def titulo(self) -> str:
        return self.vista.titulo

    @property
    def captcha(self) -> tuple[str, ...]:
        return self.vista.captcha

    # ---------- Registro, tope y No evaluable ----------

    def _registrar(self, tecla, texto, se_movio, landmark=None, **extra) -> Paso:
        """Una pulsación ejecutada: cuenta 1 y queda en la trayectoria."""
        self.pulsaciones += 1
        return self._anotar(tecla, texto, se_movio, landmark, **extra)

    def _anotar(self, tecla, texto, se_movio, landmark=None, **extra) -> Paso:
        paso = Paso(tecla, texto, self.cursor if self.cursor >= 0 else None, se_movio,
                    self.pulsaciones, landmark, profundidad=self.profundidad, url=self.url,
                    **extra)
        self.trayectoria.append(paso)
        return paso

    def _terminar(self, tecla, motivo, detalle, contada=False, **extra) -> Paso:
        """Deja la tarea No evaluable. contada=True si la tecla sí se ejecutó (p. ej. el
        Enter que dio timeout); el paso final registra el motivo y las pulsaciones."""
        if contada:
            self.pulsaciones += 1
        paso = self._anotar(tecla, f"no evaluable: {motivo}", False, no_evaluable=motivo,
                            **extra)
        self.no_evaluable = NoEvaluable(motivo, detalle, self.pulsaciones)
        return paso

    def _verificar_sesion(self):
        if self.no_evaluable:
            raise SesionTerminada(f"la tarea ya es No evaluable ({self.no_evaluable.motivo})")

    def _tope_alcanzado(self, tecla) -> Paso | None:
        """Si ya se gastó el tope, la tecla no se ejecuta y la tarea queda No evaluable."""
        if self.tope_pulsaciones is not None and self.pulsaciones >= self.tope_pulsaciones:
            return self._terminar(tecla, "tope_pulsaciones",
                                  f"tope de {self.tope_pulsaciones} pulsaciones")
        return None

    # ---------- Teclas ----------

    def pulsar(self, tecla: str) -> Paso:
        """Una pulsación: H, K, D, F, Tab, flecha (abajo), Enter o volver (Alt+←). Las de
        salto siempre avanzan hacia adelante."""
        self._verificar_sesion()
        if tecla not in TECLAS:
            raise ValueError(f"Tecla no soportada: {tecla}")
        if tecla == "Enter":
            accion = self._accion_enter()  # valida ANTES de contar: lo no permitido no cuenta
        if fin := self._tope_alcanzado(tecla):
            return fin
        if tecla == "D":
            return self._pulsar_D()
        if tecla == "Enter":
            return self._enter(accion)
        if tecla == "volver":
            return self._volver()
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
        sobrantes cuentan y no mueven (D1). Si se alcanza el tope, se detiene ahí."""
        self._verificar_sesion()
        if n is None:
            n = len(self.paradas) - 1 - self.cursor
        pasos = []
        for _ in range(n):
            if fin := self._tope_alcanzado("leer"):
                pasos.append(fin)
                break
            pasos.append(self._saltar("leer"))
        return pasos

    def lista_elementos(self, tipo: str) -> list[Parada]:
        """Lista de elementos (NVDA+F7): "enlaces" o "encabezados", en orden del documento.
        Solo consulta: no mueve el cursor ni suma pulsaciones (para eso, elegir_de_lista)."""
        rol = ELEMENTOS[tipo]
        return [p for p in self.paradas if p.rol == rol]

    def elegir_de_lista(self, tipo: str, posicion: int) -> list[Paso]:
        """Abre la lista de elementos (1 pulsación) y baja con flecha hasta `posicion`
        (0 = el primero): 1 + posicion pulsaciones, una por paso (CLAUDE.md). La lista abre
        en el primer elemento, en orden del documento, sin filtrar escribiendo (por verificar
        en NVDA: si abre en el más cercano al cursor). El cursor sigue a la selección; el
        Enter que activa el elemento es otra pulsación. Elegir QUÉ posición (por nombre,
        probando los ambiguos) es de las estrategias (3C), no del emulador."""
        self._verificar_sesion()
        elementos = self.lista_elementos(tipo)
        if not 0 <= posicion < len(elementos):
            raise IndexError(f"La lista de {tipo} tiene {len(elementos)} elementos")
        pasos = []
        for i, parada in enumerate(elementos[:posicion + 1]):
            tecla = f"lista_{tipo}" if i == 0 else "flecha_lista"
            if fin := self._tope_alcanzado(tecla):
                pasos.append(fin)
                break
            self.cursor = parada.indice
            self._marca = -1
            pasos.append(self._registrar(tecla, anuncio(parada), se_movio=True))
        return pasos

    # ---------- Enter y volver (Fase 3B) ----------

    def _accion_enter(self) -> str:
        """Qué hace Enter sobre la parada del cursor (sin red: solo decide). Devuelve
        "navegar", "fragmento" o "en_sitio"; lanza AccionNoPermitida si no se debe ejecutar.

        - Botón, enlace o menuitem con aria-expanded, o pestaña → "en_sitio": clic en la misma
          página (expandir, colapsar, seleccionar pestaña).
        - Enlace con "#id" de la misma página → "fragmento" (p. ej. "Saltar al contenido").
        - Enlace con href="#" o javascript: → "en_sitio" (depende de JavaScript).
        - Enlace con mailto:, tel:, etc. → no se ejecuta: abriría otra aplicación.
        - Otro enlace (incluida la misma página sin "#", que recarga) → "navegar".
          menuitem sin url en el árbol también: el navegador lee el href del DOM.
        - Todo lo demás (campos, botones sin expanded, encabezados, texto) → no se ejecuta.
        """
        if self.cursor < 0:
            raise AccionNoPermitida("el cursor está antes de la primera parada")
        p = self.paradas[self.cursor]
        if (p.rol in ROLES_EXPANDIBLES and p.expandido is not None) or p.rol == "tab":
            return "en_sitio"
        if p.rol not in ROLES_ENLACE:
            raise AccionNoPermitida(f"Enter no se ejecuta en {p.rol} '{p.nombre}'")
        if p.url is None:
            return "navegar" if p.rol == "menuitem" else "en_sitio"
        esquema = urlparse(p.url).scheme.lower()
        if esquema == "javascript":
            return "en_sitio"
        if esquema not in ESQUEMAS_NAVEGABLES:
            raise AccionNoPermitida(f"Enter en '{p.nombre}' abriría otra aplicación ({esquema})")
        destino, fragmento = urldefrag(p.url)
        if self.url and destino == urldefrag(self.url)[0] and p.url.endswith("#" + fragmento):
            return "fragmento" if fragmento else "en_sitio"
        return "navegar"

    def _enter(self, accion: str) -> Paso:
        if self.navegador is None:
            raise RuntimeError("Enter que navega o activa necesita un navegador en vivo")
        parada = self.paradas[self.cursor]
        if accion == "navegar":
            return self._navegar(parada)
        raise NotImplementedError(accion)

    def _navegar(self, parada: Parada) -> Paso:
        """Enter en enlace: el navegador abre el destino en una pestaña nueva (una por nivel).
        La pulsación cuenta aunque la carga falle o exceda la profundidad."""
        r = self.navegador.navegar(parada)
        if isinstance(r, Falla):
            return self._terminar("Enter", r.motivo, r.detalle, contada=True)
        if isinstance(r, Documento):
            # Descarga: no cambia de página ni apila nivel; el cursor sigue en el enlace.
            # Se registra el hecho medido (¿PDF con capa de texto?); el veredicto es de 3D.
            nombre = Path(urlparse(r.url).path).name or r.url
            return self._registrar("Enter", f"documento descargado: {nombre}",
                                   se_movio=False, documento=r)
        if self.profundidad + 1 > PROFUNDIDAD_MAX:
            self.navegador.volver()  # la página del nivel 4 no se muestra
            return self._terminar(
                "Enter", "profundidad",
                f"el enlace lleva al nivel {self.profundidad + 1} (máx. {PROFUNDIDAD_MAX})",
                contada=True)
        paradas, finales = aplanar_pagina(r.arbol)
        self._historial.append(Vista(paradas, finales, r.url, r.titulo, r.estado_http,
                                     r.captcha))
        # Al cargar, NVDA anuncia el título; su lectura automática no es una pulsación y no
        # se cuenta. El cursor queda antes de la primera parada.
        return self._registrar("Enter", r.titulo, se_movio=True, estado_http=r.estado_http,
                               captcha=r.captcha)

    def _volver(self) -> Paso:
        """Alt+←: 1 pulsación. Se cierra la pestaña del nivel actual y se reusa la página
        anterior tal como quedó (mismo árbol, sin recapturar): el cursor queda en el enlace
        que se activó. Sin página anterior no pasa nada y cuenta 1 (como D1)."""
        if self.profundidad == 0:
            return self._registrar("volver", "no hay página anterior", se_movio=False)
        self.navegador.volver()
        self._historial.pop()
        return self._registrar("volver", self.titulo, se_movio=True)

    @classmethod
    def en_vivo(cls, navegador, url: str, tope_pulsaciones: int | None = None) -> "Emulador":
        """Abre el punto de entrada (nivel 0). Si la carga falla, el emulador queda No
        evaluable con 0 pulsaciones."""
        r = navegador.abrir(url)
        if isinstance(r, Pagina):
            return cls(*aplanar_pagina(r.arbol), navegador=navegador, url=r.url,
                       titulo=r.titulo, estado_http=r.estado_http, captcha=r.captcha,
                       tope_pulsaciones=tope_pulsaciones)
        emu = cls([], navegador=navegador, url=url, tope_pulsaciones=tope_pulsaciones)
        if isinstance(r, Falla):
            emu._terminar("entrada", r.motivo, r.detalle)
        else:
            emu._terminar("entrada", "falla_tecnica", "la entrada es un documento, no una página")
        return emu
