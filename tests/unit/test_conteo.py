"""Pruebas propias de M07 `egm.conteo` (plan 001, T-001-25): FR-001-07, FR-001-08, FR-001-09,
FR-001-11, FR-001-13 y NFR-000-02.

No leen ningún archivo: el esquema y los documentos se arman a mano, de modo que las pruebas no
dependen de M03, M04 ni M05. Los esperados están escritos a mano a partir del contrato de datos
(§5: $R$, $E$, $M$, $P$, $S$, $S^{IE}$, $T_1$, $T_2$, $T_4$, $t$, $t^{IE}$, $u$, $u^{IE}$) y
ninguno sale de ejecutar el código bajo prueba.

Documentos (la fila del archivo es la que se indica; el N.º es «N» + la fila):

| Fila | Estado | $I_r$ | $J_r$ | Nivel | $G_r = H_r$ |
|---|---|---|---|---|---|
| 2 | En el mapa | I1, I2 | D1, D2 | Evaluación de impacto | no |
| 3 | En el mapa | I1 | D1 | Estudio de caso | sí |
| 4 | Empírico pendiente | I3 | (ninguna) | Evaluación de impacto | no |
| 5 | Empírico pendiente | (ninguna) | D2 | Sin nivel | no |
| 6 | No empírico | I1 | D1 | Evaluación de impacto | no |
| 7 | Sin tipo de documento válido | I2 | D2 | Sin nivel | no |
| 8 | En el mapa | I2 | D1, D3 | Evaluación de impacto | no |
| 9 | En el mapa | I1, I3 | D3 | un nivel fuera de la lista | no |

Las filas 6 y 7 traen intervención y dimensión pero no son estudios empíricos: no cuentan en nada.
"""

from collections.abc import Mapping, Sequence

import pytest

from egm.conteo import (
    ConteosHoja,
    VarianteHoja,
    conjuntos,
    evaluacion_impacto,
    mapa,
    por_intervencion,
    por_nivel,
    semantica_hoja,
)
from egm.modelo import (
    SIN_NIVEL,
    Anclas,
    Conteo,
    Corpus,
    DatosCrudos,
    Documento,
    Enfoque,
    Esquema,
    EstadoDocumento,
    Lista,
    RefFila,
)

I1, I2, I3 = "I1", "I2", "I3"
D1, D2, D3 = "D1", "D2", "D3"
IMPACTO = "Evaluación de impacto"
CASO = "Estudio de caso"
INFORME = "Informe de proyecto"
FUERA_DE_LISTA = "Nivel que no está en la lista"
EMPIRICO = "Estudio empírico (evaluación/caso)"

EN_EL_MAPA = EstadoDocumento.EN_EL_MAPA
PENDIENTE = EstadoDocumento.EMPIRICO_PENDIENTE
NO_EMPIRICO = EstadoDocumento.NO_EMPIRICO
SIN_TIPO = EstadoDocumento.SIN_TIPO_VALIDO


def _ref(fila: int) -> RefFila:
    return RefFila(f"N{fila}", fila)


def _doc(
    fila: int,
    estado: EstadoDocumento,
    intervenciones: Sequence[str],
    dimensiones: Sequence[str],
    nivel: str,
    *,
    igual: bool = False,
) -> Documento:
    return Documento(
        ref=_ref(fila),
        anio=None,
        tipo_documento=EMPIRICO if estado in (EN_EL_MAPA, PENDIENTE) else None,
        tipo_fuente=None,
        metodologia=None,
        intervenciones=tuple(intervenciones),
        dimensiones=tuple(dimensiones),
        nivel=nivel,
        enfoque=Enfoque.SIN_DILIGENCIAR,
        estado=estado,
        textos={},
        crudos=DatosCrudos(principal_igual_secundaria=igual),
    )


