# Atorapp — FEMECI 2026 · completitud de tareas con lector de pantalla

## Qué es
**Atorapp** (siempre con doble p) es una herramienta que **estima** automáticamente si una persona
que usa lector de pantalla puede **completar tareas reales** en un sitio web, y cuánto le cuesta. Es el
INSTRUMENTO que se valida, no el juez: la referencia es la auditoría manual con NVDA. Se aplica en
sitios institucionales de Sinaloa. Hipótesis de trabajo: el **puntaje de conformidad automática**
(axe-core) **no distingue** las tareas completables de las no completables. No se busca probar que axe
es inútil, sino caracterizar sus puntos ciegos. Nunca decir "conformidad WCAG" a secas: axe revisa solo
una parte; el puntaje es un índice definido por Atorapp, con fórmula y denominador explícitos.

Proyecto individual de Javier Sandoval (ITESM Sinaloa). Asesor: Dr. Alonso. FEMECI 2026,
Sistemas Informáticos, Anexo 2 (desarrollo tecnológico: el protagonista es la herramienta).
Software libre, repositorio público.

**Entregables:** (1) resultados del estudio, (2) reporte por sitio con correcciones sugeridas,
(3) 2-3 páginas corregidas para medir el antes/después. NO construir un corrector automático.

## Entorno (Windows)
- Python del proyecto: **3.12**. Hay varias versiones instaladas; `python` apunta a otra.
  Entorno: `py -3.12 -m venv .venv`, activar con `.venv\Scripts\Activate.ps1`. Nada global.
- Ruta: `C:\proyectos\femeci-accesibilidad`. El usuario de Windows tiene espacios: nada del
  proyecto bajo el perfil de usuario.

## Arquitectura (en este orden)
1. **Captura** — Playwright sobre el sitio EN VIVO (para que carguen JS y CSS). Guarda HTML
   renderizado + árbol de accesibilidad. **Sigue la ruta de cada tarea** entre páginas
   (profundidad máx. 3). Se lee "por adentro": el árbol, no la pantalla.
2. **Chequeo automático** — axe-core (WCAG 2.0/2.1 A y AA). Dos puntajes, ambos documentados:
   por **reglas** (pasadas / aplicables) y por **elementos** (el de reglas esconde la magnitud).
3. **Emulador simplificado de lector de pantalla** (determinista, sin IA), inspirado en los
   comandos de NVDA, NUNCA presentado como equivalente a NVDA. Límites declarados: no reproduce
   modo foco/exploración, no lee iframes, no anuncia aria-live, no lee contenido de PDFs, no modela
   el control de foco de modales. Es un ENTORNO: cursor sobre el árbol,
   acciones H, K, D, F (siguiente campo de formulario), Tab, flecha, **leer de corrido**, Enter; devuelve lo que se anunciaría.
   La tecla F reconoce todos los roles de campo de formulario (textbox, searchbox, combobox,
   checkbox, radio, listbox, spinbutton y campos de fecha) **y los botones**, como NVDA (F = cualquier
   campo de formulario; B sería solo botones). Constante `ROLES_F` en `src/emulador.py`.
   *Por verificar en NVDA.*
   Límites del aplanado (declarados): **1 StaticText = 1 parada** (un párrafo con un enlace en medio
   son 3 paradas; un párrafo largo es 1 aunque NVDA lo parta en líneas); el árbol marca enfocable lo
   que tiene `tabindex="-1"` (Tab llega a donde el teclado real no; comprobado); un landmark sin
   paradas adentro no es alcanzable con D (se cambia en 3B); lo que está dentro de `aria-hidden` no existe para el
   emulador aunque sea enfocable.
   Fricción = total de pulsaciones de la ruta (salto + lectura). Tab solo llega a enfocables.
   Estrategias programadas (p. ej. "H hasta la sección, luego leer") corren sobre este entorno.
   Deciden la relevancia con una lista declarada de palabras clave por tarea
   (`config/palabras_clave.yaml`), no por significado.
   PDFs: sin capa de texto = escaneado = no completable.
4. **Agente por decisiones** (IA) — **NO se construye** (decisión del 1-nov aplicada). Queda como
   trabajo futuro (ver **Proyección**). El instrumento son las estrategias programadas.
