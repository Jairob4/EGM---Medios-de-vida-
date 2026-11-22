# Kit de arranque para Claude Code — EGM medios de vida

## Contenido

```
CLAUDE.md                         reglas permanentes del proyecto
.claude/settings.json             bloquea escritura en data/raw/ y docs/fuentes/
.claude/agents/                   arquitecto, implementador, disenador-front, verificador
.claude/skills/
  contrato-matriz/                contrato con el xlsx + referencia verificada de la v4
  especificacion-srs/             cómo llenar specs con su plantilla
  trazabilidad/                   matriz fuente → requisito → componente → tarea → prueba
  plan-modulo/                    cómo escribir y ejecutar un plan.md
  calidad-python/                 estándares de código y pruebas
  sistema-diseno-egm/             sistema de diseño «Fichero» + tokens + colofón
docs/specs/_plantilla/            su spec-template.md, sin cambios
docs/planes/_plantilla-plan-spec.md   plantilla de plan por spec (la que rige la Fase 3)
docs/arquitectura/adr/_plantilla-adr.md
prompts/                          un prompt por fase (1 specs, 2 arquitectura, 3 planes; 4 de referencia)
```

## Instalación

1. Cree el repositorio y copie el contenido de esta carpeta en su raíz.
2. Fuentes (el prompt de la fase 1 las busca con estos nombres):

| Fuente | Destino | Estado |
|---|---|---|
| Matriz v4 | `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` | ya incluida |
| Presentación del equipo (texto extraído) | `docs/fuentes/presentacion_equipo_2026-10_texto.md` | ya incluida |
| Presentación original | `docs/fuentes/presentacion_equipo_2026-10.pptx` | opcional, cópiela usted |
| Propuesta, versión general | `docs/fuentes/propuesta_herramienta_general.pdf` | ya incluida |
| Propuesta, versión técnica | `docs/fuentes/propuesta_herramienta_tecnica.pdf` | opcional, cópiela usted |
| Estado del proyecto | `docs/fuentes/estado_proyecto_2026-10-31.md` | ya incluido |

   **No** suba `Jairo Blanco.pdf` (formato de vinculación): contiene cédula, celular y dirección, y lo
   que el colofón necesita de él ya está extraído en la skill de diseño.
3. Abra Claude Code en la raíz y verifique con `/agents` y `/permissions` que se cargaron los subagentes
   y las reglas de `settings.json`. Las skills se descubren al iniciar la sesión; si agrega una con la
   sesión abierta, reinicie.
4. Pegue `prompts/PROMPT_FASE_1_specs.md`.

## Compuertas

Fase 1 → usted revisa specs y responde los `[NEEDS CLARIFICATION]` → Fase 2 → revisa arquitectura y
bocetos → Fase 3 → revisa planes → Fase 4, un plan a la vez.

## Pendientes suyos que el kit deja marcados

- Colofón: si su nombre aparece y con qué rol (`pie-de-pagina.md`), y el permiso de uso de los logos institucionales. El código Minciencias, el correo de contacto, los logos y la omisión de la categoría y de la línea de investigación ya están decididos (NFR-000-11).
- Stack web (lo propone el ADR-003). Despliegue (ADR-004), que el equipo decide después de la demostración.

Ya decididos: umbral de porcentajes ($n_{min} = 100$, `contrato-datos.md` §8); métrica de avance por fila (no se incluye); tabla 3 de la hoja EGM (regla 9 de `CLAUDE.md`); versión de Python (la elige Claude Code para el entorno del proyecto).
