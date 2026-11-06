"""Estrategias programadas (Fase 3C): deterministas, sin IA, sobre el emulador de 3A/3B.

Cada estrategia decide con lo anunciado (roles, nombres, títulos al llegar) y con una lista
declarada de palabras clave (config/palabras_clave.yaml), no por significado.
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.emulador import ROLES_CAMPO, TEXTO, normalizar

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
                         lista(datos["busqueda"]), tareas)


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
            return {"contacto": p.nombre}
        if self.b.letra == "B":
            if p.rol in ("heading", TEXTO) and coincide(p.nombre, self.b.clave.marcador):
                self.marcador, self.requisitos = True, []
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
