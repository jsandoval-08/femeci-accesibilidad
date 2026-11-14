# Reporte de Atorapp: sin_contacto

Esta es una estimación de Atorapp sobre lo que un lector de pantalla anunciaría; la referencia es la auditoría manual con NVDA. El puntaje de conformidad automática mide solo lo que axe-core revisa, sobre la página fijada de antemano para cada tarea.

Fecha: 2026-11-13T22:41:56-07:00 · Umbral: 15 pulsaciones · Palabras clave: versión 2

## Resumen

| Tarea | Estado | Falla | Estrategia | Fricción | Trayectoria |
|---|---|---|---|---|---|
| A | no_completable | no_encontrado | no_dirigida | 42 consumidas | leer×42 |
| B | completable | — | H_a_seccion | 9 | H×3, leer×6 |
| C | completable | — | enlace_por_nombre | 5 | lista_enlaces×1, flecha_lista×3, Enter×1 |
| D | completable | — | F_a_campos | 3 | F×3 |

## Llegó primero a otra cosa

Estrategias que creyeron llegar, pero no al objetivo correcto. No cambian el estado; en un sitio real eso también le puede pasar a una persona.

Ninguna.

## Detalle por tarea

### Tarea A

- Entrada: sin_contacto.html
- Objetivo correcto: NO_EXISTE
- Motivo: ninguna estrategia encontró el objetivo
- Con otros umbrales: 10: no_completable, 15: no_completable, 25: no_completable
- Veredicto NVDA: no medido · ¿Lo encuentra un usuario vidente?: no medido
- Puntajes de axe en sin_contacto.html: reglas: 100.0 % · elementos: 100.0 % · reglas conservador: 100.0 % · elementos conservador: 100.0 %

### Tarea B

- Entrada: sin_contacto.html · Trámite: Licencia de construcción
- Objetivo correcto: Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno
- Motivo: se llegó al objetivo correcto
- Con otros umbrales: 10: completable, 15: completable, 25: completable
- Veredicto NVDA: no medido · ¿Lo encuentra un usuario vidente?: no medido
- Puntajes de axe en sin_contacto.html: reglas: 100.0 % · elementos: 100.0 % · reglas conservador: 100.0 % · elementos conservador: 100.0 %

### Tarea C

- Entrada: sin_contacto.html
- Objetivo correcto: docs/plan_municipal.pdf
- Motivo: se llegó al objetivo correcto
- Con otros umbrales: 10: completable, 15: completable, 25: completable
- Veredicto NVDA: no medido · ¿Lo encuentra un usuario vidente?: no medido
- Puntajes de axe en sin_contacto.html: reglas: 100.0 % · elementos: 100.0 % · reglas conservador: 100.0 % · elementos conservador: 100.0 %

### Tarea D

- Entrada: sin_contacto.html
- Objetivo correcto: Nombre completo|Trámite|Fecha preferida
- Motivo: se llegó al objetivo correcto
- Con otros umbrales: 10: completable, 15: completable, 25: completable
- Veredicto NVDA: no medido · ¿Lo encuentra un usuario vidente?: no medido
- Puntajes de axe en sin_contacto.html: reglas: 100.0 % · elementos: 100.0 % · reglas conservador: 100.0 % · elementos conservador: 100.0 %
