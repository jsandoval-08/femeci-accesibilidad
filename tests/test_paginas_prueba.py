"""Fase 1B: las páginas de prueba se abren con capturar() y el árbol muestra la falla prevista.

Además, cada friccion_esperada de los .esperado.yaml se recalcula sobre el árbol REAL
recorriendo la ruta declarada paso a paso (contador mínimo, no es el emulador). Lo que se
verifica es el costo de la ruta declarada; que esa sea la mejor estrategia se argumenta en
el campo `razon` de cada tarea.

Convenciones de conteo (ver CLAUDE.md):
  - Paradas (flecha abajo): encabezado, enlace, botón, campo de formulario y texto suelto.
    El texto dentro de una parada no es otra parada; el contenedor de una lista no cuenta.
  - El cursor empieza ANTES de la primera parada.
  - H / K / F: 1 pulsación por cada encabezado / enlace / campo saltado hasta el objetivo.
  - leer: 1 pulsación por parada avanzada.  lista_enlaces (NVDA+F7): 1 + flechas hasta el
    enlace (orden del documento, sin filtrar escribiendo).  Enter: 1.  volver (Alt+←): 1.
"""

import json
import re
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

from src.captura import capturar

PAGINAS = Path(__file__).parent / "paginas"
NOMBRES = [
    "perfecta",
    "sin_encabezados",
    "sin_contacto",
    "enlaces_ambiguos",
    "formulario_sin_etiquetas",
    "pdf_escaneado",
]
DESTINOS = ["enlaces_ambiguos_tramite", "enlaces_ambiguos_otro"]
UMBRAL = 15  # UMBRAL de fricción para "completable"
LANDMARKS = {"banner", "navigation", "main", "contentinfo", "region", "complementary", "search"}
ESTADOS = {"completable", "con_dificultad", "no_completable"}
TIPOS_FALLA = {"no_encontrado", "no_identificable", "cierre_roto"}
ESTRATEGIAS = {"H_a_seccion", "F_a_campos", "enlace_por_nombre", "probar_enlaces", "no_dirigida"}
CAMPOS = {"textbox", "searchbox", "combobox", "checkbox", "radio", "listbox", "spinbutton",
          "date", "DateTime", "InputTime"}
PARADAS = {"heading", "link", "button"} | CAMPOS


def _paradas(arbol):
    """Lineariza el árbol en orden de documento: lista de (rol, nombre, url) por parada."""
    nodos = {n["nodeId"]: n for n in arbol["nodes"]}
    raiz = next(n for n in arbol["nodes"] if "parentId" not in n)
    salida = []

    def visitar(n, dentro_de_parada):
        rol = n["role"]["value"]
        nombre = n.get("name", {}).get("value", "")
        if not n.get("ignored") and not dentro_de_parada:
            if rol in PARADAS:
                url = next((p["value"].get("value") for p in n.get("properties", [])
                            if p["name"] == "url"), None)
                salida.append((rol, nombre, url))
                dentro_de_parada = True
            elif rol == "StaticText" and nombre.strip():
                salida.append((rol, nombre, None))
        for hijo in n.get("childIds", []):
            if hijo in nodos:
                visitar(nodos[hijo], dentro_de_parada)

    visitar(raiz, False)
    return salida


@pytest.fixture(scope="module")
def capturas(tmp_path_factory):
    """Captura cada página una vez; devuelve {nombre: {"nodos": [...], "paradas": [...]}}."""
    base = tmp_path_factory.mktemp("capturas")
    salida = {}
    for nombre in NOMBRES + DESTINOS:
        carpeta = capturar((PAGINAS / f"{nombre}.html").resolve().as_uri(), base=base)
        meta = json.loads((carpeta / "metadatos.json").read_text(encoding="utf-8"))
        assert meta["estado_http"] == 200 and meta["num_iframes"] == 0
        arbol = json.loads((carpeta / "arbol_ax.json").read_text(encoding="utf-8"))
        salida[nombre] = {
            "nodos": [
                (n["role"]["value"], n.get("name", {}).get("value", ""))
                for n in arbol["nodes"]
                if not n.get("ignored")
            ],
            "paradas": _paradas(arbol),
        }
    return salida


# ---------- Contador de fricción de una ruta declarada ----------

