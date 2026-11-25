"""M05 `egm.lectura`: lee todas las filas no vacías de la matriz (arquitectura §6.1, M05).

Camino válido (T-001-24): todas las filas no vacías, sin límite de filas (contrato §4 reglas 4 y
5); comparación de los valores de lista tras quitar espacios en los extremos (regla 6); dimensiones
marcadas solo por el 1 numérico (regla 10); $I_r$ en el orden de la lista (§5); nivel de evidencia
o `SIN_NIVEL`; año entero (regla 12); textos tal cual; `DatosCrudos` (texto «1», espacios,
$G_r = H_r$); clasificación del enfoque por prefijo (§6) y estado de cada documento (§4).

No corrige ningún valor. Las categorías, las dimensiones y los valores ancla salen del `Esquema`
que descubrió M04; este módulo solo escribe el prefijo «No aplica» del contrato §4.1 y la tabla
de palabras del enfoque del §6. El orden de las columnas de dimensiones lo da
`egm.esquema.columnas_del_bloque`, la única regla del bloque.

Advertencias de fila (historia 2; códigos de `egm.modelo`, ámbito `fila`, con `ref`, `columna` y
`valor`): valor fuera de lista en toda columna con lista, espacios en los extremos, dimensión con un
valor que no es 1, 0 ni vacío, año no reconocido, N.º vacío o repetido, $G_r = H_r$, no empírico con
intervención, tipo de documento fuera de lista y enfoque sin clasificar. Ninguna corrige ni descarta
el valor: `valor` es el texto de la celda tal como está. Un valor fuera de lista se conserva en el
documento y no se cuenta; los de cada fila salen en el orden de sus columnas.

Reglas del núcleo (arquitectura §4.1): importa `egm.modelo`, `egm.esquema` y `egm.libro`; no
importa la biblioteca de lectura de libros ni la capa web; sin entrada ni salida.
"""

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from egm.esquema import HOJA_MATRIZ, columnas_del_bloque
from egm.libro import Libro, Valor
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
    Advertencia,
    AnioNoReconocido,
    Corpus,
    DatosCrudos,
    Documento,
    Enfoque,
    Esquema,
    EstadoDocumento,
    Lista,
    RefFila,
    Rol,
)

__all__ = ["clasificar_enfoque", "leer"]

_PREFIJO_NO_APLICA: Final = "No aplica"
"""Valor ancla «Prefijo no aplicable» (contrato §4.1)."""

_PALABRAS_DE_ENFOQUE: Final[Mapping[str, Enfoque]] = {
    "sí": Enfoque.SI,
    "no": Enfoque.NO,
    "parcial": Enfoque.PARCIAL,
}
"""Primera palabra completa de la columna de enfoque, en minúscula (contrato §6): la única tabla."""

_PRIMERA_PALABRA: Final = re.compile(r"\w+")

_AMBITO_FILA: Final = "fila"

_ROLES_DE_TEXTO: Final = (
    Rol.REFERENCIA,
    Rol.PAIS_POBLACION,
    Rol.DELIMITADOR_INICIAL,
    Rol.DELIMITADOR_FINAL,
    Rol.ENFOQUE,
    Rol.HALLAZGOS,
    Rol.VACIO,
    Rol.LIMITACIONES,
    Rol.APORTE,
)
"""Columnas cuyo texto se guarda tal cual en `Documento.textos` (arquitectura §6.1, M05)."""

_ROLES_COMPARADOS: Final = (
    Rol.INTERVENCION_PRINCIPAL,
    Rol.INTERVENCION_SECUNDARIA,
    Rol.TIPO_DOCUMENTO,
    Rol.TIPO_FUENTE,
    Rol.METODOLOGIA,
    Rol.NIVEL_EVIDENCIA,
)
"""Columnas cuyo valor se compara con una lista tras quitar espacios (contrato §4 regla 6)."""


