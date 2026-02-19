from dataclasses import dataclass

from src.application.errors._base import KeycloakError


@dataclass(eq=False)
class KeyCloakRuntimeError(KeycloakError):
    message: str = "Keycloak runtime error"
