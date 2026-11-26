"""M21 `app.colofon`: el colofón compuesto por bloques con bandera (arquitectura M21; ADR-005).

Dos bloques están siempre presentes y no se configuran: «Datos» (NFR-000-12, armado en tiempo de
ejecución) y «Referencia de diseño» de 3ie (NFR-000-16). Los nueve bloques configurables vienen
apagados por defecto (`app.configuracion`) y se encienden uno a uno. Reglas de composición
(ADR-005, punto 3):

- un bloque apagado no deja rastro en el HTML: no entra en el modelo de vista;
- un bloque encendido cuyo texto lleva una marca de pendiente de confirmación se omite completo;
- un bloque de logo encendido cuyo archivo no existe se omite completo (imagen y texto
  alternativo) y deja un registro técnico sin datos;
- sin matriz cargada, «Datos» no muestra cifras (US-001-4.2).

Los textos institucionales llegan en la configuración; los de los dos bloques fijos, del catálogo
de `egm.textos` (M10). La plantilla solo dibuja el modelo de vista.
"""

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from egm import textos
from egm.modelo import Identificacion

__all__ = [
    "CARPETA_DE_LOGOS",
    "BloqueColofon",
    "ConfiguracionColofon",
    "Logo",
    "VistaBloqueColofon",
    "VistaColofon",
    "VistaLogo",
    "componer",
]

_registro = logging.getLogger(__name__)

CARPETA_DE_LOGOS: Final[Path] = Path(__file__).resolve().parent / "estaticos" / "logos"
"""Carpeta de los logos: se sirven desde `/estaticos/logos/`; se buscan por nombre de archivo."""

URL_DE_LOGOS: Final = "/estaticos/logos/"

# Marca de pendiente de confirmación: «[POR CONFIRMAR …]» (pie-de-pagina.md) o un `[NEEDS
# CLARIFICATION: …]` que haya quedado dentro de un texto.
_PENDIENTE: Final = re.compile(r"\[\s*(POR CONFIRMAR|NEEDS CLARIFICATION)", re.IGNORECASE)

# Los bloques que van antes de «Datos» y de la referencia; el resto (contacto, logos) va después
# (orden de pie-de-pagina.md).
_ANTES_DE_DATOS: Final = frozenset(
    {"proyecto", "grupo", "codigo_minciencias", "semillero", "equipo", "herramienta"}
)


@dataclass(frozen=True, slots=True)
class Logo:
    """Un logo: su archivo (por nombre, dentro de `CARPETA_DE_LOGOS`), texto alternativo y placa."""

    ruta: Path
    alt: str
    placa_clara: bool


@dataclass(frozen=True, slots=True)
class BloqueColofon:
    """Un bloque configurable: clave, bandera, texto y, si lo lleva, logo."""

    clave: str
    activo: bool
    texto: str | None
    logo: Logo | None


@dataclass(frozen=True, slots=True)
class ConfiguracionColofon:
    """Los bloques configurables, en el orden de `pie-de-pagina.md` (sin «Datos» ni referencia)."""

    bloques: tuple[BloqueColofon, ...]


@dataclass(frozen=True, slots=True)
class VistaLogo:
    """Un logo listo para dibujar: URL local, texto alternativo y si va sobre placa clara."""

    ruta: str
    alt: str
    placa_clara: bool


@dataclass(frozen=True, slots=True)
class VistaBloqueColofon:
    """Un bloque visible. `rotulo` se dibuja en negrita, seguido de un punto."""

    clave: str
    rotulo: str | None
    texto: str | None
    logo: VistaLogo | None


@dataclass(frozen=True, slots=True)
class VistaColofon:
    """Solo los bloques visibles, en orden."""

    bloques: tuple[VistaBloqueColofon, ...]


def _logo_visible(bloque: BloqueColofon, logo: Logo, carpeta: Path) -> VistaLogo | None:
    """El logo si su archivo existe; si no, `None` y un registro técnico sin datos."""
    nombre = logo.ruta.name
    if not nombre or not (carpeta / nombre).is_file():
        _registro.warning("Logo del colofón sin archivo: bloque %s", bloque.clave)
        return None
    return VistaLogo(URL_DE_LOGOS + nombre, logo.alt, logo.placa_clara)


def _bloque_visible(bloque: BloqueColofon, carpeta: Path) -> VistaBloqueColofon | None:
    """El bloque configurable como vista, o `None` si se omite (apagado, pendiente o sin logo)."""
    if not bloque.activo:
        return None
    if bloque.texto is not None and _PENDIENTE.search(bloque.texto):
        return None
    logo = None
    if bloque.logo is not None:
        logo = _logo_visible(bloque, bloque.logo, carpeta)
        if logo is None:
            return None
    if logo is None and not bloque.texto:
        return None
    return VistaBloqueColofon(bloque.clave, None, bloque.texto or None, logo)


def _bloque_datos(ident: Identificacion | None, n_documentos: int | None) -> VistaBloqueColofon:
    if ident is None or n_documentos is None:
        texto = textos.fijo("colofon.datos.sin_matriz")
    else:
        texto = f"{textos.cabecera_corrida(ident, n_documentos)}."
    return VistaBloqueColofon("datos", textos.fijo("colofon.datos.rotulo"), texto, None)


def _bloque_referencia() -> VistaBloqueColofon:
    return VistaBloqueColofon(
        "referencia_diseno",
        textos.fijo("colofon.referencia.rotulo"),
        textos.fijo("colofon.referencia.texto"),
        None,
    )


def componer(
    config: ConfiguracionColofon,
    ident: Identificacion | None,
    n_documentos: int | None,
    carpeta_de_logos: Path = CARPETA_DE_LOGOS,
) -> VistaColofon:
    """Compone el colofón: bloques encendidos y presentables, «Datos» y la referencia a 3ie.

    `ident` y `n_documentos` son los de la matriz cargada, o `None` sin matriz (entonces «Datos»
    dice «Aún no se ha cargado ninguna matriz.», sin cifras). El orden es el de `pie-de-pagina.md`:
    proyecto, grupo, código, semillero, equipo y herramienta; «Datos» y la referencia; contacto y
    logos. `carpeta_de_logos` solo la cambian las pruebas.
    """
    visibles: Sequence[VistaBloqueColofon | None] = [
        _bloque_visible(b, carpeta_de_logos) for b in config.bloques
    ]
    antes = [
        v
        for b, v in zip(config.bloques, visibles, strict=True)
        if v is not None and b.clave in _ANTES_DE_DATOS
    ]
    despues = [
        v
        for b, v in zip(config.bloques, visibles, strict=True)
        if v is not None and b.clave not in _ANTES_DE_DATOS
    ]
    fijos = [_bloque_datos(ident, n_documentos), _bloque_referencia()]
    return VistaColofon((*antes, *fijos, *despues))
