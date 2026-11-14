"""Fase 3E.3: la interfaz de una herramienta de accesibilidad tiene que ser accesible.

Abre interfaz/index.html por file:// (como con doble clic), con TODA petición que no sea file://
bloqueada y registrada, y corre axe-core 4.14.0 (vendor/, el mismo del estudio) con todas sus reglas
no experimentales (WCAG A/AA y buenas prácticas). Meta: 0 violaciones en cada vista y en cada estado
del reproductor. Revisa además teclado, foco, encabezados y que no se pida nada a la red.

Usa el interfaz/datos.js versionado: lo que se prueba es lo que se muestra.
"""

import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
INDEX = (RAIZ / "interfaz" / "index.html").as_uri()
AXE_JS = RAIZ / "vendor" / "axe-core" / "axe.min.js"


def _datos() -> dict:
    texto = (RAIZ / "interfaz" / "datos.js").read_text(encoding="utf-8")
    return json.loads(texto[texto.index("=") + 1:texto.rstrip().rindex(";")])


DATOS = _datos()
TAREAS = ([("real", t["sitio"], t["tarea"], t) for t in DATOS["reales"]]
          + [("prueba", t["sitio"], t["tarea"], t) for t in DATOS["prueba"]])


@pytest.fixture(scope="module")
def pagina(chromium):
    contexto = chromium.new_context(viewport={"width": 1366, "height": 768})
    pg = contexto.new_page()
    pg.peticiones_externas = []
    pg.errores = []

    def filtrar(ruta):
        if ruta.request.url.startswith("file:"):
            ruta.continue_()
        else:
            pg.peticiones_externas.append(ruta.request.url)
            ruta.abort()

    pg.route("**/*", filtrar)
    pg.on("pageerror", lambda e: pg.errores.append(str(e)))
    pg.on("console", lambda m: pg.errores.append(m.text) if m.type == "error" else None)
    yield pg
    contexto.close()


def _ir(pg, hash_=""):
    # Carga limpia: un goto que solo cambia el # no recarga y dejaría el estado anterior.
    pg.goto("about:blank")
    pg.goto(INDEX + hash_)
    pg.wait_for_selector("#vista h1")


def _axe(pg) -> list[dict]:
    if not pg.evaluate("typeof window.axe !== 'undefined'"):
        pg.add_script_tag(content=AXE_JS.read_text(encoding="utf-8"))
    resultado = pg.evaluate("() => axe.run(document, {resultTypes: ['violations']})")
    assert resultado["testEngine"]["version"] == "4.14.0"
    return [{"regla": v["id"], "impacto": v["impact"], "nodos": [n["target"] for n in v["nodes"]]}
            for v in resultado["violations"]]


def _encabezados_en_orden(pg):
    niveles = pg.eval_on_selector_all("main h1, main h2, main h3, main h4",
                                      "hs => hs.map(h => Number(h.tagName[1]))")
    assert niveles.count(1) == 1, niveles
    assert niveles[0] == 1
    for antes, despues in zip(niveles, niveles[1:]):
        assert despues <= antes + 1, f"salto de h{antes} a h{despues}: {niveles}"


# ---------- Datos reales, sin red ----------

def test_abre_sin_red_y_sin_errores(pagina):
    _ir(pagina)
    _ir(pagina, "#comparacion")
    _ir(pagina, "#trayectoria/prueba/perfecta/A")
    assert pagina.peticiones_externas == []
    assert pagina.errores == []


def test_inicio_separa_reales_de_prueba(pagina):
    _ir(pagina)
    assert pagina.inner_text("h1") == "Qué concluye Atorapp"
    reales = pagina.locator("section[aria-labelledby='h-reales'] .tarjeta")
    prueba = pagina.locator("section[aria-labelledby='h-prueba'] .tarjeta")
    assert reales.count() == len(DATOS["reales"])
    assert prueba.count() == len(DATOS["prueba"]) == 24
    texto = pagina.inner_text("main")
    assert "Páginas de prueba (validación del método)" in texto
    assert "conformidad WCAG" not in texto
    assert "estima" in texto


def test_lo_que_falta_dice_pendiente(pagina):
    """En las páginas de prueba no hay NVDA: no se inventa, se ve 'Pendiente' en la trayectoria."""
    _ir(pagina, "#trayectoria/prueba/perfecta/A")
    assert "NVDA\nPendiente" in pagina.inner_text(".ficha")
    for grupo, sitio, tarea, t in TAREAS:
        if not t["pasos"]:
            _ir(pagina, f"#trayectoria/{grupo}/{sitio}/{tarea}")
            assert pagina.locator("#pasos").count() == 0
            assert "pendiente" in pagina.inner_text(".reproductor").lower()


def test_sin_auc(pagina):
    _ir(pagina, "#comparacion")
    texto = pagina.inner_text("main")
    assert "No se calcula el AUC" in texto
    assert not re.search(r"AUC\s*[=:]\s*\d", texto)


# ---------- axe: 0 violaciones ----------

def test_axe_si_detecta_un_defecto(pagina):
    """Control: el 0 de las demás pruebas no es porque axe no corra. Un botón sin nombre se detecta."""
    _ir(pagina)
    pagina.evaluate("document.querySelector('main').insertAdjacentHTML('beforeend', '<button></button>')")
    assert "button-name" in {v["regla"] for v in _axe(pagina)}


def test_axe_inicio_y_comparacion(pagina):
    for hash_ in ("", "#comparacion"):
        _ir(pagina, hash_)
        assert _axe(pagina) == [], hash_


