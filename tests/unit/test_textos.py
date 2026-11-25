"""Pruebas de la base de M10 `egm.textos` (T-001-16): P-001-09.

Los esperados de E2, E3 y E10 están copiados a mano de `docs/interfaz/flujos.md` §2 (estados de
rechazo); el de `fecha()` sale del enunciado de P-001-09. Ninguno sale de ejecutar `egm.textos`.
"""

import re
from datetime import datetime

import pytest

from egm import textos
from egm.modelo import Rechazo

E2_TIPO = (
    "No se pudo cargar el archivo. El archivo elegido no es un archivo de Excel (.xlsx) que la "
    "herramienta pueda abrir, o está dañado. No se leyó y no se muestra ningún resultado. "
    "Elija la matriz bibliográfica en formato .xlsx."
)
E3_TAMANO = (
    "No se pudo cargar el archivo. El archivo pesa más de 15 MB (15 728 640 bytes), el máximo "
    "que admite la herramienta. No se leyó y no se muestra ningún resultado de ese archivo."
)
E10_CONTENIDO = (
    "No se pudo cargar el archivo. El contenido del libro es demasiado grande para abrirlo. "
    "No se leyó y no se muestra ningún resultado de ese archivo."
)


def test_fecha_en_espanol_para_el_21_de_noviembre_de_2026() -> None:
    """NFR-000-03: `fecha()` da «21 de noviembre de 2026» para esa fecha (P-001-09)."""
    assert textos.fecha(datetime(2026, 11, 21, 15, 30)) == "21 de noviembre de 2026"


@pytest.mark.parametrize(
    ("mes", "nombre"),
    [
        (1, "enero"),
        (2, "febrero"),
        (3, "marzo"),
        (4, "abril"),
        (5, "mayo"),
        (6, "junio"),
        (7, "julio"),
        (8, "agosto"),
        (9, "septiembre"),
        (10, "octubre"),
        (11, "noviembre"),
        (12, "diciembre"),
    ],
)
def test_fecha_nombra_cada_mes_sin_ceros_a_la_izquierda(mes: int, nombre: str) -> None:
    """NFR-000-03: el mes va en español y el día sin cero a la izquierda (P-001-09)."""
    assert textos.fecha(datetime(2027, mes, 5)) == f"5 de {nombre} de 2027"


def test_rechazo_por_tipo_da_el_texto_e2() -> None:
    """NFR-000-19, US-001-4.3: texto del estado E2 de `flujos.md` §2."""
    assert textos.rechazo(Rechazo("tipo")) == E2_TIPO


def test_rechazo_por_tamano_da_el_texto_e3() -> None:
    """NFR-000-19, US-001-4.4: texto del estado E3 de `flujos.md` §2."""
    assert textos.rechazo(Rechazo("tamano")) == E3_TAMANO


def test_rechazo_por_contenido_da_el_texto_e10_sin_cifras() -> None:
    """NFR-000-19, US-001-4.13: texto del estado E10; no lleva ni tamaño ni límite."""
    texto = textos.rechazo(Rechazo("contenido"))
    assert texto == E10_CONTENIDO
    assert not re.search(r"\d", texto)


def test_cada_motivo_de_rechazo_tiene_texto_propio() -> None:
    """NFR-000-19: los tres motivos dan tres textos distintos."""
    todos = {textos.rechazo(Rechazo(m)) for m in ("tipo", "tamano", "contenido")}
    assert len(todos) == 3


def test_el_catalogo_es_de_solo_lectura() -> None:
    """NFR-000-03: el catálogo único y los rótulos no se pueden alterar desde afuera."""
    with pytest.raises(TypeError):
        textos.CATALOGO["rechazo.tipo"] = "otro"  # type: ignore[index]
    with pytest.raises(TypeError):
        textos.ROTULOS["x"] = "y"  # type: ignore[index]


def test_los_rotulos_empiezan_vacios_para_que_002_y_003_los_amplien() -> None:
    """FR-001-29, arquitectura M10: `ROTULOS` existe y está vacío en la base."""
    assert len(textos.ROTULOS) == 0


def test_el_catalogo_contiene_los_textos_de_rechazo() -> None:
    """NFR-000-19: el catálogo único incluye los tres textos de rechazo (otros agregan más)."""
    assert {E2_TIPO, E3_TAMANO, E10_CONTENIDO} <= set(textos.CATALOGO.values())


# --- Estilo de los textos (NFR-000-03, SC-000-03) ------------------------------------------------

TUTEO = re.compile(
    r"\b(t[uú]|tus?|ti|contigo|tienes|puedes|eres|quieres|elige|sube|carga|selecciona|"
    r"intenta|revisa|verifica|vuelve|abre|haz|usa)\b",
    re.IGNORECASE,
)
FORMULAS = re.compile(r"[=$\\^_{}<>∑≤≥±×÷]|\b\d+\s*/\s*\d+\b")
PROHIBIDAS = (
    "error de contrato",
    "validación",
    "validacion",
    "fixture",
    "tabla 3",
    "tabla no comparable",
    "traceback",
    "excepción",
)


def _todos_los_textos() -> list[str]:
    return [*textos.CATALOGO.values(), *textos.ROTULOS.values()]


def test_hay_textos_que_revisar() -> None:
    """NFR-000-03: la revisión de estilo no pasa por vacía."""
    assert len(_todos_los_textos()) >= 3


def test_ningun_texto_lleva_preguntas() -> None:
    """NFR-000-03, SC-000-03: ni «¿» ni «?» (sin preguntas al equipo)."""
    for texto in _todos_los_textos():
        assert "¿" not in texto
        assert "?" not in texto


def test_ningun_texto_tutea() -> None:
    """NFR-000-03, SC-000-03: sin formas de tuteo."""
    for texto in _todos_los_textos():
        assert TUTEO.search(texto) is None, texto


def test_ningun_texto_lleva_formulas() -> None:
    """NFR-000-03, SC-000-03: sin símbolos ni fórmulas."""
    for texto in _todos_los_textos():
        assert FORMULAS.search(texto) is None, texto


def test_ningun_texto_usa_jerga_ni_nombra_tablas_no_comparables() -> None:
    """NFR-000-03: sin jerga técnica ni mención de una tabla no comparable de la hoja EGM."""
    for texto in _todos_los_textos():
        minusculas = texto.lower()
        for prohibida in PROHIBIDAS:
            assert prohibida not in minusculas, (prohibida, texto)
        assert re.search(r"\btabla\s+\d", minusculas) is None, texto


def test_los_detectores_de_estilo_reconocen_lo_que_deben_rechazar() -> None:
    """NFR-000-03: los patrones de la revisión sí atrapan tuteo y fórmulas de ejemplo."""
    assert TUTEO.search("Puedes elegir otro archivo")
    assert TUTEO.search("Elige la matriz")
    assert TUTEO.search("Elija la matriz") is None
    assert FORMULAS.search("n = 5")
    assert FORMULAS.search("$S(i,j)$")
