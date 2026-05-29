"""
Validación de contratos de respuesta contra JSON Schema.

Las pruebas de contrato verifican que la *forma* de la respuesta (campos, tipos,
requeridos) se mantenga estable, independientemente de los valores concretos.
Es clave para detectar cambios incompatibles en una API.
"""
from __future__ import annotations

import json
import os

import allure
from jsonschema import Draft202012Validator

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "schemas")


def load_schema(name: str) -> dict:
    path = os.path.join(_SCHEMA_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def assert_matches_schema(instance, schema_name: str) -> None:
    """Falla con un mensaje agregado y legible si la respuesta no cumple el contrato."""
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))

    if errors:
        detail = "\n".join(
            f"- {'/'.join(map(str, e.path)) or '(raíz)'}: {e.message}" for e in errors
        )
        allure.attach(detail, name=f"Violaciones de contrato ({schema_name})",
                      attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(
            f"La respuesta no cumple el contrato '{schema_name}':\n{detail}"
        )
