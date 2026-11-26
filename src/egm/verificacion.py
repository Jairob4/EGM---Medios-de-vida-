"""M08 `egm.verificacion`: verificación cruzada con la hoja `EGM` (arquitectura §6.1, M08; ADR-002).

Compara los conteos de la herramienta con los valores que la hoja `EGM` del archivo trae guardados,
solo en las tres tablas comparables del contrato §7: total de estudios (tabla 1), evaluación de
impacto (tabla 2) y nivel de evidencia (tabla 4), identificadas por el número y la frase de su
título. La herramienta **no recalcula** fórmulas (ADR-002, opción A): un valor sin número guardado
es un valor ausente y nunca vale 0. La tabla 3 de la hoja no es comparable: este módulo no la
localiza, no la lee y no produce advertencias sobre ella (ADR-002, punto 6).

Localización (T-001-43): cada tabla se ubica por la celda cuyo texto empieza por un número seguido
de punto y contiene su frase (contrato §7.2; ninguna o más de una ⇒ no reconocida); su alcance va
de la fila de encabezados al primer nombre vacío o numerado (§7.7); y sus filas y columnas se
emparejan por nombre dentro de ese alcance, con «Total estudios» incluida (§7.8). Nada depende de
coordenadas fijas.

Comparación (T-001-44): cada valor numérico guardado se compara con el conteo de la herramienta
sobre las filas que abarcan las fórmulas de esa celda (ADR-002, punto 2); el resultado de la tabla
sale de $D_k$ y $V_k$ (contrato §7.9) y la lista de «tablas verificadas» reúne las que quedaron en
«coincide» o «difiere». Las advertencias de verificación tienen códigos propios, definidos aquí:
no forman parte de la lista cerrada de `egm.modelo`, y `egm.textos` los redacta.

Explicación (T-001-45): una diferencia se explica, en este orden y de forma acumulativa (ADR-002,
punto 3), si el valor de la hoja es igual a la semántica de la hoja con $G_r = H_r$ (variante
estándar de M07), contando además el texto «1», o sin quitar los espacios en los extremos. La
`Diferencia` guarda la causa que cerró la diferencia y las filas que la producen.

Reglas del núcleo (arquitectura §4.1): importa `egm.conteo`, `egm.esquema`, `egm.libro` y
`egm.modelo`; no importa la biblioteca de lectura de libros ni la capa web; no abre archivos ni
procesos externos (NFR-000-17); sin estado global.
"""

import math
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, Literal

from egm import conteo, modelo
from egm.conteo import ConteosHoja, VarianteHoja
from egm.esquema import HOJA_MATRIZ
from egm.libro import Hoja, Libro, Valor
from egm.modelo import Advertencia, Conteo, Corpus, Documento, Esquema, RefFila

__all__ = [
    "CODIGOS_ADVERTENCIA_VERIFICACION",
    "COMPARACION_INCOMPLETA",
    "ENCABEZADO_TOTAL",
    "FRASES_DE_TITULO",
    "HOJA_ABARCA_MENOS_FILAS",
    "HOJA_EGM",
    "HOJA_EGM_AUSENTE",
    "TABLA_DIFIERE",
    "TABLA_NO_RECONOCIDA",
    "TIPOS",
    "CausaDiferencia",
    "Diferencia",
    "EstadoTabla",
    "ResultadoTabla",
    "TipoTabla",
    "Verificacion",
    "verificar",
]

type TipoTabla = Literal["total", "evaluacion_impacto", "nivel"]
"""Las tres tablas comparables de la hoja `EGM` (contrato §7.2)."""

type Clave = tuple[str, str | None]
"""Una celda comparable: (fila de la tabla, dimensión), o `None` si es «Total estudios» o el valor
único de la tabla por nivel."""

HOJA_EGM: Final = "EGM"
"""Nombre de la hoja de verificación (contrato §2)."""

ENCABEZADO_TOTAL: Final = "Total estudios"
"""Encabezado de la columna que se compara con $u$ o $u^{IE}$ (contrato §7.8)."""

