"""M02 `egm.archivo`: validación previa del archivo cargado (arquitectura §6.1, M02).

Valida, antes de leer el libro, el tamaño, el tipo y el contenido descomprimido declarado
(NFR-000-19, FR-001-20, FR-001-29). Es la única fuente de los dos límites, fijos y no configurables.

Reglas del módulo (arquitectura §4.1; las vigila P-001-10): solo biblioteca estándar y `egm.modelo`;
no importa la capa web ni la biblioteca de lectura de hojas de cálculo; trabaja con los bytes en
memoria, sin entrada ni salida y sin estado global.

El contenido descomprimido se comprueba solo con el índice del paquete (los tamaños que declara
cada parte): nunca se lee ni se descomprime ninguna parte. Qué pasa si una parte se descomprime a
más de lo declarado lo resuelve `egm.libro` (NC-ARQ-1: el libro no se abre y `procesar` lo trata
como archivo dañado).
"""

import io
import zipfile
from typing import Final

from egm.modelo import Rechazo

__all__ = ["LIMITE_BYTES", "LIMITE_DESCOMPRIMIDO", "validar_archivo"]

LIMITE_BYTES: Final[int] = 15_728_640
"""NFR-000-19: tamaño máximo de un archivo cargado (15 MiB), en bytes. Fijo."""

LIMITE_DESCOMPRIMIDO: Final[int] = 268_435_456
"""NFR-000-19: contenido descomprimido declarado máximo (256 MiB), suma de las partes. Fijo."""

# Partes sin las cuales un paquete ZIP no es un libro de hoja de cálculo `.xlsx`.
_PARTES_DEL_LIBRO: Final[tuple[str, ...]] = ("[Content_Types].xml", "xl/workbook.xml")


def validar_archivo(contenido: bytes) -> Rechazo | None:
    """Devuelve `None` si el archivo se puede leer y un `Rechazo` si no.

    Orden de las comprobaciones, de la más barata a la más costosa:

    1. Tamaño: más de `LIMITE_BYTES` bytes ⇒ `Rechazo("tamano")`, sin mirar el contenido.
    2. Tipo: un paquete ZIP legible con las partes de un libro `.xlsx`; cualquier otra cosa
       (otro tipo de archivo, extensión engañosa, archivo dañado o vacío) ⇒ `Rechazo("tipo")`.
    3. Contenido: la suma de los tamaños descomprimidos que declara el índice, de todas las partes,
       mayor que `LIMITE_DESCOMPRIMIDO` ⇒ `Rechazo("contenido")`. No descomprime nada.

    El valor exacto de cada límite se acepta y un byte más se rechaza.
    """
    if len(contenido) > LIMITE_BYTES:
        return Rechazo("tamano")
    try:
        with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
            partes = paquete.infolist()
    except (zipfile.BadZipFile, OSError, EOFError, ValueError):
        return Rechazo("tipo")
    nombres = {parte.filename for parte in partes}
    if not all(nombre in nombres for nombre in _PARTES_DEL_LIBRO):
        return Rechazo("tipo")
    if sum(parte.file_size for parte in partes) > LIMITE_DESCOMPRIMIDO:
        return Rechazo("contenido")
    return None
