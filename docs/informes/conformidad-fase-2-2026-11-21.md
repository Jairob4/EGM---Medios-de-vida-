# Informe de conformidad: Fase 2 (arquitectura e interfaz) y cierre del plan de corrección COR-011

**Fecha**: 2026-11-21
**Autor**: `verificador`. No participó en producir lo auditado.
**Lector**: Jairo. Es un documento interno.
**Alcance**: `docs/arquitectura/arquitectura.md` (estado «propuesta»), ADR-001 a ADR-005 (estado «aceptado»),
`docs/interfaz/flujos.md`, `docs/interfaz/tokens.css`, `docs/interfaz/bocetos/` (6 HTML, `boceto.css` y `boceto.js`),
la columna «Componente» de `docs/specs/trazabilidad.md`, COR-011 y su efecto en los specs.
**Modo**: solo lectura. No se corrigió nada. Solo se escribió en `docs/informes/`.

**Método**
- La cobertura se recontó con un programa. Ese programa extrajo las listas «Cubre» de `arquitectura.md` §6, M01 a M23,
  y las comparó con la columna «Componente» de `trazabilidad.md` y con los requisitos que definen los specs.
- Los contrastes de `tokens.css` se recalcularon con la fórmula de luminancia relativa de WCAG 2.2.
- El texto visible de los bocetos se extrajo, sin etiquetas, para revisar cifras, rótulos y trato de usted.
- `git diff` y `git status` se hicieron contra HEAD.
- La huella SHA-256 de la matriz se calculó en modo lectura.

**No aplica en esta fase**: `ruff`, `mypy` y `pytest --cov`. No hay código. `src/egm/`, `app/` y `tests/` solo
contienen `.gitkeep`.

---

## 1. Veredicto

- **La Fase 2 puede cerrarse cuando Jairo apruebe la arquitectura.** No hay hallazgos bloqueantes. Los 89 requisitos
  están asignados a algún módulo. Los 23 módulos cubren algún requisito. La columna «Componente» de
  `trazabilidad.md` coincide con las listas «Cubre» en los 89 requisitos.
- **Condición recomendada**: corregir los cuatro hallazgos mayores (F2-01 a F2-04) antes de empezar el plan 001, por
  el flujo de la regla 11. F2-01 afecta directamente a la historia US-001-4, que es del plan 001.
- **COR-011 queda `verificada`.**
  - Se aplicó al pie de la letra y solo sobre su lista cerrada.
  - Sus secciones 7 y 8 coinciden con el repositorio.
  - US-001-4.13 tiene cobertura en specs, trazabilidad, ADR-004 y arquitectura.
  - El efecto conjunto deja un hueco fuera de su lista: la interfaz no tiene el estado del rechazo por contenido
    descomprimido. Se registra como F2-01 y no invalida la corrección.

---

## 2. Resumen de cobertura

| Elemento | Recuento | Evidencia |
|---|---|---|
| Requisitos | 89: 19 NFR-000, 29 FR-001, 19 FR-002, 22 FR-003 | `000:74-92`, `001:403-431`, `002:235-253`, `003:233-254` |
| Requisitos con módulo | 89 de 89 | programa sobre `arquitectura.md:301-686` |
| Módulos con requisito | 23 de 23 (M01 a M23) | líneas «Cubre» de `arquitectura.md:301` a `:686` |
| Filas de `trazabilidad.md` iguales a «Cubre» | 89 de 89 | `trazabilidad.md:7-95` |
| ADR que citan los requisitos que los motivan | 5 de 5 | `ADR-001:4-6`, `ADR-002:4-5`, `ADR-003:4-6`, `ADR-004:5-6`, `ADR-005:4-5` |
| Flujos por historia | 15 de 15 (F-001-1 a 5, F-002-1 a 5, F-003-1 a 5) | `flujos.md:74-299` |
| Requisitos sin componente | 0 | — |
| Componentes sin requisito | 0 | — |

**Huecos.** No hay requisitos sin componente. Hay un hueco de interfaz: US-001-4.13 no tiene flujo ni estado (F2-01).
Las columnas «Tarea» y «Prueba» siguen vacías, como corresponde a esta fase.

**Excesos.**
- Ningún módulo queda sin requisito.
- El aviso a los 43 minutos (E7, `flujos.md:62`) no es un exceso: lo exige WCAG 2.2.1, dentro de NFR-000-04, y está
  justificado en `flujos.md:324`.
