"""Veredicto por tarea (Fase 3D): del resultado de las estrategias y el objetivo correcto al estado.

Las estrategias nunca ven el objetivo: navegan y se detienen en lo que CREEN que es (3C). Aquí, al
final, el objetivo de la referencia filtra sus hallazgos. Nunca guía la navegación. La mejor
estrategia es la de menor fricción entre las que llegaron al objetivo correcto. Las que llegaron
a otra cosa no cambian el estado, pero se registran como falsas llegadas: en un sitio real eso
también le puede pasar a una persona.

Es una estimación de Atorapp, no un juicio sobre el sitio. La referencia es la auditoría con NVDA.
"""

import re
from dataclasses import dataclass
from urllib.parse import unquote, urldefrag

from src.estrategias import Intento, ResultadoTarea, normalizar_busqueda

UMBRAL = 15
UMBRALES_SENSIBILIDAD = (10, 15, 25)
NO_EXISTE = "NO_EXISTE"  # la referencia dice que el sitio no tiene ese objetivo
# Invisible: por sí sola no bloquea a nadie (ver SELECTORES_CAPTCHA en src/navegador.py).
CAPTCHA_QUE_NO_BLOQUEA = {"recaptcha-v3-insignia"}
MIN_DIGITOS = 7  # un objetivo con al menos estos dígitos se compara como teléfono


@dataclass(frozen=True)
class FalsaLlegada:
    """Una estrategia creyó llegar, pero a otra cosa."""
    estrategia: str
    pulsaciones: int
    encontro: str


@dataclass(frozen=True)
class Veredicto:
    estado: str  # completable | con_dificultad | no_completable | no_evaluable
    tipo_falla: str | None  # no_encontrado | no_identificable | cierre_roto
    estrategia: str | None
    friccion: int | None  # si se llegó, aunque el cierre o la identificación fallen
    consumidas: int | None  # si no se resolvió: lo más consumido entre estrategias
    motivo: str | None
    falsas_llegadas: tuple[FalsaLlegada, ...]
    sensibilidad: dict[int, str]  # estado con cada umbral
    intento: Intento | None  # el que sustenta el veredicto (o el más largo, si no se resolvió)


def _digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def _partes(objetivo: str) -> list[str]:
    return [normalizar_busqueda(p) for p in objetivo.split("|") if p.strip()]


def _contacto_correcto(hallazgo: dict, objetivo: str) -> bool:
    """En A, "|" separa alternativas (correo o teléfono): basta con encontrar UNA, porque cualquiera
    sirve para contactar. Bug corregido el 8-nov, antes de correr ahome: se juntaban los dígitos de
    todo el objetivo, así que el correo nunca contaba."""
    return any(_un_contacto(hallazgo, parte) for parte in objetivo.split("|") if parte.strip())


def _un_contacto(hallazgo: dict, objetivo: str) -> bool:
    nombre, url = hallazgo["contacto"], hallazgo.get("url") or ""
    digitos = _digitos(objetivo)
    if len(digitos) >= MIN_DIGITOS:  # cualquier formato; "+52" o la palabra "Tel." no estorban
        return digitos in _digitos(nombre) or digitos in _digitos(url)
    buscado = normalizar_busqueda(objetivo)
    return buscado in normalizar_busqueda(nombre) or buscado in normalizar_busqueda(unquote(url))


def _documento_correcto(hallazgo: dict, objetivo: str) -> bool:
    """La URL del documento es el objetivo o termina en él, por segmentos completos: "docs/a.pdf"
    no coincide con ".../midocs/a.pdf"."""
    url = unquote(urldefrag(hallazgo["documento"].url)[0])
    objetivo = unquote(objetivo.strip())
    return url == objetivo or url.endswith("/" + objetivo.lstrip("/"))


def _sin_nombre(hallazgo: dict) -> bool:
    return "campos" in hallazgo and not all(hallazgo["campos"])


def hallazgo_correcto(letra: str, hallazgo: dict, objetivo: str) -> bool:
    """¿Lo que encontró la estrategia es el objetivo de la referencia? La URL se usa solo aquí, en
    el veredicto (regla del 20-oct); nunca para navegar. En B se permiten requisitos de más:
    "Descargas" en sin_encabezados es un límite declarado de decidir por rol."""
    if objetivo.strip() == NO_EXISTE:
        return False
    if letra == "A":
        return _contacto_correcto(hallazgo, objetivo)
    if letra == "C":
        return _documento_correcto(hallazgo, objetivo)
    if letra == "D" and _sin_nombre(hallazgo):
        return False  # un campo sin nombre no se puede llenar
    encontrados = [normalizar_busqueda(t) for t in hallazgo["requisitos" if letra == "B" else "campos"]]
    return all(any(p in t for t in encontrados) for p in _partes(objetivo))


