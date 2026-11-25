"""Pruebas del camino válido de M05 `egm.lectura` (T-001-24).

Cubren `leer` y `clasificar_enfoque` sin M07: FR-001-06 (todas las filas, sin límite), FR-001-10
(enfoque por prefijo), FR-001-13 (estado de cada documento) y NFR-000-06 (ninguna categoría escrita
en el código). Complementan P-001-13, P-001-14, P-001-19, P-001-20, P-001-22 y P-001-24, que están
en `test_lectura_conteo.py` y en la integración con la v4.

Esperados escritos a mano a partir del contrato de datos (§3, §4 reglas 4 a 6, 10 y 12, §5 y §6) y
del contenido documentado de la base válida sintética (constructor M23): documentos N.º 1 a 5 en las
filas 2 a 6, con el N.º 1 teórico y el N.º 5 normativo, y los N.º 2, 3 y 4 empíricos. Ninguno sale
de ejecutar `egm.lectura`. Solo fixtures.
"""

from collections.abc import Mapping
from typing import Any

import pytest

from egm.esquema import descubrir
from egm.lectura import clasificar_enfoque, leer
from egm.libro import Celda, Hoja, Libro, ListaValidacion, Valor, abrir
from egm.modelo import (
    ANIO_NO_RECONOCIDO,
    DIMENSION_VALOR_INVALIDO,
    ENFOQUE_SIN_CLASIFICAR,
    ESPACIOS_EN_LOS_EXTREMOS,
    NO_EMPIRICO_CON_INTERVENCION,
    NUMERO_REPETIDO,
    NUMERO_VACIO,
    PRINCIPAL_IGUAL_SECUNDARIA,
    SIN_NIVEL,
    TIPO_DOCUMENTO_FUERA_DE_LISTA,
    VALOR_FUERA_DE_LISTA,
    AnioNoReconocido,
    Corpus,
    DatosCrudos,
    Documento,
    Enfoque,
    Esquema,
    EstadoDocumento,
    RefFila,
    Rol,
)
from tests.constructor import (
    ENCABEZADO_DELIMITADOR_FINAL,
    ENCABEZADO_DELIMITADOR_INICIAL,
    HOJA_MATRIZ,
    VALOR_EMPIRICO,
    VALOR_IMPACTO,
    VALOR_NO_APLICA_INTERVENCION,
    VALOR_NO_APLICA_NIVEL,
    MatrizSintetica,
    carpeta_de_fixtures,
)

NUMERO = "N°"
REFERENCIA = "Referencia APA"
ANIO = "Año"
TIPO = "Tipo de documento"
FUENTE = "Tipo de fuente"
PRINCIPAL = "Tipo de intervención (EGM)"
SECUNDARIA = "Intervención secundaria (opcional)"
METODOLOGIA = "Metodología"
NIVEL = "Nivel de evidencia"
ENFOQUE = "Enfoque de género/diferencial"
HALLAZGOS = "Principales hallazgos / tesis central"
VACIO = "Vacío de conocimiento identificado"
LIMITACIONES = "Limitaciones"
APORTE = "Aporte al proyecto"

A, B, C, D = (f"Intervención {c}" for c in "ABCD")
D1, D2, D3, D4, D5, D6 = (f"Dimensión {n}" for n in (1, 2, 3, 4, 5, 6))

# Las nueve columnas de texto que M05 guarda tal cual (arquitectura §6.1, M05, `textos`).
ROLES_DE_TEXTO = {
    Rol.REFERENCIA,
    Rol.PAIS_POBLACION,
    Rol.DELIMITADOR_INICIAL,
    Rol.DELIMITADOR_FINAL,
    Rol.ENFOQUE,
    Rol.HALLAZGOS,
    Rol.VACIO,
    Rol.LIMITACIONES,
    Rol.APORTE,
}


def _base() -> MatrizSintetica:
    return MatrizSintetica.base_valida()


def _leer(contenido: bytes) -> tuple[Esquema, Corpus]:
    libro = abrir(contenido)
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema), f"se esperaba un Esquema y llegó {esquema!r}"
    return esquema, leer(libro, esquema)


def _corpus(matriz: MatrizSintetica) -> Corpus:
    return _leer(matriz.a_bytes())[1]


def _fixture(nombre: str) -> Corpus:
    return _leer((carpeta_de_fixtures() / nombre).read_bytes())[1]


def _en_fila(corpus: Corpus, fila: int) -> Documento:
    encontrados = [d for d in corpus.documentos if d.ref.fila == fila]
    assert len(encontrados) == 1, f"no hay un único documento en la fila {fila}"
    return encontrados[0]


def _documento_minimo(numero: int | None, **celdas: Any) -> dict[str, Any]:
    """Un documento con casi nada: solo su N.º y las celdas que se indiquen (encabezado → valor)."""
    return {NUMERO: numero, **celdas}


# --------------------------------------------------------------------------------------------
# La base válida completa · FR-001-06, FR-001-13, FR-002-07
# --------------------------------------------------------------------------------------------


