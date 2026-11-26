"""Pruebas de las variantes de `semantica_hoja` de M07 (plan 001, T-001-45).

Cubren ADR-002, punto 3, y el contrato de datos §7.4: la semántica de la hoja `EGM` se lee con
variantes acumulativas, cada una con una particularidad más (texto «1» como marca; valores sin
quitar los espacios en los extremos). Nada lee un archivo: el esquema y los documentos se arman a
mano, y los esperados están calculados a mano a partir de la tabla de abajo, no ejecutando el código
bajo prueba. Escenarios: US-001-3.8 (texto «1») y US-001-3.17 (espacios).

Todos los documentos son estudios empíricos con las dos intervenciones I1 e I2, las dimensiones D1
y D2 y los niveles de impacto y de caso:

| Fila | $I_r$ | $J_r$ | Texto «1» | Nivel | Particularidad |
|---|---|---|---|---|---|
| 2 | I1, I2 | D1 | D2 | impacto | texto «1» en la dimensión D2 |
| 3 | I1 | D1 | | caso | espacios en la intervención principal («I1 ») |
| 4 | I2 | D1 | | impacto | espacios en el tipo de documento |
| 5 | I1 | D2 | | impacto | espacios en el nivel de evidencia |
| 6 | I2 | D2 | | caso | $G_r = H_r$ y espacios en la principal («I2 ») |
"""

from egm.conteo import VarianteHoja, semantica_hoja
from egm.modelo import (
    ESPACIOS_EN_LOS_EXTREMOS,
    Advertencia,
    Anclas,
    Corpus,
    DatosCrudos,
    Documento,
    Enfoque,
    Esquema,
    EstadoDocumento,
    Lista,
    RefFila,
    Rol,
)

I1, I2 = "I1", "I2"
D1, D2 = "D1", "D2"
IMPACTO, CASO = "Evaluación de impacto", "Estudio de caso"
EMPIRICO = "Estudio empírico (evaluación/caso)"

ESQUEMA = Esquema(
    columnas={},
    dimensiones=(D1, D2),
    intervenciones=(I1, I2),
    niveles=(IMPACTO, CASO),
    tipos_documento=Lista((EMPIRICO,), "validacion"),
    tipos_fuente=Lista((), "presentes"),
    metodologias=Lista((), "presentes"),
    anclas=Anclas(empiricos=(EMPIRICO,), evaluacion_impacto=IMPACTO),
    advertencias=(),
    notas=(),
)


def _doc(
    fila: int,
    intervenciones: tuple[str, ...],
    dimensiones: tuple[str, ...],
    nivel: str,
    crudos: DatosCrudos = DatosCrudos(),  # noqa: B008 - inmutable
) -> Documento:
    return Documento(
        ref=RefFila(f"N{fila}", fila),
        anio=None,
        tipo_documento=EMPIRICO,
        tipo_fuente=None,
        metodologia=None,
        intervenciones=intervenciones,
        dimensiones=dimensiones,
        nivel=nivel,
        enfoque=Enfoque.SIN_DILIGENCIAR,
        estado=EstadoDocumento.EN_EL_MAPA,
        textos={},
        crudos=crudos,
    )


def _espacios(fila: int, valor: str) -> Advertencia:
    """La advertencia de lectura que guarda el texto de la celda tal como estaba."""
    return Advertencia(
        ESPACIOS_EN_LOS_EXTREMOS, "fila", RefFila(f"N{fila}", fila), "columna", valor, {}
    )


CORPUS = Corpus(
    documentos=(
        _doc(2, (I1, I2), (D1,), IMPACTO, DatosCrudos(dimensiones_como_texto=(D2,))),
        _doc(3, (I1,), (D1,), CASO, DatosCrudos(con_espacios=(Rol.INTERVENCION_PRINCIPAL,))),
        _doc(4, (I2,), (D1,), IMPACTO, DatosCrudos(con_espacios=(Rol.TIPO_DOCUMENTO,))),
        _doc(5, (I1,), (D2,), IMPACTO, DatosCrudos(con_espacios=(Rol.NIVEL_EVIDENCIA,))),
        _doc(
            6,
            (I2,),
            (D2,),
            CASO,
            DatosCrudos(
                principal_igual_secundaria=True, con_espacios=(Rol.INTERVENCION_PRINCIPAL,)
            ),
        ),
    ),
    advertencias=(
        _espacios(3, "I1 "),
        _espacios(4, EMPIRICO + " "),
        _espacios(5, IMPACTO + " "),
        _espacios(6, "I2 "),
    ),
    fila_final_leida=6,
)
TODAS = range(2, 7)


