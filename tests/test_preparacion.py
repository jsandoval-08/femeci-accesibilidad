"""Fase 3D.1: topes, títulos iguales, D a main y marcador con contenido.

Valores escritos A MANO, antes del código, desde el HTML de las páginas. SOLO páginas locales.
"""

import pytest

from src import estrategias, veredicto
from src.estrategias import Tarea, cargar_palabras, mejor_estrategia

pytestmark = pytest.mark.skip("se activa con el código de 3D.1")

PALABRAS = cargar_palabras()
TRAMITE = "Licencia de construcción"
TELEFONO = "667 555 0100"
REQUISITOS = "Identificación oficial|Comprobante de domicilio"


def _intentos(r):
    return {i.estrategia: i for i in r.intentos}


def _teclas(intento):
    return [p.tecla for p in intento.trayectoria]


# ---------- Tope de pulsaciones ----------

def test_tope_pulsaciones_exacto(vivo):
    """perfecta A con H: 6 H + 1 flecha = 7. Con tope 7 llega; con tope 6 se ejecutan 6."""
    tarea = Tarea("A", "perfecta.html")
    llega = estrategias.correr("H_a_seccion", lambda p: vivo(p, tope=7), tarea, PALABRAS)
    assert llega.llego and llega.pulsaciones == 7
    corta = estrategias.correr("H_a_seccion", lambda p: vivo(p, tope=6), tarea, PALABRAS)
    assert not corta.llego and corta.pulsaciones == 6
    assert corta.no_evaluable.motivo == "tope_pulsaciones"


def test_si_otra_llega_gana_al_tope(vivo):
    """perfecta C con tope 5: la lista llega en 5 (H necesitaría 7)."""
    r = mejor_estrategia(lambda p: vivo(p, tope=5), Tarea("C", "perfecta.html"), PALABRAS)
    v = veredicto.clasificar(r, "docs/plan_municipal.pdf")
    assert (v.estado, v.estrategia, v.friccion) == ("completable", "enlace_por_nombre", 5)
    assert _intentos(r)["H_a_seccion"].no_evaluable.motivo == "tope_pulsaciones"


def test_tope_sin_resolver_es_no_evaluable(vivo):
    """sin_contacto A con tope 10: leer no alcanza a comprobar que no existe (42): no se afirma
    no_encontrado."""
    r = mejor_estrategia(lambda p: vivo(p, tope=10), Tarea("A", "sin_contacto.html"), PALABRAS)
    v = veredicto.clasificar(r, "NO_EXISTE")
    assert v.estado == "no_evaluable" and v.tipo_falla is None
    assert "tope_pulsaciones" in v.motivo


# ---------- Tope de navegaciones ----------

def test_tope_navegaciones_exacto_enlaces_ambiguos(vivo):
    """enlaces_ambiguos B usa 9 navegaciones: con 9 llega en 35. Con 8: H×3 + 8×(K, Enter, volver)
    = 27, K = 28, y el 9.º Enter no se ejecuta ni cuenta."""
    tarea = Tarea("B", "enlaces_ambiguos.html", TRAMITE)
    llega = estrategias.correr("probar_enlaces", lambda p: vivo(p, tope_nav=9), tarea, PALABRAS)
    assert llega.llego and llega.pulsaciones == 35
    corta = estrategias.correr("probar_enlaces", lambda p: vivo(p, tope_nav=8), tarea, PALABRAS)
    assert not corta.llego and corta.pulsaciones == 28
    assert corta.no_evaluable.motivo == "tope_navegaciones"
    assert _teclas(corta).count("volver") == 8


def test_tope_navegaciones_sin_resolver_es_no_evaluable(vivo):
    r = mejor_estrategia(lambda p: vivo(p, tope_nav=8), Tarea("B", "enlaces_ambiguos.html", TRAMITE),
                         PALABRAS)
    v = veredicto.clasificar(r, "Croquis del terreno")
    assert v.estado == "no_evaluable" and "tope_navegaciones" in v.motivo


def test_descarga_cuenta_como_navegacion(vivo):
    """perfecta: el PDF es el 4.º enlace, 1 + 3 + Enter = 5. El 2.º Enter excede el tope de 1, no se
    ejecuta y no cuenta."""
    emu = vivo("perfecta.html", tope_nav=1)
    emu.elegir_de_lista("enlaces", 3)
    assert emu.pulsar("Enter").documento is not None
    assert emu.navegaciones == 1 and emu.pulsaciones == 5
    paso = emu.pulsar("Enter")
    assert paso.documento is None and paso.no_evaluable == "tope_navegaciones"
    assert emu.pulsaciones == 5 and emu.navegaciones == 1


def test_volver_no_cuenta_como_navegacion(vivo):
    """enlaces_ambiguos: K×4 llega al primer 'Leer más' (3 del menú + 1)."""
    emu = vivo("enlaces_ambiguos.html", tope_nav=5)
    for _ in range(4):
        emu.pulsar("K")
    emu.pulsar("Enter")
    assert emu.navegaciones == 1
    emu.pulsar("volver")
    assert emu.navegaciones == 1


