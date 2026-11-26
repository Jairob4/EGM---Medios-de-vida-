"""Pruebas complementarias de M08 `egm.verificacion` y de los textos de M10 (plan 001, historia 3).

Completan P-001-44 a P-001-64 con los bordes del contrato §7 que los fixtures de la historia no
alcanzan: la tabla por nivel con otra cantidad de columnas (§7.8), la tabla sin encabezados (§7.7),
un título que se repite o que se escribe en mayúsculas (§7.2), un valor guardado que no es un número
o que no es entero (§7.9, FR-001-17), una celda sin fórmula (ADR-002, punto 2) y la redacción de
cada advertencia y de cada resultado de F-001-3. Los esperados están escritos a mano desde el
contrato, ADR-002 y `docs/interfaz/flujos.md` (F-001-3); ninguno sale de ejecutar el código bajo
prueba. La
matriz base (`MatrizSintetica.base_valida`) trae los N.º 2 (A y B, impacto, dimensiones 1 y 2), 3
(C, caso, dimensiones 3 y 4) y 4 (A, informe, dimensión 1): en la tabla 1, A × Dimensión 1 vale 2,
A × Dimensión 2 y B × Dimensión 1 valen 1, y «Total estudios» de A vale 2.
"""

from typing import Any

import pytest

from egm import textos
from egm.esquema import descubrir
from egm.lectura import leer
from egm.libro import abrir
from egm.modelo import Advertencia, Conteo, RefFila
from egm.verificacion import (
    COMPARACION_INCOMPLETA,
    HOJA_ABARCA_MENOS_FILAS,
    HOJA_EGM_AUSENTE,
    TABLA_DIFIERE,
    TABLA_NO_RECONOCIDA,
    CausaDiferencia,
    Diferencia,
    EstadoTabla,
    ResultadoTabla,
    Verificacion,
    _filas_de_la_formula,
    _numero,
    verificar,
)
from tests.constructor import MatrizSintetica, carpeta_de_fixtures

A, B = "Intervención A", "Intervención B"
D1, D2 = "Dimensión 1", "Dimensión 2"
TOTAL = "Total estudios"
NIVELES = 3  # evaluación de impacto, estudio de caso e informe de proyecto
MAX = 1_048_576
MATRIZ = "'Matriz bibliográfica'"


def _verificar(matriz: MatrizSintetica) -> Verificacion:
    libro = abrir(matriz.a_bytes())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores")
    return verificar(libro, esquema, leer(libro, esquema))


def _tabla(v: Verificacion, tipo: str) -> ResultadoTabla:
    (tabla,) = (t for t in v.tablas if t.tipo == tipo)
    return tabla


def _celdas_de(tabla: ResultadoTabla) -> dict[tuple[str, str], Diferencia]:
    return {d.celda: d for d in tabla.diferencias}


def _advertencias(v: Verificacion, codigo: str) -> list[Advertencia]:
    return [a for a in v.advertencias if a.codigo == codigo]


# --------------------------------------------------------------------------------------------
# Localización y alcance (contrato §7.2, §7.7 y §7.8)
# --------------------------------------------------------------------------------------------


def test_titulo_en_mayusculas_y_con_tildes_se_reconoce() -> None:
    """US-001-3.5, FR-001-15, contrato §7.2: la frase se busca sin distinguir mayúsculas."""
    matriz = MatrizSintetica.base_valida()
    matriz.egm.tabla(1).titulo = "1. NÚMERO TOTAL DE ESTUDIOS por intervención"

    v = _verificar(matriz)

    assert _tabla(v, "total").numero == 1
    assert _tabla(v, "total").estado is EstadoTabla.COINCIDE
    assert v.verificadas == (1, 2, 4)


