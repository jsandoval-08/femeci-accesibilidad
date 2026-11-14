"""Fase 3F.2: servidor local y guardado del modo exploración. Usa el motor de prueba (sin red) y una
carpeta temporal: nunca escribe en exploracion/ ni en estudio/."""

import json
import time

import pytest
from fastapi.testclient import TestClient

from app import guardado
from app.seguridad import Config
from app.servidor import crear_app
from motor_falso import MotorFalso

HOSTS = ("ciudadano.sinaloa.gob.mx", "culiacan.gob.mx")


@pytest.fixture
def entorno(tmp_path):
    motor, abiertos = MotorFalso(), []
    app = crear_app(Config(HOSTS, tmp_path), motor=motor, abrir=abiertos.append)
    cliente = TestClient(app, base_url="http://127.0.0.1")
    cliente.headers["X-Atorapp-Token"] = app.state.token
    return cliente, motor, abiertos, tmp_path


def _eventos(cliente, id_):
    with cliente.stream("GET", f"/api/evaluaciones/{id_}/eventos") as r:
        texto = "".join(r.iter_text())
    eventos = []
    for bloque in texto.strip().split("\n\n"):
        lineas = dict(l.split(": ", 1) for l in bloque.splitlines() if not l.startswith(":"))
        if "event" in lineas:
            eventos.append((lineas["event"], json.loads(lineas["data"])))
    return eventos


def _evaluar(cliente, **pedido):
    r = cliente.post("/api/evaluaciones", json={"url": "http://127.0.0.1:9/portada.html", "tarea": "A", **pedido})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_evaluacion_completa_con_eventos_y_guardado(entorno):
    cliente, motor, _, base = entorno
    id_ = _evaluar(cliente)
    eventos = _eventos(cliente, id_)
    tipos = [t for t, _ in eventos]
    assert tipos[0] == "inicio" and tipos[-1] == "fin"
    assert tipos.count("estrategia") == 3 and tipos.count("paso") == 12 and "fase" in tipos
    assert eventos[0][1]["estrategias"][:2] == ["H_a_seccion", "D_a_seccion"]
    datos = eventos[-1][1]["datos"]
    assert datos["modo"] == "exploracion" and "no verificada con NVDA" in datos["aviso"]
    assert datos["requiere_confirmacion"] and datos["confirmacion"] is None
    assert [o["pulsaciones"] for o in datos["opciones"]] == [3, 7]
    assert (base / id_ / "exploracion.json").is_file()
    assert "pausa_s" not in motor.llamadas[0]["opciones"]  # el servidor no baja la pausa por su cuenta


def test_confirmar_y_exportar(entorno):
    cliente, _, abiertos, base = entorno
    id_ = _evaluar(cliente)
    _eventos(cliente, id_)
    assert guardado.vigente(cliente.get(f"/api/evaluaciones/{id_}").json()) is None  # por confirmar
    datos = cliente.post(f"/api/evaluaciones/{id_}/confirmacion", json={"eleccion": "1"}).json()
    v = guardado.vigente(datos)
    assert (v["estado"], v["estrategia"], v["friccion"]) == ("completable", "enlace_por_nombre", 7)
    assert [x["estrategia"] for x in v["falsas_llegadas"]] == ["H_a_seccion"]
    assert cliente.post(f"/api/evaluaciones/{id_}/confirmacion", json={"eleccion": "7"}).status_code == 422
    r = cliente.post(f"/api/evaluaciones/{id_}/exportar").json()
    md = (base / id_ / "reporte.md").read_text(encoding="utf-8")
    assert r["markdown"] == md
    assert "estimación experimental, no verificada con NVDA" in md
    assert "Confirmado por la persona (no por NVDA)" in md and "**Completable" in md
    assert "conformidad WCAG" not in md
    cliente.post(f"/api/abrir/carpeta/{id_}")
    cliente.post("/api/abrir/estudio")
    assert abiertos[0].endswith(id_) and abiertos[1].endswith("index.html")
    filas = cliente.get("/api/historial").json()
    assert filas[0]["id"] == id_ and filas[0]["estado"] == "completable"


