"""Fase 3F.2: motor del modo exploración. Solo páginas locales (tests/paginas en 127.0.0.1).

Lo central: el gancho que observa cada paso NO cambia ningún resultado. Sobre las páginas de prueba,
clasificar() con el objetivo de su .auditoria.csv da exactamente lo de su .esperado.yaml, igual que en
test_veredicto.py. Este módulo no usa el fixture `chromium`: explorar() abre su propio Playwright.
"""

import csv
import threading
from pathlib import Path

import pytest
import yaml

import app.motor as motor
from app.motor import Detenida, estimaciones, explorar, hallazgos, objetivo_de
from app.seguridad import HostBloqueado
from src.emulador import Documento
from src.veredicto import NO_EXISTE, clasificar

PAGINAS = Path(__file__).parent / "paginas"
RAPIDO = {"pausa_s": 0, "espera_ms": 0, "timeout_ms": 5_000}  # solo en 127.0.0.1


def _fila(nombre, letra):
    with open(PAGINAS / f"{nombre}.auditoria.csv", encoding="utf-8-sig", newline="") as f:
        return next(r for r in csv.DictReader(f) if r["tarea"] == letra)


CASOS = [("perfecta", "A"), ("sin_contacto", "A"), ("enlaces_ambiguos", "B"),
         ("pdf_escaneado", "C"), ("formulario_sin_etiquetas", "D")]


@pytest.mark.parametrize("nombre,letra", CASOS, ids=[f"{n}-{t}" for n, t in CASOS])
def test_el_gancho_no_cambia_el_resultado(servidor, tmp_path, nombre, letra):
    fila = _fila(nombre, letra)
    esperado = yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))["tareas"][letra]
    eventos = []
    ex = explorar(servidor + fila["entrada"], letra, fila["tramite"], tmp_path, hosts=(),
                  al_evento=lambda t, d: eventos.append((t, d)), **RAPIDO)
    v = clasificar(ex.resultado, fila["objetivo_correcto"])
    assert (v.estado, v.tipo_falla, v.estrategia) == (esperado["estado"], esperado["tipo_falla"],
                                                      esperado["estrategia"])
    assert (v.friccion if v.friccion is not None else v.consumidas) == esperado["friccion_esperada"]
    # Cada paso de cada estrategia se avisó una vez, en orden, con su estrategia.
    pasos = [d for t, d in eventos if t == "paso"]
    assert [(d["estrategia"], d["tecla"], d["pulsaciones"]) for d in pasos] == [
        (i.estrategia, p.tecla, p.pulsaciones) for i in ex.resultado.intentos for p in i.trayectoria]
    inicios = [d for t, d in eventos if t == "estrategia"]
    assert [d["indice"] for d in inicios] == list(range(1, len(ex.resultado.intentos) + 1))
    assert all(d["total"] == len(ex.resultado.intentos) for d in inicios)
    assert ("fase", {"fase": "axe"}) in eventos
    assert ex.puntajes is not None and set(ex.puntajes) == {"reglas", "elementos", "reglas_conservador",
                                                            "elementos_conservador"}
    assert (tmp_path / "capturas").is_dir()
    # Duraciones: una por estrategia y el total (axe incluido) no puede ser menor que su suma.
    assert len(ex.duraciones_s) == len(ex.resultado.intentos)
    assert all(d >= 0 for d in ex.duraciones_s)
    assert ex.duracion_s >= sum(ex.duraciones_s) - 0.1 * len(ex.duraciones_s)  # redondeo a 0.1 s


