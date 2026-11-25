"""Pruebas de M03 `egm.libro` (T-001-12): P-001-05 y P-001-06.

Esperados escritos a mano a partir del contrato de datos y del contenido documentado de la
base válida sintética (`MatrizSintetica.base_valida`, constructor M23): 5 documentos en las filas
2 a 6, encabezados en la fila 1, las tablas de la hoja `EGM` desde la fila 1. Ninguno sale de
ejecutar `egm.libro`. Solo se usan fixtures; nunca `data/raw/`.

Columnas de la base válida (base 1): 1 N.º, 2 Referencia, 3 Año, 4 Tipo de documento (lista por
rango), 6 Tipo de fuente (lista escrita), 7 y 8 Intervención principal y secundaria (escritas),
9 Metodología (escrita), 10 Nivel de evidencia (por rango), 11 delimitador, 12 a 19 dimensiones
(lista «1,0»), 20 delimitador, 21 a 25 columnas de texto.
"""

import hashlib
import io
import zipfile
import zlib
from pathlib import Path
from typing import Any

import openpyxl
import pytest
from openpyxl.worksheet.datavalidation import DataValidation

import egm.libro as modulo_libro
from egm.libro import Celda, Libro, LibroNoAbrible, ListaValidacion, abrir
from tests.constructor import (
    EN_MEMORIA,
    HOJA_EGM,
    HOJA_MATRIZ,
    VALOR_EMPIRICO,
    MatrizSintetica,
    carpeta_de_fixtures,
)


def _fixture(nombre: str) -> bytes:
    return (carpeta_de_fixtures() / nombre).read_bytes()


@pytest.fixture(scope="module")
def base() -> Libro:
    return abrir(_fixture("base_valida.xlsx"))


def _valores(libro: Libro, columna: int, hoja: str = HOJA_MATRIZ) -> tuple[str, ...] | None:
    h = libro.hoja(hoja)
    assert h is not None
    lista = h.validacion(columna)
    return None if lista is None else lista.valores


# ---- P-001-05: nombres de hojas, celdas, valor guardado ----------------------------------------


def test_nombres_de_hojas_en_el_orden_del_libro(base: Libro) -> None:
    """FR-001-01: acceso por texto; las hojas salen en el orden del archivo."""
    assert base.nombres_hojas() == (
        "Matriz bibliográfica",
        "EGM",
        "Instrucciones",
        "Guía por tipo de documento",
        "Listas",
    )


def test_hoja_inexistente_es_none_y_la_existente_se_obtiene_por_nombre(base: Libro) -> None:
    """FR-001-01: una hoja que no existe se pregunta por nombre y da `None`."""
    assert base.hoja("Hoja que no existe") is None
    assert base.hoja("matriz bibliográfica") is None  # el nombre es exacto
    assert base.hoja(HOJA_MATRIZ) is not None


def test_dimension_es_ultima_fila_y_columna_con_contenido(base: Libro) -> None:
    """FR-001-01: encabezado más 5 documentos = 6 filas; columnas A a Y = 25."""
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    assert hoja.dimension() == (6, 25)


def test_celda_con_valor_sin_formula(base: Libro) -> None:
    """FR-001-01: el encabezado y los valores de los documentos, con su tipo."""
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    assert hoja.celda(1, 1) == Celda("N°", None, "N°")
    assert hoja.celda(3, 1) == Celda(2, None, 2)  # el N.º 2 es un entero
    assert hoja.celda(3, 4).valor == VALOR_EMPIRICO
    assert hoja.celda(3, 8).valor == "Intervención B"
    assert hoja.celda(3, 3).valor == 2019


def test_celda_vacia_es_none_y_no_cero(base: Libro) -> None:
    """FR-001-17: vacío (`None`) y la marca 0 son distintos."""
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    assert hoja.celda(2, 12) == Celda(None, None, None)  # el N.º 1 no tiene marcas
    assert hoja.celda(2, 8) == Celda(None, None, None)  # sin intervención secundaria
    assert hoja.celda(3, 12).valor == 1  # N.º 2, dimensión 1
    marca_cero = hoja.celda(3, 14)  # N.º 2, dimensión 3: marcada con 0
    assert marca_cero.valor == 0
    assert marca_cero.valor is not None


def test_celda_fuera_de_la_dimension_es_vacia(base: Libro) -> None:
    """FR-001-01: preguntar más allá del contenido da una celda vacía, sin error."""
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    assert hoja.celda(500, 3) == Celda(None, None, None)
    assert hoja.celda(2, 80) == Celda(None, None, None)


