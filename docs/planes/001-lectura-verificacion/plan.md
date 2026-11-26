# Plan de implementación: 001-lectura-verificacion

**Creado**: 2026-11-22 · **Estado**: aprobado por Jairo el 2026-11-22 (COR-013 verificada)
**Spec**: [`docs/specs/001-lectura-verificacion/spec.md`](../../specs/001-lectura-verificacion/spec.md)
**Arquitectura**: `docs/arquitectura/arquitectura.md` §4, §5, §6 (M01 a M05, M07, M08, M10, M13 a M19, M21 a M23), §6.4, §9 · **ADR relacionados**: ADR-001, ADR-002, ADR-003, ADR-004, ADR-005
**Ubicación de este plan**: `docs/planes/001-lectura-verificacion/plan.md`

<!--
  Plan POR SPEC (decisión de Jairo, 21-nov-2026). Documento interno para Jairo y los subagentes; no es texto de
  interfaz. No contiene código. Reglas: CLAUDE.md y skills `plan-modulo`, `trazabilidad`, `calidad-python`.
-->

## Resumen

El spec 001 pide que la herramienta reciba la matriz desde el navegador, la compruebe antes de leerla, descubra su
estructura por el texto de los encabezados y las validaciones, lea todas sus filas, cuente estudios distintos por cruce
de intervención y dimensión con la lista de N.º de cada conteo, emita advertencias y notas legibles sin corregir nada,
se detenga solo ante la lista cerrada de errores de contrato, contraste sus conteos con las tablas comparables 1, 2 y 4
de la hoja EGM y viva solo durante la sesión.

Enfoque técnico (arquitectura §5 y ADR-001 a ADR-005): núcleo Python puro en `src/egm/` (M01 a M05, M07, M08, M10,
M13) con una fachada única `egm.procesamiento.procesar(bytes, nombre, fecha)` que devuelve `ResultadoLectura`,
`Rechazo` o `FalloContrato`; capa web FastAPI + Jinja2 + htmx en un solo proceso local (M14 a M19, M21, M22) con la
carga como cuerpo crudo, sesiones en memoria por pestaña y nada en disco; constructor de matrices sintéticas M23 para
todas las pruebas.

**Orden por plazo (entrega el 6-dic-2026).** El plan pone primero todo el núcleo (historias 1, 2 y 3 y la fachada) y
cierra con el **hito N1, «núcleo listo»**: desde ahí los planes 002 y 003 pueden consumir `procesar`, el modelo, el
esquema, el corpus y los conteos sin esperar a la web. Después vienen la carga (historia 4, hito N2, «base web lista»)
y la sesión (historia 5). Esto altera el orden de prioridad del spec (la historia 3 es P2 y la 4 es P1) por una
dependencia técnica: la vista que deja la carga muestra el resultado de la verificación antes de los resultados
(FR-001-18), así que la carga necesita la verificación terminada.

## Contexto técnico

**Lenguaje/versión**: Python 3.13 en `.venv` (ADR-003, ADR-004 punto 2). El `.venv` del repositorio ya existe con
Python 3.13.15 (`.venv/pyvenv.cfg`); T-001-02 lo confirma o lo recrea y la versión se registra en el resumen de fase
(`calidad-python`; `000`, «Notas sobre las fuentes»).
**Dependencias principales**: núcleo: `openpyxl` (única dependencia del núcleo; 3.1.5 instalada hoy en el `.venv`).
Web: FastAPI, Starlette, Jinja2, Uvicorn (ADR-003 punto 1); htmx y el guion propio servidos localmente (ADR-003
punto 6). Desarrollo: pytest, pytest-cov, hypothesis, ruff, mypy, httpx (cliente de pruebas de la aplicación).
Navegador automatizado y revisión automática de accesibilidad, que ADR-003 punto 8 deja a este plan: **Playwright para
Python con `pytest-playwright`, y axe-core inyectado desde una copia local** (paquete `axe-playwright-python`). Las
versiones exactas se fijan en T-001-02 con rango compatible; este plan no inventa números de versión.
**Almacenamiento**: ninguno. Todo vive en la memoria del proceso (NFR-000-17). La herramienta nunca lee `data/raw/`
(ADR-004 punto 1). Solo las pruebas de integración P-001-11 a P-001-15, P-001-28, P-001-39, P-001-46 y P-001-65 abren
`data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` en modo binario de lectura, sin escribir.
**Pruebas**: pytest (unidad, integración, propiedades con hypothesis), cliente de pruebas de la aplicación para rutas y
sesiones, Playwright + axe-core para escenarios de navegador (`calidad-python`, ADR-003 punto 8).
**Plataforma objetivo**: navegador del mismo equipo donde corre la herramienta, en `127.0.0.1` (restricción 5 de
`000`; ADR-004 punto 2).
**Tipo de proyecto**: núcleo Python (`src/egm/`) + capa web (`app/`).
**Metas de desempeño**: el spec no fija ninguna. Escala de referencia: 27 documentos en la v4 y 250 en el fixture de
US-001-1.5; límites fijos de NFR-000-19.
**Restricciones**: solo lectura de la matriz (NFR-000-01); número = longitud de su lista de filas (NFR-000-02,
ADR-001); categorías leídas del archivo, sin listas escritas en el código salvo los tres valores ancla del contrato §4.1
(NFR-000-06); textos en un solo catálogo, de usted, sin jerga ni fórmulas ni preguntas (NFR-000-03); nada en disco ni
en registros (NFR-000-17); núcleo sin web (NFR-000-14); ningún texto sobre la tabla no comparable de la hoja EGM
(regla 9 de `CLAUDE.md`; ADR-002 punto 6); ninguna cifra de la lámina 7 (regla 7).
**Escala/alcance**: 9 módulos del núcleo, 8 de la capa web y el constructor M23; vistas V0, V1, V2, cabecera corrida y
colofón (arquitectura §8).

## Requisitos que cubre este plan

| Requisito | Resumen | Historia | Escenario / criterio que lo verifica | Módulo(s) de la arquitectura |
|---|---|---|---|---|
| FR-001-01 | Hojas y columnas por su texto | US-001-1 | US-001-1.8, US-001-3.5, SC-001-05 | M03, M04 |
| FR-001-02 | Error de contrato por hoja o encabezado de rol faltante | US-001-2 | US-001-2.4, US-001-2.7, SC-001-02 | M04, M10, M13 |
| FR-001-03 | Bloque de dimensiones entre delimitadores | US-001-1, US-001-2 | US-001-1.4, US-001-2.5 | M04 |
| FR-001-04 | Advertencia por columna del bloque sin `1,0` o con `1,0` fuera | US-001-2 | US-001-2.6 | M04 |
| FR-001-05 | Listas desde las validaciones | US-001-1 | US-001-1.3, US-001-2.12 | M03, M04 |
| FR-001-06 | Todas las filas, sin límite | US-001-1 | US-001-1.5 | M05 |
| FR-001-07 | Regla de inclusión al mapa | US-001-1 | US-001-1.1, US-001-1.10, SC-001-01 | M07 |
| FR-001-08 | Celda = estudios distintos | US-001-1 | US-001-1.2, US-001-2.2, SC-001-01, SC-001-03 | M07 |
| FR-001-09 | Estudios del mapa sin sumar celdas | US-001-1 | US-001-1.2, SC-001-01, SC-001-03 | M07 |
| FR-001-10 | Enfoque por prefijo, con advertencia que cita la regla | US-001-1, US-001-2 | US-001-1.6, US-001-2.14 | M05, M10 |
| FR-001-11 | Lista de N.º de cada conteo | US-001-1 | US-001-1.7 | M01, M07 |
| FR-001-12 | Advertencias legibles; no corrige | US-001-2, US-001-3 | US-001-2.1, SC-001-02, SC-001-04 | M04, M05, M08, M10, M17 |
| FR-001-13 | Estado de cada documento y pendientes | US-001-1, US-001-2 | US-001-1.9, US-001-2.3, US-001-2.15, US-001-2.16 | M05, M07 |
| FR-001-14 | Comparar con las tablas comparables | US-001-3 | US-001-3.1, US-001-3.2 | M07, M08, M23 |
| FR-001-15 | Tablas por título y filas por nombre | US-001-3 | US-001-3.5, US-001-3.9 | M08 |
| FR-001-16 | «No verificable» sin error de contrato | US-001-3 | US-001-3.3, US-001-3.4, US-001-3.6 | M08 |
| FR-001-17 | Valor ausente no es 0 | US-001-3 | US-001-3.3, US-001-3.13 | M03, M08 |
| FR-001-18 | Advertir antes de los resultados y explicar | US-001-3 | US-001-3.2, US-001-3.8, US-001-3.17 | M07, M08, M10, M13, M17 |
| FR-001-19 | Nombre del archivo y fecha de lectura | US-001-1, US-001-4 | US-001-1.7, US-001-4.1 | M13, M17 |
| FR-001-20 | Carga desde el navegador; la nueva reemplaza | US-001-4 | US-001-4.1, US-001-4.2, US-001-4.5 | M02, M15, M16, M19 |
| FR-001-21 | Nota «columnas no usadas» | US-001-2 | US-001-2.8 | M04, M10 |
| FR-001-22 | Columnas categóricas sin lista | US-001-2 | US-001-2.11, US-001-2.12, US-001-2.15, SC-001-02 | M04 |
| FR-001-23 | Valores ancla | US-001-2 | US-001-2.9, US-001-2.10 | M04, M10 |
| FR-001-24 | Año no reconocido | US-001-2 | US-001-2.13 | M05 |
| FR-001-25 | Verificación solo de tablas comparables, por número | US-001-3 | US-001-3.3, US-001-3.7 | M08, M10, M17 |
| FR-001-26 | Alcance y emparejamiento dentro de cada tabla | US-001-3 | US-001-3.9, US-001-3.10, US-001-3.15, US-001-3.16 | M08 |
| FR-001-27 | Coincide, difiere o no verificable; advertir lo no comparado | US-001-3 | US-001-3.11 a US-001-3.14 | M08 |
| FR-001-28 | Descartar el archivo | US-001-5 | US-001-5.1 | M14, M15, M19 |
| FR-001-29 | Reglas de carga nueva, mensaje sin nombre ni filas | US-001-4 | US-001-4.7 a US-001-4.9, US-001-4.11 a US-001-4.13 (US-001-4.10 en el plan 002) | M02, M10, M13, M15, M16 |
| NFR-000-01 | Solo lectura; el archivo no se modifica | US-001-1, US-001-4 | SC-000-01 (parte del núcleo; US-001-4.6 completo en el plan 003) | M03, M16 |
| NFR-000-02 | Número = lista de N.º | US-001-1 | SC-001-03 (propiedad), US-001-1.7; SC-000-02 en las vistas de 002 y 003 | M01, M07 |
| NFR-000-03 | Textos de usted, sin jerga, fórmulas ni preguntas | US-001-2, US-001-3, US-001-4, US-001-5 | SC-000-03 (textos de este plan) | M10, M18 |
| NFR-000-04 | WCAG 2.2 AA (base) | US-001-4, US-001-5 | SC-000-04 en V0, V1, V2, cabecera y colofón | M18, M19 |
| NFR-000-05 | 360 px sin desplazamiento horizontal (base) | US-001-4 | SC-000-05 en V0, V1, V2, cabecera y colofón | M18 |
| NFR-000-06 | Adaptación a categorías nuevas, retiradas o renombradas | US-001-1 | SC-000-06, SC-001-05, US-001-1.3, US-001-1.4, US-001-3.11, US-001-3.12 | M04, M05, M07, M23 |
| NFR-000-09 | Determinismo; archivo y fecha en cada salida | US-001-1 | SC-000-09 | M01, M13 |
| NFR-000-11 | Colofón institucional por bloques, apagados por defecto | US-001-4 | SC-000-11 (parte automática; ver NC-P001-2) | M21, M22, M18 |
| NFR-000-12 | «Matriz: <nombre>, leída el <fecha>, <n> documentos», sin versión | US-001-4 | SC-000-12 | M13, M17, M21 |
| NFR-000-13 | Diseño «Fichero» (base) | US-001-4 | SC-000-13 en V0, V1, V2, cabecera y colofón | M18 |
| NFR-000-14 | Núcleo sin web | US-001-1 | SC-000-14 | M01 a M05, M07, M08, M10, M13 |
| NFR-000-15 | Uso desde un navegador | US-001-4 | SC-000-15 | M14 |
| NFR-000-17 | Solo durante la sesión; nada en disco ni en registros | US-001-4, US-001-5 | SC-000-17, US-001-5.1 a US-001-5.3, US-001-4.7 (US-001-5.4 a 5.6 en el plan 002) | M14, M15, M16, M19 |
| NFR-000-18 | Sesiones independientes | US-001-4, US-001-5 | SC-000-18 (resultados; la parte de filtros en el plan 002) | M15 |
| NFR-000-19 | Tipo, tamaño y contenido descomprimido antes de leer | US-001-4 | SC-000-19, US-001-4.3, US-001-4.4, US-001-4.13 | M02, M16 |
| SC-001-01 a SC-001-05 | Criterios del spec 001 | — | P-001-11 a P-001-14, P-001-46 (SC-001-01); P-001-01, P-001-24, P-001-42 (SC-001-02); P-001-25, P-001-63 (SC-001-03); P-001-43, T-001-93 (SC-001-04); P-001-23 (SC-001-05) | M04, M05, M07, M08, M10, M23 |

