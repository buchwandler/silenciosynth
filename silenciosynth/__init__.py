from __future__ import annotations

try:
    from ._version import __version__
except ImportError:
    try:
        from importlib.metadata import version

        __version__ = version("silenciosynth")
    except Exception:
        __version__ = "0.0.0"

from .bundle import Bundle, ComponentSpec, load_bundle
from .catalog import CatalogClient, CatalogModel
from .frontend import PreparedText, prepare_text
from .synthesizer import Synthesizer

__all__ = [
    "__version__",
    "Bundle",
    "ComponentSpec",
    "CatalogClient",
    "CatalogModel",
    "PreparedText",
    "Synthesizer",
    "load_bundle",
    "prepare_text",
]