TIPOS: Final[tuple[TipoTabla, ...]] = ("total", "evaluacion_impacto", "nivel")
"""Las tablas comparables, en el orden del contrato §7.2."""

FRASES_DE_TITULO: Final[Mapping[TipoTabla, str]] = {
    "total": "Número total de estudios",
    "evaluacion_impacto": "Evaluación de impacto",
    "nivel": "nivel de evidencia",
}
"""Frase propia del título de cada tabla comparable (contrato §7.2)."""

# Advertencias de verificación (ámbitos «hoja» y «tabla»). Códigos propios de M08; los redacta M10.
HOJA_EGM_AUSENTE: Final = "hoja_egm_ausente"
TABLA_NO_RECONOCIDA: Final = "tabla_no_reconocida"
COMPARACION_INCOMPLETA: Final = "comparacion_incompleta"
TABLA_DIFIERE: Final = "tabla_difiere"
HOJA_ABARCA_MENOS_FILAS: Final = "hoja_abarca_menos_filas"

CODIGOS_ADVERTENCIA_VERIFICACION: Final = (
    HOJA_EGM_AUSENTE,
    TABLA_NO_RECONOCIDA,
    COMPARACION_INCOMPLETA,
    TABLA_DIFIERE,
    HOJA_ABARCA_MENOS_FILAS,
)
"""Códigos de las advertencias que emite M08, en el orden en que se definen."""

_AMBITO_HOJA: Final = "hoja"
_AMBITO_TABLA: Final = "tabla"

_ULTIMA_FILA_DE_LA_HOJA: Final = 1_048_576
"""Última fila de una hoja `.xlsx`: tope de un rango de columna completa (`$D:$D`)."""

_TITULO: Final = re.compile(r"^\s*(\d+)\.(.*)$", re.DOTALL)
"""Título de una tabla: un número seguido de punto y el resto del texto (contrato §7.2)."""

_NUMERADO: Final = re.compile(r"^\s*\d+\.")
"""Una celda que empieza por un número seguido de punto cierra el cuerpo de una tabla (§7.7)."""

_REFERENCIA: Final = re.compile(
    r"(?P<hoja>'(?:[^']|'')+'|[\w.]+)!"
    r"\$?[A-Za-z]{1,3}\$?(?P<inicio>\d+)?"
    r"(?P<fin>:\$?[A-Za-z]{1,3}\$?(?P<final>\d+)?)?"
)
"""Rango de una fórmula con su hoja: `'Hoja'!$D$2:$D$200`, `Hoja!L$2:L$200`, `Hoja!$D:$D`."""


# --------------------------------------------------------------------------------------------
# Tipos de M08
# --------------------------------------------------------------------------------------------


class EstadoTabla(Enum):
    """Resultado de una tabla comparable (contrato §7.9)."""

    COINCIDE = auto()
    DIFIERE = auto()
    NO_VERIFICABLE = auto()


class CausaDiferencia(Enum):
    """Causa conocida de una diferencia con la hoja (contrato §7.4; ADR-002, punto 3).

    El valor de cada causa es el código de la advertencia de lectura que señala esas mismas filas.
    """

    PRINCIPAL_IGUAL_SECUNDARIA = modelo.PRINCIPAL_IGUAL_SECUNDARIA
    """La fila tiene la misma intervención como principal y como secundaria: la hoja la cuenta dos
    veces y la herramienta, una."""
    DIMENSION_VALOR_INVALIDO = modelo.DIMENSION_VALOR_INVALIDO
    """La fila trae una dimensión escrita como texto «1»: la hoja la cuenta y la herramienta no."""
    ESPACIOS_EN_LOS_EXTREMOS = modelo.ESPACIOS_EN_LOS_EXTREMOS
    """La fila trae espacios en los extremos de un valor: la hoja no lo reconoce y la herramienta
    sí."""


