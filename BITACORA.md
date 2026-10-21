# Bitácora — Atorapp (FEMECI Sinaloa 2026)

Proyecto individual de Javier Sandoval Dávila · Asesor: Dr. Alonso Amado Garfias · Área: Sistemas Informáticos (Anexo 2)

> **Nota de método:** las entradas de septiembre al 17 de octubre de 2026 se **reconstruyeron el 17-oct-2026** a partir del historial de commits de este repositorio (fecha y hora exactas) y de las notas de trabajo del proyecto. Donde la fecha exacta no está documentada, se indica. A partir del 17-oct la bitácora se lleva al día, una entrada por sesión de trabajo.

Formato de cada entrada: **Qué hice · Resultado / hallazgo · Problemas y decisiones · Siguiente paso**.

---

## Septiembre 2026 (fecha exacta por confirmar) — Elección del proyecto

- **Qué hice:** búsqueda de ideas sobre tecnología para personas con discapacidad. Se descartaron una app de Lengua de Señas Mexicana y un control de dispositivos por voz/gestos por estar ya muy cubiertos en el mercado y la investigación. Se eligió un auditor de accesibilidad web aplicado a sitios institucionales de Sinaloa.
- **Resultado:** propuesta presentada al Dr. Alonso; se le pidió por correo ser asesor.
- **Problemas y decisiones:** el proyecto empezó en equipo; por recomendación del asesor se continuó de forma individual.
- **Siguiente:** definir el enfoque y revisar sitios reales.

## 20-sep-2026 — Enfoque central y sondeo preliminar

- **Qué hice:** definí el enfoque: medir si una persona con lector de pantalla **puede completar una tarea real**, no contar violaciones WCAG sueltas. Propuse 4 tareas (contacto, requisitos de un trámite, documento descargable, formulario sin enviar). Revisé marco legal (Acuerdo SFP 2015, LGIPD arts. 3 y 32), datos de INEGI (Censo 2020) y la encuesta WebAIM #10 (71.6 % navega por encabezados). Sondeo preliminar de 6 sitios.
- **Resultado:** hay variación entre sitios (Ahome y Atención Ciudadana con buena estructura; otros sin jerarquía de encabezados). Ninguno tiene declaración de accesibilidad.
- **Problemas y decisiones:** el sondeo se hizo con una herramienta que convierte páginas a texto; **no es medición** y no se cita como resultado. El Acuerdo SFP solo obliga a la federación; para estados y municipios aplica la LGIPD, sin estándar técnico medible.
- **Siguiente:** piloto con axe-core sobre páginas renderizadas.

## 29-sep-2026 — Piloto con 3 portadas

- **Qué hice:** guardé las portadas de culiacan.gob.mx, sinaloa.gob.mx y retys.sinaloa.gob.mx y las analicé con axe-core 4.13 y su árbol de accesibilidad.
- **Resultado:** primer contraejemplo: sinaloa.gob.mx con puntaje automático alto y sin teléfono, correo ni enlace de contacto en la portada (verificado en el HTML). El puntaje por reglas oculta magnitud (Culiacán: muchos enlaces sin nombre y solo pierde una regla).
- **Problemas y decisiones:** el sondeo del 20-sep se equivocó con Culiacán (sí tiene encabezados en el árbol real). Las páginas guardadas no cargan CSS → contraste no confiable. Decisión: reportar puntaje por reglas **y** por elementos; las tareas cruzan páginas, la captura debe seguir la ruta.
- **Siguiente:** construir la captura en vivo.

## 30-sep-2026 — Arquitectura v2 y Fase 1 (código)

- **Qué hice:** decidí la arquitectura: captura en vivo → axe-core → emulador de lector de pantalla → agente de IA por decisiones → validación. Estimé costos de la API (~1 centavo por tarea con Haiku 4.5).
  Commits: Fase 0 (22:53), Fase 1A captura con Playwright: HTML, árbol de accesibilidad y metadatos (23:00); capturas por fecha y hora (23:04); Fase 1B páginas de prueba con respuestas esperadas (23:21); regla de fricción por pulsaciones con la mejor estrategia (23:38); cierre de Fase 1 (23:44).
