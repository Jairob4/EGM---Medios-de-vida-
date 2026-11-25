"""Pruebas de la base de M10 `egm.textos` (T-001-16): P-001-09.

Los esperados de E2, E3 y E10 están copiados a mano de `docs/interfaz/flujos.md` §2 (estados de
rechazo); el de `fecha()` sale del enunciado de P-001-09. Ninguno sale de ejecutar `egm.textos`.
"""

import re
from datetime import datetime

import pytest

from egm import textos
from egm.modelo import (
    CODIGOS_ADVERTENCIA_ESTRUCTURA,
    CODIGOS_ADVERTENCIA_FILA,
    CODIGOS_ERROR_CONTRATO,
    CODIGOS_NOTA,
    Advertencia,
    ErrorContrato,
    FalloContrato,
    Nota,
    Rechazo,
    RefFila,
)

E2_TIPO = (
    "No se pudo cargar el archivo. El archivo elegido no es un archivo de Excel (.xlsx) que la "
    "herramienta pueda abrir, o está dañado. No se leyó y no se muestra ningún resultado. "
    "Elija la matriz bibliográfica en formato .xlsx."
)
E3_TAMANO = (
    "No se pudo cargar el archivo. El archivo pesa más de 15 MB (15 728 640 bytes), el máximo "
    "que admite la herramienta. No se leyó y no se muestra ningún resultado de ese archivo."
)
E10_CONTENIDO = (
    "No se pudo cargar el archivo. El contenido del libro es demasiado grande para abrirlo. "
    "No se leyó y no se muestra ningún resultado de ese archivo."
)


def test_fecha_en_espanol_para_el_21_de_noviembre_de_2026() -> None:
    """NFR-000-03: `fecha()` da «21 de noviembre de 2026» para esa fecha (P-001-09)."""
    assert textos.fecha(datetime(2026, 11, 21, 15, 30)) == "21 de noviembre de 2026"


@pytest.mark.parametrize(
    ("mes", "nombre"),
    [
        (1, "enero"),
        (2, "febrero"),
        (3, "marzo"),
        (4, "abril"),
        (5, "mayo"),
        (6, "junio"),
        (7, "julio"),
        (8, "agosto"),
        (9, "septiembre"),
        (10, "octubre"),
        (11, "noviembre"),
        (12, "diciembre"),
    ],
)
def test_fecha_nombra_cada_mes_sin_ceros_a_la_izquierda(mes: int, nombre: str) -> None:
    """NFR-000-03: el mes va en español y el día sin cero a la izquierda (P-001-09)."""
    assert textos.fecha(datetime(2027, mes, 5)) == f"5 de {nombre} de 2027"


def test_rechazo_por_tipo_da_el_texto_e2() -> None:
    """NFR-000-19, US-001-4.3: texto del estado E2 de `flujos.md` §2."""
    assert textos.rechazo(Rechazo("tipo")) == E2_TIPO


def test_rechazo_por_tamano_da_el_texto_e3() -> None:
    """NFR-000-19, US-001-4.4: texto del estado E3 de `flujos.md` §2."""
    assert textos.rechazo(Rechazo("tamano")) == E3_TAMANO


def test_rechazo_por_contenido_da_el_texto_e10_sin_cifras() -> None:
    """NFR-000-19, US-001-4.13: texto del estado E10; no lleva ni tamaño ni límite."""
    texto = textos.rechazo(Rechazo("contenido"))
    assert texto == E10_CONTENIDO
    assert not re.search(r"\d", texto)


def test_cada_motivo_de_rechazo_tiene_texto_propio() -> None:
    """NFR-000-19: los tres motivos dan tres textos distintos."""
    todos = {textos.rechazo(Rechazo(m)) for m in ("tipo", "tamano", "contenido")}
    assert len(todos) == 3


def test_el_catalogo_es_de_solo_lectura() -> None:
    """NFR-000-03: el catálogo único y los rótulos no se pueden alterar desde afuera."""
    with pytest.raises(TypeError):
        textos.CATALOGO["rechazo.tipo"] = "otro"  # type: ignore[index]
    with pytest.raises(TypeError):
        textos.ROTULOS["x"] = "y"  # type: ignore[index]


