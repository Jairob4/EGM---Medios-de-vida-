# Referencia verificada: matriz v4 (extraída el 31-oct-2026)

Archivo: `matriz_bibliografica_estado_del_arte_v4.xlsx`. Re-extraer del archivo vigente antes de usar.

## Columnas de «Matriz bibliográfica» (fila 1)

| Col. | Encabezado | Tipo | Lista desplegable |
|---|---|---|---|
| A | N° | entero | — |
| B | Referencia APA | texto | — |
| C | Año | entero | — |
| D | Tipo de documento | categoría | sí |
| E | País y población | texto | — |
| F | Tipo de fuente | categoría | sí |
| G | Tipo de intervención (EGM) | categoría | sí |
| H | Intervención secundaria (opcional) | categoría | sí |
| I | Metodología | categoría | sí |
| J | Nivel de evidencia | categoría | sí |
| K | Dimensiones evaluadas / propuestas | texto | — |
| L–S | Vulnerabilidad, Humano, Social, Natural, Físico, Financiero, Estructuras y procesos, Sostenibilidad | 1/0 | sí (`1,0`) |
| T | Indicadores o categorías analíticas | texto | — |
| U | Enfoque de género/diferencial | texto con prefijo Sí/No/Parcial | — |
| V | Principales hallazgos / tesis central | texto | — |
| W | Vacío de conocimiento identificado | texto | — |
| X | Limitaciones | texto | — |
| Y | Aporte al proyecto | texto | — |

Validaciones aplicadas a las filas 2–36.

## Listas

- **D** Tipo de documento: Marco teórico · Marco metodológico · Marco normativo · Estudio empírico (evaluación/caso) · Marco crítico-contextual · Comparativo internacional
- **F** Tipo de fuente: Académica · Institucional · Territorial
- **G** Intervención: Transferencia de activos · Diagnóstico territorial · Acompañamiento técnico · Apoyo psicosocial · Acceso a mercados y finanzas · Asociatividad · No aplica (documento teórico/metodológico/normativo)
- **H** Secundaria: las 6 intervenciones (sin «No aplica»)
- **I** Metodología: Cualitativa · Cuantitativa · Mixta · Revisión documental · Evaluación de impacto · Conceptual/teórica · Análisis normativo/jurídico
- **J** Nivel de evidencia: Evaluación de impacto · Estudio de caso · Informe de proyecto · Informe descriptivo/opinión · No aplica (marco conceptual/normativo/metodológico)

Jerarquía declarada por el equipo (`Instrucciones`, B11): Evaluación de impacto > Estudio de caso > Informe de proyecto > Informe descriptivo/opinión.

## Hoja «EGM»

| Bloque | Rango | Contenido |
|---|---|---|
| 1 | A5:J11 | Número total de estudios (6 intervenciones × 8 dimensiones + «Total estudios») |
| 2 | A15:J21 | Ídem, solo «Evaluación de impacto» |
| 3 | A25:J31 | Ídem, enfoque de género = Sí (ver observación interna en SKILL.md) |
| 4 | A35:B39 | Estudios empíricos por nivel de evidencia |

Fórmulas: `COUNTIFS` sobre `'Matriz bibliográfica'!$X$2:$X$200` (rango fijo 2:200). Nota A41 de la hoja:
un estudio cuenta una vez por intervención (principal o secundaria) y por dimensión en 1; el bloque 3
requiere que la columna U empiece por «Sí». El archivo v4 no trae valores calculados guardados.

## Datos (v4)

- 27 documentos (N.º 1–27, filas 2–28): 9 marco metodológico, 7 estudio empírico, 4 marco teórico,
  3 marco normativo, 3 marco crítico-contextual, 1 comparativo internacional.
- Según la presentación del equipo: 7 diligenciados por completo, 20 solo con referencia.
- Único empírico codificado: N.º 7 (Stark et al., 2026). G = Acompañamiento técnico, H = Transferencia
  de activos, J = Evaluación de impacto, dimensiones en 1: Vulnerabilidad, Humano, Financiero.
- Valores esperados recalculados: bloque 1 con 6 celdas en 1 (2 intervenciones × 3 dimensiones),
  bloque 4 = (1, 0, 0, 0).
- Columna U de N.º 2 y N.º 7: no empiezan por Sí/No/Parcial → «Sin clasificar».
- Empíricos sin codificar: N.º 10, 11, 13, 15, 16, 24.
