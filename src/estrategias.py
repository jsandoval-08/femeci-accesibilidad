"""Estrategias programadas (Fase 3C): deterministas, sin IA, sobre el emulador de 3A/3B.

Cada estrategia decide con lo anunciado (roles, nombres, títulos al llegar) y con una lista
declarada de palabras clave (config/palabras_clave.yaml), no por significado.
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urldefrag

import yaml

from src.emulador import (FILTROS, ROLES_CAMPO, ROLES_ENLACE, ROLES_EXPANDIBLES, TEXTO,
                          AccionNoPermitida, NoEvaluable, Paso, SesionTerminada, normalizar)

RUTA_PALABRAS = Path(__file__).parent.parent / "config" / "palabras_clave.yaml"


# ---------- Palabras clave ----------

def normalizar_busqueda(texto: str) -> str:
    """Minúsculas, sin acentos y con los espacios colapsados, para comparar nombres."""
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return normalizar(sin_marcas).lower()


def coincide(texto: str, frases) -> bool:
    """¿Aparece alguna frase como palabra o frase completa? Así "ley" no coincide con "leyenda",
    y "pdf" sí con "(PDF)". Las frases ya vienen normalizadas."""
    texto = normalizar_busqueda(texto)
    return any(re.search(rf"(?<!\w){re.escape(f)}(?!\w)", texto) for f in frases)


@dataclass(frozen=True)
class PalabrasTarea:
    seccion: tuple[str, ...]
    enlace: tuple[str, ...]
    marcador: tuple[str, ...] = ()


@dataclass(frozen=True)
class PalabrasClave:
    version: int
    estado: str
    genericos: frozenset[str]
    busqueda: tuple[str, ...]
    expandir: tuple[str, ...]
    tareas: dict[str, PalabrasTarea]


def cargar_palabras(ruta: Path = RUTA_PALABRAS) -> PalabrasClave:
    datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))

    def lista(frases):
        return tuple(normalizar_busqueda(f) for f in frases)

    tareas = {}
    for letra, t in datos["tareas"].items():
        seccion = lista(t["seccion"])
        tareas[letra] = PalabrasTarea(seccion, lista(t["enlace"]) if "enlace" in t else seccion,
                                      lista(t.get("marcador", ())))
    return PalabrasClave(datos["version"], datos["estado"], frozenset(lista(datos["genericos"])),
                         lista(datos["busqueda"]), lista(datos["expandir"]), tareas)


# ---------- Tarea y criterios de "creo que llegué" ----------

@dataclass(frozen=True)
class Tarea:
    letra: str  # A | B | C | D
    entrada: str  # punto de entrada: parámetro explícito de cada tarea
    # Solo B: lo que la persona busca. Se fija ANTES de correr y nunca indica dónde está.
    tramite: str | None = None

    def __post_init__(self):
        if self.letra not in ("A", "B", "C", "D"):
            raise ValueError(f"Tarea desconocida: {self.letra}")
        if self.letra == "B" and not self.tramite:
            raise ValueError("La tarea B se define con el trámite que la persona busca")


# Palabras que dicen que un número es un teléfono (ya normalizadas).
PALABRAS_TELEFONO = ("tel", "telefono", "telefonos", "conmutador", "whatsapp", "llama", "llamanos")
_CORREO = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_NUMERO = re.compile(r"\+?\d[\d\s().-]*\d")
ESQUEMAS_CONTACTO = ("mailto:", "tel:")


def texto_de_contacto(texto: str) -> bool:
    """¿El texto anunciado trae un correo o un teléfono? Teléfono = 10 dígitos agrupados (12 con
    la lada 52 de México), o 7 o más junto a una palabra de teléfono. Exigir tantos dígitos evita
    que "Administración 2021-2024" o una fecha parezcan teléfono. Limitación: un folio de 10
    dígitos sí parecería teléfono."""
    texto = normalizar_busqueda(texto)
    if _CORREO.search(texto):
        return True
    con_palabra = coincide(texto, PALABRAS_TELEFONO)
    for numero in _NUMERO.findall(texto):
        digitos = sum(c.isdigit() for c in numero)
        if digitos in (10, 12) or (con_palabra and digitos >= 7):
            return True
    return False


def cierra_contacto(parada) -> bool:
    """Tarea A: lo anunciado trae el contacto, o el cursor YA está en un enlace mailto:/tel:
    (regla del 20-oct: Enter abriría el correo o el teléfono con el dato puesto; no se ejecuta ni
    se cobra). La URL se lee solo de la parada donde ya está el cursor, nunca para elegir a dónde
    ir."""
    if texto_de_contacto(parada.nombre):
        return True
    return parada.rol == "link" and (parada.url or "").lower().startswith(ESQUEMAS_CONTACTO)


def marcador_con_contenido(texto: str, marcadores) -> bool:
    """¿La misma parada trae el marcador y los requisitos? ("Requisitos: INE, CURP"; 1 StaticText =
    1 parada). Debe EMPEZAR con el marcador, tener texto después y no terminar en ":", porque eso
    anuncia una lista que viene después ("Requisitos para tramitar la licencia:"). Empezar con él
    evita que "Consulta los requisitos en línea" detenga la lectura. Limitación declarada: "Para
    este trámite debes presentar INE" no se reconoce."""
    texto = normalizar_busqueda(texto)
    if texto.endswith(":"):
        return False
    return any(re.match(rf"{re.escape(m)}(?!\w)\W*\w", texto) for m in marcadores)


