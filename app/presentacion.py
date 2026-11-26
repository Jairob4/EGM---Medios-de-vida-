"""M17 `app.presentacion`: los modelos de vista de la capa web (arquitectura §6.2, M17).

Convierte los resultados del núcleo en modelos de vista **inmutables** que las plantillas
(`app/plantillas`, M18) dibujan sin calcular ni formatear nada: los textos los arma `egm.textos`
(M10), el colofón lo compone `app.colofon` (M21) y aquí solo se ordenan y se reúnen. Esta parte
(plan 001, Fase 7) cubre el inicio (V0), los mensajes de carga (V1), la cabecera corrida, los avisos
de lectura (V2, antes de cualquier cifra), la vista provisional del resultado (NC-P001-1) y el
colofón. Los planes 002 y 003 agregan el mapa, la ficha, los filtros y el tablero.

Los nombres `Vista*` y sus campos son los que declaran en su cabecera las plantillas del
`disenador-front`; cada campo está descrito allí. La arquitectura no fija estos nombres.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Final, Literal, cast

from app.colofon import ConfiguracionColofon, VistaColofon, componer
from app.sesiones import AVISO_INACTIVIDAD, INACTIVIDAD, CausaFin
from egm import textos
from egm.archivo import LIMITE_BYTES
from egm.modelo import FalloContrato, Rechazo, ResultadoLectura
from egm.verificacion import Verificacion

__all__ = [
    "DESTINO_RESULTADO",
    "VistaAvisoInactividad",
    "VistaAvisos",
    "VistaCabecera",
    "VistaEnlace",
    "VistaInicio",
    "VistaLimite",
    "VistaMensaje",
    "VistaPagina",
    "VistaResultado",
    "cabecera_de",
    "colofon_de",
    "vista_avisos",
    "vista_inicio",
    "vista_mensaje_error_contrato",
    "vista_mensaje_fin_de_sesion",
    "vista_mensaje_rechazo",
    "vista_pagina",
    "vista_resultado",
]

DESTINO_RESULTADO: Final = "/vista/resultado"
"""Ruta del fragmento del resultado (plan 001); el plan 002 la convierte en la página del mapa."""

_BYTES_POR_MB: Final = 1024 * 1024


@dataclass(frozen=True, slots=True)
class VistaEnlace:
    """Un enlace que htmx resuelve con un GET del fragmento `destino` (`cabecera.html`)."""

    rotulo: str
    destino: str
    actual: bool = False


@dataclass(frozen=True, slots=True)
class VistaAvisoInactividad:
    """E7 (`aviso-inactividad.html`): lo que dice el aviso; el guion lo muestra a los 43 minutos."""

    texto: str
    tiempo: str
    boton: str


@dataclass(frozen=True, slots=True)
class VistaCabecera:
    """La cabecera corrida con matriz: el texto de NFR-000-12, la navegación (vacía en el 001) y
    el aviso de inactividad (E7), que solo existe mientras hay una matriz abierta."""

    corte: str
    vistas: tuple[VistaEnlace, ...] = ()
    aviso: VistaAvisoInactividad | None = None


@dataclass(frozen=True, slots=True)
class VistaMensaje:
    """Un mensaje de carga o de sesión (`mensaje.html`): rol, título y párrafos por separado."""

    rol: Literal["alert", "status"]
    titulo: str | None
    parrafos: tuple[str, ...]
    enlace: VistaEnlace | None = None


@dataclass(frozen=True, slots=True)
class VistaLimite:
    """El límite de tamaño ya formateado, a partir de `LIMITE_BYTES` (`inicio.html`)."""

    mb: str
    bytes: str


@dataclass(frozen=True, slots=True)
class VistaAvisos:
    """V2, «Antes de leer los resultados»: verificación, advertencias y notas, en ese orden."""

    verificacion: textos.TextoVerificacion
    rotulo_advertencias: str
    advertencias: tuple[str, ...]
    notas: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VistaResultado:
    """La vista provisional del resultado de una carga aceptada (NC-P001-1)."""

    titulo: str
    introduccion: str | None
    avisos: VistaAvisos


@dataclass(frozen=True, slots=True)
class VistaInicio:
    """V0: lo que dibuja `inicio.html`. Sin matriz, `cabecera` es `None` y no hay cifras."""

    mensaje: VistaMensaje | None
    limite: VistaLimite
    volver: VistaEnlace | None
    cabecera: VistaCabecera | None
    colofon: VistaColofon


@dataclass(frozen=True, slots=True)
class VistaPagina:
    """La página base (`GET /`): cabecera vacía y colofón sin matriz, sin datos."""

    cabecera: VistaCabecera | None
    colofon: VistaColofon


def _limite() -> VistaLimite:
    """«15» y «15 728 640», calculados de `LIMITE_BYTES` (nunca escritos a mano)."""
    return VistaLimite(
        mb=str(LIMITE_BYTES // _BYTES_POR_MB), bytes=f"{LIMITE_BYTES:,}".replace(",", " ")
    )


def _aviso_de_inactividad() -> VistaAvisoInactividad:
    """E7; los minutos que restan al aviso son los de la sesión menos los del aviso (45 − 43)."""
    minutos = (INACTIVIDAD - AVISO_INACTIVIDAD) // timedelta(minutes=1)
    return VistaAvisoInactividad(
        texto=textos.aviso_inactividad(minutos),
        tiempo=textos.fijo("sesion.e7.tiempo"),
        boton=textos.fijo("sesion.e7.boton"),
    )


def cabecera_de(resultado: ResultadoLectura | None) -> VistaCabecera | None:
    """La cabecera corrida de la matriz cargada (NFR-000-12), o `None` sin matriz."""
    if resultado is None:
        return None
    return VistaCabecera(
        textos.cabecera_corrida(resultado.identificacion, len(resultado.corpus.documentos)),
        aviso=_aviso_de_inactividad(),
    )


def colofon_de(config: ConfiguracionColofon, resultado: ResultadoLectura | None) -> VistaColofon:
    """El colofón con el bloque «Datos» de la matriz cargada, o sin matriz y sin cifras."""
    if resultado is None:
        return componer(config, None, None)
    return componer(config, resultado.identificacion, len(resultado.corpus.documentos))


def vista_avisos(resultado: ResultadoLectura) -> VistaAvisos:
    """Los avisos de V2: la verificación, las advertencias (en el orden del núcleo) y las notas."""
    verificacion = textos.verificacion(cast(Verificacion, resultado.verificacion))
    advertencias = tuple(textos.advertencia(a) for a in resultado.advertencias)
    return VistaAvisos(
        verificacion=verificacion,
        rotulo_advertencias=textos.rotulo_advertencias(len(advertencias)),
        advertencias=advertencias,
        notas=tuple(textos.nota(n) for n in resultado.notas),
    )


def vista_resultado(resultado: ResultadoLectura) -> VistaResultado:
    """La vista del resultado: título y avisos de lectura; las cifras llegan con el plan 002."""
    return VistaResultado(
        titulo=textos.fijo("resultado.titulo"),
        introduccion=None,
        avisos=vista_avisos(resultado),
    )


def _enlace_volver() -> VistaEnlace:
    return VistaEnlace(textos.fijo("mensaje.volver"), DESTINO_RESULTADO)


def vista_mensaje_rechazo(rechazo: Rechazo, conservada: ResultadoLectura | None) -> VistaMensaje:
    """E2, E3 o E10; con matriz previa agrega su cabecera y el enlace «Volver al mapa»."""
    cabecera = cabecera_de(conservada)
    texto = textos.mensaje_rechazo(rechazo, cabecera.corte if cabecera else None)
    return VistaMensaje(
        rol="alert",
        titulo=texto.titulo,
        parrafos=texto.parrafos,
        enlace=_enlace_volver() if cabecera else None,
    )


def vista_mensaje_error_contrato(fallo: FalloContrato, sesion_terminada: bool) -> VistaMensaje:
    """E4, con o sin matriz previa (con ella, la sesión terminó)."""
    texto = textos.mensaje_error_contrato(fallo, sesion_terminada)
    return VistaMensaje(rol="alert", titulo=texto.titulo, parrafos=texto.parrafos)


def vista_mensaje_fin_de_sesion(causa: CausaFin) -> VistaMensaje:
    """E8 (flujos.md §2): «Descartó el archivo…» o «La sesión terminó porque pasaron 45 minutos…».

    Sin título y sin cifras; se anuncia como estado, no como alerta. Solo hay texto para el descarte
    y la inactividad: las otras dos formas de terminar no muestran este mensaje.
    """
    clave = {CausaFin.DESCARTE: "sesion.e8.descarte", CausaFin.INACTIVIDAD: "sesion.e8.inactividad"}
    return VistaMensaje(rol="status", titulo=None, parrafos=(textos.fijo(clave[causa]),))


def vista_inicio(
    config: ConfiguracionColofon,
    mensaje: VistaMensaje | None = None,
    resultado: ResultadoLectura | None = None,
) -> VistaInicio:
    """V0 con la opción de cargar y el límite indicado.

    `resultado` es la matriz de la sesión abierta, si la hay (cuando la persona pulsa «Cargar otro
    archivo»): entonces lleva su cabecera, su colofón y el enlace para volver. Sin él, sin cifras.
    """
    return VistaInicio(
        mensaje=mensaje,
        limite=_limite(),
        volver=_enlace_volver() if resultado is not None else None,
        cabecera=cabecera_de(resultado),
        colofon=colofon_de(config, resultado),
    )


def vista_pagina(config: ConfiguracionColofon) -> VistaPagina:
    """La página base, sin datos (`GET /`)."""
    return VistaPagina(cabecera=None, colofon=colofon_de(config, None))