# --------------------------------------------------------------------------------------------
# Celdas
# --------------------------------------------------------------------------------------------


def _vacia(valor: Valor) -> bool:
    """Celda vacía: sin contenido o solo con espacios (contrato §4 reglas 4 y 6, §6)."""
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _como_texto(valor: Valor) -> str | None:
    """El contenido de una celda como texto, sin cambios; `None` si está vacía."""
    if _vacia(valor):
        return None
    return valor if isinstance(valor, str) else str(valor)


def _comparable(valor: Valor) -> str | None:
    """El contenido como texto sin espacios en los extremos; `None` si está vacía."""
    texto = _como_texto(valor)
    return None if texto is None else texto.strip()


def _numero(valor: Valor) -> str | None:
    """El N.º como texto: el entero 6 (o el decimal 6.0) es «6»; vacío es `None`."""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return _como_texto(valor)


def _anio(valor: Valor) -> int | AnioNoReconocido | None:
    """Año entero, `None` si la celda está vacía o `AnioNoReconocido` con lo que trae."""
    texto = _como_texto(valor)
    if texto is None:
        return None
    if isinstance(valor, bool):
        return AnioNoReconocido(texto)
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    return AnioNoReconocido(texto)


def _marca(valor: Valor) -> bool:
    """Solo el número 1 marca la dimensión; el texto «1» y un lógico no (contrato §4 regla 10)."""
    return isinstance(valor, int | float) and not isinstance(valor, bool) and valor == 1


# --------------------------------------------------------------------------------------------
# Enfoque
# --------------------------------------------------------------------------------------------


def clasificar_enfoque(texto: str | None) -> tuple[Enfoque, Advertencia | None]:
    """Clasifica el texto de la columna de enfoque por su primera palabra (contrato §6).

    - Vacío, `None` o solo espacios: `SIN_DILIGENCIAR`, sin advertencia.
    - Primera palabra completa, sin distinguir mayúsculas, igual a «Sí», «No» o «Parcial»: `SI`,
      `NO` o `PARCIAL`. «Si» sin tilde no es «Sí».
    - Cualquier otro comienzo: `SIN_CLASIFICAR` con una advertencia (código
      `ENFOQUE_SIN_CLASIFICAR`) cuyo `valor` es el texto sin espacios en los extremos. La
      advertencia no trae fila ni columna: `leer` las completa. Nunca se infiere la categoría del
      resto del texto.
    """
    limpio = "" if texto is None else unicodedata.normalize("NFC", texto).strip()
    if not limpio:
        return Enfoque.SIN_DILIGENCIAR, None
    palabra = _PRIMERA_PALABRA.match(limpio)
    categoria = _PALABRAS_DE_ENFOQUE.get(palabra.group().casefold()) if palabra else None
    if categoria is not None:
        return categoria, None
    advertencia = Advertencia(
        codigo=ENFOQUE_SIN_CLASIFICAR,
        ambito=_AMBITO_FILA,
        ref=None,
        columna=None,
        valor=limpio,
        datos={},
    )
    return Enfoque.SIN_CLASIFICAR, advertencia


# --------------------------------------------------------------------------------------------
# Contexto de lectura
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Contexto:
    """Lo que se necesita para leer cada fila; se arma una vez por hoja."""

    esquema: Esquema
    dimensiones: tuple[tuple[str, int], ...]
    """Nombre y columna de cada dimensión, en el orden del archivo."""
    encabezados: tuple[str | None, ...]
    """Encabezado de cada columna (sin espacios en los extremos); la columna 1 es el índice 0."""


