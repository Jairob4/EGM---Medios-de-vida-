"""Pruebas de M02 `egm.archivo` (T-001-14): P-001-07 y P-001-08.

Esperados escritos a mano a partir de NFR-000-19 y del spec 001 (US-001-4.3, US-001-4.4,
US-001-4.13): el tamaño máximo es 15 728 640 bytes (15 MiB) y el contenido descomprimido declarado
máximo es 268 435 456 bytes (256 MiB), en ambos casos el valor exacto se acepta y un byte más se
rechaza. Ninguno sale de ejecutar `egm.archivo`. Los tamaños grandes se generan en memoria
(fixtures CB-16 y CB-17); nunca se usa `data/raw/`.
"""

import io
import zipfile
from collections.abc import Mapping
from typing import Any

import pytest

from egm.archivo import LIMITE_BYTES, LIMITE_DESCOMPRIMIDO, validar_archivo
from egm.modelo import Rechazo
from tests.constructor import (
    MatrizSintetica,
    archivo_de_texto,
    archivo_extension_xlsx_otro_contenido,
)

PARTES_DEL_LIBRO = ("[Content_Types].xml", "xl/workbook.xml")


def _paquete(partes: Mapping[str, bytes], declarados: Mapping[str, int] | None = None) -> bytes:
    """Un paquete ZIP con `partes`; `declarados` altera solo el tamaño que declara el índice."""
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w", compression=zipfile.ZIP_STORED) as paquete:
        for nombre, datos in partes.items():
            paquete.writestr(nombre, datos)
            if declarados and nombre in declarados:
                paquete.filelist[-1].file_size = declarados[nombre]
    return salida.getvalue()


def _partes_minimas() -> dict[str, bytes]:
    return dict.fromkeys(PARTES_DEL_LIBRO, b"<x/>")


# --- P-001-07: tipo, tamaño y contenido descomprimido ------------------------------------------


def test_los_limites_son_los_de_nfr_000_19() -> None:
    """NFR-000-19: 15 MiB de tamaño y 256 MiB de contenido descomprimido declarado."""
    assert LIMITE_BYTES == 15 * 1024 * 1024 == 15_728_640
    assert LIMITE_DESCOMPRIMIDO == 256 * 1024 * 1024 == 268_435_456


def test_un_libro_valido_se_acepta() -> None:
    """US-001-4.3 (contraparte): un libro `.xlsx` válido no tiene rechazo."""
    assert validar_archivo(MatrizSintetica.base_valida().a_bytes()) is None


def test_texto_plano_es_de_otro_tipo() -> None:
    """SC-000-19, US-001-4.3, CB-16: un archivo de texto es `Rechazo("tipo")`."""
    assert validar_archivo(archivo_de_texto()) == Rechazo("tipo")


@pytest.mark.parametrize("variante", ["texto", "zip_sin_libro"])
def test_extension_correcta_con_otro_contenido_es_de_otro_tipo(variante: str) -> None:
    """SC-000-19, US-001-4.3, CB-16: con la extensión `.xlsx` y otro contenido ⇒ `tipo`.

    `texto`: texto plano. `zip_sin_libro`: un ZIP válido sin las partes de un libro.
    """
    contenido = archivo_extension_xlsx_otro_contenido(variante)
    assert validar_archivo(contenido) == Rechazo("tipo")


def test_archivo_danado_es_de_otro_tipo() -> None:
    """US-001-4.3, CB-16: el libro cortado a la mitad no se puede abrir ⇒ `Rechazo("tipo")`."""
    assert validar_archivo(MatrizSintetica.base_valida().a_bytes_danado()) == Rechazo("tipo")


def test_archivo_vacio_es_de_otro_tipo() -> None:
    """US-001-4.3, CB-16: cero bytes no es un paquete ⇒ `Rechazo("tipo")`."""
    assert validar_archivo(b"") == Rechazo("tipo")


def test_paquete_sin_libro_de_trabajo_es_de_otro_tipo() -> None:
    """US-001-4.3: un ZIP con `[Content_Types].xml` pero sin `xl/workbook.xml` no es un libro."""
    contenido = _paquete({"[Content_Types].xml": b"<x/>"})
    assert validar_archivo(contenido) == Rechazo("tipo")


def test_paquete_sin_tipos_de_contenido_es_de_otro_tipo() -> None:
    """US-001-4.3: un ZIP con `xl/workbook.xml` pero sin `[Content_Types].xml` no es un libro."""
    contenido = _paquete({"xl/workbook.xml": b"<x/>"})
    assert validar_archivo(contenido) == Rechazo("tipo")


def test_el_tamano_exacto_del_limite_se_acepta() -> None:
    """US-001-4.4, NFR-000-19, CB-16: 15 728 640 bytes ⇒ aceptado."""
    contenido = MatrizSintetica.base_valida().a_bytes_de_tamano(15_728_640)
    assert len(contenido) == 15_728_640
    assert validar_archivo(contenido) is None


