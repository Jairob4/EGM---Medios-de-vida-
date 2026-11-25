"""Invariantes de conteo del contrato de datos §5 sobre matrices sintéticas (P-001-25, T-001-22).

SC-001-03, NFR-000-02. Con las estrategias de M23 (`tests.constructor.matrices_validas`), el libro
se lee con `abrir`, `descubrir` (M04) y `leer` (M05) y se cuenta con M07. Los esperados salen de un
ORÁCULO escrito aquí desde las fórmulas del contrato §5: cuenta directamente sobre los documentos
que escribió la estrategia, sin llamar al código bajo prueba. $S_\\varphi$ queda para el plan 002 y
$S_\\kappa$ para el plan 003.

Los módulos M04, M05 y M07 se importan dentro de la prueba: mientras no existan, falla la prueba y
no la recolección.
"""

from dataclasses import dataclass
from typing import Any

from hypothesis import given, settings

from egm.libro import abrir
from egm.modelo import Conteo
from tests.constructor import (
    VALOR_IMPACTO,
    MatrizSintetica,
    matrices_validas,
)

ENCABEZADO_TIPO = "Tipo de documento"
ENCABEZADO_PRINCIPAL = "Tipo de intervención (EGM)"
ENCABEZADO_SECUNDARIA = "Intervención secundaria (opcional)"
ENCABEZADO_NIVEL = "Nivel de evidencia"
ENCABEZADO_NUMERO = "N°"
PRIMERA_FILA_DE_DATOS = 2  # la fila 1 del archivo es el encabezado


@dataclass(frozen=True)
class Oraculo:
    """Conteos de referencia por filas del archivo, calculados con el contrato §5."""

    intervenciones: tuple[str, ...]
    dimensiones: tuple[str, ...]
    niveles: tuple[str, ...]
    filas_r: frozenset[int]
    filas_e: frozenset[int]
    filas_m: frozenset[int]
    s: dict[tuple[str, str], frozenset[int]]
    s_ie: dict[tuple[str, str], frozenset[int]]
    t1: dict[tuple[str, str], int]
    t2: dict[tuple[str, str], int]
    t4: dict[str, int]
    suma_ir_jr: int


def _sin_no_aplica(valores: list[str] | None) -> tuple[str, ...]:
    return tuple(v for v in (valores or []) if not v.startswith("No aplica"))


def _oraculo(matriz: MatrizSintetica) -> Oraculo:
    """Las fórmulas del contrato §5 aplicadas a lo que escribió la estrategia."""
    intervenciones = _sin_no_aplica(matriz.valores_de_lista(ENCABEZADO_PRINCIPAL))
    niveles = _sin_no_aplica(matriz.valores_de_lista(ENCABEZADO_NIVEL))
    dimensiones = tuple(matriz.dimensiones())
    ancla_empirica = next(
        v
        for v in matriz.valores_de_lista(ENCABEZADO_TIPO) or []
        if v.startswith("Estudio empírico")
    )

    filas_r: set[int] = set()
    filas_e: set[int] = set()
    filas_m: set[int] = set()
    s: dict[tuple[str, str], set[int]] = {
        (i, j): set() for i in intervenciones for j in dimensiones
    }
    s_ie: dict[tuple[str, str], set[int]] = {clave: set() for clave in s}
    t1 = dict.fromkeys(s, 0)
    t2 = dict.fromkeys(s, 0)
    t4 = dict.fromkeys(niveles, 0)
    suma_ir_jr = 0

    for posicion, documento in enumerate(matriz.documentos()):
        if not documento:  # fila vacía: fuera de R
            continue
        fila = PRIMERA_FILA_DE_DATOS + posicion
        filas_r.add(fila)
        if documento.get(ENCABEZADO_TIPO) != ancla_empirica:
            continue
        filas_e.add(fila)
        principal = documento.get(ENCABEZADO_PRINCIPAL)
        secundaria = documento.get(ENCABEZADO_SECUNDARIA)
        nivel = documento.get(ENCABEZADO_NIVEL)
        es_ie = nivel == VALOR_IMPACTO
        i_r = {x for x in (principal, secundaria) if x in intervenciones}  # {G, H} ∩ 𝓘
        j_r = {j for j in dimensiones if documento.get(j) == 1}
        if nivel in t4:
            t4[nivel] += 1
        if i_r and j_r:
            filas_m.add(fila)
            suma_ir_jr += len(i_r) * len(j_r)
        for i in i_r:
            for j in j_r:
                s[(i, j)].add(fila)
                if es_ie:
                    s_ie[(i, j)].add(fila)
        for j in j_r:  # T1 y T2: un sumando por la principal y otro por la secundaria
            for i in (principal, secundaria):
                if i in intervenciones:
                    t1[(i, j)] += 1
                    if es_ie:
                        t2[(i, j)] += 1

    return Oraculo(
        intervenciones=intervenciones,
        dimensiones=dimensiones,
        niveles=niveles,
        filas_r=frozenset(filas_r),
        filas_e=frozenset(filas_e),
        filas_m=frozenset(filas_m),
        s={k: frozenset(v) for k, v in s.items()},
        s_ie={k: frozenset(v) for k, v in s_ie.items()},
        t1=t1,
        t2=t2,
        t4=t4,
        suma_ir_jr=suma_ir_jr,
    )


