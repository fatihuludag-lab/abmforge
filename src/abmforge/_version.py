from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

_PACKAGE_NAME = "abmforge"
_FALLBACK_VERSION = "0.2.0a2"


def get_version() -> str:
    """Return the installed ABMForge package version.

    The installed package metadata is the source of truth. The fallback exists
    for source-tree execution cases where package metadata is not available.
    A repository test keeps the fallback aligned with pyproject.toml.
    """
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return _FALLBACK_VERSION


__version__ = get_version()