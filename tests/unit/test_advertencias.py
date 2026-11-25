"""Pruebas P-001-26, P-001-27, P-001-29 a P-001-38 y P-001-40 a P-001-43 (T-001-31, historia 2).

Verifican la lista cerrada de errores de contrato, las advertencias de estructura y de fila, la nota
de columnas no usadas y los textos legibles de cada una (plan 001, fase 4; spec 001, US-001-2.1 a
2.16; FR-001-02, 03, 04, 10, 12, 13, 21, 22, 23, 24 y 29; SC-001-02 y SC-001-04). Se escriben antes
de la implementación (M04, M05 y M10): deben fallar hasta que T-001-32, T-001-33 y T-001-34 las
cumplan. Cada prueba abre un fixture de `data/fixtures/` (o una variante armada con el constructor
M23) con `egm.libro.abrir`, descubre la estructura con `egm.esquema.descubrir`, lee los documentos
con `egm.lectura.leer` y pasa los resultados por `egm.textos`. Nunca se abre `data/raw/`.

Esperados escritos a mano a partir del contrato de datos (§3, §3.1, §4, §4.1, §4.2 y §9), del spec
001 y de `docs/interfaz/flujos.md` (estado E4 y F-001-2); ninguno sale de ejecutar el código bajo
prueba.

Base válida (`MatrizSintetica.base_valida`): documentos N.º 1 a 5 en las filas 2 a 6 (el N.º k en la
fila k + 1); N.º 1 teórico y N.º 5 normativo; N.º 2 empírico (A principal, B secundaria, nivel de
evaluación de impacto, dimensiones 1 y 2), N.º 3 empírico (C, nivel de caso, dimensiones 3 y 4) y
N.º 4 empírico (A, nivel de informe, dimensión 1). Los documentos que un fixture agrega siguen desde
la fila 7. Sin cambios, la base no trae advertencias ni notas.

Firmas supuestas (arquitectura §6.1, M04, M05 y M10; el contrato no fija los códigos, por eso
ninguna prueba compara un código):

- `descubrir(libro) -> Esquema | FalloContrato`; `Esquema.advertencias` y `Esquema.notas` traen las
  de estructura (con `ref` en `None`); `leer(libro, esquema) -> Corpus`; `Corpus.advertencias` trae
  las de fila (`ref` con N.º y fila del archivo, `columna` y `valor`).
- `egm.textos.advertencia(Advertencia) -> str`, `nota(Nota) -> str` y
  `error_contrato(FalloContrato) -> str`. La forma de una advertencia de fila es la del ejemplo de
  F-001-2: «N.º 7, columna «Enfoque de género/diferencial», valor «…»: …». Un error de contrato
  sigue el estado E4: «No se pudo leer la matriz. Se esperaba <lo esperado>, y no se encontró / se
  encontraron: <lo encontrado>. No se muestra ninguna cifra. Revise que el archivo sea la matriz
  bibliográfica del proyecto y vuelva a cargarlo.»
- La advertencia de un valor cuyo texto traía espacios en los extremos puede guardar el valor con o
  sin ellos; las pruebas comparan el valor sin espacios.
"""

from collections.abc import Callable, Iterable
from typing import NamedTuple

import pytest

from egm.libro import abrir
from egm.modelo import (
    Advertencia,
    AnioNoReconocido,
    Corpus,
    Documento,
    Esquema,
    EstadoDocumento,
    FalloContrato,
    RefFila,
    Rol,
)
from tests.constructor import (
    ENCABEZADO_DELIMITADOR_FINAL,
    ENCABEZADO_DELIMITADOR_INICIAL,
    HOJA_MATRIZ,
    MARCADORES_CELDAS,
    NOMBRE_CON_MARCADOR,
    VALOR_EMPIRICO,
    VALOR_IMPACTO,
    MatrizSintetica,
    carpeta_de_fixtures,
)

NUMERO = "N°"
ANIO = "Año"
TIPO = "Tipo de documento"
FUENTE = "Tipo de fuente"
PRINCIPAL = "Tipo de intervención (EGM)"
SECUNDARIA = "Intervención secundaria (opcional)"
METODOLOGIA = "Metodología"
NIVEL = "Nivel de evidencia"
ENFOQUE = "Enfoque de género/diferencial"

A, B, C, D = (f"Intervención {c}" for c in "ABCD")
D1, D2, D3, D4, D5 = (f"Dimensión {n}" for n in (1, 2, 3, 4, 5))

INTERVENCIONES_BASE = tuple(f"Intervención {c}" for c in "ABCDEF")
DIMENSIONES_BASE = tuple(f"Dimensión {n}" for n in range(1, 9))
NIVELES_BASE = (VALOR_IMPACTO, "Estudio de caso", "Informe de proyecto")

# Frases fijas del estado E4 de `docs/interfaz/flujos.md` §2.
E4_INICIO = "No se pudo leer la matriz."
E4_ESPERABA = "Se esperaba"
E4_SIN_CIFRAS = "No se muestra ninguna cifra."
E4_CIERRE = "Revise que el archivo sea la matriz bibliográfica del proyecto y vuelva a cargarlo."

# Palabras que ningún texto dirigido al equipo puede traer (NFR-000-03; flujos §2, reglas de texto).
PALABRAS_PROHIBIDAS = ("error de contrato", "validación", "fixture")


# --------------------------------------------------------------------------------------------
# Ayudas
# --------------------------------------------------------------------------------------------


class Lectura(NamedTuple):
    """Resultado de leer un libro válido: la estructura y los documentos."""

    esquema: Esquema
    corpus: Corpus

    @property
    def advertencias(self) -> tuple[Advertencia, ...]:
        """Las advertencias de estructura y, después, las de fila."""
        return (*self.esquema.advertencias, *self.corpus.advertencias)


def _bytes(nombre: str) -> bytes:
    return (carpeta_de_fixtures() / nombre).read_bytes()


def _leer(contenido: bytes) -> Lectura:
    """M03, M04 y M05 sobre el libro; el contrato se cumple, así que debe haber un `Esquema`."""
    from egm.esquema import descubrir
    from egm.lectura import leer

    libro = abrir(contenido)
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema), f"se esperaba un Esquema y llegó {esquema!r}"
    return Lectura(esquema, leer(libro, esquema))


def _fixture(nombre: str) -> Lectura:
    return _leer(_bytes(nombre))