def _esquema(*, ancla_impacto: str | None = IMPACTO) -> Esquema:
    return Esquema(
        columnas={},
        dimensiones=(D1, D2, D3),
        intervenciones=(I1, I2, I3),
        niveles=(IMPACTO, CASO, INFORME),
        tipos_documento=Lista((EMPIRICO,), "validacion"),
        tipos_fuente=Lista((), "presentes"),
        metodologias=Lista((), "presentes"),
        anclas=Anclas(empiricos=(EMPIRICO,), evaluacion_impacto=ancla_impacto),
        advertencias=(),
        notas=(),
    )


DOCUMENTOS = (
    _doc(2, EN_EL_MAPA, (I1, I2), (D1, D2), IMPACTO),
    _doc(3, EN_EL_MAPA, (I1,), (D1,), CASO, igual=True),
    _doc(4, PENDIENTE, (I3,), (), IMPACTO),
    _doc(5, PENDIENTE, (), (D2,), SIN_NIVEL),
    _doc(6, NO_EMPIRICO, (I1,), (D1,), IMPACTO),
    _doc(7, SIN_TIPO, (I2,), (D2,), SIN_NIVEL),
    _doc(8, EN_EL_MAPA, (I2,), (D1, D3), IMPACTO),
    _doc(9, EN_EL_MAPA, (I1, I3), (D3,), FUERA_DE_LISTA),
)
CORPUS = Corpus(documentos=DOCUMENTOS, advertencias=(), fila_final_leida=9)
ESQUEMA = _esquema()


def _filas(conteo: Conteo) -> tuple[int, ...]:
    return tuple(ref.fila for ref in conteo.filas)


def _filas_por_clave[K](conteos: Mapping[K, Conteo]) -> dict[K, tuple[int, ...]]:
    return {clave: _filas(conteo) for clave, conteo in conteos.items()}


# --------------------------------------------------------------------------------------------
# Esperados escritos a mano
# --------------------------------------------------------------------------------------------

CLAVES = [(i, j) for i in (I1, I2, I3) for j in (D1, D2, D3)]

S_ESPERADO: dict[tuple[str, str], tuple[int, ...]] = {
    (I1, D1): (2, 3),
    (I1, D2): (2,),
    (I1, D3): (9,),
    (I2, D1): (2, 8),
    (I2, D2): (2,),
    (I2, D3): (8,),
    (I3, D1): (),
    (I3, D2): (),
    (I3, D3): (9,),
}
"""$S(i, j)$ y las filas que la producen: los estudios de $M$ con $i \\in I_r$ y $j \\in J_r$."""

S_IE_ESPERADO: dict[tuple[str, str], tuple[int, ...]] = {
    (I1, D1): (2,),
    (I1, D2): (2,),
    (I1, D3): (),
    (I2, D1): (2, 8),
    (I2, D2): (2,),
    (I2, D3): (8,),
    (I3, D1): (),
    (I3, D2): (),
    (I3, D3): (),
}
"""$S^{IE}(i, j)$: solo las filas 2 y 8 (la fila 4 es de impacto pero no marca dimensiones)."""

T1_ESPERADO: dict[tuple[str, str], int] = {
    (I1, D1): 3,  # fila 2 (1) + fila 3 (G = H: 2)
    (I1, D2): 1,
    (I1, D3): 1,
    (I2, D1): 2,
    (I2, D2): 1,
    (I2, D3): 1,
    (I3, D1): 0,
    (I3, D2): 0,
    (I3, D3): 1,
}

T2_ESPERADO: dict[tuple[str, str], int] = {
    (I1, D1): 1,  # solo la fila 2: la fila 3 (G = H) no es de impacto
    (I1, D2): 1,
    (I1, D3): 0,
    (I2, D1): 2,
    (I2, D2): 1,
    (I2, D3): 1,
    (I3, D1): 0,
    (I3, D2): 0,
    (I3, D3): 0,
}

T_ESPERADO = {I1: 4, I2: 2, I3: 2}  # I1: 1 (fila 2) + 2 (fila 3) + 1 (fila 9); I3: filas 4 y 9
T_IE_ESPERADO = {I1: 1, I2: 2, I3: 1}  # I1: fila 2; I2: filas 2 y 8; I3: fila 4


