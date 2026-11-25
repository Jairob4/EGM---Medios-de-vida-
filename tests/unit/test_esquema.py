"""Pruebas de M04 `egm.esquema.descubrir` (T-001-23 y T-001-32).

Cubren el esquema directamente, sin M05, M07 ni M10: FR-001-01 (roles por encabezado), FR-001-03
(bloque de dimensiones), FR-001-05 (listas desde la validación), FR-001-22 (camino con lista y
valores presentes), FR-001-23 (anclas) y NFR-000-06 (ninguna categoría escrita en el código);
y, de la historia 2, la lista cerrada de errores de contrato, las advertencias de estructura y la
nota de columnas no usadas con sus códigos, ámbitos, columna, valor y datos (FR-001-02, 03, 04,
12, 21, 22 y 23). Complementan P-001-14, P-001-17, P-001-18, P-001-21, P-001-23 y P-001-29 a
P-001-37, P-001-40 y P-001-42, que además revisan el texto con `egm.textos`.

Esperados escritos a mano a partir del contrato de datos (§3, §3.1, §4, §4.1, §4.2) y del contenido
documentado de la base válida sintética (constructor M23): columnas en la base válida, desde 1:
1 N.º, 2 Referencia, 3 Año, 4 Tipo de documento, 5 País y población, 6 Tipo de fuente,
7 y 8 Intervención principal y secundaria, 9 Metodología, 10 Nivel de evidencia, 11 delimitador
inicial, 12 a 19 «Dimensión 1» a «Dimensión 8», 20 delimitador final, 21 Enfoque, 22 Hallazgos,
23 Vacío, 24 Limitaciones, 25 Aporte. Ninguno sale de ejecutar `egm.esquema`. Solo fixtures.

Los códigos de error, de advertencia y de nota son los de la lista cerrada de `egm.modelo`
(decisión de Jairo, 25-nov-2026); las advertencias de estructura no traen fila (`ref=None`).
"""

import pytest

