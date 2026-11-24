"""Pruebas del constructor de matrices sintéticas M23 (`tests.constructor`).

Cubren T-001-04 (constructor base), T-001-05 (hoja EGM con fórmulas y valores guardados),
T-001-06 (archivos de carga), T-001-07 (catálogo de fixtures, P-001-01) y T-001-08 (estrategias
de hypothesis de matrices válidas al azar). Todos los esperados
están escritos a mano a partir del contrato de datos (`contrato-datos.md`, §3, §5, §7 y §9), de
los escenarios de los specs y de los límites de NFR-000-19; ninguno sale de ejecutar el
constructor.
"""

import ast
import builtins
import hashlib
import inspect
import io
import re
import struct
import subprocess
import sys
import warnings
import zipfile
import zlib
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

import pytest
from hypothesis import given, settings
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

import tests.constructor as modulo_constructor
from tests.constructor import (
    CATALOGO,
    EN_MEMORIA,
    MARCADORES_CELDAS,
    NOMBRE_CON_MARCADOR,
    TEXTOS_N7,
    Categorias,
    MatrizSintetica,
    archivo_de_texto,
    archivo_extension_xlsx_otro_contenido,
    carpeta_de_fixtures,
    categorias,
    escribir_catalogo,
    generar_catalogo,
    instancia_ejemplo,
    main,
    matrices_validas,
    parte_mayor_que_lo_declarado,
)

# --- Esperados del contrato (escritos a mano) --------------------------------------------------

ENCABEZADOS_BASE = [
    "N°",
    "Referencia APA",
    "Año",
    "Tipo de documento",
    "País y población",
    "Tipo de fuente",
    "Tipo de intervención (EGM)",
    "Intervención secundaria (opcional)",
    "Metodología",
    "Nivel de evidencia",
    "Dimensiones evaluadas / propuestas",
    "Dimensión 1",
    "Dimensión 2",
    "Dimensión 3",
    "Dimensión 4",
    "Dimensión 5",
    "Dimensión 6",
    "Dimensión 7",
    "Dimensión 8",
    "Indicadores o categorías analíticas",
    "Enfoque de género/diferencial",
    "Principales hallazgos / tesis central",
    "Vacío de conocimiento identificado",
    "Limitaciones",
    "Aporte al proyecto",
]
DIMENSIONES = [f"Dimensión {n}" for n in range(1, 9)]
INTERVENCIONES = [f"Intervención {c}" for c in "ABCDEF"]
NIVELES = ["Evaluación de impacto", "Estudio de caso", "Informe de proyecto"]
EMPIRICO = "Estudio empírico (evaluación/caso)"
HOJA = "Matriz bibliográfica"


def _abrir(contenido: bytes, *, valores: bool = False) -> Workbook:
    """Abre el libro en memoria; `valores=True` lee los valores guardados (no las fórmulas)."""
    return load_workbook(io.BytesIO(contenido), data_only=valores)


def _hoja(contenido: bytes, nombre: str, *, valores: bool = False) -> Worksheet:
    hoja = _abrir(contenido, valores=valores)[nombre]
    assert isinstance(hoja, Worksheet)
    return hoja


def _fila_1(contenido: bytes) -> list[object]:
    return [c.value for c in _hoja(contenido, HOJA)[1]]