# --------------------------------------------------------------------------------------------
# conjuntos: R, E, M, P (FR-001-07, FR-001-13)
# --------------------------------------------------------------------------------------------


def test_los_conjuntos_r_e_m_p_traen_las_filas_del_contrato() -> None:
    """FR-001-07, FR-001-13: R todas, E las empíricas, M las que entran al mapa, P = E \\ M."""
    resultado = conjuntos(CORPUS)
    assert _filas(resultado.r) == (2, 3, 4, 5, 6, 7, 8, 9)
    assert _filas(resultado.e) == (2, 3, 4, 5, 8, 9)
    assert _filas(resultado.m) == (2, 3, 8, 9)
    assert _filas(resultado.p) == (4, 5)
    assert [c.valor for c in (resultado.r, resultado.e, resultado.m, resultado.p)] == [8, 6, 4, 2]


def test_las_filas_con_intervencion_y_dimension_que_no_son_empiricas_no_entran_en_e() -> None:
    """FR-001-07: las filas 6 (no empírica) y 7 (sin tipo válido) están en R y fuera de E, M y P."""
    resultado = conjuntos(CORPUS)
    for fila in (6, 7):
        assert fila in _filas(resultado.r)
        assert fila not in _filas(resultado.e)
        assert fila not in _filas(resultado.m)
        assert fila not in _filas(resultado.p)


def test_p_es_e_menos_m_y_m_esta_en_e() -> None:
    """FR-001-13: P y M son una partición de E, con las filas en el orden del archivo."""
    resultado = conjuntos(CORPUS)
    e, m, p = set(resultado.e.filas), set(resultado.m.filas), set(resultado.p.filas)
    assert m | p == e
    assert m & p == set()
    assert e <= set(resultado.r.filas)


def test_un_corpus_vacio_da_conjuntos_vacios() -> None:
    """FR-001-07: sin documentos, todos los conjuntos valen 0 (con lista vacía)."""
    resultado = conjuntos(Corpus(documentos=(), advertencias=(), fila_final_leida=1))
    for conteo in (resultado.r, resultado.e, resultado.m, resultado.p):
        assert conteo.filas == ()
        assert conteo.valor == 0


# --------------------------------------------------------------------------------------------
# mapa: S, n y N (FR-001-07, FR-001-08, FR-001-09, FR-001-11)
# --------------------------------------------------------------------------------------------


def test_el_mapa_trae_una_celda_por_intervencion_y_dimension_con_sus_filas() -> None:
    """FR-001-07, FR-001-11: 3 × 3 celdas, también las de 0, cada una con sus filas."""
    resultado = mapa(ESQUEMA, CORPUS)
    assert resultado.intervenciones == (I1, I2, I3)
    assert resultado.dimensiones == (D1, D2, D3)
    assert list(resultado.celdas) == CLAVES  # intervención por intervención, orden del archivo
    assert _filas_por_clave({k: c.conteo for k, c in resultado.celdas.items()}) == S_ESPERADO


def test_n_y_total_son_estudios_distintos_y_no_la_suma_de_celdas() -> None:
    """FR-001-08, FR-001-09: 4 estudios (filas 2, 3, 8 y 9) en 9 celdas con estudio."""
    resultado = mapa(ESQUEMA, CORPUS)
    suma_de_celdas = sum(c.conteo.valor for c in resultado.celdas.values())
    assert _filas(resultado.estudios) == (2, 3, 8, 9)
    assert _filas(resultado.total) == (2, 3, 8, 9)
    assert resultado.estudios.valor == resultado.total.valor == 4
    assert suma_de_celdas == 9  # 2 + 1 + 1 + 2 + 1 + 1 + 1
    assert suma_de_celdas != resultado.total.valor


