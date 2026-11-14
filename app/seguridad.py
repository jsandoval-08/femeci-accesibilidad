"""Seguridad del modo exploración: configuración y bloqueo de hosts (Fase 3F).

Hay sitios con auditoría NVDA a ciegas pendiente: si Atorapp los evaluara antes, la auditoría ya no
sería a ciegas. Por eso la app los bloquea en cuatro barreras (ver app/motor.py para la 3 y la 4):
  1. La URL de entrada se rechaza antes de tocar la red.
  2. El contexto de Playwright aborta toda petición a esos hosts (NavegadorConBloqueo).
  3. Si una redirección termina en uno de ellos, se aborta toda la evaluación.
  4. Si la captura de axe termina en uno de ellos, se borra y no se reportan puntajes.
"""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

RAIZ = Path(__file__).resolve().parent.parent
RUTA_CONFIG = RAIZ / "config" / "exploracion.yaml"
ESQUEMAS = ("http", "https")


class EntradaInvalida(ValueError):
    """La URL de entrada no se puede evaluar (esquema, forma)."""


class HostBloqueado(Exception):
    """La URL (o una a la que llevó el recorrido) está en un host bloqueado."""

    def __init__(self, url: str, host: str):
        super().__init__(f"{url} está en un host bloqueado ({host}): tiene una auditoría NVDA a "
                         "ciegas pendiente. Se quita de config/exploracion.yaml cuando termine.")
        self.url, self.host = url, host


@dataclass(frozen=True)
class Config:
    hosts_bloqueados: tuple[str, ...]
    carpeta: Path  # dónde se guarda lo que corre la app


def cargar_config(ruta: Path = RUTA_CONFIG) -> Config:
    datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8")) or {}
    hosts = tuple(str(h).strip().lower().rstrip(".") for h in datos.get("hosts_bloqueados") or ()
                  if str(h).strip())
    carpeta = Path(datos.get("carpeta") or "exploracion")
    if not carpeta.is_absolute():
        carpeta = RAIZ / carpeta
    if carpeta.resolve().is_relative_to((RAIZ / "estudio").resolve()):
        raise ValueError("la carpeta del modo exploración no puede estar dentro de estudio/")
    return Config(hosts, carpeta)


def host_bloqueado(url: str, hosts) -> str | None:
    """El host bloqueado que cubre a `url` (exacto o subdominio), o None."""
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    if not host:
        return None
    return next((h for h in hosts if host == h or host.endswith("." + h)), None)


def validar_entrada(url: str, hosts) -> str:
    """Barrera 1: antes de tocar la red. Devuelve la URL limpia o lanza la excepción."""
    url = (url or "").strip()
    partes = urlparse(url)
    if partes.scheme not in ESQUEMAS or not partes.hostname:
        raise EntradaInvalida("escribe una dirección completa que empiece con http:// o https://")
    if bloqueado := host_bloqueado(url, hosts):
        raise HostBloqueado(url, bloqueado)
    return url


class NavegadorConBloqueo:
    """Barrera 2: envuelve el Browser de Playwright que recibe NavegadorEnVivo. Cada contexto nuevo
    aborta las peticiones a hosts bloqueados (un enlace hacia ellos queda como falla técnica de esa
    estrategia). Lo demás pasa tal cual al Browser real. `bloqueadas` registra lo que se abortó.
    Limitación: page.route no intercepta el destino de una redirección; eso lo cubre la barrera 3."""

    def __init__(self, navegador, hosts):
        self._navegador = navegador
        self._hosts = tuple(hosts)
        self.bloqueadas: list[str] = []

    def new_context(self, **opciones):
        contexto = self._navegador.new_context(**opciones)
        if self._hosts:
            contexto.route(lambda url: host_bloqueado(url, self._hosts) is not None, self._abortar)
        return contexto

    def _abortar(self, ruta):
        self.bloqueadas.append(ruta.request.url)
        ruta.abort("blockedbyclient")

    def __getattr__(self, nombre):
        return getattr(self._navegador, nombre)
