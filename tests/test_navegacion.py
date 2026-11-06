"""Fase 3B: navegación en vivo (Enter, volver, expandir, profundidad, No evaluable).

Todos los valores esperados de este archivo se escribieron A MANO, ANTES de implementar la
navegación, y NO se tomaron de la salida del emulador. Cada uno cita su fuente:
  - "HTML": se dedujo leyendo el HTML de la página de prueba;
  - "yaml": lo documentan los .esperado.yaml;
  - "comprobado 20-oct": hecho medido en Chromium (experimento del plan de 3B o prueba de 3A);
  - "PREDICCIÓN": aún no medido; si falla, se reporta la discrepancia, no se ajusta el valor.

Las páginas se sirven por el servidor local de tests/conftest.py (http, puerto libre), no por
file://. SOLO páginas de prueba locales: nada de sitios reales.

Reglas que se prueban (ver CLAUDE.md, 3B):
  - Enter en enlace → pestaña nueva, recaptura, cursor antes de la primera parada, anuncio =
    título. Volver (Alt+←) = 1 pulsación, reusa el árbol guardado y deja el cursor en el enlace.
  - Enter en botón con expanded → clic y recaptura en la misma página; el cursor se queda.
  - Enter en "#id" de la misma página → el cursor va al destino; cuesta 1 (bypass).
  - Enter en campos y botones sin expanded → no se ejecuta (nunca enviar formularios).
  - Profundidad = tamaño de la pila (entrada = nivel 0, máx. 3). Toda pulsación ejecutada cuenta.
  - CAPTCHA: se detecta y registra, la sesión NO se detiene.
"""

import json
from pathlib import Path

import pytest

from src.captura import capturar
from src.emulador import (PROFUNDIDAD_MAX, AccionNoPermitida, Emulador, SesionTerminada,
                          aplanar, aplanar_pagina)

PAGINAS = Path(__file__).parent / "paginas"


# ---------- Valores esperados (escritos a mano) ----------

# HTML de casos_navegacion.html, estado inicial (submenú oculto, pestaña 1 seleccionada).
# (rol, nombre, nivel, enfocable, landmarks que empiezan aquí, expandido, seleccionado)
NAV_MIGAS_PRINCIPAL = (("navigation", "Migas"), ("navigation", "Principal"))
CASOS_NAV_ANTES = [
    ("link", "Saltar al contenido", None, True, (), None, None),
    ("heading", "Casos de navegación", 1, False, (("banner", ""),), None, None),
    # La nav "Migas" está vacía: se anota aquí, junto con "Principal", que empieza aquí mismo.
    ("button", "Trámites", None, True, NAV_MIGAS_PRINCIPAL, False, None),
    ("link", "Directorio", None, True, (), None, None),
    ("heading", "Contenido", 2, False, (("main", ""),), None, None),
    ("heading", "Pestañas", 2, False, (), None, None),
    ("tab", "Lunes a viernes", None, True, (), None, True),
    # tabindex="-1": el árbol lo marca enfocable (comprobado 20-oct en 3A, casos_emulador)
    ("tab", "Sábado", None, True, (), None, False),
    ("tab", "Domingo", None, True, (), None, False),
    ("StaticText", "De 8:00 a 15:00 horas.", None, False, (), None, None),
    ("heading", "Otros controles", 2, False, (), None, None),
    ("switch", "Recibir avisos", None, True, (), None, None),
    # treeitem trae selected=false en el árbol (comprobado 20-oct, experimento del plan)
    ("treeitem", "Secretaría de Obras", None, True, (), None, False),
    ("heading", "Formulario", 2, False, (), None, None),
    ("StaticText", "Correo electrónico", None, False, (), None, None),  # <label> de textbox (3A)
    ("textbox", "Correo electrónico", None, True, (), None, None),
    ("button", "Enviar", None, True, (), None, None),
]
CASOS_NAV_FINALES = (("contentinfo", ""),)  # HTML: <footer> vacío al final