def test_la_suma_de_celdas_es_la_suma_de_ir_por_jr() -> None:
    """FR-001-09 (contrato §5): Σ S(i, j) = Σ_{r en M} |I_r||J_r| = 4 + 1 + 2 + 2, y es ≥ N."""
    resultado = mapa(ESQUEMA, CORPUS)
    suma_de_celdas = sum(c.conteo.valor for c in resultado.celdas.values())
    esperado = 2 * 2 + 1 * 1 + 1 * 2 + 2 * 1  # filas 2, 3, 8 y 9
    assert suma_de_celdas == esperado == 9
    assert suma_de_celdas >= resultado.total.valor


def test_los_pendientes_y_los_no_empiricos_no_aparecen_en_ninguna_celda() -> None:
    """FR-001-07: las filas 4 y 5 (P) y 6 y 7 (no empíricas) no están en ninguna celda."""
    resultado = mapa(ESQUEMA, CORPUS)
    en_celdas = {ref.fila for c in resultado.celdas.values() for ref in c.conteo.filas}
    assert en_celdas == {2, 3, 8, 9}


def test_el_mapa_sin_estudios_tiene_todas_las_celdas_en_cero() -> None:
    """FR-001-07: una celda en 0 es «ningún estudio registrado»; n y N valen 0 con lista vacía."""
    resultado = mapa(ESQUEMA, Corpus(documentos=(), advertencias=(), fila_final_leida=1))
    assert list(resultado.celdas) == CLAVES
    assert all(c.conteo.filas == () for c in resultado.celdas.values())
    assert resultado.estudios.valor == resultado.total.valor == 0


def test_el_mapa_es_de_solo_lectura() -> None:
    """NFR-000-02: las celdas del mapa no se pueden alterar desde afuera."""
    resultado = mapa(ESQUEMA, CORPUS)
    with pytest.raises(TypeError):
        resultado.celdas[(I1, D1)] = resultado.celdas[(I1, D2)]  # type: ignore[index]


def test_una_categoria_fuera_del_esquema_no_entra_al_mapa() -> None:
    """Contrato §5: $I_r$ es la intersección con $\\mathcal{I}$; lo ajeno al esquema no suma."""
    ajeno = _doc(10, EN_EL_MAPA, ("Otra", I2), ("Otra dimensión", D3), IMPACTO)
    corpus = Corpus((*DOCUMENTOS, ajeno), (), 10)
    resultado = mapa(ESQUEMA, corpus)
    assert set(resultado.celdas) == set(CLAVES)
    assert _filas(resultado.celdas[(I2, D3)].conteo) == (8, 10)
    assert _filas(resultado.total) == (2, 3, 8, 9, 10)  # el estudio cuenta una vez, en N
    assert por_intervencion(ESQUEMA, corpus).keys() == {I1, I2, I3}
    ie = evaluacion_impacto(ESQUEMA, corpus)
    assert ie is not None
    assert _filas(ie[(I2, D3)]) == (8, 10)


# --------------------------------------------------------------------------------------------
# evaluacion_impacto: S^IE (FR-001-07)
# --------------------------------------------------------------------------------------------


def test_s_ie_cuenta_solo_los_estudios_de_nivel_de_impacto() -> None:
    """FR-001-07: S^IE(i, j) con las filas 2 y 8; todas las combinaciones, también las de 0."""
    resultado = evaluacion_impacto(ESQUEMA, CORPUS)
    assert resultado is not None
    assert list(resultado) == CLAVES
    assert _filas_por_clave(resultado) == S_IE_ESPERADO


def test_s_ie_sin_ancla_de_impacto_es_none_y_no_cero() -> None:
    """FR-001-07, contrato §4.1: sin el nivel «Evaluación de impacto», S^IE no se calcula."""
    sin_ancla = _esquema(ancla_impacto=None)
    assert evaluacion_impacto(sin_ancla, CORPUS) is None
    # Lo demás se sigue calculando: el mapa no depende del ancla de impacto.
    assert _filas_por_clave({k: c.conteo for k, c in mapa(sin_ancla, CORPUS).celdas.items()}) == (
        S_ESPERADO
    )


# --------------------------------------------------------------------------------------------
# por_intervencion: u y u^IE (FR-001-07)
# --------------------------------------------------------------------------------------------


