"""Fase 7 del plan 001, historia 4: cargar la matriz desde la capa web (T-001-60).

Pruebas P-001-71 a P-001-84, P-001-87 y P-001-88. Se escriben antes que la capa web: fallan mientras
`app.servidor`, `app.sesiones`, `app.carga`, `app.presentacion`, `app.colofon` y `app.configuracion`
no existan (los módulos se usan dentro de cada prueba, así que falla la prueba y no la recolección).

Cliente de pruebas de Starlette sobre `app.servidor.crear_app`, con el reloj inyectado. Rutas de
la tabla «Rutas de la capa web» del plan 001: `GET /`, `GET /vista/inicio`, `POST /carga` (cuerpo
crudo, nombre en `X-EGM-Nombre`, ficha en `X-EGM-Sesion`) y `GET /vista/resultado`. Las
suposiciones que los documentos no fijan están en `tests/ayudas_web.py` (`[NEEDS CLARIFICATION]`).

Esperados escritos a mano a partir de `docs/interfaz/flujos.md` §2, §3 y §6, de la tabla de pruebas
del plan y de los docstrings del constructor de fixtures (5 documentos en `base_valida`, 8 en
`sesion_b`, 11 en `sc000_12_otro_nombre_v4`); ninguno sale de ejecutar el código bajo prueba.
Ningún dato viene de la lámina 7.
"""

import asyncio
import builtins
import dataclasses
import logging
import re
import runpy
import tempfile
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from tests.ayudas_web import (
    BORRO_TODO,
    CIERRE_E4,
    COLOFON_REFERENCIA,
    COLOFON_SIN_MATRIZ,
    CUERPO_E2,
    CUERPO_E3,
    CUERPO_E10,
    LIMITE_BYTES,
    LIMITE_DESCOMPRIMIDO,
    SIGUE_DISPONIBLE,
    TITULO_E4,
    TITULO_E4_PREVIA,
    TITULO_RECHAZO,
    RastrosEnDisco,
    Reloj,
    archivos_de_la_aplicacion,
    cabecera_esperada,
    cargar,
    cliente_de,
    colofon_html,
    crear_app,
    descomprimido_declarado,
    exacto_en_bytes,
    ficha_de,
    fixture,
    hay_resultados,
    resultado,
    texto_de_registros,
    texto_visible,
)
from tests.constructor import MARCADORES_CELDAS, NOMBRE_CON_MARCADOR, MatrizSintetica

BASE = "base_valida.xlsx"
LARGO_MINIMO_DE_FICHA = 43  # 256 bits en base 64 (43 caracteres) o en hexadecimal (64)
FECHA_AL_DIA_SIGUIENTE = "26 de noviembre de 2026"  # 44 min después de las 23:30 del 25


@contextmanager
def _servicio(config: Any = None, reloj: Any = None) -> Any:
    """La aplicación en marcha (con su ciclo de vida) y su cliente de pruebas."""
    app = crear_app(config, reloj)
    with cliente_de(app) as cliente:
        yield cliente


def _espiar_almacen(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[tuple[Any, ...]]]:
    """Registra las llamadas a `crear`, `reemplazar` y `terminar` de `AlmacenSesiones` (M15)."""
    from app import sesiones

    llamadas: dict[str, list[tuple[Any, ...]]] = {"crear": [], "reemplazar": [], "terminar": []}

    def envolver(original: Any, registro: list[tuple[Any, ...]]) -> Any:
        def envoltura(self: Any, *args: Any, **kwargs: Any) -> Any:
            registro.append((*args, *kwargs.values()))
            return original(self, *args, **kwargs)

        return envoltura

    for nombre, registro in llamadas.items():
        original = getattr(sesiones.AlmacenSesiones, nombre)
        monkeypatch.setattr(sesiones.AlmacenSesiones, nombre, envolver(original, registro))
    return llamadas


def _texto(respuesta: Any) -> str:
    return texto_visible(respuesta.text)


def _sin_resultados(respuesta: Any) -> None:
    """La respuesta no abre ninguna sesión: ni cabecera ni cifras de resultados."""
    assert respuesta.status_code < 500
    assert not hay_resultados(_texto(respuesta))


# --- P-001-71 ---------------------------------------------------------------------------------


def test_p_001_71_inicio_sin_matriz_ofrece_cargar_indica_el_limite_y_no_trae_cifras() -> None:
    """P-001-71 · US-001-4.2, ADR-005 punto 4: V0 con la opción de cargar, sin cifras."""
    with _servicio() as cliente:
        inicio = cliente.get("/vista/inicio")
        base = cliente.get("/")

    assert inicio.status_code == 200
    assert base.status_code == 200
    texto = _texto(inicio)
    assert "Cargue la matriz bibliográfica" in texto
    assert "Archivo de la matriz (Excel .xlsx, hasta 15 MB)" in texto
    assert "El límite exacto es 15 728 640 bytes." in texto
    assert "Cargar la matriz" in texto
    assert re.search(r'<input[^>]*type="file"', inicio.text)
    # Ninguna cifra de resultados ni en la vista de inicio ni en la página base.
    assert not hay_resultados(texto)
    assert not hay_resultados(_texto(base))
    # Colofón de la pantalla de inicio (página base y fragmento de V0; ver NC en tests/ayudas_web).
    pantalla = f"{texto} {_texto(base)}"
    assert COLOFON_SIN_MATRIZ in pantalla
    assert COLOFON_REFERENCIA in pantalla