def _describir(hallazgo: dict) -> str:
    if "contacto" in hallazgo:
        return hallazgo["contacto"]
    if "documento" in hallazgo:
        return hallazgo["documento"].url
    return ", ".join(hallazgo.get("requisitos") or hallazgo.get("campos") or [])


def _estado_por_friccion(friccion: int, umbral: int) -> str:
    return "completable" if friccion <= umbral else "con_dificultad"


def clasificar(resultado: ResultadoTarea, objetivo: str, umbral: int = UMBRAL) -> Veredicto:
    """Reglas, en orden; gana la primera que aplique:
    1. C: el documento correcto es un PDF sin capa de texto → cierre_roto.
    2. C: PDF correcto que no se pudo leer → no_evaluable (no se midió).
    3. Alguna estrategia llegó al objetivo correcto → por fricción.
    4. D: alguna enumeró un campo sin nombre → no_identificable.
    5. Sin resolver, con No evaluable o CAPTCHA en la ruta → no_evaluable.
    6. Lo demás, incluso si llegó a otra cosa → no_encontrado."""
    letra = resultado.tarea.letra
    intentos = resultado.intentos
    llegaron = [i for i in intentos if i.llego]
    correctos = [i for i in llegaron if hallazgo_correcto(letra, i.hallazgo, objetivo)]
    sin_nombre = [i for i in llegaron if _sin_nombre(i.hallazgo)]
    falsas = tuple(FalsaLlegada(i.estrategia, i.pulsaciones, _describir(i.hallazgo))
                   for i in llegaron if i not in correctos and i not in sin_nombre)

    def fijo(estado, tipo_falla, intento, motivo, friccion=None):
        consumidas = None if friccion is not None else intento.pulsaciones
        return Veredicto(estado, tipo_falla, intento.estrategia, friccion, consumidas, motivo, falsas,
                         {u: estado for u in UMBRALES_SENSIBILIDAD}, intento)

    if correctos:
        mejor = min(correctos, key=lambda i: i.pulsaciones)
        if letra == "C":
            doc = mejor.hallazgo["documento"]
            if doc.es_pdf and doc.capa_texto is False:
                return fijo("no_completable", "cierre_roto", mejor,
                            "PDF sin capa de texto: el lector no tiene nada que leer",
                            mejor.pulsaciones)
            if doc.es_pdf and doc.capa_texto is None:
                return fijo("no_evaluable", None, mejor,
                            f"no se pudo leer el PDF: {doc.error or 'sin detalle'}")
        return Veredicto(_estado_por_friccion(mejor.pulsaciones, umbral), None, mejor.estrategia,
                         mejor.pulsaciones, None, None, falsas,
                         {u: _estado_por_friccion(mejor.pulsaciones, u)
                          for u in UMBRALES_SENSIBILIDAD}, mejor)
    if sin_nombre:
        mejor = min(sin_nombre, key=lambda i: i.pulsaciones)
        return fijo("no_completable", "no_identificable", mejor,
                    "se llega a los campos, pero alguno se anuncia sin nombre", mejor.pulsaciones)
    mas_larga = max(intentos, key=lambda i: i.pulsaciones)
    no_evaluable = next((i.no_evaluable for i in intentos if i.no_evaluable), None)
    if no_evaluable:
        return fijo("no_evaluable", None, mas_larga,
                    f"no resuelta dentro del presupuesto: {no_evaluable.motivo}")
    captcha = [m for m in resultado.captcha if m not in CAPTCHA_QUE_NO_BLOQUEA]
    if captcha:
        return fijo("no_evaluable", None, mas_larga,
                    f"no resuelta, con CAPTCHA en la ruta: {', '.join(captcha)}")
    motivo = ("ninguna estrategia llegó al objetivo correcto; alguna llegó a otra cosa" if falsas
              else "ninguna estrategia encontró el objetivo")
    return fijo("no_completable", "no_encontrado", mas_larga, motivo)
