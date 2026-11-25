"""M04 `egm.esquema`: descubre la estructura de la matriz (arquitectura §6.1, M04).

Descubre la hoja de la matriz por nombre, los roles por el texto del encabezado (contrato §3), el
bloque de dimensiones entre sus delimitadores (§3.1), las listas de las columnas categóricas
(§4.2), los valores «No aplica» por prefijo fuera de las categorías (§4 regla 8), las anclas (§4.1)
y el orden del archivo (§4 regla 3). Las categorías y las dimensiones se leen del archivo; el módulo
solo escribe los encabezados de rol del contrato y los tres valores ancla.

Lo que incumple el contrato devuelve un `FalloContrato`, sin esquema parcial, con los errores de la
lista cerrada (`egm.modelo.CODIGOS_ERROR_CONTRATO`): `HOJA_AUSENTE` (sola, porque sin la hoja no hay
qué mirar), `ENCABEZADO_AUSENTE` (también para un delimitador del bloque),
`LISTA_OBLIGATORIA_AUSENTE` (intervenciones o nivel sin lista) y `ANCLA_EMPIRICA_AUSENTE`. Un error
trae lo esperado y lo encontrado como nombres de hojas, encabezados o valores de lista, nunca filas
de datos ni el nombre del archivo. Si hay varios, van todos, en ese orden y sin repetir.

Lo que el contrato trata como advertencia o nota no detiene la lectura: va en
`Esquema.advertencias` (sin `ref`, con ámbito «hoja» o «columna») o en `Esquema.notas`. Orden: el de
`CODIGOS_ADVERTENCIA_ESTRUCTURA` y, dentro de cada código, el de las columnas del archivo.

Reglas del núcleo (arquitectura §4.1): solo importa `egm.modelo` y `egm.libro`; sin entrada ni
salida.
"""

from collections.abc import Iterable, Mapping, Sequence
from typing import Final

from egm.libro import Hoja, Libro, ListaValidacion, Valor
from egm.modelo import (
    ANCLA_EMPIRICA_AUSENTE,
    BLOQUE_SIN_DIMENSIONES,
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
    Advertencia,
    Anclas,
    ErrorContrato,
    Esquema,
    FalloContrato,
    Lista,
    Nota,
    Rol,
)

__all__ = ["columnas_del_bloque", "descubrir"]

HOJA_MATRIZ: Final = "Matriz bibliográfica"

_ENCABEZADOS: Final[Mapping[Rol, str]] = {
    Rol.IDENTIFICADOR: "N°",
    Rol.REFERENCIA: "Referencia APA",
    Rol.ANIO: "Año",
    Rol.TIPO_DOCUMENTO: "Tipo de documento",
    Rol.PAIS_POBLACION: "País y población",
    Rol.TIPO_FUENTE: "Tipo de fuente",
    Rol.INTERVENCION_PRINCIPAL: "Tipo de intervención (EGM)",
    Rol.INTERVENCION_SECUNDARIA: "Intervención secundaria (opcional)",
    Rol.METODOLOGIA: "Metodología",
    Rol.NIVEL_EVIDENCIA: "Nivel de evidencia",
    Rol.DELIMITADOR_INICIAL: "Dimensiones evaluadas / propuestas",
    Rol.DELIMITADOR_FINAL: "Indicadores o categorías analíticas",
    Rol.ENFOQUE: "Enfoque de género/diferencial",
    Rol.HALLAZGOS: "Principales hallazgos / tesis central",
    Rol.VACIO: "Vacío de conocimiento identificado",
    Rol.LIMITACIONES: "Limitaciones",
    Rol.APORTE: "Aporte al proyecto",
}
"""Encabezado de cada rol (contrato §3): la única tabla de encabezados del núcleo."""

# Valores ancla del contrato §4.1.
_PREFIJO_EMPIRICO: Final = "Estudio empírico"
_VALOR_EVALUACION_IMPACTO: Final = "Evaluación de impacto"
_PREFIJO_NO_APLICA: Final = "No aplica"

# Marcas de una lista `1,0` (contrato §3.1): el 1 marca la dimensión y el 0 la deja sin evaluar.
_MARCAS_1_0: Final = frozenset({"1", "0"})

# Ámbitos de las advertencias de estructura.
_AMBITO_HOJA: Final = "hoja"
_AMBITO_COLUMNA: Final = "columna"