def test_sin_objetivo_se_confirma_lo_encontrado(servidor, tmp_path):
    """ce_otro_telefono (test_veredicto): H y leer llegan primero a OTRO teléfono en 3; la lista de
    enlaces llega al correcto en 7. Sin objetivo, la primera opción es la falsa llegada barata; si la
    persona confirma la otra, clasificar() da lo mismo que en el estudio."""
    ex = explorar(servidor + "ce_otro_telefono.html", "A", None, tmp_path, hosts=(), **RAPIDO)
    opciones = hallazgos(ex.resultado)
    assert len(opciones) == 2 and opciones[0]["pulsaciones"] == 3
    todas = estimaciones(ex.resultado)
    assert set(todas) == {"ninguna", "0", "1"}
    correcta = todas["1"]
    assert (correcta["estado"], correcta["estrategia"], correcta["friccion"]) == ("completable",
                                                                                 "enlace_por_nombre", 7)
    assert [x["estrategia"] for x in correcta["falsas_llegadas"]] == ["H_a_seccion", "no_dirigida"]
    assert todas["0"]["friccion"] == 3
    assert (todas["ninguna"]["estado"], todas["ninguna"]["tipo_falla"]) == ("no_completable", "no_encontrado")


def test_nadie_llega(servidor, tmp_path):
    ex = explorar(servidor + "sin_contacto.html", "A", None, tmp_path, hosts=(), **RAPIDO)
    assert hallazgos(ex.resultado) == []
    assert set(estimaciones(ex.resultado)) == {"ninguna"}


def test_pdf_confirmado_sin_capa_es_cierre_roto(servidor, tmp_path):
    ex = explorar(servidor + "pdf_escaneado.html", "C", None, tmp_path, hosts=(), **RAPIDO)
    opciones = hallazgos(ex.resultado)
    n = next(i for i, o in enumerate(opciones) if o["encontro"].endswith("docs/plan_municipal_escaneado.pdf"))
    assert estimaciones(ex.resultado)[str(n)]["tipo_falla"] == "cierre_roto"


def test_objetivo_de():
    assert objetivo_de("A", {"contacto": "Tel. 667 | 555", "url": None}) == "Tel. 667 555"
    assert objetivo_de("A", {"contacto": "", "url": "mailto:a@b.mx"}) == "mailto:a@b.mx"
    assert objetivo_de("B", {"requisitos": ["INE", " ", "CURP"]}) == "INE|CURP"
    doc = Documento("http://x/d.pdf", "application/pdf", True, True, 1, 10)
    assert objetivo_de("C", {"documento": doc}) == "http://x/d.pdf"
    assert objetivo_de("D", {"campos": ["", ""]}) == NO_EXISTE  # vacío coincidiría con todo


# ---------- Detener y bloqueos ----------

def test_detener_corta_en_la_siguiente_pulsacion(servidor, tmp_path):
    detener = threading.Event()
    pasos = []

    def al_evento(tipo, datos):
        if tipo == "paso":
            pasos.append(datos)
            detener.set()

    with pytest.raises(Detenida):
        explorar(servidor + "perfecta.html", "A", None, tmp_path, hosts=(), al_evento=al_evento,
                 detener=detener, **RAPIDO)
    assert len(pasos) == 1
    assert not (tmp_path / "capturas").exists()  # axe no llegó a correr


# ---------- Carga de prueba de la entrada ----------

@pytest.fixture
def servidor_mudo():
    """Doble de timeout: acepta la conexión y nunca responde (la página no termina de cargar)."""
    import socket
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(5)
    conexiones = []

    def aceptar():
        while True:
            try:
                conexiones.append(srv.accept()[0])
            except OSError:
                return

    threading.Thread(target=aceptar, daemon=True).start()
    yield f"http://127.0.0.1:{srv.getsockname()[1]}/"
    srv.close()
    for c in conexiones:
        c.close()


def _prohibido(*args, **kwargs):
    raise AssertionError("no debía correr")