def test_celda_con_indice_invalido_es_error(base: Libro) -> None:
    """FR-001-01: filas y columnas se cuentan desde 1."""
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    with pytest.raises(ValueError, match="desde 1"):
        hoja.celda(0, 1)
    with pytest.raises(ValueError, match="desde 1"):
        hoja.celda(1, 0)


def test_celda_con_formula_da_formula_y_valor_guardado(base: Libro) -> None:
    """FR-001-05: en la hoja `EGM`, fila 4 = «Intervención B»; B con la dimensión 1 y la
    secundaria del N.º 2 (1 estudio), D con la dimensión 3 (0 estudios, guardado como 0)."""
    egm = base.hoja(HOJA_EGM)
    assert egm is not None
    assert egm.celda(4, 1).valor == "Intervención B"
    assert egm.celda(4, 1).formula is None
    uno = egm.celda(4, 2)
    assert uno.formula is not None
    assert uno.formula.startswith("=COUNTIFS(")
    assert uno.valor_guardado == 1
    assert uno.valor == 1
    cero = egm.celda(4, 4)
    assert cero.formula is not None
    assert cero.valor_guardado == 0
    assert cero.valor_guardado is not None


def test_valor_guardado_ausente_es_none_nunca_cero() -> None:
    """FR-001-17 (CB-30): una hoja sin valores guardados da la fórmula y `None`."""
    libro = abrir(_fixture("cb30_sin_valores_guardados.xlsx"))
    egm = libro.hoja(HOJA_EGM)
    assert egm is not None
    for fila, columna in ((3, 2), (4, 2), (4, 4)):
        celda = egm.celda(fila, columna)
        assert celda.formula is not None
        assert celda.formula.startswith("=COUNTIFS(")
        assert celda.valor_guardado is None
        assert celda.valor is None
    assert egm.celda(4, 1).valor == "Intervención B"  # el texto no depende del cálculo


# ---- P-001-05: listas de validación ------------------------------------------------------------


def test_listas_escrita_y_por_rango_de_la_base_en_el_orden_de_la_lista(base: Libro) -> None:
    """FR-001-05: lista escrita (6, 7) y por rango (4, 10), en el orden en que están."""
    assert _valores(base, 4) == (
        VALOR_EMPIRICO,
        "Documento teórico",
        "Documento metodológico",
        "Documento normativo",
    )
    assert _valores(base, 6) == ("Académica", "Institucional", "Territorial")
    assert _valores(base, 7) == (
        "Intervención A",
        "Intervención B",
        "Intervención C",
        "Intervención D",
        "Intervención E",
        "Intervención F",
        "No aplica (documento teórico/metodológico/normativo)",
    )
    assert _valores(base, 8) == _valores(base, 7)
    assert _valores(base, 10) == (
        "Evaluación de impacto",
        "Estudio de caso",
        "Informe de proyecto",
        "No aplica (marco conceptual/normativo/metodológico)",
    )


def test_lista_de_dimensiones_uno_cero(base: Libro) -> None:
    """FR-001-05: las dimensiones traen la lista «1,0»; el delimitador no trae lista."""
    for columna in range(12, 20):
        assert _valores(base, columna) == ("1", "0")
    assert _valores(base, 11) is None
    assert _valores(base, 20) is None


def test_columna_sin_lista_y_hoja_sin_validaciones_dan_none(base: Libro) -> None:
    """FR-001-05: columnas sin lista, columna inexistente y hoja sin validaciones."""
    for columna in (1, 2, 3, 5, 21, 25, 99):
        assert _valores(base, columna) is None
    assert _valores(base, 1, hoja=HOJA_EGM) is None
    assert _valores(base, 2, hoja="Listas") is None


def test_lista_guardada_como_extension_x14_se_lee_del_xml() -> None:
    """FR-001-05 (ADR-001, punto 6): la metodología (col. 9) llega como extensión `x14`;
    las demás listas se siguen leyendo con la lectura normal."""
    libro = abrir(_fixture("validacion_x14.xlsx"))
    assert _valores(libro, 9) == ("Metodología A", "Metodología B", "Metodología C")
    assert _valores(libro, 6) == ("Académica", "Institucional", "Territorial")
    assert _valores(libro, 4) is not None
    assert _valores(libro, 10) is not None


@pytest.mark.parametrize(
    ("columna", "encabezado", "modo", "orden"),
    [
        (6, "Tipo de fuente", "escrita", ["Territorial", "Académica", "Institucional"]),
        (10, "Nivel de evidencia", "rango", ["Zeta", "Alfa", "Mu", "Beta"]),
        (9, "Metodología", "x14", ["Metodología C", "Metodología A", "Metodología B"]),
    ],
)
def test_el_orden_de_la_lista_no_es_alfabetico(
    columna: int, encabezado: str, modo: Any, orden: list[str]
) -> None:
    """FR-001-05: los valores salen en el orden de la lista, por cualquiera de las tres vías."""
    contenido = MatrizSintetica.base_valida().con_lista(encabezado, orden, modo=modo).a_bytes()
    assert _valores(abrir(contenido), columna) == tuple(orden)