def test_estandar_cuenta_dos_veces_g_igual_h_y_no_cuenta_el_texto_1() -> None:
    """US-001-3.2, US-001-3.8: la variante estándar es la semántica de la hoja sin más."""
    hoja = semantica_hoja(ESQUEMA, CORPUS, TODAS, VarianteHoja.ESTANDAR)

    assert dict(hoja.t1) == {(I1, D1): 2, (I1, D2): 1, (I2, D1): 2, (I2, D2): 2}
    assert dict(hoja.t) == {I1: 3, I2: 4}
    assert hoja.t2 is not None
    assert dict(hoja.t2) == {(I1, D1): 1, (I1, D2): 1, (I2, D1): 2, (I2, D2): 0}
    assert hoja.t_ie is not None
    assert dict(hoja.t_ie) == {I1: 2, I2: 2}
    assert dict(hoja.t4) == {IMPACTO: 3, CASO: 2}


def test_texto_1_como_marca_suma_la_dimension_escrita_como_texto() -> None:
    """US-001-3.8, ADR-002 punto 3: el texto «1» también marca (como `COUNTIFS(..., 1)`)."""
    hoja = semantica_hoja(ESQUEMA, CORPUS, TODAS, VarianteHoja.TEXTO_1_COMO_MARCA)

    assert dict(hoja.t1) == {(I1, D1): 2, (I1, D2): 2, (I2, D1): 2, (I2, D2): 3}
    assert dict(hoja.t) == {I1: 3, I2: 4}  # «Total estudios» no depende de las dimensiones
    assert hoja.t2 is not None
    assert dict(hoja.t2) == {(I1, D1): 1, (I1, D2): 2, (I2, D1): 2, (I2, D2): 1}
    assert dict(hoja.t4) == {IMPACTO: 3, CASO: 2}


def test_sin_quitar_espacios_deja_fuera_lo_que_la_hoja_no_reconoce() -> None:
    """US-001-3.17, ADR-002 punto 3: acumula el texto «1» y no quita los espacios en los extremos.

    La fila 3 pierde su intervención («I1 »), la 4 deja de ser empírica (tipo con espacios), la 5
    deja de ser de impacto (nivel con espacios) y la 6 cuenta una sola vez en I2 (la secundaria sí
    coincide y la principal no).
    """
    hoja = semantica_hoja(ESQUEMA, CORPUS, TODAS, VarianteHoja.SIN_QUITAR_ESPACIOS)

    assert dict(hoja.t1) == {(I1, D1): 1, (I1, D2): 2, (I2, D1): 1, (I2, D2): 2}
    assert dict(hoja.t) == {I1: 2, I2: 2}
    assert hoja.t2 is not None
    assert dict(hoja.t2) == {(I1, D1): 1, (I1, D2): 1, (I2, D1): 1, (I2, D2): 1}
    assert hoja.t_ie is not None
    assert dict(hoja.t_ie) == {I1: 1, I2: 1}
    assert dict(hoja.t4) == {IMPACTO: 1, CASO: 2}


def test_sin_quitar_espacios_ignora_las_filas_fuera_del_rango() -> None:
    """ADR-002 punto 2: solo cuentan los documentos y las advertencias de las filas pedidas."""
    hoja = semantica_hoja(ESQUEMA, CORPUS, range(6, 7), VarianteHoja.SIN_QUITAR_ESPACIOS)

    assert dict(hoja.t) == {I1: 0, I2: 1}
    assert dict(hoja.t4) == {IMPACTO: 0, CASO: 1}


def test_sin_las_advertencias_de_lectura_los_espacios_de_la_intervencion_no_se_descuentan() -> None:
    """Una intervención con espacios solo se descuenta si la lectura guardó el texto de la celda."""
    sin_avisos = Corpus(CORPUS.documentos, (), CORPUS.fila_final_leida)

    hoja = semantica_hoja(ESQUEMA, sin_avisos, TODAS, VarianteHoja.SIN_QUITAR_ESPACIOS)

    assert dict(hoja.t) == {I1: 3, I2: 3}  # la fila 6 cuenta 2 en I2; la 4 sigue fuera
