# Resultados: antes/después de atención ciudadana A (reproducciones experimentales)

Corrida única por versión, 16-nov-2026: original a las 03:54, corregida a las 03:55 (`scripts/antes_despues.py medir`).
Sin red: 0 peticiones bloqueadas, porque ni axe ni ninguna estrategia intentó salir de 127.0.0.1.
Sin cambios en umbrales (15), topes (508 / 30), palabras clave (v2), estrategias ni métrica.

- **Entrada:** la página `/asistencia-digital/`, no la tarea desde la portada. **No se compara con las 105** de la
  corrida oficial.
- **Objetivo:** `asistencia@sinaloa.gob.mx | (667) 7587123 | (667) 5027665`; basta uno.
- **Prerregistro:** `BITACORA.md`, 16-nov, con su enmienda de las 03:53.

## Tabla final

| | Original | Corregida |
|---|---|---|
| Paradas | 32 | 36 (+4 imágenes con nombre) |
| axe: reglas | 91.3 % (21 / 23) | 91.3 % (21 / 23) |
| axe: elementos | 94.8 % (164 / 173) | 94.9 % (168 / 177) |
| axe: reglas conservador | 87.5 % | 87.5 % |
| axe: elementos conservador | 94.3 % | 94.4 % |
| axe: violaciones | color-contrast (5), link-name (4) | color-contrast (5), link-name (4) |
| **Atorapp: estado** | **no_completable** (no_encontrado) | **completable** |
| Atorapp: fricción | — (32 consumidas) | **7** (D_a_main) |
| Con umbral 10 / 15 / 25 | no_completable en los tres | completable en los tres |
| Falsas llegadas | 0 | 0 |
| **NVDA** (auditoría no a ciegas, 16-nov) | **no_completable** (no_encontrado) | **completable**, 3 pulsaciones (H×1, flecha×2) |

**Puntajes de axe.**
- **Por qué los elementos suben 0.1 puntos:** las 4 imágenes ahora tienen nombre y `image-alt` las cuenta como nodos
  que pasan (164 → 168). Antes, con `alt=""`, la regla ya pasaba, así que no cambia ninguna regla.
- **Por qué no son los del sitio en vivo** (95.7 / 97.5 % el 15-nov): las 5 violaciones de `color-contrast` vienen de
  que falta el CSS del sitio. Solo vale comparar original local contra corregida local.

## Atorapp por estrategia

| Estrategia | Original: ¿llegó? | Pulsaciones | Dónde se detuvo | Corregida: ¿llegó? | Pulsaciones | Dónde se detuvo |
|---|---|---|---|---|---|---|
| H_a_seccion | no | 4 | «no hay más encabezados» | no | 4 | «no hay más encabezados» |
| D_a_seccion | no | 7 | «no hay más puntos de referencia» | no | 7 | «no hay más puntos de referencia» |
| **D_a_main** | no | 16 | fin del documento («desktop») | **sí (correcto)** | **7** | «gráfico, Línea telefónica Atención ciudadana (667) 7587123», **la mejor** |
| enlace_por_nombre | no | 14 | lista de enlaces hasta «Whatsapp», ninguno con palabra de contacto | no | 14 | igual |
| no_dirigida | no | 32 | fin del documento («desktop») | sí (correcto) | 23 | la misma imagen |
| Tab_inicio | no | 25 | «fin de los elementos enfocables» | no | 25 | igual (las imágenes no reciben foco) |
| probar_enlaces (H) | no | 4 | «no hay más encabezados» | no | 4 | igual |
| probar_enlaces (inicio) | no | 15 | «no hay más enlaces» | no | 15 | igual |

**Ruta ganadora en la corregida (7):**
1. D: navegación «Accessibility Toolbar»
2. D: banner
3. D: navegación «Navegación del sitio principal»
4. D: región «Header Widget 1»
5. D: principal
6. leer: «En Asistencia Digital te brindamos atención…»
7. leer: «gráfico, Línea telefónica Atención ciudadana (667) 7587123»

En los pasos 4 y 5 el cursor está en la misma parada: la región no tiene paradas propias, así que se anota en la
siguiente (regla de 3B).

**Validación cruzada:** la tabla de la original coincide exactamente con la reproducción sin red de la captura del
15-nov (entrada del 15-nov en la bitácora: H 4, D_a_seccion 7, D_a_main 16, enlaces 14, no_dirigida 32, Tab 25,
probar 4 y 15).

## Contra lo prerregistrado

| Instrumento | Predicción | Resultado |
|---|---|---|
| axe | igual o casi igual | **se cumple**: reglas iguales; elementos +0.1 puntos |
| Atorapp | no_completable → completable o con_dificultad | **se cumple**: no_completable → completable (7) |
| NVDA | igual que Atorapp | **se cumple**: no_completable → completable (`nvda.csv`) |

**La predicción se cumple en las tres herramientas:** axe igual (91.3 % por reglas), y Atorapp y NVDA pasan de
no_completable a completable.

## NVDA (Javier, 16-nov, copia local en Chrome; no a ciegas)

- **Original:** D por todas las regiones sin hallar contacto en la página. Las 4 tarjetas sin enlace no se oyen; Facebook y
  chat se oyen como enlace con su URL («asistenciadigital», «ciudadano.sinaloa.gob.mx»). La única ruta al número fue
  K×3–4 + Enter en «Whatsapp» del pie, que sale a wa.me; Esc cierra el diálogo del navegador y NVDA lee el número en la
  página de WhatsApp (otro host). Con la regla de host exacto no cuenta: no_completable, no_encontrado. Pulsaciones en
  blanco porque no llegó.
- **Corregida:** H×1 y flecha×2 hasta «gráfico, Línea telefónica Atención ciudadana (667) 7587123»: completable, 3.

**Coinciden en el estado, no en la magnitud: Atorapp 7, NVDA 3.** Ambos son completable con cualquier umbral (10, 15 y
25). La diferencia viene de la ruta:
- NVDA hizo H al encabezado «ASISTENCIA DIGITAL» y siguió con flecha.
- Las estrategias de Atorapp solo se detienen en un encabezado si su nombre trae una palabra clave de contacto. Ese
  encabezado no la trae, así que H_a_seccion termina con «no hay más encabezados» (4 pulsaciones) y la mejor es D_a_main (7).
- Es la misma familia de diferencia que en culiacán A y navolato A (palabras clave contra significado). No se agrega ninguna
  estrategia: sería ajustar a la referencia después de verla.

## Límites

- Mide la página, no la tarea desde la portada.
- Las 2 tarjetas del pie (`alt=""`) no se corrigen.
- Hay CSS reconstruido (`desktop`) que no viene del sitio.
- La auditoría NVDA no es a ciegas: el auditor conoce el sitio y dónde están las tarjetas.
- NVDA se audita en Chrome sobre la copia local, sin estilos (la CSP bloquea el CSS del sitio).
- Una sola corrida por versión y por herramienta.
- La corrección y la predicción las escribió el mismo equipo que hizo Atorapp. El caso ilustra el mecanismo («axe no lo
  ve, Atorapp sí»); no mide cuántas veces pasa.
