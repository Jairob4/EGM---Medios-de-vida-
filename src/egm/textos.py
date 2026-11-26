"""M10 `egm.textos`: catálogo único de los textos dirigidos al equipo (arquitectura §6.1, M10).

Todo texto de la interfaz vive aquí y en ningún otro módulo: en español, de usted, sin jerga
técnica, sin fórmulas y sin preguntas (NFR-000-03). Este módulo no calcula: recibe datos ya
calculados y devuelve cadenas (arquitectura §4.1, regla 4). Solo importa la biblioteca estándar,
`egm.modelo` y los tipos de resultado de `egm.verificacion` (M08), que no importa este módulo.

Base (plan 001, T-001-17): los textos de rechazo (estados E2, E3 y E10 de `docs/interfaz/flujos.md`
§2), `fecha()` y `ROTULOS` vacío. Historia 2 (T-001-34): `advertencia()`, `nota()` y
`error_contrato()`, cuyos textos viven también en el catálogo con las claves `advertencia.<codigo>`,
`nota.<codigo>` y `error.<codigo>`. Historia 3 (T-001-46): `verificacion()` con los textos de
F-001-3 (claves `verificacion.*`) y los cuerpos de las advertencias propias de M08
(`advertencia.<codigo>`). Los planes siguientes agregan al catálogo las conclusiones y los
rótulos.

Las plantillas del catálogo marcan los datos con `%(nombre)s` (nombres sin guion bajo) y no con
llaves, para que la revisión de estilo, que rechaza símbolos de fórmula, siga vigilando todo el
catálogo. Ningún texto lleva el nombre del archivo ni el contenido de otras celdas de la fila: solo
el N.º (o la fila), la columna y el valor señalado (FR-001-12, FR-001-29).
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Final, Literal

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
    Identificacion,
    Nota,
    Rechazo,
    RefFila,
)
from egm.verificacion import (
    COMPARACION_INCOMPLETA,
    HOJA_ABARCA_MENOS_FILAS,
    HOJA_EGM,
    HOJA_EGM_AUSENTE,
    TABLA_DIFIERE,
    TABLA_NO_RECONOCIDA,
    CausaDiferencia,
    Diferencia,
    EstadoTabla,
    ResultadoTabla,
    Verificacion,
)

__all__ = [
    "CATALOGO",
    "ROTULOS",
    "TextoMensaje",
    "TextoVerificacion",
    "advertencia",
    "aviso_inactividad",
    "cabecera_corrida",
    "error_contrato",
    "fecha",
    "fijo",
    "mensaje_error_contrato",
    "mensaje_rechazo",
    "nota",
    "rechazo",
    "rotulo_advertencias",
    "verificacion",
]

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
        # --- Advertencias propias de la verificación (M08): sin fila; dicen la hoja y la tabla.
        "advertencia.hoja_egm_ausente": (
            "El archivo no trae la hoja «%(hoja)s». Los conteos no se pueden contrastar con ella; "
            "el mapa se calcula igual desde la hoja «Matriz bibliográfica»."
        ),
        "advertencia.tabla_no_reconocida": (
            "En la hoja «%(hoja)s» no se reconoció una única tabla cuyo título tenga un número "
            "y la frase «%(frase)s». Esa tabla no se contrasta con los conteos."
        ),
        "advertencia.comparacion_incompleta.sin_pareja": (
            "Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudieron comparar %(faltantes)s valores. "
            "Sin pareja: %(nombres)s. Un valor que falta no se toma como cero."
        ),
        "advertencia.comparacion_incompleta.sin_numero.uno": (
            "Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudo comparar 1 valor, porque la hoja no "
            "trae un número guardado en esa celda. Un valor que falta no se toma como cero."
        ),
        "advertencia.comparacion_incompleta.sin_numero.varios": (
            "Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudieron comparar %(faltantes)s valores, "
            "porque la hoja no trae un número guardado en esas celdas. Un valor que falta no se "
            "toma como cero."
        ),
        "advertencia.tabla_difiere.uno": (
            "Tabla %(tabla)s de la hoja «%(hoja)s»: 1 valor difiere del conteo de esta herramienta."
        ),
        "advertencia.tabla_difiere.varios": (
            "Tabla %(tabla)s de la hoja «%(hoja)s»: %(celdas)s valores difieren de los conteos de "
            "esta herramienta."
        ),
        "advertencia.hoja_abarca_menos_filas": (
            "Las fórmulas de la hoja «%(hoja)s» abarcan de la fila %(desde)s a la fila "
            "%(hasta)s de la hoja «Matriz bibliográfica», y la herramienta leyó hasta la fila "
            "%(leida)s. La comparación se hace solo con las filas que abarca la hoja."
        ),
        # --- Resultado de la verificación (F-001-3, FR-001-18, FR-001-25).
        "verificacion.coincide": "Los conteos coinciden con la hoja EGM del archivo.",
        "verificacion.difiere": (
            "Los conteos difieren de la hoja EGM en la tabla %(tabla)s: %(celdas)s."
        ),
        "verificacion.sin_causa": "No se identificó la causa de la diferencia en %(celdas)s.",
        "verificacion.celda": "«%(fila)s» con «%(columna)s»",
        "verificacion.mas_celdas": "%(celdas)s y otras %(cuantas)s celdas",
        "verificacion.causa.principal_igual_secundaria.una": (
            "Causa conocida: %(sujeto)s tiene la misma intervención como principal y como "
            "secundaria; la hoja lo cuenta dos veces y esta herramienta, una."
        ),
        "verificacion.causa.principal_igual_secundaria.varias": (
            "Causa conocida: %(sujeto)s tienen la misma intervención como principal y como "
            "secundaria; la hoja los cuenta dos veces y esta herramienta, una."
        ),
        "verificacion.causa.dimension_valor_invalido.una": (
            "Causa conocida: %(sujeto)s tiene una dimensión con el número 1 escrito como texto; "
            "la hoja lo cuenta y esta herramienta, no."
        ),
        "verificacion.causa.dimension_valor_invalido.varias": (
            "Causa conocida: %(sujeto)s tienen una dimensión con el número 1 escrito como texto; "
            "la hoja los cuenta y esta herramienta, no."
        ),
        "verificacion.causa.espacios_en_los_extremos.una": (
            "Causa conocida: %(sujeto)s tiene espacios al comienzo o al final de un valor; la "
            "hoja los toma en cuenta y esta herramienta los ignora."
        ),
        "verificacion.causa.espacios_en_los_extremos.varias": (
            "Causa conocida: %(sujeto)s tienen espacios al comienzo o al final de un valor; la "
            "hoja los toma en cuenta y esta herramienta los ignora."
        ),
        "verificacion.sujeto.numero": "el N.º %(numero)s",
        "verificacion.sujeto.fila": "el documento de la fila %(fila)s",
        "verificacion.sujeto.varios": "los documentos %(filas)s",
        "verificacion.referencia.numero": "N.º %(numero)s",
        "verificacion.referencia.fila": "fila %(fila)s",
        "verificacion.tablas_verificadas": "Tablas verificadas: %(tablas)s.",
        "verificacion.parcial": (
            "Una o más tablas no se pudieron contrastar por completo; las advertencias de lectura "
            "dicen por qué."
        ),
        # F-001-3, «No verificable» (v4): sin lista de tablas verificadas.
        "verificacion.no_verificable.sin_valores": (
            "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo "
            "no trae guardados los resultados de esa hoja. Los conteos de esta herramienta se "
            "calculan directamente de la hoja «Matriz bibliográfica»."
        ),
        "verificacion.no_verificable.sin_hoja": (
            "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo "
            "no trae esa hoja. Los conteos de esta herramienta se calculan directamente de la hoja "
            "«Matriz bibliográfica»."
        ),
        "verificacion.no_verificable.sin_tablas": (
            "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en esa hoja "
            "no se reconocieron las tablas que se contrastan. Los conteos de esta herramienta se "
            "calculan directamente de la hoja «Matriz bibliográfica»."
        ),
        "verificacion.no_verificable.incompleta": (
            "No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en sus "
            "tablas faltan valores o categorías. Los conteos de esta herramienta se calculan "
            "directamente de la hoja «Matriz bibliográfica»."
        ),
        # --- Carga (historia 4, flujos.md §2 y §3): título y párrafos de cada mensaje por separado.
        "mensaje.rechazo.titulo": "No se pudo cargar el archivo",
        "mensaje.e4.titulo": "No se pudo leer la matriz",
        "mensaje.e4.titulo.previa": "No se pudo leer la matriz y la sesión terminó",
        "mensaje.e4.borro_todo": (
            "La herramienta borró todo: la matriz que tenía cargada y sus resultados ya no están "
            "disponibles. Para volver a verlos, cárguela otra vez."
        ),
        "mensaje.sigue_disponible": (
            "La matriz que tenía cargada sigue disponible con sus resultados: %(cabecera)s."
        ),
        "mensaje.volver": "Volver al mapa",
        # [NEEDS CLARIFICATION: nombre que se muestra si la carga llega sin nombre de archivo;
        # flujos.md no lo fija.]
        "carga.sin_nombre": "archivo sin nombre",
        # [NEEDS CLARIFICATION: texto propuesto para un fallo interno; flujos.md no lo fija.
        # Lo revisa Jairo en T-001-93.]
        "mensaje.problema": (
            "No se pudo completar la operación. No se muestra ningún resultado nuevo. Vuelva a "
            "intentarlo."
        ),
        # --- Terminar la sesión (historia 5, flujos.md §2 y §3): E7, E8, E9 y el texto fijo de la
        # cabecera. Los «45 minutos» y los «2 minutos» son los valores fijos de NFR-000-17 y de
        # WCAG 2.2.1; los 2 minutos del aviso salen de la capa web (45 menos 43).
        "sesion.e7.aviso": (
            "Su sesión se cerrará en %(minutos)s minutos por falta de actividad. Al cerrarse, la "
            "matriz deja de estar disponible."
        ),
        "sesion.e7.tiempo": "Tiempo restante:",
        "sesion.e7.boton": "Seguir con la sesión",
        "sesion.e8.descarte": (
            "Descartó el archivo. La sesión terminó y la herramienta no guarda ninguna copia del "
            "archivo ni de sus resultados."
        ),
        "sesion.e8.inactividad": (
            "La sesión terminó porque pasaron 45 minutos sin actividad. La herramienta no guarda "
            "ninguna copia del archivo. Para seguir, cargue de nuevo la matriz."
        ),
        "sesion.e9.recuperando": "Recuperando su sesión.",
        "cabecera.sesion": (
            "La sesión se cierra sola tras 45 minutos sin actividad. El archivo solo se lee: no "
            "se modifica ni se guarda."
        ),
        # --- Cabecera corrida (NFR-000-12): «Matriz: <nombre>, leída el <fecha>, <n> documentos».
        "cabecera.corte": "Matriz: %(nombre)s, leída el %(fecha)s, %(n)s documentos",
        # --- Vista del resultado y avisos de lectura (V2; NC-P001-1).
        "resultado.titulo": "Resultado de la lectura",
        "avisos.advertencias.una": "1 advertencia de lectura",
        "avisos.advertencias.varias": "%(n)s advertencias de lectura",
        # --- Colofón (flujos.md §6; ADR-005): los dos bloques siempre presentes.
        "colofon.datos.rotulo": "Datos",
        "colofon.datos.sin_matriz": "Aún no se ha cargado ninguna matriz.",
        "colofon.referencia.rotulo": "Referencia de diseño",
        "colofon.referencia.texto": (
            "International Initiative for Impact Evaluation (3ie). Building Peaceful Societies "
            "Evidence Gap Map (2019). Licencia CC BY-NC-SA 4.0. Se toma solo como referencia de "
            "diseño; no se reproduce su contenido."
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


def _plural(a: Advertencia, clave: str, dato: str) -> str:
    """La clave con «.uno» o «.varios» según el entero que traiga el dato de la advertencia."""
    return f"{clave}.{'uno' if a.datos.get(dato) == 1 else 'varios'}"


def _hoja_egm_ausente(_a: Advertencia) -> str:
    return _armar("advertencia.hoja_egm_ausente", hoja=HOJA_EGM)


def _tabla_no_reconocida(a: Advertencia) -> str:
    return _armar("advertencia.tabla_no_reconocida", hoja=HOJA_EGM, frase=a.datos.get("frase", ""))


def _comparacion_incompleta(a: Advertencia) -> str:
    sin_pareja = _como_tupla(a.datos.get("sin_pareja"))
    tabla = a.datos.get("tabla", "")
    faltantes = a.datos.get("faltantes", "")
    if sin_pareja:
        return _armar(
            "advertencia.comparacion_incompleta.sin_pareja",
            tabla=tabla,
            hoja=HOJA_EGM,
            faltantes=faltantes,
            nombres=_citar(sin_pareja),
        )
    clave = _plural(a, "advertencia.comparacion_incompleta.sin_numero", "faltantes")
    return _armar(clave, tabla=tabla, hoja=HOJA_EGM, faltantes=faltantes)


def _tabla_difiere(a: Advertencia) -> str:
    return _armar(
        _plural(a, "advertencia.tabla_difiere", "celdas"),
        tabla=a.datos.get("tabla", ""),
        hoja=HOJA_EGM,
        celdas=a.datos.get("celdas", ""),
    )


def _hoja_abarca_menos_filas(a: Advertencia) -> str:
    return _armar(
        "advertencia.hoja_abarca_menos_filas",
        hoja=HOJA_EGM,
        desde=a.datos.get("desde", ""),
        hasta=a.datos.get("hasta", ""),
        leida=a.datos.get("leida", ""),
    )


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
        HOJA_EGM_AUSENTE: _hoja_egm_ausente,
        TABLA_NO_RECONOCIDA: _tabla_no_reconocida,
        COMPARACION_INCOMPLETA: _comparacion_incompleta,
        TABLA_DIFIERE: _tabla_difiere,
        HOJA_ABARCA_MENOS_FILAS: _hoja_abarca_menos_filas,
    }
)
"""Cuerpo del texto de cada advertencia, por código: las de lectura y las de verificación."""


def advertencia(a: Advertencia) -> str:
    """Texto legible de una advertencia (FR-001-12, SC-001-04).

    Las de fila empiezan por «N.º <n>, columna «…», valor «…»: » (o «Fila <n>» si el N.º está
    vacío); el valor se muestra sin los espacios de los extremos y sin corregir. Las de estructura
    nombran la hoja, la columna o el valor; las de verificación, la hoja y la tabla. Un código
    desconocido es un error de programación y levanta `KeyError`.
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


