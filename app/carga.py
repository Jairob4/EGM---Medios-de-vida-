"""M16 `app.carga`: recibir el archivo y aplicar las reglas de la carga (arquitectura §6.2, M16).

El archivo llega como cuerpo crudo de la petición, nunca como formulario multiparte: el analizador
multiparte de Starlette vuelca a un archivo temporal en disco los archivos de más de 1 MiB, y
NFR-000-17 prohíbe cualquier copia (ADR-003, punto 3). El cuerpo se lee en flujo, contando bytes, y
la lectura se corta en cuanto pasa `LIMITE_BYTES`, sin leer el resto (NFR-000-19). El nombre del
archivo viaja en la cabecera `X-EGM-Nombre`, como componente de URI.

Reglas de FR-001-29, aplicadas aquí y no en las rutas:

- rechazo (tipo, tamaño o contenido) ⇒ la sesión anterior, si la hay, queda intacta;
- error de contrato ⇒ la sesión anterior termina y se limpia todo (una sola llamada a `terminar`);
- lectura aceptada ⇒ se crea la sesión o se reemplaza la existente (el filtro aplicado queda vacío).

Los bytes del archivo se sueltan al terminar: de la carga solo sobrevive el resultado inmutable en
la sesión. Este módulo no escribe nada en disco ni en los registros.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import unquote

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request

from app.sesiones import CABECERA_SESION, AlmacenSesiones, CausaFin
from egm import textos
from egm.archivo import LIMITE_BYTES
from egm.modelo import FalloContrato, Rechazo, ResultadoLectura
from egm.procesamiento import procesar

__all__ = [
    "CABECERA_NOMBRE",
    "Aceptada",
    "EstructuraInesperada",
    "Rechazada",
    "RespuestaCarga",
    "recibir",
]

CABECERA_NOMBRE = "X-EGM-Nombre"
"""Cabecera con el nombre del archivo, codificado como componente de URI."""


@dataclass(frozen=True, slots=True)
class Aceptada:
    """Lectura aceptada: la sesión abierta y si su ficha es nueva (hay que entregarla)."""

    ficha: str
    ficha_nueva: bool


@dataclass(frozen=True, slots=True)
class Rechazada:
    """Archivo rechazado antes de leerlo. `conservada` es la matriz que sigue abierta, si había."""

    rechazo: Rechazo
    conservada: ResultadoLectura | None


@dataclass(frozen=True, slots=True)
class EstructuraInesperada:
    """Error de contrato. `sesion_terminada` es verdadero si había una matriz cargada."""

    fallo: FalloContrato
    sesion_terminada: bool


RespuestaCarga = Aceptada | Rechazada | EstructuraInesperada
"""Lo que decide M16; la ruta lo convierte en la vista que corresponde."""


def _nombre_del_archivo(request: Request) -> str:
    """El nombre tal como llegó (se decodifica el componente de URI; no se altera nada más)."""
    crudo = request.headers.get(CABECERA_NOMBRE, "")
    return unquote(crudo) if crudo else textos.fijo("carga.sin_nombre")


async def _leer_cuerpo(request: Request) -> bytes | None:
    """El cuerpo completo, o `None` si pasa de `LIMITE_BYTES` (sin leer más allá del corte)."""
    declarado = request.headers.get("content-length", "")
    if declarado.isdigit() and int(declarado) > LIMITE_BYTES:
        return None
    cuerpo = bytearray()
    async for trozo in request.stream():
        cuerpo += trozo
        if len(cuerpo) > LIMITE_BYTES:
            return None
    return bytes(cuerpo)


async def recibir(
    request: Request, almacen: AlmacenSesiones, reloj: Callable[[], datetime]
) -> RespuestaCarga:
    """Recibe la carga de `POST /carga` y decide qué pasa con la sesión.

    La ficha de la sesión actual, si la hay, viene en `X-EGM-Sesion`. Una ficha que no abre
    ninguna sesión se trata como si no hubiera ficha.
    """
    ficha = request.headers.get(CABECERA_SESION, "")
    nombre = _nombre_del_archivo(request)
    contenido = await _leer_cuerpo(request)
    try:
        if contenido is None:
            resultado: ResultadoLectura | Rechazo | FalloContrato = Rechazo("tamano")
        else:
            resultado = await run_in_threadpool(procesar, contenido, nombre, reloj())
    finally:
        del contenido  # los bytes del archivo se sueltan aquí; solo queda el resultado
    # La sesión se mira después de leer: pudo terminar mientras se procesaba el archivo.
    previa = almacen.obtener(ficha) if ficha else None
    if isinstance(resultado, Rechazo):
        return Rechazada(resultado, previa.resultado if previa else None)
    if isinstance(resultado, FalloContrato):
        if previa is not None:
            almacen.terminar(ficha, CausaFin.ERROR_DE_CONTRATO)
        return EstructuraInesperada(resultado, previa is not None)
    if previa is not None:
        almacen.reemplazar(ficha, resultado)
        return Aceptada(ficha, False)
    return Aceptada(almacen.crear(resultado), True)