def test_los_rotulos_empiezan_vacios_para_que_002_y_003_los_amplien() -> None:
    """FR-001-29, arquitectura M10: `ROTULOS` existe y está vacío en la base."""
    assert len(textos.ROTULOS) == 0


def test_el_catalogo_contiene_los_textos_de_rechazo() -> None:
    """NFR-000-19: el catálogo único incluye los tres textos de rechazo (otros agregan más)."""
    assert {E2_TIPO, E3_TAMANO, E10_CONTENIDO} <= set(textos.CATALOGO.values())


# --- Estilo de los textos (NFR-000-03, SC-000-03) ------------------------------------------------

TUTEO = re.compile(
    r"\b(t[uú]|tus?|ti|contigo|tienes|puedes|eres|quieres|elige|sube|carga|selecciona|"
    r"intenta|revisa|verifica|vuelve|abre|haz|usa)\b",
    re.IGNORECASE,
)
FORMULAS = re.compile(r"[=$\\^_{}<>∑≤≥±×÷]|\b\d+\s*/\s*\d+\b")
PROHIBIDAS = (
    "error de contrato",
    "validación",
    "validacion",
    "fixture",
    "tabla 3",
    "tabla no comparable",
    "traceback",
    "excepción",
)


def _todos_los_textos() -> list[str]:
    return [*textos.CATALOGO.values(), *textos.ROTULOS.values()]


def test_hay_textos_que_revisar() -> None:
    """NFR-000-03: la revisión de estilo no pasa por vacía."""
    assert len(_todos_los_textos()) >= 3


def test_ningun_texto_lleva_preguntas() -> None:
    """NFR-000-03, SC-000-03: ni «¿» ni «?» (sin preguntas al equipo)."""
    for texto in _todos_los_textos():
        assert "¿" not in texto
        assert "?" not in texto


def test_ningun_texto_tutea() -> None:
    """NFR-000-03, SC-000-03: sin formas de tuteo."""
    for texto in _todos_los_textos():
        assert TUTEO.search(texto) is None, texto


def test_ningun_texto_lleva_formulas() -> None:
    """NFR-000-03, SC-000-03: sin símbolos ni fórmulas."""
    for texto in _todos_los_textos():
        assert FORMULAS.search(texto) is None, texto


def test_ningun_texto_usa_jerga_ni_nombra_tablas_no_comparables() -> None:
    """NFR-000-03: sin jerga técnica ni mención de una tabla no comparable de la hoja EGM."""
    for texto in _todos_los_textos():
        minusculas = texto.lower()
        for prohibida in PROHIBIDAS:
            assert prohibida not in minusculas, (prohibida, texto)
        assert re.search(r"\btabla\s+\d", minusculas) is None, texto


def test_los_detectores_de_estilo_reconocen_lo_que_deben_rechazar() -> None:
    """NFR-000-03: los patrones de la revisión sí atrapan tuteo y fórmulas de ejemplo."""
    assert TUTEO.search("Puedes elegir otro archivo")
    assert TUTEO.search("Elige la matriz")
    assert TUTEO.search("Elija la matriz") is None
    assert FORMULAS.search("n = 5")
    assert FORMULAS.search("$S(i,j)$")


# --- Advertencias, notas y errores de contrato (T-001-34; P-001-43, P-001-39) -------------------
# Los esperados están escritos a mano a partir de F-001-2 y del estado E4 de `flujos.md`, y de la
# redacción propuesta para los textos que `flujos.md` no fija (los revisa Jairo en T-001-93).

PRINCIPAL = "Tipo de intervención (EGM)"
ENFOQUE = "Enfoque de género/diferencial"


def _fila(
    codigo: str,
    numero: str | None,
    fila: int,
    columna: str | None,
    valor: str | None,
    **datos: object,
) -> Advertencia:
    return Advertencia(codigo, "fila", RefFila(numero, fila), columna, valor, datos)


def _estructura(
    codigo: str,
    ambito: str,
    columna: str | None = None,
    valor: str | None = None,
    **datos: object,
) -> Advertencia:
    return Advertencia(codigo, ambito, None, columna, valor, datos)


