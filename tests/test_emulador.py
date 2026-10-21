"""Fase 3A: emulador núcleo sobre árboles de accesibilidad ya capturados.

Todos los valores esperados de este archivo se escribieron A MANO, ANTES de implementar el
emulador, y NO se tomaron de su salida. Cada uno cita su fuente:
  - "yaml": lo documentan los comentarios o las razones de los .esperado.yaml;
  - "HTML": los yaml no lo documentan; se dedujo leyendo el HTML de la página.

Reglas que se prueban (ver CLAUDE.md y src/emulador.py):
  - Parada = encabezado, enlace, botón, campo, imagen (con o sin nombre) o texto suelto.
    El texto dentro de una parada se funde en su nombre. 1 StaticText = 1 parada (D3).
  - El cursor empieza ANTES de la primera parada. Cada tecla = 1 pulsación.
  - F incluye botones (D2). Sin "siguiente": no se mueve, no da la vuelta, cuenta 1 (D1).
"""

from pathlib import Path

import pytest
import yaml

from src.captura import capturar, nombre_carpeta
from src.emulador import Emulador, aplanar, normalizar

PAGINAS = Path(__file__).parent / "paginas"
CARPETA_CAPTURAS = Path(__file__).resolve().parent.parent / "capturas"
NOMBRES = [
    "perfecta",
    "sin_encabezados",
    "sin_contacto",
    "enlaces_ambiguos",
    "formulario_sin_etiquetas",
    "pdf_escaneado",
]


def _ruta_arbol(nombre):
    """Árbol de la captura más reciente en capturas/; captura de nuevo si no hay o si es
    más vieja que el .html (así nunca se prueba contra un árbol desactualizado)."""
    html = PAGINAS / f"{nombre}.html"
    url = html.resolve().as_uri()
    carpeta = CARPETA_CAPTURAS / nombre_carpeta(url)
    candidatas = sorted(carpeta.glob("*/arbol_ax.json")) if carpeta.exists() else []
    if candidatas and candidatas[-1].stat().st_mtime >= html.stat().st_mtime:
        return candidatas[-1]
    return capturar(url, base=CARPETA_CAPTURAS) / "arbol_ax.json"


@pytest.fixture(scope="module")
def arboles():
    return {n: _ruta_arbol(n) for n in NOMBRES + ["casos_emulador"]}


def _emu(arboles, nombre):
    return Emulador.desde_archivo(arboles[nombre])


def _recorrer_tecla(emu, tecla):
    """Pulsa `tecla` hasta que ya no haya siguiente; devuelve las paradas visitadas."""
    visitadas = []
    while True:
        paso = emu.pulsar(tecla)
        if not paso.se_movio:
            return visitadas
        visitadas.append(emu.paradas[paso.parada])


# ---------- Valores esperados (escritos a mano) ----------

H_PERFECTA = [  # yaml (comentario de perfecta); niveles: HTML
    (1, "Ayuntamiento de Villa Ejemplo"), (2, "Noticias"), (2, "Trámites"),
    (3, "Licencia de construcción menor"), (2, "Descargas"), (2, "Contacto"),
    (3, "Envíanos un mensaje"),
]
ESPERADO_H = {
    "perfecta": H_PERFECTA,
    "formulario_sin_etiquetas": H_PERFECTA,  # HTML: misma estructura que perfecta
    "pdf_escaneado": H_PERFECTA,  # HTML: misma estructura que perfecta
    "sin_encabezados": [],  # yaml: "Sin encabezados ni landmarks"
    "enlaces_ambiguos": [  # yaml: "h1, Noticias, Trámites, Descargas, Contacto, Envíanos..."
        (1, "Ayuntamiento de Villa Ejemplo"), (2, "Noticias"), (2, "Trámites"),
        (2, "Descargas"), (2, "Contacto"), (3, "Envíanos un mensaje"),
    ],
    "sin_contacto": [  # HTML: sin sección Contacto ni h3; termina en "Solicitud de cita"
        (1, "Ayuntamiento de Villa Ejemplo"), (2, "Noticias"), (2, "Trámites"),
        (3, "Licencia de construcción menor"), (2, "Descargas"), (2, "Solicitud de cita"),
    ],
}