# HTML: al expandir, el submenú aparece justo después del botón (su lugar en el documento).
# Los menuitem con tabindex="-1" o href: PREDICCIÓN enfocables (misma razón que arriba).
CASOS_NAV_EXPANDIDO = (
    CASOS_NAV_ANTES[:2]
    + [("button", "Trámites", None, True, NAV_MIGAS_PRINCIPAL, True, None)]
    + [
        ("link", "Licencias de construcción", None, True, (), None, None),
        ("link", "Pagos en línea", None, True, (), None, None),
        ("menuitem", "Catastro", None, True, (), None, None),
        ("menuitemcheckbox", "Solo en línea", None, True, (), None, None),
        ("menuitemradio", "Ordenar por nombre", None, True, (), None, None),
    ]
    + CASOS_NAV_ANTES[3:]
)
I_BOTON = 2  # índice del botón "Trámites" (antes y después de expandir)
I_CONTENIDO = 4  # h2 "Contenido": primera parada dentro de <main id="contenido">

K_ANTES = ["Saltar al contenido", "Directorio"]  # HTML: K no se detiene en tab/switch/treeitem
K_EXPANDIDO = ["Saltar al contenido", "Licencias de construcción", "Pagos en línea",
               "Directorio"]  # HTML: K no se detiene en menuitem
TAB_ANTES = [  # HTML: solo la pestaña seleccionada; Sábado y Domingo solo con flecha
    ("link", "Saltar al contenido"), ("button", "Trámites"), ("link", "Directorio"),
    ("tab", "Lunes a viernes"), ("switch", "Recibir avisos"),
    ("treeitem", "Secretaría de Obras"), ("textbox", "Correo electrónico"), ("button", "Enviar"),
]
F_ANTES = [  # HTML: F = campos + botones (D2); switch no está en ROLES_F (por verificar en NVDA)
    ("button", "Trámites"), ("textbox", "Correo electrónico"), ("button", "Enviar"),
]
D_ANTES = [  # HTML: (landmark, índice de la parada donde queda el cursor)
    (("banner", ""), 1), (("navigation", "Migas"), I_BOTON),
    (("navigation", "Principal"), I_BOTON), (("main", ""), I_CONTENIDO),
]

# Anuncios (redacción propia, inspirada en NVDA; ver ROTULOS en src/emulador.py)
ANUNCIOS = {
    "boton_contraido": "botón, Trámites, contraído",
    "boton_expandido": "botón, Trámites, expandido",
    "tab_seleccionada": "pestaña, Lunes a viernes, seleccionada",
    "tab_no_seleccionada": "pestaña, Sábado",
    "switch": "conmutador, Recibir avisos",
    "treeitem": "elemento de árbol, Secretaría de Obras",
    "menuitem": "elemento de menú, Catastro",
    "menuitemcheckbox": "elemento de menú de verificación, Solo en línea",
    "menuitemradio": "elemento de menú de opción, Ordenar por nombre",
    "D_migas": "navegación Migas, punto de referencia; botón, Trámites, contraído",
    "D_final": "información de contenido, punto de referencia",
}

ENLACES_PERFECTA = 4  # yaml (razón de C en perfecta): menú (3) + PDF; el PDF es el 4.º
PARADAS_PERFECTA = 44  # yaml: "Página de referencia: 44 paradas"
MARCADORES_CAPTCHA = {"g-recaptcha", "data-sitekey", "texto"}  # HTML de captcha.html


def _tuplas(paradas):
    return [(p.rol, p.nombre, p.nivel, p.enfocable, p.landmarks, p.expandido, p.seleccionado)
            for p in paradas]


# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def arbol_casos(tmp_path_factory):
    """Árbol de casos_navegacion.html en su estado inicial (captura sin red, file://)."""
    url = (PAGINAS / "casos_navegacion.html").resolve().as_uri()
    carpeta = capturar(url, base=tmp_path_factory.mktemp("capturas"))
    return json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8"))


@pytest.fixture
def casos(arbol_casos):
    paradas, finales = aplanar_pagina(arbol_casos)
    return Emulador(paradas, finales)


# La fixture `vivo` (emuladores en vivo sobre el servidor local) está en tests/conftest.py.


def _hasta(emu, tecla, nombre):
    """Pulsa `tecla` hasta que el cursor quede en una parada con ese nombre."""
    while True:
        paso = emu.pulsar(tecla)
        assert paso.se_movio, f"{tecla}: no se encontró '{nombre}'"
        if emu.paradas[paso.parada].nombre == nombre:
            return paso


def _recorrer(emu, tecla):
    vistas = []
    while (paso := emu.pulsar(tecla)).se_movio:
        vistas.append(emu.paradas[paso.parada])
    return vistas


# ---------- Aplanado: roles nuevos y landmark vacío (sin red) ----------

