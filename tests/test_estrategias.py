"""Fase 3C: estrategias programadas, palabras clave, criterios de llegada y mejor estrategia.

Todos los valores esperados de este archivo se escribieron A MANO, ANTES de implementar las
estrategias, y NO se tomaron de su salida. Cada uno se dedujo de:
  - los .esperado.yaml (estrategia y friccion_esperada de las 24 tareas);
  - las paradas reales de las páginas de desarrollo (medidas en 3A) o el HTML de las ce_*.
Si un valor no cuadra, se reporta la discrepancia: NO se ajusta el valor.

"Llegó" significa "la estrategia cree que llegó", con lo anunciado. No es "completable": el
veredicto contra el objetivo correcto es de 3D. SOLO páginas de prueba locales.

Las páginas ce_* usan href opacos: las palabras clave nunca están en la URL, salvo en una trampa
a propósito (ce_mailto), para demostrar que las estrategias no deciden con ella.
"""

from pathlib import Path

import pytest
import yaml

from src import estrategias
from src.emulador import Parada

PAGINAS = Path(__file__).parent / "paginas"
NOMBRES = ["perfecta", "sin_encabezados", "sin_contacto", "enlaces_ambiguos",
           "formulario_sin_etiquetas", "pdf_escaneado"]
# Parte de la definición de la tarea B (CLAUDE.md): lo que la persona busca, no dónde está.
TRAMITE = "licencia de construccion"
PALABRAS = estrategias.cargar_palabras()


def _tarea(letra, pagina):
    return estrategias.Tarea(letra, pagina, TRAMITE if letra == "B" else None)


def _yaml(nombre):
    return yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))


def _intentos(resultado):
    """Intentos por etiqueta (las dos variantes de probar_enlaces comparten la suya)."""
    return {i.estrategia: i for i in resultado.intentos}


def _teclas(intento):
    return [p.tecla for p in intento.trayectoria]


# ---------- Normalización y coincidencia ----------

@pytest.mark.parametrize("texto,esperado", [
    ("Trámites", "tramites"),
    ("  CONTÁCTANOS\n ahora ", "contactanos ahora"),
    ("Atención   Ciudadana", "atencion ciudadana"),
])
def test_normalizar_busqueda(texto, esperado):
    assert estrategias.normalizar_busqueda(texto) == esperado


@pytest.mark.parametrize("texto,frases,esperado", [
    ("Plan Municipal (PDF)", ["pdf"], True),
    ("Trámites", ["tramites"], True),
    ("Atención ciudadana", ["atencion ciudadana"], True),
    ("Leyenda urbana", ["ley"], False),  # palabra completa, no un pedazo
    ("Contacto", ["contactanos"], False),
    ("", ["contacto"], False),
])
def test_coincide(texto, frases, esperado):
    assert estrategias.coincide(texto, frases) is esperado


def test_palabras_version_congelada():
    assert PALABRAS.version == 2 and PALABRAS.estado == "congelada"  # v2: agrega "expandir"
    assert "menu" in PALABRAS.expandir
    assert set(PALABRAS.tareas) == {"A", "B", "C", "D"}
    # Lo que no se declara cae a la sección: A y D no tienen lista propia de enlaces.
    assert PALABRAS.tareas["A"].enlace == PALABRAS.tareas["A"].seccion
    assert PALABRAS.tareas["C"].enlace != PALABRAS.tareas["C"].seccion
    assert PALABRAS.tareas["B"].marcador


def test_tarea_b_exige_tramite():
    """El trámite es parte de la definición de la tarea B."""
    with pytest.raises(ValueError):
        estrategias.Tarea("B", "perfecta.html")


# ---------- Criterio de llegada de la tarea A ----------

@pytest.mark.parametrize("texto,es_contacto", [
    ("Teléfono: 667 555 0142", True),  # yaml: objetivo de la tarea A
    ("Tel. 712 3456", True),  # palabra de teléfono + 7 dígitos
    ("(667) 555-0142", True),  # 10 dígitos agrupados
    ("+52 667 555 0142", True),
    ("oficina@example.org", True),
    ("Escríbenos a oficina@example.org", True),
    ("Administración 2021-2024", False),  # 8 dígitos sin palabra de teléfono
    ("12 de septiembre de 2026", False),
    ("C.P. 80000", False),
    ("Se plantarán 500 árboles en colonias", False),
    ("Contacto", False),
])
def test_texto_de_contacto(texto, es_contacto):
    assert estrategias.texto_de_contacto(texto) is es_contacto


