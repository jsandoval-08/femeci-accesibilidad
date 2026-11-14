"""Servidor local del modo exploración (Fase 3F): FastAPI en 127.0.0.1, sin nada expuesto a la red.

Una evaluación a la vez, en un hilo aparte (la API síncrona de Playwright no corre dentro del bucle
asíncrono). Los pasos llegan a la UI conforme salen, por SSE (Server-Sent Events).

Protección: un servidor local que navega sitios podría dispararse desde cualquier página web abierta
en el navegador (CSRF) o por DNS rebinding. Por eso (1) solo se aceptan peticiones con Host 127.0.0.1
o localhost y (2) todo POST exige el encabezado X-Atorapp-Token, un valor al azar generado al arrancar
que solo conoce la página servida aquí.
"""

import json
import os
import secrets
import shutil
import threading
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import guardado
from app.motor import Detenida, estrategias_de, explorar
from app.seguridad import RAIZ, Config, EntradaInvalida, HostBloqueado, validar_entrada
from src.estrategias import ETIQUETAS
from src.navegador import PAUSA_S
from src.sitio import TOPE_NAVEGACIONES, TOPE_PULSACIONES
from src.veredicto import UMBRAL, UMBRALES_SENSIBILIDAD

UI = Path(__file__).resolve().parent / "ui"
INTERFAZ = RAIZ / "interfaz"
FINALES = {"fin", "detenida", "bloqueada", "error"}
LATIDO_S = 15  # comentario SSE para mantener viva la conexión


class Pedido(BaseModel):
    url: str = ""
    tarea: str = ""
    tramite: str | None = None


class Eleccion(BaseModel):
    eleccion: str


class Evaluacion:
    """Una evaluación en curso: sus eventos (se guardan todos, para quien se conecte tarde)."""

    def __init__(self, id_: str, carpeta: Path):
        self.id, self.carpeta = id_, carpeta
        self.eventos: list[tuple[str, dict]] = []
        self.terminada = False
        self.detener = threading.Event()
        self._cond = threading.Condition()

    def publicar(self, tipo: str, datos: dict) -> None:
        with self._cond:
            self.eventos.append((tipo, datos))
            self.terminada = self.terminada or tipo in FINALES
            self._cond.notify_all()

    def sse(self):
        i = 0
        while True:
            with self._cond:
                if i >= len(self.eventos) and not self.terminada:
                    self._cond.wait(LATIDO_S)
                nuevos, i, fin = self.eventos[i:], len(self.eventos), self.terminada
            if not nuevos and not fin:
                yield ": sigue\n\n"
            for tipo, datos in nuevos:
                yield f"event: {tipo}\ndata: {json.dumps(datos, ensure_ascii=False)}\n\n"
            if fin:
                return