# --------------------------------------------------------------------------------------------
# Carga de la matriz (historia 4, flujos.md §2 y §3)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TextoMensaje:
    """Un mensaje de carga: el título y sus párrafos por separado (E2, E3, E10 y E4)."""

    titulo: str
    parrafos: tuple[str, ...]


def fijo(clave: str) -> str:
    """Un texto fijo del catálogo, sin datos (por ejemplo, `mensaje.volver` o `colofon.*`)."""
    return CATALOGO[clave]


def cabecera_corrida(ident: Identificacion, n_documentos: int) -> str:
    """«Matriz: <nombre tal como llegó>, leída el <fecha>, <n> documentos» (NFR-000-12).

    El nombre se escribe tal como llegó; nunca se deduce una versión. El plural es el del texto
    fijado en NFR-000-12.
    """
    return _armar(
        "cabecera.corte",
        nombre=ident.nombre_archivo,
        fecha=fecha(ident.fecha_lectura),
        n=n_documentos,
    )


def aviso_inactividad(minutos: int) -> str:
    """E7: «Su sesión se cerrará en <minutos> minutos por falta de actividad…» (flujos.md §2)."""
    return _armar("sesion.e7.aviso", minutos=minutos)


def rotulo_advertencias(n: int) -> str:
    """«1 advertencia de lectura» o «<n> advertencias de lectura» (desplegable de V2)."""
    if n == 1:
        return CATALOGO["avisos.advertencias.una"]
    return _armar("avisos.advertencias.varias", n=n)