def test_la_base_valida_se_lee_documento_por_documento() -> None:
    """FR-001-06: cinco documentos (filas 2 a 6) con sus campos de dominio."""
    corpus = _corpus(_base())

    assert corpus.fila_final_leida == 6
    assert corpus.advertencias == ()
    assert [d.ref for d in corpus.documentos] == [RefFila(str(n), n + 1) for n in range(1, 6)]
    assert [d.anio for d in corpus.documentos] == [2015, 2019, 2021, 2022, 2010]
    assert [d.tipo_documento for d in corpus.documentos] == [
        "Documento teórico",
        VALOR_EMPIRICO,
        VALOR_EMPIRICO,
        VALOR_EMPIRICO,
        "Documento normativo",
    ]
    assert [d.tipo_fuente for d in corpus.documentos] == [
        "Académica",
        "Institucional",
        "Académica",
        "Territorial",
        "Institucional",
    ]
    assert [d.metodologia for d in corpus.documentos] == [
        "Metodología B",
        "Metodología B",
        "Metodología B",
        "Metodología B",
        None,  # el N.º 5 no tiene metodología
    ]
    assert [d.intervenciones for d in corpus.documentos] == [(), (A, B), (C,), (A,), ()]
    assert [d.dimensiones for d in corpus.documentos] == [(), (D1, D2), (D3, D4), (D1,), ()]
    assert [d.nivel for d in corpus.documentos] == [
        SIN_NIVEL,
        VALOR_IMPACTO,
        "Estudio de caso",
        "Informe de proyecto",
        SIN_NIVEL,
    ]
    assert [d.enfoque for d in corpus.documentos] == [
        Enfoque.NO,
        Enfoque.SI,
        Enfoque.PARCIAL,
        Enfoque.NO,
        Enfoque.NO,
    ]
    assert [d.estado for d in corpus.documentos] == [
        EstadoDocumento.NO_EMPIRICO,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.EN_EL_MAPA,
        EstadoDocumento.NO_EMPIRICO,
    ]
    assert all(d.crudos == DatosCrudos() for d in corpus.documentos)


def test_los_textos_se_guardan_tal_cual_en_sus_nueve_roles() -> None:
    """FR-002-07: referencia, país, hallazgos, aporte y enfoque con su texto; lo vacío es `None`."""
    documento = _en_fila(_corpus(_base()), 3)  # N.º 2

    assert set(documento.textos) == ROLES_DE_TEXTO
    assert documento.textos == {
        Rol.REFERENCIA: "Autor 2 (2019). Documento sintético 2.",
        Rol.PAIS_POBLACION: "País sintético, población sintética",
        Rol.DELIMITADOR_INICIAL: None,
        Rol.DELIMITADOR_FINAL: None,
        Rol.ENFOQUE: "Sí. Incluye el enfoque.",
        Rol.HALLAZGOS: "Hallazgo sintético 2.",
        Rol.VACIO: None,
        Rol.LIMITACIONES: None,
        Rol.APORTE: "Aporte sintético 2.",
    }


def test_los_textos_de_las_columnas_delimitadoras_tambien_se_guardan() -> None:
    """FR-002-07: «Dimensiones evaluadas / propuestas» e «Indicadores…» van en `textos`."""
    matriz = _base()
    matriz.fijar_celda(1, ENCABEZADO_DELIMITADOR_INICIAL, "Dimensiones del estudio.")
    matriz.fijar_celda(1, ENCABEZADO_DELIMITADOR_FINAL, "Indicador sintético.")
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.textos[Rol.DELIMITADOR_INICIAL] == "Dimensiones del estudio."
    assert documento.textos[Rol.DELIMITADOR_FINAL] == "Indicador sintético."


def test_un_texto_con_espacios_en_los_extremos_se_conserva_y_uno_en_blanco_es_vacio() -> None:
    """FR-002-07: «tal cual» no recorta; una celda solo con espacios es una celda vacía."""
    matriz = _base()
    matriz.fijar_celda(1, HALLAZGOS, "  Con espacios alrededor.  ")
    matriz.fijar_celda(1, LIMITACIONES, "   ")
    matriz.fijar_celda(1, VACIO, 25)
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.textos[Rol.HALLAZGOS] == "  Con espacios alrededor.  "
    assert documento.textos[Rol.LIMITACIONES] is None
    assert documento.textos[Rol.VACIO] == "25"  # un número también se muestra como texto


def test_el_corpus_y_los_textos_son_de_solo_lectura() -> None:
    """NFR-000-02: los documentos van en una tupla y `textos` no se puede alterar."""
    corpus = _corpus(_base())
    assert isinstance(corpus.documentos, tuple)
    textos: Mapping[Rol, str | None] = corpus.documentos[0].textos
    with pytest.raises(TypeError):
        textos[Rol.REFERENCIA] = "otra"  # type: ignore[index]


# --------------------------------------------------------------------------------------------
# Filas vacías y fila final · contrato §4 reglas 4 y 5
# --------------------------------------------------------------------------------------------


def test_las_filas_vacias_no_son_documentos_y_la_fila_final_es_la_ultima_con_contenido() -> None:
    """Contrato §4 regla 4: dos filas vacías en medio no cuentan; el último documento va en la 9."""
    matriz = _base().agregar_filas_vacias(2).agregar_fila(_documento_minimo(6))
    corpus = _corpus(matriz)
    assert [d.ref.fila for d in corpus.documentos] == [2, 3, 4, 5, 6, 9]
    assert corpus.documentos[-1].ref == RefFila("6", 9)
    assert corpus.fila_final_leida == 9


def test_una_fila_solo_con_espacios_se_trata_como_vacia() -> None:
    """Contrato §4 regla 4 y §6: una celda solo con espacios cuenta como vacía."""
    matriz = _base().agregar_fila({REFERENCIA: "   ", HALLAZGOS: " "})
    corpus = _corpus(matriz)
    assert len(corpus.documentos) == 5
    assert corpus.fila_final_leida == 6


def test_una_matriz_sin_documentos_da_un_corpus_vacio_con_fila_final_uno() -> None:
    """Contrato §4 regla 5: sin filas de datos, $R$ es vacío y solo se leyó el encabezado."""
    corpus = _corpus(_base().quitar_filas())
    assert corpus.documentos == ()
    assert corpus.advertencias == ()
    assert corpus.fila_final_leida == 1


def test_el_numero_vacio_con_contenido_se_lee_con_su_fila_del_archivo() -> None:
    """Contrato §4 regla 4: N.º vacío con contenido es un documento, ubicado por su fila."""
    matriz = _base().agregar_fila({REFERENCIA: "Autor sin número."})
    documento = _en_fila(_corpus(matriz), 7)
    assert documento.ref == RefFila(None, 7)