NFR-000 por plan, según arquitectura §6.4: este plan lleva NFR-000-01, 02, 03, 06, 09, 11, 12, 14, 15, 17, 18 y 19, y
la base de 04, 05 y 13.

**Fuera de alcance de este plan** (con su referencia):

- US-001-4.6 completo (huella tras usar **todas** las vistas): depende de 002 y 003 (spec 001, historia 4, «Independent
  Test»). Aquí solo la parte del núcleo (P-001-15).
- US-001-4.10 (filtros tras una carga nueva): depende de los filtros del plan 002. Aquí M15 deja vacío el espacio del
  filtro aplicado al reemplazar la sesión; el plan 002 lo prueba.
- US-001-5.4 a US-001-5.6 (actividad sobre el mapa): dependen del plan 002 (spec 001, historia 5; arquitectura §6.4).
  Aquí se prueba el mecanismo general de actividad (P-001-92, P-001-94).
- SC-000-02 en vistas (abrir la lista de N.º de un número mostrado): vistas V3 a V9 de los planes 002 y 003.
- NFR-000-16 (referencia a 3ie): asignado al plan 002 (arquitectura §6.4). M21 se crea aquí con el bloque siempre
  presente «Referencia de diseño» como parte de su estructura (ADR-005), y SC-000-16 se verifica en el plan 002.
- Filtros (M06), desglose por nivel y coocurrencias (M07), definiciones (M12), conclusiones (M09), porcentajes (M11) y
  exportación (M20): planes 002 y 003.
- Vista de red y módulo no supervisado (regla 10 de `CLAUDE.md`; arquitectura §7).

## Estructura del proyecto

### Documentación (esta feature)

```text
docs/specs/001-lectura-verificacion/
└── spec.md              # Spec aprobado (fuente de este plan)

docs/planes/001-lectura-verificacion/
└── plan.md              # Este archivo
```

### Código fuente (raíz del repositorio)

```text
pyproject.toml                    # T-001-02
src/egm/
├── __init__.py
├── py.typed
├── modelo.py                     # M01
├── archivo.py                    # M02
├── libro.py                      # M03
├── esquema.py                    # M04
├── lectura.py                    # M05
├── conteo.py                     # M07 (parte del plan 001)
├── verificacion.py               # M08
├── textos.py                     # M10 (parte del plan 001)
└── procesamiento.py              # M13

app/
├── __init__.py
├── servidor.py                   # M14 (incluye el arranque: python -m app.servidor)
├── sesiones.py                   # M15
├── carga.py                      # M16
├── presentacion.py               # M17
├── colofon.py                    # M21
├── configuracion.py              # M22
├── plantillas/                   # M18: plantillas Jinja2 (base, inicio, mensajes, avisos, cabecera, colofón)
├── estaticos/                    # M18: CSS «Fichero», fuentes Alegreya y Alegreya Sans, logos (si existen)
└── cliente/                      # M19: htmx y guion propio, servidos como estáticos

tests/
├── __init__.py
├── constructor.py                # M23 `tests.constructor`
├── unit/
├── integracion/
├── propiedades/
└── navegador/                    # escenarios con Playwright (marcados aparte)

data/fixtures/
└── *.xlsx                        # generados por M23 (ver «Catálogo de fixtures»)
```

**Decisión de estructura**: se apoya en la lista cerrada de arquitectura §6 y en su nota sobre el andamiaje (F2-10):
cada módulo del núcleo es **un archivo** (`egm.modelo` y `egm.lectura` incluidos, cuya forma deja la arquitectura a este
plan). Se retiran las carpetas `src/egm/analisis/`, `src/egm/validacion/`, `src/egm/lectura/` y `src/egm/modelo/`, que
hoy solo tienen `.gitkeep`. `app.plantillas` y `app.cliente` son carpetas de recursos, no paquetes Python. La carpeta
`tests/navegador/` agrupa pruebas, no es un módulo.

**Nombre del constructor.** El archivo es `tests/constructor.py`, módulo M23 `tests.constructor` (arquitectura §6.3).
COR-013 unificó el nombre en el prompt de la Fase 3, en la skill `calidad-python` y en el plan 003.

### Rutas de la capa web (M14; la arquitectura deja su documentación a este plan)

Las URL no llevan texto de la matriz (M14). La ficha de sesión viaja en la cabecera `X-EGM-Sesion` de cada petición
(ADR-003 punto 4); el nombre del archivo, en `X-EGM-Nombre`, codificado como componente de URI.

| Método y ruta | Qué hace | Módulos | Requisitos |
|---|---|---|---|
| `GET /` | Página base, sin datos. El guion lee la ficha de la pestaña: con ficha pide `GET /vista/resultado` (E9, «Recuperando su sesión»); sin ficha pide `GET /vista/inicio` | M14, M17, M18, M19 | US-001-4.2, US-001-5.2 |
| `GET /vista/inicio` | Fragmento V0 (y E8 si la sesión acaba de terminar) | M14, M17, M18 | US-001-4.2, FR-001-28 |
| `POST /carga` | Cuerpo crudo con el libro; responde con el fragmento de resultado o con el mensaje E2, E3, E4 o E10, y con la ficha nueva en la cabecera de la respuesta | M14, M16, M15 | FR-001-20, FR-001-29, NFR-000-19 |
| `GET /vista/resultado` | Cabecera corrida, V2 y colofón de la sesión (ver NC-P001-1); el plan 002 la convierte en la página del mapa (R-2; plan 002, T-002-16) | M14, M17, M18 | FR-001-18, FR-001-19, NFR-000-12 |
| `POST /sesion/descartar` | Termina la sesión (E8) | M14, M15 | FR-001-28, NFR-000-17 |
| `POST /sesion/latido` | Registra actividad | M14, M15 | NFR-000-17 |
| `POST /sesion/cierre` | Aviso de cierre de pestaña; borra pasados 10 s salvo que la ficha vuelva | M14, M15 | NFR-000-17 (ADR-003 punto 9) |
| `GET /estaticos/...` | CSS, fuentes, logos, htmx y guion propio, todo local | M14, M18, M19 | NFR-000-15 (ADR-003 punto 6) |

Los planes 002 y 003 agregan sus rutas (mapa, cajón, ficha, lista, definición, filtros, exportación) sobre `crear_app`.

### Arranque de la demostración (ADR-004 punto 2 pide documentarlo en este plan)

1. Si no existe el entorno: `py -3.13 -m venv .venv`.
2. Instalar: `.venv\Scripts\python -m pip install -e ".[dev]"` (y, solo para las pruebas de navegador,
   `.venv\Scripts\python -m playwright install chromium`).
3. Arrancar: `.venv\Scripts\python -m app.servidor`. Uvicorn, un solo proceso, solo en `127.0.0.1`, registro de
   accesos apagado, puerto de la configuración (por defecto 8000, fijado en M22 por T-001-62).
4. Abrir `http://127.0.0.1:8000` en el navegador del mismo equipo.

## Catálogo de fixtures (M23)

Todos los fixtures los genera `tests/constructor.py` con categorías sintéticas (permitidas en fixtures,
`calidad-python`), de forma determinista (fechas internas del libro fijas, mismo contenido en cada corrida). El comando
`python -m tests.constructor` escribe en `data/fixtures/` los fixtures con nombre; los que pesan cerca de los límites de
NFR-000-19 se generan solo en memoria con `.a_bytes()` y no se guardan en el repositorio. Ningún fixture copia la
matriz de `data/raw/` ni usa cifras de la lámina 7.

**Un fixture por caso borde de `contrato-datos.md` §9** (CB-01 a CB-41, en el orden de la tabla del contrato):

| CB | Caso borde (§9) | Fixture | Prueba que comprueba el tratamiento |
|---|---|---|---|
| 01 | Fila solo con referencia | `cb01_fila_solo_referencia.xlsx` | P-001-24 |
| 02 | Empírico sin intervención | `cb02_empirico_sin_intervencion.xlsx` | P-001-24 |
| 03 | Empírico con intervención y sin dimensiones | `cb03_empirico_sin_dimensiones.xlsx` | P-001-24, P-001-53 |
| 04 | Principal vacía y secundaria diligenciada | `cb04_solo_secundaria.xlsx` | P-001-22 |
| 05 | Estudio del mapa sin nivel o con «No aplica…» | `cb05_sin_nivel.xlsx` | P-001-24 (lectura como «Sin nivel»); presentación en el plan 002 (FR-002-12) |
| 06 | No empírico en las cifras de documentos del tablero | `cb06_no_empirico_tablero.xlsx` | plan 003 (FR-003-14) |
| 07 | $G_r = H_r$ | `cb07_misma_intervencion.xlsx` | P-001-27, P-001-45 |
| 08 | No empírico con intervención | `cb08_no_empirico_con_intervencion.xlsx` | P-001-42 |
| 09 | Dimensión fuera de $\{0, 1, \varnothing\}$ | `cb09_dimension_fuera_de_rango.xlsx` | P-001-42 |
| 10 | Valor fuera de lista | `cb10_fuera_de_lista.xlsx` | P-001-26 |
| 11 | Enfoque sin prefijo válido | `cb11_enfoque_sin_prefijo.xlsx` | P-001-20, P-001-39 |
| 12 | Más filas que el rango de las fórmulas | `cb12_250_documentos.xlsx` | P-001-19, P-001-61 |
| 13 | `N°` vacío con contenido o repetido | `cb13_numero_vacio_o_repetido.xlsx` | P-001-42 |
| 14 | Encabezado de rol renombrado o ausente | `cb14_sin_nivel_de_evidencia.xlsx` | P-001-29, P-001-81 |
| 15 | Hoja de la matriz faltante | `cb15_sin_hoja_matriz.xlsx` | P-001-32 |
| 16 | Otro tipo, dañado o mayor que el límite | `cb16_otro_tipo.txt`, `cb16_extension_xlsx_otro_contenido.xlsx`, `cb16_danado.xlsx`; tamaño exacto y +1 en memoria | P-001-07, P-001-73, P-001-74 |
| 17 | Contenido descomprimido declarado mayor que el límite | en memoria: exacto y +1 | P-001-07, P-001-75 |
| 18 | Columna ajena fuera del bloque, sin `1,0` | `cb18_columna_observaciones.xlsx` | P-001-33, P-001-79 |
| 19 | Columna ajena fuera del bloque, con `1,0` | `cb19_columna_1_0_fuera.xlsx` | P-001-31 |
| 20 | Sin ancla de estudio empírico | `cb20_sin_ancla_empirico.xlsx` | P-001-34 |
| 21 | Sin ancla de evaluación de impacto | `cb21_sin_ancla_ie.xlsx` | P-001-35, P-001-62; conclusión 2 en el plan 003 |
| 22 | Ningún valor de una lista empieza por `No aplica` | `cb22_sin_no_aplica.xlsx` | P-001-42 |
| 23 | Varios tipos empiezan por `Estudio empírico` | `cb23_varios_empiricos.xlsx` | P-001-42 |
| 24 | Intervenciones o nivel sin lista | `cb24_nivel_sin_lista.xlsx`, `cb24_principal_sin_lista.xlsx`, `cb24_secundaria_sin_lista.xlsx` | P-001-36 |
| 25 | Tipo de documento, de fuente o metodología sin lista | `cb25_fuente_sin_lista.xlsx`, `cb25_metodologia_sin_lista.xlsx` | P-001-37, P-001-40 |
| 26 | Tipo de documento sin lista, valor distinto del ancla | `cb26_tipo_sin_lista.xlsx` | P-001-40 |
| 27 | `Año` no numérico | `cb27_anio_no_numerico.xlsx` | P-001-38 |
| 28 | Tipo de documento vacío o fuera de lista | `cb28_tipo_vacio_o_fuera.xlsx` | P-001-24, P-001-41 |
| 29 | Hoja `EGM` faltante o irreconocible | `cb29_sin_hoja_egm.xlsx`, `cb29_titulo_cambiado.xlsx` | P-001-47, P-001-49 |
| 30 | Sin valores calculados | `cb30_sin_valores_guardados.xlsx` | P-001-46 |
| 31 | Categoría de la matriz sin fila o columna en la tabla | `cb31_categoria_nueva.xlsx` | P-001-54 |
| 32 | Fila o columna de la tabla que no es categoría | `cb32_categoria_solo_en_hoja.xlsx` | P-001-55 |
| 33 | Tabla con solo algunos valores calculados | `cb33_parcial_sin_diferencia.xlsx`, `cb33_parcial_con_diferencia.xlsx` | P-001-56, P-001-57 |
| 34 | Falta o se repite `Total estudios` | `cb34_sin_total.xlsx`, `cb34_total_repetido.xlsx` | P-001-59 |
| 35 | Nombre repetido dentro de una tabla | `cb35_nombre_repetido.xlsx` | P-001-58 |
| 36 | Intervención o nivel agregado | `cb36_intervencion_nivel_agregados.xlsx` | P-001-17, P-001-23, P-001-54 |
| 37 | Columna agregada dentro del bloque | `cb37_dimension_agregada.xlsx` (con y sin `1,0`) | P-001-18, P-001-31 |
| 38 | Bloque degenerado (final antes del inicial, o vacío) | `cb38_bloque_invertido.xlsx`, `cb38_bloque_vacio.xlsx` | P-001-42 |
| 39 | Encabezado de rol dentro del bloque | `cb39_rol_en_bloque.xlsx` | P-001-42 |
| 40 | Categoría o dimensión retirada | `cb40_retiradas.xlsx` | P-001-23, P-001-42, P-001-55 |
| 41 | Número escrito como texto | `cb41_texto_1.xlsx` | P-001-42, P-001-51 |