def test_p_001_71_sin_ficha_o_con_ficha_inventada_el_resultado_no_abre_nada() -> None:
    """P-001-71 · US-001-4.2, NFR-000-17: sin sesión, `GET /vista/resultado` no muestra datos."""
    with _servicio() as cliente:
        _sin_resultados(resultado(cliente, None))
        _sin_resultados(resultado(cliente, "x" * LARGO_MINIMO_DE_FICHA))


# --- P-001-72 ---------------------------------------------------------------------------------


def test_p_001_72_carga_valida_crea_la_ficha_y_muestra_la_cabecera_corrida() -> None:
    """P-001-72 · US-001-4.1, FR-001-19, FR-001-20, NFR-000-12: base_valida (5 documentos)."""
    with _servicio() as cliente:
        respuesta = cargar(cliente, fixture(BASE), BASE)
        ficha = ficha_de(respuesta)
        disponible = resultado(cliente, ficha)

    esperado = cabecera_esperada(BASE, 5)
    assert respuesta.status_code == 200
    assert len(ficha) >= LARGO_MINIMO_DE_FICHA
    assert "set-cookie" not in respuesta.headers  # la ficha no viaja en cookies (ADR-003, punto 4)
    assert esperado in _texto(respuesta)
    assert disponible.status_code == 200
    assert esperado in _texto(disponible)


def test_p_001_72_cada_carga_sin_sesion_recibe_una_ficha_distinta() -> None:
    """P-001-72 · FR-001-20, NFR-000-18: fichas aleatorias, una por sesión nueva."""
    with _servicio() as cliente:
        primera = ficha_de(cargar(cliente, fixture(BASE), BASE))
        segunda = ficha_de(cargar(cliente, fixture(BASE), BASE))

    assert primera
    assert segunda
    assert primera != segunda


def test_p_001_72_el_nombre_llega_como_componente_de_uri_y_se_muestra_tal_cual() -> None:
    """P-001-72 · US-001-4.1, NFR-000-12: tildes, espacios y signos del nombre se conservan."""
    nombre = "Matriz del equipo – año 2026 (copia) ñ.xlsx"
    with _servicio() as cliente:
        respuesta = cargar(cliente, fixture(BASE), nombre)
        disponible = resultado(cliente, ficha_de(respuesta))

    assert cabecera_esperada(nombre, 5) in _texto(respuesta)
    assert cabecera_esperada(nombre, 5) in _texto(disponible)


# --- P-001-73 ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fixture_nombre", "como_nombre"),
    [
        pytest.param("cb16_otro_tipo.txt", "cb16_otro_tipo.txt", id="otro_tipo"),
        pytest.param(
            "cb16_extension_xlsx_otro_contenido.xlsx",
            "cb16_extension_xlsx_otro_contenido.xlsx",
            id="extension_xlsx_otro_contenido",
        ),
        pytest.param("cb16_danado.xlsx", "cb16_danado.xlsx", id="danado"),
    ],
)
def test_p_001_73_tipo_no_admitido_da_e2_sin_cifras_y_sin_sesion(
    monkeypatch: pytest.MonkeyPatch, fixture_nombre: str, como_nombre: str
) -> None:
    """P-001-73 · US-001-4.3, SC-000-19, CB-16: mensaje E2; ninguna cifra; ninguna sesión creada."""
    with _servicio() as cliente:
        llamadas = _espiar_almacen(monkeypatch)
        respuesta = cargar(cliente, fixture(fixture_nombre), como_nombre)

    texto = _texto(respuesta)
    assert respuesta.status_code < 500
    assert TITULO_RECHAZO in texto
    assert CUERPO_E2 in texto
    assert not hay_resultados(texto)
    assert como_nombre not in respuesta.text  # E2 no muestra el nombre del archivo
    assert not ficha_de(respuesta)
    assert llamadas == {"crear": [], "reemplazar": [], "terminar": []}


# --- P-001-74 ---------------------------------------------------------------------------------


def test_p_001_74_el_tamano_exacto_se_acepta() -> None:
    """P-001-74 · US-001-4.4, SC-000-19, NFR-000-19: 15 728 640 bytes se leen."""
    contenido = exacto_en_bytes(LIMITE_BYTES)
    assert len(contenido) == LIMITE_BYTES

    with _servicio() as cliente:
        respuesta = cargar(cliente, contenido, "exacto.xlsx")

    assert respuesta.status_code == 200
    assert ficha_de(respuesta)
    assert cabecera_esperada("exacto.xlsx", 5) in _texto(respuesta)


def test_p_001_74_un_byte_mas_da_e3_con_el_limite_y_sin_resultados() -> None:
    """P-001-74 · US-001-4.4, SC-000-19, NFR-000-19: +1 byte recibe E3 que indica el límite."""
    contenido = exacto_en_bytes(LIMITE_BYTES + 1)
    assert len(contenido) == LIMITE_BYTES + 1

    with _servicio() as cliente:
        respuesta = cargar(cliente, contenido, "mas_uno.xlsx")

    texto = _texto(respuesta)
    assert respuesta.status_code < 500
    assert TITULO_RECHAZO in texto
    assert CUERPO_E3 in texto
    assert not hay_resultados(texto)
    assert "mas_uno.xlsx" not in respuesta.text
    assert not ficha_de(respuesta)


