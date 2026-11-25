"""M10 `egm.textos`: catálogo único de los textos dirigidos al equipo (arquitectura §6.1, M10).

Todo texto de la interfaz vive aquí y en ningún otro módulo: en español, de usted, sin jerga
técnica, sin fórmulas y sin preguntas (NFR-000-03). Este módulo no calcula: recibe datos ya
calculados y devuelve cadenas (arquitectura §4.1, regla 4). Solo importa la biblioteca estándar y
`egm.modelo`.

Base (plan 001, T-001-17): los textos de rechazo (estados E2, E3 y E10 de `docs/interfaz/flujos.md`
§2), `fecha()` y `ROTULOS` vacío. Historia 2 (T-001-34): `advertencia()`, `nota()` y
`error_contrato()`, cuyos textos viven también en el catálogo con las claves `advertencia.<codigo>`,
`nota.<codigo>` y `error.<codigo>`. Los planes siguientes agregan al catálogo la verificación, las
conclusiones y los rótulos.

Las plantillas del catálogo marcan los datos con `%(nombre)s` (nombres sin guion bajo) y no con
llaves, para que la revisión de estilo, que rechaza símbolos de fórmula, siga vigilando todo el
catálogo. Ningún texto lleva el nombre del archivo ni el contenido de otras celdas de la fila: solo
el N.º (o la fila), la columna y el valor señalado (FR-001-12, FR-001-29).
"""

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from types import MappingProxyType
from typing import Final

from egm.modelo import (
    ANIO_NO_RECONOCIDO,
    BLOQUE_SIN_DIMENSIONES,
    COLUMNA_SIN_LISTA,
    COLUMNAS_NO_USADAS,
    DIMENSION_SIN_LISTA_1_0,
    DIMENSION_VALOR_INVALIDO,
    ENFOQUE_SIN_CLASIFICAR,
    ESPACIOS_EN_LOS_EXTREMOS,
    LISTA_1_0_FUERA_DEL_BLOQUE,
    LISTA_SIN_NO_APLICA,
    NO_EMPIRICO_CON_INTERVENCION,
    NUMERO_REPETIDO,
    NUMERO_VACIO,
    PRINCIPAL_IGUAL_SECUNDARIA,
    ROL_DENTRO_DEL_BLOQUE,
    SIN_ANCLA_EVALUACION_IMPACTO,
    TIPO_DOCUMENTO_FUERA_DE_LISTA,
    VALOR_FUERA_DE_LISTA,
    VARIOS_EMPIRICOS,
    Advertencia,
    ErrorContrato,
    FalloContrato,
    Nota,
    Rechazo,
)

__all__ = ["CATALOGO", "ROTULOS", "advertencia", "error_contrato", "fecha", "nota", "rechazo"]

