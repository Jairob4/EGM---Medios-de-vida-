"""Pruebas P-001-16 a P-001-24 de la historia 1 (plan 001, T-001-21): M03, M04, M05 y M07.

Cada prueba abre un fixture de `data/fixtures/` con `egm.libro.abrir`, descubre el esquema con
`egm.esquema.descubrir`, lee los documentos con `egm.lectura.leer` y cuenta con `egm.conteo`. Nunca
se abre `data/raw/`.

Los esperados están escritos a mano a partir del contrato de datos (§4, §5, §6 y §9) y del contenido
documentado de los fixtures (constructor M23); ninguno sale de ejecutar el código bajo prueba.

Base válida (`MatrizSintetica.base_valida`), filas del archivo 2 a 6, el N.º k en la fila k + 1:

- N.º 1 teórico, N.º 5 normativo (no empíricos).
- N.º 2 empírico, Intervención A principal y B secundaria, nivel Evaluación de impacto,
  dimensiones 1 y 2 en 1.
- N.º 3 empírico, Intervención C, nivel Estudio de caso, dimensiones 3 y 4.
- N.º 4 empírico, Intervención A, nivel Informe de proyecto, dimensión 1.
- Intervenciones A a F; dimensiones 1 a 8; niveles Evaluación de impacto, Estudio de caso e
  Informe de proyecto (sin el valor «No aplica…»).

Firmas supuestas (arquitectura §6.1): `descubrir(libro) -> Esquema | FalloContrato`;
`leer(libro, esquema) -> Corpus`; `clasificar_enfoque(texto) -> (Enfoque, Advertencia | None)`;
`conjuntos(corpus)` con los `Conteo` `r`, `e`, `m` y `p`; `mapa(esquema, corpus)` con `celdas`
(`(intervencion, dimension)` → `Celda.conteo`, todas las combinaciones, también las de 0),
`estudios` y `total`; `evaluacion_impacto(esquema, corpus)` y `por_intervencion(esquema, corpus)`
y `por_nivel(esquema, corpus)` con una entrada por categoría del esquema.
"""

import ast
import re
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from egm.libro import abrir
from egm.modelo import SIN_NIVEL, Conteo, Enfoque, Esquema, EstadoDocumento, RefFila, Rol
from tests.constructor import carpeta_de_fixtures

# --------------------------------------------------------------------------------------------
# Esperados comunes (escritos a mano)
# --------------------------------------------------------------------------------------------

INTERVENCIONES_BASE = tuple(f"Intervención {c}" for c in "ABCDEF")
DIMENSIONES_BASE = tuple(f"Dimensión {n}" for n in range(1, 9))
NIVELES_BASE = ("Evaluación de impacto", "Estudio de caso", "Informe de proyecto")
ENFOQUE_ENCABEZADO = "Enfoque de género/diferencial"

A, B, C, D, G = (f"Intervención {c}" for c in "ABCDG")
D1, D2, D3, D4, D5, D9 = (f"Dimensión {n}" for n in (1, 2, 3, 4, 5, 9))


def _n(numero: int) -> RefFila:
    """El documento de la base válida con ese N.º (fila del archivo = N.º + 1)."""
    return RefFila(str(numero), numero + 1)


CELDAS_BASE: dict[tuple[str, str], tuple[RefFila, ...]] = {
    (A, D1): (_n(2), _n(4)),
    (A, D2): (_n(2),),
    (B, D1): (_n(2),),
    (B, D2): (_n(2),),
    (C, D3): (_n(3),),
    (C, D4): (_n(3),),
}
"""Celdas de la base válida con estudios: S(i, j) y los N.º que la producen (N.º 2, 3 y 4)."""


# --------------------------------------------------------------------------------------------
# Ayudas
# --------------------------------------------------------------------------------------------


class Lectura(NamedTuple):
    esquema: Esquema
    corpus: Any


def _procesar(nombre: str) -> Lectura:
    """Abre el fixture, descubre su estructura y lee sus documentos (M03, M04 y M05)."""
    from egm.esquema import descubrir
    from egm.lectura import leer

    libro = abrir((carpeta_de_fixtures() / nombre).read_bytes())
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema), f"{nombre}: se esperaba un Esquema y llegó {esquema!r}"
    return Lectura(esquema, leer(libro, esquema))


