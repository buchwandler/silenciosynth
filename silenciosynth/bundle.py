from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Mapping

from .errors import RuntimeContractError


@dataclass(frozen=True, slots=True)
class ComponentSpec:
    component_id: str
    file: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Bundle:
    root: Path
    model_id: str
    version: str
    sample_rate: int
    runtime_kind: str
    frontend: Mapping[str, Any]
    components: tuple[ComponentSpec, ...]
    raw: Mapping[str, Any]

    def path_for(self, component: ComponentSpec) -> Path:
        path = (self.root / component.file).resolve()
        if self.root.resolve() not in path.parents:
            raise RuntimeContractError(f"Component escapes bundle root: {component.file}")
        return path


def load_bundle(root: str | Path) -> Bundle:
    root = Path(root)
    data = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise RuntimeContractError("Unsupported bundle schema")
    runtime = data.get("runtime") or {}
    components = []
    for raw in data.get("components", []):
        components.append(
            ComponentSpec(
                component_id=str(raw["id"]),
                file=str(raw["file"]),
                inputs=tuple(str(x) for x in raw.get("inputs", [])),
                outputs=tuple(str(x) for x in raw.get("outputs", [])),
            )
        )
    if not components:
        raise RuntimeContractError("Bundle declares no ONNX components")
    return Bundle(
        root=root,
        model_id=str(data["model_id"]),
        version=str(data["version"]),
        sample_rate=int(data.get("sample_rate", 16000)),
        runtime_kind=str(runtime.get("kind", "unknown")),
        frontend=data.get("frontend") or {},
        components=tuple(components),
        raw=data,
    )