def mensaje_rechazo(r: Rechazo, matriz_previa: str | None = None) -> TextoMensaje:
    """E2, E3 o E10 con título y párrafos por separado (flujos.md §2).

    El título es «No se pudo cargar el archivo» y el cuerpo es el texto de `rechazo()` sin ese
    título. Con `matriz_previa` (la cabecera corrida de la matriz que sigue abierta) agrega el
    párrafo «La matriz que tenía cargada sigue disponible con sus resultados: …». Nunca trae el
    nombre del archivo rechazado.
    """
    titulo = CATALOGO["mensaje.rechazo.titulo"]
    cuerpo = rechazo(r).removeprefix(f"{titulo}. ")
    parrafos = [cuerpo]
    if matriz_previa is not None:
        parrafos.append(_armar("mensaje.sigue_disponible", cabecera=matriz_previa))
    return TextoMensaje(titulo, tuple(parrafos))


def mensaje_error_contrato(f: FalloContrato, sesion_terminada: bool) -> TextoMensaje:
    """E4 con título y párrafos por separado (flujos.md §2).

    Párrafos: lo esperado y lo encontrado de cada error; el cierre («No se muestra ninguna cifra.
    Revise …»); y, si `sesion_terminada` (había una matriz cargada), «La herramienta borró todo…».
    Nunca trae el nombre del archivo ni filas de datos (FR-001-29).
    """
    frases = " ".join(_frase_de_error(e) for e in f.errores)
    parrafos = [frases, CATALOGO["error.cierre"]]
    if sesion_terminada:
        parrafos.append(CATALOGO["mensaje.e4.borro_todo"])
    clave = "mensaje.e4.titulo.previa" if sesion_terminada else "mensaje.e4.titulo"
    return TextoMensaje(CATALOGO[clave], tuple(parrafos))


