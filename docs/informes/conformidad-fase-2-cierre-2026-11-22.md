# Informe de conformidad: cierre de la Fase 2 y auditoría única del plan de corrección COR-012

**Fecha**: 2026-11-22
**Autor**: `verificador`. No participó en producir lo auditado.
**Lector**: Jairo. Es un documento interno.
**Alcance**: COR-012 (estado `aplicada`; aprobada el 2026-11-22, opción A en todos los hallazgos y P1 (a)), los 9
archivos de su lista cerrada y su efecto conjunto sobre specs, trazabilidad, arquitectura, ADR, interfaz y skill de diseño.
**Base**: HEAD `adafb0d` («fase de arquitectura de backend y frontend inciada y primeras iteraciones») y `git diff`
sobre él.
**Modo**: solo lectura. No se corrigió nada. Solo se escribió en `docs/informes/`.

**Método**
- Atribución bloque por bloque del `git diff` sobre HEAD, comparando cada bloque con el texto literal de COR-012 §4.
- Repetición de las 12 búsquedas de la tabla de 4 bis de COR-012.
- Recuento por programa de las listas «Cubre» de `arquitectura.md` (M01 a M23), comparadas con los requisitos
  definidos en los specs y con la columna «Componente» de `trazabilidad.md`.
- Medición por programa del ancho del cuadro ASCII de `tokens.md`, en el árbol de trabajo y en HEAD.
- Conteo de finales de línea CRLF en los 9 archivos y en `trazabilidad.md`.
- SHA-256 de la matriz en modo lectura.

**No aplica en esta fase**: `ruff`, `mypy` y `pytest --cov`. No hay código: `src/egm/`, `app/` y `tests/` solo
contienen `.gitkeep`.

---

## 1. Veredicto

- **COR-012 queda `verificada`.**
  - Se aplicó al pie de la letra y solo en los 9 archivos de su lista cerrada (§2).
  - Sus secciones 7 y 8 coinciden con el repositorio.
  - Las dos desviaciones de forma que informó el corrector son aceptables y no cambian ningún texto exigido (§3).
- **F2-01 a F2-03 y F2-05 a F2-11 quedan cerrados** (§4). F2-04 ya estaba resuelto (`invariantes.md:99-100`).
- **Lo ya verificado se mantiene** (§5): 89 de 89 requisitos con módulo, «Componente» igual a «Cubre» en los 89,
  0 `[NEEDS CLARIFICATION]` en los specs, `trazabilidad.md` con 191 líneas CRLF, matriz intacta.
- **La Fase 2 puede cerrarse con la aprobación de Jairo de `arquitectura.md`.** No hay hallazgos bloqueantes. Hay tres
  hallazgos menores nuevos (F2-12 a F2-14, §7). F2-12 es un registro que hace la sesión principal y conviene hacerlo
  antes de la aprobación; F2-13 y F2-14 pueden ir a una corrección posterior o a la preparación del plan 001.

---

## 2. Aplicación literal y lista cerrada

`git status` sobre HEAD: 9 archivos modificados, exactamente los 9 de COR-012 §5 asignados al corrector, y
`docs/correcciones/COR-012.md` sin seguimiento. Ningún otro archivo cambió.

**Sesión principal.** `invariantes.md` y `COR-011.md` no tienen diferencias con HEAD: sus cambios (secciones del
21-nov-2026 de `invariantes.md:75-104` y COR-011 §9 con estado `verificada`, `COR-011.md:3`, `:202`) ya forman parte
del commit `adafb0d`, que agrega `invariantes.md` (+28) y `COR-011.md` (+224). Por eso ningún bloque del diff es de la
sesión principal. `COR-012.md` (sin seguimiento) es de la sesión principal y del `analista-impacto` en §1 a §6, y del
corrector en §7, §8 y el estado `aplicada` (`COR-012.md:3`).

**Atribución de cada bloque del diff (todos a COR-012).**