def _mapa(lectura: Lectura) -> Any:
    from egm.conteo import mapa

    resultado = mapa(lectura.esquema, lectura.corpus)
    esperadas = {
        (i, j) for i in lectura.esquema.intervenciones for j in lectura.esquema.dimensiones
    }
    assert set(resultado.celdas) == esperadas, "el mapa trae una celda por intervención y dimensión"
    return resultado


def _conjuntos(lectura: Lectura) -> Any:
    from egm.conteo import conjuntos

    return conjuntos(lectura.corpus)


def _con_estudios(mapa: Any) -> dict[tuple[str, str], tuple[RefFila, ...]]:
    """Las celdas con conteo mayor que 0: (intervención, dimensión) → filas que la producen."""
    return {k: celda.conteo.filas for k, celda in mapa.celdas.items() if celda.conteo.valor > 0}


def _filas(conteo: Conteo) -> tuple[int, ...]:
    """Números de fila del archivo de un conteo."""
    return tuple(ref.fila for ref in conteo.filas)


def _en_fila(corpus: Any, fila: int) -> Any:
    """El documento de esa fila del archivo."""
    encontrados = [d for d in corpus.documentos if d.ref.fila == fila]
    assert len(encontrados) == 1, f"no hay un único documento en la fila {fila}"
    return encontrados[0]


# --------------------------------------------------------------------------------------------
# P-001-16 · US-001-1.2, FR-001-08, FR-001-09: un estudio en cuatro celdas
# --------------------------------------------------------------------------------------------

ESTUDIO_UNICO = RefFila("1", 2)


def test_un_estudio_aparece_en_cuatro_celdas_y_cuenta_una_vez() -> None:
    """US-001-1.2: dos intervenciones por dos dimensiones dan 4 celdas y 1 estudio (FR-001-09)."""
    lectura = _procesar("esc_1_2_cuatro_celdas.xlsx")
    mapa = _mapa(lectura)

    esperado = {(i, j): (ESTUDIO_UNICO,) for i in (A, "Intervención B") for j in (D1, D2)}
    assert _con_estudios(mapa) == esperado
    assert len(mapa.celdas) == 6 * 8
    assert sum(celda.conteo.valor for celda in mapa.celdas.values()) == 4  # suma de celdas
    assert mapa.estudios.filas == (ESTUDIO_UNICO,)
    assert mapa.estudios.valor == 1  # estudios distintos, no la suma de celdas
    assert mapa.total.filas == (ESTUDIO_UNICO,)


def test_el_estudio_de_cuatro_celdas_es_un_solo_documento_del_mapa() -> None:
    """US-001-1.2, FR-001-08: R, E y M son ese documento; u(i) y S^IE se cuentan por estudio."""
    lectura = _procesar("esc_1_2_cuatro_celdas.xlsx")
    documento = _en_fila(lectura.corpus, 2)
    assert len(lectura.corpus.documentos) == 1
    assert documento.estado is EstadoDocumento.EN_EL_MAPA
    assert documento.intervenciones == (A, "Intervención B")
    assert set(documento.dimensiones) == {D1, D2}

    conjuntos = _conjuntos(lectura)
    for conteo in (conjuntos.r, conjuntos.e, conjuntos.m):
        assert conteo.filas == (ESTUDIO_UNICO,)
    assert conjuntos.p.valor == 0

    from egm.conteo import evaluacion_impacto, por_intervencion

    u = por_intervencion(lectura.esquema, lectura.corpus)
    assert u[A].filas == (ESTUDIO_UNICO,)
    assert u["Intervención B"].filas == (ESTUDIO_UNICO,)
    assert sum(u[i].valor for i in INTERVENCIONES_BASE) == 2  # una vez por intervención

    ie = evaluacion_impacto(lectura.esquema, lectura.corpus)  # el estudio es de nivel de impacto
    assert ie is not None
    for i in (A, "Intervención B"):
        for j in (D1, D2):
            assert ie[(i, j)].filas == (ESTUDIO_UNICO,)
    assert sum(conteo.valor for conteo in ie.values()) == 4


# --------------------------------------------------------------------------------------------
# P-001-17 · US-001-1.3, FR-001-05, NFR-000-06: intervención y nivel agregados
# --------------------------------------------------------------------------------------------