CATALOGO: Final[Mapping[str, str]] = MappingProxyType(
    {
        # E2: archivo que no es un libro .xlsx, o .xlsx dañado (US-001-4.3, SC-000-19).
        "rechazo.tipo": (
            "No se pudo cargar el archivo. El archivo elegido no es un archivo de Excel (.xlsx) "
            "que la herramienta pueda abrir, o está dañado. No se leyó y no se muestra ningún "
            "resultado. Elija la matriz bibliográfica en formato .xlsx."
        ),
        # E3: más de 15 728 640 bytes (US-001-4.4, SC-000-19).
        "rechazo.tamano": (
            "No se pudo cargar el archivo. El archivo pesa más de 15 MB (15 728 640 bytes), el "
            "máximo que admite la herramienta. No se leyó y no se muestra ningún resultado de ese "
            "archivo."
        ),
        # E10: contenido descomprimido declarado por encima del límite; sin cifras (US-001-4.13).
        "rechazo.contenido": (
            "No se pudo cargar el archivo. El contenido del libro es demasiado grande para "
            "abrirlo. No se leyó y no se muestra ningún resultado de ese archivo."
        ),
        # --- Advertencias de fila: «N.º 7, columna «…», valor «…»: <mensaje>» (F-001-2, FR-001-12).
        "advertencia.ref.numero": "N.º %(numero)s",
        "advertencia.ref.fila": "Fila %(fila)s",  # N.º vacío: el documento se señala por su fila
        "advertencia.ref.columna": ", columna «%(columna)s»",
        "advertencia.ref.valor": ", valor «%(valor)s»",
        "advertencia.ref.cierre": ": ",
        "advertencia.valor_fuera_de_lista": (
            "el valor no está en la lista de esa columna. La herramienta no lo cuenta y no lo "
            "corrige."
        ),
        "advertencia.espacios_en_los_extremos": (
            "el valor trae espacios al comienzo o al final. La herramienta los ignora al "
            "compararlo y no modifica la matriz."
        ),
        "advertencia.dimension_valor_invalido.texto": (
            "el número está escrito como texto y no como número. No marca la dimensión."
        ),
        "advertencia.dimension_valor_invalido.fuera": (
            "el valor no es 1 ni 0. No marca la dimensión."
        ),
        "advertencia.anio_no_reconocido": (
            "el año no se reconoce como número. El documento se cuenta igual y su año se muestra "
            "como año no reconocido."
        ),
        "advertencia.numero_vacio": (
            "la celda del N.º está vacía y la fila tiene contenido. El documento se lee y se "
            "identifica por su número de fila."
        ),
        "advertencia.numero_repetido.una": (
            "este N.º ya aparece en la fila %(anteriores)s. Este documento, en la fila %(fila)s, "
            "se lee aparte y se identifica también por su número de fila."
        ),
        "advertencia.numero_repetido.varias": (
            "este N.º ya aparece en las filas %(anteriores)s. Este documento, en la fila "
            "%(fila)s, se lee aparte y se identifica también por su número de fila."
        ),
        "advertencia.principal_igual_secundaria": (
            "la intervención «%(intervencion)s» está en la principal y también en la secundaria "
            "(columna «%(secundaria)s»). La hoja EGM la cuenta dos veces y esta herramienta, una."
        ),
        "advertencia.no_empirico_con_intervencion": (
            "el documento es de tipo «%(tipo)s» y trae una intervención. No es un estudio "
            "empírico, así que no cuenta en el mapa."
        ),
        "advertencia.no_empirico_con_intervencion.sin_tipo": (
            "el documento no es un estudio empírico y trae una intervención. No cuenta en el mapa."
        ),
        "advertencia.tipo_documento_fuera_de_lista": (
            "el tipo de documento no está en la lista de esa columna. El documento se cuenta entre "
            "los leídos, queda sin tipo válido y no cuenta como estudio empírico."
        ),
        "advertencia.enfoque_sin_clasificar": (
            "no empieza por Sí, No o Parcial, como pide la hoja Instrucciones. Queda como «Sin "
            "clasificar»."
        ),
        # --- Advertencias de estructura (sin fila: dicen la hoja, la columna o el valor).
        "advertencia.bloque_sin_dimensiones.vacio": (
            "En la hoja «Matriz bibliográfica» no hay columnas de dimensiones entre las dos "
            "columnas que delimitan el bloque. Ningún estudio entra al mapa y los estudios "
            "empíricos quedan pendientes."
        ),
        "advertencia.bloque_sin_dimensiones.invertido": (
            "En la hoja «Matriz bibliográfica», la columna que cierra el bloque de dimensiones "
            "está antes de la que lo inicia, así que el bloque no tiene dimensiones. Ningún "
            "estudio entra al mapa y los estudios empíricos quedan pendientes."
        ),
        "advertencia.rol_dentro_del_bloque": (
            "La columna «%(columna)s» está dentro del bloque de dimensiones, pero es una columna "
            "propia de la matriz. La herramienta la lee con su función y no como dimensión."
        ),
        "advertencia.lista_1_0_fuera_del_bloque": (
            "La columna «%(columna)s» está fuera del bloque de dimensiones y tiene lista de "
            "valores 1 y 0. La herramienta no la toma como dimensión."
        ),
        "advertencia.dimension_sin_lista_1_0": (
            "La columna «%(columna)s», dentro del bloque de dimensiones, no tiene la lista de "
            "valores 1 y 0. La herramienta la toma como dimensión de todos modos."
        ),
        "advertencia.lista_sin_no_aplica": (
            "La lista de la columna «%(columna)s» no tiene ningún valor que empiece por "
            "«%(valor)s». La herramienta toma todos sus valores como categorías."
        ),
        "advertencia.varios_empiricos": (
            "La lista de la columna «%(columna)s» tiene más de un valor que empieza por «Estudio "
            "empírico»: %(valores)s. La herramienta toma todos como estudio empírico."
        ),
        "advertencia.sin_ancla_evaluacion_impacto": (
            "La lista de la columna «%(columna)s» no tiene el valor «%(valor)s». La herramienta "
            "calcula el mapa, pero lo que depende de ese nivel queda como no disponible."
        ),
        "advertencia.sin_ancla_evaluacion_impacto.niveles": (" Niveles de la lista: %(niveles)s."),
        "advertencia.columna_sin_lista": (
            "La columna «%(columna)s» no tiene lista de valores. La herramienta toma los valores "
            "presentes en la matriz: %(valores)s."
        ),
        # --- Nota informativa: «Columnas no usadas: Observaciones» (F-001-2, FR-001-21).
        "nota.columnas_no_usadas": "Columnas no usadas: %(columnas)s.",
        # --- Errores de contrato, estado E4 de flujos.md §2: inicio, una frase por error y cierre.
        "error.inicio": "No se pudo leer la matriz.",
        "error.hoja_ausente": "Se esperaba la hoja %(esperado)s, y %(encontrado)s.",
        "error.encabezado_ausente": "Se esperaba la columna %(esperado)s, y %(encontrado)s.",
        "error.encabezado_ausente.varios": (
            "Se esperaban las columnas %(esperado)s, y %(encontrado)s."
        ),
        "error.ancla_empirica_ausente": (
            "Se esperaba un valor que empiece por %(esperado)s en la lista de la columna de tipo "
            "de documento, y %(encontrado)s."
        ),
        "error.lista_obligatoria_ausente": (
            "Se esperaba una lista de valores en la columna %(esperado)s, y %(encontrado)s."
        ),
        "error.lista_obligatoria_ausente.varios": (
            "Se esperaba una lista de valores en cada una de las columnas %(esperado)s, y "
            "%(encontrado)s."
        ),
        "error.encontrado.ninguno": "no se encontró",
        "error.encontrado.ninguno.varios": "no se encontraron",
        "error.encontrado.uno": "se encontró: %(valores)s",
        "error.encontrado.varios": "se encontraron: %(valores)s",
        "error.cierre": (
            "No se muestra ninguna cifra. Revise que el archivo sea la matriz bibliográfica del "
            "proyecto y vuelva a cargarlo."
        ),
    }
)
"""Catálogo único: clave del texto → texto. Los planes 001, 002 y 003 lo amplían."""