**Fixtures de escenarios y criterios** (además de los anteriores): `base_valida.xlsx` (todos los roles, listas por
validación escrita y por rango, 8 dimensiones, hoja EGM con fórmulas y valores guardados correctos);
`esc_1_2_cuatro_celdas`, `esc_1_6_enfoque`, `esc_1_8_orden_alterado`, `esc_2_1_fuera_de_lista_n3`,
`esc_2_5_sin_delimitador_final`, `esc_2_13_anio_sf_n4`, `esc_2_15_tipo_sin_lista_cuatro_docs`,
`esc_2_16_tipo_fuera_de_lista_n3`, `esc_3_1_coincide`, `esc_3_2_difiere_g_igual_h`, `esc_3_5_filas_vacias_antes`,
`esc_3_7_titulos_1_2_4` (con una tabla no comparable con valores), `esc_3_9_nombres_repetidos_entre_tablas`,
`esc_3_10_total_entre_dimensiones`, `esc_3_17_espacios`, `validacion_x14.xlsx` (lista guardada como extensión),
`sc000_06_agregadas`, `sc000_06_retiradas`, `sc000_06_renombradas`, `sc000_12_otro_nombre_v4` (otro número de
documentos, nombre con «v4»), `instancia_ejemplo.xlsx` (FX-A: réplica sintética de la instancia de ejemplo del apéndice A del contrato, con 27 documentos, $E$ = N.º 7, 10, 11, 13, 15, 16 y 24, $M$ = N.º 7, 6 × 8 categorías, los repartos de tipo de documento, tipo de fuente, metodología, enfoque y años del apéndice A, sin valores guardados en la hoja EGM y con los siete textos del N.º 7 sintéticos, escritos a mano en su docstring; la usan los planes 002 y 003), `marcadores.xlsx` (marcadores únicos en nombre y celdas, SC-000-17), `sesion_a.xlsx` y
`sesion_b.xlsx` (SC-000-18), y en memoria `parte_mayor_que_lo_declarado` (NC-ARQ-1). Todos con extensión `.xlsx`
salvo los indicados.

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: entorno, estructura conciliada con la arquitectura, constructor de fixtures y la comprobación previa
NC-ARQ-1.

- [x] T-001-01 Conciliar el andamiaje de `src/egm/` con la lista cerrada (arquitectura §6, F2-10): retirar
  `src/egm/analisis/`, `src/egm/validacion/`, `src/egm/lectura/` y `src/egm/modelo/`; crear los archivos vacíos de
  M01 a M05, M07, M08, M10 y M13, `src/egm/__init__.py` y `py.typed`; crear el esqueleto de `app/` (M14 a M19, M21,
  M22) y `tests/__init__.py`. Resultado verificable: el árbol coincide con «Estructura del proyecto» y no queda ninguna
  carpeta sin módulo. Requisitos: NFR-000-14. Módulos: M01 a M05, M07, M08, M10, M13 a M19, M21, M22, M23. Archivos:
  `src/egm/*`, `app/*`, `tests/__init__.py`.
- [x] T-001-02 [P] Crear `pyproject.toml` (estructura `src/`, paquetes `egm` y `app`, extra `dev`) con dependencias
  fijadas con rango compatible y confirmar el `.venv` con Python 3.13 (recrearlo con `py -3.13 -m venv .venv` si no lo
  es); el núcleo declara solo `openpyxl` (arquitectura §7, PE-7). Registrar la versión exacta de Python para el resumen
  de fase. Resultado verificable: `pip install -e ".[dev]"` termina sin errores y `python --version` da 3.13.x.
  Requisitos: NFR-000-14, NFR-000-15. Módulos: — (entorno). Archivos: `pyproject.toml`.
- [x] T-001-03 [P] Configurar `ruff`, `mypy --strict` sobre `src/egm/`, `pytest` (marcas `raw` para las pruebas que
  leen `data/raw/` y `navegador` para Playwright), `pytest-cov` con umbral de 90 % sobre `src/egm/` y `hypothesis`
  (perfil determinista). Resultado verificable: las cuatro herramientas corren sobre el árbol vacío sin errores.
  Requisitos: — (`calidad-python`). Módulos: —. Archivos: `pyproject.toml`.
- [x] T-001-04 Implementar el constructor base `MatrizSintetica` de M23: hojas en cualquier orden, encabezados en
  cualquier posición, validaciones como lista escrita y como referencia a rango, filas con valores de cualquier tipo
  (número, texto, vacío, espacios), fechas internas fijas y `.a_bytes()`; nunca abre rutas de `data/raw/`. Resultado
  verificable: `base_valida` se genera y `openpyxl` la abre. Requisitos: NFR-000-06, SC-001-02 (soporte). Módulos: M23.
  Archivos: `tests/constructor.py`.
- [x] T-001-05 Ampliar M23 con la hoja EGM: títulos numerados, tablas en cualquier posición, fórmulas con rangos
  sobre la hoja de la matriz **y** valores guardados controlados (incluidos ausentes, texto y parciales), libro sin
  valores guardados, y validaciones guardadas como extensión `x14`. Resultado verificable: un libro generado expone, al
  leerlo, fórmula y valor guardado en la misma celda. Requisitos: FR-001-14, FR-001-05. Módulos: M23. Archivos:
  `tests/constructor.py`.
- [x] T-001-06 Ampliar M23 con los archivos de carga: otro tipo, extensión `.xlsx` con otro contenido, paquete dañado,
  libro de exactamente 15 728 640 bytes y de un byte más, libro con contenido descomprimido declarado de exactamente
  268 435 456 bytes y de un byte más, y un libro con una parte que se descomprime a más de lo que declara su índice.
  Resultado verificable: los tamaños medidos coinciden al byte con lo pedido. Requisitos: NFR-000-19, SC-000-19.
  Módulos: M23. Archivos: `tests/constructor.py`.
- [x] T-001-07 Escribir P-001-01 y comprobar que falla; después, generar el catálogo de fixtures (tabla «Catálogo de
  fixtures»): CB-01 a CB-41, los de escenarios y FX-A, con el comando `python -m tests.constructor`. Resultado
  verificable: P-001-01 en verde. Requisitos:
  SC-001-02, SC-000-06, SC-000-12, SC-000-17, SC-000-18 (soporte). Pruebas: P-001-01. Módulos: M23. Archivos:
  `tests/constructor.py`, `data/fixtures/*.xlsx`, `tests/unit/test_constructor.py`.
- [x] T-001-08 [P] Escribir en M23 las estrategias de hypothesis que generan matrices válidas al azar (categorías,
  dimensiones, filas con y sin $G_r = H_r$, niveles, vacíos) con su hoja EGM opcional. Resultado verificable: una
  corrida de 200 ejemplos produce libros que `openpyxl` abre. Requisitos: SC-001-03 (soporte). Módulos: M23. Archivos:
  `tests/constructor.py`.
- [x] T-001-09 Resolver NC-ARQ-1: con el libro `parte_mayor_que_lo_declarado` de T-001-06, comprobar, en memoria y sin
  escribir nada, qué hacen la biblioteca de paquetes de Python y `openpyxl` al abrir ese libro y leer esa parte: si leen
  más de lo declarado, si se detienen en lo declarado o si fallan, y con qué excepción. Fijar el comportamiento en
  P-001-02 y anotar el resultado en «Riesgos y decisiones abiertas» y en el resumen de fase. P-001-02 es una prueba de
  caracterización: se escribe después de observar el comportamiento. Si el resultado es que
  se lee más de lo declarado sin error, **detenerse** y pasar el hallazgo a `analista-impacto` (corrección nueva) antes de
  implementar M02 y M03. Requisitos: NFR-000-19 (spec 001, casos borde: archivo dañado). Pruebas: P-001-02. Módulos:
  M02, M03, M23. Archivos: `tests/unit/test_nc_arq_1.py`.

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-01 | unit | SC-001-02 (cada caso borde tiene matriz sintética) | catálogo completo | Existe un fixture por cada CB-01 a CB-41; dos generaciones dan los mismos bytes; ninguno se lee de `data/raw/` |
| P-001-02 | unit | NC-ARQ-1; spec 001, casos borde («archivo dañado») | `parte_mayor_que_lo_declarado` (memoria) | El comportamiento observado en T-001-09, fijado para que un cambio de biblioteca lo haga visible; esperado por el spec: el libro no se abre y se trata como dañado |

**Punto de control**: entorno listo, fixtures generados, NC-ARQ-1 resuelto o escalado.

---

## Fase 2: Base (prerrequisitos que bloquean)

**Propósito**: tipos del dominio, acceso al libro, validación previa del archivo, catálogo de textos y reglas de
importación del núcleo.

**Crítico**: ninguna historia empieza antes de cerrar esta fase.

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-03 | unit | NFR-000-02, FR-001-11 | — (valores escritos en la prueba) | `Conteo.valor == len(filas)`; filas en orden del archivo y sin repetidos; no hay otro modo de crear un número |
| P-001-04 | unit | NFR-000-09 | — | Los tipos de M01 son inmutables; `Identificacion` guarda el nombre tal como llegó y la fecha dada |
| P-001-05 | unit | FR-001-01, FR-001-05, FR-001-17 | `base_valida`, `cb30_sin_valores_guardados`, `validacion_x14` | Nombres de hojas; celda con valor, fórmula y valor guardado; valor guardado ausente es `None`, nunca 0; listas por validación escrita, por rango y por extensión, en el orden de la lista |
| P-001-06 | unit | NFR-000-01 | `base_valida` | Los bytes de entrada no cambian tras abrir; M03 no expone ninguna operación de guardar |
| P-001-07 | unit | SC-000-19, US-001-4.3, US-001-4.4, US-001-4.13 (núcleo), NFR-000-19 | CB-16, CB-17 | Otro tipo, extensión correcta con otro contenido y dañado ⇒ `Rechazo("tipo")`; 15 728 640 bytes ⇒ aceptado; +1 ⇒ `Rechazo("tamano")`; declarado 268 435 456 ⇒ aceptado; +1 ⇒ `Rechazo("contenido")` |
| P-001-08 | unit | NFR-000-19 («sin descomprimir ninguna») | CB-17 +1 con datos comprimidos inválidos | `Rechazo("contenido")` sin error: la comprobación usa solo el índice del paquete |
| P-001-09 | unit | NFR-000-03, NFR-000-19 (mensaje propio) | — | `fecha()` da «21 de noviembre de 2026» para esa fecha; `rechazo()` da los textos E2, E3 y E10 de `flujos.md` §2, el de E10 sin cifras; ningún texto del catálogo contiene «¿», tuteo, fórmulas, «error de contrato», «validación» ni «fixture», ni nombra una tabla no comparable de la hoja EGM |
| P-001-10 | unit | SC-000-14, NFR-000-14 | — | Ningún módulo de `src/egm/` importa `app`, FastAPI, Starlette, Jinja2 ni Uvicorn; `egm.modelo` no importa otro módulo de `egm`; solo `egm.libro` importa `openpyxl` (arquitectura §4.1) |

