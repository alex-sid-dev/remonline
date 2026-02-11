from dishka import Provider

from src.config.ioc.providers.db import db_provider
from src.config.ioc.providers.gateways import gateways_provider
from src.config.ioc.providers.interactors import interactors_provider
from src.config.ioc.providers.keycloak import keycloak_provider
from src.config.ioc.providers.services import services_provider
from src.config.ioc.providers.settings import SettingsProvider


def get_providers() -> list[Provider]:
    """
    Returns a list of Dishka providers for dependency injection.

    Returns:
        list[Provider]: A list of configured providers.
    """
    return [
        SettingsProvider(),
        db_provider(),
        keycloak_provider(),
        interactors_provider(),
        gateways_provider(),
        services_provider()
    ]