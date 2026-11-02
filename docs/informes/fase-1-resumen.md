# Resumen de la Fase 1 (specs)

**Fecha**: 2026-11-02 (primera versión: 2026-11-01)  
**Lector**: Jairo. Este informe contiene información interna (sección 8) y no se comparte con el equipo.

## 1. Estado

Correcciones del 2-nov-2026 aplicadas y reauditadas. Sin código de aplicación, arquitectura ni planes de módulo.
Sin commit.

**La fase no está lista para aprobarse.** La reauditoría (`conformidad-fase-1-2026-11-02.md`) confirma las 12
decisiones y todos los controles de integridad, pero encontró 18 hallazgos nuevos: 1 mayor, 6 medios y 11 menores.
No se corrigieron: el encargo terminaba en este resumen.

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `docs/specs/contrato-datos.md` | Decisiones 1 a 5 y 6 en lo que toca al contrato; H-10, H-12, H-13, H-15, H-17, H-22; NC de H-16 |
| `docs/specs/000-vision-alcance.md` | Decisiones 6 a 11; 3 NFR y 3 SC nuevos; secciones «Decisiones futuras» y «Temas por definir con el equipo»; H-09, H-20, H-22 |
| `docs/specs/001-lectura-verificacion/spec.md` | Historia 4 (carga), 6 FR y 18 escenarios nuevos en total; H-07, H-09, H-21, H-22 |
| `docs/specs/002-mapa-interactivo/spec.md` | Decisiones 11 y 12; 1 FR y 4 escenarios nuevos; historias reordenadas; NC de H-08; H-07, H-09, H-13, H-21 a H-23 |
| `docs/specs/003-tablero-conclusiones/spec.md` | Decisión 10; 2 FR, 1 SC, historia 5 y 7 escenarios nuevos en total; historias reordenadas; H-09, H-21, H-22 |
| `docs/specs/trazabilidad.md` | Regenerado desde los specs; todos los SC y escenarios enlazados |
| `.claude/skills/sistema-diseno-egm/references/pie-de-pagina.md` | Colofón y logos según la decisión 8 |
| `docs/informes/conformidad-fase-1-2026-11-02.md` | Nuevo; lo escribió el `verificador` |
| `docs/informes/fase-1-resumen.md` | Este informe |

`data/raw/` y `docs/fuentes/` no se editaron. `.venv/` está ignorado por git.

## 3. Requisitos

| Spec | FR | NFR | Total | Antes |
|---|---|---|---|---|
| 000 Visión y alcance | 0 | 19 | 19 | 16 |
| 001 Lectura y verificación | 25 | 0 | 25 | 19 |
| 002 Mapa interactivo | 18 | 0 | 18 | 17 |
| 003 Tablero y conclusiones | 22 | 0 | 22 | 20 |
| **Total** | **65** | **19** | **84** | 72 |

Además: 35 SC, 88 escenarios y 14 historias, sin duplicados ni huecos. Según el `verificador`, 82 requisitos tienen
fuente y 2 son solo propuesta (FR-001-24 y FR-002-18), ya marcados. Los 84 están enlazados: 79 con cobertura
completa y 5 parcial (H-30).

## 4. Versión de Python

**Python 3.13.15**, en el entorno aislado del proyecto `.venv/`, creado con `py -3.13 -m venv .venv`.

Es la versión más reciente de las dos instaladas en el equipo (3.13 y 3.11), cumple el mínimo de la skill
`calidad-python` (≥ 3.11) y `openpyxl` y `pypdf` se instalaron en ella sin problema. En el entorno solo hay esos dos
paquetes y sus dependencias, usados para leer la matriz y los PDF. No se tocaron instalaciones globales ni otros
entornos. La compatibilidad con el stack se confirma en la arquitectura.

## 5. Decisiones aplicadas por criterio propio

**Dato opcional de la decisión 10: incluido** como FR-003-21 («estudios empíricos que aún no entran al mapa»; 6 en
la v4). H-37 observa que quedó como MUST sobre algo que usted dejó opcional.

**Correcciones que usted no pidió, y por qué:**

- **Reconocimiento de títulos de `EGM` (contrato §7.2).** Con la regla anterior, las frases de las tablas 2 y 4
  aparecían también en `A36` y `A35`, y esas tablas no se habrían reconocido. Ahora el título debe empezar por número
  y punto. El `verificador` lo comprobó contra el archivo.