def _estado(
    tipo: str | None,
    esquema: Esquema,
    intervenciones: tuple[str, ...],
    dimensiones: tuple[str, ...],
) -> EstadoDocumento:
    """Estado del documento por su tipo, su $I_r$ y su $J_r$ (contrato §4, estado de cada uno)."""
    if tipo in esquema.anclas.empiricos:
        return (
            EstadoDocumento.EN_EL_MAPA
            if intervenciones and dimensiones
            else EstadoDocumento.EMPIRICO_PENDIENTE
        )
    lista = esquema.tipos_documento
    if tipo is None or (lista.origen == "validacion" and tipo not in lista.valores):
        return EstadoDocumento.SIN_TIPO_VALIDO
    return EstadoDocumento.NO_EMPIRICO


# --------------------------------------------------------------------------------------------
# Advertencias de una fila
# --------------------------------------------------------------------------------------------


def _lista_de(rol: Rol, esquema: Esquema) -> Lista | None:
    """La lista de un rol comparado, solo si viene de una validación de datos; si no, `None`."""
    lista = {
        Rol.TIPO_DOCUMENTO: esquema.tipos_documento,
        Rol.TIPO_FUENTE: esquema.tipos_fuente,
        Rol.METODOLOGIA: esquema.metodologias,
    }.get(rol)
    return lista if lista is not None and lista.origen == "validacion" else None


def _fuera_de_lista(rol: Rol, valor: str, esquema: Esquema) -> bool:
    """El valor (sin espacios en los extremos) no está en la lista de su columna (contrato §4.7).

    Intervenciones y nivel aceptan además cualquier valor que empiece por «No aplica» (regla 8):
    es un valor de la lista que no es categoría. Sin lista de validación (§4.2) no se comprueba.
    """
    if rol in (Rol.INTERVENCION_PRINCIPAL, Rol.INTERVENCION_SECUNDARIA):
        return valor not in esquema.intervenciones and not valor.startswith(_PREFIJO_NO_APLICA)
    if rol is Rol.NIVEL_EVIDENCIA:
        return valor not in esquema.niveles and not valor.startswith(_PREFIJO_NO_APLICA)
    lista = _lista_de(rol, esquema)
    return lista is not None and valor not in lista.valores


def _dimension_valida(valor: Valor) -> bool:
    """Vacía, o el número 1 o el número 0 (contrato §4, regla 10); el texto «1» no lo es."""
    return _vacia(valor) or (
        isinstance(valor, int | float) and not isinstance(valor, bool) and valor in (0, 1)
    )


def _es_numero_en_texto(valor: Valor) -> bool:
    """El valor es un texto que se lee como número («1», «0», «2»), no un número de la celda."""
    if not isinstance(valor, str):
        return False
    try:
        float(valor)
    except ValueError:
        return False
    return True