@dataclass(frozen=True, slots=True)
class Diferencia:
    """Un valor de la hoja distinto del conteo de la herramienta."""

    celda: tuple[str, str]
    """(nombre de la fila, nombre de la columna) tal como están en la tabla de la hoja."""
    valor_hoja: int | float
    """El número que la hoja trae guardado."""
    conteo: Conteo
    """El conteo de la herramienta sobre las mismas filas, con las filas que lo producen."""
    explicacion: CausaDiferencia | None
    """La causa conocida; `None` si la diferencia no se pudo explicar."""
    filas: tuple[RefFila, ...]
    """Las filas de la matriz que producen esa causa en esta celda; vacío si no hay causa."""


@dataclass(frozen=True, slots=True)
class ResultadoTabla:
    """El resultado de una tabla comparable."""

    numero: int | None
    """Número inicial del título; `None` si la tabla no se reconoció."""
    tipo: TipoTabla
    estado: EstadoTabla
    diferencias: tuple[Diferencia, ...]
    sin_pareja: tuple[str, ...]
    """Nombres sin pareja (categorías de la matriz que la tabla no trae y filas o columnas de la
    tabla que no son categoría, o que se repiten)."""
    faltantes: int
    """Cuántas de las comparaciones que la tabla debía permitir no se hicieron ($|D_k| - |V_k|$);
    un valor que falta nunca se toma como 0."""


@dataclass(frozen=True, slots=True)
class Verificacion:
    """La verificación cruzada completa."""

    tablas: tuple[ResultadoTabla, ...]
    """Las tres tablas comparables, siempre en el orden: total, evaluación de impacto y nivel."""
    verificadas: tuple[int, ...]
    """Números de título de las tablas que quedaron en «coincide» o «difiere» (FR-001-25)."""
    advertencias: tuple[Advertencia, ...]


# --------------------------------------------------------------------------------------------
# Ayudas de lectura de la hoja
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Titulo:
    fila: int
    columna: int
    numero: int


def _normal(texto: str) -> str:
    """El texto en una forma comparable: sin distinguir mayúsculas ni la composición de tildes."""
    return unicodedata.normalize("NFC", texto).casefold()


def _con_contenido(valor: Valor) -> bool:
    return valor is not None and not (isinstance(valor, str) and not valor.strip())


def _nombre(valor: Valor) -> str:
    """El nombre de una fila o columna: el texto de la celda sin espacios en los extremos."""
    return str(valor).strip()


def _numero(valor: Valor) -> int | float | None:
    """El valor guardado si es un número; todo lo demás (texto, error, vacío) es un ausente."""
    if isinstance(valor, bool) or not isinstance(valor, int | float):
        return None
    if isinstance(valor, float):
        if not math.isfinite(valor):
            return None
        if valor.is_integer():
            return int(valor)
    return valor


def _titulos(hoja: Hoja, ultima_fila: int, ultima_columna: int) -> dict[TipoTabla, list[_Titulo]]:
    """Las celdas que cumplen el título de cada tabla comparable (contrato §7.2).

    Solo se miran las tres frases comparables: ninguna otra tabla de la hoja se localiza.
    """
    frases = {tipo: _normal(frase) for tipo, frase in FRASES_DE_TITULO.items()}
    encontradas: dict[TipoTabla, list[_Titulo]] = {tipo: [] for tipo in TIPOS}
    for fila in range(1, ultima_fila + 1):
        for columna in range(1, ultima_columna + 1):
            valor = hoja.celda(fila, columna).valor
            if not isinstance(valor, str):
                continue
            titulo = _TITULO.match(valor)
            if titulo is None:
                continue
            resto = _normal(titulo.group(2))
            for tipo, frase in frases.items():
                if frase in resto:
                    encontradas[tipo].append(_Titulo(fila, columna, int(titulo.group(1))))
    return encontradas