def test_el_numero_es_el_texto_del_n_de_la_matriz() -> None:
    """Contrato §3: el N.º entero 6 es el texto «6»; un N.º escrito como texto queda igual."""
    matriz = _base().agregar_fila(_documento_minimo(6)).agregar_fila(_documento_minimo(7))
    matriz.fijar_celda(6, NUMERO, "B-7")  # el documento 7 (índice 6) con el N.º escrito como texto
    corpus = _corpus(matriz)
    assert [d.ref for d in corpus.documentos[-2:]] == [RefFila("6", 7), RefFila("B-7", 8)]


def test_la_matriz_se_lee_aunque_pase_de_la_fila_200() -> None:
    """Contrato §4 regla 5 (FR-001-06): 230 documentos, también más allá del rango de la hoja."""
    matriz = _base()
    for numero in range(6, 231):
        matriz.agregar_fila(_documento_minimo(numero, **{TIPO: "Documento teórico"}))
    corpus = _corpus(matriz)
    assert len(corpus.documentos) == 230
    assert corpus.documentos[-1].ref == RefFila("230", 231)
    assert corpus.fila_final_leida == 231


# --------------------------------------------------------------------------------------------
# Intervenciones · I_r en el orden de la lista; G_r = H_r en `crudos`
# --------------------------------------------------------------------------------------------


def test_las_intervenciones_van_en_el_orden_de_la_lista_y_no_en_el_de_las_columnas() -> None:
    """Contrato §5: $I_r$ en el orden de la lista; principal B y secundaria A dan (A, B)."""
    matriz = _base()
    matriz.fijar_celda(1, PRINCIPAL, B)
    matriz.fijar_celda(1, SECUNDARIA, A)
    assert _en_fila(_corpus(matriz), 3).intervenciones == (A, B)


def test_una_intervencion_repetida_en_principal_y_secundaria_cuenta_una_vez_y_se_anota() -> None:
    """Contrato §9 ($G_r = H_r$): $I_r$ trae la intervención una vez; `crudos` lo recuerda."""
    corpus = _fixture("cb07_misma_intervencion.xlsx")
    documento = _en_fila(corpus, 7)  # N.º 6: principal D y secundaria D
    assert documento.intervenciones == (D,)
    assert documento.crudos == DatosCrudos(principal_igual_secundaria=True)
    assert all(not d.crudos.principal_igual_secundaria for d in corpus.documentos[:-1])


def test_una_secundaria_distinta_no_es_g_igual_h() -> None:
    """Contrato §9: con dos intervenciones distintas `crudos` no marca $G_r = H_r$."""
    assert _en_fila(_corpus(_base()), 3).crudos.principal_igual_secundaria is False


def test_la_secundaria_no_aplica_no_es_intervencion() -> None:
    """Contrato §4 regla 8: «No aplica…» (valor de la lista) queda fuera de $I_r$."""
    matriz = _base()
    matriz.fijar_celda(2, SECUNDARIA, VALOR_NO_APLICA_INTERVENCION)
    documento = _en_fila(_corpus(matriz), 4)  # N.º 3, solo C
    assert documento.intervenciones == (C,)
    assert documento.crudos == DatosCrudos()


def test_un_valor_fuera_de_la_lista_de_intervenciones_no_entra_en_ir() -> None:
    """Contrato §5: $I_r = \\{G_r, H_r\\} \\cap \\mathcal{I}$; lo que no es categoría no cuenta."""
    matriz = _base()
    matriz.fijar_celda(1, SECUNDARIA, "Intervención inexistente")
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.intervenciones == (A,)
    assert documento.crudos.principal_igual_secundaria is False


# --------------------------------------------------------------------------------------------
# Dimensiones · solo el 1 numérico marca; el texto «1» va a `crudos` (contrato §4 regla 10)
# --------------------------------------------------------------------------------------------


def test_el_texto_1_no_marca_la_dimension_y_se_anota_en_crudos() -> None:
    """Contrato §4 regla 10 (cb41): «1» como texto en la dimensión 3 del N.º 3 (fila 4)."""
    corpus = _fixture("cb41_texto_1.xlsx")
    documento = _en_fila(corpus, 4)
    assert documento.dimensiones == (D4,)  # el N.º 3 marcaba la 3 y la 4
    assert documento.crudos == DatosCrudos(dimensiones_como_texto=(D3,))
    assert documento.estado is EstadoDocumento.EN_EL_MAPA  # le queda la dimensión 4


def test_ningun_otro_valor_marca_la_dimension_y_solo_el_texto_1_va_a_crudos() -> None:
    """Contrato §4 regla 10: 0, 2, un lógico y un texto cualquiera no marcan; «0» no se anota."""
    matriz = _base()  # N.º 2: dimensiones 1 y 2 en 1
    for dimension, valor in (("Dimensión 3", 2), ("Dimensión 4", True), ("Dimensión 5", "Sí")):
        matriz.fijar_celda(1, dimension, valor)
    matriz.fijar_celda(1, "Dimensión 6", "0")
    matriz.fijar_celda(1, "Dimensión 7", "1")
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.dimensiones == (D1, D2)
    assert documento.crudos.dimensiones_como_texto == ("Dimensión 7",)


def test_las_dimensiones_de_un_documento_van_en_el_orden_de_las_columnas() -> None:
    """Contrato §4 regla 3: $J_r$ en el orden del bloque, aunque haya una columna nueva en medio."""
    matriz = _base().agregar_columna("Dimensión nueva", antes_de="Dimensión 2")
    matriz.fijar_celda(1, "Dimensión nueva", 1)
    esquema, corpus = _leer(matriz.a_bytes())
    assert _en_fila(corpus, 3).dimensiones == (D1, "Dimensión nueva", D2)
    assert esquema.dimensiones[:3] == (D1, "Dimensión nueva", D2)