from egm.esquema import columnas_del_bloque, descubrir
from egm.libro import abrir
from egm.modelo import (
    ANCLA_EMPIRICA_AUSENTE,
    BLOQUE_SIN_DIMENSIONES,
    CODIGOS_ADVERTENCIA_ESTRUCTURA,
    CODIGOS_ERROR_CONTRATO,
    COLUMNA_SIN_LISTA,
    COLUMNAS_NO_USADAS,
    DIMENSION_SIN_LISTA_1_0,
    ENCABEZADO_AUSENTE,
    HOJA_AUSENTE,
    LISTA_1_0_FUERA_DEL_BLOQUE,
    LISTA_OBLIGATORIA_AUSENTE,
    LISTA_SIN_NO_APLICA,
    ROL_DENTRO_DEL_BLOQUE,
    SIN_ANCLA_EVALUACION_IMPACTO,
    VARIOS_EMPIRICOS,
    Anclas,
    ErrorContrato,
    Esquema,
    FalloContrato,
    Lista,
    Nota,
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

PRINCIPAL = "Tipo de intervención (EGM)"
SECUNDARIA = "Intervención secundaria (opcional)"
NIVEL = "Nivel de evidencia"
TIPO = "Tipo de documento"
FUENTE = "Tipo de fuente"
METODOLOGIA = "Metodología"

INTERVENCIONES_BASE = tuple(f"Intervención {c}" for c in "ABCDEF")
DIMENSIONES_BASE = tuple(f"Dimensión {n}" for n in range(1, 9))
NIVELES_BASE = (VALOR_IMPACTO, "Estudio de caso", "Informe de proyecto")

COLUMNAS_BASE = {
    Rol.IDENTIFICADOR: 1,
    Rol.REFERENCIA: 2,
    Rol.ANIO: 3,
    Rol.TIPO_DOCUMENTO: 4,
    Rol.PAIS_POBLACION: 5,
    Rol.TIPO_FUENTE: 6,
    Rol.INTERVENCION_PRINCIPAL: 7,
    Rol.INTERVENCION_SECUNDARIA: 8,
    Rol.METODOLOGIA: 9,
    Rol.NIVEL_EVIDENCIA: 10,
    Rol.DELIMITADOR_INICIAL: 11,
    Rol.DELIMITADOR_FINAL: 20,
    Rol.ENFOQUE: 21,
    Rol.HALLAZGOS: 22,
    Rol.VACIO: 23,
    Rol.LIMITACIONES: 24,
    Rol.APORTE: 25,
}


def _esquema(contenido: bytes) -> Esquema:
    resultado = descubrir(abrir(contenido))
    assert isinstance(resultado, Esquema), f"se esperaba un Esquema y llegó {resultado!r}"
    return resultado


def _fixture(nombre: str) -> Esquema:
    return _esquema((carpeta_de_fixtures() / nombre).read_bytes())


def _fallo(contenido: bytes) -> FalloContrato:
    resultado = descubrir(abrir(contenido))
    assert isinstance(resultado, FalloContrato), f"se esperaba un fallo y llegó {resultado!r}"
    return resultado


def _base() -> MatrizSintetica:
    return MatrizSintetica.base_valida()


# --------------------------------------------------------------------------------------------
# Base válida · FR-001-01, FR-001-03, FR-001-05
# --------------------------------------------------------------------------------------------


def test_la_base_valida_se_descubre_completa() -> None:
    """US-001-1.8, FR-001-01/03/05: roles, dimensiones, listas y anclas de la base válida."""
    esquema = _esquema(_base().a_bytes())

    assert dict(esquema.columnas) == COLUMNAS_BASE
    assert esquema.dimensiones == DIMENSIONES_BASE
    assert esquema.intervenciones == INTERVENCIONES_BASE
    assert esquema.niveles == NIVELES_BASE
    assert esquema.tipos_documento == Lista(
        (VALOR_EMPIRICO, "Documento teórico", "Documento metodológico", "Documento normativo"),
        "validacion",
    )
    assert esquema.tipos_fuente == Lista(
        ("Académica", "Institucional", "Territorial"), "validacion"
    )
    assert esquema.metodologias == Lista(
        ("Metodología A", "Metodología B", "Metodología C"), "validacion"
    )
    assert esquema.anclas == Anclas((VALOR_EMPIRICO,), VALOR_IMPACTO)
    assert esquema.advertencias == ()
    assert esquema.notas == ()


def test_el_esquema_trae_los_17_roles_con_columnas_distintas() -> None:
    """FR-001-01: cada rol del contrato §3 tiene su columna y ninguna se repite."""
    columnas = _esquema(_base().a_bytes()).columnas
    assert set(columnas) == set(Rol)
    assert len(set(columnas.values())) == 17


def test_los_valores_no_aplica_no_son_categorias_pero_siguen_en_la_validacion() -> None:
    """Contrato §4 regla 8: el prefijo «No aplica» saca el valor de intervenciones y niveles."""
    esquema = _esquema(_base().a_bytes())
    assert VALOR_NO_APLICA_INTERVENCION not in esquema.intervenciones
    assert VALOR_NO_APLICA_NIVEL not in esquema.niveles
    assert all(not v.startswith("No aplica") for v in (*esquema.intervenciones, *esquema.niveles))


def test_la_comparacion_de_encabezados_quita_los_espacios_de_los_extremos() -> None:
    """Contrato §4 regla 6, FR-001-01: «  Año  » sigue siendo el encabezado de año."""
    matriz = _base().renombrar_encabezado("Año", "  Año ")
    assert _esquema(matriz.a_bytes()).columnas[Rol.ANIO] == 3


def test_el_orden_de_las_hojas_no_importa() -> None:
    """US-001-1.8: la hoja de la matriz se busca por nombre, no por posición."""
    matriz = _base().ordenar_hojas("Guía por tipo de documento", "EGM", HOJA_MATRIZ)
    assert dict(_esquema(matriz.a_bytes()).columnas) == COLUMNAS_BASE


# --------------------------------------------------------------------------------------------
# Orden alterado · P-001-21, FR-001-01
# --------------------------------------------------------------------------------------------


def test_las_posiciones_de_los_roles_siguen_al_encabezado_en_la_variante_reordenada() -> None:
    """US-001-1.8, FR-001-01: orden de columnas dado a mano para `esc_1_8_orden_alterado`.

    Partiendo de la base: nivel a la posición 1, año tras «Aporte al proyecto», tipo de documento
    tras «Limitaciones» y enfoque antes de «Referencia APA».
    """
    esquema = _fixture("esc_1_8_orden_alterado.xlsx")
    assert dict(esquema.columnas) == {
        Rol.NIVEL_EVIDENCIA: 1,
        Rol.IDENTIFICADOR: 2,
        Rol.ENFOQUE: 3,
        Rol.REFERENCIA: 4,
        Rol.PAIS_POBLACION: 5,
        Rol.TIPO_FUENTE: 6,
        Rol.INTERVENCION_PRINCIPAL: 7,
        Rol.INTERVENCION_SECUNDARIA: 8,
        Rol.METODOLOGIA: 9,
        Rol.DELIMITADOR_INICIAL: 10,
        Rol.DELIMITADOR_FINAL: 19,
        Rol.HALLAZGOS: 20,
        Rol.VACIO: 21,
        Rol.LIMITACIONES: 22,
        Rol.TIPO_DOCUMENTO: 23,
        Rol.APORTE: 24,
        Rol.ANIO: 25,
    }
    assert esquema.dimensiones == DIMENSIONES_BASE
    assert esquema.intervenciones == INTERVENCIONES_BASE
    assert esquema.niveles == NIVELES_BASE


# --------------------------------------------------------------------------------------------
# Bloque de dimensiones · P-001-18, FR-001-03
# --------------------------------------------------------------------------------------------


def test_las_columnas_agregadas_al_bloque_son_dimensiones_en_su_posicion() -> None:
    """US-001-1.4, FR-001-03: la nueva entre 4 y 5 y la otra al final; las dos son dimensión."""
    esquema = _fixture("cb37_dimension_agregada.xlsx")
    assert esquema.dimensiones == (
        *DIMENSIONES_BASE[:4],
        "Dimensión nueva",
        *DIMENSIONES_BASE[4:],
        "Dimensión sin lista",
    )
    assert esquema.columnas[Rol.DELIMITADOR_FINAL] == 22  # la base lo tenía en 20; +2 columnas


def test_una_columna_ajena_fuera_del_bloque_no_es_dimension_ni_rol() -> None:
    """Contrato §3 (columna de otro encabezado fuera del bloque se ignora), FR-001-03."""
    for nombre in ("cb18_columna_observaciones.xlsx", "cb19_columna_1_0_fuera.xlsx"):
        esquema = _fixture(nombre)
        assert esquema.dimensiones == DIMENSIONES_BASE, nombre
        assert dict(esquema.columnas) == COLUMNAS_BASE, nombre  # la ajena va al final (col. 26)


def test_el_bloque_es_lo_que_hay_entre_los_delimitadores_y_cambia_con_ellos() -> None:
    """Contrato §3.1: ni las dimensiones ni su orden son fijos; salen de entre los delimitadores."""
    matriz = _base().mover_columna("Dimensión 8", antes_de="Dimensión 1")
    esquema = _esquema(matriz.a_bytes())
    assert esquema.dimensiones == ("Dimensión 8", *DIMENSIONES_BASE[:7])


def test_sin_columnas_entre_los_delimitadores_no_hay_dimensiones() -> None:
    """Contrato §3.1: bloque vacío o invertido da un esquema sin dimensiones."""
    assert _fixture("cb38_bloque_vacio.xlsx").dimensiones == ()
    assert _fixture("cb38_bloque_invertido.xlsx").dimensiones == ()


def test_un_encabezado_de_rol_dentro_del_bloque_conserva_su_rol_y_no_es_dimension() -> None:
    """Contrato §3.1: «Metodología» tras «Dimensión 4» se toma con su rol, no como dimensión."""
    esquema = _fixture("cb39_rol_en_bloque.xlsx")
    assert esquema.dimensiones == DIMENSIONES_BASE
    assert esquema.columnas[Rol.METODOLOGIA] == 15  # tras las dimensiones 1 a 4 (columnas 11 a 14)
    assert esquema.columnas[Rol.DELIMITADOR_FINAL] == 20


# --------------------------------------------------------------------------------------------
# Categorías del archivo · P-001-14, P-001-17, P-001-23, FR-001-05, NFR-000-06
# --------------------------------------------------------------------------------------------


def test_las_intervenciones_y_niveles_agregados_van_donde_estan_en_la_lista() -> None:
    """US-001-1.3, FR-001-05: «Intervención G» y el nivel nuevo, antes del valor «No aplica…»."""
    esquema = _fixture("cb36_intervencion_nivel_agregados.xlsx")
    assert esquema.intervenciones == (*INTERVENCIONES_BASE, "Intervención G")
    assert esquema.niveles == (*NIVELES_BASE, "Estudio cuasiexperimental")


def test_las_categorias_retiradas_de_las_listas_desaparecen_del_esquema() -> None:
    """SC-001-05 (cb40): sin «Intervención C» ni «Informe de proyecto» ni «Dimensión 8»."""
    esquema = _fixture("cb40_retiradas.xlsx")
    assert esquema.intervenciones == ("Intervención A", "Intervención B", *INTERVENCIONES_BASE[3:])
    assert esquema.niveles == NIVELES_BASE[:2]
    assert esquema.dimensiones == DIMENSIONES_BASE[:7]


def test_las_categorias_y_la_dimension_agregadas_y_retiradas_de_sc000_06() -> None:
    """SC-000-06: cada archivo muestra las categorías y dimensiones que trae."""
    agregadas = _fixture("sc000_06_agregadas.xlsx")
    assert agregadas.intervenciones == (*INTERVENCIONES_BASE, "Intervención G")
    assert agregadas.dimensiones == (*DIMENSIONES_BASE, "Dimensión 9")
    assert agregadas.niveles == (*NIVELES_BASE, "Estudio cuasiexperimental")

    retiradas = _fixture("sc000_06_retiradas.xlsx")
    assert retiradas.intervenciones == INTERVENCIONES_BASE[:5]
    assert retiradas.dimensiones == DIMENSIONES_BASE[:7]
    assert retiradas.niveles == NIVELES_BASE[:2]


def test_las_categorias_renombradas_se_toman_con_su_nombre_nuevo() -> None:
    """SC-000-06: «Intervención Alfa» y «Estudio monográfico» salen de las listas de su archivo."""
    esquema = _fixture("sc000_06_renombradas.xlsx")
    assert esquema.intervenciones == ("Intervención Alfa", *INTERVENCIONES_BASE[1:])
    assert esquema.niveles == (VALOR_IMPACTO, "Estudio monográfico", "Informe de proyecto")


def test_las_intervenciones_de_solo_secundaria_van_al_final_en_su_orden() -> None:
    """Contrato §4 regla 3: la principal sin «F» y la secundaria con «G» antes de «A»."""
    matriz = _base()
    matriz.quitar_valor_de_lista(PRINCIPAL, "Intervención F")
    matriz.quitar_valor_de_lista(PRINCIPAL, "Intervención B")
    matriz.agregar_valor_a_lista(SECUNDARIA, "Intervención G", posicion=1)
    esquema = _esquema(matriz.a_bytes())
    # Principal: A, C, D, E; solo en la secundaria, en el orden de su lista: G, B, F.
    assert esquema.intervenciones == (
        "Intervención A",
        "Intervención C",
        "Intervención D",
        "Intervención E",
        "Intervención G",
        "Intervención B",
        "Intervención F",
    )


def test_una_intervencion_en_ambas_listas_aparece_una_vez() -> None:
    """Contrato §4 regla 3: la intervención que está en las dos listas se cuenta una vez."""
    esquema = _esquema(_base().a_bytes())
    assert esquema.intervenciones == INTERVENCIONES_BASE  # las seis están en ambas listas


def test_el_valor_no_aplica_de_la_secundaria_tampoco_es_categoria() -> None:
    """Contrato §4 regla 8: sin él en la principal, la secundaria no lo agrega como categoría."""
    matriz = _base().quitar_valor_de_lista(PRINCIPAL, VALOR_NO_APLICA_INTERVENCION)
    assert _esquema(matriz.a_bytes()).intervenciones == INTERVENCIONES_BASE


def test_sin_valor_no_aplica_en_la_lista_todos_los_valores_son_categorias() -> None:
    """Contrato §4.1 (cb22): nivel sin «No aplica…»: todos sus valores son niveles."""
    esquema = _fixture("cb22_sin_no_aplica.xlsx")
    assert esquema.niveles == NIVELES_BASE


def test_los_espacios_de_los_extremos_de_un_valor_de_lista_no_cuentan() -> None:
    """Contrato §4 regla 6: la lista con «Estudio de caso » da la categoría sin el espacio."""
    matriz = _base().renombrar_valor_de_lista(NIVEL, "Estudio de caso", "Estudio de caso ")
    assert _esquema(matriz.a_bytes()).niveles == NIVELES_BASE


@pytest.mark.parametrize("modo", ["escrita", "rango", "x14"])
def test_la_lista_se_lee_de_la_validacion_en_sus_tres_formas(modo: str) -> None:
    """FR-001-05, contrato §4 regla 2: lista escrita, por rango o guardada como extensión."""
    matriz = _base().con_lista(PRINCIPAL, [*INTERVENCIONES_BASE, "Intervención G"], modo=modo)  # type: ignore[arg-type]
    assert _esquema(matriz.a_bytes()).intervenciones == (*INTERVENCIONES_BASE, "Intervención G")


# --------------------------------------------------------------------------------------------
# Columnas sin lista · FR-001-22 (valores presentes)
# --------------------------------------------------------------------------------------------


def test_fuente_y_metodologia_sin_lista_usan_los_valores_presentes() -> None:
    """Contrato §4.2: sin lista, la lista son los valores de las filas, en su orden de aparición."""
    matriz = _base().sin_lista(FUENTE).sin_lista(METODOLOGIA)
    esquema = _esquema(matriz.a_bytes())
    # Fuentes por documento: Académica, Institucional, Académica, Territorial, Institucional.
    assert esquema.tipos_fuente == Lista(("Académica", "Institucional", "Territorial"), "presentes")
    # Metodología: «Metodología B» en los N.º 1 a 4; el N.º 5 la deja vacía.
    assert esquema.metodologias == Lista(("Metodología B",), "presentes")
    assert esquema.tipos_documento.origen == "validacion"


def test_tipo_de_documento_sin_lista_busca_el_ancla_en_los_valores_presentes() -> None:
    """Contrato §4.1: sin lista de tipo, el ancla empírica se busca en los valores presentes."""
    esquema = _fixture("cb26_tipo_sin_lista.xlsx")
    # Tipos por documento: teórico, empírico (tres), normativo y, en el N.º 6 que agrega el
    # fixture, «Marco teórico».
    assert esquema.tipos_documento == Lista(
        ("Documento teórico", VALOR_EMPIRICO, "Documento normativo", "Marco teórico"), "presentes"
    )
    assert esquema.anclas.empiricos == (VALOR_EMPIRICO,)


# --------------------------------------------------------------------------------------------
# Anclas · FR-001-23 (§4.1)
# --------------------------------------------------------------------------------------------


def test_varios_valores_que_empiezan_por_estudio_empirico_son_todos_ancla() -> None:
    """Contrato §4.1 (cb23): se toman todos, en el orden de la lista."""
    esquema = _fixture("cb23_varios_empiricos.xlsx")
    assert esquema.anclas.empiricos == (VALOR_EMPIRICO, "Estudio empírico (modalidad ampliada)")


def test_sin_ancla_de_evaluacion_de_impacto_el_esquema_se_arma_sin_ella() -> None:
    """Contrato §4.1 (cb21): la ancla de impacto es `None` y lo demás se descubre igual."""
    esquema = _fixture("cb21_sin_ancla_ie.xlsx")
    assert esquema.anclas.evaluacion_impacto is None
    assert esquema.niveles == ("Evaluación de resultados", "Estudio de caso", "Informe de proyecto")


# --------------------------------------------------------------------------------------------
# Lo que no se reconoce: `FalloContrato` (primeras pruebas; los errores completos, más abajo)
# --------------------------------------------------------------------------------------------


def test_sin_la_hoja_de_la_matriz_se_devuelve_un_fallo_que_la_nombra() -> None:
    """Contrato §2: la hoja de la matriz es obligatoria."""
    fallo = _fallo((carpeta_de_fixtures() / "cb15_sin_hoja_matriz.xlsx").read_bytes())
    assert len(fallo.errores) == 1
    assert fallo.errores[0].esperado == (HOJA_MATRIZ,)
    assert HOJA_MATRIZ not in fallo.errores[0].encontrado


def test_un_encabezado_de_rol_renombrado_o_ausente_da_un_fallo_que_lo_nombra() -> None:
    """Contrato §3: renombrar equivale a que falte."""
    ausente = _fallo(_base().quitar_columna(NIVEL).a_bytes())
    assert ausente.errores[0].esperado == (NIVEL,)
    renombrado = _fallo(_base().renombrar_encabezado("Año", "Anio").a_bytes())
    assert renombrado.errores[0].esperado == ("Año",)
    assert "Anio" in renombrado.errores[0].encontrado


def test_sin_un_delimitador_del_bloque_se_devuelve_un_fallo() -> None:
    """Contrato §3.1: falta uno de los dos delimitadores."""
    fallo = _fallo(_base().quitar_columna(ENCABEZADO_DELIMITADOR_FINAL).a_bytes())
    assert fallo.errores[0].esperado == (ENCABEZADO_DELIMITADOR_FINAL,)


@pytest.mark.parametrize(
    ("nombre", "columna"),
    [
        ("cb24_principal_sin_lista.xlsx", PRINCIPAL),
        ("cb24_secundaria_sin_lista.xlsx", SECUNDARIA),
        ("cb24_nivel_sin_lista.xlsx", NIVEL),
    ],
)
def test_una_columna_de_intervencion_o_nivel_sin_lista_da_un_fallo_que_la_nombra(
    nombre: str, columna: str
) -> None:
    """Contrato §4.2: intervención principal, secundaria o nivel sin lista."""
    fallo = _fallo((carpeta_de_fixtures() / nombre).read_bytes())
    assert fallo.errores[0].esperado == (columna,)


def test_sin_ancla_de_estudio_empirico_el_fallo_da_lo_esperado_y_lo_encontrado() -> None:
    """Contrato §4.1 (cb20): se nombra el prefijo esperado y los valores de la lista."""
    fallo = _fallo((carpeta_de_fixtures() / "cb20_sin_ancla_empirico.xlsx").read_bytes())
    assert fallo.errores[0].esperado == ("Estudio empírico",)
    assert fallo.errores[0].encontrado == (
        "Estudio de campo",
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
    )


# --------------------------------------------------------------------------------------------
# `columnas_del_bloque` · FR-001-03 (contrato §3.1): la regla del bloque, una sola vez
# --------------------------------------------------------------------------------------------

_ENCABEZADOS_DE_LA_BASE = _base().encabezados()


def test_columnas_del_bloque_da_nombre_y_columna_de_cada_dimension_en_orden() -> None:
    """FR-001-03: las ocho dimensiones de la base válida están en las columnas 12 a 19."""
    esperado = tuple((f"Dimensión {n}", 11 + n) for n in range(1, 9))
    assert columnas_del_bloque(_ENCABEZADOS_DE_LA_BASE, COLUMNAS_BASE) == esperado


def test_columnas_del_bloque_coincide_con_las_dimensiones_del_esquema() -> None:
    """FR-001-03: `descubrir` y `columnas_del_bloque` usan la misma regla."""
    matriz = _base().agregar_columna("Dimensión nueva", antes_de="Dimensión 5")
    esquema = _esquema(matriz.a_bytes())
    columnas = columnas_del_bloque(matriz.encabezados(), esquema.columnas)
    assert tuple(nombre for nombre, _ in columnas) == esquema.dimensiones
    assert dict(columnas)["Dimensión nueva"] == 16  # la columna 16: después de las cuatro primeras


def test_columnas_del_bloque_omite_columnas_sin_encabezado() -> None:
    """Contrato §3.1: solo cuentan las columnas del bloque con encabezado."""
    encabezados = [None] * 5
    encabezados[0], encabezados[4] = "Inicio", "Fin"
    encabezados[1], encabezados[3] = "Dimensión A", "Dimensión B"
    columnas = {Rol.DELIMITADOR_INICIAL: 1, Rol.DELIMITADOR_FINAL: 5}
    assert columnas_del_bloque(encabezados, columnas) == (("Dimensión A", 2), ("Dimensión B", 4))


def test_columnas_del_bloque_no_toma_como_dimension_un_encabezado_de_rol() -> None:
    """Contrato §3.1: «Año» dentro del bloque conserva su rol y no es dimensión."""
    encabezados: list[str | None] = ["Inicio", "Dimensión A", "Año", "Dimensión B", "Fin"]
    columnas = {Rol.DELIMITADOR_INICIAL: 1, Rol.ANIO: 3, Rol.DELIMITADOR_FINAL: 5}
    assert columnas_del_bloque(encabezados, columnas) == (("Dimensión A", 2), ("Dimensión B", 4))


@pytest.mark.parametrize(
    ("inicio", "fin"),
    [(5, 2), (3, 3), (3, 4)],
    ids=["final_antes_del_inicial", "mismo_lugar", "pegados"],
)
def test_columnas_del_bloque_sin_columnas_entre_los_delimitadores_es_vacio(
    inicio: int, fin: int
) -> None:
    """Contrato §3.1: delimitador final antes del inicial o sin columnas entre ellos."""
    encabezados: list[str | None] = ["Dimensión A", "Dimensión B", "Inicio", "Fin", "Dimensión C"]
    columnas = {Rol.DELIMITADOR_INICIAL: inicio, Rol.DELIMITADOR_FINAL: fin}
    assert columnas_del_bloque(encabezados, columnas) == ()


# --------------------------------------------------------------------------------------------
# Errores de contrato (T-001-32) · FR-001-02, FR-001-03, FR-001-22, FR-001-23
# --------------------------------------------------------------------------------------------

ENCABEZADOS_DE_LA_BASE_SIN_NIVEL = tuple(e for e in _base().encabezados() if e != NIVEL)
OTRO_EMPIRICO = "Estudio empírico (modalidad ampliada)"
MARCA = "Marca de revisión"


def test_sin_la_hoja_de_la_matriz_el_error_es_hoja_ausente_con_las_hojas_encontradas() -> None:
    """Contrato §2, §9: un solo error; lo esperado es la hoja y lo hallado, las otras."""
    fallo = _fallo((carpeta_de_fixtures() / "cb15_sin_hoja_matriz.xlsx").read_bytes())

    assert len(fallo.errores) == 1
    error = fallo.errores[0]
    assert error.codigo == HOJA_AUSENTE
    assert error.esperado == (HOJA_MATRIZ,)
    assert "EGM" in error.encontrado
    assert HOJA_MATRIZ not in error.encontrado


def test_sin_encabezado_de_nivel_el_error_es_encabezado_ausente_con_los_encabezados_hallados() -> (
    None
):
    """Contrato §3, FR-001-02 (cb14): se nombra el que falta y los encabezados de la fila 1."""
    fallo = _fallo(_base().quitar_columna(NIVEL).a_bytes())

    assert fallo.errores == (
        ErrorContrato(ENCABEZADO_AUSENTE, (NIVEL,), ENCABEZADOS_DE_LA_BASE_SIN_NIVEL),
    )


def test_un_encabezado_renombrado_equivale_a_que_falte_y_el_nuevo_se_ve_en_lo_encontrado() -> None:
    """Contrato §3: «Anio» en lugar de «Año»; el error no trae ningún valor de las filas."""
    fallo = _fallo(_base().renombrar_encabezado("Año", "Anio").a_bytes())

    (error,) = fallo.errores
    assert error.codigo == ENCABEZADO_AUSENTE
    assert error.esperado == ("Año",)
    assert set(error.encontrado) == (set(_base().encabezados()) - {"Año"}) | {"Anio"}


def test_sin_los_dos_delimitadores_un_solo_error_los_nombra_en_el_orden_del_contrato() -> None:
    """Contrato §3.1, FR-001-03: el delimitador es un encabezado de rol; un error, dos nombres."""
    matriz = _base().quitar_columna(ENCABEZADO_DELIMITADOR_FINAL)
    matriz.quitar_columna(ENCABEZADO_DELIMITADOR_INICIAL)
    fallo = _fallo(matriz.a_bytes())

    (error,) = fallo.errores
    assert error.codigo == ENCABEZADO_AUSENTE
    assert error.esperado == (ENCABEZADO_DELIMITADOR_INICIAL, ENCABEZADO_DELIMITADOR_FINAL)


def test_dos_columnas_obligatorias_sin_lista_van_en_un_error_en_el_orden_del_contrato() -> None:
    """Contrato §4.2, FR-001-22: principal y secundaria sin lista, en un error y en orden."""
    fallo = _fallo(_base().sin_lista(SECUNDARIA).sin_lista(PRINCIPAL).a_bytes())

    assert fallo.errores == (ErrorContrato(LISTA_OBLIGATORIA_AUSENTE, (PRINCIPAL, SECUNDARIA), ()),)


def test_sin_ancla_empirica_el_error_trae_el_prefijo_y_los_valores_de_la_lista() -> None:
    """Contrato §4.1, FR-001-23 (cb20): esperado, el prefijo; hallados, los de la lista."""
    fallo = _fallo(
        _base().renombrar_valor_de_lista(TIPO, VALOR_EMPIRICO, "Estudio de campo").a_bytes()
    )

    assert fallo.errores == (
        ErrorContrato(
            ANCLA_EMPIRICA_AUSENTE,
            ("Estudio empírico",),
            (
                "Estudio de campo",
                "Documento teórico",
                "Documento metodológico",
                "Documento normativo",
            ),
        ),
    )


def test_sin_lista_de_tipo_el_ancla_se_busca_en_los_valores_presentes_y_el_error_los_trae() -> None:
    """Contrato §4.1: tipo sin lista y sin «Estudio empírico…» en las filas; van los presentes."""
    matriz = _base().sin_lista(TIPO).reemplazar_valor(TIPO, VALOR_EMPIRICO, "Estudio de campo")
    fallo = _fallo(matriz.a_bytes())

    assert fallo.errores == (
        ErrorContrato(
            ANCLA_EMPIRICA_AUSENTE,
            ("Estudio empírico",),
            ("Documento teórico", "Estudio de campo", "Documento normativo"),
        ),
    )


def test_varios_errores_van_juntos_en_el_orden_de_la_lista_y_sin_repetir() -> None:
    """Contrato §3, §4.1, §4.2: encabezado, lista obligatoria y ancla, en un `FalloContrato`."""
    matriz = _base().quitar_columna(NIVEL).sin_lista(PRINCIPAL)
    matriz.renombrar_valor_de_lista(TIPO, VALOR_EMPIRICO, "Estudio de campo")
    fallo = _fallo(matriz.a_bytes())

    assert [e.codigo for e in fallo.errores] == [
        ENCABEZADO_AUSENTE,
        LISTA_OBLIGATORIA_AUSENTE,
        ANCLA_EMPIRICA_AUSENTE,
    ]
    # El nivel no tiene columna: no se le exige lista; solo la principal.
    assert fallo.errores[0].esperado == (NIVEL,)
    assert fallo.errores[1].esperado == (PRINCIPAL,)
    codigos = [e.codigo for e in fallo.errores]
    assert len(codigos) == len(set(codigos))


def test_el_fallo_no_trae_esquema_y_sus_codigos_son_de_la_lista_cerrada() -> None:
    """Decisión de Jairo, 25-nov-2026: lista cerrada; ningún esquema parcial."""
    contenidos = [
        (carpeta_de_fixtures() / "cb15_sin_hoja_matriz.xlsx").read_bytes(),
        _base().quitar_columna(NIVEL).a_bytes(),
        _base().sin_lista(NIVEL).a_bytes(),
        _base().renombrar_valor_de_lista(TIPO, VALOR_EMPIRICO, "Estudio de campo").a_bytes(),
    ]
    for contenido in contenidos:
        resultado = descubrir(abrir(contenido))
        assert isinstance(resultado, FalloContrato)
        assert not isinstance(resultado, Esquema)
        assert {e.codigo for e in resultado.errores} <= set(CODIGOS_ERROR_CONTRATO)
        assert all(e.esperado for e in resultado.errores)


# --------------------------------------------------------------------------------------------
# Advertencias de estructura (T-001-32) · FR-001-04, FR-001-12, FR-001-22, FR-001-23
# --------------------------------------------------------------------------------------------


def _como_tuplas(
    esquema: Esquema,
) -> list[tuple[str, str, str | None, str | None, dict[str, object]]]:
    """Código, ámbito, columna, valor y datos de cada advertencia de estructura."""
    return [(a.codigo, a.ambito, a.columna, a.valor, dict(a.datos)) for a in esquema.advertencias]


def test_la_base_valida_no_trae_advertencias_ni_notas() -> None:
    """Contrato §3.1: sin casos borde, el esquema sale limpio."""
    esquema = _esquema(_base().a_bytes())
    assert esquema.advertencias == ()
    assert esquema.notas == ()


def test_columna_con_lista_1_0_fuera_del_bloque_es_advertencia_y_no_nota() -> None:
    """Contrato §3.1, FR-001-04 (cb19): sin fila, ámbito columna; la columna no va en la nota."""
    esquema = _fixture("cb19_columna_1_0_fuera.xlsx")

    assert _como_tuplas(esquema) == [(LISTA_1_0_FUERA_DEL_BLOQUE, "columna", MARCA, None, {})]
    assert esquema.advertencias[0].ref is None
    assert esquema.notas == ()


def test_la_lista_1_0_se_reconoce_en_cualquier_orden() -> None:
    """Contrato §3.1: «0,1» es tan lista `1,0` como «1,0»."""
    esquema = _esquema(_base().agregar_columna(MARCA, lista=["0", "1"]).a_bytes())
    assert [a.codigo for a in esquema.advertencias] == [LISTA_1_0_FUERA_DEL_BLOQUE]
    assert esquema.notas == ()


def test_una_lista_que_no_es_1_0_fuera_del_bloque_no_es_advertencia_y_va_en_la_nota() -> None:
    """Contrato §3, FR-001-21: solo la lista `1,0` vuelve advertencia a la columna ajena."""
    esquema = _esquema(_base().agregar_columna("Opinión", lista=["Sí", "No"]).a_bytes())
    assert esquema.advertencias == ()
    assert esquema.notas == (Nota(COLUMNAS_NO_USADAS, {"columnas": ("Opinión",)}),)


def test_columna_del_bloque_sin_lista_1_0_es_advertencia_y_la_que_la_tiene_no() -> None:
    """Contrato §3.1, FR-001-04 (cb37): «Dimensión sin lista» advierte y sigue siendo dimensión."""
    esquema = _fixture("cb37_dimension_agregada.xlsx")

    assert _como_tuplas(esquema) == [
        (DIMENSION_SIN_LISTA_1_0, "columna", "Dimensión sin lista", None, {})
    ]
    assert "Dimensión sin lista" in esquema.dimensiones
    assert esquema.notas == ()


def test_columna_del_bloque_con_otra_lista_tambien_advierte() -> None:
    """Contrato §3.1: una lista distinta de `1,0` no es la lista de la dimensión."""
    matriz = _base().agregar_columna(
        "Dimensión Sí/No",
        rol="dimension",
        antes_de=ENCABEZADO_DELIMITADOR_FINAL,
        lista=["Sí", "No"],
    )
    esquema = _esquema(matriz.a_bytes())
    assert [(a.codigo, a.columna) for a in esquema.advertencias] == [
        (DIMENSION_SIN_LISTA_1_0, "Dimensión Sí/No")
    ]


def test_bloque_vacio_es_una_advertencia_de_hoja_con_motivo_vacio() -> None:
    """Contrato §3.1, §9 (cb38): sin columnas entre los delimitadores; nada más."""
    esquema = _fixture("cb38_bloque_vacio.xlsx")

    assert _como_tuplas(esquema) == [
        (BLOQUE_SIN_DIMENSIONES, "hoja", None, None, {"motivo": "vacio"})
    ]
    assert esquema.notas == ()


def test_bloque_invertido_advierte_el_bloque_y_cada_columna_con_lista_1_0_que_quedo_fuera() -> None:
    """Contrato §3.1 (cb38): el bloque invertido no tiene dimensiones y las ocho columnas con
    lista `1,0` quedan fuera de él; cada una advierte, en el orden del archivo."""
    esquema = _fixture("cb38_bloque_invertido.xlsx")

    assert _como_tuplas(esquema) == [
        (BLOQUE_SIN_DIMENSIONES, "hoja", None, None, {"motivo": "invertido"}),
        *((LISTA_1_0_FUERA_DEL_BLOQUE, "columna", d, None, {}) for d in DIMENSIONES_BASE),
    ]
    assert esquema.notas == ()


def test_bloque_con_solo_columnas_de_rol_no_tiene_dimensiones_y_advierte_las_dos_cosas() -> None:
    """Contrato §3.1: «Metodología» es lo único entre los delimitadores: rol dentro y vacío."""
    matriz = _base()
    for dimension in DIMENSIONES_BASE:
        matriz.quitar_columna(dimension)
    matriz.mover_columna(METODOLOGIA, despues_de=ENCABEZADO_DELIMITADOR_INICIAL)
    esquema = _esquema(matriz.a_bytes())

    assert esquema.dimensiones == ()
    assert [(a.codigo, a.columna) for a in esquema.advertencias] == [
        (BLOQUE_SIN_DIMENSIONES, None),
        (ROL_DENTRO_DEL_BLOQUE, METODOLOGIA),
    ]


def test_rol_dentro_del_bloque_es_una_advertencia_de_columna_y_no_cambia_las_dimensiones() -> None:
    """Contrato §3.1, §9 (cb39): «Metodología» dentro del bloque se toma con su rol."""
    esquema = _fixture("cb39_rol_en_bloque.xlsx")

    assert _como_tuplas(esquema) == [(ROL_DENTRO_DEL_BLOQUE, "columna", METODOLOGIA, None, {})]
    assert esquema.notas == ()


def test_un_rol_fuera_del_bloque_no_advierte() -> None:
    """Contrato §3.1: solo el encabezado de rol que cae entre los delimitadores advierte."""
    esquema = _esquema(_base().mover_columna(METODOLOGIA, posicion=1).a_bytes())
    assert esquema.advertencias == ()


def test_lista_de_nivel_sin_no_aplica_advierte_con_la_columna_y_el_prefijo() -> None:
    """Contrato §4.1 (cb22): la columna es la de nivel y el valor, el prefijo buscado."""
    esquema = _fixture("cb22_sin_no_aplica.xlsx")

    assert _como_tuplas(esquema) == [(LISTA_SIN_NO_APLICA, "columna", NIVEL, "No aplica", {})]


def test_lista_de_la_principal_sin_no_aplica_tambien_advierte() -> None:
    """Contrato §4.1: la intervención principal trae su valor «No aplica…»; sin él, advertencia."""
    esquema = _esquema(
        _base().quitar_valor_de_lista(PRINCIPAL, VALOR_NO_APLICA_INTERVENCION).a_bytes()
    )
    assert _como_tuplas(esquema) == [(LISTA_SIN_NO_APLICA, "columna", PRINCIPAL, "No aplica", {})]


def test_la_secundaria_sin_no_aplica_no_advierte() -> None:
    """Contrato §4.1: la secundaria es opcional y su lista no lleva «No aplica…»; no se exige."""
    esquema = _esquema(
        _base().quitar_valor_de_lista(SECUNDARIA, VALOR_NO_APLICA_INTERVENCION).a_bytes()
    )
    assert esquema.advertencias == ()


def test_varios_empiricos_advierte_con_la_columna_y_todos_los_valores() -> None:
    """Contrato §4.1 (cb23): los valores van en `datos`, en el orden de la lista."""
    esquema = _fixture("cb23_varios_empiricos.xlsx")

    assert _como_tuplas(esquema) == [
        (VARIOS_EMPIRICOS, "columna", TIPO, None, {"valores": (VALOR_EMPIRICO, OTRO_EMPIRICO)})
    ]


def test_sin_ancla_de_evaluacion_de_impacto_advierte_con_el_valor_esperado_y_los_niveles() -> None:
    """Contrato §4.1 (cb21): el valor es el que falta; `niveles`, los de la lista."""
    esquema = _fixture("cb21_sin_ancla_ie.xlsx")

    assert _como_tuplas(esquema) == [
        (
            SIN_ANCLA_EVALUACION_IMPACTO,
            "columna",
            NIVEL,
            VALOR_IMPACTO,
            {"niveles": ("Evaluación de resultados", "Estudio de caso", "Informe de proyecto")},
        )
    ]


@pytest.mark.parametrize(
    ("nombre", "columna", "presentes"),
    [
        ("cb25_fuente_sin_lista.xlsx", FUENTE, ("Académica", "Institucional", "Territorial")),
        ("cb25_metodologia_sin_lista.xlsx", METODOLOGIA, ("Metodología B",)),
    ],
    ids=["fuente", "metodologia"],
)
def test_columna_sin_lista_advierte_con_los_valores_presentes(
    nombre: str, columna: str, presentes: tuple[str, ...]
) -> None:
    """Contrato §4.2 (cb25): la advertencia nombra la columna y trae los valores presentes."""
    esquema = _fixture(nombre)
    assert _como_tuplas(esquema) == [
        (COLUMNA_SIN_LISTA, "columna", columna, None, {"valores": presentes})
    ]


def test_tipo_de_documento_sin_lista_advierte_con_sus_valores_presentes() -> None:
    """Contrato §4.2 (esc. 2.15): tipo sin lista; los valores van en el orden de aparición."""
    esquema = _fixture("esc_2_15_tipo_sin_lista_cuatro_docs.xlsx")
    assert _como_tuplas(esquema) == [
        (
            COLUMNA_SIN_LISTA,
            "columna",
            TIPO,
            None,
            {"valores": (VALOR_EMPIRICO, "Marco teórico", "Estudio empirico")},
        )
    ]


def test_tres_columnas_sin_lista_advierten_cada_una_en_el_orden_del_archivo() -> None:
    """Contrato §4.2: tipo de documento (col. 4), de fuente (6) y metodología (9), en ese orden."""
    matriz = _base().sin_lista(METODOLOGIA).sin_lista(TIPO).sin_lista(FUENTE)
    esquema = _esquema(matriz.a_bytes())
    assert [a.columna for a in esquema.advertencias] == [TIPO, FUENTE, METODOLOGIA]
    assert {a.codigo for a in esquema.advertencias} == {COLUMNA_SIN_LISTA}


def test_las_advertencias_van_en_el_orden_de_los_codigos_y_las_de_estructura_no_traen_fila() -> (
    None
):
    """Contrato §3.1, §4.1, §4.2: orden estable; ámbito hoja o columna; sin `ref`; nota única."""
    matriz = _base()
    matriz.mover_columna(METODOLOGIA, despues_de="Dimensión 4")
    matriz.agregar_columna(MARCA, lista=["1", "0"])
    matriz.agregar_columna("Observaciones", valores=["Nota"])
    matriz.agregar_columna(
        "Dimensión sin lista", rol="dimension", antes_de=ENCABEZADO_DELIMITADOR_FINAL
    )
    matriz.quitar_valor_de_lista(NIVEL, VALOR_NO_APLICA_NIVEL)
    matriz.renombrar_valor_de_lista(NIVEL, VALOR_IMPACTO, "Evaluación de resultados")
    matriz.agregar_valor_a_lista(TIPO, OTRO_EMPIRICO)
    matriz.sin_lista(FUENTE)
    esquema = _esquema(matriz.a_bytes())

    assert [(a.codigo, a.columna) for a in esquema.advertencias] == [
        (ROL_DENTRO_DEL_BLOQUE, METODOLOGIA),
        (LISTA_1_0_FUERA_DEL_BLOQUE, MARCA),
        (DIMENSION_SIN_LISTA_1_0, "Dimensión sin lista"),
        (LISTA_SIN_NO_APLICA, NIVEL),
        (VARIOS_EMPIRICOS, TIPO),
        (SIN_ANCLA_EVALUACION_IMPACTO, NIVEL),
        (COLUMNA_SIN_LISTA, FUENTE),
    ]
    assert [a.codigo for a in esquema.advertencias] == [
        c for c in CODIGOS_ADVERTENCIA_ESTRUCTURA if c != BLOQUE_SIN_DIMENSIONES
    ]
    assert all(a.ref is None for a in esquema.advertencias)
    assert {a.ambito for a in esquema.advertencias} == {"columna"}
    assert esquema.notas == (Nota(COLUMNAS_NO_USADAS, {"columnas": ("Observaciones",)}),)


# --------------------------------------------------------------------------------------------
# Nota de columnas no usadas (T-001-32) · FR-001-21
# --------------------------------------------------------------------------------------------


def test_una_columna_ajena_sin_lista_va_en_la_nota_sin_advertencia() -> None:
    """Contrato §3, FR-001-21 (cb18): la nota trae el nombre de la columna; no hay advertencia."""
    esquema = _fixture("cb18_columna_observaciones.xlsx")

    assert esquema.advertencias == ()
    assert esquema.notas == (Nota(COLUMNAS_NO_USADAS, {"columnas": ("Observaciones",)}),)


def test_las_columnas_ajenas_van_en_una_sola_nota_en_el_orden_del_archivo_y_sin_repetir() -> None:
    """Contrato §3: una antes del bloque, dos al final y una repetida; una nota, tres nombres."""
    matriz = _base()
    matriz.agregar_columna("Observaciones", valores=["Nota"])
    matriz.agregar_columna("Comentarios del equipo")
    matriz.agregar_columna("Observaciones", valores=["Otra nota"])
    matriz.agregar_columna("Etiqueta", posicion=1)
    esquema = _esquema(matriz.a_bytes())

    assert esquema.advertencias == ()
    assert esquema.notas == (
        Nota(
            COLUMNAS_NO_USADAS,
            {"columnas": ("Etiqueta", "Observaciones", "Comentarios del equipo")},
        ),
    )
    assert esquema.dimensiones == DIMENSIONES_BASE


def test_una_columna_sin_encabezado_no_es_dimension_ni_advertencia_ni_se_nombra_en_la_nota() -> (
    None
):
    """Contrato §3: sin encabezado no hay nombre; fuera o dentro del bloque se ignora."""
    matriz = _base()
    matriz.agregar_columna(None, valores=["x"])
    matriz.agregar_columna(None, antes_de="Dimensión 3", valores=["y"])
    esquema = _esquema(matriz.a_bytes())

    assert esquema.advertencias == ()
    assert esquema.notas == ()
    assert esquema.dimensiones == DIMENSIONES_BASE


def test_las_columnas_con_lista_1_0_tras_un_bloque_invertido_no_van_en_la_nota() -> None:
    """Contrato §3, §3.1: con lista `1,0` es advertencia, no «no usada»."""
    assert _fixture("cb38_bloque_invertido.xlsx").notas == ()
