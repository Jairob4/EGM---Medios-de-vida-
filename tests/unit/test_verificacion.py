"""Pruebas P-001-44, P-001-45, P-001-47 a P-001-62 y P-001-64 de la historia 3 (plan 001, T-001-41).

M08 `egm.verificacion` (y M10 para P-001-64) contra la hoja EGM de matrices sintéticas. Cada prueba
abre un fixture de `data/fixtures/` (o una variante armada con M23, la matriz sintética de
`tests.constructor`) con `egm.libro.abrir`, descubre el esquema (M04), lee el corpus (M05) y llama a
`egm.verificacion.verificar(libro, esquema, corpus)`. Nunca se abre `data/raw/`.

Los esperados están escritos a mano desde el contrato de datos (§5, §7 y §9), el ADR-002, los
escenarios US-001-3.1 a 3.17 y los textos de F-001-3 (`docs/interfaz/flujos.md`); ninguno sale de
ejecutar el código bajo prueba. Documentos de la base válida (fila del archivo = N.º + 1):

- N.º 2 empírico, A principal y B secundaria, nivel Evaluación de impacto, dimensiones 1 y 2.
- N.º 3 empírico, C, nivel Estudio de caso, dimensiones 3 y 4.
- N.º 4 empírico, A, nivel Informe de proyecto, dimensión 1.
- La hoja EGM trae las tablas 1 (total), 2 (evaluación de impacto), 3 (enfoque, no comparable) y 4
  (nivel); la 1 y la 2 con una columna por dimensión (1 a 8) y «Total estudios»; la 4, «Estudios».
  Las fórmulas abarcan las filas 2 a 200 y cada fórmula trae su valor guardado (el de la hoja).

Interfaz que las pruebas suponen (arquitectura §6.1, M08; ver «NC» al final de este docstring):

- `verificar(libro, esquema, corpus) -> Verificacion` con `tablas`, `verificadas` y `advertencias`.
- `ResultadoTabla`: `numero`, `tipo` (`"total"`, `"evaluacion_impacto"`, `"nivel"`), `estado`
  (`EstadoTabla`: se compara por su nombre `COINCIDE`, `DIFIERE`, `NO_VERIFICABLE`), `diferencias`,
  `sin_pareja` y `faltantes`.
- Diferencia: la arquitectura solo dice «celda, valor de la hoja, conteo, explicación, filas que la
  explican». Las pruebas suponen los atributos `celda` (pareja `(fila, columna)` de nombres),
  `valor_hoja`, `conteo` (entero o `Conteo`), `explicacion` y `filas` (tupla de `RefFila` o
  `Conteo`). La explicación se compara con los códigos de `egm.modelo` de la misma causa en la
  lectura: `PRINCIPAL_IGUAL_SECUNDARIA`, `DIMENSION_VALOR_INVALIDO` (texto «1») y
  `ESPACIOS_EN_LOS_EXTREMOS`. Todo este acceso está en las ayudas `_celda`, `_valor_hoja`,
  `_conteo`, `_causa` y `_filas_de`, para cambiarlo en un solo lugar.
- Las advertencias de verificación no tienen códigos en `egm.modelo`; las pruebas buscan el nombre o
  la cifra dentro de cualquiera de sus campos (`_texto`), sin suponer un código.
- `egm.textos.verificacion(v)` devuelve un `TextoVerificacion` cuyas cadenas se recogen sin suponer
  su forma (`_cadenas`).

NC (abiertos, a Jairo): [NEEDS CLARIFICATION: nombres de los campos de `Diferencia` y tipo de su
explicación] · [NEEDS CLARIFICATION: códigos y datos de las advertencias de verificación] ·
[NEEDS CLARIFICATION: forma de `TextoVerificacion`] · [NEEDS CLARIFICATION: `Verificacion.tablas`
con hoja ausente: ¿tres tablas «no verificable» o ninguna?] · [NEEDS CLARIFICATION: `faltantes` con
un nombre repetido (CB-35) y con «Total estudios» ausente (CB-34)].

Los módulos de la historia 3 se importan dentro de cada prueba: mientras `egm.verificacion` no
exista, falla la prueba y no la recolección.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import cache
from typing import Any, NamedTuple

import pytest

from egm.libro import abrir
from egm.modelo import (
    DIMENSION_VALOR_INVALIDO,
    ESPACIOS_EN_LOS_EXTREMOS,
    PRINCIPAL_IGUAL_SECUNDARIA,
    Conteo,
    RefFila,
)
from tests.constructor import (
    VALOR_EMPIRICO,
    MatrizSintetica,
    carpeta_de_fixtures,
)

# --------------------------------------------------------------------------------------------
# Esperados comunes (escritos a mano)
# --------------------------------------------------------------------------------------------

A, B, C, D, F, G = (f"Intervención {c}" for c in "ABCDFG")
D1, D2, D3, D4, D5 = (f"Dimensión {n}" for n in (1, 2, 3, 4, 5))
TOTAL = "Total estudios"
TIPOS = {"total", "evaluacion_impacto", "nivel"}
NUMERO_DE = {"total": 1, "evaluacion_impacto": 2, "nivel": 4}

PRINCIPAL = "Tipo de intervención (EGM)"
NIVEL = "Nivel de evidencia"


def _n(numero: int) -> RefFila:
    """El documento de la base válida con ese N.º (fila del archivo = N.º + 1)."""
    return RefFila(str(numero), numero + 1)


# --------------------------------------------------------------------------------------------
# Ayudas
# --------------------------------------------------------------------------------------------


class Lectura(NamedTuple):
    libro: Any
    esquema: Any
    corpus: Any
    verificacion: Any


def _bytes(nombre: str) -> bytes:
    return (carpeta_de_fixtures() / f"{nombre}.xlsx").read_bytes()


def _verificar_bytes(contenido: bytes) -> Lectura:
    """Abre, descubre, lee y verifica (M03, M04, M05 y M08)."""
    from egm.esquema import descubrir
    from egm.lectura import leer
    from egm.verificacion import verificar

    libro = abrir(contenido)
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "una matriz válida no debe dar fallo de contrato"
    corpus = leer(libro, esquema)
    return Lectura(libro, esquema, corpus, verificar(libro, esquema, corpus))


@cache
def _de_fixture(nombre: str) -> Lectura:
    return _verificar_bytes(_bytes(nombre))


def _verificar_fixture(nombre: str) -> Any:
    return _de_fixture(nombre).verificacion


def _verificar_matriz(matriz: MatrizSintetica) -> Any:
    return _verificar_bytes(matriz.a_bytes()).verificacion


def _por_tipo(v: Any) -> dict[str, Any]:
    return {t.tipo: t for t in v.tablas}


def _estados(v: Any) -> dict[str, str]:
    """Estado de cada tabla por su tipo, por el nombre del miembro de `EstadoTabla`."""
    return {t.tipo: t.estado.name for t in v.tablas}


def _cadenas(valor: object) -> list[str]:
    """Todas las cadenas que contiene un objeto, sin suponer su forma."""
    if valor is None:
        return []
    if isinstance(valor, str):
        return [valor]
    if isinstance(valor, Enum):
        return [valor.name, *_cadenas(valor.value)]
    if isinstance(valor, Mapping):
        return [s for k, v in valor.items() for s in (*_cadenas(k), *_cadenas(v))]
    if is_dataclass(valor) and not isinstance(valor, type):
        return [s for f in fields(valor) for s in _cadenas(getattr(valor, f.name))]
    if isinstance(valor, Iterable):
        return [s for v in valor for s in _cadenas(v)]
    return [str(valor)]


def _texto(objeto: object) -> str:
    return "\n".join(_cadenas(objeto))


def _menciona(v: Any, texto: str) -> bool:
    """Alguna advertencia de la verificación nombra `texto` en cualquiera de sus campos."""
    return any(texto in _texto(a) for a in v.advertencias)


def _celda(d: Any) -> tuple[str, str]:
    celda = tuple(d.celda)
    assert len(celda) == 2, celda
    return celda[0], celda[1]


def _entero(x: Any) -> int:
    return x.valor if isinstance(x, Conteo) else int(x)


def _valor_hoja(d: Any) -> int:
    return _entero(d.valor_hoja)


def _conteo(d: Any) -> int:
    return _entero(d.conteo)


def _causa(d: Any) -> Any:
    causa = d.explicacion
    return getattr(causa, "value", causa)


def _filas_de(d: Any) -> tuple[RefFila, ...]:
    filas = d.filas
    return tuple(filas.filas) if isinstance(filas, Conteo) else tuple(filas)


def _comparables_sin_diferencias(t: Any) -> None:
    """La tabla coincide: todas las comparaciones, y nada sin pareja ni faltante."""
    assert t.estado.name == "COINCIDE"
    assert t.diferencias == ()
    assert t.sin_pareja == ()
    assert t.faltantes == 0


def _documento_d_sin_dimensiones(numero: int) -> dict[str, Any]:
    """Empírico con intervención D, nivel de caso y las ocho dimensiones en 0."""
    return {
        "N°": numero,
        "Referencia APA": f"Autor {numero} (2020). Documento sintético {numero}.",
        "Año": 2020,
        "Tipo de documento": VALOR_EMPIRICO,
        "Tipo de fuente": "Académica",
        PRINCIPAL: D,
        NIVEL: "Estudio de caso",
        **{f"Dimensión {n}": 0 for n in range(1, 9)},
    }


# --------------------------------------------------------------------------------------------
# P-001-44 · US-001-3.1
# --------------------------------------------------------------------------------------------


def test_p_001_44_las_tres_tablas_coinciden() -> None:
    """P-001-44 · US-001-3.1, FR-001-14: esc_3_1_coincide, las tres tablas «coincide»."""
    v = _verificar_fixture("esc_3_1_coincide")

    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    assert len(v.tablas) == 3
    assert {t.tipo: t.numero for t in v.tablas} == NUMERO_DE
    for t in v.tablas:
        _comparables_sin_diferencias(t)
    assert v.verificadas == (1, 2, 4)
    assert v.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-45 · US-001-3.2
# --------------------------------------------------------------------------------------------


def test_p_001_45_g_igual_h_difiere_y_se_explica_con_la_fila() -> None:
    """P-001-45 · US-001-3.2, FR-001-18, CB-07: esc_3_2, difiere por el N.º 6 (G = H = D).

    El N.º 6 (fila 7) tiene D como principal y secundaria, nivel de caso y la dimensión 5: la hoja
    cuenta 2 donde la herramienta cuenta 1, en (D, Dimensión 5) y en (D, Total estudios). En las
    tablas 2 y 4 no hay diferencia: no es de impacto y el nivel se cuenta una vez por fila.
    """
    v = _verificar_fixture("esc_3_2_difiere_g_igual_h")

    assert _estados(v) == {
        "total": "DIFIERE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    assert v.verificadas == (1, 2, 4)
    diferencias = _por_tipo(v)["total"].diferencias
    assert {_celda(d) for d in diferencias} == {(D, D5), (D, TOTAL)}
    for d in diferencias:
        assert _valor_hoja(d) == 2
        assert _conteo(d) == 1
        assert _causa(d) == PRINCIPAL_IGUAL_SECUNDARIA
        assert _filas_de(d) == (RefFila("6", 7),)
    assert _por_tipo(v)["evaluacion_impacto"].diferencias == ()
    assert _por_tipo(v)["nivel"].diferencias == ()
    assert len(v.advertencias) >= 1  # advierte antes de los resultados (FR-001-18)


# --------------------------------------------------------------------------------------------
# P-001-47 · US-001-3.4
# --------------------------------------------------------------------------------------------


def test_p_001_47_sin_hoja_egm_el_mapa_se_calcula_y_no_es_verificable() -> None:
    """P-001-47 · US-001-3.4, FR-001-16, CB-29: cb29_sin_hoja_egm, ningún `FalloContrato`."""
    import egm.conteo as conteo

    lectura = _de_fixture("cb29_sin_hoja_egm")
    v = lectura.verificacion

    assert not hasattr(v, "errores")  # no es un `FalloContrato`
    assert v.verificadas == ()
    assert all(t.estado.name == "NO_VERIFICABLE" for t in v.tablas)
    assert len(v.advertencias) >= 1
    # El mapa se calcula igual: los tres estudios de la base (N.º 2, 3 y 4) están en el mapa.
    mapa = conteo.mapa(lectura.esquema, lectura.corpus)
    assert mapa.total.valor == 3
    assert mapa.celdas[(A, D1)].conteo.filas == (_n(2), _n(4))


# --------------------------------------------------------------------------------------------
# P-001-48 · US-001-3.5
# --------------------------------------------------------------------------------------------


def test_p_001_48_tablas_en_otra_posicion_se_localizan_por_titulo() -> None:
    """P-001-48 · US-001-3.5, FR-001-15: esc_3_5, filas vacías antes de cada tabla; «coincide»."""
    v = _verificar_fixture("esc_3_5_filas_vacias_antes")

    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    assert {t.tipo: t.numero for t in v.tablas} == NUMERO_DE
    for t in v.tablas:
        _comparables_sin_diferencias(t)
    assert v.verificadas == (1, 2, 4)
    assert v.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-49 · US-001-3.6
# --------------------------------------------------------------------------------------------


def test_p_001_49_tabla_con_titulo_cambiado_no_es_verificable_y_las_otras_se_comparan() -> None:
    """P-001-49 · US-001-3.6, FR-001-16, CB-29: cb29_titulo_cambiado (título de la tabla 1)."""
    v = _verificar_fixture("cb29_titulo_cambiado")

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    assert _por_tipo(v)["total"].diferencias == ()
    assert v.verificadas == (2, 4)
    assert len(v.advertencias) >= 1


# --------------------------------------------------------------------------------------------
# P-001-50 · US-001-3.7
# --------------------------------------------------------------------------------------------


def test_p_001_50_solo_las_tablas_1_2_y_4_y_ninguna_advertencia_por_la_3() -> None:
    """P-001-50 · US-001-3.7, FR-001-25: esc_3_7, la tabla 3 trae valores (7) y no se lee."""
    v = _verificar_fixture("esc_3_7_titulos_1_2_4")

    assert v.verificadas == (1, 2, 4)
    assert sorted(t.numero for t in v.tablas) == [1, 2, 4]
    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    assert v.advertencias == ()  # ADR-002, punto 6: nada sobre la tabla 3


def test_p_001_50_una_tabla_3_con_nombres_repetidos_no_genera_advertencias() -> None:
    """P-001-50 · FR-001-25, ADR-002 punto 6: la tabla 3 con una fila repetida y valores
    equivocados se ignora; las tablas 1, 2 y 4 siguen en «coincide»."""
    matriz = MatrizSintetica.base_valida()
    tabla3 = matriz.egm.tabla(3)
    tabla3.duplicar_fila(A)
    tabla3.duplicar_columna("No")
    for fila in tabla3.filas:
        for columna in range(len(tabla3.encabezados)):
            tabla3.fijar_valor(fila.nombre, columna, 99)
    matriz.egm.tabla(4).mover(fila=matriz.egm.tabla(4).fila + 1)  # sigue el espacio entre tablas

    v = _verificar_matriz(matriz)

    assert v.verificadas == (1, 2, 4)
    assert sorted(t.numero for t in v.tablas) == [1, 2, 4]
    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    assert v.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-51 · US-001-3.8
# --------------------------------------------------------------------------------------------


def test_p_001_51_dimension_escrita_como_texto_se_explica_con_la_fila() -> None:
    """P-001-51 · US-001-3.8, FR-001-18, CB-41: cb41_texto_1.

    El N.º 3 (fila 4) trae el texto «1» en la dimensión 3: la hoja lo cuenta y la herramienta no
    (solo el 1 numérico marca). Diferencia en (C, Dimensión 3): hoja 1, herramienta 0.
    """
    v = _verificar_fixture("cb41_texto_1")

    assert _estados(v) == {
        "total": "DIFIERE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    diferencias = _por_tipo(v)["total"].diferencias
    assert [_celda(d) for d in diferencias] == [(C, D3)]
    (d,) = diferencias
    assert _valor_hoja(d) == 1
    assert _conteo(d) == 0
    assert _causa(d) == DIMENSION_VALOR_INVALIDO
    assert _filas_de(d) == (RefFila("3", 4),)
    assert v.verificadas == (1, 2, 4)
    assert len(v.advertencias) >= 1


# --------------------------------------------------------------------------------------------
# P-001-52 · US-001-3.9
# --------------------------------------------------------------------------------------------


def test_p_001_52_nombres_repetidos_entre_tablas_se_comparan_dentro_de_cada_una() -> None:
    """P-001-52 · US-001-3.9, FR-001-15, FR-001-26: esc_3_9, dos intervenciones llevan el nombre
    de dos niveles; las tres tablas «coincide»."""
    v = _verificar_fixture("esc_3_9_nombres_repetidos_entre_tablas")

    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    for t in v.tablas:
        _comparables_sin_diferencias(t)
    assert v.verificadas == (1, 2, 4)
    assert v.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-53 · US-001-3.10
# --------------------------------------------------------------------------------------------


def test_p_001_53_total_estudios_entre_dimensiones_se_compara_con_u() -> None:
    """P-001-53 · US-001-3.10, FR-001-26, CB-03: esc_3_10, «Total estudios» entre las dimensiones
    4 y 5 y un estudio de D sin dimensiones: «coincide»."""
    v = _verificar_fixture("esc_3_10_total_entre_dimensiones")

    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    for t in v.tablas:
        _comparables_sin_diferencias(t)
    assert v.verificadas == (1, 2, 4)


def test_p_001_53_un_cero_guardado_en_total_estudios_se_compara_y_no_es_ausente() -> None:
    """P-001-53 · FR-001-26, FR-001-17: el estudio de D sin dimensiones suma 1 en «Total estudios».

    Si la hoja guarda 0 allí, esa celda difiere (un 0 guardado se compara, no se toma por ausente).
    """
    matriz = MatrizSintetica.base_valida().agregar_fila(_documento_d_sin_dimensiones(6))
    matriz.egm.tabla(1).fijar_valor(D, TOTAL, 0)

    v = _verificar_matriz(matriz)

    assert _estados(v) == {
        "total": "DIFIERE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    (d,) = _por_tipo(v)["total"].diferencias
    assert _celda(d) == (D, TOTAL)
    assert _valor_hoja(d) == 0
    assert _conteo(d) == 1
    assert _causa(d) not in {
        PRINCIPAL_IGUAL_SECUNDARIA,
        DIMENSION_VALOR_INVALIDO,
        ESPACIOS_EN_LOS_EXTREMOS,
    }


# --------------------------------------------------------------------------------------------
# P-001-54 · US-001-3.11
# --------------------------------------------------------------------------------------------


def test_p_001_54_categoria_nueva_que_la_hoja_no_tiene() -> None:
    """P-001-54 · US-001-3.11, FR-001-27, NFR-000-06, CB-31, CB-36: cb31_categoria_nueva.

    «Intervención G» está en las listas y en el N.º 6, y no tiene fila en las tablas 1 y 2: esas
    quedan «no verificable». La hoja guarda además A a F, correctos. La tabla 4 coincide: el N.º 6
    es de nivel de caso y la hoja lo cuenta. Comparaciones que faltan en cada tabla: la fila G por
    sus 8 dimensiones y «Total estudios» = 9 (contrato §7.9).
    """
    import egm.conteo as conteo

    lectura = _de_fixture("cb31_categoria_nueva")
    v = lectura.verificacion

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "NO_VERIFICABLE",
        "nivel": "COINCIDE",
    }
    for tipo in ("total", "evaluacion_impacto"):
        tabla = _por_tipo(v)[tipo]
        assert tabla.diferencias == ()
        assert G in tabla.sin_pareja
        assert tabla.faltantes == 9
    assert v.verificadas == (4,)
    assert _menciona(v, G)
    # El mapa sí muestra la categoría nueva: el N.º 6 (fila 7) está en (G, Dimensión 5).
    mapa = conteo.mapa(lectura.esquema, lectura.corpus)
    assert mapa.celdas[(G, D5)].conteo.filas == (RefFila("6", 7),)


# --------------------------------------------------------------------------------------------
# P-001-55 · US-001-3.12
# --------------------------------------------------------------------------------------------


def test_p_001_55_categoria_que_sigue_en_la_hoja() -> None:
    """P-001-55 · US-001-3.12, FR-001-27, NFR-000-06, CB-32, CB-40: cb32_categoria_solo_en_hoja.

    «Intervención F» ya no está en las listas y la hoja conserva su fila: en las tablas 1 y 2 esa
    fila queda sin pareja (9 comparaciones que faltan) y la advertencia la nombra.
    """
    v = _verificar_fixture("cb32_categoria_solo_en_hoja")

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "NO_VERIFICABLE",
        "nivel": "COINCIDE",
    }
    for tipo in ("total", "evaluacion_impacto"):
        tabla = _por_tipo(v)[tipo]
        assert tabla.diferencias == ()
        assert F in tabla.sin_pareja
        assert tabla.faltantes == 9
    assert v.verificadas == (4,)
    assert _menciona(v, F)


# --------------------------------------------------------------------------------------------
# P-001-56 y P-001-57 · US-001-3.13 y US-001-3.14
# --------------------------------------------------------------------------------------------


def test_p_001_56_valores_parciales_sin_diferencias_no_es_verificable() -> None:
    """P-001-56 · US-001-3.13, FR-001-17, FR-001-27, CB-33: cb33_parcial_sin_diferencia.

    La tabla 1 solo guarda valores en las filas A y B (2 de 6 filas × 9 columnas = 18 de 54):
    faltan 36, que nunca se toman por 0.
    """
    v = _verificar_fixture("cb33_parcial_sin_diferencia")

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    tabla = _por_tipo(v)["total"]
    assert tabla.diferencias == ()
    assert tabla.faltantes == 36
    assert v.verificadas == (2, 4)
    assert _menciona(v, "36")


def test_p_001_57_valores_parciales_con_una_diferencia_difiere() -> None:
    """P-001-57 · US-001-3.14, FR-001-27, CB-33: cb33_parcial_con_diferencia.

    Igual que la anterior, pero la hoja guarda 5 en (A, Dimensión 1), donde hay 2 estudios (N.º 2
    y 4). Difiere en ese valor, advierte los 36 que no se compararon y no hay causa conocida.
    """
    v = _verificar_fixture("cb33_parcial_con_diferencia")

    assert _estados(v) == {
        "total": "DIFIERE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    tabla = _por_tipo(v)["total"]
    (d,) = tabla.diferencias
    assert _celda(d) == (A, D1)
    assert _valor_hoja(d) == 5
    assert _conteo(d) == 2
    assert _causa(d) not in {
        PRINCIPAL_IGUAL_SECUNDARIA,
        DIMENSION_VALOR_INVALIDO,
        ESPACIOS_EN_LOS_EXTREMOS,
    }
    assert tabla.faltantes == 36
    assert v.verificadas == (1, 2, 4)
    assert _menciona(v, "36")


# --------------------------------------------------------------------------------------------
# P-001-58 y P-001-59 · US-001-3.15 y US-001-3.16
# --------------------------------------------------------------------------------------------


def test_p_001_58_nombre_repetido_dentro_de_una_tabla_no_es_verificable() -> None:
    """P-001-58 · US-001-3.15, FR-001-26, CB-35: cb35_nombre_repetido (fila D dos veces)."""
    v = _verificar_fixture("cb35_nombre_repetido")

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    tabla = _por_tipo(v)["total"]
    assert tabla.diferencias == ()
    assert D in tabla.sin_pareja
    assert v.verificadas == (2, 4)
    assert _menciona(v, D)


@pytest.mark.parametrize("nombre", ["cb34_sin_total", "cb34_total_repetido"])
def test_p_001_59_total_estudios_ausente_o_repetido_no_es_verificable(nombre: str) -> None:
    """P-001-59 · US-001-3.16, FR-001-26, CB-34: la columna «Total estudios» falta o se repite en
    la tabla 1; las demás columnas, correctas, no producen diferencias."""
    v = _verificar_fixture(nombre)

    assert _estados(v) == {
        "total": "NO_VERIFICABLE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    tabla = _por_tipo(v)["total"]
    assert tabla.diferencias == ()
    assert TOTAL in tabla.sin_pareja
    assert v.verificadas == (2, 4)
    assert _menciona(v, TOTAL)


# --------------------------------------------------------------------------------------------
# P-001-60 · US-001-3.17
# --------------------------------------------------------------------------------------------


def test_p_001_60_espacios_en_los_extremos_se_explican_con_la_fila() -> None:
    """P-001-60 · US-001-3.17, FR-001-18: esc_3_17, «Intervención A » en el N.º 2 (fila 3).

    La hoja no cuenta ese estudio como de A (el nombre no es exacto) y la herramienta sí lo hace,
    porque quita los espacios en los extremos. Difiere en A × Dimensión 1 (hoja 1, herramienta 2),
    A × Dimensión 2 (0 y 1) y A × Total estudios (1 y 2) de la tabla 1; y, en la tabla 2, donde el
    N.º 2 es la única evaluación de impacto, en las mismas tres celdas (0 y 1).
    """
    v = _verificar_fixture("esc_3_17_espacios")

    assert _estados(v) == {"total": "DIFIERE", "evaluacion_impacto": "DIFIERE", "nivel": "COINCIDE"}
    esperados = {
        "total": {(A, D1): (1, 2), (A, D2): (0, 1), (A, TOTAL): (1, 2)},
        "evaluacion_impacto": {(A, D1): (0, 1), (A, D2): (0, 1), (A, TOTAL): (0, 1)},
    }
    for tipo, celdas in esperados.items():
        diferencias = _por_tipo(v)[tipo].diferencias
        assert {_celda(d): (_valor_hoja(d), _conteo(d)) for d in diferencias} == celdas, tipo
        for d in diferencias:
            assert _causa(d) == ESPACIOS_EN_LOS_EXTREMOS
            assert _filas_de(d) == (RefFila("2", 3),)
    assert v.verificadas == (1, 2, 4)
    assert len(v.advertencias) >= 1


# --------------------------------------------------------------------------------------------
# P-001-61 · US-001-1.5 (advertencia)
# --------------------------------------------------------------------------------------------


def test_p_001_61_hoja_que_abarca_menos_filas_advierte_y_compara_solo_ese_rango() -> None:
    """P-001-61 · US-001-1.5, CB-12, ADR-002 punto 2: cb12_250_documentos.

    Hay 250 documentos (filas 2 a 251, el N.º k + 1 se repite en ciclo de 5) y las fórmulas llegan
    a la fila 200. En las filas 2 a 200 los N.º 2 y 4 (A × Dimensión 1) aparecen 40 veces cada uno:
    80; en todas, 50 cada uno: 100. La hoja guarda 80, así que solo coincide si M08 compara sobre
    las filas 2 a 200.
    """
    from egm.conteo import VarianteHoja, semantica_hoja

    lectura = _de_fixture("cb12_250_documentos")
    v = lectura.verificacion

    # Premisa del fixture, con el conteo de la hoja sobre cada rango (M07, ya probado).
    en_200 = semantica_hoja(lectura.esquema, lectura.corpus, range(2, 201), VarianteHoja.ESTANDAR)
    en_251 = semantica_hoja(lectura.esquema, lectura.corpus, range(2, 252), VarianteHoja.ESTANDAR)
    assert en_200.t1[(A, D1)] == 80
    assert en_251.t1[(A, D1)] == 100

    assert _estados(v) == dict.fromkeys(TIPOS, "COINCIDE")
    assert v.verificadas == (1, 2, 4)
    assert len(v.advertencias) >= 1  # la hoja abarca menos filas que las leídas


# --------------------------------------------------------------------------------------------
# P-001-62 · US-001-2.10 (tabla)
# --------------------------------------------------------------------------------------------


def test_p_001_62_sin_ancla_de_evaluacion_de_impacto_la_tabla_2_no_es_verificable() -> None:
    """P-001-62 · US-001-2.10, FR-001-23, CB-21: cb21_sin_ancla_ie.

    La lista de nivel no trae «Evaluación de impacto». La tabla 2 queda «no verificable» sin
    comparar nada (contrato §7.9, último párrafo); las tablas 1 y 4 se comparan y coinciden.
    """
    v = _verificar_fixture("cb21_sin_ancla_ie")

    assert _estados(v) == {
        "total": "COINCIDE",
        "evaluacion_impacto": "NO_VERIFICABLE",
        "nivel": "COINCIDE",
    }
    assert _por_tipo(v)["evaluacion_impacto"].diferencias == ()
    assert v.verificadas == (1, 4)


# --------------------------------------------------------------------------------------------
# P-001-64 · FR-001-25, FR-001-18, NFR-000-03 (textos de F-001-3)
# --------------------------------------------------------------------------------------------

TUTEO = re.compile(
    r"\b(t[uú]|tus?|ti|contigo|tienes|puedes|eres|quieres|elige|sube|carga|selecciona|"
    r"intenta|revisa|verifica|vuelve|abre|haz|usa)\b",
    re.IGNORECASE,
)
FORMULAS = re.compile(r"[=$\\^_{}<>∑≤≥±×÷]|\b\d+\s*/\s*\d+\b")


def _texto_de_verificacion(nombre: str) -> str:
    from egm import textos

    return _texto(textos.verificacion(_verificar_fixture(nombre)))


def _revisar_estilo(texto: str) -> None:
    """NFR-000-03: sin preguntas, sin tuteo, sin fórmulas y sin nombrar otra tabla de la hoja."""
    assert texto.strip()
    assert "?" not in texto
    assert "¿" not in texto
    assert TUTEO.search(texto) is None, texto
    assert FORMULAS.search(texto) is None, texto
    minusculas = texto.lower()
    for prohibida in ("tabla no comparable", "tabla 3", "error de contrato", "traceback"):
        assert prohibida not in minusculas, prohibida
    # Toda tabla nombrada es una de las comparables: 1, 2 o 4.
    for numero in re.findall(r"\btabla\s+(\d+)", minusculas):
        assert numero in {"1", "2", "4"}, texto
    for lista in re.findall(r"tablas verificadas:\s*([^.]*)\.", minusculas):
        assert set(re.findall(r"\d+", lista)) <= {"1", "2", "4"}, texto


def test_p_001_64_texto_de_coincide_lista_las_tablas_1_2_y_4() -> None:
    """P-001-64 · FR-001-25, NFR-000-03: esc_3_1_coincide, texto de «Coincide» de F-001-3."""
    texto = _texto_de_verificacion("esc_3_1_coincide")

    assert (
        "Los conteos coinciden con la hoja EGM del archivo. Tablas verificadas: 1, 2 y 4." in texto
    )
    _revisar_estilo(texto)


def test_p_001_64_texto_de_difiere_dice_la_tabla_las_celdas_y_la_causa() -> None:
    """P-001-64 · FR-001-18, NFR-000-03: esc_3_2_difiere_g_igual_h, texto de «Difiere» de F-001-3.

    Tabla 1; celdas (Intervención D con Dimensión 5, e Intervención D con Total estudios); causa:
    el N.º 6 tiene la misma intervención como principal y como secundaria.
    """
    texto = _texto_de_verificacion("esc_3_2_difiere_g_igual_h")

    assert "Los conteos difieren de la hoja EGM en la tabla 1" in texto
    assert D in texto
    assert D5 in texto
    assert (
        "Causa conocida: el N.º 6 tiene la misma intervención como principal y como secundaria; "
        "la hoja lo cuenta dos veces y esta herramienta, una."
    ) in texto
    _revisar_estilo(texto)


def test_p_001_64_texto_de_no_verificable_no_trae_lista_de_tablas() -> None:
    """P-001-64 · FR-001-25, NFR-000-03: cb30_sin_valores_guardados, texto «No verificable»."""
    texto = _texto_de_verificacion("cb30_sin_valores_guardados")

    assert (
        "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo no "
        "trae guardados los resultados de esa hoja. Los conteos de esta herramienta se calculan "
        "directamente de la hoja «Matriz bibliográfica»."
    ) in texto
    assert "tablas verificadas" not in texto.lower()
    _revisar_estilo(texto)
