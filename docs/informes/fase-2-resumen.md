# Resumen de la Fase 2 (arquitectura e interfaz)

**Fecha**: 2026-11-21
**Autor**: `verificador`
**Lector**: Jairo. Es un documento interno y no se comparte con el equipo.
**Evidencia**: `docs/informes/conformidad-fase-2-2026-11-21.md`, con archivo y línea de cada dato.

## 1. Estado de la fase

**La Fase 2 está completa y puede cerrarse en cuanto usted apruebe la arquitectura.** La arquitectura
(`docs/arquitectura/arquitectura.md`) está en estado «propuesta».

- **Cobertura completa**:
  - los 89 requisitos tienen al menos un módulo;
  - los 23 módulos cubren al menos un requisito;
  - la columna «Componente» de `docs/specs/trazabilidad.md` coincide con la arquitectura en los 89.
- **Hallazgos**: no hay bloqueantes. Hay cuatro mayores (F2-01 a F2-04) y siete menores (F2-05 a F2-11).
- **COR-011 queda `verificada`.** El texto de su sección 9 está en el informe de conformidad, §11.
- **Specs**:
  - 0 `[NEEDS CLARIFICATION]` abiertos;
  - 89 requisitos, 15 historias, 122 escenarios y 35 criterios de éxito;
  - ID únicos y sin referencias colgantes.
- **Integridad**:
  - la matriz está intacta: SHA-256 `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`;
  - `data/raw/` y `docs/fuentes/` no tienen cambios;
  - el trabajo de la Fase 2 sigue sin commit sobre 997e932, el commit con el que cerró la Fase 1.

## 2. Módulos (lista cerrada)

| N.º | Módulo | Qué hace | Plan que lo crea |
|---|---|---|---|
| M01 | `egm.modelo` | Tipos del dominio; todo número es la longitud de su lista de filas | 001 |
| M02 | `egm.archivo` | Tipo y tamaño antes de leer; los dos límites de NFR-000-19 | 001 |
| M03 | `egm.libro` | Abre el libro en memoria, solo lectura | 001 |
| M04 | `egm.esquema` | Columnas por encabezado, bloque de dimensiones, listas y errores de contrato | 001 |
| M05 | `egm.lectura` | Documentos, advertencias, estados y enfoque | 001 |
| M06 | `egm.filtros` | Los cuatro filtros, la regla de «activo» y «Sin nivel» | 002 |
| M07 | `egm.conteo` | Conteos de estudios distintos y coocurrencias | 001 |
| M08 | `egm.verificacion` | Contraste con las tablas comparables de la hoja EGM | 001 |
| M09 | `egm.conclusiones` | Cifras clave y las seis conclusiones | 003 |
| M10 | `egm.textos` | Catálogo único de textos para el equipo | 001 |
| M11 | `egm.porcentajes` | Porcentajes apagados; solo existe la capacidad | 003 |
| M12 | `egm.definiciones` | Definiciones de filas y columnas | 002 |
| M13 | `egm.procesamiento` | Entrada única del núcleo | 001 |
| M14 | `app.servidor` | Rutas y política de registros | 001 |
| M15 | `app.sesiones` | Sesiones en memoria: 45 minutos y 10 segundos de gracia | 001 |
| M16 | `app.carga` | Recepción del archivo sin pasar por el disco | 001 |
| M17 | `app.presentacion` | Modelos de vista, sin cálculo propio | 001 |
| M18 | `app.plantillas` | Plantillas y CSS «Fichero» | 001 |
| M19 | `app.cliente` | JavaScript mínimo: sesión, actividad y conversión del mapa a PNG | 001 |
| M20 | `app.exportacion` | SVG del mapa y tabla de conteos en `.xlsx` | 002 |
| M21 | `app.colofon` | Colofón por bloques, apagados por defecto | 001 |
| M22 | `app.configuracion` | Configuración local leída al arrancar | 001 |
| M23 | `tests.constructor` | Matrices sintéticas para las pruebas | 001 |

Fuera del alcance, sin implementar: la vista de red y el módulo no supervisado. Quedan documentados como siete puntos
de extensión (arquitectura §7).

## 3. ADR y su estado

| ADR | Decisión | Estado |
|---|---|---|
| ADR-001 | La fuente es la hoja «Matriz bibliográfica»; se cuentan estudios distintos y cada número lleva su lista de filas | Aceptado, 21-nov-2026 |
| ADR-002 | Sin recálculo de fórmulas; sin valores guardados, la verificación queda «no verificable» | Aceptado, 21-nov-2026 |
| ADR-003 | FastAPI + Jinja2 + htmx, HTML y CSS propios, Uvicorn local, Python 3.13 | Aceptado, 21-nov-2026; editado después por decisiones de la interfaz (F2-04) |
| ADR-004 | Carga desde el navegador, versión local en `127.0.0.1`, definiciones en texto UTF-8 y límite de contenido descomprimido | Aceptado, 21-nov-2026; NC-ADR004-1 abierto a propósito |
| ADR-005 | Colofón por bloques; solo «Datos» y la referencia a 3ie visibles | Aceptado, 21-nov-2026; con nota de revisión del mismo día (NC-INT-1) |

## 4. Decisiones suyas que constan

**21-nov-2026, después de cerrar la Fase 1**
- Aprobó la Fase 1.
- Nada de la Universidad del Magdalena se publica hasta que haya autorización.
- El stack lo propone el ADR-003.

**21-nov-2026, arquitectura**
- ADR-001 a ADR-005 aceptados.
- Exportación: el mapa en PNG, con SVG adicional; los conteos en `.xlsx`.
- Recargar la página no termina la sesión: hay 10 segundos de gracia.
- Las definiciones van en un archivo de texto UTF-8.
- Límite de contenido descomprimido: 268 435 456 bytes (COR-011).
- Se aprueba el punto 2 del ADR-002.
- El despliegue lo decide el equipo.