def _libro_openpyxl(
    preparar: Any,
) -> bytes:
    """Libro armado con `openpyxl` para variantes que el constructor no genera."""
    libro = openpyxl.Workbook()
    hoja = libro.active
    assert hoja is not None
    hoja.title = "Datos"
    preparar(libro, hoja)
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def test_rango_en_hoja_con_comillas_omite_vacios_y_lee_numeros_como_texto() -> None:
    """FR-001-05: rango en hoja con espacios en el nombre; los vacíos no son valores y un
    número entero se lee como su texto (`1`, no `1.0`)."""

    def preparar(libro: Any, hoja: Any) -> None:
        otra = libro.create_sheet("Mis listas")
        for fila, valor in enumerate((1, None, 0, "Sí"), start=1):
            otra.cell(fila, 1).value = valor
        validacion = DataValidation(type="list", formula1="'Mis listas'!$A$1:$A$4")
        validacion.add("B2:B9")
        hoja.add_data_validation(validacion)

    assert _valores(abrir(_libro_openpyxl(preparar)), 2, hoja="Datos") == ("1", "0", "Sí")


def test_lista_por_rango_en_la_misma_hoja_y_lista_escrita_con_varios_rangos() -> None:
    """FR-001-05: referencia sin hoja (la de la validación); una validación sobre dos áreas
    sirve a las columnas de ambos."""

    def preparar(_libro: Any, hoja: Any) -> None:
        for fila, valor in enumerate(("uno", "dos"), start=1):
            hoja.cell(fila, 5).value = valor
        por_rango = DataValidation(type="list", formula1="$E$1:$E$2")
        por_rango.add("A2:A5")
        escrita = DataValidation(type="list", formula1='"Sí,No,Parcial"')
        escrita.add("C2:C5")
        escrita.add("D2:D5")
        hoja.add_data_validation(escrita)
        hoja.add_data_validation(por_rango)

    libro = abrir(_libro_openpyxl(preparar))
    assert _valores(libro, 1, hoja="Datos") == ("uno", "dos")
    assert _valores(libro, 3, hoja="Datos") == ("Sí", "No", "Parcial")
    assert _valores(libro, 4, hoja="Datos") == ("Sí", "No", "Parcial")
    assert _valores(libro, 2, hoja="Datos") is None


def test_validacion_que_no_es_lista_o_no_se_resuelve_no_da_lista() -> None:
    """FR-001-05: una validación de tipo entero, un rango a una hoja inexistente y una
    referencia que no es rango (nombre definido, no admitido) no entregan lista."""

    def preparar(_libro: Any, hoja: Any) -> None:
        entero = DataValidation(type="whole", operator="between", formula1="0", formula2="9")
        entero.add("A2:A5")
        sin_hoja = DataValidation(type="list", formula1="Fantasma!$A$1:$A$3")
        sin_hoja.add("B2:B5")
        nombre = DataValidation(type="list", formula1="MiLista")
        nombre.add("C2:C5")
        for validacion in (entero, sin_hoja, nombre):
            hoja.add_data_validation(validacion)

    libro = abrir(_libro_openpyxl(preparar))
    for columna in (1, 2, 3):
        assert _valores(libro, columna, hoja="Datos") is None


def test_lista_validacion_es_inmutable() -> None:
    """FR-001-05: la lista es un valor; sus valores forman una tupla."""
    lista = ListaValidacion(("a", "b"))
    assert lista.valores == ("a", "b")
    with pytest.raises(AttributeError):
        lista.valores = ("c",)  # type: ignore[misc]


# ---- P-001-06: solo lectura, en memoria ---------------------------------------------------------


def test_los_bytes_de_entrada_no_cambian_tras_abrir_y_leer() -> None:
    """NFR-000-01: abrir y recorrer el libro no altera los bytes recibidos."""
    contenido = _fixture("base_valida.xlsx")
    huella = hashlib.sha256(contenido).hexdigest()
    copia = bytes(contenido)
    libro = abrir(contenido)
    for nombre in libro.nombres_hojas():
        hoja = libro.hoja(nombre)
        assert hoja is not None
        filas, columnas = hoja.dimension()
        for fila in range(1, filas + 1):
            for columna in range(1, columnas + 1):
                hoja.celda(fila, columna)
                hoja.validacion(columna)
    assert hashlib.sha256(contenido).hexdigest() == huella
    assert contenido == copia


