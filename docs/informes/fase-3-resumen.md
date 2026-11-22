# Resumen de la Fase 3 — Planes por spec

**Fecha**: 22-nov-2026 · **Para**: Jairo · **Estado**: los tres planes están en borrador, a la espera de su revisión.
Detalle y evidencia: `docs/informes/conformidad-fase-3-2026-11-22.md`.

## 1. Planes escritos

| Plan | Tareas | Pruebas | Qué entrega |
|---|---|---|---|
| `docs/planes/001-lectura-verificacion/plan.md` | 61 | 95 | Lectura, advertencias, verificación con la hoja EGM, carga desde el navegador, sesión, cabecera y colofón. Crea el constructor de matrices sintéticas, con un fixture por cada caso borde del contrato |
| `docs/planes/002-mapa-interactivo/plan.md` | 50 | 68 | Mapa, filtros, detalle de cada cajón, definiciones, exportación y accesibilidad del mapa |
| `docs/planes/003-tablero-conclusiones/plan.md` | 57 | 51 | Cifras clave, las seis conclusiones, aclaraciones de confianza, filtros del tablero y paso entre mapa y tablero |
| **Total** | **168** | **214** | |

Resultado de la auditoría: **conforme con reservas**. Los 89 requisitos tienen tarea, los 122 escenarios tienen
prueba y ningún plan usa un módulo que la arquitectura no defina. No hay hallazgos graves. Hay seis de severidad media
(F3-01 a F3-06) y once menores. La huella de la matriz no cambió, `docs/fuentes/` no tiene cambios y aún no hay código.

## 2. Orden de ejecución

Un plan a la vez, como indica `docs/planes/README.md`:

1. **Plan 001.** Deja el hito N1 (núcleo listo, fase 6) y el hito N2 (base web lista, fase 7).
2. **Plan 002.** Sus fases 3 y 4 dejan el mínimo entregable: el mapa con filtros, «Actualizar vista» y «Restablecer».
3. **Plan 003.** Su fase 5 deja las cifras clave, las conclusiones 1 a 3 y las aclaraciones de confianza.

## 3. Camino crítico hacia el 6-dic-2026

Plan 001 completo, plan 002 hasta la fase 4 y plan 003 hasta la fase 5: **114 tareas y 160 pruebas** en unos 14 días,
es decir, unas ocho tareas por día, con unos dieciséis puntos de detención para resumen y commit. La opinión técnica
es que el plazo es **ajustado y con riesgo alto**. El riesgo mayor está en la parte web y de sesión del plan 001, con
sus pruebas en navegador, y en que la comprobación NC-ARQ-1 detenga ese plan si su resultado es adverso. Si hay que
recortar, la decisión es suya. Lo que más tiempo liberaría son las pruebas en navegador de la sesión del plan 001 y la
fase de accesibilidad del plan 002.

## 4. Hallazgos de severidad media

- **F3-01.** Hay escenarios que los planes 001 y 002 pasan al 003 y que este no recoge: la huella después de usar
  todas las vistas (US-001-4.6), la parte del tablero de US-001-4.10, de US-002-4.6 y de US-002-4.14.
- **F3-02.** El plan 003 usa una réplica sintética de la matriz vigente (FX-A) que, según él, crea el plan 001. El plan
  001 no la incluye.
- **F3-03.** Ningún plan agrega el filtro a los conjuntos ni al conteo de evaluación de impacto, y el plan 003 los
  necesita filtrados.
- **F3-04.** El plan 003 nombra el constructor `tests/fixtures_builder.py`, mientras los planes 001 y 002 usan
  `tests/constructor.py`.
- **F3-05.** Cada plan pone en una carpeta distinta las pruebas en navegador y el guion del cliente.
- **F3-06.** Tres pruebas de los planes 002 y 003 toman sus valores esperados de la matriz vigente y no del apéndice A
  del contrato.

## 5. Pendientes abiertos

**Necesitan su decisión** (cada uno trae una propuesta en su plan):

- Plan 001: NC-P001-1, sobre la vista que se muestra tras una carga aceptada mientras no exista el mapa, y NC-P001-2,
  sobre los archivos de los logos.
- Plan 002: NC-P002-2 a NC-P002-5, sobre el lector de pantalla, el formato de las definiciones, el enlace de un DOI y
  el orden de los valores sin lista. NC-P002-1 queda resuelto por lo que ya dicen los planes 001 y 002, y se puede cerrar.
- Plan 003: NC-P003-1 a NC-P003-5, sobre las conclusiones 3, 4 y 6, la trazabilidad de las cifras de celdas y la
  comprobación con una persona del equipo. Si se adopta, la propuesta de NC-P003-1 puede requerir una corrección del
  spec 003 por el flujo de la regla 11.
- La autorización para descargar las dependencias y los recursos locales (F3-09). El plan 001 la da por hecha, pero
  no consta en ningún registro.

**Se resuelve dentro del plan 001**: NC-ARQ-1, en la tarea T-001-09.

**Van a COR-013**: O-1 (nombre del constructor, ampliada con F3-04), O-2 (ADR-003, punto 2 frente al punto 4,
ampliada con F3-16), O-3 (el filtro en las firmas del conteo), O-4 (NFR-000-16 frente al colofón), F2-13 (fecha de
la nota de ADR-003), F2-14 (datos del colofón dados por confirmados) y F3-17 (la tabla de la arquitectura sobre el
filtro de nivel y NFR-000-09).

## 6. Lo que necesita la Fase 4

Antes de empezar el plan 001:

1. Su aprobación del plan 001.
2. La autorización de las descargas (F3-09).

Antes de la tarea que se indica, para no rehacer trabajo:

3. El nombre del constructor (O-1 y F3-04), antes de T-001-04.
4. Decidir dónde se crea FX-A (F3-02), antes de T-001-07.
5. La carpeta de las pruebas en navegador (F3-05), antes de T-001-61.
6. NC-P001-1 y O-2, antes de la fase 7 del plan 001.

Antes de aprobar los planes 002 y 003: resolver o aceptar F3-01, F3-03 y F3-06, y los hallazgos menores que les
correspondan.

El implementador se detiene en cada punto de control y en los hitos N1 y N2. Los commits los hace usted al terminar
cada historia.