def test_titulo_que_cumple_dos_tablas_o_se_repite_no_se_reconoce() -> None:
    """US-001-3.6, FR-001-16, contrato §7.2: más de una celda que cumple ⇒ tabla no reconocida.

    El título de la tabla 2 trae también la frase de la tabla 1: dos celdas cumplen la de la tabla
    1, que queda «no verificable» con su advertencia, y la tabla 2 se compara.
    """
    matriz = MatrizSintetica.base_valida()
    matriz.egm.tabla(2).titulo = "2. Evaluación de impacto y número total de estudios"

    v = _verificar(matriz)

    assert _tabla(v, "total").numero is None
    assert _tabla(v, "total").estado is EstadoTabla.NO_VERIFICABLE
    assert _tabla(v, "evaluacion_impacto").estado is EstadoTabla.COINCIDE
    assert v.verificadas == (2, 4)
    (aviso,) = _advertencias(v, TABLA_NO_RECONOCIDA)
    assert aviso.datos["tipo"] == "total"
    assert aviso.datos["titulos"] == 2


def test_tabla_por_nivel_con_dos_columnas_queda_sin_pareja() -> None:
    """FR-001-26, contrato §7.8: con más de una columna de valores, esos valores no se emparejan.

    Cada nivel se debía comparar una vez por cada una de las dos columnas: 3 niveles por 2.
    """
    matriz = MatrizSintetica.base_valida()
    nivel = matriz.egm.tabla(4)
    nivel.duplicar_columna("Estudios")
    nivel.renombrar_columna(1, "Otra columna")

    v = _verificar(matriz)

    tabla = _tabla(v, "nivel")
    assert tabla.estado is EstadoTabla.NO_VERIFICABLE
    assert tabla.diferencias == ()
    assert tabla.sin_pareja == ("Estudios", "Otra columna")
    assert tabla.faltantes == NIVELES * 2
    assert v.verificadas == (1, 2)


def test_tabla_por_nivel_sin_columna_de_valores_no_es_verificable() -> None:
    """FR-001-26, contrato §7.8: sin ninguna columna con encabezado, cada nivel queda sin pareja."""
    matriz = MatrizSintetica.base_valida()
    matriz.egm.tabla(4).quitar_columna("Estudios")

    v = _verificar(matriz)

    tabla = _tabla(v, "nivel")
    assert tabla.estado is EstadoTabla.NO_VERIFICABLE
    assert tabla.sin_pareja == ()
    assert tabla.faltantes == NIVELES
    assert v.verificadas == (1, 2)


def test_tabla_al_final_de_la_hoja_sin_encabezados_ni_filas_no_es_verificable() -> None:
    """FR-001-26, contrato §7.7: sin fila de encabezados debajo del título, nada se compara."""
    matriz = MatrizSintetica.base_valida()
    nivel = matriz.egm.tabla(4)
    nivel.encabezado_nombres = None
    nivel.encabezados.clear()
    nivel.filas.clear()

    v = _verificar(matriz)

    tabla = _tabla(v, "nivel")
    assert tabla.numero == 4
    assert tabla.estado is EstadoTabla.NO_VERIFICABLE
    assert tabla.faltantes == NIVELES
    assert v.verificadas == (1, 2)


def test_total_estudios_con_otras_mayusculas_se_empareja_y_se_nombra_como_esta_en_la_hoja() -> None:
    """FR-001-26, contrato §7.8: «Total estudios» se reconoce sin distinguir mayúsculas.

    Con el valor guardado distinto, la diferencia nombra la columna tal como la escribe la hoja.
    """
    matriz = MatrizSintetica.base_valida()
    tabla = matriz.egm.tabla(1)
    tabla.renombrar_columna(TOTAL, "TOTAL ESTUDIOS")
    tabla.fijar_valor(A, "TOTAL ESTUDIOS", 5)

    v = _verificar(matriz)

    resultado = _tabla(v, "total")
    assert resultado.estado is EstadoTabla.DIFIERE
    assert resultado.sin_pareja == ()
    (d,) = resultado.diferencias
    assert d.celda == (A, "TOTAL ESTUDIOS")
    assert d.valor_hoja == 5
    assert d.conteo.valor == 2
    assert d.explicacion is None
    assert d.filas == ()


