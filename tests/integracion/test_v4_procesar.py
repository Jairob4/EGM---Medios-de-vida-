"""Fase 6 del plan 001: la fachada `procesar` sobre la matriz real (v4) (T-001-50).

Prueba P-001-65 · US-001-1.7 (identificación), FR-001-19, NFR-000-09.

La prueba abre `data/raw/` solo en modo binario de lectura (`open(ruta, "rb")`), entrega los bytes
a `egm.procesamiento.procesar` y comprueba que el archivo queda idéntico (SHA-256 del apéndice A
del contrato de datos). Los esperados están escritos a mano a partir de `referencia-v4.md`: 27
documentos (N.º 1 a 27, filas 2 a 28) y ninguna tabla verificada, porque la v4 no trae valores
calculados guardados.

`egm.procesamiento` se importa dentro de cada prueba: mientras no exista, falla la prueba y no la
recolección.
"""

import hashlib
from datetime import datetime
from pathlib import Path

import pytest

RUTA_V4 = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "matriz_bibliografica_estado_del_arte_v4.xlsx"
)

omitir_sin_v4 = pytest.mark.skipif(
    not RUTA_V4.is_file(),
    reason="no está la matriz v4 en data/raw/: la prueba contra la matriz real no se puede correr",
)

SHA256_V4 = "7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1".lower()
NOMBRE_V4 = "matriz_bibliografica_estado_del_arte_v4.xlsx"


def _bytes_v4() -> bytes:
    """Los bytes de la v4, abierta solo en modo binario de lectura."""
    with open(RUTA_V4, "rb") as archivo:
        return archivo.read()


def _sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest().lower()


@pytest.mark.raw
@omitir_sin_v4
def test_p_001_65_la_v4_se_identifica_con_el_nombre_y_la_fecha_inyectada() -> None:
    """P-001-65 · US-001-1.7, FR-001-19, NFR-000-09: nombre tal como llegó y fecha dada."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    contenido = _bytes_v4()
    assert _sha256(contenido) == SHA256_V4
    fecha = datetime(2031, 5, 17, 9, 30, 45)

    resultado = procesar(contenido, NOMBRE_V4, fecha)

    assert isinstance(resultado, ResultadoLectura)
    assert resultado.identificacion.nombre_archivo == NOMBRE_V4
    assert resultado.identificacion.fecha_lectura == fecha
    assert resultado.identificacion.fecha_lectura is fecha
    # La matriz leída es la v4: 27 documentos en las filas 2 a 28 (referencia-v4.md).
    assert len(resultado.corpus.documentos) == 27
    assert resultado.corpus.fila_final_leida == 28
    # La v4 no trae valores guardados en la hoja EGM: ninguna tabla comparable se verificó.
    assert resultado.verificacion.verificadas == ()
    # El archivo de data/raw/ queda idéntico.
    assert _sha256(_bytes_v4()) == SHA256_V4


@pytest.mark.raw
@omitir_sin_v4
def test_p_001_65_el_nombre_llega_sin_cambios_aunque_no_sea_el_del_archivo() -> None:
    """P-001-65 · US-001-1.7, FR-001-19: ningún nombre se corrige ni se deduce una versión."""
    from egm.modelo import ResultadoLectura
    from egm.procesamiento import procesar

    nombre = "  Mi matriz (copia)  ñ final.XLSX "
    fecha = datetime(2026, 11, 25, 8, 0, 0)

    resultado = procesar(_bytes_v4(), nombre, fecha)

    assert isinstance(resultado, ResultadoLectura)
    assert resultado.identificacion.nombre_archivo == nombre
    assert resultado.identificacion.fecha_lectura == fecha
    assert _sha256(_bytes_v4()) == SHA256_V4