- **Resultado:** captura en vivo de Culiacán a 1366×768: 726 nodos, 28 encabezados con jerarquía rota (sin h2), 49 enlaces (9 sin nombre), teléfono como texto plano en el pie, submenús colapsados.
- **Problemas y decisiones:** los números del piloto de Culiacán estaban contaminados (sin CSS el menú móvil duplicaba enlaces: 12 vs 9 reales) → no se reportan, se re-miden en vivo. El agente recibe solo nombres y roles, nunca HTML. Descarté el agente "tecla por tecla" por costo.
- **Siguiente:** Fase 2, axe-core en vivo.

## 05-oct-2026 — Fase 2: axe-core en vivo sobre 5 portadas

- **Qué hice:** integré axe-core 4.14 en la captura y el módulo de puntajes (commit 7b954fb, 12:29). Medí 5 portadas en vivo y las páginas de prueba.
- **Resultado:** puntajes por reglas entre 76 % y 89.7 %, por elementos entre 76 % y 97.6 %. Hallazgo: en la página de prueba sin encabezados, axe reporta la regla `bypass` como **incompleta** (no la cuenta en su puntaje) aunque fallan sus tres chequeos.
- **Problemas y decisiones:** 4 de 5 portadas tienen iframes que el árbol no cubre (NVDA sí los lee) → límite declarado.
- **Siguiente:** puntaje conservador y piloto con recorrido manual.

## 08-oct-2026 — Puntaje conservador, formatos y antecedentes

- **Qué hice:** agregué el puntaje conservador (incompletas como fallas), commit ab81c20 (08:46). Revisé los formatos oficiales de registro y la rúbrica. Investigué antecedentes 2021-2026 (Latte, AXNav, TaskAudit, A11yNavigator) y patentes (Bank of America, SAP).
- **Resultado:** aun con el puntaje pesimista, la página sin encabezados conserva 92.3 %. A11yNavigator (ASE 2025) es el antecedente más cercano en web; ninguno evalúa Sinaloa ni da veredicto por tarea cívica.
- **Problemas y decisiones:** el Dr. Aldo Uriarte confirmó que no se requiere carta de postulación y que la ficha técnica es opcional. La rúbrica califica resultados y conclusiones aunque la plantilla no los trae → se agregan como secciones.
- **Siguiente:** registro en la plataforma.

## 17-oct-2026 — Nombre, registro y revisión crítica externa

- **Qué hice:**
  - Confirmé con el Dr. Alonso (vía TI) que el Tec no ofrece acceso por API a modelos de IA → la API la pago yo, con tope de $20 USD.
  - Elegí el nombre **Atorapp**.
  - Llené el CUVI y el registro en la plataforma CONFÍE (folio SIN-FEMECI-2026-C01-00137, guardado sin enviar).
  - Pedí dos revisiones críticas externas a otra IA.
- **Resultado:** veredicto de la revisión: candidato creíble a medalla; el primer lugar depende de la evidencia.
- **Problemas y decisiones:**
  - Atorapp **estima** (no "determina") y se valida contra auditoría manual con NVDA, hecha antes y a ciegas.
  - Se llama "emulador simplificado" y se declaran sus límites.
  - El contraejemplo de sinaloa.gob.mx es de arquitectura de información, no una barrera específica del lector → se agrega el control "¿lo encuentra un usuario vidente?".
  - Nuevo estado "No evaluable".
  - El análisis principal es la matriz de confusión, con AUC para axe.
  - Regla del 1-nov con conjunto balanceado.
  - Se agrega un experimento antes/después que cambia solo el defecto.
  - Alcance: piso de 10 sitios con tareas A y B.
  - Registro extendido al 23-oct; por indicación del Dr. Alonso y la Dra. Kim, primero se envía lo que pueda llenar solo.
- **Siguiente:** escribir el Anexo 2, actualizar los textos registrados y empezar la auditoría manual con NVDA.

---

<!-- Plantilla para nuevas entradas:

## DD-mmm-2026 — Título

- **Qué hice:**
- **Resultado:**
- **Problemas y decisiones:**
- **Siguiente:**
-->
