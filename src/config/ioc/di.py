from dishka import Provider

from src.config.ioc.providers.db import db_provider
from src.config.ioc.providers.gateways import gateways_provider
from src.config.ioc.providers.interactors import interactors_provider
from src.config.ioc.providers.keycloak import keycloak_provider
from src.config.ioc.providers.services import services_provider
from src.config.ioc.providers.settings import SettingsProvider
from src.config.settings import Settings


def get_providers(settings: Settings) -> list[Provider]:
    """
    Returns a list of Dishka providers for dependency injection.
    """
    return [
        SettingsProvider(settings),
        db_provider(),
        keycloak_provider(),
        interactors_provider(),
        gateways_provider(),
        services_provider(),
    ]
