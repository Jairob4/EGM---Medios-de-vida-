# Colofón (pie de página, sección de información)

Se compone como el colofón de un libro académico: prosa breve en Alegreya, alineada a la izquierda.
Los datos marcados `[POR CONFIRMAR]` **no se publican** hasta que Jairo los confirme; mientras tanto se
omite la línea completa (no se muestra el marcador al público). La categoría y la línea de investigación
del grupo se omiten por decisión de Jairo.

**Visibilidad (ADR-005; decisiones de Jairo del 21-nov-2026).** Con la configuración por defecto solo se publican
«Datos» y la referencia de diseño a 3ie. Los demás bloques de este archivo (proyecto, grupo de investigación,
código Minciencias, semillero, equipo del proyecto, herramienta, contacto y los dos logos) vienen **apagados por
defecto** y no dejan rastro en el HTML: nada de la Universidad del Magdalena, ni logos ni nombres, se publica hasta
que Jairo tenga la autorización. Cada bloque se enciende por separado en la configuración. Los datos confirmados de este archivo
se conservan para ese momento; la línea «Herramienta» sigue pendiente de confirmación y no se publica aunque se encienda. El orden y el texto de los bloques siguen valiendo (ADR-005,
punto 1).

## Contenido

**Proyecto.** Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los
medios de vida de la población víctima en Colombia.
*Por defecto: apagado (ADR-005).*

**Grupo de investigación.** Organización y Empresa (GIOE), Universidad del Magdalena, Santa Marta.
Director del grupo: Óscar García Vargas.
Código Minciencias: COL0016423.
*Por defecto: apagados el grupo y el código Minciencias, cada uno con su bandera (ADR-005).*

**Semillero.** Desarrollo Rural y Economía Solidaria.
*Por defecto: apagado (ADR-005).*

**Equipo del proyecto.** Amanda Vargas Prieto, investigadora principal. Lina Martínez, coinvestigadora.
*Por defecto: apagado (ADR-005).*

**Herramienta.** [POR CONFIRMAR si se incluye y con qué rol] Jairo de Jesús Blanco Pérez, semillerista.
*Por defecto: apagado y, mientras esté marcado como pendiente de confirmación, omitido aunque se encienda (ADR-005).*

**Datos.** Matriz bibliográfica del estado del arte: nombre del archivo y número de documentos leídos en
tiempo de ejecución (nunca escritos a mano), con fecha de lectura. La herramienta no afirma una versión
que el archivo no declare. Decisión de Jairo, 3-nov-2026: «Matriz: <nombre del archivo tal como llegó>,
leída el <fecha de la carga>, <n> documentos».
*Siempre visible; no es configurable (ADR-005).*

**Referencia de diseño.** International Initiative for Impact Evaluation (3ie). Building Peaceful
Societies Evidence Gap Map (2019). Licencia CC BY-NC-SA 4.0. Se toma solo como referencia de diseño;
no se reproduce su contenido.
*Siempre visible; no es configurable (ADR-005).*

**Contacto.** ogarciav@unimagdalena.edu.co
*Por defecto: apagado (ADR-005).*

## Logos

Los logos de Minciencias y de la Universidad del Magdalena vienen apagados por defecto, cada uno con su bandera
(ADR-005). Solo se publican cuando Jairo tenga la autorización y los suministre en `docs/interfaz/logos/`. Cuando se
publiquen:

- No se recolorean ni se deforman.
- Llevan texto alternativo.
- Son legibles en modo claro y oscuro, sobre una placa clara si hace falta, y desde 360 px de ancho.
- No son fuente de requisitos: de ellos no se toman colores, datos ni textos.

## Fuentes de lo confirmado

- Sigla del grupo y semillero: documento general de la propuesta (portada). Nombre del proyecto: estado del proyecto al 31-oct-2026 (§2), que lo toma de la presentación del equipo.
- Nombre completo del grupo, ciudad y director: decisión de Jairo, 21-nov-2026.
- Investigadora principal y coinvestigadora: presentación del equipo (octubre de 2026).
- Código Minciencias, correo de contacto, logos y omisión de categoría y línea: decisión de Jairo
  (2-nov-2026).
- Visibilidad por defecto de cada bloque: decisiones de Jairo del 21-nov-2026 (ADR-005, NC-INT-1).
