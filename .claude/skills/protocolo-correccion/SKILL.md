---
name: protocolo-correccion
description: Protocolo obligatorio de correcciones del proyecto EGM — explicar el error, proponer y evaluar opciones con el sistema completo, esperar aprobación de Jairo, aplicar y verificar consistencia. Usar al corregir cualquier archivo de docs/specs, arquitectura, interfaz o planes.
---

# Protocolo de corrección

## Principio

Ninguna corrección toca un archivo sin pasar por las cinco etapas, en este orden. Una
corrección local puede romper algo en otro spec; el protocolo existe para verlo antes.

| Etapa | Quién | Resultado |
|---|---|---|
| 1. Explicar el error | `analista-impacto` | Qué es, evidencia, regla incumplida |
| 2. Proponer y evaluar | `analista-impacto` | Opciones, impacto, recomendación |
| **Compuerta** | **Jairo** | Estado `aprobada` con la opción elegida |
| 3. Aplicar | `corrector` | Solo lo aprobado, en los archivos listados |
| 4. Verificar consistencia | `corrector` | Autocomprobación contra el sistema completo |
| 5. Auditoría independiente | `verificador` | Estado `verificada`; una sola vez, al cerrar el plan |

**Plan de corrección.** Es el conjunto de correcciones que Jairo encarga de una vez, por
ejemplo todos los pendientes de una auditoría. Las etapas 1 a 4 se repiten por cada corrección,
una a la vez. La etapa 5 **no** se ejecuta por corrección: el `verificador` corre una sola vez,
cuando todas las correcciones del plan estén en `aplicada`, `rechazada` o descartadas, y audita el
conjunto. Mientras tanto, cada corrección queda en `aplicada` y la siguiente puede empezar.
Llamarlo por cada corrección malgasta tokens.

## Archivo de la corrección

`docs/correcciones/COR-NNN.md`, numeración consecutiva, plantilla en
`references/plantilla-correccion.md`. Estados: `propuesta`, `aprobada`, `rechazada`,
`aplicada`, `verificada`. La sesión principal guarda la propuesta que devuelve el analista y
actualiza el estado cuando Jairo decide.

## Reglas

1. **Una corrección por error.** Se permite un lote solo si todas son de riesgo bajo y tocan
   los mismos archivos; cada una conserva su propia sección.
2. **Siempre hay opción 0** («no corregir»), con sus consecuencias.
3. **La recomendación se justifica con el sistema completo**: cite al menos tres elementos
   vinculados (IDs, términos, valores, ADR) o declare explícitamente que no hay vínculos.
4. **Riesgo.** Bajo: redacción o terminología sin cambio de significado, de valor ni de ID,
   verificable por búsqueda. Medio: cambia una regla o escenario dentro de un solo spec.
   Alto: cambia un contrato, una definición matemática, un valor repetido en varios lugares,
   un estado, o afecta a dos o más specs.
5. **Si una opción choca con un invariante**, no es una corrección: es una decisión de
   Jairo y se presenta como tal, sin aplicarla.
6. **Alcance cerrado.** La lista «Archivos a modificar» es exhaustiva. Nada fuera de ella.
7. **Lo desconocido se marca** `[NEEDS CLARIFICATION]`; no se resuelve por suposición.
8. **Intocable:** `data/raw/`, `docs/fuentes/`, las decisiones de Jairo y `invariantes.md`.
9. **Aprobación.** Solo vale si Jairo nombra la opción elegida. Sin eso, el corrector no actúa.