def _advertencias_de_fila(
    documento: Documento,
    valores: Sequence[Valor],
    contexto: _Contexto,
    anteriores: tuple[int, ...],
) -> list[Advertencia]:
    """Las advertencias de una fila, ordenadas por columna; ninguna corrige el valor.

    `documento` es el que ya se leyó de la fila y `valores` sus celdas. `valor` de cada
    advertencia es el texto de la celda tal como está (con sus espacios); `anteriores` son las
    filas previas con el mismo N.º.
    """
    esquema = contexto.esquema
    columnas = esquema.columnas
    ref = documento.ref
    encontradas: list[tuple[int, Advertencia]] = []

    def anotar(
        codigo: str, columna: int, valor: str | None, datos: Mapping[str, object] | None = None
    ) -> None:
        advertencia = Advertencia(
            codigo=codigo,
            ambito=_AMBITO_FILA,
            ref=ref,
            columna=contexto.encabezados[columna - 1],
            valor=valor,
            datos={} if datos is None else datos,
        )
        encontradas.append((columna, advertencia))

    def texto_de(rol: Rol) -> str | None:
        return _como_texto(valores[columnas[rol] - 1])

    if ref.numero is None:
        anotar(NUMERO_VACIO, columnas[Rol.IDENTIFICADOR], None)
    elif anteriores:
        anotar(
            NUMERO_REPETIDO,
            columnas[Rol.IDENTIFICADOR],
            ref.numero,
            {"filas_anteriores": anteriores},
        )

    if isinstance(documento.anio, AnioNoReconocido):
        anotar(ANIO_NO_RECONOCIDO, columnas[Rol.ANIO], documento.anio.texto)

    for rol in _ROLES_COMPARADOS:
        valor = texto_de(rol)
        if valor is None:
            continue
        if _fuera_de_lista(rol, valor.strip(), esquema):
            codigo = (
                TIPO_DOCUMENTO_FUERA_DE_LISTA if rol is Rol.TIPO_DOCUMENTO else VALOR_FUERA_DE_LISTA
            )
            anotar(codigo, columnas[rol], valor)
        if rol in documento.crudos.con_espacios:
            anotar(ESPACIOS_EN_LOS_EXTREMOS, columnas[rol], valor)

    for nombre, columna in contexto.dimensiones:
        celda = valores[columna - 1]
        if not _dimension_valida(celda):
            anotar(
                DIMENSION_VALOR_INVALIDO,
                columna,
                _como_texto(celda),
                {"dimension": nombre, "numero_en_texto": _es_numero_en_texto(celda)},
            )

    if documento.crudos.principal_igual_secundaria:
        anotar(
            PRINCIPAL_IGUAL_SECUNDARIA,
            columnas[Rol.INTERVENCION_PRINCIPAL],
            texto_de(Rol.INTERVENCION_PRINCIPAL),
            {
                "intervencion": documento.intervenciones[0],
                "columna_secundaria": contexto.encabezados[
                    columnas[Rol.INTERVENCION_SECUNDARIA] - 1
                ],
            },
        )

    if documento.estado is EstadoDocumento.NO_EMPIRICO and documento.intervenciones:
        rol = (
            Rol.INTERVENCION_PRINCIPAL
            if _comparable(texto_de(Rol.INTERVENCION_PRINCIPAL)) in documento.intervenciones
            else Rol.INTERVENCION_SECUNDARIA
        )
        anotar(
            NO_EMPIRICO_CON_INTERVENCION,
            columnas[rol],
            texto_de(rol),
            {
                "tipo_documento": documento.tipo_documento,
                "intervenciones": documento.intervenciones,
            },
        )

    _, de_enfoque = clasificar_enfoque(documento.textos[Rol.ENFOQUE])
    if de_enfoque is not None:
        anotar(ENFOQUE_SIN_CLASIFICAR, columnas[Rol.ENFOQUE], de_enfoque.valor, de_enfoque.datos)

    encontradas.sort(key=lambda par: par[0])
    return [advertencia for _, advertencia in encontradas]


# --------------------------------------------------------------------------------------------
# Un documento
# --------------------------------------------------------------------------------------------


