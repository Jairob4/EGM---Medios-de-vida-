# ADR-005: Colofón por bloques, con los bloques institucionales apagados por defecto

**Fecha**: 2026-11-21 · **Estado**: aceptado, 2026-11-21 [Fuente: decisión de Jairo, 21-nov-2026]
**Requisitos que la motivan**: NFR-000-11, NFR-000-12, NFR-000-16, NFR-000-03, NFR-000-04, NFR-000-05, SC-000-11,
SC-000-12, SC-000-16

> **Nota de revisión, 2026-11-21 (Fase 2, interfaz; NC-INT-1)** [Fuente: decisión de Jairo, 21-nov-2026]. Qué
> cambió: además de los seis bloques ya apagados, vienen apagados por defecto `proyecto`, `semillero` y `equipo`. Con
> la configuración por defecto solo quedan visibles «Datos» y la referencia a 3ie. Por qué: hasta que Jairo tenga la
> autorización no se publica en el colofón ningún bloque institucional ni de personas; el `disenador-front` lo planteó
> como NC-INT-1 en `docs/interfaz/flujos.md` y Jairo lo decidió. Afecta al punto 2, a la tabla de bloques y a las
> consecuencias. El estado sigue «aceptado»; los specs no cambian.

## Contexto

- NFR-000-11 pide un colofón con la información del grupo, el código Minciencias COL0016423, el correo de contacto y
  los logos de Minciencias y de la Universidad del Magdalena; omite categoría y línea de investigación; no publica datos
  pendientes de confirmación (se omite la línea completa); logos sin recolorear ni deformar, con texto alternativo,
  legibles en claro y oscuro y desde 360 px.
- **Decisión de Jairo, 21-nov-2026**: los specs no cambian, pero nada de la Universidad del Magdalena (logos ni nombres)
  se publica hasta que Jairo tenga autorización. Cada bloque institucional se activa por configuración y viene
  **apagado por defecto**; NFR-000-11 se cumple al encenderlos. Los bocetos muestran el colofón con esos bloques
  apagados.
- NFR-000-12: el bloque «Datos» se arma en tiempo de ejecución («Matriz: <nombre del archivo tal como llegó>, leída el
  <fecha de la carga>, <n> documentos»), sin deducir versión.
- NFR-000-16 y SC-000-16: la referencia a 3ie aparece citada en el colofón.
- Contenido confirmado y fuentes: `.claude/skills/sistema-diseno-egm/references/pie-de-pagina.md`. La línea
  «Herramienta» está marcada «[POR CONFIRMAR]». Los logos aún no están en `docs/interfaz/logos/` (resumen de la fase 1,
  §7).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| A. Colofón escrito en la plantilla, comentando o borrando lo institucional | Inmediato | Encender un bloque exige editar la plantilla; fácil publicar algo por error; no es configuración |
| B. Un solo interruptor «institucional» para todo | Simple | No permite encender, por ejemplo, el logo de Minciencias sin el de la universidad |
| C. **Bloques en la configuración, una bandera por bloque, apagadas por defecto**; «Datos» y «Referencia de diseño» siempre presentes | Cumple la decisión del 21-nov-2026 con granularidad; publicar algo exige un cambio explícito en la configuración; NFR-000-11 se comprueba encendiendo los bloques | Un poco más de código y de pruebas |

## Decisión

**Opción C**, en `app.colofon` (M21) y `app.configuracion` (M22).

1. El colofón es una lista ordenada de bloques (`BloqueColofon`: clave, `activo`, texto, logo). El orden y el texto
   siguen `pie-de-pagina.md`. Los textos institucionales viven en la configuración, no en la plantilla.
2. Bloques y valor por defecto (antes NC-ADR005-1; ampliado por NC-INT-1). Se apagan por defecto nueve bloques:
   `proyecto`, `grupo`, `codigo_minciencias`, `semillero`, `equipo`, `herramienta`, `contacto`, `logo_minciencias` y
   `logo_unimagdalena`. Hasta la autorización, solo «Datos» y la referencia a 3ie quedan visibles, y son los únicos
   siempre visibles [Fuente: decisión de Jairo, 21-nov-2026]. Cada bloque apagado se enciende por separado cuando Jairo
   tenga la autorización.

   | Bloque | Contenido (de `pie-de-pagina.md`) | Por defecto |
   |---|---|---|
   | `proyecto` | Nombre del proyecto | **apagado** (NC-INT-1) |
   | `grupo` | Organización y Empresa (GIOE), Universidad del Magdalena, Santa Marta; director | **apagado** |
   | `codigo_minciencias` | COL0016423 | **apagado** |
   | `semillero` | Desarrollo Rural y Economía Solidaria | **apagado** (NC-INT-1) |
   | `equipo` | Investigadora principal y coinvestigadora | **apagado** (NC-INT-1) |
   | `herramienta` | Línea «Herramienta» | **apagado** y, además, omitida mientras esté marcada como pendiente de confirmación |
   | `contacto` | Correo de contacto | **apagado** |
   | `logo_minciencias` | Logo, texto alternativo, placa clara si hace falta | **apagado** |
   | `logo_unimagdalena` | Logo, texto alternativo, placa clara si hace falta | **apagado** |
   | `datos` | Texto de NFR-000-12 en tiempo de ejecución | siempre; no configurable |
   | `referencia_diseno` | Cita de 3ie | siempre; no configurable |

3. Reglas de composición: un bloque apagado no deja rastro en el HTML (ni oculto ni comentado). Un bloque encendido
   cuyo texto contenga una marca de pendiente de confirmación se omite completo. Un bloque de logo encendido cuyo
   archivo no exista se omite completo y produce un registro técnico sin datos. Los logos se dibujan con sus
   proporciones y sus colores originales (sin filtros CSS), con texto alternativo y sobre una placa clara en modo
   oscuro si hace falta.
4. Sin matriz cargada, el bloque «Datos» no muestra cifras (US-001-4.2).
5. La comprobación de SC-000-11 se hace con una configuración de prueba que enciende todos los bloques; la configuración
   por defecto se comprueba aparte: el colofón contiene solo «Datos» y la referencia a 3ie; ningún texto ni logo de la
   Universidad del Magdalena, ni el nombre del proyecto, del semillero o de las personas del equipo aparece.

## Consecuencias

- Positivas:
  - Con la configuración por defecto no se publica nada de la Universidad del Magdalena ni ningún bloque institucional
    o de personas; el colofón muestra solo «Datos» y la referencia a 3ie. Encender un bloque es un acto explícito y
    revisable.
  - NFR-000-11 se cumple y se comprueba al encender los bloques, sin tocar plantillas ni specs.
  - «Datos» y la referencia 3ie no se pueden apagar por error (NFR-000-12, NFR-000-16).
- Negativas / deuda aceptada:
  - Con la configuración por defecto, SC-000-11 no se cumple en la demostración; queda pendiente de la autorización de
    Jairo y de los logos en `docs/interfaz/logos/`.
- Requisitos afectados y cómo se verifican:
  - NFR-000-11: SC-000-11 con todos los bloques encendidos; prueba de que con la configuración por defecto el colofón
    solo tiene los bloques `datos` y `referencia_diseno`, y no contiene «Universidad del Magdalena», «unimagdalena» ni
    ningún logo.
  - NFR-000-12: SC-000-12 con una matriz sintética de otro nombre y otro número de documentos, y con «v4» en el nombre.
  - NFR-000-16: SC-000-16.