@dataclass(frozen=True)
class _Busqueda:
    """Lo que una estrategia sabe de la tarea: su letra y las palabras. Nunca el objetivo."""
    tarea: Tarea
    palabras: PalabrasClave

    @property
    def letra(self) -> str:
        return self.tarea.letra

    @property
    def clave(self) -> PalabrasTarea:
        return self.palabras.tareas[self.letra]


class _Cierre:
    """Lo que ya se oyó en un recorrido por una página, y si con eso la tarea se da por resuelta.
    Tarea C no está aquí: cierra cuando Enter devuelve un Documento."""

    def __init__(self, b: _Busqueda):
        self.b = b
        self.marcador = False
        self.requisitos: list[str] = []
        self.campos: list[str] = []

    def ver(self, p) -> dict | None:
        """Registra la parada donde quedó el cursor. Solo A cierra con una sola parada."""
        if self.b.letra == "A" and cierra_contacto(p):
            return {"contacto": p.nombre, "url": p.url}  # la url es solo para el veredicto
        if self.b.letra == "B":
            if p.rol in ("heading", TEXTO) and coincide(p.nombre, self.b.clave.marcador):
                con_contenido = (p.rol == TEXTO
                                 and marcador_con_contenido(p.nombre, self.b.clave.marcador))
                self.marcador, self.requisitos = True, [p.nombre] if con_contenido else []
            elif self.marcador and p.rol == TEXTO:
                self.requisitos.append(p.nombre)
        elif self.b.letra == "D" and self._es_campo_buscado(p):
            self.campos.append(p.nombre)
        return None

    def _es_campo_buscado(self, p) -> bool:
        """La búsqueda del sitio no es "el formulario" de la tarea D."""
        return (p.rol in ROLES_CAMPO and p.rol != "searchbox"
                and not coincide(p.nombre, self.b.palabras.busqueda))

    def fin(self, siguiente) -> dict | None:
        """¿La siguiente parada revela que el bloque ya terminó? Se mira SOLO su ROL, nunca su
        nombre, y no se cobra (CLAUDE.md: subestima hasta 1 pulsación; es coherente con el fin de
        documento, que tampoco se cobra). siguiente=None: no hay más."""
        rol = siguiente.rol if siguiente else None
        if self.b.letra == "B" and self.marcador and rol != TEXTO:
            # Un marcador sin texto después no cuenta: se oyó el título, no un requisito.
            requisitos, self.marcador, self.requisitos = self.requisitos, False, []
            return {"requisitos": requisitos} if requisitos else None
        if self.b.letra == "D" and self.campos and rol in (None, "button", "link", "heading"):
            return {"campos": self.campos}
        return None


