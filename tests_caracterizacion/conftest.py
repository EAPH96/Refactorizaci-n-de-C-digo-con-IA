"""Configuración de la suite de caracterización (independiente de tests/).

Vive fuera de tests/ porque el reto prohíbe modificar esa carpeta.
"""

import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
for ruta in (AQUI, AQUI.parent / "src"):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))

import gestor  # noqa: E402


@pytest.fixture(autouse=True)
def sistema_limpio():
    """Estado vacío antes y después de cada prueba (igual que tests/conftest.py)."""
    gestor.reiniciar_sistema()
    yield
    gestor.reiniciar_sistema()
