# Plan de implementación: [NNN-FEATURE]

**Creado**: [FECHA] · **Estado**: borrador | aprobado | en ejecución | terminado
**Spec**: [`docs/specs/NNN-<feature>/spec.md`](../../specs/NNN-<feature>/spec.md)
**Arquitectura**: `docs/arquitectura/arquitectura.md` §[n] · **ADR relacionados**: [ADR-xxx]
**Ubicación de este plan**: `docs/planes/NNN-<feature>/plan.md`

<!--
  Plantilla de plan POR SPEC, la que rige la Fase 3 (decisión de Jairo, 21-nov-2026).
  Reglas que no se negocian (ver CLAUDE.md y skill `plan-modulo`):
  - No se escribe este plan sin arquitectura aprobada; no se escribe código sin este plan aprobado.
  - Toda tarea cita los requisitos que satisface (FR/NFR/SC). Toda prueba cita su escenario o criterio.
  - Pruebas primero: en cada historia, las pruebas se escriben y se ven fallar antes del código.
  - Lo que no esté en el spec no se implementa. Datos no verificados → [NEEDS CLARIFICATION: …].
  - Las pruebas usan `data/fixtures/`, nunca `data/raw/`.
-->

## Resumen

[Del spec: requisito principal + enfoque técnico tomado de la arquitectura y los ADR.]

## Contexto técnico

<!--
  ACCIÓN REQUERIDA: reemplazar con lo que fijan la arquitectura y los ADR aprobados.
  Si algo no está decidido allí, marcarlo [NEEDS CLARIFICATION: …]; no decidirlo en el plan.
-->

**Lenguaje/versión**: [p. ej., Python 3.x — ver ADR · NEEDS CLARIFICATION]
**Dependencias principales**: [p. ej., lector de xlsx, capa web según ADR · NEEDS CLARIFICATION]
**Almacenamiento**: [p. ej., lectura de `data/raw/` en solo lectura · N/A]
**Pruebas**: [p. ej., pytest + pruebas de propiedades — ver skill `calidad-python`]
**Plataforma objetivo**: [p. ej., navegador web, servidor local · NEEDS CLARIFICATION]
**Tipo de proyecto**: núcleo Python (`src/egm/`) + capa web (`app/`)
**Metas de desempeño**: [según NFR del spec · NEEDS CLARIFICATION]
**Restricciones**: [según NFR del spec; p. ej., conteos y no porcentajes bajo el umbral, trazabilidad a N.º de fila]
**Escala/alcance**: [p. ej., número de filas de la matriz, número de vistas · NEEDS CLARIFICATION]

## Requisitos que cubre este plan

| Requisito | Resumen | Historia | Escenario / criterio que lo verifica | Módulo(s) de la arquitectura |
|---|---|---|---|---|
| FR-xxx-nn | | US-xxx-n | US-xxx-n.m / SC-xxx-nn | |
| NFR-xxx-nn | | — | SC-xxx-nn | |

Fuera de alcance de este plan: [lista, con referencia al spec]

## Estructura del proyecto

### Documentación (esta feature)

```text
docs/specs/NNN-<feature>/
└── spec.md              # Spec aprobado (fuente de este plan)

docs/planes/NNN-<feature>/
└── plan.md              # Este archivo
```

### Código fuente (raíz del repositorio)

<!--
  ACCIÓN REQUERIDA: dejar solo las rutas reales que toca esta feature, según la arquitectura.
  No inventar módulos que la arquitectura no define.
-->

```text
src/egm/
├── [modulo]/            # p. ej., lectura, validación, modelo, análisis
└── ...

app/
└── [vista o ruta]/      # capa web según ADR

tests/
├── unit/
├── integracion/
└── propiedades/

data/fixtures/
└── [matriz-sintetica].xlsx
```

**Decisión de estructura**: [Explicar qué carpetas usa esta feature y en qué sección de la
arquitectura se apoya.]