def _enlace(nombre, url):
    return Parada(0, "link", nombre, None, True, (), "1", url=url)


@pytest.mark.parametrize("parada,cierra", [
    (_enlace("Escríbenos", "mailto:a@example.org"), True),  # regla del 20-oct
    (_enlace("Llámanos", "tel:+526675550100"), True),
    (_enlace("Inicio", "http://127.0.0.1/contacto.html"), False),  # la URL no decide
    (_enlace("Sin url", None), False),
    (Parada(0, "StaticText", "Teléfono: 667 555 0142", None, False, (), "1"), True),
])
def test_cierra_contacto(parada, cierra):
    assert estrategias.cierra_contacto(parada) is cierra


# ---------- Las 24 tareas de los .esperado.yaml ----------

RUTAS = [(n, t) for n in NOMBRES for t in "ABCD"]


@pytest.mark.parametrize("nombre,letra", RUTAS, ids=[f"{n}-{t}" for n, t in RUTAS])
def test_yaml(nombre, letra, vivo):
    t = _yaml(nombre)["tareas"][letra]
    r = estrategias.mejor_estrategia(vivo, _tarea(letra, t["entrada"]), PALABRAS)
    assert r.estrategia == t["estrategia"]
    if t["tipo_falla"] == "no_encontrado":
        assert r.mejor is None and r.friccion is None
        assert r.consumidas == t["friccion_esperada"] and r.motivo
    else:
        assert r.mejor.llego and r.friccion == t["friccion_esperada"]


# perfecta: costo a mano de cada estrategia sobre sus 44 paradas (None = no llega). Encabezados:
# Contacto es el 6.º, Trámites el 3.º, Descargas el 5.º. Landmarks: banner, nav, main, Noticias,
# Trámites, Descargas, Contacto. Enfocables: 3 del menú, PDF, 3 campos, botón.
PERFECTA = {
    "A": {"H_a_seccion": 7, "D_a_seccion": 8, "enlace_por_nombre": None, "no_dirigida": 35,
          "Tab_inicio": None},
    "B": {"H_a_seccion": 9, "D_a_seccion": 11, "enlace_por_nombre": None, "no_dirigida": 31,
          "Tab_inicio": None},
    "C": {"H_a_seccion": 7, "D_a_seccion": 8, "enlace_por_nombre": 5, "no_dirigida": 34,
          "Tab_inicio": 5},
    "D": {"H_a_seccion": 9, "D_a_seccion": 10, "enlace_por_nombre": None, "F_a_campos": 3,
          "no_dirigida": 42, "Tab_inicio": 7},
}


@pytest.mark.parametrize("letra", "ABCD")
def test_perfecta_costo_de_cada_estrategia(letra, vivo):
    intentos = _intentos(estrategias.mejor_estrategia(vivo, _tarea(letra, "perfecta.html"), PALABRAS))
    for estrategia, costo in PERFECTA[letra].items():
        i = intentos[estrategia]
        if costo is None:
            assert not i.llego and i.motivo, estrategia
        else:
            assert i.llego and i.pulsaciones == costo, estrategia
    assert ("F_a_campos" in intentos) is (letra == "D")  # F solo aplica a la tarea D


def test_no_llega_reporta_lo_consumido_por_cada_una(vivo):
    """perfecta A: la lista recorre sus 4 enlaces (1 + 3) sin candidato; Tab recorre 8
    enfocables y pulsa 1 más para saber que no hay más."""
    intentos = _intentos(estrategias.mejor_estrategia(vivo, _tarea("A", "perfecta.html"), PALABRAS))
    assert intentos["enlace_por_nombre"].pulsaciones == 4
    assert intentos["Tab_inicio"].pulsaciones == 9


# ---------- Hechos que se registran para 3D (sin veredicto) ----------

@pytest.mark.parametrize("pagina,capa_texto", [("perfecta.html", True),
                                               ("pdf_escaneado.html", False)])
def test_c_registra_documento(pagina, capa_texto, vivo):
    r = estrategias.mejor_estrategia(vivo, _tarea("C", pagina), PALABRAS)
    assert r.mejor.llego and r.mejor.hallazgo["documento"].capa_texto is capa_texto


