/*
 * M19 `app.cliente`: guion propio de la herramienta (ADR-003, puntos 2 a 6; plan 001, T-001-68).
 *
 * Sin dependencias salvo htmx (servido desde esta misma aplicación), sin código en línea y sin
 * evaluación de texto como código: la política de contenido solo admite `script-src 'self'`.
 * No calcula ni compone datos: envía lo que la persona elige, guarda la ficha de la sesión en la
 * pestaña, coloca los fragmentos que el servidor devuelve, pasa el foco y anuncia lo que cambió.
 *
 * Alcance: carga del archivo, ficha de sesión, estados E1 y E9, foco y anuncios (Fase 7); y, en la
 * Fase 8, el fin de la sesión (ADR-003, puntos 5 y 9; NFR-000-17): registro de actividad, latido
 * como máximo una vez por minuto (el primero tras un silencio sale de inmediato, y el último de un
 * minuto con actividad sale al cumplirse), aviso de cierre al ocultarse la página (`pagehide`: no
 * al cambiar de pestaña), aviso E7 a los 43 minutos con su temporizador y «Seguir con la sesión»,
 * y E8 a los 45 minutos. Los demás comportamientos de los planes 002 y 003 se agregan después.
 *
 * Los textos que ve la persona vienen de las plantillas (atributos `data-egm-texto-*`) o del
 * servidor; este archivo no escribe ninguno propio.
 *
 * Ganchos que usa (plantillas M18):
 *   form[data-egm-carga], input[data-egm-archivo], button[data-egm-cargar]
 *   #estado-carga[data-egm-texto-leyendo]   estado E1
 *   #estado-pagina[data-egm-texto-recuperando]   estado E9
 *   #mensajes, #contenido, #anuncio, [data-egm-foco], [data-egm-descartar], .corte
 *   [data-egm-aviso] (E7, llega con `hidden`), [data-egm-temporizador] (`m:ss`), [data-egm-seguir]
 */
