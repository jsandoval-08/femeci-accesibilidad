"""Fase 3F.2: bloqueo de hosts del modo exploración. Nada contra sitios reales: el bloqueo en vivo
se prueba bloqueando "localhost" mientras las páginas se sirven desde 127.0.0.1."""

import pytest
from playwright.sync_api import Error as ErrorPlaywright

from app.seguridad import (EntradaInvalida, HostBloqueado, NavegadorConBloqueo, cargar_config,
                           host_bloqueado, validar_entrada)

HOSTS = ("ciudadano.sinaloa.gob.mx", "culiacan.gob.mx")


def test_config_sin_sitios_bloqueados_tras_la_auditoria_del_15_nov():
    # El 15-nov terminó la auditoría NVDA de ciudadano, Culiacán, atención ciudadana y Navolato: la lista
    # queda vacía. Se vuelve a llenar ANTES de explorar el siguiente sitio que se audite a ciegas.
    config = cargar_config()
    assert config.hosts_bloqueados == ()
    assert config.carpeta.name == "exploracion"
    assert "estudio" not in config.carpeta.parts


def test_config_no_acepta_carpeta_dentro_de_estudio(tmp_path):
    ruta = tmp_path / "c.yaml"
    ruta.write_text("hosts_bloqueados: []\ncarpeta: estudio/exploracion\n", encoding="utf-8")
    with pytest.raises(ValueError, match="estudio"):
        cargar_config(ruta)


@pytest.mark.parametrize("url,esperado", [
    ("https://ciudadano.sinaloa.gob.mx/tramites", "ciudadano.sinaloa.gob.mx"),
    ("https://CULIACAN.gob.mx/", "culiacan.gob.mx"),
    ("https://www.culiacan.gob.mx/x", "culiacan.gob.mx"),
    ("http://a.b.culiacan.gob.mx./", "culiacan.gob.mx"),
    ("https://sinaloa.gob.mx/", None),  # el dominio padre de ciudadano no está bloqueado
    ("https://noculiacan.gob.mx/", None),  # no es subdominio: solo comparte el final del texto
    ("https://culiacan.gob.mx.ejemplo.com/", None),
    ("mailto:a@culiacan.gob.mx", None),
])
def test_host_bloqueado(url, esperado):
    assert host_bloqueado(url, HOSTS) == esperado


def test_validar_entrada():
    assert validar_entrada("  https://sinaloa.gob.mx/ ", HOSTS) == "https://sinaloa.gob.mx/"
    with pytest.raises(HostBloqueado, match="auditoría NVDA a ciegas"):
        validar_entrada("https://www.culiacan.gob.mx/", HOSTS)
    for mala in ("", "sinaloa.gob.mx", "file:///C:/x.html", "javascript:alert(1)", "ftp://a.mx/"):
        with pytest.raises(EntradaInvalida):
            validar_entrada(mala, HOSTS)


def test_el_contexto_aborta_las_peticiones_a_hosts_bloqueados(chromium, servidor):
    puerto = servidor.rsplit(":", 1)[1].rstrip("/")
    nav = NavegadorConBloqueo(chromium, ("localhost",))
    contexto = nav.new_context()
    pagina = contexto.new_page()
    try:
        pagina.goto(f"{servidor}perfecta.html")  # 127.0.0.1: pasa
        with pytest.raises(ErrorPlaywright):
            pagina.goto(f"http://localhost:{puerto}/perfecta.html")
        assert nav.bloqueadas == [f"http://localhost:{puerto}/perfecta.html"]
        assert nav.version == chromium.version  # lo demás pasa al Browser real
    finally:
        contexto.close()