5. **Validación** — contra la auditoría manual (referencia). **Pospuesta** (ver **Estado actual**):
   mientras no se haga, Atorapp corre SOLO sobre páginas de prueba locales y no se afirma nada
   sobre sitios reales. Lo siguiente aplica cuando se retome:
   - La auditoría manual con NVDA se hace ANTES de correr Atorapp en cada sitio y sin ver su
     resultado. Ahí se fija el **objetivo correcto** de cada tarea y se anota "¿lo encuentra un
     usuario vidente?" (separa barrera de accesibilidad de problema de arquitectura de información).
   - Principal: matriz de confusión (Atorapp vs NVDA manual), descriptivos por sitio y por tarea,
     contraejemplos con trayectoria reproducible y motivo del fallo. Errores de Atorapp clasificados: planificación /
     interacción / barrera real del sitio.
   - Las tareas de un mismo sitio NO son independientes: no tratar ~60 obs. como independientes.
   - axe vs veredictos: el puntaje es continuo → **AUC** (o umbral fijado antes de ver datos).
     Spearman solo secundario y exploratorio. Análisis de sensibilidad del puntaje conservador
     (¿reclasifica páginas y mejora la concordancia con NVDA?).
   - Páginas que puntúa axe: fijas de antemano por tarea (ruta de la auditoría manual), nunca las
     que visiten las estrategias.
   - Segundo evaluador independiente a ciegas sobre submuestra estratificada de 10-12 tareas:
     acuerdo observado, tabla de desacuerdos y kappa PONDERADO.
   - Experimento antes/después: 2-3 reproducciones locales con barrera real confirmada; versión
     corregida que cambia SOLO el defecto; se corren axe, Atorapp y NVDA en ambas. Páginas
     corregidas se re-miden igual que las originales. No se diseña para que gane Atorapp.

## Definiciones (no cambiar sin avisar)
- **Tareas** (todas terminan ANTES de enviar nada): A Contacto · B Requisitos de un trámite ·
  C Abrir un documento descargable · D Llegar a un formulario e identificar sus campos
  - **El trámite es parte de la definición de la tarea B**: es lo que la persona busca. Se fija por
    sitio ANTES de correr y nunca indica dónde está (nombra qué se busca, no su ubicación). Sirve,
    p. ej., para descartar por el título al llegar una página de otro trámite.