def test_una_dimension_sin_diligenciar_no_marca_y_el_documento_queda_pendiente() -> None:
    """Contrato §9: empírico con intervención y sin ninguna dimensión en 1 → pendiente."""
    matriz = _base()
    for dimension in (D1, D2):
        matriz.fijar_celda(1, dimension, None)
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.dimensiones == ()
    assert documento.intervenciones == (A, B)
    assert documento.estado is EstadoDocumento.EMPIRICO_PENDIENTE


# --------------------------------------------------------------------------------------------
# Comparación tras quitar espacios en los extremos · contrato §4 regla 6
# --------------------------------------------------------------------------------------------


def test_los_espacios_en_los_extremos_se_quitan_y_se_anotan_en_crudos() -> None:
    """Contrato §4 regla 6 (esc_3_17): «Intervención A » (N.º 2, fila 3) cuenta como la A."""
    documento = _en_fila(_fixture("esc_3_17_espacios.xlsx"), 3)
    assert documento.intervenciones == (A, B)
    assert documento.crudos == DatosCrudos(con_espacios=(Rol.INTERVENCION_PRINCIPAL,))
    assert documento.estado is EstadoDocumento.EN_EL_MAPA


def test_los_espacios_se_anotan_por_columna_en_un_orden_fijo() -> None:
    """Contrato §4 regla 6: principal, secundaria, tipo, fuente, metodología y nivel, en orden."""
    matriz = _base()
    cambios = {
        NIVEL: f" {VALOR_IMPACTO}",
        FUENTE: "Institucional  ",
        TIPO: f"{VALOR_EMPIRICO} ",
        SECUNDARIA: f" {B} ",
        PRINCIPAL: f"\t{A}",
        METODOLOGIA: " Metodología B",
    }
    for encabezado, valor in cambios.items():
        matriz.fijar_celda(1, encabezado, valor)
    documento = _en_fila(_corpus(matriz), 3)

    assert documento.crudos.con_espacios == (
        Rol.INTERVENCION_PRINCIPAL,
        Rol.INTERVENCION_SECUNDARIA,
        Rol.TIPO_DOCUMENTO,
        Rol.TIPO_FUENTE,
        Rol.METODOLOGIA,
        Rol.NIVEL_EVIDENCIA,
    )
    # Los valores quedan sin los espacios y comparan igual a los de la lista.
    assert documento.tipo_documento == VALOR_EMPIRICO
    assert documento.tipo_fuente == "Institucional"
    assert documento.metodologia == "Metodología B"
    assert documento.nivel == VALOR_IMPACTO
    assert documento.intervenciones == (A, B)
    assert documento.estado is EstadoDocumento.EN_EL_MAPA


def test_una_celda_solo_con_espacios_no_es_valor_ni_se_anota() -> None:
    """Contrato §4 regla 6 y §6: «   » es una celda vacía; no hay espacios que quitar."""
    matriz = _base()
    matriz.fijar_celda(1, FUENTE, "   ")
    documento = _en_fila(_corpus(matriz), 3)
    assert documento.tipo_fuente is None
    assert documento.crudos == DatosCrudos()


# --------------------------------------------------------------------------------------------
# Nivel · el texto o `SIN_NIVEL`
# --------------------------------------------------------------------------------------------


def test_el_nivel_vacio_y_el_no_aplica_son_sin_nivel() -> None:
    """Contrato §9 (CB-05): nivel vacío o «No aplica…» → `SIN_NIVEL`; el resto, su texto."""
    matriz = _base()
    matriz.fijar_celda(1, NIVEL, None)
    matriz.fijar_celda(2, NIVEL, VALOR_NO_APLICA_NIVEL)
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 3).nivel == SIN_NIVEL
    assert _en_fila(corpus, 4).nivel == SIN_NIVEL
    assert _en_fila(corpus, 5).nivel == "Informe de proyecto"


def test_un_nivel_que_ya_no_esta_en_la_lista_conserva_su_texto() -> None:
    """Contrato §4 regla 7: la herramienta no corrige; el nivel queda como está escrito."""
    matriz = _base()
    matriz.fijar_celda(1, NIVEL, "Nivel que no está en la lista")
    assert _en_fila(_corpus(matriz), 3).nivel == "Nivel que no está en la lista"


# --------------------------------------------------------------------------------------------
# Año · entero, vacío o no reconocido (contrato §4 regla 12)
# --------------------------------------------------------------------------------------------


def test_el_anio_entero_es_un_entero_y_el_vacio_es_none() -> None:
    """Contrato §4 regla 12: 2019 es el entero 2019; sin año, `None`; solo espacios, `None`."""
    matriz = _base()
    matriz.fijar_celda(2, ANIO, None)
    matriz.fijar_celda(3, ANIO, "  ")
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 3).anio == 2019
    assert _en_fila(corpus, 4).anio is None
    assert _en_fila(corpus, 5).anio is None


def test_el_anio_escrito_como_texto_o_con_decimales_es_no_reconocido() -> None:
    """Contrato §4 regla 12 (cb27): «s. f.» y «2019» como texto; también 2019.5 y un lógico."""
    corpus = _fixture("cb27_anio_no_numerico.xlsx")
    assert _en_fila(corpus, 7).anio == AnioNoReconocido("s. f.")
    assert _en_fila(corpus, 8).anio == AnioNoReconocido("2019")  # el texto, no el entero
    assert _en_fila(corpus, 3).anio == 2019  # el año numérico de la base sigue igual

    matriz = _base()
    matriz.fijar_celda(1, ANIO, 2019.5)
    matriz.fijar_celda(2, ANIO, True)
    otro = _corpus(matriz)
    assert _en_fila(otro, 3).anio == AnioNoReconocido("2019.5")
    assert _en_fila(otro, 4).anio == AnioNoReconocido("True")