def test_casos_navegacion_paradas(arbol_casos):
    paradas, finales = aplanar_pagina(arbol_casos)
    assert _tuplas(paradas) == CASOS_NAV_ANTES
    assert finales == CASOS_NAV_FINALES
    assert aplanar(arbol_casos) == paradas  # aplanar conserva su firma (scripts/medicion)
    assert all(p.id_dom for p in paradas)


def test_K_no_se_detiene_en_roles_nuevos(casos):
    vistas = _recorrer(casos, "K")
    assert [p.nombre for p in vistas] == K_ANTES


def test_tab_solo_pestana_seleccionada(casos):
    vistas = _recorrer(casos, "Tab")
    assert [(p.rol, p.nombre) for p in vistas] == TAB_ANTES


def test_F_casos_navegacion(casos):
    vistas = _recorrer(casos, "F")
    assert [(p.rol, p.nombre) for p in vistas] == F_ANTES


def test_anuncios_roles_nuevos(casos):
    anuncios = [casos.pulsar("flecha").anuncio for _ in range(len(CASOS_NAV_ANTES))]
    assert anuncios[I_BOTON] == ANUNCIOS["boton_contraido"]
    assert anuncios[6] == ANUNCIOS["tab_seleccionada"]
    assert anuncios[7] == ANUNCIOS["tab_no_seleccionada"]
    assert anuncios[11] == ANUNCIOS["switch"]
    assert anuncios[12] == ANUNCIOS["treeitem"]


def test_D_landmark_vacio(casos):
    """Migas (vacía) se anota en el botón; el footer vacío final se anuncia sin mover."""
    pasos = [casos.pulsar("D") for _ in range(6)]
    assert [(p.landmark, p.parada) for p in pasos[:4]] == D_ANTES
    assert all(p.se_movio for p in pasos[:4])
    assert pasos[1].anuncio == ANUNCIOS["D_migas"]  # anuncio combinado: limitación declarada
    # 5.º D: landmark final vacío. Anuncia, no mueve el cursor, cuenta 1.
    assert pasos[4].landmark == ("contentinfo", "")
    assert pasos[4].anuncio == ANUNCIOS["D_final"]
    assert not pasos[4].se_movio and pasos[4].parada == I_CONTENIDO
    assert pasos[4].pulsaciones == 5
    # 6.º D: ya no hay más (D1).
    assert pasos[5].landmark is None and pasos[5].anuncio == "no hay más puntos de referencia"
    assert pasos[5].pulsaciones == 6


# ---------- Reglas sin red: Enter no permitido, volver sin historial, tope ----------

def test_enter_no_permitido(casos):
    """Enter en el botón de enviar, en un campo, en un encabezado o antes de la primera
    parada: no se ejecuta, no cuenta y no queda en la trayectoria."""
    with pytest.raises(AccionNoPermitida):
        casos.pulsar("Enter")  # cursor antes de la primera parada
    for objetivo in ("Correo electrónico", "Enviar"):  # F: Trámites, Correo, Enviar
        _hasta(casos, "F", objetivo)
        antes = (casos.pulsaciones, len(casos.trayectoria))
        with pytest.raises(AccionNoPermitida):
            casos.pulsar("Enter")
        assert (casos.pulsaciones, len(casos.trayectoria)) == antes
    emu = Emulador(casos.paradas)
    emu.pulsar("H")
    with pytest.raises(AccionNoPermitida):
        emu.pulsar("Enter")


def test_volver_sin_historial(casos):
    paso = casos.pulsar("volver")
    assert not paso.se_movio and paso.anuncio == "no hay página anterior"
    assert paso.pulsaciones == 1 and casos.cursor == -1


def test_tope_pulsaciones(casos):
    """Con tope 5 se ejecutan 5 pulsaciones; la 6.ª no se ejecuta y la tarea queda No
    evaluable con 5 consumidas. Después, cualquier tecla lanza SesionTerminada."""
    emu = Emulador(casos.paradas, tope_pulsaciones=5)
    for _ in range(5):
        assert emu.pulsar("flecha").no_evaluable is None
    paso = emu.pulsar("flecha")
    assert paso.no_evaluable == "tope_pulsaciones" and paso.pulsaciones == 5
    assert emu.no_evaluable.motivo == "tope_pulsaciones"
    assert emu.no_evaluable.pulsaciones == 5 and emu.cursor == 4
    assert emu.trayectoria[-1] == paso
    with pytest.raises(SesionTerminada):
        emu.pulsar("flecha")