def test_la_intervencion_agregada_es_fila_del_mapa_con_su_conteo() -> None:
    """US-001-1.3: «Intervención G» (lista y N.º 6, fila 7) aparece como fila del mapa."""
    lectura = _procesar("cb36_intervencion_nivel_agregados.xlsx")
    mapa = _mapa(lectura)
    seis = RefFila("6", 7)

    esperado_lista = (*INTERVENCIONES_BASE, G)  # agregada antes del valor «No aplica…»
    assert lectura.esquema.intervenciones == esperado_lista
    assert mapa.intervenciones == esperado_lista
    assert mapa.celdas[(G, D5)].conteo.valor == 1
    assert mapa.celdas[(G, D5)].conteo.filas == (seis,)
    assert _con_estudios(mapa) == {**CELDAS_BASE, (G, D5): (seis,)}
    assert mapa.total.filas == (_n(2), _n(3), _n(4), seis)


def test_el_nivel_agregado_es_un_nivel_del_esquema_y_cuenta_su_estudio() -> None:
    """US-001-1.3, NFR-000-06: el nivel nuevo sale de la lista de su archivo (T4)."""
    from egm.conteo import por_nivel

    lectura = _procesar("cb36_intervencion_nivel_agregados.xlsx")
    nuevo = "Estudio cuasiexperimental"
    assert lectura.esquema.niveles == (*NIVELES_BASE, nuevo)

    t4 = por_nivel(lectura.esquema, lectura.corpus)
    assert t4[nuevo].filas == (RefFila("6", 7),)
    assert t4["Evaluación de impacto"].filas == (_n(2),)
    assert t4["Estudio de caso"].filas == (_n(3),)
    assert t4["Informe de proyecto"].filas == (_n(4),)
    assert _en_fila(lectura.corpus, 7).nivel == nuevo


# --------------------------------------------------------------------------------------------
# P-001-18 · US-001-1.4, FR-001-03: dimensión agregada dentro del bloque
# --------------------------------------------------------------------------------------------


def test_la_columna_nueva_del_bloque_es_dimension_en_su_posicion() -> None:
    """US-001-1.4: «Dimensión nueva» (con lista 1,0) entre las dimensiones 4 y 5."""
    lectura = _procesar("cb37_dimension_agregada.xlsx")
    mapa = _mapa(lectura)
    esperadas = (
        *DIMENSIONES_BASE[:4],
        "Dimensión nueva",
        *DIMENSIONES_BASE[4:],
        "Dimensión sin lista",  # otra columna del bloque, sin lista: también es dimensión
    )
    assert lectura.esquema.dimensiones == esperadas
    assert mapa.dimensiones == esperadas


def test_la_dimension_agregada_se_cuenta_con_los_estudios_que_la_marcan() -> None:
    """US-001-1.4, FR-001-03: N.º 2 y 4 (filas 3 y 5) marcan la nueva; N.º 3 marca la otra."""
    lectura = _procesar("cb37_dimension_agregada.xlsx")
    mapa = _mapa(lectura)
    nueva, sin_lista = "Dimensión nueva", "Dimensión sin lista"

    esperado = {
        **CELDAS_BASE,
        (A, nueva): (_n(2), _n(4)),
        (B, nueva): (_n(2),),
        (C, sin_lista): (_n(3),),
    }
    assert _con_estudios(mapa) == esperado
    assert set(_en_fila(lectura.corpus, 3).dimensiones) == {D1, D2, nueva}
    assert set(_en_fila(lectura.corpus, 4).dimensiones) == {D3, D4, sin_lista}


# --------------------------------------------------------------------------------------------
# P-001-19 · US-001-1.5 (conteo), FR-001-06: 250 documentos
# --------------------------------------------------------------------------------------------


def test_se_leen_los_250_documentos_sin_limite_de_filas() -> None:
    """US-001-1.5: |R| = 250 (filas 2 a 251), también las que pasan de la fila 200."""
    lectura = _procesar("cb12_250_documentos.xlsx")
    corpus = lectura.corpus
    assert len(corpus.documentos) == 250
    assert corpus.documentos[0].ref == RefFila("1", 2)
    assert corpus.documentos[-1].ref == RefFila("250", 251)
    assert corpus.fila_final_leida == 251

    conjuntos = _conjuntos(lectura)
    assert conjuntos.r.valor == 250
    assert conjuntos.e.valor == 150  # 3 de cada 5 (N.º 2, 3 y 4 de la base, repetidos 50 veces)
    assert conjuntos.m.valor == 150
    assert conjuntos.p.valor == 0


