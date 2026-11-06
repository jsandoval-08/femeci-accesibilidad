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

## 20-oct-2026 — Fase 3A: emulador núcleo

- **Qué hice:**
  - Escribí `src/emulador.py`: aplana el árbol CDP en paradas; cursor; teclas H, K, D, F, Tab, flecha y leer de corrido; lista de elementos; anuncio (rol + nombre); trayectoria reproducible.
  - Agregué la página de casos límite `tests/paginas/casos_emulador.html` y `tests/test_emulador.py`.
  - Los valores esperados se escribieron **a mano, antes de implementar**, y se guardaron en un commit propio (5d060ae). Cada uno cita su fuente: yaml o HTML.
- **Resultado:**
  - Las **17 rutas de una sola página** de los `.esperado.yaml` dan **exactamente** su `friccion_esperada`.
  - Las 7 rutas que cruzan páginas o abren el PDF quedan en skip, porque son de 3B.
  - Las secuencias H, K, D, F y Tab y los conteos de paradas de las 6 páginas coinciden con lo escrito a mano.
  - Suite completa: 93 pasan, 7 skip, 1 xfail.
- **Problemas y decisiones:**
  - D1: si no hay siguiente, el cursor no se mueve, no da la vuelta y la pulsación cuenta 1.
  - D2: F incluye botones (por verificar en NVDA).
  - D3: 1 StaticText = 1 parada, declarado como limitación.
  - D4: las imágenes son parada con o sin alt; las de `alt=""` quedan fuera.
  - Comprobado: el árbol marca enfocable lo que tiene `tabindex="-1"` → limitación declarada de Tab.
  - **Discrepancia:** Chromium ignora el `<label>` de una casilla (`labelFor`), así que su rótulo no sale como parada. Mi valor esperado sí lo contaba. Quedó en xfail estricto hasta decidir; **decidido (a):** se sigue el árbol, se corrigió el valor esperado y se quitó el xfail. Queda por verificar en NVDA que casilla + rótulo se lean como una sola línea.
  - Medí en las 5 portadas (capturas del 5-oct) los roles fuera de la lista de paradas, con `scripts/medicion/roles_fuera.py` y `detalle.py`:
    - 0 `menuitem`, `switch`, `treeitem` y `option` suelto;
    - 4 `tab` en Culiacán, que hoy quedan como texto suelto;
    - 1 landmark vacío en Atención Ciudadana.
  - Con eso se decidió, para 3B:
    - roles interactivos no-enlace como parada propia (K no se detiene);
    - Tab en `tab` solo si está seleccionada;
    - landmark vacío anotado en la siguiente parada.
- **Siguiente:**
  - Fase 3B: navegación en vivo (Enter, recaptura, profundidad, No evaluable).
  - Verificar en NVDA los puntos marcados en CLAUDE.md durante la auditoría manual.

## 20-oct-2026 — Fase 3B: navegación en vivo

- **Qué hice:**
  - Plan primero, aprobado con 5 decisiones. Después: valores esperados a mano en su propio commit (e90106d), código en 6 pasos chicos y un commit de medición.
  - Páginas nuevas (solo locales, servidas por http desde un servidor de pruebas en puerto libre):
    - `casos_navegacion`: submenú colapsado con `menuitem`, pestañas, `switch`, `treeitem`, "Saltar al contenido" y landmarks vacíos;
    - `destino_menu`;
    - `cadena_0..4` para la profundidad;
    - `fallas` y `captcha`.
  - `src/navegador.py`:
    - una pestaña nueva por nivel; volver = cerrar la pestaña y reusar el árbol guardado;
    - clic en la misma página para expandir y para las pestañas;
    - destino de `#id`;
    - descarga de PDF y capa de texto con pypdf;
    - CAPTCHA heurístico.
  - En el emulador: Enter, volver, tope de pulsaciones, No evaluable, `elegir_de_lista`, roles interactivos no-enlace y landmark vacío.
  - Medición sobre las capturas del 5-oct (`scripts/medicion/enlaces_href.py`), antes de fijar la pestaña por nivel.
- **Resultado:**
  - Las **24 rutas** de los `.esperado.yaml` dan **exactamente** su `friccion_esperada`, con 0 skip.
    - Las 6 tareas C activan el PDF correcto. La capa de texto falta solo en `pdf_escaneado`.
    - La B de enlaces_ambiguos da 35 en vivo: probando enlaces, volver regresa al enlace activado.
  - "Saltar al contenido" cuesta 1 y deja el cursor en el contenido.
  - Todas las paradas escritas a mano para `casos_navegacion`, antes y después de expandir, coincidieron con el árbol real. También las predicciones de enfocable en los `menuitem`.
  - Suite completa: 127 pasan, 0 skip.
