---
name: calidad-python
description: Estándares de código y pruebas Python del proyecto EGM (estructura del núcleo src/egm, tipado, lint, pytest, pruebas de propiedades, cobertura, lectura segura del xlsx). Usar al escribir o revisar cualquier código Python del repositorio.
---

# Calidad Python

## Principios de diseño

- **Núcleo puro** (`src/egm/`): sin imports de la capa web, sin estado global, sin E/S fuera de
  `lectura/`. El análisis recibe estructuras del dominio y devuelve estructuras del dominio.
- La capa web (`app/`) solo orquesta: llama al núcleo y presenta. Ningún cálculo de conteos en plantillas
  o rutas.
- Las categorías (intervenciones, dimensiones, niveles) se leen de la matriz; prohibido codificar las
  listas como constantes del dominio (sí se permiten en fixtures).
- Cada resultado numérico viaja con su **conjunto de N.º de filas** que lo producen (trazabilidad).
- Errores de contrato → excepción tipada con hoja, celda y mensaje en español. Advertencias de
  validación → lista de objetos, nunca `print`.

## Herramientas

| Aspecto | Herramienta | Regla |
|---|---|---|
| Versión | Python ≥ 3.11 | [NEEDS CLARIFICATION: versión exacta del entorno de Jairo] |
| Proyecto | `pyproject.toml` | dependencias fijadas con rango compatible |
| Lint y formato | `ruff` | sin errores |
| Tipado | `mypy --strict` en `src/egm/` | sin errores |
| Pruebas | `pytest` | todas en verde |
| Propiedades | `hypothesis` | invariantes de conteo del contrato |
| Cobertura | `pytest-cov` | ≥ 90 % de líneas en `src/egm/` |

## Lectura del xlsx

- `openpyxl.load_workbook(ruta, read_only=True)` para datos; una segunda carga sin `data_only` solo si
  se necesitan fórmulas o validaciones. Nunca llamar a `save()` sobre un libro de `data/raw/`.
- Distinguir celda vacía (`None`) de 0. Un valor en caché `None` en la hoja `EGM` es «sin calcular»,
  no 0.

## Pruebas

- Estructura: `tests/unit/`, `tests/integracion/`, `tests/propiedades/`.
- Docstring de cada prueba: ID del escenario o criterio que verifica (`US-001-1.2`, `SC-003-01`).
- Fixtures en `data/fixtures/`, generados por un script versionado (`tests/fixtures_builder.py`) para
  poder reconstruirlos; uno por caso borde del contrato.
- Esperados escritos a mano a partir del contrato o de `referencia-v4.md`; nunca copiados de la salida
  del código bajo prueba.
- Prueba de integración obligatoria contra la matriz real de `data/raw/` en modo lectura, con los valores
  de `referencia-v4.md` (o los re-extraídos de la versión vigente).