def test_los_estudios_de_mas_alla_de_la_fila_200_entran_al_mapa() -> None:
    """US-001-1.5, FR-001-06: el último estudio de la celda (A, D1) está en la fila 250."""
    mapa = _mapa(_procesar("cb12_250_documentos.xlsx"))
    celda_a1 = mapa.celdas[(A, D1)].conteo
    assert celda_a1.valor == 100  # N.º 2, 4, 7, 9, …, 247, 249
    assert celda_a1.filas[-1] == RefFila("249", 250)
    assert mapa.celdas[(C, D3)].conteo.valor == 50  # N.º 3, 8, …, 248
    assert mapa.total.valor == 150


# --------------------------------------------------------------------------------------------
# P-001-20 · US-001-1.6, FR-001-10: clasificación del enfoque diferencial
# --------------------------------------------------------------------------------------------


def test_cada_texto_de_enfoque_queda_en_su_categoria() -> None:
    """US-001-1.6: No, Sin clasificar, Sí, Parcial, Sin clasificar y Sin diligenciar."""
    lectura = _procesar("esc_1_6_enfoque.xlsx")
    esperado = [
        Enfoque.NO,
        Enfoque.SIN_CLASIFICAR,
        Enfoque.SI,
        Enfoque.PARCIAL,
        Enfoque.SIN_CLASIFICAR,
        Enfoque.SIN_DILIGENCIAR,
    ]
    assert [d.enfoque for d in lectura.corpus.documentos] == esperado
    assert [d.ref.fila for d in lectura.corpus.documentos] == [2, 3, 4, 5, 6, 7]


def test_solo_los_enfoques_sin_clasificar_traen_advertencia() -> None:
    """US-001-1.6: «Nota: …» (N.º 2, fila 3) y «Si bien…» (N.º 5, fila 6); ninguna más."""
    lectura = _procesar("esc_1_6_enfoque.xlsx")
    filas = sorted(a.ref.fila for a in lectura.corpus.advertencias if a.ref is not None)
    assert filas == [3, 6]
    assert len(lectura.corpus.advertencias) == 2  # ninguna sin fila: la celda vacía no advierte


def test_el_texto_de_enfoque_se_conserva_tal_cual() -> None:
    """US-001-1.6, FR-001-10: el texto completo se guarda; la celda vacía es `None`."""
    lectura = _procesar("esc_1_6_enfoque.xlsx")
    assert (
        _en_fila(lectura.corpus, 3).textos[Rol.ENFOQUE]
        == "Nota: el documento menciona el enfoque de forma general."
    )
    assert _en_fila(lectura.corpus, 6).textos[Rol.ENFOQUE] == (
        "Si bien menciona el enfoque, no lo desarrolla."
    )
    assert _en_fila(lectura.corpus, 7).textos[Rol.ENFOQUE] is None


@pytest.mark.parametrize(
    ("texto", "categoria", "con_advertencia"),
    [
        ("No desarrolla el enfoque.", Enfoque.NO, False),
        ("Nota: el documento menciona el enfoque de forma general.", Enfoque.SIN_CLASIFICAR, True),
        ("Sí, aborda el enfoque de género.", Enfoque.SI, False),
        ("Parcial: solo en un componente.", Enfoque.PARCIAL, False),
        ("Si bien menciona el enfoque, no lo desarrolla.", Enfoque.SIN_CLASIFICAR, True),
        (None, Enfoque.SIN_DILIGENCIAR, False),
        ("   ", Enfoque.SIN_DILIGENCIAR, False),
        ("NO. Sin enfoque.", Enfoque.NO, False),  # sin distinguir mayúsculas
        ("  sí. Con espacios al inicio.", Enfoque.SI, False),
        ("Si", Enfoque.SIN_CLASIFICAR, True),  # «Si» sin tilde no es Sí
        ("Nombre del enfoque", Enfoque.SIN_CLASIFICAR, True),  # «Nombre» no es la palabra «No»
        ("Parcialmente incluido", Enfoque.SIN_CLASIFICAR, True),  # no es la palabra «Parcial»
    ],
)
def test_clasificar_enfoque_por_primera_palabra_completa(
    texto: str | None, categoria: Enfoque, con_advertencia: bool
) -> None:
    """US-001-1.6, FR-001-10 (contrato §6): prefijo como palabra completa, nunca por el resto."""
    from egm.lectura import clasificar_enfoque

    obtenida, advertencia = clasificar_enfoque(texto)
    assert obtenida is categoria
    assert (advertencia is not None) is con_advertencia


