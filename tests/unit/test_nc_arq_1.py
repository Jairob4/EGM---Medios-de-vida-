"""P-001-02: caracterización de NC-ARQ-1 (T-001-09). Spec 001, casos borde («archivo dañado»).

Qué hacen la biblioteca de paquetes de Python (`zipfile`) y `openpyxl` ante un libro que tiene una
parte que se descomprime a más de lo que declara el índice del paquete. Todo en memoria
(`io.BytesIO`); no se escribe ni se abre ningún archivo.

Resultado observado el 2026-11-24 con Python 3.13.15 (MSC v.1944, 64 bit) y openpyxl 3.1.5:

- **Nunca se lee más de lo declarado.** `zipfile` acota la lectura de cada parte al tamaño que
  declara el índice (`ZipInfo.file_size`); lo que sobra del flujo comprimido no se descomprime.
- Con el libro `parte_mayor_que_lo_declarado` (el CRC-32 del índice es el de la parte completa),
  `zipfile` falla con `BadZipFile("Bad CRC-32 …")` al llegar al final de lo declarado, antes de
  entregar la parte completa: `testzip()` devuelve el nombre de la parte, `read()` lanza
  `BadZipFile`, y `openpyxl.load_workbook` lanza `BadZipFile` en modo normal y en `read_only=True`.
- Si el índice trae además un CRC-32 coherente con los bytes declarados (paquete armado a
  propósito), `zipfile` entrega exactamente los bytes declarados, sin error. Entonces: si el
  recorte parte el XML, `openpyxl` falla con `xml.etree.ElementTree.ParseError` (al abrir en
  modo normal; al leer la hoja en `read_only=True`); si el recorte cae justo después del
  cierre de la hoja, el libro se abre y se lee completo, y el resto del flujo no se
  descomprime.

Efecto para M02 y M03 (arquitectura §4): el libro del fixture se rechaza como tipo no admitido
(`Rechazo("tipo")`) porque falla con `BadZipFile`; el caso del CRC coherente exige además que M03
trate también `ParseError` como archivo dañado. No hay lectura de más sin error.

Los esperados están escritos a mano a partir de esa observación: si una versión nueva de la
biblioteca cambia el comportamiento, estas pruebas lo hacen visible.
"""

import io
import struct
import zipfile
import zlib
from xml.etree.ElementTree import ParseError

import openpyxl
import pytest

from tests.constructor import MatrizSintetica, parte_mayor_que_lo_declarado

_PARTE = "xl/worksheets/sheet1.xml"
_HOJA = "Matriz bibliográfica"
_REAL = 1_048_576  # bytes que la parte descomprime de verdad (fixture de T-001-06)


def _flujo_crudo(contenido: bytes, nombre: str) -> bytes:
    """Descomprime el flujo completo de una parte, sin pasar por el límite de `zipfile`."""
    with zipfile.ZipFile(io.BytesIO(contenido)) as zf:
        info = zf.getinfo(nombre)
    desplazamiento = info.header_offset
    largo_nombre, largo_extra = struct.unpack(
        "<HH", contenido[desplazamiento + 26 : desplazamiento + 30]
    )
    inicio = desplazamiento + 30 + largo_nombre + largo_extra
    return zlib.decompressobj(-15).decompress(contenido[inicio : inicio + info.compress_size])


def _libro_con_parte(real: bytes, declarado: int, crc_de: bytes) -> bytes:
    """El libro base con `_PARTE` de `real` bytes, un índice que declara `declarado` bytes y el
    CRC-32 de `crc_de` (paquete armado a propósito; solo el índice se altera)."""
    base = MatrizSintetica.base_valida().a_bytes()
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(base)) as origen, zipfile.ZipFile(salida, "w") as destino:
        for info in origen.infolist():
            datos = real if info.filename == _PARTE else origen.read(info.filename)
            nueva = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            nueva.compress_type = zipfile.ZIP_DEFLATED
            destino.writestr(nueva, datos)
            if info.filename == _PARTE:
                registrada = destino.filelist[-1]
                registrada.file_size = declarado
                registrada.CRC = zlib.crc32(crc_de)
    return salida.getvalue()


@pytest.fixture(scope="module")
def libro() -> bytes:
    return parte_mayor_que_lo_declarado()


def test_el_fixture_declara_menos_de_lo_que_descomprime(libro: bytes) -> None:
    """P-001-02 (premisa): el índice declara menos que el flujo; el paquete es pequeño."""
    with zipfile.ZipFile(io.BytesIO(libro)) as zf:
        declarado = zf.getinfo(_PARTE).file_size
    assert len(libro) < 100_000
    assert 0 < declarado < _REAL
    assert len(_flujo_crudo(libro, _PARTE)) == _REAL


def test_zipfile_testzip_senala_la_parte(libro: bytes) -> None:
    """P-001-02 / NC-ARQ-1: `testzip()` devuelve el nombre de la parte con CRC incorrecto."""
    with zipfile.ZipFile(io.BytesIO(libro)) as zf:
        assert zf.testzip() == _PARTE


