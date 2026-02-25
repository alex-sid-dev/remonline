"""Auto-discovery utilities for DI registration and table mapping."""

import importlib
import inspect
from collections.abc import Callable
from pathlib import Path


def _iter_module_names(package_path: str) -> list[str]:
    """Return fully-qualified module names for every .py file in a package tree."""
    pkg = importlib.import_module(package_path)
    base_dir = Path(pkg.__path__[0])
    modules: list[str] = []

    for py_file in sorted(base_dir.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue
        relative = py_file.relative_to(base_dir)
        parts = list(relative.with_suffix("").parts)
        modules.append(f"{package_path}.{'.'.join(parts)}")

    return modules


def discover_classes(package_path: str, *, suffix: str) -> list[type]:
    """Find all classes whose name ends with *suffix* defined in *package_path*."""
    result: list[type] = []
    for mod_name in _iter_module_names(package_path):
        try:
            module = importlib.import_module(mod_name)
        except Exception:  # noqa: BLE001
            continue
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith(suffix) and obj.__module__ == mod_name:
                result.append(obj)
    return result


def discover_functions(
    package_path: str,
    *,
    prefix: str = "",
    suffix: str = "",
) -> list[Callable[..., object]]:
    """Find all top-level functions matching *prefix* and *suffix*."""
    result: list[Callable[..., object]] = []
    for mod_name in _iter_module_names(package_path):
        try:
            module = importlib.import_module(mod_name)
        except Exception:  # noqa: BLE001
            continue
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if (
                obj.__module__ == mod_name
                and name.startswith(prefix)
                and name.endswith(suffix)
            ):
                result.append(obj)
    return result


def discover_gateway_bindings(
    adapters_package: str,
    ports_module_prefix: str = "src.application.ports",
) -> list[tuple[type, type]]:
    """Discover adapter -> port bindings by inspecting base classes.

    Returns ``(adapter_class, port_class)`` pairs for every adapter that
    directly inherits from a type whose module starts with *ports_module_prefix*.
    """
    bindings: list[tuple[type, type]] = []
    for mod_name in _iter_module_names(adapters_package):
        try:
            module = importlib.import_module(mod_name)
        except Exception:  # noqa: BLE001
            continue
        for _name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != mod_name:
                continue
            for base in cls.__mro__[1:]:
                base_mod = getattr(base, "__module__", "")
                if base_mod.startswith(ports_module_prefix):
                    bindings.append((cls, base))
    return bindings