def test_un_byte_mas_que_el_limite_es_tamano_excedido() -> None:
    """US-001-4.4, NFR-000-19, CB-16: 15 728 641 bytes ⇒ `Rechazo("tamano")`."""
    contenido = MatrizSintetica.base_valida().a_bytes_de_tamano(15_728_641)
    assert len(contenido) == 15_728_641
    assert validar_archivo(contenido) == Rechazo("tamano")


def test_el_tamano_se_comprueba_antes_que_el_tipo() -> None:
    """US-001-4.4: un archivo de otro tipo mayor que el límite es `tamano`, sin leerlo."""
    assert validar_archivo(bytes(15_728_641)) == Rechazo("tamano")


def test_el_descomprimido_declarado_exacto_se_acepta() -> None:
    """US-001-4.13, NFR-000-19, CB-17: declarado 268 435 456 ⇒ aceptado."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(268_435_456)
    assert validar_archivo(contenido) is None


def test_un_byte_mas_de_descomprimido_declarado_es_contenido_excedido() -> None:
    """US-001-4.13, NFR-000-19, CB-17: declarado 268 435 457 ⇒ `Rechazo("contenido")`."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(268_435_457)
    assert validar_archivo(contenido) == Rechazo("contenido")


def test_el_descomprimido_es_la_suma_de_todas_las_partes() -> None:
    """NFR-000-19 («suma de todas las partes»): ninguna parte pasa sola el límite y la suma sí.

    Tres partes que declaran 100 MiB cada una suman 300 MiB (> 256 MiB); con dos, 200 MiB
    (≤ 256 MiB) se acepta.
    """
    cien_mib = 100 * 1024 * 1024
    partes = _partes_minimas()
    partes["xl/hoja_a.xml"] = b"<x/>"
    partes["xl/hoja_b.xml"] = b"<x/>"
    declarados = {"xl/hoja_a.xml": cien_mib, "xl/hoja_b.xml": cien_mib}
    assert validar_archivo(_paquete(partes, declarados)) is None
    partes["xl/hoja_c.xml"] = b"<x/>"
    declarados["xl/hoja_c.xml"] = cien_mib
    assert validar_archivo(_paquete(partes, declarados)) == Rechazo("contenido")


def test_el_limite_de_la_suma_es_exacto_con_varias_partes() -> None:
    """NFR-000-19: con el índice en dos partes, la suma 268 435 456 se acepta y +1 se rechaza."""
    mitad = LIMITE_DESCOMPRIMIDO // 2
    # Las dos partes mínimas del libro declaran 4 bytes cada una (`<x/>`): se cuentan en la suma.
    base = len(PARTES_DEL_LIBRO) * 4
    partes = {**_partes_minimas(), "xl/hoja_a.xml": b"<x/>", "xl/hoja_b.xml": b"<x/>"}
    exacto: Mapping[str, int] = {
        "xl/hoja_a.xml": mitad,
        "xl/hoja_b.xml": LIMITE_DESCOMPRIMIDO - mitad - base,
    }
    mas_uno: Mapping[str, int] = {**exacto, "xl/hoja_b.xml": exacto["xl/hoja_b.xml"] + 1}
    assert validar_archivo(_paquete(partes, exacto)) is None
    assert validar_archivo(_paquete(partes, mas_uno)) == Rechazo("contenido")


def test_el_rechazo_no_lleva_datos_del_archivo() -> None:
    """US-001-4.3, FR-001-29: el rechazo es solo el motivo, sin nombre ni contenido."""
    rechazo = validar_archivo(archivo_de_texto())
    assert isinstance(rechazo, Rechazo)
    assert rechazo.motivo == "tipo"


# --- P-001-08: la comprobación del contenido usa solo el índice del paquete -------------------


def test_datos_comprimidos_invalidos_con_declarado_excedido_no_dan_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NFR-000-19 («sin descomprimir ninguna»), CB-17 +1 con datos comprimidos inválidos.

    La parte de relleno declara más que el límite y sus datos no son un flujo válido: el
    resultado es `Rechazo("contenido")` sin error, y ninguna parte se lee ni se descomprime.
    """

    def _no_debe_leerse(*_argumentos: Any, **_opciones: Any) -> None:
        raise AssertionError("M02 no debe leer ni descomprimir ninguna parte del paquete")

    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(
        268_435_457, datos_invalidos=True
    )
    monkeypatch.setattr(zipfile.ZipFile, "read", _no_debe_leerse)
    monkeypatch.setattr(zipfile.ZipFile, "open", _no_debe_leerse)
    monkeypatch.setattr(zipfile.ZipFile, "testzip", _no_debe_leerse)
    assert validar_archivo(contenido) == Rechazo("contenido")


def test_datos_invalidos_con_declarado_exacto_se_aceptan_sin_leerlos() -> None:
    """NFR-000-19: dentro del límite, M02 no mira los datos; abrirlos es tarea de `egm.libro`."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(
        268_435_456, datos_invalidos=True
    )
    assert validar_archivo(contenido) is None
