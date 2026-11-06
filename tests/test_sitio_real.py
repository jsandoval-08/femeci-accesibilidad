"""Fase 3D.1: modo "sitio real", topes en la corrida y línea de comandos.

Ninguna prueba toca un sitio real. Las negativas reemplazan capturar y sync_playwright por una falla,
lo que demuestra que se niegan ANTES de tocar la red. example.test es un dominio reservado.
Los veredictos NVDA de estos CSV temporales son INVENTADOS, solo para probar la regla.
Este módulo no usa la fixture `chromium`: correr_sitio() abre sus propios Playwright.
"""

from pathlib import Path

import pytest

from src import sitio

pytestmark = pytest.mark.skip("se activa con el código de 3D.1")

PAGINAS = Path(__file__).parent / "paginas"
ENCABEZADO = "tarea,entrada,tramite,objetivo_correcto,veredicto_nvda,vidente_lo_encuentra,pagina_axe\n"
BASE = "https://www.example.test/"
HOST = "www.example.test"


def _csv(tmp_path, *filas):
    ruta = tmp_path / "prueba.auditoria.csv"
    ruta.write_text(ENCABEZADO + "".join(f + "\n" for f in filas), encoding="utf-8-sig")
    return ruta


@pytest.fixture
def sin_red(monkeypatch):
    def falla(*a, **k):
        raise AssertionError("tocó la red")
    monkeypatch.setattr(sitio, "capturar", falla)
    monkeypatch.setattr(sitio, "sync_playwright", falla)


# ---------- Valores fijados por escrito ----------

def test_topes_fijados():
    assert sitio.TOPE_PULSACIONES == 508  # 4 niveles × 127 paradas (scripts/medicion/paradas.py)
    assert sitio.TOPE_NAVEGACIONES == 30  # enlaces_ambiguos B usa 9


# ---------- Negativas, antes de tocar la red ----------

def test_sin_flag_rechaza_externa(tmp_path, sin_red):
    with pytest.raises(ValueError, match="local"):
        sitio.correr_sitio(_csv(tmp_path, "A,inicio.html,,x,completable,sí,"), BASE, tmp_path)


def test_falta_un_veredicto_dice_cual(tmp_path, sin_red):
    ruta = _csv(tmp_path, "A,inicio.html,,x,completable,sí,", "C,inicio.html,,y,,sí,")
    with pytest.raises(sitio.AuditoriaIncompleta, match=r"C \(línea 3\)"):
        sitio.correr_sitio(ruta, BASE, tmp_path, sitio_real=HOST)


@pytest.mark.parametrize("nombre", ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
                                    "formulario_sin_etiquetas", "pdf_escaneado"])
def test_csv_del_repositorio_se_niegan(tmp_path, sin_red, nombre):
    """No hay auditoría: ningún CSV del repositorio puede correr como sitio real."""
    with pytest.raises(sitio.AuditoriaIncompleta):
        sitio.correr_sitio(PAGINAS / f"{nombre}.auditoria.csv", "http://127.0.0.1:9/", tmp_path,
                           sitio_real="127.0.0.1")


def test_no_evaluable_cuenta_como_lleno(tmp_path):
    fila = sitio.leer_auditoria(_csv(tmp_path, "A,inicio.html,,x,no_evaluable,,"))[0]
    assert fila.veredicto_nvda == "no_evaluable"
    assert sitio.faltan_veredictos([fila]) == []


def test_flag_de_otro_host(tmp_path, sin_red):
    with pytest.raises(ValueError, match="host"):
        sitio.correr_sitio(_csv(tmp_path, "A,inicio.html,,x,completable,sí,"), BASE, tmp_path,
                           sitio_real="otro.example.test")


@pytest.mark.parametrize("fila", [
    "A,https://otro.example.test/,,x,completable,sí,",
    "A,inicio.html,,x,completable,sí,https://otro.example.test/",
])
def test_csv_con_otro_host(tmp_path, sin_red, fila):
    with pytest.raises(ValueError, match="host"):
        sitio.correr_sitio(_csv(tmp_path, fila), BASE, tmp_path, sitio_real=HOST)


