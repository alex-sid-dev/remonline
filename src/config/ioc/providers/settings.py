from dishka import Provider, Scope, provide

from src.config.settings import Settings


class SettingsProvider(Provider):
    """Provides application settings."""

    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return self._settings
