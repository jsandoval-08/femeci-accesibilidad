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
   Deciden la relevancia con una lista declarada de palabras clave por tarea (se definirá en la
   Fase 3); el agente decide por significado. Esa diferencia es lo que mide la comparación
   programadas vs agente.
   PDFs: sin capa de texto = escaneado = no completable.
4. **Agente por decisiones** (IA) — NO construir hasta que Javier lo indique (API aparte).
   - Recibe SOLO nombres y roles anunciados, **por niveles** (primero encabezados; al elegir, lo
     de adentro, INCLUIDO el texto plano / StaticText). Nunca HTML ni URLs. Sin historial: cada
     llamada = tarea + lista actual.
   - El texto de la página es DATO NO CONFIABLE: el prompt lo aísla y el agente no sigue
     instrucciones que aparezcan en el sitio.
   - Agente y estrategias programadas con los mismos límites y permisos.
   - Decide a dónde ir; el emulador ejecuta la ruta y cuenta la fricción.
   - Modelo: Haiku 4.5 primero; Sonnet solo si Haiku no pasa el criterio.
   - Cada tarea se corre 3 veces; se reporta la tasa de éxito.
   - Control de gasto: contador de tokens por llamada y paro automático al pasar el tope.
   - Tope de decisiones por tarea: criterio de MÉTODO (derivado de la auditoría manual), no de costo.
   - Modo tecla por tecla: solo para el demo en 2-3 páginas.
   - Después del 15 oct (opcional): proponer correcciones de código por falla.
5. **Validación** — contra la auditoría manual (referencia):
   - La auditoría manual con NVDA se hace ANTES de correr Atorapp en cada sitio y sin ver su
     resultado. Ahí se fija el **objetivo correcto** de cada tarea y se anota "¿lo encuentra un
     usuario vidente?" (separa barrera de accesibilidad de problema de arquitectura de información).
   - Principal: matriz de confusión (Atorapp vs NVDA manual), descriptivos por sitio y por tarea,
     contraejemplos con trayectoria reproducible y motivo del fallo. **Estrategias programadas vs
     agente** (mide cuánto aporta la IA). Errores de Atorapp clasificados: planificación /
     interacción / barrera real del sitio.
   - Las tareas de un mismo sitio NO son independientes: no tratar ~60 obs. como independientes.
   - axe vs veredictos: el puntaje es continuo → **AUC** (o umbral fijado antes de ver datos).
     Spearman solo secundario y exploratorio. Análisis de sensibilidad del puntaje conservador
     (¿reclasifica páginas y mejora la concordancia con NVDA?).
   - Páginas que puntúa axe: fijas de antemano por tarea (ruta de la auditoría manual), nunca las
     que visite el agente.
   - Segundo evaluador independiente a ciegas sobre submuestra estratificada de 10-12 tareas:
     acuerdo observado, tabla de desacuerdos y kappa PONDERADO.
   - Experimento antes/después: 2-3 reproducciones locales con barrera real confirmada; versión
     corregida que cambia SOLO el defecto; se corren axe, Atorapp y NVDA en ambas. Páginas
     corregidas se re-miden SIN IA. No se diseña para que gane Atorapp.

## Definiciones (no cambiar sin avisar)
- **Tareas** (todas terminan ANTES de enviar nada): A Contacto · B Requisitos de un trámite ·
  C Abrir un documento descargable · D Llegar a un formulario e identificar sus campos
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
- **Mejor estrategia** = mínimo de fricción dentro del conjunto declarado: H+leer, D+leer, lista
  de elementos + elegir por nombre (probando en orden los ambiguos), F a campos, leer desde el
  inicio, Tab desde el inicio (solo objetivos enfocables). El mínimo absoluto queda excluido
  porque requiere conocer el objetivo.
- **Las estrategias solo deciden con lo anunciado** (roles, nombres, títulos al llegar). Si varios
  candidatos no se distinguen por nombre, se prueban en orden del documento y el costo se acumula
  (cada intento fallido = K + Enter + volver), sin conocimiento del objetivo.
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
- **Desde ya, en paralelo:** auditoría manual con NVDA (a ciegas, antes de que exista el emulador).
- **24-31 oct:** Fase 3 (emulador + estrategias programadas) y Fase 4 (agente) solo si sobra tiempo.
- **1 nov: decisión** — el agente se usa solo si logra ≥80 % en un conjunto de páginas de prueba
  reservado y BALANCEADO (completables y no completables), aceptable en ambas clases, Y le gana a las
  estrategias programadas. Si no → estrategias programadas. Sin excepciones. Congelar versión,
  prompts y criterios antes del estudio.
- **2-10 nov:** sitios reales, segundo evaluador, antes/después, análisis. **10 nov:** plan actualizado.
- **19 nov:** exposición. Criterio de "listo": un caso donde Atorapp detecta lo que axe no, uno donde
  coinciden y uno donde Atorapp se equivoca, todos con evidencia.