# ---------- Motor: recorrer una página y activar enlaces relevantes ----------

def _pulsar(emu, tecla):
    """Una pulsación. Si dejó la tarea No evaluable (timeout, profundidad, tope, falla técnica),
    se corta la estrategia: correr() lo reporta aparte, nunca como "no llegó"."""
    paso = emu.leer_de_corrido(1)[0] if tecla == "leer" else emu.pulsar(tecla)
    if emu.no_evaluable:
        raise SesionTerminada(emu.no_evaluable.motivo)
    return paso


def _siguiente(emu, tecla):
    """Siguiente parada a la que llegaría esta tecla, sin pulsarla. Quien llama usa solo su rol
    (y su nivel o sus landmarks, que también son estructura), nunca su nombre."""
    filtro = FILTROS[tecla]
    return next((p for p in emu.paradas[emu.cursor + 1:] if filtro(p)), None)


def _ya_abierta(emu, parada) -> bool:
    """No se re-entra a una URL abierta en la pila: gastaría profundidad sin avanzar. Una página
    ya cerrada sí se puede reabrir: con enlaces ambiguos, la persona no sabe por el nombre que
    llevan al mismo lugar. Un "#id" de la misma página no es re-entrar. Este es el único uso de
    la URL, además de cierra_contacto, y no decide relevancia."""
    if not parada.url:
        return False
    destino = urldefrag(parada.url)[0]
    if "#" in parada.url and destino == urldefrag(emu.url or "")[0]:
        return False
    return destino in {urldefrag(u)[0] for u in emu.urls_abiertas}


def _activar(emu, b, continuar, aceptar=None) -> dict | None:
    """Enter en el enlace del cursor. Si navega, sigue en la página nueva con `continuar` y, si
    no se resolvió, vuelve: cada intento fallido acumula su costo. Si `aceptar` rechaza la
    página (por su título), vuelve sin pulsar nada más."""
    if _ya_abierta(emu, emu.paradas[emu.cursor]):
        return None
    nivel = emu.profundidad
    try:
        paso = _pulsar(emu, "Enter")
    except AccionNoPermitida:  # mailto:, tel:: abriría otra aplicación; no se ejecuta ni cuenta
        return None
    if paso.documento:
        return {"documento": paso.documento} if b.letra == "C" else None
    if emu.profundidad == nivel:  # misma página (fragmento o clic): se sigue desde el cursor
        return None
    if aceptar is None or aceptar(emu):
        if hallazgo := continuar(emu, b):
            return hallazgo
    _pulsar(emu, "volver")
    return None


def _procesar(emu, b, cierre, continuar) -> dict | None:
    """Lo que se hace en la parada donde quedó el cursor."""
    p = emu.paradas[emu.cursor]
    if hallazgo := cierre.ver(p):
        return hallazgo
    if _debe_expandir(p, b):
        _pulsar(emu, "Enter")  # clic en la misma página; las paradas nuevas quedan después
        return None
    if continuar and p.rol in ROLES_ENLACE and coincide(p.nombre, b.clave.enlace):
        return _activar(emu, b, continuar)
    return None


def _debe_expandir(p, b) -> bool:
    """Un control colapsado se abre solo si su nombre es relevante: "Idioma" se queda cerrado,
    porque cada Enter cuesta y cambia la página. Limitación declarada: la lista de enlaces no ve
    los botones, así que no descubre lo que está en un submenú cerrado (no se mezclan estrategias)."""
    return (p.rol in ROLES_EXPANDIBLES and p.expandido is False
            and coincide(p.nombre, b.clave.seccion + b.clave.enlace + b.palabras.expandir))


