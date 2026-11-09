"""Fase 3D: veredicto por tarea y expansión de menús colapsados.

Todos los valores esperados se escribieron A MANO, ANTES de implementar. El estado y el tipo de
falla de las 24 tareas vienen de los .esperado.yaml; el objetivo correcto, de los
<pagina>.auditoria.csv, escritos a mano. Si un valor no cuadra, se reporta: NO se ajusta.
SOLO páginas de prueba locales.
"""

import csv
from pathlib import Path

import pytest
import yaml

veredicto = pytest.importorskip("src.veredicto")
from src.emulador import Documento, NoEvaluable  # noqa: E402
from src.estrategias import (Intento, ResultadoTarea, Tarea, cargar_palabras,  # noqa: E402
                             mejor_estrategia)

PAGINAS = Path(__file__).parent / "paginas"
NOMBRES = ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
           "formulario_sin_etiquetas", "pdf_escaneado"]
TRAMITE = "Licencia de construcción"
PALABRAS = cargar_palabras()
TELEFONO = "667 555 0100"  # el de ce_p1


def _intento(estrategia, pulsaciones, hallazgo=None, no_evaluable=None, captcha=()):
    return Intento(estrategia, hallazgo is not None, pulsaciones, (),
                   None if hallazgo else "no encontró", no_evaluable, hallazgo, captcha)


def _resultado(letra, intentos, captcha=()):
    return ResultadoTarea(Tarea(letra, "p.html", "t" if letra == "B" else None), "x", None, None,
                          None, None, None, captcha, tuple(intentos))


def _documento(url="http://x/docs/plan.pdf", es_pdf=True, capa=True):
    return Documento(url, "application/pdf", es_pdf, capa, 1, 10)


def _falsas(v):
    return [f.estrategia for f in v.falsas_llegadas]


# ---------- Comparación del hallazgo contra el objetivo ----------

@pytest.mark.parametrize("letra,hallazgo,objetivo,correcto", [
    # A: con 7 dígitos o más se comparan los dígitos, con cualquier formato
    ("A", {"contacto": "Teléfono: 667 555 0142", "url": None}, "667 555 0142", True),
    ("A", {"contacto": "(667) 555-0142", "url": None}, "667 555 0142", True),
    ("A", {"contacto": "Llámanos", "url": "tel:+526675550142"}, "667 555 0142", True),
    ("A", {"contacto": "Tel. 667 555 0999", "url": None}, "667 555 0142", False),
    # A: sin dígitos, el texto en el nombre o en el mailto
    ("A", {"contacto": "Escríbenos", "url": "mailto:Oficina@Example.org"}, "oficina@example.org", True),
    ("A", {"contacto": "oficina@example.org", "url": None}, "oficina@example.org", True),
    ("A", {"contacto": "otra@example.org", "url": None}, "oficina@example.org", False),
    # 8-nov (bug): en A, "|" separa alternativas; basta UNA. Antes se juntaban los dígitos de todo
    # el objetivo y el correo nunca contaba (y con dígitos en el correo, tampoco el teléfono).
    ("A", {"contacto": "oficina@example.org", "url": None}, "oficina@example.org|(668) 555-0142", True),
    ("A", {"contacto": "Escríbenos", "url": "mailto:oficina@example.org"},
     "oficina@example.org|(668) 555-0142", True),
    ("A", {"contacto": "Tel. (668) 555-0142", "url": None}, "oficina@example.org|(668) 555-0142", True),
    ("A", {"contacto": "Tel. 668 555 0142", "url": None}, "oficina2026@example.org|668 555 0142", True),
    ("A", {"contacto": "oficina2026@example.org", "url": None}, "oficina2026@example.org|668 555 0142",
     True),
    ("A", {"contacto": "otra@example.org", "url": None}, "oficina@example.org|(668) 555-0142", False),
    ("A", {"contacto": "Tel. 668 555 0999", "url": None}, "oficina@example.org|(668) 555-0142", False),
    # B: todos los requisitos; los extras se permiten ("Descargas", límite declarado)
    ("B", {"requisitos": ["Identificación", "Croquis"]}, "Identificación|Croquis", True),
    ("B", {"requisitos": ["Identificación", "Croquis", "Descargas"]}, "Identificación|Croquis", True),
    ("B", {"requisitos": ["Identificación"]}, "Identificación|Croquis", False),
    # C: la URL del documento termina en el objetivo
    ("C", {"documento": _documento()}, "docs/plan.pdf", True),
    ("C", {"documento": _documento()}, "http://x/docs/plan.pdf", True),
    ("C", {"documento": _documento()}, "docs/otro.pdf", False),
    ("C", {"documento": _documento("http://x/midocs/plan.pdf")}, "docs/plan.pdf", False),
    # D: cada campo del objetivo en algún nombre; un campo sin nombre nunca es correcto
    ("D", {"campos": ["Nombre completo", "Trámite"]}, "Nombre completo|Trámite", True),
    ("D", {"campos": ["Nombre completo *", "Tramite"]}, "Nombre completo|Trámite", True),
    ("D", {"campos": ["Nombre completo"]}, "Nombre completo|Trámite", False),
    ("D", {"campos": ["Nombre completo", "Trámite", ""]}, "Nombre completo|Trámite", False),
    # La referencia dice que no existe: ningún hallazgo es correcto
    ("A", {"contacto": "Tel. 667 555 0999", "url": None}, "NO_EXISTE", False),
])
def test_hallazgo_correcto(letra, hallazgo, objetivo, correcto):
    assert veredicto.hallazgo_correcto(letra, hallazgo, objetivo) is correcto


