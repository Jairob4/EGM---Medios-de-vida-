"""Fase 6 del plan 001: la fachada del núcleo `egm.procesamiento.procesar` (T-001-50).

Pruebas P-001-66 a P-001-70. La fachada encadena M02 (validar), M03 (abrir), M04 (descubrir),
M05 (leer) y M08 (verificar) y devuelve un resultado inmutable, un `Rechazo` o un `FalloContrato`,
nunca resultados parciales (arquitectura §5 y §6.1, M13).

`egm.procesamiento` se importa dentro de cada prueba: mientras no exista, falla la prueba y no la
recolección. Los esperados están escritos a mano a partir del plan, la arquitectura y los
contratos; ninguno sale de ejecutar `procesar`.
"""

import dataclasses
import json
import subprocess
import sys
import zipfile
from collections import Counter
from collections.abc import Callable
from datetime import datetime
from typing import Any
from xml.etree.ElementTree import ParseError

import pytest

from tests.constructor import (
    CATALOGO,
    EN_MEMORIA,
    MatrizSintetica,
    archivo_de_texto,
    parte_mayor_que_lo_declarado,
)

NOMBRE = "matriz de prueba (copia).xlsx"
FECHA_A = datetime(2026, 11, 25, 10, 0, 0)
FECHA_B = datetime(2031, 1, 2, 23, 59, 59)

# Códigos de las advertencias que emite M08 (ADR-002), escritos a mano.
CODIGOS_DE_VERIFICACION = frozenset(
    {
        "hoja_egm_ausente",
        "tabla_no_reconocida",
        "comparacion_incompleta",
        "tabla_difiere",
        "hoja_abarca_menos_filas",
    }
)


def _fixture(nombre: str) -> bytes:
    """Los bytes de un fixture del catálogo (o de los que solo viven en memoria), generado al
    momento y sin escribir nada."""
    generador = CATALOGO.get(nombre) or EN_MEMORIA[nombre]
    return generador()


def _base() -> bytes:
    return MatrizSintetica.base_valida().a_bytes()


# --- P-001-66 ----------------------------------------------------------------------------------


@pytest.mark.parametrize("nombre_fixture", ["base_valida.xlsx", "esc_3_2_difiere_g_igual_h.xlsx"])
def test_p_001_66_mismos_bytes_y_nombre_dan_resultados_iguales_salvo_la_fecha(
    nombre_fixture: str,
) -> None:
    """P-001-66 · SC-000-09, NFR-000-09: determinismo; la fecha es lo único que cambia."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    contenido = _fixture(nombre_fixture)

    primero = procesar(contenido, NOMBRE, FECHA_A)
    segundo = procesar(contenido, NOMBRE, FECHA_B)

    assert isinstance(primero, ResultadoLectura)
    assert isinstance(segundo, ResultadoLectura)
    assert primero.identificacion.fecha_lectura == FECHA_A
    assert segundo.identificacion.fecha_lectura == FECHA_B
    assert primero != segundo  # la fecha sí distingue los resultados
    igualado = dataclasses.replace(segundo, identificacion=primero.identificacion)
    assert primero == igualado
    assert primero.corpus == segundo.corpus
    assert primero.esquema == segundo.esquema
    assert primero.advertencias == segundo.advertencias
    assert primero.notas == segundo.notas
    assert primero.verificacion == segundo.verificacion


def test_p_001_66_la_identificacion_es_el_nombre_y_la_fecha_dados() -> None:
    """P-001-66 · NFR-000-09: nombre tal como llegó y fecha inyectada, sin leer el reloj."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    nombre = "  Otra matriz  (v9) ñ.XLSX "
    fecha = datetime(1999, 12, 31, 23, 59, 59)  # una fecha que el reloj nunca daría hoy

    resultado = procesar(_base(), nombre, fecha)

    assert isinstance(resultado, ResultadoLectura)
    assert resultado.identificacion.nombre_archivo == nombre
    assert resultado.identificacion.fecha_lectura is fecha