MENU = ["Inicio", "Gobierno", "Transparencia"]
PDF = "Plan Municipal de Desarrollo (PDF)"
TARJETAS = [  # HTML: nombre de cada una de las 12 tarjetas, en orden
    "Leer más", "clic aquí", "Leer más", "clic aquí", "Leer más", "Leer más",
    "Leer más", "clic aquí", "Leer más", "Leer más", "clic aquí", "Leer más",
]
ESPERADO_K = {
    # yaml (razón de C: el PDF es el 4.º, tras los 3 del menú) + HTML (no hay más enlaces)
    **{n: MENU + [PDF] for n in NOMBRES if n != "enlaces_ambiguos"},
    # yaml: "menú (3), 12 tarjetas, PDF, 3 íconos sin nombre"; nombres de tarjetas: HTML
    "enlaces_ambiguos": MENU + TARJETAS + [PDF, "", "", ""],
}

D_PERFECTA = [  # HTML: header, nav con nombre, main, 4 section con nombre, footer.
    # El <form> no tiene nombre: no es landmark (ARIA).
    ("banner", ""), ("navigation", "Principal"), ("main", ""), ("region", "Noticias"),
    ("region", "Trámites"), ("region", "Descargas"), ("region", "Contacto"),
    ("contentinfo", ""),
]
ESPERADO_D = {
    "perfecta": D_PERFECTA,
    "formulario_sin_etiquetas": D_PERFECTA,  # HTML
    "pdf_escaneado": D_PERFECTA,  # HTML
    "enlaces_ambiguos": D_PERFECTA,  # HTML
    "sin_contacto": [  # HTML
        ("banner", ""), ("navigation", "Principal"), ("main", ""), ("region", "Noticias"),
        ("region", "Trámites"), ("region", "Descargas"), ("region", "Solicitud de cita"),
        ("contentinfo", ""),
    ],
    "sin_encabezados": [],  # yaml: "Sin encabezados ni landmarks"
}

F_PERFECTA = [  # yaml (ruta de D: los 3 campos) + HTML (el botón, porque F incluye botones)
    ("textbox", "Nombre completo"), ("textbox", "Correo electrónico"),
    ("textbox", "Mensaje"), ("button", "Enviar mensaje"),
]
ESPERADO_F = {
    "perfecta": F_PERFECTA,
    "sin_encabezados": F_PERFECTA,
    "enlaces_ambiguos": F_PERFECTA,
    "pdf_escaneado": F_PERFECTA,
    "sin_contacto": [  # yaml (ruta de D) + HTML (botón)
        ("textbox", "Nombre completo"), ("combobox", "Trámite"),
        ("textbox", "Fecha preferida"), ("button", "Solicitar cita"),
    ],
    "formulario_sin_etiquetas": [  # yaml (ruta de D: campos sin nombre) + HTML (botón)
        ("textbox", ""), ("textbox", ""), ("textbox", ""), ("button", "Enviar mensaje"),
    ],
}

ESPERADO_N_PARADAS = {
    "perfecta": 44,  # yaml: "Página de referencia: 44 paradas"
    "sin_contacto": 42,  # yaml: leer de corrido hasta el fin = 42
    "sin_encabezados": 44,  # HTML: mismas paradas que perfecta (divs en vez de h/landmarks)
    "formulario_sin_etiquetas": 44,  # HTML: el <span> rótulo ocupa el lugar del <label>
    "pdf_escaneado": 44,  # HTML: igual que perfecta
    # HTML: 1 + 3 + 20 + (1 + 12×3) + 2 + 3 + 6 + 1 + 3 íconos + 1 pie = 77
    "enlaces_ambiguos": 77,
}

# yaml (comentario de sin_encabezados): "título (1), menú (3), noticias (20), trámites (7),
# descargas (2), contacto (2), ..." → índice (desde 0) donde empieza cada bloque.
SIN_ENCABEZADOS_BLOQUES = {
    0: "Ayuntamiento de Villa Ejemplo", 1: "Inicio", 4: "Noticias", 24: "Trámites",
    31: "Descargas", 33: "Contacto", 34: "Teléfono: 667 555 0142",
}

TAB_PERFECTA = (  # HTML: enfocables en orden del documento
    [("link", n) for n in MENU + [PDF]]
    + [("textbox", "Nombre completo"), ("textbox", "Correo electrónico"),
       ("textbox", "Mensaje"), ("button", "Enviar mensaje")]
)

