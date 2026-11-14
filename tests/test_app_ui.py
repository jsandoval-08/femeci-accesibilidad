"""Fase 3F.5: la app del modo exploración tiene que ser accesible y funcionar de punta a punta.

- axe-core 4.14.0 (vendor/, el mismo del estudio) con todas sus reglas no experimentales: 0 violaciones
  en cada pantalla y estado (Inicio, errores, Evaluando, Detenida, Resultado por confirmar / después de
  «No» / confirmado, Recorrido, Historial, Acerca de). Control: un botón sin nombre sí se detecta.
- Teclado, foco visible (anillo naranja de 4 px), encabezados en orden, cero peticiones fuera de 127.0.0.1.
- Punta a punta con el motor REAL sobre tests/paginas (perfecta.html y sin_contacto.html, tarea A).

El servidor corre en un hilo con uvicorn; la carpeta de salida es temporal (nunca exploracion/ ni estudio/).
"""

import threading
import time
from pathlib import Path

import pytest
import uvicorn

from app.seguridad import Config
from app.servidor import crear_app
from motor_falso import MotorFalso

RAIZ = Path(__file__).resolve().parents[1]
AXE_JS = RAIZ / "vendor" / "axe-core" / "axe.min.js"
BLOQUEADOS = ("ciudadano.sinaloa.gob.mx", "culiacan.gob.mx")


def _levantar(app):
    srv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    hilo = threading.Thread(target=srv.run, daemon=True)
    hilo.start()
    while not srv.started:
        time.sleep(0.02)
    puerto = srv.servers[0].sockets[0].getsockname()[1]
    return srv, hilo, f"http://127.0.0.1:{puerto}/"


@pytest.fixture(scope="module")
def app_falsa(tmp_path_factory):
    """La app con el motor de prueba: espera a mitad del recorrido hasta que se libere."""
    estado = {"liberar": threading.Event(), "abiertos": []}

    def motor(*args, **kwargs):
        return MotorFalso(liberar=estado["liberar"], no_carga=estado.get("no_carga", False))(*args, **kwargs)

    app = crear_app(Config(BLOQUEADOS, tmp_path_factory.mktemp("exploracion")), motor=motor,
                    abrir=estado["abiertos"].append)
    srv, hilo, url = _levantar(app)
    estado["url"] = url
    yield estado
    estado["liberar"].set()
    srv.should_exit = True
    hilo.join(5)


@pytest.fixture
def pagina(chromium):
    # Sin movimiento: axe mide el contraste del estado final, no de un cuadro a medias de la animación
    # (las animaciones de la app solo corren con prefers-reduced-motion: no-preference).
    contexto = chromium.new_context(viewport={"width": 1366, "height": 768}, reduced_motion="reduce")
    pg = contexto.new_page()
    pg.externas, pg.errores = [], []

    def filtrar(ruta):
        if ruta.request.url.startswith("http://127.0.0.1:"):
            ruta.continue_()
        else:
            pg.externas.append(ruta.request.url)
            ruta.abort()

    pg.route("**/*", filtrar)
    pg.on("pageerror", lambda e: pg.errores.append(str(e)))
    pg.on("console", lambda m: pg.errores.append(m.text) if m.type == "error" else None)
    yield pg
    assert pg.externas == []
    contexto.close()


def _axe(pg) -> list:
    if not pg.evaluate("typeof window.axe !== 'undefined'"):
        pg.add_script_tag(content=AXE_JS.read_text(encoding="utf-8"))
    r = pg.evaluate("() => axe.run(document, {resultTypes: ['violations']})")
    assert r["testEngine"]["version"] == "4.14.0"
    return [{"regla": v["id"], "nodos": [n["target"] for n in v["nodes"]]} for v in r["violations"]]


def _encabezados_en_orden(pg):
    niveles = pg.eval_on_selector_all("main h1, main h2, main h3", "hs => hs.map(h => Number(h.tagName[1]))")
    assert niveles.count(1) == 1 and niveles[0] == 1, niveles
    for antes, despues in zip(niveles, niveles[1:]):
        assert despues <= antes + 1, niveles


def _ir(pg, url, hash_=""):
    pg.goto("about:blank")
    pg.goto(url + hash_)
    pg.wait_for_selector("#vista h1")


def _evaluar(pg, url, sitio="http://127.0.0.1:9/portada.html", tarea="A", tramite=""):
    _ir(pg, url)
    pg.fill("#url", sitio)
    pg.check(f"input[name=tarea][value={tarea}]")
    pg.fill("#tramite", tramite)
    pg.click("#b-evaluar")


# ---------- axe: 0 violaciones en cada pantalla y estado ----------

