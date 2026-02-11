from dataclasses import dataclass

from src.application.errors._base import KeycloakError


@dataclass
class KeyCloakRuntimeError(KeycloakError):

    @property
    def message(self) -> str:
        return "Keycloak runtime error"