- [x] T-001-10 [P] Escribir P-001-03 y P-001-04 en `tests/unit/test_modelo.py`.
- [x] T-001-11 Implementar M01 `egm.modelo` con los tipos de arquitectura §6 (M01) y los comunes (`RefFila`, `Conteo`,
  `EstadoDocumento`, `Enfoque`, `SIN_NIVEL`, `Advertencia`, `Nota`, `ErrorContrato`, `Identificacion`,
  `ResultadoLectura`, `Rechazo`, `FalloContrato`); `Esquema`, `Documento` y `Corpus` se declaran aquí y se completan
  con T-001-23 y T-001-24. Requisitos: NFR-000-02, FR-001-11, NFR-000-09. Pruebas: P-001-03, P-001-04. Módulos: M01.
  Archivos: `src/egm/modelo.py`.
- [x] T-001-12 [P] Escribir P-001-05 y P-001-06 en `tests/unit/test_libro.py`.
- [x] T-001-13 Implementar M03 `egm.libro`: `abrir(bytes)` en memoria, `Libro`, `Hoja`, `Celda` y `ListaValidacion`
  (lectura normal L1 y, si el paquete trae validaciones de extensión, lectura de su XML L2; ADR-001 punto 6). Comprobar
  qué modo de carga de `openpyxl` entrega las validaciones (ver riesgo R-5) y abrir dos veces si hace falta para tener
  fórmula y valor guardado. Requisitos: NFR-000-01, FR-001-01, FR-001-05, FR-001-17. Pruebas: P-001-05, P-001-06.
  Módulos: M03. Archivos: `src/egm/libro.py`.
- [x] T-001-14 [P] Escribir P-001-07 y P-001-08 en `tests/unit/test_archivo.py`.
- [x] T-001-15 Implementar M02 `egm.archivo`: `LIMITE_BYTES`, `LIMITE_DESCOMPRIMIDO` y `validar_archivo` (tamaño, paquete
  con las partes de un libro `.xlsx`, suma de tamaños declarados en el índice sin descomprimir). Requisitos: NFR-000-19,
  FR-001-20, FR-001-29. Pruebas: P-001-07, P-001-08. Módulos: M02. Archivos: `src/egm/archivo.py`.
- [x] T-001-16 [P] Escribir P-001-09 en `tests/unit/test_textos.py` y P-001-10 en `tests/unit/test_importaciones.py`.
- [x] T-001-17 Implementar la base de M10 `egm.textos`: estructura del catálogo único, `fecha()`, `rechazo()` con los
  textos E2, E3 y E10 de `flujos.md` §2 y `ROTULOS` vacío para que 002 y 003 lo amplíen. Requisitos: NFR-000-03,
  NFR-000-19, FR-001-29. Pruebas: P-001-09, P-001-10. Módulos: M10. Archivos: `src/egm/textos.py`.

**Punto de control**: base lista; P-001-03 a P-001-10 en verde. Ya pueden empezar las historias.

---

## Fase 3: Historia 1 — Leer y contar una matriz (prioridad: P1)

**Objetivo**: descubrir la estructura en el camino válido, leer todos los documentos, asignar estados y calcular los
conteos de estudios distintos con su lista de N.º.

**Prueba independiente**: con la v4 y con fixtures, comparando con el apéndice A y con esperados escritos a mano desde
el contrato, sin interfaz (spec 001, historia 1). Las pruebas llaman a `abrir`, `descubrir`, `leer` y a M07; la fachada
llega en la fase 6.

### Pruebas de la historia 1 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-11 | integración (`raw`) | US-001-1.1, FR-001-07, SC-001-01 | v4 (`data/raw/`, solo lectura) | 27 documentos; $\lvert E\rvert = 7$; $N = 1$ (N.º 7); 6 de 48 celdas en 1, exactamente {Transferencia de activos, Acompañamiento técnico} × {Vulnerabilidad, Humano, Financiero}; 42 en 0 (apéndice A) |
| P-001-12 | integración (`raw`) | US-001-1.7 (listas), FR-001-11 | v4 | Cada una de las 6 celdas en 1 tiene `Conteo` con una sola `RefFila`, de N.º 7 |
| P-001-13 | integración (`raw`) | US-001-1.9, FR-001-13 | v4 | 1 en el mapa, 6 empíricos pendientes, 20 no empíricos, 0 sin tipo de documento válido |
| P-001-14 | integración (`raw`) | SC-001-01 (resto del apéndice A, salvo verificación) | v4 | Hojas; listas (6 tipos de documento, 3 de fuente, 6 intervenciones más «No aplica…», 7 metodologías, 4 niveles más «No aplica…»); 8 dimensiones en el orden del apéndice; por tipo 9/7/4/3/3/1; $T_4$: Evaluación de impacto 1 y demás 0; $t(i)$ 1 en Transferencia de activos y Acompañamiento técnico y 0 en las demás; fuente 6/1/0 y 20 sin diligenciar; metodología 6 Conceptual/teórica, 1 Evaluación de impacto, 20 sin diligenciar; años 1992 a 2026; enfoque 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar; en $M$, 1 Sin clasificar (N.º 7) |
| P-001-15 | integración (`raw`) | SC-000-01, NFR-000-01 (parte del núcleo de US-001-4.6) | v4 | SHA-256 antes y después de leer y contar = `7E1714DE…52C3A1` (apéndice A) |
| P-001-16 | unit | US-001-1.2, FR-001-08, FR-001-09 | `esc_1_2_cuatro_celdas` | El estudio aparece en 4 celdas; estudios del mapa = 1; suma de celdas = 4 |
| P-001-17 | unit | US-001-1.3, FR-001-05, NFR-000-06 | `cb36_intervencion_nivel_agregados` | La intervención agregada es fila del mapa, con conteo 1 y su N.º |
| P-001-18 | unit | US-001-1.4, FR-001-03 | `cb37_dimension_agregada` (con `1,0`) | La columna nueva es dimensión con el nombre de su encabezado, en su posición |
| P-001-19 | unit | US-001-1.5 (conteo), FR-001-06 | `cb12_250_documentos` | $\lvert R\rvert = 250$ (la advertencia sobre el rango de la hoja se prueba en P-001-61) |
| P-001-20 | unit | US-001-1.6, FR-001-10 | `esc_1_6_enfoque` | «No desarrolla…» ⇒ No; «Nota: …» ⇒ Sin clasificar con advertencia; «Sí, aborda…» ⇒ Sí; «Parcial: …» ⇒ Parcial; «Si bien…» ⇒ Sin clasificar con advertencia; vacía ⇒ Sin diligenciar |
| P-001-21 | unit | US-001-1.8, FR-001-01 | `esc_1_8_orden_alterado` y `base_valida` | Mismos conteos, con sus listas, en ambos |
| P-001-22 | unit | US-001-1.10, CB-04 | `cb04_solo_secundaria` | Entra al mapa en la fila de su secundaria; ninguna advertencia por la principal vacía |
| P-001-23 | unit | SC-001-05, SC-000-06, NFR-000-06 | `sc000_06_agregadas`, `sc000_06_retiradas`, `sc000_06_renombradas`, `cb40_retiradas` | Cada esquema muestra las categorías y dimensiones de su archivo; además, ningún nombre de categoría de los fixtures ni de la v4 aparece como literal en `src/egm/`, salvo los tres valores ancla del contrato §4.1 |
| P-001-24 | unit | SC-001-02 (CB-01, 02, 03, 05, 28) | `cb01`, `cb02`, `cb03`, `cb05`, `cb28` | CB-01 y CB-28: sin tipo de documento válido, en $R$ y no en $E$; CB-02 y CB-03: en $E$ y en $P$; CB-05: nivel `SIN_NIVEL` para vacío y para «No aplica…» |
| P-001-25 | propiedades | SC-001-03, NFR-000-02 | estrategias de M23 | $S^{IE} \le S \le T_1$, $T_2 \le T_1$, $\sum_\ell T_4(\ell) \le \lvert E\rvert$, $\sum_{i,j} S(i,j) = \sum_{r \in M} \lvert I_r\rvert\,\lvert J_r\rvert \ge N$, y todo `Conteo.valor == len(filas)`; esperados de un oráculo escrito en la prueba desde las fórmulas del contrato §5. $S_\varphi$ queda para el plan 002 y $S_\kappa$ para el 003 |

- [x] T-001-20 [US-001-1] Escribir P-001-11 a P-001-15 en `tests/integracion/test_v4_lectura.py` (marca `raw`; apertura
  en modo binario de lectura).
- [x] T-001-21 [P] [US-001-1] Escribir P-001-16 a P-001-24 en `tests/unit/test_lectura_conteo.py`.
- [x] T-001-22 [P] [US-001-1] Escribir P-001-25 en `tests/propiedades/test_invariantes_conteo.py`.

### Implementación de la historia 1

- [x] T-001-23 [US-001-1] Implementar el camino válido de M04 `egm.esquema.descubrir`: hoja por nombre, roles por
  encabezado (contrato §3), bloque entre delimitadores en el orden de las columnas (§3.1), listas desde la validación o
  los valores presentes (`Lista.origen`), valores «No aplica» por prefijo fuera de las categorías, anclas $v_{emp}$ y
  $v_{IE}$ (§4.1), intervenciones en el orden de la lista principal y luego las de solo secundaria (§4 regla 3). Deja
  listo el orden que consume FR-002-01 y el ancla que consume FR-003-22. Requisitos: FR-001-01, FR-001-03, FR-001-05,
  FR-001-22 (camino con lista), NFR-000-06. Pruebas: P-001-14, P-001-17, P-001-18, P-001-21, P-001-23. Módulos: M04,
  M01. Archivos: `src/egm/esquema.py`, `src/egm/modelo.py`.
- [x] T-001-24 [US-001-1] Implementar el camino válido de M05 `egm.lectura.leer` y `clasificar_enfoque`: todas las filas
  no vacías sin límite (§4 reglas 4 y 5), comparación tras quitar espacios en los extremos, dimensiones marcadas solo por
  el 1 numérico, $I_r$ en el orden de la lista, nivel o `SIN_NIVEL`, año entero, textos tal cual, `DatosCrudos` (texto
  «1», espacios, $G_r = H_r$) y estado de cada documento (§4). Depende de T-001-23. Requisitos: FR-001-06, FR-001-10,
  FR-001-13, NFR-000-06. Pruebas: P-001-13, P-001-14, P-001-19, P-001-20, P-001-22, P-001-24. Módulos: M05, M01.
  Archivos: `src/egm/lectura.py`, `src/egm/modelo.py`.
- [x] T-001-25 [US-001-1] Implementar la parte del plan 001 de M07 `egm.conteo`: `conjuntos` ($R$, $E$, $M$, $P$),
  `mapa` sin filtro (`Celda` con su `Conteo`; estudios $n$ y total $N$ distintos, nunca suma de celdas),
  `evaluacion_impacto` ($S^{IE}$, `None` sin ancla), `por_intervencion` ($u$, $u^{IE}$), `por_nivel` ($T_4$) y
  `semantica_hoja` ($T_1$, $T_2$, $t$, $t^{IE}$ sobre un rango de filas, variante estándar). Sin parámetro `filtro`
  todavía (ver observación O-3). Depende de T-001-24. Requisitos: FR-001-07, FR-001-08, FR-001-09, FR-001-11,
  FR-001-13, NFR-000-02. Pruebas: P-001-11, P-001-12, P-001-14, P-001-16, P-001-25. Módulos: M07. Archivos:
  `src/egm/conteo.py`.