def _buscar(paradas, cursor, rol, nombre):
    """Primera parada después del cursor con ese rol y nombre."""
    for i in range(cursor + 1, len(paradas)):
        if paradas[i][0] == rol and paradas[i][1] == nombre:
            return i
    raise AssertionError(f"No se encontró {rol} '{nombre}' después de la parada {cursor}")


def _texto_pdf(ruta):
    lector = PdfReader(PAGINAS / ruta)
    return "".join(p.extract_text() or "" for p in lector.pages).strip()


def friccion(ruta, pagina, capturas):
    """Recorre la ruta sobre el árbol real. Devuelve (pulsaciones, cierre_ok)."""
    pila, cursor, total, cierre_ok = [], -1, 0, True
    for paso in ruta:
        tecla = paso["tecla"]
        paradas = capturas[pagina]["paradas"]
        if tecla in ("H", "K", "F"):
            roles = {"H": {"heading"}, "K": {"link"}, "F": CAMPOS}[tecla]
            j = _buscar(paradas, cursor, paso["rol"], paso["nombre"])
            assert paradas[j][0] in roles
            total += sum(1 for r, _, _ in paradas[cursor + 1:j + 1] if r in roles)
            cursor = j
        elif tecla in ("leer", "leer_de_corrido"):
            if paso.get("hasta") == "fin":
                total += len(paradas) - 1 - cursor
                cursor = len(paradas) - 1
            else:
                objetivo = paso.get("hasta", paso)
                j = _buscar(paradas, cursor, objetivo["rol"], objetivo["nombre"])
                total += j - cursor
                cursor = j
        elif tecla == "lista_enlaces":
            j = _buscar(paradas, -1, "link", paso["nombre"])
            enlaces = [i for i, (r, _, _) in enumerate(paradas) if r == "link"]
            total += 1 + enlaces.index(j)  # abrir lista + flechas
            cursor = j
        elif tecla == "Enter":
            total += 1
            destino = paso["destino"]
            if destino.endswith(".pdf"):
                cierre_ok = _texto_pdf(destino) != ""
            else:
                pila.append((pagina, cursor))
                pagina, cursor = destino.removesuffix(".html"), -1
        elif tecla == "volver":
            total += 1
            pagina, cursor = pila.pop()
        elif tecla == "probar_enlaces":
            # Sin conocer el objetivo: prueba en orden cada enlace con esos nombres
            # (K + Enter); si al llegar se anuncia otra cosa, vuelve (Alt+←) y sigue.
            # La URL se usa SOLO aquí, como oráculo de a dónde llega cada intento.
            for i in range(cursor + 1, len(paradas)):
                rol, nombre, url = paradas[i]
                if rol != "link" or nombre not in paso["nombres"]:
                    continue
                total += sum(1 for r, _, _ in paradas[cursor + 1:i + 1] if r == "link") + 1
                cursor = i
                if url.endswith("/" + paso["destino"]):
                    pila.append((pagina, cursor))
                    pagina, cursor = paso["destino"].removesuffix(".html"), -1
                    break
                total += 1  # volver
            else:
                raise AssertionError("Ningún candidato llevó al destino")
        else:
            raise AssertionError(f"Tecla desconocida: {tecla}")
    return total, cierre_ok


# ---------- Estructura de cada página ----------

def _roles(nodos):
    return [r for r, _ in nodos]


def test_perfecta(capturas):
    nodos = capturas["perfecta"]["nodos"]
    assert [n for r, n in nodos if r == "heading"][:4] == [
        "Ayuntamiento de Villa Ejemplo", "Noticias", "Trámites", "Licencia de construcción menor",
    ]
    assert {"banner", "navigation", "main", "contentinfo"} <= set(_roles(nodos))
    campos = [n for r, n in nodos if r == "textbox"]
    assert len(campos) == 3 and all(campos)


def test_bloque_noticias_igual_en_todas(capturas):
    """El bloque de noticias son 20 paradas en todas las páginas."""
    for nombre in NOMBRES:
        paradas = capturas[nombre]["paradas"]
        inicio = next(i for i, p in enumerate(paradas) if p[1] == "Noticias")
        fin = next(i for i, p in enumerate(paradas) if p[1] == "Trámites")
        assert fin - inicio == 20, nombre