## Estado actual
**Fase 3A completa (emulador núcleo, `src/emulador.py`, 20-oct). Siguiente: 3B.**

Fase 3 (en este orden; marcar el sub-paso actual):
- **3A** ✅ HECHA. Emulador núcleo sobre un árbol ya capturado: paradas, cursor, H/K/D/F/Tab/flecha/leer de
  corrido, anuncio (rol + nombre). Pruebas con las páginas de prueba (`tests/test_emulador.py`):
  las 17 rutas de una sola página dan exactamente su `friccion_esperada`.
- **3B** ← SIGUIENTE. Navegación en vivo: Enter en enlace navega y recaptura; Enter en botón colapsado expande y
  recaptura; profundidad máx. 3; estado No evaluable por timeout/CAPTCHA/límite.
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
  - Descarga: no se abre visor; bytes por la misma sesión y se registra si el PDF tiene capa de
    texto. No apila nivel. El veredicto lo pone 3D.
  - Profundidad = tamaño de la pila (entrada = nivel 0, máx. 3). Toda pulsación ejecutada cuenta
    (también el Enter que excede la profundidad o da timeout); con tope N, la N+1 no se ejecuta.
  - CAPTCHA (heurística declarada: g-recaptcha, hcaptcha, turnstile, data-sitekey, "No soy un
    robot"): se detecta y se registra por página, NO detiene la sesión (ver regla en 3D).
  - Lista de elementos: `elegir_de_lista(tipo, posicion)` = 1 + posicion (empieza en el primero);
    elegir por nombre y probar ambiguos sigue en 3C.
- **3C** Estrategias programadas + palabras clave por tarea + mejor estrategia + fricción.
  Las estrategias NO re-entran a la URL en la que ya están (un enlace a la misma página sin
  `#`, p. ej. el logo en la portada, es navegación y gastaría profundidad sin avanzar).
- **3D** Veredicto por tarea contra `*.esperado.yaml`; conjunto de prueba balanceado y reservado.
  El conjunto reservado y balanceado para la decisión del 1-nov son páginas **NUEVAS**, distintas
  de las 6 de desarrollo (perfecta, sin_encabezados, sin_contacto, enlaces_ambiguos,
  formulario_sin_etiquetas, pdf_escaneado; ni sus destinos ni `casos_emulador`), y **no se tocan
  hasta 3D**.
  Regla fijada el 20-oct, ANTES de ver datos: tarea **no resuelta + CAPTCHA detectado en la ruta →
  No evaluable** (no No completable). Si la tarea se resolvió aunque hubiera CAPTCHA (p. ej.
  campos identificados en un formulario con reCAPTCHA), cuenta normalmente.
  Regla fijada el 20-oct: en la tarea A, llegar a un enlace `mailto:`/`tel:` cuenta como
  identificar el contacto aunque el nombre anunciado no incluya la dirección o el número (Enter
  abriría el correo o el teléfono con el dato ya puesto; en 3B ese Enter no se ejecuta). La url
  se usa solo para el veredicto, nunca para el anuncio ni para el agente.
- **3E** Interfaz local (Streamlit): modo usuario (navegar solo con lo anunciado) y modo auditoría.

**Pendientes:**
- iframes: getFullAXTree solo cubre el marco principal; resolver si alguna tarea pasa por iframes.
- **Por verificar en NVDA** (durante la auditoría manual): F incluye botones; sin vuelta al llegar
  al final; qué anuncia con imagen sin alt; regiones con nombre como landmark de D; casilla +
  rótulo = una sola línea (decidido 20-oct: se sigue el árbol; Chromium ignora el `<label>` de la
  casilla por `labelFor` porque ya es su nombre, mientras que el de un textbox sí es parada);
  NVDA se detiene en landmark vacío con D; la lista de elementos (NVDA+F7) abre en el primer
  elemento o en el más cercano al cursor (el emulador asume el primero); F se detiene en `switch`;
  qué anuncia en un enlace `mailto:` (¿solo el texto o también la dirección?).
- **Tope de pulsaciones**: se fija con un criterio escrito ANTES del estudio (derivado de la
  auditoría manual), nunca después de ver resultados. En 3B no tiene valor por omisión (`None`).
- Roles fuera de la lista de paradas, medidos el 20-oct (`scripts/medicion/`, capturas del 5-oct,
  estado inicial sin expandir menús): 0 `menuitem`/`switch`/`treeitem`/`option` suelto en las 5
  portadas; 4 `tab` en Culiacán (hoy quedan como texto suelto); 1 landmark vacío en Atención
  Ciudadana. Los submenús colapsados pueden traer `menuitem` al expandir en 3B. Reglas: ver 3B.