def _filas_de_la_formula(formula: str | None, ultima_leida: int) -> tuple[int, int]:
    """Las filas de la matriz que abarca una celda de la hoja (ADR-002, punto 2).

    Con fórmula: la intersección de los rangos que remiten a la hoja de la matriz. Sin fórmula (un
    número escrito), o con una fórmula que no remite a ella: todas las filas leídas.
    """
    desde, hasta = 1, _ULTIMA_FILA_DE_LA_HOJA
    remite = False
    for referencia in _REFERENCIA.finditer(formula or ""):
        nombre = referencia["hoja"]
        if nombre.startswith("'"):
            nombre = nombre[1:-1].replace("''", "'")
        if nombre != HOJA_MATRIZ:
            continue
        remite = True
        inicio = int(referencia["inicio"]) if referencia["inicio"] else None
        if referencia["fin"] is None:
            primera, ultima = (1, _ULTIMA_FILA_DE_LA_HOJA) if inicio is None else (inicio, inicio)
        else:
            final = int(referencia["final"]) if referencia["final"] else _ULTIMA_FILA_DE_LA_HOJA
            primera, ultima = inicio or 1, final
        desde, hasta = max(desde, primera), min(hasta, ultima)
    if not remite:
        return 2, ultima_leida
    return desde, hasta


# --------------------------------------------------------------------------------------------
# Conteos de la herramienta y de la hoja, sobre un rango de filas
# --------------------------------------------------------------------------------------------


def _mapa_de_la_hoja(tipo: TipoTabla, hoja: ConteosHoja) -> dict[Clave, int]:
    """Los conteos de la semántica de la hoja que corresponden a una tabla, por celda."""
    if tipo == "nivel":
        return {(nivel, None): valor for nivel, valor in hoja.t4.items()}
    cuerpo, total = (hoja.t1, hoja.t) if tipo == "total" else (hoja.t2, hoja.t_ie)
    celdas: dict[Clave, int] = {(i, j): v for (i, j), v in (cuerpo or {}).items()}
    celdas.update({(i, None): valor for i, valor in (total or {}).items()})
    return celdas


class _Calculos:
    """Los conteos que se comparan, calculados una vez por rango de filas."""

    def __init__(self, esquema: Esquema, corpus: Corpus) -> None:
        self._esquema = esquema
        self._corpus = corpus
        self._de_la_herramienta: dict[tuple[TipoTabla, int, int], Mapping[Clave, Conteo]] = {}
        self._de_la_hoja: dict[tuple[TipoTabla, int, int, VarianteHoja], Mapping[Clave, int]] = {}
        self._de_un_documento: dict[tuple[TipoTabla, int, VarianteHoja], Mapping[Clave, int]] = {}

    def herramienta(self, tipo: TipoTabla, filas: range) -> Mapping[Clave, Conteo]:
        """$S$ y $u$, $S^{IE}$ y $u^{IE}$ o $T_4$ de la herramienta sobre esas filas."""
        llave = (tipo, filas.start, filas.stop)
        if llave not in self._de_la_herramienta:
            acotado = Corpus(
                documentos=tuple(d for d in self._corpus.documentos if d.ref.fila in filas),
                advertencias=self._corpus.advertencias,
                fila_final_leida=self._corpus.fila_final_leida,
            )
            self._de_la_herramienta[llave] = self._calcular(tipo, acotado)
        return self._de_la_herramienta[llave]

    def _calcular(self, tipo: TipoTabla, corpus: Corpus) -> Mapping[Clave, Conteo]:
        esquema = self._esquema
        if tipo == "nivel":
            return {(n, None): c for n, c in conteo.por_nivel(esquema, corpus).items()}
        if tipo == "total":
            cuerpo = {k: c.conteo for k, c in conteo.mapa(esquema, corpus).celdas.items()}
            por_i = conteo.por_intervencion(esquema, corpus)
        else:
            cuerpo = dict(conteo.evaluacion_impacto(esquema, corpus) or {})
            por_i = conteo.por_intervencion(esquema, corpus, solo_ie=True)
        celdas: dict[Clave, Conteo] = {(i, j): c for (i, j), c in cuerpo.items()}
        celdas.update({(i, None): c for i, c in por_i.items()})
        return celdas

    def hoja(self, tipo: TipoTabla, filas: range, variante: VarianteHoja) -> Mapping[Clave, int]:
        """La semántica de la hoja sobre esas filas, con esa variante."""
        llave = (tipo, filas.start, filas.stop, variante)
        if llave not in self._de_la_hoja:
            hoja = conteo.semantica_hoja(self._esquema, self._corpus, filas, variante)
            self._de_la_hoja[llave] = _mapa_de_la_hoja(tipo, hoja)
        return self._de_la_hoja[llave]

    def de_un_documento(
        self, tipo: TipoTabla, documento: Documento, variante: VarianteHoja
    ) -> Mapping[Clave, int]:
        """Lo que la hoja cuenta de ese solo documento con esa variante."""
        llave = (tipo, documento.ref.fila, variante)
        if llave not in self._de_un_documento:
            solo = Corpus((documento,), self._corpus.advertencias, documento.ref.fila)
            fila = documento.ref.fila
            hoja = conteo.semantica_hoja(self._esquema, solo, range(fila, fila + 1), variante)
            self._de_un_documento[llave] = _mapa_de_la_hoja(tipo, hoja)
        return self._de_un_documento[llave]

    def filas_que_explican(
        self,
        tipo: TipoTabla,
        clave: Clave,
        filas: range,
        causa: CausaDiferencia,
        variante: VarianteHoja,
        anterior: VarianteHoja | None,
    ) -> tuple[RefFila, ...]:
        """Los documentos del rango cuya lectura con `variante` cambia esa celda respecto de la
        variante anterior (o, para la primera causa, respecto de contarla una sola vez)."""
        refs: list[RefFila] = []
        for documento in self._corpus.documentos:
            if documento.ref.fila not in filas or not _tiene(documento, causa):
                continue
            con_causa = self.de_un_documento(tipo, documento, variante)[clave]
            sin_causa = (
                min(1, con_causa)
                if anterior is None
                else self.de_un_documento(tipo, documento, anterior)[clave]
            )
            if con_causa != sin_causa:
                refs.append(documento.ref)
        return tuple(refs)


