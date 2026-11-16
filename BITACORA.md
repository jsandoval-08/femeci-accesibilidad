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

## 08-nov-2026 — Fase 4, paso 1: del Excel de auditoría NVDA a los CSV (sin correr sitios)

- **Qué hice:**
  - Javier hizo una mini auditoría NVDA a ciegas: sinaloa A, ahome A y ciudadano B. Las demás filas no tienen veredicto y no se usan.
  - Revisé los riesgos contra el código ANTES de correr nada.
  - `scripts/excel_a_csv.py`:
    - escribe un CSV por pestaña con las 7 columnas que lee `src/sitio.py`, en utf-8-sig y solo con las filas que tienen veredicto;
    - guarda las notas del auditor aparte, en `notas_nvda.csv`;
    - valida todo con el lector de Atorapp antes de escribir.
  - Copié el Excel original a `estudio/auditoria/` como evidencia (sha256 `411d608b…`). La versión corregida lo reemplazará y git guardará las dos.
  - `openpyxl==3.1.5` agregado a `requirements.txt`.
- **Resultado:**
  - Suite completa: 369 pasan (8 nuevas).
  - Rompí a propósito la validación nueva y las pruebas detectaron las 4 roturas.
  - **No se corrió ningún sitio real.**
- **Problemas y decisiones:**
  - **`objetivo_correcto` con forma de URL en ahome A y ciudadano B.** El veredicto de A compara teléfono o correo y el de B compara los requisitos leídos, así que una URL nunca coincide. Esas tareas habrían dado no_completable sin importar lo que hiciera Atorapp.
    - El lector ahora rechaza una URL en A, B y D, igual que rechaza un objetivo vacío. En C sí vale, porque ahí el objetivo es la URL del documento.
    - Es validación de entrada, no un cambio de veredicto, y se agregó antes de correr nada.
    - Javier corrige el Excel antes de correr, con lo que vio en el paso vidente de su auditoría. Así la corrección sigue siendo a ciegas respecto a Atorapp.
  - **Riesgos revisados para ciudadano B:**
    - No puede dar completable solo por quedarse en la portada: B compara los requisitos leídos, no la URL.
    - Si los requisitos aparecen sin cambiar de URL, el clic recaptura la misma página y se sigue leyendo desde el cursor.
    - Enter solo se ejecuta en enlaces, `menuitem` y controles con `expanded`. Si las tarjetas son texto o botones sin `expanded`, Atorapp no puede abrirlas: es un límite del emulador y se reportará, no se arregla.
  - **Hallazgo antes de correr:** las estrategias de B no usan el nombre del trámite para elegir un enlace, solo para rechazar por el título al llegar (regla declarada desde 3C).
    - **Decisión: se corre como está.** Cambiarla después de leer la ruta NVDA ("Enter en Acta de nacimiento") sería ajustar Atorapp a la referencia.
    - Queda como limitación y como trabajo futuro.
  - **sinaloa A con `NO_EXISTE`:** da no_completable / no_encontrado. Un contacto en otro host (regla: un subdominio es otro sitio) cuenta como falsa llegada. Riesgo declarado: si alguna estrategia queda No evaluable (timeout o tope), la regla 5 vuelve toda la tarea no_evaluable.
- **Siguiente:**
  - Con el Excel corregido: convertir, correr los 3 sitios con `--sitio-real` (una sola vez cada uno) y hacer el análisis conjunto.

## 08-nov-2026 — Fase 4, pasos 2 y 3: primeras corridas en sitios reales