(function () {
  'use strict';

  // --- Nombres fijos del contrato con el servidor (app/carga.py, app/sesiones.py, app/servidor.py)
  const RUTA_CARGA = '/carga';
  const RUTA_INICIO = '/vista/inicio';
  const RUTA_RESULTADO = '/vista/resultado';
  const CABECERA_SESION = 'X-EGM-Sesion';
  const CABECERA_NOMBRE = 'X-EGM-Nombre';
  const CABECERA_DESTINO = 'X-EGM-Destino';
  const RUTA_LATIDO = '/sesion/latido';
  const RUTA_CIERRE = '/sesion/cierre';
  const CLAVE_FICHA = 'egm-sesion';
  const DESTINOS = ['contenido', 'mensajes'];

  // Tiempos fijos de NFR-000-17, ADR-003 (punto 5) y flujos.md §2 (E7: 43 minutos; E8: 45).
  const LATIDO_MS = 60 * 1000;
  const AVISO_MS = 43 * 60 * 1000;
  const INACTIVIDAD_MS = 45 * 60 * 1000;

  // --- Ficha de la sesión ------------------------------------------------------------------------
  // Vive en el almacenamiento de la pestaña, nunca en una cookie (ADR-003, punto 4): al cerrar la
  // pestaña desaparece y la sesión ya no se puede reabrir. Si el navegador no deja usar el
  // almacenamiento, la ficha se conserva solo en memoria mientras dure la página.
  let fichaEnMemoria = '';

  function leerFicha() {
    try {
      return window.sessionStorage.getItem(CLAVE_FICHA) || fichaEnMemoria;
    } catch (error) {
      return fichaEnMemoria;
    }
  }

  function guardarFicha(ficha) {
    fichaEnMemoria = ficha;
    try {
      window.sessionStorage.setItem(CLAVE_FICHA, ficha);
    } catch (error) {
      // sin almacenamiento: queda la copia en memoria
    }
  }

  function borrarFicha() {
    fichaEnMemoria = '';
    try {
      window.sessionStorage.removeItem(CLAVE_FICHA);
    } catch (error) {
      // sin almacenamiento: nada más que borrar
    }
  }

  // --- Foco y anuncios ---------------------------------------------------------------------------

  /** Pasa el foco al elemento marcado con [data-egm-foco], primero dentro de `region`. */
  function enfocar(region) {
    const marcado =
      (region && region.querySelector('[data-egm-foco]')) ||
      document.querySelector('[data-egm-foco]');
    if (marcado) {
      marcado.focus();
    }
  }

  let temporizadorAnuncio = 0;
  let temporizadorEscritura = 0;

  /** Vacía la región de anuncios: al terminar la sesión no debe quedar nada de la matriz. */
  function vaciarAnuncio() {
    window.clearTimeout(temporizadorEscritura);
    window.clearTimeout(temporizadorAnuncio);
    const region = document.getElementById('anuncio');
    if (region) {
      region.textContent = '';
    }
  }

  /** Escribe `texto` en la región de anuncios (aria-live) para que el lector de pantalla lo lea. */
  function anunciar(texto) {
    const region = document.getElementById('anuncio');
    if (!region || !texto) {
      return;
    }
    // Se vacía primero para que un mismo texto se anuncie otra vez.
    region.textContent = '';
    window.clearTimeout(temporizadorEscritura);
    temporizadorEscritura = window.setTimeout(function () {
      region.textContent = texto;
    }, 50);
    // Pasado un rato se vacía: un anuncio viejo no debe quedar como texto de la página.
    window.clearTimeout(temporizadorAnuncio);
    temporizadorAnuncio = window.setTimeout(function () {
      region.textContent = '';
    }, 5000);
  }

  /** Anuncia la línea de la cabecera corrida («Matriz: …»), que el servidor ya armó. */
  function anunciarCorte() {
    const corte = document.querySelector('#cabecera-corrida .corte');
    if (corte) {
      anunciar(corte.textContent.trim());
    }
  }

  /**
   * Un fallo que no trae un fragmento de la herramienta (por ejemplo, un error interno): muestra
   * el texto fijo que el servidor entregó como un mensaje de alerta. No inventa ningún texto.
   */
  function mostrarProblema(texto) {
    if (!texto) {
      return;
    }
    const mensaje = document.createElement('div');
    mensaje.className = 'mensaje';
    mensaje.setAttribute('role', 'alert');
    const parrafo = document.createElement('p');
    parrafo.setAttribute('tabindex', '-1');
    parrafo.setAttribute('data-egm-foco', '');
    parrafo.textContent = texto;
    mensaje.appendChild(parrafo);
    const mensajes = document.getElementById('mensajes');
    const contenido = document.getElementById('contenido');
    if (mensajes) {
      mensajes.replaceChildren(mensaje);
      enfocar(mensajes);
    } else if (contenido) {
      contenido.insertBefore(mensaje, contenido.firstChild);
      enfocar(contenido);
    }
  }

  // --- Carga del archivo -------------------------------------------------------------------------

  /**
   * Envía el archivo elegido como cuerpo crudo de `POST /carga` (ADR-003, punto 3), con el nombre
   * codificado como componente de URI en `X-EGM-Nombre` y la ficha actual, si la hay, en
   * `X-EGM-Sesion`. Se usa `fetch` y no htmx porque la respuesta de un rechazo es un 413 o un 422
   * con un fragmento válido, y porque htmx arma el cuerpo como formulario.
   */
  async function enviarCarga(formulario) {
    const entrada = formulario.querySelector('[data-egm-archivo]');
    const boton = formulario.querySelector('[data-egm-cargar]');
    const estado = formulario.querySelector('#estado-carga');
    const archivo = entrada && entrada.files ? entrada.files[0] : null;
    if (!archivo) {
      // Sin archivo elegido no se envía nada: el foco va al selector para que la persona elija.
      if (entrada) {
        entrada.focus();
      }
      return;
    }

    // E1: el aviso se anuncia (región role="status") y el botón queda inactivo.
    boton.disabled = true;
    if (estado) {
      estado.textContent = estado.getAttribute('data-egm-texto-leyendo') || '';
    }
    const mensajes = document.getElementById('mensajes');
    if (mensajes) {
      mensajes.replaceChildren();
    }

    const cabeceras = {
      'Content-Type': 'application/octet-stream',
      [CABECERA_NOMBRE]: encodeURIComponent(archivo.name),
    };
    const ficha = leerFicha();
    if (ficha) {
      cabeceras[CABECERA_SESION] = ficha;
    }

    try {
      const respuesta = await window.fetch(RUTA_CARGA, {
        method: 'POST',
        headers: cabeceras,
        body: archivo,
        cache: 'no-store',
        credentials: 'same-origin',
      });
      const fichaNueva = respuesta.headers.get(CABECERA_SESION);
      if (fichaNueva) {
        guardarFicha(fichaNueva);
      }
      if (leerFicha()) {
        anclar(); // el servidor contó la carga como actividad
      }
      const destino = respuesta.headers.get(CABECERA_DESTINO);
      const tipo = respuesta.headers.get('Content-Type') || '';
      const texto = await respuesta.text();
      if (tipo.startsWith('text/html') && DESTINOS.includes(destino)) {
        // htmx coloca el fragmento, procesa sus atributos hx-* y aplica los intercambios fuera de
        // banda (cabecera corrida y colofón). El foco lo pasa el oyente de `htmx:afterSettle`.
        window.htmx.swap('#' + destino, texto, { swapStyle: 'innerHTML' });
        if (respuesta.ok && destino === 'contenido') {
          anunciarCorte();
        }
      } else if (tipo.startsWith('text/plain')) {
        mostrarProblema(texto);
      }
    } catch (error) {
      // Sin respuesta (se cortó la conexión): la persona puede volver a intentarlo. El texto del
      // aviso lo debe entregar el servidor; ver el reporte de T-001-68.
    } finally {
      // Si la vista no cambió (rechazo o fallo), el formulario sigue ahí: se deja como estaba.
      if (formulario.isConnected) {
        boton.disabled = false;
        if (estado) {
          estado.textContent = '';
        }
      }
    }
  }

  document.addEventListener('submit', function (evento) {
    const formulario = evento.target;
    if (formulario instanceof Element && formulario.matches('form[data-egm-carga]')) {
      evento.preventDefault();
      enviarCarga(formulario);
    }
  });

  // --- htmx: ficha en cada petición, respuestas con cuerpo y foco -------------------------------

  // La ficha viaja en la cabecera `X-EGM-Sesion` de toda petición de htmx (ADR-003, punto 4).
  document.addEventListener('htmx:configRequest', function (evento) {
    const ficha = leerFicha();
    if (ficha) {
      evento.detail.headers[CABECERA_SESION] = ficha;
    }
  });

  // htmx no intercambia por defecto las respuestas 4xx. Las de la herramienta traen un fragmento
  // válido y la cabecera `X-EGM-Destino`: se colocan donde esa cabecera indica.
  document.addEventListener('htmx:beforeSwap', function (evento) {
    const xhr = evento.detail.xhr;
    const destino = xhr ? xhr.getResponseHeader(CABECERA_DESTINO) : null;
    if (!DESTINOS.includes(destino)) {
      return;
    }
    const sitio = document.getElementById(destino);
    if (sitio) {
      evento.detail.shouldSwap = true;
      evento.detail.isError = false;
      evento.detail.target = sitio;
    }
  });

  // Una vez colocado un fragmento: el foco pasa al elemento marcado y, si la vista ya no tiene
  // matriz, la ficha deja de servir. Los intercambios fuera de banda (cabecera y colofón) también
  // disparan este evento: solo cuentan los de #contenido y #mensajes.
  document.addEventListener('htmx:afterSettle', function (evento) {
    const sitio = evento.target;
    if (!(sitio instanceof Element)) {
      return;
    }
    if (sitio.id === 'contenido') {
      // La cabecera corrida lleva «Descartar el archivo» solo si hay una matriz abierta.
      if (!document.querySelector('[data-egm-descartar]')) {
        borrarFicha();
        detenerCuenta();
        vaciarAnuncio();
      } else {
        anclar(); // la respuesta del servidor contó como actividad
      }
      enfocar(sitio);
    } else if (sitio.id === 'mensajes') {
      enfocar(sitio);
    }
  });

  // «Descartar el archivo» (`POST /sesion/descartar`, que htmx envía con la ficha): al terminar la
  // sesión con éxito, la ficha de la pestaña se borra y los avisos se detienen.
  document.addEventListener('htmx:afterRequest', function (evento) {
    const origen = evento.detail.elt;
    if (
      evento.detail.successful &&
      origen instanceof Element &&
      origen.closest('[data-egm-descartar]')
    ) {
      borrarFicha();
      detenerCuenta();
      vaciarAnuncio();
    }
  });

  // Un error interno del servidor trae un texto fijo en texto plano: se muestra como alerta.
  document.addEventListener('htmx:responseError', function (evento) {
    const xhr = evento.detail.xhr;
    const tipo = xhr.getResponseHeader('Content-Type') || '';
    if (tipo.startsWith('text/plain') && !xhr.getResponseHeader(CABECERA_DESTINO)) {
      mostrarProblema(xhr.responseText);
    }
  });

  // --- Fin de la sesión: actividad, latido, aviso de cierre, E7 y E8 -----------------------------

  /** Hay sesión abierta en esta pestaña: la ficha existe y la cabecera trae el aviso E7. */
  function haySesion() {
    return leerFicha() !== '' && document.querySelector('[data-egm-aviso]') !== null;
  }

  // `ancla`: la última vez que el servidor confirmó actividad con la ficha (respuesta de un
  // latido, de una carga o de un fragmento). Los avisos se cuentan desde ahí, porque el servidor
  // mide sus 45 minutos desde su último latido o petición, no desde la última interacción.
  let ancla = 0;
  let ultimoLatido = 0;
  let temporizadorLatido = 0;
  let temporizadorAviso = 0;
  let temporizadorFin = 0;
  let temporizadorCuenta = 0;

  function detenerCuenta() {
    window.clearTimeout(temporizadorAviso);
    window.clearTimeout(temporizadorFin);
    window.clearTimeout(temporizadorCuenta);
    window.clearTimeout(temporizadorLatido);
    temporizadorAviso = temporizadorFin = temporizadorCuenta = temporizadorLatido = 0;
  }

  /** Formatea los milisegundos que faltan como `m:ss`. */
  function formatearRestante(ms) {
    const total = Math.max(0, Math.ceil(ms / 1000));
    const segundos = total % 60;
    return Math.floor(total / 60) + ':' + (segundos < 10 ? '0' : '') + segundos;
  }

  function actualizarTemporizador() {
    const aviso = document.querySelector('[data-egm-aviso]');
    const reloj = document.querySelector('[data-egm-temporizador]');
    window.clearTimeout(temporizadorCuenta);
    temporizadorCuenta = 0;
    if (!aviso || aviso.hidden) {
      return;
    }
    if (reloj) {
      reloj.textContent = formatearRestante(ancla + INACTIVIDAD_MS - Date.now());
    }
    temporizadorCuenta = window.setTimeout(actualizarTemporizador, 1000);
  }

  function mostrarAviso() {
    temporizadorAviso = 0;
    if (!haySesion()) {
      return;
    }
    if (Date.now() - ancla < AVISO_MS) {
      programarCuenta(); // el reloj se adelantó o la cuenta se movió: se vuelve a calcular
      return;
    }
    const aviso = document.querySelector('[data-egm-aviso]');
    if (aviso && aviso.hidden) {
      aviso.hidden = false; // role="alert": el lector de pantalla lo anuncia; el foco no se mueve
    }
    actualizarTemporizador();
  }

  /** Oculta E7; si el foco estaba dentro, lo pasa a la vista en curso para que no se pierda. */
  function ocultarAviso() {
    const aviso = document.querySelector('[data-egm-aviso]');
    window.clearTimeout(temporizadorCuenta);
    temporizadorCuenta = 0;
    if (!aviso || aviso.hidden) {
      return;
    }
    const teniaElFoco = aviso.contains(document.activeElement);
    aviso.hidden = true;
    if (teniaElFoco) {
      enfocar(document.getElementById('contenido'));
    }
  }

  /** Los 45 minutos se cumplieron: se pide la vista de carga, que trae E8 si el servidor la cerró. */
  function finDeSesion() {
    temporizadorFin = 0;
    if (!haySesion()) {
      return;
    }
    if (Date.now() - ancla < INACTIVIDAD_MS) {
      programarCuenta();
      return;
    }
    sesionTerminada();
  }

  /** La sesión ya no existe en el servidor: se vuelve a la carga (E8 si fue por inactividad). */
  function sesionTerminada() {
    detenerCuenta();
    ocultarAviso();
    if (window.htmx) {
      window.htmx
        .ajax('GET', RUTA_INICIO, { target: '#contenido', swap: 'innerHTML' })
        .catch(function () {
          // Sin respuesta: la ficha ya no sirve; la próxima carga abrirá una sesión nueva.
          borrarFicha();
        });
    }
  }

  /** Programa E7 y E8 a partir de `ancla`. */
  function programarCuenta() {
    window.clearTimeout(temporizadorAviso);
    window.clearTimeout(temporizadorFin);
    temporizadorAviso = temporizadorFin = 0;
    if (!haySesion()) {
      ocultarAviso();
      return;
    }
    const ahora = Date.now();
    temporizadorAviso = window.setTimeout(mostrarAviso, Math.max(0, ancla + AVISO_MS - ahora));
    temporizadorFin = window.setTimeout(finDeSesion, Math.max(0, ancla + INACTIVIDAD_MS - ahora));
  }

  /** El servidor acaba de contar actividad con la ficha: la cuenta de los avisos empieza de nuevo. */
  function anclar() {
    ancla = Date.now();
    programarCuenta();
  }

  /** `POST /sesion/latido` con la ficha; 204 reinicia la cuenta y 410 dice que la sesión terminó. */
  async function enviarLatido() {
    const ficha = leerFicha();
    window.clearTimeout(temporizadorLatido);
    temporizadorLatido = 0;
    if (!ficha) {
      return;
    }
    ultimoLatido = Date.now();
    try {
      const respuesta = await window.fetch(RUTA_LATIDO, {
        method: 'POST',
        headers: { [CABECERA_SESION]: ficha },
        cache: 'no-store',
        credentials: 'same-origin',
      });
      if (respuesta.status === 204) {
        anclar(); // se mide al recibir la respuesta: nunca antes de lo que contó el servidor
      } else if (respuesta.status === 410 && leerFicha() === ficha) {
        sesionTerminada();
      }
    } catch (error) {
      // Sin respuesta: la siguiente actividad lo vuelve a intentar.
    }
  }

  /**
   * Latido como máximo una vez por minuto: el primero tras un silencio sale ya; el resto, al
   * cumplirse el minuto, un solo latido que recoge toda la actividad del intervalo.
   */
  function solicitarLatido() {
    const desdeElUltimo = Date.now() - ultimoLatido;
    if (desdeElUltimo >= LATIDO_MS) {
      enviarLatido();
    } else if (!temporizadorLatido) {
      temporizadorLatido = window.setTimeout(enviarLatido, LATIDO_MS - desdeElUltimo);
    }
  }

  /**
   * Puntero, teclado, toque, foco y desplazamiento cuentan como actividad (ADR-003, punto 5) y
   * retiran el aviso E7.
   */
  let ultimoX = -1;
  let ultimoY = -1;

  function alActividad(evento) {
    if (!haySesion()) {
      return;
    }
    if (evento && evento.type === 'pointermove') {
      // Un movimiento que no cambia de lugar (el navegador los emite al cambiar el diseño de la
      // página) no es una interacción de la persona.
      if (evento.clientX === ultimoX && evento.clientY === ultimoY) {
        return;
      }
      ultimoX = evento.clientX;
      ultimoY = evento.clientY;
    }
    ocultarAviso();
    solicitarLatido();
  }

  ['pointerdown', 'pointermove', 'keydown', 'touchstart', 'focusin', 'focus', 'scroll'].forEach(
    function (tipo) {
      window.addEventListener(tipo, alActividad, { capture: true, passive: true });
    }
  );

  // «Seguir con la sesión»: lo mismo que cualquier otra interacción, también si el clic llega sin
  // que antes llegue un movimiento (por ejemplo, desde un lector de pantalla).
  document.addEventListener('click', function (evento) {
    const origen = evento.target;
    if (origen instanceof Element && origen.closest('[data-egm-seguir]')) {
      alActividad();
    }
  });

  // Aviso de cierre: al ocultarse la página para descargarla (cerrar la pestaña, recargar o
  // navegar), no al cambiar de pestaña. La ficha va en la petición; `keepalive` deja que termine
  // aunque la página ya no exista. Si la ficha vuelve en 10 s (recarga), el servidor no borra.
  window.addEventListener('pagehide', function () {
    const ficha = leerFicha();
    if (!ficha) {
      return;
    }
    try {
      window
        .fetch(RUTA_CIERRE, {
          method: 'POST',
          headers: { [CABECERA_SESION]: ficha },
          keepalive: true,
          cache: 'no-store',
          credentials: 'same-origin',
        })
        .catch(function () {
          // la página ya se va: nada más que hacer
        });
    } catch (error) {
      // sin red: el servidor la cerrará por inactividad
    }
  });

  // Una página que vuelve del historial rápido del navegador sigue con su ficha: lo avisa con un
  // latido para anular el aviso de cierre que dio al irse.
  window.addEventListener('pageshow', function (evento) {
    if (evento.persisted) {
      enviarLatido();
    }
  });

  // --- Arranque: E9 «Recuperando su sesión» ----------------------------------------------------

  /**
   * `GET /` trae la página con el estado de recarga vacío. Con ficha en la pestaña se pide el
   * resultado (E9: «Recuperando su sesión.»); sin ficha, la vista de carga. Si la sesión ya no
   * existe, el servidor devuelve la vista de carga sin mensaje.
   */
  function iniciar() {
    const estado = document.getElementById('estado-pagina');
    if (!estado || !window.htmx) {
      return;
    }
    const recuperando = leerFicha() !== '';
    if (recuperando) {
      estado.textContent = estado.getAttribute('data-egm-texto-recuperando') || '';
    }
    window.htmx
      .ajax('GET', recuperando ? RUTA_RESULTADO : RUTA_INICIO, {
        target: '#contenido',
        swap: 'innerHTML',
      })
      .then(function () {
        if (recuperando) {
          anunciarCorte();
          // La ficha volvió: un latido propio anula el aviso de cierre que la página anterior
          // pudo dar al irse, aunque su petición llegara después de esta.
          if (haySesion()) {
            enviarLatido();
          }
        }
      })
      .catch(function () {
        // Sin respuesta: se quita el aviso de recarga para no dejarlo fijo.
        estado.textContent = '';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