def test_p_001_66_el_nombre_no_cambia_la_lectura() -> None:
    """P-001-66 · NFR-000-09: dos nombres dan la misma lectura, salvo la identificación."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    contenido = _base()
    uno = procesar(contenido, "uno.xlsx", FECHA_A)
    otro = procesar(contenido, "otro.xlsx", FECHA_A)

    assert isinstance(uno, ResultadoLectura)
    assert isinstance(otro, ResultadoLectura)
    assert uno.identificacion.nombre_archivo == "uno.xlsx"
    assert otro.identificacion.nombre_archivo == "otro.xlsx"
    assert dataclasses.replace(otro, identificacion=uno.identificacion) == uno


# --- P-001-67 ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("nombre_fixture", "codigo_esperado"),
    [
        ("cb14_sin_nivel_de_evidencia.xlsx", "encabezado_ausente"),
        ("cb15_sin_hoja_matriz.xlsx", "hoja_ausente"),
        ("cb20_sin_ancla_empirico.xlsx", "ancla_empirica_ausente"),
        ("cb24_nivel_sin_lista.xlsx", "lista_obligatoria_ausente"),
    ],
)
def test_p_001_67_un_error_de_contrato_devuelve_solo_el_fallo(
    nombre_fixture: str, codigo_esperado: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P-001-67 · FR-001-02, FR-001-29, US-001-2.4, US-001-2.7: sin corpus ni conteos."""
    from egm import lectura, verificacion
    from egm.modelo import FalloContrato
    from egm.procesamiento import procesar

    llamadas: list[str] = []
    leer_real = lectura.leer
    verificar_real = verificacion.verificar

    def leer_espiado(*argumentos: Any, **claves: Any) -> Any:
        llamadas.append("leer")
        return leer_real(*argumentos, **claves)

    def verificar_espiado(*argumentos: Any, **claves: Any) -> Any:
        llamadas.append("verificar")
        return verificar_real(*argumentos, **claves)

    monkeypatch.setattr(lectura, "leer", leer_espiado)
    monkeypatch.setattr(verificacion, "verificar", verificar_espiado)

    resultado = procesar(_fixture(nombre_fixture), NOMBRE, FECHA_A)

    assert isinstance(resultado, FalloContrato)
    assert [e.codigo for e in resultado.errores] == [codigo_esperado]
    # Solo el fallo: ni corpus, ni esquema, ni conteos, ni verificación.
    assert {c.name for c in dataclasses.fields(resultado)} == {"errores"}
    assert not hasattr(resultado, "corpus")
    assert llamadas == []  # tras el error de contrato no se lee ni se verifica nada


def test_p_001_67_el_fallo_no_lleva_el_nombre_del_archivo() -> None:
    """P-001-67 · FR-001-29, NFR-000-17: el fallo no repite el nombre que llegó."""
    from egm.modelo import FalloContrato
    from egm.procesamiento import procesar

    nombre = "nombre-secreto-123.xlsx"
    resultado = procesar(_fixture("cb14_sin_nivel_de_evidencia.xlsx"), nombre, FECHA_A)

    assert isinstance(resultado, FalloContrato)
    assert nombre not in repr(resultado)


# --- P-001-68 ----------------------------------------------------------------------------------