- **Problemas y decisiones:**
  - Comprobado en Chromium:
    - un PDF en headless se descarga ("Download is starting"), no abre visor;
    - los id del DOM no cambian tras un clic;
    - `<a role="menuitem" href>` no trae `url` en el árbol, así que se lee el href del DOM;
    - `role="option"` suelto no se expone.
  - Pestaña por nivel en vez de clic + `go_back`: así volver no recarga y los id siguen sirviendo.
    - Medido antes de decidir: de 164 enlaces de las 5 portadas, 150 tienen URL navegable, 6 son `#id`, 7 `#` solo, 0 `javascript:` y 1 `mailto:`.
    - Los 22 `<a>` sin href están dentro de botones con `aria-expanded`, es decir, acordeones.
    - Error mío en la primera versión de la medición: mezclaba `href="#"` con enlaces a la misma página. Corregido.
  - Profundidad: entrada = nivel 0; por eso son 5 páginas de cadena. La profundidad es el tamaño de la pila; toda pulsación ejecutada cuenta.
  - CAPTCHA: se registra y no detiene. Regla fijada en 3D antes de ver datos: "no resuelta + CAPTCHA en la ruta → No evaluable".
  - `mailto:`/`tel:` no se ejecutan. En 3D, llegar a ese enlace cuenta como identificar el contacto en la tarea A.
  - El enlace a la misma página sin `#` es navegación. En 3C, las estrategias no re-entran a la URL actual.
  - Tope de pulsaciones sin valor por omisión: se fija con criterio escrito antes del estudio.
  - Bug de las pruebas corregido: el hilo del servidor que atendía `/lento/` hacía abortar a Python al cerrar ("Fatal Python error"). Ahora usa hilos no daemon.
  - Limitaciones nuevas declaradas en CLAUDE.md (3B). Nuevos puntos por verificar en NVDA:
    - si la lista de elementos abre en el primero o en el más cercano al cursor;
    - si F se detiene en `switch`;
    - qué anuncia en un enlace `mailto:`.
- **Siguiente:**
  - Fase 3C: estrategias programadas, palabras clave por tarea, mejor estrategia y fricción.
  - Seguir la auditoría manual con NVDA a ciegas.

## 05-nov-2026 — Fase 3C: estrategias programadas

- **Qué hice:**
  - Plan primero, aprobado con 4 decisiones. Después: valores esperados a mano en su propio commit (603f422) y código en pasos chicos.
  - `src/estrategias.py`: H y D a la sección, lista de enlaces por nombre, F a campos, leer desde el inicio, Tab desde el inicio y probar enlaces ambiguos. También criterios de "creo que llegué", mejor estrategia y resultado por tarea con trayectoria.
  - `config/palabras_clave.yaml`: **versión 1, congelada**. Cualquier cambio posterior va en esta bitácora con su razón.
  - Páginas `tests/paginas/ce_*`, con href opacos y una trampa con palabras clave solo en la URL.
  - Decisiones aplicadas en CLAUDE.md: el agente de IA no se construye (queda como Proyección), sin conjunto reservado, auditoría con NVDA pospuesta y solo páginas de prueba locales.
- **Resultado:**
  - En las **24 tareas** de los `.esperado.yaml`, la mejor estrategia coincide con su `estrategia` y su `friccion_esperada`.
  - Suite completa: 204 pasan, 0 skip, en 2 corridas seguidas (76 son de 3C).
  - Rompí 6 reglas a propósito (título, no re-entrada, re-entrada por "visitadas", mailto, fin sin cobrar, búsqueda) y las pruebas detectaron las 6.
  - Esto demuestra que la implementación es correcta, **no** que funcione en otros sitios: no se corrió en sitios reales ni hay referencia NVDA.