# Columnas cuya lista de validación es obligatoria (contrato §4.2); sin ella, error de contrato.
_ROLES_CON_LISTA_OBLIGATORIA: Final = (
    Rol.INTERVENCION_PRINCIPAL,
    Rol.INTERVENCION_SECUNDARIA,
    Rol.NIVEL_EVIDENCIA,
)
# Columnas con lista de categorías que traen un valor «No aplica…»: la secundaria es opcional y su
# lista no lo trae, así que no se le exige.
_ROLES_CON_NO_APLICA: Final = (Rol.INTERVENCION_PRINCIPAL, Rol.NIVEL_EVIDENCIA)
# Columnas categóricas sin lista de las que la lectura sigue con los valores presentes (§4.2).
_ROLES_SIN_LISTA_PERMITIDA: Final = (Rol.TIPO_DOCUMENTO, Rol.TIPO_FUENTE, Rol.METODOLOGIA)


def _error(codigo: str, esperado: Iterable[str], encontrado: Iterable[str]) -> ErrorContrato:
    return ErrorContrato(codigo, tuple(esperado), tuple(encontrado))


def _advertencia(
    codigo: str,
    ambito: str,
    columna: str | None = None,
    valor: str | None = None,
    **datos: object,
) -> Advertencia:
    """Advertencia de estructura: sin fila (`ref=None`)."""
    return Advertencia(codigo, ambito, None, columna, valor, datos)


def _texto(valor: Valor) -> str | None:
    """El contenido de una celda como texto sin espacios en los extremos; `None` si no hay."""
    if valor is None:
        return None
    texto = valor.strip() if isinstance(valor, str) else str(valor)
    return texto or None


def _sin_repetidos(valores: Iterable[str]) -> tuple[str, ...]:
    """Textos sin espacios en los extremos, sin vacíos y sin repetidos, en su orden."""
    vistos: dict[str, None] = {}
    for valor in valores:
        limpio = valor.strip()
        if limpio:
            vistos.setdefault(limpio)
    return tuple(vistos)


def _categorias(valores: Iterable[str]) -> tuple[str, ...]:
    """Los valores de una lista que son categorías: sin los que empiezan por «No aplica»."""
    return tuple(v for v in valores if not v.startswith(_PREFIJO_NO_APLICA))


def _roles(encabezados: list[str | None]) -> dict[Rol, int]:
    """Columna (desde 1) de cada rol cuyo encabezado está; si se repite, la primera."""
    por_encabezado = {texto: rol for rol, texto in _ENCABEZADOS.items()}
    columnas: dict[Rol, int] = {}
    for posicion, encabezado in enumerate(encabezados, start=1):
        rol = por_encabezado.get(encabezado) if encabezado is not None else None
        if rol is not None:
            columnas.setdefault(rol, posicion)
    return columnas


def columnas_del_bloque(
    encabezados: Sequence[str | None], columnas: Mapping[Rol, int]
) -> tuple[tuple[str, int], ...]:
    """Dimensiones del bloque como `(nombre, columna)`, en el orden del archivo (§3.1).

    Es la única regla del bloque de dimensiones: `descubrir` la usa para los nombres y
    `egm.lectura.leer` para saber en qué columna está cada dimensión.

    - `encabezados`: los de la fila 1, uno por columna desde la 1, sin espacios en los extremos y
      con `None` donde no hay encabezado.
    - `columnas`: la columna de cada rol (`Esquema.columnas`); debe traer los dos delimitadores.
    - Resultado: las columnas entre los dos delimitadores, ambos excluidos, con encabezado y que no
      lleven el encabezado de un rol; la columna cuenta desde 1. Con el delimitador final antes del
      inicial o pegado a él, no hay ninguna.
    """
    inicio = columnas[Rol.DELIMITADOR_INICIAL]
    fin = columnas[Rol.DELIMITADOR_FINAL]
    encabezados_de_rol = set(_ENCABEZADOS.values())
    return tuple(
        (encabezado, posicion)
        for posicion, encabezado in enumerate(encabezados, start=1)
        if inicio < posicion < fin
        and encabezado is not None
        and encabezado not in encabezados_de_rol
    )


