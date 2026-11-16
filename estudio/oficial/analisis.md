# Análisis conjunto: Atorapp contra la auditoría NVDA

Resultados oficiales según la regla del 13-nov (BITACORA.md); la corrida del 8-nov sigue intacta en estudio/resultados/.

Atorapp es una estimación; la referencia es la auditoría manual con NVDA, hecha a ciegas y antes de correr Atorapp. Las tareas de un mismo sitio no son independientes: no hay p-valores ni intervalos.

Tareas: 6 · sitios: 5

## Por tarea

| Sitio | Tarea | NVDA | Atorapp | Falla | Fricción | Mejor estrategia | Falsas llegadas | Atorapp con 10 / 15 / 25 | axe reglas | axe elementos | reglas cons. | elementos cons. | NVDA pulsaciones aprox. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ahome | A | con_dificultad | no_evaluable | — | 0 consumidas | H_a_seccion | 0 | no_evaluable / no_evaluable / no_evaluable | no medido | no medido | no medido | no medido | 35 |
| atencion | A | no_completable | no_completable | no_encontrado | 105 consumidas | no_dirigida | 0 | no_completable / no_completable / no_completable | 95.7 % | 97.5 % | 95.7 % | 97.5 % | 11 |
| ciudadano | A | con_dificultad | completable | — | 13 | Tab_inicio | 0 | con_dificultad / completable / completable | 73.7 % | 72.3 % | 73.7 % | 71.0 % | 17 |
| ciudadano | B | con_dificultad | no_completable | no_encontrado | 73 consumidas | no_dirigida | 0 | no_completable / no_completable / no_completable | 73.7 % | 72.3 % | 73.7 % | 71.0 % | 20 |
| culiacan | A | completable | con_dificultad | — | 41 | Tab_inicio | 0 | con_dificultad / con_dificultad / con_dificultad | 89.7 % | 95.0 % | 83.3 % | 94.3 % | 5 |
| sinaloa | A | no_completable | no_completable | no_encontrado | 123 consumidas | no_dirigida | 0 | no_completable / no_completable / no_completable | 87.5 % | 94.5 % | 83.3 % | 83.0 % | no medido |

## Matriz NVDA (filas) contra Atorapp (columnas)

| NVDA \ Atorapp | completable | con_dificultad | no_completable |
|---|---|---|---|
| completable | 0 | 1 | 0 |
| con_dificultad | 1 | 0 | 1 |
| no_completable | 0 | 0 | 2 |

Comparables: 5. Excluidas: sin NVDA 0, no evaluable en NVDA 0, no evaluable en Atorapp 1.

## Acuerdo observado

- 3 clases: 2 de 5
- Binario (se logró / no_completable): 4 de 5

## Sensibilidad al umbral (acuerdo de 3 clases)

- Umbral 10: 3 de 5
- Umbral 15: 2 de 5
- Umbral 25: 2 de 5

## Referencia corregida después de la corrida

Estas referencias NVDA se corrigieron DESPUÉS de ver el resultado de Atorapp, al aplicar una regla que ya existía (ver BITACORA.md). Atorapp no se volvió a correr. Las secciones de arriba usan la referencia vigente; aquí, el acuerdo con la referencia original.

- atencion A: completable → no_completable

Acuerdo con la referencia original:

- 3 clases: 1 de 5
- Binario (se logró / no_completable): 3 de 5
- Umbral 10 (3 clases): 2 de 5
- Umbral 15 (3 clases): 1 de 5
- Umbral 25 (3 clases): 1 de 5

## Falsas llegadas

Tareas con al menos una: 0 de 6.

## AUC de los puntajes de axe

No se calcula: hay 5 tareas comparables (de 6 tareas en 5 sitios); con menos de 10 el AUC no es interpretable: solo puede tomar unos cuantos valores (con 1 tarea de cada clase, 0 o 1) y no dice nada de axe.

## Notas del auditor (no las lee Atorapp)

- **ahome A** (2026-11-08): ruta: Primer intento ~30 pulsaciones, ruta directa ~35 (H, D, K y Enter hasta Contacto). Conteo manual aproximado; auditor principiante. · dónde se atoró: Se encuentra el contacto, pero cuesta mas de 15 pulsaciones.
- **sinaloa A** (2026-11-08): ruta: H, D y K en la portada (5 a 10 min). Conteo manual aproximado; auditor principiante. · dónde se atoró: En la portada solo hay redes sociales y enlaces a otros portales (no abiertos). Sin telefono ni correo del portal. Se mide por host exacto.
- **ciudadano A** (2026-11-15): ruta: H (no hay encabezados), luego K hasta el pie: ~17. Con Tab también ~17 (3 enlaces del pie salen primero + 14 hasta el correo). D no avanza: el sitio no tiene regiones. Conteo manual aproximado; auditor principiante. · dónde se atoró: Contacto en el pie y en el bloque de Asistencia Digital. Sin landmarks (D inútil). Orden de Tab raro: empieza por el pie (posible tabindex>0, sin confirmar). Las tarjetas de trámites no reciben foco con Tab. Un campo y un botón sin nombre antes de VALIDAR UN DOCUMENTO. La ruta con Tab se hizo ya sabiendo dónde estaba.
- **ciudadano B** (2026-11-08): ruta: Flechas cuadro por cuadro hasta Acta de nacimiento, Enter, flechas hasta Requisitos. Conteo manual aproximado; auditor principiante. · dónde se atoró: Los tramites se leen como texto uno por uno con flechas; se activan con Enter. Llegar a los requisitos cuesta ~20 pulsaciones. Los requisitos se muestran sin cambiar la URL (posible ventana emergente o app de una sola pagina).
- **culiacan A** (2026-11-15): ruta: Mejor ruta: 4 D hasta la región 'información de contenido' + 1 al correo = ~5. Primer intento (H, K, L y Tab) ~45 sin reconocer el contacto; con solo flecha abajo ~120 hasta el teléfono. Conteo manual aproximado; auditor principiante. · dónde se atoró: Correo como mailto: y teléfono como texto plano en el pie. Ningún encabezado de contacto: H no ayuda. NVDA parte 'Teléfono' y el número en dos líneas. La pasada con D se hizo ya sabiendo dónde estaba.
- **atencion A** (2026-11-15): ruta: Única ruta: ~4 D al pie + 3-4 K al enlace 'Whatsapp' + Enter + Esc (diálogo del navegador) + 1-2 H al encabezado 'Chatea en WhatsApp con el +52 667 502 7665' = ~11. El número se lee en api.whatsapp.com (otro host). Portada y Asistencia digital revisadas con H, K, L, D, Tab y flechas: no se lee ningún contacto. Conteo manual aproximado; auditor principiante. CORRECCIÓN 15-nov: la única ruta sale del host (api.whatsapp.com); por la regla de host exacto del 8-nov no cuenta, así que el veredicto pasa de completable a no_completable. · dónde se atoró: En Asistencia digital un vidente ve teléfono, WhatsApp y correo, pero NVDA no lee las tarjetas (texto no accesible, probablemente imágenes). Tiene widget de accesibilidad y aun así falla. El enlace 'Whatsapp' no avisa que sale del sitio ni que abre un diálogo de Chrome que se queda con el foco. 20 botones del mapa llamados 'Marker'; lista de municipios 'cliqueable' sin rol ni foco. Dentro del host el contacto existe (un vidente lo ve en /asistencia-digital/), pero NVDA no lo lee; solo se alcanza saliendo a api.whatsapp.com.
