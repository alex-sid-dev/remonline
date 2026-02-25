from dishka import Provider, Scope

from src.config._discovery import discover_classes


def interactors_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    handlers = discover_classes("src.application.commands", suffix="CommandHandler")
    provider.provide_all(*handlers)
    return provider