ROTULOS: Final[Mapping[str, str]] = MappingProxyType({})
"""Rótulos cortos de la interfaz. Vacío en la base; los planes 002 y 003 lo amplían."""

# Meses en una tabla propia: el resultado no depende de la configuración regional del equipo.
_MESES: Final = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def rechazo(r: Rechazo) -> str:
    """Texto de la interfaz para un archivo rechazado antes de leerlo (E2, E3 o E10)."""
    return CATALOGO[f"rechazo.{r.motivo}"]


def fecha(d: datetime) -> str:
    """Fecha en español, por ejemplo «21 de noviembre de 2026» (día sin cero a la izquierda)."""
    return f"{d.day} de {_MESES[d.month - 1]} de {d.year}"


# --------------------------------------------------------------------------------------------
# Advertencias, notas y errores de contrato (historia 2)
# --------------------------------------------------------------------------------------------


def _armar(clave: str, **datos: object) -> str:
    """La plantilla del catálogo con sus datos."""
    return CATALOGO[clave] % datos


def _citar(valores: Sequence[str]) -> str:
    """Los valores entre comillas angulares: «A», «B» y «C» (la comilla evita «y» ante «i»)."""
    citados = [f"«{valor}»" for valor in valores]
    if len(citados) <= 1:
        return "".join(citados)
    return f"{', '.join(citados[:-1])} y {citados[-1]}"


def _como_tupla(dato: object) -> tuple[str, ...]:
    """Los textos de un dato que M04 o M05 entregan como tupla de valores; vacío si no lo es."""
    if isinstance(dato, tuple | list):
        return tuple(str(elemento) for elemento in dato)
    return ()