def test_si_la_entrada_no_carga_no_corren_estrategias_ni_axe(servidor_mudo, tmp_path, monkeypatch):
    monkeypatch.setattr(motor, "mejor_estrategia", _prohibido)
    monkeypatch.setattr(motor, "_puntuar", _prohibido)
    eventos = []
    ex = explorar(servidor_mudo, "A", None, tmp_path, hosts=(), al_evento=lambda t, d: eventos.append(t),
                  pausa_s=0, timeout_carga_ms=1_000)
    assert ex.no_cargo["tipo"] == "timeout" and "Timeout" in ex.no_cargo["detalle"]
    assert ex.no_cargo["motivo"] == "No cargó en el navegador de Atorapp en 1 s"
    assert ex.puntajes is None and ex.error_axe == "la página no cargó" and ex.duraciones_s == ()
    assert eventos == []  # ni "estrategia", ni "paso", ni "fase" (axe)
    assert not (tmp_path / "capturas").exists()
    todas = estimaciones(ex.resultado, ex.no_cargo["motivo"])
    assert set(todas) == {"ninguna"}
    v = todas["ninguna"]
    assert (v["estado"], v["tipo_falla"], v["estrategia"], v["motivo"]) == (
        "no_evaluable", None, None, ex.no_cargo["motivo"])
    assert "ninguna estrategia" not in v["motivo"]


def test_motivo_exacto_con_el_tope_de_60_s(tmp_path, monkeypatch):
    """Doble de NavegadorEnVivo.abrir: devuelve el timeout sin esperar 60 s."""
    from src.emulador import Falla
    from src.navegador import NavegadorEnVivo
    monkeypatch.setattr(NavegadorEnVivo, "abrir", lambda self, url: Falla("timeout", "Page.goto: Timeout 60000ms exceeded."))
    monkeypatch.setattr(motor, "mejor_estrategia", _prohibido)
    monkeypatch.setattr(motor, "_puntuar", _prohibido)
    ex = explorar("http://127.0.0.1:9/x.html", "A", None, tmp_path, hosts=(), pausa_s=0)
    assert ex.no_cargo["motivo"] == "No cargó en el navegador de Atorapp en 60 s"
    from app.guardado import a_diccionario
    d = a_diccionario(ex)
    assert d["intentos"] == [] and d["requiere_confirmacion"] is False
    assert d["no_cargo"]["detalle"].startswith("Page.goto")


def test_falla_tecnica_al_cargar_no_dice_60_s(tmp_path, monkeypatch):
    from src.emulador import Falla
    from src.navegador import NavegadorEnVivo
    monkeypatch.setattr(NavegadorEnVivo, "abrir", lambda self, url: Falla("falla_tecnica", "net::ERR_CONNECTION_REFUSED"))
    monkeypatch.setattr(motor, "mejor_estrategia", _prohibido)
    ex = explorar("http://127.0.0.1:9/x.html", "A", None, tmp_path, hosts=(), pausa_s=0)
    assert ex.no_cargo["tipo"] == "falla_tecnica" and "60" not in ex.no_cargo["motivo"]


def test_entrada_bloqueada_no_abre_playwright(tmp_path, monkeypatch):
    def prohibido():
        raise AssertionError("no debía tocar la red")

    monkeypatch.setattr(motor, "sync_playwright", prohibido)
    with pytest.raises(HostBloqueado):
        explorar("https://www.culiacan.gob.mx/", "A", None, tmp_path,
                 hosts=("ciudadano.sinaloa.gob.mx", "culiacan.gob.mx"))
    with pytest.raises(ValueError, match="trámite"):
        explorar("http://127.0.0.1:1/x.html", "B", "  ", tmp_path, hosts=())
    with pytest.raises(ValueError, match="pausa"):
        explorar("https://ejemplo.invalid/", "A", None, tmp_path, hosts=(), pausa_s=0)


def test_redireccion_a_host_bloqueado_aborta_todo(servidor, tmp_path):
    """La entrada está en 127.0.0.1 (pasa la barrera 1) y redirige a localhost (bloqueado)."""
    eventos = []
    with pytest.raises(HostBloqueado, match="localhost"):
        explorar(servidor + "redirige_a/localhost/perfecta.html", "A", None, tmp_path,
                 hosts=("localhost",), al_evento=lambda t, d: eventos.append(t), **RAPIDO)
    assert "paso" not in eventos
    assert not (tmp_path / "capturas").exists()
