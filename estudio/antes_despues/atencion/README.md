# Antes/después: atención ciudadana, tarea A — REPRODUCCIONES EXPERIMENTALES

**Estas páginas no son el sitio oficial.** Son copias locales de
`https://atencionciudadana.sinaloa.gob.mx/asistencia-digital/`, hechas a partir de la captura de Atorapp del
15-nov-2026 19:28, para el experimento antes/después (sección 6.8 del Anexo). El prerregistro y su enmienda están en
`BITACORA.md` (16-nov).

| Carpeta / archivo | Qué es |
|---|---|
| `original/index.html` | La captura con 4 cambios que no tocan el árbol de accesibilidad: un comentario que la rotula; un `<meta>` CSP que impide cargar nada externo (ni CSS ni JS ni imágenes del sitio); las 6 tarjetas de `main` apuntando a `tarjetas/`; y una regla de **CSS reconstruido** (`#elementor-device-mode::after{content:"desktop"}`), que **no viene del sitio** y deja el árbol idéntico al capturado. |
| `corregida/index.html` | `original/` con el `alt` de las 4 tarjetas sin enlace cambiado por su texto visible literal. Nada más. |
| `correccion.diff` | El diff completo entre las dos versiones (4 líneas). |
| `tarjetas/` | Las 6 PNG (16-nov, con sha256 en `descarga.json`) y su transcripción validada. |
| `validacion_arbol.txt` | Árbol de `original/` contra el capturado: 32 de 32 paradas idénticas. |
| `mediciones/` | axe y Atorapp, una corrida por versión (`scripts/antes_despues.py medir`). |
| `nvda.csv` | Resultado de NVDA en las dos versiones, anotado por Javier el 16-nov (columnas abajo). |
| `resultados.md` | Tabla final original contra corregida, con la tabla por estrategia. |

**Plantilla `nvda.csv`:** una fila por versión. Las columnas son:
- `estado_nvda`: completable, con_dificultad, no_completable o no_evaluable.
- `tipo_falla`: solo si no_completable (no_encontrado, no_identificable o cierre_roto).
- `pulsaciones_aprox`: el conteo como en la auditoría (saltos + lectura).
- `ruta_nvda`: las teclas, p. ej. «D×5, flecha×2».
- `dato_oido`: el contacto tal como lo anunció NVDA.
- `notas`: lo demás.

`a_ciegas` ya viene en `no`: el auditor conoce el sitio. Mismo umbral (15) y la misma entrada que Atorapp
(`/asistencia-digital/`).

**Cómo abrirlas (también para NVDA):** desde la raíz del repo,
`py -3.12 -m http.server 8765 --bind 127.0.0.1 --directory estudio/antes_despues/atencion`, y luego
`http://127.0.0.1:8765/original/` y `http://127.0.0.1:8765/corregida/`. Por la CSP se ven sin estilos, pero el
árbol que lee el lector es el del sitio. Un enlace del menú o del pie sí lleva al sitio real: la tarea termina antes.

**Límites:**
- La entrada es la página `/asistencia-digital/`, no la tarea desde la portada. La fricción no se compara con las 105
  de la corrida oficial.
- Las 2 tarjetas del pie (correo y línea telefónica) también tienen `alt=""` y no se corrigen.
- Sin el CSS del sitio, los puntajes de axe que dependen de estilos (p. ej. contraste) no son los del sitio en vivo.
  Solo vale comparar original local contra corregida local.