def _prefijo_de_fila(a: Advertencia) -> str:
    """«N.º 7, columna «…», valor «…»: » (o «Fila 7, …» si el N.º está vacío)."""
    if a.ref is None:
        return ""
    if a.ref.numero is None:
        prefijo = _armar("advertencia.ref.fila", fila=a.ref.fila)
    else:
        prefijo = _armar("advertencia.ref.numero", numero=a.ref.numero)
    if a.columna:
        prefijo += _armar("advertencia.ref.columna", columna=a.columna)
    if a.valor is not None and a.valor.strip():
        prefijo += _armar("advertencia.ref.valor", valor=a.valor.strip())
    return prefijo + CATALOGO["advertencia.ref.cierre"]


def _dimension_invalida(a: Advertencia) -> str:
    texto = a.datos.get("numero_en_texto") is True
    return CATALOGO[f"advertencia.dimension_valor_invalido.{'texto' if texto else 'fuera'}"]


def _numero_repetido(a: Advertencia) -> str:
    anteriores = _como_tupla(a.datos.get("filas_anteriores"))
    clave = "advertencia.numero_repetido." + ("una" if len(anteriores) <= 1 else "varias")
    fila = a.ref.fila if a.ref is not None else ""
    if len(anteriores) <= 1:
        junto = "".join(anteriores)
    else:
        junto = f"{', '.join(anteriores[:-1])} y {anteriores[-1]}"
    return _armar(clave, anteriores=junto, fila=fila)


def _principal_igual_secundaria(a: Advertencia) -> str:
    return _armar(
        "advertencia.principal_igual_secundaria",
        intervencion=a.datos.get("intervencion", a.valor or ""),
        secundaria=a.datos.get("columna_secundaria", ""),
    )


def _no_empirico_con_intervencion(a: Advertencia) -> str:
    tipo = a.datos.get("tipo_documento")
    if tipo is None:
        return CATALOGO["advertencia.no_empirico_con_intervencion.sin_tipo"]
    return _armar("advertencia.no_empirico_con_intervencion", tipo=tipo)


def _bloque_sin_dimensiones(a: Advertencia) -> str:
    invertido = a.datos.get("motivo") == "invertido"
    return CATALOGO[f"advertencia.bloque_sin_dimensiones.{'invertido' if invertido else 'vacio'}"]


def _de_la_columna(codigo: str) -> Callable[[Advertencia], str]:
    """Texto que solo nombra la columna de la advertencia."""
    return lambda a: _armar(f"advertencia.{codigo}", columna=a.columna or "")


def _lista_sin_no_aplica(a: Advertencia) -> str:
    return _armar(
        "advertencia.lista_sin_no_aplica", columna=a.columna or "", valor=a.valor or "No aplica"
    )


def _varios_empiricos(a: Advertencia) -> str:
    valores = _citar(_como_tupla(a.datos.get("valores")))
    return _armar("advertencia.varios_empiricos", columna=a.columna or "", valores=valores)


def _sin_ancla_evaluacion_impacto(a: Advertencia) -> str:
    texto = _armar(
        "advertencia.sin_ancla_evaluacion_impacto", columna=a.columna or "", valor=a.valor or ""
    )
    niveles = _como_tupla(a.datos.get("niveles"))
    if niveles:
        texto += _armar("advertencia.sin_ancla_evaluacion_impacto.niveles", niveles=_citar(niveles))
    return texto


def _columna_sin_lista(a: Advertencia) -> str:
    valores = _citar(_como_tupla(a.datos.get("valores")))
    return _armar("advertencia.columna_sin_lista", columna=a.columna or "", valores=valores)


def _fijo(codigo: str) -> Callable[[Advertencia], str]:
    """Texto sin datos propios: el prefijo de la fila ya dice N.º, columna y valor."""
    return lambda _a: CATALOGO[f"advertencia.{codigo}"]