def test_u_cuenta_estudios_empiricos_por_intervencion_sin_exigir_dimensiones() -> None:
    """FR-001-07 (contrato §5): u(I3) incluye la fila 4, empírica pendiente y sin dimensiones."""
    resultado = por_intervencion(ESQUEMA, CORPUS)
    assert _filas_por_clave(resultado) == {I1: (2, 3, 9), I2: (2, 8), I3: (4, 9)}


def test_u_ie_cuenta_solo_los_estudios_de_nivel_de_impacto() -> None:
    """FR-001-07: u^IE por intervención: I1 la fila 2; I2 las filas 2 y 8; I3 la fila 4."""
    resultado = por_intervencion(ESQUEMA, CORPUS, solo_ie=True)
    assert _filas_por_clave(resultado) == {I1: (2,), I2: (2, 8), I3: (4,)}


def test_u_trae_una_entrada_por_intervencion_aunque_valga_cero() -> None:
    """FR-001-07: sin estudios, cada intervención del esquema está con 0 y lista vacía."""
    vacio = Corpus(documentos=(), advertencias=(), fila_final_leida=1)
    for solo_ie in (False, True):
        resultado = por_intervencion(ESQUEMA, vacio, solo_ie=solo_ie)
        assert list(resultado) == [I1, I2, I3]
        assert all(c.filas == () for c in resultado.values())


def test_u_ie_sin_ancla_de_impacto_no_se_confunde_con_cero() -> None:
    """FR-001-07, contrato §4.1: sin ancla, u^IE no existe; pedirla es un error, no un 0."""
    with pytest.raises(ValueError, match="evaluación de impacto"):
        por_intervencion(_esquema(ancla_impacto=None), CORPUS, solo_ie=True)
    # u sí se calcula sin ancla.
    sin_ancla = por_intervencion(_esquema(ancla_impacto=None), CORPUS)
    assert _filas(sin_ancla[I1]) == (2, 3, 9)


# --------------------------------------------------------------------------------------------
# por_nivel: T4 (FR-001-07)
# --------------------------------------------------------------------------------------------


def test_t4_cuenta_los_estudios_empiricos_de_cada_nivel_del_esquema() -> None:
    """FR-001-07 (contrato §5): T4 de impacto = filas 2, 4 y 8 (E incluye los pendientes)."""
    resultado = por_nivel(ESQUEMA, CORPUS)
    assert _filas_por_clave(resultado) == {IMPACTO: (2, 4, 8), CASO: (3,), INFORME: ()}
    assert list(resultado) == [IMPACTO, CASO, INFORME]


def test_t4_deja_fuera_sin_nivel_y_niveles_que_no_estan_en_la_lista() -> None:
    """FR-001-07: la fila 5 (sin nivel) y la 9 (nivel fuera de la lista) no suman; Σ T4 ≤ |E|."""
    resultado = por_nivel(ESQUEMA, CORPUS)
    en_niveles = {ref.fila for c in resultado.values() for ref in c.filas}
    assert en_niveles == {2, 3, 4, 8}
    assert sum(c.valor for c in resultado.values()) == 4
    assert sum(c.valor for c in resultado.values()) <= conjuntos(CORPUS).e.valor == 6
    assert SIN_NIVEL not in resultado


def test_t4_no_cuenta_documentos_que_no_son_empiricos() -> None:
    """FR-001-07: la fila 6 (no empírica, nivel de impacto) no está en T4."""
    assert 6 not in {ref.fila for ref in por_nivel(ESQUEMA, CORPUS)[IMPACTO].filas}


# --------------------------------------------------------------------------------------------
# semantica_hoja: T1, T2, t y t^IE (FR-001-14)
# --------------------------------------------------------------------------------------------

TODAS_LAS_FILAS = range(2, 10)