_ESCALA: Final = (
    (CausaDiferencia.PRINCIPAL_IGUAL_SECUNDARIA, VarianteHoja.ESTANDAR, None),
    (
        CausaDiferencia.DIMENSION_VALOR_INVALIDO,
        VarianteHoja.TEXTO_1_COMO_MARCA,
        VarianteHoja.ESTANDAR,
    ),
    (
        CausaDiferencia.ESPACIOS_EN_LOS_EXTREMOS,
        VarianteHoja.SIN_QUITAR_ESPACIOS,
        VarianteHoja.TEXTO_1_COMO_MARCA,
    ),
)
"""Causas en el orden de ADR-002, punto 3: la variante de la hoja que la explica y la anterior."""


def _tiene(documento: Documento, causa: CausaDiferencia) -> bool:
    """El documento trae la particularidad de esa causa."""
    crudos = documento.crudos
    if causa is CausaDiferencia.PRINCIPAL_IGUAL_SECUNDARIA:
        return crudos.principal_igual_secundaria
    if causa is CausaDiferencia.DIMENSION_VALOR_INVALIDO:
        return bool(crudos.dimensiones_como_texto)
    return bool(crudos.con_espacios)


def _explicar(
    calculos: _Calculos, tipo: TipoTabla, clave: Clave, valor: int | float, filas: range
) -> tuple[CausaDiferencia | None, tuple[RefFila, ...]]:
    """La primera causa, en el orden de ADR-002, cuya variante de la hoja da el valor guardado."""
    for causa, variante, anterior in _ESCALA:
        if calculos.hoja(tipo, filas, variante)[clave] == valor:
            return causa, calculos.filas_que_explican(tipo, clave, filas, causa, variante, anterior)
    return None, ()


# --------------------------------------------------------------------------------------------
# Una tabla comparable
# --------------------------------------------------------------------------------------------


def _unicos(nombres: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(nombres))


