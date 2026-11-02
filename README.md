# EGM · Medios de vida

Aplicación web de **solo lectura** que lee la matriz bibliográfica del estado del arte del proyecto
«Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los medios de vida
de la población víctima en Colombia» y presenta:

1. el mapa de evidencias y brechas (EGM) interactivo;
2. un tablero analítico con conclusiones calculadas, cada una trazable hasta las filas de la matriz.

Está pensada para procesar las versiones presentes y futuras de esa matriz sin reconstruirse: toma las
categorías del propio archivo. La matriz es del equipo de investigación; la herramienta nunca la modifica.

Semillero Desarrollo Rural y Economía Solidaria · Grupo GIOE · Universidad del Magdalena.

## Estado

**Fase de specs.** Todavía no hay código de la aplicación. Los specs están en versión v0, con el alcance
por acordar con la investigadora principal.

## Mapa de carpetas

| Ruta | Contenido |
|---|---|
| `docs/fuentes/` | Fuentes de verdad, solo lectura |
| `docs/specs/` | Contrato de datos, visión y alcance, specs por feature y trazabilidad |
| `docs/arquitectura/` | Arquitectura y ADR (fase siguiente) |
| `docs/interfaz/` | Flujos y bocetos (fase siguiente) |
| `docs/planes/` | Plan por módulo (fase posterior) |
| `docs/informes/` | Informes de fase y de conformidad |
| `data/raw/` | Matriz vigente, solo lectura |
| `data/fixtures/` | Matrices sintéticas para pruebas |
| `src/egm/` | Núcleo de la herramienta; sus subcarpetas son provisionales hasta que las confirme la arquitectura |
| `app/` | Capa web |
| `tests/` | Pruebas unitarias, de integración y de propiedades |

Las reglas del proyecto y el flujo de trabajo por fases están en [CLAUDE.md](CLAUDE.md).