def test_elegir_de_lista(casos):
    """Lista de elementos (NVDA+F7): 1 + posición (empieza en el primero, orden del documento).
    Cada pulsación es un paso de la trayectoria."""
    pasos = casos.elegir_de_lista("enlaces", 1)  # K_ANTES: el 2.º enlace es "Directorio"
    assert [p.tecla for p in pasos] == ["lista_enlaces", "flecha_lista"]
    assert casos.paradas[casos.cursor].nombre == "Directorio"
    assert casos.pulsaciones == 2
    pasos = casos.elegir_de_lista("encabezados", 0)  # HTML: el 1.º es el h1
    assert len(pasos) == 1 and casos.paradas[casos.cursor].nombre == "Casos de navegación"
    assert casos.pulsaciones == 3
    with pytest.raises(IndexError):
        casos.elegir_de_lista("enlaces", len(K_ANTES))


# ---------- En vivo: Enter en enlace, volver, profundidad ----------

def test_enter_enlace_navega_y_volver(vivo):
    emu = vivo("cadena_0.html")
    assert emu.profundidad == 0 and emu.url.endswith("/cadena_0.html")
    _hasta(emu, "K", "Siguiente")  # HTML: h1 + enlace → el enlace es la parada 1
    paso = emu.pulsar("Enter")
    assert paso.anuncio == "Cadena 1"  # HTML: <title> de cadena_1
    assert paso.parada is None and emu.cursor == -1  # cursor antes de la primera parada
    assert paso.profundidad == 1 and emu.profundidad == 1 and paso.pulsaciones == 2
    assert emu.url.endswith("/cadena_1.html") and paso.url == emu.url
    assert [p.nombre for p in emu.paradas] == ["Cadena 1", "Siguiente"]

    capturas = emu.navegador.capturas
    paso = emu.pulsar("volver")
    assert paso.anuncio == "Cadena 0" and paso.pulsaciones == 3
    assert emu.profundidad == 0 and emu.cursor == 1  # en el enlace que se activó
    assert emu.url.endswith("/cadena_0.html")
    assert emu.navegador.capturas == capturas  # volver no recaptura


def test_profundidad_maxima(vivo):
    """Niveles 1, 2 y 3 se permiten; el Enter que lleva al nivel 4 se ejecuta, cuenta, y deja
    la tarea No evaluable sin mostrar esa página."""
    assert PROFUNDIDAD_MAX == 3
    emu = vivo("cadena_0.html")
    for nivel in (1, 2, 3):
        emu.pulsar("K")
        paso = emu.pulsar("Enter")
        assert paso.anuncio == f"Cadena {nivel}" and emu.profundidad == nivel
    assert emu.pulsaciones == 6
    emu.pulsar("K")
    paso = emu.pulsar("Enter")
    assert paso.no_evaluable == "profundidad" and paso.pulsaciones == 8
    assert emu.no_evaluable.motivo == "profundidad" and emu.no_evaluable.pulsaciones == 8
    assert emu.profundidad == 3 and emu.url.endswith("/cadena_3.html") and emu.cursor == 1
    with pytest.raises(SesionTerminada):
        emu.pulsar("flecha")


def test_profundidad_es_de_pila(vivo):
    """Ir y volver no acumula profundidad: lo que se limita es la distancia a la entrada."""
    emu = vivo("cadena_0.html")
    for _ in range(5):
        emu.pulsar("K")  # 2.ª vuelta en adelante: no hay más enlaces, cuenta 1 y no se mueve
        emu.pulsar("Enter")
        assert emu.profundidad == 1
        emu.pulsar("volver")
        assert emu.profundidad == 0 and emu.cursor == 1
    assert emu.no_evaluable is None and emu.pulsaciones == 15


def test_arboles_guardados(vivo, tmp_path):
    emu = vivo("cadena_0.html", carpeta=tmp_path)
    emu.pulsar("K")
    emu.pulsar("Enter")
    assert sorted(p.name for p in tmp_path.glob("*_arbol_ax.json")) == [
        "00_arbol_ax.json", "01_arbol_ax.json"]


# ---------- En vivo: misma página (fragmento, expandir, pestañas) ----------

def test_saltar_al_contenido(vivo):
    """Bypass: Enter en "Saltar al contenido" cuesta 1 y deja el cursor en el contenido.
    Si saliera caro, el emulador castigaría justo lo que axe pide (regla bypass)."""
    emu = vivo("casos_navegacion.html")
    antes = emu.paradas
    emu.pulsar("K")
    paso = emu.pulsar("Enter")
    assert paso.parada == I_CONTENIDO and paso.pulsaciones == 2
    assert paso.anuncio == "encabezado nivel 2, Contenido"
    assert emu.profundidad == 0 and emu.paradas is antes  # sin recaptura ni nivel nuevo