def test_pausa_menor_a_un_segundo(tmp_path, sin_red):
    with pytest.raises(ValueError, match="pausa"):
        sitio.correr_sitio(_csv(tmp_path, "A,inicio.html,,x,completable,sí,"), BASE, tmp_path,
                           sitio_real=HOST, pausa_s=0.5)


def test_ya_no_existe_solo_local(tmp_path, sin_red):
    with pytest.raises(TypeError):
        sitio.correr_sitio(_csv(tmp_path, "A,inicio.html,,x,completable,sí,"), BASE, tmp_path,
                           solo_local=False)


# ---------- Corridas locales ----------

def test_modo_real_con_auditoria_completa_corre(tmp_path, servidor):
    """Servidor local con sitio_real="127.0.0.1". ce_solo_otro: nadie llega al 0100."""
    ruta = _csv(tmp_path, "A,ce_solo_otro.html,,667 555 0100,no_completable,no,")
    r = sitio.correr_sitio(ruta, servidor, tmp_path, sitio_real="127.0.0.1", espera_ms=0, pausa_s=1.0)
    t = r.tareas[0]
    assert (t.veredicto.estado, t.veredicto.tipo_falla) == ("no_completable", "no_encontrado")
    assert t.fila.veredicto_nvda == "no_completable"


def test_corrida_aplica_topes(tmp_path, servidor, monkeypatch):
    """Por omisión se pasan los dos topes al emulador de CADA estrategia."""
    vistos = []
    original = sitio.Emulador.en_vivo

    def espia(nav, url, **k):
        vistos.append((k["tope_pulsaciones"], k["tope_navegaciones"]))
        return original(nav, url, **k)
    monkeypatch.setattr(sitio.Emulador, "en_vivo", espia)
    ruta = _csv(tmp_path, "A,ce_solo_otro.html,,NO_EXISTE,,,")
    sitio.correr_sitio(ruta, servidor, tmp_path, timeout_ms=5_000, espera_ms=0, pausa_s=0)
    assert vistos and set(vistos) == {(508, 30)}


def test_tope_chico_en_corrida(tmp_path, servidor):
    """ce_solo_otro con tope 1: ninguna estrategia termina (H necesita 3): no se afirma nada."""
    ruta = _csv(tmp_path, "A,ce_solo_otro.html,,667 555 0100,,,")
    r = sitio.correr_sitio(ruta, servidor, tmp_path, timeout_ms=5_000, espera_ms=0, pausa_s=0, tope=1)
    assert r.tareas[0].veredicto.estado == "no_evaluable"
    assert "tope_pulsaciones" in r.tareas[0].veredicto.motivo


# ---------- Línea de comandos ----------

def test_cli_sin_flag_rechaza_externa(tmp_path, sin_red, capsys):
    from src.correr_sitio import main
    ruta = _csv(tmp_path, "A,inicio.html,,x,completable,sí,")
    assert main([str(ruta), BASE, "--carpeta", str(tmp_path)]) == 2
    assert "local" in capsys.readouterr().err


def test_cli_con_flag_sin_auditoria_se_niega(tmp_path, sin_red, capsys):
    from src.correr_sitio import main
    ruta = _csv(tmp_path, "A,inicio.html,,x,,,")
    assert main([str(ruta), BASE, "--carpeta", str(tmp_path), "--sitio-real", HOST]) == 2
    assert "veredicto_nvda" in capsys.readouterr().err


def test_cli_corre_y_escribe_reporte(tmp_path, servidor, capsys):
    from src.correr_sitio import main
    ruta = _csv(tmp_path, "A,ce_solo_otro.html,,667 555 0100,,,")
    assert main([str(ruta), servidor, "--carpeta", str(tmp_path)]) == 0
    assert (tmp_path / "prueba.reporte.json").exists() and (tmp_path / "prueba.reporte.md").exists()
    assert "prueba.reporte.md" in capsys.readouterr().out