# ---------- Reglas de veredicto ----------

BIEN = {"contacto": "Tel. 667 555 0142", "url": None}
OTRO = {"contacto": "Tel. 667 555 0999", "url": None}


@pytest.mark.parametrize("friccion,estado", [(15, "completable"), (16, "con_dificultad")])
def test_umbral_exacto(friccion, estado):
    v = veredicto.clasificar(_resultado("A", [_intento("H_a_seccion", friccion, BIEN)]), "667 555 0142")
    assert v.estado == estado and v.tipo_falla is None and v.friccion == friccion


def test_sensibilidad():
    v = veredicto.clasificar(_resultado("A", [_intento("H_a_seccion", 12, BIEN)]), "667 555 0142")
    assert v.estado == "completable"
    assert v.sensibilidad == {10: "con_dificultad", 15: "completable", 25: "completable"}
    con_diez = veredicto.clasificar(_resultado("A", [_intento("H_a_seccion", 12, BIEN)]),
                                    "667 555 0142", umbral=10)
    assert con_diez.estado == "con_dificultad"


def test_menor_friccion_entre_las_correctas():
    r = _resultado("A", [_intento("H_a_seccion", 3, OTRO), _intento("enlace_por_nombre", 7, BIEN),
                         _intento("no_dirigida", 20, BIEN)])
    v = veredicto.clasificar(r, "667 555 0142")
    assert (v.estado, v.estrategia, v.friccion) == ("completable", "enlace_por_nombre", 7)
    assert _falsas(v) == ["H_a_seccion"]
    falsa = v.falsas_llegadas[0]
    assert falsa.pulsaciones == 3 and "667 555 0999" in falsa.encontro


def test_solo_otra_cosa_es_no_encontrado():
    r = _resultado("A", [_intento("H_a_seccion", 3, OTRO), _intento("Tab_inicio", 9)])
    v = veredicto.clasificar(r, "667 555 0142")
    assert (v.estado, v.tipo_falla) == ("no_completable", "no_encontrado")
    assert v.friccion is None and v.consumidas == 9 and v.motivo
    assert _falsas(v) == ["H_a_seccion"]


def test_no_existe_y_alguien_cree_llegar():
    v = veredicto.clasificar(_resultado("A", [_intento("H_a_seccion", 3, OTRO)]), "NO_EXISTE")
    assert (v.estado, v.tipo_falla) == ("no_completable", "no_encontrado")
    assert _falsas(v) == ["H_a_seccion"]


def test_pdf_sin_capa_es_cierre_roto():
    r = _resultado("C", [_intento("enlace_por_nombre", 5, {"documento": _documento(capa=False)})])
    v = veredicto.clasificar(r, "docs/plan.pdf")
    assert (v.estado, v.tipo_falla, v.friccion) == ("no_completable", "cierre_roto", 5)


def test_pdf_ilegible_es_no_evaluable():
    r = _resultado("C", [_intento("enlace_por_nombre", 5, {"documento": _documento(capa=None)})])
    v = veredicto.clasificar(r, "docs/plan.pdf")
    assert v.estado == "no_evaluable" and v.tipo_falla is None and v.motivo


