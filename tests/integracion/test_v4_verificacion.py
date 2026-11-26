"""Historia 3 del plan 001: verificación de la matriz real (v4) contra su hoja EGM (T-001-40).

Prueba P-001-46 · US-001-3.3, FR-001-16, FR-001-17, FR-001-25, SC-001-01, CB-30.

La v4 no trae valores calculados guardados en la hoja EGM (apéndice A del contrato de datos: 0
celdas numéricas), así que la verificación esperada es «no verificable», con advertencia, sin lista
de tablas verificadas y sin tomar ningún valor ausente por 0. La prueba abre `data/raw/` solo en
modo binario de lectura (`open(ruta, "rb")`), entrega los bytes a `egm.libro.abrir` y comprueba que
el archivo queda idéntico (SHA-256 del apéndice A). La misma comprobación, con el fixture sintético
`cb30_sin_valores_guardados` (la otra fixture de P-001-46), corre sin la marca `raw`.

`egm.verificacion` se importa dentro de cada prueba: mientras no exista, falla la prueba y no la
recolección. Los esperados están escritos a mano desde el apéndice A y el contrato §7.
"""

import hashlib
from pathlib import Path
from typing import Any

import pytest

from egm.libro import abrir
from tests.constructor import carpeta_de_fixtures

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
TIPOS = {"total", "evaluacion_impacto", "nivel"}


def _bytes_v4() -> bytes:
    """Los bytes de la v4, abierta solo en modo binario de lectura."""
    with open(RUTA_V4, "rb") as archivo:
        return archivo.read()


def _sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest().lower()


def _verificar(contenido: bytes) -> Any:
    """`abrir`, `descubrir`, `leer` y `verificar`; devuelve la `Verificacion`."""
    from egm.esquema import descubrir
    from egm.lectura import leer
    from egm.verificacion import verificar

    libro = abrir(contenido)
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "no debe dar un fallo de contrato"
    corpus = leer(libro, esquema)
    return verificar(libro, esquema, corpus)


def _comprobar_no_verificable(v: Any) -> None:
    """Ninguna tabla se pudo comparar: sin lista de verificadas, sin diferencias y con aviso."""
    assert v.verificadas == ()
    # Con la hoja reconocida hay tres tablas comparables; ninguna «coincide» ni «difiere». Si un
    # valor ausente se tomara por 0, las celdas en 0 de la herramienta darían «coincide».
    assert {t.tipo for t in v.tablas} == TIPOS
    assert len(v.tablas) == 3  # solo las tres comparables (arquitectura §6.1, M08)
    assert all(t.estado.name == "NO_VERIFICABLE" for t in v.tablas)
    assert all(t.diferencias == () for t in v.tablas)
    assert len(v.advertencias) >= 1


@pytest.mark.raw
@omitir_sin_v4
def test_p_001_46_la_v4_no_es_verificable_y_queda_intacta() -> None:
    """P-001-46 · US-001-3.3, FR-001-16, FR-001-17, FR-001-25, SC-001-01, CB-30: la v4.

    Resultado «no verificable» con advertencia, lista de tablas verificadas vacía y ningún ausente
    tomado como 0; el SHA-256 de la v4 es el mismo antes y después.
    """
    antes = _sha256(_bytes_v4())
    assert antes == SHA256_V4  # el archivo vigente es el del apéndice A

    v = _verificar(_bytes_v4())

    _comprobar_no_verificable(v)
    despues = _sha256(_bytes_v4())
    assert despues == antes
    assert despues == SHA256_V4


def test_p_001_46_cb30_sin_valores_guardados_no_es_verificable() -> None:
    """P-001-46 · US-001-3.3, FR-001-16, FR-001-17, CB-30: cb30_sin_valores_guardados.

    Fixture sintético equivalente a la v4 en lo que importa: las tablas de la hoja EGM tienen sus
    fórmulas y ningún valor guardado.
    """
    contenido = (carpeta_de_fixtures() / "cb30_sin_valores_guardados.xlsx").read_bytes()

    v = _verificar(contenido)

    _comprobar_no_verificable(v)
