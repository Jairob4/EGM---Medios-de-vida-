# Resumen de la Fase 2 (arquitectura e interfaz)

**Fecha**: 2026-11-21, actualizado el 2026-11-22 al cerrar COR-012
**Autor**: `verificador`
**Lector**: Jairo. Es un documento interno y no se comparte con el equipo.
**Evidencia**: `docs/informes/conformidad-fase-2-2026-11-21.md` y
`docs/informes/conformidad-fase-2-cierre-2026-11-22.md`, con el archivo y la línea de cada dato.

## 1. Estado de la fase

**La Fase 2 está completa. Se cierra cuando usted apruebe la arquitectura.** Usted condicionó esa aprobación a que
COR-012 quedara aplicada y verificada, y ya lo está. La arquitectura (`docs/arquitectura/arquitectura.md`) sigue en
estado «propuesta» hasta su aprobación.

- **Correcciones**:
  - COR-011 está `verificada` (21-nov-2026).
  - COR-012 está `verificada` (22-nov-2026). El texto para su sección 9 está en el informe de cierre, §9.
- **Hallazgos**:
  - Los de la Fase 2 (F2-01 a F2-11) quedan cerrados. F2-04 se cerró con su ratificación del 21-nov-2026 y los demás
    con COR-012.
  - Quedan tres hallazgos menores nuevos, ninguno bloqueante (sección 6).
- **Cobertura completa**:
  - los 89 requisitos tienen al menos un módulo;
  - los 23 módulos cubren al menos un requisito;
  - la columna «Componente» de `docs/specs/trazabilidad.md` coincide con la arquitectura en los 89.
- **Specs**: sin cambios en esta fase.
  - 0 `[NEEDS CLARIFICATION]` abiertos;
  - 89 requisitos, 15 historias, 122 escenarios y 35 criterios de éxito;
  - ID únicos y sin referencias colgantes.
- **Integridad**:
  - la matriz está intacta: SHA-256 `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`;
  - `data/raw/`, `docs/fuentes/` y los specs no tienen cambios.
- **Commits**:
  - el trabajo de la Fase 2 y COR-011 están en el commit `adafb0d`;
  - los cambios de COR-012 están sin commit, en 9 archivos y en `docs/correcciones/COR-012.md`.

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

La vista de red y el módulo no supervisado quedan fuera del alcance y sin implementar. Están documentados como siete
puntos de extensión (arquitectura §7).

## 3. ADR y su estado

| ADR | Decisión | Estado |
|---|---|---|
| ADR-001 | La fuente es la hoja «Matriz bibliográfica»; se cuentan estudios distintos y cada número lleva su lista de filas | Aceptado, 21-nov-2026 |
| ADR-002 | Sin recálculo de fórmulas; sin valores guardados, la verificación queda «no verificable» | Aceptado, 21-nov-2026 |
| ADR-003 | FastAPI + Jinja2 + htmx, HTML y CSS propios, Uvicorn local, Python 3.13 | Aceptado, 21-nov-2026. Los cambios a sus puntos 6 y 7 los ratificó usted. COR-012 agregó una nota de revisión y el segundo límite de NFR-000-19 |
| ADR-004 | Carga desde el navegador, versión local en `127.0.0.1`, definiciones en texto UTF-8 y límite de contenido descomprimido | Aceptado, 21-nov-2026; NC-ADR004-1 abierto a propósito |
| ADR-005 | Colofón por bloques; solo «Datos» y la referencia a 3ie visibles | Aceptado, 21-nov-2026; su nota de revisión (NC-INT-1) la ratificó usted |

Desde el 21-nov-2026, un ADR aceptado solo cambia por una propuesta COR o por un ADR nuevo que lo reemplace.

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

**21-nov-2026, cierre de la Fase 2**
- Ratificó los cambios a ADR-003 (puntos 6 y 7) y a ADR-005 (nota de revisión) posteriores a su aceptación (F2-04).
- Fijó la regla de que un ADR aceptado solo cambia por COR o por un ADR nuevo.
- Agrupó F2-01 a F2-11 en COR-012 y condicionó la aprobación de la arquitectura a que se aplique y se verifique.

**22-nov-2026**
- Aprobó COR-012 con la opción A en todos los hallazgos.
- Aprobó P1 (a): las tipografías se sirven localmente (ADR-003, punto 6).

**Correcciones**
- COR-011: aprobada (opción B) el 21-nov-2026, aplicada y verificada.
- COR-012: aprobada el 22-nov-2026, aplicada y verificada.

## 5. Qué cambió con COR-012