# --------------------------------------------------------------------------------------------
# P-001-21 · US-001-1.8, FR-001-01: columnas y hojas en otro orden
# --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("nombre", ["base_valida.xlsx", "esc_1_8_orden_alterado.xlsx"])
def test_mismos_conteos_y_listas_con_otro_orden_de_columnas_y_hojas(nombre: str) -> None:
    """US-001-1.8: la base y su variante reordenada dan las mismas listas y los mismos conteos."""
    lectura = _procesar(nombre)
    mapa = _mapa(lectura)

    assert lectura.esquema.intervenciones == INTERVENCIONES_BASE
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE
    assert lectura.esquema.niveles == NIVELES_BASE
    assert _con_estudios(mapa) == CELDAS_BASE
    assert mapa.estudios.filas == (_n(2), _n(3), _n(4))
    assert mapa.total.filas == (_n(2), _n(3), _n(4))
    assert [d.anio for d in lectura.corpus.documentos] == [2015, 2019, 2021, 2022, 2010]
    assert [d.estado for d in lectura.corpus.documentos] == [
        EstadoDocumento.NO_EMPIRICO,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.NO_EMPIRICO,
    ]


def test_los_roles_se_encuentran_por_encabezado_aunque_cambie_la_posicion() -> None:
    """US-001-1.8, FR-001-01: en la variante, los roles movidos quedan donde está su encabezado."""
    base = _procesar("base_valida.xlsx").esquema.columnas
    alterado = _procesar("esc_1_8_orden_alterado.xlsx").esquema.columnas
    assert dict(base) != dict(alterado)
    assert alterado[Rol.NIVEL_EVIDENCIA] < alterado[Rol.IDENTIFICADOR]  # el nivel pasó al inicio
    assert alterado[Rol.ENFOQUE] < alterado[Rol.REFERENCIA]
    assert alterado[Rol.TIPO_DOCUMENTO] > alterado[Rol.LIMITACIONES]
    assert alterado[Rol.ANIO] > alterado[Rol.APORTE]
    assert base[Rol.ANIO] < base[Rol.TIPO_DOCUMENTO] < base[Rol.NIVEL_EVIDENCIA]


# --------------------------------------------------------------------------------------------
# P-001-22 · US-001-1.10, CB-04: solo intervención secundaria
# --------------------------------------------------------------------------------------------


def test_el_estudio_con_solo_secundaria_entra_al_mapa_en_su_fila() -> None:
    """US-001-1.10: N.º 6 (fila 7), principal vacía y secundaria D, entra en la fila de D."""
    lectura = _procesar("cb04_solo_secundaria.xlsx")
    mapa = _mapa(lectura)
    seis = RefFila("6", 7)

    documento = _en_fila(lectura.corpus, 7)
    assert documento.estado is EstadoDocumento.EN_EL_MAPA
    assert documento.intervenciones == (D,)
    assert mapa.celdas[(D, D5)].conteo.filas == (seis,)
    assert _con_estudios(mapa) == {**CELDAS_BASE, (D, D5): (seis,)}
    assert _filas(_conjuntos(lectura).m) == (3, 4, 5, 7)


def test_la_principal_vacia_con_secundaria_no_genera_advertencia() -> None:
    """US-001-1.10, CB-04: ninguna advertencia por la principal vacía (ni otra) en la lectura."""
    lectura = _procesar("cb04_solo_secundaria.xlsx")
    assert lectura.corpus.advertencias == ()
    assert [a for a in lectura.esquema.advertencias if a.ref is not None] == []


# --------------------------------------------------------------------------------------------
# P-001-23 · SC-001-05, SC-000-06, NFR-000-06: las categorías son las de cada archivo
# --------------------------------------------------------------------------------------------