def test_documento_que_no_es_pdf_cuenta():
    doc = Documento("http://x/docs/plan.docx", "application/msword", False, None, None, None)
    v = veredicto.clasificar(_resultado("C", [_intento("H_a_seccion", 5, {"documento": doc})]),
                             "docs/plan.docx")
    assert v.estado == "completable"


def test_documento_equivocado_es_no_encontrado():
    r = _resultado("C", [_intento("H_a_seccion", 5, {"documento": _documento(capa=False)})])
    v = veredicto.clasificar(r, "docs/otro.pdf")
    assert (v.estado, v.tipo_falla) == ("no_completable", "no_encontrado")


def test_un_campo_sin_nombre_es_no_identificable():
    r = _resultado("D", [_intento("F_a_campos", 3, {"campos": ["Nombre", "", "Mensaje"]})])
    v = veredicto.clasificar(r, "Nombre|Correo|Mensaje")
    assert (v.estado, v.tipo_falla, v.friccion) == ("no_completable", "no_identificable", 3)
    assert not v.falsas_llegadas  # sin nombre no se puede saber si es otro formulario


def test_otra_estrategia_con_campos_correctos_gana():
    r = _resultado("D", [_intento("F_a_campos", 2, {"campos": [""]}),
                         _intento("H_a_seccion", 9, {"campos": ["Nombre"]})])
    v = veredicto.clasificar(r, "Nombre")
    assert (v.estado, v.estrategia, v.friccion) == ("completable", "H_a_seccion", 9)


NE = NoEvaluable("timeout", "lento", 2)


def test_no_evaluable_sin_resolver():
    r = _resultado("A", [_intento("H_a_seccion", 2), _intento("enlace_por_nombre", 2, no_evaluable=NE)])
    v = veredicto.clasificar(r, "667 555 0142")
    assert v.estado == "no_evaluable" and v.tipo_falla is None and "timeout" in v.motivo


def test_no_evaluable_gana_a_falsa_llegada():
    """No se sabe si el correcto estaba tras el timeout: no se afirma no_encontrado."""
    r = _resultado("A", [_intento("H_a_seccion", 3, OTRO), _intento("enlace_por_nombre", 2, no_evaluable=NE)])
    v = veredicto.clasificar(r, "667 555 0142")
    assert v.estado == "no_evaluable" and _falsas(v) == ["H_a_seccion"]


def test_resuelta_gana_a_no_evaluable():
    r = _resultado("A", [_intento("H_a_seccion", 3, BIEN), _intento("enlace_por_nombre", 2, no_evaluable=NE)])
    assert veredicto.clasificar(r, "667 555 0142").estado == "completable"


@pytest.mark.parametrize("captcha,estado", [
    (("g-recaptcha",), "no_evaluable"),  # no resuelta + CAPTCHA en la ruta (regla del 20-oct)
    (("recaptcha-v3-insignia",), "no_completable"),  # invisible: por sí sola no bloquea
    (("recaptcha-v3-insignia", "hcaptcha"), "no_evaluable"),
    ((), "no_completable"),
])
def test_captcha_sin_resolver(captcha, estado):
    r = _resultado("A", [_intento("H_a_seccion", 2)], captcha=captcha)
    assert veredicto.clasificar(r, "667 555 0142").estado == estado


def test_captcha_resuelta_cuenta_normal():
    r = _resultado("D", [_intento("F_a_campos", 3, {"campos": ["Nombre"]})], captcha=("g-recaptcha",))
    assert veredicto.clasificar(r, "Nombre").estado == "completable"


# ---------- Las 24 tareas: estado y tipo_falla del yaml, objetivo del CSV ----------

def _objetivos(nombre):
    with open(PAGINAS / f"{nombre}.auditoria.csv", encoding="utf-8-sig", newline="") as f:
        return {fila["tarea"]: fila for fila in csv.DictReader(f)}


RUTAS = [(n, t) for n in NOMBRES for t in "ABCD"]