def test_un_documento_con_anio_no_reconocido_sigue_en_r_y_en_el_mapa() -> None:
    """Contrato §4 regla 12: el documento se cuenta en $R$; el año no cambia su estado."""
    documento = _en_fila(_fixture("cb27_anio_no_numerico.xlsx"), 7)
    assert documento.estado is EstadoDocumento.EN_EL_MAPA


# --------------------------------------------------------------------------------------------
# Estado de cada documento · contrato §4 (FR-001-13)
# --------------------------------------------------------------------------------------------


def test_un_tipo_de_documento_fuera_de_su_lista_es_sin_tipo_valido() -> None:
    """Contrato §4, estado: tipo vacío o fuera de la lista → sin tipo de documento válido."""
    matriz = _base()
    matriz.fijar_celda(2, TIPO, "Tipo que no es de la lista")
    matriz.fijar_celda(3, TIPO, None)
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 4).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert _en_fila(corpus, 5).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert _en_fila(corpus, 4).tipo_documento == "Tipo que no es de la lista"  # tal cual
    assert _en_fila(corpus, 5).tipo_documento is None


def test_sin_lista_de_tipo_de_documento_todo_valor_distinto_del_ancla_es_no_empirico() -> None:
    """Contrato §4: sin lista, un valor no vacío distinto de $v_{emp}$ es no empírico."""
    matriz = _base().sin_lista(TIPO)
    matriz.fijar_celda(0, TIPO, "Otro tipo cualquiera")
    matriz.fijar_celda(4, TIPO, "   ")
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 2).estado is EstadoDocumento.NO_EMPIRICO
    assert _en_fila(corpus, 6).estado is EstadoDocumento.SIN_TIPO_VALIDO  # solo espacios = vacío
    assert _en_fila(corpus, 3).estado is EstadoDocumento.EN_EL_MAPA


def test_un_no_empirico_con_intervencion_y_dimensiones_sigue_siendo_no_empirico() -> None:
    """Contrato §4 y §9 (cb08): no entra en $E$, ni en el mapa, ni como pendiente."""
    documento = _en_fila(_fixture("cb08_no_empirico_con_intervencion.xlsx"), 7)
    assert documento.estado is EstadoDocumento.NO_EMPIRICO
    assert documento.intervenciones == (D,)  # I_r sí se calcula; el estado no depende de él
    assert documento.dimensiones == (D1,)


def test_cada_valor_ancla_empirico_es_empirico_cuando_hay_varios() -> None:
    """Contrato §4.1: con dos valores que empiezan por «Estudio empírico», ambos son empíricos."""
    matriz = _base().agregar_valor_a_lista(TIPO, "Estudio empírico (otro)")
    matriz.fijar_celda(2, TIPO, "Estudio empírico (otro)")
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 4).estado is EstadoDocumento.EN_EL_MAPA
    assert _en_fila(corpus, 3).estado is EstadoDocumento.EN_EL_MAPA


def test_un_empirico_sin_intervencion_ni_dimension_es_pendiente() -> None:
    """Contrato §5: $P = E \\setminus M$; sin $I_r$ y sin $J_r$ el estudio queda pendiente."""
    matriz = _base().agregar_fila(_documento_minimo(6, **{TIPO: VALOR_EMPIRICO}))
    documento = _en_fila(_corpus(matriz), 7)
    assert documento.intervenciones == ()
    assert documento.dimensiones == ()
    assert documento.estado is EstadoDocumento.EMPIRICO_PENDIENTE


def test_la_fila_solo_con_numero_no_tiene_tipo_valido() -> None:
    """Contrato §4: la fila sin tipo de documento queda en $R$ como sin tipo válido."""
    documento = _en_fila(_corpus(_base().agregar_fila(_documento_minimo(6))), 7)
    assert documento.estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert documento.tipo_documento is None
    assert documento.enfoque is Enfoque.SIN_DILIGENCIAR
    assert documento.nivel == SIN_NIVEL


# --------------------------------------------------------------------------------------------
# Enfoque · contrato §6 (FR-001-10)
# --------------------------------------------------------------------------------------------


def test_el_enfoque_sin_clasificar_trae_su_advertencia_con_fila_columna_y_texto() -> None:
    """Contrato §6: la advertencia de la fila 3 (N.º 2) nombra la fila, la columna y el texto."""
    corpus = _fixture("esc_1_6_enfoque.xlsx")
    por_fila = {a.ref.fila: a for a in corpus.advertencias if a.ref is not None}

    assert sorted(por_fila) == [3, 6]
    nota = por_fila[3]
    assert nota.codigo == ENFOQUE_SIN_CLASIFICAR
    assert nota.ref == RefFila("2", 3)
    assert nota.columna == ENFOQUE
    assert nota.valor == "Nota: el documento menciona el enfoque de forma general."
    assert por_fila[6].ref == RefFila("5", 6)
    assert por_fila[6].valor == "Si bien menciona el enfoque, no lo desarrolla."


def test_la_advertencia_de_la_funcion_aun_no_tiene_fila_ni_columna() -> None:
    """Arquitectura M05: `clasificar_enfoque` solo recibe el texto; `leer` le pone la fila."""
    categoria, advertencia = clasificar_enfoque("  Nota: algo.  ")
    assert categoria is Enfoque.SIN_CLASIFICAR
    assert advertencia is not None
    assert advertencia.codigo == ENFOQUE_SIN_CLASIFICAR
    assert advertencia.ref is None
    assert advertencia.columna is None
    assert advertencia.valor == "Nota: algo."