def _emparejar(
    categorias: Sequence[str], observados: Sequence[tuple[int, str]]
) -> tuple[dict[str, int], list[str]]:
    """Empareja por nombre exacto: categoría → posición en la hoja, y los nombres que sobran.

    Un nombre repetido dentro del alcance no se empareja (contrato §7.8).
    """
    veces = {nombre: 0 for _, nombre in observados}
    for _, nombre in observados:
        veces[nombre] += 1
    conocidas = set(categorias)
    emparejadas = {n: pos for pos, n in observados if n in conocidas and veces[n] == 1}
    sobrantes = _unicos([n for _, n in observados if n not in conocidas])
    return emparejadas, sobrantes


@dataclass(frozen=True, slots=True)
class _Alcance:
    """Lo que hay dentro de una tabla: filas del cuerpo y celdas de encabezado, con su posición."""

    cuerpo: tuple[tuple[int, str], ...]
    encabezados: tuple[tuple[int, str], ...]


def _alcance(hoja: Hoja, titulo: _Titulo, ultima_fila: int, ultima_columna: int) -> _Alcance:
    """El alcance de la tabla (contrato §7.7): la columna de nombres es la del título."""
    primera = titulo.columna
    fila_de_encabezados = next(
        (
            fila
            for fila in range(titulo.fila + 1, ultima_fila + 1)
            if any(
                _con_contenido(hoja.celda(fila, c).valor)
                for c in range(primera, ultima_columna + 1)
            )
        ),
        None,
    )
    if fila_de_encabezados is None:
        return _Alcance((), ())
    encabezados = tuple(
        (columna, _nombre(hoja.celda(fila_de_encabezados, columna).valor))
        for columna in range(primera + 1, ultima_columna + 1)
        if _con_contenido(hoja.celda(fila_de_encabezados, columna).valor)
    )
    cuerpo: list[tuple[int, str]] = []
    for fila in range(fila_de_encabezados + 1, ultima_fila + 1):
        valor = hoja.celda(fila, primera).valor
        if not _con_contenido(valor) or (isinstance(valor, str) and _NUMERADO.match(valor)):
            break
        cuerpo.append((fila, _nombre(valor)))
    return _Alcance(tuple(cuerpo), encabezados)


@dataclass(frozen=True, slots=True)
class _Columnas:
    """El emparejamiento de las columnas de una tabla."""

    emparejadas: Mapping[str | None, int]
    """Dimensión (o `None`: «Total estudios» o el valor de la tabla por nivel) → columna."""
    encabezado_de_none: str
    """Texto del encabezado que quedó emparejado con `None`."""
    universo: int
    """Cuántas columnas debía permitir comparar la tabla (categorías y sobrantes)."""
    sin_pareja: tuple[str, ...]


def _columnas_de_dos_ejes(esquema: Esquema, encabezados: Sequence[tuple[int, str]]) -> _Columnas:
    """Columnas de las tablas 1 y 2: las dimensiones y «Total estudios» (contrato §7.8)."""
    dimensiones = set(esquema.dimensiones)
    de_dimension = [(c, n) for c, n in encabezados if n in dimensiones]
    de_total = [(c, n) for c, n in encabezados if n not in dimensiones and _es_total(n)]
    otras = [n for _, n in encabezados if n not in dimensiones and not _es_total(n)]
    emparejadas, _ = _emparejar(esquema.dimensiones, de_dimension)
    columnas: dict[str | None, int] = dict(emparejadas.items())
    sobrantes = _unicos(otras)
    sin_pareja = [d for d in esquema.dimensiones if d not in emparejadas]
    texto_total = ENCABEZADO_TOTAL
    if len(de_total) == 1:
        columnas[None] = de_total[0][0]
        texto_total = de_total[0][1]
    else:
        sin_pareja.append(ENCABEZADO_TOTAL)
    return _Columnas(
        emparejadas=columnas,
        encabezado_de_none=texto_total,
        universo=len(esquema.dimensiones) + 1 + len(sobrantes),
        sin_pareja=tuple(sin_pareja + sobrantes),
    )


def _es_total(nombre: str) -> bool:
    return nombre.casefold() == ENCABEZADO_TOTAL.casefold()