@pytest.mark.parametrize("nombre,letra", RUTAS, ids=[f"{n}-{t}" for n, t in RUTAS])
def test_yaml(nombre, letra, vivo):
    esperado = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))["tareas"][letra]
    fila = _objetivos(nombre)[letra]
    tarea = Tarea(letra, fila["entrada"], fila["tramite"] or None)
    v = veredicto.clasificar(mejor_estrategia(vivo, tarea, PALABRAS), fila["objetivo_correcto"])
    assert v.estado == esperado["estado"]
    assert v.tipo_falla == esperado["tipo_falla"]
    assert v.estrategia == esperado["estrategia"]
    assert (v.friccion if v.friccion is not None else v.consumidas) == esperado["friccion_esperada"]
    assert not v.falsas_llegadas


def test_sensibilidad_no_cambia_ningun_estado_de_las_24_a_mano():
    """Valores de los yaml: lo logrado cuesta a lo sumo 9 o al menos 32. Ninguno está entre
    10 y 25, así que el estado no depende de cuál de los tres umbrales se use."""
    fricciones = []
    for nombre in NOMBRES:
        tareas = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))["tareas"]
        fricciones += [t["friccion_esperada"] for t in tareas.values() if t["estado"] != "no_completable"]
    assert not [f for f in fricciones if 10 <= f <= 25]


# ---------- Objetivo correcto en vivo (ce_*) ----------

def test_otro_telefono_no_decide(vivo):
    """ce_otro_telefono: H = 2 + 1 = 3 y leer = 3 llegan a 0999. Lista: 1 + Enter + 5 en ce_p1 = 7."""
    r = mejor_estrategia(vivo, Tarea("A", "ce_otro_telefono.html"), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 3  # lo que cree 3C
    v = veredicto.clasificar(r, TELEFONO)
    assert (v.estado, v.estrategia, v.friccion) == ("completable", "enlace_por_nombre", 7)
    assert _falsas(v) == ["H_a_seccion", "no_dirigida"]


def test_solo_otro_telefono(vivo):
    """ce_solo_otro: H = 3, leer = 3; lo más consumido = 3."""
    v = veredicto.clasificar(mejor_estrategia(vivo, Tarea("A", "ce_solo_otro.html"), PALABRAS), TELEFONO)
    assert (v.estado, v.tipo_falla) == ("no_completable", "no_encontrado")
    assert v.consumidas == 3 and _falsas(v) == ["H_a_seccion", "no_dirigida"]


# ---------- Expansión de menús ----------

def _anuncios(intento):
    return [p.anuncio for p in intento.trayectoria]


def test_menu_colapsado(vivo):
    """ce_menu: h1 1, Idioma 2, Menú 3, Enter 4, Contacto 5, Enter 6, 5 paradas en ce_p1 = 11.
    Tab llega al enlace, pero en ce_p1 el teléfono es texto: no llega. La lista no ve el enlace
    oculto. Completable con 15 y 25, con dificultad con 10."""
    r = mejor_estrategia(vivo, Tarea("A", "ce_menu.html"), PALABRAS)
    assert r.estrategia == "no_dirigida" and r.friccion == 11
    assert "botón, Menú, expandido" in _anuncios(r.mejor)
    assert not any("Idioma, expandido" in a for i in r.intentos for a in _anuncios(i))
    v = veredicto.clasificar(r, TELEFONO)
    assert v.estado == "completable"
    assert v.sensibilidad == {10: "con_dificultad", 15: "completable", 25: "completable"}


def test_menu_con_palabra_clave_dentro_de_seccion(vivo):
    """ce_menu_tramite: H 1, flecha al botón 2, Enter 3, enlace 4, Enter 5; en ce_requisitos,
    H a Servicios 1 + 5 flechas = 6; total 11. Leer también da 11: gana H por el orden."""
    r = mejor_estrategia(vivo, Tarea("B", "ce_menu_tramite.html", TRAMITE), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 11
    v = veredicto.clasificar(r, "Identificación oficial|Comprobante de domicilio")
    assert v.estado == "completable"


def test_menuitem_se_activa(vivo):
    """ce_menu_item: h1 1, botón 2, Enter 3, menuitem 4, Enter 5, 5 paradas en ce_p1 = 10."""
    r = mejor_estrategia(vivo, Tarea("A", "ce_menu_item.html"), PALABRAS)
    assert r.estrategia == "no_dirigida" and r.friccion == 10
    assert veredicto.clasificar(r, TELEFONO).estado == "completable"