<!--
  ============================================================================
  IMPORTANTE: las tareas de abajo son EJEMPLOS. Reemplazarlas por tareas reales derivadas de:
  - las historias de usuario del spec (US-xxx-n),
  - los requisitos FR/NFR y criterios SC del spec,
  - las entidades y contratos de la arquitectura y de `contrato-datos.md`.
  NO conservar las tareas de ejemplo.
  Formato de tarea:
  - [ ] T-NNN-nn [P] [US-xxx-n] Verbo + resultado verificable. Requisitos: FR-…. Pruebas: P-NNN-nn. Archivos: rutas.
  [P] = puede hacerse en paralelo (archivos distintos, sin dependencias pendientes).
  ============================================================================
-->

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: inicializar lo que la feature necesita y aún no existe.

- [ ] T-NNN-01 Crear la estructura de carpetas según «Estructura del proyecto». Requisitos: —. Archivos: […].
- [ ] T-NNN-02 [P] Crear o ampliar los fixtures sintéticos en `data/fixtures/` para los escenarios del spec. Requisitos: […].
- [ ] T-NNN-03 [P] Configurar lint, tipado y pruebas según `calidad-python` (si no están configurados).

---

## Fase 2: Base (prerrequisitos que bloquean)

**Propósito**: núcleo que DEBE estar terminado antes de cualquier historia de usuario.

**Crítico**: ninguna historia empieza antes de cerrar esta fase.

Ejemplos (ajustar a la feature):

- [ ] T-NNN-04 Implementar o reutilizar las entidades del modelo que usan todas las historias. Requisitos: […]. Archivos: `src/egm/[…]`.
- [ ] T-NNN-05 Implementar el manejo de errores y mensajes de validación comunes. Requisitos: […].
- [ ] T-NNN-06 Exponer la trazabilidad de cada número calculado a la lista de N.º de fila. Requisitos: […].

**Punto de control**: base lista; ya pueden empezar las historias.

---

## Fase 3: Historia 1 — [Título] (prioridad: P1)

**Objetivo**: [qué entrega esta historia]

**Prueba independiente**: [cómo verificar que la historia funciona por sí sola]

### Pruebas de la historia 1 (se escriben primero y deben fallar)

| ID prueba | Tipo (unit / integración / propiedades / e2e) | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-NNN-01 | | US-xxx-1.1 | `data/fixtures/…` | |
| P-NNN-02 | | SC-xxx-nn | `data/fixtures/…` | |

- [ ] T-NNN-10 [P] [US-xxx-1] Escribir P-NNN-01 en `tests/unit/test_[nombre].py`.
- [ ] T-NNN-11 [P] [US-xxx-1] Escribir P-NNN-02 en `tests/integracion/test_[nombre].py`.

### Implementación de la historia 1

- [ ] T-NNN-12 [P] [US-xxx-1] [Verbo + resultado]. Requisitos: FR-…. Pruebas: P-NNN-01. Archivos: `src/egm/[…]`.
- [ ] T-NNN-13 [US-xxx-1] [Verbo + resultado] (depende de T-NNN-12). Requisitos: FR-…. Pruebas: P-NNN-02. Archivos: […].
- [ ] T-NNN-14 [US-xxx-1] Conectar con la capa web, si la historia lo pide. Requisitos: FR-…. Archivos: `app/[…]`.

**Punto de control**: la historia 1 funciona y se prueba de forma independiente.

---

## Fase 4: Historia 2 — [Título] (prioridad: P2)

**Objetivo**: [qué entrega esta historia]

**Prueba independiente**: [cómo verificar que la historia funciona por sí sola]

### Pruebas de la historia 2 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-NNN-10 | | US-xxx-2.1 | `data/fixtures/…` | |

- [ ] T-NNN-20 [P] [US-xxx-2] Escribir P-NNN-10 en `tests/[…]/test_[nombre].py`.

### Implementación de la historia 2

- [ ] T-NNN-21 [US-xxx-2] [Verbo + resultado]. Requisitos: FR-…. Pruebas: P-NNN-10. Archivos: […].
- [ ] T-NNN-22 [US-xxx-2] Integrar con componentes de la historia 1 (solo si hace falta).

