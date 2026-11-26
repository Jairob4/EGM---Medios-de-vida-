# Informe de conformidad — cierre del plan 001 (T-001-95), versión definitiva

**Fecha**: 2026-11-26 · **Auditor**: `verificador` (no participó en producir lo auditado) · **Documento interno, para Jairo.**
**Plan auditado**: `docs/planes/001-lectura-verificacion/plan.md`, Fases 1 a 9 (T-001-01 a T-001-95 marcadas `[x]` en el
árbol de trabajo; T-001-93 y T-001-94 aprobadas por Jairo el 26-nov-2026, `plan.md:739-743`).
**Origen**: fusiona las dos auditorías independientes del mismo día, A (primera versión de este archivo) y B
(`conformidad-plan-001-2026-11-26-b.md`). Los puntos en que diferían se volvieron a comprobar en los archivos citados.
**Alcance**: cierre de un plan de implementación, no de un plan de corrección: no se dictamina ninguna `COR-NNN`. Solo
lectura; nada se corrigió.

---

## 1. Dictamen

**La implementación del plan 001 es conforme a sus specs, a la arquitectura y al plan.** No hay hallazgos de gravedad
alta, ni huecos (44 de 44 requisitos con componente, tarea y prueba; 95 de 95 pruebas P-001 localizadas; los 145 pares
«P-001-NN (`archivo`)» de `trazabilidad.md` existen), ni excesos de alcance en el código. Las reglas inviolables 1, 3, 4,
5, 6, 7, 8 y 10 se cumplen. Quedan 13 no conformidades, todas documentales o de trazabilidad: **ninguna exige cambiar
código**. Tres necesitan una decisión de Jairo (sección 4). El plan no queda formalmente «terminado» hasta resolver
NC-05 y NC-08 (sección 7).

---

## 2. Resultados de las herramientas

Python 3.13.15 del `.venv`.

