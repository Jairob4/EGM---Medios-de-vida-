"""M14 `app.servidor`: la aplicación ASGI (arquitectura §6.2, M14; ADR-003).

FastAPI sobre Starlette, servida por Uvicorn en un solo proceso y solo en `127.0.0.1`. Este módulo
solo orquesta: llama a `app.carga` (M16), a `app.sesiones` (M15) y a `app.presentacion` (M17) y
dibuja con las plantillas (M18). Ningún cálculo vive aquí.

Rutas del plan 001: `GET /`, `GET /vista/inicio`, `POST /carga`, `GET /vista/resultado`,
`GET /estaticos/...` y las de la sesión (Fase 8): `POST /sesion/descartar`, `POST /sesion/latido` y
`POST /sesion/cierre`. Las de los planes 002 y 003 se agregan con `ampliaciones` de `crear_app`,
que reciben la aplicación y los servicios.

Toda petición con una ficha vigente cuenta como actividad (ADR-003, punto 5) y anula un aviso de
cierre pendiente (la ficha volvió; punto 9). Una tarea periódica, atada al ciclo de vida de la
aplicación, purga las sesiones vencidas con el reloj inyectado.

Las URL nunca llevan texto de la matriz. La ficha de sesión viaja en `X-EGM-Sesion`, nunca en una
cookie.

Política de registros (NFR-000-17, arquitectura M14): sin registro de accesos; nunca el cuerpo ni
las cabeceras de una petición; un error interno se registra solo por su tipo y el módulo donde
ocurrió, sin su mensaje (puede contener el valor de una celda) ni su traza. La persona recibe un
texto fijo.

Cabeceras de seguridad: la política de contenido solo admite recursos de la propia aplicación y
ningún estilo ni guion en línea (ADR-003, punto 6; NFR-000-15).
"""

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

import uvicorn
from fastapi import FastAPI
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.requests import ClientDisconnect, Request
from starlette.responses import HTMLResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app import carga, presentacion
from app.carga import Aceptada, EstructuraInesperada, Rechazada
from app.configuracion import RUTA_DE_CONFIGURACION, Configuracion, cargar_configuracion
from app.sesiones import CABECERA_SESION, AlmacenSesiones, CausaFin, Sesion
from egm import textos

__all__ = [
    "CABECERA_DESTINO",
    "INTERVALO_DE_PURGA",
    "Servicios",
    "crear_app",
    "main",
    "renderizar",
]

_registro = logging.getLogger(__name__)

_RAIZ: Final = Path(__file__).resolve().parent
CARPETA_DE_PLANTILLAS: Final = _RAIZ / "plantillas"
CARPETA_DE_ESTATICOS: Final = _RAIZ / "estaticos"
CARPETA_DEL_CLIENTE: Final = _RAIZ / "cliente"

CABECERA_DESTINO: Final = "X-EGM-Destino"
"""Dónde coloca el guion el fragmento que responde `POST /carga`: `contenido` (reemplaza la vista) o
`mensajes` (un rechazo que no cambia de vista)."""

INTERVALO_DE_PURGA: Final = timedelta(seconds=5)
"""Cada cuánto corre la purga de sesiones vencidas. Una sesión vencida no se sirve de todos modos
(M15 la termina al mirarla); la purga solo suelta la memoria."""

HOST: Final = "127.0.0.1"
"""Solo el equipo local (NFR-000-15)."""

