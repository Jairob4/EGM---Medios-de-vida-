"""M22 `app.configuracion`: la configuración local de la herramienta (arquitectura §6.2, M22).

Un archivo de texto opcional junto a la instalación, en TOML y leído con la biblioteca estándar.
Sin archivo, o con el archivo vacío, rigen los valores por defecto, que son los seguros: los nueve
bloques configurables del colofón apagados (ADR-005) y el puerto 8000. El límite de tamaño y la
inactividad no se configuran: son fijos en el código (`egm.archivo` y `app.sesiones`).

Forma del archivo (todo es opcional)::

    puerto = 8000

    [colofon.proyecto]          # una tabla por bloque; claves: activo, texto
    activo = true
    texto = "..."

    [colofon.logo_minciencias]  # los logos: activo, archivo, alt, placa_clara
    activo = true
    archivo = "minciencias.svg"
    alt = "..."
    placa_clara = false

Los planes 002 y 003 agregan aquí la ruta de las definiciones y la política de porcentajes.

[NEEDS CLARIFICATION: el nombre del archivo de configuración (`egm.toml` junto a `pyproject.toml`)
y los nombres de archivo de los logos (`minciencias.svg`, `unimagdalena.svg`) son propuestas; la
arquitectura no los fija.]
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Final

from app.colofon import BloqueColofon, ConfiguracionColofon, Logo

__all__ = [
    "PUERTO_POR_DEFECTO",
    "RUTA_DE_CONFIGURACION",
    "Configuracion",
    "ErrorDeConfiguracion",
    "cargar_configuracion",
]

PUERTO_POR_DEFECTO: Final = 8000
RUTA_DE_CONFIGURACION: Final[Path] = Path(__file__).resolve().parent.parent / "egm.toml"
"""Dónde busca `python -m app.servidor` el archivo de configuración (junto a la instalación)."""


class ErrorDeConfiguracion(ValueError):
    """El archivo de configuración no se puede usar. El mensaje nunca repite sus valores."""


@dataclass(frozen=True, slots=True)
class Configuracion:
    """La configuración leída al arrancar."""

    colofon: ConfiguracionColofon
    puerto: int = PUERTO_POR_DEFECTO


# Los textos son los de `pie-de-pagina.md`. Todos los bloques vienen apagados (ADR-005, punto 2).
_PROYECTO: Final = (
    "Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los "
    "medios de vida de la población víctima en Colombia."
)
_GRUPO: Final = (
    "Organización y Empresa (GIOE), Universidad del Magdalena, Santa Marta. Director del grupo: "
    "Óscar García Vargas."
)
_HERRAMIENTA: Final = (
    "[POR CONFIRMAR si se incluye y con qué rol] Jairo de Jesús Blanco Pérez, semillerista."
)


def _bloques_por_defecto() -> tuple[BloqueColofon, ...]:
    return (
        BloqueColofon("proyecto", False, _PROYECTO, None),
        BloqueColofon("grupo", False, _GRUPO, None),
        BloqueColofon("codigo_minciencias", False, "Código Minciencias: COL0016423.", None),
        BloqueColofon("semillero", False, "Desarrollo Rural y Economía Solidaria.", None),
        BloqueColofon(
            "equipo",
            False,
            "Amanda Vargas Prieto, investigadora principal. Lina Martínez, coinvestigadora.",
            None,
        ),
        BloqueColofon("herramienta", False, _HERRAMIENTA, None),
        BloqueColofon("contacto", False, "ogarciav@unimagdalena.edu.co", None),
        BloqueColofon(
            "logo_minciencias",
            False,
            None,
            Logo(Path("minciencias.svg"), "Logotipo de Minciencias", False),
        ),
        BloqueColofon(
            "logo_unimagdalena",
            False,
            None,
            Logo(Path("unimagdalena.svg"), "Logotipo de la Universidad del Magdalena", False),
        ),
    )


def _como_tabla(dato: object) -> Mapping[str, Any]:
    if not isinstance(dato, dict):
        raise ErrorDeConfiguracion("Una sección de la configuración debe ser una tabla.")
    return dato


def _texto(tabla: Mapping[str, Any], clave: str) -> str:
    valor = tabla[clave]
    if not isinstance(valor, str):
        raise ErrorDeConfiguracion(f"El valor de «{clave}» debe ser un texto.")
    return valor


def _booleano(tabla: Mapping[str, Any], clave: str) -> bool:
    valor = tabla[clave]
    if not isinstance(valor, bool):
        raise ErrorDeConfiguracion(f"El valor de «{clave}» debe ser verdadero o falso.")
    return valor


def _ajustar_bloque(bloque: BloqueColofon, ajustes: Mapping[str, Any]) -> BloqueColofon:
    """El bloque con los ajustes del archivo: `activo`, `texto` y, en los logos, el archivo."""
    conocidas = {"activo", "texto"} | ({"archivo", "alt", "placa_clara"} if bloque.logo else set())
    desconocidas = sorted(set(ajustes) - conocidas)
    if desconocidas:
        raise ErrorDeConfiguracion(
            f"El bloque «{bloque.clave}» no admite la clave «{desconocidas[0]}»."
        )
    nuevo = bloque
    if "activo" in ajustes:
        nuevo = replace(nuevo, activo=_booleano(ajustes, "activo"))
    if "texto" in ajustes:
        nuevo = replace(nuevo, texto=_texto(ajustes, "texto"))
    if nuevo.logo is not None:
        logo = nuevo.logo
        if "archivo" in ajustes:
            logo = replace(logo, ruta=Path(_texto(ajustes, "archivo")))
        if "alt" in ajustes:
            logo = replace(logo, alt=_texto(ajustes, "alt"))
        if "placa_clara" in ajustes:
            logo = replace(logo, placa_clara=_booleano(ajustes, "placa_clara"))
        nuevo = replace(nuevo, logo=logo)
    return nuevo


def _colofon(datos: Mapping[str, Any]) -> ConfiguracionColofon:
    bloques = _bloques_por_defecto()
    ajustes = {clave: _como_tabla(v) for clave, v in _como_tabla(datos).items()}
    conocidos = {b.clave for b in bloques}
    desconocidos = sorted(set(ajustes) - conocidos)
    if desconocidos:
        raise ErrorDeConfiguracion(f"El colofón no tiene un bloque «{desconocidos[0]}».")
    return ConfiguracionColofon(
        tuple(_ajustar_bloque(b, ajustes.get(b.clave, {})) for b in bloques)
    )


def _puerto(datos: Mapping[str, Any]) -> int:
    if "puerto" not in datos:
        return PUERTO_POR_DEFECTO
    puerto = datos["puerto"]
    if isinstance(puerto, bool) or not isinstance(puerto, int) or not 1 <= puerto <= 65535:
        raise ErrorDeConfiguracion("El puerto debe ser un número entero entre 1 y 65535.")
    return puerto


def cargar_configuracion(ruta: Path | None) -> Configuracion:
    """Lee la configuración de `ruta`; con `None` o si el archivo no existe, la de por defecto.

    Un archivo que no es TOML válido, una clave desconocida o un valor de tipo equivocado levantan
    `ErrorDeConfiguracion` (sin repetir los valores). El archivo solo se abre en modo lectura.
    """
    datos: dict[str, Any] = {}
    if ruta is not None and ruta.is_file():
        try:
            with open(ruta, "rb") as archivo:
                datos = tomllib.load(archivo)
        except tomllib.TOMLDecodeError as error:
            mensaje = "El archivo de configuración no es un TOML válido."
            raise ErrorDeConfiguracion(mensaje) from error
    desconocidas = sorted(set(datos) - {"puerto", "colofon"})
    if desconocidas:
        raise ErrorDeConfiguracion(f"La configuración no admite la clave «{desconocidas[0]}».")
    return Configuracion(colofon=_colofon(datos.get("colofon", {})), puerto=_puerto(datos))