**Punto de control**: la historia 1 funciona y se prueba sola. El implementador se detiene y resume.

---

## Fase 4: Historia 2 — Recibir advertencias legibles (prioridad: P1)

**Objetivo**: la lista cerrada de errores de contrato, las advertencias de estructura y de fila, y la nota de columnas
no usadas, con textos legibles; nada se corrige.

**Prueba independiente**: con fixtures de cada caso borde del contrato (spec 001, historia 2).

### Pruebas de la historia 2 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-26 | unit | US-001-2.1, FR-001-12, CB-10 | `esc_2_1_fuera_de_lista_n3` | Advertencia con N.º 3, columna y valor; el valor no se cuenta |
| P-001-27 | unit | US-001-2.2, FR-001-08, CB-07 | `cb07_misma_intervencion` | Una vez en su celda; advertencia de que la hoja EGM lo cuenta dos veces |
| P-001-28 | integración (`raw`) | US-001-2.3, FR-001-13 | v4 | Pendientes: N.º 10, 11, 13, 15, 16 y 24 |
| P-001-29 | unit | US-001-2.4, FR-001-02, CB-14 | `cb14_sin_nivel_de_evidencia` | `FalloContrato` que nombra «Nivel de evidencia»; ningún esquema ni corpus |
| P-001-30 | unit | US-001-2.5, FR-001-03 | `esc_2_5_sin_delimitador_final` | `FalloContrato` que nombra «Indicadores o categorías analíticas» |
| P-001-31 | unit | US-001-2.6, FR-001-04, CB-19, CB-37 | `cb19_columna_1_0_fuera`, `cb37_dimension_agregada` (sin `1,0`) | Una advertencia por cada columna; el proceso sigue |
| P-001-32 | unit | US-001-2.7, FR-001-02, CB-15 | `cb15_sin_hoja_matriz` | `FalloContrato` que nombra la hoja «Matriz bibliográfica»; nada más |
| P-001-33 | unit | US-001-2.8, FR-001-21, CB-18 | `cb18_columna_observaciones` | Nota «columnas no usadas: Observaciones»; ninguna advertencia |
| P-001-34 | unit | US-001-2.9, FR-001-23, CB-20 | `cb20_sin_ancla_empirico` | `FalloContrato` con el valor esperado y los encontrados |
| P-001-35 | unit | US-001-2.10, FR-001-23, CB-21 | `cb21_sin_ancla_ie` | Advertencia; mapa calculado; `evaluacion_impacto` es `None` |
| P-001-36 | unit | US-001-2.11, FR-001-22, CB-24 | `cb24_*` | `FalloContrato` que nombra la columna sin lista (nivel, principal o secundaria) |
| P-001-37 | unit | US-001-2.12, FR-001-22, CB-25 | `cb25_fuente_sin_lista`, `cb25_metodologia_sin_lista` | Advertencia; la lista son los valores presentes |
| P-001-38 | unit | US-001-2.13, FR-001-24, CB-27 | `esc_2_13_anio_sf_n4` | Advertencia con N.º 4, columna y «s. f.»; documento contado con año no reconocido |
| P-001-39 | integración (`raw`) | US-001-2.14, FR-001-10, CB-11 | v4 | N.º 2 y 7 «Sin clasificar», cada uno con una advertencia que cita la regla de la hoja Instrucciones (B14) y no agrega nada más |
| P-001-40 | unit | US-001-2.15, FR-001-13, FR-001-22, CB-25, CB-26 | `esc_2_15_tipo_sin_lista_cuatro_docs` | Advertencia que nombra la columna y los valores presentes; estados en ese orden: en el mapa, no empírico, no empírico, sin tipo de documento válido |
| P-001-41 | unit | US-001-2.16, FR-001-13, CB-28 | `esc_2_16_tipo_fuera_de_lista_n3` | Advertencia con N.º 3, columna y valor; sin tipo de documento válido |
| P-001-42 | unit | SC-001-02 (CB-08, 09, 13, 22, 23, 38, 39, 40, 41 y espacios en los extremos) | fixtures de esos CB | Cada caso con el tratamiento del contrato §9: advertencia y seguir; la trazabilidad de CB-13 usa el número de fila; CB-38 deja el bloque sin dimensiones y los empíricos pendientes; CB-39 toma la columna con su rol; ningún valor corregido |
| P-001-43 | unit | SC-001-04, FR-001-12, FR-001-29 (texto) | `marcadores` y los de P-001-26 a P-001-42 | Todo texto de advertencia de fila contiene N.º o número de fila, columna y valor; los de archivo, hoja, columna o tabla nombran cuál; el texto de error de contrato dice lo esperado y lo encontrado, sin el nombre del archivo ni marcadores de celdas |

- [x] T-001-30 [US-001-2] Escribir P-001-28 y P-001-39 en `tests/integracion/test_v4_advertencias.py` (marca `raw`).
- [x] T-001-31 [P] [US-001-2] Escribir P-001-26, P-001-27, P-001-29 a P-001-38 y P-001-40 a P-001-43 en
  `tests/unit/test_advertencias.py`.

### Implementación de la historia 2

- [x] T-001-32 [US-001-2] Completar M04 con la lista cerrada de errores de contrato (hoja, encabezado de rol,
  delimitador, ancla empírica, intervenciones o nivel sin lista; invariantes, 2-nov-2026), que devuelve `FalloContrato`
  sin esquema parcial, y con las advertencias y notas de estructura (bloque degenerado, rol dentro del bloque, `1,0`
  fuera del bloque, columna del bloque sin `1,0`, lista sin «No aplica», varias anclas empíricas, columnas categóricas
  sin lista, columnas no usadas). Requisitos: FR-001-02, FR-001-03, FR-001-04, FR-001-12, FR-001-21, FR-001-22,
  FR-001-23. Pruebas: P-001-29 a P-001-37, P-001-40, P-001-42. Módulos: M04. Archivos: `src/egm/esquema.py`.
- [x] T-001-33 [US-001-2] Completar M05 con las advertencias por fila: valor fuera de lista en todas las filas, espacios
  en los extremos, dimensión fuera de $\{0,1,\varnothing\}$ o escrita como texto, año no reconocido, `N°` vacío o
  repetido, $G_r = H_r$, no empírico con intervención, tipo de documento fuera de lista, enfoque sin prefijo. Ninguna
  corrige el valor. Requisitos: FR-001-10, FR-001-12, FR-001-13, FR-001-24. Pruebas: P-001-26 a P-001-28, P-001-38,
  P-001-39, P-001-41, P-001-42. Módulos: M05. Archivos: `src/egm/lectura.py`.
- [x] T-001-34 [US-001-2] Ampliar M10 con `advertencia()`, `nota()` y `error_contrato()` (lo esperado y lo encontrado,
  sin nombre de archivo ni filas de datos; textos E4 de `flujos.md` §2 y el ejemplo de F-001-2). Los textos que
  `flujos.md` no fija se redactan con sus mismas reglas y Jairo los revisa en T-001-93. Requisitos: FR-001-02,
  FR-001-10, FR-001-12, FR-001-21, FR-001-23, NFR-000-03. Pruebas: P-001-39, P-001-43, P-001-09. Módulos: M10.
  Archivos: `src/egm/textos.py`.

**Punto de control**: las historias 1 y 2 funcionan cada una por separado. El implementador se detiene y resume.

---

## Fase 5: Historia 3 — Verificar contra la hoja EGM (prioridad: P2; adelantada por dependencia)

**Objetivo**: comparar los conteos con las tablas comparables 1, 2 y 4 de la hoja EGM según el contrato §7 y ADR-002,
clasificar cada tabla y explicar las diferencias de causa conocida.

**Prueba independiente**: con fixtures que traen valores guardados (spec 001, historia 3), llamando a
`egm.verificacion.verificar(libro, esquema, corpus)`.

### Pruebas de la historia 3 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-44 | unit | US-001-3.1, FR-001-14 | `esc_3_1_coincide` | Las tres tablas «coincide» |
| P-001-45 | unit | US-001-3.2, FR-001-18, CB-07 | `esc_3_2_difiere_g_igual_h` | «Difiere»; celdas indicadas; explicación por la fila con $G_r = H_r$, listada |
| P-001-46 | integración (`raw`) | US-001-3.3, FR-001-16, FR-001-17, FR-001-25, SC-001-01, CB-30 | v4; `cb30_sin_valores_guardados` | «No verificable» con advertencia; lista de tablas verificadas vacía; ningún ausente tomado como 0 |
| P-001-47 | unit | US-001-3.4, FR-001-16, CB-29 | `cb29_sin_hoja_egm` | Mapa calculado; «no verificable» con advertencia; ningún `FalloContrato` |
| P-001-48 | unit | US-001-3.5, FR-001-15 | `esc_3_5_filas_vacias_antes` | Tablas localizadas por título; «coincide» |
| P-001-49 | unit | US-001-3.6, FR-001-16, CB-29 | `cb29_titulo_cambiado` | Esa tabla «no verificable» con advertencia; las otras comparadas |
| P-001-50 | unit | US-001-3.7, FR-001-25 | `esc_3_7_titulos_1_2_4` | Verificadas = (1, 2, 4); la tabla no comparable del fixture no se lee, no aparece ni genera advertencia (ADR-002 punto 6) |
| P-001-51 | unit | US-001-3.8, FR-001-18, CB-41 | `cb41_texto_1` | «Difiere»; explicación por la fila con la dimensión escrita como texto, listada |
| P-001-52 | unit | US-001-3.9, FR-001-15, FR-001-26 | `esc_3_9_nombres_repetidos_entre_tablas` | Cada valor comparado dentro de su tabla, incluida la de nivel; las tres «coincide» |
| P-001-53 | unit | US-001-3.10, FR-001-26, CB-03 | `esc_3_10_total_entre_dimensiones` | «Total estudios» comparada con $u$; el estudio sin dimensiones cuenta allí; «coincide» |
| P-001-54 | unit | US-001-3.11, FR-001-27, NFR-000-06, CB-31, CB-36 | `cb31_categoria_nueva` | Esas tablas «no verificable»; la advertencia nombra la intervención; el mapa la incluye |
| P-001-55 | unit | US-001-3.12, FR-001-27, NFR-000-06, CB-32, CB-40 | `cb32_categoria_solo_en_hoja` | «No verificable»; la advertencia nombra esa fila |
| P-001-56 | unit | US-001-3.13, FR-001-17, FR-001-27, CB-33 | `cb33_parcial_sin_diferencia` | «No verificable»; la advertencia dice cuántos faltaron |
| P-001-57 | unit | US-001-3.14, FR-001-27, CB-33 | `cb33_parcial_con_diferencia` | «Difiere» con ese valor; advertencia de lo no comparado |
| P-001-58 | unit | US-001-3.15, FR-001-26, CB-35 | `cb35_nombre_repetido` | «No verificable»; la advertencia nombra la fila |
| P-001-59 | unit | US-001-3.16, FR-001-26, CB-34 | `cb34_sin_total`, `cb34_total_repetido` | «No verificable»; la advertencia lo indica |
| P-001-60 | unit | US-001-3.17, FR-001-18 | `esc_3_17_espacios` | «Difiere»; explicación por la fila con espacios en los extremos, listada |
| P-001-61 | unit | US-001-1.5 (advertencia), CB-12 | `cb12_250_documentos` (fórmulas sobre las filas 2 a 200) | Advertencia de que la hoja abarca menos filas; la comparación usa solo las filas que abarcan las fórmulas (ADR-002 punto 2) |
| P-001-62 | unit | US-001-2.10 (tabla), FR-001-23, CB-21 | `cb21_sin_ancla_ie` | La tabla de evaluación de impacto «no verificable» sin aplicar el punto 9 del contrato §7 |
| P-001-63 | propiedades | SC-001-03, FR-001-14 | estrategias de M23 con hoja EGM | Con valores guardados escritos por un oráculo de la prueba con la semántica de la hoja, sin $G_r = H_r$, sin texto «1» y sin espacios: las tres tablas «coincide»; los invariantes del §5 se cumplen sobre las filas que abarcan las fórmulas |
| P-001-64 | unit | FR-001-25, FR-001-18, NFR-000-03 | `esc_3_1_coincide`, `esc_3_2_difiere_g_igual_h`, `cb30_sin_valores_guardados` | Textos de F-001-3: «Tablas verificadas: 1, 2 y 4»; «no verificable» sin lista; «difiere» con su causa; ningún texto nombra otra tabla de la hoja |