@pytest.mark.parametrize("pagina,campos", [
    ("perfecta.html", ["Nombre completo", "Correo electrónico", "Mensaje"]),
    ("sin_contacto.html", ["Nombre completo", "Trámite", "Fecha preferida"]),
    ("formulario_sin_etiquetas.html", ["", "", ""]),
])
def test_d_enumera_campos(pagina, campos, vivo):
    r = estrategias.mejor_estrategia(vivo, _tarea("D", pagina), PALABRAS)
    assert r.mejor.hallazgo["campos"] == campos


def test_b_registra_requisitos(vivo):
    r = estrategias.mejor_estrategia(vivo, _tarea("B", "perfecta.html"), PALABRAS)
    assert r.mejor.hallazgo["requisitos"] == [
        "Identificación oficial vigente", "Comprobante de domicilio",
        "Comprobante de pago del predial", "Croquis del terreno"]


def test_b_sin_encabezados_incluye_descargas(vivo):
    """Límite declarado: 'Descargas' es texto sin marca y la estrategia lo lee como requisito;
    distinguirlo exigiría significado (por eso el yaml dice 32 y no 31)."""
    r = estrategias.mejor_estrategia(vivo, _tarea("B", "sin_encabezados.html"), PALABRAS)
    assert r.mejor.hallazgo["requisitos"][-2:] == ["Croquis del terreno", "Descargas"]


def test_a_registra_contacto(vivo):
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "perfecta.html"), PALABRAS)
    assert r.mejor.hallazgo["contacto"] == "Teléfono: 667 555 0142"


# ---------- Páginas ce_*: casos que los yaml no cubren ----------

def test_cruza_por_nombre_sin_reentrar_y_sin_falsos_telefonos(vivo):
    """ce_contacto: enlaces 'Contacto' (misma URL, no se activa) y 'Contáctanos'.
    Lista: 1 + 1 + Enter = 3; en ce_p1 lee 5 paradas (tres textos que NO son teléfono) = 8.
    Leer: 3 + Enter + 5 = 9. H y D no tienen sección con palabra clave."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_contacto.html"), PALABRAS)
    assert r.estrategia == "enlace_por_nombre" and r.friccion == 8
    assert r.mejor.hallazgo["contacto"] == "Tel. 667 555 0100"
    assert _teclas(r.mejor).count("Enter") == 1
    assert _intentos(r)["no_dirigida"].pulsaciones == 9
    assert not _intentos(r)["H_a_seccion"].llego
    assert not _intentos(r)["D_a_seccion"].llego


def test_mailto_cierra_sin_enter_y_la_url_no_decide(vivo):
    """ce_mailto: 'Inicio' tiene palabras clave SOLO en su URL (no existe ese archivo) y
    'Escríbenos' es mailto. Tab: 2. Leer: 4. Ninguna estrategia pulsa Enter."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_mailto.html"), PALABRAS)
    assert r.estrategia == "Tab_inicio" and r.friccion == 2
    assert _intentos(r)["no_dirigida"].pulsaciones == 4
    assert not _intentos(r)["enlace_por_nombre"].llego  # "Escríbenos" no es palabra de la tarea A
    assert all("Enter" not in _teclas(i) for i in r.intentos)


def test_tel_elegido_por_nombre(vivo):
    """ce_tel: 'Teléfono' es el 2.º enlace: 1 + 1 = 2, sin Enter (abriría otra aplicación).
    Empata con Tab (2) y gana por el orden declarado."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_tel.html"), PALABRAS)
    assert r.estrategia == "enlace_por_nombre" and r.friccion == 2
    assert _intentos(r)["Tab_inicio"].pulsaciones == 2
    assert "Enter" not in _teclas(r.mejor)


def test_busqueda_no_es_el_formulario(vivo):
    """ce_formulario: F = búsqueda, botón Buscar, Nombre, Colonia = 4 (no sigue al botón Enviar).
    H = Oficina, Solicitud + F, F = 4: empata y gana H por el orden declarado. Tab = 4."""
    r = estrategias.mejor_estrategia(vivo, _tarea("D", "ce_formulario.html"), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 4
    f = _intentos(r)["F_a_campos"]
    assert f.llego and f.pulsaciones == 4 and f.hallazgo["campos"] == ["Nombre", "Colonia"]
    assert _intentos(r)["Tab_inicio"].pulsaciones == 4
    assert _intentos(r)["no_dirigida"].pulsaciones == 8


def test_marcador_sin_requisitos_no_cuenta(vivo):
    """ce_requisitos: 'Requisitos generales' va seguido de un encabezado, no cuenta. El bloque
    real termina en un enlace, que no se cobra. H = 1 + 5 flechas = 6; leer = 6 (empate)."""
    r = estrategias.mejor_estrategia(vivo, _tarea("B", "ce_requisitos.html"), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 6
    assert r.mejor.hallazgo["requisitos"] == ["Identificación oficial", "Comprobante de domicilio"]
    assert _intentos(r)["no_dirigida"].pulsaciones == 6


def test_candidato_fallido_acumula_costo(vivo):
    """ce_candidatos: 'Contacto' lleva a ce_p2, sin datos. Lista: 1 + Enter + leer 2 + volver = 5;
    luego 1 + 1 + Enter + leer 5 = 8; total 13. Leer: 2 + Enter + 2 + volver + 1 + Enter + 5 = 13."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_candidatos.html"), PALABRAS)
    assert r.estrategia == "enlace_por_nombre" and r.friccion == 13
    assert _teclas(r.mejor).count("volver") == 1
    assert _intentos(r)["no_dirigida"].pulsaciones == 13