def _columnas_de_nivel(encabezados: Sequence[tuple[int, str]]) -> _Columnas:
    """Columna de la tabla por nivel: la única con encabezado además de la de nombres (§7.8)."""
    if len(encabezados) == 1:
        columna, texto = encabezados[0]
        return _Columnas({None: columna}, texto, 1, ())
    nombres = _unicos([n for _, n in encabezados])
    return _Columnas({}, "", max(1, len(nombres)), tuple(nombres))


def _tabla_no_verificable(tipo: TipoTabla, numero: int | None) -> ResultadoTabla:
    return ResultadoTabla(numero, tipo, EstadoTabla.NO_VERIFICABLE, (), (), 0)


@dataclass(frozen=True, slots=True)
class _Comparacion:
    """Lo que dejó comparar una tabla: resultado, advertencias y filas que abarcan sus fórmulas."""

    resultado: ResultadoTabla
    advertencias: tuple[Advertencia, ...]
    formulas: tuple[tuple[int, int], ...]


def _comparar(
    hoja: Hoja,
    titulo: _Titulo,
    tipo: TipoTabla,
    esquema: Esquema,
    calculos: _Calculos,
    ultima_leida: int,
    limites: tuple[int, int],
) -> _Comparacion:
    """Compara una tabla reconocida con los conteos de la herramienta (contrato §7.9)."""
    ultima_fila, ultima_columna = limites
    alcance = _alcance(hoja, titulo, ultima_fila, ultima_columna)
    categorias = esquema.niveles if tipo == "nivel" else esquema.intervenciones
    filas_emparejadas, filas_sobrantes = _emparejar(categorias, alcance.cuerpo)
    columnas = (
        _columnas_de_nivel(alcance.encabezados)
        if tipo == "nivel"
        else _columnas_de_dos_ejes(esquema, alcance.encabezados)
    )
    orden = (*esquema.dimensiones, None) if tipo != "nivel" else (None,)

    posibles = (len(categorias) + len(filas_sobrantes)) * columnas.universo
    diferencias: list[Diferencia] = []
    formulas: list[tuple[int, int]] = []
    comparadas = 0
    for categoria in categorias:
        if categoria not in filas_emparejadas:
            continue
        for dimension in orden:
            if dimension not in columnas.emparejadas:
                continue
            celda = hoja.celda(filas_emparejadas[categoria], columnas.emparejadas[dimension])
            desde, hasta = _filas_de_la_formula(celda.formula, ultima_leida)
            if celda.formula is not None:
                formulas.append((desde, hasta))
            guardado = _numero(celda.valor_guardado)
            if guardado is None:
                continue
            comparadas += 1
            filas = range(desde, hasta + 1)
            clave: Clave = (categoria, dimension)
            propio = calculos.herramienta(tipo, filas)[clave]
            if guardado != propio.valor:
                causa, explican = _explicar(calculos, tipo, clave, guardado, filas)
                nombre_columna = columnas.encabezado_de_none if dimension is None else dimension
                diferencias.append(
                    Diferencia((categoria, nombre_columna), guardado, propio, causa, explican)
                )

    sin_pareja = _unicos(
        [c for c in categorias if c not in filas_emparejadas]
        + filas_sobrantes
        + list(columnas.sin_pareja)
    )
    faltantes = posibles - comparadas
    if diferencias:
        estado = EstadoTabla.DIFIERE
    elif posibles and comparadas == posibles:
        estado = EstadoTabla.COINCIDE
    else:
        estado = EstadoTabla.NO_VERIFICABLE

    advertencias: list[Advertencia] = []
    if diferencias:
        advertencias.append(
            _advertencia(
                TABLA_DIFIERE,
                _AMBITO_TABLA,
                {"tabla": titulo.numero, "tipo": tipo, "celdas": len(diferencias)},
            )
        )
    if faltantes:
        advertencias.append(
            _advertencia(
                COMPARACION_INCOMPLETA,
                _AMBITO_TABLA,
                {
                    "tabla": titulo.numero,
                    "tipo": tipo,
                    "comparadas": comparadas,
                    "faltantes": faltantes,
                    "sin_pareja": tuple(sin_pareja),
                },
            )
        )
    resultado = ResultadoTabla(
        titulo.numero, tipo, estado, tuple(diferencias), tuple(sin_pareja), faltantes
    )
    return _Comparacion(resultado, tuple(advertencias), tuple(formulas))