def _recorrer(emu, b, tecla, continuar=None, es_fin=None) -> dict | None:
    """Avanza con `tecla` parada por parada hasta resolver, hasta que `es_fin` diga que acabó la
    sección o hasta que no haya más. "leer" se detiene sola al final del documento (no se cobra
    una de más; yaml: sin_contacto A = 42 con 42 paradas). F y Tab cuestan 1 al descubrir que no
    hay más (D1)."""
    cierre = _Cierre(b)
    if emu.cursor >= 0:  # ya está en la parada a la que saltó H o D
        if hallazgo := _procesar(emu, b, cierre, continuar):
            return hallazgo
    while True:
        siguiente = _siguiente(emu, tecla)
        if hallazgo := cierre.fin(siguiente):
            return hallazgo
        if siguiente is None:
            if tecla != "leer":
                _pulsar(emu, tecla)
            return None
        if es_fin and es_fin(siguiente):
            return None
        _pulsar(emu, tecla)
        if hallazgo := _procesar(emu, b, cierre, continuar):
            return hallazgo


def _por_saltos(emu, b, tecla, continuar) -> dict | None:
    """H o D hasta una sección con palabra clave, luego lee esa sección (en la tarea D, F desde
    ahí). Si no se resolvió, sigue saltando desde donde quedó."""
    while True:
        paso = _pulsar(emu, tecla)
        if tecla == "D":
            if paso.landmark is None:  # no hay más
                return None
            nombre = paso.landmark[1]
            es_fin = lambda q: bool(q.landmarks)  # noqa: E731 - empieza otro landmark
            if not paso.se_movio:  # landmark final vacío: no hay nada que leer
                continue
        else:
            if not paso.se_movio:
                return None
            nombre = emu.paradas[emu.cursor].nombre
            nivel = emu.paradas[emu.cursor].nivel or 1
            es_fin = lambda q: q.rol == "heading" and (q.nivel or 1) <= nivel  # noqa: B023, E731
        if not coincide(nombre, b.clave.seccion):
            continue
        if b.letra == "D":
            hallazgo = _recorrer(emu, b, "F")
        else:
            hallazgo = _recorrer(emu, b, "leer", continuar, es_fin)
        if hallazgo:
            return hallazgo


# ---------- Estrategias ----------
# Firma común: (emu, b) -> hallazgo o None. Con el cursor antes de la primera parada, también al
# llegar a una página nueva: tras cruzar se conserva la misma estrategia.

def h_a_seccion(emu, b):
    return _por_saltos(emu, b, "H", h_a_seccion)


def d_a_seccion(emu, b):
    return _por_saltos(emu, b, "D", d_a_seccion)


def d_a_main(emu, b):
    """D hasta `main`, con o sin nombre, y desde ahí hasta el final del documento (no solo hasta el
    final de main: el contacto suele estar en el pie). Saltarse el menú es el uso más común de D.
    En la tarea D sigue con F."""
    while True:
        paso = _pulsar(emu, "D")
        if paso.landmark is None:  # no hay más
            return None
        if paso.landmark[0] == "main" and paso.se_movio:
            if b.letra == "D":
                return _recorrer(emu, b, "F")
            return _recorrer(emu, b, "leer", d_a_main)


def _elegir(emu, posicion):
    emu.elegir_de_lista("enlaces", posicion)
    if emu.no_evaluable:
        raise SesionTerminada(emu.no_evaluable.motivo)


def enlace_por_nombre(emu, b):
    """Lista de enlaces (NVDA+F7): elige por nombre, en orden del documento. Cada elección abre la
    lista de nuevo: 1 + posición. Si ninguno coincide, la recorre completa para comprobarlo.
    La lista de encabezados no se usa: cuesta n + 1 contra n de H, así que nunca gana."""
    probados = set()
    while True:
        enlaces = emu.lista_elementos("enlaces")
        posicion = next((i for i, p in enumerate(enlaces)
                         if p.id_dom not in probados and coincide(p.nombre, b.clave.enlace)
                         and not _ya_abierta(emu, p)), None)
        if posicion is None:
            if enlaces and not probados:
                _elegir(emu, len(enlaces) - 1)
            return None
        probados.add(enlaces[posicion].id_dom)
        _elegir(emu, posicion)
        if hallazgo := _Cierre(b).ver(emu.paradas[emu.cursor]):
            return hallazgo
        if hallazgo := _activar(emu, b, _tras_elegir):
            return hallazgo