- **Qué hice:**
  - Javier corrigió dos objetivos en el Excel:
    - ahome A: `correo|teléfono`;
    - ciudadano B: 4 fragmentos de requisitos.
  - Copié el Excel corregido (sha256 `ff689a11…`) y lo convertí. git guarda las dos versiones.
  - Corregí un bug del veredicto de A (detalle abajo), con prueba primero y antes de correr ahome.
  - Corrí cada sitio **una sola vez** con `--sitio-real` y pausa de 1 s:
    - sinaloa a las 20:12;
    - ciudadano a las 20:13;
    - ahome a las 20:17.
  - `scripts/analisis_conjunto.py`:
    - matriz, acuerdo y sensibilidad con 10, 15 y 25;
    - el AUC no se reporta con menos de 10 tareas comparables (umbral fijado antes de ver los datos).
  - Reportes en `estudio/resultados/`. Las capturas quedan fuera de git.
- **Resultado:**

  | Sitio | Tarea | NVDA | Atorapp | Fricción | axe (reglas / elementos / reglas cons. / elementos cons.) |
  |---|---|---|---|---|---|
  | sinaloa | A | no_completable | no_completable, no_encontrado | 123 consumidas | 87.5 / 94.5 / 83.3 / 83.0 % |
  | ciudadano | B | con_dificultad | no_completable, no_encontrado | 73 consumidas | 73.7 / 72.3 / 73.7 / 71.0 % |
  | ahome | A | con_dificultad | no_evaluable (timeout) | 0 | no medido (timeout) |

  - 2 tareas comparables: acuerdo de 1 de 2, igual en 3 clases y en binario, y con los umbrales 10, 15 y 25. Hubo 0 falsas llegadas.
  - **sinaloa A coincide por la razón correcta:**
    - la portada capturada tiene 123 paradas, pero ninguna con palabra clave de contacto ni enlace `mailto:`/`tel:`;
    - ninguna estrategia salió de la portada y la más larga la leyó completa;
    - el auditor anotó lo mismo: no hay teléfono ni correo en ese host.
  - **ciudadano B no coincide por un límite del emulador, no por una barrera del sitio:**
    - en el árbol, "Acta de nacimiento" es `StaticText` (parada 27), no un enlace ni un botón;
    - NVDA lo activa con Enter; el emulador no ejecuta Enter sobre texto (regla de 3B);
    - además, B no usa el nombre del trámite para elegir (decidido antes de correr: no se cambia);
    - es un **error de interacción** de Atorapp, en la clasificación de CLAUDE.md;
    - axe puntúa 73.7 % y no puede ver este problema; tampoco Atorapp lo resolvió.
  - **ahome A:** la entrada no cargó en 60 s, ni para axe ni para las estrategias. Se registra como no_evaluable y no se reintentó. No se averiguó si el sitio estaba caído o rechazaba al navegador automatizado: averiguarlo exigiría más peticiones.
  - Suite completa: 377 pasan, 0 fallan (8 de ellas nuevas: 7 del veredicto de A y 1 del análisis conjunto).
- **Problemas y decisiones:**
  - **Bug del veredicto de A:** con `|`, se juntaban los dígitos de todo el objetivo.
    - Con `correo|teléfono`, el correo nunca contaba; con un número en el correo, tampoco el teléfono.
    - Contradecía CLAUDE.md ("`|` separa varios valores") y las instrucciones de la hoja de auditoría. Ninguna prueba lo cubría, porque las páginas de prueba tienen un solo teléfono.
    - Ahora son alternativas: basta una. Javier lo aprobó antes de correr ahome, y sinaloa y ciudadano no dependen de esta regla.
    - En la práctica no influyó: ahome quedó no_evaluable.
  - Regla de B confirmada sin cambios: exige **todos** los fragmentos (cada uno dentro de algún requisito leído), con requisitos de más permitidos.
  - El reporte JSON guarda solo la trayectoria resumida de la estrategia más larga. Para explicar ciudadano usé la captura de la portada. Pendiente: guardar la trayectoria completa con anuncios, para tener contraejemplos reproducibles.
  - Error mío en el análisis, corregido antes del commit: el motivo del AUC mezclaba tareas comparables con sitios.