def _valores_presentes(hoja: Hoja, columna: int, ultima_fila: int) -> tuple[str, ...]:
    """Valores distintos no vacíos de una columna (desde la fila 2), en su orden de aparición."""
    return _sin_repetidos(
        texto
        for fila in range(2, ultima_fila + 1)
        if (texto := _texto(hoja.celda(fila, columna).valor)) is not None
    )


def _lista_de_validacion(hoja: Hoja, columna: int) -> Lista | None:
    """La lista de validación de la columna, o `None` si no tiene."""
    validacion = hoja.validacion(columna)
    return None if validacion is None else Lista(_sin_repetidos(validacion.valores), "validacion")


def _lista_o_presentes(hoja: Hoja, columna: int, ultima_fila: int) -> Lista:
    """La lista de validación o, sin ella, los valores presentes de la columna (§4.2)."""
    return _lista_de_validacion(hoja, columna) or Lista(
        _valores_presentes(hoja, columna, ultima_fila), "presentes"
    )


def _es_lista_1_0(validacion: ListaValidacion | None) -> bool:
    """La validación es una lista `1,0`: sus valores son el 1 y el 0, en cualquier orden."""
    return validacion is not None and set(_sin_repetidos(validacion.valores)) == _MARCAS_1_0


def _empiricos(tipos_documento: Lista) -> tuple[str, ...]:
    """Valores de la lista de tipo de documento que empiezan por el ancla empírica (§4.1)."""
    return tuple(v for v in tipos_documento.valores if v.startswith(_PREFIJO_EMPIRICO))


def _errores_de_contrato(
    encabezados: Sequence[str | None],
    columnas: Mapping[Rol, int],
    obligatorias: Mapping[Rol, Lista | None],
    tipos_documento: Lista | None,
) -> tuple[ErrorContrato, ...]:
    """Errores de contrato de lo que no es la hoja, en el orden de la lista cerrada.

    - `ENCABEZADO_AUSENTE`: los encabezados de rol que faltan (también los dos delimitadores), en el
      orden de la tabla de roles; lo encontrado son los encabezados de la fila 1, sin repetir.
    - `LISTA_OBLIGATORIA_AUSENTE`: las columnas de intervención o de nivel, con encabezado, sin
      lista de validación; no se encuentra nada.
    - `ANCLA_EMPIRICA_AUSENTE`: el valor esperado y los valores de la lista de tipo de documento.

    Cada comprobación usa solo lo que está: sin el encabezado de nivel se siguen revisando las
    otras dos columnas y el ancla.
    """
    errores: list[ErrorContrato] = []
    faltan = tuple(texto for rol, texto in _ENCABEZADOS.items() if rol not in columnas)
    if faltan:
        errores.append(
            _error(ENCABEZADO_AUSENTE, faltan, _sin_repetidos(e for e in encabezados if e))
        )
    sin_lista = tuple(_ENCABEZADOS[rol] for rol, lista in obligatorias.items() if lista is None)
    if sin_lista:
        errores.append(_error(LISTA_OBLIGATORIA_AUSENTE, sin_lista, ()))
    if tipos_documento is not None and not _empiricos(tipos_documento):
        errores.append(
            _error(ANCLA_EMPIRICA_AUSENTE, (_PREFIJO_EMPIRICO,), tipos_documento.valores)
        )
    return tuple(errores)


def _bloque_sin_dimensiones(inicio: int, fin: int) -> Advertencia:
    """El bloque no tiene dimensiones; `datos["motivo"]` es «invertido» (el delimitador final
    antes del inicial) o «vacio» (ninguna columna de dimensión entre los dos)."""
    motivo = "invertido" if fin < inicio else "vacio"
    return _advertencia(BLOQUE_SIN_DIMENSIONES, _AMBITO_HOJA, motivo=motivo)