**Punto de control**: las historias 1 y 2 funcionan cada una por separado.

---

## Fase 5: Historia 3 — [Título] (prioridad: P3)

**Objetivo**: [qué entrega esta historia]

**Prueba independiente**: [cómo verificar que la historia funciona por sí sola]

### Pruebas de la historia 3 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-NNN-20 | | US-xxx-3.1 | `data/fixtures/…` | |

- [ ] T-NNN-30 [P] [US-xxx-3] Escribir P-NNN-20 en `tests/[…]/test_[nombre].py`.

### Implementación de la historia 3

- [ ] T-NNN-31 [US-xxx-3] [Verbo + resultado]. Requisitos: FR-…. Pruebas: P-NNN-20. Archivos: […].

**Punto de control**: todas las historias funcionan de forma independiente.

---

[Agregar más fases de historia según el spec, con el mismo patrón.]

---

## Fase N: Cierre y aspectos transversales

**Propósito**: mejoras que afectan a varias historias.

- [ ] T-NNN-90 Actualizar `docs/specs/trazabilidad.md` (tarea y prueba por requisito).
- [ ] T-NNN-91 Limpieza y refactorización sin cambiar comportamiento (pruebas en verde).
- [ ] T-NNN-92 [P] Pruebas de propiedades adicionales en `tests/propiedades/`.
- [ ] T-NNN-93 Revisión de accesibilidad y textos de interfaz (español, de usted, sin jerga), si aplica.
- [ ] T-NNN-94 Solicitar la verificación al subagente `verificador`.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)**: sin dependencias; puede empezar de inmediato.
- **Base (fase 2)**: depende de la fase 1; BLOQUEA todas las historias.
- **Historias (fase 3 en adelante)**: dependen de la fase 2.
  - Se ejecutan en orden de prioridad (P1 → P2 → P3), una a la vez.
- **Cierre (fase final)**: depende de las historias que se decida entregar.

### Dependencias entre historias

- **Historia 1 (P1)**: empieza tras la fase 2; sin dependencias de otras historias.
- **Historia 2 (P2)**: empieza tras la fase 2; puede integrarse con la 1, pero se prueba sola.
- **Historia 3 (P3)**: empieza tras la fase 2; puede integrarse con la 1 y la 2, pero se prueba sola.

### Dependencias con otros módulos o specs

- [Módulo o spec] → [interfaz que se consume] · [estado: listo / pendiente]

### Dentro de cada historia

- Pruebas primero: se escriben y se comprueba que fallan.
- Modelo antes que análisis; análisis antes que capa web.
- Implementación del núcleo antes que la integración.
- Historia terminada (pruebas en verde) antes de pasar a la siguiente prioridad.

## Riesgos y decisiones abiertas

- [Riesgo] → [mitigación] · [ADR-xxx] · [NEEDS CLARIFICATION: …]

## Definición de terminado

- [ ] Todas las pruebas del plan en verde; cobertura según `calidad-python`.
- [ ] Lint y tipado sin errores.
- [ ] Cada requisito del apartado «Requisitos que cubre este plan» tiene tarea y prueba en `trazabilidad.md`.
- [ ] Cada número mostrado es trazable a la lista de N.º de fila de la matriz.
- [ ] Ningún archivo de `data/raw/` ni `docs/fuentes/` modificado.
- [ ] Informe del `verificador` sin huecos ni excesos abiertos.
- [ ] [Criterios propios de la feature]

## Notas

- La etiqueta [US-xxx-n] vincula la tarea con su historia para la trazabilidad.
- Cada historia debe poder terminarse y probarse por sí sola.
- Los commits los hace Jairo; al terminar cada historia, detenerse y resumir lo hecho.
- Detenerse en cada punto de control para validar la historia de forma independiente.
- Si una tarea exige algo fuera del plan: detenerse y reportarlo; no ampliar el alcance.
- Evitar: tareas vagas, dos tareas sobre el mismo archivo en paralelo, dependencias entre
  historias que rompan su independencia.