- Los puntos de extensión PE-1 a PE-7 (`arquitectura.md:725-744`) están documentados, sin implementar.
- Las carpetas `src/egm/analisis/` y `src/egm/validacion/` del andamiaje inicial no corresponden a ningún módulo de la
  lista cerrada (F2-10).

---

## 3. Coherencia entre ADR, arquitectura e invariantes del 21-nov-2026

| Tema | ADR | Arquitectura | Invariantes | Resultado |
|---|---|---|---|---|
| Stack: FastAPI + Jinja2 + htmx, HTML y CSS propios, Uvicorn local, Python 3.13 | ADR-003:60 | §3 `:85-88` | `:82` | Coherente |
| Sesión: 45 minutos fijos | ADR-003:80-82 (punto 5) | M15 `:568`; §5.2 `:252` | `:60` | Coherente |
| Sesión: 10 s de gracia al recargar; cerrar la pestaña sí la termina | ADR-003:104-111 (punto 9) | M15 `:563-565`, `:569`; §5.2 `:251` | `:84` | Coherente |
| Sesión: las cuatro formas de terminar | ADR-003:16-18 | §5.2 `:250-253`, cuatro filas | NFR-000-17 (`000:87`) | Coherente |
| Límite de 15 728 640 bytes | ADR-003:19-20 | §5 `:175`; etapa 1 `:203`; M02 `:308` | `:49` | Coherente |
| Límite de 268 435 456 bytes, motivo `"contenido"` | ADR-004:61-65 | etapa 1 `:204-205`; M01 `:298`; M02 `:309`, `:313-315` | `:86` | Coherente. La vista V1 de §8 no lo nombra (F2-01) |
| Exportación: SVG en M20 y PNG en M19 | ADR-003:93-97 | M19 `:622-635`; M20 `:637-647` | `:83`, `:95` | Coherente |
| Colofón: solo «Datos» y 3ie visibles; nueve bloques apagados | ADR-005:7-12, `:45-63` | M21 `:649-666`; M22 `:668-675`; §8 `:762` | `:87`, `:92` | Coherente. Desfasados: `flujos.md:308`, `colofon.html:27` y la skill (F2-02, F2-03) |
| Definiciones: texto UTF-8 junto a la instalación, leído al arrancar | ADR-004:53-60 | M12 `:523-534`; M22 | `:85` | Coherente |
| Núcleo sin web | ADR-003:116 | P1 `:20`; §4.1 reglas 1 a 4 `:124-131`; M13 | NFR-000-14 | Coherente. No hay código que comprobar |
| Vista de red y módulo no supervisado | — | §7 `:725-744` | `:10` | Documentados y no implementados. PE-2 «no se crea en el código» (`:734`) |

---

## 4. Flujos e historias

- **Un flujo por historia**: 15 de 15.
- **Textos conformes a los specs.**
  - «Actualizar vista» y «Restablecer» aparecen una sola vez cada uno en `mapa.html` y en `tablero.html`
    (FR-002-19).
  - «Sin nivel» está en la leyenda, con 0 estudios del mapa en la v4 (FR-002-12, H-59): `flujos.md:201-205`.
  - Sin filtros, «ningún estudio registrado» (FR-002-04). Con filtros, «ningún estudio registrado con los filtros
    activos», sin «brecha» (FR-002-14, FR-003-15).
  - «n de N»: `flujos.md:209-215`, `tablero.html:163-169`.
  - Solo hay conteos. Los bocetos no tienen ningún «%» de texto: los «%» de `boceto.css` son medidas de CSS.
  - El título es «Evidencias sobre medios de vida» en los seis bocetos.
  - «Ningún estudio cumple estos filtros» (FR-003-16).
- **Datos de los bocetos y de los flujos**, contrastados con el apéndice A (`contrato-datos.md:368-410`):
  - 27 documentos, 7 empíricos, 1 en el mapa y 6 pendientes (N.º 10, 11, 13, 15, 16 y 24).
  - 6 celdas en 1 y 42 en 0, de 48.
  - Tipos de documento 9/7/4/3/3/1. Fuentes 6/1/0/20. Metodología 6 Conceptual/teórica, 1 Evaluación de impacto y 20
    sin diligenciar.
  - Años de 1992 a 2026. Enfoque: N.º 2 y 7 «Sin clasificar».
  - Todo coincide.
  - «Stark et al. (2026)» está verificado en `docs/fuentes/estado_proyecto_2026-10-31.md:29` y en `referencia-v4.md:59`.
  - Los textos que el apéndice no trae van como marcadores entre corchetes (`flujos.md:350-352`).