def test_expandir_submenu_y_volver(vivo):
    emu = vivo("casos_navegacion.html")
    url = emu.url
    _hasta(emu, "F", "Trámites")
    paso = emu.pulsar("Enter")
    assert paso.anuncio == ANUNCIOS["boton_expandido"] and paso.parada == I_BOTON
    assert paso.pulsaciones == 2 and emu.profundidad == 0 and emu.url == url
    assert _tuplas(emu.paradas) == CASOS_NAV_EXPANDIDO
    expandido = emu.paradas

    # K tras expandir no se detiene en menuitem (la lista de enlaces no cuesta: es la misma
    # secuencia que K desde el inicio).
    assert [p.nombre for p in emu.lista_elementos("enlaces")] == K_EXPANDIDO

    anuncios = [emu.pulsar("flecha").anuncio for _ in range(5)]
    assert anuncios[0] == "enlace, Licencias de construcción"
    assert anuncios[2:] == [ANUNCIOS["menuitem"], ANUNCIOS["menuitemcheckbox"],
                            ANUNCIOS["menuitemradio"]]
    assert emu.paradas is expandido  # flecha no recaptura

    # Enlace normal del submenú: navega; al volver, el árbol sigue expandido y el cursor
    # queda en el enlace. F(1) + Enter(2) + flecha(3) + Enter(4) + volver(5).
    emu = vivo("casos_navegacion.html")
    _hasta(emu, "F", "Trámites")
    emu.pulsar("Enter")
    expandido = emu.paradas
    emu.pulsar("flecha")  # "Licencias de construcción" (parada 3)
    paso = emu.pulsar("Enter")
    assert paso.anuncio == "Destino del menú" and emu.profundidad == 1
    paso = emu.pulsar("volver")
    assert paso.pulsaciones == 5 and emu.cursor == I_BOTON + 1
    assert emu.paradas is expandido and emu.paradas[I_BOTON].expandido is True


def test_colapsar(vivo):
    emu = vivo("casos_navegacion.html")
    _hasta(emu, "F", "Trámites")
    emu.pulsar("Enter")
    paso = emu.pulsar("Enter")
    assert paso.anuncio == ANUNCIOS["boton_contraido"] and emu.cursor == I_BOTON
    assert _tuplas(emu.paradas) == CASOS_NAV_ANTES


def test_menuitem_navega_por_href(vivo):
    """El <a role="menuitem" href> no trae url en el árbol (comprobado 20-oct): la URL se lee
    del href del DOM."""
    emu = vivo("casos_navegacion.html")
    _hasta(emu, "F", "Trámites")
    emu.pulsar("Enter")
    for _ in range(3):  # Licencias, Pagos, Catastro
        emu.pulsar("flecha")
    assert emu.paradas[emu.cursor].rol == "menuitem"
    paso = emu.pulsar("Enter")
    assert paso.anuncio == "Destino del menú" and emu.profundidad == 1
    assert paso.pulsaciones == 6 and emu.url.endswith("/destino_menu.html")


def test_pestana(vivo):
    """Enter en una pestaña no seleccionada la selecciona sin cambiar de página; después Tab
    se detiene en la nueva seleccionada y salta las demás."""
    emu = vivo("casos_navegacion.html")
    _hasta(emu, "H", "Pestañas")  # h1, Contenido, Pestañas = 3
    emu.pulsar("flecha")
    emu.pulsar("flecha")  # Sábado (parada 7)
    paso = emu.pulsar("Enter")
    assert paso.anuncio == "pestaña, Sábado, seleccionada" and paso.parada == 7
    assert paso.pulsaciones == 6 and emu.profundidad == 0
    assert [p.seleccionado for p in emu.paradas[6:9]] == [False, True, False]
    assert emu.paradas[9].nombre == "De 9:00 a 13:00 horas."  # HTML: panel del sábado
    assert len(emu.paradas) == len(CASOS_NAV_ANTES)
    paso = emu.pulsar("Tab")  # Domingo no está seleccionada: sigue el switch
    assert emu.paradas[paso.parada].rol == "switch"


# ---------- En vivo: documentos (tarea C) ----------