def test_nivel_con_espacios_se_explica_en_las_tablas_2_y_4() -> None:
    """US-001-3.17, FR-001-18, ADR-002 punto 3: el nivel del N.º 2 trae un espacio al final.

    La hoja no lo reconoce como «Evaluación de impacto»: en la tabla 4 cuenta 0 donde la herramienta
    cuenta 1, y en la tabla 2 (el N.º 2 es su único estudio) las seis celdas de A y B también.
    """
    matriz = MatrizSintetica.base_valida()
    matriz.fijar_celda(1, "Nivel de evidencia", "Evaluación de impacto ")

    v = _verificar(matriz)

    assert _tabla(v, "total").estado is EstadoTabla.COINCIDE
    nivel = _tabla(v, "nivel")
    assert nivel.estado is EstadoTabla.DIFIERE
    (d,) = nivel.diferencias
    assert (d.celda, d.valor_hoja, d.conteo.valor) == (("Evaluación de impacto", "Estudios"), 0, 1)
    assert d.explicacion is CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS
    assert d.filas == (RefFila("2", 3),)
    impacto = _tabla(v, "evaluacion_impacto")
    assert impacto.estado is EstadoTabla.DIFIERE
    assert set(_celdas_de(impacto)) == {(i, c) for i in (A, B) for c in (D1, D2, TOTAL)}
    assert {d.explicacion for d in impacto.diferencias} == {
        CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS
    }
    assert v.verificadas == (1, 2, 4)


# --------------------------------------------------------------------------------------------
# Valores guardados (contrato §7.9, FR-001-17)
# --------------------------------------------------------------------------------------------


def test_un_texto_guardado_es_un_valor_ausente_y_nunca_cero() -> None:
    """FR-001-17, contrato §7.9: un texto (como un error de la hoja) no se compara ni vale 0."""
    matriz = MatrizSintetica.base_valida()
    matriz.egm.tabla(1).fijar_valor(A, D1, "#N/A")

    v = _verificar(matriz)

    tabla = _tabla(v, "total")
    assert tabla.estado is EstadoTabla.NO_VERIFICABLE
    assert tabla.faltantes == 1
    assert tabla.diferencias == ()
    (aviso,) = _advertencias(v, COMPARACION_INCOMPLETA)
    assert textos.advertencia(aviso) == (
        "Tabla 1 de la hoja «EGM»: no se pudo comparar 1 valor, porque la hoja no trae un número "
        "guardado en esa celda. Un valor que falta no se toma como cero."
    )


def test_un_numero_entero_escrito_con_decimal_se_compara_y_uno_no_entero_difiere() -> None:
    """FR-001-14, contrato §7.9: 1.0 es 1 y coincide; 1.5 difiere, sin causa conocida."""
    matriz = MatrizSintetica.base_valida()
    tabla = matriz.egm.tabla(1)
    tabla.fijar_valor(A, D2, 1.0)
    tabla.fijar_valor(B, D1, 1.5)

    v = _verificar(matriz)

    resultado = _tabla(v, "total")
    assert resultado.estado is EstadoTabla.DIFIERE
    (d,) = resultado.diferencias
    assert d.celda == (B, D1)
    assert d.valor_hoja == 1.5
    assert d.conteo.valor == 1
    assert d.explicacion is None
    assert resultado.faltantes == 0
    assert v.verificadas == (1, 2, 4)