---

## 5. Bocetos y `tokens.css`

**Bocetos.**
- **Datos**: ninguno abre `data/raw/`. Ninguno carga recursos externos: el único `@import` es `../tokens.css`
  (`boceto.css:3`).
- **Contenido prohibido**: 0 coincidencias de cifras de la lámina 7, de la tabla 3, de «Magdalena» o «unimagdalena»,
  de «[POR CONFIRMAR]», de GIOE y de los nombres del equipo.
- **Colofón**: «Datos» y la referencia a 3ie, y nada más, en los seis bocetos.
- **Textos**: en español, de usted. Ninguna pregunta al equipo y nada de tuteo. Tampoco aparecen «error de contrato»,
  «validación» ni «fixture».
- **Observación de estilo, sin hallazgo**:
  - «PNG», «SVG» y «Excel» aparecen en los botones de descarga (`mapa.html`). Son siglas técnicas, pero llevan su
    explicación.
  - «15 MB (15 728 640 bytes)» (`carga.html`) redondea 15 MiB. La cifra exacta en bytes evita el equívoco.

**`tokens.css`.** Se recalcularon los 27 contrastes declarados (`tokens.css:144-172`). Los 27 coinciden con lo
declarado, a dos decimales.
- **Texto ≥ 4,5:1** en los dos modos. El mínimo es `--cabecera` sobre `--cajon` en oscuro, con 4,74.
- **Contorno del cajón vacío ≥ 3:1**: 3,20 en claro y 4,10 en oscuro.
- **Rellenos de nivel por debajo de 3:1**: nivel 3 (2,37 y 2,27) y nivel 1 frente al 2 (2,24). Quedan cubiertos por un
  borde ≥ 5,65:1, el número escrito y la leyenda. Es conforme con WCAG 1.4.11 y con SC-000-10.
- **A qué requisito corresponde**: el contraste corresponde a NFR-000-04 (WCAG 2.2 AA), no a NFR-000-03, que trata
  del lenguaje. `tokens.css:5-7` lo cita bien. Nada en `tokens.css` contradice NFR-000-03.

---

## 6. COR-011: auditoría única del plan de corrección

| Comprobación | Resultado | Evidencia |
|---|---|---|
| 5.1 a 5.7 aplicados al pie de la letra | Sí | `git diff`: `000:92`, `:116`, `:120`; `001:234-237`, `:396`; `contrato:32`, `:342` |
| 5.8 en trazabilidad, con CRLF | Sí. Solo cambian `:121` y `:150` de la segunda tabla. En la primera solo cambia la columna «Componente», que es tarea de la fase y no de COR-011. 191 líneas, 191 CRLF y ningún CR suelto | comparación por columnas contra HEAD |
| 5.9 en ADR-004 | Sí | `ADR-004:61-65`, `:88`, `:92-93`. No queda la viñeta «pendiente» |
| 5.10 en arquitectura | Sí, los nueve cambios | `:181`, `:204-205`, `:298`, `:305`, `:309`, `:313-315`, `:682-683`, `:776`, `:789` |
| 5.11 en invariantes | Sí, igual al texto de la propuesta | `invariantes.md:86` |
| Solo sobre su lista | Sí. ADR-003, specs 002 y 003, `docs/interfaz/`, `data/raw/` y `docs/fuentes/` sin cambios de COR-011 | `git status`, `git diff --stat` |
| `268 435 456` dentro de `docs/specs/` | Solo en NFR-000-19 (`000:92`) | búsqueda |
| «pendiente de aplicar en el spec mediante COR-011» | 0 coincidencias fuera de `COR-011.md`, donde se cita como texto anterior | búsqueda en `docs/` |
| US-001-4.13 con cobertura | Sí: escenario `001:234-237`; `trazabilidad.md:121`, `:150`; `ADR-004:65`, `:88`, `:93`. No en la interfaz (F2-01) | búsqueda |
| Sección 7 frente al repositorio | Coincide | — |
| Sección 8 frente al repositorio | Coincide, incluida la nota sobre las 3 coincidencias en ADR-004 (`:65`, `:88`, `:93`) | — |
| Lista cerrada de errores de contrato | Sin cambios. «contenido» es un rechazo antes de leer, no un error de contrato | `000:92`; M01 `:298` |