def test_sin_encabezados(capturas):
    nodos = capturas["sin_encabezados"]["nodos"]
    assert "heading" not in _roles(nodos)
    assert not LANDMARKS & set(_roles(nodos))


def test_sin_contacto(capturas):
    nodos = capturas["sin_contacto"]["nodos"]
    textos = " ".join(n for _, n in nodos).lower()
    assert "contacto" not in textos and "tel" not in textos and "@" not in textos
    assert not re.search(r"\d{3}\s?\d{3}", textos)  # ningún número de teléfono
    html = (PAGINAS / "sin_contacto.html").read_text(encoding="utf-8")
    assert "tel:" not in html and "mailto:" not in html
    campos = [n for r, n in nodos if r in ("textbox", "combobox")]
    assert len(campos) == 3 and all(campos)


def test_enlaces_ambiguos(capturas):
    paradas = capturas["enlaces_ambiguos"]["paradas"]
    enlaces = [(n, u) for r, n, u in paradas if r == "link"]
    nombres = [n for n, _ in enlaces]
    assert nombres.count("Leer más") == 8 and nombres.count("clic aquí") == 4
    assert nombres.count("") == 3  # íconos-enlace sin nombre
    tarjetas = [u for n, u in enlaces if n in ("Leer más", "clic aquí")]
    assert tarjetas[8].endswith("/enlaces_ambiguos_tramite.html")  # tarjeta 9 de 12
    assert sum(u.endswith("/enlaces_ambiguos_otro.html") for u in tarjetas) == 11


def test_formulario_sin_etiquetas(capturas):
    nodos = capturas["formulario_sin_etiquetas"]["nodos"]
    campos = [n for r, n in nodos if r == "textbox"]
    assert len(campos) == 3 and all(n == "" for n in campos)
    html = (PAGINAS / "formulario_sin_etiquetas.html").read_text(encoding="utf-8").lower()
    formulario = re.search(r"<form.*?</form>", html, flags=re.S).group(0)
    for prohibido in ("<label", "placeholder", "title=", "aria-label", "aria-labelledby", "aria-describedby"):
        assert prohibido not in formulario, prohibido


def test_pdfs():
    assert "Plan Municipal de Desarrollo" in _texto_pdf("docs/plan_municipal.pdf")
    assert _texto_pdf("docs/plan_municipal_escaneado.pdf") == ""


# ---------- Respuestas esperadas ----------

def _esperado(nombre):
    return yaml.safe_load((PAGINAS / f"{nombre}.esperado.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("nombre", NOMBRES)
def test_esperado_yaml(nombre, capturas):
    datos = _esperado(nombre)
    assert datos["pagina"] == f"{nombre}.html"
    assert set(datos["tareas"]) == {"A", "B", "C", "D"}
    for clave, t in datos["tareas"].items():
        donde = f"{nombre} {clave}"
        assert (PAGINAS / t["entrada"]).exists(), donde
        assert t["estado"] in ESTADOS and t["estrategia"] in ESTRATEGIAS and t["razon"], donde

        # La fricción declarada coincide con la del árbol real
        f, cierre_ok = friccion(t["ruta"], t["entrada"].removesuffix(".html"), capturas)
        assert f == t["friccion_esperada"], f"{donde}: árbol {f} ≠ yaml {t['friccion_esperada']}"

        # El estado sale de la regla de fricción
        if t["estado"] == "no_completable":
            assert t["tipo_falla"] in TIPOS_FALLA, donde
            if t["tipo_falla"] == "cierre_roto":
                assert not cierre_ok, donde
        else:
            assert t["tipo_falla"] is None and cierre_ok, donde
            esperado = "completable" if f <= UMBRAL else "con_dificultad"
            assert t["estado"] == esperado, f"{donde}: fricción {f} → {esperado}"


def test_casos_lejos_del_umbral():
    """Los casos con dificultad siguen siéndolo con el umbral mayor de sensibilidad (25)."""
    assert _esperado("sin_encabezados")["tareas"]["A"]["friccion_esperada"] > 25
    assert _esperado("sin_encabezados")["tareas"]["B"]["friccion_esperada"] > 25
    assert _esperado("enlaces_ambiguos")["tareas"]["B"]["friccion_esperada"] > 25