def test_esquema_con_categorias_y_dimension_agregadas() -> None:
    """SC-000-06: intervención G, nivel «Estudio cuasiexperimental» y «Dimensión 9» agregados."""
    lectura = _procesar("sc000_06_agregadas.xlsx")
    mapa = _mapa(lectura)
    seis = RefFila("6", 7)

    assert lectura.esquema.intervenciones == (*INTERVENCIONES_BASE, G)
    assert lectura.esquema.dimensiones == (*DIMENSIONES_BASE, D9)
    assert lectura.esquema.niveles == (*NIVELES_BASE, "Estudio cuasiexperimental")
    assert (mapa.intervenciones, mapa.dimensiones) == (
        lectura.esquema.intervenciones,
        lectura.esquema.dimensiones,
    )
    assert _con_estudios(mapa) == {**CELDAS_BASE, (G, D5): (seis,), (G, D9): (seis,)}
    assert lectura.corpus.advertencias == ()


def test_esquema_con_categorias_y_dimension_retiradas() -> None:
    """SC-000-06: «Intervención F», «Informe de proyecto» y «Dimensión 8» ya no están."""
    lectura = _procesar("sc000_06_retiradas.xlsx")
    mapa = _mapa(lectura)

    assert lectura.esquema.intervenciones == INTERVENCIONES_BASE[:5]
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE[:7]
    assert lectura.esquema.niveles == NIVELES_BASE[:2]
    assert (mapa.intervenciones, mapa.dimensiones) == (
        lectura.esquema.intervenciones,
        lectura.esquema.dimensiones,
    )
    assert len(mapa.celdas) == 5 * 7
    assert _con_estudios(mapa) == CELDAS_BASE
    assert lectura.corpus.advertencias == ()


def test_esquema_con_categorias_renombradas() -> None:
    """SC-000-06: «Intervención A» pasa a «Intervención Alfa» y «Estudio de caso» a otro nombre."""
    lectura = _procesar("sc000_06_renombradas.xlsx")
    mapa = _mapa(lectura)
    alfa = "Intervención Alfa"

    assert lectura.esquema.intervenciones == (alfa, *INTERVENCIONES_BASE[1:])
    assert lectura.esquema.niveles == (
        "Evaluación de impacto",
        "Estudio monográfico",
        "Informe de proyecto",
    )
    esperado = {
        (alfa if i == A else i, j): filas for (i, j), filas in CELDAS_BASE.items()
    }  # mismos estudios, nombre nuevo
    assert _con_estudios(mapa) == esperado
    assert lectura.corpus.advertencias == ()


def test_esquema_con_categorias_retiradas_que_todavia_usan_filas() -> None:
    """SC-001-05 (cb40): C y «Informe de proyecto» salen de las listas, «Dimensión 8» de la hoja."""
    lectura = _procesar("cb40_retiradas.xlsx")
    mapa = _mapa(lectura)

    assert lectura.esquema.intervenciones == (
        A,
        "Intervención B",
        D,
        "Intervención E",
        "Intervención F",
    )
    assert lectura.esquema.dimensiones == DIMENSIONES_BASE[:7]
    assert lectura.esquema.niveles == NIVELES_BASE[:2]
    # El N.º 3 (fila 4) solo usaba C: I_r queda vacío, no entra al mapa y queda pendiente.
    assert all(C not in clave for clave in mapa.celdas)
    assert _con_estudios(mapa) == {k: v for k, v in CELDAS_BASE.items() if C not in k}
    assert _filas(mapa.total) == (3, 5)
    assert _en_fila(lectura.corpus, 4).estado is EstadoDocumento.EMPIRICO_PENDIENTE


# Valores anclas del contrato §4.1: los únicos nombres de categoría que el código puede escribir.
ANCLAS_PERMITIDAS = frozenset({"Estudio empírico", "Evaluación de impacto", "No aplica"})

