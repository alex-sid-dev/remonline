from dataclasses import dataclass

from src.application.errors._base import VaultError


@dataclass
class VaultRuntimeError(VaultError):

    @property
    def message(self) -> str:
        return "Vault runtime error"
