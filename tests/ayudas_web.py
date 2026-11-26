"""Ayudas de las pruebas de la capa web (plan 001, Fase 7; los planes 002 y 003 las reutilizan).

Centraliza las suposiciones de interfaz que la arquitectura y los flujos no fijan, para que un
cambio de nombre se corrija en un solo lugar. Cada una está marcada `[NEEDS CLARIFICATION]`:

- `CAB_SESION`: nombre de la cabecera de la ficha, tanto en las peticiones (ADR-003, punto 4) como
  en la respuesta de `POST /carga` («con la ficha nueva en la cabecera de la respuesta», plan 001,
  tabla de rutas). El plan solo fija el nombre de la petición; se supone el mismo en la respuesta.
- `crear_app(config, reloj=...)`: la arquitectura fija `crear_app(config)`; la inyección del reloj
  (P-001-91, «reloj inyectado») se supone como parámetro `reloj` que devuelve un `datetime`.
- `dataclasses.replace(config, colofon=...)`: campo `colofon` de `Configuracion` (M22) que lleva el
  `ConfiguracionColofon` de M21; la arquitectura no nombra el campo.

Los módulos de la capa web se importan por su espacio de nombres y se usan dentro de las funciones:
mientras la capa no exista falla la prueba, no la recolección. Los esperados de texto se escriben a
mano en las pruebas a partir de `docs/interfaz/flujos.md` §2, §3 y §6.
"""

import functools
import os
import re
import socket
import tempfile
import threading
import time
import traceback
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import quote

from tests.constructor import MatrizSintetica, carpeta_de_fixtures

CAB_SESION = "X-EGM-Sesion"
CAB_NOMBRE = "X-EGM-Nombre"

FECHA_LECTURA = datetime(2026, 11, 25, 9, 30)
FECHA_LECTURA_TEXTO = "25 de noviembre de 2026"

LIMITE_BYTES = 15_728_640
LIMITE_DESCOMPRIMIDO = 268_435_456

# Esperados escritos a mano a partir de flujos.md §2 (E2, E3, E10, E4) y §6 (colofón).
TITULO_RECHAZO = "No se pudo cargar el archivo"
CUERPO_E2 = (
    "El archivo elegido no es un archivo de Excel (.xlsx) que la herramienta pueda abrir, o está "
    "dañado. No se leyó y no se muestra ningún resultado. Elija la matriz bibliográfica en "
    "formato .xlsx."
)
CUERPO_E3 = (
    "El archivo pesa más de 15 MB (15 728 640 bytes), el máximo que admite la herramienta. No se "
    "leyó y no se muestra ningún resultado de ese archivo."
)
CUERPO_E10 = (
    "El contenido del libro es demasiado grande para abrirlo. No se leyó y no se muestra ningún "
    "resultado de ese archivo."
)
TITULO_E4 = "No se pudo leer la matriz"
TITULO_E4_PREVIA = "No se pudo leer la matriz y la sesión terminó"
CIERRE_E4 = "Revise que el archivo sea la matriz bibliográfica del proyecto y vuelva a cargarlo."
BORRO_TODO = (
    "La herramienta borró todo: la matriz que tenía cargada y sus resultados ya no están "
    "disponibles. Para volver a verlos, cárguela otra vez."
)
SIGUE_DISPONIBLE = "La matriz que tenía cargada sigue disponible con sus resultados: "
COLOFON_SIN_MATRIZ = "Datos. Aún no se ha cargado ninguna matriz."
COLOFON_REFERENCIA = (
    "Referencia de diseño. International Initiative for Impact Evaluation (3ie). Building "
    "Peaceful Societies Evidence Gap Map (2019). Licencia CC BY-NC-SA 4.0. Se toma solo como "
    "referencia de diseño; no se reproduce su contenido."
)

# Una cifra de resultado: el número de documentos, estudios o celdas (no el límite de tamaño).
CIFRA_DE_RESULTADO = re.compile(r"\b\d+\s+(documentos?|estudios?|celdas?)\b")
CABECERA = re.compile(r"Matriz: (?P<nombre>.+?), leída el (?P<fecha>.+?), (?P<n>\d+) documentos")


def cabecera_esperada(nombre: str, n_documentos: int, fecha: str = FECHA_LECTURA_TEXTO) -> str:
    """«Matriz: <nombre>, leída el <fecha>, <n> documentos» (NFR-000-12), escrito a mano."""
    return f"Matriz: {nombre}, leída el {fecha}, {n_documentos} documentos"


# --- Fixtures ---------------------------------------------------------------------------------


@functools.cache
def fixture(nombre: str) -> bytes:
    """Los bytes de un fixture de `data/fixtures/` (solo lectura)."""
    with open(carpeta_de_fixtures() / nombre, "rb") as archivo:
        return archivo.read()


@functools.cache
def exacto_en_bytes(tamano: int) -> bytes:
    """Una matriz válida de exactamente `tamano` bytes (CB-16, en memoria)."""
    return MatrizSintetica.base_valida().a_bytes_de_tamano(tamano)


