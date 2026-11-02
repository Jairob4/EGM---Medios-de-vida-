---
name: especificacion-srs
description: Cómo escribir los specs del proyecto EGM con la plantilla de Jairo (docs/specs/_plantilla/spec-template.md) — identificadores, fuentes obligatorias, criterios verificables y marcas NEEDS CLARIFICATION. Usar al crear o editar cualquier archivo en docs/specs/.
---

# Escritura de specs

## Plantilla y alcance

- Cada feature usa **sin alterar su estructura** `docs/specs/_plantilla/spec-template.md`
  (User Scenarios & Testing, Edge Cases, Requirements, Key Entities, Success Criteria).
  Encabezados de la plantilla en inglés; contenido en español.
- Única extensión permitida: dentro de *Requirements*, una subsección
  `### Non-Functional Requirements` cuando la feature tenga requisitos de calidad propios.
- Los specs describen **qué** y **por qué**, nunca **cómo**: sin frameworks, librerías ni nombres de
  archivos de código. El stack es decisión de arquitectura (ADR).
- Todos los specs están en versión **v0** hasta que el alcance se acuerde con la investigadora
  principal (fase F1 de la propuesta). Indicarlo bajo `**Created**`: `**Estado**: v0 — propuesta, alcance por acordar`.

## Identificadores (únicos en todo el repositorio)

| Elemento | Formato | Ejemplo |
|---|---|---|
| Historia | `US-<spec>-<n>` | `US-002-1` |
| Escenario | `US-<spec>-<n>.<m>` | `US-002-1.3` |
| Requisito funcional | `FR-<spec>-<nn>` | `FR-001-04` |
| Requisito no funcional | `NFR-<spec>-<nn>` | `NFR-000-02` |
| Criterio de éxito | `SC-<spec>-<nn>` | `SC-003-01` |

`<spec>` es el número de la carpeta (`000` para visión y requisitos globales).

## Reglas de contenido

1. **Fuente obligatoria.** Cada FR/NFR termina con su origen entre corchetes:
   `[Fuente: doc. general §4.2]`, `[Fuente: lámina 6]`, `[Fuente: Instrucciones B20]`,
   `[Fuente: decisión de Jairo, 31-oct-2026]`. Sin fuente → no es requisito: va como
   `[NEEDS CLARIFICATION]` o se descarta.
2. **Verificable.** Cada FR se comprueba con al menos un escenario Given/When/Then o un SC.
   Prohibido: «rápido», «intuitivo», «amigable» sin cifra o criterio observable.
3. **Datos reales solo de la matriz.** Los esperados de los escenarios salen de `contrato-matriz`
   (`referencia-v4.md`) o de fixtures sintéticos descritos en el propio escenario. Nunca de la lámina 7.
4. **Historias independientes** (P1 = MVP): cada una se puede demostrar sola.
5. **Edge Cases** cubre como mínimo los casos borde del contrato que afecten a la feature.
6. **Key Entities** usa los nombres del dominio: Documento, Estudio empírico, Intervención, Dimensión,
   Nivel de evidencia, Celda del mapa, Conclusión, Advertencia de validación.
7. **Success Criteria** medibles y agnósticos de tecnología.
8. Lo que no se sabe se marca `[NEEDS CLARIFICATION: <pregunta concreta>]` y se lista al final del
   informe de la fase. No se resuelve por suposición.

## Specs de este proyecto

| Carpeta | Feature | Prioridad |
|---|---|---|
| `000-vision-alcance.md` | Visión, actores, alcance, fuera de alcance, restricciones y NFR globales | — |
| `contrato-datos.md` | Contrato con la matriz (deriva de la skill `contrato-matriz`) | — |
| `001-lectura-verificacion/` | Leer, validar, contar y verificar contra la hoja EGM (fase F2) | P1 |
| `002-mapa-interactivo/` | Mapa con burbujas, detalle por celda, definiciones, filtros, exportar (F3) | P2 |
| `003-tablero-conclusiones/` | Tablero: cifras clave, las 6 conclusiones con trazabilidad (F4) | P3 |

Fuera de alcance (registrar en `000`, sin spec propio): vista de red (F5), módulo no supervisado.

## Antes de entregar

- [ ] Ningún nombre de tecnología en los specs.
- [ ] Todo FR/NFR con fuente y con escenario o SC que lo verifique.
- [ ] Identificadores únicos y sin huecos.
- [ ] `trazabilidad.md` actualizado (skill `trazabilidad`).