def _partes(contenido: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        return {i.filename: paquete.read(i.filename) for i in paquete.infolist()}


# ================================================================================================
# T-001-04 · Constructor base (NFR-000-06, SC-001-02 soporte)
# ================================================================================================


def test_base_valida_se_genera_y_openpyxl_la_abre() -> None:
    """NFR-000-06: `base_valida` se genera, `openpyxl` la abre y trae los roles del contrato §3."""
    contenido = MatrizSintetica.base_valida().a_bytes()

    libro = _abrir(contenido)
    assert libro.sheetnames == [
        "Matriz bibliográfica",
        "EGM",
        "Instrucciones",
        "Guía por tipo de documento",
        "Listas",
    ]
    assert _fila_1(contenido) == ENCABEZADOS_BASE
    # Un documento por fila bajo el encabezado: N.º 1 a 5 en la columna A.
    hoja = _hoja(contenido, HOJA)
    assert [hoja.cell(fila, 1).value for fila in range(2, 8)] == [1, 2, 3, 4, 5, None]


def test_base_valida_tiene_ocho_dimensiones_entre_los_delimitadores() -> None:
    """NFR-000-06: el bloque de dimensiones está entre los dos delimitadores del contrato §3.1."""
    encabezados = _fila_1(MatrizSintetica.base_valida().a_bytes())
    inicio = encabezados.index("Dimensiones evaluadas / propuestas")
    fin = encabezados.index("Indicadores o categorías analíticas")
    assert encabezados[inicio + 1 : fin] == DIMENSIONES


def test_hojas_en_cualquier_orden() -> None:
    """NFR-000-06: las hojas pueden ir en cualquier orden."""
    matriz = MatrizSintetica.base_valida().ordenar_hojas(
        "Guía por tipo de documento", "Matriz bibliográfica", "Listas", "EGM"
    )
    libro = _abrir(matriz.a_bytes())
    assert libro.sheetnames == [
        "Guía por tipo de documento",
        "Matriz bibliográfica",
        "Listas",
        "EGM",
        "Instrucciones",
    ]


def test_hoja_renombrada_y_hoja_quitada() -> None:
    """NFR-000-06: se puede renombrar o quitar una hoja (hoja de la matriz faltante, CB-15)."""
    renombrada = MatrizSintetica.base_valida().renombrar_hoja("Matriz bibliográfica", "Otra")
    assert "Otra" in _abrir(renombrada.a_bytes()).sheetnames

    quitada = MatrizSintetica.base_valida().quitar_hoja("Matriz bibliográfica")
    nombres = _abrir(quitada.a_bytes()).sheetnames
    assert "Matriz bibliográfica" not in nombres
    assert nombres[0] == "EGM"


def test_encabezados_en_cualquier_posicion() -> None:
    """NFR-000-06: las columnas se pueden mover; los datos y la validación se mueven con ellas."""
    matriz = MatrizSintetica.base_valida().mover_columna("Nivel de evidencia", posicion=1)
    contenido = matriz.a_bytes()

    encabezados = _fila_1(contenido)
    assert encabezados[0] == "Nivel de evidencia"
    assert encabezados[1] == "N°"
    # El documento N.º 1 es de tipo teórico: su nivel «No aplica…» viaja con la columna.
    hoja = _hoja(contenido, HOJA)
    assert hoja["A2"].value == "No aplica (marco conceptual/normativo/metodológico)"
    # La validación de la lista de nivel quedó sobre la columna A, filas 2 a 36.
    rangos = {str(v.sqref) for v in hoja.data_validations.dataValidation}
    assert "A2:A36" in rangos


def test_fila_de_encabezados_en_otra_fila() -> None:
    """NFR-000-06: el encabezado puede estar en otra fila; los datos van debajo."""
    contenido = MatrizSintetica.base_valida().con_fila_encabezado(3).a_bytes()
    hoja = _hoja(contenido, HOJA)
    assert hoja["A3"].value == "N°"
    assert hoja["A1"].value is None
    assert hoja["A4"].value == 1


def test_columna_quitada_renombrada_y_agregada() -> None:
    """NFR-000-06: variantes pequeñas de columnas (CB-14, CB-18, CB-37)."""
    base = MatrizSintetica.base_valida
    sin_nivel = _fila_1(base().quitar_columna("Nivel de evidencia").a_bytes())
    assert "Nivel de evidencia" not in sin_nivel
    assert len(sin_nivel) == 24

    renombrada = _fila_1(base().renombrar_encabezado("Nivel de evidencia", "Nivel").a_bytes())
    assert renombrada[9] == "Nivel"

    ajena = _fila_1(
        base().agregar_columna("Observaciones", despues_de="Aporte al proyecto").a_bytes()
    )
    assert ajena[-1] == "Observaciones"
    assert len(ajena) == 26

    dentro = _fila_1(
        base()
        .agregar_columna("Dimensión 9", antes_de="Indicadores o categorías analíticas")
        .a_bytes()
    )
    assert dentro[19] == "Dimensión 9"
    assert dentro[20] == "Indicadores o categorías analíticas"


def test_las_dimensiones_se_listan_en_el_orden_del_archivo() -> None:
    """NFR-000-06: `dimensiones()` devuelve las columnas entre los delimitadores, en orden."""
    matriz = MatrizSintetica.base_valida().agregar_columna(
        "Dimensión 9", antes_de="Indicadores o categorías analíticas"
    )
    assert matriz.dimensiones() == [*DIMENSIONES, "Dimensión 9"]


def test_validacion_como_lista_escrita() -> None:
    """FR-001-05 (insumo): la lista de tipo de fuente va escrita en la validación, en su orden."""
    hoja = _hoja(MatrizSintetica.base_valida().a_bytes(), HOJA)
    validaciones = {str(v.sqref): v.formula1 for v in hoja.data_validations.dataValidation}
    assert validaciones["F2:F36"] == '"Académica,Institucional,Territorial"'
    assert validaciones["L2:L36"] == '"1,0"'
    assert validaciones["G2:G36"] == (
        '"Intervención A,Intervención B,Intervención C,Intervención D,Intervención E,'
        'Intervención F,No aplica (documento teórico/metodológico/normativo)"'
    )


def test_validacion_como_referencia_a_rango() -> None:
    """FR-001-05 (insumo): la lista de tipo de documento va como referencia a un rango."""
    contenido = MatrizSintetica.base_valida().a_bytes()
    hoja = _hoja(contenido, HOJA)
    validaciones = {str(v.sqref): v.formula1 for v in hoja.data_validations.dataValidation}
    assert validaciones["D2:D36"] == "Listas!$A$2:$A$5"
    assert validaciones["J2:J36"] == "Listas!$B$2:$B$5"

    listas = _hoja(contenido, "Listas")
    assert [listas.cell(f, 1).value for f in range(2, 6)] == [
        "Estudio empírico (evaluación/caso)",
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
    ]
    assert [listas.cell(f, 2).value for f in range(2, 6)] == [
        "Evaluación de impacto",
        "Estudio de caso",
        "Informe de proyecto",
        "No aplica (marco conceptual/normativo/metodológico)",
    ]


def test_lista_cambia_de_modo_y_se_puede_alterar() -> None:
    """NFR-000-06: una lista pasa de escrita a rango; se le agrega un valor y se le quita otro."""
    matriz = (
        MatrizSintetica.base_valida()
        .con_lista("Tipo de fuente", ["Alfa", "Beta"], modo="rango")
        .agregar_valor_a_lista("Tipo de documento", "Documento nuevo")
        .quitar_valor_de_lista("Tipo de documento", "Documento normativo")
        .sin_lista("Metodología")
    )
    contenido = matriz.a_bytes()
    hoja = _hoja(contenido, HOJA)
    validaciones = {str(v.sqref): v.formula1 for v in hoja.data_validations.dataValidation}
    # Sin lista: no hay validación sobre la columna I (Metodología).
    assert "I2:I36" not in validaciones
    # Las listas por rango siguen el orden de las columnas: D, F, J → A, B, C.
    assert validaciones["F2:F36"] == "Listas!$B$2:$B$3"
    listas = _hoja(contenido, "Listas")
    assert [listas.cell(f, 1).value for f in range(2, 7)] == [
        "Estudio empírico (evaluación/caso)",
        "Documento teórico",
        "Documento metodológico",
        "Documento nuevo",
        None,
    ]


def test_lista_con_coma_en_modo_escrito_se_rechaza() -> None:
    """NFR-000-06: una validación escrita no admite valores con coma (hay que usar un rango)."""
    with pytest.raises(ValueError, match="coma"):
        MatrizSintetica.base_valida().con_lista("Tipo de fuente", ["a,b", "c"])


def test_filas_con_valores_de_cualquier_tipo() -> None:
    """NFR-000-06: número, texto, vacío, espacios y «1» como texto se guardan con su tipo."""
    matriz = MatrizSintetica.base_valida().agregar_fila(
        {
            "N°": 6,
            "Referencia APA": "   ",
            "Año": "2019",
            "Tipo de documento": None,
            "Dimensión 1": "1",
            "Dimensión 2": 0,
            "Dimensión 3": 1,
        }
    )
    hoja = _hoja(matriz.a_bytes(), HOJA)
    fila = 7  # cinco documentos de la base más el encabezado: la nueva fila es la 7
    assert hoja.cell(fila, 1).value == 6
    assert hoja.cell(fila, 2).value == "   "
    assert hoja.cell(fila, 3).value == "2019"
    assert isinstance(hoja.cell(fila, 3).value, str)
    assert hoja.cell(fila, 4).value is None
    assert hoja["L7"].value == "1"
    assert isinstance(hoja["L7"].value, str)
    assert hoja["M7"].value == 0
    assert isinstance(hoja["M7"].value, int)
    assert hoja["N7"].value == 1
    assert isinstance(hoja["N7"].value, int)


def test_fila_vacia_y_celda_alterada() -> None:
    """NFR-000-06: filas vacías al final y celdas puntuales alteradas."""
    matriz = MatrizSintetica.base_valida().agregar_filas_vacias(2).fijar_celda(0, "Año", "sf")
    hoja = _hoja(matriz.a_bytes(), HOJA)
    assert hoja["C2"].value == "sf"
    assert all(c.value is None for c in hoja[7])
    assert all(c.value is None for c in hoja[8])


def test_fechas_internas_y_marcas_del_paquete_fijas() -> None:
    """NFR-000-06: las fechas internas del libro y las marcas de tiempo del paquete son fijas."""
    contenido = MatrizSintetica.base_valida().a_bytes()
    libro = _abrir(contenido)
    assert libro.properties.created == datetime(2000, 1, 1, 0, 0, 0)
    assert libro.properties.modified == datetime(2000, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        assert {i.date_time for i in paquete.infolist()} == {(2000, 1, 1, 0, 0, 0)}


def test_misma_generacion_mismos_bytes() -> None:
    """NFR-000-06: dos generaciones del mismo libro dan exactamente los mismos bytes."""
    assert MatrizSintetica.base_valida().a_bytes() == MatrizSintetica.base_valida().a_bytes()
    variante = MatrizSintetica.base_valida().quitar_columna("Limitaciones")
    assert variante.a_bytes() == variante.copia().a_bytes()


def test_copia_independiente() -> None:
    """NFR-000-06: una copia se altera sin tocar el original (variantes pequeñas)."""
    original = MatrizSintetica.base_valida()
    variante = original.copia().quitar_columna("Limitaciones").quitar_filas()
    assert len(_fila_1(original.a_bytes())) == 25
    assert len(_fila_1(variante.a_bytes())) == 24


def test_el_constructor_nunca_abre_rutas_de_los_datos_reales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NFR-000-01 (soporte): generar libros no abre ningún archivo ni nombra `raw` en el código."""
    abiertos: list[str] = []
    abrir_real = builtins.open

    def espia(archivo: object, *args: object, **kwargs: object) -> object:
        abiertos.append(str(archivo))
        return abrir_real(archivo, *args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(builtins, "open", espia)
    MatrizSintetica.base_valida().a_bytes()
    # `openpyxl` abre archivos temporales con sufijo al azar: se compara por carpeta, no por texto.
    assert not any("raw" in Path(ruta).parts for ruta in abiertos)

    fuente = Path(__file__).resolve().parents[1] / "constructor.py"
    arbol = ast.parse(fuente.read_text(encoding="utf-8"))
    docstrings = {
        id(nodo.body[0].value)
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Module | ast.ClassDef | ast.FunctionDef)
        and nodo.body
        and isinstance(nodo.body[0], ast.Expr)
        and isinstance(nodo.body[0].value, ast.Constant)
    }
    cadenas = [
        nodo.value
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Constant)
        and isinstance(nodo.value, str)
        and id(nodo) not in docstrings
    ]
    assert not [c for c in cadenas if "raw" in c.lower()]


# ================================================================================================
# T-001-05 · Hoja EGM, fórmulas y valores guardados (FR-001-14, FR-001-05)
# ================================================================================================


def _matriz_controlada() -> MatrizSintetica:
    """Cuatro documentos de la matriz, con conteos de la hoja calculados a mano.

    Documento 1: empírico, principal A, secundaria B, nivel de impacto, dimensiones 1 y 2 en 1
    y la 3 en 0.
    Documento 2: empírico, principal A y secundaria A (la hoja cuenta doble), nivel de caso,
    dimensión 1.
    Documento 3: teórico (no entra en la hoja), principal A, dimensión 1.
    Documento 4: empírico, principal C, nivel de impacto, dimensión 1 escrita como texto «1»
    (la hoja la cuenta).
    """
    return (
        MatrizSintetica.base_valida()
        .quitar_filas()
        .agregar_fila(
            {
                "N°": 1,
                "Tipo de documento": EMPIRICO,
                "Tipo de intervención (EGM)": "Intervención A",
                "Intervención secundaria (opcional)": "Intervención B",
                "Nivel de evidencia": "Evaluación de impacto",
                "Dimensión 1": 1,
                "Dimensión 2": 1,
                "Dimensión 3": 0,
            }
        )
        .agregar_fila(
            {
                "N°": 2,
                "Tipo de documento": EMPIRICO,
                "Tipo de intervención (EGM)": "Intervención A",
                "Intervención secundaria (opcional)": "Intervención A",
                "Nivel de evidencia": "Estudio de caso",
                "Dimensión 1": 1,
            }
        )
        .agregar_fila(
            {
                "N°": 3,
                "Tipo de documento": "Documento teórico",
                "Tipo de intervención (EGM)": "Intervención A",
                "Dimensión 1": 1,
            }
        )
        .agregar_fila(
            {
                "N°": 4,
                "Tipo de documento": EMPIRICO,
                "Tipo de intervención (EGM)": "Intervención C",
                "Nivel de evidencia": "Evaluación de impacto",
                "Dimensión 1": "1",
            }
        )
    )


def _localizar_titulo(hoja: Worksheet, numero: int) -> tuple[int, int]:
    """(fila, columna) de la celda cuyo texto empieza por «<numero>. »."""
    for fila in hoja.iter_rows():
        for celda in fila:
            if isinstance(celda.value, str) and celda.value.startswith(f"{numero}. "):
                return celda.row, celda.column
    raise AssertionError(f"no hay título de la tabla {numero}")


def _leer_tabla(hoja: Worksheet, numero: int) -> dict[str, dict[str, object]]:
    """Cuerpo de la tabla: nombre de fila → {encabezado → valor}; acaba en la primera sin nombre."""
    fila_t, col = _localizar_titulo(hoja, numero)
    encabezados = {}
    columna = col + 1
    while hoja.cell(fila_t + 1, columna).value is not None:
        encabezados[columna] = hoja.cell(fila_t + 1, columna).value
        columna += 1
    cuerpo: dict[str, dict[str, object]] = {}
    fila = fila_t + 2
    while hoja.cell(fila, col).value is not None:
        cuerpo[hoja.cell(fila, col).value] = {
            str(enc): hoja.cell(fila, c).value for c, enc in encabezados.items()
        }
        fila += 1
    return cuerpo


def _fila_con(
    a: int = 0, b: int = 0, c: int = 0, d: int = 0, e: int = 0, f: int = 0, g: int = 0, h: int = 0
) -> dict[str, int]:
    return {f"Dimensión {n}": v for n, v in enumerate((a, b, c, d, e, f, g, h), start=1)}


def _contar_formulas(contenido: bytes) -> tuple[int, int]:
    """(celdas con fórmula, de ellas las que traen valor guardado) en la hoja EGM."""
    formulas = _hoja(contenido, "EGM")
    valores = _hoja(contenido, "EGM", valores=True)
    n_formulas = n_con_valor = 0
    for fila in formulas.iter_rows():
        for celda in fila:
            if isinstance(celda.value, str) and celda.value.startswith("="):
                n_formulas += 1
                if valores[celda.coordinate].value is not None:
                    n_con_valor += 1
    return n_formulas, n_con_valor


def test_un_libro_expone_formula_y_valor_guardado_en_la_misma_celda() -> None:
    """FR-001-14: al leerlo, una celda de la hoja EGM da su fórmula y su valor guardado."""
    contenido = _matriz_controlada().a_bytes()
    con_formulas = _hoja(contenido, "EGM")
    con_valores = _hoja(contenido, "EGM", valores=True)

    fila_t, col = _localizar_titulo(con_formulas, 1)
    # Primera fila de nombres: la intervención A; primera columna: Dimensión 1.
    nombre = con_formulas.cell(fila_t + 2, col).value
    assert nombre == "Intervención A"
    fila = fila_t + 2
    esperada = (
        f"=COUNTIFS('Matriz bibliográfica'!$G$2:$G$200,$A{fila},"
        "'Matriz bibliográfica'!$D$2:$D$200,\"Estudio empírico*\","
        "'Matriz bibliográfica'!$L$2:$L$200,1)"
        f"+COUNTIFS('Matriz bibliográfica'!$H$2:$H$200,$A{fila},"
        "'Matriz bibliográfica'!$D$2:$D$200,\"Estudio empírico*\","
        "'Matriz bibliográfica'!$L$2:$L$200,1)"
    )
    assert con_formulas.cell(fila, col + 1).value == esperada
    # Mismo celda, valor guardado: doc. 1 (principal) + doc. 2 (principal y secundaria) = 3.
    assert con_valores.cell(fila, col + 1).value == 3


def test_tabla_1_valores_guardados_correctos() -> None:
    """FR-001-14: tabla 1 (total de estudios), conteo de la hoja sobre las filas 2 a 200."""
    cuerpo = _leer_tabla(_hoja(_matriz_controlada().a_bytes(), "EGM", valores=True), 1)
    assert list(cuerpo) == INTERVENCIONES
    # Documento 1: A y B en las dimensiones 1 y 2; documento 2: A dos veces en la 1;
    # documento 4: C en la 1 (el texto «1» lo cuenta la hoja). El documento 3 no es empírico.
    assert cuerpo["Intervención A"] == {**_fila_con(3, 1), "Total estudios": 3}
    assert cuerpo["Intervención B"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert cuerpo["Intervención C"] == {**_fila_con(1), "Total estudios": 1}
    for nombre in ("Intervención D", "Intervención E", "Intervención F"):
        assert cuerpo[nombre] == {**_fila_con(), "Total estudios": 0}


def test_tabla_2_valores_guardados_correctos() -> None:
    """FR-001-14: tabla 2 (evaluación de impacto): solo los documentos con nivel de impacto."""
    cuerpo = _leer_tabla(_hoja(_matriz_controlada().a_bytes(), "EGM", valores=True), 2)
    assert list(cuerpo) == INTERVENCIONES
    assert cuerpo["Intervención A"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert cuerpo["Intervención B"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert cuerpo["Intervención C"] == {**_fila_con(1), "Total estudios": 1}
    assert cuerpo["Intervención D"] == {**_fila_con(), "Total estudios": 0}


def test_tabla_4_valores_guardados_correctos() -> None:
    """FR-001-14: tabla 4 (por nivel): documentos empíricos por nivel."""
    cuerpo = _leer_tabla(_hoja(_matriz_controlada().a_bytes(), "EGM", valores=True), 4)
    assert cuerpo == {
        "Evaluación de impacto": {"Estudios": 2},
        "Estudio de caso": {"Estudios": 1},
        "Informe de proyecto": {"Estudios": 0},
    }


def test_tabla_3_existe_con_valores_y_es_distinta_de_las_comparables() -> None:
    """FR-001-14: la hoja trae una tabla 3 con valores (no comparable) para las pruebas."""
    hoja = _hoja(_matriz_controlada().a_bytes(), "EGM", valores=True)
    cuerpo = _leer_tabla(hoja, 3)
    assert list(cuerpo) == INTERVENCIONES
    assert all(isinstance(v, int) for fila in cuerpo.values() for v in fila.values())


def test_base_valida_trae_valores_guardados_correctos_en_las_tres_tablas() -> None:
    """FR-001-14: `base_valida` (5 documentos, 3 empíricos) trae la hoja con valores correctos."""
    hoja = _hoja(MatrizSintetica.base_valida().a_bytes(), "EGM", valores=True)
    t1 = _leer_tabla(hoja, 1)
    # Documento 2 (A y B; dimensiones 1 y 2, impacto), documento 3 (C; dimensiones 3 y 4, caso),
    # documento 4 (A; dimensión 1, informe).
    assert t1["Intervención A"] == {**_fila_con(2, 1), "Total estudios": 2}
    assert t1["Intervención B"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert t1["Intervención C"] == {**_fila_con(0, 0, 1, 1), "Total estudios": 1}
    t2 = _leer_tabla(hoja, 2)
    assert t2["Intervención A"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert t2["Intervención B"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert t2["Intervención C"] == {**_fila_con(), "Total estudios": 0}
    assert _leer_tabla(hoja, 4) == {
        "Evaluación de impacto": {"Estudios": 1},
        "Estudio de caso": {"Estudios": 1},
        "Informe de proyecto": {"Estudios": 1},
    }


def test_las_formulas_abarcan_solo_el_rango_configurado() -> None:
    """FR-001-14: más filas que el rango de las fórmulas; la hoja cuenta solo ese rango (CB-12)."""
    matriz = _matriz_controlada()
    matriz.egm.fila_final_formulas = 3
    contenido = matriz.a_bytes()
    hoja_f = _hoja(contenido, "EGM")
    fila_t, col = _localizar_titulo(hoja_f, 1)
    assert "$G$2:$G$3" in hoja_f.cell(fila_t + 2, col + 1).value
    # Filas 2 y 3 de la hoja = documentos 1 y 2: A=3 en la dimensión 1, C queda en 0.
    cuerpo = _leer_tabla(_hoja(contenido, "EGM", valores=True), 1)
    assert cuerpo["Intervención A"]["Dimensión 1"] == 3
    assert cuerpo["Intervención C"]["Dimensión 1"] == 0


def test_las_formulas_siguen_la_columna_aunque_se_mueva_o_renombre() -> None:
    """FR-001-14: la hoja se genera con las letras reales de la matriz tras mover columnas."""
    matriz = _matriz_controlada().mover_columna("Tipo de intervención (EGM)", posicion=1)
    hoja = _hoja(matriz.a_bytes(), "EGM")
    fila_t, col = _localizar_titulo(hoja, 1)
    # La principal pasó a la columna A y todo lo demás se corrió una letra a la derecha.
    assert "'Matriz bibliográfica'!$A$2:$A$200" in hoja.cell(fila_t + 2, col + 1).value
    assert "'Matriz bibliográfica'!$E$2:$E$200" in hoja.cell(fila_t + 2, col + 1).value
    renombrada = _matriz_controlada().renombrar_encabezado("Nivel de evidencia", "Nivel")
    valores = _hoja(renombrada.a_bytes(), "EGM", valores=True)
    assert _leer_tabla(valores, 4)["Evaluación de impacto"] == {"Estudios": 2}


def test_titulos_numerados_y_tablas_en_cualquier_posicion() -> None:
    """FR-001-14: los títulos van numerados y las tablas se pueden poner en cualquier posición."""
    matriz = _matriz_controlada()
    matriz.egm.tabla(2).mover(fila=30, columna=3)
    matriz.egm.tabla(1).titulo = "1. Total de estudios por intervención y dimensión"
    contenido = matriz.a_bytes()
    hoja = _hoja(contenido, "EGM")
    assert hoja.cell(30, 3).value.startswith("2. ")
    assert hoja.cell(30, 4).value is None  # el título ocupa solo su celda
    assert _localizar_titulo(hoja, 1)[1] == 1
    assert hoja.cell(_localizar_titulo(hoja, 1)[0], 1).value == (
        "1. Total de estudios por intervención y dimensión"
    )
    # El nombre de la primera fila quedó en la columna C y la fórmula lo cita en C.
    assert hoja.cell(32, 3).value == "Intervención A"
    assert "$C32" in hoja.cell(32, 4).value
    valores = _hoja(contenido, "EGM", valores=True)
    assert valores.cell(32, 4).value == 1  # tabla 2: A en la dimensión 1 (documento 1)


def test_desplazar_todas_las_tablas_deja_filas_vacias_antes() -> None:
    """FR-001-14: las tablas pueden empezar más abajo (filas vacías antes, esc. 3.5)."""
    base = _hoja(_matriz_controlada().a_bytes(), "EGM")
    matriz = _matriz_controlada()
    matriz.egm.desplazar(filas=4)
    desplazada = _hoja(matriz.a_bytes(), "EGM")
    assert _localizar_titulo(desplazada, 1)[0] == _localizar_titulo(base, 1)[0] + 4
    assert all(c.value is None for c in desplazada[1])


def test_valores_guardados_ausentes_texto_y_parciales() -> None:
    """FR-001-14, FR-001-17: un valor guardado puede faltar, ser texto o estar solo en parte."""
    matriz = _matriz_controlada()
    tabla = matriz.egm.tabla(1)
    tabla.fijar_valor("Intervención A", "Dimensión 1", None)  # ausente
    tabla.fijar_valor("Intervención B", "Dimensión 1", "n/d")  # texto
    tabla.fijar_valor("Intervención C", "Total estudios", 7)  # distinto del conteo
    contenido = matriz.a_bytes()

    con_valores = _leer_tabla(_hoja(contenido, "EGM", valores=True), 1)
    assert con_valores["Intervención A"]["Dimensión 1"] is None
    assert con_valores["Intervención B"]["Dimensión 1"] == "n/d"
    assert con_valores["Intervención C"]["Total estudios"] == 7
    # Lo demás de la tabla conserva su valor correcto: la tabla queda con solo algunos valores.
    assert con_valores["Intervención A"]["Dimensión 2"] == 1
    assert con_valores["Intervención A"]["Total estudios"] == 3
    # Las fórmulas siguen ahí, también en las celdas sin valor.
    con_formulas = _leer_tabla(_hoja(contenido, "EGM"), 1)
    assert str(con_formulas["Intervención A"]["Dimensión 1"]).startswith("=COUNTIFS(")


def test_libro_sin_valores_guardados() -> None:
    """FR-001-14: un libro sin valores guardados trae las fórmulas y ningún valor (CB-30)."""
    matriz = _matriz_controlada()
    matriz.egm.sin_valores_guardados()
    n_formulas, n_con_valor = _contar_formulas(matriz.a_bytes())
    assert n_formulas > 100
    assert n_con_valor == 0


def test_con_egm_sin_valores_guardados_desde_el_inicio() -> None:
    """FR-001-14: `con_egm(valores_guardados=False)` genera lo mismo que borrar los valores."""
    matriz = MatrizSintetica.base_valida().quitar_hoja("EGM").con_egm(valores_guardados=False)
    n_formulas, n_con_valor = _contar_formulas(matriz.a_bytes())
    assert n_formulas > 100
    assert n_con_valor == 0


def test_valor_guardado_de_una_celda_con_formula_se_escribe_en_el_xml_de_la_celda() -> None:
    """FR-001-14 (R-4): el valor va en el `<v>` de la misma celda que tiene la `<f>`."""
    partes = _partes(_matriz_controlada().a_bytes())
    xml = partes["xl/worksheets/sheet2.xml"].decode("utf-8")
    # Hoja EGM: segunda del libro. Todas las celdas con fórmula traen su valor numérico.
    celdas = re.findall(r"<c r=\"([A-Z]+\d+)\"[^>]*><f>(.*?)</f><v>(.*?)</v></c>", xml)
    assert len(celdas) > 100
    assert all(re.fullmatch(r"\d+", valor) for _, _, valor in celdas)


def test_paquete_con_valores_guardados_sigue_siendo_un_zip_integro() -> None:
    """FR-001-14 (R-4): reempaquetar no deja partes repetidas ni dañadas."""
    contenido = _matriz_controlada().a_bytes()
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        nombres = paquete.namelist()
        assert paquete.testzip() is None
    assert len(nombres) == len(set(nombres))
    assert "[Content_Types].xml" in nombres
    assert "xl/workbook.xml" in nombres


@pytest.mark.filterwarnings("ignore:Data Validation extension")
def test_validacion_guardada_como_extension_x14() -> None:
    """FR-001-05: una lista como extensión `x14` está en el XML y no como validación normal."""
    contenido = (
        MatrizSintetica.base_valida().con_lista("Tipo de fuente", ["A1", "B2", "C3"], modo="x14")
    ).a_bytes()

    xml = _partes(contenido)["xl/worksheets/sheet1.xml"].decode("utf-8")
    assert "x14:dataValidation" in xml
    raiz = ElementTree.fromstring(xml)
    x14 = "{http://schemas.microsoft.com/office/spreadsheetml/2009/9/main}"
    xm = "{http://schemas.microsoft.com/office/excel/2006/main}"
    validaciones = list(raiz.iter(f"{x14}dataValidation"))
    assert len(validaciones) == 1
    assert validaciones[0].get("type") == "list"
    assert validaciones[0].find(f"{x14}formula1/{xm}f").text == "Listas!$B$2:$B$4"  # type: ignore[union-attr]
    assert validaciones[0].find(f"{xm}sqref").text == "F2:F36"  # type: ignore[union-attr]
    # Los valores de la lista están en la hoja auxiliar, en el orden dado.
    listas = _hoja(contenido, "Listas")
    assert [listas.cell(f, 2).value for f in range(2, 5)] == ["A1", "B2", "C3"]

    # `openpyxl` descarta la extensión: la lectura normal no ve validación sobre F.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hoja = _hoja(contenido, HOJA)
    rangos = {str(v.sqref) for v in hoja.data_validations.dataValidation}
    assert "F2:F36" not in rangos
    assert "G2:G36" in rangos  # las demás listas siguen siendo validaciones normales


def test_tabla_se_edita_por_nombre_para_las_variantes_de_los_casos_borde() -> None:
    """FR-001-14: renombrar, quitar o repetir filas y columnas de una tabla (CB-31 a CB-35)."""
    matriz = _matriz_controlada()
    tabla = matriz.egm.tabla(1)
    tabla.renombrar_fila("Intervención F", "Intervención ajena")
    tabla.quitar_fila("Intervención E")
    tabla.duplicar_fila("Intervención D")
    tabla.duplicar_columna("Total estudios")
    tabla.renombrar_columna("Dimensión 8", "Dimensión ajena")
    tabla.quitar_columna("Dimensión 7")
    cuerpo_hoja = _hoja(matriz.a_bytes(), "EGM", valores=True)
    fila_t, col = _localizar_titulo(cuerpo_hoja, 1)
    nombres = []
    fila = fila_t + 2
    while cuerpo_hoja.cell(fila, col).value is not None:
        nombres.append(cuerpo_hoja.cell(fila, col).value)
        fila += 1
    assert nombres == [
        "Intervención A",
        "Intervención B",
        "Intervención C",
        "Intervención D",
        "Intervención D",
        "Intervención ajena",
    ]
    encabezados = [cuerpo_hoja.cell(fila_t + 1, c).value for c in range(col, col + 12)]
    assert encabezados == [
        "Intervención",
        *DIMENSIONES[:6],
        "Dimensión ajena",
        "Total estudios",
        "Total estudios",
        None,
        None,
    ]


def test_tabla_se_puede_quitar_y_la_hoja_se_puede_quitar() -> None:
    """FR-001-14: una hoja EGM sin tabla 2, o sin hoja (CB-29)."""
    matriz = _matriz_controlada()
    matriz.egm.quitar_tabla(2)
    hoja = _hoja(matriz.a_bytes(), "EGM")
    with pytest.raises(AssertionError):
        _localizar_titulo(hoja, 2)
    assert _localizar_titulo(hoja, 4)

    sin_hoja = _abrir(_matriz_controlada().quitar_hoja("EGM").a_bytes())
    assert "EGM" not in sin_hoja.sheetnames


def test_el_titulo_de_las_tablas_comparables_trae_su_frase_propia() -> None:
    """FR-001-14: contrato §7.2, frases propias de las tablas comparables en sus títulos."""
    hoja = _hoja(_matriz_controlada().a_bytes(), "EGM")
    titulos = {n: hoja.cell(*_localizar_titulo(hoja, n)).value for n in (1, 2, 4)}
    assert "número total de estudios" in titulos[1].lower()
    assert "evaluación de impacto" in titulos[2].lower()
    assert "nivel de evidencia" in titulos[4].lower()
    # Ninguna frase propia se repite en otro título comparable.
    assert "número total de estudios" not in titulos[2].lower()
    assert "evaluación de impacto" not in titulos[4].lower()
    assert "nivel de evidencia" not in titulos[1].lower()


# ================================================================================================
# T-001-06 · Archivos de carga (NFR-000-19, SC-000-19)
# ================================================================================================

LIMITE_TAMANO = 15_728_640
LIMITE_DESCOMPRIMIDO = 268_435_456


def test_archivo_de_otro_tipo_es_texto_y_no_un_paquete() -> None:
    """NFR-000-19: otro tipo de archivo (texto)."""
    contenido = archivo_de_texto()
    assert not zipfile.is_zipfile(io.BytesIO(contenido))
    contenido.decode("utf-8")  # es texto legible
    assert len(contenido) > 0


def test_extension_xlsx_con_otro_contenido() -> None:
    """NFR-000-19: nombre de libro con otro contenido: texto o un paquete que no es un libro."""
    texto = archivo_extension_xlsx_otro_contenido()
    assert not zipfile.is_zipfile(io.BytesIO(texto))
    assert texto != archivo_de_texto()

    paquete = archivo_extension_xlsx_otro_contenido("zip_sin_libro")
    assert zipfile.is_zipfile(io.BytesIO(paquete))
    with zipfile.ZipFile(io.BytesIO(paquete)) as zf:
        assert "xl/workbook.xml" not in zf.namelist()
        assert "[Content_Types].xml" not in zf.namelist()

    with pytest.raises(ValueError, match="variante"):
        archivo_extension_xlsx_otro_contenido("otra")


def test_paquete_danado() -> None:
    """NFR-000-19: un paquete dañado (cortado a la mitad) no se abre como paquete."""
    contenido = MatrizSintetica.base_valida().a_bytes_danado()
    completo = MatrizSintetica.base_valida().a_bytes()
    assert len(contenido) == len(completo) // 2
    assert contenido[:2] == b"PK"  # empieza como un paquete
    assert not zipfile.is_zipfile(io.BytesIO(contenido))
    with pytest.raises(zipfile.BadZipFile):
        zipfile.ZipFile(io.BytesIO(contenido))


@pytest.mark.parametrize("tamano", [LIMITE_TAMANO, LIMITE_TAMANO + 1])
def test_libro_de_tamano_exacto(tamano: int) -> None:
    """NFR-000-19, SC-000-19: 15 728 640 bytes exactos y un byte más; el libro se abre."""
    contenido = MatrizSintetica.base_valida().a_bytes_de_tamano(tamano)
    assert len(contenido) == tamano
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        assert paquete.testzip() is None
    libro = load_workbook(io.BytesIO(contenido), read_only=True)
    assert "Matriz bibliográfica" in libro.sheetnames
    libro.close()


def test_libro_de_tamano_exacto_es_determinista_y_menor_pide_error() -> None:
    """NFR-000-19: mismos bytes en cada generación; un tamaño menor que el mínimo se rechaza."""
    matriz = MatrizSintetica.base_valida()
    assert matriz.a_bytes_de_tamano(2_000_000) == matriz.a_bytes_de_tamano(2_000_000)
    with pytest.raises(ValueError, match="tamaño"):
        matriz.a_bytes_de_tamano(100)


def _suma_declarada(contenido: bytes) -> int:
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        return sum(i.file_size for i in paquete.infolist())


@pytest.mark.parametrize("declarado", [LIMITE_DESCOMPRIMIDO, LIMITE_DESCOMPRIMIDO + 1])
def test_libro_con_contenido_descomprimido_declarado_exacto(declarado: int) -> None:
    """NFR-000-19, SC-000-19: 268 435 456 bytes declarados y un byte más, sin materializarlos."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(declarado)
    assert _suma_declarada(contenido) == declarado
    assert len(contenido) < 1_000_000  # nada se materializó
    libro = load_workbook(io.BytesIO(contenido), read_only=True)
    assert "Matriz bibliográfica" in libro.sheetnames
    libro.close()


def test_declarado_con_datos_comprimidos_invalidos() -> None:
    """NFR-000-19 (P-001-08): el declarado se cumple aunque el relleno no se descomprima."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(
        LIMITE_DESCOMPRIMIDO + 1, datos_invalidos=True
    )
    assert _suma_declarada(contenido) == LIMITE_DESCOMPRIMIDO + 1
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        relleno = next(i for i in paquete.infolist() if i.file_size > LIMITE_DESCOMPRIMIDO // 2)
        assert relleno.compress_type == zipfile.ZIP_DEFLATED
    comprimido = _bytes_comprimidos(contenido, relleno)
    with pytest.raises(zlib.error):
        zlib.decompressobj(-15).decompress(comprimido)


def test_declarado_menor_que_lo_real_se_rechaza() -> None:
    """NFR-000-19: no se puede declarar menos que lo que ya pesan las partes."""
    with pytest.raises(ValueError, match="declarado"):
        MatrizSintetica.base_valida().a_bytes_con_descomprimido_declarado(10)


def _bytes_comprimidos(contenido: bytes, info: zipfile.ZipInfo) -> bytes:
    """Bytes de la parte en el paquete (encabezado local de 30 bytes, nombre y extra aparte)."""
    desde = info.header_offset
    largo_nombre, largo_extra = struct.unpack("<HH", contenido[desde + 26 : desde + 30])
    inicio = desde + 30 + largo_nombre + largo_extra
    return contenido[inicio : inicio + info.compress_size]


def test_parte_mayor_que_lo_declarado() -> None:
    """NFR-000-19 (NC-ARQ-1): una parte se descomprime a más de lo que declara su índice."""
    contenido = parte_mayor_que_lo_declarado()
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        infos = paquete.infolist()
    mayores = []
    for info in infos:
        if info.compress_type != zipfile.ZIP_DEFLATED:
            continue
        real = len(zlib.decompressobj(-15).decompress(_bytes_comprimidos(contenido, info)))
        if real > info.file_size:
            mayores.append((info.filename, real, info.file_size))
    assert [m[0] for m in mayores] == ["xl/worksheets/sheet1.xml"]
    _, real, declarado = mayores[0]
    assert real == 1_048_576
    assert 0 < declarado < real
    # El resto del índice es verdadero y el paquete pesa poco: el relleno es barato.
    assert len(contenido) < 100_000


def test_parte_mayor_que_lo_declarado_acepta_otro_tamano_real() -> None:
    """NFR-000-19: el tamaño real de la parte se puede elegir; uno menor que la parte se rechaza."""
    contenido = MatrizSintetica.base_valida().a_bytes_con_parte_mayor_que_lo_declarado(
        tamano_real=5_000_000
    )
    with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
        info = paquete.getinfo("xl/worksheets/sheet1.xml")
    real = len(zlib.decompressobj(-15).decompress(_bytes_comprimidos(contenido, info)))
    assert real == 5_000_000
    with pytest.raises(ValueError, match="tamaño"):
        MatrizSintetica.base_valida().a_bytes_con_parte_mayor_que_lo_declarado(tamano_real=10)


def test_archivos_de_carga_son_deterministas() -> None:
    """NFR-000-19: mismos bytes en cada generación de los archivos de carga."""
    assert archivo_de_texto() == archivo_de_texto()
    assert parte_mayor_que_lo_declarado() == parte_mayor_que_lo_declarado()
    assert archivo_extension_xlsx_otro_contenido("zip_sin_libro") == (
        archivo_extension_xlsx_otro_contenido("zip_sin_libro")
    )
    base = MatrizSintetica.base_valida()
    assert base.a_bytes_danado() == base.a_bytes_danado()
    assert base.a_bytes_con_descomprimido_declarado(LIMITE_DESCOMPRIMIDO) == (
        base.a_bytes_con_descomprimido_declarado(LIMITE_DESCOMPRIMIDO)
    )


# ================================================================================================
# T-001-07 · Catálogo de fixtures (SC-001-02; SC-000-06, SC-000-12, SC-000-17 y SC-000-18 soporte)
# ================================================================================================

# Nombres del plan 001, «Catálogo de fixtures» (copiados a mano de la tabla del plan).
NOMBRES_DEL_CATALOGO = frozenset(
    {
        "cb01_fila_solo_referencia.xlsx",
        "cb02_empirico_sin_intervencion.xlsx",
        "cb03_empirico_sin_dimensiones.xlsx",
        "cb04_solo_secundaria.xlsx",
        "cb05_sin_nivel.xlsx",
        "cb06_no_empirico_tablero.xlsx",
        "cb07_misma_intervencion.xlsx",
        "cb08_no_empirico_con_intervencion.xlsx",
        "cb09_dimension_fuera_de_rango.xlsx",
        "cb10_fuera_de_lista.xlsx",
        "cb11_enfoque_sin_prefijo.xlsx",
        "cb12_250_documentos.xlsx",
        "cb13_numero_vacio_o_repetido.xlsx",
        "cb14_sin_nivel_de_evidencia.xlsx",
        "cb15_sin_hoja_matriz.xlsx",
        "cb16_otro_tipo.txt",
        "cb16_extension_xlsx_otro_contenido.xlsx",
        "cb16_danado.xlsx",
        "cb18_columna_observaciones.xlsx",
        "cb19_columna_1_0_fuera.xlsx",
        "cb20_sin_ancla_empirico.xlsx",
        "cb21_sin_ancla_ie.xlsx",
        "cb22_sin_no_aplica.xlsx",
        "cb23_varios_empiricos.xlsx",
        "cb24_nivel_sin_lista.xlsx",
        "cb24_principal_sin_lista.xlsx",
        "cb24_secundaria_sin_lista.xlsx",
        "cb25_fuente_sin_lista.xlsx",
        "cb25_metodologia_sin_lista.xlsx",
        "cb26_tipo_sin_lista.xlsx",
        "cb27_anio_no_numerico.xlsx",
        "cb28_tipo_vacio_o_fuera.xlsx",
        "cb29_sin_hoja_egm.xlsx",
        "cb29_titulo_cambiado.xlsx",
        "cb30_sin_valores_guardados.xlsx",
        "cb31_categoria_nueva.xlsx",
        "cb32_categoria_solo_en_hoja.xlsx",
        "cb33_parcial_sin_diferencia.xlsx",
        "cb33_parcial_con_diferencia.xlsx",
        "cb34_sin_total.xlsx",
        "cb34_total_repetido.xlsx",
        "cb35_nombre_repetido.xlsx",
        "cb36_intervencion_nivel_agregados.xlsx",
        "cb37_dimension_agregada.xlsx",
        "cb38_bloque_invertido.xlsx",
        "cb38_bloque_vacio.xlsx",
        "cb39_rol_en_bloque.xlsx",
        "cb40_retiradas.xlsx",
        "cb41_texto_1.xlsx",
        "base_valida.xlsx",
        "esc_1_2_cuatro_celdas.xlsx",
        "esc_1_6_enfoque.xlsx",
        "esc_1_8_orden_alterado.xlsx",
        "esc_2_1_fuera_de_lista_n3.xlsx",
        "esc_2_5_sin_delimitador_final.xlsx",
        "esc_2_13_anio_sf_n4.xlsx",
        "esc_2_15_tipo_sin_lista_cuatro_docs.xlsx",
        "esc_2_16_tipo_fuera_de_lista_n3.xlsx",
        "esc_3_1_coincide.xlsx",
        "esc_3_2_difiere_g_igual_h.xlsx",
        "esc_3_5_filas_vacias_antes.xlsx",
        "esc_3_7_titulos_1_2_4.xlsx",
        "esc_3_9_nombres_repetidos_entre_tablas.xlsx",
        "esc_3_10_total_entre_dimensiones.xlsx",
        "esc_3_17_espacios.xlsx",
        "validacion_x14.xlsx",
        "sc000_06_agregadas.xlsx",
        "sc000_06_retiradas.xlsx",
        "sc000_06_renombradas.xlsx",
        "sc000_12_otro_nombre_v4.xlsx",
        "instancia_ejemplo.xlsx",
        "marcadores.xlsx",
        "sesion_a.xlsx",
        "sesion_b.xlsx",
    }
)
# Fixtures que pesan cerca de los límites de NFR-000-19: solo en memoria, nunca guardados.
NOMBRES_EN_MEMORIA = frozenset(
    {
        "cb16_tamano_exacto",
        "cb16_tamano_mas_uno",
        "cb17_declarado_exacto",
        "cb17_declarado_mas_uno",
        "parte_mayor_que_lo_declarado",
    }
)

TIPO = "Tipo de documento"
PRINCIPAL = "Tipo de intervención (EGM)"
SECUNDARIA = "Intervención secundaria (opcional)"
NIVEL = "Nivel de evidencia"
INICIAL = "Dimensiones evaluadas / propuestas"
FINAL = "Indicadores o categorías analíticas"
TOTAL = "Total estudios"
NO_APLICA_INTERVENCION = "No aplica (documento teórico/metodológico/normativo)"
NO_APLICA_NIVEL = "No aplica (marco conceptual/normativo/metodológico)"
LISTAS_DE_LA_BASE = frozenset(
    {"Tipo de documento", "Tipo de fuente", PRINCIPAL, SECUNDARIA, "Metodología", NIVEL}
    | set(DIMENSIONES)
)


@pytest.fixture(scope="module")
def catalogo() -> dict[str, bytes]:
    return generar_catalogo()


def _docs(contenido: bytes) -> list[dict[str, object]]:
    """Cada documento de la hoja de la matriz (encabezado → valor y `_fila`), sin filas vacías."""
    hoja = _hoja(contenido, HOJA)
    encabezados = [c.value for c in hoja[1]]
    docs: list[dict[str, object]] = []
    for fila in hoja.iter_rows(min_row=2):
        valores = {str(e): c.value for e, c in zip(encabezados, fila, strict=False) if e}
        if any(v is not None for v in valores.values()):
            docs.append({**valores, "_fila": fila[0].row})
    return docs


def _doc(docs: list[dict[str, object]], numero: object) -> dict[str, object]:
    return next(d for d in docs if d["N°"] == numero)


def _listas(contenido: bytes) -> dict[str, list[str]]:
    """Encabezado → valores de su lista de validación, escrita o por rango (no lee `x14`)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        libro = _abrir(contenido)
    hoja = libro[HOJA]
    por_letra = {get_column_letter(c.column): str(c.value) for c in hoja[1] if c.value}
    listas: dict[str, list[str]] = {}
    for validacion in hoja.data_validations.dataValidation:
        formula = validacion.formula1
        if formula.startswith('"'):
            valores = formula.strip('"').split(",")
        else:
            nombre, rango = formula.split("!")
            celdas = libro[nombre.strip("'")][rango.replace("$", "")]
            valores = [c.value for fila in celdas for c in fila]
        for area in str(validacion.sqref).split():
            letra = re.match(r"[A-Z]+", area)
            assert letra is not None
            listas[por_letra[letra.group()]] = valores
    return listas


def _encabezados(contenido: bytes) -> list[object]:
    return _fila_1(contenido)


def _guardados(contenido: bytes, numero: int) -> dict[str, dict[str, object]]:
    return _leer_tabla(_hoja(contenido, "EGM", valores=True), numero)


def _nombres_de_tabla(contenido: bytes, numero: int) -> list[object]:
    """Nombres de fila de la tabla, en orden y con repetidos."""
    hoja = _hoja(contenido, "EGM")
    fila_t, col = _localizar_titulo(hoja, numero)
    nombres = []
    fila = fila_t + 2
    while hoja.cell(fila, col).value is not None:
        nombres.append(hoja.cell(fila, col).value)
        fila += 1
    return nombres


def _encabezados_de_tabla(contenido: bytes, numero: int) -> list[object]:
    hoja = _hoja(contenido, "EGM")
    fila_t, col = _localizar_titulo(hoja, numero)
    encabezados = []
    columna = col + 1
    while hoja.cell(fila_t + 1, columna).value is not None:
        encabezados.append(hoja.cell(fila_t + 1, columna).value)
        columna += 1
    return encabezados


def _formulas(contenido: bytes) -> list[str]:
    hoja = _hoja(contenido, "EGM")
    return [
        str(c.value)
        for fila in hoja.iter_rows()
        for c in fila
        if isinstance(c.value, str) and c.value.startswith("=")
    ]


def _estudios_hoja(contenido: bytes) -> dict[str, tuple[object, ...]]:
    """Tabla 1 guardada: intervención → (dimensiones 1 a 8, total)."""
    return {
        nombre: (*(fila[d] for d in DIMENSIONES), fila[TOTAL])
        for nombre, fila in _guardados(contenido, 1).items()
    }


CEROS = (0, 0, 0, 0, 0, 0, 0, 0, 0)
# Tabla 1 de `base_valida`, a mano: N.º 2 (G=A, H=B; dimensiones 1 y 2), N.º 3 (G=C; 3 y 4),
# N.º 4 (G=A; 1). Cada fila: dimensiones 1 a 8 y «Total estudios».
TABLA_1_BASE = {
    "Intervención A": (2, 1, 0, 0, 0, 0, 0, 0, 2),
    "Intervención B": (1, 1, 0, 0, 0, 0, 0, 0, 1),
    "Intervención C": (0, 0, 1, 1, 0, 0, 0, 0, 1),
    "Intervención D": CEROS,
    "Intervención E": CEROS,
    "Intervención F": CEROS,
}


# ---- P-001-01 ----------------------------------------------------------------------------------


def test_p_001_01_existe_un_fixture_por_cada_caso_borde(catalogo: dict[str, bytes]) -> None:
    """SC-001-02 (P-001-01): un fixture por cada CB-01 a CB-41, con los nombres del plan."""
    assert set(catalogo) == NOMBRES_DEL_CATALOGO
    assert set(CATALOGO) == NOMBRES_DEL_CATALOGO
    assert set(EN_MEMORIA) == NOMBRES_EN_MEMORIA
    for numero in range(1, 42):
        prefijo = f"cb{numero:02d}_"
        assert any(n.startswith(prefijo) for n in set(CATALOGO) | set(EN_MEMORIA)), prefijo
    assert all(isinstance(c, bytes) and len(c) > 0 for c in catalogo.values())


def test_p_001_01_dos_generaciones_dan_los_mismos_bytes(catalogo: dict[str, bytes]) -> None:
    """SC-001-02 (P-001-01): dos generaciones del catálogo dan exactamente los mismos bytes."""
    segunda = generar_catalogo()
    huellas = {n: hashlib.sha256(c).hexdigest() for n, c in catalogo.items()}
    assert huellas == {n: hashlib.sha256(c).hexdigest() for n, c in segunda.items()}
    # Los fixtures en memoria que pesan poco también son deterministas.
    assert EN_MEMORIA["cb17_declarado_exacto"]() == EN_MEMORIA["cb17_declarado_exacto"]()
    assert EN_MEMORIA["parte_mayor_que_lo_declarado"]() == parte_mayor_que_lo_declarado()


def test_p_001_01_ningun_fixture_se_lee_de_los_datos_reales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SC-001-02 (P-001-01): generar el catálogo completo no abre ninguna ruta de la matriz real."""
    abiertos: list[str] = []
    abrir_real = builtins.open

    def espia(archivo: object, *args: object, **kwargs: object) -> object:
        abiertos.append(str(archivo))
        return abrir_real(archivo, *args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(builtins, "open", espia)
    monkeypatch.setattr(io, "open", espia)
    generar_catalogo()
    # `openpyxl` abre archivos temporales con sufijo al azar: se compara por carpeta, no por texto.
    assert [r for r in abiertos if "raw" in (p.lower() for p in Path(r).parts)] == []


def test_los_fixtures_guardados_son_los_del_catalogo(catalogo: dict[str, bytes]) -> None:
    """SC-001-02: lo que hay en `data/fixtures/` es lo que genera el catálogo, y pesa poco."""
    carpeta = carpeta_de_fixtures()
    for nombre, contenido in catalogo.items():
        assert (carpeta / nombre).read_bytes() == contenido, nombre
    assert max(len(c) for c in catalogo.values()) < 200_000
    # Los fixtures cercanos a los límites de NFR-000-19 no se guardan.
    for nombre in EN_MEMORIA:
        assert not list(carpeta.glob(f"{nombre}*")), nombre


def test_escribir_catalogo_escribe_los_mismos_bytes_del_catalogo(
    tmp_path: Path, catalogo: dict[str, bytes]
) -> None:
    """SC-001-02: `escribir_catalogo` escribe cada fixture con los mismos bytes y su tamaño."""
    escritos = escribir_catalogo(tmp_path / "directo")
    assert set(escritos) == NOMBRES_DEL_CATALOGO
    for nombre, contenido in catalogo.items():
        assert (tmp_path / "directo" / nombre).read_bytes() == contenido, nombre
        assert escritos[nombre] == len(contenido)


def test_main_escribe_en_la_carpeta_indicada_y_la_de_fixtures_por_defecto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """SC-001-02: `main` escribe en `--destino`, o en `data/fixtures/` si no se indica."""
    dos = {"base_valida.xlsx": CATALOGO["base_valida.xlsx"], "cb16_otro_tipo.txt": archivo_de_texto}
    monkeypatch.setattr(modulo_constructor, "CATALOGO", dos)
    assert main(["--destino", str(tmp_path)]) == 0
    assert {p.name for p in tmp_path.iterdir()} == set(dos)
    assert "2 archivos escritos" in capsys.readouterr().out
    assert carpeta_de_fixtures() == Path(__file__).resolve().parents[2] / "data" / "fixtures"


def test_el_comando_python_m_tests_constructor_escribe_en_la_carpeta_indicada(
    tmp_path: Path, catalogo: dict[str, bytes]
) -> None:
    """SC-001-02: el comando documentado funciona en otro proceso y repite los mismos bytes."""
    raiz = Path(__file__).resolve().parents[2]
    subprocess.run(
        [sys.executable, "-m", "tests.constructor", "--destino", str(tmp_path)],
        cwd=raiz,
        check=True,
        capture_output=True,
    )
    assert {p.name for p in tmp_path.iterdir()} == NOMBRES_DEL_CATALOGO
    for nombre, contenido in catalogo.items():
        assert (tmp_path / nombre).read_bytes() == contenido, nombre


def test_reemplazar_valor_cambia_las_celdas_de_la_columna_que_valen_lo_indicado() -> None:
    """SC-001-02 (soporte): `reemplazar_valor` cambia solo las celdas iguales de la columna."""
    matriz = MatrizSintetica.base_valida().reemplazar_valor(PRINCIPAL, "Intervención A", "Otra")
    docs = _docs(matriz.a_bytes())
    assert [d[PRINCIPAL] for d in docs] == [
        NO_APLICA_INTERVENCION,
        "Otra",
        "Intervención C",
        "Otra",
        NO_APLICA_INTERVENCION,
    ]


# ---- Casos borde CB-01 a CB-15 -----------------------------------------------------------------


def test_cb01_fila_solo_con_numero_y_referencia(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-01: una fila nueva con solo N.º y referencia (sin tipo de documento)."""
    docs = _docs(catalogo["cb01_fila_solo_referencia.xlsx"])
    assert [d["N°"] for d in docs] == [1, 2, 3, 4, 5, 6]
    llenas = {k for k, v in docs[-1].items() if v is not None}
    assert llenas == {"N°", "Referencia APA", "_fila"}


def test_cb02_empirico_sin_intervencion(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-02: estudio empírico sin intervención y con una dimensión en 1."""
    d = _docs(catalogo["cb02_empirico_sin_intervencion.xlsx"])[-1]
    assert d[TIPO] == EMPIRICO
    assert d[PRINCIPAL] is None
    assert d[SECUNDARIA] is None
    assert 1 in [d[x] for x in DIMENSIONES]


def test_cb03_empirico_con_intervencion_y_sin_dimensiones(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-03: empírico con intervención y ninguna dimensión en 1; la hoja lo cuenta."""
    contenido = catalogo["cb03_empirico_sin_dimensiones.xlsx"]
    d = _docs(contenido)[-1]
    assert d[TIPO] == EMPIRICO
    assert d[PRINCIPAL] == "Intervención D"
    assert all(d[x] in (0, None) for x in DIMENSIONES)
    # «Total estudios» de la hoja cuenta al estudio sin dimensiones; ninguna dimensión lo cuenta.
    assert _estudios_hoja(contenido)["Intervención D"] == (0, 0, 0, 0, 0, 0, 0, 0, 1)


def test_cb04_principal_vacia_y_secundaria_diligenciada(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-04: empírico con principal vacía, secundaria diligenciada y dimensión en 1."""
    contenido = catalogo["cb04_solo_secundaria.xlsx"]
    d = _docs(contenido)[-1]
    assert d[TIPO] == EMPIRICO
    assert d[PRINCIPAL] is None
    assert d[SECUNDARIA] == "Intervención D"
    assert [d[x] for x in DIMENSIONES].count(1) >= 1
    # La hoja lo cuenta por su secundaria (segundo sumando de T1).
    assert _estudios_hoja(contenido)["Intervención D"][8] == 1


def test_cb05_estudio_del_mapa_sin_nivel_o_con_no_aplica(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-05: dos estudios del mapa, uno sin nivel y otro con «No aplica…»."""
    docs = _docs(catalogo["cb05_sin_nivel.xlsx"])
    sin_nivel, no_aplica = docs[-2], docs[-1]
    for d in (sin_nivel, no_aplica):
        assert d[TIPO] == EMPIRICO
        assert d[PRINCIPAL] == "Intervención D"
        assert 1 in [d[x] for x in DIMENSIONES]
    assert sin_nivel[NIVEL] is None
    assert str(no_aplica[NIVEL]).startswith("No aplica")


def test_cb06_no_empirico_en_las_cifras_de_documentos(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-06: documentos no empíricos con datos propios, uno sin nivel de evidencia."""
    docs = _docs(catalogo["cb06_no_empirico_tablero.xlsx"])
    nuevos = docs[5:]
    assert len(nuevos) == 2
    assert all(d[TIPO] != EMPIRICO and d[TIPO] is not None for d in nuevos)
    assert any(d[NIVEL] is None for d in nuevos)
    assert all(d["Año"] is not None and d["Referencia APA"] for d in nuevos)


def test_cb07_misma_intervencion_en_principal_y_secundaria(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-07: un empírico con G = H; la hoja lo cuenta dos veces."""
    contenido = catalogo["cb07_misma_intervencion.xlsx"]
    d = _docs(contenido)[-1]
    assert d[TIPO] == EMPIRICO
    assert d[PRINCIPAL] == d[SECUNDARIA] == "Intervención D"
    assert _estudios_hoja(contenido)["Intervención D"] == (0, 0, 0, 0, 2, 0, 0, 0, 2)


def test_cb08_no_empirico_con_intervencion(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-08: documento no empírico con intervención distinta de «No aplica»."""
    contenido = catalogo["cb08_no_empirico_con_intervencion.xlsx"]
    d = _docs(contenido)[-1]
    assert d[TIPO] != EMPIRICO
    assert d[PRINCIPAL] == "Intervención D"
    # No entra a la hoja: ninguna celda de la intervención D cuenta.
    assert _estudios_hoja(contenido)["Intervención D"] == CEROS


def test_cb09_dimension_fuera_de_rango(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-09: dimensiones con 2 y con texto «Sí», fuera de {0, 1, vacío}."""
    d = _docs(catalogo["cb09_dimension_fuera_de_rango.xlsx"])[-1]
    assert d["Dimensión 2"] == 2
    assert d["Dimensión 3"] == "Sí"
    assert d["Dimensión 5"] == 1


def test_cb10_valor_fuera_de_lista(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-10: valores de fuente, metodología y nivel que no están en su lista."""
    contenido = catalogo["cb10_fuera_de_lista.xlsx"]
    d = _docs(contenido)[-1]
    listas = _listas(contenido)
    for columna in ("Tipo de fuente", "Metodología", NIVEL):
        assert d[columna] is not None
        assert d[columna] not in listas[columna], columna


def test_cb11_enfoque_sin_prefijo_valido(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-11: tres textos de enfoque que no empiezan por Sí, No ni Parcial."""
    docs = _docs(catalogo["cb11_enfoque_sin_prefijo.xlsx"])[5:]
    textos = [str(d["Enfoque de género/diferencial"]) for d in docs]
    assert len(textos) == 3
    primeras = [t.split()[0].strip(":,.").lower() for t in textos]
    assert not set(primeras) & {"sí", "no", "parcial"}
    assert any(t.startswith("Si bien") for t in textos)  # «Si» sin tilde
    assert any(t.startswith("Nota:") for t in textos)


def test_cb12_250_documentos_y_formulas_hasta_la_fila_200(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-12: 250 documentos (filas 2 a 251); las fórmulas llegan a la fila 200."""
    contenido = catalogo["cb12_250_documentos.xlsx"]
    docs = _docs(contenido)
    assert [d["N°"] for d in docs] == list(range(1, 251))
    assert docs[-1]["_fila"] == 251
    formulas = _formulas(contenido)
    assert len(formulas) > 100
    assert all("$200" in f and "$201" not in f for f in formulas)
    # Hay estudios empíricos más allá de la fila 200.
    assert any(d[TIPO] == EMPIRICO and int(str(d["_fila"])) > 200 for d in docs)
    # Las validaciones cubren los 250 documentos.
    hoja = _hoja(contenido, HOJA)
    assert all(str(v.sqref).endswith("251") for v in hoja.data_validations.dataValidation)


def test_cb13_numero_vacio_con_contenido_y_numero_repetido(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-13: una fila con N.º vacío y contenido, y otra que repite el N.º 3."""
    docs = _docs(catalogo["cb13_numero_vacio_o_repetido.xlsx"])
    assert [d["N°"] for d in docs] == [1, 2, 3, 4, 5, None, 3]
    sin_numero = docs[5]
    assert sin_numero[TIPO] == EMPIRICO
    assert sin_numero["Referencia APA"]


def test_cb14_sin_el_encabezado_nivel_de_evidencia(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-14: falta «Nivel de evidencia»; los demás encabezados siguen."""
    encabezados = _encabezados(catalogo["cb14_sin_nivel_de_evidencia.xlsx"])
    assert encabezados == [e for e in ENCABEZADOS_BASE if e != NIVEL]


def test_cb15_sin_la_hoja_de_la_matriz(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-15: no existe la hoja «Matriz bibliográfica»; las demás sí."""
    nombres = _abrir(catalogo["cb15_sin_hoja_matriz.xlsx"]).sheetnames
    assert "Matriz bibliográfica" not in nombres
    assert "EGM" in nombres
    assert "Instrucciones" in nombres


# ---- Casos borde CB-16 a CB-30 -----------------------------------------------------------------


def test_cb16_otro_tipo_extension_enganosa_y_danado(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-16: texto, nombre de libro con otro contenido y paquete dañado."""
    texto = catalogo["cb16_otro_tipo.txt"]
    assert not zipfile.is_zipfile(io.BytesIO(texto))
    texto.decode("utf-8")
    otro = catalogo["cb16_extension_xlsx_otro_contenido.xlsx"]
    assert not zipfile.is_zipfile(io.BytesIO(otro))
    danado = catalogo["cb16_danado.xlsx"]
    assert danado[:2] == b"PK"
    assert not zipfile.is_zipfile(io.BytesIO(danado))


def test_cb16_y_cb17_en_memoria_tienen_los_tamanos_de_nfr_000_19() -> None:
    """SC-001-02, CB-16 y CB-17: exacto y +1, solo en memoria (tamaño y declarado al byte)."""
    assert len(EN_MEMORIA["cb16_tamano_exacto"]()) == LIMITE_TAMANO
    assert len(EN_MEMORIA["cb16_tamano_mas_uno"]()) == LIMITE_TAMANO + 1
    assert _suma_declarada(EN_MEMORIA["cb17_declarado_exacto"]()) == LIMITE_DESCOMPRIMIDO
    assert _suma_declarada(EN_MEMORIA["cb17_declarado_mas_uno"]()) == LIMITE_DESCOMPRIMIDO + 1


def test_cb18_columna_ajena_sin_lista(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-18: «Observaciones», fuera del bloque y sin lista `1,0`."""
    contenido = catalogo["cb18_columna_observaciones.xlsx"]
    assert _encabezados(contenido) == [*ENCABEZADOS_BASE, "Observaciones"]
    assert "Observaciones" not in _listas(contenido)
    assert any(d["Observaciones"] for d in _docs(contenido))


def test_cb19_columna_ajena_con_lista_1_0(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-19: una columna fuera del bloque con lista `1,0`."""
    contenido = catalogo["cb19_columna_1_0_fuera.xlsx"]
    encabezados = _encabezados(contenido)
    extra = [e for e in encabezados if e not in ENCABEZADOS_BASE]
    assert len(extra) == 1
    assert encabezados.index(extra[0]) > encabezados.index(FINAL)
    assert _listas(contenido)[str(extra[0])] == ["1", "0"]


def test_cb20_sin_ancla_de_estudio_empirico(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-20: ningún valor de la lista de tipo empieza por «Estudio empírico»."""
    contenido = catalogo["cb20_sin_ancla_empirico.xlsx"]
    lista = _listas(contenido)[TIPO]
    assert len(lista) == 4
    assert not [v for v in lista if v.startswith("Estudio empírico")]
    assert all(d[TIPO] in lista for d in _docs(contenido))


def test_cb21_sin_ancla_de_evaluacion_de_impacto(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-21: la lista de nivel no incluye «Evaluación de impacto»."""
    contenido = catalogo["cb21_sin_ancla_ie.xlsx"]
    lista = _listas(contenido)[NIVEL]
    assert len(lista) == 4
    assert "Evaluación de impacto" not in lista
    assert all(d[NIVEL] in lista for d in _docs(contenido))


def test_cb22_ninguna_lista_con_no_aplica(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-22: la lista de nivel no trae ningún valor que empiece por «No aplica»."""
    contenido = catalogo["cb22_sin_no_aplica.xlsx"]
    lista = _listas(contenido)[NIVEL]
    assert lista == ["Evaluación de impacto", "Estudio de caso", "Informe de proyecto"]
    assert not any(str(d[NIVEL]).startswith("No aplica") for d in _docs(contenido))


def test_cb23_varios_tipos_empiezan_por_estudio_empirico(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-23: dos valores de la lista de tipo empiezan por «Estudio empírico»."""
    contenido = catalogo["cb23_varios_empiricos.xlsx"]
    lista = _listas(contenido)[TIPO]
    assert len([v for v in lista if v.startswith("Estudio empírico")]) == 2
    assert _docs(contenido)[-1][TIPO] in lista


@pytest.mark.parametrize(
    ("archivo", "columna"),
    [
        ("cb24_nivel_sin_lista.xlsx", NIVEL),
        ("cb24_principal_sin_lista.xlsx", PRINCIPAL),
        ("cb24_secundaria_sin_lista.xlsx", SECUNDARIA),
        ("cb25_fuente_sin_lista.xlsx", "Tipo de fuente"),
        ("cb25_metodologia_sin_lista.xlsx", "Metodología"),
        ("cb26_tipo_sin_lista.xlsx", TIPO),
    ],
)
def test_cb24_cb25_cb26_una_columna_sin_lista(
    catalogo: dict[str, bytes], archivo: str, columna: str
) -> None:
    """SC-001-02, CB-24, CB-25 y CB-26: una sola columna categórica sin lista de validación."""
    assert set(_listas(catalogo[archivo])) == LISTAS_DE_LA_BASE - {columna}


def test_cb26_tipo_sin_lista_con_un_valor_distinto_del_ancla(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-26: sin lista de tipo, hay un valor no vacío distinto del ancla."""
    docs = _docs(catalogo["cb26_tipo_sin_lista.xlsx"])
    assert docs[-1][TIPO] == "Marco teórico"


def test_cb27_anio_no_numerico(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-27: «s. f.» y un año escrito como texto."""
    docs = _docs(catalogo["cb27_anio_no_numerico.xlsx"])
    assert [d["Año"] for d in docs[5:]] == ["s. f.", "2019"]


def test_cb28_tipo_vacio_o_fuera_de_lista(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-28: un documento con tipo vacío y otro con tipo fuera de la lista."""
    contenido = catalogo["cb28_tipo_vacio_o_fuera.xlsx"]
    vacio, fuera = _docs(contenido)[5:]
    assert vacio[TIPO] is None
    assert vacio["Referencia APA"]
    assert fuera[TIPO] is not None
    assert fuera[TIPO] not in _listas(contenido)[TIPO]


def test_cb29_sin_hoja_egm_y_titulo_cambiado(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-29: hoja EGM ausente; y hoja con el título de una tabla cambiado."""
    assert "EGM" not in _abrir(catalogo["cb29_sin_hoja_egm.xlsx"]).sheetnames
    hoja = _hoja(catalogo["cb29_titulo_cambiado.xlsx"], "EGM")
    titulos = {n: str(hoja.cell(*_localizar_titulo(hoja, n)).value).lower() for n in (1, 2, 4)}
    assert "número total de estudios" not in titulos[1]
    assert "evaluación de impacto" in titulos[2]
    assert "nivel de evidencia" in titulos[4]


def test_cb30_sin_valores_guardados(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-30: la hoja EGM trae las fórmulas y ningún valor guardado."""
    n_formulas, n_con_valor = _contar_formulas(catalogo["cb30_sin_valores_guardados.xlsx"])
    assert n_formulas > 100
    assert n_con_valor == 0


# ---- Casos borde CB-31 a CB-41 -----------------------------------------------------------------


def test_cb31_intervencion_en_la_lista_sin_fila_en_la_hoja(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-31: «Intervención G» en las listas y en un estudio, sin fila en las tablas."""
    contenido = catalogo["cb31_categoria_nueva.xlsx"]
    listas = _listas(contenido)
    assert "Intervención G" in listas[PRINCIPAL]
    assert "Intervención G" in listas[SECUNDARIA]
    assert _docs(contenido)[-1][PRINCIPAL] == "Intervención G"
    for tabla in (1, 2):
        assert _nombres_de_tabla(contenido, tabla) == INTERVENCIONES


def test_cb32_fila_de_la_hoja_cuya_intervencion_ya_no_esta_en_la_lista(
    catalogo: dict[str, bytes],
) -> None:
    """SC-001-02, CB-32: «Intervención F» sale de las listas y sigue como fila de la hoja."""
    contenido = catalogo["cb32_categoria_solo_en_hoja.xlsx"]
    listas = _listas(contenido)
    assert "Intervención F" not in listas[PRINCIPAL]
    assert "Intervención F" not in listas[SECUNDARIA]
    assert not any("Intervención F" in (d[PRINCIPAL], d[SECUNDARIA]) for d in _docs(contenido))
    assert "Intervención F" in _nombres_de_tabla(contenido, 1)
    assert _estudios_hoja(contenido) == TABLA_1_BASE  # los demás valores, correctos


def test_cb33_parcial_sin_diferencia(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-33: la tabla 1 trae solo algunos valores guardados, todos correctos."""
    contenido = catalogo["cb33_parcial_sin_diferencia.xlsx"]
    tabla = _guardados(contenido, 1)
    assert tabla["Intervención A"] == {**_fila_con(2, 1), "Total estudios": 2}
    assert tabla["Intervención B"] == {**_fila_con(1, 1), "Total estudios": 1}
    for letra in "CDEF":
        assert all(v is None for v in tabla[f"Intervención {letra}"].values())
    # La tabla 2 conserva todos sus valores.
    t2 = _guardados(contenido, 2)
    assert all(isinstance(v, int) for fila in t2.values() for v in fila.values())


def test_cb33_parcial_con_diferencia(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-33: igual que el parcial sin diferencia, con un valor distinto del conteo."""
    parcial = _guardados(catalogo["cb33_parcial_con_diferencia.xlsx"], 1)
    sin = _guardados(catalogo["cb33_parcial_sin_diferencia.xlsx"], 1)
    diferentes = [
        (nombre, columna)
        for nombre in parcial
        for columna in parcial[nombre]
        if parcial[nombre][columna] != sin[nombre][columna]
    ]
    assert diferentes == [("Intervención A", "Dimensión 1")]
    assert parcial["Intervención A"]["Dimensión 1"] == 5  # el conteo correcto es 2


def test_cb34_sin_total_y_total_repetido(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-34: la tabla 1 sin «Total estudios» y con «Total estudios» dos veces."""
    sin_total = catalogo["cb34_sin_total.xlsx"]
    assert _encabezados_de_tabla(sin_total, 1) == DIMENSIONES
    assert _encabezados_de_tabla(sin_total, 2) == [*DIMENSIONES, TOTAL]
    repetido = catalogo["cb34_total_repetido.xlsx"]
    assert _encabezados_de_tabla(repetido, 1) == [*DIMENSIONES, TOTAL, TOTAL]
    assert _encabezados_de_tabla(repetido, 2) == [*DIMENSIONES, TOTAL]


def test_cb35_nombre_repetido_dentro_de_una_tabla(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-35: la tabla 1 repite la fila «Intervención D»."""
    contenido = catalogo["cb35_nombre_repetido.xlsx"]
    assert _nombres_de_tabla(contenido, 1) == [
        "Intervención A",
        "Intervención B",
        "Intervención C",
        "Intervención D",
        "Intervención D",
        "Intervención E",
        "Intervención F",
    ]
    assert _nombres_de_tabla(contenido, 2) == INTERVENCIONES


def test_cb36_intervencion_y_nivel_agregados(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-36: una intervención y un nivel nuevos en las listas, usados por un estudio."""
    contenido = catalogo["cb36_intervencion_nivel_agregados.xlsx"]
    listas = _listas(contenido)
    assert listas[PRINCIPAL] == [*INTERVENCIONES, "Intervención G", NO_APLICA_INTERVENCION]
    assert listas[NIVEL] == [*NIVELES, "Estudio cuasiexperimental", NO_APLICA_NIVEL]
    d = _docs(contenido)[-1]
    assert d[PRINCIPAL] == "Intervención G"
    assert d[NIVEL] == "Estudio cuasiexperimental"
    assert _nombres_de_tabla(contenido, 1) == INTERVENCIONES  # la hoja no la tiene


def test_cb37_dimension_agregada_con_y_sin_lista(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-37: dos columnas nuevas dentro del bloque, una con `1,0` y otra sin lista."""
    contenido = catalogo["cb37_dimension_agregada.xlsx"]
    encabezados = _encabezados(contenido)
    inicio, fin = encabezados.index(INICIAL), encabezados.index(FINAL)
    assert encabezados[inicio + 1 : fin] == [
        *DIMENSIONES[:4],
        "Dimensión nueva",
        *DIMENSIONES[4:],
        "Dimensión sin lista",
    ]
    listas = _listas(contenido)
    assert listas["Dimensión nueva"] == ["1", "0"]
    assert "Dimensión sin lista" not in listas


def test_cb38_bloque_invertido_y_bloque_vacio(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-38: el delimitador final antes del inicial, y ninguna columna entre ellos."""
    invertido = _encabezados(catalogo["cb38_bloque_invertido.xlsx"])
    assert invertido.index(FINAL) < invertido.index(INICIAL)
    vacio = _encabezados(catalogo["cb38_bloque_vacio.xlsx"])
    assert vacio.index(FINAL) == vacio.index(INICIAL) + 1
    assert not set(DIMENSIONES) & set(vacio)


def test_cb39_encabezado_de_rol_dentro_del_bloque(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-39: «Metodología» (un rol) queda entre los dos delimitadores."""
    encabezados = _encabezados(catalogo["cb39_rol_en_bloque.xlsx"])
    inicio, fin = encabezados.index(INICIAL), encabezados.index(FINAL)
    assert "Metodología" in encabezados[inicio + 1 : fin]
    assert sorted(encabezados, key=str) == sorted(ENCABEZADOS_BASE, key=str)


def test_cb40_categorias_y_dimension_retiradas(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-40: intervención, nivel y dimensión retirados; filas que aún los usan."""
    contenido = catalogo["cb40_retiradas.xlsx"]
    listas = _listas(contenido)
    assert "Intervención C" not in listas[PRINCIPAL]
    assert "Intervención C" not in listas[SECUNDARIA]
    assert "Informe de proyecto" not in listas[NIVEL]
    assert "Dimensión 8" not in _encabezados(contenido)
    docs = _docs(contenido)
    assert _doc(docs, 3)[PRINCIPAL] == "Intervención C"  # sigue usando el valor retirado
    assert _doc(docs, 4)[NIVEL] == "Informe de proyecto"
    # La hoja conserva la fila y la columna retiradas.
    assert "Intervención C" in _nombres_de_tabla(contenido, 1)
    assert "Dimensión 8" in _encabezados_de_tabla(contenido, 1)


def test_cb41_numero_escrito_como_texto(catalogo: dict[str, bytes]) -> None:
    """SC-001-02, CB-41: «1» como texto en una dimensión; la hoja guardada lo cuenta."""
    contenido = catalogo["cb41_texto_1.xlsx"]
    d = _doc(_docs(contenido), 3)
    assert d["Dimensión 3"] == "1"
    assert d["Dimensión 4"] == 1
    # La hoja cuenta el texto «1» (como Excel): la celda C × Dimensión 3 vale 1.
    assert _estudios_hoja(contenido)["Intervención C"] == (0, 0, 1, 1, 0, 0, 0, 0, 1)


# ---- Fixtures de escenarios y criterios ---------------------------------------------------------


def test_base_valida_del_catalogo(catalogo: dict[str, bytes]) -> None:
    """SC-001-02: `base_valida.xlsx` trae los 17 roles, 8 dimensiones y la hoja con valores."""
    contenido = catalogo["base_valida.xlsx"]
    assert contenido == MatrizSintetica.base_valida().a_bytes()
    assert _encabezados(contenido) == ENCABEZADOS_BASE
    assert _estudios_hoja(contenido) == TABLA_1_BASE


def test_esc_1_2_un_estudio_en_cuatro_celdas(catalogo: dict[str, bytes]) -> None:
    """US-001-1.2: un estudio empírico, dos intervenciones distintas y dos dimensiones en 1."""
    contenido = catalogo["esc_1_2_cuatro_celdas.xlsx"]
    docs = _docs(contenido)
    assert len(docs) == 1
    d = docs[0]
    assert d[TIPO] == EMPIRICO
    assert d[PRINCIPAL] != d[SECUNDARIA]
    assert d[PRINCIPAL] is not None
    assert d[SECUNDARIA] is not None
    assert [d[x] for x in DIMENSIONES].count(1) == 2
    # La hoja lo cuenta en 4 celdas: 2 intervenciones por 2 dimensiones.
    assert sum(sum(int(str(x)) for x in v[:8]) for v in _estudios_hoja(contenido).values()) == 4


def test_esc_1_6_enfoque(catalogo: dict[str, bytes]) -> None:
    """US-001-1.6: seis textos de enfoque, en el orden del escenario, el último vacío."""
    docs = _docs(catalogo["esc_1_6_enfoque.xlsx"])
    textos = [d["Enfoque de género/diferencial"] for d in docs]
    inicios = ["No desarrolla", "Nota:", "Sí, aborda", "Parcial:", "Si bien"]
    assert len(textos) == 6
    assert [str(t)[: len(i)] for t, i in zip(textos[:5], inicios, strict=True)] == inicios
    assert textos[5] is None


def test_esc_1_8_orden_alterado(catalogo: dict[str, bytes]) -> None:
    """US-001-1.8: hojas y columnas de rol en otro orden, el bloque entre sus delimitadores."""
    contenido = catalogo["esc_1_8_orden_alterado.xlsx"]
    base = catalogo["base_valida.xlsx"]
    assert _abrir(contenido).sheetnames != _abrir(base).sheetnames
    assert sorted(_abrir(contenido).sheetnames) == sorted(_abrir(base).sheetnames)
    encabezados = _encabezados(contenido)
    assert encabezados != ENCABEZADOS_BASE
    assert sorted(encabezados, key=str) == sorted(ENCABEZADOS_BASE, key=str)
    assert encabezados[encabezados.index(INICIAL) + 1 : encabezados.index(FINAL)] == DIMENSIONES
    # Mismos conteos de la hoja que con el orden original.
    assert _estudios_hoja(contenido) == TABLA_1_BASE
    assert _guardados(contenido, 4) == _guardados(base, 4)


def test_esc_2_1_fuera_de_lista_n3(catalogo: dict[str, bytes]) -> None:
    """US-001-2.1: el N.º 3 con una intervención que no está en la lista."""
    contenido = catalogo["esc_2_1_fuera_de_lista_n3.xlsx"]
    valor = _doc(_docs(contenido), 3)[PRINCIPAL]
    assert valor == "Intervención Z"
    assert valor not in _listas(contenido)[PRINCIPAL]


def test_esc_2_5_sin_delimitador_final(catalogo: dict[str, bytes]) -> None:
    """US-001-2.5: no está el encabezado «Indicadores o categorías analíticas»."""
    encabezados = _encabezados(catalogo["esc_2_5_sin_delimitador_final.xlsx"])
    assert FINAL not in encabezados
    assert INICIAL in encabezados


def test_esc_2_13_anio_sf_n4(catalogo: dict[str, bytes]) -> None:
    """US-001-2.13: el N.º 4 con «s. f.» en la columna de año."""
    docs = _docs(catalogo["esc_2_13_anio_sf_n4.xlsx"])
    assert _doc(docs, 4)["Año"] == "s. f."
    assert [d["Año"] for d in docs if d["N°"] != 4] == [2015, 2019, 2021, 2010]


def test_esc_2_15_tipo_sin_lista_cuatro_docs(catalogo: dict[str, bytes]) -> None:
    """US-001-2.15: sin lista de tipo, cuatro documentos en el orden del escenario."""
    contenido = catalogo["esc_2_15_tipo_sin_lista_cuatro_docs.xlsx"]
    assert TIPO not in _listas(contenido)
    docs = _docs(contenido)
    assert [d[TIPO] for d in docs] == [EMPIRICO, "Marco teórico", "Estudio empirico", None]
    primero = docs[0]
    assert primero[PRINCIPAL] is not None
    assert 1 in [primero[x] for x in DIMENSIONES]


def test_esc_2_16_tipo_fuera_de_lista_n3(catalogo: dict[str, bytes]) -> None:
    """US-001-2.16: con lista de tipo, el N.º 3 con un valor que no está en ella."""
    contenido = catalogo["esc_2_16_tipo_fuera_de_lista_n3.xlsx"]
    valor = _doc(_docs(contenido), 3)[TIPO]
    assert valor is not None
    assert valor not in _listas(contenido)[TIPO]


def test_esc_3_1_coincide(catalogo: dict[str, bytes]) -> None:
    """US-001-3.1: hoja con todas las categorías, valores correctos y ningún G = H."""
    contenido = catalogo["esc_3_1_coincide.xlsx"]
    docs = _docs(contenido)
    assert not any(d[PRINCIPAL] is not None and d[PRINCIPAL] == d[SECUNDARIA] for d in docs)
    assert _estudios_hoja(contenido) == TABLA_1_BASE
    assert _nombres_de_tabla(contenido, 1) == INTERVENCIONES


def test_esc_3_2_difiere_g_igual_h(catalogo: dict[str, bytes]) -> None:
    """US-001-3.2: un estudio con la misma intervención en ambas columnas; la hoja cuenta doble."""
    contenido = catalogo["esc_3_2_difiere_g_igual_h.xlsx"]
    d = _docs(contenido)[-1]
    assert d[PRINCIPAL] == d[SECUNDARIA] == "Intervención D"
    esperado = {**TABLA_1_BASE, "Intervención D": (0, 0, 0, 0, 2, 0, 0, 0, 2)}
    assert _estudios_hoja(contenido) == esperado


def test_esc_3_5_filas_vacias_antes(catalogo: dict[str, bytes]) -> None:
    """US-001-3.5: filas vacías adicionales antes de cada tabla, con valores correctos."""
    contenido = catalogo["esc_3_5_filas_vacias_antes.xlsx"]
    hoja = _hoja(contenido, "EGM")
    # En la base los títulos están en las filas 1, 10, 19 y 28; aquí se corren 2, 4, 6 y 8.
    assert [_localizar_titulo(hoja, n)[0] for n in (1, 2, 3, 4)] == [3, 14, 25, 36]
    assert all(c.value is None for c in hoja[1])
    assert all(c.value is None for c in hoja[2])
    assert _estudios_hoja(contenido) == TABLA_1_BASE


def test_esc_3_7_titulos_1_2_4_con_tabla_no_comparable_con_valores(
    catalogo: dict[str, bytes],
) -> None:
    """US-001-3.7: títulos numerados 1, 2 y 4 en las comparables y una tabla 3 con valores."""
    contenido = catalogo["esc_3_7_titulos_1_2_4.xlsx"]
    hoja = _hoja(contenido, "EGM")
    titulos = {n: str(hoja.cell(*_localizar_titulo(hoja, n)).value) for n in (1, 2, 3, 4)}
    assert all(t.startswith(f"{n}. ") for n, t in titulos.items())
    assert "número total de estudios" in titulos[1].lower()
    assert "evaluación de impacto" in titulos[2].lower()
    assert "nivel de evidencia" in titulos[4].lower()
    tabla_3 = _guardados(contenido, 3)
    assert list(tabla_3) == INTERVENCIONES
    assert all(fila == {"Sí": 7, "No": 7, "Parcial": 7} for fila in tabla_3.values())
    assert _estudios_hoja(contenido) == TABLA_1_BASE


def test_esc_3_9_nombres_repetidos_entre_tablas(catalogo: dict[str, bytes]) -> None:
    """US-001-3.9: nombres de fila repetidos entre tablas, con valores correctos y distintos."""
    contenido = catalogo["esc_3_9_nombres_repetidos_entre_tablas.xlsx"]
    t1_nombres = _nombres_de_tabla(contenido, 1)
    t4_nombres = _nombres_de_tabla(contenido, 4)
    repetidos = {"Estudio de caso", "Informe de proyecto"}
    assert repetidos <= set(t1_nombres) & set(t4_nombres)
    assert t1_nombres == _nombres_de_tabla(contenido, 2)
    # A mano: N.º 2 (G=A, H=«Estudio de caso», impacto, dim. 1 y 2); N.º 3 (G=«Informe de
    # proyecto», nivel «Estudio de caso», 3 y 4); N.º 4 (G=A, nivel «Informe de proyecto», 1);
    # N.º 6 (G=«Estudio de caso», nivel «Estudio de caso», 1); N.º 7 (G=«Estudio de caso», nivel
    # «Informe de proyecto», 1 y 3).
    t1 = _guardados(contenido, 1)
    assert t1["Estudio de caso"] == {**_fila_con(3, 1, 1), "Total estudios": 3}
    assert t1["Informe de proyecto"] == {**_fila_con(0, 0, 1, 1), "Total estudios": 1}
    assert t1["Intervención A"] == {**_fila_con(2, 1), "Total estudios": 2}
    t2 = _guardados(contenido, 2)
    assert t2["Estudio de caso"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert t2["Informe de proyecto"] == {**_fila_con(), "Total estudios": 0}
    t4 = _guardados(contenido, 4)
    assert t4["Evaluación de impacto"] == {"Estudios": 1}
    assert t4["Estudio de caso"] == {"Estudios": 2}
    assert t4["Informe de proyecto"] == {"Estudios": 2}


def test_esc_3_10_total_entre_dimensiones(catalogo: dict[str, bytes]) -> None:
    """US-001-3.10: «Total estudios» entre dos dimensiones y un estudio sin dimensiones."""
    contenido = catalogo["esc_3_10_total_entre_dimensiones.xlsx"]
    for tabla in (1, 2):
        encabezados = _encabezados_de_tabla(contenido, tabla)
        assert encabezados == [*DIMENSIONES[:4], TOTAL, *DIMENSIONES[4:]]
    d = _docs(contenido)[-1]
    assert d[PRINCIPAL] == "Intervención D"
    assert all(d[x] in (0, None) for x in DIMENSIONES)
    t1 = _guardados(contenido, 1)
    assert t1["Intervención D"] == {**_fila_con(), "Total estudios": 1}
    assert t1["Intervención A"] == {**_fila_con(2, 1), "Total estudios": 2}
    t2 = _guardados(contenido, 2)
    assert t2["Intervención A"] == {**_fila_con(1, 1), "Total estudios": 1}
    assert t2["Intervención D"] == {**_fila_con(), "Total estudios": 0}


def test_esc_3_17_espacios(catalogo: dict[str, bytes]) -> None:
    """US-001-3.17: un espacio al final de la intervención del N.º 2, que la hoja no cuenta."""
    contenido = catalogo["esc_3_17_espacios.xlsx"]
    assert _doc(_docs(contenido), 2)[PRINCIPAL] == "Intervención A "
    # Solo el N.º 4 cuenta para A (dimensión 1); el N.º 2 sigue contando para B por su secundaria.
    esperado = {**TABLA_1_BASE, "Intervención A": (1, 0, 0, 0, 0, 0, 0, 0, 1)}
    assert _estudios_hoja(contenido) == esperado


@pytest.mark.filterwarnings("ignore:Data Validation extension")
def test_validacion_x14_del_catalogo(catalogo: dict[str, bytes]) -> None:
    """FR-001-05: una lista guardada como extensión, junto a las listas escrita y por rango."""
    contenido = catalogo["validacion_x14.xlsx"]
    xml = _partes(contenido)["xl/worksheets/sheet1.xml"].decode("utf-8")
    assert xml.count("<x14:dataValidation ") == 1
    listas = _listas(contenido)
    assert "Metodología" not in listas  # solo la ve la lectura de la extensión
    assert listas["Tipo de fuente"] == ["Académica", "Institucional", "Territorial"]  # escrita
    assert listas[TIPO][0] == EMPIRICO  # por rango
    hoja = _hoja(contenido, "Listas")
    columna = next(c.column for c in hoja[1] if c.value == "Metodología")
    assert [hoja.cell(f, columna).value for f in range(2, 5)] == [
        "Metodología A",
        "Metodología B",
        "Metodología C",
    ]


def test_sc000_06_agregadas(catalogo: dict[str, bytes]) -> None:
    """SC-000-06: una intervención, una dimensión y un nivel agregados, y un estudio que los usa."""
    contenido = catalogo["sc000_06_agregadas.xlsx"]
    listas = _listas(contenido)
    assert "Intervención G" in listas[PRINCIPAL]
    assert "Estudio cuasiexperimental" in listas[NIVEL]
    encabezados = _encabezados(contenido)
    assert encabezados[encabezados.index(INICIAL) + 1 : encabezados.index(FINAL)] == [
        *DIMENSIONES,
        "Dimensión 9",
    ]
    d = _docs(contenido)[-1]
    assert (d[PRINCIPAL], d[NIVEL], d["Dimensión 9"]) == (
        "Intervención G",
        "Estudio cuasiexperimental",
        1,
    )
    # La hoja también trae las categorías nuevas.
    assert "Intervención G" in _nombres_de_tabla(contenido, 1)
    assert "Dimensión 9" in _encabezados_de_tabla(contenido, 1)


def test_sc000_06_retiradas(catalogo: dict[str, bytes]) -> None:
    """SC-000-06: una intervención, una dimensión y un nivel retirados, sin filas que los usen."""
    contenido = catalogo["sc000_06_retiradas.xlsx"]
    listas = _listas(contenido)
    assert "Intervención F" not in listas[PRINCIPAL]
    assert "Informe de proyecto" not in listas[NIVEL]
    assert "Dimensión 8" not in _encabezados(contenido)
    docs = _docs(contenido)
    assert not any(d[PRINCIPAL] == "Intervención F" for d in docs)
    assert not any(d[NIVEL] == "Informe de proyecto" for d in docs)
    assert "Intervención F" not in _nombres_de_tabla(contenido, 1)


def test_sc000_06_renombradas(catalogo: dict[str, bytes]) -> None:
    """SC-000-06: una intervención y un nivel renombrados, que no son valores ancla."""
    contenido = catalogo["sc000_06_renombradas.xlsx"]
    listas = _listas(contenido)
    assert "Intervención A" not in listas[PRINCIPAL]
    assert "Intervención Alfa" in listas[PRINCIPAL]
    assert "Estudio de caso" not in listas[NIVEL]
    assert "Estudio monográfico" in listas[NIVEL]
    docs = _docs(contenido)
    assert [d[PRINCIPAL] for d in docs if d["N°"] in (2, 4)] == ["Intervención Alfa"] * 2
    assert _doc(docs, 3)[NIVEL] == "Estudio monográfico"
    # Los valores ancla siguen: tipo empírico, evaluación de impacto y «No aplica…».
    assert EMPIRICO in listas[TIPO]
    assert "Evaluación de impacto" in listas[NIVEL]
    assert any(v.startswith("No aplica") for v in listas[NIVEL])


def test_sc000_12_otro_numero_de_documentos(catalogo: dict[str, bytes]) -> None:
    """SC-000-12: otro número de documentos que `base_valida` (11 en vez de 5)."""
    docs = _docs(catalogo["sc000_12_otro_nombre_v4.xlsx"])
    assert [d["N°"] for d in docs] == list(range(1, 12))


def test_marcadores_unicos_en_las_celdas(catalogo: dict[str, bytes]) -> None:
    """SC-000-17: marcadores únicos en celdas; el nombre con marcador lo da el constructor."""
    contenido = catalogo["marcadores.xlsx"]
    texto = " ".join(str(v) for d in _docs(contenido) for v in d.values() if v is not None)
    assert len(MARCADORES_CELDAS) >= 5
    assert len(set(MARCADORES_CELDAS)) == len(MARCADORES_CELDAS)
    for marcador in MARCADORES_CELDAS:
        assert texto.count(marcador) == 1, marcador
    assert NOMBRE_CON_MARCADOR.endswith(".xlsx")
    assert NOMBRE_CON_MARCADOR != "marcadores.xlsx"
    # Ningún otro fixture los trae.
    for nombre, otro in catalogo.items():
        if nombre == "marcadores.xlsx" or not zipfile.is_zipfile(io.BytesIO(otro)):
            continue
        xml = b"".join(_partes(otro).values())
        assert not any(m.encode() in xml for m in MARCADORES_CELDAS), nombre
        assert NOMBRE_CON_MARCADOR.encode() not in xml


def test_sesiones_a_y_b_son_distintas_y_validas(catalogo: dict[str, bytes]) -> None:
    """SC-000-18: dos matrices sintéticas válidas que muestran categorías y conteos distintos."""
    a, b = catalogo["sesion_a.xlsx"], catalogo["sesion_b.xlsx"]
    assert len({a, b, catalogo["base_valida.xlsx"]}) == 3
    assert len(_docs(a)) == 5
    assert len(_docs(b)) == 8
    assert "Intervención Norte" in _listas(a)[PRINCIPAL]
    assert "Intervención Sur" in _listas(b)[PRINCIPAL]
    assert "Intervención Sur" not in _listas(a)[PRINCIPAL]
    assert "Intervención Norte" not in _listas(b)[PRINCIPAL]


# ---- FX-A: instancia de ejemplo sintética (apéndice A del contrato) -----------------------------


def test_fx_a_replica_sintetica_del_apendice_a(catalogo: dict[str, bytes]) -> None:
    """US-001-1.1 (insumo de los planes 002 y 003): FX-A reproduce las medidas del apéndice A."""
    contenido = catalogo["instancia_ejemplo.xlsx"]
    docs = _docs(contenido)
    listas = _listas(contenido)
    hoja = _hoja(contenido, HOJA)

    # Hojas y rangos: 27 documentos en las filas 2 a 28; validaciones de las filas 2 a 36.
    assert _abrir(contenido).sheetnames[:4] == [
        "Matriz bibliográfica",
        "EGM",
        "Instrucciones",
        "Guía por tipo de documento",
    ]
    assert [d["N°"] for d in docs] == list(range(1, 28))
    assert [d["_fila"] for d in docs] == list(range(2, 29))
    assert {str(v.sqref).split(":")[1][1:] for v in hoja.data_validations.dataValidation} == {"36"}

    # Listas: 6 tipos, 3 fuentes, 6 intervenciones y «No aplica», 7 metodologías, 4 niveles y
    # «No aplica».
    assert len(listas[TIPO]) == 6
    assert len(listas["Tipo de fuente"]) == 3
    assert len(listas[PRINCIPAL]) == 7
    assert listas[PRINCIPAL][:2] == ["Transferencia de activos", "Acompañamiento técnico"]
    assert listas[PRINCIPAL] == listas[SECUNDARIA]
    assert len(listas["Metodología"]) == 7
    assert len(listas[NIVEL]) == 5
    assert listas[PRINCIPAL][-1].startswith("No aplica")
    assert listas[NIVEL][-1].startswith("No aplica")

    # Dimensiones: ocho, en este orden.
    dimensiones = [
        "Vulnerabilidad",
        "Humano",
        "Social",
        "Natural",
        "Físico",
        "Financiero",
        "Estructuras y procesos",
        "Sostenibilidad",
    ]
    encabezados = _encabezados(contenido)
    assert encabezados[encabezados.index(INICIAL) + 1 : encabezados.index(FINAL)] == dimensiones

    # Reparto por tipo de documento: 9 metodológico, 7 empírico, 4 teórico, 3 normativo,
    # 3 crítico-contextual y 1 comparativo internacional.
    por_tipo: dict[object, int] = {}
    for d in docs:
        por_tipo[d[TIPO]] = por_tipo.get(d[TIPO], 0) + 1
    assert sorted(por_tipo.values(), reverse=True) == [9, 7, 4, 3, 3, 1]
    assert por_tipo[EMPIRICO] == 7

    # E, M y P (contrato §5), calculados aquí a partir de las celdas.
    empiricos = [d for d in docs if d[TIPO] == EMPIRICO]
    assert [d["N°"] for d in empiricos] == [7, 10, 11, 13, 15, 16, 24]

    def intervenciones(d: dict[str, object]) -> set[str]:
        return {
            str(x)
            for x in (d[PRINCIPAL], d[SECUNDARIA])
            if x is not None and not str(x).startswith("No aplica")
        }

    def marcadas(d: dict[str, object]) -> set[str]:
        return {x for x in dimensiones if d[x] == 1}

    mapa = [d for d in empiricos if intervenciones(d) and marcadas(d)]
    assert [d["N°"] for d in mapa] == [7]
    pendientes = [d["N°"] for d in empiricos if d not in mapa]
    assert pendientes == [10, 11, 13, 15, 16, 24]
    celdas = {(i, j) for d in mapa for i in intervenciones(d) for j in marcadas(d)}
    assert celdas == {
        (i, j)
        for i in ("Transferencia de activos", "Acompañamiento técnico")
        for j in ("Vulnerabilidad", "Humano", "Financiero")
    }
    assert len(listas[PRINCIPAL]) - 1 == 6  # 6 × 8 = 48 celdas
    assert len(dimensiones) == 8

    # T4: solo el N.º 7 trae nivel, de impacto.
    niveles = [d[NIVEL] for d in empiricos]
    assert niveles.count("Evaluación de impacto") == 1
    assert niveles.count(None) == 6

    # Tipo de fuente y metodología: 6 + 1 diligenciadas, 20 vacías.
    fuentes = [d["Tipo de fuente"] for d in docs]
    assert (fuentes.count("Académica"), fuentes.count("Institucional")) == (6, 1)
    assert fuentes.count("Territorial") == 0
    assert fuentes.count(None) == 20
    metodologias = [d["Metodología"] for d in docs]
    assert metodologias.count("Conceptual/teórica") == 6
    assert metodologias.count("Evaluación de impacto") == 1
    assert metodologias.count(None) == 20

    # Enfoque: 5 «No», 2 sin prefijo válido (N.º 2 y 7), 20 vacíos.
    enfoques = {int(str(d["N°"])): d["Enfoque de género/diferencial"] for d in docs}
    assert sum(1 for t in enfoques.values() if t is None) == 20
    claros = [n for n, t in enfoques.items() if t and str(t).split()[0].rstrip(".,:") == "No"]
    assert len(claros) == 5
    sin_prefijo = [
        n
        for n, t in enfoques.items()
        if t and str(t).split()[0].rstrip(".,:").lower() not in ("sí", "no", "parcial")
    ]
    assert sorted(sin_prefijo) == [2, 7]

    # Años de 1992 a 2026.
    anios = [int(str(d["Año"])) for d in docs]
    assert all(isinstance(d["Año"], int) for d in docs)
    assert (min(anios), max(anios)) == (1992, 2026)

    # Hoja EGM con fórmulas y sin ningún valor guardado; tablas de 6 filas por 8 dimensiones.
    n_formulas, n_con_valor = _contar_formulas(contenido)
    assert n_formulas > 100
    assert n_con_valor == 0
    assert len(_nombres_de_tabla(contenido, 1)) == 6
    assert _encabezados_de_tabla(contenido, 1) == [*dimensiones, TOTAL]
    assert len(_nombres_de_tabla(contenido, 4)) == 4


def test_fx_a_trae_los_siete_textos_del_n7_escritos_en_su_docstring(
    catalogo: dict[str, bytes],
) -> None:
    """US-002-2.4, US-003-2.7 (insumo): los siete textos del N.º 7 son los del docstring de FX-A."""
    d = _doc(_docs(catalogo["instancia_ejemplo.xlsx"]), 7)
    assert set(TEXTOS_N7) == {
        "País y población",
        INICIAL,
        FINAL,
        "Principales hallazgos / tesis central",
        "Vacío de conocimiento identificado",
        "Limitaciones",
        "Aporte al proyecto",
    }
    documentacion = inspect.getdoc(instancia_ejemplo)
    assert documentacion is not None
    documentacion = " ".join(documentacion.split())  # los textos se parten en varias líneas
    for encabezado, texto in TEXTOS_N7.items():
        assert d[encabezado] == texto
        assert texto in documentacion, encabezado


def test_el_constructor_no_nombra_la_lamina_ni_defectos_de_la_matriz_del_equipo() -> None:
    """Reglas 7 y 9 de CLAUDE.md: el código del constructor no las nombra."""
    fuente = (Path(__file__).resolve().parents[1] / "constructor.py").read_text(encoding="utf-8")
    minusculas = fuente.lower()
    for palabra in ("lámina", "inconsisten", "discrepan", "defectuos", "error de la matriz"):
        assert palabra not in minusculas, palabra


# ================================================================================================
# T-001-08 · Estrategias de hypothesis de matrices válidas (SC-001-03, soporte)
# ================================================================================================

# Los diecisiete encabezados de rol del contrato §3, escritos a mano.
ENCABEZADOS_DE_ROL = [
    "N°",
    "Referencia APA",
    "Año",
    "Tipo de documento",
    "País y población",
    "Tipo de fuente",
    "Tipo de intervención (EGM)",
    "Intervención secundaria (opcional)",
    "Metodología",
    "Nivel de evidencia",
    "Dimensiones evaluadas / propuestas",
    "Indicadores o categorías analíticas",
    "Enfoque de género/diferencial",
    "Principales hallazgos / tesis central",
    "Vacío de conocimiento identificado",
    "Limitaciones",
    "Aporte al proyecto",
]
INICIAL = "Dimensiones evaluadas / propuestas"
FINAL = "Indicadores o categorías analíticas"
PRINCIPAL = "Tipo de intervención (EGM)"
SECUNDARIA = "Intervención secundaria (opcional)"
COLUMNAS_CON_LISTA = [
    "Tipo de documento",
    "Tipo de fuente",
    PRINCIPAL,
    SECUNDARIA,
    "Metodología",
    "Nivel de evidencia",
]
TEXTOS_LIBRES = [
    "País y población",
    INICIAL,
    FINAL,
    "Principales hallazgos / tesis central",
    "Vacío de conocimiento identificado",
    "Limitaciones",
    "Aporte al proyecto",
]
IMPACTO = "Evaluación de impacto"


def _es_empirico(documento: dict[str, object]) -> bool:
    """Contrato §4.1: el tipo empieza por «Estudio empírico» (sin distinguir mayúsculas)."""
    tipo = documento.get("Tipo de documento")
    return isinstance(tipo, str) and tipo.casefold().startswith("estudio empírico")


def _conteo_t1(
    documentos: list[dict[str, object]],
    intervencion: str,
    dimension: str | None,
    *,
    solo_impacto: bool = False,
) -> int:
    """T_1 (o T_2) del contrato §5, escrito a mano: principal más secundaria entre los empíricos."""
    total = 0
    for d in documentos:
        if not _es_empirico(d):
            continue
        if solo_impacto and d.get("Nivel de evidencia") != IMPACTO:
            continue
        if dimension is not None and d.get(dimension) != 1:
            continue
        total += (d.get(PRINCIPAL) == intervencion) + (d.get(SECUNDARIA) == intervencion)
    return total


def _conteo_t4(documentos: list[dict[str, object]], nivel: str) -> int:
    return sum(1 for d in documentos if _es_empirico(d) and d.get("Nivel de evidencia") == nivel)


def _fila_del_titulo(hoja: Worksheet, prefijo: str) -> int:
    """Fila de la celda de la columna A que empieza por el número de la tabla y un punto."""
    filas = []
    for fila in range(1, hoja.max_row + 1):
        valor = hoja.cell(fila, 1).value
        if isinstance(valor, str) and valor.startswith(prefijo):
            filas.append(fila)
    assert len(filas) == 1, prefijo
    return filas[0]


def _misma_intervencion(documento: dict[str, object]) -> bool:
    """G = H con una intervención real (ni vacía ni «No aplica…»)."""
    g = documento.get(PRINCIPAL)
    return isinstance(g, str) and not g.startswith("No aplica") and g == documento.get(SECUNDARIA)


def _ruta_de_la_matriz(matriz: MatrizSintetica) -> str:
    """Parte del paquete con la hoja de la matriz (las hojas van numeradas en su orden)."""
    return f"xl/worksheets/sheet{matriz.nombres_de_hojas().index(HOJA) + 1}.xml"


def _hay_numeros(hoja: Worksheet) -> bool:
    return any(isinstance(c.value, int | float) for fila in hoja.iter_rows() for c in fila)


def _tiene_valores_guardados(contenido: bytes) -> bool:
    return _hay_numeros(_hoja(contenido, "EGM", valores=True))


def _comprobar_egm(formulas: Worksheet, valores: Worksheet, matriz: MatrizSintetica) -> None:
    """La hoja EGM trae fórmulas `COUNTIFS` y, si guardó valores, los que da el contrato."""
    con_valores = _hay_numeros(valores)
    documentos = matriz.documentos()
    lista_g = matriz.valores_de_lista(PRINCIPAL) or []
    lista_nivel = matriz.valores_de_lista("Nivel de evidencia") or []
    intervenciones = [v for v in lista_g if not v.startswith("No aplica")]
    niveles = [v for v in lista_nivel if not v.startswith("No aplica")]
    dimensiones = matriz.dimensiones()

    def revisar(fila: int, columna: int, esperado: int) -> None:
        celda = formulas.cell(fila, columna).value
        assert isinstance(celda, str)
        assert celda.startswith("=COUNTIFS(")
        guardado = valores.cell(fila, columna).value
        if con_valores:
            assert guardado == esperado
        else:
            assert guardado is None

    for prefijo, solo_impacto in (("1. ", False), ("2. ", True)):
        titulo = _fila_del_titulo(formulas, prefijo)
        # Los encabezados de la tabla: desde la columna B hasta la primera celda vacía.
        encabezados: dict[object, int] = {}
        for c in range(2, formulas.max_column + 1):
            encabezado = formulas.cell(titulo + 1, c).value
            if encabezado is None:
                break
            encabezados[encabezado] = c
        assert list(encabezados)[:-1] == dimensiones
        assert list(encabezados)[-1] == "Total estudios"
        for i, intervencion in enumerate(intervenciones):
            fila = titulo + 2 + i
            assert formulas.cell(fila, 1).value == intervencion
            for dimension in [*dimensiones, None]:
                columna = encabezados[dimension or "Total estudios"]
                esperado = _conteo_t1(
                    documentos, intervencion, dimension, solo_impacto=solo_impacto
                )
                revisar(fila, columna, esperado)
    titulo = _fila_del_titulo(formulas, "4. ")
    for i, nivel in enumerate(niveles):
        assert formulas.cell(titulo + 2 + i, 1).value == nivel
        revisar(titulo + 2 + i, 2, _conteo_t4(documentos, nivel))


def _comprobar_libro(matriz: MatrizSintetica, *, con_egm: bool | None = None) -> bytes:
    """Invariantes de un libro válido: `openpyxl` lo abre y cumple el contrato (§2, §3, §4, §7)."""
    contenido = matriz.a_bytes()
    libro = _abrir(contenido)
    assert HOJA in libro.sheetnames
    hoja = libro[HOJA]
    assert isinstance(hoja, Worksheet)

    # Roles: todos los encabezados de rol, una sola vez; el bloque entre los delimitadores.
    encabezados = [c.value for c in hoja[1]]
    assert encabezados == matriz.encabezados()
    for rol in ENCABEZADOS_DE_ROL:
        assert encabezados.count(rol) == 1, rol
    inicio, fin = encabezados.index(INICIAL), encabezados.index(FINAL)
    assert fin - inicio >= 2
    dimensiones = encabezados[inicio + 1 : fin]
    assert dimensiones == matriz.dimensiones()
    assert len(set(dimensiones)) == len(dimensiones)
    assert not set(dimensiones) & set(ENCABEZADOS_DE_ROL)

    # Cada columna con lista (las dimensiones con `1,0`) trae su validación de datos.
    for dimension in dimensiones:
        assert matriz.valores_de_lista(dimension) == ["1", "0"]
    en_openpyxl = hoja.data_validations.dataValidation
    hoja_xml = _partes(contenido)[_ruta_de_la_matriz(matriz)]
    en_x14 = hoja_xml.count(b"<x14:dataValidation ")
    assert len(en_openpyxl) + en_x14 == len(dimensiones) + len(COLUMNAS_CON_LISTA)
    con_uno_cero = [dv for dv in en_openpyxl if dv.type == "list" and dv.formula1 == '"1,0"']
    assert len(con_uno_cero) == len(dimensiones)

    # Anclas: un solo valor «Estudio empírico…», el de impacto y un «No aplica…» por lista.
    tipos = matriz.valores_de_lista("Tipo de documento") or []
    assert len([t for t in tipos if t.startswith("Estudio empírico")]) == 1
    niveles = matriz.valores_de_lista("Nivel de evidencia") or []
    assert IMPACTO in niveles
    assert len([n for n in niveles if n.startswith("No aplica")]) == 1
    for columna in (PRINCIPAL, SECUNDARIA):
        lista = matriz.valores_de_lista(columna) or []
        assert len([v for v in lista if v.startswith("No aplica")]) == 1
        assert len([v for v in lista if not v.startswith("No aplica")]) >= 1
    assert matriz.valores_de_lista(PRINCIPAL) == matriz.valores_de_lista(SECUNDARIA)

    # Filas: lo escrito es lo leído; N.º enteros y únicos; categorías dentro de su lista.
    documentos = matriz.documentos()
    leidas = list(hoja.iter_rows(min_row=2, max_row=1 + len(documentos), values_only=True))
    assert len(leidas) == len(documentos)
    assert hoja.max_row <= 1 + len(documentos) or not documentos
    for fila, documento in zip(leidas, documentos, strict=True):
        assert list(fila) == [documento.get(e) for e in encabezados]
    numeros = [d["N°"] for d in documentos if d]
    assert all(isinstance(n, int) and not isinstance(n, bool) for n in numeros)
    assert len(set(numeros)) == len(numeros)
    no_aplica_g = [v for v in matriz.valores_de_lista(PRINCIPAL) or [] if v.startswith("No aplica")]
    for documento in documentos:
        for columna in COLUMNAS_CON_LISTA:
            valor = documento.get(columna)
            assert valor is None or valor in (matriz.valores_de_lista(columna) or [])
        for dimension in dimensiones:
            marca = documento.get(dimension)
            assert marca in (1, 0, None)
            assert not isinstance(marca, bool)
        if documento and not _es_empirico(documento):
            assert documento.get(PRINCIPAL) in (None, *no_aplica_g)

    # Hoja EGM.
    tiene_egm = "EGM" in libro.sheetnames
    if con_egm is not None:
        assert tiene_egm is con_egm
    if tiene_egm:
        formulas = libro["EGM"]
        assert isinstance(formulas, Worksheet)
        _comprobar_egm(formulas, _hoja(contenido, "EGM", valores=True), matriz)
    return contenido


@pytest.fixture(scope="module")
def corrida_de_200() -> dict[str, object]:
    """Corre una vez 200 ejemplos de `matrices_validas()` y anota qué variabilidad aparece."""
    visto: dict[str, set[object]] = {
        nombre: set()
        for nombre in (
            "n_documentos",
            "con_egm",
            "valores_guardados",
            "g_igual_h",
            "empirico_sin_nivel",
            "empirico_sin_secundaria",
            "solo_espacios",
            "n_dimensiones",
            "orden_de_columnas",
            "intervenciones",
            "niveles",
            "modos",
            "filas_vacias",
            "hojas",
            "ancla_empirico",
            "dimension_vacia_en_empirico",
            "empirico_sin_dimensiones",
        )
    }
    ejemplos: list[int] = []

    @settings(max_examples=200)
    @given(matrices_validas())
    def corrida(matriz: MatrizSintetica) -> None:
        contenido = _comprobar_libro(matriz)
        ejemplos.append(len(contenido))
        documentos = matriz.documentos()
        reales = [d for d in documentos if d]
        empiricos = [d for d in reales if _es_empirico(d)]
        dimensiones = matriz.dimensiones()
        hojas = matriz.nombres_de_hojas()
        visto["n_documentos"].add(len(reales))
        visto["con_egm"].add("EGM" in hojas)
        if "EGM" in hojas:
            visto["valores_guardados"].add(matriz.egm.guardar_valores)
        visto["g_igual_h"].add(any(_misma_intervencion(d) for d in reales))
        visto["empirico_sin_nivel"].add(any(d.get("Nivel de evidencia") is None for d in empiricos))
        visto["empirico_sin_secundaria"].add(any(d.get(SECUNDARIA) is None for d in empiricos))
        visto["solo_espacios"].add(
            any(
                isinstance(d.get(c), str) and not str(d.get(c)).strip()
                for d in reales
                for c in TEXTOS_LIBRES
            )
        )
        visto["n_dimensiones"].add(len(dimensiones))
        visto["orden_de_columnas"].add(tuple(matriz.encabezados()))
        visto["intervenciones"].add(tuple(matriz.valores_de_lista(PRINCIPAL) or []))
        visto["niveles"].add(tuple(matriz.valores_de_lista("Nivel de evidencia") or []))
        visto["filas_vacias"].add(len(documentos) - len(reales))
        visto["hojas"].add(tuple(hojas))
        tipos = matriz.valores_de_lista("Tipo de documento") or []
        visto["ancla_empirico"].add(next(t for t in tipos if t.startswith("Estudio empírico")))
        visto["dimension_vacia_en_empirico"].add(
            any(d.get(x) is None for d in empiricos for x in dimensiones)
        )
        visto["empirico_sin_dimensiones"].add(
            any(all(d.get(x) != 1 for x in dimensiones) for d in empiricos)
        )
        # Modo de cada lista: escrita en la validación, por rango (hoja Listas) o `x14`.
        if "Listas" in hojas:
            visto["modos"].add("rango")
        hoja_xml = _partes(contenido)[_ruta_de_la_matriz(matriz)]
        if b"<x14:dataValidation " in hoja_xml:
            visto["modos"].add("x14")
        if b'formula1>"' in hoja_xml.replace(b"&quot;", b'"'):
            visto["modos"].add("escrita")

    corrida()
    return {"ejemplos": len(ejemplos), **visto}


def test_una_corrida_de_200_ejemplos_produce_libros_que_openpyxl_abre(
    corrida_de_200: dict[str, object],
) -> None:
    """SC-001-03 (soporte): 200 ejemplos al azar dan libros que `openpyxl` abre y cumplen el
    contrato (roles, anclas, bloque de dimensiones con `1,0`, hoja EGM con valores coherentes)."""
    assert corrida_de_200["ejemplos"] == 200


def test_la_corrida_cubre_la_variabilidad_pedida(corrida_de_200: dict[str, object]) -> None:
    """SC-001-03 (soporte): las estrategias varían documentos, categorías, vacíos, orden y hoja."""
    visto = {k: v for k, v in corrida_de_200.items() if isinstance(v, set)}
    cantidades: set[int] = visto["n_documentos"]  # type: ignore[assignment]
    assert {0, 1} <= cantidades
    assert any(n >= 100 for n in cantidades)
    assert any(n > 199 for n in cantidades)  # más documentos que el rango 2:200 de la hoja
    assert visto["con_egm"] == {True, False}
    assert visto["valores_guardados"] == {True, False}
    assert visto["g_igual_h"] == {True, False}
    assert visto["empirico_sin_nivel"] == {True, False}
    assert visto["empirico_sin_secundaria"] == {True, False}
    assert visto["solo_espacios"] == {True, False}
    assert visto["dimension_vacia_en_empirico"] == {True, False}
    assert visto["empirico_sin_dimensiones"] == {True, False}
    assert len(visto["n_dimensiones"]) >= 6
    assert len(visto["orden_de_columnas"]) >= 40
    assert len(visto["intervenciones"]) >= 40
    assert len(visto["niveles"]) >= 20
    assert visto["modos"] == {"escrita", "rango", "x14"}
    filas_vacias: set[int] = visto["filas_vacias"]  # type: ignore[assignment]
    assert 0 in filas_vacias
    assert any(n > 0 for n in filas_vacias)
    assert len(visto["hojas"]) >= 4
    assert len(visto["ancla_empirico"]) >= 2


@settings(max_examples=20)
@given(matrices_validas(con_egm=False, max_documentos=40))
def test_sin_hoja_egm_cuando_se_pide(matriz: MatrizSintetica) -> None:
    """SC-001-03 (soporte): `con_egm=False` nunca trae la hoja EGM."""
    _comprobar_libro(matriz, con_egm=False)


@settings(max_examples=20)
@given(matrices_validas(con_egm=True, valores_guardados=True, max_documentos=40))
def test_con_hoja_egm_y_valores_guardados_coherentes(matriz: MatrizSintetica) -> None:
    """SC-001-03 (soporte): la hoja EGM trae los valores que dan T_1, T_2 y T_4 del contrato §5."""
    contenido = _comprobar_libro(matriz, con_egm=True)
    assert _tiene_valores_guardados(contenido)


@settings(max_examples=20)
@given(matrices_validas(con_egm=True, valores_guardados=False, max_documentos=40))
def test_con_hoja_egm_sin_valores_guardados(matriz: MatrizSintetica) -> None:
    """FR-001-14 (soporte): `valores_guardados=False` deja las fórmulas sin valor guardado."""
    contenido = _comprobar_libro(matriz, con_egm=True)
    assert not _tiene_valores_guardados(contenido)


@settings(max_examples=20)
@given(matrices_validas(misma_intervencion=True, max_documentos=30))
def test_con_filas_con_g_igual_h_cuando_se_pide(matriz: MatrizSintetica) -> None:
    """SC-001-03 (soporte), contrato §5: al menos un estudio empírico con la misma intervención
    como principal y secundaria (la hoja lo cuenta dos veces)."""
    _comprobar_libro(matriz)
    iguales = [d for d in matriz.documentos() if d and _misma_intervencion(d)]
    assert iguales
    assert any(_es_empirico(d) for d in iguales)


@settings(max_examples=20)
@given(matrices_validas(misma_intervencion=False, max_documentos=30))
def test_sin_filas_con_g_igual_h_cuando_se_pide(matriz: MatrizSintetica) -> None:
    """SC-001-03 (soporte): con `misma_intervencion=False`, ningún documento repite la
    intervención como principal y secundaria."""
    _comprobar_libro(matriz)
    assert not [d for d in matriz.documentos() if d and _misma_intervencion(d)]


@settings(max_examples=30)
@given(matrices_validas(min_documentos=3, max_documentos=7))
def test_el_numero_de_documentos_respeta_los_limites(matriz: MatrizSintetica) -> None:
    """SC-001-03 (soporte): `min_documentos` y `max_documentos` acotan los documentos."""
    assert 3 <= len([d for d in matriz.documentos() if d]) <= 7


@settings(max_examples=3)
@given(
    matrices_validas(con_egm=True, valores_guardados=True, min_documentos=250, max_documentos=260)
)
def test_con_mas_documentos_que_el_rango_de_la_hoja_las_formulas_llegan_al_final(
    matriz: MatrizSintetica,
) -> None:
    """Contrato §7 punto 3 (soporte): una matriz válida no excede el rango de las fórmulas; la
    hoja las extiende hasta la última fila de datos (el caso borde CB-12 es otra cosa)."""
    contenido = _comprobar_libro(matriz, con_egm=True)
    ultima = 1 + matriz.n_filas
    assert ultima > 200
    formulas = _hoja(contenido, "EGM")
    titulo = _fila_del_titulo(formulas, "1. ")
    texto = formulas.cell(titulo + 2, 2).value
    assert isinstance(texto, str)
    assert f"${ultima}," in texto


def test_parametros_incoherentes_de_las_estrategias_se_rechazan() -> None:
    """SC-001-03 (soporte): límites contradictorios se rechazan al construir la estrategia."""
    with pytest.raises(ValueError, match="min_documentos"):
        matrices_validas(min_documentos=5, max_documentos=2)
    with pytest.raises(ValueError, match="misma_intervencion"):
        matrices_validas(misma_intervencion=True, max_documentos=0)
    with pytest.raises(ValueError, match="min_documentos"):
        matrices_validas(min_documentos=-1)


@settings(max_examples=100)
@given(categorias())
def test_las_categorias_sinteticas_cumplen_el_contrato(cat: Categorias) -> None:
    """Contrato §4.1 y §5 (soporte): nombres distintos, anclas y valores «No aplica…» presentes."""
    for lista in (
        cat.lista_intervenciones,
        cat.lista_niveles,
        cat.lista_tipos,
        cat.lista_fuentes,
        cat.lista_metodologias,
        cat.dimensiones,
    ):
        assert lista
        assert len({v.casefold() for v in lista}) == len(lista)
        assert all(v and v == v.strip() and not v.startswith("=") for v in lista)
        assert not any(c in v for v in lista for c in '"*?~<>=')
    assert len([t for t in cat.lista_tipos if t.startswith("Estudio empírico")]) == 1
    assert cat.ancla_empirico in cat.lista_tipos
    assert IMPACTO in cat.lista_niveles
    assert len([v for v in cat.lista_niveles if v.startswith("No aplica")]) == 1
    assert len([v for v in cat.lista_intervenciones if v.startswith("No aplica")]) == 1
    assert cat.intervenciones
    assert not any(v.startswith("No aplica") for v in cat.intervenciones)
    assert not any(v.startswith("No aplica") for v in cat.niveles)
    assert len(cat.dimensiones) >= 1
    # Ningún nombre repite el de una columna de rol ni se confunde con otra categoría.
    todos = [*cat.intervenciones, *cat.dimensiones, *cat.niveles]
    assert len({v.casefold() for v in todos}) == len(todos)
    assert not set(cat.dimensiones) & set(ENCABEZADOS_DE_ROL)


def test_generar_matrices_al_azar_no_abre_archivos_de_los_datos_reales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NFR-000-01 (soporte): generar matrices al azar no abre ninguna ruta de los datos reales."""
    abiertos: list[str] = []
    abrir_real = builtins.open

    def espia(archivo: object, *args: object, **kwargs: object) -> object:
        abiertos.append(str(archivo))
        return abrir_real(archivo, *args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(builtins, "open", espia)

    @settings(max_examples=5)
    @given(matrices_validas(max_documentos=5))
    def generar(matriz: MatrizSintetica) -> None:
        matriz.a_bytes()

    generar()
    assert not any("raw" in Path(ruta).parts for ruta in abiertos)
