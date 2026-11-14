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
