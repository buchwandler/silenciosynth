from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Mapping

from .errors import CatalogError

DEFAULT_CATALOG_URL = (
    "https://raw.githubusercontent.com/buchwandler/silencio-onnx-bundles/main/catalog/models.json"
)


@dataclass(frozen=True, slots=True)
class CatalogModel:
    model_id: str
    version: str
    release_tag: str
    bundle_url: str
    sha256: str
    size: int
    sample_rate: int
    runtime_kind: str
    data: Mapping[str, Any]


def _validate(data: Mapping[str, Any]) -> None:
    if data.get("schema") != 1 or not isinstance(data.get("models"), dict):
        raise CatalogError("Unsupported or invalid Silencio catalog")


class CatalogClient:
    def __init__(self, *, url: str | None = None, path: str | Path | None = None):
        env_path = os.environ.get("SILENCIOSYNTH_CATALOG_PATH")
        self.path = Path(path or env_path).expanduser() if (path or env_path) else None
        self.url = url or os.environ.get("SILENCIOSYNTH_CATALOG_URL", DEFAULT_CATALOG_URL)

    def load(self) -> Mapping[str, Any]:
        if self.path is not None:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            with urllib.request.urlopen(self.url, timeout=30) as response:
                data = json.load(response)
        _validate(data)
        return data

    def models(self) -> tuple[CatalogModel, ...]:
        data = self.load()
        return tuple(self._model(k, v) for k, v in data["models"].items())

    def model(self, model_id: str) -> CatalogModel:
        data = self.load()
        try:
            raw = data["models"][model_id]
        except KeyError as exc:
            raise CatalogError(f"Unknown Silencio model: {model_id}") from exc
        return self._model(model_id, raw)

    @staticmethod
    def _model(model_id: str, raw: Mapping[str, Any]) -> CatalogModel:
        asset = raw.get("bundle") or {}
        runtime = raw.get("runtime") or {}
        required = ["version", "release_tag", "sample_rate"]
        if (
            any(key not in raw for key in required)
            or not asset.get("url")
            or not asset.get("sha256")
        ):
            raise CatalogError(f"Catalog entry {model_id!r} is incomplete")
        return CatalogModel(
            model_id=model_id,
            version=str(raw["version"]),
            release_tag=str(raw["release_tag"]),
            bundle_url=str(asset["url"]),
            sha256=str(asset["sha256"]),
            size=int(asset.get("size", 0)),
            sample_rate=int(raw["sample_rate"]),
            runtime_kind=str(runtime.get("kind", "unknown")),
            data=raw,
        )
