"""M03 `egm.libro`: el libro `.xlsx` en memoria, de solo lectura (arquitectura §6.1, M03).

Es el único módulo de `egm` que importa la biblioteca de lectura de hojas de cálculo (arquitectura
§4.1, regla 3). Recibe los bytes del archivo, nunca una ruta (ADR-004, punto 1), no guarda ni
escribe nada (NFR-000-01) y expone, por celda, el valor, la fórmula y el valor guardado, y, por
columna, su lista de validación de datos (ADR-001, punto 6).

Lectura de las listas:

- L1: lectura normal de `openpyxl` (validaciones estándar, listas escritas o por rango). El modo
  `read_only=True` no entrega las validaciones (la hoja de solo lectura no tiene
  `data_validations`; riesgo R-5 del plan 001), así que se usa el modo normal.
- L2: si el paquete trae validaciones guardadas como extensión `x14`, que `openpyxl` descarta, se
  leen del XML de la hoja dentro del paquete, en memoria.

Se abre el libro dos veces: con fórmulas (`data_only=False`) y con los valores guardados
(`data_only=True`), porque `openpyxl` entrega una cosa u otra por carga.
"""

import io
import re
import warnings
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Final, Protocol
from xml.etree import ElementTree

import openpyxl
from openpyxl.utils.cell import range_boundaries

__all__ = ["Celda", "Hoja", "Libro", "LibroNoAbrible", "ListaValidacion", "Valor", "abrir"]

type Valor = str | int | float | bool | datetime | date | time | timedelta | None
"""Lo que puede traer una celda: texto, número, fecha, lógico o vacío (`None`)."""


class LibroNoAbrible(Exception):
    """El contenido recibido no se pudo abrir como libro `.xlsx` (dañado o de otro tipo).

    Cubre `zipfile.BadZipFile` (también por CRC incoherente con lo declarado), `ParseError` del
    XML y los demás fallos de apertura de la biblioteca (NC-ARQ-1, R-1 del plan 001). El mensaje
    nunca trae el contenido del archivo. M02 y M13 la convierten en `Rechazo("tipo")`.
    """


@dataclass(frozen=True)
class Celda:
    """Una celda.

    - Constante: `valor` es el contenido, `formula` es `None` y `valor_guardado` es el contenido.
    - Fórmula: `formula` es su texto (con «=»); `valor_guardado` es el valor que el archivo trae
      guardado, o `None` si no trae ninguno (nunca 0); `valor` es ese mismo valor guardado.
    - Vacía: los tres son `None`.
    """

    valor: Valor
    formula: str | None
    valor_guardado: Valor


@dataclass(frozen=True)
class ListaValidacion:
    """Los valores de una lista de validación de datos, en el orden de la lista."""

    valores: tuple[str, ...]


class Hoja(Protocol):
    """Una hoja del libro. Filas y columnas se cuentan desde 1."""

    def dimension(self) -> tuple[int, int]:
        """Última fila y última columna con contenido; `(0, 0)` si la hoja está vacía."""
        ...

    def celda(self, fila: int, columna: int) -> Celda:
        """La celda; fuera de la dimensión es una celda vacía."""
        ...

    def validacion(self, columna: int) -> ListaValidacion | None:
        """La lista de validación de la columna, o `None` si no tiene o no se puede resolver."""
        ...


class Libro(Protocol):
    """El libro en memoria, de solo lectura."""

    def nombres_hojas(self) -> tuple[str, ...]:
        """Los nombres de las hojas, en el orden del archivo."""
        ...

    def hoja(self, nombre: str) -> Hoja | None:
        """La hoja de ese nombre exacto, o `None` si no existe."""
        ...


_NS_PRINCIPAL: Final = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_NS_RELACIONES_DOC: Final = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_NS_RELACIONES_PAQUETE: Final = "http://schemas.openxmlformats.org/package/2006/relationships"
_NS_X14: Final = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"
_NS_XM: Final = "http://schemas.microsoft.com/office/excel/2006/main"

_REFERENCIA: Final = re.compile(
    r"^(?:(?P<hoja>'(?:[^']|'')+'|[^'!]+)!)?(?P<rango>\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)$"
)

