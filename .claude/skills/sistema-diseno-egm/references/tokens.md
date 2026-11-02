# Tokens del sistema «Fichero»

Valores iniciales: el subagente `disenador-front` debe verificar contrastes con una herramienta y
ajustarlos sin cambiar el concepto.

## Color (modo claro)

| Token | Hex | Uso |
|---|---|---|
| `--papel` | `#FCFCFA` | Fondo general (blanco de ficha, neutro, no crema) |
| `--tinta` | `#1E2A44` | Texto principal y nivel «Evaluación de impacto» |
| `--tinta-media` | `#45628F` | Texto secundario, bordes, nivel «Estudio de caso» |
| `--rayado` | `#A9C1DC` | Rayado de fichas, retícula, divisores (solo líneas, nunca texto) |
| `--cajon` | `#F2F5F9` | Fondo de cada cajón de la cajonera |
| `--cabecera` | `#B3262E` | Único acento: línea roja de cabecera de ficha; marca la selección actual |

## Niveles de evidencia (ordinal, un solo tono)

| Nivel (jerarquía del equipo) | Relleno | Borde |
|---|---|---|
| Evaluación de impacto | `--tinta` | continuo |
| Estudio de caso | `--tinta-media` | continuo |
| Informe de proyecto | `#8AA3C4` | continuo `--tinta-media` |
| Informe descriptivo/opinión | sin relleno | punteado `--tinta-media` |
| Brecha (cajón vacío) | `--cajon` | contorno discontinuo `--rayado` + texto «ningún estudio registrado» |

Los niveles se leen de la matriz; si aparece un nivel nuevo, el sistema debe asignarle un estilo
derivado y mostrar una advertencia de diseño, no fallar.

## Modo oscuro

`--papel #17202E`, `--tinta #E6ECF4`, `--tinta-media #A9BCD6`, `--rayado #33445E`, `--cajon #1E293A`,
`--cabecera #E0565D`. Invertir la escala de niveles para conservar «más contraste = mayor nivel».

## Tipografía (Google Fonts)

| Rol | Familia | Tamaño / interlineado |
|---|---|---|
| Títulos de sección | Alegreya 600 | 35 px / 1.15 |
| Título de página | Alegreya 700 | 44 px / 1.1 |
| Texto corrido, conclusiones | Alegreya 400 | 18 px / 1.55, medida ≤ 68 caracteres |
| Interfaz, filtros, leyendas | Alegreya Sans 500 | 15 px / 1.4 |
| Cifras | Alegreya Sans con `font-variant-numeric: lining-nums tabular-nums` | según contexto |

Escala de razón $1.25$: $15 \to 18 \to 22.5 \to 28 \to 35 \to 44$ px. Sin mayúsculas sostenidas en etiquetas.

## Retícula y espaciado

- Unidad base $u = 8$ px; espacios en múltiplos de $u$.
- Escritorio (≥ 1200 px): 12 columnas; cajonera en 9, columna de notas al margen en 3.
- Tableta: cajonera a ancho completo; notas bajo cada cifra.
- Móvil (≥ 360 px): una columna; cajonera con desplazamiento horizontal y primera columna fija.
- Radios: 2 px en cajones y fichas (objetos de papel); 0 en divisores. Sombras: ninguna salvo la ficha
  abierta (una sola, sutil, para indicar que está encima).

## Boceto de la vista principal (escritorio)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Mapa de evidencias y brechas            Matriz v4, 27 documentos, leída hoy  │ ← cabecera corrida
├───────────────────────────────────────────────────────┬─────────────────────┤
│ Filtros: [Fuente ▾] [Metodología ▾] [Nivel ▾] [Año ▾]  │                     │
│ «Mostrando todos los estudios empíricos codificados»   │  Notas al margen    │
│                                                       │                     │
│              Vuln. Hum. Soc. Nat. Fís. Fin. EyP Sost. │  1 estudio:         │
│ Transf. act.  ●1   ●1   ┄    ┄    ┄    ●1   ┄   ┄     │  N.º 7 (Stark et    │
│ Diagn. terr.  ┄    ┄    ┄    ┄    ┄    ┄    ┄   ┄     │  al., 2026)         │
│ Acomp. téc.  [●1]  ●1   ┄    ┄    ┄    ●1   ┄   ┄     │                     │
│ Apoyo psic.   ┄    ┄    ┄    ┄    ┄    ┄    ┄   ┄     │  ┌───────────────┐  │
│ Mercados      ┄    ┄    ┄    ┄    ┄    ┄    ┄   ┄     │  │ FICHA (rayada)│  │
│ Asociativ.    ┄    ┄    ┄    ┄    ┄    ┄    ┄   ┄     │  │ N.º 7, 2026   │  │
│                                                       │  │ Eval. impacto │  │
│ Leyenda de niveles; cajón ┄ = ningún estudio registrado  │  └───────────────┘  │
├───────────────────────────────────────────────────────┴─────────────────────┤
│ Lo que dicen los datos (conclusiones con conteo y nota al margen)           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Colofón: proyecto, grupo, semillero, universidad, datos, créditos           │
└─────────────────────────────────────────────────────────────────────────────┘
```

`[●1]` = cajón seleccionado (línea roja de cabecera). Las cifras del boceto corresponden a la matriz v4.