def test_t1_t2_t_y_t_ie_de_la_hoja_con_el_conteo_doble_de_g_igual_h() -> None:
    """FR-001-14 (contrato §5): la fila 3 (G = H) suma 2 en T1, t; la 2 y la 8 son de impacto."""
    resultado = semantica_hoja(ESQUEMA, CORPUS, TODAS_LAS_FILAS, VarianteHoja.ESTANDAR)
    assert isinstance(resultado, ConteosHoja)
    assert dict(resultado.t1) == T1_ESPERADO
    assert resultado.t2 is not None
    assert dict(resultado.t2) == T2_ESPERADO
    assert dict(resultado.t) == T_ESPERADO
    assert resultado.t_ie is not None
    assert dict(resultado.t_ie) == T_IE_ESPERADO


def test_g_igual_h_cuenta_una_vez_en_s_y_dos_en_t1_de_la_hoja() -> None:
    """FR-001-08, FR-001-14: (I1, D1) = S 2 (filas 2 y 3) frente a T1 3, por la fila 3 con G = H."""
    celda = mapa(ESQUEMA, CORPUS).celdas[(I1, D1)].conteo
    hoja = semantica_hoja(ESQUEMA, CORPUS, TODAS_LAS_FILAS, VarianteHoja.ESTANDAR)
    assert celda.valor == 2
    assert hoja.t1[(I1, D1)] == 3
    assert hoja.t[I1] == 4  # y la columna «Total estudios» de la hoja difiere de u(I1) = 3
    assert por_intervencion(ESQUEMA, CORPUS)[I1].valor == 3


def test_la_hoja_solo_cuenta_las_filas_del_rango() -> None:
    """FR-001-14, contrato §7.3: con las filas 2 a 4 solo cuentan los estudios 2, 3 y 4."""
    resultado = semantica_hoja(ESQUEMA, CORPUS, range(2, 5), VarianteHoja.ESTANDAR)
    assert resultado.t2 is not None
    assert resultado.t_ie is not None
    assert dict(resultado.t) == {I1: 3, I2: 1, I3: 1}  # filas 2 (I1, I2), 3 (I1 ×2) y 4 (I3)
    assert dict(resultado.t_ie) == {I1: 1, I2: 1, I3: 1}
    assert resultado.t1[(I1, D1)] == 3
    assert resultado.t1[(I3, D3)] == 0  # la fila 9 queda fuera del rango
    assert resultado.t2[(I2, D1)] == 1  # la fila 8 queda fuera del rango
    assert dict(resultado.t1) == {
        (I1, D1): 3,
        (I1, D2): 1,
        (I1, D3): 0,
        (I2, D1): 1,
        (I2, D2): 1,
        (I2, D3): 0,
        (I3, D1): 0,
        (I3, D2): 0,
        (I3, D3): 0,
    }


def test_un_rango_sin_documentos_da_ceros_en_toda_la_hoja() -> None:
    """FR-001-14: un rango que no abarca ninguna fila deja todo en 0, una entrada por categoría."""
    resultado = semantica_hoja(ESQUEMA, CORPUS, range(100, 120), VarianteHoja.ESTANDAR)
    assert resultado.t2 is not None
    assert resultado.t_ie is not None
    assert dict(resultado.t1) == dict.fromkeys(CLAVES, 0)
    assert dict(resultado.t2) == dict.fromkeys(CLAVES, 0)
    assert dict(resultado.t) == dict.fromkeys((I1, I2, I3), 0)
    assert dict(resultado.t_ie) == dict.fromkeys((I1, I2, I3), 0)


def test_la_hoja_sin_ancla_de_impacto_no_trae_t2_ni_t_ie() -> None:
    """FR-001-14, contrato §4.1: T2 y t^IE son `None` (no 0); T1 y t se calculan igual."""
    resultado = semantica_hoja(
        _esquema(ancla_impacto=None), CORPUS, TODAS_LAS_FILAS, VarianteHoja.ESTANDAR
    )
    assert resultado.t2 is None
    assert resultado.t_ie is None
    assert dict(resultado.t1) == T1_ESPERADO
    assert dict(resultado.t) == T_ESPERADO