@pytest.mark.parametrize("grupo,sitio,tarea", [(g, s, k) for g, s, k, _ in TAREAS],
                         ids=[f"{g}-{s}-{k}" for g, s, k, _ in TAREAS])
def test_axe_trayectoria(pagina, grupo, sitio, tarea):
    _ir(pagina, f"#trayectoria/{grupo}/{sitio}/{tarea}")
    assert _axe(pagina) == [], "al abrir"
    if pagina.locator("#b-siguiente").count():
        for _ in range(3):
            if pagina.is_enabled("#b-siguiente"):
                pagina.click("#b-siguiente")
        assert _axe(pagina) == [], "a mitad del recorrido"
        if pagina.is_enabled("#b-final"):
            pagina.click("#b-final")
        assert _axe(pagina) == [], "al final"


def test_axe_durante_la_reproduccion(pagina):
    _ir(pagina, "#trayectoria/prueba/sin_contacto/A")  # 42 pasos
    pagina.select_option("#velocidad", "rapida")
    pagina.click("#b-reproducir")
    pagina.wait_for_function("document.querySelector('#pasos li[aria-current=step]') !== null")
    assert pagina.inner_text("#b-reproducir") == "Pausar"
    assert _axe(pagina) == []
    pagina.click("#b-reproducir")
    assert pagina.inner_text("#b-reproducir") == "Reproducir"


# ---------- Teclado, foco y encabezados ----------

def test_encabezados_en_orden(pagina):
    for hash_ in ["", "#comparacion"] + [f"#trayectoria/{g}/{s}/{k}" for g, s, k, _ in TAREAS[:4]]:
        _ir(pagina, hash_)
        _encabezados_en_orden(pagina)


def test_primer_tab_es_saltar_al_contenido(pagina):
    _ir(pagina)
    pagina.keyboard.press("Tab")
    assert pagina.evaluate("document.activeElement.id") == "saltar"
    pagina.keyboard.press("Enter")
    assert pagina.evaluate("document.activeElement.tagName") == "H1"


def test_navegar_con_teclado_lleva_el_foco_al_h1(pagina):
    _ir(pagina)
    pagina.focus("nav a[data-vista='comparacion']")
    pagina.keyboard.press("Enter")
    pagina.wait_for_function("document.activeElement.tagName === 'H1' && location.hash === '#comparacion'")
    assert pagina.get_attribute("nav a[data-vista='comparacion']", "aria-current") == "page"


def test_tarjeta_se_abre_con_teclado(pagina):
    _ir(pagina)
    enlace = pagina.locator("section[aria-labelledby='h-prueba'] .tarjeta-enlace").first
    enlace.focus()
    pagina.keyboard.press("Enter")
    pagina.wait_for_function("document.activeElement.tagName === 'H1' && location.hash.startsWith('#trayectoria/')")
    assert "Tarea A" in pagina.inner_text("h1")


def test_reproductor_con_teclado_y_anuncio(pagina):
    _ir(pagina, "#trayectoria/prueba/perfecta/A")  # H×6, leer×1
    pagina.focus("#b-siguiente")
    pagina.keyboard.press("Space")
    pagina.keyboard.press("Enter")
    actual = pagina.locator("#pasos li[aria-current=step]")
    assert actual.get_attribute("data-i") == "1"
    assert "Paso 2 de 7" in pagina.inner_text("#vivo")
    assert "Tecla H" in pagina.inner_text("#vivo")
    pagina.focus("#deslizador")
    pagina.keyboard.press("End")
    assert pagina.locator("#pasos li[aria-current=step]").get_attribute("data-i") == "6"
    assert "Llegó al objetivo correcto" in pagina.inner_text("#ahora")
    assert pagina.is_disabled("#b-siguiente")


def test_identidad_visual(pagina):
    """Fase 3F.4: la fuente carga por file:// sin red, el foco es el anillo naranja del logo y el
    estado No evaluable es un rombo (forma propia, no el círculo de completable)."""
    _ir(pagina, "#trayectoria/prueba/perfecta/A")
    pagina.evaluate("document.fonts.ready")
    assert pagina.evaluate("document.fonts.check('700 20px \"Atkinson Hyperlegible\"')")
    pagina.keyboard.press("Tab")
    s = pagina.evaluate("""() => { const s = getComputedStyle(document.activeElement);
        return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset]; }""")
    assert s == ["solid", "4px", "rgb(232, 89, 12)", "3px"]
    assert pagina.inner_text(".marca-nombre") == "Atorapp"
    assert pagina.peticiones_externas == []


def test_foco_visible(pagina):
    """Cada control enfocable tiene un contorno visible al recibir el foco con teclado."""
    _ir(pagina, "#trayectoria/prueba/perfecta/A")
    pagina.keyboard.press("Tab")
    vistos = 0
    for _ in range(25):
        pagina.keyboard.press("Tab")
        estilo = pagina.evaluate("""() => {
            const e = document.activeElement, s = getComputedStyle(e);
            const tarjeta = e.closest('.tarjeta');
            const t = tarjeta ? getComputedStyle(tarjeta) : null;
            return {tag: e.tagName, ancho: parseFloat(s.outlineWidth), estilo: s.outlineStyle,
                    tarjeta: t ? parseFloat(t.outlineWidth) : 0};
        }""")
        if estilo["tag"] == "BODY":
            break
        assert (estilo["estilo"] != "none" and estilo["ancho"] >= 2) or estilo["tarjeta"] >= 2, estilo
        vistos += 1
    assert vistos >= 10
