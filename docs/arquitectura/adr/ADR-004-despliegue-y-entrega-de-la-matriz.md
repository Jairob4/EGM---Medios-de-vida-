# ADR-004: Despliegue y forma de entregar la matriz a la aplicación

**Fecha**: 2026-11-21 · **Estado**: aceptado, 2026-11-21 [Fuente: decisión de Jairo, 21-nov-2026]; el despliegue
posterior a la demostración queda como decisión futura del equipo (NC-ADR004-1)
**Requisitos que la motivan**: NFR-000-01, NFR-000-15, NFR-000-17, NFR-000-18, NFR-000-19, FR-001-20, FR-001-29,
FR-002-08, SC-000-15, SC-000-17

## Contexto

- La primera versión terminada es **local, para la demostración** (restricción 5 de `000`; decisión de Jairo,
  2-nov-2026). Si se despliega y dónde lo decide **el equipo después de la demostración** (`000`, «Decisiones futuras»).
- En la versión local, quien consulta usa el equipo donde corre la herramienta y no instala nada más (SC-000-15).
- La matriz llega por **carga desde el navegador**; se valida tipo y tamaño antes de leerla; vive solo durante la sesión;
  una carga nueva reemplaza a la anterior (FR-001-20, FR-001-29, NFR-000-17, NFR-000-19).
- El doc. técnico §4.2 RNF3 y §5.2 proponían un archivo autocontenido sin servidor; la decisión de Jairo del
  31-oct-2026 pide aplicación web y deja a la arquitectura cómo se sirve (`000`, «Notas sobre las fuentes»).
- Las definiciones de filas y columnas vienen de un archivo de texto aparte; si no existe, «definición no disponible»
  (FR-002-08; decisión de Jairo, 2-nov-2026). El spec no fija su formato ni su ubicación; los fija este ADR (punto 4).
- Un libro `.xlsx` es un paquete comprimido: un archivo de menos de 15 728 640 bytes puede ocupar mucho más al
  descomprimirse y agotar la memoria. NFR-000-19 solo limita el tamaño del archivo.
- `data/raw/` contiene la matriz vigente, de solo lectura, para pruebas y control de huella del proyecto.

## Opciones consideradas

Entrega de la matriz:

| Opción | A favor | En contra |
|---|---|---|
| A. Carga desde el navegador en cada sesión, bytes solo en memoria | Es lo que piden FR-001-20 y NFR-000-17; la matriz del equipo nunca se copia | Hay que cargarla en cada sesión (es lo pedido) |
| B. La aplicación lee una ruta fija, por ejemplo `data/raw/` | Cómodo para Jairo | Contradice FR-001-20 y NFR-000-17; ataría la herramienta a una copia del archivo |
| C. Carpeta vigilada en el servidor | Automático | Persistencia en disco; contradice NFR-000-17 |

Despliegue de la versión de demostración:

| Opción | A favor | En contra |
|---|---|---|
| D1. Proceso local en el equipo de la demostración, escuchando solo en `127.0.0.1`, abierto en el navegador de ese equipo | Cumple SC-000-15; nadie más en la red lo alcanza; sin TLS ni cuentas | Solo un equipo |
| D2. Servidor en la red local o en internet | Varias personas a la vez | Decisión del equipo, posterior a la demostración; exige TLS, revisión de registros del proxy y del alojamiento, y un almacén de sesiones adecuado |
| D3. Ejecutable empaquetado para cada equipo | No requiere Python en cada equipo | Trabajo de empaquetado no pedido para la demostración |

## Decisión

1. **Entrega de la matriz: opción A.** La herramienta nunca lee `data/raw/` ni ninguna ruta del disco para obtener la
   matriz. La persona elige el archivo en su navegador; `app.carga` recibe los bytes en memoria, `egm.archivo` valida
   tipo y tamaño y `egm.procesamiento` lee. Rechazo ⇒ se conserva lo anterior; error de contrato ⇒ se limpia todo y
   termina la sesión; lectura aceptada ⇒ reemplaza y borra filtros (FR-001-29).
2. **Despliegue de la demostración: opción D1.** Un comando de arranque, dentro del `.venv` con Python 3.13, inicia
   Uvicorn con un solo proceso, escuchando solo en `127.0.0.1` y en un puerto configurable, con el registro de accesos
   apagado. La persona abre la dirección local en el navegador del mismo equipo. El plan 001 documenta el comando y los
   pasos de instalación para Jairo.