@asynccontextmanager
async def _ciclo_de_vida(app: Any, estado: dict[str, Any]) -> Any:
    """Arranca y apaga la aplicación con el protocolo de ciclo de vida de ASGI."""
    entrada: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    salida: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def recibir() -> dict[str, Any]:
        return await entrada.get()

    async def enviar(mensaje: dict[str, Any]) -> None:
        await salida.put(mensaje)

    alcance = {"type": "lifespan", "asgi": {"version": "3.0"}, "state": estado}
    tarea = asyncio.create_task(app(alcance, recibir, enviar))
    await entrada.put({"type": "lifespan.startup"})
    arranque = await salida.get()
    assert arranque["type"] == "lifespan.startup.complete"
    try:
        yield
    finally:
        await entrada.put({"type": "lifespan.shutdown"})
        await salida.get()
        await tarea


async def _carga_en_flujo(app: Any, total: int, trozo: int) -> tuple[int, bytes, int]:
    """Envía `total` bytes en trozos a `POST /carga` sin `Content-Length`.

    Devuelve el estado, el cuerpo de la respuesta y cuántos bytes entregó a la aplicación.
    """
    entregados = 0
    restante = total
    cuerpo = b""
    estado_http = 0

    async def recibir() -> dict[str, Any]:
        nonlocal entregados, restante
        if restante <= 0:
            return {"type": "http.disconnect"}
        n = min(trozo, restante)
        restante -= n
        entregados += n
        return {"type": "http.request", "body": bytes(n), "more_body": restante > 0}

    async def enviar(mensaje: dict[str, Any]) -> None:
        nonlocal cuerpo, estado_http
        if mensaje["type"] == "http.response.start":
            estado_http = mensaje["status"]
        elif mensaje["type"] == "http.response.body":
            cuerpo += mensaje.get("body", b"")

    estado: dict[str, Any] = {}
    async with _ciclo_de_vida(app, estado):
        alcance = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/carga",
            "raw_path": b"/carga",
            "root_path": "",
            "query_string": b"",
            "headers": [
                (b"host", b"127.0.0.1:8000"),
                (b"content-type", b"application/octet-stream"),
                (b"x-egm-nombre", b"corte.xlsx"),
            ],
            "client": ("127.0.0.1", 50000),
            "server": ("127.0.0.1", 8000),
            "state": dict(estado),
        }
        await app(alcance, recibir, enviar)
    return estado_http, cuerpo, entregados


def test_p_001_74_la_lectura_del_cuerpo_se_corta_al_pasar_el_limite() -> None:
    """P-001-74 · US-001-4.4, NFR-000-19: no se lee el resto del cuerpo una vez pasado el límite."""
    trozo = 65_536
    total = LIMITE_BYTES + 200 * trozo  # unos 12,5 MiB por encima del límite
    app = crear_app()

    estado_http, cuerpo, entregados = asyncio.run(_carga_en_flujo(app, total, trozo))

    texto = texto_visible(cuerpo.decode("utf-8"))
    assert estado_http < 500
    assert CUERPO_E3 in texto
    assert entregados > LIMITE_BYTES  # leyó hasta pasar el límite...
    assert entregados <= LIMITE_BYTES + 2 * trozo  # ...y ahí se detuvo
    assert entregados < total


# --- P-001-75 ---------------------------------------------------------------------------------


def test_p_001_75_contenido_descomprimido_exacto_se_acepta() -> None:
    """P-001-75 · US-001-4.13, SC-000-19, FR-001-29: 268 435 456 bytes declarados se leen."""
    with _servicio() as cliente:
        respuesta = cargar(cliente, descomprimido_declarado(LIMITE_DESCOMPRIMIDO), "exacto_d.xlsx")

    assert respuesta.status_code == 200
    assert ficha_de(respuesta)
    assert cabecera_esperada("exacto_d.xlsx", 5) in _texto(respuesta)


def test_p_001_75_un_byte_mas_declarado_da_e10_y_conserva_la_sesion_anterior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-75 · US-001-4.13, SC-000-19, FR-001-29: E10 sin cifras; la sesión anterior sigue."""
    rechazado = descomprimido_declarado(LIMITE_DESCOMPRIMIDO + 1)
    with _servicio() as cliente:
        ficha = ficha_de(cargar(cliente, fixture(BASE), BASE))
        llamadas = _espiar_almacen(monkeypatch)
        respuesta = cargar(cliente, rechazado, "rechazado_d.xlsx", ficha)
        sigue = resultado(cliente, ficha)

    texto = _texto(respuesta)
    anterior = cabecera_esperada(BASE, 5)
    assert respuesta.status_code < 500
    assert TITULO_RECHAZO in texto
    assert CUERPO_E10 in texto
    assert "268 435 456" not in texto  # E10 no lleva el límite
    assert "15 728 640" not in texto
    assert "rechazado_d.xlsx" not in respuesta.text
    assert SIGUE_DISPONIBLE + anterior in texto
    assert llamadas == {"crear": [], "reemplazar": [], "terminar": []}
    assert anterior in _texto(sigue)


# --- P-001-76 ---------------------------------------------------------------------------------


def test_p_001_76_cargar_otro_archivo_deja_solo_los_resultados_del_nuevo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-76 · US-001-4.5, FR-001-20: base_valida y luego sesion_b con la misma ficha."""
    reloj = Reloj(datetime(2026, 11, 25, 23, 30))
    with _servicio(reloj=reloj) as cliente:
        ficha = ficha_de(cargar(cliente, fixture(BASE), BASE))
        llamadas = _espiar_almacen(monkeypatch)
        reloj.avanzar(minutes=44)
        nueva = cargar(cliente, fixture("sesion_b.xlsx"), "sesion_b.xlsx", ficha)
        misma_ficha = resultado(cliente, ficha)

    esperado = cabecera_esperada("sesion_b.xlsx", 8, FECHA_AL_DIA_SIGUIENTE)
    assert nueva.status_code == 200
    assert len(llamadas["reemplazar"]) == 1
    assert llamadas["reemplazar"][0][0] == ficha
    assert llamadas["crear"] == []
    for texto in (_texto(nueva), _texto(misma_ficha)):
        assert esperado in texto
        assert BASE not in texto
        assert "5 documentos" not in texto