def test_axe_si_detecta_un_defecto(app_falsa, pagina):
    _ir(pagina, app_falsa["url"])
    pagina.evaluate("document.querySelector('main').insertAdjacentHTML('beforeend', '<button></button>')")
    assert "button-name" in {v["regla"] for v in _axe(pagina)}


def test_axe_inicio_historial_y_acerca(app_falsa, pagina):
    for hash_, espera in (("", "#formulario"), ("#historial", "#vista h1"), ("#acerca", "#h-modo")):
        _ir(pagina, app_falsa["url"], hash_)
        pagina.wait_for_selector(espera)
        assert _axe(pagina) == [], hash_
        _encabezados_en_orden(pagina)
    assert pagina.errores == []


def test_axe_errores_del_formulario(app_falsa, pagina):
    _evaluar(pagina, app_falsa["url"], sitio="", tarea="B")
    assert pagina.get_attribute("#url", "aria-invalid") == "true"
    assert pagina.get_attribute("#tramite", "aria-invalid") == "true"
    assert pagina.evaluate("document.activeElement.id") == "url"
    assert _axe(pagina) == []
    _evaluar(pagina, app_falsa["url"], sitio="https://www.culiacan.gob.mx/")
    pagina.wait_for_selector("[role=alert]")
    assert "a ciegas" in pagina.inner_text("[role=alert]")
    assert _axe(pagina) == []


def test_axe_evaluando_resultado_y_recorrido(app_falsa, pagina):
    app_falsa["liberar"].clear()
    _evaluar(pagina, app_falsa["url"])
    pagina.wait_for_selector("#ev-lista li[aria-current=step]")
    assert "Estrategia 2 de 3" in pagina.inner_text("#ev-estrategia")
    assert pagina.inner_text("#ev-tecla .sr-only") == "Insert más F7"
    assert _axe(pagina) == [], "evaluando"
    _encabezados_en_orden(pagina)
    # Reloj: junto a "Estrategia k de n", se actualiza solo y NO está dentro del aria-live.
    assert pagina.evaluate("document.getElementById('ev-tiempo').parentElement === document.getElementById('ev-estrategia').parentElement")
    assert pagina.evaluate("!document.getElementById('ev-tiempo').closest('[aria-live], [role=status], [role=alert]')")
    antes = pagina.inner_text("#ev-tiempo")
    pagina.wait_for_function("t => document.getElementById('ev-tiempo').textContent !== t", arg=antes, timeout=4000)
    assert pagina.inner_text("#ev-tiempo").startswith("Tiempo: 00:0")
    app_falsa["liberar"].set()
    pagina.wait_for_selector("#h-estima")
    assert pagina.evaluate("document.activeElement.tagName") == "H1"
    texto = pagina.inner_text("#estima")
    assert "Por confirmar" in texto and "Llegué a esto: «Teléfono: 667 555 0999»" in texto
    assert "Completable" not in texto  # nunca a secas sin confirmar
    assert "Duración total: 01:15" in pagina.inner_text("main")  # 75.4 s del motor de prueba
    assert pagina.locator("table tbody tr td:nth-child(4)").all_inner_texts() == ["00:04", "01:01", "00:01"]
    assert _axe(pagina) == [], "por confirmar"
    _encabezados_en_orden(pagina)
    pagina.click("#b-no")
    assert pagina.evaluate("document.activeElement.id") == "h-otras"
    assert _axe(pagina) == [], "después de No"
    pagina.click("#otras [data-eleccion='1']")
    pagina.wait_for_selector(".insignia--completable")
    assert "Confirmado por ti" in pagina.inner_text("#estima")
    assert "Fricción: 7 pulsaciones" in pagina.inner_text("#estima")
    assert _axe(pagina) == [], "confirmado"
    pagina.click("#b-exportar")
    pagina.wait_for_selector("#b-carpeta")
    assert pagina.inner_text(".ruta").endswith("reporte.md")
    assert _axe(pagina) == [], "exportado"
    pagina.click("text=Ver recorrido paso a paso")
    pagina.wait_for_selector(".recorrido")
    assert pagina.locator(".recorrido li").count() == 7
    assert _axe(pagina) == [], "recorrido"
    _encabezados_en_orden(pagina)
    _ir(pagina, app_falsa["url"], "#historial")
    pagina.wait_for_selector("table")
    assert _axe(pagina) == [], "historial con datos"
    assert pagina.errores == []


def test_axe_entrada_que_no_cargo(app_falsa, pagina):
    app_falsa["no_carga"] = True
    try:
        _evaluar(pagina, app_falsa["url"])
        pagina.wait_for_selector("#h-estima")
    finally:
        app_falsa["no_carga"] = False
    estima = pagina.inner_text("#estima")
    assert "No evaluable" in estima and "No cargó en el navegador de Atorapp en 60 s" in estima
    assert "ninguna estrategia encontró" not in estima.lower() and "Completable" not in estima
    axe = pagina.inner_text("#h-axe >> xpath=..")
    assert "No se pudo medir: la página no cargó." in axe and "Timeout" not in axe and "Playwright" not in axe
    assert pagina.locator("#h-estr").count() == 0  # sin tabla de estrategias
    assert _axe(pagina) == []
    _encabezados_en_orden(pagina)
    assert pagina.errores == []


