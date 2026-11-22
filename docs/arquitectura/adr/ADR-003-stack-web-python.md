# ADR-003: Stack web en Python con control total de HTML y CSS

**Fecha**: 2026-11-21 · **Estado**: aceptado, 2026-11-21 [Fuente: decisión de Jairo, 21-nov-2026]
**Requisitos que la motivan**: NFR-000-03, NFR-000-04, NFR-000-06, NFR-000-05, NFR-000-10, NFR-000-13, NFR-000-14, NFR-000-15,
NFR-000-17, NFR-000-18, NFR-000-19, FR-001-20, FR-001-28, FR-001-29, FR-002-15, FR-002-16, FR-002-19, FR-003-03,
SC-000-04, SC-000-13, SC-000-17, SC-000-18, SC-002-04

> **Nota de revisión, 2026-11-22 (COR-012, F2-07).** Qué cambió: la verificación de NFR-000-19 en «Consecuencias»
> nombra también el límite de contenido descomprimido, que fija ADR-004, punto 5. La decisión de este ADR no cambia.
>
> **Nota de revisión, 2026-11-22 (COR-013, O-2 y F3-16).** Qué cambió: el punto 2 ya no dice que todo funcione sin el guion; aclara que los controles son elementos reales de HTML que htmx envía con la ficha de sesión del punto 4 y que la carga y la sesión necesitan el guion, como ya exigían los puntos 3 y 4. La decisión de este ADR no cambia.

## Contexto

- Aplicación web; análisis y tablero con filtros en Python (restricciones 1 y 2 de `000`; decisión de Jairo,
  31-oct-2026). Entorno `.venv` con Python 3.13.
- El diseño «Fichero» (skill `sistema-diseno-egm`) no puede ser genérico (NFR-000-13): cajonera con patrón `grid` de
  WAI-ARIA, fichas con rayado, notas al margen, colofón de libro, un solo movimiento. Exige escribir el HTML y el CSS a
  mano.
- Requisitos que condicionan el stack:
  - **Sesión efímera sin persistencia** (NFR-000-17, NFR-000-18): archivo solo en memoria, nada en disco ni en registros,
    sesiones independientes; fin al descartar, al cerrar la pestaña, a los 45 min sin interacción (fijo) o con un error
    de contrato.
  - **Carga desde el navegador con validación de tipo y tamaño** antes de leer, límite fijo de 15 728 640 bytes
    (NFR-000-19, FR-001-20, FR-001-29).
  - **Actividad** = cualquier interacción con la página, incluido pasar el cursor sobre una burbuja (US-001-5.4), que no
    tiene por qué generar una petición.
  - **Filtros** con un solo «Actualizar vista» y un solo «Restablecer», comunes a mapa y tablero, con estado compartido;
    mover un control no filtra (FR-002-15, FR-002-19).
  - **Accesibilidad** WCAG 2.2 AA, todo con teclado, 360 px (NFR-000-04, NFR-000-05, SC-002-04).
  - **Exportación** de imagen y tabla (FR-002-16).
- **Plazo**: entrega el 6-dic-2026, quince días desde hoy, con tres specs (001 a 003) y un plan por spec.
- Hecho técnico: el analizador multiparte de Starlette (base de FastAPI) guarda cada archivo recibido en un archivo
  temporal que pasa a disco cuando supera 1 MiB; Werkzeug (Flask) hace algo equivalente. Shiny para Python guarda los
  archivos subidos en una carpeta temporal en disco. Por eso, en cualquier opción con servidor, la carga debe leerse
  como cuerpo crudo en memoria.

## Opciones consideradas

Criterios: S = sesión efímera sin disco; C = carga con validación previa; I = 45 min de inactividad con actividad del
cliente; F = filtros con «Actualizar vista» y «Restablecer» compartidos; A = accesibilidad AA y teclado; D = diseño
«Fichero» con HTML y CSS propios; P = alcanzable para el 6-dic-2026. ● cumple con facilidad; ◐ cumple con trabajo
adicional o riesgo; ○ no cumple o lo impide.

| Opción | S | C | I | F | A | D | P |
|---|---|---|---|---|---|---|---|
| **A. FastAPI (Starlette) + Jinja2 + htmx, HTML/CSS propios, sesiones en memoria** | ● | ● | ◐ | ● | ● | ● | ● |
| B. Flask + Jinja2 + htmx | ● | ● | ◐ | ● | ● | ● | ● |
| C. Streamlit | ◐ | ◐ | ○ | ◐ | ○ | ○ | ● |
| D. Dash (Plotly) | ◐ | ◐ | ◐ | ● | ◐ | ◐ | ◐ |
| E. Shiny para Python | ○ | ◐ | ◐ | ● | ◐ | ◐ | ◐ |
| F. Python en el navegador (Pyodide) con HTML/CSS propios, sin servidor de aplicación | ● | ● | ● | ● | ● | ● | ○ |