@pytest.fixture
def abrir_prohibido(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Cambia `egm.libro.abrir` por una función que anota la llamada; la lista queda vacía si
    nadie abrió el libro."""
    from egm import libro

    llamadas: list[int] = []

    def abrir_falso(contenido: bytes) -> Any:
        llamadas.append(len(contenido))
        raise AssertionError("no debía abrirse el libro de un archivo rechazado")

    monkeypatch.setattr(libro, "abrir", abrir_falso)
    return llamadas


@pytest.mark.parametrize(
    ("generar", "motivo"),
    [
        (archivo_de_texto, "tipo"),
        (lambda: _fixture("cb16_extension_xlsx_otro_contenido.xlsx"), "tipo"),
        (lambda: _fixture("cb16_danado.xlsx"), "tipo"),
        (lambda: _fixture("cb16_tamano_mas_uno"), "tamano"),
        (lambda: _fixture("cb17_declarado_mas_uno"), "contenido"),
    ],
    ids=["cb16_texto", "cb16_extension", "cb16_danado", "cb16_tamano", "cb17_contenido"],
)
def test_p_001_68_un_archivo_rechazado_no_abre_el_libro(
    generar: Callable[[], bytes], motivo: str, abrir_prohibido: list[int]
) -> None:
    """P-001-68 · SC-000-19, NFR-000-19, US-001-4.3, 4.4, 4.13: `Rechazo` antes de abrir."""
    from egm.modelo import Rechazo
    from egm.procesamiento import procesar

    resultado = procesar(generar(), NOMBRE, FECHA_A)

    assert resultado == Rechazo(motivo)  # type: ignore[arg-type]
    assert abrir_prohibido == []  # `abrir` no se llamó


def test_p_001_68_los_limites_exactos_se_aceptan() -> None:
    """P-001-68 · SC-000-19, NFR-000-19: el valor exacto de cada límite no se rechaza."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    for nombre in ("cb16_tamano_exacto", "cb17_declarado_exacto"):
        resultado = procesar(_fixture(nombre), NOMBRE, FECHA_A)
        assert isinstance(resultado, ResultadoLectura), nombre


def test_p_001_68_la_parte_que_excede_lo_declarado_es_tipo() -> None:
    """P-001-68 · NC-ARQ-1, SC-000-19: la parte mayor que lo declarado es un archivo dañado."""
    from egm.modelo import Rechazo
    from egm.procesamiento import procesar

    resultado = procesar(parte_mayor_que_lo_declarado(), NOMBRE, FECHA_A)

    assert resultado == Rechazo("tipo")


@pytest.mark.parametrize(
    "error",
    [
        ParseError("XML partido"),
        zipfile.BadZipFile("CRC incoherente"),
        EOFError("fin inesperado"),
        KeyError("xl/workbook.xml"),
        RuntimeError("falla cualquiera"),
    ],
    ids=lambda error: type(error).__name__,
)
def test_p_001_68_toda_excepcion_al_abrir_es_archivo_danado(
    error: Exception, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P-001-68 · NC-ARQ-1, SC-000-19: toda excepción al abrir ⇒ `Rechazo("tipo")`."""
    from egm import libro
    from egm.modelo import Rechazo
    from egm.procesamiento import procesar

    def abrir_que_falla(contenido: bytes) -> Any:
        raise error

    monkeypatch.setattr(libro, "abrir", abrir_que_falla)

    resultado = procesar(_base(), NOMBRE, FECHA_A)

    assert resultado == Rechazo("tipo")


def test_p_001_68_un_libro_que_no_se_abre_se_rechaza_como_tipo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-68 · NC-ARQ-1: `LibroNoAbrible` de M03 ⇒ `Rechazo("tipo")`, sin dejar el error."""
    from egm import libro
    from egm.modelo import Rechazo
    from egm.procesamiento import procesar

    def abrir_que_falla(contenido: bytes) -> Any:
        raise libro.LibroNoAbrible("El archivo no se pudo abrir.")

    monkeypatch.setattr(libro, "abrir", abrir_que_falla)

    resultado = procesar(_base(), NOMBRE, FECHA_A)

    assert resultado == Rechazo("tipo")


# --- P-001-69 ----------------------------------------------------------------------------------


def test_p_001_69_las_advertencias_de_verificacion_van_primero() -> None:
    """P-001-69 · FR-001-18, ADR-002 punto 5: la verificación se advierte antes que lo demás."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    resultado = procesar(_fixture("esc_3_2_difiere_g_igual_h.xlsx"), NOMBRE, FECHA_A)

    assert isinstance(resultado, ResultadoLectura)
    codigos = [a.codigo for a in resultado.advertencias]
    # La hoja cuenta dos veces el estudio con G = H: la verificación advierte la diferencia y la
    # lectura advierte la fila con la misma intervención principal y secundaria.
    assert "tabla_difiere" in codigos
    assert "principal_igual_secundaria" in codigos
    posiciones_de_verificacion = [
        i for i, codigo in enumerate(codigos) if codigo in CODIGOS_DE_VERIFICACION
    ]
    posiciones_de_lectura = [
        i for i, codigo in enumerate(codigos) if codigo not in CODIGOS_DE_VERIFICACION
    ]
    assert posiciones_de_verificacion
    assert posiciones_de_lectura
    assert max(posiciones_de_verificacion) < min(posiciones_de_lectura)
    assert codigos[0] in CODIGOS_DE_VERIFICACION


def test_p_001_69_ninguna_advertencia_se_pierde_ni_se_repite() -> None:
    """P-001-69 · FR-001-18: las advertencias del resultado son las de la verificación, el
    esquema y el corpus, cada una una vez, con la verificación primero."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    resultado = procesar(_fixture("esc_3_2_difiere_g_igual_h.xlsx"), NOMBRE, FECHA_A)

    assert isinstance(resultado, ResultadoLectura)
    de_verificacion = resultado.verificacion.advertencias
    esperadas = (*de_verificacion, *resultado.esquema.advertencias, *resultado.corpus.advertencias)
    assert resultado.advertencias == esperadas
    assert Counter(a.codigo for a in resultado.advertencias) == Counter(a.codigo for a in esperadas)
    assert len(de_verificacion) >= 1


def test_p_001_69_las_notas_son_las_del_esquema() -> None:
    """P-001-69 · FR-001-18, US-001-4.9: la columna ajena sin lista queda como nota informativa."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    resultado = procesar(_fixture("cb18_columna_observaciones.xlsx"), NOMBRE, FECHA_A)

    assert isinstance(resultado, ResultadoLectura)
    assert [n.codigo for n in resultado.notas] == ["columnas_no_usadas"]
    assert resultado.notas == resultado.esquema.notas


# --- P-001-70 ----------------------------------------------------------------------------------

_SCRIPT_DEL_PROCESO_APARTE = """
import json
import sys
from datetime import datetime

from egm import conteo
from egm.modelo import ResultadoLectura
from egm.procesamiento import procesar

contenido = sys.stdin.buffer.read()
resultado = procesar(contenido, "base.xlsx", datetime(2026, 11, 25))
assert isinstance(resultado, ResultadoLectura), type(resultado).__name__
mapa = conteo.mapa(resultado.esquema, resultado.corpus)
prohibidos = ("app", "fastapi", "starlette", "jinja2", "uvicorn")
cargados = sorted(
    nombre
    for nombre in sys.modules
    if nombre.split(".")[0] in prohibidos
)
print(json.dumps({"cargados": cargados, "documentos": len(resultado.corpus.documentos)}))
"""


def test_p_001_70_procesar_no_carga_la_capa_web() -> None:
    """P-001-70 · SC-000-14, NFR-000-14: en un proceso aparte, ni `app` ni las bibliotecas web."""
    contenido = _base()

    completado = subprocess.run(
        [sys.executable, "-c", _SCRIPT_DEL_PROCESO_APARTE],
        input=contenido,
        capture_output=True,
        check=False,
        timeout=120,
    )

    assert completado.returncode == 0, completado.stderr.decode("utf-8", errors="replace")
    salida = json.loads(completado.stdout.decode("utf-8"))
    assert salida["cargados"] == []
    assert salida["documentos"] > 0  # la prueba corrió de verdad, no se saltó la lectura