def test_advertencia_de_fila_sigue_la_forma_de_f_001_2_y_quita_los_espacios_del_valor() -> None:
    """FR-001-12, SC-001-04: «N.º, columna, valor: …»; el valor sin espacios en los extremos."""
    a = _fila("valor_fuera_de_lista", "3", 4, PRINCIPAL, "  Intervención Z ")
    assert textos.advertencia(a) == (
        "N.º 3, columna «Tipo de intervención (EGM)», valor «Intervención Z»: el valor no está en "
        "la lista de esa columna. La herramienta no lo cuenta y no lo corrige."
    )


def test_advertencia_del_enfoque_es_el_ejemplo_de_f_001_2() -> None:
    """FR-001-10, SC-001-04 (F-001-2): cita la regla de Instrucciones y la categoría."""
    a = _fila("enfoque_sin_clasificar", "7", 8, ENFOQUE, "Se menciona el enfoque")
    assert textos.advertencia(a) == (
        "N.º 7, columna «Enfoque de género/diferencial», valor «Se menciona el enfoque»: no "
        "empieza por Sí, No o Parcial, como pide la hoja Instrucciones. Queda como «Sin "
        "clasificar»."
    )


def test_advertencia_sin_numero_usa_la_fila_y_sin_valor_omite_el_valor() -> None:
    """FR-001-12 (CB-13): con el N.º vacío el documento se señala por su fila."""
    a = _fila("numero_vacio", None, 7, "N°", None)
    assert textos.advertencia(a) == (
        "Fila 7, columna «N°»: la celda del N.º está vacía y la fila tiene contenido. El "
        "documento se lee y se identifica por su número de fila."
    )


def test_advertencia_sin_columna_omite_la_columna() -> None:
    """FR-001-12: si faltara la columna, el texto no deja un hueco ni inventa un nombre."""
    a = _fila("anio_no_reconocido", "4", 5, None, "s. f.")
    assert textos.advertencia(a).startswith("N.º 4, valor «s. f.»: el año no se reconoce")


def test_numero_repetido_dice_la_fila_anterior_y_la_propia() -> None:
    """FR-001-12 (CB-13): una fila anterior, dos y varias."""
    una = _fila("numero_repetido", "3", 8, "N°", "3", filas_anteriores=(4,))
    assert textos.advertencia(una) == (
        "N.º 3, columna «N°», valor «3»: este N.º ya aparece en la fila 4. Este documento, en la "
        "fila 8, se lee aparte y se identifica también por su número de fila."
    )
    varias = _fila("numero_repetido", "3", 12, "N°", "3", filas_anteriores=(4, 8, 9))
    assert textos.advertencia(varias).endswith(
        "este N.º ya aparece en las filas 4, 8 y 9. Este documento, en la fila 12, se lee aparte "
        "y se identifica también por su número de fila."
    )
    dos = _fila("numero_repetido", "3", 12, "N°", "3", filas_anteriores=(4, 8))
    assert "en las filas 4 y 8." in textos.advertencia(dos)


def test_dimension_con_numero_en_texto_y_dimension_fuera_de_rango_se_distinguen() -> None:
    """FR-001-12, SC-001-02 (CB-09, CB-41): texto «1» frente a un valor que no es 1 ni 0."""
    como_texto = _fila(
        "dimension_valor_invalido",
        "3",
        4,
        "Dimensión 3",
        "1",
        dimension="Dimensión 3",
        numero_en_texto=True,
    )
    assert textos.advertencia(como_texto) == (
        "N.º 3, columna «Dimensión 3», valor «1»: el número está escrito como texto y no como "
        "número. No marca la dimensión."
    )
    fuera = _fila(
        "dimension_valor_invalido",
        "6",
        7,
        "Dimensión 2",
        "2",
        dimension="Dimensión 2",
        numero_en_texto=False,
    )
    assert textos.advertencia(fuera) == (
        "N.º 6, columna «Dimensión 2», valor «2»: el valor no es 1 ni 0. No marca la dimensión."
    )


def test_advertencia_de_principal_igual_a_secundaria_dice_lo_que_cuenta_cada_uno() -> None:
    """FR-001-12, SC-001-02 (CB-07): la hoja EGM lo cuenta dos veces y la herramienta, una."""
    a = _fila(
        "principal_igual_secundaria",
        "6",
        7,
        PRINCIPAL,
        "Intervención D",
        intervencion="Intervención D",
        columna_secundaria="Intervención secundaria (opcional)",
    )
    assert textos.advertencia(a) == (
        "N.º 6, columna «Tipo de intervención (EGM)», valor «Intervención D»: la intervención "
        "«Intervención D» está en la principal y también en la secundaria (columna «Intervención "
        "secundaria (opcional)»). La hoja EGM la cuenta dos veces y esta herramienta, una."
    )


