"""M23 `tests.constructor`: constructor de matrices sintéticas `.xlsx` para las pruebas.

Genera, solo en memoria y de forma determinista, libros con la estructura del contrato de datos
(`docs/specs/contrato-datos.md`): hojas, encabezados de rol, bloque de dimensiones entre
delimitadores, listas por validación (escrita, por rango o guardada como extensión `x14`), filas con
valores de cualquier tipo y hoja `EGM` con fórmulas **y** valores guardados controlados. También
genera los archivos de carga de NFR-000-19 (otro tipo, dañado, de tamaño exacto, de contenido
descomprimido declarado exacto y con una parte mayor que lo declarado).

Reglas del constructor:

- Todas las categorías son sintéticas (permitidas en fixtures); ninguna copia la matriz real del
  equipo ni usa cifras de la presentación.
- Determinista: las fechas internas del libro y las marcas de tiempo del paquete son fijas, y el
  orden de las partes es estable. Dos generaciones dan los mismos bytes.
- Nunca abre ni nombra rutas de los datos reales del equipo: no lee ningún archivo.

Uso típico (constructor fluido; cada método devuelve el mismo objeto, y `copia()` permite derivar
variantes)::

    contenido = MatrizSintetica.base_valida().quitar_columna("Nivel de evidencia").a_bytes()

El catálogo de fixtures con nombre (`CATALOGO`: un archivo por caso borde del contrato §9 y por
escenario o criterio de los planes) se escribe en `data/fixtures/` con::

    python -m tests.constructor

Los fixtures que pesan cerca de los límites de NFR-000-19 (`EN_MEMORIA`) se generan solo en
memoria y no se guardan.
"""

from __future__ import annotations

import argparse
import copy
import io
import random
import re
import zipfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Self
from xml.sax.saxutils import escape

from hypothesis import strategies as st
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# --- Constantes del contrato (permitidas aquí: son fixtures) -----------------------------------

HOJA_MATRIZ = "Matriz bibliográfica"
HOJA_EGM = "EGM"
HOJA_LISTAS = "Listas"
HOJA_INSTRUCCIONES = "Instrucciones"
HOJA_GUIA = "Guía por tipo de documento"

VALOR_EMPIRICO = "Estudio empírico (evaluación/caso)"
VALOR_IMPACTO = "Evaluación de impacto"
VALOR_NO_APLICA_INTERVENCION = "No aplica (documento teórico/metodológico/normativo)"
VALOR_NO_APLICA_NIVEL = "No aplica (marco conceptual/normativo/metodológico)"

ENCABEZADO_DELIMITADOR_INICIAL = "Dimensiones evaluadas / propuestas"
ENCABEZADO_DELIMITADOR_FINAL = "Indicadores o categorías analíticas"
ENCABEZADO_TOTAL = "Total estudios"

FECHA_FIJA = datetime(2000, 1, 1, 0, 0, 0)
_FECHA_PAQUETE = (2000, 1, 1, 0, 0, 0)
_RELLENO = "docProps/relleno.bin"

ModoLista = Literal["escrita", "rango", "x14"]

_URI_X14_VALIDACIONES = "{CCE6A557-97BC-4b89-ADB6-D9C93CAAB3DF}"
_NS_X14 = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"
_NS_XM = "http://schemas.microsoft.com/office/excel/2006/main"


class _Sentinela:
    """Valor único que no se copia al copiar profundamente (comparación por identidad)."""

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre

    def __repr__(self) -> str:
        return self._nombre

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        return self


AUTOMATICO: Any = _Sentinela("AUTOMATICO")
"""Valor guardado que el constructor calcula con la semántica de la hoja (`COUNTIFS`)."""


# --- Modelo de la hoja de la matriz ------------------------------------------------------------


@dataclass
class Columna:
    """Una columna de la matriz. El `id` es estable aunque se renombre o se mueva."""

    id: int
    encabezado: str | None
    rol: str | None = None
    lista: list[str] | None = None
    modo_lista: ModoLista = "escrita"


# --- Modelo de la hoja EGM ---------------------------------------------------------------------


@dataclass(frozen=True)
class _Ref:
    """Referencia estable a una columna de la matriz (por `id`), con su letra de respaldo."""

    id: int
    letra_respaldo: str


@dataclass(frozen=True)
class _Criterio:
    """Una condición de `COUNTIFS`: la columna y cómo se compara."""

    ref: _Ref
    tipo: Literal["nombre", "prefijo", "igual", "uno"]
    texto: str = ""


_Termino = tuple[_Criterio, ...]


@dataclass
class CeldaEgm:
    """Celda del cuerpo de una tabla: con fórmula (suma de `COUNTIFS`) o con un literal.

    `valor` es el valor guardado de una celda con fórmula: `AUTOMATICO` (el que daría la hoja),
    `None` (ausente) o cualquier número o texto.
    """

    terminos: tuple[_Termino, ...] | None = None
    literal: Any = None
    valor: Any = AUTOMATICO


@dataclass
class FilaEgm:
    nombre: str | None
    celdas: list[CeldaEgm] = field(default_factory=list)


@dataclass
class TablaEgm:
    """Una tabla de la hoja EGM: título numerado, encabezados y cuerpo.

    `fila` y `columna` (1-based) son la celda del título; los nombres de fila van en esa misma
    columna y los valores a su derecha.
    """

    numero: int
    titulo: str
    encabezado_nombres: str | None
    encabezados: list[str | None]
    filas: list[FilaEgm]
    fila: int
    columna: int = 1

    def mover(self, *, fila: int | None = None, columna: int | None = None) -> Self:
        if fila is not None:
            self.fila = fila
        if columna is not None:
            self.columna = columna
        return self

    def _indice_fila(self, fila: str | int) -> int:
        if isinstance(fila, int):
            return fila
        for i, f in enumerate(self.filas):
            if f.nombre == fila:
                return i
        raise KeyError(f"No hay fila {fila!r} en la tabla {self.numero}")

    def _indice_columna(self, columna: str | int) -> int:
        if isinstance(columna, int):
            return columna
        for i, e in enumerate(self.encabezados):
            if e == columna:
                return i
        raise KeyError(f"No hay columna {columna!r} en la tabla {self.numero}")

    def celda(self, fila: str | int, columna: str | int) -> CeldaEgm:
        return self.filas[self._indice_fila(fila)].celdas[self._indice_columna(columna)]

    def fijar_valor(self, fila: str | int, columna: str | int, valor: Any) -> Self:
        """Fija el valor guardado de una celda con fórmula: número, texto o `None` (ausente)."""
        self.celda(fila, columna).valor = valor
        return self

    def fijar_literal(self, fila: str | int, columna: str | int, valor: Any) -> Self:
        """Reemplaza la celda por un valor escrito, sin fórmula."""
        celda = self.celda(fila, columna)
        celda.terminos = None
        celda.literal = valor
        return self

    def renombrar_fila(self, viejo: str, nuevo: str | None) -> Self:
        self.filas[self._indice_fila(viejo)].nombre = nuevo
        return self

    def quitar_fila(self, nombre: str) -> Self:
        del self.filas[self._indice_fila(nombre)]
        return self

    def duplicar_fila(self, nombre: str) -> Self:
        """Repite una fila justo debajo de sí misma (nombre repetido dentro de la tabla)."""
        indice = self._indice_fila(nombre)
        self.filas.insert(indice + 1, copy.deepcopy(self.filas[indice]))
        return self

    def agregar_fila(self, nombre: str | None, valores: Sequence[Any] | None = None) -> Self:
        """Agrega una fila con valores escritos (uno por columna; los que falten, vacíos)."""
        dados = list(valores or [])
        dados += [None] * (len(self.encabezados) - len(dados))
        self.filas.append(FilaEgm(nombre, [CeldaEgm(literal=v) for v in dados]))
        return self

    def renombrar_columna(self, viejo: str, nuevo: str | None) -> Self:
        self.encabezados[self._indice_columna(viejo)] = nuevo
        return self

    def quitar_columna(self, encabezado: str) -> Self:
        indice = self._indice_columna(encabezado)
        del self.encabezados[indice]
        for f in self.filas:
            del f.celdas[indice]
        return self

    def duplicar_columna(self, encabezado: str) -> Self:
        """Repite una columna (con sus fórmulas) justo a la derecha de sí misma."""
        indice = self._indice_columna(encabezado)
        self.encabezados.insert(indice + 1, self.encabezados[indice])
        for f in self.filas:
            f.celdas.insert(indice + 1, copy.deepcopy(f.celdas[indice]))
        return self

    def sin_valores_guardados(self) -> Self:
        for f in self.filas:
            for c in f.celdas:
                if c.terminos is not None:
                    c.valor = None
        return self


@dataclass
class HojaEgm:
    """La hoja `EGM`: tablas con fórmulas sobre la hoja de la matriz y sus valores guardados."""

    nombre: str = HOJA_EGM
    tablas: list[TablaEgm] = field(default_factory=list)
    fila_final_formulas: int = 200
    guardar_valores: bool = True

    def tabla(self, numero: int) -> TablaEgm:
        """La primera tabla creada con ese número (aunque su título se haya cambiado)."""
        for t in self.tablas:
            if t.numero == numero:
                return t
        raise KeyError(f"No hay tabla {numero}")

    def quitar_tabla(self, numero: int) -> Self:
        self.tablas.remove(self.tabla(numero))
        return self

    def desplazar(self, *, filas: int = 0, columnas: int = 0) -> Self:
        """Corre todas las tablas (filas vacías antes, columnas vacías a la izquierda)."""
        for t in self.tablas:
            t.fila += filas
            t.columna += columnas
        return self

    def sin_valores_guardados(self) -> Self:
        """Ninguna celda con fórmula trae valor guardado (libro «sin calcular»)."""
        self.guardar_valores = False
        return self


# --- Empaquetado -------------------------------------------------------------------------------


@dataclass
class _Parte:
    """Una parte del paquete. `declarado` y `compresion_declarada` alteran solo el índice."""

    nombre: str
    datos: bytes
    compresion: int = zipfile.ZIP_DEFLATED
    declarado: int | None = None
    compresion_declarada: int | None = None


def _empaquetar(partes: Iterable[_Parte]) -> bytes:
    """Escribe el paquete con marcas de tiempo, atributos y orden fijos (mismos bytes siempre)."""
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for parte in partes:
            info = zipfile.ZipInfo(parte.nombre, date_time=_FECHA_PAQUETE)
            info.compress_type = parte.compresion
            info.create_system = 3
            info.external_attr = 0o644 << 16
            zf.writestr(info, parte.datos, compress_type=parte.compresion, compresslevel=6)
            # El índice se escribe al cerrar, desde estos objetos: aquí se altera lo declarado.
            registrada = zf.filelist[-1]
            if parte.declarado is not None:
                registrada.file_size = parte.declarado
            if parte.compresion_declarada is not None:
                registrada.compress_type = parte.compresion_declarada
    return salida.getvalue()


def _leer_partes(contenido: bytes) -> list[_Parte]:
    with zipfile.ZipFile(io.BytesIO(contenido)) as zf:
        return [_Parte(i.filename, zf.read(i.filename)) for i in zf.infolist()]


_PATRON_FORMULA = re.compile(r'<c r="([A-Z]+[0-9]+)"([^>]*)><f>(.*?)</f><v ?/></c>', re.DOTALL)


def _con_valores_guardados(xml: str, valores: Mapping[str, Any]) -> str:
    """Escribe el valor guardado en el `<v>` de cada celda con fórmula (R-4 del plan 001).

    `openpyxl` guarda la fórmula con un `<v/>` vacío; aquí se completa con el valor controlado.
    Un valor `None` deja la celda sin valor guardado.
    """

    def reemplazo(m: re.Match[str]) -> str:
        referencia, atributos, formula = m.group(1), m.group(2), m.group(3)
        valor = valores.get(referencia)
        if valor is None:
            return m.group(0)
        if isinstance(valor, bool):
            raise TypeError("Un valor guardado booleano no está soportado")
        if isinstance(valor, int | float):
            return f'<c r="{referencia}"{atributos}><f>{formula}</f><v>{valor!r}</v></c>'
        return (
            f'<c r="{referencia}"{atributos} t="str"><f>{formula}</f>'
            f"<v>{escape(str(valor))}</v></c>"
        )

    return _PATRON_FORMULA.sub(reemplazo, xml)


def _con_validaciones_x14(xml: str, validaciones: Sequence[tuple[str, str]]) -> str:
    """Agrega, al final de la hoja, listas guardadas como extensión `x14` (rango, fórmula)."""
    if not validaciones:
        return xml
    cuerpo = "".join(
        '<x14:dataValidation type="list" allowBlank="1" showInputMessage="1" '
        'showErrorMessage="1">'
        f"<x14:formula1><xm:f>{escape(formula)}</xm:f></x14:formula1>"
        f"<xm:sqref>{rango}</xm:sqref></x14:dataValidation>"
        for rango, formula in validaciones
    )
    extension = (
        f'<extLst><ext uri="{_URI_X14_VALIDACIONES}" xmlns:x14="{_NS_X14}">'
        f'<x14:dataValidations xmlns:xm="{_NS_XM}" count="{len(validaciones)}">{cuerpo}'
        "</x14:dataValidations></ext></extLst>"
    )
    cierre = "</worksheet>"
    if not xml.endswith(cierre):
        raise ValueError("La hoja generada no termina como se esperaba")
    return xml[: -len(cierre)] + extension + cierre


_PATRON_MODIFICADO = re.compile(r"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)")