# --- P-001-77 ---------------------------------------------------------------------------------


def test_p_001_77_error_de_contrato_con_matriz_previa_termina_la_sesion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-77 · US-001-4.7, FR-001-29, NFR-000-17: E4 con matriz previa; la ficha ya no abre."""
    nombre_nuevo = "MARCA-NOMBRE-CB14-77AB.xlsx"
    with _servicio() as cliente:
        ficha = ficha_de(cargar(cliente, fixture("marcadores.xlsx"), NOMBRE_CON_MARCADOR))
        llamadas = _espiar_almacen(monkeypatch)
        respuesta = cargar(
            cliente, fixture("cb14_sin_nivel_de_evidencia.xlsx"), nombre_nuevo, ficha
        )
        despues = resultado(cliente, ficha)

    texto = _texto(respuesta)
    assert respuesta.status_code < 500
    assert TITULO_E4_PREVIA in texto
    assert "Se esperaba la columna «Nivel de evidencia»" in texto
    assert "no se encontró: «" in texto or "se encontraron: «" in texto
    assert BORRO_TODO in texto
    assert CIERRE_E4 in texto
    assert not hay_resultados(texto)
    for prohibido in (nombre_nuevo, NOMBRE_CON_MARCADOR, *MARCADORES_CELDAS):
        assert prohibido not in respuesta.text
    # La sesión terminó: M15 la terminó y la ficha anterior ya no abre nada.
    assert [llamada[0] for llamada in llamadas["terminar"]] == [ficha]
    _sin_resultados(despues)
    for marca in (NOMBRE_CON_MARCADOR, *MARCADORES_CELDAS):
        assert marca not in despues.text


# --- P-001-78 y P-001-79 ----------------------------------------------------------------------


def test_p_001_78_carga_nueva_con_advertencias_se_acepta_con_su_advertencia() -> None:
    """P-001-78 · US-001-4.8, FR-001-29: valor fuera de lista; resultados solo del nuevo."""
    nuevo = "esc_2_1_fuera_de_lista_n3.xlsx"
    with _servicio() as cliente:
        ficha = ficha_de(cargar(cliente, fixture(BASE), BASE))
        respuesta = cargar(cliente, fixture(nuevo), nuevo, ficha)
        disponible = resultado(cliente, ficha)

    advertencia = (
        "N.º 3, columna «Tipo de intervención (EGM)», valor «Intervención Z»: el valor no está "
        "en la lista de esa columna. La herramienta no lo cuenta y no lo corrige."
    )
    assert respuesta.status_code == 200
    for texto in (_texto(respuesta), _texto(disponible)):
        assert cabecera_esperada(nuevo, 5) in texto
        assert advertencia in texto
        assert BASE not in texto


def test_p_001_79_carga_nueva_con_solo_una_nota_se_acepta_con_la_nota() -> None:
    """P-001-79 · US-001-4.9, FR-001-29, CB-18: columna «Observaciones» sin lista."""
    nuevo = "cb18_columna_observaciones.xlsx"
    with _servicio() as cliente:
        ficha = ficha_de(cargar(cliente, fixture(BASE), BASE))
        respuesta = cargar(cliente, fixture(nuevo), nuevo, ficha)
        disponible = resultado(cliente, ficha)

    assert respuesta.status_code == 200
    for texto in (_texto(respuesta), _texto(disponible)):
        assert cabecera_esperada(nuevo, 5) in texto
        assert "Columnas no usadas: Observaciones." in texto
        assert BASE not in texto


# --- P-001-80 ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("contenido", "cuerpo"),
    [
        pytest.param(fixture("cb16_otro_tipo.txt"), CUERPO_E2, id="e2_tipo"),
        pytest.param(exacto_en_bytes(LIMITE_BYTES + 1), CUERPO_E3, id="e3_tamano"),
    ],
)
def test_p_001_80_rechazo_con_matriz_previa_conserva_la_matriz_y_sus_resultados(
    monkeypatch: pytest.MonkeyPatch, contenido: bytes, cuerpo: str
) -> None:
    """P-001-80 · US-001-4.11, FR-001-29: E2 o E3 con matriz previa; la anterior sigue."""
    reloj = Reloj(datetime(2026, 11, 25, 23, 30))
    with _servicio(reloj=reloj) as cliente:
        ficha = ficha_de(cargar(cliente, fixture(BASE), BASE))
        llamadas = _espiar_almacen(monkeypatch)
        reloj.avanzar(minutes=44)
        respuesta = cargar(cliente, contenido, "rechazado.xlsx", ficha)
        sigue = resultado(cliente, ficha)

    texto = _texto(respuesta)
    anterior = cabecera_esperada(BASE, 5)  # con la fecha de su lectura, no la del intento
    assert respuesta.status_code < 500
    assert TITULO_RECHAZO in texto
    assert cuerpo in texto
    assert SIGUE_DISPONIBLE + anterior in texto
    assert "rechazado.xlsx" not in respuesta.text
    assert llamadas == {"crear": [], "reemplazar": [], "terminar": []}
    assert anterior in _texto(sigue)


# --- P-001-81 ---------------------------------------------------------------------------------


def test_p_001_81_primera_carga_con_error_de_contrato_nombra_el_encabezado_sin_cifras(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-81 · US-001-4.12, FR-001-29, CB-14: E4 sin matriz previa, sin nombre ni filas."""
    nombre = "MARCA-NOMBRE-CB14-81CD.xlsx"
    with _servicio() as cliente:
        llamadas = _espiar_almacen(monkeypatch)
        respuesta = cargar(cliente, fixture("cb14_sin_nivel_de_evidencia.xlsx"), nombre)

    texto = _texto(respuesta)
    assert respuesta.status_code < 500
    assert TITULO_E4 in texto
    assert "Se esperaba la columna «Nivel de evidencia»" in texto
    assert "no se encontró: «" in texto or "se encontraron: «" in texto
    assert "No se muestra ninguna cifra." in texto
    assert CIERRE_E4 in texto
    assert "la sesión terminó" not in texto  # sin matriz previa no hay sesión que terminar
    assert not hay_resultados(texto)
    assert nombre not in respuesta.text
    for fila_de_datos in ("Autor 2", "Documento sintético", "País sintético", "Intervención A"):
        assert fila_de_datos not in respuesta.text
    minusculas = texto.lower()
    for jerga in ("error de contrato", "sesión efímera", "validación", "fixture", "traceback"):
        assert jerga not in minusculas
    assert not ficha_de(respuesta)
    assert llamadas["crear"] == []


