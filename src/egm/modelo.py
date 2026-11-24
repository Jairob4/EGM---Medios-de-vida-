"""M01 `egm.modelo`: tipos inmutables del dominio (arquitectura §6.1, M01).

Reglas del módulo (arquitectura §4.1, regla 2; las vigila P-001-10): solo biblioteca estándar, ningún
otro módulo de `egm`, sin estado global y sin entrada ni salida.

Garantía de trazabilidad (NFR-000-02, FR-001-11): un número del sistema es un `Conteo`, cuyo único dato
es la lista de filas que lo producen. El valor se calcula como la longitud de esa lista; no se puede
pasar ni asignar de otro modo.

`Esquema`, `Documento` y `Corpus` se declaran aquí con los campos de la arquitectura (M04 y M05). Los
tipos auxiliares que usan (`Rol`, `Lista`, `Anclas`, `AnioNoReconocido`, `DatosCrudos`) también viven
aquí para que M01 no dependa de otro módulo. T-001-23 y T-001-24 completan lo que falte.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from types import MappingProxyType
from typing import Final, Literal, Protocol

__all__ = [
    "SIN_NIVEL",
    "Advertencia",
    "Anclas",
    "AnioNoReconocido",
    "Conteo",
    "Corpus",
    "DatosCrudos",
    "Documento",
    "Enfoque",
    "ErrorContrato",
    "EstadoDocumento",
    "Esquema",
    "FalloContrato",
    "Identificacion",
    "Lista",
    "Nota",
    "Rechazo",
    "RefFila",
    "ResultadoLectura",
    "ResultadoVerificacion",
    "Rol",
]

SIN_NIVEL: Final = "Sin nivel"
"""Entrada «Sin nivel» (FR-002-12): nivel de un documento sin nivel de evidencia."""


def _congelar[K, V](mapeo: Mapping[K, V]) -> Mapping[K, V]:
    """Copia el mapeo en una vista de solo lectura, para que nadie lo altere desde afuera."""
    return MappingProxyType(dict(mapeo))


# --------------------------------------------------------------------------------------------
# Trazabilidad y conteo
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RefFila:
    """Identifica un documento para la trazabilidad."""

    numero: str | None
    """N.º tal como está en la matriz (`None` si la celda está vacía)."""
    fila: int
    """Número de fila del archivo."""


@dataclass(frozen=True, slots=True)
class Conteo:
    """Un número del sistema: la lista de filas que lo producen.

    Las filas van en el orden del archivo (fila de menor a mayor) y sin repetidos; de lo contrario,
    `ValueError`. El valor es la longitud de la lista y no hay otra forma de darlo.
    """

    filas: tuple[RefFila, ...]

    def __post_init__(self) -> None:
        # Copia a tupla: una lista de origen no puede alterar el conteo después.
        filas = tuple(self.filas)
        object.__setattr__(self, "filas", filas)
        for anterior, actual in zip(filas, filas[1:], strict=False):
            if actual.fila == anterior.fila:
                raise ValueError(f"fila repetida en el conteo: {actual.fila}")
            if actual.fila < anterior.fila:
                raise ValueError("las filas del conteo deben ir en el orden del archivo")

    @property
    def valor(self) -> int:
        """Longitud de `filas`."""
        return len(self.filas)


# --------------------------------------------------------------------------------------------
# Enumerados y valor fijo
# --------------------------------------------------------------------------------------------


class EstadoDocumento(Enum):
    """Estado de cada documento de $R$ (contrato §4, «Estado de cada documento»)."""

    EN_EL_MAPA = auto()
    EMPIRICO_PENDIENTE = auto()
    NO_EMPIRICO = auto()
    SIN_TIPO_VALIDO = auto()


class Enfoque(Enum):
    """Categoría del enfoque de género/diferencial (contrato §6)."""

    SI = auto()
    NO = auto()
    PARCIAL = auto()
    SIN_CLASIFICAR = auto()
    SIN_DILIGENCIAR = auto()


class Rol(Enum):
    """Rol de columna de la matriz (contrato §3). El encabezado de cada rol lo fija M04."""

    IDENTIFICADOR = auto()
    REFERENCIA = auto()
    ANIO = auto()
    TIPO_DOCUMENTO = auto()
    PAIS_POBLACION = auto()
    TIPO_FUENTE = auto()
    INTERVENCION_PRINCIPAL = auto()
    INTERVENCION_SECUNDARIA = auto()
    METODOLOGIA = auto()
    NIVEL_EVIDENCIA = auto()
    DELIMITADOR_INICIAL = auto()
    DELIMITADOR_FINAL = auto()
    ENFOQUE = auto()
    HALLAZGOS = auto()
    VACIO = auto()
    LIMITACIONES = auto()
    APORTE = auto()


# --------------------------------------------------------------------------------------------
# Advertencias, notas y errores de contrato
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Advertencia:
    """Advertencia de validación (nunca un `print`)."""

    codigo: str
    ambito: str
    ref: RefFila | None
    columna: str | None
    valor: str | None
    datos: Mapping[str, object] = field(hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "datos", _congelar(self.datos))


@dataclass(frozen=True, slots=True)
class Nota:
    """Nota informativa (no es una advertencia)."""

    codigo: str
    datos: Mapping[str, object] = field(hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "datos", _congelar(self.datos))


@dataclass(frozen=True, slots=True)
class ErrorContrato:
    """Error de contrato: código, lo esperado y lo encontrado (sin nombre de archivo ni datos)."""

    codigo: str
    esperado: tuple[str, ...]
    encontrado: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FalloContrato:
    """Resultado de una matriz que incumple el contrato."""

    errores: tuple[ErrorContrato, ...]


@dataclass(frozen=True, slots=True)
class Rechazo:
    """Resultado de un archivo rechazado antes de leerlo."""

    motivo: Literal["tipo", "tamano", "contenido"]


# --------------------------------------------------------------------------------------------
# Esquema, documentos y corpus (se completan con T-001-23 y T-001-24)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Lista:
    """Valores de una columna categórica y su origen (contrato §4.2)."""

    valores: tuple[str, ...]
    origen: Literal["validacion", "presentes"]


@dataclass(frozen=True, slots=True)
class Anclas:
    """Valores ancla (contrato §4.1): $v_{emp}$ (uno o varios) y $v_{IE}$ o `None`."""

    empiricos: tuple[str, ...]
    evaluacion_impacto: str | None


@dataclass(frozen=True, slots=True)
class Esquema:
    """Estructura descubierta de la matriz (M04). El orden de cada tupla es el del archivo."""

    columnas: Mapping[Rol, int] = field(hash=False)
    dimensiones: tuple[str, ...]
    intervenciones: tuple[str, ...]
    niveles: tuple[str, ...]
    tipos_documento: Lista
    tipos_fuente: Lista
    metodologias: Lista
    anclas: Anclas
    advertencias: tuple[Advertencia, ...]
    notas: tuple[Nota, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "columnas", _congelar(self.columnas))


@dataclass(frozen=True, slots=True)
class AnioNoReconocido:
    """Año que no es un número entero (contrato §4 regla 12). T-001-24 completa sus datos."""


@dataclass(frozen=True, slots=True)
class DatosCrudos:
    """Lo necesario para explicar diferencias con la hoja EGM. T-001-24 completa sus campos."""


@dataclass(frozen=True, slots=True)
class Documento:
    """Una fila no vacía de la matriz (M05)."""

    ref: RefFila
    anio: int | AnioNoReconocido | None
    tipo_documento: str | None
    tipo_fuente: str | None
    metodologia: str | None
    intervenciones: tuple[str, ...]
    dimensiones: tuple[str, ...]
    nivel: str
    """Texto del nivel de evidencia o `SIN_NIVEL`."""
    enfoque: Enfoque
    estado: EstadoDocumento
    textos: Mapping[Rol, str | None] = field(hash=False)
    crudos: DatosCrudos

    def __post_init__(self) -> None:
        object.__setattr__(self, "textos", _congelar(self.textos))


@dataclass(frozen=True, slots=True)
class Corpus:
    """Todas las filas no vacías, en el orden del archivo (M05)."""

    documentos: tuple[Documento, ...]
    advertencias: tuple[Advertencia, ...]
    fila_final_leida: int


# --------------------------------------------------------------------------------------------
# Resultado de la lectura
# --------------------------------------------------------------------------------------------


class ResultadoVerificacion(Protocol):
    """Forma mínima de la `Verificacion` de M08, que M01 no puede importar (arquitectura §4.1)."""

    @property
    def verificadas(self) -> tuple[int, ...]:
        """Números de título de las tablas en «coincide» o «difiere»."""
        ...

    @property
    def advertencias(self) -> tuple[Advertencia, ...]:
        """Advertencias de la verificación."""
        ...


@dataclass(frozen=True, slots=True)
class Identificacion:
    """Nombre del archivo tal como llegó y fecha de lectura dada (NFR-000-09)."""

    nombre_archivo: str
    fecha_lectura: datetime


@dataclass(frozen=True, slots=True)
class ResultadoLectura:
    """Todo lo que produce una lectura válida de la matriz."""

    identificacion: Identificacion
    esquema: Esquema
    corpus: Corpus
    advertencias: tuple[Advertencia, ...]
    notas: tuple[Nota, ...]
    verificacion: ResultadoVerificacion