def test_la_hoja_solo_trae_las_categorias_del_esquema() -> None:
    """FR-001-14: una intervención o dimensión ajena al esquema no genera entrada ni suma."""
    ajeno = _doc(10, EN_EL_MAPA, ("Otra", I2), ("Otra dimensión", D3), IMPACTO)
    corpus = Corpus((*DOCUMENTOS, ajeno), (), 10)
    resultado = semantica_hoja(ESQUEMA, corpus, range(2, 11), VarianteHoja.ESTANDAR)
    assert resultado.t2 is not None
    assert resultado.t_ie is not None
    assert list(resultado.t1) == CLAVES
    assert list(resultado.t) == [I1, I2, I3]
    assert resultado.t1[(I2, D3)] == T1_ESPERADO[(I2, D3)] + 1  # la fila 10 suma una vez
    assert resultado.t2[(I2, D3)] == T2_ESPERADO[(I2, D3)] + 1
    assert resultado.t[I2] == T_ESPERADO[I2] + 1
    assert resultado.t_ie[I2] == T_IE_ESPERADO[I2] + 1


def test_los_conteos_de_la_hoja_son_enteros_de_solo_lectura() -> None:
    """FR-001-14: la semántica de la hoja son enteros (no `Conteo`) y no se altera desde afuera."""
    resultado = semantica_hoja(ESQUEMA, CORPUS, TODAS_LAS_FILAS, VarianteHoja.ESTANDAR)
    assert all(type(v) is int for v in resultado.t1.values())
    assert all(type(v) is int for v in resultado.t.values())
    with pytest.raises(TypeError):
        resultado.t[I1] = 0  # type: ignore[index]


# --------------------------------------------------------------------------------------------
# Invariantes del contrato §5 sobre este corpus (NFR-000-02)
# --------------------------------------------------------------------------------------------


def test_los_invariantes_del_contrato_se_cumplen_en_cada_celda() -> None:
    """NFR-000-02 (contrato §5): S^IE ≤ S ≤ T1, T2 ≤ T1, u ≤ t y u^IE ≤ t^IE (mismas filas)."""
    s = mapa(ESQUEMA, CORPUS).celdas
    s_ie = evaluacion_impacto(ESQUEMA, CORPUS)
    hoja = semantica_hoja(ESQUEMA, CORPUS, TODAS_LAS_FILAS, VarianteHoja.ESTANDAR)
    u = por_intervencion(ESQUEMA, CORPUS)
    u_ie = por_intervencion(ESQUEMA, CORPUS, solo_ie=True)
    assert s_ie is not None
    assert hoja.t2 is not None
    assert hoja.t_ie is not None
    for clave in CLAVES:
        assert s_ie[clave].valor <= s[clave].conteo.valor <= hoja.t1[clave]
        assert hoja.t2[clave] <= hoja.t1[clave]
        assert s_ie[clave].valor <= hoja.t2[clave]
    for i in (I1, I2, I3):
        assert u[i].valor <= hoja.t[i]
        assert u_ie[i].valor <= hoja.t_ie[i]
        assert hoja.t_ie[i] <= hoja.t[i]


def test_todo_numero_es_un_conteo_con_valor_igual_a_sus_filas() -> None:
    """NFR-000-02, FR-001-11: cada número es un `Conteo` y su valor es la longitud de su lista."""
    resultado = mapa(ESQUEMA, CORPUS)
    ie = evaluacion_impacto(ESQUEMA, CORPUS)
    assert ie is not None
    c = conjuntos(CORPUS)
    todos = [
        resultado.estudios,
        resultado.total,
        c.r,
        c.e,
        c.m,
        c.p,
        *(celda.conteo for celda in resultado.celdas.values()),
        *ie.values(),
        *por_nivel(ESQUEMA, CORPUS).values(),
        *por_intervencion(ESQUEMA, CORPUS).values(),
        *por_intervencion(ESQUEMA, CORPUS, solo_ie=True).values(),
    ]
    assert all(isinstance(x, Conteo) and x.valor == len(x.filas) for x in todos)
    assert len(todos) == 6 + 9 + 9 + 3 + 3 + 3
