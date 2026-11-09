"""Fase 3D: lector del CSV de auditoría y reporte por sitio. Valores a mano, antes del código.

Este módulo no usa la fixture `chromium`: correr_sitio() abre sus propios Playwright (axe y luego
las estrategias) y la API síncrona no admite dos abiertos en el mismo hilo. SOLO páginas locales.
"""

import json
from pathlib import Path

import pytest

sitio = pytest.importorskip("src.sitio")
reporte = pytest.importorskip("src.reporte")

PAGINAS = Path(__file__).parent / "paginas"
ENCABEZADO = "tarea,entrada,tramite,objetivo_correcto,veredicto_nvda,vidente_lo_encuentra,pagina_axe\n"


def _csv(tmp_path, *filas, encabezado=ENCABEZADO):
    ruta = tmp_path / "prueba.auditoria.csv"
    ruta.write_text(encabezado + "".join(f + "\n" for f in filas), encoding="utf-8-sig")
    return ruta


# ---------- Lector ----------

def test_lee_filas(tmp_path):
    filas = sitio.leer_auditoria(_csv(
        tmp_path,
        "A,inicio.html,,667 555 0142,completable,sí,",
        "B,tramites.html,Licencia,Croquis|Predial,no_completable,no,detalle.html",
        "C,inicio.html,,docs/plan.pdf,,,",
    ))
    a, b, c = filas
    assert (a.tarea, a.entrada, a.tramite) == ("A", "inicio.html", None)
    assert a.veredicto_nvda == "completable" and a.vidente_lo_encuentra is True
    assert a.pagina_axe == "inicio.html"  # vacía: se usa la entrada
    assert b.tramite == "Licencia" and b.objetivo_correcto == "Croquis|Predial"
    assert b.vidente_lo_encuentra is False and b.pagina_axe == "detalle.html"
    assert c.veredicto_nvda is None and c.vidente_lo_encuentra is None  # vacío = no medido


def test_sin_columna_pagina_axe_tambien_sirve(tmp_path):
    enc = "tarea,entrada,tramite,objetivo_correcto,veredicto_nvda,vidente_lo_encuentra\n"
    filas = sitio.leer_auditoria(_csv(tmp_path, "A,i.html,,NO_EXISTE,,", encabezado=enc))
    assert filas[0].pagina_axe == "i.html" and filas[0].objetivo_correcto == "NO_EXISTE"


@pytest.mark.parametrize("filas,error", [
    (["Z,i.html,,x,,,"], "línea 2"),  # tarea desconocida
    (["A,i.html,,x,,,", "A,i.html,,x,,,"], "línea 3"),  # tarea repetida
    (["B,i.html,,x,,,"], "línea 2"),  # B sin trámite
    (["A,,,x,,,"], "línea 2"),  # sin entrada
    (["A,i.html,,,,,"], "línea 2"),  # objetivo vacío: hay que escribir NO_EXISTE
    (["A,i.html,,x,tal vez,,"], "línea 2"),  # veredicto fuera del vocabulario
    (["A,i.html,,x,,quizá,"], "línea 2"),  # vidente fuera del vocabulario
    # Fase 4 (8-nov): en A, B y D el objetivo es lo que se OYE (teléfono/correo, requisitos,
    # campos); una URL nunca coincidiría y daría no_completable fijo, como un objetivo vacío.
    (["A,i.html,,https://www.ejemplo.gob.mx/,,,"], "línea 2"),
    (["B,i.html,Acta,INE|https://x.gob.mx/req,,,"], "línea 2"),
    (["D,i.html,,http://x.gob.mx/form,,,"], "línea 2"),
])
def test_errores_con_numero_de_linea(tmp_path, filas, error):
    with pytest.raises(sitio.ErrorAuditoria, match=error):
        sitio.leer_auditoria(_csv(tmp_path, *filas))


def test_objetivo_url_solo_vale_en_c_y_correo_no_es_url(tmp_path):
    """C compara la URL del documento: ahí una URL completa es válida. Un correo no es URL."""
    filas = sitio.leer_auditoria(_csv(
        tmp_path,
        "A,i.html,,contacto@ejemplo.gob.mx|667 555 0142,,,",
        "C,i.html,,https://x.gob.mx/docs/plan.pdf,,,",
    ))
    assert [f.tarea for f in filas] == ["A", "C"]


def test_columna_faltante(tmp_path):
    with pytest.raises(sitio.ErrorAuditoria, match="objetivo_correcto"):
        sitio.leer_auditoria(_csv(tmp_path, "A,i.html,,", encabezado="tarea,entrada,tramite\n"))


@pytest.mark.parametrize("nombre", ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
                                    "formulario_sin_etiquetas", "pdf_escaneado"])
def test_csv_de_referencia_validos_y_sin_datos_de_nvda(nombre):
    """No hay auditoría: ningún CSV del repositorio puede traer un veredicto NVDA."""
    filas = sitio.leer_auditoria(PAGINAS / f"{nombre}.auditoria.csv")
    assert [f.tarea for f in filas] == ["A", "B", "C", "D"]
    assert all(f.veredicto_nvda is None and f.vidente_lo_encuentra is None for f in filas)


# ---------- Seguro: nada de sitios reales ----------

def test_rechaza_base_externa(tmp_path):
    with pytest.raises(ValueError, match="local"):
        sitio.correr_sitio(PAGINAS / "perfecta.auditoria.csv", "https://example.org/", tmp_path)