def test_una_celda_sin_formula_se_compara_sobre_todas_las_filas_leidas() -> None:
    """ADR-002 punto 2: un número escrito, sin fórmula, se compara sobre todas las filas leídas."""
    coincide = MatrizSintetica.base_valida()
    coincide.egm.tabla(1).fijar_literal(A, D1, 2)
    difiere = MatrizSintetica.base_valida()
    difiere.egm.tabla(1).fijar_literal(A, D1, 3)

    assert _tabla(_verificar(coincide), "total").estado is EstadoTabla.COINCIDE
    resultado = _tabla(_verificar(difiere), "total")
    assert resultado.estado is EstadoTabla.DIFIERE
    (d,) = resultado.diferencias
    assert (d.celda, d.valor_hoja, d.conteo.valor) == ((A, D1), 3, 2)
    assert d.conteo.filas == (RefFila("2", 3), RefFila("4", 5))


def test_numero_solo_acepta_numeros_finitos() -> None:
    """FR-001-17, contrato §7.9: lógico, texto, vacío y no finito son ausentes; 2.0 es 2."""
    assert _numero(True) is None
    assert _numero("2") is None
    assert _numero(None) is None
    assert _numero(float("inf")) is None
    assert _numero(float("nan")) is None
    assert _numero(2.0) == 2
    assert isinstance(_numero(2.0), int)
    assert _numero(0) == 0
    assert _numero(1.5) == 1.5


# --------------------------------------------------------------------------------------------
# Filas que abarcan las fórmulas (ADR-002, punto 2)
# --------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("formula", "esperado"),
    [
        (f'=COUNTIFS({MATRIZ}!$D$2:$D$200,"x")', (2, 200)),
        (f"=COUNTIFS({MATRIZ}!$D$2:$D$200,$A5,{MATRIZ}!L$2:L$200,1)", (2, 200)),
        (f'=COUNTIFS({MATRIZ}!$D$2:$D$200,"x",{MATRIZ}!$J$3:$J$150)', (3, 150)),  # intersección
        (f'=COUNTIFS({MATRIZ}!$D:$D,"x")', (1, MAX)),  # columna completa
        (f'=COUNTIFS({MATRIZ}!$D$4:$D,"x")', (4, MAX)),  # sin fila final
        (f'=COUNTIFS({MATRIZ}!$D7,"x")', (7, 7)),  # una sola celda
        (
            f"=COUNTIFS('Otra hoja'!$D$2:$D$9,\"x\",{MATRIZ}!$D$2:$D$60)",
            (2, 60),
        ),  # otra hoja no cuenta
        ("=COUNTIFS('Otra hoja'!$D$2:$D$9,\"x\")", (2, 99)),  # no remite a la matriz: todas
        ("=1+1", (2, 99)),
        (None, (2, 99)),
    ],
)
def test_filas_que_abarca_una_formula(formula: str | None, esperado: tuple[int, int]) -> None:
    """ADR-002 punto 2: intersección de los rangos que remiten a la hoja de la matriz.

    Sin fórmula, o con una que no remite a esa hoja, son todas las filas leídas (aquí, hasta la 99).
    """
    assert _filas_de_la_formula(formula, 99) == esperado


# --------------------------------------------------------------------------------------------
# Textos de las advertencias propias de la verificación (F-001-2 y F-001-3, FR-001-12)
# --------------------------------------------------------------------------------------------


def _fixture(nombre: str) -> Verificacion:
    libro = abrir((carpeta_de_fixtures() / f"{nombre}.xlsx").read_bytes())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores")
    return verificar(libro, esquema, leer(libro, esquema))


def test_advertencia_de_hoja_ausente() -> None:
    """US-001-3.4, FR-001-16: el texto dice que falta la hoja y que el mapa se calcula igual."""
    (aviso,) = _fixture("cb29_sin_hoja_egm").advertencias

    assert aviso.codigo == HOJA_EGM_AUSENTE
    assert textos.advertencia(aviso) == (
        "El archivo no trae la hoja «EGM». Los conteos no se pueden contrastar con ella; el mapa "
        "se calcula igual desde la hoja «Matriz bibliográfica»."
    )


