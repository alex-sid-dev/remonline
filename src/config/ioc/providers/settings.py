from dishka import Provider, Scope, provide

from src.config.settings import Settings


class SettingsProvider(Provider):
    """
    Provides application settings.
    """

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        """
        Provides the Settings instance.
        """
        return Settings()