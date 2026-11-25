"""Historia 1 del plan 001: leer y contar la matriz real (v4) en modo lectura.

Pruebas P-001-11 a P-001-15 (T-001-20). Abren `data/raw/` solo en modo binario de lectura
(`open(ruta, "rb")`) y entregan los bytes a `egm.libro.abrir`; nunca escriben. Llaman a
`abrir`, `descubrir` (M04), `leer` (M05) y a M07; los módulos aún no implementados se importan
dentro de cada prueba, para que la ausencia de uno falle solo esa prueba y no la recolección.

Los esperados están escritos a mano desde el apéndice A del contrato de datos
(`docs/specs/contrato-datos.md`), no de la salida del código bajo prueba.
"""

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from egm.libro import abrir
from egm.modelo import SIN_NIVEL, Conteo, Enfoque, EstadoDocumento

pytestmark = pytest.mark.raw

RUTA_V4 = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "matriz_bibliografica_estado_del_arte_v4.xlsx"
)

omitir_sin_v4 = pytest.mark.skipif(
    not RUTA_V4.is_file(),
    reason="no está la matriz v4 en data/raw/: la prueba contra la matriz real no se puede correr",
)

# --- Esperados del apéndice A (v4) ------------------------------------------------------------

SHA256_V4 = "7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1".lower()

HOJAS = ("Matriz bibliográfica", "EGM", "Instrucciones", "Guía por tipo de documento")

TIPOS_DOCUMENTO = (
    "Marco teórico",
    "Marco metodológico",
    "Marco normativo",
    "Estudio empírico (evaluación/caso)",
    "Marco crítico-contextual",
    "Comparativo internacional",
)
TIPOS_FUENTE = ("Académica", "Institucional", "Territorial")
INTERVENCIONES = (
    "Transferencia de activos",
    "Diagnóstico territorial",
    "Acompañamiento técnico",
    "Apoyo psicosocial",
    "Acceso a mercados y finanzas",
    "Asociatividad",
)
NO_APLICA_INTERVENCION = "No aplica (documento teórico/metodológico/normativo)"
METODOLOGIAS = (
    "Cualitativa",
    "Cuantitativa",
    "Mixta",
    "Revisión documental",
    "Evaluación de impacto",
    "Conceptual/teórica",
    "Análisis normativo/jurídico",
)
NIVELES = (
    "Evaluación de impacto",
    "Estudio de caso",
    "Informe de proyecto",
    "Informe descriptivo/opinión",
)
NO_APLICA_NIVEL = "No aplica (marco conceptual/normativo/metodológico)"
DIMENSIONES = (
    "Vulnerabilidad",
    "Humano",
    "Social",
    "Natural",
    "Físico",
    "Financiero",
    "Estructuras y procesos",
    "Sostenibilidad",
)

# Columnas de la hoja de la matriz con lista de validación (G = intervención principal, J = nivel).
COLUMNA_PRINCIPAL = 7
COLUMNA_NIVEL = 10

NUMEROS_E = {"7", "10", "11", "13", "15", "16", "24"}
NUMEROS_P = {"10", "11", "13", "15", "16", "24"}
NUMEROS_NO_EMPIRICOS = {str(n) for n in (1, 2, 3, 4, 5, 6, 8, 9, 12, 14)} | {
    str(n) for n in (*range(17, 24), 25, 26, 27)
}
CELDAS_EN_1 = {
    (i, j)
    for i in ("Transferencia de activos", "Acompañamiento técnico")
    for j in ("Vulnerabilidad", "Humano", "Financiero")
}


# --- Ayudas -----------------------------------------------------------------------------------


def _bytes_v4() -> bytes:
    """Los bytes de la v4, abierta solo en modo binario de lectura."""
    with open(RUTA_V4, "rb") as archivo:
        return archivo.read()


def _sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest().lower()


def _leer_v4() -> tuple[Any, Any, Any, Any]:
    """`abrir`, `descubrir` y `leer` sobre la v4: `(libro, esquema, corpus, M07)`.

    Los imports son locales: M04, M05 y M07 los implementan las tareas T-001-23 a T-001-25.
    """
    import egm.conteo as conteo
    from egm.esquema import descubrir
    from egm.lectura import leer

    libro = abrir(_bytes_v4())
    esquema = descubrir(libro)
    assert not hasattr(esquema, "errores"), "la v4 no debe dar un fallo de contrato"
    corpus = leer(libro, esquema)
    return libro, esquema, corpus, conteo


def _numeros(conteo: Conteo) -> set[str]:
    """N.º de las filas de un `Conteo`, como texto (`RefFila.numero` es el N.º de la matriz)."""
    return {str(ref.numero) for ref in conteo.filas}