def test_advertencia_de_tabla_no_reconocida_nombra_la_frase_y_no_un_numero() -> None:
    """US-001-3.6: la tabla que no se reconoció se nombra por la frase de su título."""
    (aviso,) = _fixture("cb29_titulo_cambiado").advertencias

    assert aviso.codigo == TABLA_NO_RECONOCIDA
    assert textos.advertencia(aviso) == (
        "En la hoja «EGM» no se reconoció una única tabla cuyo título tenga un número y la frase "
        "«Número total de estudios». Esa tabla no se contrasta con los conteos."
    )


def test_advertencia_de_valores_que_faltan_con_y_sin_nombres_sin_pareja() -> None:
    """US-001-3.11, US-001-3.13, contrato §7.9: tabla, nombres sin pareja y cuántos faltaron."""
    sin_numero = list(_fixture("cb33_parcial_sin_diferencia").advertencias)
    con_pareja = list(_fixture("cb31_categoria_nueva").advertencias)

    assert [textos.advertencia(a) for a in sin_numero] == [
        "Tabla 1 de la hoja «EGM»: no se pudieron comparar 36 valores, porque la hoja no trae un "
        "número guardado en esas celdas. Un valor que falta no se toma como cero."
    ]
    assert [textos.advertencia(a) for a in con_pareja] == [
        "Tabla 1 de la hoja «EGM»: no se pudieron comparar 9 valores. Sin pareja: «Intervención "
        "G». Un valor que falta no se toma como cero.",
        "Tabla 2 de la hoja «EGM»: no se pudieron comparar 9 valores. Sin pareja: «Intervención "
        "G». Un valor que falta no se toma como cero.",
    ]


def test_advertencia_de_diferencias_en_singular_y_en_plural() -> None:
    """US-001-3.2, FR-001-18: cuántos valores difieren en la tabla."""
    varios = _fixture("esc_3_2_difiere_g_igual_h")
    uno = Advertencia(TABLA_DIFIERE, "tabla", None, None, None, {"tabla": 4, "celdas": 1})

    assert _advertencias(varios, TABLA_DIFIERE)[0].datos["celdas"] == 2
    assert [textos.advertencia(a) for a in varios.advertencias] == [
        "Tabla 1 de la hoja «EGM»: 2 valores difieren de los conteos de esta herramienta."
    ]
    assert textos.advertencia(uno) == (
        "Tabla 4 de la hoja «EGM»: 1 valor difiere del conteo de esta herramienta."
    )


def test_advertencia_de_que_la_hoja_abarca_menos_filas() -> None:
    """US-001-1.5, CB-12, ADR-002 punto 2: desde y hasta qué fila llegan las fórmulas."""
    avisos = _advertencias(_fixture("cb12_250_documentos"), HOJA_ABARCA_MENOS_FILAS)

    assert [a.datos for a in avisos] == [{"desde": 2, "hasta": 200, "leida": 251}]
    assert textos.advertencia(avisos[0]) == (
        "Las fórmulas de la hoja «EGM» abarcan de la fila 2 a la fila 200 de la hoja «Matriz "
        "bibliográfica», y la herramienta leyó hasta la fila 251. La comparación se hace solo con "
        "las filas que abarca la hoja."
    )


# --------------------------------------------------------------------------------------------
# Textos de F-001-3 (FR-001-18, FR-001-25, NFR-000-03)
# --------------------------------------------------------------------------------------------


def _tabla_texto(
    numero: int | None,
    tipo: Any,
    estado: EstadoTabla,
    diferencias: tuple[Diferencia, ...] = (),
) -> ResultadoTabla:
    return ResultadoTabla(numero, tipo, estado, diferencias, (), 0)


def _dif(fila: str, columna: str, causa: CausaDiferencia | None, *filas: RefFila) -> Diferencia:
    return Diferencia((fila, columna), 2, Conteo(()), causa, tuple(filas))