# Nombres de categoría de los fixtures (constructor M23) y de la instancia v4 (apéndice A).
NOMBRES_DE_CATEGORIA = frozenset(
    {
        "Estudio empírico (evaluación/caso)",
        "No aplica (documento teórico/metodológico/normativo)",
        "No aplica (marco conceptual/normativo/metodológico)",
        "Estudio de caso",
        "Informe de proyecto",
        "Informe descriptivo/opinión",
        "Estudio cuasiexperimental",
        "Estudio monográfico",
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
        "Documento crítico-contextual",
        "Estudio comparativo internacional",
        "Académica",
        "Institucional",
        "Territorial",
        "Conceptual/teórica",
        "Transferencia de activos",
        "Acompañamiento técnico",
        "Vulnerabilidad",
        "Humano",
        "Social",
        "Natural",
        "Físico",
        "Financiero",
        "Estructuras y procesos",
        "Sostenibilidad",
        "Dimensión nueva",
        "Dimensión sin lista",
    }
)
PATRON_DE_NOMBRES_NUMERADOS = re.compile(
    r"^(Intervención ([A-G]|Alfa|Norte|Sur|sintética \d+)|Dimensión \d+"
    r"|Metodología ([A-C]|sintética \d+)|Nivel sintético \d+)$"
)

MODULOS_Y_FUNCIONES = {
    "esquema.py": {"descubrir"},
    "lectura.py": {"leer", "clasificar_enfoque"},
    "conteo.py": {
        "conjuntos",
        "mapa",
        "evaluacion_impacto",
        "por_intervencion",
        "por_nivel",
        "semantica_hoja",
    },
}


def _literales_de_texto(fuente: str) -> list[str]:
    """Cadenas que el código escribe, sin las documentaciones (módulo, clase, función)."""
    arbol = ast.parse(fuente)
    documentaciones: set[int] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            primero = nodo.body[0] if nodo.body else None
            if (
                isinstance(primero, ast.Expr)
                and isinstance(primero.value, ast.Constant)
                and isinstance(primero.value.value, str)
            ):
                documentaciones.add(id(primero.value))
    return [
        nodo.value
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Constant)
        and isinstance(nodo.value, str)
        and id(nodo) not in documentaciones
    ]


def _nombres_de_categoria_escritos(fuente: str) -> list[str]:
    """Literales del código que son nombres de categoría, salvo los valores ancla."""
    encontrados = []
    for texto in _literales_de_texto(fuente):
        limpio = texto.strip()
        if limpio in ANCLAS_PERMITIDAS:
            continue
        if limpio in NOMBRES_DE_CATEGORIA or PATRON_DE_NOMBRES_NUMERADOS.match(limpio):
            encontrados.append(limpio)
    return encontrados


def test_ningun_nombre_de_categoria_esta_escrito_en_el_codigo_salvo_las_anclas() -> None:
    """SC-001-05, NFR-000-06: M04, M05 y M07 existen y `src/egm/` no escribe categorías."""
    # El barrido mismo: ve un nombre de categoría y deja pasar una documentación y las anclas.
    ejemplo = '"""Doc: Intervención A."""\nx = "Intervención A"\ny = "Evaluación de impacto"\n'
    assert _nombres_de_categoria_escritos(ejemplo) == ["Intervención A"]

    carpeta = Path(__file__).resolve().parents[2] / "src" / "egm"
    for archivo, funciones in MODULOS_Y_FUNCIONES.items():
        arbol = ast.parse((carpeta / archivo).read_text(encoding="utf-8"))
        definidas = {n.name for n in arbol.body if isinstance(n, ast.FunctionDef)}
        assert funciones <= definidas, f"{archivo} aún no define {sorted(funciones - definidas)}"

    escritos = {
        archivo.name: _nombres_de_categoria_escritos(archivo.read_text(encoding="utf-8"))
        for archivo in sorted(carpeta.glob("*.py"))
    }
    assert {nombre: valores for nombre, valores in escritos.items() if valores} == {}


# --------------------------------------------------------------------------------------------
# P-001-24 · SC-001-02 (CB-01, 02, 03, 05, 28): estados y niveles de los casos borde
# --------------------------------------------------------------------------------------------

FILAS_DE_ESTUDIOS_BASE = (3, 4, 5)  # N.º 2, 3 y 4 de la base válida


def test_cb01_fila_solo_con_referencia_esta_en_r_y_no_en_e() -> None:
    """SC-001-02, CB-01: la fila 7 (N.º 6, solo referencia) queda sin tipo de documento válido."""
    lectura = _procesar("cb01_fila_solo_referencia.xlsx")
    conjuntos = _conjuntos(lectura)

    assert _en_fila(lectura.corpus, 7).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert _filas(conjuntos.r) == (2, 3, 4, 5, 6, 7)
    assert _filas(conjuntos.e) == FILAS_DE_ESTUDIOS_BASE
    assert _filas(conjuntos.m) == FILAS_DE_ESTUDIOS_BASE


