# Análisis conjunto: Atorapp contra la auditoría NVDA

Atorapp es una estimación; la referencia es la auditoría manual con NVDA, hecha a ciegas y antes de correr Atorapp. Las tareas de un mismo sitio no son independientes: no hay p-valores ni intervalos.

Tareas: 3 · sitios: 3

## Por tarea

| Sitio | Tarea | NVDA | Atorapp | Falla | Fricción | Mejor estrategia | Falsas llegadas | Atorapp con 10 / 15 / 25 | axe reglas | axe elementos | reglas cons. | elementos cons. | NVDA pulsaciones aprox. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ahome | A | con_dificultad | no_evaluable | — | 0 consumidas | H_a_seccion | 0 | no_evaluable / no_evaluable / no_evaluable | no medido | no medido | no medido | no medido | 35 |
| ciudadano | B | con_dificultad | no_completable | no_encontrado | 73 consumidas | no_dirigida | 0 | no_completable / no_completable / no_completable | 73.7 % | 72.3 % | 73.7 % | 71.0 % | 20 |
| sinaloa | A | no_completable | no_completable | no_encontrado | 123 consumidas | no_dirigida | 0 | no_completable / no_completable / no_completable | 87.5 % | 94.5 % | 83.3 % | 83.0 % | no medido |

## Matriz NVDA (filas) contra Atorapp (columnas)

| NVDA \ Atorapp | completable | con_dificultad | no_completable |
|---|---|---|---|
| completable | 0 | 0 | 0 |
| con_dificultad | 0 | 0 | 1 |
| no_completable | 0 | 0 | 1 |

Comparables: 2. Excluidas: sin NVDA 0, no evaluable en NVDA 0, no evaluable en Atorapp 1.

## Acuerdo observado

- 3 clases: 1 de 2
- Binario (se logró / no_completable): 1 de 2

## Sensibilidad al umbral (acuerdo de 3 clases)

- Umbral 10: 1 de 2
- Umbral 15: 1 de 2
- Umbral 25: 1 de 2

## Falsas llegadas

Tareas con al menos una: 0 de 3.

## AUC de los puntajes de axe

No se calcula: hay 2 tareas comparables (de 3 tareas en 3 sitios); con menos de 10 el AUC no es interpretable: solo puede tomar unos cuantos valores (con 1 tarea de cada clase, 0 o 1) y no dice nada de axe.

## Notas del auditor (no las lee Atorapp)

- **ahome A** (2026-11-08): ruta: Primer intento ~30 pulsaciones, ruta directa ~35 (H, D, K y Enter hasta Contacto). Conteo manual aproximado; auditor principiante. · dónde se atoró: Se encuentra el contacto, pero cuesta mas de 15 pulsaciones.
- **sinaloa A** (2026-11-08): ruta: H, D y K en la portada (5 a 10 min). Conteo manual aproximado; auditor principiante. · dónde se atoró: En la portada solo hay redes sociales y enlaces a otros portales (no abiertos). Sin telefono ni correo del portal. Se mide por host exacto.
- **ciudadano B** (2026-11-08): ruta: Flechas cuadro por cuadro hasta Acta de nacimiento, Enter, flechas hasta Requisitos. Conteo manual aproximado; auditor principiante. · dónde se atoró: Los tramites se leen como texto uno por uno con flechas; se activan con Enter. Llegar a los requisitos cuesta ~20 pulsaciones. Los requisitos se muestran sin cambiar la URL (posible ventana emergente o app de una sola pagina).