def _advertencias_del_bloque(
    hoja: Hoja, encabezados: Sequence[str | None], columnas: Mapping[Rol, int]
) -> tuple[list[Advertencia], Nota | None]:
    """Advertencias del bloque de dimensiones (§3.1) y nota de columnas no usadas (§3).

    Orden: bloque sin dimensiones; rol dentro del bloque; lista `1,0` fuera del bloque; dimensión
    sin lista `1,0`; dentro de cada código, el orden de las columnas. La nota nombra, en una sola,
    las columnas de otro encabezado fuera del bloque que no traen lista `1,0`.
    """
    inicio, fin = columnas[Rol.DELIMITADOR_INICIAL], columnas[Rol.DELIMITADOR_FINAL]
    encabezados_de_rol = set(_ENCABEZADOS.values())
    dimensiones = columnas_del_bloque(encabezados, columnas)

    sin_dimensiones = [] if dimensiones else [_bloque_sin_dimensiones(inicio, fin)]
    roles_dentro: list[Advertencia] = []
    con_lista_fuera: list[Advertencia] = []
    no_usadas: list[str] = []
    for posicion, encabezado in enumerate(encabezados, start=1):
        if encabezado is None:
            continue
        dentro = inicio < posicion < fin
        if encabezado in encabezados_de_rol:
            if dentro:
                roles_dentro.append(
                    _advertencia(ROL_DENTRO_DEL_BLOQUE, _AMBITO_COLUMNA, encabezado)
                )
        elif dentro:
            continue  # es una dimensión: se revisa más abajo
        elif _es_lista_1_0(hoja.validacion(posicion)):
            con_lista_fuera.append(
                _advertencia(LISTA_1_0_FUERA_DEL_BLOQUE, _AMBITO_COLUMNA, encabezado)
            )
        else:
            no_usadas.append(encabezado)
    sin_lista_1_0 = [
        _advertencia(DIMENSION_SIN_LISTA_1_0, _AMBITO_COLUMNA, nombre)
        for nombre, posicion in dimensiones
        if not _es_lista_1_0(hoja.validacion(posicion))
    ]
    nota = Nota(COLUMNAS_NO_USADAS, {"columnas": _sin_repetidos(no_usadas)}) if no_usadas else None
    return [*sin_dimensiones, *roles_dentro, *con_lista_fuera, *sin_lista_1_0], nota


def _advertencias_de_listas(
    columnas: Mapping[Rol, int], listas: Mapping[Rol, Lista], anclas: Anclas
) -> list[Advertencia]:
    """Advertencias de las listas de categorías y de las anclas (§4.1 y §4.2).

    - `LISTA_SIN_NO_APLICA`: la lista de intervención principal o de nivel sin ningún valor que
      empiece por «No aplica»; `valor` es ese prefijo.
    - `VARIOS_EMPIRICOS`: más de un valor de tipo de documento empieza por el ancla empírica;
      `datos["valores"]` los trae.
    - `SIN_ANCLA_EVALUACION_IMPACTO`: la lista de nivel no trae el valor de evaluación de impacto;
      `valor` es el valor esperado y `datos["niveles"]` los niveles de la lista.
    - `COLUMNA_SIN_LISTA`: tipo de documento, de fuente o metodología sin lista; `datos["valores"]`
      son los valores presentes.

    Orden: el de esos códigos y, dentro de cada uno, el de las columnas del archivo.
    """

    def por_columna(roles: Iterable[Rol]) -> list[Rol]:
        return sorted(roles, key=lambda rol: columnas[rol])

    sin_no_aplica = [
        _advertencia(LISTA_SIN_NO_APLICA, _AMBITO_COLUMNA, _ENCABEZADOS[rol], _PREFIJO_NO_APLICA)
        for rol in por_columna(_ROLES_CON_NO_APLICA)
        if not any(v.startswith(_PREFIJO_NO_APLICA) for v in listas[rol].valores)
    ]
    varios = (
        [
            _advertencia(
                VARIOS_EMPIRICOS,
                _AMBITO_COLUMNA,
                _ENCABEZADOS[Rol.TIPO_DOCUMENTO],
                valores=anclas.empiricos,
            )
        ]
        if len(anclas.empiricos) > 1
        else []
    )
    sin_impacto = (
        []
        if anclas.evaluacion_impacto is not None
        else [
            _advertencia(
                SIN_ANCLA_EVALUACION_IMPACTO,
                _AMBITO_COLUMNA,
                _ENCABEZADOS[Rol.NIVEL_EVIDENCIA],
                _VALOR_EVALUACION_IMPACTO,
                niveles=_categorias(listas[Rol.NIVEL_EVIDENCIA].valores),
            )
        ]
    )
    sin_lista = [
        _advertencia(
            COLUMNA_SIN_LISTA, _AMBITO_COLUMNA, _ENCABEZADOS[rol], valores=listas[rol].valores
        )
        for rol in por_columna(_ROLES_SIN_LISTA_PERMITIDA)
        if listas[rol].origen == "presentes"
    ]
    return [*sin_no_aplica, *varios, *sin_impacto, *sin_lista]