def _leer_documento(fila: int, valores: Sequence[Valor], contexto: _Contexto) -> Documento:
    """El documento de una fila no vacía (`valores`: sus celdas desde la columna 1)."""
    esquema = contexto.esquema

    def celda(rol: Rol) -> Valor:
        return valores[esquema.columnas[rol] - 1]

    comparables: dict[Rol, str | None] = {}
    con_espacios: list[Rol] = []
    for rol in _ROLES_COMPARADOS:
        crudo = celda(rol)
        comparables[rol] = _comparable(crudo)
        if isinstance(crudo, str) and comparables[rol] not in (None, crudo):
            con_espacios.append(rol)

    principal = comparables[Rol.INTERVENCION_PRINCIPAL]
    secundaria = comparables[Rol.INTERVENCION_SECUNDARIA]
    presentes = {principal, secundaria}
    intervenciones = tuple(i for i in esquema.intervenciones if i in presentes)
    dimensiones = tuple(n for n, columna in contexto.dimensiones if _marca(valores[columna - 1]))
    como_texto = tuple(n for n, columna in contexto.dimensiones if valores[columna - 1] == "1")

    nivel = comparables[Rol.NIVEL_EVIDENCIA]
    if nivel is None or nivel.startswith(_PREFIJO_NO_APLICA):
        nivel = SIN_NIVEL

    ref = RefFila(_numero(celda(Rol.IDENTIFICADOR)), fila)
    textos = {rol: _como_texto(celda(rol)) for rol in _ROLES_DE_TEXTO}
    enfoque, _ = clasificar_enfoque(textos[Rol.ENFOQUE])

    tipo = comparables[Rol.TIPO_DOCUMENTO]
    return Documento(
        ref=ref,
        anio=_anio(celda(Rol.ANIO)),
        tipo_documento=tipo,
        tipo_fuente=comparables[Rol.TIPO_FUENTE],
        metodologia=comparables[Rol.METODOLOGIA],
        intervenciones=intervenciones,
        dimensiones=dimensiones,
        nivel=nivel,
        enfoque=enfoque,
        estado=_estado(tipo, esquema, intervenciones, dimensiones),
        textos=textos,
        crudos=DatosCrudos(
            dimensiones_como_texto=como_texto,
            con_espacios=tuple(con_espacios),
            principal_igual_secundaria=(
                principal is not None
                and principal == secundaria
                and principal in esquema.intervenciones
            ),
        ),
    )


# --------------------------------------------------------------------------------------------
# La hoja
# --------------------------------------------------------------------------------------------


def leer(libro: Libro, esquema: Esquema) -> Corpus:
    """Lee todos los documentos de la hoja de la matriz, en el orden del archivo.

    `esquema` es el que `egm.esquema.descubrir` sacó de este mismo `libro`; sin la hoja de la
    matriz, `ValueError`. Se leen todas las filas desde la 2, sin límite; una fila con todas sus
    celdas vacías (o solo con espacios) no es un documento. `Corpus.fila_final_leida` es la última
    fila leída con contenido, o 1 (el encabezado) si no hay ninguna. `RefFila.numero` es el N.º
    como texto y `RefFila.fila` la fila del archivo (el encabezado está en la fila 1).

    Solo el 1 numérico marca una dimensión. Los textos van sin cambios; el valor de una lista se
    guarda sin espacios en los extremos y, si los tenía, queda anotado en `Documento.crudos`.
    `Corpus.advertencias` trae las de cada fila (ver el docstring del módulo), fila por fila y,
    dentro de cada una, en el orden de sus columnas. Un N.º repetido se advierte en cada fila
    posterior a la primera que lo trae, con las filas anteriores en `datos["filas_anteriores"]`.
    """
    hoja = libro.hoja(HOJA_MATRIZ)
    if hoja is None:
        raise ValueError(f"el libro no tiene la hoja de la matriz ({HOJA_MATRIZ})")

    ultima_fila, ultima_columna = hoja.dimension()
    columnas = range(1, ultima_columna + 1)
    encabezados = tuple(_comparable(hoja.celda(1, c).valor) for c in columnas)
    contexto = _Contexto(
        esquema=esquema,
        dimensiones=columnas_del_bloque(list(encabezados), esquema.columnas),
        encabezados=encabezados,
    )

    documentos: list[Documento] = []
    advertencias: list[Advertencia] = []
    filas_por_numero: dict[str, list[int]] = {}
    fila_final = 1
    for fila in range(2, ultima_fila + 1):
        valores = [hoja.celda(fila, c).valor for c in columnas]
        if all(_vacia(valor) for valor in valores):
            continue
        documento = _leer_documento(fila, valores, contexto)
        numero = documento.ref.numero
        previas = filas_por_numero.setdefault(numero.strip(), []) if numero is not None else []
        advertencias.extend(_advertencias_de_fila(documento, valores, contexto, tuple(previas)))
        previas.append(fila)
        documentos.append(documento)
        fila_final = fila

    return Corpus(
        documentos=tuple(documentos),
        advertencias=tuple(advertencias),
        fila_final_leida=fila_final,
    )
