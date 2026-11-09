# Reporte de Atorapp: ahome

Esta es una estimación de Atorapp sobre lo que un lector de pantalla anunciaría; la referencia es la auditoría manual con NVDA. El puntaje de conformidad automática mide solo lo que axe-core revisa, sobre la página fijada de antemano para cada tarea.

Fecha: 2026-11-08T20:22:10-07:00 · Umbral: 15 pulsaciones · Palabras clave: versión 2

## Resumen

| Tarea | Estado | Falla | Estrategia | Fricción | Trayectoria |
|---|---|---|---|---|---|
| A | no_evaluable | — | H_a_seccion | 0 consumidas | entrada×1 |

## Llegó primero a otra cosa

Estrategias que creyeron llegar, pero no al objetivo correcto. No cambian el estado; en un sitio real eso también le puede pasar a una persona.

Ninguna.

## Detalle por tarea

### Tarea A

- Entrada: https://www.ahome.gob.mx/
- Objetivo correcto: contacto@ahome.gob.mx|(668) 816-4000
- Motivo: no resuelta dentro del presupuesto: timeout
- Con otros umbrales: 10: no_evaluable, 15: no_evaluable, 25: no_evaluable
- Veredicto NVDA: con_dificultad · ¿Lo encuentra un usuario vidente?: sí
- Puntajes de axe en https://www.ahome.gob.mx/: no medido (TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://www.ahome.gob.mx/", waiting until "load"
)