- [x] T-001-40 [US-001-3] Escribir P-001-46 en `tests/integracion/test_v4_verificacion.py` (marca `raw`).
- [x] T-001-41 [P] [US-001-3] Escribir P-001-44, P-001-45, P-001-47 a P-001-62 y P-001-64 en
  `tests/unit/test_verificacion.py`.
- [x] T-001-42 [P] [US-001-3] Escribir P-001-63 en `tests/propiedades/test_verificacion_propiedades.py`.

### Implementación de la historia 3

- [x] T-001-43 [US-001-3] Implementar en M08 la localización y el alcance: hoja EGM, títulos con número y punto más su
  frase (contrato §7.2; ninguno o más de uno ⇒ no reconocida), alcance de cada tabla (§7.7) y emparejamiento de filas y
  columnas dentro de ella, incluida «Total estudios» (§7.8). No localiza ni lee ninguna tabla que no sea comparable.
  Requisitos: FR-001-15, FR-001-26. Pruebas: P-001-48, P-001-49, P-001-50, P-001-52, P-001-53, P-001-58, P-001-59.
  Módulos: M08, M03. Archivos: `src/egm/verificacion.py`.
- [x] T-001-44 [US-001-3] Implementar en M08 la comparación: valor comparable solo numérico (ADR-002 punto 1), filas
  que abarcan las fórmulas (punto 2) con su advertencia, $D_k$ y $V_k$, clasificación y lista de verificadas
  (contrato §7.9; ADR-002 punto 4), casos «no verificable» del §7.5 y sin ancla de evaluación de impacto, advertencias
  de lo no comparado. Depende de T-001-43. Requisitos: FR-001-12, FR-001-14, FR-001-16, FR-001-17, FR-001-25,
  FR-001-27. Pruebas: P-001-44, P-001-46, P-001-47, P-001-54 a P-001-57, P-001-61, P-001-62, P-001-63. Módulos: M08,
  M07. Archivos: `src/egm/verificacion.py`.
- [x] T-001-45 [US-001-3] Implementar la explicación de diferencias en el orden de ADR-002 punto 3: ampliar
  `semantica_hoja` de M07 con las variantes «texto 1 como marca» y «sin quitar espacios», y en M08 listar las filas de
  cada causa. Depende de T-001-44. Requisitos: FR-001-18. Pruebas: P-001-45, P-001-51, P-001-60. Módulos: M07, M08.
  Archivos: `src/egm/conteo.py`, `src/egm/verificacion.py`.
- [x] T-001-46 [US-001-3] Ampliar M10 con `verificacion()` y los textos de F-001-3. Requisitos: FR-001-18, FR-001-25,
  NFR-000-03. Pruebas: P-001-64. Módulos: M10. Archivos: `src/egm/textos.py`.

**Punto de control**: las historias 1, 2 y 3 funcionan cada una por separado. El implementador se detiene y resume.

---

## Fase 6: Fachada del núcleo — hito N1 «núcleo listo» (transversal a las historias 1 a 4)

**Objetivo**: `egm.procesamiento.procesar` encadena validar, abrir, descubrir, leer y verificar, sin resultados
parciales, y deja congelada la interfaz que consumen los planes 002 y 003.

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-65 | integración (`raw`) | US-001-1.7 (identificación), FR-001-19 | v4 | `ResultadoLectura.identificacion` con el nombre tal como llegó y la fecha inyectada |
| P-001-66 | unit | SC-000-09, NFR-000-09 | `base_valida`, `esc_3_2_difiere_g_igual_h` | Dos llamadas con los mismos bytes y nombre, y fechas distintas, dan resultados iguales salvo la fecha |
| P-001-67 | unit | FR-001-02, FR-001-29 (sin parciales), US-001-2.4, US-001-2.7 | `cb14`, `cb15`, `cb20`, `cb24_nivel_sin_lista` | `procesar` devuelve solo `FalloContrato`, sin corpus ni conteos |
| P-001-68 | unit | SC-000-19, NFR-000-19, US-001-4.3, US-001-4.4, US-001-4.13 (núcleo); NC-ARQ-1 | CB-16, CB-17, `parte_mayor_que_lo_declarado` | `Rechazo` con su motivo antes de abrir el libro (`abrir` no se llama); la parte que excede lo declarado ⇒ `Rechazo("tipo")` |
| P-001-69 | unit | FR-001-18 (orden) | `esc_3_2_difiere_g_igual_h` | En `ResultadoLectura.advertencias` las de verificación van primero (ADR-002 punto 5) |
| P-001-70 | unit | SC-000-14, NFR-000-14 | `base_valida` | En un proceso aparte, `procesar` y los conteos corren sin que `app`, FastAPI, Starlette, Jinja2 ni Uvicorn queden cargados |

- [x] T-001-50 Escribir P-001-65 en `tests/integracion/test_v4_procesar.py` (marca `raw`) y P-001-66 a P-001-70 en
  `tests/unit/test_procesamiento.py`.
- [x] T-001-51 Implementar M13 `egm.procesamiento.procesar(contenido, nombre_archivo, fecha_lectura)`: M02; M03 (toda
  excepción al abrir ⇒ `Rechazo("tipo")`, el trato de archivo dañado); M04 (`FalloContrato` ⇒ fin); M05; M08; arma
  `ResultadoLectura` con identificación, advertencias de verificación primero y notas. Requisitos: FR-001-02,
  FR-001-18, FR-001-19, FR-001-29, NFR-000-09, NFR-000-14, NFR-000-19. Pruebas: P-001-65 a P-001-70. Módulos: M13.
  Archivos: `src/egm/procesamiento.py`.
- [x] T-001-52 Congelar la interfaz pública del núcleo del plan 001 (`__all__`, docstrings en español, `mypy --strict`
  sin errores) y resumir para Jairo lo que queda disponible para 002 y 003 (ver «Dependencias con otros módulos o
  specs»). Requisitos: NFR-000-14. Pruebas: P-001-10, P-001-70. Módulos: M01, M04, M05, M07, M08, M10, M13. Archivos:
  `src/egm/*`.

**Punto de control — hito N1**: todo el núcleo del plan 001 en verde, cobertura de `src/egm/` ≥ 90 %. El
implementador se detiene y resume.

---

## Fase 7: Historia 4 — Cargar la matriz (prioridad: P1) — hito N2 «base web lista»

**Objetivo**: la carga desde el navegador con las reglas de FR-001-29, la cabecera corrida, los avisos V2 y el colofón.

**Prueba independiente**: cargando archivos válidos y no válidos, sin revisar ningún conteo (spec 001, historia 4).

### Pruebas de la historia 4 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-71 | integración (cliente de pruebas) | US-001-4.2, ADR-005 punto 4 | — | V0: opción de cargar, el límite indicado, ninguna cifra; colofón «Datos. Aún no se ha cargado ninguna matriz.» |
| P-001-72 | integración | US-001-4.1, FR-001-19, FR-001-20, NFR-000-12 | `base_valida` | Ficha nueva; cabecera «Matriz: <nombre tal como llegó>, leída el <fecha>, <n> documentos»; resultado disponible en `GET /vista/resultado` |
| P-001-73 | integración | US-001-4.3, SC-000-19, CB-16 | `cb16_otro_tipo.txt`, `cb16_extension_xlsx_otro_contenido`, `cb16_danado` | Mensaje E2; ninguna cifra; ninguna sesión creada |
| P-001-74 | integración | US-001-4.4, SC-000-19, NFR-000-19 | CB-16 de 15 728 640 bytes y +1 (memoria) | El exacto se acepta; el de +1 recibe E3 con el límite; la lectura del cuerpo se corta al pasar el límite, sin leer el resto |
| P-001-75 | integración | US-001-4.13, SC-000-19, FR-001-29 | sesión con `base_valida`; CB-17 exacto y +1 | El exacto se acepta; el +1 recibe E10, sin cifras ni resultados del rechazado; la sesión anterior y sus resultados siguen |
| P-001-76 | integración | US-001-4.5, FR-001-20 | `base_valida`, luego `sesion_b` | Solo los resultados del nuevo; la misma ficha ya no da los del anterior |
| P-001-77 | integración | US-001-4.7, FR-001-29, NFR-000-17 | `marcadores`, luego `cb14_sin_nivel_de_evidencia` | E4 con matriz previa (lo esperado y lo encontrado), sin nombre del archivo ni marcadores; la sesión terminó y la ficha anterior ya no abre nada |
| P-001-78 | integración | US-001-4.8, FR-001-29 | `base_valida`, luego `esc_2_1_fuera_de_lista_n3` | Aceptado con su advertencia; resultados solo del nuevo |
| P-001-79 | integración | US-001-4.9, FR-001-29, CB-18 | `base_valida`, luego `cb18_columna_observaciones` | Aceptado con la nota «columnas no usadas: Observaciones»; resultados solo del nuevo |
| P-001-80 | integración | US-001-4.11, FR-001-29 | `base_valida`, luego CB-16 (tipo y tamaño) | Mensaje del rechazo; la matriz anterior y sus resultados siguen disponibles (texto «E2 / E3 / E10 con matriz previa») |
| P-001-81 | integración | US-001-4.12, FR-001-29, CB-14 | `cb14_sin_nivel_de_evidencia` | Mensaje que nombra «Nivel de evidencia», sin nombre del archivo ni filas de datos, ninguna cifra |
| P-001-82 | integración | SC-000-12, NFR-000-12 | `sc000_12_otro_nombre_v4` | Cabecera y colofón con ese nombre, esa fecha y ese número; ninguna versión deducida |
| P-001-83 | integración | NFR-000-11, SC-000-11 (parte automática), ADR-005 puntos 2, 3 y 5 | `base_valida`; configuración por defecto y de prueba con todos los bloques encendidos | Por defecto: solo «Datos» y la referencia a 3ie, ningún texto ni logo de la Universidad del Magdalena y ningún rastro de los bloques apagados en el HTML. Todo encendido: código y correo; sin categoría, línea de investigación ni marcador de pendiente; la línea «Herramienta» omitida mientras siga pendiente; un logo sin archivo se omite completo |
| P-001-84 | integración | NFR-000-17 (carga y registros), SC-000-17 (parte de la carga) | `marcadores` | Durante y después de la carga no aparece ningún archivo nuevo en la carpeta temporal del sistema ni en la de la aplicación; la carga no usa el analizador multiparte; los registros no contienen marcadores ni el nombre del archivo; registro de accesos apagado; cabeceras de seguridad sin recursos externos |
| P-001-85 | navegador | SC-000-15, NFR-000-15, US-001-4.1 | `base_valida` | En Chromium sobre `127.0.0.1`: elegir el archivo, ver E1 y luego la cabecera; todas las peticiones van a `127.0.0.1` |
| P-001-86 | navegador | SC-000-04, SC-000-05 (base), NFR-000-04, NFR-000-05 | `base_valida`, CB-14, CB-16, CB-17 | axe-core sin hallazgos de nivel A o AA en V0, E2, E3, E4, E10, V2, cabecera y colofón; a 360 px, sin desplazamiento horizontal; el foco pasa al título del mensaje; `role="alert"` y `role="status"` según `flujos.md` §2 |
| P-001-87 | integración | FR-001-18, FR-001-25, FR-001-12 (presentación) | `esc_3_2_difiere_g_igual_h`, `esc_3_1_coincide` | En `GET /vista/resultado` el bloque «Antes de leer los resultados» va antes de cualquier cifra: primero la verificación, luego las advertencias, luego las notas |
| P-001-88 | integración | SC-000-18 (resultados), NFR-000-18 | `sesion_a`, `sesion_b` | Dos fichas, cada una ve solo sus resultados; una ficha no abre la otra sesión |