def test_ninguna_de_estas(entorno):
    cliente, _, _, _ = entorno
    id_ = _evaluar(cliente)
    _eventos(cliente, id_)
    v = guardado.vigente(cliente.post(f"/api/evaluaciones/{id_}/confirmacion", json={"eleccion": "ninguna"}).json())
    assert (v["estado"], v["tipo_falla"]) == ("no_completable", "no_encontrado")


def test_markdown_por_confirmar_es_condicional(entorno):
    cliente, _, _, _ = entorno
    id_ = _evaluar(cliente)
    _eventos(cliente, id_)
    md = cliente.post(f"/api/evaluaciones/{id_}/exportar").json()["markdown"]
    assert "**Por confirmar.** Si es lo que buscabas: Completable" in md
    assert "\n**Completable" not in md  # nunca completable a secas


@pytest.mark.parametrize("pedido,codigo,texto", [
    ({"tarea": "B"}, 422, "trámite"),
    ({"tarea": "B", "tramite": "   "}, 422, "trámite"),
    ({"tarea": "Z"}, 422, "tarea"),
    ({"url": "sinaloa.gob.mx"}, 422, "http"),
    ({"url": "https://www.culiacan.gob.mx/"}, 403, "a ciegas"),
    ({"url": "https://ciudadano.sinaloa.gob.mx/tramite"}, 403, "a ciegas"),
])
def test_pedidos_rechazados_sin_correr_nada(entorno, pedido, codigo, texto):
    cliente, motor, _, base = entorno
    r = cliente.post("/api/evaluaciones", json={"url": "http://127.0.0.1:9/p.html", "tarea": "A", **pedido})
    assert r.status_code == codigo and texto in r.json()["detail"]
    assert motor.llamadas == [] and list(base.iterdir()) == []


def test_tramite_llega_al_motor(entorno):
    cliente, motor, _, _ = entorno
    _eventos(cliente, _evaluar(cliente, tarea="B", tramite=" Licencia de construcción "))
    assert (motor.llamadas[0]["letra"], motor.llamadas[0]["tramite"]) == ("B", "Licencia de construcción")


def test_sin_token_o_con_otro_host_se_niega(entorno):
    cliente, motor, _, _ = entorno
    sin_token = TestClient(cliente.app, base_url="http://127.0.0.1")
    assert sin_token.post("/api/evaluaciones", json={"url": "http://127.0.0.1:9/", "tarea": "A"}).status_code == 403
    otro = TestClient(cliente.app, base_url="http://atacante.example")
    otro.headers["X-Atorapp-Token"] = cliente.app.state.token
    assert otro.get("/api/historial").status_code == 403
    assert motor.llamadas == []


def test_detener_no_guarda_nada(tmp_path):
    import threading
    liberar = threading.Event()
    app = crear_app(Config(HOSTS, tmp_path), motor=MotorFalso(liberar=liberar), abrir=lambda r: None)
    cliente = TestClient(app, base_url="http://127.0.0.1")
    cliente.headers["X-Atorapp-Token"] = app.state.token
    id_ = _evaluar(cliente)
    assert cliente.post("/api/evaluaciones", json={"url": "http://127.0.0.1:9/", "tarea": "A"}).status_code == 409
    cliente.post(f"/api/evaluaciones/{id_}/detener")
    liberar.set()
    assert _eventos(cliente, id_)[-1][0] == "detenida"
    assert not (tmp_path / id_).exists()
    assert cliente.get("/api/historial").json() == []


def test_ids_fuera_de_exploracion(entorno):
    cliente, _, _, _ = entorno
    for malo in ("..", "..%2F..%2Festudio", "20261114-120000_x_A"):
        assert cliente.get(f"/api/evaluaciones/{malo}").status_code == 404