# --------------------------------------------------------------------------------------------
# Resultado de la verificación (historia 3, F-001-3)
# --------------------------------------------------------------------------------------------

_MAXIMO_DE_CELDAS: Final = 10
"""Cuántas celdas nombra el texto de una tabla que difiere; las demás se cuentan."""


@dataclass(frozen=True, slots=True)
class TextoVerificacion:
    """El texto de F-001-3: el resultado y el mensaje completo para el equipo."""

    resultado: Literal["coincide", "difiere", "no verificable"]
    mensaje: str


def _unir(piezas: Sequence[str]) -> str:
    """«A», «A y B» o «A, B y C»."""
    if len(piezas) <= 1:
        return "".join(piezas)
    return f"{', '.join(piezas[:-1])} y {piezas[-1]}"


def _celdas_de(diferencias: Sequence[Diferencia]) -> str:
    """Las celdas como «Fila» con «Columna»; pasadas las diez, el resto solo se cuenta."""
    piezas = [
        _armar("verificacion.celda", fila=d.celda[0], columna=d.celda[1]) for d in diferencias
    ]
    if len(piezas) <= _MAXIMO_DE_CELDAS:
        return _unir(piezas)
    return _armar(
        "verificacion.mas_celdas",
        celdas=", ".join(piezas[:_MAXIMO_DE_CELDAS]),
        cuantas=len(piezas) - _MAXIMO_DE_CELDAS,
    )