# --- P-001-82 ---------------------------------------------------------------------------------


def test_p_001_82_cabecera_y_colofon_usan_el_nombre_la_fecha_y_el_numero_de_la_carga() -> None:
    """P-001-82 · SC-000-12, NFR-000-12: otro nombre (con «v4»), otra fecha, 11 documentos."""
    nombre = "matriz_prueba_v4.xlsx"
    reloj = Reloj(datetime(2026, 12, 1, 14, 5))
    with _servicio(reloj=reloj) as cliente:
        respuesta = cargar(cliente, fixture("sc000_12_otro_nombre_v4.xlsx"), nombre)
        disponible = resultado(cliente, ficha_de(respuesta))

    cabecera = cabecera_esperada(nombre, 11, "1 de diciembre de 2026")
    for pagina in (respuesta, disponible):
        texto = _texto(pagina)
        assert cabecera in texto
        colofon = colofon_html(pagina.text)
        assert colofon is not None
        assert f"Datos. {cabecera}." in texto_visible(colofon)
        # Ninguna versión deducida: «v4» solo aparece dentro del nombre tal como llegó.
        sin_nombre = texto.replace(nombre, "")
        assert "v4" not in sin_nombre
        assert "versión" not in sin_nombre.lower()


# --- P-001-83 ---------------------------------------------------------------------------------

# Rastros de los bloques apagados (ADR-005, punto 2): ningún texto institucional, ni logo, ni
# comentado ni oculto. Cada término se busca en el HTML completo, sin distinguir mayúsculas.
RASTROS_DE_BLOQUES_APAGADOS = (
    "universidad del magdalena",
    "unimagdalena",
    "col0016423",
    "gioe",
    "minciencias",
    "desarrollo rural",
    "economía solidaria",
    "marco de evaluación",
    "amanda vargas",
    "lina martínez",
    "jairo",
    "semillero",
    "<img",
    "logos/",
)

TEXTOS_DE_PRUEBA_DE_BLOQUES = {
    "proyecto": (
        "Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los "
        "medios de vida de la población víctima en Colombia."
    ),
    "grupo": "Organización y Empresa (GIOE), Universidad del Magdalena, Santa Marta.",
    "codigo_minciencias": "Código Minciencias: COL0016423.",
    "semillero": "Desarrollo Rural y Economía Solidaria.",
    "equipo": "Amanda Vargas Prieto, investigadora principal. Lina Martínez, coinvestigadora.",
    "herramienta": (
        "[POR CONFIRMAR si se incluye y con qué rol] Jairo de Jesús Blanco Pérez, semillerista."
    ),
    "contacto": "ogarciav@unimagdalena.edu.co",
}


def _sin_bloques_apagados(html: str) -> None:
    minusculas = html.lower()
    for rastro in RASTROS_DE_BLOQUES_APAGADOS:
        assert rastro not in minusculas, rastro