Detalles menores del resultado:
- El texto de 5.10 para M23 quitó una «y». F2-08.
- 5.10 no incluyó la vista V1 de §8 (`:751`). Parte de F2-01.
- El NC sobre la biblioteca de lectura solo consta en `COR-011.md:79` y `:175`. F2-06.

---

## 7. Specs

- `[NEEDS CLARIFICATION]` abiertos en `docs/specs/`: **0**. Las dos coincidencias están en
  `_plantilla/spec-template.md:88-89`, que es la plantilla.
- **ID únicos**: ningún ID se define dos veces. No hay huecos de numeración en FR, NFR, SC ni escenarios. No hay
  referencias colgantes en specs, trazabilidad, arquitectura, ADR, flujos ni bocetos.
- **Fuentes**: los 89 requisitos tienen `[Fuente: …]`.

| Recuento | Valor |
|---|---|
| Requisitos | 89 (NFR-000: 19; FR-001: 29; FR-002: 19; FR-003: 22) |
| Historias | 15 (001: 5; 002: 5; 003: 5) |
| Escenarios | **122** (001: 62; 002: 30; 003: 30). Son 121 al cierre de la Fase 1 más US-001-4.13 |
| Criterios de éxito | 35 (SC-000: 19; SC-001: 5; SC-002: 5; SC-003: 6) |

---

## 8. Reglas de `CLAUDE.md` e integridad

- **Regla 3: datos no verificados.**
  - No se afirma ningún dato sin fuente.
  - Lo que el apéndice A no trae va como marcador.
  - NC-ADR004-1 sigue abierto a propósito y marcado (`ADR-004:68-76`).
- **Regla 7: lámina 7.** Ninguna de sus cifras aparece en arquitectura, ADR, flujos ni bocetos. Las cifras de la
  interfaz son las de la v4 (0 y 1 en las celdas).
- **Regla 9: tabla 3.**
  - La discrepancia, es decir, la columna M y el criterio `"Sí*"`, no se describe en ningún entregable de la Fase 2.
  - En `docs/specs/`, la tabla 3 aparece solo en el contrato §7, como no comparable (`contrato-datos.md:283-284`).
  - En la arquitectura aparece solo como «no comparable, no se lee» (`ADR-002:11`, `:62`; `arquitectura.md:446`,
    `:492`, `:764`). Son documentos internos (`arquitectura.md:12`).
  - `flujos.md:13` la nombra, para decir que no se menciona, en un documento sin marca de interno (F2-11).
  - Los bocetos no la mencionan.
  - La descripción completa de la discrepancia sigue solo en los registros internos: `interno-tabla3-hoja-egm.md`,
    `hallazgos-matriz-para-equipo.md`, la skill `contrato-matriz:64`, `invariantes.md` y `docs/fuentes/`.
- **Regla 11**: ver F2-04 y la sección 10.
- **Huella**: SHA-256 de `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` =
  `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`. Es igual a la de `contrato-datos.md:374`.
- **`data/raw/` y `docs/fuentes/`**: sin cambios. `git status` y `git diff` están vacíos para ambas rutas.
- **Estado de git**:
  - HEAD es **997e932**, no b954d30. La Fase 1 ya quedó en un commit.
  - La Fase 2 y COR-011 siguen sin commit sobre 997e932.
  - Además, `prompts/PROMPT_FASE_2_arquitectura.md` está modificado y `prompts/RETOMAR_2026-11-21.md` borrado. Esto
    último consta en `invariantes.md:79`.

---

## 9. Hallazgos

### Mayores

**F2-01. El rechazo por contenido descomprimido (US-001-4.13) no tiene estado en la interfaz.**
- La tabla de estados de `flujos.md:54-56` tiene E2 (rechazo por tipo) y E3 (rechazo por tamaño), pero no tiene un
  estado para el rechazo por contenido descomprimido.
