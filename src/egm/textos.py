"""M10 `egm.textos`: catálogo único de los textos dirigidos al equipo (arquitectura §6.1, M10).

Todo texto de la interfaz vive aquí y en ningún otro módulo: en español, de usted, sin jerga
técnica, sin fórmulas y sin preguntas (NFR-000-03). Este módulo no calcula: recibe datos ya
calculados y devuelve cadenas (arquitectura §4.1, regla 4). Solo importa la biblioteca estándar y
`egm.modelo`.

Esta es la base del módulo (plan 001, T-001-17): los textos de rechazo (estados E2, E3 y E10 de
`docs/interfaz/flujos.md` §2), `fecha()` y `ROTULOS` vacío. Los planes siguientes agregan al
catálogo sus advertencias, notas, errores de contrato, verificación, conclusiones y rótulos.
"""

from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType
from typing import Final

from egm.modelo import Rechazo

__all__ = ["CATALOGO", "ROTULOS", "fecha", "rechazo"]

CATALOGO: Final[Mapping[str, str]] = MappingProxyType(
    {
        # E2: archivo que no es un libro .xlsx, o .xlsx dañado (US-001-4.3, SC-000-19).
        "rechazo.tipo": (
            "No se pudo cargar el archivo. El archivo elegido no es un archivo de Excel (.xlsx) "
            "que la herramienta pueda abrir, o está dañado. No se leyó y no se muestra ningún "
            "resultado. Elija la matriz bibliográfica en formato .xlsx."
        ),
        # E3: más de 15 728 640 bytes (US-001-4.4, SC-000-19).
        "rechazo.tamano": (
            "No se pudo cargar el archivo. El archivo pesa más de 15 MB (15 728 640 bytes), el "
            "máximo que admite la herramienta. No se leyó y no se muestra ningún resultado de ese "
            "archivo."
        ),
        # E10: contenido descomprimido declarado por encima del límite; sin cifras (US-001-4.13).
        "rechazo.contenido": (
            "No se pudo cargar el archivo. El contenido del libro es demasiado grande para "
            "abrirlo. No se leyó y no se muestra ningún resultado de ese archivo."
        ),
    }
)
"""Catálogo único: clave del texto → texto. Los planes 001, 002 y 003 lo amplían."""

ROTULOS: Final[Mapping[str, str]] = MappingProxyType({})
"""Rótulos cortos de la interfaz. Vacío en la base; los planes 002 y 003 lo amplían."""

# Meses en una tabla propia: el resultado no depende de la configuración regional del equipo.
_MESES: Final = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def rechazo(r: Rechazo) -> str:
    """Texto de la interfaz para un archivo rechazado antes de leerlo (E2, E3 o E10)."""
    return CATALOGO[f"rechazo.{r.motivo}"]


def fecha(d: datetime) -> str:
    """Fecha en español, por ejemplo «21 de noviembre de 2026» (día sin cero a la izquierda)."""
    return f"{d.day} de {_MESES[d.month - 1]} de {d.year}"
