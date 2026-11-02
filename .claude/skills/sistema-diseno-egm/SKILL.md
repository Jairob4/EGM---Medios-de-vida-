---
name: sistema-diseno-egm
description: Sistema de diseño «Fichero» de la web del EGM — concepto, tokens de color y tipografía, retícula, componentes (mapa-cajonera, ficha, notas al margen, colofón) y reglas de accesibilidad. Usar al diseñar flujos, bocetos, plantillas, CSS o cualquier vista de la aplicación.
---

# Sistema de diseño «Fichero»

## Tema, público y tarea

- **Tema**: un estado del arte sobre reparación de medios de vida de víctimas del conflicto en Colombia.
  Tono sobrio y respetuoso: es investigación sobre víctimas, no un producto comercial.
- **Público**: equipo de investigación multidisciplinario (no ingeniería), evaluadores académicos.
- **Tarea principal**: mostrar dónde hay estudios y dónde no, y permitir comprobar cada cifra.

## Concepto

La matriz es, literalmente, un **fichero bibliográfico**: una ficha por documento. La web adopta el
vocabulario del fichero de biblioteca:

- el **mapa es una cajonera**: cada cruce intervención × dimensión es un cajón; el número de estudios
  es cuántas fichas contiene; un cajón vacío es una brecha;
- abrir un cajón muestra sus **fichas** (detalle de los estudios), con el rayado de una ficha de catálogo;
- las cifras del tablero llevan **notas al margen** que remiten a las fichas que las producen.

Lo memorable es **una sola cosa**: la cajonera como pieza principal de la página. Todo lo demás es
silencioso y disciplinado.

## Decisiones (y qué se evitó a propósito)

| Eje | Decisión | Se evita |
|---|---|---|
| Color | Blanco de ficha, tinta azul-negra, rayado azul pálido; el rojo de la línea de cabecera de la ficha es el **único acento** y marca solo la selección actual | fondo crema + acento terracota; negro teñido con acento ácido |
| Evidencia | Escala **ordinal de un solo tono** (tinta): más oscuro = mayor nivel en la jerarquía del equipo, más forma/borde para no depender del color | paletas categóricas arcoíris; verde/rosado como juicio de valor |
| Brecha | Cajón vacío con contorno discontinuo y la leyenda «ningún estudio registrado»; nunca rojo (no es un error) | rosado o rojo de alarma |
| Tipografía | Alegreya (texto y títulos) y Alegreya Sans (interfaz), de Huerta Tipográfica (Argentina), pensadas para textos literarios y académicos | serif de display de alto contraste genérica; monoespaciada para etiquetas |
| Estructura | Numeración de secciones solo donde hay secuencia real (pasos de lectura del mapa) | etiquetas en mayúsculas sobre cada título; cadenas con puntos medios; flechas en cada enlace |
| Movimiento | Un único movimiento: el cajón se abre (la ficha entra desde el margen) al seleccionar una celda; respeta `prefers-reduced-motion` | animaciones de entrada por sección |

Tokens completos: `references/tokens.md`. Pie de página: `references/pie-de-pagina.md`.

## Componentes

1. **Cabecera corrida** (como la de una revista): título corto de la herramienta a la izquierda; a la
   derecha el corte de datos («Matriz v4, 27 documentos, leída el …»), siempre visible.
2. **Cajonera (mapa)**: filas = intervenciones, columnas = dimensiones, leídas de la matriz.
   Dentro de cada cajón, una burbuja por nivel de evidencia presente, ordenadas por jerarquía;
   **área** proporcional al número de estudios: $r \propto \sqrt{n}$. El número siempre visible junto a
   la burbuja (no solo en el tooltip).
3. **Ficha** (panel de detalle): fondo con el rayado de ficha de catálogo; por estudio: N.º en la matriz,
   referencia APA, año, nivel de evidencia, tipo de fuente.
4. **Notas al margen**: en pantallas anchas, columna derecha con la procedencia de cada cifra
   («3 estudios: N.º 7, 10, 15»); en móvil, se despliegan bajo la cifra.
5. **Filtros**: tipo de fuente, metodología, nivel de evidencia, año. Los filtros activos se resumen en
   una frase legible encima del mapa («Mostrando solo fuentes territoriales desde 2015»).
6. **Conclusiones**: frases en lenguaje llano, cada una con su conteo y su nota al margen.
7. **Colofón** (pie de página): ver referencia.

## Reglas de calidad

- WCAG 2.2 AA: contraste ≥ 4.5:1 en texto; la cajonera es navegable con teclado (patrón `grid` de
  WAI-ARIA) y cada cajón tiene etiqueta accesible («Acompañamiento técnico por Humano: 1 estudio»).
- Nunca codificar información solo con color: nivel de evidencia = tono + estilo de borde + leyenda.
- Funciona desde 360 px de ancho: en móvil la cajonera permite desplazamiento horizontal con la columna
  de intervenciones fija.
- Textos de interfaz: de usted, frase en mayúscula inicial, verbos concretos («Abrir fichas»,
  «Descargar mapa»), sin jerga. Los mensajes vacíos orientan: «Ningún estudio cumple estos filtros.
  Quite el filtro de año para ver más».
- Revisar cada vista con captura de pantalla antes de darla por terminada, en claro y oscuro, en 360 px
  y 1440 px.