def _conjunto(conjuntos: Any, nombre: str) -> Conteo:
    """Un conjunto de `Conjuntos` (R, E, M o P): por su nombre en mayúscula o minúscula."""
    for candidato in (nombre, nombre.lower()):
        if hasattr(conjuntos, candidato):
            valor: Conteo = getattr(conjuntos, candidato)
            return valor
    raise AttributeError(f"Conjuntos no tiene el conjunto {nombre}")


# --- P-001-11 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_11_conjuntos_y_mapa_de_la_v4() -> None:
    """P-001-11 · US-001-1.1, FR-001-07, SC-001-01: apéndice A, conjuntos y 6 de 48 celdas."""
    _, esquema, corpus, conteo = _leer_v4()

    conjuntos = conteo.conjuntos(corpus)
    assert _conjunto(conjuntos, "R").valor == 27
    assert _conjunto(conjuntos, "E").valor == 7
    assert _numeros(_conjunto(conjuntos, "E")) == NUMEROS_E
    assert _conjunto(conjuntos, "M").valor == 1
    assert _numeros(_conjunto(conjuntos, "M")) == {"7"}
    assert _conjunto(conjuntos, "P").valor == 6
    assert _numeros(_conjunto(conjuntos, "P")) == NUMEROS_P

    mapa = conteo.mapa(esquema, corpus)
    assert mapa.total.valor == 1
    assert _numeros(mapa.total) == {"7"}
    assert mapa.estudios.valor == 1
    assert len(mapa.celdas) == 48

    en_1 = {clave for clave, celda in mapa.celdas.items() if celda.conteo.valor == 1}
    en_0 = {clave for clave, celda in mapa.celdas.items() if celda.conteo.valor == 0}
    assert en_1 == CELDAS_EN_1
    assert len(en_1) == 6
    assert len(en_0) == 42
    assert en_1 | en_0 == set(mapa.celdas)


# --- P-001-12 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_12_cada_celda_en_1_trae_su_fila_n_7() -> None:
    """P-001-12 · US-001-1.7 (listas), FR-001-11: cada celda en 1 es un `Conteo` del N.º 7."""
    _, esquema, corpus, conteo = _leer_v4()
    mapa = conteo.mapa(esquema, corpus)

    for clave in CELDAS_EN_1:
        celda_conteo = mapa.celdas[clave].conteo
        assert isinstance(celda_conteo, Conteo)
        assert len(celda_conteo.filas) == 1, clave
        assert celda_conteo.valor == 1, clave
        (ref,) = celda_conteo.filas
        assert str(ref.numero) == "7", clave
        assert ref.fila == 8, clave  # N.º 7 está en la fila 8 del archivo (N.º 1 en la fila 2)


# --- P-001-13 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_13_estado_de_los_documentos_de_la_v4() -> None:
    """P-001-13 · US-001-1.9, FR-001-13: 1 en el mapa, 6 pendientes, 20 no empíricos, 0 sin tipo."""
    _, _, corpus, _ = _leer_v4()

    estados = Counter(documento.estado for documento in corpus.documentos)
    assert estados[EstadoDocumento.EN_EL_MAPA] == 1
    assert estados[EstadoDocumento.EMPIRICO_PENDIENTE] == 6
    assert estados[EstadoDocumento.NO_EMPIRICO] == 20
    assert estados[EstadoDocumento.SIN_TIPO_VALIDO] == 0
    assert sum(estados.values()) == 27

    def numeros(estado: EstadoDocumento) -> set[str]:
        return {str(d.ref.numero) for d in corpus.documentos if d.estado == estado}

    assert numeros(EstadoDocumento.EN_EL_MAPA) == {"7"}
    assert numeros(EstadoDocumento.EMPIRICO_PENDIENTE) == NUMEROS_P
    assert numeros(EstadoDocumento.NO_EMPIRICO) == NUMEROS_NO_EMPIRICOS