@functools.cache
def descomprimido_declarado(declarado: int) -> bytes:
    """Un libro válido cuyo índice declara `declarado` bytes descomprimidos (CB-17, en memoria)."""
    return MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(declarado)


# --- Reloj y aplicación -----------------------------------------------------------------------


class Reloj:
    """Reloj inyectable: devuelve siempre la misma hora hasta que la prueba lo avanza."""

    def __init__(self, ahora: datetime = FECHA_LECTURA) -> None:
        self.ahora = ahora

    def __call__(self) -> datetime:
        return self.ahora

    def avanzar(self, **delta: float) -> None:
        self.ahora += timedelta(**delta)


def crear_app(config: Any | None = None, reloj: Callable[[], datetime] | None = None) -> Any:
    """`app.servidor.crear_app` con la configuración por defecto y el reloj inyectado."""
    from app import servidor
    from app.configuracion import cargar_configuracion

    return servidor.crear_app(
        config if config is not None else cargar_configuracion(None),
        reloj=reloj if reloj is not None else Reloj(),
    )


def cliente_de(app: Any) -> Any:
    """Cliente de pruebas de Starlette; un error del servidor llega como respuesta 500."""
    from starlette.testclient import TestClient

    return TestClient(app, raise_server_exceptions=False)


# --- Servidor real para las pruebas de navegador ----------------------------------------------

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ETIQUETA_ARCHIVO = "Archivo de la matriz"


@contextmanager
def servidor_real(app: Any) -> Iterator[str]:
    """Un servidor Uvicorn real en `127.0.0.1`, en un puerto libre y sin registro de accesos.

    Entrega la URL base y detiene el servidor al salir.
    """
    import uvicorn

    with socket.socket() as sonda:
        sonda.bind(("127.0.0.1", 0))
        puerto = sonda.getsockname()[1]
    servidor = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="warning", access_log=False)
    )
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    plazo = time.monotonic() + 15
    while not servidor.started:
        assert hilo.is_alive(), "el servidor no arrancó"
        assert time.monotonic() < plazo, "el servidor tardó demasiado en arrancar"
        time.sleep(0.05)
    try:
        yield f"http://127.0.0.1:{puerto}"
    finally:
        servidor.should_exit = True
        hilo.join(timeout=15)


def nombre_en_cabecera(nombre: str) -> str:
    """El nombre del archivo como componente de URI (plan 001, tabla de rutas)."""
    return quote(nombre, safe="")


def cargar(cliente: Any, contenido: bytes, nombre: str, ficha: str | None = None) -> Any:
    """`POST /carga`: cuerpo crudo con el libro, nombre en `X-EGM-Nombre`, ficha si hay sesión."""
    cabeceras = {CAB_NOMBRE: nombre_en_cabecera(nombre)}
    if ficha:
        cabeceras[CAB_SESION] = ficha
    return cliente.post("/carga", content=contenido, headers=cabeceras)


def resultado(cliente: Any, ficha: str | None) -> Any:
    """`GET /vista/resultado` con la ficha de la sesión (o sin ella)."""
    cabeceras = {CAB_SESION: ficha} if ficha else {}
    return cliente.get("/vista/resultado", headers=cabeceras)


def ficha_de(respuesta: Any) -> str:
    """La ficha de sesión que la respuesta de la carga entrega en su cabecera."""
    return respuesta.headers.get(CAB_SESION, "")


# --- Texto visible ----------------------------------------------------------------------------

_EN_LINEA = {
    "a", "abbr", "b", "bdi", "bdo", "cite", "code", "em", "i", "kbd", "mark", "q", "s",
    "small", "span", "strong", "sub", "sup", "u", "time",
}  # fmt: skip
_OCULTOS = {"script", "style", "head", "template"}