@pytest.mark.parametrize("pagina,capa_texto", [
    ("perfecta.html", True),  # yaml: "El PDF tiene texto"
    ("pdf_escaneado.html", False),  # yaml: "el PDF es solo una imagen escaneada"
])
def test_pdf(vivo, pagina, capa_texto, tmp_path):
    """Enter en el enlace al PDF: no se abre visor; se descargan los bytes por la misma
    sesión y se registra si tiene capa de texto. No apila nivel; el cursor queda en el enlace.
    El veredicto (completable / cierre roto) es de 3D."""
    emu = vivo(pagina, carpeta=tmp_path)
    pasos = emu.elegir_de_lista("enlaces", ENLACES_PERFECTA - 1)
    assert len(pasos) == ENLACES_PERFECTA
    enlace = emu.cursor
    assert emu.paradas[enlace].nombre == "Plan Municipal de Desarrollo (PDF)"
    paso = emu.pulsar("Enter")
    doc = paso.documento
    assert doc.es_pdf and doc.capa_texto is capa_texto
    assert doc.paginas == 1  # tests/paginas/generar_pdfs.py: una página Letter
    assert doc.url.endswith(".pdf") and doc.error is None
    assert paso.pulsaciones == ENLACES_PERFECTA + 1  # = friccion_esperada de C (yaml: 5)
    assert emu.profundidad == 0 and emu.cursor == enlace
    assert len(list(tmp_path.glob("*.pdf"))) == 1  # evidencia guardada


def test_descarga_usa_la_misma_sesion(servidor, chromium):
    """El PDF exige una cookie (conftest: /con_cookie/): los bytes se piden con las cookies del
    contexto de navegación. Sin la cookie el servidor responde 403 y es una página, no un PDF."""
    from src.emulador import Documento, Pagina
    from src.navegador import NavegadorEnVivo

    url = servidor + "con_cookie/docs/plan_municipal.pdf"
    nav = NavegadorEnVivo(chromium, timeout_ms=5_000, espera_ms=0, pausa_s=0)
    try:
        sin_cookie = nav.abrir(url)
        assert isinstance(sin_cookie, Pagina) and sin_cookie.estado_http == 403
        nav.contexto.add_cookies([{"name": "sesion", "value": "ok", "url": servidor}])
        doc = nav.abrir(url)
        assert isinstance(doc, Documento) and doc.es_pdf and doc.capa_texto is True
    finally:
        nav.cerrar()


# ---------- En vivo: fallas simuladas ----------

def test_timeout_en_enter(vivo):
    emu = vivo("fallas.html", timeout_ms=1_000)
    _hasta(emu, "K", "Página lenta")
    paso = emu.pulsar("Enter")
    assert paso.no_evaluable == "timeout" and paso.pulsaciones == 2  # el Enter cuenta
    assert emu.no_evaluable.motivo == "timeout" and emu.no_evaluable.pulsaciones == 2
    assert emu.profundidad == 0


def test_timeout_en_entrada(vivo):
    emu = vivo("lento/perfecta.html", timeout_ms=1_000)
    assert emu.no_evaluable.motivo == "timeout" and emu.no_evaluable.pulsaciones == 0
    assert emu.trayectoria[-1].no_evaluable == "timeout"


def test_captcha_se_registra_y_no_detiene(vivo):
    emu = vivo("fallas.html")
    assert emu.captcha == ()
    _hasta(emu, "K", "Verificación")
    paso = emu.pulsar("Enter")
    assert set(paso.captcha) == MARCADORES_CAPTCHA and set(emu.captcha) == MARCADORES_CAPTCHA
    assert emu.no_evaluable is None and emu.profundidad == 1
    assert emu.pulsar("H").anuncio == "encabezado nivel 1, Verificación de seguridad"


def test_404_no_es_no_evaluable(vivo):
    """Un enlace roto es un hallazgo del sitio, no una falla técnica de Atorapp."""
    emu = vivo("fallas.html")
    _hasta(emu, "K", "Página inexistente")
    paso = emu.pulsar("Enter")
    assert paso.estado_http == 404 and emu.no_evaluable is None and emu.profundidad == 1


def test_redireccion(vivo):
    emu = vivo("fallas.html")
    _hasta(emu, "K", "Redirección")
    paso = emu.pulsar("Enter")
    assert paso.url.endswith("/perfecta.html") and paso.estado_http == 200
    assert len(emu.paradas) == PARADAS_PERFECTA
