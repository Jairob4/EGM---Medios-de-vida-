// Boceto: comportamiento mínimo para revisar con teclado. No calcula ni dibuja datos.
// En app/ este papel lo cumplen htmx y app.cliente (M19); aquí solo se simula.
(function () {
  "use strict";
  // Tema para la revisión: ?tema=oscuro o ?tema=claro (por defecto, el del sistema).
  var tema = new URLSearchParams(location.search).get("tema");
  if (tema === "oscuro" || tema === "claro") document.documentElement.setAttribute("data-tema", tema);

  // Cajonera: patrón grid de WAI-ARIA con foco itinerante (un solo tabulador entra al mapa).
  document.querySelectorAll('[role="grid"]').forEach(function (grid) {
    var filas = Array.prototype.slice.call(grid.querySelectorAll('[role="row"]'));
    // Una entrada por celda; la esquina vacía queda como null para alinear columnas.
    var matriz = filas.map(function (f) {
      return Array.prototype.slice.call(f.children).map(function (celda) { return celda.querySelector("button"); });
    });
    var todos = [].concat.apply([], matriz).filter(Boolean);
    todos.forEach(function (b) { b.tabIndex = -1; });
    var inicial = grid.querySelector('[aria-selected="true"] button') || matriz[1][1] || todos[0];
    inicial.tabIndex = 0;
    function mover(f, c) {
      f = Math.max(0, Math.min(matriz.length - 1, f));
      c = Math.max(0, Math.min(matriz[f].length - 1, c));
      if (!matriz[f][c]) c = c + 1 < matriz[f].length ? c + 1 : c - 1; // salta la esquina
      if (!matriz[f][c]) return;
      todos.forEach(function (b) { b.tabIndex = -1; });
      matriz[f][c].tabIndex = 0; matriz[f][c].focus();
    }
    grid.addEventListener("keydown", function (e) {
      var f = -1, c = -1;
      matriz.forEach(function (fila, i) { var j = fila.indexOf(document.activeElement); if (j >= 0) { f = i; c = j; } });
      if (f < 0) return;
      var k = e.key;
      if (k === "ArrowRight") mover(f, c + 1);
      else if (k === "ArrowLeft") mover(f, c - 1);
      else if (k === "ArrowDown") mover(f + 1, c);
      else if (k === "ArrowUp") mover(f - 1, c);
      else if (k === "Home") e.ctrlKey ? mover(0, 0) : mover(f, 0);
      else if (k === "End") e.ctrlKey ? mover(matriz.length - 1, matriz[f].length - 1) : mover(f, matriz[f].length - 1);
      else return;
      e.preventDefault();
    });
    // Abrir un cajón: marca la selección (línea roja). En app/, htmx trae las fichas al margen.
    grid.addEventListener("click", function (e) {
      var b = e.target.closest("button.cajon");
      if (!b) return;
      grid.querySelectorAll('[aria-selected="true"]').forEach(function (td) { td.setAttribute("aria-selected", "false"); });
      b.parentElement.setAttribute("aria-selected", "true");
      var aviso = document.getElementById("anuncio");
      if (aviso) aviso.textContent = "Fichas de " + b.getAttribute("aria-label") + " abiertas en el margen.";
    });
  });

  // Definiciones: el botón del encabezado muestra u oculta su definición.
  document.querySelectorAll("button.encabezado[aria-controls]").forEach(function (b) {
    b.addEventListener("click", function () {
      var panel = document.getElementById(b.getAttribute("aria-controls"));
      var abierto = b.getAttribute("aria-expanded") === "true";
      document.querySelectorAll("button.encabezado[aria-expanded='true']").forEach(function (o) { o.setAttribute("aria-expanded", "false"); });
      b.setAttribute("aria-expanded", abierto ? "false" : "true");
      if (panel) {
        panel.hidden = abierto;
        var nombre = panel.querySelector("[data-nombre]");
        if (nombre) nombre.textContent = b.textContent.trim();
      }
    });
  });
})();