def _referencia(ref: RefFila) -> str:
    if ref.numero is None:
        return _armar("verificacion.referencia.fila", fila=ref.fila)
    return _armar("verificacion.referencia.numero", numero=ref.numero)


def _sujeto(filas: Sequence[RefFila]) -> str:
    """«el N.º 6», «el documento de la fila 7» o «los documentos N.º 6 y N.º 9»."""
    if len(filas) == 1:
        (ref,) = filas
        if ref.numero is None:
            return _armar("verificacion.sujeto.fila", fila=ref.fila)
        return _armar("verificacion.sujeto.numero", numero=ref.numero)
    return _armar("verificacion.sujeto.varios", filas=_unir([_referencia(r) for r in filas]))


def _frase_de_causa(tabla: ResultadoTabla, causa: CausaDiferencia) -> str | None:
    """«Causa conocida: …» con las filas de todas las celdas de la tabla que tienen esa causa."""
    por_fila = {
        ref.fila: ref for d in tabla.diferencias if d.explicacion is causa for ref in d.filas
    }
    if not por_fila:
        return None
    filas = [por_fila[fila] for fila in sorted(por_fila)]
    numero = "una" if len(filas) == 1 else "varias"
    return _armar(f"verificacion.causa.{causa.value}.{numero}", sujeto=_sujeto(filas))