class _ExtractorDeTexto(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.partes: list[str] = []
        self._profundidad_oculta = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _OCULTOS:
            self._profundidad_oculta += 1
        elif tag not in _EN_LINEA:
            self.partes.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in _OCULTOS:
            self._profundidad_oculta = max(0, self._profundidad_oculta - 1)
        elif tag not in _EN_LINEA:
            self.partes.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._profundidad_oculta:
            self.partes.append(data)


def texto_visible(html: str) -> str:
    """El texto que la persona lee: sin etiquetas, scripts ni estilos, con espacios normalizados."""
    extractor = _ExtractorDeTexto()
    extractor.feed(html)
    texto = "".join(extractor.partes).replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", texto).strip()


def colofon_html(html: str) -> str | None:
    """El pie con `aria-label="Colofón"` (boceto `colofon.html`), o `None` si no hay."""
    m = re.search(
        r'<footer[^>]*aria-label="Colof(?:ó|&oacute;|&#243;)n"[^>]*>(.*?)</footer>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    return m.group(1) if m else None


def hay_resultados(texto: str) -> bool:
    """Si el texto muestra los resultados de una matriz: la cabecera corrida o alguna cifra."""
    return bool(CABECERA.search(texto) or CIFRA_DE_RESULTADO.search(texto))


def raiz_del_repositorio() -> Path:
    return Path(__file__).resolve().parents[1]


# --- Terminar la sesión (plan 001, Fase 8) ------------------------------------------------------

# Esperados escritos a mano a partir de flujos.md §2 (E7, E8, E9) y §3 (F-001-5).
E8_DESCARTE = (
    "Descartó el archivo. La sesión terminó y la herramienta no guarda ninguna copia del archivo "
    "ni de sus resultados."
)
E8_INACTIVIDAD = (
    "La sesión terminó porque pasaron 45 minutos sin actividad. La herramienta no guarda ninguna "
    "copia del archivo. Para seguir, cargue de nuevo la matriz."
)
E7_AVISO = (
    "Su sesión se cerrará en 2 minutos por falta de actividad. Al cerrarse, la matriz deja de "
    "estar disponible."
)
E7_BOTON = "Seguir con la sesión"
E9_RECUPERANDO = "Recuperando su sesión."
CABECERA_SESION_FIJA = (
    "La sesión se cierra sola tras 45 minutos sin actividad. El archivo solo se lee: no se "
    "modifica ni se guarda."
)

INACTIVIDAD = timedelta(minutes=45)
GRACIA_CIERRE = timedelta(seconds=10)
"""Los valores fijos de NFR-000-17 y ADR-003 (punto 9), escritos a mano: no se leen de `app`."""

RUTA_DESCARTAR = "/sesion/descartar"
RUTA_LATIDO = "/sesion/latido"
RUTA_CIERRE = "/sesion/cierre"


def enviar_a_sesion(cliente: Any, ruta: str, ficha: str | None) -> Any:
    """`POST` de una ruta de sesión (descartar, latido o cierre) con la ficha en su cabecera."""
    cabeceras = {CAB_SESION: ficha} if ficha else {}
    return cliente.post(ruta, headers=cabeceras)


def entradas_de(carpeta: Path) -> set[str]:
    """Los nombres que hay en una carpeta (vacío si no se puede leer)."""
    try:
        return {entrada.name for entrada in os.scandir(carpeta)}
    except OSError:
        return set()


_IGNORADOS_EN_LA_RAIZ = (
    ".coverage",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    ".ruff_cache",
    "graphify-out",
    ".venv",
    ".git",
    "__pycache__",
)


def archivos_de_la_aplicacion() -> set[str]:
    """Archivos de `app/` (sin cachés) y de la raíz del repositorio (sin cachés de pruebas)."""
    raiz = raiz_del_repositorio()
    en_app = {
        str(ruta.relative_to(raiz))
        for ruta in (raiz / "app").rglob("*")
        if ruta.is_file() and "__pycache__" not in ruta.parts
    }
    en_raiz = {
        nombre
        for nombre in entradas_de(raiz)
        if not nombre.startswith(_IGNORADOS_EN_LA_RAIZ) and (raiz / nombre).is_file()
    }
    return en_app | en_raiz


class RastrosEnDisco:
    """SC-000-17: lo que pasó en la carpeta temporal del sistema y en la de la aplicación.

    Se toma la foto antes de empezar; `hallazgos` lista los archivos nuevos que traen un marcador
    de la matriz (en el nombre o en el contenido) o una copia del libro, y cualquier archivo nuevo
    en la carpeta de la aplicación.
    """

    def __init__(self, marcas: tuple[str, ...]) -> None:
        self._marcas = marcas
        self._temporal = Path(tempfile.gettempdir())
        self._antes_temporal = entradas_de(self._temporal)
        self._antes_app = archivos_de_la_aplicacion()

    def hallazgos(self) -> list[str]:
        nuevos = [self._temporal / n for n in entradas_de(self._temporal) - self._antes_temporal]
        resultado = []
        for ruta in nuevos:
            archivos = [ruta] if ruta.is_file() else [p for p in ruta.rglob("*") if p.is_file()]
            for archivo in archivos:
                if any(marca in str(archivo) for marca in self._marcas):
                    resultado.append(f"nombre: {archivo}")
                    continue
                try:
                    if archivo.stat().st_size > 20_000_000:
                        continue
                    datos = archivo.read_bytes()
                except OSError:
                    continue
                if datos.startswith(b"PK\x03\x04") or any(
                    m.encode() in datos for m in self._marcas
                ):
                    resultado.append(f"contenido: {archivo}")
        resultado += [
            f"en la aplicación: {n}" for n in archivos_de_la_aplicacion() - self._antes_app
        ]
        return resultado


def texto_de_registros(registros: list[Any]) -> str:
    """Todo lo que los registros de `logging` dejaron: nombre, mensaje, argumentos y trazas."""
    partes = []
    for registro in registros:
        partes += [
            registro.name,
            registro.getMessage(),
            str(registro.args),
            registro.exc_text or "",
        ]
        if registro.exc_info:
            partes.append("".join(traceback.format_exception(*registro.exc_info)))
    return "\n".join(partes)