- [x] T-001-60 [US-001-4] Escribir P-001-71 a P-001-84, P-001-87 y P-001-88 en `tests/integracion/test_carga_web.py`.
- [x] T-001-61 [P] [US-001-4] Escribir P-001-85 y P-001-86 en `tests/navegador/test_carga_navegador.py` (marca
  `navegador`).

### Implementación de la historia 4

- [x] T-001-62 [P] [US-001-4] Implementar M22 `app.configuracion.cargar_configuracion`: archivo de texto opcional junto
  a la instalación (TOML, leído con la biblioteca estándar), bloques del colofón todos apagados por defecto, puerto
  por defecto 8000; sin límite de tamaño ni inactividad, que son fijos en el código. Requisitos: NFR-000-11. Pruebas:
  P-001-83. Módulos: M22. Archivos: `app/configuracion.py`.
- [x] T-001-63 [US-001-4] Implementar M21 `app.colofon.componer` con los bloques y reglas de ADR-005 (bloque «Datos»
  con el texto de NFR-000-12 en tiempo de ejecución o «Aún no se ha cargado ninguna matriz.»; «Referencia de diseño»
  siempre presente; bloque con marca de pendiente o logo inexistente omitido completo). Depende de T-001-62.
  Requisitos: NFR-000-11, NFR-000-12. Pruebas: P-001-71, P-001-82, P-001-83. Módulos: M21. Archivos:
  `app/colofon.py`.
- [x] T-001-64 [US-001-4] Implementar M15 `app.sesiones.AlmacenSesiones` (parte de la carga): ficha aleatoria de
  256 bits, `crear`, `reemplazar` (deja vacío el filtro aplicado; el tipo `Filtro` llega con el plan 002), `obtener`,
  `terminar` con su causa; ninguna sesión ve otra. Requisitos: NFR-000-17, NFR-000-18, FR-001-20, FR-001-29.
  Pruebas: P-001-76, P-001-77, P-001-88. Módulos: M15. Archivos: `app/sesiones.py`.
- [x] T-001-65 [US-001-4] Implementar M16 `app.carga.recibir`: cuerpo crudo leído en flujo con corte al pasar
  `LIMITE_BYTES`, nombre desde `X-EGM-Nombre`, llamada a `procesar` con la fecha de lectura, reglas de FR-001-29
  (rechazo ⇒ conserva; error de contrato ⇒ termina y limpia; aceptada ⇒ crea o reemplaza), bytes soltados al terminar.
  Depende de T-001-64. Requisitos: FR-001-20, FR-001-29, NFR-000-01, NFR-000-17, NFR-000-19. Pruebas: P-001-72 a
  P-001-81, P-001-84. Módulos: M16. Archivos: `app/carga.py`.
- [x] T-001-66 [US-001-4] Implementar en M17 `vista_inicio`, la cabecera corrida, el bloque de avisos V2 (verificación,
  advertencias y notas, en ese orden, antes de cualquier cifra) y el colofón como modelos de vista inmutables, más la
  vista de resultado de NC-P001-1. Requisitos: FR-001-12, FR-001-18, FR-001-19, FR-001-25, NFR-000-12. Pruebas:
  P-001-71, P-001-72, P-001-82, P-001-87. Módulos: M17. Archivos: `app/presentacion.py`.
- [x] T-001-67 [P] [US-001-4] (`disenador-front`) Escribir en M18 las plantillas base, V0, mensajes E1 a E4 y E10,
  avisos V2, cabecera corrida y colofón, y la hoja de estilo «Fichero» base con modo claro y oscuro, a partir de
  `docs/interfaz/bocetos/carga.html` y `colofon.html`; tipografías Alegreya y Alegreya Sans servidas localmente con su
  licencia; sin estilos en línea. El `implementador` las conecta. Requisitos: NFR-000-03, NFR-000-04, NFR-000-05,
  NFR-000-11, NFR-000-13. Pruebas: P-001-86. Módulos: M18. Archivos: `app/plantillas/*`, `app/estaticos/*`.
- [x] T-001-68 [US-001-4] Implementar en M19 la carga: enviar el archivo como cuerpo crudo con el nombre en
  `X-EGM-Nombre`, guardar la ficha en el almacenamiento de la pestaña y enviarla en `X-EGM-Sesion` en toda petición de
  htmx, estado E1, foco y anuncios accesibles; htmx servido localmente sin estilos en línea. Requisitos: FR-001-20,
  NFR-000-04, NFR-000-17. Pruebas: P-001-85, P-001-86. Módulos: M19. Archivos: `app/cliente/*`.
- [x] T-001-69 [US-001-4] Implementar M14 `app.servidor.crear_app`: rutas de la tabla «Rutas de la capa web» (las de
  carga, inicio y resultado), cabeceras de seguridad con política de contenido sin recursos externos, política de
  registros (sin accesos, sin cuerpos ni cabeceras, errores solo por tipo y módulo) y el arranque
  `python -m app.servidor` en `127.0.0.1`. Requisitos: NFR-000-15, NFR-000-17. Pruebas: P-001-71, P-001-84, P-001-85.
  Módulos: M14. Archivos: `app/servidor.py`.
- [x] T-001-70 [US-001-4] Ampliar M10 con los textos de carga con y sin matriz previa (E2, E3, E10 y E4 con matriz
  previa) y la cabecera corrida, tal como los fija `flujos.md` §2 y §3. Requisitos: FR-001-29, NFR-000-03. Pruebas:
  P-001-77, P-001-80, P-001-81. Módulos: M10. Archivos: `src/egm/textos.py`.

**Punto de control — hito N2**: la historia 4 funciona y se prueba sola; `crear_app` admite las rutas de 002 y 003. El
implementador se detiene y resume.

---

## Fase 8: Historia 5 — Terminar la sesión (prioridad: P2)

**Objetivo**: terminar la sesión al descartar, al cerrar la pestaña, tras 45 minutos sin actividad o con un error de
contrato en una carga nueva (este último ya cubierto por P-001-77), sin dejar copia.

**Prueba independiente**: cargando una matriz sintética y terminando la sesión de cada forma (spec 001, historia 5).
Los escenarios de actividad sobre el mapa (US-001-5.4 a 5.6) van en el plan 002.

### Pruebas de la historia 5 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-001-89 | integración | US-001-5.1, FR-001-28 | `base_valida` | `POST /sesion/descartar` termina la sesión; E8 «Descartó el archivo…»; ninguna cifra; la ficha ya no abre nada |
| P-001-90 | navegador | US-001-5.2, ADR-003 punto 9 | `base_valida` | Cerrar la pestaña y abrir otra: V0 sin cifras; pasados 10 s el servidor ya no tiene la sesión; recargar antes de 10 s la conserva (E9) |
| P-001-91 | integración | US-001-5.3, NFR-000-17 | `base_valida` (reloj inyectado) | A 44 min 59 s la sesión sigue; a 45 min se purga; mensaje E8 de inactividad |
| P-001-92 | integración y navegador | SC-000-17, NFR-000-17 | `marcadores` | Tras cada una de las cuatro formas de terminar, ningún marcador en la carpeta temporal del sistema, en la carpeta de la aplicación ni en los registros, y la sesión no se puede abrir (la de cierre de pestaña, pasados 10 s); una interacción antes de los 45 min la mantiene abierta |
| P-001-93 | navegador | NFR-000-04 (WCAG 2.2.1), NFR-000-17 | `base_valida` (reloj simulado) | E7 a los 43 min con «Seguir con la sesión»; pulsarlo, u otra interacción, reinicia la cuenta |
| P-001-94 | navegador | NFR-000-17 (actividad), ADR-003 punto 5 | `base_valida` (reloj simulado) | Puntero, teclado, toque, foco y desplazamiento cuentan; como máximo un latido por minuto; el primero tras un silencio sale de inmediato |
| P-001-95 | integración | NFR-000-18, SC-000-18 (fin) | `sesion_a`, `sesion_b` | Terminar una sesión no afecta a la otra |

- [x] T-001-80 [US-001-5] Escribir P-001-89, P-001-91, P-001-95 y la parte de cliente de pruebas de P-001-92 en
  `tests/integracion/test_sesion.py`.
- [x] T-001-81 [P] [US-001-5] Escribir P-001-90, P-001-93, P-001-94 y la parte de navegador de P-001-92 en
  `tests/navegador/test_sesion_navegador.py`.

### Implementación de la historia 5

- [x] T-001-82 [US-001-5] Completar M15: `INACTIVIDAD` (45 min, fijo), `GRACIA_CIERRE` (10 s, fijo),
  `registrar_actividad`, `purgar_vencidas(ahora)` con reloj inyectable, tarea periódica de purga atada al ciclo de vida
  de la aplicación y borrado por aviso de cierre salvo que la ficha vuelva. Requisitos: FR-001-28, NFR-000-17,
  NFR-000-18. Pruebas: P-001-89, P-001-90, P-001-91, P-001-95. Módulos: M15. Archivos: `app/sesiones.py`.
- [x] T-001-83 [US-001-5] Agregar en M14 las rutas `POST /sesion/descartar`, `POST /sesion/latido` y
  `POST /sesion/cierre`. Depende de T-001-82. Requisitos: FR-001-28, NFR-000-17. Pruebas: P-001-89, P-001-92.
  Módulos: M14. Archivos: `app/servidor.py`.
- [x] T-001-84 [US-001-5] Completar M19: registro de actividad, latido como máximo una vez por minuto, aviso de cierre
  al ocultarse la página (con la ficha en la petición), temporizador visible E7, E8 y E9, botón «Descartar el archivo».
  Requisitos: FR-001-28, NFR-000-04, NFR-000-17. Pruebas: P-001-90, P-001-92, P-001-93, P-001-94. Módulos: M19.
  Archivos: `app/cliente/*`.
- [x] T-001-85 [P] [US-001-5] Ampliar M10 y M18 con los textos y plantillas de E7, E8 y E9 de `flujos.md` §2 y el
  texto fijo de la cabecera de F-001-5 (`disenador-front` en las plantillas). Requisitos: NFR-000-03, NFR-000-04,
  FR-001-28. Pruebas: P-001-89, P-001-93. Módulos: M10, M18. Archivos: `src/egm/textos.py`, `app/plantillas/*`.

**Punto de control**: todas las historias funcionan de forma independiente. El implementador se detiene y resume.

---

## Fase 9: Cierre y aspectos transversales

- [x] T-001-90 Actualizar `docs/specs/trazabilidad.md`: columna «Prueba» de cada requisito del plan y estado `implementado` de los requisitos
  cuyas tareas, en todos los planes, estén terminadas (regla de estados de `trazabilidad.md`). La columna «Tarea» ya
  está llena desde la Fase 3. Requisitos: todos los del plan.
- [x] T-001-91 Limpieza y refactorización sin cambiar comportamiento (pruebas en verde). Requisitos: —.
- [x] T-001-92 [P] Cobertura ≥ 90 % de líneas en `src/egm/`, `ruff` y `mypy --strict` sin errores. Requisitos: —
  (`calidad-python`).
- [ ] T-001-93 Revisión de Jairo del catálogo de textos M10 de este plan (SC-000-03) y de la legibilidad de las
  advertencias (SC-001-04): de usted, sin jerga, sin fórmulas, sin preguntas, sin mención de la tabla no comparable.
  Requisitos: NFR-000-03, FR-001-12.
- [ ] T-001-94 Revisión de Jairo de V0, V1, V2, cabecera y colofón contra «Fichero» (SC-000-13) y revisión manual del
  colofón en modo claro y oscuro y a 360 px (SC-000-11, sujeto a NC-P001-2). Requisitos: NFR-000-11, NFR-000-13.
- [ ] T-001-95 Solicitar la verificación al subagente `verificador`. Requisitos: —.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)**: sin dependencias. T-001-09 (NC-ARQ-1) bloquea T-001-13 y T-001-15.
- **Base (fase 2)**: depende de la fase 1; bloquea todas las historias.
- **Historias 1, 2 y 3 (fases 3 a 5)**: en ese orden, una a la vez; la 2 completa M04 y M05 de la 1; la 3 usa la 1.
- **Fachada (fase 6, hito N1)**: depende de las fases 3 a 5.
- **Historia 4 (fase 7, hito N2)**: depende del hito N1.
- **Historia 5 (fase 8)**: depende de la historia 4 (sesión creada por la carga).
- **Cierre (fase 9)**: depende de todas.

### Dependencias entre historias

