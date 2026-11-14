/* Atorapp — interfaz de resultados (Fase 3E). Sin bibliotecas ni red: los datos vienen de datos.js
   (window.ATORAPP), generado por scripts/generar_datos_interfaz.py. Lo que no está en los datos se
   muestra como "pendiente" o "no medido": aquí no se calcula ningún veredicto. */
(function () {
  "use strict";

  var D = window.ATORAPP;
  var vista = document.getElementById("vista");

  // ---------- Vocabulario ----------

  var TAREAS = {
    A: "Contacto",
    B: "Requisitos de un trámite",
    C: "Abrir un documento descargable",
    D: "Llegar a un formulario e identificar sus campos"
  };
  var ESTADOS = {
    completable: "Completable",
    con_dificultad: "Con dificultad",
    no_completable: "No completable",
    no_evaluable: "No evaluable"
  };
  var FALLAS = {
    no_encontrado: "no se encontró el objetivo",
    no_identificable: "no se puede identificar el objetivo",
    cierre_roto: "el cierre no funciona"
  };
  var ESTRATEGIAS = {
    H_a_seccion: "H hasta la sección, luego leer",
    D_a_seccion: "D hasta la sección, luego leer",
    D_a_main: "D hasta el contenido principal y leer hasta el final",
    enlace_por_nombre: "Lista de enlaces, elegir por nombre",
    F_a_campos: "F a los campos del formulario",
    no_dirigida: "Leer desde el inicio",
    Tab_inicio: "Tab desde el inicio",
    probar_enlaces: "Probar en orden los enlaces ambiguos"
  };
  // [lo que se ve en la tecla, cómo se dice, qué hace]
  var TECLAS = {
    H: ["H", "H", "siguiente encabezado"],
    K: ["K", "K", "siguiente enlace"],
    D: ["D", "D", "siguiente punto de referencia"],
    F: ["F", "F", "siguiente campo de formulario"],
    Tab: ["Tab", "Tab", "siguiente elemento enfocable"],
    flecha: ["↓", "flecha abajo", "siguiente línea"],
    leer: ["↓", "flecha abajo", "leer la siguiente línea"],
    Enter: ["Enter", "Enter", "activar"],
    volver: ["Alt+←", "Alt más flecha izquierda", "volver a la página anterior"],
    lista_enlaces: ["Ins+F7", "Insert más F7", "abrir la lista de enlaces"],
    lista_encabezados: ["Ins+F7", "Insert más F7", "abrir la lista de encabezados"],
    flecha_lista: ["↓", "flecha abajo", "bajar en la lista"],
    entrada: ["—", "ninguna tecla", "cargar la página de entrada"]
  };
  var PAGINAS_PRUEBA = {
    perfecta: "Página bien construida",
    sin_encabezados: "Sin encabezados",
    sin_contacto: "Sin datos de contacto",
    enlaces_ambiguos: "Enlaces ambiguos («Ver más»)",
    formulario_sin_etiquetas: "Formulario sin etiquetas",
    pdf_escaneado: "PDF escaneado, sin texto"
  };
  var PUNTAJES = [
    ["reglas", "Reglas"],
    ["elementos", "Elementos"],
    ["reglas_conservador", "Reglas (conservador)"],
    ["elementos_conservador", "Elementos (conservador)"]
  ];
  var VELOCIDADES = { lenta: 2200, normal: 1200, rapida: 450 };

  // ---------- Iconos (decorativos: el texto siempre dice lo mismo) ----------

  var ICONOS = {
    completable: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="m7.5 12.3 3 3 6-6.3" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    con_dificultad: '<path d="M12 2.5 22.5 20.5h-21Z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M12 9v5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1.4" fill="#fff"/>',
    no_completable: '<rect x="2" y="2" width="20" height="20" rx="5" fill="currentColor"/><path d="m8 8 8 8m0-8-8 8" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
    // Rombo con guion (Fase 3F.4): forma propia, distinta del círculo de completable.
    no_evaluable: '<path d="M12 1.2 22.8 12 12 22.8 1.2 12Z" fill="currentColor"/><path d="M7.6 12h8.8" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>',
    pendiente: '<circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-dasharray="3 3"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
    si: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="m7.5 12.3 3 3 6-6.3" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    no: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7.5 9.5h9m-9 5h9" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/><path d="m14.5 6.5-5 11" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>',
    nc: '<circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M7.5 12h9" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>',
    llego: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="m7.5 12.3 3 3 6-6.3" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    detenido: '<rect x="2" y="2" width="20" height="20" rx="5" fill="currentColor"/><rect x="8" y="8" width="8" height="8" rx="1" fill="#fff"/>',
    umbral: '<path d="M12 2.5 22.5 20.5h-21Z" fill="currentColor"/><path d="M12 9v5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1.4" fill="#fff"/>',
    inicio: '<path d="M6 5v14M19 5l-9 7 9 7Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    anterior: '<path d="M16 5 7 12l9 7Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    siguiente: '<path d="m8 5 9 7-9 7Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    final: '<path d="M18 5v14M5 5l9 7-9 7Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    reproducir: '<path d="M7 4.5v15l12.5-7.5Z" fill="currentColor"/>',
    pausar: '<rect x="6" y="5" width="4.2" height="14" rx="1" fill="currentColor"/><rect x="13.8" y="5" width="4.2" height="14" rx="1" fill="currentColor"/>'
  };

  function icono(nombre) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (ICONOS[nombre] || "") + "</svg>";
  }

  // ---------- Utilidades ----------

  function esc(valor) {
    return String(valor == null ? "" : valor)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function host(url) {
    var m = /^[a-z]+:\/\/([^/]+)/i.exec(url || "");
    return m ? m[1].replace(/^www\./, "") : url;
  }

  function nombreSitio(t) {
    return t.grupo === "real" ? host(t.url_base) : t.sitio + ".html";
  }

  function pct(v) {
    return (v * 100).toLocaleString("es-MX", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " %";
  }

  function fecha(iso) {
    if (!iso) return "pendiente";
    var meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
    var p = iso.slice(0, 10).split("-");
    return Number(p[2]) + "-" + meses[Number(p[1]) - 1] + "-" + p[0];
  }

  function etiquetaCorrida(t) {
    // "segunda corrida, 2026-11-14" -> "segunda corrida, 14-nov-2026"
    return String(t.corrida || "").replace(/\d{4}-\d{2}-\d{2}/, function (f) { return fecha(f); });
  }

  function chip(estado) {
    if (!estado) {
      return '<span class="chip chip-pendiente">' + icono("pendiente") + "Pendiente</span>";
    }
    return '<span class="chip chip-' + esc(estado) + '">' + icono(estado) + esc(ESTADOS[estado] || estado) + "</span>";
  }

  // Misma regla de exclusión que src/analisis.py: sin NVDA, o no evaluable en cualquiera, no se compara.
  function comparacion(t, corto) {
    if (t.grupo === "prueba") {
      return t.coincide_esperado
        ? { clase: "si", texto: corto ? "Coincide" : "Coincide con la respuesta esperada" }
        : { clase: "no", texto: corto ? "No coincide" : "No coincide con la respuesta esperada" };
    }
    if (!t.veredicto_nvda) return { clase: "nc", texto: corto ? "Sin comparar" : "Sin comparar: NVDA pendiente" };
    if (t.veredicto_nvda === "no_evaluable") return { clase: "nc", texto: corto ? "Sin comparar" : "Sin comparar: no evaluable en NVDA" };
    if (t.estado === "no_evaluable") return { clase: "nc", texto: corto ? "Sin comparar" : "Sin comparar: Atorapp no pudo evaluar" };
    return t.estado === t.veredicto_nvda
      ? { clase: "si", texto: corto ? "Coinciden" : "Coincide con NVDA" }
      : { clase: "no", texto: corto ? "No coinciden" : "No coincide con NVDA" };
  }

  function acuerdoHtml(t, corto) {
    var c = comparacion(t, corto);
    return '<p class="acuerdo acuerdo-' + c.clase + '">' + icono(c.clase) + esc(c.texto) + "</p>";
  }

  function cuenta(t) {
    if (t.friccion != null) return t.friccion + " pulsaciones";
    if (t.consumidas != null) return t.consumidas + " pulsaciones consumidas";
    return "pulsaciones: pendiente";
  }

  function estadoTexto(t) {
    var texto = ESTADOS[t.estado] || t.estado;
    if (t.tipo_falla) texto += ": " + (FALLAS[t.tipo_falla] || t.tipo_falla);
    return texto;
  }

  // ---------- Datos: un solo arreglo con todas las tareas ----------

  var TODAS = [];
  D.reales.forEach(function (t) { t.grupo = "real"; TODAS.push(t); });
  D.prueba.forEach(function (t) { t.grupo = "prueba"; TODAS.push(t); });

  function ruta(t) {
    return "#trayectoria/" + t.grupo + "/" + encodeURIComponent(t.sitio) + "/" + t.tarea;
  }

  function buscar(grupo, sitio, tarea) {
    for (var i = 0; i < TODAS.length; i++) {
      var t = TODAS[i];
      if (t.grupo === grupo && t.sitio === sitio && t.tarea === tarea) return i;
    }
    return -1;
  }

  // ---------- Inicio ----------

  function tarjeta(t, chica) {
    var nivel = chica ? "h4" : "h3";
    var titulo = chica
      ? "Tarea " + t.tarea + " · " + TAREAS[t.tarea] + '<span class="sr-only"> en ' + esc(nombreSitio(t)) + "</span>"
      : '<span class="tarjeta-tarea">Tarea ' + t.tarea + " · " + esc(TAREAS[t.tarea]) + "</span>" + esc(nombreSitio(t));
    var segunda = /^segunda/.test(t.corrida || "") ? ' <span class="etiqueta">' + esc(etiquetaCorrida(t)) + "</span>" : "";
    var referencia = t.grupo === "real"
      ? "<div><dt>NVDA</dt><dd>" + chip(t.veredicto_nvda) + "</dd></div>"
      : "<div><dt>Esperado</dt><dd>" + chip(t.esperado.estado) + "</dd></div>";
    return '<li><article class="tarjeta borde-' + esc(t.estado) + '">' +
      "<" + nivel + '><a class="tarjeta-enlace" href="' + ruta(t) + '">' + titulo + "</a></" + nivel + ">" +
      '<dl class="pares"><div><dt>Atorapp estima</dt><dd>' + chip(t.estado) + "</dd></div>" + referencia + "</dl>" +
      acuerdoHtml(t) +
      '<p class="meta">' + esc(cuenta(t)) + segunda + "</p>" +
      '<span class="tarjeta-ver" aria-hidden="true">Ver recorrido →</span>' +
      "</article></li>";
  }

  function vistaInicio() {
    var a = D.analisis.acuerdo;
    var iguales = a.n ? Math.round(a.tres_clases * a.n) : 0;
    var coinciden = D.prueba.filter(function (t) { return t.coincide_esperado; }).length;
    var sitios = {};
    D.reales.forEach(function (t) { sitios[t.sitio] = true; });

    var html = '<p class="antetitulo">FEMECI 2026 · Resultados</p>' +
      '<h1 tabindex="-1">Qué concluye Atorapp</h1>' +
      '<p class="entrada">Atorapp <strong>estima</strong> si una persona que usa lector de pantalla puede completar una ' +
      "tarea real en un sitio web y cuántas pulsaciones le cuesta. La referencia es la auditoría manual con NVDA.</p>" +
      '<ul class="cifras">' +
      '<li class="cifra"><span class="cifra-valor">' + D.reales.length + ' <small>tareas</small></span>' +
      '<span class="cifra-texto">en ' + Object.keys(sitios).length + " sitios reales de Sinaloa</span></li>" +
      '<li class="cifra"><span class="cifra-valor">' + (a.n ? iguales + " <small>de</small> " + a.n : "pendiente") + "</span>" +
      '<span class="cifra-texto">tareas comparables en las que Atorapp coincide con NVDA</span></li>' +
      '<li class="cifra"><span class="cifra-valor">' + coinciden + " <small>de</small> " + D.prueba.length + "</span>" +
      '<span class="cifra-texto">tareas de prueba con el resultado esperado (escrito a mano)</span></li>' +
      "</ul>";

    html += '<section aria-labelledby="h-reales"><h2 id="h-reales">Sitios reales de Sinaloa</h2>' +
      '<p class="seccion-intro">Auditados primero a mano con NVDA, a ciegas; después corrió Atorapp. ' +
      "Cada tarjeta abre el recorrido paso a paso.</p>" +
      '<ul class="tarjetas">' + D.reales.map(function (t) { return tarjeta(t, false); }).join("") + "</ul></section>";

    html += '<section aria-labelledby="h-prueba"><h2 id="h-prueba">Páginas de prueba (validación del método)</h2>' +
      '<p class="seccion-intro">Páginas hechas para el proyecto, con una barrera conocida y la respuesta escrita a mano antes ' +
      "del código. No tienen auditoría NVDA. Comprueban que Atorapp hace lo que dice, no que funcione en cualquier sitio.</p>";
    Object.keys(PAGINAS_PRUEBA).forEach(function (pagina) {
      var tareas = D.prueba.filter(function (t) { return t.sitio === pagina; });
      if (!tareas.length) return;
      html += '<div class="grupo-prueba"><h3>' + esc(PAGINAS_PRUEBA[pagina]) + " <code>" + esc(pagina) + ".html</code></h3>" +
        '<ul class="tarjetas tarjetas-chicas">' + tareas.map(function (t) { return tarjeta(t, true); }).join("") + "</ul></div>";
    });
    html += "</section>";
    vista.innerHTML = html;
    return "Inicio";
  }

  // ---------- Trayectoria ----------

  var rep = null; // estado del reproductor

  function teclaHtml(tecla, grande) {
    var k = TECLAS[tecla] || [tecla, tecla, ""];
    return '<span class="tecla" aria-hidden="true">' + esc(k[0]) + "</span>" +
      '<span class="sr-only">Tecla: ' + esc(k[1]) + "</span>" +
      (grande ? '<span class="tecla-desc">' + esc(k[2]) + "</span>" : "");
  }

  function marcasDe(i) {
    return (rep.marcas || []).filter(function (m) { return m.paso === i; });
  }

  function marcaHtml(m) {
    return '<span class="marca-paso marca-' + esc(m.tipo) + '">' + icono(m.tipo) + esc(m.texto) + "</span>";
  }

  function paginaTexto(p) {
    if (!p.pagina) return "página: pendiente";
    var nombre = p.pagina === "/" ? "/ (portada)" : p.pagina;
    return "Página: " + nombre + " · nivel " + p.profundidad;
  }

  function vistaTrayectoria(indice) {
    var t = TODAS[indice];
    var sitio = nombreSitio(t);
    var html = '<nav class="migas" aria-label="Ruta"><ol><li><a href="#inicio">Inicio</a></li>' +
      "<li>" + esc(t.grupo === "real" ? "Sitios reales" : "Páginas de prueba") + "</li>" +
      '<li aria-current="page">' + esc(sitio) + " · Tarea " + t.tarea + "</li></ol></nav>" +
      '<p class="antetitulo">Recorrido de Atorapp · ' + esc(t.grupo === "real" ? "sitio real" : "página de prueba") + "</p>" +
      '<h1 tabindex="-1">Tarea ' + t.tarea + " · " + esc(TAREAS[t.tarea]) + " — " + esc(sitio) + "</h1>";

    // Ficha: tarea y veredicto
    var objetivo = t.objetivo_correcto === "NO_EXISTE"
      ? "No existe en el sitio (según la auditoría)"
      : String(t.objetivo_correcto || "pendiente").split("|").join(" · ");
    html += '<div class="ficha"><section class="caja" aria-labelledby="h-tarea"><h2 id="h-tarea">La tarea</h2><dl class="datos">' +
      "<dt>Entrada</dt><dd>" + esc(t.entrada === "/" ? "/ (portada)" : t.entrada) + "</dd>" +
      (t.tramite ? "<dt>Trámite buscado</dt><dd>" + esc(t.tramite) + "</dd>" : "") +
      "<dt>Objetivo correcto</dt><dd>" + esc(objetivo) + "</dd>" +
      "<dt>Mejor estrategia</dt><dd>" + esc(ESTRATEGIAS[t.estrategia] || t.estrategia || "pendiente") + "</dd>" +
      "<dt>Corrida</dt><dd>" + esc(etiquetaCorrida(t) || "pendiente") + "</dd>" +
      "</dl></section>";

    var referencia = t.grupo === "real"
      ? '<dt>NVDA</dt><dd>' + chip(t.veredicto_nvda) + "</dd>"
      : "<dt>NVDA</dt><dd>" + chip(null) + "</dd><dt>Respuesta esperada</dt><dd>" + chip(t.esperado.estado) + " · " +
        esc(t.esperado.friccion) + " pulsaciones</dd>";
    html += '<section class="caja" aria-labelledby="h-veredicto"><h2 id="h-veredicto">Lo que concluye</h2>' +
      '<dl class="datos"><dt>Atorapp estima</dt><dd>' + chip(t.estado) + "</dd>" +
      (t.tipo_falla ? "<dt>Tipo de falla</dt><dd>" + esc(FALLAS[t.tipo_falla] || t.tipo_falla) + "</dd>" : "") + referencia +
      "<dt>Esfuerzo</dt><dd>" + esc(cuenta(t)) + " (umbral: " + D.umbral + ")</dd></dl>" +
      '<div style="margin-top:.8rem">' + acuerdoHtml(t) + "</div>" +
      '<p class="motivo"><strong>Motivo:</strong> ' + esc(t.motivo || "llegó al objetivo correcto") + "</p>" +
      (t.grupo === "prueba" && t.esperado.razon ? '<p class="nota-corrida"><strong>Por qué se esperaba:</strong> ' + esc(t.esperado.razon) + "</p>" : "") +
      (t.nota_corrida ? '<p class="nota-corrida">' + esc(t.nota_corrida) + "</p>" : "") +
      "</section></div>";

    // Reproductor
    html += '<section class="reproductor" aria-labelledby="h-recorrido">' +
      '<div class="reproductor-encabezado"><h2 id="h-recorrido">Recorrido paso a paso</h2>' +
      (t.pasos ? '<p class="meta">' + t.pasos.length + (t.pasos.length === 1 ? " paso" : " pasos") + " · lo que anunciaría el lector según Atorapp</p>" : "") + "</div>";
    if (t.pasos && t.pasos.length) {
      html += '<p class="viendo" id="viendo" hidden></p>' +
        '<div class="ahora" id="ahora"></div>' +
        '<div class="controles"><div class="botones" role="group" aria-label="Control del recorrido">' +
        '<button type="button" class="boton" id="b-inicio">' + icono("inicio") + "Inicio</button>" +
        '<button type="button" class="boton" id="b-anterior">' + icono("anterior") + "Anterior</button>" +
        '<button type="button" class="boton boton-primario" id="b-reproducir">' + icono("reproducir") + "<span>Reproducir</span></button>" +
        '<button type="button" class="boton" id="b-siguiente">' + icono("siguiente") + "Siguiente</button>" +
        '<button type="button" class="boton" id="b-final">' + icono("final") + "Final</button></div>" +
        '<label class="ajuste" for="velocidad">Velocidad <select id="velocidad">' +
        '<option value="lenta">Lenta</option><option value="normal" selected>Normal</option><option value="rapida">Rápida</option>' +
        "</select></label></div>" +
        '<div class="deslizador"><label for="deslizador">Ir al paso</label><input type="range" id="deslizador" min="0" step="1"></div>' +
        '<p class="sr-only" id="vivo" aria-live="polite"></p>' +
        '<section class="lista-pasos" id="lista-pasos" tabindex="0" aria-labelledby="h-pasos">' +
        '<h3 id="h-pasos">Todos los pasos</h3><ol class="pasos" id="pasos"></ol></section>';
    } else {
      html += '<div class="pendiente"><p><strong>Trayectoria completa: pendiente.</strong> ' +
        (t.ciego ? "Este sitio tiene una auditoría NVDA a ciegas en curso; su recorrido se mostrará al terminarla."
          : "El reporte de esta corrida solo guardó el resumen.") + "</p>" +
        (t.trayectoria ? "<p>Resumen guardado: <code>" + esc(t.trayectoria) + "</code></p>" : "") + "</div>";
    }
    html += "</section>";

    // Falsas llegadas
    html += '<section aria-labelledby="h-falsas"><h2 id="h-falsas">Llegó primero a otra cosa</h2>' +
      '<p class="seccion-intro">Estrategias que creyeron llegar, pero no al objetivo correcto. No cambian el veredicto; ' +
      "en un sitio real eso también le puede pasar a una persona.</p>";
    if (t.falsas_llegadas == null) {
      html += "<p>Pendiente.</p>";
    } else if (!t.falsas_llegadas.length) {
      html += "<p>Ninguna.</p>";
    } else {
      html += '<ul class="falsas">' + t.falsas_llegadas.map(function (f, k) {
        return "<li><span><strong>" + esc(ESTRATEGIAS[f.estrategia] || f.estrategia) + "</strong>: en " + f.pulsaciones +
          " pulsaciones encontró «" + esc(f.encontro) + "»</span>" +
          (f.pasos && f.pasos.length ? '<button type="button" class="boton" data-falsa="' + k + '">Ver este recorrido</button>' : "") + "</li>";
      }).join("") + "</ul>";
    }
    html += "</section>";

    // Vecinas
    var previa = indice > 0 ? TODAS[indice - 1] : null;
    var proxima = indice < TODAS.length - 1 ? TODAS[indice + 1] : null;
    html += '<nav class="vecinas" aria-label="Otras tareas">' +
      (previa ? '<a href="' + ruta(previa) + '">← ' + esc(nombreSitio(previa)) + " · Tarea " + previa.tarea + "</a>" : "<span></span>") +
      (proxima ? '<a href="' + ruta(proxima) + '">' + esc(nombreSitio(proxima)) + " · Tarea " + proxima.tarea + " →</a>" : "") +
      "</nav>";

    vista.innerHTML = html;

    if (t.pasos && t.pasos.length) {
      iniciarReproductor(t, t.pasos, t.marcas, null);
      vista.querySelectorAll("[data-falsa]").forEach(function (b) {
        b.addEventListener("click", function () {
          var f = t.falsas_llegadas[Number(b.getAttribute("data-falsa"))];
          iniciarReproductor(t, f.pasos, [], f);
          document.getElementById("h-recorrido").scrollIntoView({ block: "start" });
          document.getElementById("b-reproducir").focus();
        });
      });
    }
    return "Tarea " + t.tarea + " en " + sitio;
  }

  function iniciarReproductor(t, pasos, marcas, falsa) {
    detener();
    rep = { t: t, pasos: pasos, marcas: marcas || [], i: -1, timer: null };
    var viendo = document.getElementById("viendo");
    if (falsa) {
      viendo.hidden = false;
      viendo.innerHTML = "Viendo la falsa llegada de «" + esc(ESTRATEGIAS[falsa.estrategia] || falsa.estrategia) +
        '». <a href="' + ruta(t) + '" id="volver-principal">Volver al recorrido principal</a>';
      document.getElementById("volver-principal").addEventListener("click", function (e) {
        e.preventDefault();
        iniciarReproductor(t, t.pasos, t.marcas, null);
        document.getElementById("b-reproducir").focus();
      });
    } else {
      viendo.hidden = true;
      viendo.textContent = "";
    }
    var lista = document.getElementById("pasos");
    lista.innerHTML = pasos.map(function (p, i) {
      var ms = rep.marcas.filter(function (m) { return m.paso === i; });
      return '<li data-i="' + i + '"><span class="paso-num">' + (i + 1) + "</span>" +
        "<span>" + teclaHtml(p.tecla, false) + "</span>" +
        '<span class="paso-anuncio">' + (p.anuncio ? esc(p.anuncio) : '<span class="anuncio-vacio">(sin anuncio)</span>') +
        ms.map(function (m) { return '<span class="paso-marca paso-marca-' + esc(m.tipo) + '">' + esc(m.texto) + "</span>"; }).join("") +
        "</span>" +
        '<span class="paso-cuenta">' + p.pulsaciones + '<span class="sr-only"> pulsaciones acumuladas</span></span></li>';
    }).join("");
    lista.onclick = function (e) {
      var li = e.target.closest("li[data-i]");
      if (li) { detener(); ir(Number(li.getAttribute("data-i")), true); }
    };
    var deslizador = document.getElementById("deslizador");
    deslizador.max = String(pasos.length);
    deslizador.oninput = function () { detener(); ir(Number(deslizador.value) - 1, true); };
    document.getElementById("b-inicio").onclick = function () { detener(); ir(-1, true); };
    document.getElementById("b-anterior").onclick = function () { detener(); ir(rep.i - 1, true); };
    document.getElementById("b-siguiente").onclick = function () { detener(); ir(rep.i + 1, true); };
    document.getElementById("b-final").onclick = function () { detener(); ir(rep.pasos.length - 1, true); };
    document.getElementById("b-reproducir").onclick = alternar;
    document.getElementById("velocidad").onchange = function () { if (rep.timer) { detener(); reproducir(); } };
    ir(-1, false);
  }

  function ir(i, anunciar) {
    var pasos = rep.pasos;
    i = Math.max(-1, Math.min(pasos.length - 1, i));
    rep.i = i;
    var umbral = D.umbral;
    var total = pasos[pasos.length - 1].pulsaciones;
    var escala = Math.max(total, umbral) * 1.08 || 1;
    var p = i >= 0 ? pasos[i] : null;
    var n = p ? p.pulsaciones : 0;
    var k = p ? (TECLAS[p.tecla] || [p.tecla, p.tecla, ""]) : null;

    var html = '<div class="tecla-grande">' +
      (p ? teclaHtml(p.tecla, true) : '<span class="tecla" aria-hidden="true">·</span><span class="tecla-desc">antes de la primera pulsación</span>') +
      "</div>" +
      '<div class="ahora-texto"><p class="ahora-paso">' + (p ? "Paso " + (i + 1) + " de " + pasos.length : "Inicio · el cursor está antes de la primera línea") + "</p>" +
      '<p class="anuncio">' + (p
        ? (p.anuncio ? "<q>" + esc(p.anuncio) + "</q>" : '<span class="anuncio-vacio">(sin anuncio)</span>')
        : '<span class="anuncio-vacio">Pulsa «Siguiente» o «Reproducir».</span>') + "</p>" +
      '<div class="contador"><span class="contador-num">' + n + " <small>pulsaciones</small></span>" +
      '<span class="medidor" aria-hidden="true"><span class="medidor-relleno' + (n > umbral ? " pasado" : "") + '" style="width:' + (100 * n / escala) + '%"></span>' +
      '<span class="medidor-umbral" style="left:calc(' + (100 * umbral / escala) + '% - 1.5px)"><span>umbral ' + umbral + "</span></span></span></div>" +
      '<div class="marcas-ahora">' + (p ? marcasDe(i).map(marcaHtml).join("") : "") + "</div>" +
      (p ? '<p class="ahora-pagina">' + esc(paginaTexto(p)) +
        (p.documento ? " · documento: " + esc(p.documento.es_pdf ? (p.documento.capa_texto ? "PDF con texto" : p.documento.capa_texto === false ? "PDF sin capa de texto" : "PDF no leído") : "no es PDF") : "") +
        (p.no_evaluable ? " · " + esc(p.no_evaluable) : "") + "</p>" : "") +
      "</div>";
    document.getElementById("ahora").innerHTML = html;

    document.getElementById("b-inicio").disabled = i < 0;
    document.getElementById("b-anterior").disabled = i < 0;
    document.getElementById("b-siguiente").disabled = i >= pasos.length - 1;
    document.getElementById("b-final").disabled = i >= pasos.length - 1;
    var deslizador = document.getElementById("deslizador");
    deslizador.value = String(i + 1);
    deslizador.setAttribute("aria-valuetext", p ? "Paso " + (i + 1) + " de " + pasos.length : "Inicio");

    var lista = document.getElementById("pasos");
    lista.querySelectorAll("li").forEach(function (li, j) {
      if (j === i) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
      li.classList.toggle("futuro", j > i);
    });
    var actual = lista.querySelector('li[aria-current="step"]');
    if (actual) {
      var caja = document.getElementById("lista-pasos");
      var arriba = actual.offsetTop - caja.clientHeight / 2;
      caja.scrollTop = Math.max(0, arriba);
    }

    // Solo se anuncia al avanzar a mano: durante la reproducción la región se calla para no saturar.
    var vivo = document.getElementById("vivo");
    if (anunciar && !rep.timer) {
      vivo.textContent = p
        ? "Paso " + (i + 1) + " de " + pasos.length + ". Tecla " + k[1] + ". Anuncia: " + (p.anuncio || "nada") + ". " +
          n + " pulsaciones." + marcasDe(i).map(function (m) { return " " + m.texto + "."; }).join("")
        : "Inicio del recorrido.";
    }
  }

  function boton() { return document.getElementById("b-reproducir"); }

  function reproducir() {
    if (!rep) return;
    if (rep.i >= rep.pasos.length - 1) ir(-1, false);
    var ms = VELOCIDADES[document.getElementById("velocidad").value] || VELOCIDADES.normal;
    rep.timer = setInterval(function () {
      if (rep.i >= rep.pasos.length - 1) { detener(); return; }
      ir(rep.i + 1, false);
    }, ms);
    boton().innerHTML = icono("pausar") + "<span>Pausar</span>";
  }

  function detener() {
    if (rep && rep.timer) {
      clearInterval(rep.timer);
      rep.timer = null;
      var b = boton();
      if (b) b.innerHTML = icono("reproducir") + "<span>Reproducir</span>";
      var vivo = document.getElementById("vivo");
      if (vivo) vivo.textContent = "Pausado en el paso " + (rep.i + 1) + " de " + rep.pasos.length + ".";
    }
  }

  function alternar() { if (rep && rep.timer) detener(); else reproducir(); }

  // ---------- Comparación ----------

  function puntajeHtml(v) {
    if (v == null) return '<span class="no-medido">no medido</span>';
    return '<span class="puntaje">' + pct(v) + '<span class="barra" aria-hidden="true"><span style="width:' + (v * 100) + '%"></span></span></span>';
  }

  function vistaComparacion() {
    var a = D.analisis;
    var m = a.matriz;
    var html = '<p class="antetitulo">Comparación</p><h1 tabindex="-1">Atorapp frente a NVDA y axe</h1>' +
      '<p class="entrada">¿Coincide lo que estima Atorapp con la auditoría manual con NVDA? ¿Y qué dice el puntaje de ' +
      "conformidad automática de axe-core sobre las mismas páginas?</p>";

    // Tabla por tarea real
    function filaSitio(t) {
      return '<th scope="row"><a href="' + ruta(t) + '">' + esc(nombreSitio(t)) + " · Tarea " + t.tarea + "</a>" +
        (/^segunda/.test(t.corrida || "") ? '<br><span class="etiqueta">' + esc(etiquetaCorrida(t)) + "</span>" : "") + "</th>";
    }
    html += '<section aria-labelledby="h-tabla"><h2 id="h-tabla">Sitios reales: Atorapp frente a NVDA</h2>' +
      '<div class="tabla-envoltura"><table><caption>Veredicto por tarea</caption>' +
      '<thead><tr><th scope="col">Sitio y tarea</th><th scope="col">Atorapp estima</th><th scope="col">NVDA</th>' +
      '<th scope="col">¿Coinciden?</th><th scope="col" class="num">Pulsaciones de Atorapp</th></tr></thead><tbody>';
    D.reales.forEach(function (t) {
      html += "<tr>" + filaSitio(t) + "<td>" + chip(t.estado) + "</td><td>" + chip(t.veredicto_nvda) + "</td><td>" +
        acuerdoHtml(t, true) + '</td><td class="num">' + esc(t.friccion != null ? t.friccion : t.consumidas != null ? t.consumidas + " consumidas" : "pendiente") + "</td></tr>";
    });
    html += "</tbody></table></div></section>";

    html += '<section aria-labelledby="h-axe"><h2 id="h-axe">Sitios reales: puntaje de conformidad automática (axe-core)</h2>' +
      '<div class="tabla-envoltura"><table><caption>Los 4 puntajes en la página fijada de antemano para cada tarea</caption>' +
      '<thead><tr><th scope="col">Sitio y tarea</th><th scope="col">NVDA</th>' +
      PUNTAJES.map(function (p) { return '<th scope="col" class="num">' + esc(p[1]) + "</th>"; }).join("") + "</tr></thead><tbody>";
    D.reales.forEach(function (t) {
      html += "<tr>" + filaSitio(t) + "<td>" + chip(t.veredicto_nvda) + "</td>" +
        PUNTAJES.map(function (p) { return '<td class="num">' + puntajeHtml(t.puntajes ? t.puntajes[p[0]] : null) + "</td>"; }).join("") + "</tr>";
    });
    html += "</tbody></table></div>" +
      '<dl class="definiciones"><dt>Puntaje por reglas</dt><dd>Reglas de axe aprobadas entre reglas aplicables (aprobadas + violadas).</dd>' +
      "<dt>Puntaje por elementos</dt><dd>Elementos que pasan entre elementos revisados; el de reglas esconde cuántos fallan.</dd>" +
      "<dt>Conservador</dt><dd>Lo que axe no pudo decidir cuenta como falla: es una cota inferior.</dd></dl>" +
      '<p class="seccion-intro">Miden solo lo que axe revisa automáticamente; no son «conformidad WCAG».</p></section>';

    // Matriz
    var clases = m.clases;
    html += '<section aria-labelledby="h-matriz"><h2 id="h-matriz">Matriz de confusión</h2><div class="matriz-bloque"><div>' +
      '<div class="tabla-envoltura"><table class="matriz"><caption>Filas: veredicto NVDA · columnas: lo que estima Atorapp</caption>' +
      '<thead><tr><td class="matriz-eje">NVDA \\ Atorapp</td>' + clases.map(function (c) { return '<th scope="col">' + esc(ESTADOS[c]) + "</th>"; }).join("") +
      "</tr></thead><tbody>" +
      clases.map(function (fila) {
        return '<tr><th scope="row">' + esc(ESTADOS[fila]) + "</th>" + clases.map(function (col) {
          var v = m.matriz[fila][col];
          var clase = (fila === col ? "diagonal " : "") + (v > 0 ? "lleno" : "cero");
          return '<td class="' + clase + '">' + v + "</td>";
        }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>" +
      '<ul class="leyenda-matriz"><li><span class="muestra muestra-diagonal" aria-hidden="true"></span>Diagonal: coinciden</li>' +
      '<li><span class="muestra muestra-lleno" aria-hidden="true"></span>Celda con al menos una tarea</li></ul>' +
      '<p class="meta" style="margin-top:.8rem">Comparables: ' + m.n + ". Fuera de la matriz: sin NVDA " + m.excluidas.sin_nvda +
      ", no evaluable en NVDA " + m.excluidas.no_evaluable_nvda + ", no evaluable en Atorapp " + m.excluidas.no_evaluable_atorapp + ".</p></div>";

    var acuerdo = a.acuerdo;
    var tres = acuerdo.n ? Math.round(acuerdo.tres_clases * acuerdo.n) : null;
    var bin = acuerdo.n ? Math.round(acuerdo.binario * acuerdo.n) : null;
    html += '<div class="caja"><h3>Acuerdo observado</h3>' +
      (acuerdo.n
        ? '<span class="acuerdo-grande">' + tres + " de " + acuerdo.n + "</span><p>tareas comparables con el mismo veredicto (3 clases).</p>" +
          "<p><strong>" + bin + " de " + acuerdo.n + "</strong> en binario: se logró (completable o con dificultad) contra no completable.</p>"
        : "<p>Pendiente: no hay tareas comparables.</p>") +
      "<h4>Con otros umbrales</h4><ul class=\"lista-simple\">" +
      Object.keys(a.acuerdo_por_umbral).map(function (u) {
        var v = a.acuerdo_por_umbral[u];
        return "<li>Umbral " + esc(u) + ": " + v.iguales + " de " + v.n + "</li>";
      }).join("") + "</ul>" +
      '<p class="meta">Se reporta como fracción, no como porcentaje: con tan pocas tareas un porcentaje aparenta más de lo que dice. ' +
      "Las tareas de un mismo sitio no son independientes.</p></div></div></section>";

    // AUC
    html += '<section aria-labelledby="h-auc"><h2 id="h-auc">¿Distingue axe las tareas completables?</h2>' +
      '<div class="pendiente"><p><strong>Todavía no se puede responder.</strong> ' +
      (a.auc.calculado ? "" : "No se calcula el AUC: " + esc(a.auc.motivo) + ".") + "</p></div></section>";

    // Páginas de prueba
    html += '<section aria-labelledby="h-prueba-comp"><h2 id="h-prueba-comp">Páginas de prueba frente a su respuesta esperada</h2>' +
      '<p class="seccion-intro">La respuesta esperada se escribió a mano, antes del código; no es NVDA. Las reglas y palabras clave se ' +
      "diseñaron viendo estas mismas páginas: coincidir demuestra que la implementación es correcta, no que funcione en otros sitios.</p>" +
      '<div class="tabla-envoltura"><table><caption>24 tareas en 6 páginas de prueba</caption><thead><tr>' +
      '<th scope="col">Página y tarea</th><th scope="col">Atorapp estima</th><th scope="col">Esperado</th>' +
      '<th scope="col" class="num">Pulsaciones (obtenidas / esperadas)</th><th scope="col">¿Coincide?</th></tr></thead><tbody>' +
      D.prueba.map(function (t) {
        var obtenidas = t.friccion != null ? t.friccion : t.consumidas;
        return '<tr><th scope="row"><a href="' + ruta(t) + '">' + esc(t.sitio) + ".html · Tarea " + t.tarea + "</a></th>" +
          "<td>" + chip(t.estado) + "</td><td>" + chip(t.esperado.estado) + "</td>" +
          '<td class="num">' + esc(obtenidas) + " / " + esc(t.esperado.friccion) + "</td><td>" + acuerdoHtml(t, true) + "</td></tr>";
      }).join("") + "</tbody></table></div></section>";

    vista.innerHTML = html;
    return "Comparación";
  }

  // ---------- Rutas ----------

  function render(enfocar) {
    detener();
    rep = null;
    var hash = decodeURIComponent(location.hash.replace(/^#/, ""));
    var partes = hash.split("/");
    var titulo, activa = null;
    if (partes[0] === "trayectoria" && partes.length === 4 && buscar(partes[1], partes[2], partes[3]) >= 0) {
      titulo = vistaTrayectoria(buscar(partes[1], partes[2], partes[3]));
    } else if (partes[0] === "comparacion") {
      titulo = vistaComparacion();
      activa = "comparacion";
    } else {
      titulo = vistaInicio();
      activa = "inicio";
    }
    document.title = titulo + " — Atorapp";
    document.querySelectorAll(".navegacion a").forEach(function (a) {
      if (a.getAttribute("data-vista") === activa) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    if (enfocar) {
      window.scrollTo(0, 0);
      var h1 = vista.querySelector("h1");
      if (h1) h1.focus();
    }
  }

  document.getElementById("saltar").addEventListener("click", function (e) {
    e.preventDefault();
    var h1 = vista.querySelector("h1");
    (h1 || document.getElementById("contenido")).focus();
  });

  document.getElementById("pie-datos").textContent =
    "Datos generados el " + fecha(D.generado) + " a partir de los reportes de Atorapp (umbral: " + D.umbral + " pulsaciones). " +
    "No corre Atorapp en vivo.";

  window.addEventListener("hashchange", function () { render(true); });
  render(false);
})();