| Opción | A favor | En contra |
|---|---|---|
| A | HTML semántico escrito a mano: control total del DOM, de ARIA y del CSS. Sin compilación de front-end. Lectura del cuerpo en flujo con corte por tamaño, nativa en ASGI. Cliente de pruebas incluido. Jinja2 también sirve para las plantillas de exportación | La sesión en memoria y la actividad del cliente se escriben a mano (unas decenas de líneas de JavaScript). Hay que evitar el analizador multiparte |
| B | Igual de capaz que A; muy documentado | Sincrónico: leer el cuerpo en flujo es posible pero menos directo; sin ventaja frente a A |
| C | Muy rápido para prototipos | Estética y DOM propios de la biblioteca: no permite «Fichero» (NFR-000-13). Re-ejecuta el guion en cada interacción. Sin control del teclado ni del patrón `grid`. La sesión vive mientras dure la conexión, sin reglas de inactividad propias |
| D | Filtros y estado bien resueltos; gráficos | Componentes React propios: el HTML de la cajonera exigiría un componente a medida compilado. Accesibilidad dispar entre componentes. La carga viaja en base64 por el estado de la aplicación |
| E | Modelo reactivo claro; sesión = conexión (cerrar la pestaña la termina) | Guarda los archivos subidos en disco (viola NFR-000-17 salvo un componente propio). Basado en Bootstrap: requiere deshacer su estilo |
| F | El archivo nunca sale del navegador: NFR-000-17 y NFR-000-18 casi por construcción. Despliegue como archivos estáticos | Descarga y arranque del intérprete (decenas de MB, varios segundos). Depuración y pruebas de la capa de interfaz más difíciles. Riesgo alto para quince días. Separa menos limpiamente núcleo y vista |

## Decisión

**Opción A: FastAPI + Jinja2 + htmx, servida por Uvicorn en local** [Fuente: decisión de Jairo, 21-nov-2026]. Es la
única que cumple a la vez el control total del HTML y el CSS (NFR-000-13, NFR-000-04) y el plazo, con el menor riesgo
técnico.

Concreción:

1. **Servidor**: FastAPI sobre Starlette, servido por Uvicorn en un solo proceso (el almacén de sesiones vive en su
   memoria; ADR-004). Plantillas Jinja2 con autoescape. Versiones fijadas en el archivo de dependencias del plan 001,
   compatibles con Python 3.13.
2. **Interacción**: htmx para enviar «Actualizar vista», «Restablecer», abrir un cajón o una ficha y reemplazar los
   fragmentos de mapa, tablero y avisos en una sola respuesta. Los controles son formularios, botones y enlaces reales
   de HTML (semántica, teclado y accesibilidad); htmx los envía con la ficha de sesión del punto 4 y evita recargar la
   página. La herramienta necesita el guion activo: la carga (punto 3) y la sesión (punto 4) dependen de él.
3. **Carga**: `app.cliente` envía el archivo con una petición cuyo cuerpo son los bytes del archivo y cuyo nombre va en
   una cabecera (codificado). `app.carga` lee el flujo contando bytes y corta al pasar `LIMITE_BYTES`; nunca usa el
   analizador multiparte. Ningún archivo temporal.
4. **Sesión**: ficha aleatoria guardada en el almacenamiento de la pestaña (no en cookie), enviada en una cabecera en
   cada petición. Al cerrar la pestaña la ficha desaparece y la sesión no se puede reabrir (US-001-5.2, SC-000-17); un
   aviso de cierre al ocultarse la página hace que el servidor la borre pasado el período de gracia (punto 9). Las
   cookies se descartan porque se comparten entre pestañas y sobreviven al cierre de una pestaña, lo que permitiría
   reabrir la sesión.
5. **Actividad**: el cliente escucha puntero, teclado, toque, foco y desplazamiento y envía un latido como máximo una
   vez por minuto (el primero tras un silencio sale de inmediato); el servidor mide los 45 minutos desde el último
   latido o petición.
6. **Recursos locales**: htmx, el guion propio, el CSS y las tipografías Alegreya y Alegreya Sans (licencia SIL Open
   Font License) se sirven desde la propia aplicación. Ningún recurso externo ni red de distribución: la demostración
   funciona sin internet y ningún tercero recibe peticiones. Política de seguridad de contenido restrictiva, sin
   estilos en línea. Consecuencias para las plantillas, señaladas por el `disenador-front` en `docs/interfaz/flujos.md`
   §7, punto 7 [Fuente: decisión de Jairo, 21-nov-2026]:
   - El radio de cada burbuja ($r \propto \sqrt{n}$) va como atributo del SVG (`r`), no por `style`.
   - El ancho de la cajonera y su número de columnas salen del número de dimensiones leídas del archivo, que entrega el
     modelo de vista del mapa (M17); nunca se fijan en 8 ni en otro número escrito en la hoja de estilo (NFR-000-06).
     Se expresan sin estilos en línea: por atributos o `viewBox` del SVG, o por reglas de CSS que no fijen el número de
     columnas. La técnica la elige el `disenador-front` dentro de esa regla.
