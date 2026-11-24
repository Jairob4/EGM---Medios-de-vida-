"""Configuración común de las pruebas: perfil determinista de hypothesis (T-001-03)."""

from hypothesis import HealthCheck, settings

# Perfil determinista: misma semilla en cada corrida, sin plazo por ejemplo y sin base de ejemplos
# en disco (nada se escribe fuera de la memoria; NFR-000-17).
settings.register_profile(
    "determinista",
    derandomize=True,
    deadline=None,
    database=None,
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)
