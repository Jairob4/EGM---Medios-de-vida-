# Plan de implementación: 003-tablero-conclusiones

**Creado**: 2026-11-22 · **Estado**: borrador (pendiente de revisión de Jairo)
**Spec**: [`docs/specs/003-tablero-conclusiones/spec.md`](../../specs/003-tablero-conclusiones/spec.md)
**Arquitectura**: `docs/arquitectura/arquitectura.md` (aprobada el 22-nov-2026) §4, §5, §5.1, §6.1 (M06, M07, M09, M10,
M11), §6.2 (M14, M15, M17, M18, M22), §6.3 (M23), §6.4, §7 y §8 (V2, V7, V8, V9) · **ADR relacionados**: ADR-001
(número = lista, estudios distintos), ADR-002 (verificación; nada sobre tablas no comparables), ADR-003 (stack, pruebas,
recursos locales, sin estilos en línea), ADR-005 (colofón, solo consumido)
**Interfaz**: `docs/interfaz/flujos.md` §2 (E5, E6), §5 (F-003-1 a F-003-5), §9 (NC-INT-2, NC-INT-3);
boceto `docs/interfaz/bocetos/tablero.html`
**Ubicación de este plan**: `docs/planes/003-tablero-conclusiones/plan.md`

Documento interno, para Jairo y los subagentes. No es texto de interfaz ni lleva código.

## Resumen

El tablero (V8) muestra juntos las cifras clave, el mapa y las seis conclusiones, con su lista de N.º (V9) para cada
número, los mismos cuatro filtros del mapa con estado compartido y las aclaraciones que impiden leer más de lo que los
datos permiten (spec 003, FR-003-01 a FR-003-22).

Enfoque técnico (arquitectura §5 y §6): el núcleo calcula cifras y conclusiones como **datos** en `egm.conclusiones`
(M09), siempre como `Conteo` con su lista de `RefFila` (ADR-001, P2), recalculadas en cada petición desde el `Corpus`
con el `Filtro` aplicado de la sesión. `egm.textos` (M10) llena plantillas fijas con esos datos (P6, SC-003-06).
`app.presentacion` (M17) arma el modelo de vista del tablero y `app.plantillas` (M18) lo dibuja sin calcular nada.
`egm.porcentajes` (M11) se crea con el interruptor apagado y $n_{min} = 100$; ninguna vista lo usa (NFR-000-07).

**Prioridad por plazo (entrega del 6-dic-2026)**: primero las cifras clave (historia 1) y las conclusiones 1 a 3
(historia 2, parte A), luego las aclaraciones de confianza (historia 4), las conclusiones 4 a 6 (historia 2, parte B),
los filtros (historia 3) y el recorrido entre vistas (historia 5). Es un orden de ejecución, no un recorte de
alcance: todos los requisitos de la tabla siguiente se implementan. Si el plazo obliga a recortar, lo decide Jairo.

## Contexto técnico

**Lenguaje/versión**: Python 3.13 en `.venv` del proyecto (arquitectura §3, ADR-003).
**Dependencias principales**: `openpyxl` solo dentro de `egm.libro` (plan 001); FastAPI (Starlette) + Jinja2 + htmx +
Uvicorn, todo servido localmente (ADR-003). Este plan no agrega dependencias.
**Almacenamiento**: ninguno. Resultado de lectura y filtro aplicado en la memoria de la sesión (M15, P4). Las pruebas
leen `data/fixtures/`; una sola prueba de integración lee `data/raw/` en modo lectura (skill `calidad-python`).
**Pruebas**: `pytest`, `hypothesis` (propiedades), cliente de pruebas de la aplicación para rutas y sesiones,
navegador automatizado con revisión automática de accesibilidad (ADR-003, punto 8; las herramientas exactas las fija
el plan 001). Cobertura ≥ 90 % de líneas en `src/egm/`; `ruff` y `mypy --strict` sin errores.
**Plataforma objetivo**: navegador en el mismo equipo, servidor local en 127.0.0.1 (ADR-004, SC-000-15).
**Tipo de proyecto**: núcleo Python (`src/egm/`) + capa web (`app/`).
**Metas de desempeño**: el spec 003 no fija ninguna; se recalcula en cada petición (arquitectura §5). N/A.
**Restricciones**: conteos, no porcentajes (FR-003-17, NFR-000-07); cada número trazable a sus N.º (NFR-000-02);
brecha provisional, «ningún estudio registrado» y nunca «no investigado» (NFR-000-08); sin «brecha» con filtros
activos (FR-003-15); plantillas fijas (FR-003-12, SC-003-06); categorías leídas del archivo, nunca escritas en el código
(P3); ninguna cifra de la lámina 7 en esperados ni textos; ningún texto sobre tablas de la hoja EGM que no sean las
comparables (ADR-002, punto 6); `data/raw/` de solo lectura.
**Escala/alcance**: una matriz por sesión; la instancia de ejemplo tiene 27 documentos y $6 \times 8 = 48$ celdas
(contrato, apéndice A). Una vista (V8) con su lista (V9), más el bloque de filtros V7 y el de avisos V2 que vienen de
los planes 002 y 001.

### Definiciones operativas (del contrato §5 y §6; no agregan reglas)

Con $\varphi$ el filtro aplicado (conjunción de los cuatro controles, contrato §5) y $M_\varphi = \{r \in M : \varphi(r)\}$:

- Total de celdas: $|\mathcal{I}| \cdot |\mathcal{J}|$, con $\mathcal{I}$ y $\mathcal{J}$ leídos del archivo (FR-003-02).
- Celdas con estudios: $\{(i,j) : S_\varphi(i,j) > 0\}$; celdas sin estudios: el resto (FR-003-01).
- Conclusión 1: $\{(i,j) : S_\varphi(i,j) = 0\}$, revisados $M_\varphi$ (FR-003-05).
- Conclusión 2: $\{(i,j) : S_\varphi(i,j) > 0,\ S^{IE}_\varphi(i,j) = 0\}$, con el desglose por nivel de cada cruce;
  sin $v_{\text{IE}}$, «no disponible» (FR-003-06, FR-003-22).
- Conclusión 3: por intervención $i$ y categoría $\kappa$ de la sección 6 del contrato,
  $|\{r \in M_\varphi : i \in I_r,\ \gamma(r) = \kappa\}|$ (FR-003-07; base $M_\varphi$ y las cinco categorías de la sección 6, incluida «Sin diligenciar», NC-P003-1).