- **«Registros internos» (decisión 4) frente a «los registros no contienen datos de la matriz» (decisión 6).** Se
  interpretó el primero como registros del proyecto (apéndice B e informes), no como registros de ejecución.
- **Historias reordenadas** por prioridad conservando sus ID, así que el número ya no sigue el orden del archivo.
  US-003-2 subió a P1, porque US-003-4 (P1) depende de leer conclusiones.
- **`.xlsx` por contenido.** La validación de tipo mira el contenido, no solo la extensión.
- **`contrato-matriz`.** Su regla «fila vacía = columna A vacía» difiere del contrato. El contrato deja registrado por
  qué prevalece; no se editó la skill.

## 6. Hallazgos

### Del informe anterior (H-01 a H-23)

**Cerrados (18):** H-01, H-02, H-03, H-06, H-07, H-09 a H-17, H-19, H-20, H-22 y H-23. H-16 se cuenta aquí porque
quedó como `[NEEDS CLARIFICATION]` con propuesta sin aplicar, como usted pidió; sigue esperando su decisión.

**Cerrados con residuo (5):**

| Hallazgo | Residuo |
|---|---|
| H-04 | «N.º, columna y valor» no aplica a las advertencias de archivo |
| H-05 | La nota cita un «plan aprobado» que no está en el repositorio |
| H-08 | Parte «sin nivel» como NC, según lo pedido; falta el nivel «No aplica» y `contrato §9` |
| H-18 | Cita inexacta de $N_{min}$ |
| H-21 | Dependencias restantes en `003:10-11`, US-003-1.4 y US-001-4.6 |

### Nuevos: abiertos (H-24 a H-41)

**Mayor**

| Hallazgo | Asunto |
|---|---|
| H-24 | §7 no define dónde termina cada tabla de `EGM` (los nombres de fila se repiten en `A6`, `A16`, `A26`), cómo reconocer «Total estudios», ni qué resultado da una categoría nueva que la hoja no tenga o una tabla con valores parciales. La verificación queda sin resultado definido |

**Medios**

| Hallazgo | Asunto |
|---|---|
| H-25 | Sin lista de tipo de documento, los no empíricos caen en «pendiente de codificación» |
| H-26 | «Pendiente de codificación» da 0 en la v4, mientras las láminas 8 y 10 y la skill hablan de 20. La cifra sigue la regla, pero el rótulo choca con los datos del equipo |
| H-27 | Nueve reglas del redactor, entre ellas §7.2, §7.4 y «registros internos», citan fuente sin marca de propuesta |
| H-28 | Un valor con espacios es causa conocida de diferencia, pero acabaría como «diferencia sin explicar» |
| H-29 | «Organización y Empresa», «Santa Marta» y «Director del grupo: Óscar García Vargas» no constan en ninguna fuente del repositorio. Ver la sección 8 |
| H-30 | Cobertura parcial en NFR-000-11, NFR-000-17, FR-001-25, FR-002-08 y FR-002-18 |

**Menores**

| Hallazgo | Asunto |
|---|---|
| H-31 | Nota `000:137` desactualizada |
| H-32 | `sistema-diseno-egm/SKILL.md:44` aún dice «Matriz v4, 27 documentos» |
| H-33 | Ancla «No aplica» sin tratamiento; $v_{\text{emp}}$ y $v_{\text{IE}}$ sin definir |
| H-34 | «Celda» quedó con dos sentidos (hoja y mapa) |
| H-35 | SC-000-09 dice «registra» y choca con NFR-000-17 |
| H-36 | Inicio de sesión contradictorio; filtros tras una carga nueva sin definir |
| H-37 | FR-003-21 es MUST sobre un dato opcional |
| H-38 | Historia y actores siguen dirigidos a Jairo, aunque los errores los recibe quien carga |
| H-39 | Bloque de dimensiones degenerado sin regla |
| H-40 | `trazabilidad.md` oculta propuestas parciales y un enlace |
| H-41 | SC-003-06 («misma frase») choca con FR-003-11, FR-003-16 y FR-003-22 |

## 7. Puntos abiertos por spec

### `[NEEDS CLARIFICATION]` (6)