- F-001-4 dice «Cubre: US-001-4.1 a 4.12» (`flujos.md:87`).
- `carga.html:11` también se limita a 4.1 a 4.12, y no tiene ninguna sección para ese caso.
- El mensaje de NFR-000-19, «El contenido del libro es demasiado grande para abrirlo», da 0 coincidencias en
  `docs/interfaz/`.
- En `arquitectura.md:751`, la vista V1 sigue diciendo «Rechazo por tipo o tamaño».
- La causa es que COR-011 excluyó `docs/interfaz/` de su lista y que 5.10 no tocó §8.
- Sin el estado, el plan 001 no tendría un flujo de interfaz para un escenario de US-001-4.
- **Propuesta**: una corrección, por el flujo de la regla 11, que agregue:
  - en `flujos.md`, el estado del rechazo por contenido, con y sin matriz previa, y US-001-4.13 en el «Cubre» de
    F-001-4;
  - en `carga.html`, la sección correspondiente;
  - en `arquitectura.md` §8, la palabra «contenido» en V1.

**F2-02. `flujos.md` mantiene abiertos NC-INT-1 a NC-INT-4, que Jairo ya decidió, y su texto contradice esas
decisiones.**
- `flujos.md:357-375` conserva los cuatro como `[NEEDS CLARIFICATION]`, con recomendaciones previas a las decisiones.
- NC-INT-2 recomienda tratar como «Sin nivel» a los empíricos pendientes (`:362-367`). Jairo decidió lo contrario
  (`invariantes.md:93`; `arquitectura.md:391-394`).
- NC-INT-1 afirma que ADR-005 deja encendidos «Proyecto», «Semillero» y «Equipo» (`:357-361`). ADR-005 ya los apaga
  (`ADR-005:7-12`, `:45-63`).
- NC-INT-4 afirma que M19 no tiene la conversión a PNG (`:371-375`). M19 ya la tiene (`arquitectura.md:622-635`).
- §6 todavía habla de «los seis bloques institucionales» (`:308`).
- La nota de `colofon.html:27` remite a «la instrucción de esta tarea; ver NC-INT-1».
- `arquitectura.md:791` da por decididos los cuatro NC. Los dos entregables se contradicen.
- **Propuesta**: una corrección que registre en `flujos.md` §9 las decisiones del 21-nov-2026 y actualice §6 y la nota
  del boceto.

**F2-03. La skill `sistema-diseno-egm` contradice ADR-005, NC-INT-3 y NFR-000-12 (contradicción conocida:
confirmada).**
- `references/tokens.md:77`: «Colofón: proyecto, grupo, semillero, universidad, datos, créditos».
- `references/pie-de-pagina.md:36`: «Se publican los logos de Minciencias y de la Universidad del Magdalena».
- `references/tokens.md:60`, en la cabecera del boceto ASCII:
  - dice «Mapa de evidencias y brechas», contra NC-INT-3 (`invariantes.md:94`);
  - dice «Matriz v4, 27 documentos, leída hoy», que deduce una versión, contra NFR-000-12 (`000:85`).
- `SKILL.md:54` remite a esa referencia.
- **Clasificación**: guía desactualizada respecto de decisiones posteriores y fechadas.
  - No es un defecto de los specs, que según la decisión del 21-nov-2026 no cambian.
  - Tampoco es un defecto de la arquitectura.
  - Prevalecen ADR-005 y las invariantes (`:87`, `:92`).
  - El riesgo es real: el `disenador-front` y el `implementador` leen esa skill. ADR-005 punto 1 (`:43-44`) toma de
    `pie-de-pagina.md` el orden y el texto de los bloques, pero no su visibilidad.
- **Propuesta**: una corrección de la skill, como se hizo con `contrato-matriz` en COR-006, que:
  - indique que los bloques institucionales vienen apagados por defecto (ADR-005);
  - cambie el título del boceto ASCII;
  - quite «v4» y «hoy» de la cabecera de ejemplo.

**F2-04. Ediciones de ADR después de quedar «aceptados», sin propuesta de corrección (regla 11).**
- Las invariantes registran primero «ADR-001 a ADR-005 aceptados» (`:82`). Después registran las decisiones de
  interfaz, una de las cuales «modifica ADR-005» (`:92`).