POLITICA_DE_CONTENIDO: Final = (
    "default-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; "
    "form-action 'self'; frame-ancestors 'none'"
)
_CABECERAS_DE_SEGURIDAD: Final = {
    "Content-Security-Policy": POLITICA_DE_CONTENIDO,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


@dataclass(frozen=True, slots=True)
class Servicios:
    """Lo que las rutas comparten: configuración, almacén de sesiones, reloj y plantillas."""

    config: Configuracion
    almacen: AlmacenSesiones
    reloj: Callable[[], datetime]
    plantillas: Environment


Ampliacion = Callable[[FastAPI, Servicios], None]
"""Cómo los planes 002 y 003 agregan sus rutas sobre `crear_app`."""


def _entorno_de_plantillas() -> Environment:
    """Jinja2 con autoescape y sin variables sin definir en silencio."""
    return Environment(
        loader=FileSystemLoader(CARPETA_DE_PLANTILLAS),
        autoescape=True,
        undefined=StrictUndefined,
        auto_reload=False,
    )


def renderizar(
    servicios: Servicios,
    plantilla: str,
    contexto: dict[str, Any],
    estado: int = 200,
    cabeceras: dict[str, str] | None = None,
) -> HTMLResponse:
    """Dibuja una plantilla con su contexto (modelos de vista) en una respuesta HTML."""
    texto = servicios.plantillas.get_template(plantilla).render(**contexto)
    return HTMLResponse(texto, status_code=estado, headers=cabeceras)


# --- Registros y cabeceras ----------------------------------------------------------------------


def _modulo_del_error(error: BaseException) -> str:
    """El módulo donde ocurrió el error: el más profundo de la aplicación o del núcleo."""
    modulo = "desconocido"
    propio = None
    traza = error.__traceback__
    while traza is not None:
        nombre = str(traza.tb_frame.f_globals.get("__name__", modulo))
        modulo = nombre
        if nombre.startswith(("app.", "egm.")):
            propio = nombre
        traza = traza.tb_next
    return propio or modulo


class Resguardo:
    """Middleware ASGI: cabeceras de seguridad en toda respuesta y errores sin filtraciones."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        estatico = scope["path"].startswith("/estaticos/")
        iniciada = False

        async def enviar(mensaje: Message) -> None:
            nonlocal iniciada
            if mensaje["type"] == "http.response.start":
                iniciada = True
                cabeceras = MutableHeaders(scope=mensaje)
                for nombre, valor in _CABECERAS_DE_SEGURIDAD.items():
                    cabeceras[nombre] = valor
                if not estatico:
                    cabeceras["Cache-Control"] = "no-store"
            await send(mensaje)

        try:
            await self.app(scope, receive, enviar)
        except Exception as error:
            # Solo el tipo y el módulo: el mensaje y la traza pueden traer valores de celdas.
            _registro.error(
                "Error interno: tipo %s, módulo %s", type(error).__name__, _modulo_del_error(error)
            )
            if not iniciada:
                respuesta = Response(
                    textos.fijo("mensaje.problema"),
                    status_code=500,
                    media_type="text/plain",
                )
                await respuesta(scope, receive, enviar)


# --- Rutas --------------------------------------------------------------------------------------


def _ficha_de(request: Request) -> str:
    return request.headers.get(CABECERA_SESION, "")


def _sesion_de(request: Request, servicios: Servicios) -> Sesion | None:
    """La sesión de la ficha de la petición, o `None` (sin ficha o con una que no abre nada).

    La petición cuenta como actividad (ADR-003, punto 5) y, si había un aviso de cierre pendiente,
    lo anula: la ficha volvió (punto 9).
    """
    ficha = _ficha_de(request)
    if not ficha or not servicios.almacen.registrar_actividad(ficha):
        return None
    return servicios.almacen.obtener(ficha)


def _fin_por_inactividad(
    request: Request, servicios: Servicios
) -> presentacion.VistaMensaje | None:
    """E8 de inactividad, si la ficha de la petición es de una sesión terminada por inactividad."""
    ficha = _ficha_de(request)
    if ficha and servicios.almacen.consumir_fin_por_inactividad(ficha):
        return presentacion.vista_mensaje_fin_de_sesion(CausaFin.INACTIVIDAD)
    return None


def _responder_inicio(
    servicios: Servicios,
    sesion: Sesion | None,
    mensaje: presentacion.VistaMensaje | None = None,
    estado: int = 200,
    cabeceras: dict[str, str] | None = None,
) -> HTMLResponse:
    vista = presentacion.vista_inicio(
        servicios.config.colofon, mensaje, sesion.resultado if sesion else None
    )
    return renderizar(
        servicios,
        "inicio.html",
        {
            "mensaje": vista.mensaje,
            "limite": vista.limite,
            "volver": vista.volver,
            "cabecera": vista.cabecera,
            "colofon": vista.colofon,
        },
        estado,
        cabeceras,
    )


def _responder_resultado(
    servicios: Servicios, sesion: Sesion, cabeceras: dict[str, str] | None = None
) -> HTMLResponse:
    resultado = sesion.resultado
    return renderizar(
        servicios,
        "resultado.html",
        {
            "resultado": presentacion.vista_resultado(resultado),
            "cabecera": presentacion.cabecera_de(resultado),
            "colofon": presentacion.colofon_de(servicios.config.colofon, resultado),
        },
        cabeceras=cabeceras,
    )


def _responder_carga(servicios: Servicios, respuesta: carga.RespuestaCarga) -> Response:
    """Convierte la decisión de M16 en el fragmento que corresponde (plan 001, tabla de rutas)."""
    if isinstance(respuesta, Aceptada):
        sesion = servicios.almacen.obtener(respuesta.ficha)
        if sesion is None:  # terminó entre la carga y la respuesta; no hay nada que mostrar
            return _responder_inicio(servicios, None, cabeceras={CABECERA_DESTINO: "contenido"})
        cabeceras = {CABECERA_DESTINO: "contenido"}
        if respuesta.ficha_nueva:
            cabeceras[CABECERA_SESION] = respuesta.ficha
        return _responder_resultado(servicios, sesion, cabeceras)
    if isinstance(respuesta, Rechazada):
        mensaje = presentacion.vista_mensaje_rechazo(respuesta.rechazo, respuesta.conservada)
        estado = 413 if respuesta.rechazo.motivo == "tamano" else 422
        return renderizar(
            servicios, "mensaje.html", {"mensaje": mensaje}, estado, {CABECERA_DESTINO: "mensajes"}
        )
    assert isinstance(respuesta, EstructuraInesperada)
    mensaje = presentacion.vista_mensaje_error_contrato(respuesta.fallo, respuesta.sesion_terminada)
    if respuesta.sesion_terminada:  # la matriz previa ya no está: se vuelve a la carga
        return _responder_inicio(servicios, None, mensaje, 422, {CABECERA_DESTINO: "contenido"})
    return renderizar(
        servicios, "mensaje.html", {"mensaje": mensaje}, 422, {CABECERA_DESTINO: "mensajes"}
    )


def _registrar_rutas(app: FastAPI, servicios: Servicios) -> None:
    async def pagina(request: Request) -> Response:
        vista = presentacion.vista_pagina(servicios.config.colofon)
        return renderizar(
            servicios, "base.html", {"cabecera": vista.cabecera, "colofon": vista.colofon}
        )

    async def inicio(request: Request) -> Response:
        sesion = _sesion_de(request, servicios)
        mensaje = None if sesion else _fin_por_inactividad(request, servicios)
        return _responder_inicio(servicios, sesion, mensaje)

    async def resultado(request: Request) -> Response:
        sesion = _sesion_de(request, servicios)
        if sesion is None:  # sin sesión: la vista de carga, sin cifras (E9; E8 si fue inactividad)
            return _responder_inicio(servicios, None, _fin_por_inactividad(request, servicios))
        return _responder_resultado(servicios, sesion)

    async def cargar(request: Request) -> Response:
        servicios.almacen.registrar_actividad(_ficha_de(request))
        try:
            respuesta = await carga.recibir(request, servicios.almacen, servicios.reloj)
        except ClientDisconnect:
            return Response(status_code=400)
        return _responder_carga(servicios, respuesta)

    async def descartar(request: Request) -> Response:
        """FR-001-28: termina la sesión de inmediato y vuelve a la carga con E8 (US-001-5.1)."""
        ficha = _ficha_de(request)
        mensaje: presentacion.VistaMensaje | None
        if ficha and servicios.almacen.obtener(ficha) is not None:
            servicios.almacen.terminar(ficha, CausaFin.DESCARTE)
            mensaje = presentacion.vista_mensaje_fin_de_sesion(CausaFin.DESCARTE)
        else:  # nada que descartar: no se afirma que se descartó algo
            mensaje = _fin_por_inactividad(request, servicios)
        return _responder_inicio(
            servicios, None, mensaje, cabeceras={CABECERA_DESTINO: "contenido"}
        )

    async def latido(request: Request) -> Response:
        """NFR-000-17: registra actividad; 410 si la ficha ya no abre ninguna sesión."""
        ficha = _ficha_de(request)
        vigente = bool(ficha) and servicios.almacen.registrar_actividad(ficha)
        return Response(status_code=204 if vigente else 410)

    async def cierre(request: Request) -> Response:
        """ADR-003, punto 9: aviso de cierre de pestaña. Responde igual con o sin sesión."""
        servicios.almacen.avisar_cierre(_ficha_de(request))
        return Response(status_code=204)

    app.add_api_route("/", pagina, methods=["GET"], include_in_schema=False)
    app.add_api_route("/vista/inicio", inicio, methods=["GET"], include_in_schema=False)
    app.add_api_route("/vista/resultado", resultado, methods=["GET"], include_in_schema=False)
    app.add_api_route("/carga", cargar, methods=["POST"], include_in_schema=False)
    app.add_api_route("/sesion/descartar", descartar, methods=["POST"], include_in_schema=False)
    app.add_api_route("/sesion/latido", latido, methods=["POST"], include_in_schema=False)
    app.add_api_route("/sesion/cierre", cierre, methods=["POST"], include_in_schema=False)


async def _purgar_periodicamente(servicios: Servicios) -> None:
    """Purga las sesiones vencidas cada `INTERVALO_DE_PURGA`; un fallo no detiene la tarea."""
    while True:
        await asyncio.sleep(INTERVALO_DE_PURGA.total_seconds())
        try:
            servicios.almacen.purgar_vencidas(servicios.reloj())
        except Exception as error:
            # Como en `Resguardo`: solo el tipo y el módulo, nunca el mensaje ni la traza.
            _registro.error(
                "Error interno: tipo %s, módulo %s", type(error).__name__, _modulo_del_error(error)
            )


@asynccontextmanager
async def _ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    """La tarea de purga vive mientras viva la aplicación (`app.state.purga`)."""
    tarea = asyncio.create_task(_purgar_periodicamente(app.state.servicios))
    app.state.purga = tarea
    try:
        yield
    finally:
        tarea.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tarea


def crear_app(
    config: Configuracion,
    reloj: Callable[[], datetime] | None = None,
    ampliaciones: Sequence[Ampliacion] = (),
) -> FastAPI:
    """Arma la aplicación: rutas, estáticos locales, cabeceras de seguridad y registros.

    `reloj` da la fecha de lectura de cada carga (por defecto, la hora local del equipo); las
    pruebas inyectan uno propio. `ampliaciones` agregan rutas: cada una recibe la aplicación y los
    `Servicios` (planes 002 y 003). Los servicios quedan en `app.state.servicios`.
    """
    reloj = reloj if reloj is not None else datetime.now
    servicios = Servicios(config, AlmacenSesiones(reloj), reloj, _entorno_de_plantillas())
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=_ciclo_de_vida,
        middleware=[Middleware(Resguardo)],
    )
    app.state.servicios = servicios
    _registrar_rutas(app, servicios)
    for ampliacion in ampliaciones:
        ampliacion(app, servicios)
    # El cliente (M19) se monta antes: la ruta más específica gana. Las carpetas pueden no existir.
    app.mount(
        "/estaticos/cliente",
        StaticFiles(directory=CARPETA_DEL_CLIENTE, check_dir=False),
        name="cliente",
    )
    app.mount(
        "/estaticos",
        StaticFiles(directory=CARPETA_DE_ESTATICOS, check_dir=False),
        name="estaticos",
    )
    return app


def main() -> None:
    """`python -m app.servidor`: Uvicorn, un proceso, solo en 127.0.0.1, sin registro de accesos."""
    config = cargar_configuracion(RUTA_DE_CONFIGURACION)
    uvicorn.run(
        crear_app(config),
        host=HOST,
        port=config.puerto,
        access_log=False,
        server_header=False,
    )


if __name__ == "__main__":
    main()
