from dishka import Provider, Scope

from src.application.ports.error_log_writer import ErrorLogWriter
from src.config._discovery import discover_gateway_bindings
from src.infra.adapters.error_log_writer import ErrorLogWriterAdapter


def gateways_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)

    for adapter_cls, port_cls in discover_gateway_bindings("src.infra.adapters"):
        provider.provide(adapter_cls, provides=port_cls)

    # ErrorLogWriterAdapter uses structural typing (no inheritance) and APP scope
    provider.provide(ErrorLogWriterAdapter, provides=ErrorLogWriter, scope=Scope.APP)

    return provider
