/* Atorapp · modo exploración (Fase 3F.3). Sin bibliotecas. Aquí no se decide ningún veredicto: todo
   lo calcula el servidor con src/ (clasificar). La UI solo muestra, pide confirmar y manda órdenes. */
(function () {
  "use strict";

  var TOKEN = document.querySelector('meta[name="atorapp-token"]').content;
  var vista = document.getElementById("vista");
  var vivo = document.getElementById("vivo");
  var UMBRAL = 15;

  // ---------- Vocabulario (el mismo de interfaz/app.js) ----------

  var TAREAS = {
    A: ["Contacto", "Teléfono o correo de atención"],
    B: ["Requisitos de un trámite", "Escribe el trámite abajo"],
    C: ["Documento", "Un archivo descargable"],
    D: ["Formulario", "Qué campos pide, sin enviar"]
  };
  var TAREAS_LARGAS = {
    A: "Contacto", B: "Requisitos de un trámite", C: "Abrir un documento descargable",
    D: "Llegar a un formulario e identificar sus campos"
  };
  var ESTADOS = {
    completable: "Completable", con_dificultad: "Con dificultad",
    no_completable: "No completable", no_evaluable: "No evaluable"
  };
  var FALLAS = {
    no_encontrado: "no se encontró", no_identificable: "no se puede identificar",
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
  var PUNTAJES = [
    ["reglas", "Por reglas"], ["elementos", "Por elementos"],
    ["reglas_conservador", "Reglas, conservador"], ["elementos_conservador", "Elementos, conservador"]
  ];

  // Formas de los estados (decorativas: el texto siempre dice lo mismo).
  var FORMAS = {
    completable: '<circle cx="20" cy="20" r="17" fill="currentColor"/><path d="M11 20 L18 27 L29 13" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    con_dificultad: '<path d="M20 3 L37 35 H3 Z" fill="currentColor"/><line x1="20" y1="14" x2="20" y2="24" stroke="#fff" stroke-width="4" stroke-linecap="round"/><circle cx="20" cy="29.5" r="2.3" fill="#fff"/>',
    no_completable: '<rect x="3" y="3" width="34" height="34" rx="6" fill="currentColor"/><path d="M13 13 L27 27 M27 13 L13 27" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
    no_evaluable: '<path d="M20 2 L38 20 L20 38 L2 20 Z" fill="currentColor"/><line x1="12.5" y1="20" x2="27.5" y2="20" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
    pendiente: '<circle cx="20" cy="20" r="16" fill="none" stroke="currentColor" stroke-width="3.5"/><path d="M15.5 15.5 Q16 11 20 11 Q24.5 11 24.5 15 Q24.5 18 20.5 20 V23" stroke="currentColor" stroke-width="3.5" fill="none" stroke-linecap="round"/><circle cx="20" cy="28.5" r="2.2" fill="currentColor"/>',
    alerta: '<path d="M20 3 L37 35 H3 Z" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"/><line x1="20" y1="14" x2="20" y2="24" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/><circle cx="20" cy="29.5" r="2.3" fill="currentColor"/>'
  };

  function forma(nombre) {
    return '<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false">' + (FORMAS[nombre] || "") + "</svg>";
  }

  function insignia(estado) {
    return '<p class="insignia insignia--' + estado + '">' + forma(estado) + esc(ESTADOS[estado]) + "</p>";
  }

  // ---------- Utilidades ----------

  function esc(valor) {
    return String(valor == null ? "" : valor)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function host(url) {
    var m = /^[a-z]+:\/\/([^/]+)/i.exec(url || "");
    return m ? m[1] : url;
  }

  function pct(v) {
    return (v * 100).toLocaleString("es-MX", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " %";
  }

  function fecha(iso) {
    if (!iso) return "";
    var meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
    var p = iso.slice(0, 10).split("-");
    return Number(p[2]) + "-" + meses[Number(p[1]) - 1] + "-" + p[0] + ", " + iso.slice(11, 16);
  }

  function nombreEstrategia(clave) { return ESTRATEGIAS[clave] || clave; }

  // mm:ss (los minutos pueden pasar de 59); null = evaluación guardada antes de medir el tiempo.
  function mmss(segundos) {
    if (segundos === null || segundos === undefined) return "no medida";
    var t = Math.max(0, Math.round(segundos));
    var m = Math.floor(t / 60), s = t % 60;
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  function pulsaciones(n) { return n + (n === 1 ? " pulsación" : " pulsaciones"); }

  function anunciar(texto) {
    vivo.textContent = "";
    window.setTimeout(function () { vivo.textContent = texto; }, 60);
  }

  function enfocarTitulo() {
    var h1 = vista.querySelector("h1");
    if (h1) { h1.setAttribute("tabindex", "-1"); h1.focus(); }
  }

  function pedir(metodo, ruta, cuerpo) {
    var opciones = { method: metodo, headers: { "X-Atorapp-Token": TOKEN } };
    if (cuerpo !== undefined) {
      opciones.headers["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(cuerpo);
    }
    return fetch(ruta, opciones).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (datos) {
        if (!r.ok) {
          var error = new Error(typeof datos.detail === "string" ? datos.detail : "El servidor respondió " + r.status);
          error.codigo = r.status;
          throw error;
        }
        return datos;
      });
    });
  }

  function barra(valor, total, etiqueta, clase) {
    var ancho = Math.max(0, Math.min(100, (valor / total) * 100));
    return '<div class="barra ' + (clase || "") + '" role="img" aria-label="' + esc(etiqueta) + '">' +
      '<div class="barra-relleno" style="width:' + ancho.toFixed(1) + '%"></div></div>';
  }

  function barraUmbral(n) {
    var paso = n > UMBRAL;
    return '<p class="barra-texto"><strong>' + esc(pulsaciones(n)) + "</strong> · " +
      (paso ? "pasó el umbral de dificultad (" + UMBRAL + ")" : "umbral de dificultad: " + UMBRAL) + "</p>" +
      barra(paso ? UMBRAL : n, UMBRAL, paso ? n + " pulsaciones, pasó el umbral de " + UMBRAL : n + " de " + UMBRAL + " pulsaciones",
        paso ? "barra--paso" : "");
  }

  function teclaHtml(tecla, clase) {
    var k = TECLAS[tecla] || [tecla, tecla, ""];
    return '<span class="tecla ' + (clase || "") + '" aria-hidden="true">' + esc(k[0]) + "</span>" +
      '<span class="sr-only">' + esc(k[1]) + "</span>";
  }

  function filaPaso(p, n, actual) {
    return '<li' + (actual ? ' aria-current="step"' : "") + '><span class="n">' + n + "</span><span>" +
      teclaHtml(p.tecla, "tecla--chica") + '</span><span class="texto">“' + esc(p.anuncio) + "”</span></li>";
  }

  function contexto(d) {
    return esc(host(d.url)) + " · Tarea " + esc(d.tarea) + " · " + esc(TAREAS_LARGAS[d.tarea]) +
      (d.tramite ? " · Trámite: " + esc(d.tramite) : "");
  }

  // ---------- Estado de la evaluación en curso (vive fuera de las vistas) ----------

  var EN_CURSO = null;  // {id, url, tarea, tramite, estrategias, estrategia, pasos, fase, final, fuente}
  var ANUNCIO_CADA_PASO = false;

  function seguir(id) {
    EN_CURSO = { id: id, pasos: [], estrategia: null, fase: null, final: null, ultimoAnuncio: 0,
                 inicioMs: Date.now(), finMs: null };
    var fuente = new EventSource("/api/evaluaciones/" + encodeURIComponent(id) + "/eventos");
    EN_CURSO.fuente = fuente;
    function al(tipo, fn) {
      fuente.addEventListener(tipo, function (e) { if (EN_CURSO && EN_CURSO.id === id) fn(JSON.parse(e.data)); });
    }
    al("inicio", function (d) {
      EN_CURSO.url = d.url; EN_CURSO.tarea = d.tarea; EN_CURSO.tramite = d.tramite;
      EN_CURSO.estrategias = d.estrategias;
      pintarEvaluando();
    });
    al("estrategia", function (d) {
      EN_CURSO.estrategia = d; EN_CURSO.pasos = [];
      anunciar("Estrategia " + d.indice + " de " + d.total + ": " + nombreEstrategia(d.estrategia));
      pintarEvaluando(true);
    });
    al("paso", function (d) {
      EN_CURSO.pasos.push(d);
      if (ANUNCIO_CADA_PASO && Date.now() - EN_CURSO.ultimoAnuncio > 1500) {
        EN_CURSO.ultimoAnuncio = Date.now();
        anunciar("Tecla " + (TECLAS[d.tecla] || [d.tecla, d.tecla])[1] + ": " + d.anuncio);
      }
      pedirPintado();
    });
    al("fase", function () {
      EN_CURSO.fase = "axe";
      anunciar("Las estrategias terminaron. Midiendo con axe-core.");
      pintarEvaluando(true);
    });
    ["fin", "detenida", "bloqueada", "error"].forEach(function (tipo) {
      al(tipo, function (d) {
        fuente.close();  // si no, EventSource se reconecta y repite todo
        EN_CURSO.final = { tipo: tipo, datos: d };
        EN_CURSO.finMs = Date.now();  // el reloj se congela al terminar
        if (tipo === "fin") {
          anunciar("Evaluación terminada.");
          var id = EN_CURSO.id;
          EN_CURSO = null;
          if (location.hash === "#evaluando") location.hash = "#resultado/" + id;
        } else {
          anunciar(tipo === "detenida" ? "Evaluación detenida." : "La evaluación no terminó.");
          pintarEvaluando(true);
        }
      });
    });
  }

  // Reloj de la pantalla Evaluando: se pinta cada segundo en #ev-tiempo, que está FUERA del aria-live
  // (el lector no lo anuncia cada segundo; quien quiera saber el tiempo lo lee como texto).
  var RELOJ = null;
  function pintarTiempo() {
    var el = document.getElementById("ev-tiempo");
    if (!el || !EN_CURSO) { window.clearInterval(RELOJ); RELOJ = null; return; }
    el.textContent = "Tiempo: " + mmss(((EN_CURSO.finMs || Date.now()) - EN_CURSO.inicioMs) / 1000);
    if (EN_CURSO.finMs) { window.clearInterval(RELOJ); RELOJ = null; }
  }

  var pintadoPendiente = false;
  function pedirPintado() {
    if (pintadoPendiente) return;
    pintadoPendiente = true;
    window.requestAnimationFrame(function () { pintadoPendiente = false; pintarEvaluando(false); });
  }

  // ---------- Vista: Inicio ----------

  function vistaInicio() {
    var tarjetas = ["A", "B", "C", "D"].map(function (t, i) {
      return '<label class="tarea"><input type="radio" name="tarea" value="' + t + '"' + (i === 0 ? " checked" : "") +
        '><span class="tarea-texto"><span class="tarea-nombre">' + t + " · " + esc(TAREAS[t][0]) +
        '</span><span class="tarea-desc">' + esc(TAREAS[t][1]) + "</span></span></label>";
    }).join("");
    var curso = EN_CURSO && !EN_CURSO.final
      ? '<div class="aviso">' + forma("alerta") + '<div><p><strong>Hay una evaluación en curso.</strong></p><p><a href="#evaluando">Ver la evaluación en curso</a></p></div></div>'
      : "";
    vista.innerHTML =
      "<h1>Evalúa un sitio</h1>" +
      '<p class="entrada">Pega la dirección, elige qué quiere hacer la persona y Atorapp recorre la página como lo haría alguien con lector de pantalla.</p>' +
      curso +
      '<div id="error-envio"></div>' +
      '<form class="formulario" id="formulario" novalidate>' +
      '<div class="campo"><label for="url">Dirección del sitio</label>' +
      '<input id="url" name="url" type="url" inputmode="url" autocomplete="url" spellcheck="false" placeholder="https://www.ejemplo.gob.mx" aria-describedby="error-url">' +
      '<p class="error-campo" id="error-url"></p></div>' +
      '<fieldset class="tareas"><legend>Tarea</legend><div class="tarjetas-tarea">' + tarjetas + "</div></fieldset>" +
      '<div class="campo campo--secundario"><label for="tramite">Trámite (solo para la tarea B)</label>' +
      '<input id="tramite" name="tramite" type="text" autocomplete="off" placeholder="Por ejemplo: acta de nacimiento" aria-describedby="ayuda-tramite error-tramite">' +
      '<p class="ayuda" id="ayuda-tramite">Nombra qué se busca, no dónde está. Sin trámite no se puede correr la tarea B.</p>' +
      '<p class="error-campo" id="error-tramite"></p></div>' +
      '<div class="acciones"><button type="submit" class="boton" id="b-evaluar">Evaluar</button>' +
      '<p class="nota">Pausa de 1 s entre páginas · nunca envía formularios</p></div>' +
      "</form>";
    document.getElementById("formulario").addEventListener("submit", enviar);
  }

  function marcarError(campo, mensaje) {
    var entrada = document.getElementById(campo);
    document.getElementById("error-" + campo).textContent = mensaje;
    if (mensaje) entrada.setAttribute("aria-invalid", "true"); else entrada.removeAttribute("aria-invalid");
  }

  function enviar(e) {
    e.preventDefault();
    var url = document.getElementById("url").value.trim();
    var tarea = document.querySelector('input[name="tarea"]:checked').value;
    var tramite = document.getElementById("tramite").value.trim();
    var errorUrl = /^https?:\/\/[^\s/]+/i.test(url) ? "" : "Escribe una dirección completa que empiece con http:// o https://.";
    var errorTramite = tarea === "B" && !tramite ? "La tarea B necesita el trámite que la persona busca." : "";
    marcarError("url", errorUrl);
    marcarError("tramite", errorTramite);
    document.getElementById("error-envio").innerHTML = "";
    if (errorUrl || errorTramite) {
      document.getElementById(errorUrl ? "url" : "tramite").focus();
      return;
    }
    var boton = document.getElementById("b-evaluar");
    boton.disabled = true;
    pedir("POST", "/api/evaluaciones", { url: url, tarea: tarea, tramite: tramite }).then(function (r) {
      seguir(r.id);
      location.hash = "#evaluando";
    }).catch(function (error) {
      boton.disabled = false;
      var titulo = error.codigo === 403 ? "Este sitio está bloqueado." : "No se pudo empezar.";
      var caja = document.getElementById("error-envio");
      caja.innerHTML = '<div class="aviso aviso--error" role="alert">' + forma("alerta") +
        "<div><p><strong>" + esc(titulo) + "</strong></p><p>" + esc(error.message) + "</p></div></div>";
    });
  }

  // ---------- Vista: Evaluando ----------

  function vistaEvaluando() {
    if (!EN_CURSO) { location.replace("#inicio"); return false; }
    vista.innerHTML =
      '<div class="cabeza"><div><p class="contexto" id="ev-contexto"></p><h1 id="ev-titulo">Recorriendo la página…</h1></div>' +
      '<button type="button" class="boton boton--secundario boton--chico" id="b-detener">Detener</button></div>' +
      '<div id="ev-final"></div>' +
      '<section class="actual" aria-labelledby="h-actual"><h2 id="h-actual" class="sr-only">Paso actual</h2>' +
      '<div id="ev-tecla"></div>' +
      '<div class="actual-datos"><p class="rotulo">Lo que anunciaría el lector</p>' +
      '<p class="anuncio" id="ev-anuncio">—</p><div id="ev-barra"></div><p class="nota"><span id="ev-estrategia"></span> · <span id="ev-tiempo">Tiempo: 00:00</span></p></div></section>' +
      '<section aria-labelledby="h-rec"><div class="encabezado-seccion"><h2 id="h-rec">Recorrido de esta estrategia</h2>' +
      '<label class="opcion-anunciar"><input type="checkbox" id="anunciar-cada"' + (ANUNCIO_CADA_PASO ? " checked" : "") +
      "> Anunciar cada paso</label></div>" +
      '<ol class="recorrido" id="ev-lista"></ol></section>';
    document.getElementById("b-detener").addEventListener("click", function () {
      if (!EN_CURSO || EN_CURSO.final) return;
      this.disabled = true;
      this.textContent = "Deteniendo…";
      anunciar("Deteniendo en la siguiente pulsación.");
      pedir("POST", "/api/evaluaciones/" + encodeURIComponent(EN_CURSO.id) + "/detener").catch(function () {});
    });
    document.getElementById("anunciar-cada").addEventListener("change", function () { ANUNCIO_CADA_PASO = this.checked; });
    window.clearInterval(RELOJ);
    RELOJ = window.setInterval(pintarTiempo, 1000);
    pintarTiempo();
    pintarEvaluando(true);
    return true;
  }

  function pintarEvaluando(completo) {
    if (location.hash !== "#evaluando" || !EN_CURSO) return;
    var lista = document.getElementById("ev-lista");
    if (!lista) return;
    var e = EN_CURSO;
    if (e.url) document.getElementById("ev-contexto").innerHTML = contexto(e);
    var ultimo = e.pasos[e.pasos.length - 1];
    document.getElementById("ev-tecla").innerHTML = ultimo
      ? teclaHtml(ultimo.tecla, "tecla--grande")
      : '<span class="tecla tecla--grande" aria-hidden="true">·</span><span class="sr-only">sin pulsaciones todavía</span>';
    document.getElementById("ev-anuncio").textContent = ultimo ? "“" + ultimo.anuncio + "”" : "—";
    // La barra se recrea en cada pintada: se arranca desde el ancho anterior para que el relleno se deslice.
    var cajaBarra = document.getElementById("ev-barra");
    var rellenoViejo = cajaBarra.querySelector(".barra-relleno");
    var anchoViejo = rellenoViejo ? rellenoViejo.style.width : "0%";
    cajaBarra.innerHTML = barraUmbral(ultimo ? ultimo.pulsaciones : 0);
    var rellenoNuevo = cajaBarra.querySelector(".barra-relleno");
    if (rellenoNuevo && anchoViejo !== rellenoNuevo.style.width) {
      var destino = rellenoNuevo.style.width;
      rellenoNuevo.style.width = anchoViejo;
      void rellenoNuevo.offsetWidth; // fuerza el reflujo para que la transición arranque
      rellenoNuevo.style.width = destino;
    }
    // Mientras la evaluación sigue, se marca para animar (pulso, puntos, brillo en la barra).
    var ocupado = !e.final;
    document.getElementById("h-actual").parentElement.classList.toggle("ocupado", ocupado);
    document.getElementById("ev-titulo").classList.toggle("cargando", ocupado);
    var s = e.estrategia;
    var texto = s ? "Estrategia " + s.indice + " de " + s.total + ": " + nombreEstrategia(s.estrategia) : "Abriendo la página de entrada…";
    if (ultimo) texto += ultimo.profundidad ? " · a " + ultimo.profundidad + " de 3 páginas de la entrada" : " · en la página de entrada";
    if (e.fase === "axe") texto = "Las estrategias terminaron. Midiendo con axe-core…";
    document.getElementById("ev-estrategia").textContent = texto;
    if (e.fase === "axe") document.getElementById("ev-titulo").textContent = "Midiendo con axe-core…";

    // La lista: se reconstruye al cambiar de estrategia; si no, solo se agregan los pasos nuevos.
    var hay = lista.children.length;
    if (completo || hay > e.pasos.length) { lista.innerHTML = ""; hay = 0; }
    var actual = lista.querySelector('[aria-current="step"]');
    if (actual) actual.removeAttribute("aria-current");
    var html = "";
    for (var i = hay; i < e.pasos.length; i++) html += filaPaso(e.pasos[i], i + 1, i === e.pasos.length - 1);
    if (html) lista.insertAdjacentHTML("beforeend", html);
    else if (lista.lastElementChild) lista.lastElementChild.setAttribute("aria-current", "step");
    if (lista.lastElementChild && lista.lastElementChild.scrollIntoView && document.activeElement === document.body) {
      lista.lastElementChild.scrollIntoView({ block: "nearest" });
    }

    if (e.final) pintarFinal(e.final);
  }

  function pintarFinal(final) {
    var titulos = { detenida: "Evaluación detenida", bloqueada: "Evaluación bloqueada", error: "La evaluación falló" };
    var mensajes = {
      detenida: "La detuviste. Lo recorrido no se guardó como resultado.",
      bloqueada: final.datos.mensaje,
      error: final.datos.mensaje
    };
    document.getElementById("ev-titulo").textContent = titulos[final.tipo];
    var boton = document.getElementById("b-detener");
    if (boton) boton.remove();
    document.getElementById("ev-final").innerHTML =
      '<div class="aviso' + (final.tipo === "detenida" ? "" : " aviso--error") + '">' + forma("alerta") +
      "<div><p><strong>" + esc(titulos[final.tipo]) + ".</strong></p><p>" + esc(mensajes[final.tipo]) + "</p>" +
      '<p><a href="#inicio">Nueva evaluación</a></p></div></div>';
    enfocarTitulo();
  }

  // ---------- Vista: Resultado ----------

  function vigente(d) {
    if (!d.requiere_confirmacion) return d.estimaciones.ninguna;
    return d.confirmacion ? d.estimaciones[d.confirmacion.eleccion] : null;
  }

  function textoEstado(v) {
    var partes = [];
    if (v.friccion !== null && v.friccion !== undefined) {
      partes.push("Fricción: " + pulsaciones(v.friccion) + " (umbral " + UMBRAL + ").");
    } else if (v.consumidas !== null && v.consumidas !== undefined) {
      partes.push(pulsaciones(v.consumidas) + " consumidas sin resolver.");
    }
    if (v.tipo_falla) partes.push("Motivo: " + FALLAS[v.tipo_falla] + ".");
    return partes.join(" ");
  }

  function sensibilidad(v) {
    return "Con otros umbrales: " + Object.keys(v.sensibilidad).map(function (u) {
      return u + ": " + ESTADOS[v.sensibilidad[u]].toLowerCase();
    }).join(" · ") + ".";
  }

  function tarjetaEstima(d, cambiando) {
    var v = vigente(d);
    var cuerpo, clase = "tarjeta tarjeta--estima";
    if (d.no_cargo) {
      // La entrada no abrió: no hubo estrategias, así que no se habla de "lo que encontraron".
      clase += " tarjeta--" + v.estado;
      cuerpo = insignia(v.estado) +
        '<p class="grande">' + esc(d.no_cargo.motivo) + ".</p>" +
        '<p class="nota">No se corrió ninguna estrategia ni axe-core. Esto no dice nada sobre la accesibilidad del sitio: solo que Atorapp no pudo abrir la página de entrada.</p>' +
        '<p class="nota"><strong>Estimación experimental, no verificada con NVDA.</strong></p>';
    } else if (!v || cambiando) {
      var primera = d.opciones[0], cond = d.estimaciones["0"];
      cuerpo = '<p class="insignia insignia--pendiente">' + forma("pendiente") + "Por confirmar</p>" +
        '<p class="llegue">Llegué a esto: «' + esc(primera.encontro) + "»</p>" +
        '<p class="grande">En ' + esc(pulsaciones(primera.pulsaciones)) + " con «" + esc(nombreEstrategia(primera.estrategia)) + "».</p>" +
        '<p class="nota">Si es lo que buscabas: ' + esc(ESTADOS[cond.estado].toLowerCase()) +
        (cond.friccion !== null ? " (" + cond.friccion + (cond.friccion <= UMBRAL ? " ≤ " : " > ") + UMBRAL + ")" : "") +
        (cond.tipo_falla ? ", porque " + esc(FALLAS[cond.tipo_falla]) : "") + ". Atorapp no sabe qué buscabas: dímelo tú.</p>" +
        '<p class="pregunta" id="pregunta">¿Es lo que buscabas?</p>' +
        '<div class="acciones" role="group" aria-labelledby="pregunta" id="si-no">' +
        '<button type="button" class="boton boton--chico" data-eleccion="0">Sí, es esto</button>' +
        '<button type="button" class="boton boton--secundario boton--chico" id="b-no">No</button></div>' +
        '<div id="otras"></div>';
    } else {
      clase += " tarjeta--" + v.estado;
      var eleccion = d.confirmacion && d.confirmacion.eleccion;
      var lead = "";
      if (eleccion && eleccion !== "ninguna") lead = '<p class="llegue">Llegó a «' + esc(d.opciones[Number(eleccion)].encontro) + "»</p>";
      else if (eleccion === "ninguna") lead = '<p class="grande">Dijiste que nada de lo encontrado era lo que buscabas.</p>';
      else lead = '<p class="grande">Ninguna estrategia encontró algo que parezca ' + esc(TAREAS_LARGAS[d.tarea].toLowerCase()) + " con lo anunciado.</p>";
      cuerpo = insignia(v.estado) + lead +
        '<p class="grande">' + esc(textoEstado(v)) + "</p>" +
        (v.motivo ? '<p class="nota">' + esc(v.motivo) + ".</p>" : "") +
        (v.estrategia ? '<p class="nota">Mejor estrategia: ' + esc(nombreEstrategia(v.estrategia)) + ".</p>" : "") +
        '<p class="nota">' + esc(sensibilidad(v)) + "</p>" +
        (v.falsas_llegadas.length ? '<p class="nota">Llegó primero a otra cosa: ' + v.falsas_llegadas.map(function (x) {
          return esc(nombreEstrategia(x.estrategia)) + ", en " + x.pulsaciones + " («" + esc(x.encontro) + "»)";
        }).join("; ") + ".</p>" : "") +
        '<p class="nota"><strong>' + (eleccion ? "Confirmado por ti" : "Sin confirmación posible: no llegó a nada") +
        " · estimación experimental, no verificada con NVDA.</strong></p>" +
        (d.requiere_confirmacion ? '<p><button type="button" class="boton boton--secundario boton--chico" id="b-cambiar">Cambiar mi respuesta</button></p>' : "");
    }
    return '<section class="' + clase + '" aria-labelledby="h-estima" id="estima"><h2 id="h-estima">Atorapp estima</h2>' + cuerpo + "</section>";
  }

  function tarjetaAxe(d) {
    var filas;
    if (d.no_cargo) {
      filas = '<p class="grande">No se pudo medir: la página no cargó.</p>';  // el error del navegador queda en exploracion.json
    } else if (!d.puntajes) {
      filas = '<p class="grande">No medido: ' + esc(d.error_axe || "sin detalle") + ".</p>";
    } else {
      filas = PUNTAJES.map(function (p) {
        var v = d.puntajes[p[0]];
        if (v === null || v === undefined) {
          return '<div class="puntaje"><span>' + esc(p[1]) + '</span><span></span><span class="puntaje-valor">no medido</span></div>';
        }
        return '<div class="puntaje"><span>' + esc(p[1]) + "</span>" +
          barra(v * 100, 100, p[1] + ": " + pct(v), "barra--puntaje") +
          '<span class="puntaje-valor">' + pct(v) + "</span></div>";
      }).join("");
    }
    return '<section class="tarjeta" aria-labelledby="h-axe"><h2 id="h-axe">axe-core dice</h2>' + filas +
      '<p class="enfasis">Un puntaje alto no garantiza que la tarea se pueda completar.</p>' +
      '<p class="nota">Conformidad automática: mide solo lo que axe-core revisa, en la página de entrada.</p></section>';
  }

  function tablaEstrategias(d) {
    if (d.no_cargo) return "";  // no corrió ninguna estrategia
    var filas = d.intentos.map(function (i) {
      var detalle = i.llego ? "«" + i.encontro + "»" : i.motivo;
      return "<tr><th scope=\"row\">" + esc(nombreEstrategia(i.estrategia)) + '</th><td><span class="si-no">' +
        (i.llego ? "sí" : "no") + '</span></td><td class="num">' + i.pulsaciones + '</td><td class="num">' + esc(mmss(i.duracion_s)) + "</td><td>" + esc(detalle) + "</td></tr>";
    }).join("");
    return '<section aria-labelledby="h-estr"><div class="encabezado-seccion"><h2 id="h-estr">Qué hizo cada estrategia</h2></div>' +
      '<div class="tabla-envoltura"><table><caption>«Cree que llegó» es lo que concluye cada estrategia con lo anunciado; no es un veredicto.</caption>' +
      '<thead><tr><th scope="col">Estrategia</th><th scope="col">¿Cree que llegó?</th><th scope="col">Pulsaciones</th><th scope="col">Duración</th><th scope="col">Encontró o motivo</th></tr></thead>' +
      "<tbody>" + filas + "</tbody></table></div></section>";
  }

  function vistaResultado(id) {
    vista.innerHTML = "<h1>Resultado</h1><p>Cargando…</p>";
    pedir("GET", "/api/evaluaciones/" + encodeURIComponent(id)).then(function (d) {
      pintarResultado(id, d, false);
      enfocarTitulo();
    }).catch(function (error) {
      vista.innerHTML = '<h1>Resultado</h1><div class="aviso aviso--error">' + forma("alerta") + "<div><p>" + esc(error.message) +
        '</p><p><a href="#historial">Ir al historial</a></p></div></div>';
      enfocarTitulo();
    });
  }

  function pintarResultado(id, d, cambiando) {
    vista.innerHTML =
      '<div><p class="contexto">' + contexto(d) + " · " + esc(fecha(d.fecha)) + "</p><h1>Resultado</h1>" +
      '<p class="nota">Duración total: ' + esc(mmss(d.duracion_s)) + " (mm:ss, axe incluido)</p></div>" +
      '<div class="tarjetas">' + tarjetaEstima(d, cambiando) + tarjetaAxe(d) + "</div>" +
      (d.captcha.length ? '<p class="nota">CAPTCHA detectado en la ruta: ' + esc(d.captcha.join(", ")) + ".</p>" : "") +
      tablaEstrategias(d) +
      '<div class="acciones"><a class="boton" href="#recorrido/' + esc(id) + '">Ver recorrido paso a paso</a>' +
      '<button type="button" class="boton boton--secundario" id="b-exportar">Exportar reporte en Markdown</button>' +
      '<a class="boton boton--secundario" href="#inicio">Nueva evaluación</a></div>' +
      '<div class="exportado" id="exportado" role="status"></div>';

    function elegir(eleccion) {
      pedir("POST", "/api/evaluaciones/" + encodeURIComponent(id) + "/confirmacion", { eleccion: eleccion }).then(function (nuevo) {
        pintarResultado(id, nuevo, false);
        var v = vigente(nuevo);
        anunciar("Respuesta guardada. Atorapp estima: " + ESTADOS[v.estado] + ".");
        document.getElementById("h-estima").setAttribute("tabindex", "-1");
        document.getElementById("h-estima").focus();
      });
    }
    vista.querySelectorAll("[data-eleccion]").forEach(function (b) {
      b.addEventListener("click", function () { elegir(b.getAttribute("data-eleccion")); });
    });
    var no = document.getElementById("b-no");
    if (no) no.addEventListener("click", function () {
      var otras = d.opciones.slice(1).map(function (o, i) {
        return '<li><button type="button" class="boton boton--secundario" data-eleccion="' + (i + 1) + '">«' + esc(o.encontro) +
          "» · " + esc(pulsaciones(o.pulsaciones)) + " · " + esc(nombreEstrategia(o.estrategia)) + "</button></li>";
      }).join("");
      document.getElementById("otras").innerHTML =
        '<p class="pregunta" id="h-otras" tabindex="-1">' + (otras ? "¿Alguna de estas? Las encontraron otras estrategias." : "Ninguna otra estrategia encontró algo distinto.") + "</p>" +
        '<ul class="opciones">' + otras +
        '<li><button type="button" class="boton boton--secundario" data-eleccion="ninguna">Ninguna de estas</button></li></ul>';
      document.getElementById("si-no").remove();
      document.querySelectorAll("#otras [data-eleccion]").forEach(function (b) {
        b.addEventListener("click", function () { elegir(b.getAttribute("data-eleccion")); });
      });
      document.getElementById("h-otras").focus();
    });
    var cambiar = document.getElementById("b-cambiar");
    if (cambiar) cambiar.addEventListener("click", function () {
      pintarResultado(id, d, true);
      document.getElementById("pregunta").setAttribute("tabindex", "-1");
      document.getElementById("pregunta").focus();
    });
    document.getElementById("b-exportar").addEventListener("click", function () {
      pedir("POST", "/api/evaluaciones/" + encodeURIComponent(id) + "/exportar").then(function (r) {
        var caja = document.getElementById("exportado");
        caja.innerHTML = '<p><strong>Reporte guardado en:</strong></p><p class="ruta">' + esc(r.ruta) + "</p>" +
          '<button type="button" class="boton boton--secundario boton--chico" id="b-carpeta">Abrir carpeta</button>';
        document.getElementById("b-carpeta").addEventListener("click", function () {
          pedir("POST", "/api/abrir/carpeta/" + encodeURIComponent(id));
        });
      }).catch(function (error) {
        document.getElementById("exportado").innerHTML = "<p>No se pudo exportar: " + esc(error.message) + "</p>";
      });
    });
  }

  // ---------- Vista: Recorrido paso a paso ----------

  function vistaRecorrido(id) {
    vista.innerHTML = "<h1>Recorrido paso a paso</h1><p>Cargando…</p>";
    pedir("GET", "/api/evaluaciones/" + encodeURIComponent(id)).then(function (d) {
      var v = vigente(d);
      var base = v || d.estimaciones["0"];
      var titulo = v ? (v.estrategia ? "Recorrido de «" + nombreEstrategia(v.estrategia) + "», la que sustenta la estimación." : "")
        : "Recorrido de la opción más barata, todavía sin confirmar.";
      var pasos = base.pasos;
      vista.innerHTML =
        '<div><p class="contexto">' + contexto(d) + "</p><h1>Recorrido paso a paso</h1></div>" +
        '<p class="entrada">' + esc(titulo) + " " + esc(pasos.length ? pulsaciones(pasos[pasos.length - 1].pulsaciones) + " en total." : "") + "</p>" +
        (pasos.length ? '<ol class="recorrido">' + pasos.map(function (p, i) { return filaPaso(p, i + 1, false); }).join("") + "</ol>"
          : "<p>Sin pulsaciones.</p>") +
        '<div class="acciones"><a class="boton boton--secundario" href="#resultado/' + esc(id) + '">Volver al resultado</a></div>';
      enfocarTitulo();
    }).catch(function (error) {
      vista.innerHTML = "<h1>Recorrido paso a paso</h1><p>" + esc(error.message) + "</p>";
      enfocarTitulo();
    });
  }

  // ---------- Vista: Historial ----------

  function vistaHistorial() {
    vista.innerHTML = "<h1>Historial</h1><p>Cargando…</p>";
    pedir("GET", "/api/historial").then(function (filas) {
      var cuerpo = filas.length ? '<div class="tabla-envoltura"><table><caption>Evaluaciones guardadas en la carpeta exploracion/, de la más reciente a la más antigua. Fuera del estudio.</caption>' +
        '<thead><tr><th scope="col">Fecha</th><th scope="col">Sitio</th><th scope="col">Tarea</th><th scope="col">Estimación</th><th scope="col">Detalle</th></tr></thead><tbody>' +
        filas.map(function (f) {
          return "<tr><td>" + esc(fecha(f.fecha)) + "</td><td>" + esc(host(f.url)) + "</td><td>" + esc(f.tarea) + " · " + esc(TAREAS[f.tarea][0]) +
            (f.tramite ? " (" + esc(f.tramite) + ")" : "") + "</td><td>" + (f.por_confirmar ? "Por confirmar" : esc(ESTADOS[f.estado])) +
            '</td><td><a href="#resultado/' + esc(f.id) + '">Ver resultado<span class="sr-only"> de ' + esc(host(f.url)) + ", tarea " + esc(f.tarea) + ", " + esc(fecha(f.fecha)) + "</span></a></td></tr>";
        }).join("") + "</tbody></table></div>"
        : "<p>Todavía no hay evaluaciones guardadas.</p>";
      vista.innerHTML = "<h1>Historial</h1>" + cuerpo;
      enfocarTitulo();
    });
  }

  // ---------- Vista: Acerca de ----------

  function vistaAcerca() {
    vista.innerHTML = "<h1>Acerca de Atorapp</h1>";
    pedir("GET", "/api/info").then(function (info) {
      vista.innerHTML =
        "<h1>Acerca de Atorapp</h1>" +
        '<p class="entrada">Atorapp estima si una persona que usa lector de pantalla puede completar una tarea real en un sitio web, y cuánto le cuesta en pulsaciones.</p>' +
        '<section class="seccion" aria-labelledby="h-modo"><h2 id="h-modo">Modo exploración y estudio</h2>' +
        "<p>Esta app es el <strong>modo exploración</strong>: una estimación experimental para cualquier sitio, <strong>no verificada con NVDA</strong>. No conoce el objetivo correcto: se detiene en lo que cree que es y te pide confirmar. Lo que corre se guarda en la carpeta <code>exploracion/</code> y nunca entra al estudio.</p>" +
        "<p>El <strong>estudio</strong> (botón «Estudio (validado con NVDA)») compara a Atorapp contra auditorías manuales con NVDA hechas a ciegas, con el objetivo correcto fijado antes de correr.</p></section>" +
        '<section class="seccion" aria-labelledby="h-limites"><h2 id="h-limites">Límites del emulador</h2><ul class="lista-acerca">' +
        "<li>Es un emulador simplificado inspirado en los comandos de NVDA. No equivale a NVDA.</li>" +
        "<li>No reproduce el modo foco, no lee iframes, no anuncia aria-live, no lee el contenido de los PDF y no modela el foco de los modales.</li>" +
        "<li>Las estrategias deciden con lo anunciado y una lista de palabras clave, no por significado.</li>" +
        "<li>La fricción es esfuerzo de navegación (pulsaciones), no la dificultad humana completa. Umbral: " + info.umbral + " pulsaciones (también se reporta con " + info.umbrales.join(", ") + ").</li>" +
        "<li>Sin objetivo fijado de antemano, la opción más barata puede ser una falsa llegada: por eso se pide confirmar.</li></ul></section>" +
        '<section class="seccion" aria-labelledby="h-nunca"><h2 id="h-nunca">Lo que nunca hace</h2><ul class="lista-acerca">' +
        "<li>Nunca envía formularios ni abre enlaces de correo o teléfono.</li>" +
        "<li>Espera " + info.pausa_s + " s entre páginas y se detiene a las " + info.topes.pulsaciones + " pulsaciones o " + info.topes.navegaciones + " páginas por estrategia.</li>" +
        "<li>No evalúa los sitios bloqueados: " + (info.hosts_bloqueados.length ? info.hosts_bloqueados.map(esc).join(", ") : "ninguno") + ". Tienen una auditoría NVDA a ciegas pendiente.</li></ul></section>" +
        '<section class="seccion" aria-labelledby="h-creditos"><h2 id="h-creditos">Créditos</h2>' +
        "<p>Proyecto de Javier Sandoval (ITESM Sinaloa) para FEMECI 2026. Software libre. Usa axe-core para el puntaje de conformidad automática y la fuente Atkinson Hyperlegible del Braille Institute (licencia SIL OFL 1.1).</p></section>";
      enfocarTitulo();
    });
  }

  // ---------- Ruteo ----------

  function marcarMenu(nombre) {
    document.querySelectorAll(".menu a[data-vista]").forEach(function (a) {
      if (a.getAttribute("data-vista") === nombre) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function rutear() {
    var partes = (location.hash || "#inicio").slice(1).split("/");
    var nombre = partes[0] || "inicio";
    var menu = { inicio: "inicio", evaluando: "inicio", resultado: "inicio", recorrido: "inicio", historial: "historial", acerca: "acerca" };
    marcarMenu(menu[nombre] || "inicio");
    var titulos = { historial: "Historial", acerca: "Acerca de", evaluando: "Evaluando", resultado: "Resultado", recorrido: "Recorrido" };
    document.title = (titulos[nombre] ? titulos[nombre] + " · " : "") + "Atorapp · modo exploración";
    if (nombre === "evaluando") { if (vistaEvaluando()) enfocarTitulo(); return; }
    if (nombre === "resultado" && partes[1]) return vistaResultado(decodeURIComponent(partes[1]));
    if (nombre === "recorrido" && partes[1]) return vistaRecorrido(decodeURIComponent(partes[1]));
    if (nombre === "historial") return vistaHistorial();
    if (nombre === "acerca") return vistaAcerca();
    vistaInicio();
    if (location.hash) enfocarTitulo();
  }

  document.getElementById("b-estudio").addEventListener("click", function () {
    pedir("POST", "/api/abrir/estudio").then(function () {
      anunciar("Se abrió la interfaz del estudio en tu navegador.");
    });
  });
  document.getElementById("saltar").addEventListener("click", function (e) {
    e.preventDefault();
    enfocarTitulo();
  });
  window.addEventListener("hashchange", rutear);
  rutear();
})();
