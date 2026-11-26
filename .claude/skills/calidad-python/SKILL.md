---
name: calidad-python
description: Estándares de código y pruebas Python del proyecto EGM (estructura del núcleo src/egm, tipado, lint, pytest, pruebas de propiedades, cobertura, lectura segura del xlsx). Usar al escribir o revisar cualquier código Python del repositorio.
---

# Calidad Python

## Principios de diseño

- **Núcleo puro** (`src/egm/`): sin imports de la capa web, sin estado global y sin E/S: recibe la
  matriz como bytes en memoria (`egm.procesamiento.procesar`) y solo `egm.libro` usa la biblioteca de
  lectura del libro (arquitectura §4.1, regla 3; ADR-004, punto 1). El análisis recibe estructuras del
  dominio y devuelve estructuras del dominio.
- La capa web (`app/`) solo orquesta: llama al núcleo y presenta. Ningún cálculo de conteos en plantillas
  o rutas.
- Las categorías (intervenciones, dimensiones, niveles) se leen de la matriz; prohibido codificar las
  listas como constantes del dominio (sí se permiten en fixtures).
- Cada resultado numérico viaja con su **conjunto de N.º de filas** que lo producen (trazabilidad).
- Errores de contrato → valor `FalloContrato` con sus `ErrorContrato` (código, lo esperado y lo
  encontrado), que `egm.esquema.descubrir` y `egm.procesamiento.procesar` devuelven como resultado; el
  mensaje en español lo arma `egm.textos`, sin nombre de archivo ni filas de datos (arquitectura §6.1,
  M01, M04, M10 y M13). Advertencias de validación → lista de objetos `Advertencia`, nunca `print`.

## Herramientas

| Aspecto | Herramienta | Regla |
|---|---|---|
| Versión | Python ≥ 3.11 | La elige Claude Code para el entorno aislado del proyecto y se registra en el resumen de la fase (decisión de Jairo, 2-nov-2026; `000-vision-alcance.md`, «Notas sobre las fuentes») |
| Proyecto | `pyproject.toml` | dependencias fijadas con rango compatible |
| Lint y formato | `ruff` | sin errores |
| Tipado | `mypy --strict` en `src/egm/` | sin errores |
| Pruebas | `pytest` | todas en verde |
| Propiedades | `hypothesis` | invariantes de conteo del contrato |
| Cobertura | `pytest-cov` | ≥ 90 % de líneas en `src/egm/` |

## Lectura del xlsx

- `openpyxl.load_workbook(io.BytesIO(contenido))` en modo normal, solo en `egm.libro` y sobre los bytes en memoria, nunca sobre una ruta del disco (ADR-004, punto 1; arquitectura M03): una carga con fórmulas (`data_only=False`) y otra con los valores guardados (`data_only=True`). No se usa `read_only=True`, porque en ese modo la hoja no entrega las validaciones de datos (ADR-001, L1; plan 001, R-5; COR-018). Nunca llamar a `save()` sobre un libro de `data/raw/`.
- Distinguir celda vacía (`None`) de 0. Un valor en caché `None` en la hoja `EGM` es «sin calcular»,
  no 0.

## Pruebas

- Estructura: `tests/constructor.py` (M23), `tests/unit/`, `tests/integracion/`, `tests/propiedades/` y
  `tests/navegador/` (mapa del repositorio de `CLAUDE.md`; plan 001, «Estructura del proyecto»).
- Marcas de `pytest` (las configura T-001-03 del plan 001): `raw` en toda prueba que abra `data/raw/`, de
  cualquier plan, aunque su plan no la nombre; `navegador` en toda prueba de `tests/navegador/`.
- Docstring de cada prueba: ID del escenario o criterio que verifica (`US-001-1.2`, `SC-003-01`).
- Fixtures en `data/fixtures/`, generados por un script versionado (`tests/constructor.py`, módulo M23 `tests.constructor` de la arquitectura) para
  poder reconstruirlos; uno por caso borde del contrato.
- Esperados escritos a mano a partir del contrato o de `referencia-v4.md`; nunca copiados de la salida
  del código bajo prueba.
- Prueba de integración obligatoria contra la matriz real de `data/raw/` en modo lectura, con los valores
  de `referencia-v4.md` (o los re-extraídos de la versión vigente).