# --- P-001-14 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_14_resto_del_apendice_a_de_la_v4() -> None:
    """P-001-14 · SC-001-01: hojas, listas, dimensiones, composiciones, T4, t(i), años y enfoque."""
    libro, esquema, corpus, conteo = _leer_v4()
    documentos = corpus.documentos

    # Hojas del libro (M03) y listas descubiertas (M04).
    assert libro.nombres_hojas() == HOJAS
    assert esquema.tipos_documento.valores == TIPOS_DOCUMENTO
    assert esquema.tipos_fuente.valores == TIPOS_FUENTE
    assert esquema.metodologias.valores == METODOLOGIAS
    assert esquema.intervenciones == INTERVENCIONES
    assert esquema.niveles == NIVELES
    # Las listas de intervención y de nivel traen, además, su valor «No aplica…».
    hoja = libro.hoja("Matriz bibliográfica")
    assert hoja.validacion(COLUMNA_PRINCIPAL).valores == (*INTERVENCIONES, NO_APLICA_INTERVENCION)
    assert hoja.validacion(COLUMNA_NIVEL).valores == (*NIVELES, NO_APLICA_NIVEL)

    # Dimensiones: 8, en el orden del archivo.
    assert esquema.dimensiones == DIMENSIONES

    # Por tipo: 9 metodológico, 7 empírico, 4 teórico, 3 normativo, 3 crítico, 1 comparativo.
    por_tipo = Counter(d.tipo_documento for d in documentos)
    assert por_tipo == {
        "Marco metodológico": 9,
        "Estudio empírico (evaluación/caso)": 7,
        "Marco teórico": 4,
        "Marco normativo": 3,
        "Marco crítico-contextual": 3,
        "Comparativo internacional": 1,
    }

    # T4: Evaluación de impacto 1 y los demás niveles 0.
    t4 = conteo.por_nivel(esquema, corpus)
    assert {nivel: t4[nivel].valor for nivel in NIVELES} == {
        "Evaluación de impacto": 1,
        "Estudio de caso": 0,
        "Informe de proyecto": 0,
        "Informe descriptivo/opinión": 0,
    }

    # t(i): 1 en Transferencia de activos y Acompañamiento técnico, 0 en las demás
    # (estudios distintos, u(i); coincide con t(i) porque ningún estudio repite la intervención).
    u = conteo.por_intervencion(esquema, corpus)
    esperado_u = dict.fromkeys(INTERVENCIONES, 0)
    esperado_u |= {"Transferencia de activos": 1, "Acompañamiento técnico": 1}
    assert {i: u[i].valor for i in INTERVENCIONES} == esperado_u

    # Tipo de fuente: 6 Académica, 1 Institucional, 0 Territorial, 20 sin diligenciar (None).
    fuente = Counter(d.tipo_fuente for d in documentos)
    assert fuente == {"Académica": 6, "Institucional": 1, None: 20}
    assert fuente["Territorial"] == 0

    # Metodología: 6 Conceptual/teórica, 1 Evaluación de impacto, 20 sin diligenciar (None).
    metodologia = Counter(d.metodologia for d in documentos)
    assert metodologia == {"Conceptual/teórica": 6, "Evaluación de impacto": 1, None: 20}

    # Años: todos enteros, de 1992 a 2026.
    anios = [d.anio for d in documentos]
    assert all(isinstance(a, int) and not isinstance(a, bool) for a in anios)
    assert min(anios) == 1992
    assert max(anios) == 2026

    # Enfoque (todo el corpus): 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar.
    enfoque = Counter(d.enfoque for d in documentos)
    assert enfoque[Enfoque.NO] == 5
    assert enfoque[Enfoque.SIN_CLASIFICAR] == 2
    assert enfoque[Enfoque.SIN_DILIGENCIAR] == 20
    assert enfoque[Enfoque.SI] == 0
    assert enfoque[Enfoque.PARCIAL] == 0
    assert {str(d.ref.numero) for d in documentos if d.enfoque == Enfoque.SIN_CLASIFICAR} == {
        "2",
        "7",
    }

    # Enfoque (en M): 1 Sin clasificar, el N.º 7.
    en_m = [d for d in documentos if d.estado == EstadoDocumento.EN_EL_MAPA]
    assert [(str(d.ref.numero), d.enfoque) for d in en_m] == [("7", Enfoque.SIN_CLASIFICAR)]
    assert SIN_NIVEL not in {d.nivel for d in en_m}  # el N.º 7 tiene nivel de evidencia


# --- P-001-15 ---------------------------------------------------------------------------------


@omitir_sin_v4
def test_p_001_15_la_lectura_no_altera_la_v4() -> None:
    """P-001-15 · SC-000-01, NFR-000-01: SHA-256 de la v4 antes y después de leer y contar."""
    antes = _sha256(_bytes_v4())
    assert antes == SHA256_V4  # el archivo vigente es el del apéndice A

    _, esquema, corpus, conteo = _leer_v4()
    conteo.mapa(esquema, corpus)
    conteo.conjuntos(corpus)
    conteo.por_nivel(esquema, corpus)

    despues = _sha256(_bytes_v4())
    assert despues == antes
    assert despues == SHA256_V4