| Archivo | Bloque del diff | Punto de COR-012 | Literal |
|---|---|---|---|
| `docs/interfaz/flujos.md` | `:13` | 4.21 | Sí |
| | `:56-57` (E10 y «E2 / E3 / E10») | 4.1 | Sí |
| | `:87-88` | 4.2 | Sí |
| | `:276-281` (F-003-3) | 4.8 | Sí |
| | `:309-312` (§6) | 4.5 | Sí |
| | `:330` (§7, punto 5) | 4.6 | Sí |
| | `:358-373` (§9) | 4.7 | Sí |
| `docs/interfaz/bocetos/carga.html` | `:11` y `:52-58` (E10) | 4.3 | Sí |
| `docs/interfaz/bocetos/colofon.html` | `:27` | 4.9 | Sí |
| `docs/interfaz/bocetos/tablero.html` | `:161` y `:170` (`pend-f`) | 4.19 | Sí |
| `docs/arquitectura/arquitectura.md` | `:7` | 4.14 | Sí |
| | `:267-270` (andamiaje) | 4.20 | Sí |
| | `:687` (coma en M23) | 4.18 | Sí |
| | `:756` (V1) | 4.4 | Sí |
| | `:782` (fila de riesgo NC-ARQ-1) | 4.15 | Sí |
| | `:787`, `:797`, `:798` (§10) | 4.16 y 4.10 | Sí |
| `docs/arquitectura/adr/ADR-003-stack-web-python.md` | `:8-9` (nota) y `:133-135` | 4.17 | Sí |
| `.claude/skills/sistema-diseno-egm/SKILL.md` | `:42` y `:54` | 4.11 | Sí |
| `.../references/tokens.md` | `:35`, `:60-61`, `:64`, `:78`, `:82` | 4.12 y P1 (a) | Sí, salvo el relleno (§3) |
| `.../references/pie-de-pagina.md` | `:8-14`, ocho líneas en cursiva (`:20`, `:25`, `:28`, `:31`, `:34`, `:40`, `:45`, `:48`), `:52-54`, `:68` | 4.13 | Sí |

**Finales de línea.** Los 9 archivos tienen todas sus líneas en CRLF, igual que en HEAD (por ejemplo, `flujos.md`:
373 de 373; `arquitectura.md`: 798 de 798; `pie-de-pagina.md`: 68 de 68).

**No se tocaron** (COR-012 §5): specs, `trazabilidad.md`, ADR-001, ADR-002, ADR-004, ADR-005, `tokens.css`,
`boceto.css`, `boceto.js`, `index.html`, `mapa.html`, `estudio.html`, `src/`, `data/` ni `docs/fuentes/`.

---

## 3. Las dos desviaciones de forma

**`tokens.md`: el cuadro mide 77 caracteres y no 78. Aceptable.**
- El cuadro ya medía 77 en HEAD: líneas 59, 61 y 64 a 78 de HEAD, por programa. La premisa de 4.12 («conserva 78
  caracteres») era inexacta. Lo exigido era conservar el ancho, y 4.12 deja el relleno al corrector.
- Las líneas nuevas `:60` y `:61` miden 77, igual que el borde `:59`. Las palabras son las de 4.12.
- `:78` («Colofón: «Datos» y referencia a 3ie; los demás bloques, apagados por defecto») mide 77 sin espacio antes
  del «│». El texto es el literal de 4.12. Solo falta un espacio de relleno, que es una diferencia visual.
- `:63-64` (filtros) miden 78, como en HEAD. El corrector las dejó así. Es irregularidad previa del boceto, no de COR-012.

**`pie-de-pagina.md`: las líneas en cursiva van pegadas al párrafo anterior. Aceptable.**
- Es la aplicación literal de 4.13 («Debajo de cada bloque … va una línea en cursiva»).
- El archivo ya usaba esa forma: en `:22-24`, el director y el código Minciencias van en líneas seguidas del mismo bloque.
- Es una referencia que leen los subagentes como texto fuente. Al mostrarse como Markdown, cada frase en cursiva
  queda al final de su bloque, que es su sitio. El sentido no cambia.

---

## 4. Hallazgos F2-01 a F2-11 (sin F2-04)

**Búsquedas de 4 bis de COR-012, repetidas**

