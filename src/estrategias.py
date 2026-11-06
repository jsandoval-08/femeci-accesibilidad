"""Estrategias programadas (Fase 3C): deterministas, sin IA, sobre el emulador de 3A/3B.

Cada estrategia decide con lo anunciado (roles, nombres, títulos al llegar) y con una lista
declarada de palabras clave (config/palabras_clave.yaml), no por significado.
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.emulador import normalizar

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