@pytest.mark.parametrize(
    ("texto", "categoria"),
    [
        ("SÍ", Enfoque.SI),
        ("sí, claro", Enfoque.SI),
        ("Sí. Con la tilde escrita aparte.", Enfoque.SI),  # «i» + acento combinado
        ("Sí", Enfoque.SI),
        ("no", Enfoque.NO),
        ("No-aplica el enfoque", Enfoque.NO),
        ("PARCIAL", Enfoque.PARCIAL),
        ("\tParcial\n", Enfoque.PARCIAL),
        ("Sin enfoque definido", Enfoque.SIN_CLASIFICAR),  # «Sin» no es «Sí»
        ("Sí/No", Enfoque.SI),
        ("¿Sí?", Enfoque.SIN_CLASIFICAR),  # no empieza por la palabra
        ("1", Enfoque.SIN_CLASIFICAR),
    ],
)
def test_la_primera_palabra_completa_decide_la_categoria(texto: str, categoria: Enfoque) -> None:
    """Contrato §6: palabra completa, sin distinguir mayúsculas; «Si» sin tilde no es Sí."""
    obtenida, advertencia = clasificar_enfoque(texto)
    assert obtenida is categoria
    assert (advertencia is not None) is (categoria is Enfoque.SIN_CLASIFICAR)


def test_el_enfoque_que_no_es_texto_se_lee_como_su_texto() -> None:
    """Contrato §6: un número en la columna de enfoque no es un prefijo válido."""
    matriz = _base()
    matriz.fijar_celda(1, ENFOQUE, 5)
    corpus = _corpus(matriz)
    documento = _en_fila(corpus, 3)
    assert documento.enfoque is Enfoque.SIN_CLASIFICAR
    assert documento.textos[Rol.ENFOQUE] == "5"
    assert [a.ref for a in corpus.advertencias] == [RefFila("2", 3)]


def test_el_enfoque_vacio_o_en_blanco_es_sin_diligenciar_y_sin_advertencia() -> None:
    """Contrato §6: celda vacía o solo espacios → sin diligenciar; no advierte."""
    matriz = _base()
    matriz.fijar_celda(1, ENFOQUE, None)
    matriz.fijar_celda(2, ENFOQUE, "   ")
    corpus = _corpus(matriz)
    assert _en_fila(corpus, 3).enfoque is Enfoque.SIN_DILIGENCIAR
    assert _en_fila(corpus, 4).enfoque is Enfoque.SIN_DILIGENCIAR
    assert _en_fila(corpus, 4).textos[Rol.ENFOQUE] is None
    assert corpus.advertencias == ()


# --------------------------------------------------------------------------------------------
# Argumentos que no corresponden y lectura sin efectos
# --------------------------------------------------------------------------------------------


def test_un_libro_sin_la_hoja_de_la_matriz_no_se_puede_leer() -> None:
    """Contrato §2: `leer` recibe el libro y el esquema que salió de él; sin hoja, `ValueError`."""
    libro = abrir(_base().a_bytes())
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema)
    otro = abrir(_base().renombrar_hoja(HOJA_MATRIZ, "Otra hoja").a_bytes())
    with pytest.raises(ValueError, match="hoja"):
        leer(otro, esquema)


def test_leer_dos_veces_da_lo_mismo() -> None:
    """NFR-000-02: la lectura no guarda estado ni altera el libro."""
    libro = abrir(_base().a_bytes())
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema)
    assert leer(libro, esquema) == leer(libro, esquema)


# --------------------------------------------------------------------------------------------
# Números decimales con valor entero (un libro puede guardar 2019.0 en lugar de 2019)
# --------------------------------------------------------------------------------------------


class _HojaConCambios:
    """La hoja de un libro real, con algunas celdas cambiadas: `(fila, columna)` → valor."""

    def __init__(self, hoja: Hoja, cambios: dict[tuple[int, int], Valor]) -> None:
        self._hoja = hoja
        self._cambios = cambios

    def dimension(self) -> tuple[int, int]:
        return self._hoja.dimension()

    def celda(self, fila: int, columna: int) -> Celda:
        if (fila, columna) in self._cambios:
            valor = self._cambios[(fila, columna)]
            return Celda(valor, None, valor)
        return self._hoja.celda(fila, columna)

    def validacion(self, columna: int) -> ListaValidacion | None:
        return self._hoja.validacion(columna)


class _LibroConCambios:
    def __init__(self, libro: Libro, cambios: dict[tuple[int, int], Valor]) -> None:
        self._libro = libro
        self._cambios = cambios

    def nombres_hojas(self) -> tuple[str, ...]:
        return self._libro.nombres_hojas()

    def hoja(self, nombre: str) -> Hoja | None:
        hoja = self._libro.hoja(nombre)
        return None if hoja is None else _HojaConCambios(hoja, self._cambios)


def test_un_decimal_con_valor_entero_es_ese_entero_en_el_n_y_en_el_anio_y_marca_con_1() -> None:
    """Contrato §3 y §4 reglas 10 y 12: 6.0 es el N.º «6», 2019.0 es 2019 y 1.0 marca."""
    libro = abrir(_base().a_bytes())
    esquema = descubrir(libro)
    assert isinstance(esquema, Esquema)
    columnas = esquema.columnas
    cambios: dict[tuple[int, int], Valor] = {
        (3, columnas[Rol.IDENTIFICADOR]): 2.0,  # el N.º 2 (fila 3)
        (3, columnas[Rol.ANIO]): 2019.0,
        (3, 14): 0.0,  # «Dimensión 3»: el 0 decimal no marca
        (3, 12): 1.0,  # «Dimensión 1»: el 1 decimal sí marca
        (4, columnas[Rol.IDENTIFICADOR]): 3.5,  # un N.º decimal no entero queda con su texto
    }
    documentos = leer(_LibroConCambios(libro, cambios), esquema).documentos
    segunda = next(d for d in documentos if d.ref.fila == 3)
    tercera = next(d for d in documentos if d.ref.fila == 4)
    assert segunda.ref == RefFila("2", 3)
    assert segunda.anio == 2019
    assert D1 in segunda.dimensiones
    assert "Dimensión 3" not in segunda.dimensiones
    assert tercera.ref == RefFila("3.5", 4)


# --------------------------------------------------------------------------------------------
# Advertencias por fila · T-001-33 (FR-001-10, FR-001-12, FR-001-13, FR-001-24; contrato §4 y §9)
# --------------------------------------------------------------------------------------------