def _tras_elegir(emu, b):
    """En la página nueva: la tarea C vuelve a la lista. Lo demás no está en la lista de enlaces:
    D sigue con F, y A y B leen desde el inicio."""
    if b.letra == "C":
        return enlace_por_nombre(emu, b)
    if b.letra == "D":
        return _recorrer(emu, b, "F")
    return no_dirigida(emu, b)


def f_a_campos(emu, b):
    """Solo F, solo tarea D. No cruza de página: F nunca se detiene en un enlace."""
    return _recorrer(emu, b, "F")


def no_dirigida(emu, b):
    """Leer desde el inicio: lo único que no depende de la estructura de la página."""
    return _recorrer(emu, b, "leer", no_dirigida)


def tab_inicio(emu, b):
    """Tab desde el inicio. Solo sirve con objetivos enfocables: un texto no se alcanza."""
    return _recorrer(emu, b, "Tab", tab_inicio)


def _titulo_aceptable(emu, b, titulo_origen: str) -> bool:
    """Decide con el título anunciado al llegar, sin pulsar más (yaml: cada intento fallido = K +
    Enter + volver = 3). En B se compara con el trámite buscado, no con la lista: "Otro trámite"
    trae la palabra "trámite" y aun así es otra página. Si el título es igual al de la página de
    origen, no dice nada: no se rechaza y la página se inspecciona, con su costo. Limitación
    declarada: un título distinto, pero poco informativo ("Detalle"), se rechaza aunque sea el
    enlace correcto."""
    if normalizar_busqueda(emu.titulo) == normalizar_busqueda(titulo_origen):
        return True
    if b.letra == "B":
        frases = (normalizar_busqueda(b.tarea.tramite),)
    else:
        frases = b.clave.seccion + b.clave.enlace
    return coincide(emu.titulo, frases)


def _probar_con_k(emu, b):
    """K por los enlaces. Los de nombre genérico no se distinguen, así que se prueban en orden y
    el costo se acumula. Los enlaces sin nombre no se prueban: ese es el defecto del sitio.
    En la página aceptada se sigue con H + leer, como en la ruta del yaml."""
    while True:
        paso = _pulsar(emu, "K")
        if not paso.se_movio:
            return None
        p = emu.paradas[emu.cursor]
        if hallazgo := _Cierre(b).ver(p):
            return hallazgo
        if normalizar_busqueda(p.nombre) in b.palabras.genericos:
            origen = emu.titulo
            if hallazgo := _activar(emu, b, h_a_seccion, lambda e: _titulo_aceptable(e, b, origen)):
                return hallazgo


def probar_desde_seccion(emu, b):
    """H a la sección con palabra clave y, desde ahí, probar enlaces en orden."""
    while True:
        paso = _pulsar(emu, "H")
        if not paso.se_movio:
            return None
        if coincide(emu.paradas[emu.cursor].nombre, b.clave.seccion):
            return _probar_con_k(emu, b)


def probar_desde_inicio(emu, b):
    """Para páginas sin sección: H ya gastó las pulsaciones y dejó el cursor lejos, así que esta
    variante es un intento aparte, desde el inicio."""
    return _probar_con_k(emu, b)


# El orden es el de desempate: no cambia la fricción, solo el nombre reportado.
ESTRATEGIAS = {
    "H_a_seccion": h_a_seccion,
    "D_a_seccion": d_a_seccion,
    "D_a_main": d_a_main,
    "enlace_por_nombre": enlace_por_nombre,
    "F_a_campos": f_a_campos,
    "no_dirigida": no_dirigida,
    "Tab_inicio": tab_inicio,
    "probar_enlaces": probar_desde_seccion,
    "probar_enlaces_inicio": probar_desde_inicio,
}
SOLO_TAREA_D = {"F_a_campos"}
# Las dos variantes de probar_enlaces se reportan con el mismo nombre (vocabulario de los yaml).
ETIQUETAS = {"probar_enlaces_inicio": "probar_enlaces"}