- **Siguiente:**
  - Decidir si ahome se corre una vez más otro día, registrándolo como segunda corrida y no como reemplazo.
  - Completar la auditoría de las filas pendientes (ahome B, sinaloa B, ciudadano A, culiacán).
  - Guardar la trayectoria completa en el reporte.

## 13-nov-2026 — Fase 3E: regla para la segunda corrida (fijada ANTES de correrla)

- **Qué hice:**
  - Esta entrada se escribe y se sube a git **antes** de correr ningún sitio. Así la regla no se
    puede ajustar después de ver los resultados.
  - Motivo de la segunda corrida: los reportes del 8-nov solo guardaron la trayectoria resumida. El
    reporte ya guarda la trayectoria completa (commit `92e735b`), y la interfaz de 3E la necesita.
- **Regla (decidida por Javier el 13-nov, sin haber visto ninguna segunda corrida):**
  1. Si la corrida del 8-nov de una tarea fue `no_evaluable` por falla técnica (timeout, error de
     carga), su resultado oficial pasa a ser el de la segunda corrida: veredicto, puntajes de axe y
     pasos. En la interfaz se marca "segunda corrida, AAAA-MM-DD". Hoy aplica solo a **ahome A**.
  2. En las demás tareas manda la corrida del 8-nov. La segunda corrida solo aporta los pasos, y
     solo si coinciden estado, tipo de falla, fricción o pulsaciones consumidas y trayectoria
     resumida. Si no coinciden, los pasos quedan "pendiente" y se declara la diferencia.
  3. Una tarea que no estaba en la corrida del 8-nov (p. ej. ciudadano A, cuando se audite) se toma
     de su primera corrida.
  4. Este es el **único reintento de ahome**. Si vuelve a fallar, ahome A queda `no_evaluable` con
     su motivo y no se corre otra vez.
  5. `estudio/resultados/` (corrida del 8-nov) no se toca. La segunda corrida va a
     `estudio/corridas/AAAA-MM-DD/<sitio>/`. Los resultados oficiales y el análisis que resultan de
     la regla van a `estudio/oficial/`.
- **Alcance de esta noche:** solo sinaloa.gob.mx y www.ahome.gob.mx, una vez cada uno, con
  `--sitio-real` y pausa de 1 s.
  - **ciudadano no se corre:** mañana Javier hace a ciegas la auditoría NVDA de ciudadano A, y antes
    no debe ver ninguna trayectoria de ese sitio. Comando para correrlo después de la auditoría (con
    la fila A ya en el CSV):
    `.venv\Scripts\python.exe -m src.correr_sitio estudio/auditoria/ciudadano.auditoria.csv https://ciudadano.sinaloa.gob.mx/ --carpeta estudio/corridas/AAAA-MM-DD/ciudadano --sitio-real ciudadano.sinaloa.gob.mx`
    Luego, `.venv\Scripts\python.exe scripts/generar_datos_interfaz.py` sin `--ciego ciudadano`.
- **Resultado:** (se completa en la entrada de cierre de 3E).
- **Problemas y decisiones:** las de arriba.
- **Siguiente:** correr sinaloa y ahome; generar `interfaz/datos.js`.

## 14-nov-2026 — Fase 3E: interfaz estática para la demo (3E.1, 3E.2, 3E.3)

- **Qué hice:**
  - 3E.1 Datos:
    - el reporte guarda la trayectoria completa (`pasos`) y lo que halló cada intento (`encontro`);
    - las 24 tareas de prueba tienen reportes en `estudio/resultados_prueba/`;
    - segunda corrida de sinaloa y ahome con la regla de la entrada anterior;
    - `scripts/generar_datos_interfaz.py` arma `estudio/oficial/` e `interfaz/datos.js`.
  - 3E.2 Vistas: Inicio, Trayectoria (reproductor paso a paso) y Comparación, en `interfaz/`. Sin
    bibliotecas, sin red y sin `fetch()`.
  - 3E.3: `tests/test_interfaz.py` corre axe-core 4.14.0 sobre la interfaz y revisa teclado, foco y
    encabezados.
