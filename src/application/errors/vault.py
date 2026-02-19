from dataclasses import dataclass

from src.application.errors._base import VaultError


@dataclass(eq=False)
class VaultRuntimeError(VaultError):
    message: str = "Vault runtime error"