# Una validación: columnas que cubre y fórmula (lista escrita o referencia).
type _Validacion = tuple[tuple[tuple[int, int], ...], str]


def _abrir_hojas_x14(paquete: zipfile.ZipFile) -> dict[str, list[_Validacion]]:
    """L2: validaciones de extensión `x14` por nombre de hoja, leídas del XML del paquete."""
    marca = _NS_X14.encode()
    nombre_a_parte = _partes_de_las_hojas(paquete)
    encontradas: dict[str, list[_Validacion]] = {}
    for nombre, parte in nombre_a_parte.items():
        xml = paquete.read(parte)
        if marca not in xml:
            continue
        raiz = ElementTree.fromstring(xml)
        validaciones: list[_Validacion] = []
        for v in raiz.iter(f"{{{_NS_X14}}}dataValidation"):
            if v.get("type") != "list":
                continue
            formula = v.findtext(f"{{{_NS_X14}}}formula1/{{{_NS_XM}}}f")
            sqref = v.findtext(f"{{{_NS_XM}}}sqref")
            if formula is None or sqref is None:
                continue
            validaciones.append((_columnas_de(sqref), formula))
        if validaciones:
            encontradas[nombre] = validaciones
    return encontradas


def _partes_de_las_hojas(paquete: zipfile.ZipFile) -> dict[str, str]:
    """Nombre de cada hoja → ruta de su parte XML en el paquete."""
    libro = ElementTree.fromstring(paquete.read("xl/workbook.xml"))
    relaciones = ElementTree.fromstring(paquete.read("xl/_rels/workbook.xml.rels"))
    destinos = {
        r.get("Id"): r.get("Target", "")
        for r in relaciones.iter(f"{{{_NS_RELACIONES_PAQUETE}}}Relationship")
    }
    partes: dict[str, str] = {}
    for hoja in libro.iter(f"{{{_NS_PRINCIPAL}}}sheet"):
        destino = destinos.get(hoja.get(f"{{{_NS_RELACIONES_DOC}}}id"))
        nombre = hoja.get("name")
        if destino is None or nombre is None:
            continue
        partes[nombre] = destino.lstrip("/") if destino.startswith("/") else f"xl/{destino}"
    return partes


def _columnas_de(sqref: str) -> tuple[tuple[int, int], ...]:
    """Rangos de columnas (primera, última) que cubren las áreas de un `sqref`."""
    columnas = []
    for area in sqref.split():
        minimo, _fila_min, maximo, _fila_max = range_boundaries(area)
        if minimo is not None and maximo is not None:
            columnas.append((minimo, maximo))
    return tuple(columnas)


def _texto(valor: object) -> str:
    """Un valor de una celda de lista como texto: un número entero se lee `1`, no `1.0`."""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


class _Hoja:
    """Hoja de solo lectura sobre dos cargas del mismo libro (fórmulas y valores guardados)."""

    def __init__(
        self,
        libro: "_Libro",
        nombre: str,
        con_formulas: Any,
        con_valores: Any,
        extension: list[_Validacion],
    ) -> None:
        self._libro = libro
        self._nombre = nombre
        self._formulas = con_formulas
        self._valores = con_valores
        self._extension = extension
        self._dimension: tuple[int, int] | None = None

    def dimension(self) -> tuple[int, int]:
        if self._dimension is None:
            ultima_fila = ultima_columna = 0
            for fila in self._formulas.iter_rows():
                for celda in fila:
                    if celda.value is not None:
                        ultima_fila = max(ultima_fila, celda.row)
                        ultima_columna = max(ultima_columna, celda.column)
            self._dimension = (ultima_fila, ultima_columna)
        return self._dimension

    def celda(self, fila: int, columna: int) -> Celda:
        if fila < 1 or columna < 1:
            raise ValueError("Las filas y las columnas se cuentan desde 1")
        ultima_fila, ultima_columna = self.dimension()
        if fila > ultima_fila or columna > ultima_columna:
            return Celda(None, None, None)
        origen = self._formulas.cell(fila, columna)
        guardado: Valor = self._valores.cell(fila, columna).value
        if origen.data_type == "f":
            texto = getattr(origen.value, "text", origen.value)
            return Celda(guardado, str(texto), guardado)
        return Celda(origen.value, None, origen.value)

    def validacion(self, columna: int) -> ListaValidacion | None:
        estandar: list[_Validacion] = []
        for v in self._formulas.data_validations.dataValidation:
            if v.type != "list" or v.formula1 is None:
                continue
            columnas = tuple((r.min_col, r.max_col) for r in v.sqref.ranges)
            estandar.append((columnas, v.formula1))
        for columnas, formula in (*estandar, *self._extension):
            if any(minimo <= columna <= maximo for minimo, maximo in columnas):
                valores = self._libro._resolver(formula, self._nombre)
                if valores is not None:
                    return ListaValidacion(valores)
        return None