**21-nov-2026, interfaz**
- Solo «Datos» y la referencia a 3ie quedan visibles en el colofón (NC-INT-1).
- Los empíricos pendientes sin nivel no cuentan como «Sin nivel» (NC-INT-2).
- El título es «Evidencias sobre medios de vida» (NC-INT-3).
- M20 entrega el SVG y M19 lo convierte en PNG (NC-INT-4).
- Se autorizó completar las listas «Cubre» de M08 y M09.

**COR-011**: aprobada (opción B) el 21-nov-2026, aplicada y verificada.

## 5. Decisiones abiertas

- **NC-ADR004-1, despliegue después de la demostración**. Lo decide el equipo una vez hecha la demostración. La
  arquitectura sirve sin cambios para seguir en local o para un ejecutable empaquetado. Un servidor compartido exigiría
  revisar los registros del alojamiento y el almacén de sesiones (ADR-004).
- **Ratificación de las ediciones a ADR-003 y ADR-005 posteriores a su aceptación** (F2-04). La propuesta es que usted
  las ratifique al aprobar la Fase 2 y que, desde entonces, un ADR aceptado solo cambie por una propuesta COR.

## 6. Correcciones propuestas antes del plan 001

Las cuatro siguen el flujo de la regla 11: analista, su aprobación y corrector. Cuando terminen, se hace una sola
auditoría.

1. **F2-01. Estado de interfaz del rechazo por contenido descomprimido (US-001-4.13).**
   - Falta en `flujos.md`, en `carga.html` y en la vista V1 de la arquitectura.
   - El mensaje es «El contenido del libro es demasiado grande para abrirlo».
2. **F2-02. Llevar a `flujos.md` las decisiones NC-INT-1 a NC-INT-4.**
   - Hoy figuran como abiertas y una de las recomendaciones dice lo contrario de lo decidido.
   - En la misma corrección conviene marcar `flujos.md` como documento interno (F2-11).
3. **F2-03. Actualizar la skill `sistema-diseno-egm`.**
   - Sigue listando el grupo y la universidad en el colofón.
   - Su boceto lleva el título «Mapa de evidencias y brechas» y una cabecera con «v4» y «leída hoy».
   - Contradice ADR-005, NC-INT-3 y NFR-000-12.
4. **F2-04. Registrar la ratificación indicada en la sección 5.**

Los menores (F2-05 a F2-10) pueden ir en la misma tanda o atenderse al preparar el plan 001.

## 7. Puntos que quedan para preparar los planes

- **Biblioteca de lectura ante una parte que se descomprime a más de lo declarado.** Se comprueba al preparar el plan
  001. El spec ya trata ese caso como un archivo dañado (COR-011, §4 y §6). Hoy no consta en la arquitectura (F2-06).
- **Plan 001** (ADR-003 y ADR-004):
  - versiones fijadas de las dependencias;
  - rutas de la aplicación;
  - comando de arranque y pasos de instalación;
  - herramientas de prueba en navegador y de revisión de accesibilidad.
- **Constructor de fixtures (M23)**, en la preparación del plan 001, con:
  - libros de tamaño exacto y de contenido descomprimido exacto;
  - validaciones de extensión para probar el respaldo de ADR-001;
  - valores guardados controlados para la verificación.
- **Andamiaje de `src/egm/`.** Las carpetas `analisis/` y `validacion/` no corresponden a ningún módulo. El plan 001
  debe conciliarlas con la lista cerrada (F2-10).
- **Tablero con filtro**: definir cómo se presenta la cifra de empíricos pendientes con «n de N» (F2-09, plan 003).

## 8. Cómo ver los bocetos

1. Abra en el navegador el archivo `docs/interfaz/bocetos/index.html`, con doble clic o arrastrándolo a una pestaña.
   No necesita servidor ni internet.
2. El índice lleva a las cinco vistas: carga y mensajes de sesión, mapa con cajón abierto, detalle del N.º 7, tablero y
   colofón.
3. Cada vista tiene su versión oscura. Puede abrirla desde el enlace «(oscuro)» del índice o agregando `?tema=oscuro`
   al final de la dirección. Sin ese parámetro, la vista sigue el tema del sistema.
4. Puede revisar el mapa solo con el teclado: Tab para entrar a la cajonera, las flechas para moverse e Intro para
   abrir un cajón.
5. Los bocetos usan las cifras de la v4 del apéndice A del contrato. Los textos que el apéndice no trae aparecen entre
   corchetes, como marcadores.
6. Las tipografías Alegreya no se cargan en los bocetos; se ven con las del sistema.

## 9. Lo que necesita la Fase 3 para empezar

1. Su aprobación de `docs/arquitectura/arquitectura.md`, que pasa de «propuesta» a «aprobada».
2. Las correcciones de la sección 6 aplicadas y auditadas, o su indicación expresa de cuáles pasan a la preparación
   del plan 001. Como mínimo, F2-01, porque toca la historia US-001-4 del plan 001.
3. La ratificación de la sección 5, registrada en `invariantes.md` por la sesión principal.
4. Su commit del trabajo de la Fase 2 y de COR-011. Los commits los hace usted.
5. Un plan por spec, con `docs/planes/_plantilla-plan-spec.md`, en el orden 001 → 002 → 003, para llegar al 6-dic-2026.
6. En cada historia, las pruebas antes que su implementación. Cada NFR-000 va en los planes cuyas historias afecta,
   según el reparto de la arquitectura §6.4.