| Búsqueda | Dónde | Esperado | Obtenido | Evidencia |
|---|---|---|---|---|
| «demasiado grande para abrirlo» | `docs/interfaz/` | 2 | 2 | `flujos.md:56`, `carga.html:56` |
| «tabla 3» (sin distinguir mayúsculas) | `docs/interfaz/` | 0 | 0 | — |
| «seis bloques» (sin distinguir mayúsculas) | `docs/interfaz/` y la skill | 0 | 0 | — |
| «brechas» | la skill | 0 | 1 | `SKILL.md:42`, texto exigido por 4.11 («sin la palabra «brechas»»); no es un título que la use |
| «Matriz v4» | `tokens.md` | 0 | 0 | — |
| «leída hoy» | `tokens.md` | 0 | 0 | — |
| «Google Fonts» | `tokens.md` | 0 | 0 | también 0 en toda la skill |
| «Se publican los logos» | la skill | 0 | 0 | — |
| `[NEEDS CLARIFICATION: NC-INT` | `docs/`, salvo `informes/` y `correcciones/` | 0 | 0 | — |
| «NC-ARQ-1» | `arquitectura.md` | 3 | 3 | `:782`, `:787`, `:798`; fuera de ahí solo en `COR-012.md` |
| «268 435 456» | ADR-003 | 0 | 0 | — |
| «pend-f» | `tablero.html` | 1 | 1 | `:170` |
| «4.1 a 4.12» | `docs/interfaz/` | 0 | 0 | — |

**Estado de cada hallazgo**

| Hallazgo | Estado | Evidencia |
|---|---|---|
| F2-01 | Cerrado | E10 en `flujos.md:56-57`, estados y «Cubre» `:87-88`; sección E10 en `carga.html:52-58` y cabecera `:11`; V1 con «contenido descomprimido» y NFR-000-19 en `arquitectura.md:756`. El mensaje coincide con NFR-000-19 (`000-vision-alcance.md:92`) y con US-001-4.13 (`001/spec.md:234-237`). E10 es único y E2 a E9 no se renumeraron |
| F2-02 | Cerrado | §9 como puntos decididos, `flujos.md:358-373`; §6 con nueve bloques, `:309-312`; §7, punto 5, `:330`; nota del boceto, `colofon.html:27`; fila NC-INT, `arquitectura.md:797`. NC-INT-2 coincide con `invariantes.md:93` |
| F2-03 | Cerrado | `SKILL.md:42`, `:54`; `tokens.md:35`, `:60-61`, `:78`, `:82`; `pie-de-pagina.md:8-14`, `:52-54`, `:68`. Los nueve bloques coinciden con ADR-005, punto 2 (`ADR-005:44-63`). Ver F2-14 |
| F2-05 | Cerrado | `arquitectura.md:7` remite a `invariantes.md`, secciones del 21-nov-2026 (`:75-101`) |
| F2-06 | Cerrado | NC-ARQ-1 en `arquitectura.md:782`, `:787` y `:798`, con `[NEEDS CLARIFICATION: …]` y destino «preparación del plan 001» |
| F2-07 | Cerrado | `ADR-003:133-135` nombra el segundo límite y remite a ADR-004, punto 5, sin repetir la cifra; nota de revisión `:8-9`. Ver F2-13 |
| F2-08 | Cerrado | `arquitectura.md:687`: «de otro tipo,» |
| F2-09 | Cerrado | `tablero.html:170` («0 de 6») y nota `:161`; `flujos.md:276-281`. «0 de 6» y «0 de 7» salen del apéndice A: $\lvert P\rvert = 6$, $\lvert E\rvert = 7$, 0 territoriales (`contrato-datos.md:393`, `:395`, `:402`) |
| F2-10 | Cerrado | `arquitectura.md:267-270`. El árbol sigue igual: `src/egm/{analisis,lectura,modelo,validacion}/.gitkeep` |
| F2-11 | Cerrado | `flujos.md:13`: «Ningún flujo, boceto ni texto usa información interna del proyecto.» |

---

