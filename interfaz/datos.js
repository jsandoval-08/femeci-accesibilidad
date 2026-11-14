// Generado por scripts/generar_datos_interfaz.py. No editar a mano.
window.ATORAPP = {
 "generado": "2026-11-14T08:01:27-07:00",
 "umbral": 15,
 "nota": "Esta es una estimación de Atorapp sobre lo que un lector de pantalla anunciaría; la referencia es la auditoría manual con NVDA. El puntaje de conformidad automática mide solo lo que axe-core revisa, sobre la página fijada de antemano para cada tarea.",
 "reales": [
  {
   "sitio": "ahome",
   "url_base": "https://www.ahome.gob.mx/",
   "tarea": "A",
   "entrada": "/",
   "tramite": null,
   "objetivo_correcto": "contacto@ahome.gob.mx|(668) 816-4000",
   "pagina_axe": "/",
   "estado": "no_evaluable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": null,
   "consumidas": 0,
   "motivo": "no resuelta dentro del presupuesto: timeout",
   "sensibilidad": {
    "10": "no_evaluable",
    "15": "no_evaluable",
    "25": "no_evaluable"
   },
   "trayectoria": "entrada×1",
   "pasos": [
    {
     "tecla": "entrada",
     "anuncio": "no evaluable: timeout",
     "pulsaciones": 0,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": null,
     "no_evaluable": "timeout",
     "pagina": "/"
    }
   ],
   "encontro": null,
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": null,
   "error_axe": "TimeoutError: Page.goto: Timeout 60000ms exceeded.\nCall log:\n  - navigating to \"https://www.ahome.gob.mx/\", waiting until \"load\"\n",
   "veredicto_nvda": "con_dificultad",
   "vidente_lo_encuentra": true,
   "corrida": "segunda corrida, 2026-11-14",
   "fecha": "2026-11-14T07:57:45-07:00",
   "nota_corrida": "La corrida del 2026-11-08 fue no_evaluable, 0 pulsaciones consumidas (no resuelta dentro del presupuesto: timeout). Por la regla del 13-nov, el resultado oficial es el de la segunda corrida (único reintento).",
   "ciego": false,
   "marcas": [
    {
     "paso": 0,
     "tipo": "detenido",
     "texto": "Aquí se detuvo sin poder evaluar: no resuelta dentro del presupuesto: timeout"
    }
   ]
  },
  {
   "sitio": "ciudadano",
   "url_base": "https://ciudadano.sinaloa.gob.mx/",
   "tarea": "B",
   "entrada": "/",
   "tramite": "Acta de nacimiento",
   "objetivo_correcto": "Certificado de nacimiento|constancia de inexistencia de no registro|Acta de matrimonio|Identificación oficial",
   "pagina_axe": "/",
   "estado": "no_completable",
   "tipo_falla": "no_encontrado",
   "estrategia": "no_dirigida",
   "friccion": null,
   "consumidas": 73,
   "motivo": "ninguna estrategia encontró el objetivo",
   "sensibilidad": {
    "10": "no_completable",
    "15": "no_completable",
    "25": "no_completable"
   },
   "trayectoria": null,
   "falsas_llegadas": null,
   "captcha": [],
   "puntajes": {
    "reglas": 0.7368421052631579,
    "elementos": 0.7225433526011561,
    "reglas_conservador": 0.7368421052631579,
    "elementos_conservador": 0.7102272727272727
   },
   "veredicto_nvda": "con_dificultad",
   "vidente_lo_encuentra": true,
   "corrida": "corrida del 2026-11-08",
   "fecha": "2026-11-08T20:14:20-07:00",
   "nota_corrida": "Pendiente: auditoría NVDA a ciegas en curso en este sitio.",
   "pasos": null,
   "encontro": null,
   "ciego": true,
   "marcas": []
  },
  {
   "sitio": "sinaloa",
   "url_base": "https://sinaloa.gob.mx/",
   "tarea": "A",
   "entrada": "/",
   "tramite": null,
   "objetivo_correcto": "NO_EXISTE",
   "pagina_axe": "/",
   "estado": "no_completable",
   "tipo_falla": "no_encontrado",
   "estrategia": "no_dirigida",
   "friccion": null,
   "consumidas": 123,
   "motivo": "ninguna estrategia encontró el objetivo",
   "sensibilidad": {
    "10": "no_completable",
    "15": "no_completable",
    "25": "no_completable"
   },
   "trayectoria": "leer×123",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.875,
    "elementos": 0.945054945054945,
    "reglas_conservador": 0.8333333333333334,
    "elementos_conservador": 0.8295819935691319
   },
   "veredicto_nvda": "no_completable",
   "vidente_lo_encuentra": false,
   "corrida": "corrida del 2026-11-08",
   "fecha": "2026-11-08T20:13:30-07:00",
   "nota_corrida": "Pasos de la segunda corrida (2026-11-14), que dio el mismo resultado; el veredicto es el de la primera.",
   "pasos": [
    {
     "tecla": "leer",
     "anuncio": "enlace, Ir al contenido",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Transparencia, contraído",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Sala de Prensa",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Facebook",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, X-twitter",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Instagram",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Youtube",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, BIENVENIDO AL PORTAL DE SINALOA",
     "pulsaciones": 10,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 4, Cuarto Informe de Gobierno",
     "pulsaciones": 11,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Informe",
     "pulsaciones": 12,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Anexo Estadístico",
     "pulsaciones": 13,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 4, Tercer Informe de Gobierno",
     "pulsaciones": 14,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Informe",
     "pulsaciones": 15,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Anexo Estadístico",
     "pulsaciones": 16,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 4, Segundo Informe de Gobierno",
     "pulsaciones": 17,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Informe",
     "pulsaciones": 18,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Anexo Estadístico",
     "pulsaciones": 19,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 4, Primer Informe de Gobierno",
     "pulsaciones": 20,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Informe",
     "pulsaciones": 21,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Descargar Anexo Estadístico",
     "pulsaciones": 22,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 4, Plan Estatal de Desarrollo 2022-2027",
     "pulsaciones": 23,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTA EL PLAN ESTATAL DE DESARROLLO",
     "pulsaciones": 24,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 6, LICITACIÓN PÚBLICA FINANCIAMIENTO No. GES-SAF-SSPIF-01/2026",
     "pulsaciones": 25,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR SITIO OFICIAL",
     "pulsaciones": 26,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 6, LICITACIÓN PÚBLICA FINANCIAMIENTO No. GES-SAF-SSPIF-02/2026",
     "pulsaciones": 27,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR SITIO OFICIAL",
     "pulsaciones": 28,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 6, LICITACIÓN PÚBLICA FINANCIAMIENTO No. GES-SAF-SSPIF-03/2026",
     "pulsaciones": 29,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR SITIO OFICIAL",
     "pulsaciones": 30,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 6, Convocatoria para ocupar la Titularidad de la Comisión Estatal de Búsqueda de Personas en el Estado de Sinaloa.",
     "pulsaciones": 31,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR LA CONVOCATORIA",
     "pulsaciones": 32,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR PROPUESTA Y PERFIL DE IDONEIDAD",
     "pulsaciones": 33,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR CANDIDATOS REGISTRADOS",
     "pulsaciones": 34,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR NOMBRAMIENTO",
     "pulsaciones": 35,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 6, Convocatoria a los medianos productores de maíz blanco.",
     "pulsaciones": 36,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, CONSULTAR LA CONVOCATORIA",
     "pulsaciones": 37,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, SERVICIOS Y TRÁMITES MÁS BUSCADOS",
     "pulsaciones": 38,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Acta de<br> Nacimiento",
     "pulsaciones": 39,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Acta de Nacimiento",
     "pulsaciones": 40,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Renovación de Licencia de Conducir",
     "pulsaciones": 41,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Renovación de Licencia de Conducir",
     "pulsaciones": 42,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Tenencia y calcomanía particular",
     "pulsaciones": 43,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Tenencia y calcomanía particular",
     "pulsaciones": 44,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Carta de no antecedentes penales",
     "pulsaciones": 45,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Carta de no antecedentes penales",
     "pulsaciones": 46,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Declaración de Nómina Empresarial",
     "pulsaciones": 47,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Declaración de Nómina Empresarial",
     "pulsaciones": 48,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Facturación Electrónica",
     "pulsaciones": 49,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Facturación Electrónica",
     "pulsaciones": 50,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Periódico Oficial De Sinaloa",
     "pulsaciones": 51,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Denuncia Ciudadana",
     "pulsaciones": 52,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Transparencia",
     "pulsaciones": 53,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "En cumplimiento a la Ley de Transparencia y Acceso a la Información Pública del Estado de Sinaloa, la información pública del Poder Ejecutivo del Estado de Sinaloa, se encuentra vigente y disponible en la Plataforma Nacional de Transparencia:",
     "pulsaciones": 54,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, https://plataformadetransparencia.org.mx",
     "pulsaciones": 55,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Todas las páginas de gobierno del estado que suministran información o brindan servicio a la ciudadanía siguen activas y en total operación para bien de las y los sinaloenses.",
     "pulsaciones": 56,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Al igual puedes ingresar al Portal Estatal de Transparencia Estatal en:",
     "pulsaciones": 57,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, https://transparencia.sinaloa.gob.mx/",
     "pulsaciones": 58,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Portal de Transparencia de Sinaloa",
     "pulsaciones": 59,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Plataforma Nacional de Transparencia",
     "pulsaciones": 60,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, GABINETE EJECUTIVO",
     "pulsaciones": 61,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Lic. Graciela Domínguez Nava",
     "pulsaciones": 62,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Gobernadora del Estado de Sinaloa",
     "pulsaciones": 63,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, César Julio Saucedo Barrón",
     "pulsaciones": 64,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría General de Gobierno",
     "pulsaciones": 65,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Wilfredo Véliz Figueroa",
     "pulsaciones": 66,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Administración y Finanzas",
     "pulsaciones": 67,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Ismael Bello Esquivel",
     "pulsaciones": 68,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Agricultura y Ganadería",
     "pulsaciones": 69,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Francisco Javier Barrón Aguayo",
     "pulsaciones": 70,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Bienestar y Desarrollo Sustentable",
     "pulsaciones": 71,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Diego Armando Aguerrebere Espitia",
     "pulsaciones": 72,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Economía",
     "pulsaciones": 73,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Gloria Himelda Félix Niebla",
     "pulsaciones": 74,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Educación Pública y Cultura",
     "pulsaciones": 75,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Brenda García Félix",
     "pulsaciones": 76,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de las Mujeres",
     "pulsaciones": 77,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, José Manuel Acosta Bernal",
     "pulsaciones": 78,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Obras Públicas",
     "pulsaciones": 79,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Lic. Flor Emilia Guerra Mena",
     "pulsaciones": 80,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Pesca y Acuacultura",
     "pulsaciones": 81,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Dr. Cuitláhuac González Galindo",
     "pulsaciones": 82,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Salud",
     "pulsaciones": 83,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, General Brigadier de Estado Mayor Sinuhé Téllez López",
     "pulsaciones": 84,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Seguridad Pública",
     "pulsaciones": 85,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Sandra Guadalupe Angulo Cázarez",
     "pulsaciones": 86,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Transparencia y Rendición de Cuentas",
     "pulsaciones": 87,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Mireya Sosa Osuna",
     "pulsaciones": 88,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Secretaría de Turismo",
     "pulsaciones": 89,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Mtro. José Isabel Ibarra Valdivia",
     "pulsaciones": 90,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Coordinación de Asesores",
     "pulsaciones": 91,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Maraly Franco Salinas",
     "pulsaciones": 92,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Coordinación de Comunicación Social",
     "pulsaciones": 93,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Dr. Rodolfo Monreal Ávila",
     "pulsaciones": 94,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Coordinación General de Desarrollo Tecnológico y Proyectos Especiales",
     "pulsaciones": 95,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, ÚLTIMAS NOTICIAS",
     "pulsaciones": 96,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace",
     "pulsaciones": 97,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "NOTICIAS",
     "pulsaciones": 98,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, PALACIO DE GOBIERNO SE ILUMINA DE AZUL POR EL DÍA MUNDIAL DE LA DIABETES",
     "pulsaciones": 99,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "En el marco del Día Mundial de la Diabetes, con el lema “Acción temprana contra la diabetes” Palacio de Gobierno se ilumina de color azul",
     "pulsaciones": 100,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Read more about PALACIO DE GOBIERNO SE ILUMINA DE AZUL POR EL DÍA MUNDIAL DE LA DIABETES",
     "pulsaciones": 101,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Noviembre 13, 2026",
     "pulsaciones": 102,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace",
     "pulsaciones": 103,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "NOTICIAS",
     "pulsaciones": 104,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, La confianza de la sociedad en sus gobiernos construye seguridad y bienestar, afirma Gobernadora Graciela Domínguez",
     "pulsaciones": 105,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "*La mandataria estatal acudió a la presentación del Segundo Informe de labores de la diputada local Moncerrat López López del Partido del Trabajo. Culiacán, Sinaloa",
     "pulsaciones": 106,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Read more about La confianza de la sociedad en sus gobiernos construye seguridad y bienestar, afirma Gobernadora Graciela Domínguez",
     "pulsaciones": 107,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Noviembre 13, 2026",
     "pulsaciones": 108,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace",
     "pulsaciones": 109,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "NOTICIAS",
     "pulsaciones": 110,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Avanza en Mazatlán proyecto de vivienda para familias desplazadas; 56 lotes podrían estarán listos en unos meses",
     "pulsaciones": 111,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Mazatlán, Sinaloa, a 13 de noviembre de 2026.– Como parte de las acciones emprendidas por el Gobierno de Sinaloa, para atender las necesidades de las",
     "pulsaciones": 112,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Read more about Avanza en Mazatlán proyecto de vivienda para familias desplazadas; 56 lotes podrían estarán listos en unos meses",
     "pulsaciones": 113,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Noviembre 13, 2026",
     "pulsaciones": 114,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Ver Todas",
     "pulsaciones": 115,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace",
     "pulsaciones": 116,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Es el portal único de trámites, información y participación ciudadana para el Gobierno del Estado de Sinaloa.",
     "pulsaciones": 117,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Facebook",
     "pulsaciones": 118,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Twitter",
     "pulsaciones": 119,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Instagram",
     "pulsaciones": 120,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Youtube",
     "pulsaciones": 121,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "Ave. Insurgentes S/N Col. Centro Sinaloa, Culiacán, Sinaloa C.P. 80000",
     "pulsaciones": 122,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    },
    {
     "tecla": "leer",
     "anuncio": "desktop",
     "pulsaciones": 123,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/"
    }
   ],
   "encontro": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 15,
     "tipo": "umbral",
     "texto": "Aquí pasa de 15 pulsaciones (umbral)"
    },
    {
     "paso": 122,
     "tipo": "detenido",
     "texto": "Aquí se detuvo sin encontrar el objetivo correcto"
    }
   ]
  }
 ],
 "prueba": [
  {
   "tarea": "A",
   "entrada": "perfecta.html",
   "tramite": null,
   "objetivo_correcto": "667 555 0142",
   "pagina_axe": "perfecta.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 7,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×6, leer×1",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Contacto",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Teléfono: 667 555 0142",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    }
   ],
   "encontro": "Teléfono: 667 555 0142",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 6,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "perfecta",
   "url_base": null,
   "fecha": "2026-11-13T22:41:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 7,
    "estrategia": "H_a_seccion",
    "razon": "H seis veces llega al h2 'Contacto' y el teléfono es la siguiente parada: 6 + 1 = 7."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "perfecta.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "perfecta.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 9,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×3, leer×6",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 8,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "perfecta",
   "url_base": null,
   "fecha": "2026-11-13T22:41:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 9,
    "estrategia": "H_a_seccion",
    "razon": "H cuatro veces llega al h3 del trámite; luego 5 paradas (párrafo + 4 requisitos): 4 + 5 = 9."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "perfecta.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal.pdf",
   "pagina_axe": "perfecta.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "enlace_por_nombre",
   "friccion": 5,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "lista_enlaces×1, flecha_lista×3, Enter×1",
   "pasos": [
    {
     "tecla": "lista_enlaces",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal.pdf",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
      "es_pdf": true,
      "capa_texto": true
     },
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 4,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "perfecta",
   "url_base": null,
   "fecha": "2026-11-13T22:41:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 5,
    "estrategia": "enlace_por_nombre",
    "razon": "En la lista de enlaces el PDF es el 4.º (tras los 3 del menú): 1 + 3 + Enter = 5. Por H costaría 7. El PDF tiene texto."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "perfecta.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Correo electrónico|Mensaje",
   "pagina_axe": "perfecta.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Correo electrónico",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Mensaje",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/perfecta.html"
    }
   ],
   "encontro": "Nombre completo, Correo electrónico, Mensaje",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "perfecta",
   "url_base": null,
   "fecha": "2026-11-13T22:41:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "F recorre los 3 campos y cada uno se anuncia con su etiqueta: 3. No se envía nada."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "A",
   "entrada": "sin_encabezados.html",
   "tramite": null,
   "objetivo_correcto": "667 555 0142",
   "pagina_axe": "sin_encabezados.html",
   "estado": "con_dificultad",
   "tipo_falla": null,
   "estrategia": "no_dirigida",
   "friccion": 35,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "con_dificultad",
    "15": "con_dificultad",
    "25": "con_dificultad"
   },
   "trayectoria": "leer×35",
   "pasos": [
    {
     "tecla": "leer",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Noticias",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Lo más reciente del Ayuntamiento.",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Inicia campaña de reforestación en parques",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "12 de septiembre de 2026",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se plantarán 500 árboles en colonias del municipio.",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Rehabilitan alumbrado en el centro",
     "pulsaciones": 10,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "10 de septiembre de 2026",
     "pulsaciones": 11,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se cambiaron 120 luminarias por tecnología LED.",
     "pulsaciones": 12,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Festival cultural de otoño",
     "pulsaciones": 13,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "5 de septiembre de 2026",
     "pulsaciones": 14,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Música, danza y teatro gratuitos en la plaza principal.",
     "pulsaciones": 15,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Jornada de vacunación para mascotas",
     "pulsaciones": 16,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "1 de septiembre de 2026",
     "pulsaciones": 17,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Aplicación gratuita de vacuna antirrábica.",
     "pulsaciones": 18,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Mantenimiento a la red de agua potable",
     "pulsaciones": 19,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "28 de agosto de 2026",
     "pulsaciones": 20,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trabajos en tuberías de tres colonias.",
     "pulsaciones": 21,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Torneo municipal de futbol infantil",
     "pulsaciones": 22,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "25 de agosto de 2026",
     "pulsaciones": 23,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Participan niñas y niños de 8 a 12 años.",
     "pulsaciones": 24,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trámites",
     "pulsaciones": 25,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Licencia de construcción menor",
     "pulsaciones": 26,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 27,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 28,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 29,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 30,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 31,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Descargas",
     "pulsaciones": 32,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 33,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Contacto",
     "pulsaciones": 34,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Teléfono: 667 555 0142",
     "pulsaciones": 35,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    }
   ],
   "encontro": "Teléfono: 667 555 0142",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 0.9230769230769231,
    "elementos_conservador": 0.9846153846153847
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 15,
     "tipo": "umbral",
     "texto": "Aquí pasa de 15 pulsaciones (umbral)"
    },
    {
     "paso": 34,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_encabezados",
   "url_base": null,
   "fecha": "2026-11-13T22:41:46-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "con_dificultad",
    "tipo_falla": null,
    "friccion": 35,
    "estrategia": "no_dirigida",
    "razon": "No hay encabezado, landmark ni enlace que lleve a 'Contacto'; solo se llega leyendo desde el inicio: 1 + 3 + 20 + 7 + 2 + 2 = 35 paradas (> 25)."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "sin_encabezados.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "sin_encabezados.html",
   "estado": "con_dificultad",
   "tipo_falla": null,
   "estrategia": "no_dirigida",
   "friccion": 32,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "con_dificultad",
    "15": "con_dificultad",
    "25": "con_dificultad"
   },
   "trayectoria": "leer×32",
   "pasos": [
    {
     "tecla": "leer",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Noticias",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Lo más reciente del Ayuntamiento.",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Inicia campaña de reforestación en parques",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "12 de septiembre de 2026",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se plantarán 500 árboles en colonias del municipio.",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Rehabilitan alumbrado en el centro",
     "pulsaciones": 10,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "10 de septiembre de 2026",
     "pulsaciones": 11,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se cambiaron 120 luminarias por tecnología LED.",
     "pulsaciones": 12,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Festival cultural de otoño",
     "pulsaciones": 13,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "5 de septiembre de 2026",
     "pulsaciones": 14,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Música, danza y teatro gratuitos en la plaza principal.",
     "pulsaciones": 15,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Jornada de vacunación para mascotas",
     "pulsaciones": 16,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "1 de septiembre de 2026",
     "pulsaciones": 17,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Aplicación gratuita de vacuna antirrábica.",
     "pulsaciones": 18,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Mantenimiento a la red de agua potable",
     "pulsaciones": 19,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "28 de agosto de 2026",
     "pulsaciones": 20,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trabajos en tuberías de tres colonias.",
     "pulsaciones": 21,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Torneo municipal de futbol infantil",
     "pulsaciones": 22,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "25 de agosto de 2026",
     "pulsaciones": 23,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Participan niñas y niños de 8 a 12 años.",
     "pulsaciones": 24,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trámites",
     "pulsaciones": 25,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Licencia de construcción menor",
     "pulsaciones": 26,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 27,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 28,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 29,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 30,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 31,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Descargas",
     "pulsaciones": 32,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno, Descargas",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 0.9230769230769231,
    "elementos_conservador": 0.9846153846153847
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 15,
     "tipo": "umbral",
     "texto": "Aquí pasa de 15 pulsaciones (umbral)"
    },
    {
     "paso": 31,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_encabezados",
   "url_base": null,
   "fecha": "2026-11-13T22:41:46-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "con_dificultad",
    "tipo_falla": null,
    "friccion": 32,
    "estrategia": "no_dirigida",
    "razon": "Los requisitos son divs sueltos sin encabezado ni lista; leyendo desde el inicio: 1 + 3 + 20 + 7 = 31 paradas hasta 'Croquis del terreno', + 1 = 32 (> 25): 'Descargas' también es texto suelto, sin marca que cierre el bloque; el siguiente rol distinto de texto es el enlace al PDF. Corregido el 5-nov: el 31 suponía comprensión semántica de 'Descargas'."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "sin_encabezados.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal.pdf",
   "pagina_axe": "sin_encabezados.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "enlace_por_nombre",
   "friccion": 5,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "lista_enlaces×1, flecha_lista×3, Enter×1",
   "pasos": [
    {
     "tecla": "lista_enlaces",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal.pdf",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
      "es_pdf": true,
      "capa_texto": true
     },
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 0.9230769230769231,
    "elementos_conservador": 0.9846153846153847
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 4,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_encabezados",
   "url_base": null,
   "fecha": "2026-11-13T22:41:46-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 5,
    "estrategia": "enlace_por_nombre",
    "razon": "El enlace conserva su nombre; no depende de encabezados: 1 + 3 + 1 = 5."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "sin_encabezados.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Correo electrónico|Mensaje",
   "pagina_axe": "sin_encabezados.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Correo electrónico",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Mensaje",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_encabezados.html"
    }
   ],
   "encontro": "Nombre completo, Correo electrónico, Mensaje",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 0.9230769230769231,
    "elementos_conservador": 0.9846153846153847
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_encabezados",
   "url_base": null,
   "fecha": "2026-11-13T22:41:46-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "Los campos tienen etiqueta y F no depende de encabezados: 3."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "A",
   "entrada": "sin_contacto.html",
   "tramite": null,
   "objetivo_correcto": "NO_EXISTE",
   "pagina_axe": "sin_contacto.html",
   "estado": "no_completable",
   "tipo_falla": "no_encontrado",
   "estrategia": "no_dirigida",
   "friccion": null,
   "consumidas": 42,
   "motivo": "ninguna estrategia encontró el objetivo",
   "sensibilidad": {
    "10": "no_completable",
    "15": "no_completable",
    "25": "no_completable"
   },
   "trayectoria": "leer×42",
   "pasos": [
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Lo más reciente del Ayuntamiento.",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Inicia campaña de reforestación en parques",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "12 de septiembre de 2026",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se plantarán 500 árboles en colonias del municipio.",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Rehabilitan alumbrado en el centro",
     "pulsaciones": 10,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "10 de septiembre de 2026",
     "pulsaciones": 11,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Se cambiaron 120 luminarias por tecnología LED.",
     "pulsaciones": 12,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Festival cultural de otoño",
     "pulsaciones": 13,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "5 de septiembre de 2026",
     "pulsaciones": 14,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Música, danza y teatro gratuitos en la plaza principal.",
     "pulsaciones": 15,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Jornada de vacunación para mascotas",
     "pulsaciones": 16,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "1 de septiembre de 2026",
     "pulsaciones": 17,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Aplicación gratuita de vacuna antirrábica.",
     "pulsaciones": 18,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Mantenimiento a la red de agua potable",
     "pulsaciones": 19,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "28 de agosto de 2026",
     "pulsaciones": 20,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trabajos en tuberías de tres colonias.",
     "pulsaciones": 21,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Torneo municipal de futbol infantil",
     "pulsaciones": 22,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "25 de agosto de 2026",
     "pulsaciones": 23,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Participan niñas y niños de 8 a 12 años.",
     "pulsaciones": 24,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 25,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 26,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 27,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 28,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 29,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 30,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 31,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 32,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 33,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Solicitud de cita",
     "pulsaciones": 34,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Nombre completo",
     "pulsaciones": 35,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 36,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Trámite",
     "pulsaciones": 37,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "cuadro combinado, Trámite",
     "pulsaciones": 38,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Fecha preferida",
     "pulsaciones": 39,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "edición, Fecha preferida",
     "pulsaciones": 40,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "botón, Solicitar cita",
     "pulsaciones": 41,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Ayuntamiento de Villa Ejemplo. Sitio ficticio para pruebas.",
     "pulsaciones": 42,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    }
   ],
   "encontro": null,
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 15,
     "tipo": "umbral",
     "texto": "Aquí pasa de 15 pulsaciones (umbral)"
    },
    {
     "paso": 41,
     "tipo": "detenido",
     "texto": "Aquí se detuvo sin encontrar el objetivo correcto"
    }
   ],
   "sitio": "sin_contacto",
   "url_base": null,
   "fecha": "2026-11-13T22:41:56-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "no_completable",
    "tipo_falla": "no_encontrado",
    "friccion": 42,
    "estrategia": "no_dirigida",
    "razon": "No hay teléfono, correo ni enlace de contacto. La fricción (42) es lo que cuesta leer la página completa para comprobar que no existe."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "sin_contacto.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "sin_contacto.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 9,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×3, leer×6",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 8,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_contacto",
   "url_base": null,
   "fecha": "2026-11-13T22:41:56-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 9,
    "estrategia": "H_a_seccion",
    "razon": "Igual que perfecta.html: 4 + 5 = 9."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "sin_contacto.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal.pdf",
   "pagina_axe": "sin_contacto.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "enlace_por_nombre",
   "friccion": 5,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "lista_enlaces×1, flecha_lista×3, Enter×1",
   "pasos": [
    {
     "tecla": "lista_enlaces",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal.pdf",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
      "es_pdf": true,
      "capa_texto": true
     },
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 4,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_contacto",
   "url_base": null,
   "fecha": "2026-11-13T22:41:56-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 5,
    "estrategia": "enlace_por_nombre",
    "razon": "Igual que perfecta.html: 1 + 3 + 1 = 5."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "sin_contacto.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Trámite|Fecha preferida",
   "pagina_axe": "sin_contacto.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "F",
     "anuncio": "cuadro combinado, Trámite",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Fecha preferida",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/sin_contacto.html"
    }
   ],
   "encontro": "Nombre completo, Trámite, Fecha preferida",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "sin_contacto",
   "url_base": null,
   "fecha": "2026-11-13T22:41:56-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "Formulario de solicitud de cita (no de contacto) con campos etiquetados: 3. No se envía."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "A",
   "entrada": "enlaces_ambiguos.html",
   "tramite": null,
   "objetivo_correcto": "667 555 0142",
   "pagina_axe": "enlaces_ambiguos.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 6,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×5, leer×1",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Contacto",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Teléfono: 667 555 0142",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    }
   ],
   "encontro": "Teléfono: 667 555 0142",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.9473684210526315,
    "elementos": 0.9788732394366197,
    "reglas_conservador": 0.9473684210526315,
    "elementos_conservador": 0.9788732394366197
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 5,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "enlaces_ambiguos",
   "url_base": null,
   "fecha": "2026-11-13T22:42:14-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 6,
    "estrategia": "H_a_seccion",
    "razon": "Contacto es el 5.º encabezado: 5 + 1 = 6."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "enlaces_ambiguos.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "enlaces_ambiguos.html",
   "estado": "con_dificultad",
   "tipo_falla": null,
   "estrategia": "probar_enlaces",
   "friccion": 35,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "con_dificultad",
    "15": "con_dificultad",
    "25": "con_dificultad"
   },
   "trayectoria": "H×3, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, volver×1, K×1, Enter×1, H×1, leer×5",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 5,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, clic aquí",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 8,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 10,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 11,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 12,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, clic aquí",
     "pulsaciones": 13,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 14,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 15,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 16,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 17,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 18,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 19,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 20,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 21,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 22,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 23,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 24,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, clic aquí",
     "pulsaciones": 25,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Otro trámite - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 26,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_otro.html"
    },
    {
     "tecla": "volver",
     "anuncio": "Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 27,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "K",
     "anuncio": "enlace, Leer más",
     "pulsaciones": 28,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "Licencia de construcción menor - Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 29,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Licencia de construcción menor",
     "pulsaciones": 30,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 2, Requisitos",
     "pulsaciones": 31,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 32,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 33,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 34,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 35,
     "profundidad": 1,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos_tramite.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.9473684210526315,
    "elementos": 0.9788732394366197,
    "reglas_conservador": 0.9473684210526315,
    "elementos_conservador": 0.9788732394366197
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 15,
     "tipo": "umbral",
     "texto": "Aquí pasa de 15 pulsaciones (umbral)"
    },
    {
     "paso": 34,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "enlaces_ambiguos",
   "url_base": null,
   "fecha": "2026-11-13T22:42:14-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "con_dificultad",
    "tipo_falla": null,
    "friccion": 35,
    "estrategia": "probar_enlaces",
    "razon": "Los 12 enlaces de tarjeta se anuncian solo como 'Leer más' o 'clic aquí': no se distinguen por nombre y los títulos no son encabezados. La mejor estrategia: H a 'Trámites' (3) y probar los enlaces en orden. Cada intento fallido cuesta K + Enter + volver (3) y llega a 'Otro trámite'; el correcto es el 9.º: 8×3 + 2 = 26. En la página del trámite, H a 'Requisitos' (2) y leer 4: total 3 + 26 + 2 + 4 = 35 (> 25). Leer las tarjetas de corrido sería peor: 3 + 27 + 1 + 6 = 37."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "enlaces_ambiguos.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal.pdf",
   "pagina_axe": "enlaces_ambiguos.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 6,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×4, leer×1, Enter×1",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "leer",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal.pdf",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
      "es_pdf": true,
      "capa_texto": true
     },
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.9473684210526315,
    "elementos": 0.9788732394366197,
    "reglas_conservador": 0.9473684210526315,
    "elementos_conservador": 0.9788732394366197
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 5,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "enlaces_ambiguos",
   "url_base": null,
   "fecha": "2026-11-13T22:42:14-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 6,
    "estrategia": "H_a_seccion",
    "razon": "Por la lista de enlaces el PDF es el 16.º (1 + 15 + 1 = 17); por H a 'Descargas' es mejor: 4 + 1 + 1 = 6."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "enlaces_ambiguos.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Correo electrónico|Mensaje",
   "pagina_axe": "enlaces_ambiguos.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Correo electrónico",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Mensaje",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/enlaces_ambiguos.html"
    }
   ],
   "encontro": "Nombre completo, Correo electrónico, Mensaje",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.9473684210526315,
    "elementos": 0.9788732394366197,
    "reglas_conservador": 0.9473684210526315,
    "elementos_conservador": 0.9788732394366197
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "enlaces_ambiguos",
   "url_base": null,
   "fecha": "2026-11-13T22:42:14-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "Formulario con etiquetas: 3."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "A",
   "entrada": "formulario_sin_etiquetas.html",
   "tramite": null,
   "objetivo_correcto": "667 555 0142",
   "pagina_axe": "formulario_sin_etiquetas.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 7,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×6, leer×1",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Contacto",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Teléfono: 667 555 0142",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    }
   ],
   "encontro": "Teléfono: 667 555 0142",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.95,
    "elementos": 0.96875,
    "reglas_conservador": 0.95,
    "elementos_conservador": 0.96875
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 6,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "formulario_sin_etiquetas",
   "url_base": null,
   "fecha": "2026-11-13T22:42:24-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 7,
    "estrategia": "H_a_seccion",
    "razon": "Igual que perfecta.html: 6 + 1 = 7."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "formulario_sin_etiquetas.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "formulario_sin_etiquetas.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 9,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×3, leer×6",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.95,
    "elementos": 0.96875,
    "reglas_conservador": 0.95,
    "elementos_conservador": 0.96875
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 8,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "formulario_sin_etiquetas",
   "url_base": null,
   "fecha": "2026-11-13T22:42:24-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 9,
    "estrategia": "H_a_seccion",
    "razon": "Igual que perfecta.html: 4 + 5 = 9."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "formulario_sin_etiquetas.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal.pdf",
   "pagina_axe": "formulario_sin_etiquetas.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "enlace_por_nombre",
   "friccion": 5,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "lista_enlaces×1, flecha_lista×3, Enter×1",
   "pasos": [
    {
     "tecla": "lista_enlaces",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal.pdf",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
      "es_pdf": true,
      "capa_texto": true
     },
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.95,
    "elementos": 0.96875,
    "reglas_conservador": 0.95,
    "elementos_conservador": 0.96875
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 4,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "formulario_sin_etiquetas",
   "url_base": null,
   "fecha": "2026-11-13T22:42:24-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 5,
    "estrategia": "enlace_por_nombre",
    "razon": "Igual que perfecta.html: 1 + 3 + 1 = 5."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "formulario_sin_etiquetas.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Correo electrónico|Mensaje",
   "pagina_axe": "formulario_sin_etiquetas.html",
   "estado": "no_completable",
   "tipo_falla": "no_identificable",
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": "se llega a los campos, pero alguno se anuncia sin nombre",
   "sensibilidad": {
    "10": "no_completable",
    "15": "no_completable",
    "25": "no_completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/formulario_sin_etiquetas.html"
    }
   ],
   "encontro": ", , ",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 0.95,
    "elementos": 0.96875,
    "reglas_conservador": 0.95,
    "elementos_conservador": 0.96875
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "detenido",
     "texto": "Llegó a los campos, pero alguno no tiene nombre"
    }
   ],
   "sitio": "formulario_sin_etiquetas",
   "url_base": null,
   "fecha": "2026-11-13T22:42:24-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "no_completable",
    "tipo_falla": "no_identificable",
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "F llega a los 3 campos (3 pulsaciones), pero se anuncian sin nombre (sin label, placeholder, title ni aria-label): no se puede identificar qué pide cada uno."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "A",
   "entrada": "pdf_escaneado.html",
   "tramite": null,
   "objetivo_correcto": "667 555 0142",
   "pagina_axe": "pdf_escaneado.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 7,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×6, leer×1",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Descargas",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Contacto",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Teléfono: 667 555 0142",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    }
   ],
   "encontro": "Teléfono: 667 555 0142",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 6,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "pdf_escaneado",
   "url_base": null,
   "fecha": "2026-11-13T22:42:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 7,
    "estrategia": "H_a_seccion",
    "razon": "Igual que perfecta.html: 6 + 1 = 7."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "B",
   "entrada": "pdf_escaneado.html",
   "tramite": "Licencia de construcción",
   "objetivo_correcto": "Identificación oficial vigente|Comprobante de domicilio|Comprobante de pago del predial|Croquis del terreno",
   "pagina_axe": "pdf_escaneado.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "H_a_seccion",
   "friccion": 9,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "H×3, leer×6",
   "pasos": [
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 1, Ayuntamiento de Villa Ejemplo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Noticias",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "H",
     "anuncio": "encabezado nivel 2, Trámites",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "encabezado nivel 3, Licencia de construcción menor",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Requisitos para tramitar la licencia:",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Identificación oficial vigente",
     "pulsaciones": 6,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de domicilio",
     "pulsaciones": 7,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Comprobante de pago del predial",
     "pulsaciones": 8,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "leer",
     "anuncio": "Croquis del terreno",
     "pulsaciones": 9,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    }
   ],
   "encontro": "Identificación oficial vigente, Comprobante de domicilio, Comprobante de pago del predial, Croquis del terreno",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 8,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "pdf_escaneado",
   "url_base": null,
   "fecha": "2026-11-13T22:42:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 9,
    "estrategia": "H_a_seccion",
    "razon": "Igual que perfecta.html: 4 + 5 = 9."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "C",
   "entrada": "pdf_escaneado.html",
   "tramite": null,
   "objetivo_correcto": "docs/plan_municipal_escaneado.pdf",
   "pagina_axe": "pdf_escaneado.html",
   "estado": "no_completable",
   "tipo_falla": "cierre_roto",
   "estrategia": "enlace_por_nombre",
   "friccion": 5,
   "consumidas": null,
   "motivo": "PDF sin capa de texto: el lector no tiene nada que leer",
   "sensibilidad": {
    "10": "no_completable",
    "15": "no_completable",
    "25": "no_completable"
   },
   "trayectoria": "lista_enlaces×1, flecha_lista×3, Enter×1",
   "pasos": [
    {
     "tecla": "lista_enlaces",
     "anuncio": "enlace, Inicio",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Gobierno",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Transparencia",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "flecha_lista",
     "anuncio": "enlace, Plan Municipal de Desarrollo (PDF)",
     "pulsaciones": 4,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "Enter",
     "anuncio": "documento descargado: plan_municipal_escaneado.pdf",
     "pulsaciones": 5,
     "profundidad": 0,
     "se_movio": false,
     "landmark": null,
     "documento": {
      "url": "http://127.0.0.1:55691/docs/plan_municipal_escaneado.pdf",
      "es_pdf": true,
      "capa_texto": false
     },
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    }
   ],
   "encontro": "http://127.0.0.1:55691/docs/plan_municipal_escaneado.pdf",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 4,
     "tipo": "detenido",
     "texto": "Llegó al documento, pero no se puede leer"
    }
   ],
   "sitio": "pdf_escaneado",
   "url_base": null,
   "fecha": "2026-11-13T22:42:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "no_completable",
    "tipo_falla": "cierre_roto",
    "friccion": 5,
    "estrategia": "enlace_por_nombre",
    "razon": "Se llega con 5 pulsaciones, pero el PDF es solo una imagen escaneada: el lector no tiene nada que leer; el cierre está roto."
   },
   "coincide_esperado": true
  },
  {
   "tarea": "D",
   "entrada": "pdf_escaneado.html",
   "tramite": null,
   "objetivo_correcto": "Nombre completo|Correo electrónico|Mensaje",
   "pagina_axe": "pdf_escaneado.html",
   "estado": "completable",
   "tipo_falla": null,
   "estrategia": "F_a_campos",
   "friccion": 3,
   "consumidas": null,
   "motivo": null,
   "sensibilidad": {
    "10": "completable",
    "15": "completable",
    "25": "completable"
   },
   "trayectoria": "F×3",
   "pasos": [
    {
     "tecla": "F",
     "anuncio": "edición, Nombre completo",
     "pulsaciones": 1,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Correo electrónico",
     "pulsaciones": 2,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    },
    {
     "tecla": "F",
     "anuncio": "edición, Mensaje",
     "pulsaciones": 3,
     "profundidad": 0,
     "se_movio": true,
     "landmark": null,
     "documento": null,
     "no_evaluable": null,
     "pagina": "/pdf_escaneado.html"
    }
   ],
   "encontro": "Nombre completo, Correo electrónico, Mensaje",
   "falsas_llegadas": [],
   "captcha": [],
   "puntajes": {
    "reglas": 1.0,
    "elementos": 1.0,
    "reglas_conservador": 1.0,
    "elementos_conservador": 1.0
   },
   "veredicto_nvda": null,
   "vidente_lo_encuentra": null,
   "ciego": false,
   "marcas": [
    {
     "paso": 2,
     "tipo": "llego",
     "texto": "Llegó al objetivo correcto"
    }
   ],
   "sitio": "pdf_escaneado",
   "url_base": null,
   "fecha": "2026-11-13T22:42:35-07:00",
   "corrida": "corrida del 2026-11-13",
   "esperado": {
    "estado": "completable",
    "tipo_falla": null,
    "friccion": 3,
    "estrategia": "F_a_campos",
    "razon": "Igual que perfecta.html: 3."
   },
   "coincide_esperado": true
  }
 ],
 "analisis": {
  "matriz": {
   "clases": [
    "completable",
    "con_dificultad",
    "no_completable"
   ],
   "matriz": {
    "completable": {
     "completable": 0,
     "con_dificultad": 0,
     "no_completable": 0
    },
    "con_dificultad": {
     "completable": 0,
     "con_dificultad": 0,
     "no_completable": 1
    },
    "no_completable": {
     "completable": 0,
     "con_dificultad": 0,
     "no_completable": 1
    }
   },
   "n": 2,
   "excluidas": {
    "sin_nvda": 0,
    "no_evaluable_nvda": 0,
    "no_evaluable_atorapp": 1
   }
  },
  "acuerdo": {
   "n": 2,
   "tres_clases": 0.5,
   "binario": 0.5
  },
  "acuerdo_por_umbral": {
   "10": {
    "n": 2,
    "iguales": 1
   },
   "15": {
    "n": 2,
    "iguales": 1
   },
   "25": {
    "n": 2,
    "iguales": 1
   }
  },
  "falsas_llegadas": {
   "tareas_con_falsa": 0,
   "n_tareas": 3,
   "por_sitio": {
    "ahome": 0,
    "ciudadano": 0,
    "sinaloa": 0
   }
  },
  "auc": {
   "calculado": false,
   "motivo": "hay 2 tareas comparables (de 3 tareas en 3 sitios); con menos de 10 el AUC no es interpretable: solo puede tomar unos cuantos valores (con 1 tarea de cada clase, 0 o 1) y no dice nada de axe"
  }
 },
 "notas_nvda": [
  {
   "sitio": "ahome",
   "tarea": "A",
   "ruta_nvda": "Primer intento ~30 pulsaciones, ruta directa ~35 (H, D, K y Enter hasta Contacto). Conteo manual aproximado; auditor principiante.",
   "pulsaciones_aprox": "35",
   "que_me_atoro": "Se encuentra el contacto, pero cuesta mas de 15 pulsaciones.",
   "fecha_auditoria": "2026-11-08"
  },
  {
   "sitio": "sinaloa",
   "tarea": "A",
   "ruta_nvda": "H, D y K en la portada (5 a 10 min). Conteo manual aproximado; auditor principiante.",
   "pulsaciones_aprox": "",
   "que_me_atoro": "En la portada solo hay redes sociales y enlaces a otros portales (no abiertos). Sin telefono ni correo del portal. Se mide por host exacto.",
   "fecha_auditoria": "2026-11-08"
  },
  {
   "sitio": "ciudadano",
   "tarea": "B",
   "ruta_nvda": "Flechas cuadro por cuadro hasta Acta de nacimiento, Enter, flechas hasta Requisitos. Conteo manual aproximado; auditor principiante.",
   "pulsaciones_aprox": "20",
   "que_me_atoro": "Los tramites se leen como texto uno por uno con flechas; se activan con Enter. Llegar a los requisitos cuesta ~20 pulsaciones. Los requisitos se muestran sin cambiar la URL (posible ventana emergente o app de una sola pagina).",
   "fecha_auditoria": "2026-11-08"
  }
 ]
};
