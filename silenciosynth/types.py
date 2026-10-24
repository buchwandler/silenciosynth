from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class InstalledBundle:
    model_id: str
    version: str
    root: Path
    manifest: Mapping[str, Any]