def test_lo_que_no_carga_pagina_no_cuenta(vivo):
    """casos_navegacion (HTML): 'Saltar al contenido' es #id; 'Trámites' es botón colapsado. Con tope
    0 ambos funcionan: no cargan una página. El enlace normal sí se niega."""
    emu = vivo("casos_navegacion.html", tope_nav=0)
    emu.pulsar("K")
    emu.pulsar("Enter")  # fragmento
    assert emu.no_evaluable is None and emu.navegaciones == 0
    emu = vivo("casos_navegacion.html", tope_nav=0)
    for _ in range(3):
        emu.pulsar("flecha")
    emu.pulsar("Enter")  # expande
    assert emu.no_evaluable is None and emu.navegaciones == 0
    emu = vivo("casos_navegacion.html", tope_nav=0)
    emu.elegir_de_lista("enlaces", 1)  # "Directorio"
    assert emu.pulsar("Enter").no_evaluable == "tope_navegaciones"


# ---------- Títulos iguales ----------

def test_titulo_igual_no_decide(vivo):
    """ce_titulo_igual: todas se titulan 'Ayuntamiento'. Desde el inicio: K 1, Enter 2, H 3, H sin
    más 4, volver 5, K 6, Enter 7, H 8, flechas 11. Desde la sección: 1 más = 12."""
    r = mejor_estrategia(vivo, Tarea("B", "ce_titulo_igual.html", TRAMITE), PALABRAS)
    assert r.estrategia == "probar_enlaces" and r.friccion == 11
    v = veredicto.clasificar(r, REQUISITOS)
    assert v.estado == "completable"


def test_titulo_distinto_sigue_rechazando(vivo):
    """enlaces_ambiguos B: 'Otro trámite - ...' no es el título de origen: 3 por intento, 35."""
    r = mejor_estrategia(vivo, Tarea("B", "enlaces_ambiguos.html", TRAMITE), PALABRAS)
    assert r.friccion == 35


# ---------- D a main ----------

def test_d_a_main(vivo):
    """ce_main: D nav 1, D main 2 (queda en Bienvenida), flecha 3. Leer: 3 enlaces + 2 = 5."""
    r = mejor_estrategia(vivo, Tarea("A", "ce_main.html"), PALABRAS)
    assert r.estrategia == "D_a_main" and r.friccion == 3
    assert _intentos(r)["no_dirigida"].pulsaciones == 5
    assert not _intentos(r)["D_a_seccion"].llego


def test_d_a_main_sin_main(vivo):
    """ce_contacto: solo un nav. D 1, D sin más 2: no llega."""
    i = estrategias.correr("D_a_main", vivo, Tarea("A", "ce_contacto.html"), PALABRAS)
    assert not i.llego and i.pulsaciones == 2


def test_d_a_main_lee_hasta_el_fin_del_documento(vivo):
    """perfecta A: main empieza en la parada 4 y el teléfono es la 34: D×3 + 30 flechas = 33.
    Tarea D, F desde main: D×3 + F×3 = 6."""
    a = estrategias.correr("D_a_main", vivo, Tarea("A", "perfecta.html"), PALABRAS)
    assert a.llego and a.pulsaciones == 33
    d = estrategias.correr("D_a_main", vivo, Tarea("D", "perfecta.html"), PALABRAS)
    assert d.llego and d.pulsaciones == 6


# ---------- Marcador con contenido ----------

@pytest.mark.parametrize("texto,esperado", [
    ("Requisitos: INE, CURP", True),
    ("Debes presentar INE y CURP.", True),
    ("Requisitos para tramitar la licencia:", False),  # anuncia una lista que viene después
    ("Requisitos:", False),
    ("Requisitos", False),
    ("Consulta los requisitos en línea", False),  # no empieza con el marcador
    ("Para este trámite debes presentar INE", False),  # límite declarado
    ("Requisitorias judiciales pendientes", False),  # palabra completa
])
def test_marcador_con_contenido(texto, esperado):
    assert estrategias.marcador_con_contenido(texto, PALABRAS.tareas["B"].marcador) is esperado


def test_requisitos_en_la_misma_parada(vivo):
    """ce_requisitos_linea: H 1, flecha 2; lo siguiente es un encabezado. Leer también da 2."""
    r = mejor_estrategia(vivo, Tarea("B", "ce_requisitos_linea.html", TRAMITE), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 2
    assert veredicto.clasificar(r, REQUISITOS).estado == "completable"


def test_frase_que_menciona_requisitos_no_llega(vivo):
    """ce_requisitos_no: la frase no trae requisitos y sigue un encabezado: nadie llega."""
    r = mejor_estrategia(vivo, Tarea("B", "ce_requisitos_no.html", TRAMITE), PALABRAS)
    assert r.mejor is None