- **Problemas y decisiones:**
  - **Bug de 3B encontrado al arrancar:** la suite fallaba en 9 de 11 corridas, siempre en un Enter sobre PDF (`Timeout exceeded while waiting for event "download"`), lo que daba un No evaluable falso.
    - El 20-oct se reportó "127 pasan" sin detectar que era intermitente.
    - Ahora los bytes se piden con `contexto.request`. Prueba nueva: un PDF que exige cookie confirma que usa la misma sesión.
    - Aceptación: 5 corridas seguidas limpias (128 pasan). No determiné por qué se perdía el evento.
  - **Corrección del yaml:** `sin_encabezados` B pasó de **31 a 32**. El 31 suponía comprensión semántica de "Descargas": es texto suelto sin marca, y una estrategia que decide por rol no puede saber que ya no es un requisito. La ruta ahora termina en "Descargas". El estado no cambia (con dificultad en 10, 15 y 25).
  - **Lo que revela el fin no se cobra:** subestima hasta 1 pulsación; la estrategia ve el ROL de la siguiente parada, nunca su nombre. Es coherente con el fin de documento, que tampoco se cobra. Cobrarlo habría cambiado 11 valores del yaml sin cambiar ningún estado.
  - **El trámite es parte de la tarea B:** se fija por sitio antes de correr y nunca indica dónde está. Sin él, "Otro trámite" no se puede rechazar por el título (trae la palabra "trámite") y B de `enlaces_ambiguos` costaría 51 en lugar de 35.
  - **Error mío en CLAUDE.md, corregido:** escribí "URL ya visitada en ese intento". Con esa regla, los 8 intentos a `enlaces_ambiguos_otro.html` se habrían saltado usando la URL. Lo correcto es no re-entrar a una URL abierta en la pila.
  - **Ajuste al plan:** `mejor_estrategia` quedó en el paso 6, no en un commit propio, para poder probar cada estrategia al agregarla. Por eso algunos commits intermedios (6 a 8) tienen pruebas de 3C aún sin pasar; se corrieron solo las de esa pieza.
  - **Sin conjunto reservado:** las reglas y palabras se diseñaron viendo las mismas páginas contra las que se prueban.
  - Nuevos puntos en CLAUDE.md:
    - por verificar en NVDA: rótulos `<span>` de `formulario_sin_etiquetas`, que sí se oyen con flechas;
    - antes de tocar sitios reales: menús colapsados, títulos iguales en todo el sitio, `main` sin nombre y marcador con los requisitos en la misma parada.
- **Siguiente:**
  - Fase 3D: veredicto por tarea contra los `.esperado.yaml`.

## 06-nov-2026 — Fase 3D: veredicto, entrada por sitio, reporte y análisis

- **Qué hice:**
  - Plan primero, aprobado con 5 decisiones. Después: valores esperados a mano en su propio commit (4bcff13) y código en pasos chicos.
  - `src/veredicto.py`: estado y `tipo_falla` a partir de lo que encontró cada estrategia y del objetivo correcto.
  - Expansión de menús colapsados dentro de las estrategias, con 3 páginas nuevas (`ce_menu*`).
  - `src/sitio.py`: lector del CSV de auditoría y corrida por sitio, con un seguro que rechaza URL no locales.
  - `src/reporte.py`: JSON y Markdown por sitio, con la sección "Llegó primero a otra cosa".
  - `src/analisis.py`: matriz, acuerdo observado, AUC con scikit-learn y conteo de falsas llegadas.
- **Resultado:**
  - Las **24 tareas** dan su `estado` y `tipo_falla` del yaml, sin tocar ningún yaml.
  - Suite completa: 317 pasan, 0 skip, en 2 corridas seguidas (113 son de 3D).
  - Los 3 casos de menús dan los valores calculados a mano: 11, 11 y 10.
  - En `ce_menu`, el estado cambia con el umbral: completable con 15 y 25, con dificultad con 10. En las 24 tareas ningún estado depende del umbral, porque lo logrado cuesta a lo sumo 9 o al menos 32.
  - Rompí 11 reglas a propósito y las pruebas detectaron las 11. El seguro de páginas locales no se rompió a propósito, porque esa prueba intentaría conectarse a un sitio externo; se prueba que rechaza.
  - **No hay resultados del estudio:** no se corrió ningún sitio real ni hay auditoría NVDA. El módulo de análisis solo se probó con datos inventados que viven en `tests/test_analisis.py`, y no se reportan.
- **Problemas y decisiones:**
  - **Cambio en la definición de mejor estrategia:** ahora es la de menor fricción entre las que llegan al objetivo correcto. El objetivo solo filtra al final, nunca guía la navegación.
  - **Falsas llegadas:** no cambian el estado, pero se muestran en el reporte y se cuentan aparte en el análisis, porque en un sitio real eso también le puede pasar a una persona.
  - **Palabras clave, cambio a versión 2:** se agrega la lista `expandir` (`menu`, `menu principal`, `abrir menu`, `navegacion`); las demás no cambian. Razón: un botón "Menú" no coincide con ninguna palabra de tarea y su submenú nunca se abriría, lo que daba `no_encontrado` falso.
  - **Objetivo correcto:** los yaml no lo declaran y no se podía deducir de la `ruta`, porque la de `sin_encabezados` B termina en "Descargas". Quedó en un `<pagina>.auditoria.csv` a mano por página, con `veredicto_nvda` vacío porque no hay auditoría.
  - **Página que puntúa axe:** columna opcional `pagina_axe`; vacía usa la entrada. CLAUDE.md pide fijarla de antemano por tarea.
  - **AUC fijado antes de ver datos:** contra NVDA; principal sin `con_dificultad`; secundario contándolo como logrado. Sin p-valores ni intervalos, porque las tareas de un sitio no son independientes.
  - **Corrección de redacción, no de prueba:** el reporte decía "Estimación" y la prueba pedía "estimación"; se cambió el texto del reporte.
  - **Limitaciones nuevas:** la lista de enlaces no descubre lo que está en un submenú cerrado; un enlace roto al documento correcto da `no_encontrado`.
  - Sigue pendiente, antes de sitios reales: títulos iguales en todo el sitio, `main` sin nombre y marcador con los requisitos en la misma parada.
