# Resumen de la Fase 4 — Código del plan 001 «Lectura y verificación»

**Fecha**: 26-nov-2026 · **Para**: Jairo · **Estado**: las Fases 1 a 9 del plan 001 están hechas y la verificación de cierre (T-001-95) fue aceptada por Jairo. Las correcciones COR-017 y COR-018 están verificadas.
Detalle y evidencia: `docs/informes/conformidad-plan-001-2026-11-26.md`.

## 1. Entorno registrado

- Python **3.13.15** (`.venv/pyvenv.cfg`).
- openpyxl **3.1.5**.
- Navegador de las pruebas de interfaz: Chromium de Playwright (instalado con autorización de Jairo el 26-nov-2026).

## 2. Qué se entregó

- **Núcleo `src/egm/`**: modelo (M01), archivo (M02), libro (M03), esquema (M04), lectura (M05), conteo (M07), verificación contra la hoja EGM (M08), catálogo de textos (M10) y la fachada `egm.procesamiento.procesar` (M13). Interfaz congelada en el hito N1 (`__all__` de cada módulo, `mypy --strict` limpio).
- **Capa web `app/`**: configuración, sesión (inactividad de 45 minutos y gracia de cierre de 10 segundos), servidor, presentación, plantillas y estilos del sistema «Fichero», `egm.js` y htmx local. Hito N2 alcanzado: se carga la matriz, se muestra el resultado de la lectura y se termina la sesión.
- **Pruebas**: constructor de matrices sintéticas (M23) y 74 fixtures deterministas.

## 3. Resultados de la verificación de cierre

| Comprobación | Resultado |
|---|---|
| Pruebas sin navegador | 771 en verde |
| Pruebas de navegador (Chromium) | 63 en verde |
| Cobertura de `src/egm/` | 99,72 % (umbral 90 %) |
| `ruff` y `mypy --strict` | Sin errores |
| Huella de la matriz y `data/raw/` | Intactas |
| Requisitos del plan con tarea, código y prueba | 44 de 44 |

Dictamen: conforme; las no conformidades son solo de documentos y de trazabilidad.

## 4. NC-ARQ-1

Resuelto en T-001-09 (24-nov-2026; P-001-02): la biblioteca no lee más de lo declarado; un libro dañado se rechaza como «archivo dañado».

## 5. Qué queda disponible para los planes 002 y 003

El núcleo de lectura, conteo y verificación; la fachada `procesar`; la base web con sesión, cabecera, colofón y avisos de lectura (V0, V1, V2); y los textos del catálogo M10. La arquitectura §6.1 se pone al día con la interfaz real mediante COR-018.

## 6. Pendientes

- COR-017 y COR-018 verificadas el 26-nov-2026 (`docs/informes/conformidad-cor-017-018-2026-11-26.md`); NC-V-1 y NC-V-2 decididos por Jairo.
- NC-P001-2: archivos de los logos (`minciencias.svg`, `unimagdalena.svg`) y NC-P001-4: nombre de `egm.toml`; la revisión de NFR-000-11 queda sujeta a ellos.
- Deudas sin tarea (docstrings sin ID de escenario, prueba del catálogo para los códigos de M08, avisos de las corridas, carpeta temporal compartida de P-001-84 y P-001-92): las resuelve una tarea del `implementador` cuando Jairo lo decida.
- Commit de Jairo de las Fases 5 a 9 y de las correcciones.
- Sin comprobar: lector de pantalla y `pageshow` con página restaurada.