# ---------- Resultados ----------

@dataclass(frozen=True)
class Intento:
    """Una estrategia en una tarea. llego = "cree que llegó", con lo anunciado; NO es completable
    (el veredicto contra el objetivo correcto es de 3D)."""
    estrategia: str
    llego: bool
    pulsaciones: int
    trayectoria: tuple[Paso, ...]
    motivo: str | None  # por qué no llegó
    no_evaluable: NoEvaluable | None
    hallazgo: dict | None  # contacto, requisitos, documento o campos
    captcha: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoTarea:
    tarea: Tarea
    estrategia: str  # la mejor; si nadie llegó, la que más consumió
    mejor: Intento | None
    friccion: int | None
    consumidas: int | None  # si nadie llegó: máximo entre estrategias (la comprobación más larga)
    motivo: str | None
    no_evaluable: NoEvaluable | None  # solo si nadie llegó y alguna quedó No evaluable
    captcha: tuple[str, ...]  # marcadores vistos en cualquier intento; la regla es de 3D
    intentos: tuple[Intento, ...]


def correr(clave: str, fabrica, tarea: Tarea, palabras: PalabrasClave) -> Intento:
    """Corre una estrategia con un emulador nuevo: ninguna hereda el cursor ni la pila de otra.
    fabrica(entrada) -> Emulador. Nunca recibe el objetivo."""
    emu = fabrica(tarea.entrada)
    captcha_entrada = emu.captcha
    hallazgo = None
    if not emu.no_evaluable:
        try:
            hallazgo = ESTRATEGIAS[clave](emu, _Busqueda(tarea, palabras))
        except SesionTerminada:
            hallazgo = None
    motivo = None
    if emu.no_evaluable:
        motivo = f"no evaluable: {emu.no_evaluable.motivo}"
    elif hallazgo is None:
        motivo = "no encontró el objetivo con lo anunciado"
    marcas = dict.fromkeys(captcha_entrada)
    for paso in emu.trayectoria:
        marcas.update(dict.fromkeys(paso.captcha))
    return Intento(ETIQUETAS.get(clave, clave), hallazgo is not None, emu.pulsaciones,
                   tuple(emu.trayectoria), motivo, emu.no_evaluable, hallazgo, tuple(marcas))


def mejor_estrategia(fabrica, tarea: Tarea, palabras: PalabrasClave) -> ResultadoTarea:
    """Mínima fricción entre las que llegan; en empate, la primera en el orden declarado. Si
    ninguna llega: lo más consumido y el motivo. Si además alguna quedó No evaluable, la tarea no
    se resolvió dentro del presupuesto: nunca cuenta como "no llegó"."""
    intentos = tuple(correr(clave, fabrica, tarea, palabras) for clave in ESTRATEGIAS
                     if clave not in SOLO_TAREA_D or tarea.letra == "D")
    marcas = dict.fromkeys(m for i in intentos for m in i.captcha)
    llegaron = [i for i in intentos if i.llego]
    if llegaron:
        mejor = min(llegaron, key=lambda i: i.pulsaciones)
        return ResultadoTarea(tarea, mejor.estrategia, mejor, mejor.pulsaciones, None, None, None,
                              tuple(marcas), intentos)
    mas_larga = max(intentos, key=lambda i: i.pulsaciones)
    no_evaluable = next((i.no_evaluable for i in intentos if i.no_evaluable), None)
    motivo = (f"no resuelta dentro del presupuesto: {no_evaluable.motivo}" if no_evaluable
              else "ninguna estrategia encontró el objetivo")
    return ResultadoTarea(tarea, mas_larga.estrategia, None, None, mas_larga.pulsaciones, motivo,
                          no_evaluable, tuple(marcas), intentos)
