# Proyecto FEMECI 2026 — Herramienta de completitud de tareas con lector de pantalla

## Qué es
**Herramienta** que determina automáticamente si una persona que usa lector de pantalla puede
**completar tareas reales** en un sitio web, y cuánto le cuesta. Se valida y se aplica en sitios
institucionales de Sinaloa. Hipótesis de trabajo: el **puntaje de conformidad automática** (axe-core)
NO predice si la tarea se completa. Nunca decir "conformidad WCAG" a secas: axe revisa solo una parte.

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
3. **Emulador de lector de pantalla** (determinista, sin IA) — un ENTORNO: cursor sobre el árbol,
   acciones H, K, D, F (siguiente campo de formulario), Tab, flecha, **leer de corrido**, Enter; devuelve lo que se anunciaría.
   La tecla F debe reconocer todos los roles de campo de formulario (textbox, combobox, checkbox,
   radio, listbox, spinbutton y campos de fecha).
   Fricción = total de pulsaciones de la ruta (salto + lectura). Tab solo llega a enfocables.
   Estrategias programadas (p. ej. "H hasta la sección, luego leer") corren sobre este entorno.
   Deciden la relevancia con una lista declarada de palabras clave por tarea (se definirá en la
   Fase 3); el agente decide por significado. Esa diferencia es lo que mide la comparación
   programadas vs agente.
   PDFs: sin capa de texto = escaneado = no completable.
4. **Agente por decisiones** (IA) — NO construir hasta que Javier lo indique (API aparte).
   - Recibe SOLO nombres y roles anunciados, **por niveles** (primero encabezados; al elegir, lo
     de adentro). Nunca HTML ni URLs. Sin historial: cada llamada = tarea + lista actual.
   - Decide a dónde ir; el emulador ejecuta la ruta y cuenta la fricción.
   - Modelo: Haiku 4.5 primero; Sonnet solo si Haiku no pasa el criterio.
   - Cada tarea se corre 3 veces; se reporta la tasa de éxito.
   - Control de gasto: contador de tokens por llamada y paro automático al pasar el tope.
   - Tope de decisiones por tarea: criterio de MÉTODO (derivado de la auditoría manual), no de costo.
   - Modo tecla por tecla: solo para el demo en 2-3 páginas.
   - Después del 15 oct (opcional): proponer correcciones de código por falla.
5. **Validación** — contra la auditoría manual (referencia):
   - Matriz de confusión 3×3, precisión/recall. **Estrategias programadas vs agente** (mide cuánto
     aporta la IA).
   - Kappa de Cohen con un segundo evaluador independiente a ciegas (2-3 sitios).
   - Análisis por tarea (~60 obs.); Spearman con intervalos de confianza, como exploratoria.
   - Evidencia central: contraejemplos documentados (puntaje alto + tarea no completable).
   - Páginas corregidas se re-miden SIN IA (emulador + recorrido manual NVDA): evita circularidad.

## Definiciones (no cambiar sin avisar)
- **Tareas** (todas terminan ANTES de enviar nada): A Contacto · B Requisitos de un trámite ·
  C Abrir un documento descargable · D Llegar a un formulario e identificar sus campos
- **Estados** — se deciden por la **fricción**: pulsaciones totales (saltos + lectura) con la
  MEJOR estrategia. `UMBRAL = 15`, configurable; se reporta sensibilidad con 10, 15 y 25.
  - **Completable** = se llega y el cierre funciona, con fricción ≤ UMBRAL.
  - **Con dificultad** = se llega y el cierre funciona, con fricción > UMBRAL.
  - **No completable** = no se llega, o no se puede identificar el objetivo, o el cierre está roto.
    Se registra como `tipo_falla`: `no_encontrado` · `no_identificable` · `cierre_roto`.
  - "Dirigida / no dirigida" queda como campo descriptivo (`estrategia`); ya NO decide el estado.
- **Elemento (parada)** = cada parada de flecha abajo: encabezado, enlace, botón, campo de
  formulario y texto suelto (párrafo, elemento de lista, rótulo). El texto dentro de una parada
  no es otra parada; el contenedor de una lista no cuenta.
- **Conteo de pulsaciones**: el cursor empieza antes de la primera parada. H / K / F = 1 por cada
  encabezado / enlace / campo saltado. Flecha abajo = 1 por parada. Lista de enlaces (NVDA+F7)
  = 1 + flechas hasta el enlace, en orden del documento (no se filtra escribiendo). Enter = 1.
  Volver (Alt+←) = 1.
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

## Calendario
- **15 oct:** registro. Captura + axe + emulador + estrategias + piloto 3-5 sitios.
- **Desde ~5 oct, en paralelo:** auditoría manual de ~15 sitios con NVDA.
- **16-31 oct:** agente. **1 nov: decisión** — ≥80% de acierto en páginas de prueba → agente;
  si no → estrategias programadas (plan base). Sin excepciones.
- **10 nov:** plan actualizado. **19 nov:** exposición. Fase de todos los municipios: al final, opcional.

## Estado actual
**Fase 1 completa. Siguiente: Fase 2 (axe-core en vivo).**

**Pendientes:**
- iframes: getFullAXTree solo cubre el marco principal; resolver si alguna tarea pasa por iframes.