def test_p_001_83_por_defecto_el_colofon_solo_trae_datos_y_la_referencia_a_3ie() -> None:
    """P-001-83 · NFR-000-11, SC-000-11 (parte automática), ADR-005 puntos 2, 3 y 5."""
    from app.configuracion import cargar_configuracion

    with _servicio(cargar_configuracion(None)) as cliente:
        inicio = cliente.get("/vista/inicio")
        base = cliente.get("/")
        con_matriz = resultado(cliente, ficha_de(cargar(cliente, fixture(BASE), BASE)))

    for pagina in (inicio, base, con_matriz):
        _sin_bloques_apagados(pagina.text)
    colofon = colofon_html(con_matriz.text)
    assert colofon is not None
    texto = texto_visible(colofon)
    datos = f"Datos. {cabecera_esperada(BASE, 5)}."
    assert datos in texto
    assert COLOFON_REFERENCIA in texto
    sobrante = texto.replace(datos, "").replace(COLOFON_REFERENCIA, "").replace("Colofón", "")
    assert not re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", sobrante), sobrante  # ningún otro bloque


def _configuracion_con_todos_los_bloques_encendidos() -> Any:
    """Configuración de prueba con todos los bloques configurables encendidos (ADR-005, punto 5).

    [NEEDS CLARIFICATION: campo `colofon` de `Configuracion` y tipo de `Logo.ruta`; la
    arquitectura fija `BloqueColofon(clave, activo, texto, logo)` y `Logo(ruta, alt, placa_clara)`.]
    """
    from app.colofon import BloqueColofon, ConfiguracionColofon, Logo
    from app.configuracion import cargar_configuracion

    bloques = [
        BloqueColofon(clave, True, texto, None)
        for clave, texto in TEXTOS_DE_PRUEBA_DE_BLOQUES.items()
    ]
    # Logos encendidos cuyo archivo no existe: cada uno se omite completo (ADR-005, punto 3).
    for clave in ("logo_minciencias", "logo_unimagdalena"):
        inexistente = Path(tempfile.gettempdir()) / "egm-logo-que-no-existe" / f"{clave}.svg"
        bloques.append(
            BloqueColofon(clave, True, None, Logo(inexistente, f"Alt de {clave}", False))
        )
    config = cargar_configuracion(None)
    return dataclasses.replace(config, colofon=ConfiguracionColofon(bloques=tuple(bloques)))


def test_p_001_83_con_todos_los_bloques_encendidos_aparecen_codigo_y_correo() -> None:
    """P-001-83 · NFR-000-11, SC-000-11, ADR-005 punto 5: bloques encendidos y reglas de omisión."""
    config = _configuracion_con_todos_los_bloques_encendidos()
    with _servicio(config) as cliente:
        pagina = resultado(cliente, ficha_de(cargar(cliente, fixture(BASE), BASE)))

    colofon = colofon_html(pagina.text)
    assert colofon is not None
    texto = texto_visible(colofon)
    minusculas = pagina.text.lower()
    # Encendidos: el código y el correo, además de los dos bloques siempre presentes.
    assert "COL0016423" in texto
    assert "ogarciav@unimagdalena.edu.co" in texto
    assert TEXTOS_DE_PRUEBA_DE_BLOQUES["proyecto"] in texto
    assert f"Datos. {cabecera_esperada(BASE, 5)}." in texto
    assert COLOFON_REFERENCIA in texto
    # Omitidos: categoría y línea de investigación; marca de pendiente (la línea completa).
    assert "línea de investigación" not in minusculas
    assert "categoría" not in texto.lower()
    assert "POR CONFIRMAR" not in pagina.text
    assert "Blanco" not in texto
    assert "Herramienta." not in texto
    # Un logo sin archivo se omite completo: ni imagen ni texto alternativo.
    assert "<img" not in colofon.lower()
    assert "Alt de logo_minciencias" not in pagina.text
    assert "Alt de logo_unimagdalena" not in pagina.text


# --- P-001-84 ---------------------------------------------------------------------------------


def _espia_de_temporales(original: Any, nombre: str, registro: list[str]) -> Any:
    def espia(*args: Any, **kwargs: Any) -> Any:
        registro.append(nombre)
        return original(*args, **kwargs)

    return espia


