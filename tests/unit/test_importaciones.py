"""Pruebas de las reglas de importación del núcleo (T-001-16): P-001-10.

Verifica SC-000-14 y NFR-000-14 con las reglas de arquitectura §4.1: ningún módulo de `src/egm/`
importa `app` ni una biblioteca web (FastAPI, Starlette, Jinja2, Uvicorn); `egm.modelo` no importa
otro módulo de `egm`; solo `egm.libro` importa `openpyxl`.

La comprobación recorre con `ast` todos los archivos `.py` de `src/egm/` (incluye los que aún
están vacíos y los que se agreguen después), sin importar ningún módulo. Cada regla tiene además
una prueba negativa con un fragmento de código escrito a mano que debe rechazar.
"""

import ast
from pathlib import Path

import pytest

RAIZ_NUCLEO = Path(__file__).resolve().parents[2] / "src" / "egm"

PROHIBIDOS_WEB = frozenset({"app", "fastapi", "starlette", "jinja2", "uvicorn"})
BIBLIOTECA_DE_LIBROS = "openpyxl"
MODULO_DEL_LIBRO = "egm.libro"
MODULO_DE_TIPOS = "egm.modelo"


def _importados(codigo: str, modulo: str) -> list[str]:
    """Nombres completos de todo lo que importa el código, en cualquier lugar del módulo.

    Una importación relativa se resuelve contra el paquete del módulo. `from egm import x`
    cuenta como importar `egm.x`.
    """
    paquete = modulo.split(".")[:-1]
    nombres: list[str] = []
    for nodo in ast.walk(ast.parse(codigo)):
        if isinstance(nodo, ast.Import):
            nombres.extend(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:
                base = paquete[: len(paquete) - (nodo.level - 1)]
                if nodo.module:
                    base = [*base, nodo.module]
            else:
                base = (nodo.module or "").split(".")
            raiz = ".".join(base)
            nombres.append(raiz)
            nombres.extend(f"{raiz}.{alias.name}" for alias in nodo.names if alias.name != "*")
    return nombres


def _infracciones(codigo: str, modulo: str) -> list[str]:
    """Reglas 1 a 3 de arquitectura §4.1 aplicadas a un módulo; lista vacía si las cumple."""
    problemas: list[str] = []
    for nombre in _importados(codigo, modulo):
        raiz = nombre.split(".")[0]
        if raiz in PROHIBIDOS_WEB:
            problemas.append(f"{modulo} importa {nombre} (regla 1)")
        if raiz == "egm" and modulo == MODULO_DE_TIPOS and nombre != "egm":
            problemas.append(f"{modulo} importa {nombre} (regla 2)")
        if raiz == BIBLIOTECA_DE_LIBROS and modulo != MODULO_DEL_LIBRO:
            problemas.append(f"{modulo} importa {nombre} (regla 3)")
    return problemas


def _modulos_del_nucleo() -> list[tuple[str, Path]]:
    """Pares (nombre del módulo, archivo) de cada `.py` de `src/egm/`."""
    encontrados: list[tuple[str, Path]] = []
    for archivo in sorted(RAIZ_NUCLEO.rglob("*.py")):
        partes = archivo.relative_to(RAIZ_NUCLEO.parent).with_suffix("").parts
        if partes[-1] == "__init__":
            partes = partes[:-1]
        encontrados.append((".".join(partes), archivo))
    return encontrados


def test_el_recorrido_encuentra_el_nucleo() -> None:
    """SC-000-14: el recorrido ve los módulos reales (no pasa por no mirar nada)."""
    nombres = {nombre for nombre, _ in _modulos_del_nucleo()}
    assert {"egm.modelo", "egm.libro", "egm.textos"} <= nombres


def test_el_nucleo_cumple_las_reglas_de_importacion() -> None:
    """SC-000-14, NFR-000-14: ningún módulo de `src/egm/` rompe las reglas 1 a 3 de §4.1."""
    problemas: list[str] = []
    for nombre, archivo in _modulos_del_nucleo():
        problemas.extend(_infracciones(archivo.read_text(encoding="utf-8"), nombre))
    assert problemas == []


def test_solo_el_libro_importa_la_biblioteca_de_hojas_de_calculo() -> None:
    """SC-000-14 (regla 3): `egm.libro` sí importa `openpyxl`; ningún otro módulo lo hace."""
    quienes = {
        nombre
        for nombre, archivo in _modulos_del_nucleo()
        if any(
            n.split(".")[0] == BIBLIOTECA_DE_LIBROS
            for n in _importados(archivo.read_text(encoding="utf-8"), nombre)
        )
    }
    assert quienes == {MODULO_DEL_LIBRO}


def test_el_modelo_no_importa_otro_modulo_de_egm() -> None:
    """SC-000-14 (regla 2): `egm.modelo` solo usa la biblioteca estándar."""
    codigo = (RAIZ_NUCLEO / "modelo.py").read_text(encoding="utf-8")
    assert [n for n in _importados(codigo, "egm.modelo") if n.split(".")[0] == "egm"] == []


# --- Pruebas negativas: la regla debe rechazar estos fragmentos --------------------------------


@pytest.mark.parametrize(
    "fragmento",
    [
        "import app",
        "from app.servidor import crear",
        "import fastapi",
        "from starlette.responses import Response",
        "import jinja2.sandbox",
        "from uvicorn import run",
        "def f():\n    import fastapi\n",
    ],
)
def test_la_regla_1_rechaza_la_capa_web(fragmento: str) -> None:
    """SC-000-14 (regla 1): un módulo del núcleo que importa `app` o una biblioteca web."""
    assert _infracciones(fragmento, "egm.conteo") != []


@pytest.mark.parametrize(
    "fragmento",
    [
        "import egm.libro",
        "from egm import libro",
        "from egm.libro import abrir",
        "from . import conteo",
        "from .libro import abrir",
        "def f():\n    from egm.textos import fecha\n",
    ],
)
def test_la_regla_2_rechaza_que_el_modelo_importe_egm(fragmento: str) -> None:
    """SC-000-14 (regla 2): `egm.modelo` importando otro módulo de `egm`."""
    assert _infracciones(fragmento, "egm.modelo") != []


def test_la_regla_2_no_alcanza_a_los_demas_modulos() -> None:
    """SC-000-14 (regla 2): otros módulos sí pueden importar `egm.modelo`."""
    assert _infracciones("from egm.modelo import Rechazo", "egm.textos") == []
    assert _infracciones("from .modelo import Rechazo", "egm.textos") == []


@pytest.mark.parametrize(
    "fragmento",
    [
        "import openpyxl",
        "from openpyxl import load_workbook",
        "import openpyxl.worksheet.datavalidation",
        "def f():\n    import openpyxl\n",
    ],
)
def test_la_regla_3_rechaza_openpyxl_fuera_del_libro(fragmento: str) -> None:
    """SC-000-14 (regla 3): `openpyxl` en un módulo que no es `egm.libro`."""
    assert _infracciones(fragmento, "egm.lectura") != []


def test_la_regla_3_permite_openpyxl_en_el_libro() -> None:
    """SC-000-14 (regla 3): `egm.libro` puede importar `openpyxl`."""
    assert _infracciones("import openpyxl\nfrom openpyxl import Workbook", "egm.libro") == []


def test_un_modulo_vacio_o_con_biblioteca_estandar_cumple() -> None:
    """SC-000-14: un archivo vacío y uno con solo biblioteca estándar no tienen infracciones."""
    assert _infracciones("", "egm.verificacion") == []
    assert _infracciones("import io\nfrom dataclasses import dataclass", "egm.modelo") == []