_CUERPOS: Final[Mapping[str, Callable[[Advertencia], str]]] = MappingProxyType(
    {
        ENFOQUE_SIN_CLASIFICAR: _fijo(ENFOQUE_SIN_CLASIFICAR),
        VALOR_FUERA_DE_LISTA: _fijo(VALOR_FUERA_DE_LISTA),
        ESPACIOS_EN_LOS_EXTREMOS: _fijo(ESPACIOS_EN_LOS_EXTREMOS),
        DIMENSION_VALOR_INVALIDO: _dimension_invalida,
        ANIO_NO_RECONOCIDO: _fijo(ANIO_NO_RECONOCIDO),
        NUMERO_VACIO: _fijo(NUMERO_VACIO),
        NUMERO_REPETIDO: _numero_repetido,
        PRINCIPAL_IGUAL_SECUNDARIA: _principal_igual_secundaria,
        NO_EMPIRICO_CON_INTERVENCION: _no_empirico_con_intervencion,
        TIPO_DOCUMENTO_FUERA_DE_LISTA: _fijo(TIPO_DOCUMENTO_FUERA_DE_LISTA),
        BLOQUE_SIN_DIMENSIONES: _bloque_sin_dimensiones,
        ROL_DENTRO_DEL_BLOQUE: _de_la_columna(ROL_DENTRO_DEL_BLOQUE),
        LISTA_1_0_FUERA_DEL_BLOQUE: _de_la_columna(LISTA_1_0_FUERA_DEL_BLOQUE),
        DIMENSION_SIN_LISTA_1_0: _de_la_columna(DIMENSION_SIN_LISTA_1_0),
        LISTA_SIN_NO_APLICA: _lista_sin_no_aplica,
        VARIOS_EMPIRICOS: _varios_empiricos,
        SIN_ANCLA_EVALUACION_IMPACTO: _sin_ancla_evaluacion_impacto,
        COLUMNA_SIN_LISTA: _columna_sin_lista,
    }
)
"""Cuerpo del texto de cada advertencia de la lista cerrada, por código."""


def advertencia(a: Advertencia) -> str:
    """Texto legible de una advertencia (FR-001-12, SC-001-04).

    Las de fila empiezan por «N.º <n>, columna «…», valor «…»: » (o «Fila <n>» si el N.º está
    vacío); el valor se muestra sin los espacios de los extremos y sin corregir. Las de estructura
    nombran la hoja, la columna o el valor. Un código fuera de la lista cerrada es un error de
    programación y levanta `KeyError`.
    """
    return _prefijo_de_fila(a) + _CUERPOS[a.codigo](a)


def nota(n: Nota) -> str:
    """Texto legible de una nota informativa (FR-001-21): «Columnas no usadas: …»."""
    if n.codigo != COLUMNAS_NO_USADAS:
        raise KeyError(n.codigo)
    columnas = ", ".join(_como_tupla(n.datos.get("columnas")))
    return _armar("nota.columnas_no_usadas", columnas=columnas)


def _lo_encontrado(valores: Sequence[str], esperados: int) -> str:
    """«no se encontró», «se encontró: «A»» o «se encontraron: «A» y «B»» (estado E4)."""
    if not valores:
        return CATALOGO["error.encontrado.ninguno" + (".varios" if esperados > 1 else "")]
    clave = "error.encontrado." + ("uno" if len(valores) == 1 else "varios")
    return _armar(clave, valores=_citar(valores))


def _frase_de_error(e: ErrorContrato) -> str:
    clave = f"error.{e.codigo}"
    if len(e.esperado) > 1 and f"{clave}.varios" in CATALOGO:
        clave += ".varios"
    return _armar(
        clave,
        esperado=_citar(e.esperado),
        encontrado=_lo_encontrado(e.encontrado, len(e.esperado)),
    )


def error_contrato(f: FalloContrato) -> str:
    """Texto del estado E4 (flujos.md §2) con todo lo esperado y lo encontrado de cada error.

    «No se pudo leer la matriz. Se esperaba …, y no se encontró / se encontraron: …. No se muestra
    ninguna cifra. Revise que el archivo sea la matriz bibliográfica del proyecto y vuelva a
    cargarlo.» Nunca trae el nombre del archivo ni filas de datos (FR-001-29).
    """
    frases = [_frase_de_error(e) for e in f.errores]
    return " ".join([CATALOGO["error.inicio"], *frases, CATALOGO["error.cierre"]])