- ADR-005 recibió una nota de revisión y cambió su punto 2 y su tabla (`ADR-005:7-12`, `:45-63`).
- ADR-003 también cambió su contenido por decisiones de la interfaz, sin nota de revisión: punto 6 (`:85-90`, que cita
  `flujos.md` §7) y punto 7 (`:97`, NC-INT-4).
- Las dos ediciones se apoyan en decisiones fechadas de Jairo. La autorización expresa que se conoce cubre el
  borrador de `arquitectura.md` (M08, M09, M19 y M20), no los ADR aceptados.
- ADR-005 lleva nota y ADR-003 no: el criterio es desigual.
- Como los ADR no tienen commit, no se puede reconstruir qué cambió exactamente después de la aceptación.
- Ver la recomendación en la sección 10.

### Menores

**F2-05. La entrada de la arquitectura remite a un tramo del prompt que no contiene las decisiones.**
- `arquitectura.md:5-6` cita las decisiones del 21-nov-2026 en `prompts/PROMPT_FASE_2_arquitectura.md:10-21`.
- Ese tramo solo tiene el marcador sin llenar «[Stack web…]» (`:11`, con un espacio al final) y las tareas.
- Las decisiones están en `invariantes.md:75-96`.

**F2-06. El NC sobre la biblioteca de lectura no consta en la arquitectura.**
- El NC pregunta qué hace la biblioteca ante una parte que se descomprime a más de lo declarado.
- Solo está en `COR-011.md:79` y `:175`.
- `arquitectura.md` §9 (`:768-777`) y §10 (`:779-791`) no lo recogen, y §10 dice «Ninguno queda pendiente».
- Puede perderse al preparar el plan 001.

**F2-07. ADR-003 verifica NFR-000-19 solo con el primer límite.**
- `ADR-003:130`: «SC-000-19 con archivos de 15 728 640 bytes y de un byte más».
- No nombra el límite de contenido descomprimido, que sí está en `ADR-004:92-93`.
- COR-011 excluyó ADR-003 a propósito.

**F2-08. Texto ambiguo en M23 tras COR-011.**
- `arquitectura.md:682-683` dice «archivos dañados, de otro tipo de tamaño exacto y de contenido descomprimido
  declarado exacto».
- El texto de 5.10 quitó la «y» entre «de otro tipo» y «de tamaño exacto».
- Se aplicó al pie de la letra.

**F2-09. El boceto del tablero con filtro omite la cifra de empíricos pendientes.**
- `tablero.html:77` la muestra sin filtros (FR-003-21, obligatoria).
- El estado con filtro, `tablero.html:165-169`, tiene cinco cifras y no tiene esa.
- `flujos.md` (F-003-3, `:272-280`) no dice cómo se presenta esa cifra con «n de N».

**F2-10. El andamiaje de `src/egm/` no coincide con la lista cerrada de módulos.**
- Hay `src/egm/analisis/`, `lectura/`, `modelo/` y `validacion/`, con `.gitkeep`.
- La arquitectura define módulos `egm.modelo`, `egm.lectura` y once más, y no tiene ni `analisis` ni `validacion`
  (`arquitectura.md:261-269`, `:270-545`).
- El plan 001 debe conciliarlo. Si no, crearía paquetes fuera de la lista cerrada.

**F2-11. `flujos.md` nombra la tabla 3 y no está marcado como interno.**
- `flujos.md:13`: «Ningún flujo, boceto ni texto menciona la tabla 3 de la hoja EGM».
- `arquitectura.md:12` se declara interno; `flujos.md` no tiene esa marca.
- Si los flujos se mostraran al equipo, esa línea contravendría la regla 9.
- **Propuesta**: marcar `flujos.md` como interno o quitar la frase, en la misma corrección de F2-02.

---

## 10. Pregunta de proceso: ¿se ajustan a la regla 11 los cambios de hoy a los ADR aceptados?

**Respuesta: no del todo.**
- La regla 11 de `CLAUDE.md` exige analista-impacto → aprobación de Jairo → corrector para toda corrección de la
  arquitectura.
- Los ADR-003 y ADR-005 cambiaron de contenido después de quedar «aceptados» (F2-04). No hay una propuesta de
  corrección que los recoja.
- Atenuantes:
  - Cada cambio se apoya en una decisión fechada de Jairo (`invariantes.md:91-96`).
  - Ocurrió dentro de la misma fase, que aún no está cerrada.
  - ADR-005 lo declara en una nota de revisión.