def _advertencia(codigo: str, ambito: str, datos: Mapping[str, object]) -> Advertencia:
    return Advertencia(codigo, ambito, None, None, None, datos)


# --------------------------------------------------------------------------------------------
# Verificación
# --------------------------------------------------------------------------------------------


def _advertencia_de_filas(
    formulas: Sequence[tuple[int, int]], ultima_leida: int
) -> Advertencia | None:
    """La hoja abarca menos filas que las leídas (US-001-1.5; ADR-002, punto 2)."""
    if ultima_leida < 2 or not formulas:
        return None
    desde = max(d for d, _ in formulas)
    hasta = min(h for _, h in formulas)
    if desde <= 2 and hasta >= ultima_leida:
        return None
    return _advertencia(
        HOJA_ABARCA_MENOS_FILAS,
        _AMBITO_HOJA,
        {"desde": desde, "hasta": hasta, "leida": ultima_leida},
    )


def verificar(libro: Libro, esquema: Esquema, corpus: Corpus) -> Verificacion:
    """Contrasta los conteos con las tablas comparables de la hoja `EGM` (FR-001-14 a 18).

    Siempre devuelve las tres tablas, en el orden total, evaluación de impacto y nivel. Cada una
    queda «coincide» (se compararon todos los valores esperados y ninguno difiere), «difiere»
    (algún valor guardado es distinto del conteo) o «no verificable» (hoja ausente, tabla no
    reconocida, falta el ancla de evaluación de impacto, valores sin número guardado o categorías
    sin pareja). Nunca es un error de contrato, nunca toma un valor ausente por 0 y nunca toca la
    tabla 3 de la hoja.
    """
    hoja = libro.hoja(HOJA_EGM)
    if hoja is None:
        return Verificacion(
            tablas=tuple(_tabla_no_verificable(tipo, None) for tipo in TIPOS),
            verificadas=(),
            advertencias=(_advertencia(HOJA_EGM_AUSENTE, _AMBITO_HOJA, {"hoja": HOJA_EGM}),),
        )

    limites = hoja.dimension()
    titulos = _titulos(hoja, *limites)
    calculos = _Calculos(esquema, corpus)
    ultima_leida = corpus.fila_final_leida
    resultados: list[ResultadoTabla] = []
    avisos: list[Advertencia] = []
    formulas: list[tuple[int, int]] = []
    for tipo in TIPOS:
        reconocidos = titulos[tipo]
        if len(reconocidos) != 1:
            resultados.append(_tabla_no_verificable(tipo, None))
            avisos.append(
                _advertencia(
                    TABLA_NO_RECONOCIDA,
                    _AMBITO_TABLA,
                    {"tipo": tipo, "frase": FRASES_DE_TITULO[tipo], "titulos": len(reconocidos)},
                )
            )
            continue
        titulo = reconocidos[0]
        if tipo == "evaluacion_impacto" and esquema.anclas.evaluacion_impacto is None:
            resultados.append(_tabla_no_verificable(tipo, titulo.numero))  # contrato §7.9, cierre
            continue
        comparacion = _comparar(hoja, titulo, tipo, esquema, calculos, ultima_leida, limites)
        resultados.append(comparacion.resultado)
        avisos.extend(comparacion.advertencias)
        formulas.extend(comparacion.formulas)

    abarca = _advertencia_de_filas(formulas, ultima_leida)
    verificadas = sorted(
        {
            t.numero
            for t in resultados
            if t.numero is not None and t.estado is not EstadoTabla.NO_VERIFICABLE
        }
    )
    return Verificacion(
        tablas=tuple(resultados),
        verificadas=tuple(verificadas),
        advertencias=(*((abarca,) if abarca else ()), *avisos),
    )