def test_m03_no_expone_ninguna_operacion_de_guardar(base: Libro) -> None:
    """NFR-000-01: ni el módulo, ni el libro, ni la hoja ofrecen guardar o escribir."""
    prohibidos = ("save", "guardar", "write", "escribir", "dump", "set", "asignar", "close")
    hoja = base.hoja(HOJA_MATRIZ)
    assert hoja is not None
    for objeto in (modulo_libro, base, hoja):
        publicos = [n for n in dir(objeto) if not n.startswith("_")]
        for nombre in publicos:
            assert not any(nombre.lower().startswith(p) for p in prohibidos), nombre
    assert sorted(n for n in dir(base) if not n.startswith("_")) == ["hoja", "nombres_hojas"]
    assert sorted(n for n in dir(hoja) if not n.startswith("_")) == [
        "celda",
        "dimension",
        "validacion",
    ]


def test_abrir_no_guarda_ni_escribe_en_disco(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """NFR-000-01: `abrir` no llama a `save` de la biblioteca y no deja nada en el directorio
    de trabajo; también con el libro de extensión `x14`."""

    def no_guardar(*_a: object, **_k: object) -> None:
        raise AssertionError("se intentó guardar el libro")

    monkeypatch.setattr(openpyxl.workbook.workbook.Workbook, "save", no_guardar)
    monkeypatch.chdir(tmp_path)
    for nombre in ("base_valida.xlsx", "validacion_x14.xlsx", "cb30_sin_valores_guardados.xlsx"):
        libro = abrir(_fixture(nombre))
        assert libro.nombres_hojas()
    assert list(tmp_path.iterdir()) == []


def test_abrir_solo_recibe_bytes_nunca_una_ruta() -> None:
    """ADR-004, punto 1: una ruta (texto o `Path`) no es contenido; no se abre del disco."""
    ruta = carpeta_de_fixtures() / "base_valida.xlsx"
    with pytest.raises(TypeError):
        abrir(str(ruta))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        abrir(ruta)  # type: ignore[arg-type]


def test_abrir_no_emite_avisos_con_extension_x14(recwarn: pytest.WarningsRecorder) -> None:
    """ADR-001, punto 6: el aviso de la biblioteca por la extensión no sale; M03 la lee."""
    abrir(_fixture("validacion_x14.xlsx"))
    assert [w for w in recwarn if "extension" in str(w.message)] == []


# ---- Archivo no abrible (NC-ARQ-1, R-1) ---------------------------------------------------------


@pytest.mark.parametrize(
    "contenido",
    [
        _fixture("cb16_danado.xlsx"),
        _fixture("cb16_otro_tipo.txt"),
        _fixture("cb16_extension_xlsx_otro_contenido.xlsx"),
        b"",
        EN_MEMORIA["parte_mayor_que_lo_declarado"](),
    ],
    ids=[
        "danado",
        "texto",
        "extension_con_otro_contenido",
        "vacio",
        "parte_mayor_que_lo_declarado",
    ],
)
def test_un_archivo_que_no_se_puede_abrir_lanza_libro_no_abrible(contenido: bytes) -> None:
    """NFR-000-19 / NC-ARQ-1: paquete dañado, otro contenido o CRC incoherente (`BadZipFile`)
    se traducen a `LibroNoAbrible`."""
    with pytest.raises(LibroNoAbrible):
        abrir(contenido)


def test_xml_recortado_con_crc_coherente_lanza_libro_no_abrible() -> None:
    """NC-ARQ-1 (R-1): con el CRC coherente con lo declarado el paquete se lee, pero el XML
    queda partido: `ParseError` de la biblioteca, traducido a `LibroNoAbrible`."""
    base = MatrizSintetica.base_valida().a_bytes()
    parte = "xl/worksheets/sheet1.xml"
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(base)) as origen, zipfile.ZipFile(salida, "w") as destino:
        for info in origen.infolist():
            datos = origen.read(info.filename)
            if info.filename == parte:
                datos = datos[: len(datos) // 2]  # recorte dentro del XML
            nueva = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            nueva.compress_type = zipfile.ZIP_DEFLATED
            destino.writestr(nueva, datos)
            assert zlib.crc32(datos) == destino.filelist[-1].CRC
    with pytest.raises(LibroNoAbrible):
        abrir(salida.getvalue())


def test_libro_no_abrible_no_menciona_el_contenido() -> None:
    """NFR-000-19: el mensaje de la excepción no trae el contenido del archivo."""
    with pytest.raises(LibroNoAbrible) as error:
        abrir(b"texto secreto del equipo")
    assert "secreto" not in str(error.value)