- Conclusión 4: pares de intervenciones $|\{r \in M_\varphi : i, i' \in I_r\}|$ y de dimensiones
  $|\{r \in M_\varphi : j, j' \in J_r\}|$, de `egm.conteo.coocurrencias` (FR-003-08; forma de NC-P003-3).
- Conclusión 5: documentos $\{r \in R : \text{cumple\_documento}(r, \varphi)\}$ por tipo de documento, tipo de fuente,
  metodología y año (FR-003-09, FR-003-14).
- Conclusión 6: por celda con $S_\varphi(i,j) > 0$, los textos tal cual de sus estudios (FR-003-10).
- «n de N»: $N$ es el total sin filtrar del mismo elemento y $n$ el total con $\varphi$ (contrato §5).

## Requisitos que cubre este plan

| Requisito | Resumen | Historia | Escenario / criterio que lo verifica | Módulo(s) de la arquitectura |
|---|---|---|---|---|
| FR-003-01 | Cifras clave | US-003-1 | US-003-1.1, US-003-1.2, SC-003-02 | M09, M10, M17, M18, M14 |
| FR-003-02 | Total de celdas desde las categorías del archivo | US-003-1 | US-003-1.3 | M09 |
| FR-003-03 | Mapa, cifras y conclusiones juntos | US-003-1, US-003-5 | US-003-1.4, US-003-5.3 | M17, M18 |
| FR-003-04 | Cada conclusión con su conteo y su lista de N.º y referencia | US-003-1, US-003-2 | US-003-1.2, US-003-2.8, SC-003-01, SC-003-05 | M09, M17, M18, M14 |
| FR-003-05 | Conclusión 1: cruces sin estudio, fecha, brecha provisional | US-003-2 | US-003-2.1 | M09, M10 |
| FR-003-06 | Conclusión 2: cruces sin evaluación de impacto, por nivel | US-003-2 | US-003-2.2, US-003-2.3 | M09, M07 |
| FR-003-07 | Conclusión 3: enfoque por intervención | US-003-2 | US-003-2.4 | M09 (consume M05) |
| FR-003-08 | Conclusión 4: qué aparece junto y qué nunca | US-003-2 | US-003-2.5, US-003-2.9 | M07, M09 |
| FR-003-09 | Conclusión 5: composición con «sin diligenciar» | US-003-2 | US-003-2.6 | M09 |
| FR-003-10 | Conclusión 6: textos tal cual por celda | US-003-2 | US-003-2.7 | M09 |
| FR-003-11 | Conclusión sin casos: lo dice y cuántos se revisaron | US-003-2 | US-003-2.3, caso borde «ningún estudio en el mapa» | M09, M10 |
| FR-003-12 | Lenguaje llano por plantillas | US-003-2 | SC-003-04, SC-003-06 | M10 |
| FR-003-13 | Mismos cuatro filtros, estado compartido | US-003-3, US-003-5 | US-003-3.1, US-003-5.1, US-003-5.2 | M17, M14 (consume M06, M15) |
| FR-003-14 | Recalcular, filtro visible, «n de N»; no empíricos como «Sin nivel» | US-003-3 | US-003-3.1, US-003-3.5, SC-003-03 | M06, M09, M17 |
| FR-003-15 | Con filtro, «ningún estudio registrado con los filtros activos», nunca «brecha» | US-003-3 | US-003-3.3 | M10, M17 |
| FR-003-16 | «Ningún estudio cumple estos filtros» | US-003-3 | US-003-3.2 | M09, M10 |
| FR-003-17 | Conteos, no porcentajes | US-003-4 | US-003-4.1, SC-003-04 | M11, M22, M09 |
| FR-003-18 | Estudios distintos; un estudio en varias celdas | US-003-4 | US-003-4.2 | M09, M10 |
| FR-003-19 | El mapa no dice qué ayuda funciona | US-003-4 | US-003-4.3 | M10, M17 |
| FR-003-20 | Resultado de la verificación en lenguaje llano | US-003-4 | US-003-4.4, US-003-4.5 | M17 (consume M08, M10 del plan 001) |
| FR-003-21 | Empíricos que aún no entran al mapa, con su lista (obligatorio) | US-003-1 | US-003-1.5 | M09, M10 |
| FR-003-22 | Sin ancla de evaluación de impacto, conclusión 2 «no disponible» | US-003-2 | US-003-2.10 | M09 (consume M04) |
| NFR-000-02 | Todo número se abre en su lista de N.º | todas | SC-000-02, SC-003-01 | M09, M17 |
| NFR-000-03 | Español, de usted, sin jerga ni fórmulas ni preguntas | todas | SC-000-03 | M10, M18 |
| NFR-000-04 | WCAG 2.2 AA | todas | SC-000-04 | M18 (consume M19) |
| NFR-000-05 | Desde 360 px sin desplazamiento horizontal de la página | todas | SC-000-05 | M18 |
| NFR-000-07 | Porcentajes inactivos, interruptor y $n_{min} = 100$ | US-003-4 | SC-000-07 | M11, M22 |
| NFR-000-08 | «Ningún estudio registrado»; brecha provisional | US-003-2, US-003-3 | SC-000-08 | M10 |
| NFR-000-13 | Diseño no genérico según la guía | todas | SC-000-13 | M18 |
| SC-003-01 a SC-003-06 | Criterios del spec 003 | — | ver tablas de pruebas | M09, M10, M17 |

Requisitos de otros specs que este plan **solo comprueba** desde el tablero, sin implementarlos: FR-002-12 (entrada
«Sin nivel» común), FR-002-15 (estado compartido), FR-002-18 y FR-002-19 (un solo «Actualizar vista» y un solo «Restablecer»), del plan 002, y NFR-000-01 y FR-001-29, del plan 001, en US-003-3.5, US-003-5.1 a 5.5 y las partes del tablero de US-002-4.6, US-002-4.14, US-001-4.6 y US-001-4.10.

Fuera de alcance de este plan: filtros por intervención, dimensión o enfoque (spec 002, decisión del 1-nov-2026);
porcentajes visibles (FR-003-17); exportación del tablero (FR-002-16 es solo del mapa); módulo no supervisado y vista de
red (regla 10 de `CLAUDE.md`): solo se citan sus puntos de extensión PE-1 a PE-7 (arquitectura §7), en particular PE-4,
que `coocurrencias` deja disponible sin que este plan construya ninguna red.

## Estructura del proyecto

### Documentación (esta feature)

```text
docs/specs/003-tablero-conclusiones/
└── spec.md              # Spec aprobado (fuente de este plan)

docs/planes/003-tablero-conclusiones/
└── plan.md              # Este archivo
```

### Código fuente (raíz del repositorio)

```text
src/egm/
├── conclusiones          # M09 (crea): cifras clave y seis conclusiones como datos
├── porcentajes           # M11 (crea): política inactiva
├── filtros               # M06 (amplía): cumple_documento
├── conteo                # M07 (amplía): coocurrencias
└── textos                # M10 (amplía): plantillas de conclusiones, rótulos de cifras, aclaraciones

app/
├── servidor              # M14 (amplía): rutas del tablero y de la lista de una cifra o conclusión
├── presentacion          # M17 (amplía): vista_tablero, vista_lista
├── plantillas/           # M18 (amplía): plantilla y fragmentos del tablero (disenador-front)
└── configuracion         # M22 (amplía): interruptor y n_min de porcentajes

tests/
├── constructor.py       # M23 tests.constructor (amplía): fixtures FX-003-nn
├── unit/                 # test_conclusiones_*.py, test_porcentajes.py, test_filtros_documentos.py, test_textos_conclusiones.py
├── integracion/          # test_tablero_*.py
└── propiedades/          # test_tablero_propiedades.py

data/fixtures/
└── 003-*.xlsx            # generados por M23, nunca a mano
```

**Decisión de estructura**: la forma de cada módulo (archivo `.py` o paquete) la fija el plan 001 al conciliar el
andamiaje de `src/egm/` (arquitectura §6); este plan usa el nombre del módulo y no crea ninguno fuera de la lista
cerrada de la arquitectura §6. El recálculo independiente que exige SC-003-03 vive dentro del archivo de prueba de
propiedades, no como módulo.

### Fixtures

Todos los fixtures nuevos los genera `tests/constructor.py` (M23 `tests.constructor`); los esperados se escriben a mano a partir del
spec y del contrato, nunca copiados de la salida del código.

| ID | Archivo | Qué contiene | Escenarios |
|---|---|---|---|
| FX-A | réplica sintética de la instancia de ejemplo (apéndice A); **la crea el plan 001**: `instancia_ejemplo.xlsx` | 27 documentos, $E$ = N.º 7, 10, 11, 13, 15, 16, 24; $M$ = N.º 7; 6 × 8 categorías; sin valores guardados en la hoja EGM; textos sintéticos del N.º 7 escritos a mano | US-003-1.1, 1.2, 1.5, 2.1, 2.3 a 2.7, 4.2 a 4.4; US-001-4.6 y US-001-4.10 (partes del tablero) |
| FX-RAW | `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx`, **solo lectura** | matriz vigente | SC-003-02 |
| FX-003-01 | `003-siete-por-nueve.xlsx` | 7 intervenciones y 9 dimensiones en las listas | US-003-1.3 |
| FX-003-02 | `003-celda-sin-ie.xlsx` | una celda con 3 estudios: 2 estudios de caso y 1 informe de proyecto | US-003-2.2 |
| FX-003-03 | `003-dimensiones-nunca-juntas.xlsx` | dos dimensiones marcadas en estudios distintos y nunca en el mismo | US-003-2.9 |
| FX-003-04 | `003-sin-ancla-ie.xlsx` | lista de nivel sin «Evaluación de impacto» | US-003-2.10 |
| FX-003-05 | `003-verificacion-difiere.xlsx` (o el fixture de «difiere» del plan 001, si ya lo trae) | hoja EGM con valores guardados que difieren en una tabla comparable, con explicación conocida | US-003-4.5 |
| FX-003-06 | `003-territorial-uno-de-cuatro.xlsx` | 4 estudios del mapa, 1 de fuente Territorial | US-003-3.1, 3.2, 3.3, 3.4, US-003-5.x; US-002-4.6 y US-001-4.10 (partes del tablero) |
| FX-003-07 | `003-sin-nivel-no-empiricos.xlsx` | 2 estudios del mapa (uno «Estudio de caso», otro sin nivel) y 2 documentos no empíricos | US-003-3.5 |
| FX-003-08 | `003-pendiente-sin-nivel.xlsx` | FX-003-07 más un estudio empírico pendiente sin nivel | NC-INT-2 (FR-003-14) |
| FX-003-09 | `003-sin-estudios-en-mapa.xlsx` | estudios empíricos, ninguno en $M$ | caso borde «ningún estudio en el mapa», FR-003-11 |
| FX-003-10 | `003-enfoque-mixto.xlsx` | estudios del mapa con enfoque «Sí…», «No…», «Parcial…», «Si bien…», «Nota:…» y vacío, en dos intervenciones | FR-003-07, contrato §6 |
| FX-003-11 | `003-composicion.xlsx` | documentos con cada campo de la conclusión 5 vacío en alguna fila, un año no entero y un tipo de documento fuera de lista | FR-003-09, casos borde de año |
| FX-003-12a / 12b | `003-plantillas-a.xlsx`, `003-plantillas-b.xlsx` | dos matrices con datos distintos que producen, para cada conclusión, el mismo caso | SC-003-06 |
| FX-003-13 | `003-textos-por-celda.xlsx` | una celda con 2 estudios con indicadores, vacío y limitaciones conocidos, uno de ellos con un campo vacío | FR-003-10 |
| EST-M23 | estrategias de `hypothesis` del plan 001, ampliadas | matrices al azar dentro del contrato | SC-003-01, SC-003-03 |
| FX-002-12 | `002_no_empiricos.xlsx` (del plan 002, se reutiliza) | 2 estudios del mapa de nivel «Estudio de caso» y 1 documento no empírico | US-002-4.14 (parte del tablero) |

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: dejar listos los archivos y fixtures que necesita la feature.

- [ ] T-003-01 Crear los archivos vacíos de M09 y M11 y los de prueba listados en «Estructura del proyecto», con la
  forma de módulo que fije el plan 001. Requisitos: —. Módulos: M09, M11. Archivos: `src/egm/conclusiones`,
  `src/egm/porcentajes`, `tests/unit/`, `tests/integracion/`, `tests/propiedades/`.
- [ ] T-003-02 [P] Ampliar el constructor con FX-003-01 a FX-003-13 y regenerarlos en `data/fixtures/`; reutilizar
  FX-A y, si existe, el fixture de «difiere» del plan 001. Requisitos: SC-003-02, SC-003-03, SC-003-06 (soporte).
  Módulos: M23. Archivos: `tests/constructor.py`, `data/fixtures/003-*.xlsx`.

**Punto de control**: las interfaces de los planes 001 y 002 listadas en «Dependencias» están disponibles; si falta
alguna, detenerse y avisar a Jairo.

---

## Fase 2: Base (prerrequisitos que bloquean)

**Propósito**: tipos de M09, política de porcentajes y su configuración.

**Crítico**: ninguna historia empieza antes de cerrar esta fase.

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-01 | unit | SC-000-07 (configuración por defecto) | — | `PoliticaPorcentajes()` tiene `activo = False` y `n_min = 100`; `permitido` es falso con cualquier denominador |
| P-003-02 | unit | SC-000-07 (umbral) | — | con `activo = True`: un denominador de 99 filas se rechaza y uno de 100 se acepta |
| P-003-03 | unit | NFR-000-07 | archivo de configuración de prueba | sin clave de porcentajes, `cargar_configuracion` deja apagado y 100; con valores escritos, los toma |
| P-003-04 | unit | NFR-000-02, FR-003-04 | — | `CifrasClave`, `Conclusion` e `ItemConclusion` son inmutables; todo número que exponen es un `Conteo` (o la longitud de una tupla de cruces, ver NC-P003-2); `caso` solo admite los cuatro valores de M09 |

- [ ] T-003-05 Escribir P-003-01 a P-003-04 en `tests/unit/test_porcentajes.py` y `tests/unit/test_conclusiones_tipos.py`;
  comprobar que fallan.
- [ ] T-003-06 [P] Implementar `PoliticaPorcentajes` y `permitido` en M11. Requisitos: NFR-000-07, FR-003-17.
  Pruebas: P-003-01, P-003-02. Módulos: M11. Archivos: `src/egm/porcentajes`.
- [ ] T-003-07 [P] Ampliar `cargar_configuracion` con el interruptor y $n_{min}$, apagado y 100 por defecto (depende de
  T-003-06). Requisitos: NFR-000-07. Pruebas: P-003-03. Módulos: M22. Archivos: `app/configuracion`.
- [ ] T-003-08 Definir en M09 los tipos públicos `CifrasClave` (cada cifra con $n$ y $N$), `Conclusion` e
  `ItemConclusion` (cruces, conteos por nivel, por enfoque, pares, composición, textos tal cual), sin lógica de cálculo.
  Requisitos: NFR-000-02, FR-003-04. Pruebas: P-003-04. Módulos: M09 (consume M01). Archivos: `src/egm/conclusiones`.

**Punto de control**: base lista; ya pueden empezar las historias.

---

## Fase 3: Historia 1 — Ver las cifras clave (prioridad: P1)

**Objetivo**: el tablero muestra las seis cifras clave y cada una abre su lista de N.º con referencia.

**Prueba independiente**: con FX-A, las cifras y sus listas coinciden con el apéndice A del contrato.

### Pruebas de la historia 1 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-10 | unit | US-003-1.1 | FX-A | 27 documentos, 7 estudios empíricos registrados, 1 estudio en el mapa, 6 celdas con estudios, 42 celdas sin ningún estudio registrado, total 48 |
| P-003-11 | unit | US-003-1.2 | FX-A | la lista de «estudios empíricos registrados» es N.º 7, 10, 11, 13, 15, 16 y 24, en el orden del archivo |
| P-003-12 | unit | US-003-1.3, FR-003-02 | FX-003-01 | total de celdas 63, sin ningún cambio de código |
| P-003-13 | unit | US-003-1.5, FR-003-21 | FX-A | «estudios empíricos que aún no entran al mapa» = 6, lista N.º 10, 11, 13, 15, 16 y 24 |
| P-003-14 | propiedades | SC-003-01, NFR-000-02 | EST-M23 | cada cifra vale la longitud de su lista; $\lvert M\rvert + \lvert P\rvert = \lvert E\rvert$; celdas con + celdas sin = total; listas sin repetidos y en el orden del archivo |
| P-003-15 | integración | SC-003-02 | FX-RAW (solo lectura) | las seis cifras coinciden con el apéndice A; el archivo no se abre en modo escritura |
| P-003-16 | integración (cliente de pruebas) | US-003-1.2, US-003-1.5, SC-000-02 | FX-A | la ruta del tablero muestra las seis cifras como botones; la ruta de la lista de una cifra devuelve sus N.º con su referencia y la frase de igualdad entre lista y cifra; ninguna URL lleva texto de la matriz |

- [ ] T-003-10 [P] [US-003-1] Escribir P-003-10 a P-003-13 en `tests/unit/test_conclusiones_cifras.py`.
- [ ] T-003-11 [P] [US-003-1] Escribir P-003-14 en `tests/propiedades/test_tablero_propiedades.py` y P-003-15 en
  `tests/integracion/test_tablero_matriz_vigente.py`.
- [ ] T-003-12 [P] [US-003-1] Escribir P-003-16 en `tests/integracion/test_tablero_rutas.py`.

### Implementación de la historia 1

- [ ] T-003-13 [US-003-1] Implementar `cifras_clave` sin filtro: documentos ($R$), $E$, $M$, $P$, celdas con y sin
  estudios y total desde `Esquema`, usando `egm.conteo.conjuntos` y `egm.conteo.mapa`. Requisitos: FR-003-01,
  FR-003-02, FR-003-21, NFR-000-02. Pruebas: P-003-10 a P-003-15. Módulos: M09 (consume M04, M05, M07).
  Archivos: `src/egm/conclusiones`.
- [ ] T-003-14 [US-003-1] Agregar al catálogo los rótulos de las seis cifras y la frase de igualdad entre lista y cifra.
  Requisitos: FR-003-01, FR-003-21, NFR-000-03. Pruebas: P-003-16. Módulos: M10. Archivos: `src/egm/textos`.
- [ ] T-003-15 [US-003-1] Implementar `vista_tablero` (cabecera, avisos V2 y colofón del plan 001, sección de cifras) y
  `vista_lista(sesion, cifra)` con N.º y referencia; agregar las rutas del tablero y de la lista, por posición.
  Requisitos: FR-003-01, FR-003-04, NFR-000-02. Pruebas: P-003-16. Módulos: M17, M14 (consume M15).
  Archivos: `app/presentacion`, `app/servidor`.
- [ ] T-003-16 [US-003-1] **(disenador-front)** Plantilla del tablero y sección «Cifras clave» con su margen V9, según
  `tablero.html` y la skill `sistema-diseno-egm`; el `implementador` la conecta. Requisitos: FR-003-01, FR-003-03,
  NFR-000-04, NFR-000-13. Pruebas: P-003-16. Módulos: M18. Archivos: `app/plantillas/`.

**Punto de control**: la historia 1 funciona sola. El implementador se detiene y resume; Jairo hace el commit.

---

## Fase 4: Historia 2, parte A — Conclusiones 1 a 3 (prioridad: P1)

**Objetivo**: las conclusiones 1 a 3 se leen en lenguaje llano, cada una con su conteo y su lista.

**Prueba independiente**: conclusión por conclusión, con FX-A y matrices sintéticas de resultado conocido.

### Pruebas de la historia 2, parte A (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-20 | unit | US-003-2.1, FR-003-05 | FX-A | conclusión 1 «con casos»: 42 de 48 cruces, los 42 en el orden del archivo, revisados = N.º 7; el texto lleva la fecha de lectura inyectada y la aclaración de brecha provisional |
| P-003-21 | unit | US-003-2.2, FR-003-06 | FX-003-02 | la celda: 3 estudios, 0 de evaluación de impacto, 2 estudios de caso, 1 informe de proyecto, con sus N.º |
| P-003-22 | unit | US-003-2.3, FR-003-11 | FX-A | conclusión 2 «sin casos», revisados = 1 (N.º 7) |
| P-003-23 | unit | US-003-2.10, FR-003-22 | FX-003-04 | conclusión 2 «no disponible»; se devuelven las seis conclusiones y las otras cinco no están «no disponible» |
| P-003-24 | unit | US-003-2.4, FR-003-07 | FX-A | Acompañamiento técnico: de 1 estudio, 0 lo incorporan, 0 parcial, 0 no, 1 sin clasificar (N.º 7) y 0 sin diligenciar |
| P-003-25 | unit | FR-003-07, contrato §6 | FX-003-10 | cada estudio en una sola categoría; «Si bien…» y «Nota:…» quedan «sin clasificar»; la suma por categorías es el número de estudios de la intervención |
| P-003-26 | unit | FR-003-11, caso borde «ningún estudio en el mapa» | FX-003-09 | cifras del mapa en 0; conclusiones 1 a 3 presentes, con caso «sin casos» y revisados = 0 |
| P-003-27 | unit | SC-003-06 (conclusiones 1 a 3) | FX-003-12a, FX-003-12b | para el mismo caso, el texto de cada conclusión es idéntico al reemplazar los datos calculados por marcas |
| P-003-28 | integración (cliente de pruebas) | US-003-2.8, SC-003-01 (1 a 3) | FX-A | la sección «Lo que dicen los datos» muestra las conclusiones 1 a 3 con su nota al margen; la lista de cada una tiene tantos N.º como su conteo |

- [ ] T-003-20 [P] [US-003-2] Escribir P-003-20 a P-003-26 en `tests/unit/test_conclusiones_1_3.py`.
- [ ] T-003-21 [P] [US-003-2] Escribir P-003-27 en `tests/unit/test_textos_conclusiones.py` y P-003-28 en
  `tests/integracion/test_tablero_rutas.py`.

### Implementación de la historia 2, parte A

- [ ] T-003-22 [US-003-2] Implementar la conclusión 1 como datos (cruces en 0, revisados, casos «con casos» y «sin
  casos»). Requisitos: FR-003-05, FR-003-04, FR-003-11. Pruebas: P-003-20, P-003-26. Módulos: M09 (consume M07).
  Archivos: `src/egm/conclusiones`.
- [ ] T-003-23 [US-003-2] Implementar la conclusión 2 con `egm.conteo.evaluacion_impacto` y el desglose por nivel de las
  celdas; «no disponible» cuando no hay $v_{\text{IE}}$. Requisitos: FR-003-06, FR-003-11, FR-003-22. Pruebas: P-003-21
  a P-003-23. Módulos: M09 (consume M04, M07). Archivos: `src/egm/conclusiones`.
- [ ] T-003-24 [US-003-2] Implementar la conclusión 3 por intervención, sobre los estudios del mapa, con las cinco categorías de `Enfoque`, incluida «sin diligenciar», en los
  datos y en la vista, para que la suma dé el número de estudios (NC-P003-1). Requisitos: FR-003-07,
  FR-003-11. Pruebas: P-003-24, P-003-25, P-003-26. Módulos: M09 (consume M05). Archivos: `src/egm/conclusiones`.
- [ ] T-003-25 [US-003-2] Escribir en el catálogo las plantillas de las conclusiones 1 a 3 para cada caso, la
  aclaración de brecha provisional y la de «sin clasificar», con la fecha en español de M10. Requisitos: FR-003-05,
  FR-003-11, FR-003-12, NFR-000-03, NFR-000-08. Pruebas: P-003-20, P-003-27. Módulos: M10. Archivos: `src/egm/textos`.
- [ ] T-003-26 [US-003-2] Agregar las conclusiones 1 a 3 al modelo de vista del tablero y su lista a `vista_lista`.
  Requisitos: FR-003-04. Pruebas: P-003-28. Módulos: M17, M14. Archivos: `app/presentacion`, `app/servidor`.
- [ ] T-003-27 [US-003-2] **(disenador-front)** Sección «Lo que dicen los datos» con las conclusiones 1 a 3, el
  desplegable de cruces, la tabla de enfoque con sus cinco categorías y las notas al margen. Requisitos: FR-003-04, NFR-000-04, NFR-000-13.
  Pruebas: P-003-28. Módulos: M18. Archivos: `app/plantillas/`.

**Punto de control**: conclusiones 1 a 3 en verde. El implementador se detiene y resume.

---

## Fase 5: Historia 4 — Confiar en lo que se lee (prioridad: P1)

**Objetivo**: el tablero no deja sacar de una frase más de lo que los datos permiten.

**Prueba independiente**: revisión de los textos del tablero con FX-A y con FX-003-05.

### Pruebas de la historia 4 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-30 | integración | US-003-4.1, FR-003-17 | FX-A, FX-003-06 con filtro | el HTML del tablero, con la configuración por defecto, no contiene «%» ni «por ciento» |
| P-003-31 | unit | US-003-4.2, FR-003-18 | FX-A | la aclaración dice que las 6 celdas con estudios provienen de 1 estudio (N.º 7) |
| P-003-32 | unit | US-003-4.3, FR-003-19 | FX-A | la aclaración de que el mapa indica dónde hay evidencia y no qué ayuda funciona está presente |
| P-003-33 | integración | US-003-4.4, FR-003-20 | FX-A | el tablero muestra en lenguaje llano que los conteos no se pudieron contrastar con la hoja EGM |
| P-003-34 | integración | US-003-4.5, FR-003-20 | FX-003-05 | el tablero nombra las tablas verificadas que difieren, por su número, con su explicación; no aparece ningún número de tabla distinto de los de las tablas comparables |
| P-003-35 | unit | SC-003-04, NFR-000-03, NFR-000-08, SC-000-08 | — (catálogo M10) | ninguna plantilla del tablero contiene «%», «no investigado», fórmulas ni signos de pregunta; las variantes con filtro no contienen «brecha» |
| P-003-36 | integración | SC-000-07 | FX-A, configuración con el interruptor encendido y $n_{min} = 1$ | el tablero sigue sin porcentajes, porque ninguna vista los pide |

- [ ] T-003-30 [P] [US-003-4] Escribir P-003-31, P-003-32 y P-003-35 en `tests/unit/test_textos_conclusiones.py`.
- [ ] T-003-31 [P] [US-003-4] Escribir P-003-30, P-003-33, P-003-34 y P-003-36 en `tests/integracion/test_tablero_confianza.py`.

### Implementación de la historia 4

- [ ] T-003-32 [US-003-4] Escribir en el catálogo las aclaraciones de estudios distintos (con sus datos) y de lo que el
  mapa no dice. Requisitos: FR-003-18, FR-003-19, NFR-000-03. Pruebas: P-003-31, P-003-32, P-003-35. Módulos: M10.
  Archivos: `src/egm/textos`.
- [ ] T-003-33 [US-003-4] Agregar a `CifrasClave` el `Conteo` de estudios distintos que ocupan las celdas con estudios.
  Requisitos: FR-003-18, NFR-000-02. Pruebas: P-003-31. Módulos: M09 (consume M07). Archivos: `src/egm/conclusiones`.
- [ ] T-003-34 [US-003-4] Agregar al modelo de vista del tablero el resultado de la verificación (texto de
  `egm.textos.verificacion`, plan 001) y las aclaraciones. Requisitos: FR-003-19, FR-003-20. Pruebas: P-003-33,
  P-003-34. Módulos: M17 (consume M08, M10). Archivos: `app/presentacion`.
- [ ] T-003-35 [US-003-4] **(disenador-front)** Aclaraciones bajo las cifras clave y bloque «Antes de leer los
  resultados» en el tablero. Requisitos: FR-003-19, FR-003-20, NFR-000-04. Pruebas: P-003-33. Módulos: M18.
  Archivos: `app/plantillas/`.
- [ ] T-003-36 [US-003-4] Pasar la política de M22 a la capa web sin que ninguna vista pida porcentajes, y dejar
  P-003-36 en verde. Requisitos: FR-003-17, NFR-000-07. Pruebas: P-003-30, P-003-36. Módulos: M22, M17.
  Archivos: `app/configuracion`, `app/presentacion`.

**Punto de control**: historias 1, 2 (parte A) y 4 en verde: cifras clave, conclusiones 1 a 3 y confianza. El
implementador se detiene y resume.

---

## Fase 6: Historia 2, parte B — Conclusiones 4 a 6 (prioridad: P1)

**Objetivo**: las conclusiones 4 a 6 se leen con su conteo y su lista, y las seis aparecen junto a las cifras.

**Prueba independiente**: conclusión por conclusión, con FX-A y matrices sintéticas.

### Pruebas de la historia 2, parte B (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-40 | unit | US-003-2.5, FR-003-08 | FX-A | 1 estudio (N.º 7) analiza Acompañamiento técnico junto con Transferencia de activos; Vulnerabilidad, Humano y Financiero se miden juntas en 1 estudio |
| P-003-41 | unit | US-003-2.9, FR-003-08 | FX-003-03 | las dos dimensiones aparecen como «nunca se miden juntas», con la aclaración de que se refiere a los estudios registrados |
| P-003-42 | propiedades | FR-003-08, PE-4 | EST-M23 | cada par es simétrico; su lista está contenida en la de cada miembro; ningún par de un elemento consigo mismo |
| P-003-43 | unit | US-003-2.6, FR-003-09 | FX-A | 27 documentos; 0 de fuente territorial; 20 sin tipo de fuente diligenciado; año más reciente 2026; reparto por tipo de documento y metodología del apéndice A |
| P-003-44 | unit | FR-003-09, casos borde de año | FX-003-11 | «sin diligenciar» visible en cada reparto; «año no reconocido» separado de «sin diligenciar»; «Sin tipo de documento válido» con su conteo |
| P-003-45 | integración | US-003-2.7, FR-003-10 | FX-A | para Acompañamiento técnico × Humano, los textos de indicadores, vacío y limitaciones del N.º 7 son, tal cual, los escritos a mano en el docstring de FX-A |
| P-003-46 | unit | FR-003-10 | FX-003-13 | los textos de cada estudio de la celda salen tal cual y en el orden del archivo; el campo vacío se trata según NC-P003-4 |
| P-003-47 | propiedades | SC-003-01, US-003-2.8 | EST-M23 | se devuelven seis conclusiones en orden; en cada una, el conteo mostrado es la longitud de su lista |
| P-003-48 | unit | SC-003-06 (conclusiones 4 a 6) | FX-003-12a, FX-003-12b | mismo texto para el mismo caso, solo cambian los datos |
| P-003-49 | integración (cliente de pruebas) | US-003-1.4, FR-003-03 (parte), US-003-2.8 | FX-A | el tablero muestra juntas las cifras clave y las seis conclusiones; la lista de cada conclusión 4 a 6 coincide con su conteo |

- [ ] T-003-40 [P] [US-003-2] Escribir P-003-40, P-003-41, P-003-43, P-003-44 y P-003-46 en `tests/unit/test_conclusiones_4_6.py`.
- [ ] T-003-41 [P] [US-003-2] Escribir P-003-42 y P-003-47 en `tests/propiedades/test_tablero_propiedades.py`.
- [ ] T-003-42 [P] [US-003-2] Escribir P-003-45 en `tests/integracion/test_tablero_rutas.py`, P-003-48 en
  `tests/unit/test_textos_conclusiones.py` y P-003-49 en `tests/integracion/test_tablero_rutas.py`.

### Implementación de la historia 2, parte B

- [ ] T-003-43 [US-003-2] Implementar `coocurrencias(esquema, corpus, filtro)`: pares de intervenciones y de dimensiones
  con su `Conteo`, en el orden del archivo (PE-4, sin ninguna vista de red). Requisitos: FR-003-08, NFR-000-02.
  Pruebas: P-003-42. Módulos: M07. Archivos: `src/egm/conteo`.
- [ ] T-003-44 [US-003-2] Implementar la conclusión 4 sobre `coocurrencias`, según la forma que fije NC-P003-3.
  Requisitos: FR-003-08, FR-003-11. Pruebas: P-003-40, P-003-41. Módulos: M09 (consume M07). Archivos: `src/egm/conclusiones`.
- [ ] T-003-45 [P] [US-003-2] Implementar la conclusión 5 sobre documentos: repartos por tipo de documento, tipo de
  fuente, metodología y año, con «sin diligenciar», «año no reconocido» y «Sin tipo de documento válido»; rango de
  años. Requisitos: FR-003-09. Pruebas: P-003-43, P-003-44. Módulos: M09 (consume M04, M05). Archivos: `src/egm/conclusiones`.
- [ ] T-003-46 [P] [US-003-2] Implementar la conclusión 6: por celda con estudios, los textos tal cual de
  `Documento.textos`. Requisitos: FR-003-10. Pruebas: P-003-45, P-003-46. Módulos: M09 (consume M05).
  Archivos: `src/egm/conclusiones`.
- [ ] T-003-47 [US-003-2] Escribir las plantillas de las conclusiones 4 a 6 para cada caso. Requisitos: FR-003-11,
  FR-003-12, NFR-000-03. Pruebas: P-003-41, P-003-48. Módulos: M10. Archivos: `src/egm/textos`.
- [ ] T-003-48 [US-003-2] Agregar las conclusiones 4 a 6 al modelo de vista y a `vista_lista`. Requisitos: FR-003-04,
  FR-003-03. Pruebas: P-003-49. Módulos: M17, M14. Archivos: `app/presentacion`, `app/servidor`.
- [ ] T-003-49 [US-003-2] **(disenador-front)** Conclusiones 4 a 6: frases de coocurrencia, tablas de composición y
  desplegables de textos por celda. Requisitos: FR-003-03, FR-003-04, NFR-000-04, NFR-000-13. Pruebas: P-003-49.
  Módulos: M18. Archivos: `app/plantillas/`.

**Punto de control**: las seis conclusiones en verde. El implementador se detiene y resume.

---

## Fase 7: Historia 3 — Filtrar el tablero (prioridad: P2)

**Objetivo**: el tablero aplica los mismos filtros del mapa y lo recalcula todo con «n de N».

**Prueba independiente**: con FX-003-06 y FX-003-07, comparando con y sin filtros.

### Pruebas de la historia 3 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-50 | unit | US-003-3.5, FR-003-14 | FX-003-07 | con «Estudio de caso» oculto, documentos «3 de 4»; con «Sin nivel» oculto y «Estudio de caso» visible, «1 de 4» |
| P-003-51 | unit | FR-003-14 (NC-INT-2) | FX-003-08 | sin filtro, el empírico pendiente sin nivel cuenta en documentos; con el filtro de nivel activo, queda fuera aunque «Sin nivel» esté visible |
| P-003-52 | unit | US-003-3.1, FR-003-14 | FX-003-06 | con solo Territorial: estudios del mapa «1 de 4», cada cifra con su $n$ y su $N$ del mismo tipo, listas recalculadas |
| P-003-53 | unit | US-003-3.2, FR-003-16 | FX-003-06, filtro que no deja estudios | cada conclusión de estudios queda «sin_estudios_filtro» y su texto es «Ningún estudio cumple estos filtros.» |
| P-003-54 | unit | US-003-3.3, FR-003-15 | FX-003-06 con filtro | la conclusión 1 rotula los cruces en 0 «ningún estudio registrado con los filtros activos» y no usa «brecha» |
| P-003-55 | propiedades | SC-003-03 | EST-M23 | en todas las combinaciones de los cuatro filtros, cifras y conclusiones coinciden con un recálculo independiente escrito en la prueba a partir del contrato §5 |
| P-003-56 | integración (cliente de pruebas) | US-003-3.4 | FX-003-06 | tras abrir la lista de una conclusión y volver, el mismo filtro sigue activo |
| P-003-57 | integración (cliente de pruebas) | US-003-3.1, FR-003-13 | FX-003-06 | tras «Actualizar vista» en el tablero, el resumen del filtro queda visible y se muestra «1 de 4» |
| P-003-58 | integración (cliente de pruebas) | US-002-4.14 (parte del tablero), FR-002-12, FR-003-14 | FX-002-12 | antes de ocultarla, la leyenda del tablero muestra «Sin nivel» con 0 estudios en el mapa; tras ocultar «Sin nivel» y pulsar «Actualizar vista» desde el tablero, el mapa del tablero sigue contando los 2 estudios y la cifra de documentos muestra «2 de 3» |

- [ ] T-003-50 [P] [US-003-3] Escribir P-003-50 y P-003-51 en `tests/unit/test_filtros_documentos.py`, y P-003-52 a
  P-003-54 en `tests/unit/test_conclusiones_filtro.py`.
- [ ] T-003-51 [P] [US-003-3] Escribir P-003-55 en `tests/propiedades/test_tablero_propiedades.py`.
- [ ] T-003-52 [P] [US-003-3] Escribir P-003-56 a P-003-58 en `tests/integracion/test_tablero_filtros.py`.

### Implementación de la historia 3

- [ ] T-003-53 [US-003-3] Implementar `cumple_documento`: un documento no empírico cumple el filtro de nivel como «Sin
  nivel»; un empírico pendiente sin nivel no (NC-INT-2); los demás controles como `cumple_estudio`. Requisitos:
  FR-003-14. Pruebas: P-003-50, P-003-51. Módulos: M06. Archivos: `src/egm/filtros`.
- [ ] T-003-54 [US-003-3] Aplicar el filtro en `cifras_clave` y `conclusiones`: $n$ y $N$ por tipo de elemento y caso
  «sin_estudios_filtro». Requisitos: FR-003-13, FR-003-14, FR-003-16. Pruebas: P-003-52, P-003-53, P-003-55.
  Módulos: M09 (consume M06, M07). Archivos: `src/egm/conclusiones`.
- [ ] T-003-55 [US-003-3] Escribir en el catálogo las variantes con filtro de cada plantilla (rótulo con filtros activos,
  «Ningún estudio cumple estos filtros.», «n de N»), sin «brecha». Requisitos: FR-003-15, FR-003-16, NFR-000-08.
  Pruebas: P-003-53, P-003-54, P-003-35. Módulos: M10. Archivos: `src/egm/textos`.
- [ ] T-003-56 [US-003-3] Agregar al tablero el bloque de filtros V7 del plan 002 con lo aplicado, el resumen y «n de N»,
  y hacer que «Actualizar vista» y «Restablecer» enviados desde el tablero devuelvan el tablero. Requisitos: FR-003-13,
  FR-003-14, FR-002-12 (parte del tablero de US-002-4.14). Pruebas: P-003-56 a P-003-58. Módulos: M17, M14 (consume M06, M15). Archivos: `app/presentacion`, `app/servidor`.
- [ ] T-003-57 [US-003-3] **(disenador-front)** Bloque de filtros en el tablero y estado «Tablero con un filtro activo»
  del boceto. Requisitos: FR-003-13, FR-003-15, NFR-000-04. Pruebas: P-003-57. Módulos: M18. Archivos: `app/plantillas/`.

**Punto de control**: el tablero filtra solo. El implementador se detiene y resume.

---

## Fase 8: Historia 5 — Recorrer el mapa y el tablero (prioridad: P3)

**Objetivo**: pasar del mapa al tablero sin perder el filtro aplicado; el tablero contiene el mapa.

**Prueba independiente**: con ambas vistas construidas (depende del plan 002), activando filtros en una y revisando la otra.

### Pruebas de la historia 5 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-60 | integración (cliente de pruebas) | US-003-5.1 | FX-003-06 | filtro aplicado en el mapa ⇒ el tablero lo muestra activo |
| P-003-61 | integración (cliente de pruebas) | US-003-5.2 | FX-003-06 | filtro aplicado en el tablero ⇒ el mapa lo muestra activo |
| P-003-62 | integración (cliente de pruebas) | US-003-5.3, FR-003-03 | FX-A | el tablero contiene las cifras clave, la cajonera y las conclusiones |
| P-003-63 | integración (cliente de pruebas) | US-003-5.4 | FX-003-06 | una selección sin aplicar no cambia nada: mapa y tablero muestran lo último aplicado |
| P-003-64 | integración (cliente de pruebas) | US-003-5.5, FR-002-19 | FX-003-06 | «Restablecer» o «Actualizar vista» desde el tablero dejan mapa y tablero con el mismo estado |
| P-003-65 | integración (cliente de pruebas) | US-002-4.6 (parte del tablero), FR-002-18, FR-002-19 | FX-003-06 | con un filtro activo, «Restablecer» enviado desde el tablero devuelve de inmediato el tablero sin filtrar (4 estudios del mapa, sin «n de N»), sin pasar por «Actualizar vista»; ningún filtro queda activo y el mapa muestra lo mismo |
| P-003-66 | integración (cliente de pruebas) | US-001-4.10 (parte del tablero), FR-001-29 | FX-003-06, luego FX-A | con un filtro aplicado, una carga nueva válida deja el tablero del archivo nuevo sin filtros, sin «n de N» y sin ningún filtro activo |
| P-003-67 | integración (cliente de pruebas) | US-001-4.6 (completo), NFR-000-01, SC-000-01 | FX-A, con su huella SHA-256 tomada antes | tras cargarlo y pedir todas las vistas (resultado, mapa, cajón, ficha, definición, descargas SVG y `.xlsx`, tablero y la lista de cada cifra y de cada conclusión), la huella del archivo no cambia |

- [ ] T-003-60 [US-003-5] Escribir P-003-60 a P-003-67 en `tests/integracion/test_tablero_recorrido.py`.

### Implementación de la historia 5

- [ ] T-003-61 [US-003-5] Incluir en el modelo del tablero la cajonera de `vista_mapa` (plan 002), sin recalcularla, y la
  navegación «Mapa | Tablero». Requisitos: FR-003-03, FR-003-13. Pruebas: P-003-60 a P-003-62. Módulos: M17.
  Archivos: `app/presentacion`.
- [ ] T-003-62 [US-003-5] **(disenador-front)** Cajonera dentro del tablero con su foco itinerante (M19 del plan 002, sin
  cambios) y navegación con la vista actual marcada. Requisitos: FR-003-03, NFR-000-04. Pruebas: P-003-62.
  Módulos: M18. Archivos: `app/plantillas/`.
- [ ] T-003-63 [US-003-5] Comprobar en las rutas comunes que el estado aplicado es uno solo por sesión, cualquiera que sea
  la vista de origen. Requisitos: FR-003-13, FR-002-18, FR-002-19, FR-001-29 (parte del tablero de US-001-4.10), NFR-000-01 (US-001-4.6 completo). Pruebas: P-003-63 a P-003-67. Módulos: M14 (consume M15).
  Archivos: `app/servidor`.

**Punto de control**: todas las historias funcionan de forma independiente. El implementador se detiene y resume.

---

## Fase 9: Cierre y aspectos transversales

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-003-90 | navegador | NFR-000-04, NFR-000-05, SC-000-04, SC-000-05 | FX-A, FX-003-06 con filtro | la revisión automática de accesibilidad del tablero no deja hallazgos AA a 360 px y 1440 px, en claro y oscuro; a 360 px la página no se desplaza en horizontal; las cifras y conclusiones se recorren solo con teclado |

- [ ] T-003-90 Escribir y pasar P-003-90 en `tests/navegador/test_tablero_accesibilidad.py` (marca `navegador`). Requisitos: NFR-000-04, NFR-000-05.
  Módulos: M18.
- [ ] T-003-91 [P] **(disenador-front)** Revisión con capturas del tablero en 360 px y 1440 px, claro y oscuro; Jairo
  aprueba la vista (SC-000-13). Requisitos: NFR-000-13, NFR-000-04, NFR-000-05. Módulos: M18.
- [ ] T-003-92 [P] Revisión manual de los textos del catálogo y de la vista contra SC-003-04 y SC-000-03 (sin tuteo,
  fórmulas ni preguntas, sin «brecha» con filtros, sin afirmaciones sobre si una ayuda funciona). Requisitos: FR-003-12,
  NFR-000-03. Módulos: M10.
- [ ] T-003-93 Preparar la comprobación de SC-003-05 (una persona del equipo verifica una conclusión con la matriz
  abierta usando solo los N.º del tablero), según NC-P003-5. Requisitos: FR-003-04. Módulos: M17.
- [ ] T-003-94 Limpieza sin cambiar comportamiento; cobertura ≥ 90 % en `src/egm/`, `ruff` y `mypy --strict` sin
  errores; la prueba de importaciones del plan 001 incluye M09 y M11 (NFR-000-14). Requisitos: —. Módulos: M09, M11.
- [ ] T-003-95 Actualizar la columna «Prueba» y el estado `implementado` (regla de estados de `trazabilidad.md`) de `docs/specs/trazabilidad.md` para cada requisito de este
  plan. La columna «Tarea» ya está llena desde la Fase 3. Requisitos: todos los del plan.
- [ ] T-003-96 Solicitar la verificación al subagente `verificador`.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)** y **base (fase 2)**: dependen de que los planes 001 y 002 hayan entregado las interfaces de
  abajo; la fase 2 bloquea todas las historias.
- **Historias**: en el orden del plazo: historia 1 → historia 2 parte A → historia 4 → historia 2 parte B → historia 3
  → historia 5, una a la vez.
- **Cierre**: después de las historias que Jairo decida entregar.

### Dependencias entre historias

- **Historia 1**: tras la fase 2; sin dependencias de otras historias.
- **Historia 2 (A y B)**: tras la fase 2; se integra en la vista de la historia 1, pero sus pruebas del núcleo no la
  necesitan. La parte B (T-003-44) espera NC-P003-3.
- **Historia 4**: tras la fase 2; usa la vista de la historia 1 para las pruebas de integración.
- **Historia 3**: tras la fase 2; necesita las funciones de las historias 1 y 2 para recalcular con filtro.
- **Historia 5**: necesita el mapa del plan 002 terminado.

### Dependencias con otros módulos o specs

Se consumen por su interfaz pública de la arquitectura §6; este plan no las replanifica.

- Plan 001 → M01 `RefFila`, `Conteo`, `EstadoDocumento`, `Enfoque`, `SIN_NIVEL`, `Identificacion`, `ResultadoLectura` ·
  pendiente.
- Plan 001 → M04 `Esquema` (intervenciones, dimensiones, niveles, listas, `anclas.v_IE`) · pendiente.
- Plan 001 → M05 `Corpus`, `Documento` (estado, nivel, enfoque, año, `textos`) · pendiente.
- Plan 001 → M07 `conjuntos`, `mapa` sin filtro, `evaluacion_impacto` · pendiente.
- Plan 001 → M08 `Verificacion` y M10 `verificacion(v)`, `fecha(d)`, `ROTULOS` · pendiente.
- Plan 001 → M13 `procesar`; M14 `crear_app`; M15 `AlmacenSesiones`; M17 cabecera, avisos V2 y colofón; M18 plantilla
  base; M22 `cargar_configuracion` · pendiente.
- Plan 001 → M23 `MatrizSintetica`, `.a_bytes()`, estrategias de propiedades, FX-A y, si existe, el fixture de
  «difiere»; herramientas de navegador automatizado y de revisión de accesibilidad (ADR-003, punto 8) · pendiente.
- Plan 002 → M06 `Filtro`, `SIN_FILTRO`, `opciones` (con la entrada «Sin nivel» también por documentos no empíricos,
  FR-002-12), `normalizar`, `cumple_estudio`, `activos` · pendiente. Este plan agrega solo `cumple_documento`.
- Plan 002 → M07 `mapa` y `evaluacion_impacto` con filtro, y desglose por nivel de cada celda · pendiente.
- Plan 002 → M10 rótulos del mapa («ningún estudio registrado», «… con los filtros activos», «Sin nivel») · pendiente.
- Plan 002 → M15 `aplicar_filtro`; M14 rutas «Actualizar vista» y «Restablecer»; M17 `vista_mapa` y modelo de filtros
  (resumen, «n de N»); M18 fragmentos de cajonera y filtros; M19 teclado de la cajonera · pendiente.

### Dentro de cada historia

- Pruebas primero: se escriben y se comprueba que fallan.
- Modelo antes que análisis; núcleo (M07, M09, M10) antes que capa web (M17, M14, M18).
- Historia en verde antes de pasar a la siguiente.

## Riesgos y decisiones abiertas

- **Plazo del 6-dic-2026**, con el plan 003 al final de la cadena 001 → 002 → 003 (arquitectura §9) → orden por
  prioridad de este plan; el punto de control de la fase 5 deja cifras clave, conclusiones 1 a 3 y confianza
  terminadas. Cualquier recorte lo decide Jairo.
- **Interfaces de 001 y 002 sin implementar todavía** → el punto de control de la fase 1 comprueba cada una; una firma
  distinta de la arquitectura §6 se reporta, no se adapta aquí.
- **Ningún número de la lámina 7** en esperados ni en textos; los esperados de FX-A salen del apéndice A, y los demás, de
  los fixtures descritos.
- **Tablas no comparables de la hoja EGM**: P-003-34 comprueba que el tablero no menciona ninguna (ADR-002, punto 6).
- **NC-P003-1, decidido por Jairo el 22-nov-2026**: la conclusión 3 toma como base los estudios del mapa y muestra «sin diligenciar» como quinta categoría, para que la suma dé el total (FR-003-07 ajustado por COR-013). Afecta T-003-24, T-003-27.
- **NC-P003-2, decidido por Jairo el 22-nov-2026**: cada cifra de celdas lleva la lista de cruces y los N.º de los estudios que los ocupan; para las celdas sin estudios, los estudios revisados. Afecta T-003-08, T-003-13, T-003-15.
- **NC-P003-3, decidido por Jairo el 22-nov-2026**: conclusión 4 según la propuesta del plan (agrupación por el conjunto de dimensiones de cada estudio; «nunca juntas» = pares con estudios propios y ninguno en común; dimensiones sin estudios, aparte), con base en los estudios del mapa. Afecta T-003-44, T-003-47.
- **NC-P003-4, decidido por Jairo el 22-nov-2026**: en la conclusión 6, un campo de texto vacío muestra el rótulo «sin diligenciar», sin otro texto. Afecta T-003-46.
- **NC-P003-5, decidido por Jairo el 22-nov-2026**: Jairo coordina la comprobación manual de SC-003-05 con la matriz vigente y el resultado se registra en el informe de la fase. Afecta T-003-93.

## Definición de terminado

- [ ] Todas las pruebas del plan en verde; cobertura ≥ 90 % de líneas en `src/egm/`.
- [ ] Lint y tipado sin errores.
- [ ] Cada requisito del apartado «Requisitos que cubre este plan» tiene tarea y prueba en `trazabilidad.md`.
- [ ] Cada número del tablero se abre en su lista de N.º, y la lista reproduce el número (SC-003-01, SC-000-02).
- [ ] Con la configuración por defecto, ningún porcentaje en el tablero (SC-000-07).
- [ ] Ningún texto dice «no investigado», ni «brecha» con filtros activos (SC-000-08, SC-003-04).
- [ ] FR-003-21 implementado y verificado (US-003-1.5).
- [ ] Ningún archivo de `data/raw/` ni `docs/fuentes/` modificado.
- [ ] NC-P003-1 a NC-P003-5 aplicados según las decisiones de Jairo del 22-nov-2026.
- [ ] Informe del `verificador` sin huecos ni excesos abiertos.

## Notas

- La etiqueta [US-003-n] vincula la tarea con su historia; **(disenador-front)** marca las tareas de vistas, que el
  `implementador` solo conecta.
- Los commits los hace Jairo; al terminar cada historia, el implementador se detiene y resume lo hecho.
- Si una tarea exige algo fuera del plan, o un módulo fuera de la lista de la arquitectura §6: detenerse y reportarlo.
- Las plantillas de M10 son internas del código; los textos que el equipo lee siguen las reglas de NFR-000-03.
- SC-003-05 (T-003-93) y SC-000-03 (T-003-92) se verifican por revisión manual; en la columna «Prueba» de `trazabilidad.md` figuran como «revisión manual (T-…)». Un caso borde del spec se cita por su texto entre comillas.

## Requisito → tarea (resumen)

FR-003-01: T-003-13, 14, 15, 16 · FR-003-02: T-003-13 · FR-003-03: T-003-16, 48, 49, 61, 62 · FR-003-04: T-003-08,
15, 22, 26, 27, 48, 49, 93 · FR-003-05: T-003-22, 25 · FR-003-06: T-003-23 · FR-003-07: T-003-24 · FR-003-08:
T-003-43, 44 · FR-003-09: T-003-45 · FR-003-10: T-003-46 · FR-003-11: T-003-22, 23, 24, 25, 44, 47 · FR-003-12:
T-003-25, 47, 92 · FR-003-13: T-003-54, 56, 57, 61, 63 · FR-003-14: T-003-53, 54, 56 · FR-003-15: T-003-55, 57 ·
FR-003-16: T-003-54, 55 · FR-003-17: T-003-06, 36 · FR-003-18: T-003-32, 33 · FR-003-19: T-003-32, 34, 35 ·
FR-003-20: T-003-34, 35 · FR-003-21: T-003-13, 14 · FR-003-22: T-003-23 · NFR-000-02: T-003-08, 13, 15, 33, 43 ·
NFR-000-03: T-003-14, 25, 32, 47, 92 · NFR-000-04: T-003-16, 27, 35, 49, 57, 62, 90, 91 · NFR-000-05: T-003-90, 91 · NFR-000-07: T-003-06, 07, 36
· NFR-000-08: T-003-25, 55 · NFR-000-13: T-003-16, 27, 49, 91.