def _referencia_a_hoja(nombre: str) -> str:
    """Nombre de hoja listo para una fórmula: con comillas simples solo si hace falta."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", nombre):
        return nombre
    return "'" + nombre.replace("'", "''") + "'"


# --- Contenido sintético de la base válida -----------------------------------------------------

_INTERVENCIONES = [f"Intervención {c}" for c in "ABCDEF"] + [VALOR_NO_APLICA_INTERVENCION]
_TIPOS_DOCUMENTO = [
    VALOR_EMPIRICO,
    "Documento teórico",
    "Documento metodológico",
    "Documento normativo",
]
_TIPOS_FUENTE = ["Académica", "Institucional", "Territorial"]
_METODOLOGIAS = ["Metodología A", "Metodología B", "Metodología C"]
_NIVELES = [VALOR_IMPACTO, "Estudio de caso", "Informe de proyecto", VALOR_NO_APLICA_NIVEL]
_DIMENSIONES = [f"Dimensión {n}" for n in range(1, 9)]


def _marcas(*unos: int) -> dict[str, int]:
    """Las ocho dimensiones: 1 en las indicadas (de 1 a 8) y 0 en las demás."""
    return {f"Dimensión {n}": int(n in unos) for n in range(1, 9)}


def _documento(
    numero: int,
    tipo: str,
    anio: int,
    fuente: str,
    principal: str,
    secundaria: str | None = None,
    *,
    nivel: str = VALOR_NO_APLICA_NIVEL,
    marcas: Mapping[str, int] | None = None,
    enfoque: str = "No desarrolla el enfoque.",
) -> dict[str, Any]:
    """Un documento sintético de la base válida (encabezado → valor)."""
    return {
        "N°": numero,
        "Referencia APA": f"Autor {numero} ({anio}). Documento sintético {numero}.",
        "Año": anio,
        "Tipo de documento": tipo,
        "País y población": "País sintético, población sintética",
        "Tipo de fuente": fuente,
        "Tipo de intervención (EGM)": principal,
        "Intervención secundaria (opcional)": secundaria,
        "Metodología": None if numero == 5 else "Metodología B",
        "Nivel de evidencia": nivel,
        **(marcas or {}),
        "Enfoque de género/diferencial": enfoque,
        "Principales hallazgos / tesis central": f"Hallazgo sintético {numero}.",
        "Aporte al proyecto": f"Aporte sintético {numero}.",
    }


# --- El constructor ----------------------------------------------------------------------------


class MatrizSintetica:
    """Constructor fluido de una matriz sintética (arquitectura §6.3, M23).

    Cada método que cambia la matriz devuelve el mismo objeto; `copia()` da una copia profunda
    para derivar variantes de una base. `a_bytes()` genera el libro `.xlsx` en memoria.
    """

    def __init__(self, *, hoja_matriz: str = HOJA_MATRIZ) -> None:
        self.hoja_matriz = hoja_matriz
        self._columnas: list[Columna] = []
        self._filas: list[dict[int, Any]] = []
        self._siguiente_id = 0
        self._fila_encabezado = 1
        self._validar_hasta = 36
        self._matriz_presente = True
        self._hojas_extra: dict[str, list[list[Any]]] = {}
        self._orden: list[str] = []
        self._egm: HojaEgm | None = None

    # ---- bases ----------------------------------------------------------------------------

    @classmethod
    def base_valida(cls) -> Self:
        """Matriz válida: los 17 roles, 8 dimensiones, listas escritas y por rango, 5 documentos.

        Documentos (todos sintéticos): N.º 1 teórico; N.º 2 empírico con intervención A principal
        y B secundaria, nivel de impacto, dimensiones 1 y 2; N.º 3 empírico con C, nivel de caso,
        dimensiones 3 y 4; N.º 4 empírico con A, nivel de informe, dimensión 1; N.º 5 normativo.
        La hoja `EGM` trae las tablas 1 a 4 con fórmulas y los valores guardados que daría la hoja.
        """
        m = cls()
        for encabezado, rol, lista, modo in (
            ("N°", "identificador", None, "escrita"),
            ("Referencia APA", "referencia", None, "escrita"),
            ("Año", "anio", None, "escrita"),
            ("Tipo de documento", "tipo_documento", _TIPOS_DOCUMENTO, "rango"),
            ("País y población", "pais_poblacion", None, "escrita"),
            ("Tipo de fuente", "tipo_fuente", _TIPOS_FUENTE, "escrita"),
            ("Tipo de intervención (EGM)", "intervencion_principal", _INTERVENCIONES, "escrita"),
            (
                "Intervención secundaria (opcional)",
                "intervencion_secundaria",
                _INTERVENCIONES,
                "escrita",
            ),
            ("Metodología", "metodologia", _METODOLOGIAS, "escrita"),
            ("Nivel de evidencia", "nivel_evidencia", _NIVELES, "rango"),
            (ENCABEZADO_DELIMITADOR_INICIAL, "delimitador_inicial", None, "escrita"),
            *((d, "dimension", ["1", "0"], "escrita") for d in _DIMENSIONES),
            (ENCABEZADO_DELIMITADOR_FINAL, "delimitador_final", None, "escrita"),
            ("Enfoque de género/diferencial", "enfoque", None, "escrita"),
            ("Principales hallazgos / tesis central", "hallazgos", None, "escrita"),
            ("Vacío de conocimiento identificado", "vacio", None, "escrita"),
            ("Limitaciones", "limitaciones", None, "escrita"),
            ("Aporte al proyecto", "aporte", None, "escrita"),
        ):
            m.agregar_columna(encabezado, rol=rol, lista=lista, modo_lista=modo)  # type: ignore[arg-type]
        for documento in (
            _documento(1, "Documento teórico", 2015, "Académica", VALOR_NO_APLICA_INTERVENCION),
            _documento(
                2, VALOR_EMPIRICO, 2019, "Institucional", "Intervención A", "Intervención B",
                nivel=VALOR_IMPACTO, marcas=_marcas(1, 2), enfoque="Sí. Incluye el enfoque.",
            ),
            _documento(
                3, VALOR_EMPIRICO, 2021, "Académica", "Intervención C",
                nivel="Estudio de caso", marcas=_marcas(3, 4),
                enfoque="Parcial. Solo en un componente.",
            ),
            _documento(
                4, VALOR_EMPIRICO, 2022, "Territorial", "Intervención A",
                nivel="Informe de proyecto", marcas=_marcas(1), enfoque="No. No lo desarrolla.",
            ),
            _documento(
                5, "Documento normativo", 2010, "Institucional", VALOR_NO_APLICA_INTERVENCION
            ),
        ):  # fmt: skip
            m.agregar_fila(documento)
        m.agregar_hoja(HOJA_INSTRUCCIONES, [["Instrucciones sintéticas de diligenciamiento."]])
        m.agregar_hoja(HOJA_GUIA, [["Guía sintética por tipo de documento."]])
        m.con_egm()
        return m

    def copia(self) -> Self:
        """Copia profunda: se puede alterar sin tocar el original."""
        return copy.deepcopy(self)

    # ---- hojas ----------------------------------------------------------------------------

    def _nombres_por_defecto(self) -> list[str]:
        nombres = [self.hoja_matriz] if self._matriz_presente else []
        if self._egm is not None:
            nombres.append(self._egm.nombre)
        nombres.extend(self._hojas_extra)
        if self._columnas_con_rango():
            nombres.append(HOJA_LISTAS)
        return nombres

    def nombres_de_hojas(self) -> list[str]:
        """Nombres de las hojas, en el orden en que quedarán en el libro."""
        por_defecto = self._nombres_por_defecto()
        pedidas = [n for n in self._orden if n in por_defecto]
        return pedidas + [n for n in por_defecto if n not in pedidas]

    def ordenar_hojas(self, *nombres: str) -> Self:
        """Pone las hojas indicadas primero, en ese orden; las demás siguen en su orden."""
        desconocidas = [n for n in nombres if n not in self._nombres_por_defecto()]
        if desconocidas:
            raise KeyError(f"No hay hojas {desconocidas!r}")
        self._orden = list(nombres)
        return self

    def agregar_hoja(self, nombre: str, filas: Sequence[Sequence[Any]]) -> Self:
        """Hoja auxiliar con las filas dadas (p. ej. `Instrucciones`)."""
        if nombre in self._nombres_por_defecto():
            raise ValueError(f"Ya existe la hoja {nombre!r}")
        self._hojas_extra[nombre] = [list(f) for f in filas]
        return self

    def renombrar_hoja(self, viejo: str, nuevo: str) -> Self:
        if nuevo in self._nombres_por_defecto():
            raise ValueError(f"Ya existe la hoja {nuevo!r}")
        if viejo == self.hoja_matriz and self._matriz_presente:
            self.hoja_matriz = nuevo
        elif self._egm is not None and viejo == self._egm.nombre:
            self._egm.nombre = nuevo
        elif viejo in self._hojas_extra:
            self._hojas_extra = {
                (nuevo if n == viejo else n): f for n, f in self._hojas_extra.items()
            }
        else:
            raise KeyError(f"No se puede renombrar la hoja {viejo!r}")
        self._orden = [nuevo if n == viejo else n for n in self._orden]
        return self

    def quitar_hoja(self, nombre: str) -> Self:
        """Quita una hoja. La hoja auxiliar de listas no se quita: existe si alguna lista la usa."""
        if nombre == self.hoja_matriz and self._matriz_presente:
            self._matriz_presente = False
        elif self._egm is not None and nombre == self._egm.nombre:
            self._egm = None
        elif nombre in self._hojas_extra:
            del self._hojas_extra[nombre]
        else:
            raise KeyError(f"No se puede quitar la hoja {nombre!r}")
        self._orden = [n for n in self._orden if n != nombre]
        return self

    # ---- columnas -------------------------------------------------------------------------

    def _columna(self, encabezado: str) -> Columna:
        for c in self._columnas:
            if c.encabezado == encabezado:
                return c
        raise KeyError(f"No hay columna {encabezado!r}")

    def _por_rol(self, rol: str) -> Columna | None:
        return next((c for c in self._columnas if c.rol == rol), None)

    def _indice_destino(
        self, antes_de: str | None, despues_de: str | None, posicion: int | None
    ) -> int:
        """Índice (base 0) donde insertar; sin indicación, al final. `posicion` es base 1."""
        indicaciones = [x for x in (antes_de, despues_de, posicion) if x is not None]
        if len(indicaciones) > 1:
            raise ValueError("Indique una sola de antes_de, despues_de y posicion")
        if antes_de is not None:
            return self._columnas.index(self._columna(antes_de))
        if despues_de is not None:
            return self._columnas.index(self._columna(despues_de)) + 1
        if posicion is not None:
            return max(0, min(posicion - 1, len(self._columnas)))
        return len(self._columnas)

    def agregar_columna(
        self,
        encabezado: str | None,
        *,
        rol: str | None = None,
        antes_de: str | None = None,
        despues_de: str | None = None,
        posicion: int | None = None,
        valores: Sequence[Any] | None = None,
        lista: Sequence[str] | None = None,
        modo_lista: ModoLista = "escrita",
    ) -> Self:
        """Agrega una columna; `valores` da una celda por fila existente (las demás, vacías)."""
        destino = self._indice_destino(antes_de, despues_de, posicion)
        columna = Columna(self._siguiente_id, encabezado, rol)
        self._siguiente_id += 1
        self._columnas.insert(destino, columna)
        for i, fila in enumerate(self._filas):
            if valores is not None and i < len(valores):
                fila[columna.id] = valores[i]
        if lista is not None:
            self._fijar_lista(columna, lista, modo_lista)
        return self

    def quitar_columna(self, encabezado: str) -> Self:
        columna = self._columna(encabezado)
        self._columnas.remove(columna)
        for fila in self._filas:
            fila.pop(columna.id, None)
        return self

    def renombrar_encabezado(self, viejo: str, nuevo: str | None) -> Self:
        self._columna(viejo).encabezado = nuevo
        return self

    def mover_columna(
        self,
        encabezado: str,
        *,
        antes_de: str | None = None,
        despues_de: str | None = None,
        posicion: int | None = None,
    ) -> Self:
        columna = self._columna(encabezado)
        self._columnas.remove(columna)
        self._columnas.insert(self._indice_destino(antes_de, despues_de, posicion), columna)
        return self

    def con_fila_encabezado(self, fila: int) -> Self:
        """Fila del archivo (base 1) donde van los encabezados; los datos van debajo."""
        if fila < 1:
            raise ValueError("La fila de encabezados es 1 o mayor")
        self._fila_encabezado = fila
        return self

    def encabezados(self) -> list[str | None]:
        """Encabezados de las columnas, en el orden del archivo."""
        return [c.encabezado for c in self._columnas]

    def _columnas_de_dimension(self) -> list[Columna]:
        inicial = self._por_rol("delimitador_inicial")
        final = self._por_rol("delimitador_final")
        if inicial is None or final is None:
            return []
        i, j = self._columnas.index(inicial), self._columnas.index(final)
        return [c for c in self._columnas[i + 1 : j] if c.rol in (None, "dimension")]

    def dimensiones(self) -> list[str]:
        """Encabezados de las columnas entre los dos delimitadores, en el orden del archivo."""
        return [c.encabezado for c in self._columnas_de_dimension() if c.encabezado is not None]

    # ---- listas de validación -------------------------------------------------------------

    @staticmethod
    def _revisar_lista(valores: Sequence[str], modo: ModoLista) -> list[str]:
        lista = list(valores)
        if not lista:
            raise ValueError("Una lista de validación no puede estar vacía")
        if modo == "escrita":
            if any("," in v for v in lista):
                raise ValueError("Un valor con coma no cabe en una lista escrita: use un rango")
            if len(",".join(lista)) > 255:
                raise ValueError("Una lista escrita no puede pasar de 255 caracteres")
        return lista

    def _fijar_lista(self, columna: Columna, valores: Sequence[str], modo: ModoLista) -> None:
        columna.lista = self._revisar_lista(valores, modo)
        columna.modo_lista = modo

    def con_lista(
        self, encabezado: str, valores: Sequence[str], *, modo: ModoLista = "escrita"
    ) -> Self:
        """Lista de validación de una columna: escrita en la validación, por rango o `x14`."""
        self._fijar_lista(self._columna(encabezado), valores, modo)
        return self

    def sin_lista(self, encabezado: str) -> Self:
        self._columna(encabezado).lista = None
        return self

    def _lista_de(self, encabezado: str) -> Columna:
        columna = self._columna(encabezado)
        if columna.lista is None:
            raise ValueError(f"La columna {encabezado!r} no tiene lista")
        return columna

    def agregar_valor_a_lista(
        self, encabezado: str, valor: str, *, posicion: int | None = None
    ) -> Self:
        """Agrega un valor a la lista (al final, o en `posicion`, base 1)."""
        columna = self._lista_de(encabezado)
        assert columna.lista is not None
        columna.lista.insert(len(columna.lista) if posicion is None else posicion - 1, valor)
        return self

    def quitar_valor_de_lista(self, encabezado: str, valor: str) -> Self:
        columna = self._lista_de(encabezado)
        assert columna.lista is not None
        columna.lista.remove(valor)
        return self

    def renombrar_valor_de_lista(self, encabezado: str, viejo: str, nuevo: str) -> Self:
        columna = self._lista_de(encabezado)
        assert columna.lista is not None
        columna.lista[columna.lista.index(viejo)] = nuevo
        return self

    def con_validacion_hasta(self, fila: int) -> Self:
        """Última fila del archivo (base 1) que cubren las validaciones (por defecto, la 36)."""
        self._validar_hasta = fila
        return self

    def _columnas_con_rango(self) -> list[Columna]:
        return [c for c in self._columnas if c.lista is not None and c.modo_lista != "escrita"]

    # ---- filas ----------------------------------------------------------------------------

    @property
    def n_filas(self) -> int:
        return len(self._filas)

    def agregar_fila(self, valores: Mapping[str, Any] | None = None) -> Self:
        """Agrega un documento: encabezado → valor (número, texto, vacío, espacios…)."""
        self._filas.append({self._columna(e).id: v for e, v in (valores or {}).items()})
        return self

    def agregar_filas_vacias(self, cantidad: int) -> Self:
        self._filas.extend({} for _ in range(cantidad))
        return self

    def fijar_celda(self, fila: int, encabezado: str, valor: Any) -> Self:
        """Cambia una celda; `fila` cuenta los documentos desde 0 (la primera fila de datos)."""
        self._filas[fila][self._columna(encabezado).id] = valor
        return self

    def reemplazar_valor(self, encabezado: str, viejo: Any, nuevo: Any) -> Self:
        """Cambia, en todos los documentos, las celdas de la columna que valen `viejo`."""
        columna = self._columna(encabezado)
        for fila in self._filas:
            if fila.get(columna.id) == viejo:
                fila[columna.id] = nuevo
        return self

    def quitar_filas(self) -> Self:
        self._filas.clear()
        return self

    def documentos(self) -> list[dict[str, Any]]:
        """Los documentos tal como se escribirán: encabezado → valor, en el orden de las filas.

        Una fila vacía es un diccionario vacío; las celdas vacías no aparecen. Es una copia.
        """
        nombres = {c.id: c.encabezado for c in self._columnas if c.encabezado is not None}
        return [
            {nombres[i]: v for i, v in fila.items() if i in nombres and v is not None}
            for fila in self._filas
        ]

    def valores_de_lista(self, encabezado: str) -> list[str] | None:
        """La lista de validación de la columna (copia), o `None` si no tiene."""
        lista = self._columna(encabezado).lista
        return None if lista is None else list(lista)

    # ---- hoja EGM -------------------------------------------------------------------------

    @property
    def egm(self) -> HojaEgm:
        if self._egm is None:
            raise ValueError("La matriz no tiene hoja EGM: use con_egm()")
        return self._egm

    def _ref(self, rol: str) -> _Ref:
        columna = self._por_rol(rol)
        if columna is None:
            raise ValueError(f"No hay columna con el rol {rol!r} para construir la hoja EGM")
        return _Ref(columna.id, get_column_letter(self._columnas.index(columna) + 1))

    def _ref_de(self, columna: Columna) -> _Ref:
        return _Ref(columna.id, get_column_letter(self._columnas.index(columna) + 1))

    def con_egm(
        self,
        *,
        valores_guardados: bool = True,
        fila_final_formulas: int = 200,
        nombre: str = HOJA_EGM,
    ) -> Self:
        """Agrega la hoja `EGM` con las tablas 1 a 4 según las categorías de la matriz actual.

        Tabla 1: total de estudios (principal + secundaria) por intervención y dimensión, más
        `Total estudios`. Tabla 2: igual, solo evaluaciones de impacto. Tabla 3: enfoque (Sí, No,
        Parcial) por intervención; no es comparable. Tabla 4: estudios por nivel. Cada celda es una
        suma de `COUNTIFS` sobre las filas 2 a `fila_final_formulas` de la hoja de la matriz; el
        valor guardado es el que daría la hoja, calculado al generar el libro.
        """
        if self._egm is not None:
            raise ValueError("La matriz ya tiene hoja EGM")
        tipo, principal = self._ref("tipo_documento"), self._ref("intervencion_principal")
        secundaria, nivel = self._ref("intervencion_secundaria"), self._ref("nivel_evidencia")
        enfoque = self._ref("enfoque")
        dimensiones = [(c.encabezado, self._ref_de(c)) for c in self._columnas_de_dimension()]

        def sin_no_aplica(encabezado: str) -> list[str]:
            lista = self._columna(encabezado).lista or []
            return [v for v in lista if not v.startswith("No aplica")]

        intervenciones = sin_no_aplica("Tipo de intervención (EGM)")
        niveles = sin_no_aplica("Nivel de evidencia")
        empirico = _Criterio(tipo, "prefijo", "Estudio empírico")
        impacto = _Criterio(nivel, "igual", VALOR_IMPACTO)

        def por_intervencion(*extra: _Criterio) -> tuple[_Termino, ...]:
            return tuple(
                (_Criterio(ref, "nombre"), empirico, *extra) for ref in (principal, secundaria)
            )

        def tabla_de_intervenciones(
            numero: int, titulo: str, con_impacto: bool, fila: int
        ) -> TablaEgm:
            base = (impacto,) if con_impacto else ()
            encabezados: list[str | None] = [d for d, _ in dimensiones] + [ENCABEZADO_TOTAL]
            cuerpo = [
                FilaEgm(
                    nombre,
                    [
                        *(
                            CeldaEgm(por_intervencion(*base, _Criterio(ref, "uno")))
                            for _, ref in dimensiones
                        ),
                        CeldaEgm(por_intervencion(*base)),
                    ],
                )
                for nombre in intervenciones
            ]
            return TablaEgm(numero, titulo, "Intervención", encabezados, cuerpo, fila)

        tablas: list[TablaEgm] = []
        cursor = 1
        for numero, titulo, con_impacto in (
            (1, "1. Número total de estudios por intervención y dimensión", False),
            (2, "2. Evaluación de impacto por intervención y dimensión", True),
        ):
            tablas.append(tabla_de_intervenciones(numero, titulo, con_impacto, cursor))
            cursor += 2 + len(intervenciones) + 1
        prefijos = ("Sí", "No", "Parcial")
        tablas.append(
            TablaEgm(
                3,
                "3. Estudios por enfoque diferencial",
                "Intervención",
                list(prefijos),
                [
                    FilaEgm(
                        nombre,
                        [
                            CeldaEgm(
                                tuple(
                                    (
                                        _Criterio(ref, "nombre"),
                                        empirico,
                                        _Criterio(enfoque, "prefijo", p),
                                    )
                                    for ref in (principal, secundaria)
                                )
                            )
                            for p in prefijos
                        ],
                    )
                    for nombre in intervenciones
                ],
                cursor,
            )
        )
        cursor += 2 + len(intervenciones) + 1
        tablas.append(
            TablaEgm(
                4,
                "4. Estudios por nivel de evidencia",
                "Nivel",
                ["Estudios"],
                [
                    FilaEgm(n, [CeldaEgm(((_Criterio(nivel, "nombre"), empirico),))])
                    for n in niveles
                ],
                cursor,
            )
        )
        self._egm = HojaEgm(nombre, tablas, fila_final_formulas, valores_guardados)
        return self

    # ---- evaluación de la hoja (semántica de COUNTIFS) -------------------------------------

    def _valor_de(self, fila: Mapping[int, Any], ref: _Ref) -> Any:
        return fila.get(ref.id)

    def _cumple(self, criterio: _Criterio, valor: Any, nombre: str | None) -> bool:
        if criterio.tipo == "uno":
            # `COUNTIFS(..., 1)` cuenta el número 1 y también el texto «1».
            return (
                isinstance(valor, int | float) and not isinstance(valor, bool) and valor == 1
            ) or (isinstance(valor, str) and valor == "1")
        if not isinstance(valor, str):
            return False
        if criterio.tipo == "nombre":
            return nombre is not None and valor.casefold() == nombre.casefold()
        if criterio.tipo == "prefijo":
            return valor.casefold().startswith(criterio.texto.casefold())
        return valor.casefold() == criterio.texto.casefold()

    def _contar(self, terminos: tuple[_Termino, ...], nombre: str | None, hasta: int) -> int:
        total = 0
        for i, fila in enumerate(self._filas):
            if self._fila_encabezado + 1 + i > hasta:
                break
            for termino in terminos:
                if all(self._cumple(c, self._valor_de(fila, c.ref), nombre) for c in termino):
                    total += 1
        return total

    def _letra(self, ref: _Ref) -> str:
        for i, c in enumerate(self._columnas):
            if c.id == ref.id:
                return get_column_letter(i + 1)
        return ref.letra_respaldo

    def _formula(self, celda: CeldaEgm, nombre_celda: str, hasta: int) -> str:
        """`=COUNTIFS(...)+COUNTIFS(...)` con rangos absolutos sobre la hoja de la matriz."""
        hoja = _referencia_a_hoja(self.hoja_matriz)
        desde = self._fila_encabezado + 1
        sumandos = []
        for termino in celda.terminos or ():
            partes = []
            for c in termino:
                letra = self._letra(c.ref)
                rango = f"{hoja}!${letra}${desde}:${letra}${hasta}"
                if c.tipo == "nombre":
                    texto = nombre_celda
                elif c.tipo == "uno":
                    texto = "1"
                elif c.tipo == "prefijo":
                    texto = '"' + c.texto.replace('"', '""') + '*"'
                else:
                    texto = '"' + c.texto.replace('"', '""') + '"'
                partes.append(f"{rango},{texto}")
            sumandos.append("COUNTIFS(" + ",".join(partes) + ")")
        return "=" + "+".join(sumandos)

    # ---- generación -----------------------------------------------------------------------

    def _escribir_matriz(self, hoja: Any) -> None:
        fe = self._fila_encabezado
        for j, columna in enumerate(self._columnas, start=1):
            if columna.encabezado is not None:
                hoja.cell(fe, j).value = columna.encabezado
        for i, fila in enumerate(self._filas):
            for j, columna in enumerate(self._columnas, start=1):
                valor = fila.get(columna.id)
                if valor is None:
                    continue
                celda = hoja.cell(fe + 1 + i, j)
                celda.value = valor
                if isinstance(valor, str) and valor.startswith("="):
                    celda.data_type = "s"  # un texto que empieza por «=» sigue siendo texto

    def _rangos_de_listas(self) -> dict[int, str]:
        """Para cada columna con lista por rango o `x14`: su rango en la hoja de listas."""
        rangos = {}
        nombre = _referencia_a_hoja(HOJA_LISTAS)
        for k, columna in enumerate(self._columnas_con_rango(), start=1):
            assert columna.lista is not None
            letra = get_column_letter(k)
            rangos[columna.id] = f"{nombre}!${letra}$2:${letra}${1 + len(columna.lista)}"
        return rangos

    def _escribir_listas(self, hoja: Any) -> None:
        for k, columna in enumerate(self._columnas_con_rango(), start=1):
            assert columna.lista is not None
            hoja.cell(1, k).value = columna.encabezado
            for i, valor in enumerate(columna.lista, start=2):
                hoja.cell(i, k).value = valor

    def _validaciones(self, hoja: Any) -> list[tuple[str, str]]:
        """Agrega las validaciones normales; devuelve las de extensión `x14` (rango, fórmula)."""
        desde = self._fila_encabezado + 1
        hasta = max(self._validar_hasta, self._fila_encabezado + len(self._filas), desde)
        rangos = self._rangos_de_listas()
        x14 = []
        for j, columna in enumerate(self._columnas, start=1):
            if columna.lista is None:
                continue
            letra = get_column_letter(j)
            area = f"{letra}{desde}:{letra}{hasta}"
            if columna.modo_lista == "x14":
                x14.append((area, rangos[columna.id]))
                continue
            formula = (
                '"' + ",".join(columna.lista) + '"'
                if columna.modo_lista == "escrita"
                else rangos[columna.id]
            )
            validacion = DataValidation(type="list", formula1=formula, allow_blank=True)
            validacion.add(area)
            hoja.add_data_validation(validacion)
        return x14

    def _escribir_egm(self, hoja: Any, valores: dict[str, Any]) -> None:
        egm = self.egm
        for tabla in egm.tablas:
            col = tabla.columna
            hoja.cell(tabla.fila, col).value = tabla.titulo
            if tabla.encabezado_nombres is not None:
                hoja.cell(tabla.fila + 1, col).value = tabla.encabezado_nombres
            for j, encabezado in enumerate(tabla.encabezados, start=1):
                if encabezado is not None:
                    hoja.cell(tabla.fila + 1, col + j).value = encabezado
            letra_nombres = get_column_letter(col)
            for i, fila in enumerate(tabla.filas):
                r = tabla.fila + 2 + i
                if fila.nombre is not None:
                    hoja.cell(r, col).value = fila.nombre
                for j, celda in enumerate(fila.celdas, start=1):
                    destino = hoja.cell(r, col + j)
                    if celda.terminos is None:
                        if celda.literal is not None:
                            destino.value = celda.literal
                        continue
                    destino.value = self._formula(
                        celda, f"${letra_nombres}{r}", egm.fila_final_formulas
                    )
                    if not egm.guardar_valores:
                        continue
                    valor = celda.valor
                    if valor is AUTOMATICO:
                        valor = self._contar(celda.terminos, fila.nombre, egm.fila_final_formulas)
                    valores[destino.coordinate] = valor

    def _partes(self) -> list[_Parte]:
        """Partes del paquete del libro, con valores guardados y extensiones ya escritos."""
        nombres = self.nombres_de_hojas()
        if not nombres:
            raise ValueError("El libro no tiene ninguna hoja")
        libro = Workbook()
        libro.remove(libro.active)  # type: ignore[arg-type]
        libro.properties.creator = "constructor sintetico"
        libro.properties.created = FECHA_FIJA
        libro.properties.modified = FECHA_FIJA
        guardados: dict[str, dict[str, Any]] = {}
        x14: dict[str, list[tuple[str, str]]] = {}
        for nombre in nombres:
            hoja = libro.create_sheet(nombre)
            if self._matriz_presente and nombre == self.hoja_matriz:
                self._escribir_matriz(hoja)
                x14[nombre] = self._validaciones(hoja)
            elif self._egm is not None and nombre == self._egm.nombre:
                guardados[nombre] = {}
                self._escribir_egm(hoja, guardados[nombre])
            elif nombre in self._hojas_extra:
                for i, fila in enumerate(self._hojas_extra[nombre], start=1):
                    for j, valor in enumerate(fila, start=1):
                        hoja.cell(i, j).value = valor
            else:
                self._escribir_listas(hoja)
        bruto = io.BytesIO()
        libro.save(bruto)
        partes = _leer_partes(bruto.getvalue())
        rutas = {f"xl/worksheets/sheet{i}.xml": n for i, n in enumerate(nombres, start=1)}
        for parte in partes:
            if parte.nombre in rutas:
                nombre = rutas[parte.nombre]
                xml = parte.datos.decode("utf-8")
                xml = _con_valores_guardados(xml, guardados.get(nombre, {}))
                xml = _con_validaciones_x14(xml, x14.get(nombre, []))
                parte.datos = xml.encode("utf-8")
            elif parte.nombre == "docProps/core.xml":
                xml = parte.datos.decode("utf-8")
                fecha = FECHA_FIJA.strftime("%Y-%m-%dT%H:%M:%SZ")
                parte.datos = _PATRON_MODIFICADO.sub(rf"\g<1>{fecha}\g<2>", xml).encode("utf-8")
        return partes

    def _ruta_de_la_hoja_de_la_matriz(self) -> str:
        nombres = self.nombres_de_hojas()
        nombre = self.hoja_matriz if self._matriz_presente else nombres[0]
        return f"xl/worksheets/sheet{nombres.index(nombre) + 1}.xml"

    # ---- salidas --------------------------------------------------------------------------

    def a_bytes(self) -> bytes:
        """El libro `.xlsx`, en memoria. Mismos bytes en cada generación."""
        return _empaquetar(self._partes())

    def a_bytes_danado(self) -> bytes:
        """El libro cortado a la mitad: empieza como un paquete y no se puede abrir."""
        contenido = self.a_bytes()
        return contenido[: len(contenido) // 2]

    def a_bytes_de_tamano(self, tamano: int) -> bytes:
        """El libro con exactamente `tamano` bytes, con una parte de relleno sin comprimir.

        El relleno es una parte ajena al libro (`docProps/relleno.bin`) que `openpyxl` ignora.
        """
        partes = self._partes()
        minimo = len(_empaquetar([*partes, _Parte(_RELLENO, b"", zipfile.ZIP_STORED)]))
        if tamano < minimo:
            raise ValueError(
                f"El tamaño pedido ({tamano}) es menor que el mínimo posible ({minimo})"
            )
        contenido = _empaquetar(
            [*partes, _Parte(_RELLENO, bytes(tamano - minimo), zipfile.ZIP_STORED)]
        )
        if len(contenido) != tamano:
            raise AssertionError(f"El libro pesa {len(contenido)} bytes y se pidieron {tamano}")
        return contenido

    def a_bytes_con_descomprimido_declarado(
        self, declarado: int, *, datos_invalidos: bool = False
    ) -> bytes:
        """El libro cuyo índice declara, sumando todas sus partes, exactamente `declarado` bytes.

        Se logra editando el tamaño descomprimido declarado de una parte de relleno
        (`docProps/relleno.bin`): el paquete real pesa poco y no se descomprime nada. Con
        `datos_invalidos=True`, los datos de esa parte no son un flujo de compresión válido.
        """
        partes = self._partes()
        real = sum(len(p.datos) for p in partes)
        relleno_declarado = declarado - real
        if relleno_declarado < 0:
            raise ValueError(f"El declarado pedido ({declarado}) es menor que lo real ({real})")
        if datos_invalidos:
            relleno = _Parte(
                _RELLENO,
                b"\xff" * 64,
                zipfile.ZIP_STORED,
                relleno_declarado,
                zipfile.ZIP_DEFLATED,
            )
        else:
            relleno = _Parte(_RELLENO, bytes(16), zipfile.ZIP_DEFLATED, relleno_declarado)
        return _empaquetar([*partes, relleno])

    def a_bytes_con_parte_mayor_que_lo_declarado(self, *, tamano_real: int = 1_048_576) -> bytes:
        """El libro con una parte (la hoja de la matriz) que se descomprime a `tamano_real` bytes
        y cuyo índice declara solo su tamaño original, menor (insumo de NC-ARQ-1).

        La parte se agranda con un comentario XML de relleno al final de la hoja; comprimido pesa
        poco.
        """
        partes = self._partes()
        ruta = self._ruta_de_la_hoja_de_la_matriz()
        parte = next(p for p in partes if p.nombre == ruta)
        original = parte.datos
        cierre = b"</worksheet>"
        falta = tamano_real - len(original) - len(b"<!---->")
        if falta < 0:
            raise ValueError(
                f"El tamaño real pedido ({tamano_real}) no alcanza para la hoja ({len(original)})"
            )
        parte.datos = original[: -len(cierre)] + b"<!--" + b"x" * falta + b"-->" + cierre
        parte.declarado = len(original)
        return _empaquetar(partes)


# --- Archivos de carga que no son libros -------------------------------------------------------


def archivo_de_texto() -> bytes:
    """Un archivo de otro tipo: texto plano."""
    return "Este archivo de prueba es texto plano y no un libro de hoja de cálculo.\n".encode()


def archivo_extension_xlsx_otro_contenido(variante: str = "texto") -> bytes:
    """Contenido que se subiría con nombre `.xlsx` sin ser un libro.

    `variante="texto"`: texto plano. `variante="zip_sin_libro"`: un paquete ZIP válido que no
    tiene las partes de un libro de hoja de cálculo.
    """
    if variante == "texto":
        texto = "Contenido de otro tipo guardado con el nombre de un libro.\n"
        return texto.encode()
    if variante == "zip_sin_libro":
        documento = "Un documento de texto.\n"
        return _empaquetar([_Parte("documento.txt", documento.encode())])
    raise ValueError(f"La variante {variante!r} no existe")


def parte_mayor_que_lo_declarado() -> bytes:
    """Fixture en memoria `parte_mayor_que_lo_declarado` (NC-ARQ-1): base válida con la hoja de
    la matriz de 1 048 576 bytes descomprimidos y un índice que declara menos."""
    return MatrizSintetica.base_valida().a_bytes_con_parte_mayor_que_lo_declarado()


# --- Catálogo de fixtures (T-001-07) -----------------------------------------------------------

LIMITE_TAMANO = 15_728_640
"""NFR-000-19: tamaño máximo de un archivo cargado (15 MiB), en bytes."""
LIMITE_DESCOMPRIMIDO = 268_435_456
"""NFR-000-19: contenido descomprimido declarado máximo (256 MiB), en bytes."""

_TIPO = "Tipo de documento"
_FUENTE = "Tipo de fuente"
_PRINCIPAL = "Tipo de intervención (EGM)"
_SECUNDARIA = "Intervención secundaria (opcional)"
_METODOLOGIA = "Metodología"
_NIVEL = "Nivel de evidencia"
_ANIO = "Año"
_ENFOQUE = "Enfoque de género/diferencial"
_COLUMNAS_DE_INTERVENCION = (_PRINCIPAL, _SECUNDARIA)

Generador = Callable[[], bytes]


def _base() -> MatrizSintetica:
    return MatrizSintetica.base_valida()


def _empirico(numero: int, cambios: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Estudio empírico sintético que entra al mapa: intervención D, nivel de caso, dimensión 5."""
    documento = _documento(
        numero,
        VALOR_EMPIRICO,
        2020,
        "Académica",
        "Intervención D",
        nivel="Estudio de caso",
        marcas=_marcas(5),
    )
    return {**documento, **(cambios or {})}