# HTML de casos_emulador.html: (rol, nombre, nivel, enfocable, landmarks que empiezan aquí)
CASOS_PARADAS = [
    ("heading", "Casos límite del emulador", 1, False, (("banner", ""),)),  # <em> fundido
    ("heading", "Texto fundido", 2, False, (("main", ""), ("region", "Región anidada"))),
    ("link", "Enlace con texto anidado", None, True, ()),  # <strong> fundido
    ("button", "Botón con texto anidado", None, True, ()),  # <span> fundido
    # (aria-hidden: ni "Texto oculto..." ni "Enlace oculto" son paradas)
    ("link", "Nombre con espacios", None, True, ()),  # aria-label normalizado
    ("StaticText", "Texto con espacios de sobra", None, False, ()),
    ("StaticText", "Llame al", None, False, ()),  # D3: párrafo partido en 3 paradas
    ("link", "667 555 0142", None, True, ()),
    ("StaticText", "en horario de oficina.", None, False, ()),
    ("heading", "Imágenes", 2, False, (("region", "Imágenes"),)),
    ("image", "Escudo municipal", None, False, ()),  # con alt
    ("image", "", None, False, ()),  # sin alt: parada sin nombre
    # (alt="": no es parada)
    ("heading", "Foco", 2, False, (("region", "Foco"),)),
    # tabindex="-1": PREDICCIÓN, el árbol lo marca enfocable (Tab llegaría; limitación)
    ("link", "Enlace fuera del orden de tabulación", None, True, ()),
    ("link", "Enlace normal", None, True, ()),
    ("StaticText", "Acepto", None, False, (("form", "Formulario de prueba"),)),
    ("checkbox", "Acepto", None, True, ()),
    ("button", "Botón del formulario", None, True, ()),
    ("StaticText", "Pie", None, False, (("contentinfo", ""),)),
]


# ---------- Aplanado (paso 1) ----------

def test_normalizar():
    assert normalizar("  a   b \t c  ") == "a b c"
    assert normalizar("") == ""


@pytest.mark.xfail(strict=True, reason=(
    "DISCREPANCIA pendiente de decisión (20-oct): Chromium ignora el <label> de la casilla "
    "(ignoredReasons: labelFor), así que 'Acepto' no sale como texto suelto; en los textbox "
    "el <label> sí sale como LabelText. Las otras 18 paradas coinciden. El valor esperado "
    "no se cambia hasta decidir si el error está en él o en el emulador."))
def test_casos_emulador_paradas(arboles):
    paradas = _emu(arboles, "casos_emulador").paradas
    obtenido = [(p.rol, p.nombre, p.nivel, p.enfocable, p.landmarks) for p in paradas]
    assert obtenido == CASOS_PARADAS
    assert [p.indice for p in paradas] == list(range(len(paradas)))
    assert all(p.id_nodo for p in paradas)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_conteo_paradas(nombre, arboles):
    paradas = _emu(arboles, nombre).paradas
    assert len(paradas) == ESPERADO_N_PARADAS[nombre]
    roles = {p.rol for p in paradas}
    assert not roles & {"InlineTextBox", "ListMarker"}
    assert all(p.nombre == normalizar(p.nombre) for p in paradas)
    assert all(p.rol != "StaticText" or p.nombre for p in paradas)  # sin textos vacíos


def test_bloques_sin_encabezados(arboles):
    paradas = _emu(arboles, "sin_encabezados").paradas
    for i, nombre in SIN_ENCABEZADOS_BLOQUES.items():
        assert paradas[i].nombre == nombre, i


# ---------- Teclas (paso 2) ----------

@pytest.mark.parametrize("nombre", NOMBRES)
def test_secuencia_H(nombre, arboles):
    vistas = _recorrer_tecla(_emu(arboles, nombre), "H")
    assert all(p.rol == "heading" for p in vistas)
    assert [(p.nivel, p.nombre) for p in vistas] == ESPERADO_H[nombre]


@pytest.mark.parametrize("nombre", NOMBRES)
def test_secuencia_K(nombre, arboles):
    vistas = _recorrer_tecla(_emu(arboles, nombre), "K")
    assert all(p.rol == "link" for p in vistas)
    assert [p.nombre for p in vistas] == ESPERADO_K[nombre]


@pytest.mark.parametrize("nombre", NOMBRES)
def test_secuencia_D(nombre, arboles):
    emu = _emu(arboles, nombre)
    vistos = []
    while (paso := emu.pulsar("D")).se_movio:
        vistos.append(paso.landmark)
    assert vistos == ESPERADO_D[nombre]