def _fallo(contenido: bytes) -> FalloContrato:
    """M04 sobre un libro que incumple el contrato: no hay esquema ni corpus."""
    from egm.esquema import descubrir

    resultado = descubrir(abrir(contenido))
    assert isinstance(resultado, FalloContrato), f"se esperaba un fallo y llegó {resultado!r}"
    return resultado


def _fallo_de_fixture(nombre: str) -> FalloContrato:
    return _fallo(_bytes(nombre))


def _base() -> MatrizSintetica:
    return MatrizSintetica.base_valida()


def _n(numero: int) -> RefFila:
    """El documento de la base válida con ese N.º (la fila del archivo es el N.º + 1)."""
    return RefFila(str(numero), numero + 1)


def _doc(corpus: Corpus, fila: int) -> Documento:
    encontrados = [d for d in corpus.documentos if d.ref.fila == fila]
    assert len(encontrados) == 1, f"no hay un único documento en la fila {fila}"
    return encontrados[0]


def _en_fila(advertencias: Iterable[Advertencia], fila: int) -> list[Advertencia]:
    return [a for a in advertencias if a.ref is not None and a.ref.fila == fila]


def _en_columna(advertencias: Iterable[Advertencia], fila: int, columna: str) -> list[Advertencia]:
    return [a for a in _en_fila(advertencias, fila) if a.columna == columna]


def _una(advertencias: Iterable[Advertencia], fila: int, columna: str) -> Advertencia:
    """La única advertencia de esa fila y esa columna."""
    encontradas = _en_columna(advertencias, fila, columna)
    assert len(encontradas) == 1, f"fila {fila}, columna {columna!r}: {encontradas!r}"
    return encontradas[0]


def _valor(advertencia: Advertencia) -> str:
    """El valor de la advertencia sin espacios en los extremos."""
    assert advertencia.valor is not None, f"la advertencia no trae valor: {advertencia!r}"
    return advertencia.valor.strip()


def _texto(advertencia: Advertencia) -> str:
    from egm.textos import advertencia as texto

    return texto(advertencia)


def _texto_error(fallo: FalloContrato) -> str:
    from egm.textos import error_contrato

    return error_contrato(fallo)


def _textos_de_notas(esquema: Esquema) -> list[str]:
    from egm.textos import nota

    return [nota(n) for n in esquema.notas]


def _esperado(fallo: FalloContrato) -> list[str]:
    return [texto for error in fallo.errores for texto in error.esperado]


def _encontrado(fallo: FalloContrato) -> list[str]:
    return [texto for error in fallo.errores for texto in error.encontrado]


def _conteo_de(
    esquema: Esquema, corpus: Corpus, intervencion: str, dimension: str
) -> tuple[RefFila, ...]:
    from egm.conteo import mapa

    return mapa(esquema, corpus).celdas[(intervencion, dimension)].conteo.filas


# --------------------------------------------------------------------------------------------
# P-001-26 · US-001-2.1, FR-001-12, CB-10
# --------------------------------------------------------------------------------------------