- **Resultado:**
  - **Segunda corrida (14-nov, 07:51–07:57; la carpeta se llama `2026-11-14` porque esa es la fecha real):**
    - sinaloa A da lo mismo que el 8-nov: no_completable, 123 consumidas, mismos 4 puntajes de axe.
      Sus 123 pasos se muestran en la interfaz.
    - ahome A dio **timeout otra vez**, en las estrategias y en axe. Fue su único reintento: queda
      `no_evaluable` y no se vuelve a correr. El resultado oficial ahora sale de la segunda corrida, pero
      no cambia: el análisis queda igual (2 comparables, acuerdo 1 de 2).
    - ciudadano no se corrió (auditoría NVDA a ciegas de ciudadano A pendiente). En `datos.js` va con
      `--ciego ciudadano`: sin trayectorias.
  - Las 24 tareas de prueba coinciden con sus `.esperado.yaml`. Ninguna tiene falsas llegadas.
  - axe sobre la interfaz: **0 violaciones** en 82 estados (Inicio, Comparación, y cada una de las 27
    trayectorias al abrir, a mitad y al final, más una durante la reproducción). El control (un botón sin
    nombre) sí se detecta. Cero peticiones de red.
  - Suite completa: **426 pasan**, 0 fallan (377 previas + 1 del reporte + 8 de la regla + 40 de la interfaz).
  - `estudio/resultados/` sin cambios.
- **Problemas y decisiones:**
  - La regla se escribió y se subió a git antes de correr (commit `f8aaf00`).
  - "Falla técnica" = motivo `timeout` o `falla_tecnica`. Los topes, la profundidad y el CAPTCHA no lo son:
    son el presupuesto o una barrera.
  - Las páginas de prueba muestran "NVDA: Pendiente" y aparte la respuesta esperada, rotulada como escrita a
    mano (no NVDA).
  - El acuerdo se muestra como fracción ("1 de 2"), no como porcentaje. Sin AUC: se muestra su motivo.
  - Tema claro único: más legible en una laptop sobre una mesa con luz de sala.
- **Siguiente:**
  - Después de la auditoría a ciegas de ciudadano A: agregar la fila al CSV, correr ciudadano (comando en la
    entrada del 13-nov) y regenerar `datos.js` sin `--ciego ciudadano`.
  - Ensayar la demo abriendo `interfaz/index.html` con el Wi-Fi apagado.

---

## 14-nov-2026 — Fase 3F: app local de escritorio (modo exploración) + identidad visual

- **Qué hice:**
  - **3F.1** Plan aprobado: FastAPI + uvicorn en 127.0.0.1, ventana con pywebview (respaldo: navegador),
    la persona confirma lo encontrado, fuente Atkinson Hyperlegible local.
  - **3F.2** `app/`: bloqueo de hosts (`config/exploracion.yaml`, 4 barreras: entrada, `route` del contexto,
    redirección y captura de axe), motor `explorar()`, guardado en `exploracion/` (no se versiona),
    servidor con SSE, token en cada POST y solo Host 127.0.0.1, `Atorapp.bat` y `python -m app`.
  - **3F.3** UI con Inicio, Evaluando, Resultado, Recorrido, Historial y Acerca de, siguiendo `Diseno/app1..4`.
  - **3F.4** `interfaz/marca.css` + fuente (OFL) compartidas; aplicada a la app y a la interfaz del estudio.
  - **3F.5** Verificación (abajo).