def test_p_001_84_la_carga_no_deja_archivos_ni_usa_el_analizador_multiparte(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """P-001-84 · NFR-000-17, SC-000-17 (parte de la carga): nada en disco ni en los registros."""
    import starlette.formparsers
    import starlette.requests

    caplog.set_level(logging.DEBUG)
    contenido = fixture("marcadores.xlsx")
    rastros = RastrosEnDisco((*MARCADORES_CELDAS, NOMBRE_CON_MARCADOR))
    antes_app = archivos_de_la_aplicacion()

    # La carpeta temporal queda vacía y apartada: cualquier archivo temporal caería ahí.
    apartada = tmp_path / "temporal_apartada"
    apartada.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(apartada))
    usos_de_temporales: list[str] = []
    for nombre in (
        "SpooledTemporaryFile",
        "NamedTemporaryFile",
        "TemporaryFile",
        "TemporaryDirectory",
        "mkstemp",
        "mkdtemp",
    ):
        espia = _espia_de_temporales(getattr(tempfile, nombre), nombre, usos_de_temporales)
        monkeypatch.setattr(tempfile, nombre, espia)
        if nombre == "SpooledTemporaryFile":  # el nombre con el que lo importa el analizador
            monkeypatch.setattr(starlette.formparsers, nombre, espia, raising=False)

    # La carga no usa el analizador multiparte ni lee el cuerpo como formulario.
    def prohibido(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("la carga no puede usar el analizador multiparte")

    monkeypatch.setattr(starlette.formparsers.MultiPartParser, "__init__", prohibido)
    monkeypatch.setattr(starlette.requests.Request, "form", prohibido)

    # Ninguna escritura de archivos durante la carga.
    escrituras: list[str] = []
    abrir_original = builtins.open

    def abrir_con_espia(archivo: Any, modo: str = "r", *args: Any, **kwargs: Any) -> Any:
        if isinstance(modo, str) and any(c in modo for c in "wax+"):
            escrituras.append(str(archivo))
        return abrir_original(archivo, modo, *args, **kwargs)

    with _servicio() as cliente:
        monkeypatch.setattr(builtins, "open", abrir_con_espia)
        try:
            respuesta = cargar(cliente, contenido, NOMBRE_CON_MARCADOR)
            disponible = resultado(cliente, ficha_de(respuesta))
        finally:
            monkeypatch.setattr(builtins, "open", abrir_original)

    assert respuesta.status_code == 200
    assert cabecera_esperada(NOMBRE_CON_MARCADOR, 5) in _texto(disponible)
    assert usos_de_temporales == []
    assert list(apartada.iterdir()) == []
    assert escrituras == []
    # Carpeta temporal real del sistema y carpeta de la aplicación: nada nuevo con la matriz.
    assert rastros.hallazgos() == []
    assert archivos_de_la_aplicacion() == antes_app
    # Los registros no contienen marcadores ni el nombre del archivo.
    registros = texto_de_registros(caplog.records)
    for marca in (*MARCADORES_CELDAS, NOMBRE_CON_MARCADOR):
        assert marca not in registros


def test_p_001_84_un_error_interno_se_registra_por_tipo_sin_su_mensaje(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """P-001-84 · NFR-000-17, arquitectura M14: errores solo por tipo y módulo, sin su mensaje."""
    secreto = "MARCA-ERROR-INTERNO-4F2A"

    def falla(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(secreto)

    monkeypatch.setattr("egm.procesamiento.procesar", falla)
    monkeypatch.setattr("app.carga.procesar", falla, raising=False)
    caplog.set_level(logging.DEBUG)

    with _servicio() as cliente:
        respuesta = cargar(cliente, fixture("marcadores.xlsx"), NOMBRE_CON_MARCADOR)

    registros = texto_de_registros(caplog.records)
    assert secreto not in respuesta.text
    assert secreto not in registros
    assert NOMBRE_CON_MARCADOR not in registros
    assert "RuntimeError" in registros  # el tipo sí se registra


def test_p_001_84_el_arranque_apaga_el_registro_de_accesos_y_escucha_solo_en_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-84 · NFR-000-15, NFR-000-17: `python -m app.servidor` en 127.0.0.1, sin accesos.

    [NEEDS CLARIFICATION: se supone que el arranque usa `uvicorn.run(...)` o `uvicorn.Config(...)`
    con `host`, `port` y `access_log` explícitos; la arquitectura solo dice «sin accesos».]
    """
    import uvicorn

    registro: dict[str, Any] = {}

    def falso_run(app: Any = None, **kwargs: Any) -> None:
        registro["opciones"] = kwargs

    original_init = uvicorn.Config.__init__

    def init_con_espia(self: Any, app: Any, **kwargs: Any) -> None:
        registro.setdefault("opciones", kwargs)
        original_init(self, app, **kwargs)

    monkeypatch.setattr(uvicorn, "run", falso_run)
    monkeypatch.setattr(uvicorn.Config, "__init__", init_con_espia)
    monkeypatch.setattr(uvicorn.Server, "run", lambda self, sockets=None: None)

    runpy.run_module("app.servidor", run_name="__main__")

    opciones = registro["opciones"]
    assert opciones.get("host") == "127.0.0.1"
    assert opciones.get("port", 8000) == 8000
    assert opciones.get("access_log", True) is False
    assert opciones.get("workers", 1) == 1
    assert not opciones.get("reload", False)


def test_p_001_84_las_cabeceras_de_seguridad_no_permiten_recursos_externos() -> None:
    """P-001-84 · NFR-000-15, ADR-003 punto 6: política de contenido sin recursos externos."""
    with _servicio() as cliente:
        respuestas = [
            cliente.get("/"),
            cliente.get("/vista/inicio"),
            cargar(cliente, fixture(BASE), BASE),
            cargar(cliente, fixture("cb16_otro_tipo.txt"), "otro.txt"),
        ]

    for respuesta in respuestas:
        politica = respuesta.headers.get("content-security-policy", "")
        assert "default-src" in politica
        assert "'unsafe-inline'" not in politica  # sin estilos ni guiones en línea
        assert "'unsafe-eval'" not in politica
        assert not re.search(r"https?:|//|\*", politica)
        directivas = [d.split() for d in politica.split(";") if d.strip()]
        permitidos = {"'self'", "'none'", "data:", "blob:"}
        for directiva in directivas:
            assert set(directiva[1:]) <= permitidos, directiva


@pytest.mark.parametrize("ruta", ["/", "/vista/inicio"])
def test_p_001_84_las_paginas_no_piden_recursos_externos_ni_usan_estilos_en_linea(
    ruta: str,
) -> None:
    """P-001-84 · NFR-000-15, ADR-003 punto 6: todo recurso es local; ningún estilo en línea."""
    with _servicio() as cliente:
        html = cliente.get(ruta).text

    assert not re.search(r"""(?:src|href|action)\s*=\s*["'](?:https?:)?//""", html)
    assert not re.search(r"<style\b", html, re.IGNORECASE)
    assert not re.search(r"\sstyle\s*=", html, re.IGNORECASE)


# --- P-001-87 ---------------------------------------------------------------------------------

TITULO_DE_AVISOS = "Antes de leer los resultados"
COINCIDE = "Los conteos coinciden con la hoja EGM del archivo. Tablas verificadas: 1, 2 y 4."
DIFIERE = "Los conteos difieren de la hoja EGM en la tabla 1"
ADVERTENCIA_G_IGUAL_H = "está en la principal y también en la secundaria"
NOTA_OBSERVACIONES = "Columnas no usadas: Observaciones."


def _matriz_con_verificacion_advertencia_y_nota() -> bytes:
    """base_valida con el N.º 3 con una intervención fuera de lista y la columna «Observaciones»."""
    matriz = MatrizSintetica.base_valida()
    matriz.fijar_celda(2, "Tipo de intervención (EGM)", "Intervención Z")
    matriz.agregar_columna("Observaciones", valores=["Nota 1", None, "Nota 3", None, None])
    return matriz.a_bytes()


def _antes_de_cualquier_cifra(texto: str) -> None:
    """Lo que precede al bloque no trae cifras, salvo la cabecera corrida y su frase fija."""
    antes = texto[: texto.index(TITULO_DE_AVISOS)]
    antes = re.sub(r"Matriz: .+?, leída el .+?, \d+ documentos", "", antes)
    antes = antes.replace("La sesión se cierra sola tras 45 minutos sin actividad.", "")
    assert not re.search(r"\d", antes), antes


@pytest.mark.parametrize(
    ("contenido", "nombre", "orden"),
    [
        pytest.param(
            fixture("esc_3_1_coincide.xlsx"), "esc_3_1_coincide.xlsx", [COINCIDE], id="coincide"
        ),
        pytest.param(
            fixture("esc_3_2_difiere_g_igual_h.xlsx"),
            "esc_3_2_difiere_g_igual_h.xlsx",
            [DIFIERE, ADVERTENCIA_G_IGUAL_H],
            id="difiere_g_igual_h",
        ),
        pytest.param(
            _matriz_con_verificacion_advertencia_y_nota(),
            "verificacion_advertencia_nota.xlsx",
            ["Los conteos", "N.º 3, columna «Tipo de intervención (EGM)»", NOTA_OBSERVACIONES],
            id="verificacion_advertencia_nota",
        ),
    ],
)
def test_p_001_87_el_bloque_de_avisos_va_antes_de_las_cifras_y_en_su_orden(
    contenido: bytes, nombre: str, orden: list[str]
) -> None:
    """P-001-87 · FR-001-18, FR-001-25, FR-001-12: verificación, advertencias y notas, en orden."""
    with _servicio() as cliente:
        ficha = ficha_de(cargar(cliente, contenido, nombre))
        pagina = resultado(cliente, ficha)

    texto = _texto(pagina)
    assert TITULO_DE_AVISOS in texto
    posiciones = [texto.index(TITULO_DE_AVISOS)]
    for fragmento in orden:
        assert fragmento in texto, fragmento
        posiciones.append(texto.index(fragmento))
    assert posiciones == sorted(posiciones)
    assert len(set(posiciones)) == len(posiciones)
    _antes_de_cualquier_cifra(texto)


# --- P-001-88 ---------------------------------------------------------------------------------


def test_p_001_88_dos_fichas_ven_cada_una_solo_sus_resultados() -> None:
    """P-001-88 · SC-000-18 (resultados), NFR-000-18: sesion_a y sesion_b no se mezclan."""
    with _servicio() as cliente:
        ficha_a = ficha_de(cargar(cliente, fixture("sesion_a.xlsx"), "sesion_a.xlsx"))
        ficha_b = ficha_de(cargar(cliente, fixture("sesion_b.xlsx"), "sesion_b.xlsx"))
        ve_a = _texto(resultado(cliente, ficha_a))
        ve_b = _texto(resultado(cliente, ficha_b))
        inventada = ficha_a[:-1] + ("A" if ficha_a[-1] != "A" else "B")
        sin_sesion = resultado(cliente, inventada)

    assert ficha_a
    assert ficha_b
    assert ficha_a != ficha_b
    assert cabecera_esperada("sesion_a.xlsx", 5) in ve_a
    assert "sesion_b.xlsx" not in ve_a
    assert "8 documentos" not in ve_a
    assert cabecera_esperada("sesion_b.xlsx", 8) in ve_b
    assert "sesion_a.xlsx" not in ve_b
    assert "5 documentos" not in ve_b
    # Una ficha cercana a la de otra sesión no abre ninguna.
    _sin_resultados(sin_sesion)