def test_axe_detenida(app_falsa, pagina):
    app_falsa["liberar"].clear()
    _evaluar(pagina, app_falsa["url"])
    pagina.wait_for_selector("#ev-lista li")
    with pagina.expect_response(lambda r: r.url.endswith("/detener")):
        pagina.click("#b-detener")  # que el servidor reciba la orden antes de soltar al motor
    app_falsa["liberar"].set()
    pagina.wait_for_function("document.querySelector('#ev-titulo').textContent === 'Evaluación detenida'")
    assert "no se guardó" in pagina.inner_text("#ev-final")
    assert _axe(pagina) == []


# ---------- Teclado y foco ----------

def test_primer_tab_es_saltar_al_contenido(app_falsa, pagina):
    _ir(pagina, app_falsa["url"])
    pagina.keyboard.press("Tab")
    assert pagina.evaluate("document.activeElement.id") == "saltar"
    pagina.keyboard.press("Enter")
    assert pagina.evaluate("document.activeElement.tagName") == "H1"


def test_foco_visible_naranja(app_falsa, pagina):
    _ir(pagina, app_falsa["url"])
    vistos = 0
    for _ in range(14):
        pagina.keyboard.press("Tab")
        s = pagina.evaluate("""() => { const s = getComputedStyle(document.activeElement);
            return {tag: document.activeElement.tagName, ancho: s.outlineWidth, color: s.outlineColor,
                    estilo: s.outlineStyle, sep: s.outlineOffset}; }""")
        if s["tag"] == "BODY":
            break
        assert (s["estilo"], s["ancho"], s["color"], s["sep"]) == ("solid", "4px", "rgb(232, 89, 12)", "3px"), s
        vistos += 1
    # Saltar, 4 del menú, dirección, el grupo de radios (1 parada), trámite y Evaluar.
    assert vistos == 9


def test_estudio_abre_la_interfaz_actual(app_falsa, pagina):
    _ir(pagina, app_falsa["url"])
    pagina.click("#b-estudio")
    pagina.wait_for_function("document.querySelector('#vivo').textContent.includes('estudio')")
    assert app_falsa["abiertos"][-1].endswith(str(Path("interfaz") / "index.html"))


def test_fuente_local(app_falsa, pagina):
    _ir(pagina, app_falsa["url"])
    pagina.evaluate("document.fonts.ready")
    assert pagina.evaluate("document.fonts.check('700 20px \"Atkinson Hyperlegible\"')")


# ---------- Punta a punta con el motor real, solo páginas locales ----------

@pytest.fixture(scope="module")
def app_real(servidor, tmp_path_factory):
    base = tmp_path_factory.mktemp("exploracion_real")
    app = crear_app(Config(BLOQUEADOS, base), opciones_motor={"pausa_s": 0, "espera_ms": 0, "timeout_ms": 5_000},
                    abrir=lambda r: None)
    srv, hilo, url = _levantar(app)
    yield url, base
    srv.should_exit = True
    hilo.join(5)


def test_punta_a_punta_perfecta(app_real, servidor, pagina):
    url, base = app_real
    _evaluar(pagina, url, sitio=servidor + "perfecta.html")
    pagina.wait_for_selector("#h-estima", timeout=120_000)
    assert "Llegué a esto: «Teléfono: 667 555 0142»" in pagina.inner_text("#estima")
    pagina.click("[data-eleccion='0']")
    pagina.wait_for_selector(".insignia--completable")
    assert "Fricción: 7 pulsaciones" in pagina.inner_text("#estima")  # = perfecta.esperado.yaml A
    assert "H hasta la sección, luego leer" in pagina.inner_text("#estima")
    assert "%" in pagina.inner_text("#h-axe >> xpath=..")  # axe sí se midió
    assert len(list(base.glob("*_127.0.0.1_A/exploracion.json"))) == 1
    assert _axe(pagina) == []
    assert pagina.errores == []


def test_punta_a_punta_sin_contacto(app_real, servidor, pagina):
    url, _ = app_real
    _evaluar(pagina, url, sitio=servidor + "sin_contacto.html")
    pagina.wait_for_selector("#h-estima", timeout=120_000)
    texto = pagina.inner_text("#estima")
    assert "No completable" in texto and "42 pulsaciones consumidas" in texto  # = sin_contacto.esperado.yaml A
    assert "¿Es lo que buscabas?" not in texto  # nadie llegó: no hay nada que confirmar
    assert _axe(pagina) == []