## 5. Lo ya verificado se mantiene

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Requisitos con módulo | 89 de 89 (19 NFR-000, 29 FR-001, 19 FR-002, 22 FR-003); 23 módulos, todos con requisito; ningún ID en «Cubre» que no exista | programa sobre las listas «Cubre» de M01 a M23 |
| «Componente» igual a «Cubre» | 89 de 89, 0 diferencias | `trazabilidad.md:7-95` |
| `[NEEDS CLARIFICATION]` en los specs | 0. Las únicas 2 coincidencias de `docs/specs/` son ejemplos de la plantilla en inglés | `_plantilla/spec-template.md:88-89` |
| `trazabilidad.md` | 191 líneas, todas CRLF; sin cambios frente a HEAD | conteo y `git diff` |
| SHA-256 de la matriz | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual al registrado | `contrato-datos.md:374` |
| `docs/fuentes/`, `data/raw/` y `docs/specs/` | Sin cambios ni archivos nuevos frente a HEAD | `git diff --quiet HEAD` y `git ls-files --others` |

---

## 6. Reglas de `CLAUDE.md`

- **Regla 3.** Cada decisión registrada cita su fuente fechada (`flujos.md:361`; `pie-de-pagina.md:68`). NC-ARQ-1 va
  marcado como `[NEEDS CLARIFICATION: …]` (`arquitectura.md:782`). Hay dos inexactitudes menores: F2-13 (fecha) y
  F2-14 («datos confirmados»).
- **Regla 7.** Las cifras nuevas («0 de 6», «0 de 7», «6», «7») salen del apéndice A (`contrato-datos.md:393-402`).
  Ninguna viene de la lámina 7.
- **Regla 9.** «tabla 3» da 0 en `docs/interfaz/`. Fuera de ahí aparece solo en registros internos y en archivos
  anteriores sin cambios: `arquitectura.md`, que se declara interno (`:12`), ADR-002, `contrato-datos.md`, las
  skills, las invariantes, las COR, los informes y `docs/fuentes/`. COR-012 no agregó ninguna mención nueva fuera de
  su propio texto.
- **Regla 8.** Los textos nuevos de la interfaz (`carga.html:55-57`, `tablero.html:170`) son de usted, sin preguntas
  y sin cifras de límite.
- **Regla 11.** Hubo propuesta, aprobación de Jairo (`COR-012.md:316-319`), aplicación por el corrector solo sobre su
  lista y esta auditoría única al cierre del plan. ADR-003, que está «aceptado», cambió solo por COR-012, conforme a la
  regla del 21-nov-2026 (`invariantes.md:100`), y lleva su nota de revisión.

---

## 7. Hallazgos nuevos

Ninguno es bloqueante.

**F2-12 (menor). La aprobación de COR-012 del 22-nov-2026 no está registrada en las invariantes.**
- COR-012 §5 asigna a la sesión principal «Registro de la aprobación» en `invariantes.md` (`COR-012.md:306`).
- `invariantes.md` no tiene ninguna sección del 22-nov-2026. Solo dice que COR-012 «recoge» los hallazgos
  (`:101`). No constan la opción A en todo, P1 (a) (tipografías servidas localmente), ni la fecha.
- `invariantes.md:104` dice «Ninguno a 21-nov-2026».
- **Propuesta**: la sesión principal registra la aprobación del 22-nov-2026 antes de que usted apruebe
  `arquitectura.md`. No requiere el flujo de la regla 11.

**F2-13 (menor). La nota de revisión de ADR-003 lleva la fecha 2026-11-21, pero COR-012 se aprobó el 2026-11-22.**
- `ADR-003:8`: «Nota de revisión, 2026-11-21 (COR-012, F2-07)».
- `COR-012.md:318`: «Fecha: 2026-11-22».
- Es aplicación literal de 4.17 (`COR-012.md:232`): el error viene de la propuesta, no del corrector.
- **Propuesta**: corregir la fecha por COR, porque ADR-003 está «aceptado» (`invariantes.md:100`). Puede ir en la
  próxima corrección que se abra y no impide aprobar la arquitectura.

**F2-14 (menor). `pie-de-pagina.md` dice que todos sus datos están confirmados, pero la línea «Herramienta» sigue
marcada como pendiente.**
- `pie-de-pagina.md:12-13`: «Los datos de este archivo están confirmados y se conservan para ese momento».
- `pie-de-pagina.md:33`: «**Herramienta.** [POR CONFIRMAR si se incluye y con qué rol]». También `:4`, que explica
  que lo marcado `[POR CONFIRMAR]` no se publica.
- Es aplicación literal de 4.13 (`COR-012.md:179`). El efecto es acotado: ADR-005, punto 3, y `pie-de-pagina.md:34`
  ya omiten ese bloque mientras esté pendiente.
