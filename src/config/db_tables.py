from src.config._discovery import discover_functions


def map_tables() -> None:
    for mapper_fn in discover_functions("src.infra.models", prefix="map_", suffix="_table"):
        mapper_fn()