- **Resultado:**
  - **Cero cambios en `src/`.** El paso a paso en vivo sale de cambiar `emu.trayectoria` por una lista que
    avisa en cada `append`. Prueba de neutralidad: en perfecta A, sin_contacto A, enlaces_ambiguos B,
    pdf_escaneado C y formulario_sin_etiquetas D, `clasificar()` con su objetivo da exactamente lo del yaml.
  - Sin objetivo, el veredicto lo da `clasificar()` con el hallazgo que confirma la persona (o `NO_EXISTE`
    si nadie llegó o si dice «ninguna»): son las reglas del estudio, no unas nuevas. En ce_otro_telefono la
    primera opción es la falsa llegada (3); confirmando la otra da enlace_por_nombre, 7, igual que el estudio.
  - Punta a punta en la app sobre páginas locales: perfecta A = completable, 7 (tras confirmar); sin_contacto
    A = no completable, 42 consumidas. Iguales a sus yaml.
  - axe-core 4.14.0: **0 violaciones** en cada pantalla y estado de la app y en la interfaz del estudio, con
    el control del botón sin nombre en ambas. Foco naranja de 4 px comprobado. Cero peticiones externas.
  - Suite completa: **476 pasan** (426 previas + 50 nuevas). `git diff eba0ec8 -- src/ estudio/
    interfaz/datos.js` vacío. `Atorapp.bat` abrió la ventana en 6 s (con dependencias ya bajadas).
  - Nada se corrió contra sitios reales.
- **Problemas y decisiones:**
  - Comprobado: `route` de Playwright no intercepta el destino de un 302 (la prueba de redirección a un host
    bloqueado la atrapa la barrera 3, que aborta toda la evaluación sin guardar nada).
  - El «mejor» del modo exploración es el de menor fricción entre los que CREEN llegar: sin objetivo, una
    falsa llegada barata sale primero. Por eso se pide confirmar y se ofrecen las demás.
  - «Estudio» abre `interfaz/index.html` por file:// en el navegador (pywebview no tiene botón atrás).
  - El rombo de No evaluable lleva guion (el diseño traía «?»; mandó la especificación).
  - Dependencias nuevas con versión fija: fastapi 0.163.0, uvicorn 0.54.0, httpx 0.28.1, pywebview 6.2.1.
- **Siguiente:**
  - Quitar un host de `config/exploracion.yaml` solo cuando su auditoría NVDA a ciegas esté hecha; agregar
    ANTES cualquier sitio nuevo que se vaya a auditar.
  - Ensayar la demo con la app y con la interfaz.

## 15-nov-2026 — Fase 4: auditoría NVDA a ciegas de ciudadano A, Culiacán A y atención ciudadana A, y su primera corrida

- **Qué hice:**
  - Javier terminó la auditoría NVDA a ciegas de tres filas nuevas y las convirtió con `scripts/excel_a_csv.py`:
    ciudadano A, culiacán A y atencion A (`atencion.auditoria.csv`, con `pagina_axe` = `/asistencia-digital/`, mismo host).
    `config/exploracion.yaml` quedó con `hosts_bloqueados: []`.
  - Commit `9acd77d` con SOLO `estudio/auditoria/` y `config/exploracion.yaml`, **antes de tocar la red**: es la
    evidencia de que la referencia quedó fijada antes de la corrida.
  - Corrí cada CSV **una sola vez** con `--sitio-real` y pausa de 1 s (19:23–19:28), sin cambiar umbrales, topes,
    palabras clave (v2) ni nada más. Salida en `estudio/corridas/2026-11-15/<sitio>/` (commit `49537a5`).
    El CSV de ciudadano trae A y B, así que B se corrió otra vez; va aparte y no reemplaza al 8-nov.
  - `scripts/generar_datos_interfaz.py` sin `--ciego`: regenera `estudio/oficial/` e `interfaz/datos.js` con los 5 sitios.
