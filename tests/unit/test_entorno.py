"""Prueba de entorno de T-001-03 (infraestructura; no verifica un escenario US/SC del spec)."""

import sys

from hypothesis import settings


def test_entorno_usa_python_313_y_perfil_determinista() -> None:
    """T-001-03: Python 3.13 y perfil determinista de hypothesis activo (sin escenario de spec)."""
    assert sys.version_info[:2] == (3, 13)
    perfil = settings()
    assert perfil.derandomize is True
    assert perfil.database is None