def descubrir(libro: Libro) -> Esquema | FalloContrato:
    """Descubre la estructura de la matriz o devuelve el `FalloContrato` de lo que no reconoce.

    - Roles: el texto del encabezado de la fila 1, sin espacios en los extremos, igual al de la
      tabla del contrato §3. Con un encabezado repetido vale la primera columna.
    - `Esquema.columnas` da la columna de cada rol, contada desde 1 como en `egm.libro`.
    - Dimensiones: las columnas entre los delimitadores, en el orden del archivo, con el texto de
      su encabezado; una columna ajena fuera del bloque se ignora y va en una nota.
    - Intervenciones: la lista de la principal y, después, las que solo están en la de secundaria.
      Niveles e intervenciones no traen valores «No aplica…».
    - Listas de tipo de documento, de fuente y de metodología: la validación o, sin ella, los
      valores presentes (`Lista.origen`).
    - Errores de contrato: `FalloContrato` con todos los que haya (ver el docstring del módulo); no
      hay esquema parcial. Advertencias y nota de estructura: en el `Esquema`.
    """
    hoja = libro.hoja(HOJA_MATRIZ)
    if hoja is None:
        return FalloContrato((_error(HOJA_AUSENTE, (HOJA_MATRIZ,), libro.nombres_hojas()),))

    ultima_fila, ultima_columna = hoja.dimension()
    encabezados = [_texto(hoja.celda(1, c).valor) for c in range(1, ultima_columna + 1)]
    columnas = _roles(encabezados)

    obligatorias: dict[Rol, Lista | None] = {
        rol: _lista_de_validacion(hoja, columnas[rol])
        for rol in _ROLES_CON_LISTA_OBLIGATORIA
        if rol in columnas
    }
    tipos_documento = (
        _lista_o_presentes(hoja, columnas[Rol.TIPO_DOCUMENTO], ultima_fila)
        if Rol.TIPO_DOCUMENTO in columnas
        else None
    )
    errores = _errores_de_contrato(encabezados, columnas, obligatorias, tipos_documento)
    principal = obligatorias.get(Rol.INTERVENCION_PRINCIPAL)
    secundaria = obligatorias.get(Rol.INTERVENCION_SECUNDARIA)
    nivel = obligatorias.get(Rol.NIVEL_EVIDENCIA)
    if (
        errores
        or principal is None
        or secundaria is None
        or nivel is None
        or tipos_documento is None
    ):
        return FalloContrato(errores)

    tipos_fuente = _lista_o_presentes(hoja, columnas[Rol.TIPO_FUENTE], ultima_fila)
    metodologias = _lista_o_presentes(hoja, columnas[Rol.METODOLOGIA], ultima_fila)

    principales = _categorias(principal.valores)
    solo_secundaria = tuple(v for v in _categorias(secundaria.valores) if v not in principales)
    anclas = Anclas(
        empiricos=_empiricos(tipos_documento),
        evaluacion_impacto=(
            _VALOR_EVALUACION_IMPACTO if _VALOR_EVALUACION_IMPACTO in nivel.valores else None
        ),
    )
    del_bloque, nota = _advertencias_del_bloque(hoja, encabezados, columnas)
    de_listas = _advertencias_de_listas(
        columnas,
        {
            Rol.INTERVENCION_PRINCIPAL: principal,
            Rol.NIVEL_EVIDENCIA: nivel,
            Rol.TIPO_DOCUMENTO: tipos_documento,
            Rol.TIPO_FUENTE: tipos_fuente,
            Rol.METODOLOGIA: metodologias,
        },
        anclas,
    )
    return Esquema(
        columnas=columnas,
        dimensiones=tuple(nombre for nombre, _ in columnas_del_bloque(encabezados, columnas)),
        intervenciones=(*principales, *solo_secundaria),
        niveles=_categorias(nivel.valores),
        tipos_documento=tipos_documento,
        tipos_fuente=tipos_fuente,
        metodologias=metodologias,
        anclas=anclas,
        advertencias=(*del_bloque, *de_listas),
        notas=() if nota is None else (nota,),
    )