CODIGOS_POR_FIXTURE = [
    pytest.param(
        "esc_2_1_fuera_de_lista_n3.xlsx",
        {(VALOR_FUERA_DE_LISTA, 4, PRINCIPAL)},
        id="esc_2_1",
    ),
    pytest.param(
        "cb10_fuera_de_lista.xlsx",
        {
            (VALOR_FUERA_DE_LISTA, 7, FUENTE),
            (VALOR_FUERA_DE_LISTA, 7, METODOLOGIA),
            (VALOR_FUERA_DE_LISTA, 7, NIVEL),
        },
        id="cb10",
    ),
    pytest.param(
        "cb07_misma_intervencion.xlsx",
        {(PRINCIPAL_IGUAL_SECUNDARIA, 7, PRINCIPAL)},
        id="cb07",
    ),
    pytest.param(
        "cb08_no_empirico_con_intervencion.xlsx",
        {(NO_EMPIRICO_CON_INTERVENCION, 7, PRINCIPAL)},
        id="cb08",
    ),
    pytest.param(
        "cb09_dimension_fuera_de_rango.xlsx",
        {(DIMENSION_VALOR_INVALIDO, 7, D2), (DIMENSION_VALOR_INVALIDO, 7, D3)},
        id="cb09",
    ),
    pytest.param(
        "cb13_numero_vacio_o_repetido.xlsx",
        {(NUMERO_VACIO, 7, NUMERO), (NUMERO_REPETIDO, 8, NUMERO)},
        id="cb13",
    ),
    pytest.param(
        "esc_2_13_anio_sf_n4.xlsx",
        {(ANIO_NO_RECONOCIDO, 5, ANIO)},
        id="esc_2_13",
    ),
    pytest.param(
        "esc_2_16_tipo_fuera_de_lista_n3.xlsx",
        {(TIPO_DOCUMENTO_FUERA_DE_LISTA, 4, TIPO)},
        id="esc_2_16",
    ),
    pytest.param(
        "cb41_texto_1.xlsx",
        {(DIMENSION_VALOR_INVALIDO, 4, D3)},
        id="cb41",
    ),
    pytest.param(
        "esc_3_17_espacios.xlsx",
        {(ESPACIOS_EN_LOS_EXTREMOS, 3, PRINCIPAL)},
        id="esc_3_17",
    ),
    pytest.param(
        "cb11_enfoque_sin_prefijo.xlsx",
        {(ENFOQUE_SIN_CLASIFICAR, fila, ENFOQUE) for fila in (7, 8, 9)},
        id="cb11",
    ),
]


@pytest.mark.parametrize(("nombre", "esperadas"), CODIGOS_POR_FIXTURE)
def test_cada_caso_emite_su_codigo_en_su_fila_y_su_columna(
    nombre: str, esperadas: set[tuple[str, int, str | None]]
) -> None:
    """Contrato §9: un código por caso, con fila del archivo y encabezado real; ámbito `fila`."""
    corpus = _fixture(nombre)

    obtenidas = {(a.codigo, a.ref.fila, a.columna) for a in corpus.advertencias if a.ref}
    assert obtenidas == esperadas
    assert len(corpus.advertencias) == len(esperadas)
    assert {a.ambito for a in corpus.advertencias} == {"fila"}


def test_el_valor_de_cada_advertencia_es_la_celda_tal_como_esta() -> None:
    """Contrato §4 regla 6: ninguna advertencia corrige; el valor trae sus espacios."""
    matriz = _base().fijar_celda(1, PRINCIPAL, "  Intervención Z ")
    corpus = _corpus(matriz)

    assert {(a.codigo, a.columna, a.valor) for a in corpus.advertencias} == {
        (VALOR_FUERA_DE_LISTA, PRINCIPAL, "  Intervención Z "),
        (ESPACIOS_EN_LOS_EXTREMOS, PRINCIPAL, "  Intervención Z "),
    }
    documento = _en_fila(corpus, 3)
    assert documento.intervenciones == (B,)
    assert documento.crudos.con_espacios == (Rol.INTERVENCION_PRINCIPAL,)


def test_un_valor_fuera_de_lista_se_conserva_en_el_documento_y_no_se_cuenta() -> None:
    """Contrato §4 regla 7: el valor queda como estaba; el nivel no es de ninguna categoría."""
    documento = _en_fila(_fixture("cb10_fuera_de_lista.xlsx"), 7)

    assert documento.tipo_fuente == "Fuente fuera de lista"
    assert documento.metodologia == "Metodología fuera de lista"
    assert documento.nivel == "Nivel fuera de lista"


def test_no_aplica_con_otro_texto_es_un_valor_de_la_lista_y_no_advierte() -> None:
    """Contrato §4 regla 8: lo que empieza por «No aplica» no es categoría ni fuera de lista."""
    matriz = _base().fijar_celda(1, NIVEL, "No aplica (otro texto)")
    matriz.fijar_celda(0, PRINCIPAL, "No aplica (otro texto)")
    corpus = _corpus(matriz)

    assert corpus.advertencias == ()
    assert _en_fila(corpus, 3).nivel == SIN_NIVEL
    assert _en_fila(corpus, 2).intervenciones == ()


def test_sin_lista_de_validacion_un_valor_nuevo_no_advierte() -> None:
    """Contrato §4.2: sin lista no hay contra qué comprobar; el valor es uno de los presentes."""
    matriz = _base().sin_lista(FUENTE).fijar_celda(0, FUENTE, "Fuente comunitaria")
    corpus = _corpus(matriz)

    assert corpus.advertencias == ()
    assert _en_fila(corpus, 2).tipo_fuente == "Fuente comunitaria"