class _Libro:
    """Libro de solo lectura. Lo único público es la interfaz de `Libro`."""

    def __init__(
        self,
        con_formulas: Any,
        con_valores: Any,
        extension: dict[str, list[_Validacion]],
    ) -> None:
        self._formulas = con_formulas
        self._valores = con_valores
        self._extension = extension

    def nombres_hojas(self) -> tuple[str, ...]:
        return tuple(h.title for h in self._formulas.worksheets)

    def hoja(self, nombre: str) -> Hoja | None:
        if nombre not in self.nombres_hojas():
            return None
        return _Hoja(
            self,
            nombre,
            self._formulas[nombre],
            self._valores[nombre],
            self._extension.get(nombre, []),
        )

    def _resolver(self, formula: str, hoja_de_la_validacion: str) -> tuple[str, ...] | None:
        """Valores de una lista: escrita entre comillas o referencia a un rango; `None` si la
        referencia no se puede resolver (hoja inexistente o un nombre definido)."""
        formula = formula.strip()
        if len(formula) >= 2 and formula.startswith('"') and formula.endswith('"'):
            return tuple(formula[1:-1].split(","))
        referencia = _REFERENCIA.match(formula)
        if referencia is None:
            return None
        nombre = referencia.group("hoja")
        if nombre is None:
            nombre = hoja_de_la_validacion
        elif nombre.startswith("'"):
            nombre = nombre[1:-1].replace("''", "'")
        if nombre not in self.nombres_hojas():
            return None
        minimo_col, minimo_fila, maximo_col, maximo_fila = range_boundaries(
            referencia.group("rango").replace("$", "")
        )
        hoja = self._formulas[nombre]
        valores: list[str] = []
        for fila in hoja.iter_rows(
            min_row=minimo_fila, max_row=maximo_fila, min_col=minimo_col, max_col=maximo_col
        ):
            valores.extend(_texto(c.value) for c in fila if c.value is not None)
        return tuple(valores)


def abrir(contenido: bytes) -> Libro:
    """Abre el libro `.xlsx` desde sus bytes, en memoria y solo para leer.

    Nunca recibe una ruta ni escribe nada. Un contenido que no se puede abrir (paquete dañado,
    otro tipo de archivo, XML partido) lanza `LibroNoAbrible`.
    """
    if not isinstance(contenido, bytes):
        raise TypeError("`abrir` recibe los bytes del archivo, no una ruta")
    try:
        with zipfile.ZipFile(io.BytesIO(contenido)) as paquete:
            extension = _abrir_hojas_x14(paquete)
        with warnings.catch_warnings():
            if extension:  # el aviso de la biblioteca por la extensión sobra: se lee en L2
                warnings.simplefilter("ignore", UserWarning)
            con_formulas = openpyxl.load_workbook(io.BytesIO(contenido), data_only=False)
            con_valores = openpyxl.load_workbook(io.BytesIO(contenido), data_only=True)
    except Exception as error:  # límite del módulo: cada fallo de apertura es el mismo hecho
        raise LibroNoAbrible(
            "El archivo no se pudo abrir como libro de hoja de cálculo."
        ) from error
    return _Libro(con_formulas, con_valores, extension)
