# Planes de la Fase 3: orden de ejecución

Hay un plan por spec, escrito con `_plantilla-plan-spec.md` (decisión de Jairo, 21-nov-2026). Se ejecuta **un plan a la vez** con el `implementador` y, para las vistas, con el `disenador-front`. Cada historia empieza por sus pruebas. Los commits los hace Jairo al terminar cada historia.

| Orden | Plan | Hito que deja | Qué toman los planes siguientes |
|---|---|---|---|
| 1 | [`001-lectura-verificacion/plan.md`](001-lectura-verificacion/plan.md) | **N1, núcleo listo** (fase 6): `procesar`, los tipos de M01, Esquema y Corpus, los conteos sin filtro de M07, `Verificacion` y los textos de M10. **N2, base web lista** (fase 7): `crear_app`, sesiones, cabecera, colofón, plantilla base, CSS, el guion del cliente (carga y ficha de sesión; actividad e inactividad en la fase 8 del 001) y la configuración | El constructor de matrices sintéticas (M23, `tests/constructor.py`), CB-01 a CB-41, FX-A, las estrategias de hypothesis y las sesiones de prueba |
| 2 | [`002-mapa-interactivo/plan.md`](002-mapa-interactivo/plan.md) | **Mínimo entregable** al terminar sus fases 3 y 4: mapa con filtros, «Actualizar vista» y «Restablecer» | El filtro de M06, M07 con filtro y desglose por nivel, el filtro aplicado de M15 y los rótulos de M10 |
| 3 | [`003-tablero-conclusiones/plan.md`](003-tablero-conclusiones/plan.md) | Al terminar su fase 5: cifras clave, conclusiones 1 a 3 y confianza | — |

## Por qué en este orden

- El plan 002 consume la fachada `procesar`, el modelo y la base web del 001.
- El plan 003 consume además el filtro (M06) y las rutas de filtros del 002, y solo agrega `cumple_documento` y las coocurrencias.

## Camino crítico para el 6-dic-2026

1. El plan 001 completo, porque es la base de los otros dos.
2. El plan 002 hasta el mínimo entregable (fases 3 y 4).
3. El plan 003 hasta su fase 5.
4. Con el tiempo que quede, el resto del 002 (cajón, definiciones, exportación y accesibilidad) y del 003 (conclusiones 4 a 6, filtros y recorrido).

Si hay que recortar, decide Jairo.

## Pendientes antes de empezar el plan 001

- **Aprobación de los tres planes por Jairo**, después de aplicar COR-013 (decisión de Jairo, 22-nov-2026).
- **NC-ARQ-1** se resuelve dentro del plan 001 (T-001-09).