def test_no_empirico_con_intervencion_con_y_sin_tipo() -> None:
    """FR-001-12, SC-001-02 (CB-08): dice el tipo del documento si M05 lo entrega."""
    con_tipo = _fila(
        "no_empirico_con_intervencion",
        "6",
        7,
        PRINCIPAL,
        "Intervención D",
        tipo_documento="Documento teórico",
        intervenciones=("Intervención D",),
    )
    assert textos.advertencia(con_tipo).endswith(
        "el documento es de tipo «Documento teórico» y trae una intervención. No es un estudio "
        "empírico, así que no cuenta en el mapa."
    )
    sin_tipo = _fila("no_empirico_con_intervencion", "6", 7, PRINCIPAL, "Intervención D")
    assert textos.advertencia(sin_tipo).endswith(
        "el documento no es un estudio empírico y trae una intervención. No cuenta en el mapa."
    )


@pytest.mark.parametrize(
    ("codigo", "inicio"),
    [
        ("espacios_en_los_extremos", "el valor trae espacios al comienzo o al final."),
        ("tipo_documento_fuera_de_lista", "el tipo de documento no está en la lista"),
        ("anio_no_reconocido", "el año no se reconoce como número."),
    ],
)
def test_advertencias_de_fila_sin_datos_propios(codigo: str, inicio: str) -> None:
    """FR-001-12, FR-001-24: el cuerpo no necesita más datos que el prefijo."""
    a = _fila(codigo, "2", 3, "Columna", " Valor ")
    assert textos.advertencia(a).startswith("N.º 2, columna «Columna», valor «Valor»: " + inicio)


def test_advertencias_de_estructura_nombran_la_hoja_la_columna_o_el_valor() -> None:
    """FR-001-12, FR-001-22, FR-001-23, SC-001-04: sin N.º; dicen cuál hoja, columna o valor."""
    assert textos.advertencia(_estructura("bloque_sin_dimensiones", "hoja", motivo="vacio")) == (
        "En la hoja «Matriz bibliográfica» no hay columnas de dimensiones entre las dos columnas "
        "que delimitan el bloque. Ningún estudio entra al mapa y los estudios empíricos quedan "
        "pendientes."
    )
    invertido = _estructura("bloque_sin_dimensiones", "hoja", motivo="invertido")
    assert textos.advertencia(invertido) == (
        "En la hoja «Matriz bibliográfica», la columna que cierra el bloque de dimensiones está "
        "antes de la que lo inicia, así que el bloque no tiene dimensiones. Ningún estudio entra "
        "al mapa y los estudios empíricos quedan pendientes."
    )
    rol = _estructura("rol_dentro_del_bloque", "columna", "Metodología")
    assert textos.advertencia(rol) == (
        "La columna «Metodología» está dentro del bloque de dimensiones, pero es una columna "
        "propia de la matriz. La herramienta la lee con su función y no como dimensión."
    )
    fuera = _estructura("lista_1_0_fuera_del_bloque", "columna", "Marca de revisión")
    assert textos.advertencia(fuera) == (
        "La columna «Marca de revisión» está fuera del bloque de dimensiones y tiene lista de "
        "valores 1 y 0. La herramienta no la toma como dimensión."
    )
    sin_lista = _estructura("dimension_sin_lista_1_0", "columna", "Dimensión sin lista")
    assert textos.advertencia(sin_lista) == (
        "La columna «Dimensión sin lista», dentro del bloque de dimensiones, no tiene la lista de "
        "valores 1 y 0. La herramienta la toma como dimensión de todos modos."
    )
    sin_no_aplica = _estructura("lista_sin_no_aplica", "columna", "Nivel de evidencia", "No aplica")
    assert textos.advertencia(sin_no_aplica) == (
        "La lista de la columna «Nivel de evidencia» no tiene ningún valor que empiece por «No "
        "aplica». La herramienta toma todos sus valores como categorías."
    )
    varios = _estructura(
        "varios_empiricos",
        "columna",
        "Tipo de documento",
        valores=("Estudio empírico (A)", "Estudio empírico (B)"),
    )
    assert textos.advertencia(varios) == (
        "La lista de la columna «Tipo de documento» tiene más de un valor que empieza por "
        "«Estudio empírico»: «Estudio empírico (A)» y «Estudio empírico (B)». La herramienta "
        "toma todos como estudio empírico."
    )
    presentes = _estructura("columna_sin_lista", "columna", "Metodología", valores=("A", "B", "C"))
    assert textos.advertencia(presentes) == (
        "La columna «Metodología» no tiene lista de valores. La herramienta toma los valores "
        "presentes en la matriz: «A», «B» y «C»."
    )


