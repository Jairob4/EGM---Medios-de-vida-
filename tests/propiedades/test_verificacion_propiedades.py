"""Propiedades de la verificación contra la hoja EGM (P-001-63, T-001-42).

SC-001-03, FR-001-14 y, como complemento, FR-001-17. Con las estrategias de M23
(`tests.constructor.matrices_validas`, con hoja EGM y sin estudios con $G_r = H_r$) se arma una
matriz sintética y un ORÁCULO de esta prueba escribe en la hoja los valores guardados con la
semántica de la hoja (contrato §5: $T_1$, $T_2$, $t$, $t^{IE}$ y $T_4$, sobre las filas que abarcan
sus fórmulas), cuenta directamente sobre lo que escribió la estrategia y no llama al código bajo
prueba. Sin $G_r = H_r$, sin el texto «1» en una dimensión y sin espacios en los extremos de un
valor de categoría, la herramienta y la hoja cuentan lo mismo: las tres tablas deben dar «coincide».

Además se comprueban los invariantes del contrato §5 sobre el mismo conjunto de filas, las que
abarcan las fórmulas (nunca mezclado con todas las leídas), y que cuando las fórmulas llegan a menos
filas que las leídas aparece la advertencia y la comparación sigue siendo sobre ese rango.

Complemento (ADR-002, «Requisitos afectados», FR-001-17): si se quitan valores guardados, la tabla
afectada nunca queda en «coincide» ni toma el ausente por 0, y `faltantes` es justo lo quitado.

Los módulos de la historia 3 se importan dentro de la prueba: mientras `egm.verificacion` no exista,
falla la prueba y no la recolección.
"""

from dataclasses import dataclass
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from egm.libro import abrir
from tests.constructor import VALOR_IMPACTO, MatrizSintetica, matrices_validas

ENCABEZADO_TIPO = "Tipo de documento"
ENCABEZADO_PRINCIPAL = "Tipo de intervención (EGM)"
ENCABEZADO_SECUNDARIA = "Intervención secundaria (opcional)"
ENCABEZADO_NIVEL = "Nivel de evidencia"
TOTAL = "Total estudios"
ENCABEZADO_NIVELES = "Estudios"
PRIMERA_FILA_DE_DATOS = 2  # la fila 1 del archivo es el encabezado
PREFIJO_EMPIRICO = "Estudio empírico"

type Clave = tuple[str, str]


@dataclass(frozen=True)
class Oraculo:
    """Valores de la hoja EGM sobre las filas `2..hasta`, con la semántica de la hoja."""

    intervenciones: tuple[str, ...]
    dimensiones: tuple[str, ...]
    niveles: tuple[str, ...]
    t1: dict[Clave, int]
    t2: dict[Clave, int]
    t: dict[str, int]
    t_ie: dict[str, int]
    t4: dict[str, int]
    estudios: int
    """$|E|$ sobre esas filas."""
    ultima_fila_con_datos: int
    """Última fila no vacía del archivo (1 si no hay documentos)."""


def _sin_no_aplica(valores: list[str] | None) -> tuple[str, ...]:
    return tuple(v for v in (valores or []) if not v.startswith("No aplica"))