- **Estados** — se deciden por la **fricción**: pulsaciones totales (saltos + lectura) con la
  MEJOR estrategia. `UMBRAL = 15`, configurable; se reporta sensibilidad con 10, 15 y 25.
  - **Completable** = se llega y el cierre funciona, con fricción ≤ UMBRAL.
  - **Con dificultad** = se llega y el cierre funciona, con fricción > UMBRAL.
  - **No completable** = no se llega, o no se puede identificar el objetivo, o el cierre está roto.
    Se registra como `tipo_falla`: `no_encontrado` · `no_identificable` · `cierre_roto`.
  - **No evaluable** = falla técnica, CAPTCHA, timeout, o se agota la profundidad / el tope de
    pulsaciones sin resolver. NUNCA cuenta como no completable; se reporta aparte ("no resuelta
    dentro del presupuesto de exploración").
  - Completable exige llegar al **objetivo correcto** fijado en la auditoría manual.
  - Fricción = **esfuerzo de navegación** (pulsaciones), no dificultad humana completa. En tareas
    fallidas se reportan aparte las pulsaciones consumidas hasta detenerse.
- **Alcance**: piso de 10 sitios con tareas A y B (obligatorias); meta ~15 sitios con las 4. Por sitio
  se declara qué tareas aplican. Tarea C termina al activar el enlace correcto (no se evalúa todo el
  contenido del PDF).
  - "Dirigida / no dirigida" queda como campo descriptivo (`estrategia`); ya NO decide el estado.
- **Elemento (parada)** = cada parada de flecha abajo: encabezado, enlace, botón, campo de
  formulario, **imagen** y texto suelto (párrafo, elemento de lista, rótulo). El texto dentro de una
  parada no es otra parada; el contenedor de una lista no cuenta.
  - Imagen: con o sin nombre (anuncio "gráfico" + nombre si lo tiene). Si solo contaran las que
    tienen alt, una imagen sin alt bajaría la fricción y premiaría el error. Las de `alt=""` o de
    presentación quedan fuera porque Chromium ya no las expone como imagen (comprobado).
    *Por verificar en NVDA: qué anuncia con una imagen sin alt.*
- **Conteo de pulsaciones**: el cursor empieza antes de la primera parada. H / K / F = 1 por cada
  encabezado / enlace / campo saltado. Flecha abajo = 1 por parada. Lista de enlaces (NVDA+F7)
  = 1 + flechas hasta el enlace, en orden del documento (no se filtra escribiendo). Enter = 1.
  Volver (Alt+←) = 1.
  **Sin siguiente** (H sin más encabezados, flecha al final, Tab tras el último enfocable): el
  cursor no se mueve ni da la vuelta al inicio, se anuncia "no hay más …" y la pulsación **cuenta 1**
  (la persona sí presionó; así descubre que no hay más). NVDA por omisión no da la vuelta (JAWS sí).
  *Por verificar en NVDA.*
- **Mejor estrategia** (cambio del 6-nov) = la de **menor fricción entre las que llegan al objetivo
  correcto**. El objetivo solo filtra al final, nunca guía la navegación: las estrategias no lo
  conocen y se detienen en lo que creen que es. Las que llegaron a otra cosa no cambian el estado,
  pero se reportan como **falsas llegadas** (en el reporte, "Llegó primero a otra cosa"; en el
  análisis, conteo aparte), porque en un sitio real eso también le puede pasar a una persona.
- **Conjunto declarado de estrategias**: H+leer, D+leer, D a `main` y leer hasta el final del
  documento, lista de enlaces + elegir por nombre, F a campos, leer desde el inicio, Tab desde el inicio (solo
  objetivos enfocables) y probar en orden los enlaces ambiguos (H a la sección, o desde el inicio;
  K + Enter + volver). En ese orden se desempata: no cambia la fricción, solo el nombre reportado.
  El mínimo absoluto queda excluido porque requiere conocer el objetivo. La lista de encabezados
  no entra: cuesta 1 + (n−1) + Enter = n+1 contra n de H, así que nunca gana.
- **Lo que revela el fin no se cobra** (decidido 5-nov): la pulsación que solo confirmaría que ya
  se terminó (oír que tras el último requisito viene un encabezado, o que tras el último campo
  viene el botón) no cuenta. **Límite exacto: subestima hasta 1 pulsación; la estrategia ve el ROL
  de la siguiente parada, nunca su nombre.** Es coherente con el fin de documento, que tampoco se
  cobra: leer de corrido hasta el final cuesta una pulsación por parada leída, sin una de más para
  descubrir que no hay más (`sin_contacto` A = 42 con 42 paradas). En ambos casos la fricción mide
  lo recorrido hasta terminar de oír el objetivo. Es la única excepción a "solo deciden con lo
  anunciado". Como solo se usa el rol, un texto sin marca que sigue al objetivo se sigue leyendo
  (`sin_encabezados` B = 32: "Descargas" es texto suelto; distinguirlo exigiría significado).
- **Las estrategias solo deciden con lo anunciado** (roles, nombres, títulos al llegar). Si varios
  candidatos no se distinguen por nombre, se prueban en orden del documento y el costo se acumula
  (cada intento fallido = K + Enter + volver), sin conocimiento del objetivo. La URL no decide
  relevancia; solo se lee para dos cosas: el esquema `mailto:`/`tel:` de la parada donde YA está
  el cursor (regla del 20-oct, ver 3D) e impedir re-entrar a una URL abierta en la pila de ese
  intento (la actual o una anterior). Una página ya visitada y cerrada sí se puede volver a abrir:
  con enlaces ambiguos la persona no sabe por el nombre que llevan al mismo lugar.
- **Limitación del método**: Ctrl+F (búsqueda de texto de NVDA) queda excluido; se declara como
  limitación, no se modela. Tampoco se modela filtrar escribiendo en la lista de enlaces.
- **Punto de entrada**: parámetro explícito de cada tarea.

## Reglas de trabajo
- Responder en **español** y explicar el porqué: Javier debe poder defender todo ante un jurado.
- **Plan primero, código después.** Pasos chicos: pieza → prueba → commit → siguiente.
- **Páginas de prueba primero** (`tests/paginas/`, con respuesta conocida, incluidos casos
  semánticos ambiguos). Nada se usa en sitios reales sin pasarlas.
- Nunca enviar formularios ni crear cuentas en sitios reales. Pausas entre peticiones.
- No inventar datos. Lo que no se midió se reporta como no medido. Código simple, comentarios en español.
- **Bitácora**: al cerrar cada sesión de trabajo, agregar una entrada a `BITACORA.md` con la plantilla
  del final del archivo (qué hice, resultado, problemas y decisiones, siguiente). Fechas reales.

## Calendario
- **23 oct:** registro (la plataforma dice cierre 24/10; se trabaja con el 23). Anexo 2 con resultados
  preliminares (5 portadas, páginas de prueba, hallazgo de `bypass`).
- **Auditoría manual con NVDA: pospuesta** (5-nov). Sigue siendo la referencia del estudio.
- **1 nov: decisión aplicada** — el agente de IA NO se construye; se usan estrategias programadas.
- **Noviembre:** Fase 3 sobre páginas de prueba locales, SIN sitios reales. Sitios reales, segundo
  evaluador y análisis contra NVDA quedan sujetos a retomar la auditoría.
- **19 nov:** exposición. Criterio de "listo": un caso donde Atorapp detecta lo que axe no, uno donde
  coinciden y uno donde Atorapp se equivoca, todos con evidencia.

## Proyección (trabajo futuro, NO se construye ahora)
**Agente por decisiones (IA):** recibiría solo nombres y roles anunciados, por niveles, nunca HTML ni
URLs; el texto de la página sería dato no confiable; con los mismos límites y permisos que las
estrategias programadas. Decidiría por significado donde ellas deciden por palabras clave, y
compararlos mediría cuánto aporta la IA. Control de gasto y corrida repetida de cada tarea.

## Estado actual
**Fase 3D.1 completa (preparación para sitios reales, sin correrlos, 6-nov). Siguiente: 3E.**
**Alcance vigente (5-nov):** Atorapp corre SOLO sobre páginas de prueba locales; nada de sitios
reales. La auditoría manual con NVDA se pospone. El agente de IA no se construye. El modo
"sitio real" ya existe, pero no se ha usado: exige la auditoría antes (ver 3D.1).

Fase 3 (en este orden; marcar el sub-paso actual):
- **3A** ✅ HECHA. Emulador núcleo sobre un árbol ya capturado: paradas, cursor, H/K/D/F/Tab/flecha/leer de
  corrido, anuncio (rol + nombre). Pruebas con las páginas de prueba (`tests/test_emulador.py`):
  las 17 rutas de una sola página dan exactamente su `friccion_esperada`.
- **3B** ✅ HECHA. Navegación en vivo: Enter en enlace navega y recaptura; Enter en botón colapsado expande y
  recaptura; profundidad máx. 3; estado No evaluable por timeout/límite/falla técnica (el CAPTCHA
  se registra, ver 3D). Pruebas: `tests/test_navegacion.py` (26) y las 24 rutas de los
  `.esperado.yaml` dan exactamente su `friccion_esperada` (las 7 que cruzan páginas o activan
  el PDF, en vivo), 0 skip.
  Además (decidido 20-oct; casos primero con valores a mano, luego código):
  - Roles interactivos que no son enlace (`tab`, `menuitem`, `menuitemcheckbox`, `menuitemradio`,
    `switch`, `option` fuera de select, `treeitem`) → parada propia, texto interno fundido, K NO se
    detiene (si una tarea depende de ellos con K, es barrera real del sitio).
  - Tab en rol `tab`: solo se detiene si `selected=true` (patrón ARIA de pestañas); las demás solo
    con flecha. El anuncio incluye "seleccionada" cuando aplique.
  - Landmark sin paradas propias: se anota en la SIGUIENTE parada, para que D lo cuente.
    (1) Si es lo último del documento (no hay siguiente parada), D lo anuncia sin mover el cursor
    y la pulsación cuenta 1. (2) Limitación declarada: el anuncio de D combina el landmark con una
    parada que está FUERA de él. No se crea una parada vacía porque inflaría la fricción de flecha.
  Plan aprobado 20-oct (casos en `casos_navegacion.html`, servidor local http, no file://):
  - Enter en enlace → pestaña NUEVA del mismo contexto (una por nivel); volver = cerrar esa
    pestaña y reusar el árbol guardado, cursor en el enlace activado, sin recapturar. Limitación:
    se navega a la URL, no se ejecuta el `onclick` del enlace.
  - Enter en botón/enlace/menuitem con `expanded`, en pestaña no seleccionada o en enlace sin URL
    navegable → clic en la misma página y recaptura; el cursor se queda (se reubica por id del DOM).
  - Enter en `#id` de la misma página → el cursor va a la primera parada desde ese elemento, cuesta
    1, sin recaptura ("Saltar al contenido" = 1: es el mecanismo de `bypass`). Sin destino → clic.
  - Enter en campos y botones sin `expanded` → no se ejecuta (nunca enviar formularios).
  - Enlace a la misma página sin `#` → navegación normal (recarga). `href="#"` → clic en la
    misma página. `mailto:`/`tel:` → no se ejecuta ni cuenta (abriría otra aplicación).
    Medido en las 5 portadas del 5-oct (`scripts/medicion/enlaces_href.py`): de 164 enlaces,
    150 con URL navegable, 6 `#id`, 7 `#` solo, 0 `javascript:`, 1 `mailto:`.
  - Descarga: no se abre visor; bytes por la misma sesión (`contexto.request`, 5-nov: esperar el
    evento `download` fallaba de forma intermitente; cuesta una petición más al sitio) y se
    registra si el PDF tiene capa de texto. No apila nivel. El veredicto lo pone 3D.
  - Profundidad = tamaño de la pila (entrada = nivel 0, máx. 3). Toda pulsación ejecutada cuenta
    (también el Enter que excede la profundidad o da timeout); con tope N, la N+1 no se ejecuta.
  - CAPTCHA (heurística declarada: g-recaptcha, hcaptcha, turnstile, data-sitekey, "No soy un
    robot"): se detecta y se registra por página, NO detiene la sesión (ver regla en 3D).
  - Lista de elementos: `elegir_de_lista(tipo, posicion)` = 1 + posicion (empieza en el primero);
    elegir por nombre y probar ambiguos sigue en 3C.
  - Limitaciones declaradas de 3B: un clic en la misma página que termina navegando se reporta
    como falla técnica (no modelado); `tipo_contenido` de una descarga se deduce del nombre del
    archivo; no se anuncia el estado marcado de `switch`/`menuitemcheckbox` ni "contraído" en
    `combobox`; Enter en `switch`, `treeitem` sin `expanded` y `menuitemcheckbox/radio` no se
    ejecuta; `option` suelta no existe en el árbol de Chromium (comprobado).
- **3C** ✅ HECHA. Estrategias programadas + palabras clave por tarea + mejor estrategia + fricción.
  Pruebas: `tests/test_estrategias.py` (76); en las 24 tareas de los `.esperado.yaml`, la mejor
  estrategia coincide con su `estrategia` y su `friccion_esperada` (tras corregir `sin_encabezados`
  B a 32, ver bitácora del 5-nov). Valores escritos a mano antes del código.
  Las estrategias NO re-entran a la URL en la que ya están (un enlace a la misma página sin
  `#`, p. ej. el logo en la portada, es navegación y gastaría profundidad sin avanzar).
  Reglas: ver **Definiciones** (mejor estrategia, lo que revela el fin, trámite). Además:
  - **Palabras clave**: `config/palabras_clave.yaml`, **versión 2, congelada** el 6-nov (v2 agrega
    `expandir`, ver bitácora). Se comparan sobre nombres normalizados, como palabra o frase
    completa. Cualquier cambio sube la versión y va a `BITACORA.md` con su razón.
  - **"Creo que llegué"** (no es completable; eso es de 3D). A: el texto anunciado trae un correo, 10
    dígitos agrupados (12 con lada 52) o 7 o más junto a una palabra de teléfono; o el cursor ya está
    en un enlace `mailto:`/`tel:`. B: un marcador, y al menos 1 texto después; el bloque termina
    en la siguiente parada que no sea texto. C: un enlace con palabra clave devuelve un `Documento`.
    D: F llega a un campo que no sea de búsqueda y enumera hasta un botón o hasta que no hay más.
  - **Enlaces**: los de nombre genérico se prueban en orden; rechazo por título al llegar (en B,
    contra el trámite buscado). Los enlaces sin nombre no se prueban: ese es el defecto del sitio.
    Tras cruzar se conserva la misma estrategia (la lista lee desde el inicio en A y B, F en D,
    y `probar_enlaces` sigue con H + leer).
  - **Si nadie llega**: se reporta lo más consumido entre estrategias y el motivo; si alguna quedó
    No evaluable, la tarea es "no resuelta dentro del presupuesto", nunca "no llegó".
  - Variantes que no se modelan porque no ganan: leer las tarjetas de `enlaces_ambiguos` (36 o 37
    contra 35); la lista de encabezados (n + 1 contra n).
- **3D** ✅ HECHA. Veredicto por tarea contra `*.esperado.yaml`. Sin conjunto reservado: solo servía para
  decidir el agente, que ya no se construye. Consecuencia declarada: las reglas y palabras clave
  se diseñaron viendo las mismas páginas contra las que se prueban, así que pasar esas pruebas
  demuestra que la implementación es correcta, no que funcione en otros sitios.
  Regla fijada el 20-oct, ANTES de ver datos: tarea **no resuelta + CAPTCHA detectado en la ruta →
  No evaluable** (no No completable). Si la tarea se resolvió aunque hubiera CAPTCHA (p. ej.
  campos identificados en un formulario con reCAPTCHA), cuenta normalmente.
  Regla fijada el 20-oct: en la tarea A, llegar a un enlace `mailto:`/`tel:` cuenta como
  identificar el contacto aunque el nombre anunciado no incluya la dirección o el número (Enter
  abriría el correo o el teléfono con el dato ya puesto; en 3B ese Enter no se ejecuta). La url
  se usa solo para cerrar la tarea y para el veredicto, nunca para el anuncio.
  Pruebas: `tests/test_veredicto.py`, `test_sitio.py`, `test_analisis.py`; las 24 tareas dan su
  `estado` y `tipo_falla` del yaml. Objetivo correcto de las páginas de prueba:
  `tests/paginas/<pagina>.auditoria.csv`, a mano, sin datos de NVDA.
  - **Veredicto** (`src/veredicto.py`), reglas en orden; gana la primera que aplique: (1) C: documento
    correcto, PDF sin capa → `cierre_roto`; (2) C: PDF correcto ilegible → No evaluable; (3) alguna
    llegó al objetivo correcto → por fricción; (4) D: algún campo sin nombre (basta uno) →
    `no_identificable`; (5) sin resolver, con No evaluable o CAPTCHA en la ruta → No evaluable (la
    insignia invisible de reCAPTCHA v3 sola no bloquea); (6) lo demás → `no_encontrado`.
  - **Comparación con el objetivo**: `|` separa varios valores. A: con 7 dígitos o más se comparan
    los dígitos (nombre o `tel:`); si no, el texto (nombre o `mailto:`). B: todos los requisitos,
    con extras permitidos. C: la URL del documento es el objetivo o termina en él, por segmentos.
    D: cada campo en algún nombre. `NO_EXISTE`: la referencia dice que el sitio no lo tiene.
  - **Menús**: un control colapsado se abre solo si su nombre coincide con las palabras de la tarea o
    con `expandir`. Enter cuesta 1. **Limitación:** la lista de enlaces no ve botones, así que
    no descubre lo que está en un submenú cerrado (no se mezclan estrategias) y la fricción de esos
    objetivos puede salir más alta que la real.
  - **Entrada** (`src/sitio.py`): CSV por sitio con `tarea, entrada, tramite, objetivo_correcto,
    veredicto_nvda, vidente_lo_encuentra` y `pagina_axe` opcional (vacía = la entrada). Objetivo
    vacío es error. `correr_sitio` rechaza URL no locales si no recibe `sitio_real` (ver 3D.1).
  - **Reporte** (`src/reporte.py`): JSON + Markdown por sitio, con la sección "Llegó primero a otra
    cosa". **Análisis** (`src/analisis.py`), definido ANTES de ver datos: matriz y acuerdo (3 clases y
    binario) contra NVDA; AUC de los 4 puntajes contra NVDA (principal: excluye `con_dificultad`;
    secundario: lo cuenta como logrado; contra Atorapp, solo exploratorio); falsas llegadas por tarea.
    Sin p-valores ni intervalos: las tareas de un sitio no son independientes. **Aún no hay datos
    reales:** lo inventado vive solo en `tests/test_analisis.py` y nunca se reporta.
  - **Limitación:** un enlace roto (404) al documento correcto da `no_encontrado`, aunque quizá
    debería ser `cierre_roto`.
- **3D.1** ✅ HECHA (6-nov). Preparación para sitios reales, sin correrlos. Pruebas:
  `tests/test_preparacion.py`, `test_sitio_real.py`.
  - **Topes, por estrategia y por tarea, fijados por escrito el 6-nov ANTES de ver datos** (`src/sitio.py`):
    - `TOPE_PULSACIONES = 508`. Criterio: 4 niveles que permite la profundidad × 127 paradas, la
      portada más larga de las 5 del 5-oct (`scripts/medicion/paradas.py`: 104, 71, 123, 127, 87; solo
      se midió el número de paradas, sin correr estrategias ni veredictos). Alto a propósito: uno
      bajo volvería No evaluable un "no existe" real y escondería barreras. Reemplaza el criterio
      anterior ("derivado de la auditoría manual"), porque la auditoría está pospuesta.
    - `TOPE_NAVEGACIONES = 30` páginas cargadas (Enter que navega o descarga; volver, un `#id` y un
      clic en la misma página no cuentan; la entrada tampoco). Criterio: acota peticiones al sitio y
      tiempo de corrida; `enlaces_ambiguos` B usa 9, así que 30 deja margen amplio.
    - Agotar cualquiera sin resolver = No evaluable con motivo `tope_pulsaciones` o
      `tope_navegaciones`; el Enter que excede no hace la petición ni cuenta. Si otra estrategia llega
      al objetivo correcto, cuenta esa. **Si muchas tareas agotan un tope, se reporta como hallazgo y
      no se cambia el valor**; un cambio exige razón en la bitácora y repetir todos los sitios.
  - **Títulos iguales**: si el título al llegar es igual al de origen, no dice nada: la página se
    inspecciona con H + leer, con su costo. **Limitación:** un título distinto, pero poco informativo
    ("Detalle"), se rechaza aunque sea el enlace correcto.
  - **`main` sin nombre**: variante `D_a_main`: D hasta `main` y leer hasta el final del documento (el
    contacto suele estar en el pie); en la tarea D, F desde ahí.
  - **Marcador en la misma parada**: cuenta si el texto EMPIEZA con el marcador, tiene texto después
    y no termina en ":". **Limitación:** "Para este trámite debes presentar INE" no se reconoce.
  - **Modo sitio real**: `correr_sitio(..., sitio_real=<host>)` o `python -m src.correr_sitio ...
    --sitio-real <host>`. Se niega antes de tocar la red si: el host no coincide con `url_base`, alguna
    URL del CSV está en otro host, falta `veredicto_nvda` en alguna fila o la pausa baja de 1 s.
    **Limitaciones:** comprueba que hay veredictos, no que la auditoría se hizo a ciegas ni antes
    (sigue siendo disciplina del auditor); una estrategia puede seguir un enlace con palabra clave a
    otro dominio (bloquearlo daría `no_encontrado` falso con PDF oficiales en otro host).
- **3E** ← SIGUIENTE. Interfaz local (Streamlit): modo usuario (navegar solo con lo anunciado) y modo auditoría.

**Pendientes:**
- iframes: getFullAXTree solo cubre el marco principal; resolver si alguna tarea pasa por iframes.
- **Por verificar en NVDA** (durante la auditoría manual): F incluye botones; sin vuelta al llegar
  al final; qué anuncia con imagen sin alt; regiones con nombre como landmark de D; casilla +
  rótulo = una sola línea (decidido 20-oct: se sigue el árbol; Chromium ignora el `<label>` de la
  casilla por `labelFor` porque ya es su nombre, mientras que el de un textbox sí es parada);
  NVDA se detiene en landmark vacío con D; la lista de elementos (NVDA+F7) abre en el primer
  elemento o en el más cercano al cursor (el emulador asume el primero); F se detiene en `switch`;
  qué anuncia en un enlace `mailto:` (¿solo el texto o también la dirección?);
  `formulario_sin_etiquetas`: los rótulos son `<span>` justo antes de cada campo, así que con
  flechas sí se oye "Nombre completo" y luego "edición" (`no_identificable` vale para F, quizá no
  para una persona real).
- Roles fuera de la lista de paradas, medidos el 20-oct (`scripts/medicion/`, capturas del 5-oct,
  estado inicial sin expandir menús): 0 `menuitem`/`switch`/`treeitem`/`option` suelto en las 5
  portadas; 4 `tab` en Culiacán (hoy quedan como texto suelto); 1 landmark vacío en Atención
  Ciudadana. Los submenús colapsados pueden traer `menuitem` al expandir en 3B. Reglas: ver 3B.