def test_p001_26_valor_fuera_de_lista_del_n3_con_n_columna_y_valor() -> None:
    """US-001-2.1, FR-001-12, CB-10: el N.º 3 con una intervención fuera de lista advierte."""
    lectura = _fixture("esc_2_1_fuera_de_lista_n3.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == _n(3)
    assert advertencia.columna == PRINCIPAL
    assert advertencia.valor is not None
    assert advertencia.valor.strip() == "Intervención Z"

    texto = _texto(advertencia)
    assert "N.º 3" in texto
    assert PRINCIPAL in texto
    assert "Intervención Z" in texto


def test_p001_26_el_valor_fuera_de_lista_no_se_cuenta() -> None:
    """US-001-2.1, FR-001-12: sin intervención válida, el N.º 3 queda pendiente y fuera del mapa."""
    lectura = _fixture("esc_2_1_fuera_de_lista_n3.xlsx")
    from egm.conteo import conjuntos, mapa

    documento = _doc(lectura.corpus, 4)
    assert documento.intervenciones == ()
    assert documento.estado is EstadoDocumento.EMPIRICO_PENDIENTE
    assert conjuntos(lectura.corpus).p.filas == (_n(3),)
    resultado = mapa(lectura.esquema, lectura.corpus)
    assert resultado.total.filas == (_n(2), _n(4))
    assert resultado.celdas[(C, D3)].conteo.filas == ()
    assert "Intervención Z" not in resultado.intervenciones


def test_p001_26_cada_columna_fuera_de_lista_tiene_su_advertencia_y_no_se_cuenta() -> None:
    """US-001-2.1, FR-001-12, CB-10: tipo de fuente, metodología y nivel fuera de lista (N.º 6)."""
    lectura = _fixture("cb10_fuera_de_lista.xlsx")
    from egm.conteo import por_nivel

    assert lectura.esquema.advertencias == ()
    assert {(a.ref, a.columna, _valor(a)) for a in lectura.corpus.advertencias} == {
        (RefFila("6", 7), FUENTE, "Fuente fuera de lista"),
        (RefFila("6", 7), METODOLOGIA, "Metodología fuera de lista"),
        (RefFila("6", 7), NIVEL, "Nivel fuera de lista"),
    }
    assert len(lectura.corpus.advertencias) == 3
    # El nivel fuera de lista no suma en ninguna categoría de $T_4$ (contrato §5).
    niveles = por_nivel(lectura.esquema, lectura.corpus)
    assert {nivel: conteo.filas for nivel, conteo in niveles.items()} == {
        VALOR_IMPACTO: (_n(2),),
        "Estudio de caso": (_n(3),),
        "Informe de proyecto": (_n(4),),
    }
    for advertencia in lectura.corpus.advertencias:
        assert _valor(advertencia) in _texto(advertencia)
        assert "N.º 6" in _texto(advertencia)


# --------------------------------------------------------------------------------------------
# P-001-27 · US-001-2.2, FR-001-08, CB-07
# --------------------------------------------------------------------------------------------


def test_p001_27_misma_intervencion_se_cuenta_una_vez_en_su_celda() -> None:
    """US-001-2.2, FR-001-08, CB-07: el N.º 6 con D en principal y secundaria cuenta una vez."""
    lectura = _fixture("cb07_misma_intervencion.xlsx")
    documento = _doc(lectura.corpus, 7)

    assert documento.intervenciones == (D,)
    assert documento.crudos.principal_igual_secundaria is True
    assert _conteo_de(lectura.esquema, lectura.corpus, D, D5) == (RefFila("6", 7),)


def test_p001_27_advierte_que_la_hoja_egm_lo_cuenta_dos_veces() -> None:
    """US-001-2.2, FR-001-12, CB-07: una advertencia del N.º 6: la hoja lo cuenta dos veces."""
    lectura = _fixture("cb07_misma_intervencion.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == RefFila("6", 7)
    assert advertencia.columna in (PRINCIPAL, SECUNDARIA)
    assert _valor(advertencia) == D

    texto = _texto(advertencia)
    assert "N.º 6" in texto
    assert D in texto
    assert "EGM" in texto
    assert "dos veces" in texto


# --------------------------------------------------------------------------------------------
# P-001-29 · US-001-2.4, FR-001-02, CB-14
# --------------------------------------------------------------------------------------------


def test_p001_29_sin_encabezado_de_nivel_de_evidencia_es_un_fallo_que_lo_nombra() -> None:
    """US-001-2.4, FR-001-02, CB-14: sin «Nivel de evidencia», fallo de contrato sin esquema."""
    from egm.esquema import descubrir

    resultado = descubrir(abrir(_bytes("cb14_sin_nivel_de_evidencia.xlsx")))

    assert isinstance(resultado, FalloContrato)
    assert not isinstance(resultado, Esquema)
    assert NIVEL in _esperado(resultado)
    assert NIVEL not in _encontrado(resultado)
    assert NIVEL in _texto_error(resultado)


# --------------------------------------------------------------------------------------------
# P-001-30 · US-001-2.5, FR-001-03
# --------------------------------------------------------------------------------------------


def test_p001_30_sin_delimitador_final_es_un_fallo_que_lo_nombra() -> None:
    """US-001-2.5, FR-001-03: sin «Indicadores o categorías analíticas», fallo de contrato."""
    fallo = _fallo_de_fixture("esc_2_5_sin_delimitador_final.xlsx")

    assert ENCABEZADO_DELIMITADOR_FINAL in _esperado(fallo)
    assert ENCABEZADO_DELIMITADOR_FINAL not in _encontrado(fallo)
    assert ENCABEZADO_DELIMITADOR_INICIAL not in _esperado(fallo)
    assert ENCABEZADO_DELIMITADOR_FINAL in _texto_error(fallo)


def test_p001_30_sin_delimitador_inicial_es_un_fallo_que_lo_nombra() -> None:
    """US-001-2.5, FR-001-03: la misma regla para el otro delimitador del bloque."""
    contenido = _base().quitar_columna(ENCABEZADO_DELIMITADOR_INICIAL).a_bytes()
    fallo = _fallo(contenido)

    assert ENCABEZADO_DELIMITADOR_INICIAL in _esperado(fallo)
    assert ENCABEZADO_DELIMITADOR_FINAL not in _esperado(fallo)
    assert ENCABEZADO_DELIMITADOR_INICIAL in _texto_error(fallo)


# --------------------------------------------------------------------------------------------
# P-001-31 · US-001-2.6, FR-001-04, CB-19, CB-37
# --------------------------------------------------------------------------------------------


def test_p001_31_columna_con_lista_1_0_fuera_del_bloque_advierte_y_sigue() -> None:
    """US-001-2.6, FR-001-04, CB-19: «Marca de revisión» fuera del bloque, con lista 1,0."""
    lectura = _fixture("cb19_columna_1_0_fuera.xlsx")

    assert len(lectura.esquema.advertencias) == 1
    (advertencia,) = lectura.esquema.advertencias
    assert advertencia.ref is None
    assert "Marca de revisión" in _texto(advertencia)
    assert lectura.esquema.notas == ()
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE
    assert lectura.corpus.advertencias == ()
    assert len(lectura.corpus.documentos) == 5


def test_p001_31_columna_del_bloque_sin_lista_1_0_advierte_y_sigue() -> None:
    """US-001-2.6, FR-001-04, CB-37: «Dimensión sin lista» advierte; «Dimensión nueva» no."""
    lectura = _fixture("cb37_dimension_agregada.xlsx")

    assert len(lectura.esquema.advertencias) == 1
    (advertencia,) = lectura.esquema.advertencias
    assert advertencia.ref is None
    texto = _texto(advertencia)
    assert "Dimensión sin lista" in texto
    assert "Dimensión nueva" not in texto
    assert lectura.esquema.dimensiones == (
        D1,
        D2,
        D3,
        D4,
        "Dimensión nueva",
        D5,
        "Dimensión 6",
        "Dimensión 7",
        "Dimensión 8",
        "Dimensión sin lista",
    )
    assert lectura.corpus.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-32 · US-001-2.7, FR-001-02, CB-15
# --------------------------------------------------------------------------------------------


def test_p001_32_sin_hoja_de_la_matriz_es_un_fallo_que_nombra_la_hoja() -> None:
    """US-001-2.7, FR-001-02, CB-15: sin la hoja «Matriz bibliográfica», nada más."""
    from egm.esquema import descubrir

    resultado = descubrir(abrir(_bytes("cb15_sin_hoja_matriz.xlsx")))

    assert isinstance(resultado, FalloContrato)
    assert len(resultado.errores) == 1
    assert resultado.errores[0].esperado == (HOJA_MATRIZ,)
    assert HOJA_MATRIZ not in resultado.errores[0].encontrado
    assert "EGM" in resultado.errores[0].encontrado
    assert HOJA_MATRIZ in _texto_error(resultado)


# --------------------------------------------------------------------------------------------
# P-001-33 · US-001-2.8, FR-001-21, CB-18
# --------------------------------------------------------------------------------------------


def test_p001_33_columna_no_usada_es_una_nota_y_no_una_advertencia() -> None:
    """US-001-2.8, FR-001-21, CB-18: «columnas no usadas: Observaciones» y ninguna advertencia."""
    lectura = _fixture("cb18_columna_observaciones.xlsx")

    assert lectura.advertencias == ()
    assert len(lectura.esquema.notas) == 1
    (texto,) = _textos_de_notas(lectura.esquema)
    assert "columnas no usadas: observaciones" in texto.lower()
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE


def test_p001_33_varias_columnas_no_usadas_van_en_una_sola_nota() -> None:
    """US-001-2.8, FR-001-21: dos columnas ajenas, sin lista, fuera del bloque, una nota."""
    contenido = (
        _base()
        .agregar_columna("Observaciones", valores=["Nota 1", None, "Nota 3"])
        .agregar_columna("Comentarios del equipo", valores=[None, "Comentario 2"])
        .a_bytes()
    )
    lectura = _leer(contenido)

    assert lectura.advertencias == ()
    assert len(lectura.esquema.notas) == 1
    (texto,) = _textos_de_notas(lectura.esquema)
    assert "columnas no usadas: " in texto.lower()
    assert "Observaciones" in texto
    assert "Comentarios del equipo" in texto


def test_p001_33_sin_columnas_ajenas_no_hay_nota() -> None:
    """US-001-2.8, FR-001-21: la base válida no trae columnas ajenas, así que no hay nota."""
    lectura = _leer(_base().a_bytes())

    assert lectura.esquema.notas == ()
    assert lectura.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-34 · US-001-2.9, FR-001-23, CB-20
# --------------------------------------------------------------------------------------------


def test_p001_34_sin_ancla_de_estudio_empirico_es_un_fallo_con_esperado_y_encontrados() -> None:
    """US-001-2.9, FR-001-23, CB-20: la lista de tipo no trae «Estudio empírico…»."""
    fallo = _fallo_de_fixture("cb20_sin_ancla_empirico.xlsx")

    esperado = _esperado(fallo)
    assert len(esperado) >= 1
    assert all("Estudio empírico" in texto for texto in esperado)
    assert set(_encontrado(fallo)) == {
        "Estudio de campo",
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
    }


def test_p001_34_el_texto_del_fallo_nombra_lo_esperado_y_lo_encontrado() -> None:
    """US-001-2.9, FR-001-23, FR-001-29, CB-20: el mensaje dice el valor esperado y los hallados."""
    fallo = _fallo_de_fixture("cb20_sin_ancla_empirico.xlsx")
    texto = _texto_error(fallo)

    assert "Estudio empírico" in texto
    for encontrado in (
        "Estudio de campo",
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
    ):
        assert encontrado in texto


# --------------------------------------------------------------------------------------------
# P-001-35 · US-001-2.10, FR-001-23, CB-21
# --------------------------------------------------------------------------------------------


def test_p001_35_sin_ancla_de_evaluacion_de_impacto_advierte_y_el_mapa_se_calcula() -> None:
    """US-001-2.10, FR-001-23, CB-21: advertencia, mapa calculado y `evaluacion_impacto` en None."""
    lectura = _fixture("cb21_sin_ancla_ie.xlsx")
    from egm.conteo import evaluacion_impacto, mapa

    assert lectura.esquema.anclas.evaluacion_impacto is None
    assert len(lectura.esquema.advertencias) == 1
    (advertencia,) = lectura.esquema.advertencias
    assert advertencia.ref is None
    texto = _texto(advertencia)
    assert "Evaluación de impacto" in texto
    assert lectura.corpus.advertencias == ()

    resultado = mapa(lectura.esquema, lectura.corpus)
    assert resultado.total.filas == (_n(2), _n(3), _n(4))
    assert len(resultado.celdas) == len(INTERVENCIONES_BASE) * len(DIMENSIONES_BASE)
    assert resultado.celdas[(A, D1)].conteo.filas == (_n(2), _n(4))
    assert evaluacion_impacto(lectura.esquema, lectura.corpus) is None


# --------------------------------------------------------------------------------------------
# P-001-36 · US-001-2.11, FR-001-22, CB-24
# --------------------------------------------------------------------------------------------

SIN_LISTA_DE_ERROR = [
    pytest.param("cb24_nivel_sin_lista.xlsx", NIVEL, id="nivel"),
    pytest.param("cb24_principal_sin_lista.xlsx", PRINCIPAL, id="principal"),
    pytest.param("cb24_secundaria_sin_lista.xlsx", SECUNDARIA, id="secundaria"),
]


@pytest.mark.parametrize(("nombre", "columna"), SIN_LISTA_DE_ERROR)
def test_p001_36_columna_obligatoria_sin_lista_es_un_fallo_que_la_nombra(
    nombre: str, columna: str
) -> None:
    """US-001-2.11, FR-001-22, CB-24: nivel, principal o secundaria sin lista; se nombra."""
    from egm.esquema import descubrir

    resultado = descubrir(abrir(_bytes(nombre)))

    assert isinstance(resultado, FalloContrato)
    assert columna in _esperado(resultado)
    otras = {NIVEL, PRINCIPAL, SECUNDARIA} - {columna}
    assert not otras & set(_esperado(resultado))
    assert columna in _texto_error(resultado)


# --------------------------------------------------------------------------------------------
# P-001-37 · US-001-2.12, FR-001-22, CB-25
# --------------------------------------------------------------------------------------------

SIN_LISTA_DE_ADVERTENCIA = [
    pytest.param(
        "cb25_fuente_sin_lista.xlsx",
        FUENTE,
        ("Académica", "Institucional", "Territorial"),
        id="fuente",
    ),
    pytest.param(
        "cb25_metodologia_sin_lista.xlsx", METODOLOGIA, ("Metodología B",), id="metodologia"
    ),
]


@pytest.mark.parametrize(("nombre", "columna", "presentes"), SIN_LISTA_DE_ADVERTENCIA)
def test_p001_37_columna_sin_lista_advierte_y_usa_los_valores_presentes(
    nombre: str, columna: str, presentes: tuple[str, ...]
) -> None:
    """US-001-2.12, FR-001-22, CB-25: advertencia que nombra la columna y sus valores presentes."""
    lectura = _fixture(nombre)
    lista = {
        FUENTE: lectura.esquema.tipos_fuente,
        METODOLOGIA: lectura.esquema.metodologias,
    }[columna]

    assert lista.origen == "presentes"
    assert lista.valores == presentes
    assert len(lectura.esquema.advertencias) == 1
    (advertencia,) = lectura.esquema.advertencias
    assert advertencia.ref is None
    texto = _texto(advertencia)
    assert columna in texto
    for valor in presentes:
        assert valor in texto
    assert lectura.corpus.advertencias == ()


def test_p001_37_sin_lista_no_se_comprueban_valores_fuera_de_lista() -> None:
    """US-001-2.12, FR-001-22, contrato §4.2: sin lista, un valor nuevo es un valor presente."""
    contenido = _base().sin_lista(FUENTE).fijar_celda(0, FUENTE, "Fuente comunitaria").a_bytes()
    lectura = _leer(contenido)

    assert lectura.esquema.tipos_fuente.origen == "presentes"
    assert "Fuente comunitaria" in lectura.esquema.tipos_fuente.valores
    assert len(lectura.esquema.advertencias) == 1
    assert "Fuente comunitaria" in _texto(lectura.esquema.advertencias[0])
    assert lectura.corpus.advertencias == ()


# --------------------------------------------------------------------------------------------
# P-001-38 · US-001-2.13, FR-001-24, CB-27
# --------------------------------------------------------------------------------------------


def test_p001_38_anio_sf_del_n4_advierte_con_n_columna_y_valor() -> None:
    """US-001-2.13, FR-001-24, CB-27: el N.º 4 con «s. f.» en el año."""
    lectura = _fixture("esc_2_13_anio_sf_n4.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == _n(4)
    assert advertencia.columna == ANIO
    assert advertencia.valor == "s. f."

    texto = _texto(advertencia)
    assert "N.º 4" in texto
    assert ANIO in texto
    assert "s. f." in texto


def test_p001_38_el_documento_se_cuenta_con_anio_no_reconocido() -> None:
    """US-001-2.13, FR-001-24, CB-27: el N.º 4 sigue en $R$ y en el mapa, con año no reconocido."""
    lectura = _fixture("esc_2_13_anio_sf_n4.xlsx")
    from egm.conteo import conjuntos

    documento = _doc(lectura.corpus, 5)
    assert documento.anio == AnioNoReconocido("s. f.")
    assert documento.estado is EstadoDocumento.EN_EL_MAPA
    assert conjuntos(lectura.corpus).r.valor == 5
    assert _n(4) in conjuntos(lectura.corpus).m.filas


# --------------------------------------------------------------------------------------------
# P-001-40 · US-001-2.15, FR-001-13, FR-001-22, CB-25, CB-26
# --------------------------------------------------------------------------------------------


def test_p001_40_tipo_sin_lista_advierte_con_la_columna_y_los_valores_presentes() -> None:
    """US-001-2.15, FR-001-22, CB-25: una advertencia que nombra la columna y los valores."""
    lectura = _fixture("esc_2_15_tipo_sin_lista_cuatro_docs.xlsx")

    assert lectura.esquema.tipos_documento.origen == "presentes"
    assert lectura.esquema.tipos_documento.valores == (
        VALOR_EMPIRICO,
        "Marco teórico",
        "Estudio empirico",
    )
    assert lectura.esquema.anclas.empiricos == (VALOR_EMPIRICO,)
    assert len(lectura.esquema.advertencias) == 1
    texto = _texto(lectura.esquema.advertencias[0])
    assert TIPO in texto
    for valor in (VALOR_EMPIRICO, "Marco teórico", "Estudio empirico"):
        assert valor in texto
    assert [a for a in lectura.corpus.advertencias if a.columna == TIPO] == []


def test_p001_40_estados_de_los_cuatro_documentos() -> None:
    """US-001-2.15, FR-001-13, CB-26: en el mapa, no empírico, no empírico, sin tipo válido."""
    lectura = _fixture("esc_2_15_tipo_sin_lista_cuatro_docs.xlsx")

    assert [d.estado for d in lectura.corpus.documentos] == [
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.NO_EMPIRICO,
        EstadoDocumento.NO_EMPIRICO,
        EstadoDocumento.SIN_TIPO_VALIDO,
    ]
    assert [d.ref for d in lectura.corpus.documentos] == [_n(k) for k in (1, 2, 3, 4)]


# --------------------------------------------------------------------------------------------
# P-001-41 · US-001-2.16, FR-001-13, CB-28
# --------------------------------------------------------------------------------------------


def test_p001_41_tipo_fuera_de_lista_del_n3_advierte_y_queda_sin_tipo_valido() -> None:
    """US-001-2.16, FR-001-13, CB-28: el N.º 3 con un tipo que no está en la lista."""
    lectura = _fixture("esc_2_16_tipo_fuera_de_lista_n3.xlsx")
    from egm.conteo import conjuntos

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == _n(3)
    assert advertencia.columna == TIPO
    assert _valor(advertencia) == "Tipo fuera de lista"

    texto = _texto(advertencia)
    assert "N.º 3" in texto
    assert TIPO in texto
    assert "Tipo fuera de lista" in texto

    assert _doc(lectura.corpus, 4).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert conjuntos(lectura.corpus).e.filas == (_n(2), _n(4))
    assert conjuntos(lectura.corpus).r.valor == 5


# --------------------------------------------------------------------------------------------
# P-001-42 · SC-001-02 (CB-08, 09, 13, 22, 23, 38, 39, 40, 41 y espacios en los extremos)
# --------------------------------------------------------------------------------------------


def test_p001_42_cb08_no_empirico_con_intervencion_advierte_y_no_entra_en_e() -> None:
    """SC-001-02, CB-08: el N.º 6 no empírico con la intervención D advierte y no cuenta."""
    lectura = _fixture("cb08_no_empirico_con_intervencion.xlsx")
    from egm.conteo import conjuntos

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == RefFila("6", 7)
    assert advertencia.columna == PRINCIPAL
    assert _valor(advertencia) == D
    assert "N.º 6" in _texto(advertencia)

    assert _doc(lectura.corpus, 7).estado is EstadoDocumento.NO_EMPIRICO
    assert RefFila("6", 7) not in conjuntos(lectura.corpus).e.filas
    assert _conteo_de(lectura.esquema, lectura.corpus, D, D1) == ()


def test_p001_42_cb09_dimension_fuera_de_rango_advierte_y_no_marca() -> None:
    """SC-001-02, CB-09: el número 2 y el texto «Sí» en dos dimensiones advierten y no marcan."""
    lectura = _fixture("cb09_dimension_fuera_de_rango.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 2
    assert _valor(_una(lectura.corpus.advertencias, 7, D2)) == "2"
    assert _valor(_una(lectura.corpus.advertencias, 7, D3)) == "Sí"
    for advertencia in lectura.corpus.advertencias:
        assert advertencia.ref == RefFila("6", 7)

    documento = _doc(lectura.corpus, 7)
    assert documento.dimensiones == (D5,)
    assert documento.estado is EstadoDocumento.EN_EL_MAPA


def test_p001_42_cb13_numero_vacio_o_repetido_usa_tambien_el_numero_de_fila() -> None:
    """SC-001-02, CB-13: N.º vacío (fila 7) y N.º 3 repetido (fila 8) se identifican por la fila."""
    lectura = _fixture("cb13_numero_vacio_o_repetido.xlsx")

    assert lectura.esquema.advertencias == ()
    assert {a.ref.fila for a in lectura.corpus.advertencias if a.ref is not None} <= {4, 7, 8}
    vacio = _una(lectura.corpus.advertencias, 7, NUMERO)
    assert vacio.ref == RefFila(None, 7)
    repetido = _una(lectura.corpus.advertencias, 8, NUMERO)
    assert repetido.ref == RefFila("3", 8)
    assert _valor(repetido) == "3"

    assert "fila 7" in _texto(vacio).lower()
    texto_repetido = _texto(repetido)
    assert "N.º 3" in texto_repetido
    assert "fila 8" in texto_repetido.lower()

    # La trazabilidad distingue los dos documentos por su fila (FR-001-11).
    assert _conteo_de(lectura.esquema, lectura.corpus, D, D5) == (RefFila(None, 7), RefFila("3", 8))


def test_p001_42_cb22_lista_sin_no_aplica_advierte_y_toma_todo_como_categoria() -> None:
    """SC-001-02, CB-22: la lista de nivel sin «No aplica…» advierte nombrando la columna."""
    lectura = _fixture("cb22_sin_no_aplica.xlsx")

    assert lectura.esquema.niveles == NIVELES_BASE
    assert len(lectura.esquema.advertencias) == 1
    texto = _texto(lectura.esquema.advertencias[0])
    assert NIVEL in texto
    assert "No aplica" in texto
    assert lectura.corpus.advertencias == ()


def test_p001_42_cb23_varios_empiricos_advierte_y_todos_son_estudio_empirico() -> None:
    """SC-001-02, CB-23: dos valores «Estudio empírico…», advertencia que los nombra."""
    lectura = _fixture("cb23_varios_empiricos.xlsx")
    otro = "Estudio empírico (modalidad ampliada)"

    assert lectura.esquema.anclas.empiricos == (VALOR_EMPIRICO, otro)
    assert len(lectura.esquema.advertencias) == 1
    texto = _texto(lectura.esquema.advertencias[0])
    assert VALOR_EMPIRICO in texto
    assert otro in texto
    assert _doc(lectura.corpus, 7).estado is EstadoDocumento.EN_EL_MAPA
    assert lectura.corpus.advertencias == ()


def test_p001_42_cb38_bloque_vacio_advierte_y_los_empiricos_quedan_pendientes() -> None:
    """SC-001-02, CB-38: sin columnas entre los delimitadores, ningún estudio entra al mapa."""
    lectura = _fixture("cb38_bloque_vacio.xlsx")
    from egm.conteo import conjuntos, mapa

    assert lectura.esquema.dimensiones == ()
    assert len(lectura.esquema.advertencias) == 1
    assert "dimensiones" in _texto(lectura.esquema.advertencias[0]).lower()
    assert lectura.corpus.advertencias == ()

    assert [d.estado for d in lectura.corpus.documentos if d.ref.numero in ("2", "3", "4")] == [
        EstadoDocumento.EMPIRICO_PENDIENTE
    ] * 3
    assert conjuntos(lectura.corpus).p.filas == (_n(2), _n(3), _n(4))
    assert mapa(lectura.esquema, lectura.corpus).total.filas == ()


def test_p001_42_cb38_bloque_invertido_advierte_y_los_empiricos_quedan_pendientes() -> None:
    """SC-001-02, CB-38: el delimitador final antes del inicial tampoco deja dimensiones."""
    lectura = _fixture("cb38_bloque_invertido.xlsx")
    from egm.conteo import conjuntos, mapa

    assert lectura.esquema.dimensiones == ()
    assert len(lectura.esquema.advertencias) >= 1
    assert any("dimensiones" in _texto(a).lower() for a in lectura.esquema.advertencias)
    assert conjuntos(lectura.corpus).p.filas == (_n(2), _n(3), _n(4))
    assert mapa(lectura.esquema, lectura.corpus).total.filas == ()


def test_p001_42_cb39_rol_dentro_del_bloque_se_toma_con_su_rol_y_advierte() -> None:
    """SC-001-02, CB-39: «Metodología» dentro del bloque no es dimensión; se lee como rol."""
    lectura = _fixture("cb39_rol_en_bloque.xlsx")
    columnas = lectura.esquema.columnas

    assert lectura.esquema.dimensiones == DIMENSIONES_BASE
    assert METODOLOGIA not in lectura.esquema.dimensiones
    assert (
        columnas[Rol.DELIMITADOR_INICIAL]
        < columnas[Rol.METODOLOGIA]
        < columnas[Rol.DELIMITADOR_FINAL]
    )
    assert len(lectura.esquema.advertencias) == 1
    assert METODOLOGIA in _texto(lectura.esquema.advertencias[0])
    assert lectura.corpus.advertencias == ()
    assert _doc(lectura.corpus, 3).metodologia == "Metodología B"
    assert _doc(lectura.corpus, 6).metodologia is None


def test_p001_42_cb40_categoria_retirada_desaparece_del_mapa_y_sus_filas_advierten() -> None:
    """SC-001-02, CB-40: C, «Informe de proyecto» y «Dimensión 8» retirados; filas que los usan."""
    lectura = _fixture("cb40_retiradas.xlsx")
    from egm.conteo import mapa

    assert lectura.esquema.intervenciones == (A, B, D, "Intervención E", "Intervención F")
    assert lectura.esquema.niveles == (VALOR_IMPACTO, "Estudio de caso")
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE[:7]
    assert lectura.esquema.advertencias == ()

    assert len(lectura.corpus.advertencias) == 2
    assert _valor(_una(lectura.corpus.advertencias, 4, PRINCIPAL)) == C
    assert _valor(_una(lectura.corpus.advertencias, 5, NIVEL)) == "Informe de proyecto"
    assert _una(lectura.corpus.advertencias, 4, PRINCIPAL).ref == _n(3)
    assert _una(lectura.corpus.advertencias, 5, NIVEL).ref == _n(4)

    resultado = mapa(lectura.esquema, lectura.corpus)
    assert C not in resultado.intervenciones
    assert "Dimensión 8" not in resultado.dimensiones
    assert _doc(lectura.corpus, 4).estado is EstadoDocumento.EMPIRICO_PENDIENTE


def test_p001_42_cb41_numero_escrito_como_texto_advierte_y_no_marca() -> None:
    """SC-001-02, CB-41: el 1 como texto en la «Dimensión 3» del N.º 3 advierte y no marca."""
    lectura = _fixture("cb41_texto_1.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    advertencia = _una(lectura.corpus.advertencias, 4, D3)
    assert advertencia.ref == _n(3)
    assert _valor(advertencia) == "1"
    assert "N.º 3" in _texto(advertencia)

    documento = _doc(lectura.corpus, 4)
    assert documento.dimensiones == (D4,)
    assert documento.crudos.dimensiones_como_texto == (D3,)
    assert _conteo_de(lectura.esquema, lectura.corpus, C, D3) == ()
    assert _conteo_de(lectura.esquema, lectura.corpus, C, D4) == (_n(3),)


def test_p001_42_espacios_en_los_extremos_de_la_intervencion_advierten_sin_corregir() -> None:
    """SC-001-02, contrato §4 regla 6: «Intervención A » (N.º 2) advierte; nada se corrige."""
    lectura = _fixture("esc_3_17_espacios.xlsx")

    assert lectura.esquema.advertencias == ()
    assert len(lectura.corpus.advertencias) == 1
    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == _n(2)
    assert advertencia.columna == PRINCIPAL
    assert _valor(advertencia) == A

    documento = _doc(lectura.corpus, 3)
    assert documento.intervenciones == (A, B)
    assert documento.crudos.con_espacios == (Rol.INTERVENCION_PRINCIPAL,)
    assert "N.º 2" in _texto(advertencia)


ESPACIOS = [
    pytest.param(TIPO, Rol.TIPO_DOCUMENTO, VALOR_EMPIRICO, id="tipo"),
    pytest.param(FUENTE, Rol.TIPO_FUENTE, "Institucional", id="fuente"),
    pytest.param(PRINCIPAL, Rol.INTERVENCION_PRINCIPAL, A, id="principal"),
    pytest.param(SECUNDARIA, Rol.INTERVENCION_SECUNDARIA, B, id="secundaria"),
    pytest.param(METODOLOGIA, Rol.METODOLOGIA, "Metodología B", id="metodologia"),
    pytest.param(NIVEL, Rol.NIVEL_EVIDENCIA, VALOR_IMPACTO, id="nivel"),
]


@pytest.mark.parametrize(("columna", "rol", "valor"), ESPACIOS)
def test_p001_42_espacios_en_cada_columna_de_lista_advierten_y_el_valor_se_compara_sin_ellos(
    columna: str, rol: Rol, valor: str
) -> None:
    """SC-001-02, contrato §4 regla 6: espacios en los extremos en cada columna con lista."""
    contenido = _base().fijar_celda(1, columna, f"  {valor} ").a_bytes()
    lectura = _leer(contenido)

    advertencia = _una(lectura.corpus.advertencias, 3, columna)
    assert advertencia.ref == _n(2)
    assert _valor(advertencia) == valor
    assert len(lectura.corpus.advertencias) == 1

    documento = _doc(lectura.corpus, 3)
    assert documento.crudos.con_espacios == (rol,)
    assert documento.estado is EstadoDocumento.EN_EL_MAPA
    assert documento.intervenciones == (A, B)
    assert documento.nivel == VALOR_IMPACTO


# --------------------------------------------------------------------------------------------
# P-001-43 · SC-001-04, FR-001-12, FR-001-29 (texto)
# --------------------------------------------------------------------------------------------

FIXTURES_CON_ESQUEMA = [
    "esc_2_1_fuera_de_lista_n3.xlsx",
    "cb10_fuera_de_lista.xlsx",
    "cb07_misma_intervencion.xlsx",
    "cb19_columna_1_0_fuera.xlsx",
    "cb37_dimension_agregada.xlsx",
    "cb18_columna_observaciones.xlsx",
    "cb21_sin_ancla_ie.xlsx",
    "cb25_fuente_sin_lista.xlsx",
    "cb25_metodologia_sin_lista.xlsx",
    "esc_2_13_anio_sf_n4.xlsx",
    "esc_2_15_tipo_sin_lista_cuatro_docs.xlsx",
    "esc_2_16_tipo_fuera_de_lista_n3.xlsx",
    "cb08_no_empirico_con_intervencion.xlsx",
    "cb09_dimension_fuera_de_rango.xlsx",
    "cb13_numero_vacio_o_repetido.xlsx",
    "cb22_sin_no_aplica.xlsx",
    "cb23_varios_empiricos.xlsx",
    "cb38_bloque_vacio.xlsx",
    "cb38_bloque_invertido.xlsx",
    "cb39_rol_en_bloque.xlsx",
    "cb40_retiradas.xlsx",
    "cb41_texto_1.xlsx",
    "esc_3_17_espacios.xlsx",
    "cb11_enfoque_sin_prefijo.xlsx",
    "marcadores.xlsx",
]

FIXTURES_CON_FALLO = [
    "cb14_sin_nivel_de_evidencia.xlsx",
    "esc_2_5_sin_delimitador_final.xlsx",
    "cb15_sin_hoja_matriz.xlsx",
    "cb20_sin_ancla_empirico.xlsx",
    "cb24_nivel_sin_lista.xlsx",
    "cb24_principal_sin_lista.xlsx",
    "cb24_secundaria_sin_lista.xlsx",
]

# Lo que el texto de una advertencia de estructura debe nombrar: hoja, columna o valor (FR-001-12).
NOMBRES_DE_ESTRUCTURA = {
    "cb19_columna_1_0_fuera.xlsx": ("Marca de revisión",),
    "cb37_dimension_agregada.xlsx": ("Dimensión sin lista",),
    "cb21_sin_ancla_ie.xlsx": ("Evaluación de impacto",),
    "cb22_sin_no_aplica.xlsx": (NIVEL,),
    "cb23_varios_empiricos.xlsx": (VALOR_EMPIRICO, "Estudio empírico (modalidad ampliada)"),
    "cb25_fuente_sin_lista.xlsx": (FUENTE,),
    "cb25_metodologia_sin_lista.xlsx": (METODOLOGIA,),
    "esc_2_15_tipo_sin_lista_cuatro_docs.xlsx": (TIPO,),
    "cb39_rol_en_bloque.xlsx": (METODOLOGIA,),
}


def _revisar_texto_generico(texto: str) -> None:
    """Reglas de texto de todo mensaje al equipo (NFR-000-03): no vacío, sin jerga ni preguntas."""
    assert texto.strip()
    minusculas = texto.lower()
    for palabra in PALABRAS_PROHIBIDAS:
        assert palabra not in minusculas, f"el texto trae «{palabra}»: {texto!r}"
    assert "?" not in texto
    assert "¿" not in texto


def _revisar_texto_de_fila(advertencia: Advertencia, texto: str) -> None:
    """Una advertencia de fila dice N.º o número de fila, columna y valor (FR-001-12)."""
    assert advertencia.ref is not None
    assert advertencia.columna is not None, f"falta la columna: {advertencia!r}"
    assert advertencia.columna in texto
    if advertencia.valor is not None and advertencia.valor.strip():
        assert advertencia.valor.strip() in texto
    if advertencia.ref.numero is not None:
        assert f"N.º {advertencia.ref.numero}" in texto
    else:
        assert f"fila {advertencia.ref.fila}" in texto.lower()


@pytest.mark.parametrize("nombre", FIXTURES_CON_ESQUEMA)
def test_p001_43_textos_de_advertencias_y_notas_de_cada_fixture(nombre: str) -> None:
    """SC-001-04, FR-001-12: cada advertencia dice qué fila, columna y valor; cada nota, qué."""
    lectura = _fixture(nombre)

    for advertencia in lectura.corpus.advertencias:
        texto = _texto(advertencia)
        _revisar_texto_generico(texto)
        _revisar_texto_de_fila(advertencia, texto)

    textos_de_estructura = []
    for advertencia in lectura.esquema.advertencias:
        assert advertencia.ref is None
        texto = _texto(advertencia)
        _revisar_texto_generico(texto)
        if advertencia.columna is not None:
            assert advertencia.columna in texto
        textos_de_estructura.append(texto)
    for nombre_esperado in NOMBRES_DE_ESTRUCTURA.get(nombre, ()):
        assert any(nombre_esperado in texto for texto in textos_de_estructura), nombre_esperado

    for texto in _textos_de_notas(lectura.esquema):
        _revisar_texto_generico(texto)
        assert "Observaciones" in texto  # la única nota de estos fixtures es la de CB-18


def test_p001_43_el_ejemplo_de_la_interfaz_tiene_la_forma_n_columna_valor() -> None:
    """SC-001-04, FR-001-12 (F-001-2): «N.º 3, columna «…», valor «…»: …»."""
    (advertencia,) = _fixture("esc_2_1_fuera_de_lista_n3.xlsx").corpus.advertencias

    assert _texto(advertencia).startswith(
        "N.º 3, columna «Tipo de intervención (EGM)», valor «Intervención Z»: "
    )


def test_p001_43_el_texto_del_enfoque_cita_la_regla_de_la_hoja_instrucciones() -> None:
    """SC-001-04, FR-001-10 (F-001-2): el enfoque sin prefijo dice la regla y la categoría."""
    lectura = _fixture("cb11_enfoque_sin_prefijo.xlsx")

    assert [a.ref for a in lectura.corpus.advertencias] == [
        RefFila(str(k), k + 1) for k in (6, 7, 8)
    ]
    for numero, advertencia in zip((6, 7, 8), lectura.corpus.advertencias, strict=True):
        assert advertencia.columna == ENFOQUE
        texto = _texto(advertencia)
        assert texto.startswith(f"N.º {numero}, columna «{ENFOQUE}», valor «")
        assert "Instrucciones" in texto
        assert "Sin clasificar" in texto


@pytest.mark.parametrize("nombre", FIXTURES_CON_FALLO)
def test_p001_43_texto_del_error_de_contrato_dice_lo_esperado_y_lo_encontrado(nombre: str) -> None:
    """SC-001-04, FR-001-29 (E4): el mensaje trae lo esperado y lo encontrado, sin archivo."""
    fallo = _fallo_de_fixture(nombre)
    texto = _texto_error(fallo)

    _revisar_texto_generico(texto)
    assert texto.startswith(E4_INICIO)
    assert E4_ESPERABA in texto
    assert E4_SIN_CIFRAS in texto
    assert texto.rstrip().endswith(E4_CIERRE)
    for esperado in _esperado(fallo):
        assert esperado in texto
    for encontrado in _encontrado(fallo):
        assert encontrado in texto
    assert ".xlsx" not in texto
    assert "N.º" not in texto


def _con_marcadores() -> MatrizSintetica:
    """La base válida con un marcador único en seis celdas de texto de los N.º 2, 3 y 4."""
    matriz = _base()
    for fila, columna, texto in (
        (1, "Referencia APA", f"Autor 2 (2019). {MARCADORES_CELDAS[0]}."),
        (1, "País y población", MARCADORES_CELDAS[1]),
        (2, "Principales hallazgos / tesis central", MARCADORES_CELDAS[2]),
        (1, "Vacío de conocimiento identificado", MARCADORES_CELDAS[3]),
        (2, "Limitaciones", MARCADORES_CELDAS[4]),
        (3, "Aporte al proyecto", MARCADORES_CELDAS[5]),
    ):
        matriz.fijar_celda(fila, columna, texto)
    return matriz


def _sin_marcadores(texto: str) -> None:
    for marcador in (*MARCADORES_CELDAS, NOMBRE_CON_MARCADOR, ".xlsx"):
        assert marcador not in texto, f"el texto trae «{marcador}»: {texto!r}"


def test_p001_43_marcadores_no_produce_advertencias_ni_notas() -> None:
    """SC-001-04, SC-000-17: una matriz válida con textos libres no genera mensajes."""
    lectura = _fixture("marcadores.xlsx")

    assert lectura.advertencias == ()
    assert lectura.esquema.notas == ()


def test_p001_43_la_advertencia_de_fila_no_arrastra_las_otras_celdas_de_la_fila() -> None:
    """SC-001-04, FR-001-12: el texto solo trae el valor señalado, no los textos de esa fila."""
    contenido = _con_marcadores().fijar_celda(2, PRINCIPAL, "Intervención Z").a_bytes()
    lectura = _leer(contenido)

    (advertencia,) = lectura.corpus.advertencias
    assert advertencia.ref == _n(3)
    texto = _texto(advertencia)
    assert "Intervención Z" in texto
    _sin_marcadores(texto)


def _marcadores_sin_nivel_de_evidencia() -> bytes:
    return _con_marcadores().quitar_columna(NIVEL).a_bytes()


def _marcadores_sin_ancla_empirica() -> bytes:
    matriz = _con_marcadores().renombrar_valor_de_lista(TIPO, VALOR_EMPIRICO, "Estudio de campo")
    return matriz.reemplazar_valor(TIPO, VALOR_EMPIRICO, "Estudio de campo").a_bytes()


@pytest.mark.parametrize(
    "construir",
    [
        pytest.param(_marcadores_sin_nivel_de_evidencia, id="sin_nivel_de_evidencia"),
        pytest.param(_marcadores_sin_ancla_empirica, id="sin_ancla_empirica"),
    ],
)
def test_p001_43_el_error_de_contrato_no_trae_marcadores_de_celdas_ni_nombre_de_archivo(
    construir: Callable[[], bytes],
) -> None:
    """SC-001-04, FR-001-29, SC-000-17: ningún texto de las celdas llega al mensaje de error."""
    fallo = _fallo(construir())

    _sin_marcadores(_texto_error(fallo))