def test_solo_el_1_y_el_0_numericos_y_la_celda_vacia_son_valores_validos_de_dimension() -> None:
    """Contrato §4 regla 10: 0 y vacío no advierten; el texto «0», un lógico y otro texto, sí."""
    matriz = _base()
    matriz.fijar_celda(1, D3, 0)
    matriz.fijar_celda(1, D4, "0")
    matriz.fijar_celda(1, D5, True)
    matriz.fijar_celda(1, D6, "   ")
    corpus = _corpus(matriz)

    assert {(a.columna, a.valor) for a in corpus.advertencias} == {(D4, "0"), (D5, "True")}
    assert _en_fila(corpus, 3).dimensiones == (D1, D2)
    datos = {a.columna: a.datos for a in corpus.advertencias}
    assert datos[D4] == {"dimension": D4, "numero_en_texto": True}
    assert datos[D5] == {"dimension": D5, "numero_en_texto": False}


def test_el_2_numerico_y_el_texto_no_numerico_no_son_un_numero_escrito_como_texto() -> None:
    """Contrato §4 regla 10 y CB-09: el 2 numérico y «Sí» no son un número escrito como texto."""
    corpus = _fixture("cb09_dimension_fuera_de_rango.xlsx")

    assert {a.columna: a.datos["numero_en_texto"] for a in corpus.advertencias} == {
        D2: False,
        D3: False,
    }
    (texto_1,) = _fixture("cb41_texto_1.xlsx").advertencias
    assert texto_1.datos["numero_en_texto"] is True


def test_la_advertencia_de_g_igual_h_lleva_la_intervencion_y_la_columna_de_la_secundaria() -> None:
    """Contrato §9, G = H: M10 y M08 necesitan la intervención y la otra columna."""
    (advertencia,) = _fixture("cb07_misma_intervencion.xlsx").advertencias

    assert advertencia.datos == {"intervencion": D, "columna_secundaria": SECUNDARIA}
    assert advertencia.valor == D


def test_el_no_empirico_con_intervencion_solo_en_la_secundaria_advierte_en_esa_columna() -> None:
    """Contrato §9: la advertencia va en la columna que trae la intervención de categoría."""
    matriz = _base().fijar_celda(0, SECUNDARIA, B)
    corpus = _corpus(matriz)

    (advertencia,) = corpus.advertencias
    assert advertencia.codigo == NO_EMPIRICO_CON_INTERVENCION
    assert advertencia.ref == RefFila("1", 2)
    assert advertencia.columna == SECUNDARIA
    assert advertencia.valor == B
    assert advertencia.datos == {"tipo_documento": "Documento teórico", "intervenciones": (B,)}


def test_sin_tipo_valido_con_intervencion_no_es_un_no_empirico_con_intervencion() -> None:
    """Contrato §9: la advertencia es de los documentos de tipo válido distinto del empírico."""
    sin_tipo = _corpus(_base().fijar_celda(1, TIPO, None))
    fuera = _corpus(_base().fijar_celda(1, TIPO, "Tipo fuera de lista"))

    assert sin_tipo.advertencias == ()
    assert _en_fila(sin_tipo, 3).estado is EstadoDocumento.SIN_TIPO_VALIDO
    assert [a.codigo for a in fuera.advertencias] == [TIPO_DOCUMENTO_FUERA_DE_LISTA]


def test_el_numero_repetido_advierte_en_cada_fila_posterior_con_las_anteriores() -> None:
    """Contrato §9: «2» como número y como texto es el mismo N.º; cada repetición dice dónde."""
    matriz = _base().fijar_celda(2, NUMERO, "2").fijar_celda(3, NUMERO, " 2 ")
    corpus = _corpus(matriz)

    assert [(a.codigo, a.ref, a.valor, dict(a.datos)) for a in corpus.advertencias] == [
        (NUMERO_REPETIDO, RefFila("2", 4), "2", {"filas_anteriores": (3,)}),
        (NUMERO_REPETIDO, RefFila(" 2 ", 5), " 2 ", {"filas_anteriores": (3, 4)}),
    ]


def test_el_numero_vacio_o_en_blanco_advierte_sin_valor_y_no_cuenta_como_repetido() -> None:
    """Contrato §4 regla 4: N.º vacío o con solo espacios; la advertencia no trae valor."""
    matriz = _base().fijar_celda(1, NUMERO, None).fijar_celda(2, NUMERO, "   ")
    corpus = _corpus(matriz)

    assert [(a.codigo, a.ref, a.columna, a.valor) for a in corpus.advertencias] == [
        (NUMERO_VACIO, RefFila(None, 3), NUMERO, None),
        (NUMERO_VACIO, RefFila(None, 4), NUMERO, None),
    ]


def test_las_advertencias_de_una_fila_salen_en_el_orden_de_sus_columnas() -> None:
    """Contrato §3: año, tipo de fuente, intervención, dimensión y enfoque, como en el archivo."""
    matriz = _base()
    matriz.fijar_celda(1, ENFOQUE, "Nota: algo.")
    matriz.fijar_celda(1, D1, "x")
    matriz.fijar_celda(1, PRINCIPAL, "Intervención Z")
    matriz.fijar_celda(1, FUENTE, "Fuente fuera de lista")
    matriz.fijar_celda(1, ANIO, "s. f.")
    corpus = _corpus(matriz)

    assert [a.columna for a in corpus.advertencias] == [ANIO, FUENTE, PRINCIPAL, D1, ENFOQUE]
    assert {a.ref for a in corpus.advertencias} == {RefFila("2", 3)}


def test_las_advertencias_siguen_el_orden_de_las_filas_del_archivo() -> None:
    """Contrato §4 regla 5: filas en el orden del archivo; una fila sin advertencias no aparece."""
    matriz = _base().fijar_celda(3, ANIO, "s. f.").fijar_celda(1, ANIO, "s. f.")
    corpus = _corpus(matriz)

    assert [a.ref for a in corpus.advertencias] == [RefFila("2", 3), RefFila("4", 5)]