7. **Exportación** (FR-002-16; antes NC-ADR003-1) [Fuente: decisión de Jairo, 21-nov-2026]:
   - **Mapa**: PNG como formato principal y SVG como formato adicional. `app.exportacion` (M20) genera en Python el SVG
     desde el modelo de vista del mapa visible (vectorial, con texto real, no captura) y lo entrega; `app.cliente` (M19)
     lo convierte en PNG en el navegador, sin otra petición de datos, de modo que ambos muestran lo mismo. El servidor no
     produce PNG [Fuente: decisión de Jairo, 21-nov-2026, NC-INT-4].
   - **Tabla de conteos**: libro `.xlsx` nuevo, generado en memoria, con los filtros activos, el nombre del archivo y la
     fecha de lectura en la cabecera de la hoja, encima de la tabla.
   - Nada se escribe en disco y nunca se escribe en la matriz cargada (NFR-000-01, NFR-000-17).
8. **Pruebas**: `pytest` e `hypothesis` (propiedades) para el núcleo; cliente de pruebas de la aplicación para rutas
   y sesiones; navegador automatizado con una revisión automática de accesibilidad para escenarios de interfaz y para
   SC-000-04 y SC-000-05, complementada con revisión manual. Las herramientas exactas las fija el plan 001.
9. **Recarga de la página** (NFR-000-17; antes NC-ADR003-2) [Fuente: decisión de Jairo, 21-nov-2026]: recargar la
   página no termina la sesión. Tras el aviso de cierre, el servidor espera un período de gracia de 10 segundos antes de
   borrar la sesión; si la misma pestaña vuelve con su ficha dentro de ese plazo (recarga), la sesión sigue. Cerrar la
   pestaña sí la termina: la ficha desaparece con la pestaña y, pasados los 10 segundos, el servidor borra la sesión. La
   búsqueda de marcadores de SC-000-17 tras cerrar la pestaña se hace pasado ese plazo. Una pestaña duplicada por el
   navegador copia la ficha y comparte la sesión; se acepta como limitación conocida de la versión local.

## Consecuencias

- Positivas:
  - HTML y CSS bajo control total: el `disenador-front` entrega plantillas y CSS que se usan tal cual (NFR-000-13).
  - Sin compilación de JavaScript ni dependencias de Node: menos riesgo para el 6-dic-2026.
  - El núcleo no conoce la web; la web solo llama a `egm.procesamiento` y a las funciones de cálculo (NFR-000-14).
  - Sesiones independientes por pestaña y nada en disco (NFR-000-17, NFR-000-18).
- Negativas / deuda aceptada:
  - Un solo proceso: el almacén en memoria no se reparte entre procesos. Suficiente para la versión local; un despliegue
    con varios usuarios debe revisarlo (ADR-004).
  - Unas decenas de líneas de JavaScript propio (carga, ficha, actividad, cierre, foco) que necesitan pruebas en
    navegador.
  - La pestaña duplicada comparte sesión (punto 9).
  - Durante los 10 segundos de gracia tras cerrar la pestaña, la sesión sigue en la memoria del servidor, aunque nadie
    puede reabrirla sin la ficha.
- Requisitos afectados y cómo se verifican:
  - NFR-000-17: SC-000-17 con una matriz sintética con marcadores, terminando la sesión de las cuatro formas y buscando
    los marcadores en la carpeta temporal del sistema, en la carpeta de la aplicación y en los registros.
  - NFR-000-18: SC-000-18 con dos pestañas o dos navegadores.
  - NFR-000-19: SC-000-19 con archivos de 15 728 640 bytes y de un byte más, y con un libro dentro de ese tamaño cuyo
    contenido descomprimido declarado es igual al límite de NFR-000-19 y otro con un byte más (ADR-004, punto 5;
    US-001-4.13).
  - NFR-000-04, NFR-000-05, SC-002-04: revisión automática y manual en navegador, a 360 px y solo con teclado.
  - FR-002-19: US-002-4.10 y US-003-5.4 (mover un control no cambia la vista).
  - FR-002-16: la exportación produce PNG (en el navegador, desde el SVG), SVG y `.xlsx` con los filtros activos, el
    nombre del archivo y la fecha de lectura, y sus conteos coinciden con el mapa visible (SC-002-05).
  - NFR-000-06 en la cajonera: con un fixture de más o menos dimensiones que la v4, la cajonera muestra todas las
    columnas sin desbordar ni dejar columnas vacías; la hoja de estilo no contiene un número fijo de columnas.
  - Recarga: una recarga dentro de los 10 segundos conserva la sesión; un cierre de pestaña la termina pasado ese plazo.
  - NFR-000-13: SC-000-13, aprobación de Jairo vista por vista.