def _oraculo(matriz: MatrizSintetica, hasta: int) -> Oraculo:
    """La semántica de la hoja (suma de dos `COUNTIFS`) sobre las filas 2 a `hasta`."""
    intervenciones = _sin_no_aplica(matriz.valores_de_lista(ENCABEZADO_PRINCIPAL))
    niveles = _sin_no_aplica(matriz.valores_de_lista(ENCABEZADO_NIVEL))
    dimensiones = tuple(matriz.dimensiones())
    t1 = {(i, j): 0 for i in intervenciones for j in dimensiones}
    t2 = dict(t1)
    t = dict.fromkeys(intervenciones, 0)
    t_ie = dict(t)
    t4 = dict.fromkeys(niveles, 0)
    estudios = 0
    ultima = 1
    for posicion, documento in enumerate(matriz.documentos()):
        fila = PRIMERA_FILA_DE_DATOS + posicion
        if documento:
            ultima = fila
        if fila > hasta or not documento:
            continue
        if not str(documento.get(ENCABEZADO_TIPO, "")).startswith(PREFIJO_EMPIRICO):
            continue
        estudios += 1
        nivel = documento.get(ENCABEZADO_NIVEL)
        es_ie = nivel == VALOR_IMPACTO
        if nivel in t4:
            t4[nivel] += 1
        for categoria in (
            documento.get(ENCABEZADO_PRINCIPAL),
            documento.get(ENCABEZADO_SECUNDARIA),
        ):
            if categoria not in t:
                continue
            t[categoria] += 1
            t_ie[categoria] += int(es_ie)
            for j in dimensiones:
                if documento.get(j) == 1:
                    t1[(categoria, j)] += 1
                    t2[(categoria, j)] += int(es_ie)
    return Oraculo(intervenciones, dimensiones, niveles, t1, t2, t, t_ie, t4, estudios, ultima)


def _escribir_valores(matriz: MatrizSintetica, o: Oraculo) -> None:
    """Deja en cada celda con fórmula de las tablas 1, 2 y 4 el valor guardado del oráculo."""
    for numero, cuerpo, total in ((1, o.t1, o.t), (2, o.t2, o.t_ie)):
        tabla = matriz.egm.tabla(numero)
        for (i, j), valor in cuerpo.items():
            tabla.fijar_valor(i, j, valor)
        for i, valor in total.items():
            tabla.fijar_valor(i, TOTAL, valor)
    for nivel, valor in o.t4.items():
        matriz.egm.tabla(4).fijar_valor(nivel, ENCABEZADO_NIVELES, valor)


def _abrir_y_leer(matriz: MatrizSintetica) -> tuple[Any, Any, Any]:
    from egm.esquema import descubrir
    from egm.lectura import leer

    libro = abrir(matriz.a_bytes())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "una matriz válida no debe dar fallo de contrato"
    return libro, esquema, leer(libro, esquema)