def _no_empirico(numero: int, cambios: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Documento metodológico sintético, sin intervención (valor «No aplica…»)."""
    documento = _documento(
        numero, "Documento metodológico", 2018, "Institucional", VALOR_NO_APLICA_INTERVENCION
    )
    return {**documento, **(cambios or {})}


def _regenerar_egm(matriz: MatrizSintetica, **opciones: Any) -> MatrizSintetica:
    """Vuelve a armar la hoja `EGM` con las categorías y el contenido actuales de la matriz."""
    return matriz.quitar_hoja(HOJA_EGM).con_egm(**opciones)


def _agregar_intervencion(matriz: MatrizSintetica, nombre: str) -> None:
    """Agrega una intervención a las dos listas, antes del valor «No aplica…» (posición 7)."""
    for columna in _COLUMNAS_DE_INTERVENCION:
        matriz.agregar_valor_a_lista(columna, nombre, posicion=7)


def _quitar_intervencion(matriz: MatrizSintetica, nombre: str) -> None:
    for columna in _COLUMNAS_DE_INTERVENCION:
        matriz.quitar_valor_de_lista(columna, nombre)


def _renombrar_intervencion(matriz: MatrizSintetica, viejo: str, nuevo: str) -> None:
    """Renombra una intervención en las dos listas y en todos los documentos."""
    for columna in _COLUMNAS_DE_INTERVENCION:
        matriz.renombrar_valor_de_lista(columna, viejo, nuevo)
        matriz.reemplazar_valor(columna, viejo, nuevo)


def _con_documentos_hasta(matriz: MatrizSintetica, total: int) -> MatrizSintetica:
    """Repite en ciclo los documentos que ya tiene, con su N.º, hasta llegar a `total`."""
    plantillas = [dict(fila) for fila in matriz._filas]
    id_numero = matriz._columna("N°").id
    id_referencia = matriz._columna("Referencia APA").id
    for numero in range(len(plantillas) + 1, total + 1):
        fila = dict(plantillas[(numero - 1) % len(plantillas)])
        fila[id_numero] = numero
        fila[id_referencia] = f"Autor {numero}. Documento sintético {numero}."
        matriz._filas.append(fila)
    return matriz


# ---- CB-01 a CB-15 -----------------------------------------------------------------------------


def _cb01() -> bytes:
    """Fila solo con N.º y referencia (sin tipo de documento ni ningún otro dato)."""
    fila = {"N°": 6, "Referencia APA": "Autor 6 (2020). Documento sintético 6."}
    return _base().agregar_fila(fila).a_bytes()


def _cb02() -> bytes:
    """Estudio empírico sin intervención (principal y secundaria vacías), con una dimensión en 1."""
    cambios = {_PRINCIPAL: None, _SECUNDARIA: None}
    return _base().agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb03() -> bytes:
    """Estudio empírico con intervención y ninguna dimensión en 1 (todas en 0)."""
    return _base().agregar_fila(_empirico(6, _marcas())).a_bytes()


def _cb04() -> bytes:
    """Estudio empírico con la principal vacía, la secundaria diligenciada y una dimensión en 1."""
    cambios = {_PRINCIPAL: None, _SECUNDARIA: "Intervención D"}
    return _base().agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb05() -> bytes:
    """Dos estudios del mapa: uno sin nivel de evidencia y otro con un nivel «No aplica…»."""
    matriz = _base().agregar_fila(_empirico(6, {_NIVEL: None}))
    return matriz.agregar_fila(_empirico(7, {_NIVEL: VALOR_NO_APLICA_NIVEL})).a_bytes()


def _cb06() -> bytes:
    """Dos documentos no empíricos con datos propios; el primero sin nivel de evidencia."""
    matriz = _base().agregar_fila(_no_empirico(6, {_NIVEL: None, _METODOLOGIA: None}))
    return matriz.agregar_fila(_no_empirico(7, {_TIPO: "Documento teórico"})).a_bytes()


def _cb07() -> bytes:
    """Estudio empírico con la misma intervención en la principal y en la secundaria."""
    cambios = {_SECUNDARIA: "Intervención D"}
    return _base().agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb08() -> bytes:
    """Documento no empírico con una intervención distinta de «No aplica…» y una dimensión en 1."""
    cambios = {_PRINCIPAL: "Intervención D", **_marcas(1)}
    return _base().agregar_fila(_no_empirico(6, cambios)).a_bytes()


def _cb09() -> bytes:
    """Estudio con dimensiones fuera de {0, 1, vacío}: el número 2 y el texto «Sí»."""
    cambios = {"Dimensión 2": 2, "Dimensión 3": "Sí"}
    return _base().agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb10() -> bytes:
    """Estudio con tipo de fuente, metodología y nivel que no están en sus listas."""
    cambios = {
        _FUENTE: "Fuente fuera de lista",
        _METODOLOGIA: "Metodología fuera de lista",
        _NIVEL: "Nivel fuera de lista",
    }
    return _base().agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb11() -> bytes:
    """Tres estudios del mapa con un enfoque que no empieza por Sí, No ni Parcial."""
    matriz = _base()
    for numero, texto in (
        (6, "Nota: el documento menciona el enfoque de forma general."),
        (7, "Si bien el estudio menciona a las mujeres, no desarrolla el enfoque."),
        (8, "El estudio incorpora el enfoque en la muestra."),
    ):
        matriz.agregar_fila(_empirico(numero, {_ENFOQUE: texto}))
    return matriz.a_bytes()


def _cb12() -> bytes:
    """250 documentos (filas 2 a 251); las fórmulas de la hoja `EGM` llegan a la fila 200."""
    return _con_documentos_hasta(_base(), 250).a_bytes()


def _cb13() -> bytes:
    """Un empírico con N.º vacío y contenido, y otro documento que repite el N.º 3."""
    matriz = _base().agregar_fila(_empirico(6, {"N°": None}))
    repetido = _empirico(3, {"Referencia APA": "Autor 3 (2020). Otro documento con el N.º 3."})
    return matriz.agregar_fila(repetido).a_bytes()


def _cb14() -> bytes:
    """Falta el encabezado de rol «Nivel de evidencia»."""
    return _base().quitar_columna(_NIVEL).a_bytes()


def _cb15() -> bytes:
    """Falta la hoja «Matriz bibliográfica»."""
    return _base().quitar_hoja(HOJA_MATRIZ).a_bytes()


# ---- CB-16 a CB-30 -----------------------------------------------------------------------------


def _cb16_danado() -> bytes:
    """Paquete cortado a la mitad."""
    return _base().a_bytes_danado()


def _cb18() -> bytes:
    """Columna «Observaciones» fuera del bloque de dimensiones, sin lista `1,0`."""
    valores = ["Nota sintética 1", None, "Nota sintética 3"]
    return _base().agregar_columna("Observaciones", valores=valores).a_bytes()


def _cb19() -> bytes:
    """Columna ajena fuera del bloque de dimensiones, con lista `1,0`."""
    matriz = _base().agregar_columna("Marca de revisión", lista=["1", "0"], valores=[1, 0, 1, 0, 1])
    return matriz.a_bytes()


def _cb20() -> bytes:
    """Ningún valor de la lista de tipo empieza por «Estudio empírico»."""
    nuevo = "Estudio de campo"
    matriz = _base().renombrar_valor_de_lista(_TIPO, VALOR_EMPIRICO, nuevo)
    matriz.reemplazar_valor(_TIPO, VALOR_EMPIRICO, nuevo)
    return _regenerar_egm(matriz).a_bytes()


def _cb21() -> bytes:
    """La lista de nivel no incluye «Evaluación de impacto»."""
    nuevo = "Evaluación de resultados"
    matriz = _base().renombrar_valor_de_lista(_NIVEL, VALOR_IMPACTO, nuevo)
    matriz.reemplazar_valor(_NIVEL, VALOR_IMPACTO, nuevo)
    return _regenerar_egm(matriz).a_bytes()


def _cb22() -> bytes:
    """Ningún valor de la lista de nivel empieza por «No aplica»."""
    matriz = _base().quitar_valor_de_lista(_NIVEL, VALOR_NO_APLICA_NIVEL)
    return matriz.reemplazar_valor(_NIVEL, VALOR_NO_APLICA_NIVEL, None).a_bytes()


def _cb23() -> bytes:
    """Dos valores de la lista de tipo empiezan por «Estudio empírico»."""
    otro = "Estudio empírico (modalidad ampliada)"
    matriz = _base().agregar_valor_a_lista(_TIPO, otro, posicion=2)
    return matriz.agregar_fila(_empirico(6, {_TIPO: otro})).a_bytes()


def _sin_lista(columna: str) -> Generador:
    """Fixture con la columna sin lista de validación y todo lo demás igual a la base."""

    def construir() -> bytes:
        return _base().sin_lista(columna).a_bytes()

    return construir


def _cb26() -> bytes:
    """Tipo de documento sin lista, con un valor no vacío distinto del ancla."""
    matriz = _base().sin_lista(_TIPO)
    return matriz.agregar_fila(_no_empirico(6, {_TIPO: "Marco teórico"})).a_bytes()


def _cb27() -> bytes:
    """Años no numéricos: «s. f.» y un año escrito como texto."""
    matriz = _base().agregar_fila(_empirico(6, {_ANIO: "s. f."}))
    return matriz.agregar_fila(_empirico(7, {_ANIO: "2019"})).a_bytes()


def _cb28() -> bytes:
    """Un documento con el tipo vacío y otro con un tipo fuera de la lista."""
    matriz = _base().agregar_fila(_empirico(6, {_TIPO: None}))
    return matriz.agregar_fila(_empirico(7, {_TIPO: "Tipo fuera de lista"})).a_bytes()


def _cb29_sin_hoja() -> bytes:
    """Sin la hoja `EGM`."""
    return _base().quitar_hoja(HOJA_EGM).a_bytes()


def _cb29_titulo() -> bytes:
    """El título de la tabla 1 ya no trae su frase propia."""
    matriz = _base()
    matriz.egm.tabla(1).titulo = "1. Resumen por intervención y dimensión"
    return matriz.a_bytes()


def _cb30() -> bytes:
    """La hoja `EGM` trae las fórmulas y ningún valor guardado."""
    matriz = _base()
    matriz.egm.sin_valores_guardados()
    return matriz.a_bytes()


# ---- CB-31 a CB-41 -----------------------------------------------------------------------------


def _cb31() -> bytes:
    """«Intervención G» en las listas y en un estudio, sin fila en las tablas de la hoja."""
    matriz = _base()
    _agregar_intervencion(matriz, "Intervención G")
    return matriz.agregar_fila(_empirico(6, {_PRINCIPAL: "Intervención G"})).a_bytes()


def _cb32() -> bytes:
    """«Intervención F» sale de las listas (ningún estudio la usa) y sigue como fila de la hoja."""
    matriz = _base()
    _quitar_intervencion(matriz, "Intervención F")
    return matriz.a_bytes()


def _parcial(con_diferencia: bool) -> bytes:
    """Tabla 1 con valores guardados solo en las filas A y B; con una diferencia, A × dim. 1 = 5."""
    matriz = _base()
    tabla = matriz.egm.tabla(1)
    for fila in tabla.filas:
        if fila.nombre not in ("Intervención A", "Intervención B"):
            for encabezado in tabla.encabezados:
                tabla.fijar_valor(fila.nombre, encabezado, None)
    if con_diferencia:
        tabla.fijar_valor("Intervención A", "Dimensión 1", 5)
    return matriz.a_bytes()


def _cb33_sin_diferencia() -> bytes:
    """Tabla 1 con solo algunos valores guardados, todos correctos."""
    return _parcial(False)


def _cb33_con_diferencia() -> bytes:
    """Tabla 1 con solo algunos valores guardados, uno distinto del conteo."""
    return _parcial(True)


def _cb34_sin_total() -> bytes:
    """La tabla 1 sin la columna «Total estudios»."""
    matriz = _base()
    matriz.egm.tabla(1).quitar_columna(ENCABEZADO_TOTAL)
    return matriz.a_bytes()


def _cb34_repetido() -> bytes:
    """La tabla 1 con la columna «Total estudios» dos veces."""
    matriz = _base()
    matriz.egm.tabla(1).duplicar_columna(ENCABEZADO_TOTAL)
    return matriz.a_bytes()


def _cb35() -> bytes:
    """La tabla 1 repite la fila «Intervención D»."""
    matriz = _base()
    matriz.egm.tabla(1).duplicar_fila("Intervención D")
    for tabla in matriz.egm.tablas[1:]:
        tabla.fila += 1  # las tablas siguientes bajan una fila: sigue la fila vacía entre tablas
    return matriz.a_bytes()


def _cb36() -> bytes:
    """Una intervención y un nivel agregados a las listas, usados por un estudio."""
    matriz = _base()
    _agregar_intervencion(matriz, "Intervención G")
    matriz.agregar_valor_a_lista(_NIVEL, "Estudio cuasiexperimental", posicion=4)
    cambios = {_PRINCIPAL: "Intervención G", _NIVEL: "Estudio cuasiexperimental"}
    return matriz.agregar_fila(_empirico(6, cambios)).a_bytes()


def _cb37() -> bytes:
    """Dos columnas agregadas dentro del bloque: «Dimensión nueva» con `1,0` y otra sin lista."""
    matriz = _base()
    matriz.agregar_columna(
        "Dimensión nueva",
        rol="dimension",
        despues_de="Dimensión 4",
        lista=["1", "0"],
        valores=[None, 1, 0, 1, None],
    )
    matriz.agregar_columna(
        "Dimensión sin lista",
        rol="dimension",
        antes_de=ENCABEZADO_DELIMITADOR_FINAL,
        valores=[None, 0, 1, None, None],
    )
    return matriz.a_bytes()


def _cb38_invertido() -> bytes:
    """El delimitador final queda antes del inicial."""
    matriz = _base()
    matriz.mover_columna(ENCABEZADO_DELIMITADOR_FINAL, antes_de=ENCABEZADO_DELIMITADOR_INICIAL)
    return matriz.a_bytes()


def _cb38_vacio() -> bytes:
    """Ninguna columna entre los dos delimitadores (la hoja `EGM` se arma sin dimensiones)."""
    matriz = _base()
    for dimension in _DIMENSIONES:
        matriz.quitar_columna(dimension)
    return _regenerar_egm(matriz).a_bytes()


def _cb39() -> bytes:
    """Un encabezado de rol («Metodología») dentro del bloque de dimensiones."""
    return _base().mover_columna(_METODOLOGIA, despues_de="Dimensión 4").a_bytes()


def _cb40() -> bytes:
    """Intervención C y nivel «Informe de proyecto» retirados de las listas (siguen en filas) y
    «Dimensión 8» retirada de la matriz; la hoja `EGM` conserva sus filas y columnas."""
    matriz = _base()
    _quitar_intervencion(matriz, "Intervención C")
    matriz.quitar_valor_de_lista(_NIVEL, "Informe de proyecto")
    return matriz.quitar_columna("Dimensión 8").a_bytes()


def _cb41() -> bytes:
    """El N.º 3 con el número 1 escrito como texto en la dimensión 3."""
    return _base().fijar_celda(2, "Dimensión 3", "1").a_bytes()


# ---- Escenarios y criterios --------------------------------------------------------------------


def _esc_1_2() -> bytes:
    """Un solo estudio empírico, dos intervenciones distintas y dos dimensiones en 1."""
    documento = _documento(
        1,
        VALOR_EMPIRICO,
        2019,
        "Institucional",
        "Intervención A",
        "Intervención B",
        nivel=VALOR_IMPACTO,
        marcas=_marcas(1, 2),
    )
    return _base().quitar_filas().agregar_fila(documento).a_bytes()


def _esc_1_6() -> bytes:
    """Seis estudios con los textos de enfoque del escenario; el último con la celda vacía."""
    matriz = _base().quitar_filas()
    textos = (
        "No desarrolla el enfoque.",
        "Nota: el documento menciona el enfoque de forma general.",
        "Sí, aborda el enfoque de género.",
        "Parcial: solo en un componente.",
        "Si bien menciona el enfoque, no lo desarrolla.",
        None,
    )
    for numero, texto in enumerate(textos, start=1):
        matriz.agregar_fila(_empirico(numero, {_ENFOQUE: texto}))
    return matriz.a_bytes()


def _esc_1_8() -> bytes:
    """Hojas reordenadas y columnas de rol en otra posición; el bloque sigue entre sus dos
    delimitadores. Los conteos son los de `base_valida`."""
    matriz = _base()
    matriz.ordenar_hojas("Guía por tipo de documento", HOJA_EGM, HOJA_MATRIZ)
    matriz.mover_columna(_NIVEL, posicion=1)
    matriz.mover_columna(_ANIO, despues_de="Aporte al proyecto")
    matriz.mover_columna(_TIPO, despues_de="Limitaciones")
    matriz.mover_columna(_ENFOQUE, antes_de="Referencia APA")
    return matriz.a_bytes()


def _esc_2_1() -> bytes:
    """El N.º 3 con una intervención que no está en la lista."""
    return _base().fijar_celda(2, _PRINCIPAL, "Intervención Z").a_bytes()


def _esc_2_5() -> bytes:
    """Sin el encabezado «Indicadores o categorías analíticas»."""
    return _base().quitar_columna(ENCABEZADO_DELIMITADOR_FINAL).a_bytes()


def _esc_2_13() -> bytes:
    """El N.º 4 con «s. f.» en la columna de año."""
    return _base().fijar_celda(3, _ANIO, "s. f.").a_bytes()


def _esc_2_15() -> bytes:
    """Sin lista de tipo y cuatro documentos: empírico del mapa, «Marco teórico», «Estudio
    empirico» sin tilde y tipo vacío."""
    matriz = _base().sin_lista(_TIPO).quitar_filas()
    sin_intervencion = {_PRINCIPAL: VALOR_NO_APLICA_INTERVENCION, **_marcas()}
    matriz.agregar_fila(_empirico(1, {_PRINCIPAL: "Intervención A", **_marcas(1)}))
    matriz.agregar_fila(_no_empirico(2, {_TIPO: "Marco teórico"}))
    matriz.agregar_fila(_empirico(3, {_TIPO: "Estudio empirico", **sin_intervencion}))
    matriz.agregar_fila(_no_empirico(4, {_TIPO: None}))
    return matriz.a_bytes()


def _esc_2_16() -> bytes:
    """El N.º 3 con un tipo de documento que no está en la lista."""
    return _base().fijar_celda(2, _TIPO, "Tipo fuera de lista").a_bytes()


def _esc_3_1() -> bytes:
    """Hoja con todas las categorías, valores guardados correctos y ningún G = H."""
    return _base().a_bytes()


def _esc_3_2() -> bytes:
    """Un estudio con la misma intervención en ambas columnas; la hoja lo cuenta dos veces."""
    return _cb07()


def _esc_3_5() -> bytes:
    """Filas vacías adicionales antes de cada tabla de la hoja `EGM`."""
    matriz = _base()
    for indice, tabla in enumerate(matriz.egm.tablas):
        tabla.fila += 2 + 2 * indice
    return matriz.a_bytes()


def _esc_3_7() -> bytes:
    """Títulos numerados 1, 2 y 4 en las tablas comparables y una tabla 3 con valores (7)."""
    matriz = _base()
    tabla = matriz.egm.tabla(3)
    for fila in tabla.filas:
        for encabezado in tabla.encabezados:
            tabla.fijar_valor(fila.nombre, encabezado, 7)
    return matriz.a_bytes()


def _esc_3_9() -> bytes:
    """Nombres de fila repetidos entre las tablas 1, 2 y 4: dos intervenciones llevan el nombre de
    dos niveles. Valores guardados correctos y distintos en cada tabla."""
    matriz = _base()
    _renombrar_intervencion(matriz, "Intervención B", "Estudio de caso")
    _renombrar_intervencion(matriz, "Intervención C", "Informe de proyecto")
    matriz.agregar_fila(
        _empirico(6, {_PRINCIPAL: "Estudio de caso", _NIVEL: "Estudio de caso", **_marcas(1)})
    )
    matriz.agregar_fila(
        _empirico(
            7, {_PRINCIPAL: "Estudio de caso", _NIVEL: "Informe de proyecto", **_marcas(1, 3)}
        )
    )
    return _regenerar_egm(matriz).a_bytes()


def _mover_total(tabla: TablaEgm, posicion: int) -> None:
    """Pone la columna «Total estudios» en `posicion` (0 = primera columna de valores)."""
    indice = tabla.encabezados.index(ENCABEZADO_TOTAL)
    tabla.encabezados.insert(posicion, tabla.encabezados.pop(indice))
    for fila in tabla.filas:
        fila.celdas.insert(posicion, fila.celdas.pop(indice))


def _esc_3_10() -> bytes:
    """«Total estudios» entre las dimensiones 4 y 5, y un estudio sin dimensiones."""
    matriz = _base().agregar_fila(_empirico(6, _marcas()))
    for numero in (1, 2):
        _mover_total(matriz.egm.tabla(numero), 4)
    return matriz.a_bytes()


def _esc_3_17() -> bytes:
    """El N.º 2 con un espacio al final de su intervención principal; la hoja no lo cuenta."""
    return _base().fijar_celda(1, _PRINCIPAL, "Intervención A ").a_bytes()


def _validacion_x14() -> bytes:
    """La lista de metodología guardada como extensión `x14`; tipo de fuente escrita y tipo de
    documento por rango."""
    return _base().con_lista(_METODOLOGIA, _METODOLOGIAS, modo="x14").a_bytes()


# ---- SC-000-06, SC-000-12, SC-000-17 y SC-000-18 -----------------------------------------------


def _sc000_06_agregadas() -> bytes:
    """Una intervención, una dimensión y un nivel agregados, con un estudio que los usa."""
    matriz = _base()
    _agregar_intervencion(matriz, "Intervención G")
    matriz.agregar_valor_a_lista(_NIVEL, "Estudio cuasiexperimental", posicion=4)
    matriz.agregar_columna(
        "Dimensión 9",
        rol="dimension",
        antes_de=ENCABEZADO_DELIMITADOR_FINAL,
        lista=["1", "0"],
    )
    cambios = {
        _PRINCIPAL: "Intervención G",
        _NIVEL: "Estudio cuasiexperimental",
        "Dimensión 9": 1,
    }
    matriz.agregar_fila(_empirico(6, cambios))
    return _regenerar_egm(matriz).a_bytes()


def _sc000_06_retiradas() -> bytes:
    """Una intervención, una dimensión y un nivel retirados, sin filas que los sigan usando."""
    matriz = _base()
    _quitar_intervencion(matriz, "Intervención F")
    matriz.quitar_valor_de_lista(_NIVEL, "Informe de proyecto")
    matriz.reemplazar_valor(_NIVEL, "Informe de proyecto", "Estudio de caso")
    matriz.quitar_columna("Dimensión 8")
    return _regenerar_egm(matriz).a_bytes()


def _sc000_06_renombradas() -> bytes:
    """Una intervención y un nivel renombrados (ninguno es valor ancla)."""
    matriz = _base()
    _renombrar_intervencion(matriz, "Intervención A", "Intervención Alfa")
    matriz.renombrar_valor_de_lista(_NIVEL, "Estudio de caso", "Estudio monográfico")
    matriz.reemplazar_valor(_NIVEL, "Estudio de caso", "Estudio monográfico")
    return _regenerar_egm(matriz).a_bytes()


def _sc000_12() -> bytes:
    """Otro número de documentos (11) que `base_valida`; el nombre con «v4» lo pone la prueba."""
    return _con_documentos_hasta(_base(), 11).a_bytes()


MARCADORES_CELDAS = (
    "MARCA-REFERENCIA-3F7A",
    "MARCA-PAIS-91BC",
    "MARCA-HALLAZGO-5D2E",
    "MARCA-VACIO-C48F",
    "MARCA-LIMITACION-07AE",
    "MARCA-APORTE-B6D3",
)
"""SC-000-17: textos únicos que `marcadores.xlsx` trae, uno en cada una de seis celdas."""
NOMBRE_CON_MARCADOR = "MARCA-NOMBRE-E91D.xlsx"
"""SC-000-17: nombre de archivo con marcador único, para cargar `marcadores.xlsx` con él."""


def _marcadores() -> bytes:
    """Base válida con un marcador único en seis celdas de texto (ninguna cambia las categorías)."""
    matriz = _base()
    matriz.fijar_celda(1, "Referencia APA", f"Autor 2 (2019). {MARCADORES_CELDAS[0]}.")
    matriz.fijar_celda(1, "País y población", MARCADORES_CELDAS[1])
    matriz.fijar_celda(2, "Principales hallazgos / tesis central", MARCADORES_CELDAS[2])
    matriz.fijar_celda(1, "Vacío de conocimiento identificado", MARCADORES_CELDAS[3])
    matriz.fijar_celda(2, "Limitaciones", MARCADORES_CELDAS[4])
    matriz.fijar_celda(3, "Aporte al proyecto", MARCADORES_CELDAS[5])
    return matriz.a_bytes()


def _sesion_a() -> bytes:
    """5 documentos y la intervención A llamada «Intervención Norte»."""
    matriz = _base()
    _renombrar_intervencion(matriz, "Intervención A", "Intervención Norte")
    return _regenerar_egm(matriz).a_bytes()


def _sesion_b() -> bytes:
    """8 documentos y la intervención A llamada «Intervención Sur»."""
    matriz = _con_documentos_hasta(_base(), 8)
    _renombrar_intervencion(matriz, "Intervención A", "Intervención Sur")
    return _regenerar_egm(matriz).a_bytes()


# ---- FX-A: réplica sintética de la instancia de ejemplo (apéndice A del contrato) --------------

TEXTOS_N7: dict[str, str] = {
    "País y población": "País sintético A; hogares rurales sintéticos de una región ficticia.",
    ENCABEZADO_DELIMITADOR_INICIAL: (
        "Ingresos del hogar, acceso a asesoría técnica y capacidades productivas, "
        "evaluados a los doce meses."
    ),
    ENCABEZADO_DELIMITADOR_FINAL: (
        "Ingreso mensual del hogar; número de activos productivos; asistencia a visitas técnicas."
    ),
    "Principales hallazgos / tesis central": (
        "Los hogares con transferencia y acompañamiento aumentaron sus activos productivos "
        "frente al grupo de comparación."
    ),
    "Vacío de conocimiento identificado": (
        "No se midió la permanencia de los efectos después de los doce meses."
    ),
    "Limitaciones": "Muestra pequeña y una sola región; sin seguimiento posterior.",
    "Aporte al proyecto": (
        "Ofrece un ejemplo de diseño de evaluación con grupo de comparación para el marco "
        "del proyecto."
    ),
}

_DIMENSIONES_FXA = (
    "Vulnerabilidad",
    "Humano",
    "Social",
    "Natural",
    "Físico",
    "Financiero",
    "Estructuras y procesos",
    "Sostenibilidad",
)
_INTERVENCIONES_FXA = (
    "Transferencia de activos",
    "Acompañamiento técnico",
    *(f"Intervención sintética {n}" for n in range(1, 5)),
)
_METODOLOGIAS_FXA = (
    "Conceptual/teórica",
    "Evaluación de impacto",
    *(f"Metodología sintética {n}" for n in range(1, 6)),
)
_NIVELES_FXA = (
    VALOR_IMPACTO,
    "Estudio de caso",
    "Informe de proyecto",
    "Informe descriptivo/opinión",
    VALOR_NO_APLICA_NIVEL,
)
_METODOLOGICO = "Documento metodológico"
_TIPOS_FXA = (
    VALOR_EMPIRICO,
    _METODOLOGICO,
    "Documento teórico",
    "Documento normativo",
    "Documento crítico-contextual",
    "Estudio comparativo internacional",
)
# Tipo de documento de cada N.º (1 a 27): 9 metodológicos, 7 empíricos, 4 teóricos, 3 normativos,
# 3 crítico-contextuales y 1 comparativo internacional.
_TIPO_FXA: dict[int, str] = {
    **dict.fromkeys((1, 2, 3, 4, 5, 6, 8, 9, 12), _TIPOS_FXA[1]),
    **dict.fromkeys((7, 10, 11, 13, 15, 16, 24), _TIPOS_FXA[0]),
    **dict.fromkeys((14, 17, 18, 19), _TIPOS_FXA[2]),
    **dict.fromkeys((20, 21, 22), _TIPOS_FXA[3]),
    **dict.fromkeys((23, 25, 26), _TIPOS_FXA[4]),
    27: _TIPOS_FXA[5],
}
_ANIOS_FXA = (
    1992, 1994, 1996, 1998, 2000, 2002, 2019, 2004, 2006, 2008, 2010, 2012, 2013, 2014,
    2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024, 2025, 2025, 2026, 2026,
)  # fmt: skip


def _documento_fxa(numero: int) -> dict[str, Any]:
    anio = _ANIOS_FXA[numero - 1]
    documento: dict[str, Any] = {
        "N°": numero,
        "Referencia APA": f"Autor {numero} ({anio}). Documento sintético {numero}.",
        _ANIO: anio,
        _TIPO: _TIPO_FXA[numero],
    }
    if numero <= 6:
        documento |= {
            _FUENTE: "Académica",
            _METODOLOGIA: "Conceptual/teórica",
            _ENFOQUE: (
                "Nota: el documento menciona el enfoque de forma general."
                if numero == 2
                else "No desarrolla el enfoque."
            ),
        }
    elif numero == 7:
        documento |= {
            _FUENTE: "Institucional",
            _METODOLOGIA: "Evaluación de impacto",
            _PRINCIPAL: "Transferencia de activos",
            _SECUNDARIA: "Acompañamiento técnico",
            _NIVEL: VALOR_IMPACTO,
            _ENFOQUE: "Si bien el estudio menciona a las mujeres, no desarrolla el enfoque.",
            **dict.fromkeys(_DIMENSIONES_FXA, 0),
            "Vulnerabilidad": 1,
            "Humano": 1,
            "Financiero": 1,
            **TEXTOS_N7,
        }
    elif numero in (10, 11):
        # Empíricos sin intervención: tienen dimensiones en 1 y siguen pendientes.
        documento |= {"Social": 1} if numero == 10 else {"Natural": 1, "Físico": 1}
    return documento


def instancia_ejemplo() -> MatrizSintetica:
    """FX-A, `instancia_ejemplo.xlsx`: réplica sintética de la instancia de ejemplo del apéndice A.

    27 documentos (filas 2 a 28; validaciones de las filas 2 a 36). Estudios empíricos
    ($E$): N.º 7, 10, 11, 13, 15, 16 y 24; en el mapa ($M$): solo el N.º 7, con Transferencia de
    activos como intervención principal, Acompañamiento técnico como secundaria, nivel de
    evaluación de impacto y las dimensiones Vulnerabilidad, Humano y Financiero en 1. Seis
    intervenciones por ocho dimensiones. Repartos: tipo de documento 9 metodológicos, 7
    empíricos, 4 teóricos, 3 normativos, 3 crítico-contextuales y 1 comparativo internacional;
    tipo de fuente 6 Académica, 1 Institucional y 20 vacíos; metodología 6 Conceptual/teórica,
    1 Evaluación de impacto y 20 vacías; enfoque 5 «No», 2 sin prefijo válido (N.º 2 y 7) y 20
    vacíos; años de 1992 a 2026. La hoja `EGM` trae fórmulas y ningún valor guardado.

    Los siete textos del N.º 7 son sintéticos, escritos a mano:

    - País y población: País sintético A; hogares rurales sintéticos de una región ficticia.
    - Dimensiones evaluadas / propuestas: Ingresos del hogar, acceso a asesoría técnica y
      capacidades productivas, evaluados a los doce meses.
    - Indicadores o categorías analíticas: Ingreso mensual del hogar; número de activos
      productivos; asistencia a visitas técnicas.
    - Principales hallazgos / tesis central: Los hogares con transferencia y acompañamiento
      aumentaron sus activos productivos frente al grupo de comparación.
    - Vacío de conocimiento identificado: No se midió la permanencia de los efectos después de
      los doce meses.
    - Limitaciones: Muestra pequeña y una sola región; sin seguimiento posterior.
    - Aporte al proyecto: Ofrece un ejemplo de diseño de evaluación con grupo de comparación
      para el marco del proyecto.

    El enfoque del N.º 7 es «Si bien el estudio menciona a las mujeres, no desarrolla el
    enfoque.» (sin prefijo válido).
    """
    matriz = _base().quitar_filas()
    for viejo, nuevo in zip(_DIMENSIONES, _DIMENSIONES_FXA, strict=True):
        matriz.renombrar_encabezado(viejo, nuevo)
    matriz.con_lista(_TIPO, _TIPOS_FXA, modo="rango")
    matriz.con_lista(_PRINCIPAL, _INTERVENCIONES_FXA + (VALOR_NO_APLICA_INTERVENCION,))
    matriz.con_lista(_SECUNDARIA, _INTERVENCIONES_FXA + (VALOR_NO_APLICA_INTERVENCION,))
    matriz.con_lista(_METODOLOGIA, _METODOLOGIAS_FXA)
    matriz.con_lista(_NIVEL, _NIVELES_FXA, modo="rango")
    for numero in range(1, 28):
        matriz.agregar_fila(_documento_fxa(numero))
    return _regenerar_egm(matriz, valores_guardados=False)


# ---- Estrategias de hypothesis: matrices válidas al azar (T-001-08) ----------------------------
#
# `matrices_validas()` genera `MatrizSintetica` que cumplen el contrato de datos: todos los roles,
# listas con sus anclas (un valor «Estudio empírico…», «Evaluación de impacto» y un «No aplica…»),
# bloque de dimensiones entre sus delimitadores con listas `1,0`, valores dentro de sus listas y,
# si se pide, la hoja `EGM` con fórmulas y valores guardados que coinciden con ellas. Todo lo que
# generan son casos que la herramienta debe leer sin error ni advertencia de contenido; los casos
# borde (valores fuera de lista, encabezados cambiados, hojas que faltan…) siguen en el catálogo.
# Los libros se obtienen con `.a_bytes()`; para cada ejemplo, `.documentos()` da lo escrito.

_COLUMNAS_CON_LISTA = (_TIPO, _FUENTE, _PRINCIPAL, _SECUNDARIA, _METODOLOGIA, _NIVEL)
_ROLES_ANTES_DEL_BLOQUE = (
    ("N°", "identificador"),
    ("Referencia APA", "referencia"),
    (_ANIO, "anio"),
    (_TIPO, "tipo_documento"),
    ("País y población", "pais_poblacion"),
    (_FUENTE, "tipo_fuente"),
    (_PRINCIPAL, "intervencion_principal"),
    (_SECUNDARIA, "intervencion_secundaria"),
    (_METODOLOGIA, "metodologia"),
    (_NIVEL, "nivel_evidencia"),
)
_ROLES_DESPUES_DEL_BLOQUE = (
    (_ENFOQUE, "enfoque"),
    ("Principales hallazgos / tesis central", "hallazgos"),
    ("Vacío de conocimiento identificado", "vacio"),
    ("Limitaciones", "limitaciones"),
    ("Aporte al proyecto", "aporte"),
)
_TEXTOS_LIBRES = (
    "País y población",
    ENCABEZADO_DELIMITADOR_INICIAL,
    ENCABEZADO_DELIMITADOR_FINAL,
    "Principales hallazgos / tesis central",
    "Vacío de conocimiento identificado",
    "Limitaciones",
    "Aporte al proyecto",
)
_TIPOS_DE_APOYO = (
    "Documento teórico",
    "Documento metodológico",
    "Documento normativo",
    "Documento crítico-contextual",
    "Estudio comparativo internacional",
    "Informe técnico",
)
_FUENTES_DE_APOYO = ("Académica", "Institucional", "Territorial", "Comunitaria", "Gubernamental")
_ENFOQUES_AL_AZAR = (
    "Sí. Incluye el enfoque.",
    "Sí, aborda el enfoque de género.",
    "No. No lo desarrolla.",
    "No desarrolla el enfoque.",
    "Parcial. Solo en un componente.",
)
_MAX_DOCUMENTOS_DETALLADOS = 12
"""Documentos que hypothesis arma uno por uno; los demás se derivan de ellos con una semilla."""


@dataclass(frozen=True)
class Categorias:
    """Categorías sintéticas de una matriz al azar, tal como irán escritas en sus listas.

    `lista_*` conservan el orden y los valores «No aplica…» de la lista de validación;
    `modos` dice cómo se guarda la lista de cada columna.
    """

    lista_intervenciones: tuple[str, ...]
    lista_niveles: tuple[str, ...]
    lista_tipos: tuple[str, ...]
    lista_fuentes: tuple[str, ...]
    lista_metodologias: tuple[str, ...]
    dimensiones: tuple[str, ...]
    ancla_empirico: str
    modos: Mapping[str, ModoLista]

    @property
    def intervenciones(self) -> tuple[str, ...]:
        """Las intervenciones sin el valor «No aplica…», en el orden de la lista."""
        return tuple(v for v in self.lista_intervenciones if not v.startswith("No aplica"))

    @property
    def niveles(self) -> tuple[str, ...]:
        """Los niveles sin el valor «No aplica…», en el orden de la lista."""
        return tuple(v for v in self.lista_niveles if not v.startswith("No aplica"))

    @property
    def no_aplica_intervencion(self) -> str:
        return next(v for v in self.lista_intervenciones if v.startswith("No aplica"))

    @property
    def no_aplica_nivel(self) -> str:
        return next(v for v in self.lista_niveles if v.startswith("No aplica"))

    @property
    def tipos_no_empiricos(self) -> tuple[str, ...]:
        return tuple(v for v in self.lista_tipos if not v.startswith("Estudio empírico"))


def _modo_posible(valores: Sequence[str], modo: ModoLista) -> ModoLista:
    """Una lista escrita no admite comas ni pasar de 255 caracteres: en ese caso, por rango."""
    if modo == "escrita" and (any("," in v for v in valores) or len(",".join(valores)) > 255):
        return "rango"
    return modo


def _nombres(plantillas: Sequence[str], maximo: int, minimo: int = 1) -> st.SearchStrategy[Any]:
    """Nombres distintos con una de las plantillas (`{n}` se reemplaza por números únicos)."""
    return st.builds(
        lambda plantilla, numeros: tuple(plantilla.format(n=n) for n in numeros),
        st.sampled_from(plantillas),
        st.lists(st.integers(1, 40), min_size=minimo, max_size=maximo, unique=True),
    )


@st.composite
def categorias(draw: st.DrawFn) -> Categorias:
    """Categorías sintéticas válidas: 1 a 10 intervenciones y dimensiones, niveles agregados o
    con otros nombres, tipos y listas de apoyo, con el valor ancla de cada regla del contrato."""
    intervenciones = draw(
        _nombres(
            (
                "Intervención sintética {n}",
                "Estrategia ficticia {n}",
                "Programa ficticio {n}, componente {n}",
            ),
            10,
        )
    )
    no_aplica_i = draw(st.sampled_from((VALOR_NO_APLICA_INTERVENCION, "No aplica")))
    dimensiones = draw(
        _nombres(("Dimensión sintética {n}", "Eje ficticio {n}", "Capital ficticio {n}"), 10)
    )
    otros_niveles = draw(_nombres(("Nivel sintético {n}", "Diseño ficticio {n}"), 4, 0))
    no_aplica_n = draw(st.sampled_from((VALOR_NO_APLICA_NIVEL, "No aplica")))
    ancla = draw(
        st.sampled_from(
            (VALOR_EMPIRICO, "Estudio empírico (modalidad ampliada)", "Estudio empírico")
        )
    )
    tipos_de_apoyo = draw(
        st.lists(st.sampled_from(_TIPOS_DE_APOYO), min_size=1, max_size=4, unique=True)
    )
    fuentes = draw(
        st.lists(st.sampled_from(_FUENTES_DE_APOYO), min_size=1, max_size=5, unique=True)
    )
    metodologias = draw(_nombres(("Metodología sintética {n}",), 6))

    lista_i = draw(st.permutations([*intervenciones, no_aplica_i]))
    lista_n = draw(st.permutations([VALOR_IMPACTO, *otros_niveles, no_aplica_n]))
    lista_t = draw(st.permutations([ancla, *tipos_de_apoyo]))
    listas = {
        _TIPO: lista_t,
        _FUENTE: fuentes,
        _PRINCIPAL: lista_i,
        _SECUNDARIA: lista_i,
        _METODOLOGIA: list(metodologias),
        _NIVEL: lista_n,
    }
    pedidos = {
        columna: draw(st.sampled_from(("escrita", "escrita", "rango", "x14")))
        for columna in _COLUMNAS_CON_LISTA
    }
    modos: dict[str, ModoLista] = {
        columna: _modo_posible(listas[columna], pedidos[columna])  # type: ignore[arg-type]
        for columna in _COLUMNAS_CON_LISTA
    }
    return Categorias(
        lista_intervenciones=tuple(lista_i),
        lista_niveles=tuple(lista_n),
        lista_tipos=tuple(lista_t),
        lista_fuentes=tuple(fuentes),
        lista_metodologias=tuple(metodologias),
        dimensiones=tuple(dimensiones),
        ancla_empirico=ancla,
        modos=modos,
    )


def _texto_libre() -> st.SearchStrategy[str | None]:
    """Celda de texto libre: vacía, con texto (también con acentos o con espacios alrededor) o
    solo con espacios."""
    return st.one_of(
        st.none(),
        st.integers(1, 999).map(lambda n: f"Texto sintético {n}."),
        st.integers(1, 999).map(lambda n: f"Texto sintético {n}."),
        st.integers(1, 999).map(lambda n: f"  Texto sintético {n}. "),
        st.sampled_from(("Texto con acentos y ñ: año, reunión; ¿qué?", " ", "   ")),
    )


def _opcional(opciones: Sequence[str]) -> st.SearchStrategy[str | None]:
    """Un valor de la lista o una celda vacía (el valor, más probable)."""
    return st.one_of(st.sampled_from(opciones), st.sampled_from(opciones), st.none())


@st.composite
def documentos(
    draw: st.DrawFn,
    cat: Categorias,
    numero: int,
    *,
    empirico: bool | None = None,
    g_igual_h: bool | None = None,
) -> dict[str, Any]:
    """Un documento sintético válido (encabezado → valor) con las categorías de `cat`.

    `empirico`: `True` o `False` fijan el tipo; `None` lo deja al azar (dos de cada tres, empírico).
    `g_igual_h`: `True` repite la intervención principal como secundaria (y lo hace empírico);
    `False` nunca la repite; `None` lo deja al azar. Un documento no empírico lleva «No aplica…»
    o nada como intervención y como nivel; sus dimensiones, 0 o vacías. Un empírico trae
    dimensiones en 1, 0 o vacías (puede no tener ninguna en 1), nivel y secundaria opcionales.
    """
    es_empirico = draw(st.integers(0, 2)) > 0 if empirico is None else empirico
    es_empirico = es_empirico or g_igual_h is True
    anio = draw(st.one_of(*[st.integers(1980, 2026)] * 5, st.none()))
    documento: dict[str, Any] = {
        "N°": numero,
        "Referencia APA": f"Autor {numero}. Documento sintético {numero}.",
        _ANIO: anio,
        _FUENTE: draw(_opcional(cat.lista_fuentes)),
        _METODOLOGIA: draw(_opcional(cat.lista_metodologias)),
        _ENFOQUE: draw(
            st.one_of(
                st.sampled_from(_ENFOQUES_AL_AZAR), st.sampled_from(_ENFOQUES_AL_AZAR), st.none()
            )
        ),
    }
    for encabezado in _TEXTOS_LIBRES:
        documento[encabezado] = draw(_texto_libre())
    if es_empirico:
        principal = draw(st.sampled_from(cat.intervenciones))
        otras = [i for i in cat.intervenciones if i != principal]
        opciones = ["vacia", "vacia", "no_aplica"] + (["otra"] if otras else [])
        if g_igual_h is not False:
            opciones.append("igual")
        if g_igual_h is True:
            opciones = ["igual"]
        opcion = draw(st.sampled_from(opciones))
        secundaria = {
            "vacia": None,
            "no_aplica": cat.no_aplica_intervencion,
            "igual": principal,
            "otra": draw(st.sampled_from(otras)) if opcion == "otra" else None,
        }[opcion]
        documento |= {
            _TIPO: cat.ancla_empirico,
            _PRINCIPAL: principal,
            _SECUNDARIA: secundaria,
            _NIVEL: draw(_opcional(cat.niveles)),
        }
        posibles: tuple[int | None, ...] = (1, 0, None)
    else:
        documento |= {
            _TIPO: draw(st.sampled_from(cat.tipos_no_empiricos)),
            _PRINCIPAL: draw(st.sampled_from((None, cat.no_aplica_intervencion))),
            _SECUNDARIA: draw(st.sampled_from((None, cat.no_aplica_intervencion))),
            _NIVEL: draw(st.sampled_from((None, cat.no_aplica_nivel))),
        }
        posibles = (0, None)
    marcas = draw(
        st.lists(
            st.sampled_from(posibles),
            min_size=len(cat.dimensiones),
            max_size=len(cat.dimensiones),
        )
    )
    documento |= dict(zip(cat.dimensiones, marcas, strict=True))
    return {k: v for k, v in documento.items() if v is not None}


def _cantidades(minimo: int, maximo: int) -> st.SearchStrategy[int]:
    """Número de documentos: 0, 1, algunos (el tramo más probable) y centenares."""
    tramos = ((0, 0), (1, 1), (2, 25), (2, 25), (2, 25), (100, 300))
    candidatos = [
        st.integers(max(lo, minimo), min(hi, maximo))
        for lo, hi in tramos
        if max(lo, minimo) <= min(hi, maximo)
    ]
    return st.one_of(*candidatos) if candidatos else st.integers(minimo, maximo)


def _es_g_igual_h(documento: Mapping[str, Any]) -> bool:
    principal = documento.get(_PRINCIPAL)
    return (
        isinstance(principal, str)
        and not principal.startswith("No aplica")
        and principal == documento.get(_SECUNDARIA)
    )


@st.composite
def _armar_matriz(
    draw: st.DrawFn,
    con_egm: bool | None,
    valores_guardados: bool | None,
    misma_intervencion: bool | None,
    min_documentos: int,
    max_documentos: int,
) -> MatrizSintetica:
    cat = draw(categorias())
    cantidad = draw(
        _cantidades(max(min_documentos, 1 if misma_intervencion else 0), max_documentos)
    )

    # Documentos: hasta 25 armados uno por uno; los demás, copias de ellos con su propio N.º.
    inicio = draw(st.integers(1, 5))
    numeros = list(range(inicio, inicio + cantidad))
    if cantidad <= _MAX_DOCUMENTOS_DETALLADOS:
        numeros = draw(st.permutations(numeros))
    detallados = min(cantidad, _MAX_DOCUMENTOS_DETALLADOS)
    plantillas = [
        draw(documentos(cat, numeros[i], g_igual_h=False if misma_intervencion is False else None))
        for i in range(detallados)
    ]
    if misma_intervencion and not any(_es_g_igual_h(d) for d in plantillas):
        plantillas[0] = draw(documentos(cat, numeros[0], empirico=True, g_igual_h=True))
    filas = list(plantillas)
    if cantidad > detallados:
        azar = random.Random(draw(st.integers(0, 2**32 - 1)))
        for numero in numeros[detallados:]:
            fila = dict(azar.choice(plantillas))
            fila["N°"] = numero
            fila["Referencia APA"] = f"Autor {numero}. Documento sintético {numero}."
            filas.append(fila)
    posiciones = draw(st.lists(st.integers(0, cantidad), max_size=3))
    for posicion in sorted(posiciones, reverse=True):
        filas.insert(posicion, {})  # fila vacía entre documentos

    # Columnas: orden del contrato o al azar; el bloque siempre va entre sus delimitadores.
    bloque = [ENCABEZADO_DELIMITADOR_INICIAL, *cat.dimensiones, ENCABEZADO_DELIMITADOR_FINAL]
    rol_de = dict(_ROLES_ANTES_DEL_BLOQUE + _ROLES_DESPUES_DEL_BLOQUE)
    if draw(st.booleans()):
        orden = [*(e for e, _ in _ROLES_ANTES_DEL_BLOQUE), *bloque]
        orden += [e for e, _ in _ROLES_DESPUES_DEL_BLOQUE]
    else:
        libres = draw(st.permutations(list(rol_de)))
        corte = draw(st.integers(0, len(libres)))
        orden = [*libres[:corte], *bloque, *libres[corte:]]
    ajenas = [
        f"Columna ajena {n}" for n in draw(st.lists(st.integers(1, 3), max_size=2, unique=True))
    ]
    orden = [*ajenas, *orden] if draw(st.booleans()) else [*orden, *ajenas]
    listas = {
        _TIPO: cat.lista_tipos,
        _FUENTE: cat.lista_fuentes,
        _PRINCIPAL: cat.lista_intervenciones,
        _SECUNDARIA: cat.lista_intervenciones,
        _METODOLOGIA: cat.lista_metodologias,
        _NIVEL: cat.lista_niveles,
    }
    matriz = MatrizSintetica()
    for encabezado in orden:
        if encabezado in cat.dimensiones:
            matriz.agregar_columna(encabezado, rol="dimension", lista=("1", "0"))
        elif encabezado in listas:
            matriz.agregar_columna(
                encabezado,
                rol=rol_de[encabezado],
                lista=listas[encabezado],
                modo_lista=cat.modos[encabezado],
            )
        elif encabezado == ENCABEZADO_DELIMITADOR_INICIAL:
            matriz.agregar_columna(encabezado, rol="delimitador_inicial")
        elif encabezado == ENCABEZADO_DELIMITADOR_FINAL:
            matriz.agregar_columna(encabezado, rol="delimitador_final")
        else:
            matriz.agregar_columna(encabezado, rol=rol_de.get(encabezado))
    for fila in filas:
        matriz.agregar_fila(fila)

    # Hojas: auxiliares opcionales, hoja EGM opcional y orden de las hojas.
    if draw(st.integers(0, 3)) > 0:
        matriz.agregar_hoja(HOJA_INSTRUCCIONES, [["Instrucciones sintéticas de diligenciamiento."]])
    if draw(st.integers(0, 3)) > 0:
        matriz.agregar_hoja(HOJA_GUIA, [["Guía sintética por tipo de documento."]])
    if draw(st.booleans()) if con_egm is None else con_egm:
        guardar = draw(st.booleans()) if valores_guardados is None else valores_guardados
        matriz.con_egm(valores_guardados=guardar, fila_final_formulas=max(200, 1 + len(filas)))
    if draw(st.booleans()):
        matriz.ordenar_hojas(*draw(st.permutations(matriz.nombres_de_hojas())))
    return matriz


def matrices_validas(
    *,
    con_egm: bool | None = None,
    valores_guardados: bool | None = None,
    misma_intervencion: bool | None = None,
    min_documentos: int = 0,
    max_documentos: int = 300,
) -> st.SearchStrategy[MatrizSintetica]:
    """Estrategia de matrices válidas al azar (`MatrizSintetica`; el libro es `.a_bytes()`).

    - `con_egm`: `True` siempre con hoja `EGM`; `False` nunca; `None` al azar.
    - `valores_guardados`: con hoja `EGM`, `True` guarda los valores que da el contrato; `False`
      deja las fórmulas sin valor guardado; `None` al azar. Las fórmulas llegan hasta la última
      fila de datos (nunca hay documentos fuera del rango de la hoja).
    - `misma_intervencion`: `True` garantiza al menos un estudio empírico con la misma
      intervención como principal y secundaria; `False` ninguno; `None` al azar.
    - `min_documentos`, `max_documentos`: límites de documentos (sin contar filas vacías).

    Varía categorías (nombres, cantidad, agregadas o renombradas), número de documentos (0, 1,
    algunos y centenares), niveles y celdas vacías, textos con espacios, orden de columnas y de
    hojas, modo de las listas (escrita, por rango o `x14`) y filas vacías entre documentos.
    """
    if min_documentos < 0:
        raise ValueError("min_documentos no puede ser negativo")
    if min_documentos > max_documentos:
        raise ValueError("min_documentos no puede ser mayor que max_documentos")
    if misma_intervencion and max_documentos < 1:
        raise ValueError("misma_intervencion exige que max_documentos sea al menos 1")
    return _armar_matriz(
        con_egm, valores_guardados, misma_intervencion, min_documentos, max_documentos
    )


# ---- Registro del catálogo y comando -----------------------------------------------------------

CATALOGO: dict[str, Generador] = {
    "cb01_fila_solo_referencia.xlsx": _cb01,
    "cb02_empirico_sin_intervencion.xlsx": _cb02,
    "cb03_empirico_sin_dimensiones.xlsx": _cb03,
    "cb04_solo_secundaria.xlsx": _cb04,
    "cb05_sin_nivel.xlsx": _cb05,
    "cb06_no_empirico_tablero.xlsx": _cb06,
    "cb07_misma_intervencion.xlsx": _cb07,
    "cb08_no_empirico_con_intervencion.xlsx": _cb08,
    "cb09_dimension_fuera_de_rango.xlsx": _cb09,
    "cb10_fuera_de_lista.xlsx": _cb10,
    "cb11_enfoque_sin_prefijo.xlsx": _cb11,
    "cb12_250_documentos.xlsx": _cb12,
    "cb13_numero_vacio_o_repetido.xlsx": _cb13,
    "cb14_sin_nivel_de_evidencia.xlsx": _cb14,
    "cb15_sin_hoja_matriz.xlsx": _cb15,
    "cb16_otro_tipo.txt": archivo_de_texto,
    "cb16_extension_xlsx_otro_contenido.xlsx": archivo_extension_xlsx_otro_contenido,
    "cb16_danado.xlsx": _cb16_danado,
    "cb18_columna_observaciones.xlsx": _cb18,
    "cb19_columna_1_0_fuera.xlsx": _cb19,
    "cb20_sin_ancla_empirico.xlsx": _cb20,
    "cb21_sin_ancla_ie.xlsx": _cb21,
    "cb22_sin_no_aplica.xlsx": _cb22,
    "cb23_varios_empiricos.xlsx": _cb23,
    "cb24_nivel_sin_lista.xlsx": _sin_lista(_NIVEL),
    "cb24_principal_sin_lista.xlsx": _sin_lista(_PRINCIPAL),
    "cb24_secundaria_sin_lista.xlsx": _sin_lista(_SECUNDARIA),
    "cb25_fuente_sin_lista.xlsx": _sin_lista(_FUENTE),
    "cb25_metodologia_sin_lista.xlsx": _sin_lista(_METODOLOGIA),
    "cb26_tipo_sin_lista.xlsx": _cb26,
    "cb27_anio_no_numerico.xlsx": _cb27,
    "cb28_tipo_vacio_o_fuera.xlsx": _cb28,
    "cb29_sin_hoja_egm.xlsx": _cb29_sin_hoja,
    "cb29_titulo_cambiado.xlsx": _cb29_titulo,
    "cb30_sin_valores_guardados.xlsx": _cb30,
    "cb31_categoria_nueva.xlsx": _cb31,
    "cb32_categoria_solo_en_hoja.xlsx": _cb32,
    "cb33_parcial_sin_diferencia.xlsx": _cb33_sin_diferencia,
    "cb33_parcial_con_diferencia.xlsx": _cb33_con_diferencia,
    "cb34_sin_total.xlsx": _cb34_sin_total,
    "cb34_total_repetido.xlsx": _cb34_repetido,
    "cb35_nombre_repetido.xlsx": _cb35,
    "cb36_intervencion_nivel_agregados.xlsx": _cb36,
    "cb37_dimension_agregada.xlsx": _cb37,
    "cb38_bloque_invertido.xlsx": _cb38_invertido,
    "cb38_bloque_vacio.xlsx": _cb38_vacio,
    "cb39_rol_en_bloque.xlsx": _cb39,
    "cb40_retiradas.xlsx": _cb40,
    "cb41_texto_1.xlsx": _cb41,
    "base_valida.xlsx": lambda: _base().a_bytes(),
    "esc_1_2_cuatro_celdas.xlsx": _esc_1_2,
    "esc_1_6_enfoque.xlsx": _esc_1_6,
    "esc_1_8_orden_alterado.xlsx": _esc_1_8,
    "esc_2_1_fuera_de_lista_n3.xlsx": _esc_2_1,
    "esc_2_5_sin_delimitador_final.xlsx": _esc_2_5,
    "esc_2_13_anio_sf_n4.xlsx": _esc_2_13,
    "esc_2_15_tipo_sin_lista_cuatro_docs.xlsx": _esc_2_15,
    "esc_2_16_tipo_fuera_de_lista_n3.xlsx": _esc_2_16,
    "esc_3_1_coincide.xlsx": _esc_3_1,
    "esc_3_2_difiere_g_igual_h.xlsx": _esc_3_2,
    "esc_3_5_filas_vacias_antes.xlsx": _esc_3_5,
    "esc_3_7_titulos_1_2_4.xlsx": _esc_3_7,
    "esc_3_9_nombres_repetidos_entre_tablas.xlsx": _esc_3_9,
    "esc_3_10_total_entre_dimensiones.xlsx": _esc_3_10,
    "esc_3_17_espacios.xlsx": _esc_3_17,
    "validacion_x14.xlsx": _validacion_x14,
    "sc000_06_agregadas.xlsx": _sc000_06_agregadas,
    "sc000_06_retiradas.xlsx": _sc000_06_retiradas,
    "sc000_06_renombradas.xlsx": _sc000_06_renombradas,
    "sc000_12_otro_nombre_v4.xlsx": _sc000_12,
    "instancia_ejemplo.xlsx": lambda: instancia_ejemplo().a_bytes(),
    "marcadores.xlsx": _marcadores,
    "sesion_a.xlsx": _sesion_a,
    "sesion_b.xlsx": _sesion_b,
}
"""Fixtures con nombre: archivo → función que genera sus bytes. Los escribe `main`."""

EN_MEMORIA: dict[str, Generador] = {
    "cb16_tamano_exacto": lambda: _base().a_bytes_de_tamano(LIMITE_TAMANO),
    "cb16_tamano_mas_uno": lambda: _base().a_bytes_de_tamano(LIMITE_TAMANO + 1),
    "cb17_declarado_exacto": lambda: _base().a_bytes_con_descomprimido_declarado(
        LIMITE_DESCOMPRIMIDO
    ),
    "cb17_declarado_mas_uno": lambda: _base().a_bytes_con_descomprimido_declarado(
        LIMITE_DESCOMPRIMIDO + 1
    ),
    "parte_mayor_que_lo_declarado": parte_mayor_que_lo_declarado,
}
"""Fixtures que pesan cerca de los límites de NFR-000-19: solo en memoria, nunca se guardan."""


def generar_catalogo() -> dict[str, bytes]:
    """Los bytes de cada fixture con nombre, en memoria y sin escribir nada."""
    return {nombre: generar() for nombre, generar in CATALOGO.items()}


def carpeta_de_fixtures() -> Path:
    """`data/fixtures/` del repositorio."""
    return Path(__file__).resolve().parents[1] / "data" / "fixtures"


def escribir_catalogo(destino: Path) -> dict[str, int]:
    """Escribe el catálogo en `destino` y devuelve el tamaño en bytes de cada archivo."""
    destino.mkdir(parents=True, exist_ok=True)
    tamanos = {}
    for nombre, contenido in generar_catalogo().items():
        (destino / nombre).write_bytes(contenido)
        tamanos[nombre] = len(contenido)
    return tamanos


def main(argv: Sequence[str] | None = None) -> int:
    """`python -m tests.constructor`: escribe el catálogo en `data/fixtures/`."""
    analizador = argparse.ArgumentParser(
        prog="python -m tests.constructor",
        description="Escribe los fixtures sintéticos con nombre.",
    )
    analizador.add_argument(
        "--destino", type=Path, default=None, help="Carpeta de salida (por defecto, data/fixtures)."
    )
    argumentos = analizador.parse_args(argv)
    destino = argumentos.destino or carpeta_de_fixtures()
    tamanos = escribir_catalogo(destino)
    print(f"{len(tamanos)} archivos escritos en {destino} ({sum(tamanos.values())} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
