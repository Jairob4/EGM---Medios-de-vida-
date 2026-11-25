"""Historia 2 del plan 001: advertencias de la matriz real (v4) en modo lectura.

Pruebas P-001-28 y P-001-39 (T-001-30). Abren `data/raw/` solo en modo binario de lectura
(`open(ruta, "rb")`) y entregan los bytes a `egm.libro.abrir`; nunca escriben. Llaman a `descubrir`
(M04), `leer` (M05) y a `egm.textos` (M10); los módulos que la historia 2 amplía se importan dentro
de cada prueba, para que la ausencia de una función falle solo esa prueba y no la recolección.

Los esperados están escritos a mano desde el apéndice A del contrato de datos
(`docs/specs/contrato-datos.md`), desde la sección 6 del contrato y desde el ejemplo de F-001-2 de
`docs/interfaz/flujos.md`, no desde la salida del código bajo prueba.
"""

from pathlib import Path
from typing import Any

import pytest

from egm.libro import abrir
from egm.modelo import Enfoque, EstadoDocumento, Rol

pytestmark = pytest.mark.raw

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

# --- Esperados del apéndice A (v4) ------------------------------------------------------------

# Estudios empíricos que aún no entran al mapa (apéndice A, «Estados»; F-001-2).
NUMEROS_PENDIENTES = {"10", "11", "13", "15", "16", "24"}

# Enfoque: 2 «Sin clasificar», los N.º 2 y 7 (apéndice A, «Enfoque (todo el corpus)»).
NUMEROS_ENFOQUE_SIN_CLASIFICAR = {"2", "7"}

# Encabezado de la columna de enfoque (contrato §2, tabla de roles).
COLUMNA_ENFOQUE = "Enfoque de género/diferencial"

# Código provisional con que M05 marca la advertencia de enfoque (`egm.lectura`).
CODIGO_ENFOQUE = "enfoque_sin_clasificar"


# --- Ayudas -----------------------------------------------------------------------------------


def _bytes_v4() -> bytes:
    """Los bytes de la v4, abierta solo en modo binario de lectura."""
    with open(RUTA_V4, "rb") as archivo:
        return archivo.read()


def _leer_v4() -> Any:
    """`abrir`, `descubrir` y `leer` sobre la v4; devuelve el `Corpus`."""
    from egm.esquema import descubrir
    from egm.lectura import leer

    libro = abrir(_bytes_v4())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "la v4 no debe dar un fallo de contrato"
    return leer(libro, esquema)


# --- P-001-28 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_28_pendientes_de_la_v4() -> None:
    """P-001-28 · US-001-2.3, FR-001-13: pendientes N.º 10, 11, 13, 15, 16 y 24."""
    corpus = _leer_v4()

    pendientes = [d for d in corpus.documentos if d.estado == EstadoDocumento.EMPIRICO_PENDIENTE]
    assert len(pendientes) == 6
    assert {str(d.ref.numero) for d in pendientes} == NUMEROS_PENDIENTES
    # Cada uno con su fila del archivo, para la trazabilidad, y sin repetirse.
    assert len({d.ref.fila for d in pendientes}) == 6
    assert all(d.ref.fila >= 2 for d in pendientes)

    # Ninguno de los pendientes es el que ya está en el mapa (N.º 7).
    en_el_mapa = {
        str(d.ref.numero) for d in corpus.documentos if d.estado == EstadoDocumento.EN_EL_MAPA
    }
    assert en_el_mapa == {"7"}
    assert en_el_mapa.isdisjoint(NUMEROS_PENDIENTES)


# --- P-001-39 ---------------------------------------------------------------------------------


def _advertencias_de_enfoque(corpus: Any) -> list[Any]:
    """Las advertencias de enfoque del corpus: por su código o por su columna."""
    return [
        a for a in corpus.advertencias if a.codigo == CODIGO_ENFOQUE or a.columna == COLUMNA_ENFOQUE
    ]


@omitir_sin_v4
def test_p_001_39_enfoque_sin_clasificar_de_la_v4_con_su_advertencia() -> None:
    """P-001-39 · US-001-2.14, FR-001-10, CB-11: N.º 2 y 7 Sin clasificar, una advertencia c/u."""
    corpus = _leer_v4()

    sin_clasificar = {
        str(d.ref.numero): d for d in corpus.documentos if d.enfoque == Enfoque.SIN_CLASIFICAR
    }
    assert set(sin_clasificar) == NUMEROS_ENFOQUE_SIN_CLASIFICAR

    advertencias = _advertencias_de_enfoque(corpus)
    # Exactamente una por documento «Sin clasificar», y ninguna otra de enfoque.
    assert len(advertencias) == 2
    por_numero = {str(a.ref.numero): a for a in advertencias if a.ref is not None}
    assert set(por_numero) == NUMEROS_ENFOQUE_SIN_CLASIFICAR

    for numero, advertencia in por_numero.items():
        documento = sin_clasificar[numero]
        assert advertencia.ambito == "fila"
        assert advertencia.ref == documento.ref
        assert advertencia.columna == COLUMNA_ENFOQUE
        # El valor es el texto de la celda, sin corregir (contrato §6: se muestra completo).
        texto_celda = documento.textos[Rol.ENFOQUE]
        assert texto_celda is not None
        assert advertencia.valor == texto_celda.strip()

    # El N.º 7 está en la fila 8 del archivo (N.º 1 en la fila 2).
    assert por_numero["7"].ref.fila == 8


@omitir_sin_v4
def test_p_001_39_el_texto_de_cada_advertencia_cita_la_regla_de_instrucciones() -> None:
    """P-001-39 · US-001-2.14, FR-001-10: N.º, columna, valor, regla de Instrucciones, categoría."""
    from egm.textos import advertencia

    corpus = _leer_v4()
    advertencias = _advertencias_de_enfoque(corpus)
    assert len(advertencias) == 2

    for a in advertencias:
        texto = advertencia(a)
        assert f"N.º {a.ref.numero}" in texto
        assert COLUMNA_ENFOQUE in texto
        assert a.valor is not None
        assert a.valor in texto
        # La regla del equipo: empieza por Sí, No o Parcial, como pide la hoja Instrucciones.
        assert "Instrucciones" in texto
        for palabra in ("Sí", "No", "Parcial"):
            assert palabra in texto
        # Qué hace la herramienta con la fila: queda como «Sin clasificar».
        assert "Sin clasificar" in texto
        # Nada corrige el valor ni agrega una instrucción al equipo.
        assert "?" not in texto
