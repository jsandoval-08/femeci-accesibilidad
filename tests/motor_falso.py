"""Fase 3F: motor de prueba para el servidor y la UI. No toca la red ni Playwright.

Emite los mismos eventos que app.motor.explorar() y devuelve una Exploracion armada a mano con dos
estrategias que creen llegar a cosas distintas (la más barata es una falsa llegada, como en
ce_otro_telefono). Con `liberar` se queda esperando a mitad del recorrido: así la UI se puede revisar
"evaluando".
"""

import threading

from app.motor import Detenida, Exploracion, _sin_cargar, motivo_no_cargo
from app.seguridad import validar_entrada
from src.emulador import Paso
from src.estrategias import Intento, ResultadoTarea, Tarea

URL = "http://127.0.0.1:9/portada.html"


def _pasos(lista):
    return tuple(Paso(tecla, anuncio, n, True, n + 1, url=URL) for n, (tecla, anuncio) in enumerate(lista))


H = _pasos([("H", "encabezado, nivel 1, Ayuntamiento de Prueba"),
            ("H", "encabezado, nivel 2, Contacto"),
            ("leer", "Teléfono: 667 555 0999")])
LISTA = _pasos([("lista_enlaces", "lista de enlaces"), ("flecha_lista", "Inicio"),
                ("flecha_lista", "Atención ciudadana"), ("Enter", "Atención ciudadana"),
                ("leer", "Atención ciudadana"), ("leer", "Horario: 8 a 15 h"),
                ("leer", "Teléfono: 667 555 0100")])
TAB = _pasos([("Tab", "enlace, Inicio"), ("Tab", "enlace, Trámites")])


def resultado(letra="A", tramite=None):
    intentos = (
        Intento("H_a_seccion", True, 3, H, None, None, {"contacto": "Teléfono: 667 555 0999", "url": None}, ()),
        Intento("enlace_por_nombre", True, 7, LISTA, None, None,
                {"contacto": "Teléfono: 667 555 0100", "url": None}, ()),
        Intento("Tab_inicio", False, 2, TAB, "no encontró el objetivo con lo anunciado", None, None, ()),
    )
    return ResultadoTarea(Tarea(letra, URL, tramite), "H_a_seccion", intentos[0], 3, None, None, None, (),
                          intentos)


class MotorFalso:
    def __init__(self, liberar: threading.Event | None = None, puntajes=True, no_carga=False):
        self.no_carga = no_carga  # la carga de prueba falla: sin estrategias ni axe
        self.liberar = liberar
        self.puntajes = puntajes
        self.llamadas = []

    def __call__(self, url, letra, tramite, carpeta, hosts, al_evento=None, detener=None, **opciones):
        self.llamadas.append({"url": url, "letra": letra, "tramite": tramite, "opciones": opciones})
        validar_entrada(url, hosts)
        if self.no_carga:
            no_cargo = {"tipo": "timeout", "motivo": motivo_no_cargo("timeout", 60_000),
                        "detalle": "TimeoutError: Page.goto: Timeout 60000ms exceeded."}
            return Exploracion(url, Tarea(letra, url, tramite), "2026-11-14T12:00:00-07:00", 2, 0,
                               _sin_cargar(Tarea(letra, url, tramite), url, no_cargo), None,
                               "la página no cargó", (), 60.4, (), no_cargo)
        r = resultado(letra, tramite)
        for n, intento in enumerate(r.intentos, 1):
            al_evento("estrategia", {"indice": n, "total": len(r.intentos), "estrategia": intento.estrategia})
            for paso in intento.trayectoria:
                al_evento("paso", {"estrategia": intento.estrategia, "tecla": paso.tecla, "anuncio": paso.anuncio,
                                   "pulsaciones": paso.pulsaciones, "url": paso.url, "profundidad": 0,
                                   "se_movio": True, "landmark": None, "documento": None, "no_evaluable": None})
                if self.liberar is not None and n == 2:
                    self.liberar.wait(30)
                if detener is not None and detener.is_set():
                    raise Detenida()
        al_evento("fase", {"fase": "axe"})
        puntajes = ({"reglas": 0.875, "elementos": 0.945, "reglas_conservador": 0.833,
                     "elementos_conservador": 0.83} if self.puntajes else None)
        return Exploracion(url, r.tarea, "2026-11-14T12:00:00-07:00", 2, 0, r, puntajes,
                           None if self.puntajes else "no medido en la prueba", (),
                           75.4, (4.2, 61.0, 1.1))