def test_zipfile_read_falla_con_badzipfile_sin_entregar_la_parte(libro: bytes) -> None:
    """P-001-02 / NC-ARQ-1: `read()` lanza `BadZipFile` (CRC-32); no entrega bytes de más."""
    with zipfile.ZipFile(io.BytesIO(libro)) as zf:
        with pytest.raises(zipfile.BadZipFile, match="Bad CRC-32"):
            zf.read(_PARTE)
        with pytest.raises(zipfile.BadZipFile, match="Bad CRC-32"):
            zf.open(_PARTE).read()


def test_zipfile_por_trozos_no_pasa_de_lo_declarado(libro: bytes) -> None:
    """P-001-02 / NC-ARQ-1: leyendo por trozos, se falla antes de entregar lo declarado."""
    with zipfile.ZipFile(io.BytesIO(libro)) as zf:
        declarado = zf.getinfo(_PARTE).file_size
        entregado = 0
        parte = zf.open(_PARTE)
        try:
            while trozo := parte.read(1000):
                entregado += len(trozo)
        except zipfile.BadZipFile as error:
            fallo: Exception | None = error
        else:
            fallo = None
        finally:
            parte.close()
    assert fallo is not None
    assert entregado < declarado < _REAL


@pytest.mark.parametrize("solo_lectura", [False, True])
def test_openpyxl_falla_con_badzipfile_al_abrir(libro: bytes, solo_lectura: bool) -> None:
    """P-001-02 / NC-ARQ-1: `load_workbook` lanza `BadZipFile`, en modo normal y `read_only`."""
    with pytest.raises(zipfile.BadZipFile, match="Bad CRC-32"):
        openpyxl.load_workbook(io.BytesIO(libro), read_only=solo_lectura)


def test_con_crc_coherente_zipfile_entrega_solo_lo_declarado() -> None:
    """P-001-02 / NC-ARQ-1: con CRC coherente con lo declarado, `read()` entrega exactamente
    los bytes declarados, sin error, y no los `_REAL` del flujo."""
    base = parte_mayor_que_lo_declarado()
    real = _flujo_crudo(base, _PARTE)
    with zipfile.ZipFile(io.BytesIO(base)) as zf:
        declarado = zf.getinfo(_PARTE).file_size
    armado = _libro_con_parte(real, declarado, real[:declarado])
    with zipfile.ZipFile(io.BytesIO(armado)) as zf:
        assert zf.getinfo(_PARTE).file_size == declarado
        assert zf.testzip() is None
        entregado = zf.read(_PARTE)
    assert len(entregado) == declarado
    assert entregado == real[:declarado]
    assert len(real) == _REAL


def test_con_crc_coherente_y_recorte_que_parte_el_xml_openpyxl_falla_con_parseerror() -> None:
    """P-001-02 / NC-ARQ-1: recorte dentro del XML: `ParseError` al abrir (modo normal) o al
    leer la hoja (`read_only=True`); nunca se lee más de lo declarado."""
    base = parte_mayor_que_lo_declarado()
    real = _flujo_crudo(base, _PARTE)
    with zipfile.ZipFile(io.BytesIO(base)) as zf:
        declarado = zf.getinfo(_PARTE).file_size
    armado = _libro_con_parte(real, declarado, real[:declarado])
    with pytest.raises(ParseError, match="unclosed token"):
        openpyxl.load_workbook(io.BytesIO(armado))
    libro_solo_lectura = openpyxl.load_workbook(io.BytesIO(armado), read_only=True)
    with pytest.raises(ParseError, match="unclosed token"):
        list(libro_solo_lectura[_HOJA].iter_rows(values_only=True))
    libro_solo_lectura.close()


def test_con_crc_coherente_y_recorte_tras_el_cierre_el_libro_se_lee_sin_pasar_de_lo_declarado() -> (
    None
):
    """P-001-02 / NC-ARQ-1: recorte justo tras `</worksheet>`: el libro abre y se lee igual que
    el original; el resto del flujo (un comentario XML de relleno) no se descomprime."""
    original = _flujo_crudo(MatrizSintetica.base_valida().a_bytes(), _PARTE)
    relleno = b"<!--" + b"x" * (_REAL - len(original) - 7) + b"-->"
    real = original + relleno
    armado = _libro_con_parte(real, len(original), original)
    assert len(real) == _REAL
    with zipfile.ZipFile(io.BytesIO(armado)) as zf:
        assert len(zf.read(_PARTE)) == len(original)

    def filas(contenido: bytes) -> list[tuple[object, ...]]:
        libro_abierto = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True)
        try:
            return list(libro_abierto[_HOJA].iter_rows(values_only=True))
        finally:
            libro_abierto.close()

    leidas = filas(armado)
    assert len(leidas) > 1
    assert leidas == filas(MatrizSintetica.base_valida().a_bytes())