- Los cierres de NC anotados en los ADR (NC-ADR003-1, NC-ADR003-2, NC-ADR004-2, NC-ADR004-3 y NC-ADR005-1) son
  coherentes con las invariantes. Los que se hicieron al aceptar los ADR no son correcciones.

**Recomendación a partir de ahora.**
1. **Al aprobar la Fase 2**, Jairo ratifica de forma expresa las ediciones del 21-nov-2026 a ADR-003, puntos 6 y 7, y
   a ADR-005, nota de revisión, punto 2 y tabla. La sesión principal lo anota en las invariantes. Con eso, F2-04
   queda cerrado sin rehacer nada.
2. **Desde la aprobación**, un ADR «aceptado» solo cambia por una propuesta COR-NNN.
   - Si el cambio altera la decisión, se prefiere un ADR nuevo que lo reemplace.
   - Una nota de revisión solo se admite para registrar lo que una COR aprobada aplica, y debe citar esa COR.
3. **Mientras un documento esté en estado «propuesta»**, como hoy `arquitectura.md`, su autor puede ajustarlo con la
   autorización expresa y fechada de Jairo, como ocurrió con M08, M09, M19 y M20. Al aprobarse, rige el punto 2.

---

## 11. Texto propuesto para la sección 9 de COR-011

> **Resultado: `verificada`** (verificador, 2026-11-21; informe `docs/informes/conformidad-fase-2-2026-11-21.md`).
>
> - **Aplicación literal y solo sobre la lista.**
>   - 5.1 a 5.11 están en el repositorio tal como los fija la propuesta: `000:92`, `:116`, `:120`; `001:234-237`,
>     `:396`; `contrato:32`, `:342`; `trazabilidad:121`, `:150`; ADR-004 en `:61-65`, `:88`, `:92-93`;
>     `arquitectura.md` en `:181`, `:204-205`, `:298`, `:305`, `:309`, `:313-315`, `:682-683`, `:776`, `:789`;
>     `invariantes.md:86`.
>   - No se tocó ADR-003, los specs 002 y 003, `docs/interfaz/`, `data/raw/` ni `docs/fuentes/`.
> - **Secciones 7 y 8**: coinciden con el repositorio.
> - **Búsquedas.**
>   - `268 435 456` en `docs/specs/`: solo NFR-000-19.
>   - «demasiado grande para abrirlo»: 2 coincidencias en specs.
>   - «pendiente de aplicar en el spec mediante COR-011»: 0 coincidencias fuera de esta propuesta.
>   - `trazabilidad.md`: 191 líneas, 191 CRLF y ningún CR suelto.
> - **Cobertura**: US-001-4.13 está en el spec, en trazabilidad (NFR-000-19 y FR-001-29), en ADR-004 y en M02.
> - **Integridad**: la lista cerrada de errores de contrato no cambia. La matriz está intacta: SHA-256
>   `7E1714DE…1952C3A1`. `docs/fuentes/` no tiene cambios.
> - **Efecto conjunto**: queda un hueco fuera de la lista de esta corrección. La interfaz (`flujos.md`, `carga.html`)
>   y la vista V1 de `arquitectura.md` §8 no tienen el estado del rechazo por contenido descomprimido. Es el hallazgo
>   F2-01 de la Fase 2 y se atiende con una corrección nueva.
> - **Menores**:
>   - el texto de 5.10 para M23 perdió una «y» (F2-08);
>   - el NC sobre la biblioteca de lectura solo consta aquí y debe pasar a la preparación del plan 001 (F2-06).

---

## 12. `[NEEDS CLARIFICATION]` abiertos

- **En los specs**: ninguno.
- **En la arquitectura**: NC-ADR004-1, el despliegue posterior a la demostración (`ADR-004:68-76`). Es una decisión
  futura del equipo y queda abierto a propósito.
- **En `flujos.md`**: NC-INT-1 a NC-INT-4 aparecen como abiertos, pero ya están decididos (F2-02).
- **Para la preparación del plan 001**: qué hace la biblioteca de lectura ante una parte que se descomprime a más de lo
  declarado (`COR-011.md:79`; F2-06). El spec ya trata ese caso como un archivo dañado.