@settings(max_examples=30)
@given(
    matriz=matrices_validas(
        con_egm=True, valores_guardados=True, misma_intervencion=False, max_documentos=40
    ),
    recorte=st.integers(min_value=0, max_value=12),
)
def test_p_001_63_con_valores_de_la_semantica_de_la_hoja_las_tres_tablas_coinciden(
    matriz: MatrizSintetica, recorte: int
) -> None:
    """P-001-63 · SC-001-03, FR-001-14: las tres tablas «coincide» y los invariantes del §5.

    Las fórmulas de la hoja llegan hasta `hasta`, entre la fila 2 y la última de datos: si es
    menor que la última fila con datos, la hoja abarca menos filas que las leídas, aparece una
    advertencia y solo cuentan las filas 2 a `hasta`.
    """
    import egm.conteo as conteo
    from egm.modelo import Corpus
    from egm.verificacion import verificar

    ultima_de_la_matriz = PRIMERA_FILA_DE_DATOS - 1 + len(matriz.documentos())
    hasta = max(PRIMERA_FILA_DE_DATOS, ultima_de_la_matriz - recorte)
    matriz.egm.fila_final_formulas = hasta
    oraculo = _oraculo(matriz, hasta)
    _escribir_valores(matriz, oraculo)

    libro, esquema, corpus = _abrir_y_leer(matriz)
    v = verificar(libro, esquema, corpus)

    # Las tres tablas comparables coinciden: todas las comparaciones, sin parejas que falten.
    assert {t.tipo: t.estado.name for t in v.tablas} == {
        "total": "COINCIDE",
        "evaluacion_impacto": "COINCIDE",
        "nivel": "COINCIDE",
    }
    for tabla in v.tablas:
        assert tabla.diferencias == ()
        assert tabla.sin_pareja == ()
        assert tabla.faltantes == 0
    assert v.verificadas == (1, 2, 4)

    # La advertencia de que la hoja abarca menos filas aparece solo si, de verdad, abarca menos.
    if hasta < oraculo.ultima_fila_con_datos:
        assert len(v.advertencias) >= 1
    else:
        assert v.advertencias == ()

    # Invariantes del §5 sobre las filas que abarcan las fórmulas (nunca una mezcla de conjuntos).
    abarcadas = tuple(d for d in corpus.documentos if d.ref.fila <= hasta)
    restringido = Corpus(
        documentos=abarcadas, advertencias=(), fila_final_leida=min(hasta, corpus.fila_final_leida)
    )
    mapa = conteo.mapa(esquema, restringido)
    ie = conteo.evaluacion_impacto(esquema, restringido)
    t4 = conteo.por_nivel(esquema, restringido)
    hoja = conteo.semantica_hoja(
        esquema, restringido, range(2, hasta + 1), conteo.VarianteHoja.ESTANDAR
    )
    assert ie is not None, "las matrices sintéticas siempre traen el nivel «Evaluación de impacto»"
    for clave, valor in oraculo.t1.items():
        s = mapa.celdas[clave].conteo.valor
        s_ie = ie[clave].valor
        assert s_ie <= s <= valor, clave
        assert oraculo.t2[clave] <= valor, clave
        assert hoja.t1[clave] == valor, clave  # sin G = H, la hoja y la herramienta cuentan igual
        assert s == valor, clave
    assert sum(c.valor for c in t4.values()) <= oraculo.estudios
    assert {nivel: c.valor for nivel, c in t4.items()} == oraculo.t4


@settings(max_examples=30)
@given(
    matriz=matrices_validas(
        con_egm=True, valores_guardados=True, misma_intervencion=False, max_documentos=25
    ),
    elegidas=st.lists(st.integers(min_value=0, max_value=10**6), max_size=6),
)
def test_p_001_63_complemento_un_valor_ausente_nunca_coincide_ni_es_cero(
    matriz: MatrizSintetica, elegidas: list[int]
) -> None:
    """P-001-63 (complemento) · FR-001-17, FR-001-27, ADR-002: valores quitados de la hoja.

    Con el resto correcto, cada tabla a la que se le quitó algún valor queda «no verificable» con
    tantos `faltantes` como valores quitados, aunque la herramienta cuente 0 en esa celda; las
    demás siguen en «coincide».
    """
    from egm.verificacion import verificar

    hasta = matriz.egm.fila_final_formulas
    oraculo = _oraculo(matriz, hasta)
    _escribir_valores(matriz, oraculo)

    celdas: list[tuple[int, str, str]] = [
        (numero, i, columna)
        for numero in (1, 2)
        for i in oraculo.intervenciones
        for columna in (*oraculo.dimensiones, TOTAL)
    ] + [(4, nivel, ENCABEZADO_NIVELES) for nivel in oraculo.niveles]
    quitadas = {celdas[k % len(celdas)] for k in elegidas}
    for numero, fila, columna in quitadas:
        matriz.egm.tabla(numero).fijar_valor(fila, columna, None)

    libro, esquema, corpus = _abrir_y_leer(matriz)
    v = verificar(libro, esquema, corpus)

    por_numero = {t.numero: t for t in v.tablas}
    assert set(por_numero) == {1, 2, 4}
    for numero, tabla in por_numero.items():
        esperadas = sum(1 for q in quitadas if q[0] == numero)
        assert tabla.diferencias == ()
        assert tabla.faltantes == esperadas
        assert tabla.estado.name == ("NO_VERIFICABLE" if esperadas else "COINCIDE")
    assert v.verificadas == tuple(
        sorted(n for n, t in por_numero.items() if t.estado.name == "COINCIDE")
    )