def _filas(conteo: Conteo) -> frozenset[int]:
    """Las filas del archivo que trae un `Conteo`."""
    return frozenset(ref.fila for ref in conteo.filas)


def _conjunto(conjuntos: Any, nombre: str) -> Conteo:
    """Un conjunto de `Conjuntos` (R, E, M o P): por su nombre en mayúscula o minúscula."""
    for candidato in (nombre, nombre.lower()):
        if hasattr(conjuntos, candidato):
            valor: Conteo = getattr(conjuntos, candidato)
            return valor
    raise AttributeError(f"Conjuntos no tiene el conjunto {nombre}")


def _es_conteo_consistente(conteo: Conteo) -> bool:
    return isinstance(conteo, Conteo) and conteo.valor == len(conteo.filas)


@settings(max_examples=40)
@given(matrices_validas(con_egm=False, max_documentos=60))
def test_p_001_25_invariantes_de_conteo(matriz: MatrizSintetica) -> None:
    """P-001-25 · SC-001-03, NFR-000-02: invariantes de S, S^IE, T1, T2, T4 y de todo `Conteo`.

    S^IE <= S <= T1; T2 <= T1; suma de T4 <= |E|; suma de S = suma de |I_r||J_r| >= N; y
    `Conteo.valor == len(filas)` en todo conteo, con las filas que dice el oráculo.
    """
    import egm.conteo as conteo
    from egm.esquema import descubrir
    from egm.lectura import leer

    esperado = _oraculo(matriz)

    libro = abrir(matriz.a_bytes())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "una matriz válida no debe dar fallo de contrato"
    corpus = leer(libro, esquema)

    # Categorías en el orden del archivo (contrato §4, regla 3).
    assert tuple(esquema.intervenciones) == esperado.intervenciones
    assert tuple(esquema.dimensiones) == esperado.dimensiones
    assert tuple(esquema.niveles) == esperado.niveles

    conjuntos = conteo.conjuntos(corpus)
    mapa = conteo.mapa(esquema, corpus)
    ie = conteo.evaluacion_impacto(esquema, corpus)
    t4 = conteo.por_nivel(esquema, corpus)
    u = conteo.por_intervencion(esquema, corpus)
    u_ie = conteo.por_intervencion(esquema, corpus, solo_ie=True)
    assert ie is not None, "las matrices sintéticas siempre traen el nivel «Evaluación de impacto»"

    # Conjuntos con las filas del oráculo.
    assert _filas(_conjunto(conjuntos, "R")) == esperado.filas_r
    assert _filas(_conjunto(conjuntos, "E")) == esperado.filas_e
    assert _filas(_conjunto(conjuntos, "M")) == esperado.filas_m
    assert _filas(_conjunto(conjuntos, "P")) == esperado.filas_e - esperado.filas_m
    assert _filas(mapa.total) == esperado.filas_m
    n_estudios = mapa.total.valor
    assert n_estudios == len(esperado.filas_m)

    # S y S^IE: las filas de cada celda son las del oráculo; S^IE <= S <= T1 y T2 <= T1.
    suma_celdas = 0
    for clave, filas_s in esperado.s.items():
        celda = mapa.celdas[clave].conteo
        assert _filas(celda) == filas_s, clave
        celda_ie = ie.get(clave)
        filas_ie = _filas(celda_ie) if celda_ie is not None else frozenset()
        assert filas_ie == esperado.s_ie[clave], clave
        assert len(filas_ie) <= celda.valor <= esperado.t1[clave], clave
        assert esperado.t2[clave] <= esperado.t1[clave], clave
        suma_celdas += celda.valor

    # Suma de celdas = suma de |I_r||J_r| >= N (no es el número de estudios).
    assert suma_celdas == esperado.suma_ir_jr
    assert suma_celdas >= n_estudios

    # T4: cada nivel con las filas de E que lo tienen; la suma no supera |E|.
    assert {nivel: t4[nivel].valor for nivel in esperado.niveles} == esperado.t4
    assert sum(esperado.t4.values()) <= len(esperado.filas_e)
    assert sum(t4[nivel].valor for nivel in esperado.niveles) <= _conjunto(conjuntos, "E").valor

    # Todo número del sistema es la longitud de su lista de filas.
    todos = [
        mapa.estudios,
        mapa.total,
        *(_conjunto(conjuntos, nombre) for nombre in ("R", "E", "M", "P")),
        *(celda.conteo for celda in mapa.celdas.values()),
        *ie.values(),
        *t4.values(),
        *u.values(),
        *u_ie.values(),
    ]
    assert all(_es_conteo_consistente(c) for c in todos)