def test_probar_rechaza_por_titulo(vivo):
    """enlaces_ambiguos B: 'Otro trámite' se rechaza solo por el título (trae la palabra
    'trámite', pero no el trámite buscado). 8 intentos × 3 + K + Enter = 26 (yaml)."""
    r = estrategias.mejor_estrategia(vivo, _tarea("B", "enlaces_ambiguos.html"), PALABRAS)
    assert r.estrategia == "probar_enlaces" and r.friccion == 35
    assert _teclas(r.mejor).count("volver") == 8
    assert _teclas(r.mejor).count("Enter") == 9


# ---------- No evaluable y CAPTCHA ----------

def _lento(vivo):
    return lambda pagina: vivo(pagina, timeout_ms=1_000)


def test_timeout_es_no_evaluable_no_no_llego(vivo):
    """ce_lento: el único candidato da timeout y nadie más llega."""
    r = estrategias.mejor_estrategia(_lento(vivo), _tarea("A", "ce_lento.html"), PALABRAS)
    assert r.mejor is None and r.friccion is None
    assert r.no_evaluable.motivo == "timeout"
    assert _intentos(r)["enlace_por_nombre"].no_evaluable.motivo == "timeout"
    assert _intentos(r)["enlace_por_nombre"].pulsaciones == 2  # 1 + Enter (cuenta)


def test_si_otra_llega_gana_aunque_una_de_timeout(vivo):
    """ce_lento_con_tel: H = Portal, Teléfonos + 1 flecha = 3; la lista da timeout."""
    r = estrategias.mejor_estrategia(_lento(vivo), _tarea("A", "ce_lento_con_tel.html"), PALABRAS)
    assert r.estrategia == "H_a_seccion" and r.friccion == 3
    assert r.no_evaluable is None
    assert _intentos(r)["enlace_por_nombre"].no_evaluable.motivo == "timeout"


def test_profundidad_agotada_es_no_evaluable(vivo):
    """ce_cadena_0..3: cada página solo tiene un enlace 'Contacto' a la siguiente. Lista: 1 + Enter;
    en cada nivel lee encabezado + enlace y Enter (3 × 3 = 9) = 11; el último Enter excede."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_cadena_0.html"), PALABRAS)
    assert r.mejor is None and r.no_evaluable.motivo == "profundidad"
    assert _intentos(r)["enlace_por_nombre"].pulsaciones == 11


def test_captcha_se_registra_y_no_detiene(vivo):
    """ce_con_captcha: la regla del CAPTCHA es de 3D; aquí solo se registra. Lo más consumido
    (leer y Tab) = 6: leer = 2 + Enter + 2 + volver; Tab = 1 + Enter + 1 + 1 + volver + 1."""
    r = estrategias.mejor_estrategia(vivo, _tarea("A", "ce_con_captcha.html"), PALABRAS)
    assert r.mejor is None and r.no_evaluable is None
    assert "g-recaptcha" in r.captcha and r.consumidas == 6


# ---------- Reproducibilidad ----------

def test_reproducible(vivo):
    tarea = _tarea("B", "perfecta.html")
    uno, dos = (estrategias.correr("H_a_seccion", vivo, tarea, PALABRAS) for _ in range(2))
    assert [(p.tecla, p.anuncio, p.pulsaciones) for p in uno.trayectoria] == \
           [(p.tecla, p.anuncio, p.pulsaciones) for p in dos.trayectoria]