def test_advertencia_sin_ancla_de_evaluacion_de_impacto_con_y_sin_niveles() -> None:
    """FR-001-23, SC-001-04: dice la columna, el valor que falta y los niveles que hay."""
    con = _estructura(
        "sin_ancla_evaluacion_impacto",
        "columna",
        "Nivel de evidencia",
        "Evaluación de impacto",
        niveles=("Estudio de caso", "Informe de proyecto"),
    )
    assert textos.advertencia(con) == (
        "La lista de la columna «Nivel de evidencia» no tiene el valor «Evaluación de impacto». "
        "La herramienta calcula el mapa, pero lo que depende de ese nivel queda como no "
        "disponible. Niveles de la lista: «Estudio de caso» y «Informe de proyecto»."
    )
    sin = _estructura(
        "sin_ancla_evaluacion_impacto", "columna", "Nivel de evidencia", "Evaluación de impacto"
    )
    assert textos.advertencia(sin).endswith("queda como no disponible.")


def test_codigo_fuera_de_la_lista_cerrada_levanta_key_error() -> None:
    """NFR-000-03: un código sin texto es un error de programación, no un texto vacío."""
    with pytest.raises(KeyError):
        textos.advertencia(_estructura("codigo_inventado", "hoja"))
    with pytest.raises(KeyError):
        textos.nota(Nota("codigo_inventado", {}))


def test_nota_de_columnas_no_usadas_con_una_y_con_varias_columnas() -> None:
    """FR-001-21 (F-001-2): «Columnas no usadas: Observaciones»; una sola nota con todas."""
    una = Nota("columnas_no_usadas", {"columnas": ("Observaciones",)})
    assert textos.nota(una) == "Columnas no usadas: Observaciones."
    varias = Nota("columnas_no_usadas", {"columnas": ("Observaciones", "Comentarios del equipo")})
    assert textos.nota(varias) == "Columnas no usadas: Observaciones, Comentarios del equipo."


def test_error_de_contrato_de_hoja_ausente_sigue_el_estado_e4() -> None:
    """FR-001-02, FR-001-29 (E4): lo esperado y lo encontrado, con el cierre fijo."""
    errores = (ErrorContrato("hoja_ausente", ("Matriz bibliográfica",), ("EGM", "Instrucciones")),)
    assert textos.error_contrato(FalloContrato(errores)) == (
        "No se pudo leer la matriz. Se esperaba la hoja «Matriz bibliográfica», y se encontraron: "
        "«EGM» y «Instrucciones». No se muestra ninguna cifra. Revise que el archivo sea la "
        "matriz bibliográfica del proyecto y vuelva a cargarlo."
    )


def test_error_de_contrato_con_un_solo_encontrado_y_con_ninguno() -> None:
    """FR-001-29 (E4): «se encontró» en singular y «no se encontró» si no hay nada."""
    uno = FalloContrato((ErrorContrato("hoja_ausente", ("Matriz bibliográfica",), ("EGM",)),))
    assert "y se encontró: «EGM». No se muestra" in textos.error_contrato(uno)
    ninguno = FalloContrato((ErrorContrato("hoja_ausente", ("Matriz bibliográfica",), ()),))
    esperado = "«Matriz bibliográfica», y no se encontró. No se muestra"
    assert esperado in textos.error_contrato(ninguno)