COINCIDEN_2_Y_4 = (
    _tabla_texto(2, "evaluacion_impacto", EstadoTabla.COINCIDE),
    _tabla_texto(4, "nivel", EstadoTabla.COINCIDE),
)


def test_texto_con_varias_causas_celdas_sin_causa_y_documentos_sin_numero() -> None:
    """FR-001-18, F-001-3: cada causa lista sus filas; las celdas sin causa se dicen aparte."""
    tabla = _tabla_texto(
        1,
        "total",
        EstadoTabla.DIFIERE,
        (
            _dif("A", "D1", CausaDiferencia.PRINCIPAL_IGUAL_SECUNDARIA, RefFila("6", 7)),
            _dif("A", "Total", CausaDiferencia.PRINCIPAL_IGUAL_SECUNDARIA, RefFila("6", 7)),
            _dif("B", "D1", CausaDiferencia.PRINCIPAL_IGUAL_SECUNDARIA, RefFila("9", 10)),
            _dif("C", "D3", CausaDiferencia.DIMENSION_VALOR_INVALIDO, RefFila(None, 12)),
            _dif("D", "D4", CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS, RefFila("2", 3)),
            _dif("E", "D5", None),
        ),
    )
    v = Verificacion((tabla, *COINCIDEN_2_Y_4), (1, 2, 4), ())

    resultado = textos.verificacion(v)

    assert resultado.resultado == "difiere"
    assert resultado.mensaje == (
        "Los conteos difieren de la hoja EGM en la tabla 1: «A» con «D1», «A» con «Total», «B» "
        "con «D1», «C» con «D3», «D» con «D4» y «E» con «D5». "
        "Causa conocida: los documentos N.º 6 y N.º 9 tienen la misma intervención como "
        "principal y como secundaria; la hoja los cuenta dos veces y esta herramienta, una. "
        "Causa conocida: el documento de la fila 12 tiene una dimensión con el número 1 "
        "escrito como texto; la hoja lo cuenta y esta herramienta, no. "
        "Causa conocida: el N.º 2 tiene espacios al comienzo o al final de un valor; la hoja "
        "los toma en cuenta y esta herramienta los ignora. "
        "No se identificó la causa de la diferencia en «E» con «D5». "
        "Tablas verificadas: 1, 2 y 4."
    )


def test_texto_con_varios_documentos_con_espacios_y_dimension_como_texto() -> None:
    """FR-001-18, F-001-3: el plural de las causas de texto «1» y de espacios."""
    tabla = _tabla_texto(
        4,
        "nivel",
        EstadoTabla.DIFIERE,
        (
            _dif("N", "Estudios", CausaDiferencia.DIMENSION_VALOR_INVALIDO, RefFila("3", 4)),
            _dif("M", "Estudios", CausaDiferencia.DIMENSION_VALOR_INVALIDO, RefFila("5", 6)),
            _dif("L", "Estudios", CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS, RefFila("7", 8)),
            _dif("K", "Estudios", CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS, RefFila(None, 9)),
        ),
    )
    v = Verificacion((tabla,), (4,), ())

    assert textos.verificacion(v).mensaje == (
        "Los conteos difieren de la hoja EGM en la tabla 4: «N» con «Estudios», «M» con "
        "«Estudios», «L» con «Estudios» y «K» con «Estudios». "
        "Causa conocida: los documentos N.º 3 y N.º 5 tienen una dimensión con el número 1 "
        "escrito como texto; la hoja los cuenta y esta herramienta, no. "
        "Causa conocida: los documentos N.º 7 y fila 9 tienen espacios al comienzo o al final de "
        "un valor; la hoja los toma en cuenta y esta herramienta los ignora. "
        "Tablas verificadas: 4."
    )


