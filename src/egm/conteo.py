"""M07 `egm.conteo`: conjuntos y conteos del contrato §5 (arquitectura §6.1, M07).

Parte del plan 001 (T-001-25): `conjuntos` ($R$, $E$, $M$, $P$), `mapa` ($S$, $n$ y $N$),
`evaluacion_impacto` ($S^{IE}$), `por_intervencion` ($u$, $u^{IE}$), `por_nivel` ($T_4$) y
`semantica_hoja` ($T_1$, $T_2$, $t$, $t^{IE}$ de la hoja `EGM`, solo para la verificación). El
parámetro `filtro` y el desglose por nivel de cada celda llegan con el plan 002; las
coocurrencias, con el 003.

Reglas (NFR-000-02, FR-001-11): todo número que muestra la herramienta es un `Conteo` armado con
las filas que lo producen, en el orden del archivo y sin repetidos, y siempre cuenta **estudios
distintos** (ADR-001). $n$ y $N$ son el número de estudios del mapa, nunca la suma de las celdas:
un estudio con dos intervenciones y dos dimensiones aparece en cuatro celdas y cuenta una vez. La
única excepción son $T_1$, $T_2$, $t$ y $t^{IE}$, que reproducen la semántica de la hoja (cuenta
dos veces una fila con $G_r = H_r$) y por eso son enteros: nunca se muestran, solo se comparan.

Las categorías, las dimensiones y los valores ancla salen del `Esquema` y de los documentos que
leyó M05; este módulo no escribe ningún nombre de categoría. Los conjuntos se derivan del estado de
cada documento (contrato §4): $E$ son los estados «En el mapa» y «Empírico pendiente», $M$ el
primero y $P$ el segundo.

Reglas del núcleo (arquitectura §4.1): importa solo `egm.modelo`; no importa la biblioteca de
lectura de libros ni la capa web; sin entrada ni salida y sin estado global.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum, auto
from types import MappingProxyType

from egm.modelo import Conteo, Corpus, Documento, Esquema, EstadoDocumento, RefFila

__all__ = [
    "Celda",
    "Conjuntos",
    "ConteosHoja",
    "Mapa",
    "VarianteHoja",
    "conjuntos",
    "evaluacion_impacto",
    "mapa",
    "por_intervencion",
    "por_nivel",
    "semantica_hoja",
]

type Clave = tuple[str, str]
"""Una celda del mapa: (intervención, dimensión)."""


# --------------------------------------------------------------------------------------------
# Tipos de M07
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Conjuntos:
    """Los conjuntos del contrato §5, cada uno con las filas que lo forman."""

    r: Conteo
    """$R$: todas las filas no vacías (documentos)."""
    e: Conteo
    """$E$: estudios empíricos registrados."""
    m: Conteo
    """$M$: estudios empíricos con intervención y al menos una dimensión en 1."""
    p: Conteo
    """$P = E \\setminus M$: estudios empíricos que aún no entran al mapa."""


@dataclass(frozen=True, slots=True)
class Celda:
    """Una celda del mapa: $S(i, j)$ con los estudios distintos que la producen (FR-001-11)."""

    conteo: Conteo


@dataclass(frozen=True, slots=True)
class Mapa:
    """El mapa de evidencias: una celda por cada intervención y dimensión del esquema."""

    intervenciones: tuple[str, ...]
    """Filas del mapa, en el orden del archivo."""
    dimensiones: tuple[str, ...]
    """Columnas del mapa, en el orden del archivo."""
    celdas: Mapping[Clave, Celda] = field(hash=False)
    """Todas las combinaciones (intervención, dimensión), también las que valen 0."""
    estudios: Conteo
    """$n = |M|$ sin filtro: estudios distintos del mapa."""
    total: Conteo
    """$N = |M|$: total sin filtrar de estudios del mapa."""

    def __post_init__(self) -> None:
        object.__setattr__(self, "celdas", MappingProxyType(dict(self.celdas)))


class VarianteHoja(Enum):
    """Cómo se lee una fila para reproducir la semántica de la hoja `EGM`.

    El plan 001 (T-001-25) solo trae la variante estándar, la que lee como la herramienta: solo
    el 1 numérico marca una dimensión y los valores van sin espacios en los extremos. T-001-45
    agrega las variantes «texto 1 como marca» y «sin quitar espacios» (ADR-002, punto 3).
    """

    ESTANDAR = auto()


@dataclass(frozen=True, slots=True)
class ConteosHoja:
    """Conteos con la semántica de la hoja `EGM` sobre un rango de filas (contrato §5).

    Son enteros porque la hoja suma dos conteos (principal y secundaria) y cuenta dos veces una
    fila con $G_r = H_r$: no son estudios distintos ni llevan lista de filas. Solo sirven para
    compararlos con los valores guardados en la hoja.
    """

    t1: Mapping[Clave, int] = field(hash=False)
    """$T_1(i, j)$ para cada intervención y dimensión del esquema."""
    t2: Mapping[Clave, int] | None = field(hash=False)
    """$T_2(i, j)$; `None` si el esquema no tiene ancla de evaluación de impacto."""
    t: Mapping[str, int] = field(hash=False)
    """$t(i)$, columna «Total estudios», para cada intervención del esquema."""
    t_ie: Mapping[str, int] | None = field(hash=False)
    """$t^{IE}(i)$; `None` si el esquema no tiene ancla de evaluación de impacto."""

    def __post_init__(self) -> None:
        object.__setattr__(self, "t1", MappingProxyType(dict(self.t1)))
        object.__setattr__(self, "t", MappingProxyType(dict(self.t)))
        if self.t2 is not None:
            object.__setattr__(self, "t2", MappingProxyType(dict(self.t2)))
        if self.t_ie is not None:
            object.__setattr__(self, "t_ie", MappingProxyType(dict(self.t_ie)))


# --------------------------------------------------------------------------------------------
# Ayudas
# --------------------------------------------------------------------------------------------


def _refs(documentos: Iterable[Documento]) -> Conteo:
    """El `Conteo` de esos documentos; llegan en el orden del archivo (el de `Corpus`)."""
    return Conteo(tuple(d.ref for d in documentos))


def _es_empirico(documento: Documento) -> bool:
    """Pertenece a $E$: estado «En el mapa» o «Empírico pendiente» (contrato §4)."""
    return documento.estado in (EstadoDocumento.EN_EL_MAPA, EstadoDocumento.EMPIRICO_PENDIENTE)


def _es_de_impacto(documento: Documento, ancla: str | None) -> bool:
    """$L_r = v_{IE}$; sin ancla ningún documento lo es."""
    return ancla is not None and documento.nivel == ancla


def _claves(esquema: Esquema) -> list[Clave]:
    """Todas las celdas del mapa, intervención por intervención, en el orden del archivo."""
    return [(i, j) for i in esquema.intervenciones for j in esquema.dimensiones]


def _celdas_de_s(
    esquema: Esquema, documentos: Iterable[Documento]
) -> Mapping[Clave, list[RefFila]]:
    """Las filas de cada $S(i, j)$ entre los `documentos` (estudios empíricos, en orden)."""
    filas: dict[Clave, list[RefFila]] = {clave: [] for clave in _claves(esquema)}
    for documento in documentos:
        for i in documento.intervenciones:
            for j in documento.dimensiones:
                if (i, j) in filas:
                    filas[(i, j)].append(documento.ref)
    return filas


def _sin_ancla_de_impacto() -> ValueError:
    return ValueError("el esquema no tiene ancla de evaluación de impacto")


# --------------------------------------------------------------------------------------------
# Conjuntos y mapa
# --------------------------------------------------------------------------------------------


def conjuntos(corpus: Corpus) -> Conjuntos:
    """$R$, $E$, $M$ y $P$ del contrato §5 como `Conteo` (FR-001-07, FR-001-13).

    $R$ son todos los documentos; $E$ los de tipo empírico; $M$ los empíricos con intervención y
    al menos una dimensión en 1; $P = E \\setminus M$, los empíricos pendientes.
    """
    documentos = corpus.documentos
    return Conjuntos(
        r=_refs(documentos),
        e=_refs(d for d in documentos if _es_empirico(d)),
        m=_refs(d for d in documentos if d.estado is EstadoDocumento.EN_EL_MAPA),
        p=_refs(d for d in documentos if d.estado is EstadoDocumento.EMPIRICO_PENDIENTE),
    )


def mapa(esquema: Esquema, corpus: Corpus) -> Mapa:
    """El mapa sin filtro: $S(i, j)$ en cada celda, $n$ y $N$ (FR-001-07, FR-001-08, FR-001-09).

    Hay una celda por cada intervención y dimensión del esquema, también las que valen 0 (un 0 es
    «ningún estudio registrado»). Un estudio entra en todas las celdas de sus intervenciones y sus
    dimensiones, pero $n$ y $N$ cuentan estudios distintos y nunca son la suma de las celdas.
    """
    en_el_mapa = [d for d in corpus.documentos if d.estado is EstadoDocumento.EN_EL_MAPA]
    filas = _celdas_de_s(esquema, en_el_mapa)
    total = _refs(en_el_mapa)
    return Mapa(
        intervenciones=esquema.intervenciones,
        dimensiones=esquema.dimensiones,
        celdas={clave: Celda(Conteo(tuple(refs))) for clave, refs in filas.items()},
        estudios=total,
        total=total,
    )


def evaluacion_impacto(esquema: Esquema, corpus: Corpus) -> Mapping[Clave, Conteo] | None:
    """$S^{IE}(i, j)$: estudios empíricos de nivel «evaluación de impacto» (FR-001-07).

    `None` si el esquema no tiene ancla de evaluación de impacto (contrato §4.1): entonces
    $S^{IE}$ no se calcula, y un `None` nunca es 0. Con ancla hay una entrada por cada
    intervención y dimensión, también las de 0.
    """
    ancla = esquema.anclas.evaluacion_impacto
    if ancla is None:
        return None
    de_impacto = [d for d in corpus.documentos if _es_empirico(d) and d.nivel == ancla]
    filas = _celdas_de_s(esquema, de_impacto)
    return MappingProxyType({clave: Conteo(tuple(refs)) for clave, refs in filas.items()})


# --------------------------------------------------------------------------------------------
# Por intervención y por nivel
# --------------------------------------------------------------------------------------------


def por_intervencion(
    esquema: Esquema, corpus: Corpus, *, solo_ie: bool = False
) -> Mapping[str, Conteo]:
    """$u(i)$, o $u^{IE}(i)$ con `solo_ie`: estudios empíricos de cada intervención (FR-001-07).

    No exige dimensiones marcadas (contrato §5) y cuenta estudios distintos: es el equivalente en
    la herramienta de la columna «Total estudios» de la hoja. Hay una entrada por cada
    intervención del esquema, también las de 0. Con `solo_ie` y sin ancla de evaluación de impacto,
    `ValueError`: no hay nada que contar, y ese caso no se confunde con 0.
    """
    ancla = esquema.anclas.evaluacion_impacto
    if solo_ie and ancla is None:
        raise _sin_ancla_de_impacto()
    estudios = [
        d
        for d in corpus.documentos
        if _es_empirico(d) and (not solo_ie or _es_de_impacto(d, ancla))
    ]
    filas: dict[str, list[RefFila]] = {i: [] for i in esquema.intervenciones}
    for documento in estudios:
        for i in documento.intervenciones:
            if i in filas:
                filas[i].append(documento.ref)
    return MappingProxyType({i: Conteo(tuple(refs)) for i, refs in filas.items()})


def por_nivel(esquema: Esquema, corpus: Corpus) -> Mapping[str, Conteo]:
    """$T_4(\\ell)$: estudios empíricos de cada nivel de evidencia del esquema (FR-001-07).

    Hay una entrada por cada nivel del esquema (los valores «No aplica» no son nivel), también los
    de 0. Un estudio sin nivel, o con un nivel que no está en la lista, no suma en ninguno, de modo
    que $\\sum_\\ell T_4(\\ell) \\le |E|$.
    """
    filas: dict[str, list[RefFila]] = {nivel: [] for nivel in esquema.niveles}
    for documento in corpus.documentos:
        if _es_empirico(documento) and documento.nivel in filas:
            filas[documento.nivel].append(documento.ref)
    return MappingProxyType({nivel: Conteo(tuple(refs)) for nivel, refs in filas.items()})


# --------------------------------------------------------------------------------------------
# Semántica de la hoja
# --------------------------------------------------------------------------------------------


def _veces(documento: Documento) -> int:
    """Cuántos de los dos sumandos de la hoja (principal y secundaria) valen cada $i \\in I_r$.

    2 si $G_r = H_r$ (la hoja cuenta doble); 1 en otro caso.
    """
    return 2 if documento.crudos.principal_igual_secundaria else 1


def semantica_hoja(
    esquema: Esquema, corpus: Corpus, filas: range, variante: VarianteHoja
) -> ConteosHoja:
    """$T_1$, $T_2$, $t$ y $t^{IE}$ de la hoja `EGM` sobre las `filas` del archivo (FR-001-14).

    `filas` son números de fila de la hoja de la matriz (`RefFila.fila`): solo cuentan los
    estudios empíricos que están en ese rango, para comparar con las celdas cuyas fórmulas abarcan
    esas filas (contrato §7.3). Cada fila aporta un sumando por su intervención principal y otro por
    la secundaria, de modo que una con $G_r = H_r$ cuenta dos veces. $T_1$ y $T_2$ exigen la
    dimensión marcada; $t$ y $t^{IE}$, no. Sin ancla de evaluación de impacto, `t2` y `t_ie` son
    `None`.

    Con `VarianteHoja.ESTANDAR` la fila se lee como la herramienta la leyó.
    """
    if variante is not VarianteHoja.ESTANDAR:  # pragma: no cover - las demás llegan con T-001-45
        raise NotImplementedError(variante)
    ancla = esquema.anclas.evaluacion_impacto
    estudios = [d for d in corpus.documentos if _es_empirico(d) and d.ref.fila in filas]

    t1 = dict.fromkeys(_claves(esquema), 0)
    t2 = dict.fromkeys(t1, 0)
    t = dict.fromkeys(esquema.intervenciones, 0)
    t_ie = dict.fromkeys(t, 0)
    for documento in estudios:
        de_impacto = _es_de_impacto(documento, ancla)
        veces = _veces(documento)
        for i in documento.intervenciones:
            if i not in t:
                continue
            t[i] += veces
            t_ie[i] += veces if de_impacto else 0
            for j in documento.dimensiones:
                if (i, j) in t1:
                    t1[(i, j)] += veces
                    t2[(i, j)] += veces if de_impacto else 0
    return ConteosHoja(
        t1=t1,
        t2=None if ancla is None else t2,
        t=t,
        t_ie=None if ancla is None else t_ie,
    )
