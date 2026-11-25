"""M01 `egm.modelo`: tipos inmutables del dominio (arquitectura §6.1, M01).

Reglas del módulo (arquitectura §4.1, regla 2; las vigila P-001-10): solo biblioteca estándar,
ningún otro módulo de `egm`, sin estado global y sin entrada ni salida.

Garantía de trazabilidad (NFR-000-02, FR-001-11): un número del sistema es un `Conteo`, cuyo único
dato es la lista de filas que lo producen. El valor se calcula como la longitud de esa lista; no se
puede pasar ni asignar de otro modo.

`Esquema`, `Documento` y `Corpus` se declaran aquí con los campos de la arquitectura (M04 y M05).
Los tipos auxiliares que usan (`Rol`, `Lista`, `Anclas`, `AnioNoReconocido`, `DatosCrudos`)
también viven aquí para que M01 no dependa de otro módulo. T-001-23 y T-001-24 completan lo que
falte.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from types import MappingProxyType
from typing import Final, Literal, Protocol

__all__ = [
    "ANCLA_EMPIRICA_AUSENTE",
    "ANIO_NO_RECONOCIDO",
    "BLOQUE_SIN_DIMENSIONES",
    "CODIGOS_ADVERTENCIA_ESTRUCTURA",
    "CODIGOS_ADVERTENCIA_FILA",
    "CODIGOS_ERROR_CONTRATO",
    "CODIGOS_NOTA",
    "COLUMNAS_NO_USADAS",
    "COLUMNA_SIN_LISTA",
    "DIMENSION_SIN_LISTA_1_0",
    "DIMENSION_VALOR_INVALIDO",
    "ENCABEZADO_AUSENTE",
    "ENFOQUE_SIN_CLASIFICAR",
    "ESPACIOS_EN_LOS_EXTREMOS",
    "HOJA_AUSENTE",
    "LISTA_1_0_FUERA_DEL_BLOQUE",
    "LISTA_OBLIGATORIA_AUSENTE",
    "LISTA_SIN_NO_APLICA",
    "NO_EMPIRICO_CON_INTERVENCION",
    "NUMERO_REPETIDO",
    "NUMERO_VACIO",
    "PRINCIPAL_IGUAL_SECUNDARIA",
    "ROL_DENTRO_DEL_BLOQUE",
    "SIN_ANCLA_EVALUACION_IMPACTO",
    "SIN_NIVEL",
    "TIPO_DOCUMENTO_FUERA_DE_LISTA",
    "VALOR_FUERA_DE_LISTA",
    "VARIOS_EMPIRICOS",
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

# Lista cerrada de códigos (historia 2, decisión del 25-nov-2026). Viven aquí para que M04, M05 y
# M10 los compartan. Cada código es el valor de su constante en minúsculas.

# Advertencias de fila (ámbito «fila»; las emite M05).
ENFOQUE_SIN_CLASIFICAR: Final = "enfoque_sin_clasificar"
VALOR_FUERA_DE_LISTA: Final = "valor_fuera_de_lista"
ESPACIOS_EN_LOS_EXTREMOS: Final = "espacios_en_los_extremos"
DIMENSION_VALOR_INVALIDO: Final = "dimension_valor_invalido"
ANIO_NO_RECONOCIDO: Final = "anio_no_reconocido"
NUMERO_VACIO: Final = "numero_vacio"
NUMERO_REPETIDO: Final = "numero_repetido"
PRINCIPAL_IGUAL_SECUNDARIA: Final = "principal_igual_secundaria"
NO_EMPIRICO_CON_INTERVENCION: Final = "no_empirico_con_intervencion"
TIPO_DOCUMENTO_FUERA_DE_LISTA: Final = "tipo_documento_fuera_de_lista"

# Advertencias de estructura (ámbitos «columna», «archivo» u «hoja»; las emite M04).
BLOQUE_SIN_DIMENSIONES: Final = "bloque_sin_dimensiones"
ROL_DENTRO_DEL_BLOQUE: Final = "rol_dentro_del_bloque"
LISTA_1_0_FUERA_DEL_BLOQUE: Final = "lista_1_0_fuera_del_bloque"
DIMENSION_SIN_LISTA_1_0: Final = "dimension_sin_lista_1_0"
LISTA_SIN_NO_APLICA: Final = "lista_sin_no_aplica"
VARIOS_EMPIRICOS: Final = "varios_empiricos"
SIN_ANCLA_EVALUACION_IMPACTO: Final = "sin_ancla_evaluacion_impacto"
COLUMNA_SIN_LISTA: Final = "columna_sin_lista"

# Nota (la emite M04).
COLUMNAS_NO_USADAS: Final = "columnas_no_usadas"

# Errores de contrato (lista cerrada; los emite M04).
HOJA_AUSENTE: Final = "hoja_ausente"
ENCABEZADO_AUSENTE: Final = "encabezado_ausente"
ANCLA_EMPIRICA_AUSENTE: Final = "ancla_empirica_ausente"
LISTA_OBLIGATORIA_AUSENTE: Final = "lista_obligatoria_ausente"

CODIGOS_ADVERTENCIA_FILA: Final = (
    ENFOQUE_SIN_CLASIFICAR,
    VALOR_FUERA_DE_LISTA,
    ESPACIOS_EN_LOS_EXTREMOS,
    DIMENSION_VALOR_INVALIDO,
    ANIO_NO_RECONOCIDO,
    NUMERO_VACIO,
    NUMERO_REPETIDO,
    PRINCIPAL_IGUAL_SECUNDARIA,
    NO_EMPIRICO_CON_INTERVENCION,
    TIPO_DOCUMENTO_FUERA_DE_LISTA,
)
"""Advertencias que emite M05, en el orden de la lista cerrada."""

CODIGOS_ADVERTENCIA_ESTRUCTURA: Final = (
    BLOQUE_SIN_DIMENSIONES,
    ROL_DENTRO_DEL_BLOQUE,
    LISTA_1_0_FUERA_DEL_BLOQUE,
    DIMENSION_SIN_LISTA_1_0,
    LISTA_SIN_NO_APLICA,
    VARIOS_EMPIRICOS,
    SIN_ANCLA_EVALUACION_IMPACTO,
    COLUMNA_SIN_LISTA,
)
"""Advertencias que emite M04 (ámbitos «columna», «archivo» u «hoja»)."""

CODIGOS_NOTA: Final = (COLUMNAS_NO_USADAS,)
"""Notas que emite M04."""

CODIGOS_ERROR_CONTRATO: Final = (
    HOJA_AUSENTE,
    ENCABEZADO_AUSENTE,
    ANCLA_EMPIRICA_AUSENTE,
    LISTA_OBLIGATORIA_AUSENTE,
)
"""Errores de contrato de la lista cerrada que emite M04."""


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
    """Año que no es un número entero (contrato §4 regla 12)."""

    texto: str
    """El valor de la celda como texto (incluido un año escrito como texto, sin cambios)."""


@dataclass(frozen=True, slots=True)
class DatosCrudos:
    """Lo necesario para explicar diferencias con la hoja EGM (contrato §7, punto 4).

    Sin particularidades, todos los campos van vacíos: `DatosCrudos()`.
    """

    dimensiones_como_texto: tuple[str, ...] = ()
    """Dimensiones cuya celda es el texto «1» (no marca la dimensión; contrato §4 regla 10)."""
    con_espacios: tuple[Rol, ...] = ()
    """Roles cuyo valor traía espacios en los extremos que hubo que quitar (regla 6), en el orden
    de la lectura: intervención principal, secundaria, tipo de documento, tipo de fuente,
    metodología y nivel de evidencia."""
    principal_igual_secundaria: bool = False
    """Las intervenciones principal y secundaria son la misma categoría ($G_r = H_r$)."""


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