- **Resultado:**
  - Auditoría NVDA (de `notas_nvda.csv`, conteo manual aproximado, auditor principiante):
    - ciudadano A, con_dificultad, ~17 (H sin encabezados, luego K hasta el pie; con Tab también ~17). Sin landmarks. Orden de Tab raro
      (empieza por el pie, posible `tabindex>0`, sin confirmar). Un campo y un botón sin nombre antes de «VALIDAR UN DOCUMENTO».
      La ruta con Tab se hizo ya sabiendo dónde estaba.
    - culiacán A, completable, ~5 (4 D hasta la región «información de contenido» + 1 al correo). Primer intento ~45 sin reconocer el
      contacto; con flecha ~120. El teléfono es texto plano y NVDA lo parte en dos líneas. La pasada con D se hizo ya sabiendo dónde estaba.
    - atención A, completable, ~11, **única ruta**: ~4 D al pie, 3-4 K al enlace «Whatsapp», Enter, Esc (diálogo del navegador) y H al
      encabezado con el número. **El número se lee en api.whatsapp.com (otro host).** En Asistencia digital un vidente ve teléfono,
      WhatsApp y correo, pero NVDA no lee las tarjetas. El enlace no avisa que sale del sitio.
  - Atorapp (estado, mejor estrategia y fricción; axe reglas / elementos / reglas cons. / elementos cons.):

    | Sitio | Tarea | NVDA | Atorapp | Fricción | axe |
    |---|---|---|---|---|---|
    | ciudadano | A | con_dificultad | completable, Tab_inicio | 13 (con umbral 10: con_dificultad) | 73.7 / 72.3 / 73.7 / 71.0 % |
    | ciudadano | B | con_dificultad | no_completable, no_encontrado (igual que el 8-nov) | 73 consumidas | 73.7 / 72.3 / 73.7 / 71.0 % |
    | culiacán | A | completable | con_dificultad, Tab_inicio | 41 | 89.7 / 95.0 / 83.3 / 94.3 % |
    | atención | A | completable | no_completable, no_encontrado | 105 consumidas | 95.7 / 97.5 / 95.7 / 97.5 % |

  - Análisis oficial (`estudio/oficial/analisis.md`): 6 tareas en 5 sitios, 5 comparables (ahome A no evaluable). Acuerdo de 3 clases
    **1 de 5** (umbral 10: 2 de 5; 15 y 25: 1 de 5); binario 3 de 5. Falsas llegadas: 0 de 6. **AUC no se calcula** (5 < 10 comparables,
    umbral fijado antes). Ningún sitio cargó con problemas: sin timeouts ni CAPTCHA.
  - ciudadano B: la corrida del 15-nov dio lo mismo que la del 8-nov, y por la regla del 13-nov esa sigue siendo la oficial.
  - Suite completa: 488 pasan, 0 fallan.
- **Problemas y decisiones:**
  - Una prueba (`test_app_seguridad.py`) exigía los dos hosts bloqueados; con la lista vacía fallaba. La cambié para que verifique la lista vacía
    (el cambio de config era decisión de Javier). Es el único cambio de prueba.
  - **Criterio de host inconsistente en la referencia (para decidir, no lo resolví):** sinaloa A se juzgó por host exacto (un contacto en otro
    host no cuenta); en atención A el auditor dio `completable` por un número leído en api.whatsapp.com. Atorapp aplica el host exacto.
  - **Sesgo declarado del auditor:** ciudadano A y culiacán A se hicieron con D/Tab sabiendo dónde estaba el contacto; Atorapp no lo sabe. Eso
    abarata la ruta de NVDA frente a la de Atorapp, y no es un error de Atorapp.
  - No se cambió nada tras ver resultados. Pendiente de investigar (no hecho): costo por estrategia en culiacán A (por qué ninguna D llegó al
    pie por menos de 41) y si algún enlace «Whatsapp» se probó en atención A; el reporte guarda solo la mejor estrategia.
- **Siguiente:**
  - Decidir el criterio de host para atención A y si se anota como excepción de la referencia.
  - Reproducir culiacán A y atención A estrategia por estrategia sobre la captura guardada, sin nuevas peticiones al sitio.
  - Push cuando Javier lo decida.

---

<!-- Plantilla para nuevas entradas:

## DD-mmm-2026 — Título

- **Qué hice:**
- **Resultado:**
- **Problemas y decisiones:**
- **Siguiente:**
-->
