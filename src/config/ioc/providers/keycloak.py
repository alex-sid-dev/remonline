from dishka import Provider, Scope

from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.infra.keycloak.admin_manager import KeycloakAdminManager
from src.infra.keycloak.open_id_manager import KeycloakOpenIDManager


def keycloak_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide(KeycloakAdminManager, provides=AdminManager)
    _ = provider.provide(KeycloakOpenIDManager, provides=OpenIDManager)
    return provider