@pytest.mark.parametrize("fila", [
    "A,https://example.org/,,x,,,",  # entrada externa con base local
    "A,i.html,,x,,,https://example.org/",  # página de axe externa
])
def test_rechaza_url_externa_en_el_csv(tmp_path, fila):
    with pytest.raises(ValueError, match="local"):
        sitio.correr_sitio(_csv(tmp_path, fila), "http://127.0.0.1:9/", tmp_path)


# ---------- Trayectoria resumida ----------

def _paso(tecla):
    from src.emulador import Paso
    return Paso(tecla, "", None, True, 0)


@pytest.mark.parametrize("teclas,texto", [
    (["H"] * 6 + ["leer"], "H×6, leer×1"),
    (["lista_enlaces", "flecha_lista", "flecha_lista", "Enter"], "lista_enlaces×1, flecha_lista×2, Enter×1"),
    (["K", "Enter", "volver", "K"], "K×1, Enter×1, volver×1, K×1"),
    ([], "sin pulsaciones"),
])
def test_resumir_trayectoria(teclas, texto):
    assert reporte.resumir_trayectoria([_paso(t) for t in teclas]) == texto


# ---------- Reporte de punta a punta ----------

PUNTAJES = {"reglas", "elementos", "reglas_conservador", "elementos_conservador"}


@pytest.fixture(scope="module")
def corrida(servidor, tmp_path_factory):
    carpeta = tmp_path_factory.mktemp("reporte")
    r = sitio.correr_sitio(PAGINAS / "pdf_escaneado.auditoria.csv", servidor, carpeta,
                           timeout_ms=5_000, espera_ms=0, pausa_s=0)
    rutas = reporte.escribir_reporte(r, carpeta)
    return r, rutas


def test_reporte_json(corrida):
    _, (ruta_json, _) = corrida
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert datos["sitio"] == "pdf_escaneado"
    assert datos["palabras_version"] == 2 and datos["umbral"] == 15
    tareas = {t["tarea"]: t for t in datos["tareas"]}
    assert set(tareas) == set("ABCD")
    # Valores del yaml de pdf_escaneado
    assert (tareas["A"]["estado"], tareas["A"]["friccion"]) == ("completable", 7)
    assert tareas["A"]["estrategia"] == "H_a_seccion"
    assert tareas["A"]["trayectoria"] == "H×6, leer×1"
    assert (tareas["C"]["estado"], tareas["C"]["tipo_falla"]) == ("no_completable", "cierre_roto")
    assert tareas["C"]["motivo"]
    assert tareas["D"]["trayectoria"] == "F×3"
    assert tareas["A"]["sensibilidad"] == {"10": "completable", "15": "completable", "25": "completable"}
    assert tareas["A"]["falsas_llegadas"] == []
    # CSV sin auditoría: no medido
    assert tareas["A"]["veredicto_nvda"] is None and tareas["A"]["vidente_lo_encuentra"] is None
    # Los 4 puntajes de axe, de verdad medidos
    for t in tareas.values():
        assert set(t["puntajes"]) == PUNTAJES
        assert all(0 <= v <= 1 for v in t["puntajes"].values())


def test_reporte_markdown(corrida):
    _, (_, ruta_md) = corrida
    md = ruta_md.read_text(encoding="utf-8")
    assert "pdf_escaneado" in md and "estimación" in md
    assert "puntaje de conformidad automática" in md
    assert "conformidad WCAG" not in md
    for texto in ("cierre_roto", "H×6, leer×1", "F×3"):
        assert texto in md
    assert "## Llegó primero a otra cosa" in md and "Ninguna" in md


def test_reporte_muestra_falsas_llegadas(tmp_path, servidor):
    ruta = _csv(tmp_path, "A,ce_otro_telefono.html,,667 555 0100,,,")
    r = sitio.correr_sitio(ruta, servidor, tmp_path, timeout_ms=5_000, espera_ms=0, pausa_s=0)
    ruta_json, ruta_md = reporte.escribir_reporte(r, tmp_path)
    t = json.loads(ruta_json.read_text(encoding="utf-8"))["tareas"][0]
    # El estado no cambia, pero se ven: H (3) y leer (3) llegaron al 0999.
    assert (t["estado"], t["friccion"]) == ("completable", 7)
    assert [f["estrategia"] for f in t["falsas_llegadas"]] == ["H_a_seccion", "no_dirigida"]
    assert t["falsas_llegadas"][0]["pulsaciones"] == 3
    md = ruta_md.read_text(encoding="utf-8")
    seccion = md.split("## Llegó primero a otra cosa")[1]
    assert "H_a_seccion" in seccion and "667 555 0999" in seccion and "Ninguna" not in seccion


def test_axe_que_falla_es_no_medido(tmp_path, servidor, monkeypatch):
    def falla(*a, **k):
        raise RuntimeError("axe no corrió")
    monkeypatch.setattr(sitio, "capturar", falla)
    ruta = _csv(tmp_path, "A,ce_solo_otro.html,,NO_EXISTE,,,")
    r = sitio.correr_sitio(ruta, servidor, tmp_path, timeout_ms=5_000, espera_ms=0, pausa_s=0)
    ruta_json, ruta_md = reporte.escribir_reporte(r, tmp_path)
    t = json.loads(ruta_json.read_text(encoding="utf-8"))["tareas"][0]
    assert t["puntajes"] is None and "axe no corrió" in t["error_axe"]
    assert "no medido" in ruta_md.read_text(encoding="utf-8")