- **Propuesta**: en una corrección posterior, decir «Los datos confirmados de este archivo se conservan…», o algo
  equivalente que excluya la línea pendiente.

**Observación sin hallazgo.** El cuadro ASCII de `tokens.md` tiene bordes irregulares desde antes de COR-012: `:63-64`
miden 78 y `:74` es más larga que el resto. Es un detalle visual del boceto y ninguna regla lo exige.

---

## 8. Preparación para aprobar la arquitectura y empezar la Fase 3

- `arquitectura.md:3` sigue en «propuesta, pendiente de revisión de Jairo». La aprobación de Jairo está condicionada
  a aplicar y verificar COR-012 (`COR-012.md:319`; `invariantes.md:101`). Con este informe, la condición se cumple.
- ADR-001 a ADR-005 están aceptados. Los cambios a ADR-003 y ADR-005 posteriores a su aceptación están ratificados
  (`invariantes.md:99`) o pasan por COR-012.
- Interfaz: los 15 flujos y los 6 bocetos son coherentes con la arquitectura y los ADR. No queda ningún NC-INT abierto
  (`flujos.md:361`).
- La plantilla `docs/planes/_plantilla-plan-spec.md` existe (262 líneas) y es la que rigen `CLAUDE.md` y la skill
  `plan-modulo` (`plan-modulo/SKILL.md:11`).
- `[NEEDS CLARIFICATION]` que pasan a la preparación de los planes:
  - **NC-ARQ-1** (`arquitectura.md:782`, `:798`): se comprueba al preparar el plan 001.
  - **NC-ADR004-1** (`arquitectura.md:787`): queda abierto a propósito y lo decide el equipo después de la
    demostración.
- Lo que debe resolver la preparación del plan 001, según la arquitectura:
  - el constructor M23 (`arquitectura.md:684-688`);
  - la conciliación del andamiaje (`:267-270`);
  - NC-ARQ-1.
  No existen todavía `pyproject.toml` ni `data/fixtures/`.
- El cambio de COR-012 está sin commit sobre `adafb0d`. Los commits los hace Jairo.

---

## 9. Texto propuesto para la sección 9 de COR-012

> **Resultado: `verificada`** (verificador, 2026-11-22; informe `docs/informes/conformidad-fase-2-cierre-2026-11-22.md`).
> - Se aplicó al pie de la letra y solo en los 9 archivos de la sección 5. Cada bloque del diff sobre HEAD `adafb0d`
>   corresponde a un punto de la sección 4. Se conservaron los finales CRLF.
> - Las secciones 7 y 8 coinciden con el repositorio. Las 12 búsquedas de 4 bis dan lo esperado. La única excepción
>   es «brechas» en `SKILL.md:42`, que es el texto exigido por 4.11.
> - Desviaciones de forma aceptadas:
>   - el cuadro de `tokens.md` ya medía 77 caracteres y conserva ese ancho; la línea del colofón solo pierde un espacio
>     de relleno;
>   - las líneas en cursiva de `pie-de-pagina.md` siguen la forma que el archivo ya usaba.
> - Cierra F2-01 a F2-03 y F2-05 a F2-11. Se mantienen 89 de 89 requisitos con módulo, «Componente» igual a «Cubre»,
>   0 NC en los specs, `trazabilidad.md` con 191 líneas CRLF y la matriz intacta.
> - Hallazgos menores nuevos, que no invalidan la corrección:
>   - falta registrar en `invariantes.md` la aprobación del 22-nov-2026 (F2-12, sesión principal);
>   - la nota de ADR-003 lleva la fecha 2026-11-21 en lugar de 2026-11-22 (F2-13, error de 4.17);
>   - `pie-de-pagina.md:12-13` da por confirmados todos los datos, aunque «Herramienta» sigue pendiente (F2-14, error
>     de 4.13).

---

## 10. `[NEEDS CLARIFICATION]` abiertos

- **Specs**: ninguno.
- **Arquitectura**:
  - NC-ADR004-1 (despliegue posterior a la demostración), abierto a propósito como decisión del equipo;
  - NC-ARQ-1, para la preparación del plan 001.
- **Interfaz**: ninguno (`flujos.md:361`).