def test_texto_de_una_tabla_con_mas_de_diez_celdas_cuenta_las_que_sobran() -> None:
    """NFR-000-03, F-001-3: el texto nombra diez celdas y cuenta las demás."""
    celdas = tuple(_dif(f"F{k}", "C", None) for k in range(1, 13))
    v = Verificacion((_tabla_texto(1, "total", EstadoTabla.DIFIERE, celdas),), (1,), ())
    nombradas = ", ".join(f"«F{k}» con «C»" for k in range(1, 11))

    assert textos.verificacion(v).mensaje == (
        f"Los conteos difieren de la hoja EGM en la tabla 1: {nombradas} y otras 2 celdas. "
        f"No se identificó la causa de la diferencia en {nombradas} y otras 2 celdas. "
        "Tablas verificadas: 1."
    )


def test_texto_de_coincide_con_tablas_sin_verificar_avisa_que_faltaron() -> None:
    """FR-001-25, FR-001-27: solo se lista lo verificado y se avisa de lo que no se contrastó."""
    tablas = (
        _tabla_texto(1, "total", EstadoTabla.NO_VERIFICABLE),
        *COINCIDEN_2_Y_4,
    )

    resultado = textos.verificacion(Verificacion(tablas, (2, 4), ()))

    assert resultado.resultado == "coincide"
    assert resultado.mensaje == (
        "Los conteos coinciden con la hoja EGM del archivo. Tablas verificadas: 2 y 4. "
        "Una o más tablas no se pudieron contrastar por completo; las advertencias de lectura "
        "dicen por qué."
    )


def test_texto_de_no_verificable_cuando_el_archivo_no_trae_la_hoja() -> None:
    """US-001-3.4, FR-001-16: se dice que falta la hoja, sin lista de tablas."""
    resultado = textos.verificacion(_fixture("cb29_sin_hoja_egm"))

    assert resultado.resultado == "no verificable"
    assert resultado.mensaje == (
        "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo no "
        "trae esa hoja. Los conteos de esta herramienta se calculan directamente de la hoja "
        "«Matriz bibliográfica»."
    )


def test_texto_de_no_verificable_cuando_no_se_reconocio_ninguna_tabla() -> None:
    """US-001-3.6, FR-001-16: ninguna tabla se reconoció en la hoja."""
    aviso = Advertencia(TABLA_NO_RECONOCIDA, "tabla", None, None, None, {"frase": "x"})
    tablas = (
        _tabla_texto(None, "total", EstadoTabla.NO_VERIFICABLE),
        _tabla_texto(None, "evaluacion_impacto", EstadoTabla.NO_VERIFICABLE),
        _tabla_texto(None, "nivel", EstadoTabla.NO_VERIFICABLE),
    )

    resultado = textos.verificacion(Verificacion(tablas, (), (aviso, aviso, aviso)))

    assert resultado.mensaje == (
        "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en esa hoja no "
        "se reconocieron las tablas que se contrastan. Los conteos de esta herramienta se "
        "calculan directamente de la hoja «Matriz bibliográfica»."
    )


def test_texto_de_no_verificable_cuando_faltan_valores_o_categorias() -> None:
    """US-001-3.11, US-001-3.13: hay valores guardados, pero no alcanzan para contrastar."""
    aviso = Advertencia(
        COMPARACION_INCOMPLETA,
        "tabla",
        None,
        None,
        None,
        {"tabla": 1, "comparadas": 5, "faltantes": 4, "sin_pareja": ()},
    )
    tablas = (
        _tabla_texto(1, "total", EstadoTabla.NO_VERIFICABLE),
        _tabla_texto(2, "evaluacion_impacto", EstadoTabla.NO_VERIFICABLE),
        _tabla_texto(4, "nivel", EstadoTabla.NO_VERIFICABLE),
    )

    resultado = textos.verificacion(Verificacion(tablas, (), (aviso,)))

    assert resultado.mensaje == (
        "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en sus tablas "
        "faltan valores o categorías. Los conteos de esta herramienta se calculan directamente de "
        "la hoja «Matriz bibliográfica»."
    )