def crear_app(config: Config, motor=explorar, opciones_motor: dict | None = None, abrir=None,
              hosts_permitidos=("127.0.0.1", "localhost")) -> FastAPI:
    """motor y abrir se pueden cambiar en las pruebas (un motor de prueba; abrir sin os.startfile).
    opciones_motor: p. ej. pausa 0 en pruebas locales; explorar() exige 1 s fuera de 127.0.0.1."""
    app = FastAPI(title="Atorapp · modo exploración", docs_url=None, redoc_url=None, openapi_url=None)
    token = secrets.token_urlsafe(24)
    app.state.token = token
    opciones = dict(opciones_motor or {})
    abrir = abrir or os.startfile
    estado = {"actual": None}

    @app.middleware("http")
    async def solo_local(request: Request, siguiente):
        host = (request.headers.get("host") or "").rsplit(":", 1)[0].strip("[]")
        if host not in hosts_permitidos:
            return PlainTextResponse("Solo se atiende a 127.0.0.1.", status_code=403)
        return await siguiente(request)

    def con_token(x_atorapp_token: str = Header(default="")):
        if not secrets.compare_digest(x_atorapp_token, token):
            raise HTTPException(403, "falta el token de la app")

    def carpeta_de(id_: str) -> Path:
        carpeta = config.carpeta / id_
        if not guardado.es_id(id_) or not (carpeta / guardado.ARCHIVO).is_file():
            raise HTTPException(404, "no existe esa evaluación")
        return carpeta

    # ---------- Páginas ----------

    @app.get("/", response_class=HTMLResponse)
    def inicio():
        return (UI / "index.html").read_text(encoding="utf-8").replace("{{TOKEN}}", token)

    app.mount("/ui", StaticFiles(directory=UI, check_dir=False), name="ui")
    # Solo para compartir marca.css y las fuentes con la interfaz del estudio.
    app.mount("/estudio", StaticFiles(directory=INTERFAZ), name="estudio")

    @app.get("/api/info")
    def info():
        return {"hosts_bloqueados": list(config.hosts_bloqueados), "umbral": UMBRAL,
                "umbrales": list(UMBRALES_SENSIBILIDAD), "pausa_s": PAUSA_S,
                "topes": {"pulsaciones": TOPE_PULSACIONES, "navegaciones": TOPE_NAVEGACIONES}}

    # ---------- Evaluar ----------

    @app.post("/api/evaluaciones", dependencies=[Depends(con_token)])
    def evaluar(pedido: Pedido):
        letra, tramite = pedido.tarea.strip().upper(), (pedido.tramite or "").strip() or None
        if letra not in ("A", "B", "C", "D"):
            raise HTTPException(422, "elige una tarea: A, B, C o D")
        if letra == "B" and not tramite:
            raise HTTPException(422, "la tarea B necesita el trámite que la persona busca")
        try:
            url = validar_entrada(pedido.url, config.hosts_bloqueados)  # barrera 1
        except EntradaInvalida as e:
            raise HTTPException(422, str(e)) from None
        except HostBloqueado as e:
            raise HTTPException(403, str(e)) from None
        actual = estado["actual"]
        if actual is not None and not actual.terminada:
            raise HTTPException(409, "ya hay una evaluación en curso")
        carpeta = guardado.nueva_carpeta(config.carpeta, url, letra)
        ev = Evaluacion(carpeta.name, carpeta)
        estado["actual"] = ev
        ev.publicar("inicio", {"id": ev.id, "url": url, "tarea": letra, "tramite": tramite,
                               "estrategias": [ETIQUETAS.get(c, c) for c in estrategias_de(letra)]})
        threading.Thread(target=_correr, args=(ev, url, letra, tramite), daemon=True).start()
        return {"id": ev.id}

    def _correr(ev: Evaluacion, url, letra, tramite):
        try:
            ex = motor(url, letra, tramite, ev.carpeta, config.hosts_bloqueados, al_evento=ev.publicar,
                       detener=ev.detener, **opciones)
            datos = guardado.a_diccionario(ex)
            guardado.guardar(ev.carpeta, datos)
            ev.publicar("fin", {"id": ev.id, "datos": datos})
        except Detenida:
            shutil.rmtree(ev.carpeta, ignore_errors=True)  # lo detenido no se guarda
            ev.publicar("detenida", {})
        except HostBloqueado as e:
            shutil.rmtree(ev.carpeta, ignore_errors=True)  # barrera 3: nada de ese host se guarda
            ev.publicar("bloqueada", {"mensaje": str(e)})
        except Exception as e:  # noqa: BLE001 - se informa a la UI, no se oculta
            shutil.rmtree(ev.carpeta, ignore_errors=True)
            ev.publicar("error", {"mensaje": f"{type(e).__name__}: {e}"})

    def _en_curso(id_: str) -> Evaluacion:
        ev = estado["actual"]
        if ev is None or ev.id != id_:
            raise HTTPException(404, "esa evaluación no está en curso")
        return ev

    @app.get("/api/evaluaciones/{id_}/eventos")
    def eventos(id_: str):
        ev = _en_curso(id_)
        return StreamingResponse(ev.sse(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache"})

    @app.post("/api/evaluaciones/{id_}/detener", dependencies=[Depends(con_token)])
    def detener(id_: str):
        _en_curso(id_).detener.set()
        return {"ok": True}

    # ---------- Lo guardado ----------

    @app.get("/api/evaluaciones/{id_}")
    def leer(id_: str):
        return guardado.leer(carpeta_de(id_))

    @app.post("/api/evaluaciones/{id_}/confirmacion", dependencies=[Depends(con_token)])
    def confirmar(id_: str, eleccion: Eleccion):
        try:
            return guardado.confirmar(carpeta_de(id_), eleccion.eleccion)
        except ValueError as e:
            raise HTTPException(422, str(e)) from None

    @app.post("/api/evaluaciones/{id_}/exportar", dependencies=[Depends(con_token)])
    def exportar(id_: str):
        ruta = guardado.exportar(carpeta_de(id_))
        return {"ruta": str(ruta), "markdown": ruta.read_text(encoding="utf-8")}

    @app.get("/api/historial")
    def historial():
        return guardado.historial(config.carpeta)

    @app.post("/api/abrir/estudio", dependencies=[Depends(con_token)])
    def abrir_estudio():
        abrir(str(INTERFAZ / "index.html"))  # la interfaz 3E tal cual, por file://
        return {"ok": True}

    @app.post("/api/abrir/carpeta/{id_}", dependencies=[Depends(con_token)])
    def abrir_carpeta(id_: str):
        abrir(str(carpeta_de(id_)))
        return {"ok": True}

    return app