| Comprobación | Resultado |
|---|---|
| `pytest -m "not navegador"` | **771 pasadas**, 0 fallidas, 0 omitidas, 63 deseleccionadas. Las pruebas `raw` corrieron |
| `pytest -m navegador --browser chromium --no-cov` | **63 pasadas**, 0 fallidas |
| Cobertura de `src/egm/` | **99,72 %** (umbral 90 %). Sin cubrir solo `src/egm/libro.py:124, 128, 148, 166` |
| `ruff check .` · `ruff format --check .` | «All checks passed!» · 73 archivos ya formateados |
| `mypy --strict src/egm` · `MYPYPATH=src mypy --strict app` | Sin errores en 10 y en 7 archivos |
| SHA-256 de `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual a `contrato-datos.md:374`, antes y después de las corridas |
| `git diff --quiet HEAD -- data/raw docs/fuentes` · `git status` | Sin cambios. Solo modificados `plan.md` y `trazabilidad.md` (marcas de T-001-93 a T-001-95; los estados no cambiaron) y sin rastrear el catálogo y los dos informes |

Total: 834 pruebas en verde. Las dos auditorías corrieron `pytest` por separado y obtuvieron las mismas cifras. Esta
fusión volvió a correr `ruff`, `mypy`, la huella y `git`, pero no `pytest`: `src/`, `app/`, `tests/` y `data/` no
cambiaron después de esas corridas (`git status`). En las pruebas, `data/raw/` solo se abre con `open(…, "rb")`
(`tests/integracion/test_v4_lectura.py:106-109`), siempre con la marca `raw`. Los esperados de la v4 se copiaron a mano
del apéndice A (`test_v4_lectura.py:36-100` frente a `contrato-datos.md:368-408`). No se revisaron a mano los esperados
de las 636 funciones de prueba, uno por uno.

---

## 3. No conformidades y observaciones

Origen: **A** = primer informe, **B** = segundo informe, **A+B** = los dos. Gravedad: Mod. = moderada; Men. = menor.

### 3.1 No conformidades

| ID | Grav. | Hallazgo | Evidencia | Origen |
|---|---|---|---|---|
| NC-01 | Mod. (documental) | Tensión entre la regla 9 y el spec. Con la v4, V2 muestra advertencias que describen A-01 (enfoque sin prefijo, N.º 2 y 7) y A-04 (hoja EGM sin valores guardados). La regla dice que esos hallazgos «nunca se mencionan en la interfaz», pero el spec y `flujos.md` exigen esos textos. El código cumple el spec | `CLAUDE.md:40`; `spec.md:412, 418, 429`; `flujos.md:107-108, 120-122`; `textos.py:159, 248, 308`; `hallazgos-matriz-para-equipo.md:26, 29` | A (M-1) + B (OBS-9, C-1) |
| NC-02 | Mod. (documental) | La numeración «Tabla 1 / 2 / 4» y «Tablas verificadas: 1, 2 y 4» deja ver por omisión que hay otra tabla, aunque no la nombra. FR-001-25 y US-001-3.7 obligan a usar el número del título | `textos.py:248, 302, 856`; `spec.md:427`; `flujos.md:123` | A (M-2) + B (OBS-9) |
| NC-03 | Mod. | El registro de la regla 9 está desactualizado: dice «Hoy no hay código», y sus siete filas dicen «Sin implementar» | `hallazgos-matriz-para-equipo.md:19-20, 26-29, 35-37`. Tabla para actualizarlo en la sección 5 | A (M-3) + B (NC-3) |
| NC-04 | Mod. | El código se aparta de R-5 y falta la corrección que el plan prometía. `egm.libro` abre el libro dos veces en modo normal porque `read_only=True` no entrega las validaciones. La skill sigue pidiendo `read_only=True`, y no existe la corrección nueva que preveían R-5 y COR-016 (solo hay COR-001 a COR-017). La decisión técnica está justificada y probada (P-001-05) | `calidad-python/SKILL.md:38`; `src/egm/libro.py:9-12, 296-297`; `plan.md:836-839`; `COR-016.md:210` | A (M-4, C-2) + B (C-2, D-7) |
| NC-05 | Men. | FR-001-12 y NFR-000-11 siguen en `planificado` aunque todas sus tareas están `[x]` y son del plan 001. Según la regla, les corresponde `implementado`. Causa: T-001-90 se cerró antes de aprobarse T-001-93 y T-001-94 | `trazabilidad.md:5, 19, 39`; `plan.md:490-505, 557-562, 640-667, 739-743` | A (m-1) + B (NC-1) |
| NC-06 | Men. | La columna «Tarea» de NFR-000-17 y de FR-001-29 no recoge el plan 002, que prueba US-001-4.10 y US-001-5.4 a 5.6. Ninguna tarea del plan 002 cita NFR-000-17 en «Requisitos». El estado `planificado` es correcto en la realidad, pero contradice la regla escrita | `trazabilidad.md:25, 56`; `002/plan.md:271, 340, 342, 400, 401, 479, 624` | A (m-2, C-3) + B (NC-2, C-3) |
| NC-07 | Men. | Hay docstrings de prueba sin el ID de escenario o SC que pide la skill. Las cifras de A (109) y de B (103) dependen del criterio; se recontaron: de 636 funciones, **348** no citan ningún `US-`/`SC-` (criterio literal de la skill), **109** no citan ningún `US-`, `SC-`, `FR-`, `NFR-`, `CB-` ni `NC-ARQ-`, y **103** si también se acepta un `P-` | Concentradas en `tests/unit/test_esquema.py` y `tests/unit/test_lectura.py` (93 de las 103). Una sola no cita nada: `tests/unit/test_semantica_hoja_variantes.py:163`. Los docstrings de módulo sí citan los FR | A (m-3) + B (NC-5); recuento nuevo |
| NC-08 | Men. | El plan tiene estados viejos y la definición de terminado sigue sin marcar. No existe el resumen de la fase de código con la versión de Python (solo `fase-1` a `fase-3-resumen.md`) | `plan.md:770, 782, 787, 788` («estado: pendiente»); `plan.md:853-864` | A (m-4) + B (OBS-5, NC-4) |
| NC-09 | Men. | T-001-52 está `[x]` y pide «resumir para Jairo lo que queda disponible para 002 y 003». Ese resumen no está en `docs/informes/` (pudo darse en la sesión; no se puede comprobar). La congelación sí está hecha (`__all__`, `mypy --strict` limpio) | `plan.md:595-598`; `fase-3-resumen.md:23` (anterior al código) | B (NC-4) |
| NC-10 | Men. | La arquitectura da NC-ARQ-1 por abierto, y el plan, por resuelto | `arquitectura.md:781, 786, 797` frente a `plan.md:810-819, 870` (P-001-02 en verde) | A (m-5, C-4) + B (OBS-6, C-5) |
| NC-11 | Men. | Once `[NEEDS CLARIFICATION]` del código y de las pruebas no figuran en la tabla del plan. Uno ya está superado («Lo revisa Jairo en T-001-93») | `src/egm/textos.py:340-341, 343-344`; `app/configuracion.py:24-26`; `tests/ayudas_web.py:4-13`; `tests/integracion/test_carga_web.py:627-628, 782-783`; `tests/integracion/test_sesion.py:17-20`; `tests/navegador/test_carga_navegador.py:16-17`; `tests/navegador/test_sesion_navegador.py:17-18`; `tests/unit/test_verificacion.py:37-41`; tabla en `plan.md:866-872` | A (m-6) + B (OBS-4) |
| NC-12 | Men. | Ningún módulo muestra en V2 el texto de pendientes («6 estudios empíricos aún no entran al mapa…») que pone `flujos.md`. La arquitectura y T-001-66 definen V2 sin ese texto. La parte del núcleo de FR-001-13 sí está ($P$; P-001-13, P-001-28), y el plan 003 lo muestra en el tablero (FR-003-21) | `flujos.md:108-110`; `arquitectura.md:756`; `plan.md:658-661`; `app/presentacion.py:171-180`; `003/plan.md:96` | A (m-7, C-5) + B (OBS-7, C-6, D-11) |
| NC-13 | Men. | Hay textos repetidos en el catálogo y en las plantillas. `cabecera.sesion` y `sesion.e9.recuperando` no los usa ningún módulo; las plantillas los escriben como literales. La arquitectura no aclara si los textos fijos de las plantillas son una excepción a P6 | `src/egm/textos.py:366-370`; `app/plantillas/cabecera.html:48`; `app/plantillas/base.html:46`; `arquitectura.md:25, 622` | B (OBS-3, C-4) |

### 3.2 Observaciones (sin no conformidad)

| ID | Observación | Evidencia | Origen |
|---|---|---|---|
| OBS-01 | El «<n> documentos» de la cabecera y del colofón se calcula en la capa web como `len(...)`, no como `Conteo`. Es trazable y coincide con M21. SC-000-02 en las vistas corresponde a los planes 002 y 003 | `app/presentacion.py:159, 168` | A (O-1) + B (OBS-2) |
| OBS-02 | `CODIGOS_ADVERTENCIA_VERIFICACION` se exporta y nadie lo usa. La prueba del catálogo solo recorre los códigos de M01, y otra prueba copia a mano los 5 de M08: ninguna falla si M08 agrega un código sin texto | `src/egm/verificacion.py:47, 96-102`; `tests/unit/test_textos.py:500-509`; `tests/unit/test_procesamiento.py:37-45` | B (OBS-1, D-13) |
| OBS-03 | `crear_app(config, reloj=None, ampliaciones=())` amplía la firma de la arquitectura, con parámetros opcionales. `ampliaciones` es el registro de rutas que prometía el hito N2 | `app/servidor.py:366-370`; `arquitectura.md:559`; `plan.md:783` | B (OBS-8) |
| OBS-04 | El texto aprobado `advertencia.hoja_abarca_menos_filas` contiene la palabra «fórmulas», aunque no trae ninguna fórmula | `catalogo-textos-m10-revision.md:58` | B (OBS-10) |
| OBS-05 | Avisos que no son fallos: `StarletteDeprecationWarning` (`httpx`), `RuntimeWarning` de `runpy` en P-001-84 y 186 `UserWarning` de `openpyxl` en `tests/unit/test_constructor.py` | `tests/ayudas_web.py:137` | A + B (OBS-11) |
| OBS-06 | P-001-84 y P-001-92 buscan archivos nuevos en la carpeta temporal del sistema. Si dos corridas coinciden en el tiempo, pueden dar un falso fallo; hoy coincidieron y pasaron | — | B (OBS-12) |
| OBS-07 | «Volver al mapa» lleva a la vista provisional `/vista/resultado` mientras no exista el plan 002 (NC-P001-1 decidido) | `textos.py:339`; `plan.md:820-826` | A (O-2) |
| OBS-08 | Los docstrings de `egm.verificacion` y un comentario Jinja que no se muestra mencionan internamente la tabla no comparable. No son interfaz ni texto para el equipo. M08 no la localiza (P-001-50) | `src/egm/verificacion.py:239-240`; `app/plantillas/avisos.html:1-8` | A (O-3) |

---

## 4. Decisiones abiertas para Jairo

Se presentan como propuestas, no como correcciones. Toda corrección sigue la regla 11: `analista-impacto`, luego su
aprobación y luego `corrector`.

- **NC-V-1. Alcance de la regla 9** (NC-01). Propuesta: aclarar que la regla prohíbe presentar un hallazgo como
  inconsistencia o corrección del equipo, no las condiciones de lectura que fija el spec (FR-001-10, FR-001-12,
  FR-001-16, FR-001-27). Esa lectura ya la sigue la columna «Tratamiento» del registro (`hallazgos-…:26, 29`).
- **NC-V-2. Numeración «Tablas 1, 2 y 4» y textos fijos de las plantillas** (NC-02, NC-13). a) Si se acepta que el
  número del título que exigen FR-001-25 y US-001-3.7 deje ver por omisión otra tabla. b) Si los textos fijos de las
  plantillas son una excepción a P6 o deben salir del catálogo único, y qué se hace con las dos claves sin uso.
- **NC-V-3. COR-018** (NC-04 y las deudas de la tabla siguiente). Propuesta: una sola COR-018 por `analista-impacto`
  que recoja C-2 (`read_only=True` frente a las dos cargas en modo normal) y D-1 a D-15, y que se audite en el mismo
  cierre de plan de corrección que COR-017. COR-017 está «aplicada» (`COR-017.md:3`) con su §9 vacía (`:356-358`).
  Trata del plan 002 y no toca código del plan 001. Sus búsquedas de §9 dan hoy lo esperado, pero eso es solo
  información y no un dictamen.

| N.º | Deuda (comprobada en el archivo) | Evidencia |
|---|---|---|
| D-1 | `columnas_del_bloque` es pública en M04, y la arquitectura no la incluye | `src/egm/esquema.py:52, 151` |
| D-2 | La arquitectura nombra `Conjuntos`, `Celda`, `ConteosHoja`, `VarianteHoja` y `Clave` sin definirlos | `src/egm/conteo.py:68, 82, 107, 125` |
| D-3 | `por_intervencion(solo_ie=True)` sin ancla lanza `ValueError`; `evaluacion_impacto` devuelve `None` en el mismo caso | `src/egm/conteo.py:244-245, 267-268` |
| D-4 | `por_nivel` no trae la entrada `SIN_NIVEL` | `src/egm/conteo.py:289` |
| D-5 | Hay dos tipos `Celda`, uno en `egm.libro` y otro en `egm.conteo` | `src/egm/libro.py:48`; `src/egm/conteo.py:82` |
| D-6 | `ResultadoLectura.verificacion` es un `Protocol` de M01 y la capa web lo convierte con `cast` | `src/egm/modelo.py:419, 427`; `app/presentacion.py:173` |
| D-7 | M03 abre el libro dos veces en modo normal (C-2) | `src/egm/libro.py:296-297` |
| D-8 | Las partes mínimas del libro están escritas en el código de M02 | `src/egm/archivo.py:31` |
| D-9 | La lista cerrada de 23 códigos de M01 no está fijada en la arquitectura | `src/egm/modelo.py:202-240` |
| D-10 | El bloque invertido (CB-38) da 9 advertencias | `tests/unit/test_esquema.py:699-708` |
| D-11 | El texto de pendientes de V2 no tiene dueño (NC-12) | `flujos.md:108-110` |
| D-12 | `LISTA_SIN_NO_APLICA` solo se evalúa en la principal y en el nivel, no en la secundaria | `src/egm/esquema.py:298-299, 313-317` |
| D-13 | Los 5 códigos de verificación viven en M08, fuera de la lista de M01 (OBS-02) | `src/egm/verificacion.py:96-102` |
| D-14 | La arquitectura no define `Diferencia`, `CausaDiferencia` ni `TextoVerificacion` | `src/egm/verificacion.py:138, 155`; `src/egm/textos.py:743` |
| D-15 | `DatosCrudos` no dice qué celda de intervención traía espacios | `src/egm/modelo.py:344-357`; `tests/unit/test_semantica_hoja_variantes.py:163-168` |

D-1, D-2, D-5, D-6, D-14 y D-15 están en `__all__`, así que forman parte de la interfaz que consumen 002 y 003. Por
eso no basta la holgura de `arquitectura.md:264-265`, que solo admite tipos auxiliares internos.

---

## 5. Tabla para actualizar `hallazgos-matriz-para-equipo.md` (NC-03)

La actualiza la sesión principal; el `verificador` no edita ese archivo. Estado propuesto: «Implementada en <módulo>;
verificada en `conformidad-plan-001-2026-11-26.md`», salvo A-03, que queda parcial.

| ID | Módulo | Prueba en verde | Comprobación sobre la v4 (en memoria, huella intacta) |
|---|---|---|---|
| A-01 | `egm.lectura` (enfoque), `egm.textos` | P-001-20, P-001-39 | Dos advertencias de enfoque: N.º 2 (fila 3) y N.º 7 (fila 8) |
| A-02 | `egm.lectura` (estados), `egm.conteo` ($P$) | P-001-13, P-001-28 | $P$ = N.º 10, 11, 13, 15, 16, 24 |
| A-03 | Parcial: lectura de vacíos en `egm.lectura` (plan 001); filtros y «sin diligenciar» visibles en los planes 002 y 003 | P-001-14 | — |
| A-04 | `egm.verificacion` | P-001-46 | Tablas 1, 2 y 4 «no verificable»; ninguna tabla verificada |
| B-01 | `egm.verificacion`, que no localiza esa tabla | P-001-50 | Solo se informan las tablas 1, 2 y 4 |
| B-02 | `egm.libro`, `egm.esquema` (listas desde las validaciones) | P-001-05, P-001-14; FR-001-22: P-001-36, 37, 40 | — |
| B-03 | `egm.conteo` (dimensiones solo en $E$) | P-001-11, P-001-25 | Ninguna advertencia de dimensión |

También se debe reemplazar la frase «Hoy no hay código (Fase 1, solo specs)» (`:19-20`).

---

## 6. Requisitos y paso a `verificado`

Los cambios de estado los hace la sesión principal.

- **Pueden pasar a `verificado`** (27; en `implementado` y sin hallazgo abierto): FR-001-01 a FR-001-09, FR-001-11,
  FR-001-13 a FR-001-15, FR-001-17 a FR-001-24, FR-001-26, FR-001-28; NFR-000-12, NFR-000-15, NFR-000-18 y
  NFR-000-19. FR-001-13 pasa en lo que pide (estados y lista de pendientes en el núcleo). Mostrar los pendientes en
  V2 es NC-12 y no cambia ese requisito.
- **Dependen de NC-V-1 y NC-V-2**: FR-001-10, FR-001-16, FR-001-25 y FR-001-27. Su implementación es conforme; lo
  pendiente es la tensión entre documentos.
- **Primero a `implementado` (NC-05)**: FR-001-12, que después pasa a `verificado` según NC-V-1, y NFR-000-11, que
  pasa según la revisión con logos de NC-P001-2 (`plan.md:827-832`).
- **Dependen de NC-06**: NFR-000-17.
- **Siguen en `planificado`**, con razón (tienen tareas en los planes 002 o 003): FR-001-29, NFR-000-01, 02, 03, 04,
  05, 06, 09, 13 y 14.

NC-04 (C-2) no afecta a ningún requisito: R-5 «no cambia ningún requisito» (`plan.md:839`).

---

## 7. Definición de terminado (`plan.md:853-864`)

Ninguna casilla está marcada (NC-08). Estado según la evidencia:

| Línea | Punto | Estado |
|---|---|---|
| 853 | Pruebas P-001-01 a 95 en verde; cobertura ≥ 90 % | Cumplido (sección 2) |
| 854 | Lint y tipado sin errores | Cumplido |
| 855 | Tarea y prueba por requisito en `trazabilidad.md` | Cumplido (44 de 44) |
| 856 | Cada número calculado es un `Conteo` | Cumplido en el núcleo (P-001-03, P-001-12, P-001-25); ver OBS-01 |
| 857 | `data/raw/` y `docs/fuentes/` sin cambios | Cumplido (huella y `git`) |
| 858 | Informe del `verificador` sin huecos ni excesos abiertos | Cumplido: 0 huecos y 0 excesos. Las NC de este informe no son huecos ni excesos |
| 859 | Hito N1: interfaz pública congelada y documentada | Cumplido en el código. El resumen de T-001-52 no se puede comprobar (NC-09) |
| 860 | Hito N2: `crear_app` lista para nuevas rutas | Cumplido (`ampliaciones`, `app/servidor.py:366-370`) |
| 861 | Un fixture por caso borde | Cumplido (P-001-01; CB-01 a CB-41) |
| 862 | NC-ARQ-1 resuelto y NC-P001-1 decidido | Cumplido (`plan.md:870-871`); la arquitectura no está al día (NC-10) |
| 863 | Sin cifras de la lámina 7; ningún texto nombra la tabla no comparable | Cumplido (búsquedas con 0 coincidencias; `tests/unit/test_constructor.py:2142`; P-001-50, P-001-64); ver NC-02 |
| 864 | Versión de Python del `.venv` en el resumen de fase | **No cumplido**: no hay resumen de la fase de código (NC-08) |

Resultado: 11 de 12 cumplidos, uno de ellos con una salvedad que no se puede comprobar (859), y uno sin cumplir (864).

---

## Conclusión

El plan 001 cumple lo que pide: 834 pruebas en verde, 99,72 % de cobertura, lint y tipado limpios, la matriz intacta
y ningún hueco ni exceso. Ninguna de las 13 no conformidades exige tocar el código. Para cerrarlo formalmente, la sesión
principal tiene que hacer cuatro cosas:

1. Pasar FR-001-12 y NFR-000-11 a `implementado` (NC-05).
2. Actualizar el registro de la regla 9 con la tabla de la sección 5 (NC-03).
3. Poner al día los estados del plan y escribir el resumen de la fase de código con la versión de Python (NC-08 y
   NC-09).
4. Pasar a `verificado` los 27 requisitos de la sección 6.

El resto, que incluye cuatro requisitos y el tratamiento de COR-018 junto con COR-017, espera las decisiones NC-V-1 a
NC-V-3 de Jairo.

---

**Lectura**: nada por el grafo (como `verificador`, la evidencia es el archivo; regla 12c). Se leyeron directamente los
informes A y B, `plan.md` (tramos 590-601 y 764-873), `trazabilidad.md`, `spec.md:410-429`, `contrato-datos.md:364-411`,
`hallazgos-matriz-para-equipo.md`, `COR-017.md`, `COR-016.md` (por búsqueda) y los tramos citados de `src/egm/`, `app/`,
`tests/`, `flujos.md` y la arquitectura. Se ejecutaron `ruff`, `mypy`, `sha256sum`, `git` y un recuento propio de
docstrings en el directorio temporal de la sesión. `pytest` no se volvió a correr (sección 2).