- **Interfaz**:
  - nuevo estado E10, «Rechazo por contenido», en los flujos y en el boceto de carga, con el mensaje «El contenido del
    libro es demasiado grande para abrirlo» y sin cifras;
  - los cuatro puntos NC-INT figuran como decididos;
  - el colofón explica los nueve bloques apagados;
  - el tablero con filtro muestra «0 de 6» estudios empíricos que aún no entran al mapa;
  - la frase sobre información interna ya no nombra la tabla.
- **Arquitectura**:
  - la vista V1 incluye el rechazo por contenido;
  - la cabecera remite a las invariantes;
  - NC-ARQ-1 queda registrado;
  - un párrafo explica el andamiaje de `src/egm/`;
  - se agregó la coma en M23.
- **ADR-003**: nombra el segundo límite de NFR-000-19 y lleva nota de revisión.
- **Skill de diseño**: el título sin «brechas», la cabecera sin versión deducida, el colofón con los bloques apagados
  por defecto y las tipografías servidas localmente.

## 6. Hallazgos menores que quedan

Ninguno impide aprobar la arquitectura.

- **F2-12.** Falta registrar en las invariantes su aprobación de COR-012 del 22-nov-2026, con P1 (a). Lo hace la
  sesión principal, sin el flujo de la regla 11. Conviene hacerlo antes de su aprobación de la arquitectura.
- **F2-13.** La nota de revisión de ADR-003 lleva la fecha 21-nov-2026, aunque COR-012 se aprobó el 22-nov-2026. El
  error venía en el texto de la propuesta. Como ADR-003 está aceptado, la fecha se corrige por COR, en la próxima
  corrección que se abra.
- **F2-14.** La guía del colofón dice que todos sus datos están confirmados, pero la línea «Herramienta» sigue
  pendiente de confirmación. No tiene efecto en la interfaz, porque ese bloque se omite mientras siga pendiente. Se
  propone ajustar la frase en una corrección posterior.

## 7. Decisiones abiertas que pasan a la preparación de los planes

- **NC-ARQ-1, una parte del libro que se descomprime a más de lo declarado.** Se comprueba al preparar el plan 001
  qué hace la biblioteca de lectura en ese caso. El spec ya lo trata como un archivo dañado (COR-011). Está registrado
  en la arquitectura, §9 y §10.
- **NC-ADR004-1, despliegue después de la demostración.**
  - Es una decisión del equipo y queda abierta a propósito.
  - La arquitectura sirve sin cambios para seguir en local o para un ejecutable empaquetado.
  - Un servidor compartido obligaría a revisar los registros del alojamiento y el almacén de sesiones (ADR-004).

## 8. Puntos que quedan para preparar los planes

- **Plan 001** (ADR-003 y ADR-004):
  - versiones fijadas de las dependencias en un `pyproject.toml`, que todavía no existe;
  - rutas de la aplicación;
  - comando de arranque y pasos de instalación;
  - herramientas de prueba en el navegador y de revisión de accesibilidad.
- **Constructor de fixtures (M23)**, en la preparación del plan 001. `data/fixtures/` todavía no existe. Debe construir:
  - libros de tamaño exacto y de contenido descomprimido exacto;
  - validaciones de extensión para probar el respaldo de ADR-001;
  - valores guardados controlados para la verificación.
- **Andamiaje de `src/egm/`.** El plan 001 concilia las carpetas actuales con la lista cerrada y retira las que no
  correspondan a un módulo: `analisis/` y `validacion/` no corresponden a ninguno (arquitectura §6).
- **NC-ARQ-1**, como se indica en la sección 7.

## 9. Cómo ver los bocetos

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

## 10. Lo que necesita la Fase 3 para empezar

1. El registro de F2-12 en las invariantes, a cargo de la sesión principal.
2. Su aprobación de `docs/arquitectura/arquitectura.md`, que pasa de «propuesta» a «aprobada». Con eso se cierra la
   Fase 2.
3. Su commit de COR-012 y de los informes del cierre. Los commits los hace usted.
4. Un plan por spec, hecho con `docs/planes/_plantilla-plan-spec.md`, en el orden 001 → 002 → 003, para llegar al
   6-dic-2026. Cada plan va a `docs/planes/NNN-<feature>/plan.md` y necesita su aprobación antes de escribir código.
5. En el plan 001, la preparación de la sección 8: dependencias, constructor M23, andamiaje y NC-ARQ-1.
6. En cada historia, las pruebas antes que su implementación. Cada NFR-000 va en los planes cuyas historias afecta,
   según el reparto de la arquitectura §6.4.
7. F2-13 y F2-14 no bloquean el comienzo. Pueden ir en la primera corrección que se abra durante la Fase 3.