def _frases_de_tabla(tabla: ResultadoTabla) -> list[str]:
    """«Los conteos difieren…», cada causa conocida y, si queda alguna, las celdas sin causa."""
    frases = [
        _armar("verificacion.difiere", tabla=tabla.numero, celdas=_celdas_de(tabla.diferencias))
    ]
    for causa in CausaDiferencia:
        frase = _frase_de_causa(tabla, causa)
        if frase is not None:
            frases.append(frase)
    sin_causa = [d for d in tabla.diferencias if d.explicacion is None]
    if sin_causa:
        frases.append(_armar("verificacion.sin_causa", celdas=_celdas_de(sin_causa)))
    return frases


def _sin_numeros_guardados(v: Verificacion) -> bool:
    """Toda tabla que quedó a medias no trae ningún número ni nombre sin pareja."""
    incompletas = [a for a in v.advertencias if a.codigo == COMPARACION_INCOMPLETA]
    return bool(incompletas) and all(
        a.datos.get("comparadas") == 0 and not a.datos.get("sin_pareja") for a in incompletas
    )


def _clave_de_no_verificable(v: Verificacion) -> str:
    """Por qué no se pudo contrastar nada: hoja ausente, tablas sin reconocer, sin números..."""
    if any(a.codigo == HOJA_EGM_AUSENTE for a in v.advertencias):
        return "verificacion.no_verificable.sin_hoja"
    if all(t.numero is None for t in v.tablas):
        return "verificacion.no_verificable.sin_tablas"
    if _sin_numeros_guardados(v):
        return "verificacion.no_verificable.sin_valores"
    return "verificacion.no_verificable.incompleta"


def verificacion(v: Verificacion) -> TextoVerificacion:
    """El texto de F-001-3 para el resultado de la verificación (FR-001-18, FR-001-25).

    - Coincide: «Los conteos coinciden con la hoja EGM del archivo. Tablas verificadas: 1, 2 y 4.»
    - Difiere: «Los conteos difieren de la hoja EGM en la tabla <n>: <celdas>. Causa conocida: …»,
      con la causa de cada celda cuando se conoce.
    - No verificable: «No se pudieron contrastar los conteos con la hoja EGM del archivo, porque …»,
      sin lista de tablas verificadas.

    Solo nombra las tablas comparables, por el número de su título; nunca otra tabla de la hoja.
    """
    difieren = [t for t in v.tablas if t.estado is EstadoTabla.DIFIERE]
    partes: list[str] = []
    if difieren:
        resultado: Literal["coincide", "difiere", "no verificable"] = "difiere"
        for tabla in difieren:
            partes.extend(_frases_de_tabla(tabla))
    elif v.verificadas:
        resultado = "coincide"
        partes.append(CATALOGO["verificacion.coincide"])
    else:
        return TextoVerificacion("no verificable", CATALOGO[_clave_de_no_verificable(v)])
    partes.append(
        _armar("verificacion.tablas_verificadas", tablas=_unir([str(n) for n in v.verificadas]))
    )
    if any(t.estado is EstadoTabla.NO_VERIFICABLE for t in v.tablas):
        partes.append(CATALOGO["verificacion.parcial"])
    return TextoVerificacion(resultado, " ".join(partes))