def test_D_landmarks_anidados(arboles):
    """main y la región Noticias empiezan en la misma parada: son 2 pulsaciones de D."""
    emu = _emu(arboles, "perfecta")
    pasos = [emu.pulsar("D") for _ in range(4)]
    assert pasos[2].parada == pasos[3].parada
    assert emu.paradas[pasos[3].parada].nombre == "Noticias"
    assert pasos[3].pulsaciones == 4


@pytest.mark.parametrize("nombre", NOMBRES)
def test_secuencia_F(nombre, arboles):
    vistas = _recorrer_tecla(_emu(arboles, nombre), "F")
    assert [(p.rol, p.nombre) for p in vistas] == ESPERADO_F[nombre]


def test_F_casos_emulador(arboles):
    """F incluye botones aunque no estén en un formulario (D2); no incluye imágenes."""
    vistas = _recorrer_tecla(_emu(arboles, "casos_emulador"), "F")
    assert [(p.rol, p.nombre) for p in vistas] == [
        ("button", "Botón con texto anidado"), ("checkbox", "Acepto"),
        ("button", "Botón del formulario"),
    ]


def test_tab(arboles):
    vistas = _recorrer_tecla(_emu(arboles, "perfecta"), "Tab")
    assert [(p.rol, p.nombre) for p in vistas] == TAB_PERFECTA


def test_flecha_y_leer_de_corrido(arboles):
    emu = _emu(arboles, "perfecta")
    assert emu.cursor == -1
    paso = emu.pulsar("flecha")
    assert (paso.parada, paso.pulsaciones) == (0, 1)
    pasos = emu.leer_de_corrido(3)
    assert [p.parada for p in pasos] == [1, 2, 3]
    assert all(p.tecla == "leer" for p in pasos)
    assert emu.pulsaciones == 4
    resto = emu.leer_de_corrido()  # hasta el final, sin pulsar de más
    assert len(resto) == 44 - 4
    assert emu.cursor == 43 and emu.pulsaciones == 44


def test_anuncios(arboles):
    emu = _emu(arboles, "casos_emulador")
    anuncios = [emu.pulsar("flecha").anuncio for _ in range(len(CASOS_PARADAS))]
    assert anuncios[0] == "encabezado nivel 1, Casos límite del emulador"
    assert anuncios[2] == "enlace, Enlace con texto anidado"
    assert anuncios[3] == "botón, Botón con texto anidado"
    assert anuncios[5] == "Texto con espacios de sobra"  # texto suelto: solo el texto
    assert anuncios[10] == "gráfico, Escudo municipal"
    assert anuncios[11] == "gráfico"  # imagen sin alt
    # La casilla se alcanza con F (2.º campo según la secuencia escrita a mano), no por
    # índice: el índice depende de la discrepancia del <label> (ver xfail arriba).
    emu = _emu(arboles, "casos_emulador")
    emu.pulsar("F")
    assert emu.pulsar("F").anuncio == "casilla de verificación, Acepto"

    assert _emu(arboles, "formulario_sin_etiquetas").pulsar("F").anuncio == "edición"
    emu = _emu(arboles, "sin_contacto")
    emu.pulsar("F")
    assert emu.pulsar("F").anuncio == "cuadro combinado, Trámite"

    emu = _emu(arboles, "casos_emulador")
    assert emu.pulsar("D").anuncio == (
        "banner, punto de referencia; encabezado nivel 1, Casos límite del emulador")
    emu.pulsar("D")
    assert emu.pulsar("D").anuncio == (
        "región Región anidada, punto de referencia; encabezado nivel 2, Texto fundido")


def test_lista_elementos(arboles):
    emu = _emu(arboles, "perfecta")
    emu.pulsar("H")
    antes = (emu.cursor, emu.pulsaciones, list(emu.trayectoria))
    assert [p.nombre for p in emu.lista_elementos("enlaces")] == ESPERADO_K["perfecta"]
    assert [(p.nivel, p.nombre) for p in emu.lista_elementos("encabezados")] == H_PERFECTA
    assert (emu.cursor, emu.pulsaciones, list(emu.trayectoria)) == antes  # costo: 3C


def test_trayectoria_reproducible(arboles):
    teclas = ["H", "H", "K", "flecha", "D", "F", "Tab"]
    trayectorias = []
    for _ in range(2):
        emu = _emu(arboles, "perfecta")
        for t in teclas:
            emu.pulsar(t)
        trayectorias.append(emu.trayectoria)
    assert trayectorias[0] == trayectorias[1]
    assert [p.tecla for p in trayectorias[0]] == teclas
    assert [p.pulsaciones for p in trayectorias[0]] == list(range(1, len(teclas) + 1))