def test_cb28_tipo_vacio_o_fuera_de_la_lista_esta_en_r_y_no_en_e() -> None:
    """SC-001-02, CB-28: filas 7 (tipo vacío) y 8 (tipo fuera de la lista), aunque traigan datos."""
    lectura = _procesar("cb28_tipo_vacio_o_fuera.xlsx")
    conjuntos = _conjuntos(lectura)

    for fila in (7, 8):
        assert _en_fila(lectura.corpus, fila).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert _filas(conjuntos.r) == (2, 3, 4, 5, 6, 7, 8)
    assert _filas(conjuntos.e) == FILAS_DE_ESTUDIOS_BASE
    assert conjuntos.p.valor == 0
    assert _con_estudios(_mapa(lectura)) == CELDAS_BASE  # los dos documentos no entran al mapa


def test_cb02_empirico_sin_intervencion_esta_en_e_y_en_p() -> None:
    """SC-001-02, CB-02: la fila 7 es empírica, sin intervención, con una dimensión en 1."""
    lectura = _procesar("cb02_empirico_sin_intervencion.xlsx")
    conjuntos = _conjuntos(lectura)
    documento = _en_fila(lectura.corpus, 7)

    assert documento.estado is EstadoDocumento.EMPIRICO_PENDIENTE
    assert documento.intervenciones == ()
    assert _filas(conjuntos.e) == (*FILAS_DE_ESTUDIOS_BASE, 7)
    assert _filas(conjuntos.p) == (7,)
    assert _filas(conjuntos.m) == FILAS_DE_ESTUDIOS_BASE
    assert _con_estudios(_mapa(lectura)) == CELDAS_BASE


def test_cb03_empirico_sin_dimensiones_esta_en_e_y_en_p() -> None:
    """SC-001-02, CB-03: la fila 7 trae la intervención D y ninguna dimensión en 1."""
    from egm.conteo import por_intervencion

    lectura = _procesar("cb03_empirico_sin_dimensiones.xlsx")
    conjuntos = _conjuntos(lectura)
    documento = _en_fila(lectura.corpus, 7)

    assert documento.estado is EstadoDocumento.EMPIRICO_PENDIENTE
    assert documento.intervenciones == (D,)
    assert documento.dimensiones == ()
    assert _filas(conjuntos.e) == (*FILAS_DE_ESTUDIOS_BASE, 7)
    assert _filas(conjuntos.p) == (7,)
    assert _filas(conjuntos.m) == FILAS_DE_ESTUDIOS_BASE
    assert _con_estudios(_mapa(lectura)) == CELDAS_BASE
    # u(i) no exige dimensiones marcadas (contrato §5): el estudio cuenta en su intervención.
    assert por_intervencion(lectura.esquema, lectura.corpus)[D].filas == (RefFila("6", 7),)


def test_cb05_sin_nivel_y_nivel_no_aplica_quedan_como_sin_nivel() -> None:
    """SC-001-02, CB-05: fila 7 con nivel vacío y fila 8 con «No aplica…» → `SIN_NIVEL`."""
    from egm.conteo import por_nivel

    lectura = _procesar("cb05_sin_nivel.xlsx")
    assert _en_fila(lectura.corpus, 7).nivel == SIN_NIVEL
    assert _en_fila(lectura.corpus, 8).nivel == SIN_NIVEL
    assert _en_fila(lectura.corpus, 3).nivel == "Evaluación de impacto"  # el nivel con valor, igual

    for fila in (7, 8):
        assert _en_fila(lectura.corpus, fila).estado is EstadoDocumento.EN_EL_MAPA
    assert _filas(_conjuntos(lectura).m) == (3, 4, 5, 7, 8)
    assert _con_estudios(_mapa(lectura))[(D, D5)] == (RefFila("6", 7), RefFila("7", 8))
    # T4 solo cuenta niveles de la lista: los dos estudios sin nivel no suman en ninguno.
    t4 = por_nivel(lectura.esquema, lectura.corpus)
    assert sum(c.valor for nivel, c in t4.items() if nivel != SIN_NIVEL) == 3