**contrato-datos.md (2)**

1. `:171` Principal vacía con secundaria diligenciada (H-16). Propuesta sin aplicar: mantenerla en $M$ por su
   secundaria, con advertencia que cite B20.
2. `:382` *(Interno)* Si se comunica al equipo la discrepancia del apéndice B.

**000-vision-alcance.md (3)**

3. `:84` Identificación de la matriz (H-20). Propuesta: nombre del archivo y fecha de carga, sin deducir versión.
4. `:119` Límite de tamaño del archivo. Propuesta: 10 MB, configurable.
5. `:120` Tiempo de inactividad que termina la sesión. Propuesta: 30 minutos, configurable.

**001-lectura-verificacion (0)**

**002-mapa-interactivo (1)**

6. `:215` Estado «sin nivel» en el control único de la leyenda (H-08). Propuesta sin aplicar: entrada «Sin nivel» en
   la leyenda.

**003-tablero-conclusiones (0)**

### `[POR CONFIRMAR]` (1)

**pie-de-pagina.md**

1. `:21` Si su nombre figura y con qué rol. No se publica hasta que usted lo indique.

### Propuestas sin fuente aplicadas, pendientes de su aprobación

| Ubicación | Regla |
|---|---|
| `contrato-datos.md:83` | Orden del archivo (H-13) |
| `contrato-datos.md:101` | Una dimensión escrita como texto no marca (H-12) |
| `contrato-datos.md:108` | Año no reconocido (H-10) |
| `001-lectura-verificacion/spec.md:286` | FR-001-24, año no reconocido |
| `002-mapa-interactivo/spec.md:204` | FR-002-01, orden del archivo |
| `002-mapa-interactivo/spec.md:221` | FR-002-18, quitar filtros |

### Tema por definir con el equipo y decisión futura

- Definiciones de filas y columnas: archivo de texto aparte (`000`).
- Despliegue: lo decide el equipo después de la demostración (`000`).

## 8. La matriz y lo interno

**Integridad.** SHA-256 `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual al inicio y al
final. `data/raw/` y los archivos versionados de `docs/fuentes/` sin cambios. `Documento_tecnico_herramienta_EGM.pdf`
sigue sin versionar, así que git no puede atestiguar ese archivo. El apéndice A coincide con el recálculo del
`verificador`, incluidos $|P| = 6$ y los estados 1, 6, 20 y 0.

**H-29, regla 3 de `CLAUDE.md`.** Las líneas 13 y 14 de `pie-de-pagina.md`, que vienen del commit inicial, citan el
formato de vinculación de semillerista (25-sep-2026), que no está en `docs/fuentes/`. Esas líneas siguen sin marca y
el colofón las publicaría. No se tocaron, porque usted no pidió cambiarlas.

**Logos.** `docs/interfaz/logos/` aún no existe: SC-000-11 no se puede ejecutar hasta que usted los suministre.

**Marca sobrante.** `calidad-python/SKILL.md:24` conserva el `[NEEDS CLARIFICATION]` de la versión de Python, ya
resuelto. No se editó porque no estaba en el encargo.

**Interno.** La observación sobre la tabla 3 sigue solo en el apéndice B del contrato. Si los specs se comparten con
el equipo en F1, ese apéndice debe quedar fuera.

**Sin comprobar.** Ninguna hoja de cálculo confirmó que la fórmula de `EGM` cuente el texto «1». US-001-3.8 lo fija
en su *Given*, y la regla 10 sigue siendo propuesta.

## 9. Criterios de terminado

| Criterio | Estado |
|---|---|
| Ningún archivo de código de aplicación | Cumplido |
| `data/raw/` y `docs/fuentes/` sin modificar; hash registrado | Cumplido |
| Todo FR/NFR con fuente o propuesta marcada, y con escenario o SC; IDs únicos | Cumplido; 5 con cobertura parcial (H-30) y nueve reglas sin marcar (H-27) |
| Ninguna tecnología en los specs, salvo la restricción de Python | Cumplido |
| Reglas inviolables de `CLAUDE.md` | Incumplida la regla 3 en H-29, heredada del commit inicial |
| Informe del verificador sin huecos, o huecos listados aquí | Cumplido: listados en las secciones 6 y 7 |