3. **Registros**: solo eventos técnicos sin datos (arranque, cierre, número de sesiones activas, errores por tipo y
   módulo). Nunca nombre del archivo, valores, encabezados ni cuerpos (NFR-000-17).
4. **Configuración y definiciones**: archivos de texto junto a la instalación, de solo lectura, leídos al arrancar por
   `app.configuracion` (M22). No contienen datos de la matriz.
   - **Archivo de definiciones** (FR-002-08; antes NC-ADR004-2) [Fuente: decisión de Jairo, 21-nov-2026]: texto
     UTF-8 junto a la instalación, leído al arrancar. Cada intervención o dimensión lleva un encabezado con su nombre
     exacto y, debajo, el texto de su definición. El nombre del encabezado se empareja con el de la matriz de forma
     exacta tras quitar espacios en los extremos, como el resto del contrato. `egm.definiciones` (M12) devuelve el
     texto tal cual. El contenido lo define el equipo; si el archivo no existe o un nombre no tiene encabezado, se
     muestra «definición no disponible».
5. **Límite del contenido descomprimido** (NFR-000-19; antes NC-ADR004-3) [Fuente: decisión de Jairo, 21-nov-2026]:
   `egm.archivo` (M02) rechaza como **archivo que no se puede abrir** (el mismo trato que el spec 001 da a un archivo
   dañado) todo libro cuyo contenido descomprimido declarado supere 256 MiB ($256 \times 2^{20} = 268\,435\,456$
   bytes). La comprobación usa los tamaños declarados en el índice del paquete, antes de descomprimir nada. El
   criterio está en NFR-000-19, con un mensaje propio y sin cifras, y se comprueba con SC-000-19 y US-001-4.13 (COR-011).
6. **Despliegue posterior**: no se decide aquí; es una decisión futura del equipo (NC-ADR004-1).

`[NEEDS CLARIFICATION: NC-ADR004-1. Decisión futura, no pendiente de la Fase 2: el despliegue después de la demostración
lo decide el equipo una vez hecha la demostración, y queda abierto a propósito [Fuente: decisión de Jairo, 21-nov-2026].
Opciones: (a) seguir
local, con instalación en cada equipo que lo necesite; (b) servidor institucional o alojamiento externo de una sola
instancia, con TLS; (c) ejecutable empaquetado. Implicaciones para la arquitectura: (b) exige revisar que el proxy y el
alojamiento no registren cabeceras ni cuerpos (NFR-000-17), mantener un solo proceso o un almacén de sesiones en memoria
compartida sin disco (NFR-000-18), y definir el número de sesiones simultáneas; (a) y (c) no cambian nada. Recomendación:
no decidir antes de la demostración; la arquitectura actual sirve para (a) y (c) sin cambios y para (b) con los ajustes
indicados.]`

## Consecuencias

- Positivas:
  - La matriz del equipo nunca se copia ni se modifica (NFR-000-01, SC-000-01).
  - La demostración no depende de internet ni de terceros, y nadie fuera del equipo local alcanza la herramienta.
  - El despliegue futuro queda abierto sin rehacer nada del núcleo.
- Negativas / deuda aceptada:
  - Un solo equipo usa la versión local a la vez (varias pestañas sí, cada una con su sesión).
  - Las definiciones no se pueden mostrar hasta que el equipo suministre el archivo.
- Requisitos afectados y cómo se verifican:
  - FR-001-20, FR-001-29: US-001-4.1 a US-001-4.13.
  - NFR-000-15, SC-000-15: arrancar y usar todas las vistas en un navegador del mismo equipo, sin instalar nada más.
  - NFR-000-17: SC-000-17; además, una prueba confirma que ninguna ruta de la aplicación lee `data/raw/`.
  - FR-002-08: US-002-3.1 a US-002-3.3, con un archivo de definiciones sintético en el formato del punto 4.
  - Límite descomprimido: un libro sintético con contenido declarado de 268 435 456 bytes se acepta y uno de un byte
    más se rechaza como archivo que no se puede abrir (SC-000-19, US-001-4.13).