def test_error_de_contrato_de_encabezados_en_singular_y_en_plural() -> None:
    """FR-001-02, FR-001-03 (E4): una columna ausente y varias."""
    una = FalloContrato((ErrorContrato("encabezado_ausente", ("Nivel de evidencia",), ("N°",)),))
    assert textos.error_contrato(una) == (
        "No se pudo leer la matriz. Se esperaba la columna «Nivel de evidencia», y se encontró: "
        "«N°». No se muestra ninguna cifra. Revise que el archivo sea la matriz bibliográfica del "
        "proyecto y vuelva a cargarlo."
    )
    error = ErrorContrato("encabezado_ausente", ("Año", "Nivel de evidencia"), ("N°", "Referencia"))
    assert (
        "Se esperaban las columnas «Año» y «Nivel de evidencia», y se encontraron: «N°» y "
        "«Referencia»."
    ) in textos.error_contrato(FalloContrato((error,)))


def test_error_de_contrato_de_ancla_empirica_dice_el_valor_esperado_y_los_encontrados() -> None:
    """FR-001-23 (E4, CB-20): el prefijo esperado y los valores de la lista."""
    error = ErrorContrato("ancla_empirica_ausente", ("Estudio empírico",), ("Estudio de campo",))
    assert (
        "Se esperaba un valor que empiece por «Estudio empírico» en la lista de la columna de "
        "tipo de documento, y se encontró: «Estudio de campo»."
    ) in textos.error_contrato(FalloContrato((error,)))


def test_error_de_contrato_de_lista_obligatoria_en_singular_y_en_plural() -> None:
    """FR-001-22 (E4, CB-24): la columna sin lista de valores; sin encontrado."""
    una = ErrorContrato("lista_obligatoria_ausente", ("Nivel de evidencia",), ())
    assert (
        "Se esperaba una lista de valores en la columna «Nivel de evidencia», y no se encontró."
    ) in textos.error_contrato(FalloContrato((una,)))
    varias = ErrorContrato(
        "lista_obligatoria_ausente", ("Tipo de intervención (EGM)", "Nivel de evidencia"), ()
    )
    assert (
        "Se esperaba una lista de valores en cada una de las columnas «Tipo de intervención "
        "(EGM)» y «Nivel de evidencia», y no se encontraron."
    ) in textos.error_contrato(FalloContrato((varias,)))


def test_error_de_contrato_con_varios_errores_los_junta_sin_repetir_el_marco() -> None:
    """FR-001-29 (E4): todo lo esperado y lo encontrado de todos los errores, un solo marco."""
    fallo = FalloContrato(
        (
            ErrorContrato("encabezado_ausente", ("Año",), ("N°",)),
            ErrorContrato("lista_obligatoria_ausente", ("Nivel de evidencia",), ()),
        )
    )
    texto = textos.error_contrato(fallo)
    assert texto == (
        "No se pudo leer la matriz. Se esperaba la columna «Año», y se encontró: «N°». Se "
        "esperaba una lista de valores en la columna «Nivel de evidencia», y no se encontró. No "
        "se muestra ninguna cifra. Revise que el archivo sea la matriz bibliográfica del "
        "proyecto y vuelva a cargarlo."
    )
    assert texto.count("No se pudo leer la matriz.") == 1
    assert texto.count("No se muestra ninguna cifra.") == 1


def test_el_catalogo_tiene_texto_para_cada_codigo_de_la_lista_cerrada() -> None:
    """NFR-000-03: ningún código de M01 se queda sin texto en el catálogo único."""
    claves = set(textos.CATALOGO)
    for codigo in (*CODIGOS_ADVERTENCIA_FILA, *CODIGOS_ADVERTENCIA_ESTRUCTURA):
        propias = {c for c in claves if c.startswith(f"advertencia.{codigo}")}
        assert propias, codigo
    for codigo in CODIGOS_NOTA:
        assert f"nota.{codigo}" in claves
    for codigo in CODIGOS_ERROR_CONTRATO:
        assert f"error.{codigo}" in claves


def test_ningun_texto_armado_deja_marcas_de_plantilla_sin_llenar() -> None:
    """NFR-000-03: ninguna marca de plantilla sobrevive al armar un texto con datos mínimos."""
    for codigo in (*CODIGOS_ADVERTENCIA_FILA, *CODIGOS_ADVERTENCIA_ESTRUCTURA):
        fila = textos.advertencia(_fila(codigo, "1", 2, "Columna", "Valor"))
        estructura = textos.advertencia(_estructura(codigo, "columna"))
        assert "%" not in fila, fila
        assert "%" not in estructura, estructura