- **Siguiente:**
  - Fase 3E: interfaz local (Streamlit).
  - Decidir qué se mostrará el 19-nov sin auditoría NVDA.

## 06-nov-2026 — Fase 3D.1: preparación para sitios reales (sin correrlos)

- **Qué hice:**
  - Plan primero, aprobado con 3 decisiones y un segundo tope pedido por mí. Valores esperados a mano en su propio commit (83081fe), código en pasos chicos.
  - Medí el **número de paradas** de las 5 portadas del 5-oct (`scripts/medicion/paradas.py`). No corrí estrategias ni veredictos sobre ellas: 104, 71, 123, 127 y 87.
  - Fijé los dos topes y resolví los 3 pendientes de 3C.
  - Agregué el modo "sitio real" y `python -m src.correr_sitio`. **No se usó sobre ningún sitio real.**
- **Resultado:**
  - **Topes fijados por escrito el 6-nov, antes de ver datos:**
    - `TOPE_PULSACIONES = 508`: 4 niveles que permite la profundidad × 127 paradas de la portada más larga. Alto a propósito: uno bajo volvería No evaluable un "no existe" real y escondería barreras.
    - `TOPE_NAVEGACIONES = 30` páginas cargadas por estrategia y por tarea (Enter que navega o descarga; volver no cuenta). Acota peticiones al sitio y tiempo de corrida; `enlaces_ambiguos` B usa 9, así que 30 deja margen amplio.
    - Agotar cualquiera sin resolver da No evaluable con su motivo.
  - Las 24 tareas siguen dando su estrategia, fricción, estado y `tipo_falla`, sin tocar ningún yaml (comprobado en los pasos 4 y 5 y en la suite final).
  - Suite completa: 361 pasan, 0 skip, en 2 corridas seguidas (44 son de 3D.1).
  - Rompí 11 reglas a propósito y las pruebas detectaron las 11. Las negativas tienen la red reemplazada por una falla: si un seguro falla, la prueba falla sin conectarse.
- **Problemas y decisiones:**
  - **El tope ya no se deriva de la auditoría:** CLAUDE.md lo pedía así, pero la auditoría está pospuesta. Reemplazado por el criterio de arriba. Si muchas tareas agotan un tope, se reporta como hallazgo; no se cambia el valor.
  - **Límites de la medición:** 5 portadas de hace un mes, sin menús abiertos, sin iframes y sin páginas interiores.
  - **Títulos iguales:** si el título es igual al de origen, la página se inspecciona con su costo. Queda declarado que un título distinto, pero poco informativo, se rechaza.
  - **`main` sin nombre:** nueva variante `D_a_main`, que lee hasta el final del documento porque el contacto suele estar en el pie. Modifica el conjunto declarado de estrategias. En las 24 tareas nunca gana.
  - **Marcador en la misma parada:** regla estrecha (empieza con el marcador, tiene texto después, no termina en ":"). Una regla más amplia detenía la lectura en "Consulta los requisitos en línea". Queda declarado que "Para este trámite debes presentar INE" no se reconoce.
  - **Modo sitio real:** exige el host por escrito y `veredicto_nvda` en todas las filas. Elimina `solo_local=False`, que yo había agregado en 3D y permitía saltarse la auditoría. No comprueba que la auditoría se hiciera a ciegas ni antes; una estrategia puede seguir un enlace a otro dominio.
  - **Palabras clave:** sin cambios, siguen en la versión 2.
- **Siguiente:**
  - Fase 3E: interfaz local (Streamlit).
  - Para correr un sitio real: hacer su auditoría con NVDA y exportar su CSV.
  - Decidir qué se mostrará el 19-nov.

---

<!-- Plantilla para nuevas entradas:

## DD-mmm-2026 — Título

- **Qué hice:**
- **Resultado:**
- **Problemas y decisiones:**
- **Siguiente:**
-->