- **Historia 1 (P1)**: tras la fase 2; sin dependencias de otras historias.
- **Historia 2 (P1)**: tras la 1, porque amplía los mismos módulos; se prueba sola.
- **Historia 3 (P2)**: tras la 1; se prueba sola con `verificar`.
- **Historia 4 (P1)**: tras el hito N1; se prueba sola, sin revisar conteos.
- **Historia 5 (P2)**: tras la 4.

### Dependencias con otros módulos o specs (lo que este plan expone a 002 y 003)

- **Hito N1 (núcleo)** · estado: pendiente.
  - M13 `procesar(contenido, nombre_archivo, fecha_lectura) -> ResultadoLectura | Rechazo | FalloContrato`.
  - M01: `RefFila`, `Conteo`, `Documento`, `Corpus`, `Esquema`, `ResultadoLectura`, `Identificacion`, `Advertencia`,
    `Nota`, `EstadoDocumento`, `Enfoque`, `SIN_NIVEL`.
  - M04 `Esquema` (orden del archivo, listas con su origen, anclas); M05 `Corpus`, `Documento` (textos tal cual,
    enfoque, estado) y `clasificar_enfoque`.
  - M07 `conjuntos`, `mapa` (sin filtro; `Celda` con `conteo`), `evaluacion_impacto`, `por_intervencion`,
    `por_nivel`, `semantica_hoja`. El plan 002 agrega el parámetro `filtro` (por defecto `SIN_FILTRO`) a `conjuntos`,
    `mapa` y `evaluacion_impacto`, y el desglose por nivel en `Celda`; el 003, `coocurrencias` (arquitectura §6.1, M07).
  - M08 `Verificacion` y `ResultadoTabla` para los avisos de 002 (US-002-1.5, 1.6) y la cifra de confianza de 003
    (FR-003-20).
  - M10 `advertencia`, `nota`, `error_contrato`, `rechazo`, `verificacion`, `fecha` y `ROTULOS` (vacío, para 002 y 003).
- **Hito N2 (web)** · estado: pendiente.
  - M14 `crear_app(config)` con registro de rutas por módulo; M15 `AlmacenSesiones` con el espacio del filtro aplicado
    (002 agrega `aplicar_filtro`); M17 cabecera, avisos y colofón; M18 plantilla base y CSS «Fichero» base; M19 guion
    con la ficha en cada petición (002 agrega teclado en la cajonera y PNG); M21 colofón;
    M22 `Configuracion` (002 agrega la ruta de definiciones; 003, la política de porcentajes).
- **Fase 8 (sesión)** · estado: pendiente. M15 con reloj inyectable, `INACTIVIDAD`, `GRACIA_CIERRE` y purga; M19 con registro de actividad, latido y aviso de cierre. Los usan P-002-19, P-002-38 y P-002-48; adelantar el plan 002 tras N1 no los incluye.
- **Fixtures (M23)** · estado: pendiente (fase 1).
  - `MatrizSintetica` y `.a_bytes()`, estrategias de hypothesis, catálogo CB-01 a CB-41 (con CB-05 para FR-002-12,
    CB-06 para FR-003-14 y CB-21 para la conclusión 2), `base_valida`, FX-A (`instancia_ejemplo.xlsx`), `sc000_06_*`, `marcadores`, `sesion_a`,
    `sesion_b`. Los planes 002 y 003 amplían el constructor; no lo reescriben.
- **Del plan 002 hacia este plan**: US-001-4.10 y US-001-5.4 a 5.6 se prueban allí con las piezas de este plan.
- **Del plan 003 hacia este plan**: US-001-4.6 completo (huella tras usar todas las vistas; P-003-67 del plan 003).

Propuesta para el plazo: si Jairo lo decide, el trabajo del núcleo del plan 002 (M06, ampliación de M07) solo necesita
el hito N1 y podría empezar antes de cerrar este plan; hoy la regla es un plan a la vez, y este plan no la cambia.

### Dentro de cada historia

- Pruebas primero: se escriben y se comprueba que fallan.
- Modelo antes que análisis; análisis antes que capa web.
- Núcleo antes que la integración.
- Historia terminada (pruebas en verde) antes de pasar a la siguiente.

## Riesgos y decisiones abiertas

- **R-1. NC-ARQ-1** (heredado de arquitectura §9 y §10): qué hace la biblioteca de lectura ante una parte que se
  descomprime a más de lo declarado. → T-001-09 lo comprueba en memoria con un fixture sintético y P-001-02 lo fija.
  Esperado por el spec: archivo dañado (`Rechazo("tipo")`). Si la biblioteca lee de más sin error, se detiene el plan y
  va a `analista-impacto` (corrección nueva). **Resultado de T-001-09 (2026-11-24; Python 3.13.15, openpyxl 3.1.5;
  fijado en P-001-02, `tests/unit/test_nc_arq_1.py`)**: la biblioteca **no lee de más**. `zipfile` acota la lectura de cada parte
  al tamaño que declara el índice. Con el libro `parte_mayor_que_lo_declarado` (la parte descomprime a 1 048 576 bytes;
  el índice declara 9 284), `testzip()` devuelve el nombre de la parte, `read()` y `open().read()` lanzan
  `BadZipFile("Bad CRC-32 …")` sin entregar la parte, y `openpyxl.load_workbook` lanza `BadZipFile` en modo normal y
  en `read_only=True`; es decir, el libro no se abre, como espera el spec (`Rechazo("tipo")`). Si el índice trajera además un CRC-32 coherente con lo declarado
  (paquete armado a propósito), `zipfile` entrega exactamente los bytes declarados sin error y `openpyxl` falla con
  `xml.etree.ElementTree.ParseError` (al abrir en modo normal; al leer la hoja en `read_only=True`) si el recorte parte el XML, o
  lee el libro completo si el recorte cae tras el cierre de la hoja. **Efecto para T-001-13 y T-001-15**: no hace falta
  detener el plan; M03 debe tratar `BadZipFile` y también `ParseError` como archivo dañado. NC-ARQ-1 resuelto.
- **R-2. Vista tras una carga aceptada** mientras no exista el mapa del plan 002. `flujos.md` F-001-4 dice que la carga
  aceptada abre el mapa (V3), que crea el plan 002. → Propuesta: este plan crea `GET /vista/resultado` con la cabecera
  corrida, el bloque V2 y el colofón, y el plan 002 la convierte en la vista del mapa agregando la cajonera; no se crea
  ningún módulo nuevo. **NC-P001-1, decidido por Jairo el 22-nov-2026**: mientras no exista el mapa, una carga aceptada
  lleva a una vista provisional `/vista/resultado` (verificación, advertencias y cifras básicas); con el plan 002 la
  carga lleva al mapa. Las cifras básicas son las de la cabecera corrida («Matriz: <nombre>, leída el <fecha>, <n>
  documentos»), como en la propuesta.
- **R-3. Logos del colofón**: el repositorio no tiene los archivos de los logos de Minciencias ni de la Universidad del
  Magdalena. Con la configuración por defecto están apagados (ADR-005) y no afecta a la demostración; sí impide la
  parte de SC-000-11 que pide ver los dos logos con la configuración de prueba encendida. → P-001-83 comprueba que un
  logo sin archivo se omite completo; la revisión de T-001-94 queda sujeta a tener los archivos. **NC-P001-2, decidido por Jairo el 22-nov-2026**: la
  revisión visual de SC-000-11 con los logos encendidos espera a que Jairo tenga la autorización y los archivos; no
  bloquea la demostración.
- **R-4. Valores guardados en fixtures**: la escritura normal de `openpyxl` guarda la fórmula sin su valor calculado.
  → T-001-05 escribe el valor guardado en el XML de la celda del paquete generado; P-001-05 comprueba que se lee
  (ADR-002, «control del proceso»).
- **R-5. Validaciones y modo de carga**: `calidad-python` pide `read_only=True` para los datos; las validaciones
  podrían no estar disponibles en ese modo de `openpyxl`. → T-001-13 lo comprueba y usa el modo que entregue las
  validaciones (arquitectura §9 ya registró que la carga normal las lee en la v4). Si hay que apartarse de la skill, se
  anota como observación para una corrección nueva; no cambia ningún requisito.
- **R-6. htmx y la política de contenido**: htmx inserta estilos propios por defecto, lo que choca con «sin estilos en
  línea» (ADR-003 punto 6). → T-001-68 desactiva esa opción de htmx; P-001-86 lo comprueba sin errores de política en
  la consola.
- **R-7. Descargas externas** (htmx, Alegreya y Alegreya Sans, axe-core, Chromium de Playwright): se obtienen una vez de
  su distribución oficial, con su licencia, y se sirven o usan localmente. La herramienta no hace ninguna petición
  externa al usarse (ADR-003 punto 6). Jairo autoriza las descargas [Fuente: decisión de Jairo, 22-nov-2026].
- **R-8. Plazo del 6-dic-2026**: orden núcleo → web; hitos N1 y N2 como puntos de detención. Las pruebas de navegador
  (`navegador`) son las más lentas; corren aparte de las de unidad.

**Observaciones O-1 a O-4**: resueltas por COR-013 (22-nov-2026). O-1: el constructor es `tests/constructor.py` en todos los documentos. O-2: ADR-003, punto 2, aclarado (ver su nota de revisión del 2026-11-22). O-3: M07 se crea aquí sin `filtro` y el plan 002 lo agrega a `conjuntos`, `mapa` y `evaluacion_impacto` con su valor por defecto (arquitectura §6.1, M07). O-4: M21 crea aquí el bloque «Referencia de diseño» y SC-000-16 se verifica en el plan 002 (arquitectura §6.4).

## Definición de terminado

- [ ] Todas las pruebas del plan en verde (P-001-01 a P-001-95); cobertura ≥ 90 % en `src/egm/`.
- [ ] Lint y tipado sin errores.
- [ ] Cada requisito del apartado «Requisitos que cubre este plan» tiene tarea y prueba en `trazabilidad.md`.
- [ ] Cada número calculado es un `Conteo` trazable a su lista de N.º de fila.
- [ ] Ningún archivo de `data/raw/` ni `docs/fuentes/` modificado (P-001-15 comprueba la huella de la v4).
- [ ] Informe del `verificador` sin huecos ni excesos abiertos.
- [ ] Hito N1: `procesar` y la interfaz pública del núcleo del plan 001 congeladas y documentadas.
- [ ] Hito N2: `crear_app` lista para que 002 y 003 agreguen rutas.
- [ ] Un fixture por cada caso borde del contrato §9 (P-001-01).
- [ ] NC-ARQ-1 resuelto (P-001-02) y NC-P001-1 decidido por Jairo.
- [ ] Ningún texto ni prueba usa las cifras de la lámina 7; ningún texto nombra la tabla no comparable de la hoja EGM.
- [ ] La versión de Python del `.venv` registrada en el resumen de fase.

## `[NEEDS CLARIFICATION]` de este plan

| ID | Tema | Dónde se resuelve | Estado |
|---|---|---|---|
| NC-ARQ-1 | Parte del libro que se descomprime a más de lo declarado | T-001-09, P-001-02 | Resuelto en T-001-09, 2026-11-24 (R-1): no lee de más; falla con `BadZipFile` |
| NC-P001-1 | Vista del resultado de una carga aceptada antes del plan 002 | Jairo, sobre la propuesta de R-2 | Decidido por Jairo, 22-nov-2026 (R-2) |
| NC-P001-2 | Archivos de los logos para SC-000-11 | Jairo | Decidido por Jairo, 22-nov-2026 (R-3) |

## Notas

- La etiqueta [US-001-n] vincula la tarea con su historia para la trazabilidad.
- Cada historia debe poder terminarse y probarse por sí sola.
- Los commits los hace Jairo; al terminar cada historia y en cada hito, el implementador se detiene y resume.
- Si una tarea exige algo fuera del plan: detenerse y reportarlo; no ampliar el alcance.
- Los esperados salen del apéndice A del contrato o de fixtures descritos y se escriben a mano; nunca de la salida del
  código bajo prueba ni de la lámina 7.
- Un caso borde del spec, que no tiene ID propio, se cita por su texto entre comillas («caso borde «…»») y se entiende del spec de este plan. SC-000-03 se verifica por revisión manual (T-001-93 y sus equivalentes en los planes 002 y 003); en la columna «Prueba» de `trazabilidad.md` figura como «revisión manual (T-…)».