# ---------- Sin "siguiente" (D1, aprobada) ----------

def test_no_hay_siguiente_H(arboles):
    emu = _emu(arboles, "perfecta")
    for _ in range(7):
        emu.pulsar("H")
    ultimo = emu.cursor
    paso = emu.pulsar("H")
    assert not paso.se_movio and paso.anuncio == "no hay más encabezados"
    assert paso.parada == ultimo == emu.cursor  # no se mueve ni da la vuelta
    assert emu.paradas[ultimo].nombre == "Envíanos un mensaje"
    assert paso.pulsaciones == 8  # la pulsación sí cuenta


def test_no_hay_siguiente_desde_el_inicio(arboles):
    emu = _emu(arboles, "sin_encabezados")
    paso = emu.pulsar("D")
    assert not paso.se_movio and paso.parada is None and emu.cursor == -1
    assert paso.anuncio == "no hay más puntos de referencia" and paso.pulsaciones == 1


def test_no_hay_siguiente_flecha_y_tab(arboles):
    # perfecta: 44 paradas (yaml); la última es el pie y el último enfocable es el botón.
    emu = _emu(arboles, "perfecta")
    emu.leer_de_corrido()
    n = ESPERADO_N_PARADAS["perfecta"]
    paso = emu.pulsar("flecha")
    assert not paso.se_movio and paso.anuncio == "fin del documento"
    assert paso.parada == n - 1 and paso.pulsaciones == n + 1
    paso = emu.pulsar("Tab")  # después del último enfocable
    assert not paso.se_movio and paso.anuncio == "fin de los elementos enfocables"
    assert paso.pulsaciones == n + 2


def test_leer_n_mas_alla_del_final(arboles):
    """leer_de_corrido(n) pulsa n veces: las que pasan del final cuentan y no mueven (D1)."""
    emu = _emu(arboles, "perfecta")
    n = ESPERADO_N_PARADAS["perfecta"]
    pasos = emu.leer_de_corrido(n + 2)
    assert [p.se_movio for p in pasos[-3:]] == [True, False, False]
    assert emu.pulsaciones == n + 2


# ---------- Rutas de los .esperado.yaml (paso 4) ----------

def _yaml(nombre):
    return yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))


RUTAS = [(n, t) for n in NOMBRES for t in "ABCD"]
MOTIVO_SKIP = {
    "C": "3B: el Enter abre el PDF y el cierre se evalúa al llegar (y el costo de la lista "
         "de enlaces es de 3C)",
    "B_enlaces_ambiguos": "3B: la ruta cruza a enlaces_ambiguos_tramite.html",
}


def _avanzar_hasta(emu, tecla, rol, nombre):
    """Pulsa `tecla` hasta que el cursor quede en la parada (rol, nombre) de la ruta."""
    while True:
        paso = emu.pulsar(tecla)
        assert paso.se_movio, f"{tecla}: no se encontró {rol} '{nombre}'"
        p = emu.paradas[paso.parada]
        if (p.rol, p.nombre) == (rol, nombre):
            return


def recorrer_ruta(emu, ruta):
    """Reproduce una ruta de un .esperado.yaml sobre el emulador; devuelve las pulsaciones."""
    for paso in ruta:
        tecla = paso["tecla"]
        if tecla in ("H", "K", "F"):
            _avanzar_hasta(emu, tecla, paso["rol"], paso["nombre"])
        elif tecla in ("leer", "leer_de_corrido"):
            hasta = paso.get("hasta", paso)
            if hasta == "fin":
                emu.leer_de_corrido()
            else:
                _avanzar_hasta(emu, "flecha", hasta["rol"], hasta["nombre"])
        else:
            raise AssertionError(f"Tecla fuera de 3A: {tecla}")
    return emu.pulsaciones


@pytest.mark.parametrize("nombre,tarea", RUTAS, ids=[f"{n}-{t}" for n, t in RUTAS])
def test_rutas_yaml(nombre, tarea, arboles):
    if tarea == "C":
        pytest.skip(MOTIVO_SKIP["C"])
    if (nombre, tarea) == ("enlaces_ambiguos", "B"):
        pytest.skip(MOTIVO_SKIP["B_enlaces_ambiguos"])
    t = _yaml(nombre)["tareas"][tarea]
    emu = _emu(arboles, t["entrada"].removesuffix(".html"))
    assert recorrer_ruta(emu, t["ruta"]) == t["friccion_esperada"]
