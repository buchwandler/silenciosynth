from __future__ import annotations

from pathlib import Path
from typing import Any
from collections.abc import Sequence
import numpy as np

from .bundle import load_bundle
from .catalog import CatalogClient
from .errors import RuntimeContractError
from .frontend import PreparedText, prepare_text
from .runtime import BundleRuntime
from .store import BundleStore


class Synthesizer:
    def __init__(self, root: str | Path, *, providers: Sequence[str] | None = None):
        self.bundle = load_bundle(root)
        self.runtime = BundleRuntime(self.bundle, providers=providers)

    @classmethod
    def from_catalog(
        cls,
        model_id: str = "silencio-v1",
        *,
        catalog: CatalogClient | None = None,
        store: BundleStore | None = None,
        providers: Sequence[str] | None = None,
    ) -> Synthesizer:
        model = (catalog or CatalogClient()).model(model_id)
        root = (store or BundleStore()).install(model)
        return cls(root, providers=providers)

    def prepare(self, text: str) -> PreparedText:
        return prepare_text(text, frontend=self.bundle.frontend)

    def synthesize(
        self,
        text: str,
        *,
        reference_audio: np.ndarray,
        reference_sample_rate: int = 16000,
        **options: Any,
    ) -> np.ndarray:
        if self.bundle.runtime_kind != "silencio-e2e-v1":
            raise RuntimeContractError(
                "This MVP can load and execute bundle components, but end-to-end synthesis requires "
                "a stabilized silencio-e2e-v1 adapter or the planned silencio-split-v1 orchestrator. "
                "Use runtime.run_component(...) while developing the first exporter contract."
            )
        prepared = self.prepare(text)
        result = self.runtime.run_component(
            "model",
            {
                "input_ids": prepared.input_ids,
                "reference_audio": np.asarray(reference_audio, dtype=np.float32)[None, :],
                "reference_sample_rate": np.asarray([reference_sample_rate], dtype=np.int64),
            },
        )
        try:
            audio = result["audio"]
        except KeyError as exc:
            raise RuntimeContractError("silencio-e2e-v1 model did not return 'audio'") from exc
        return np.asarray(audio, dtype=np.float32).reshape(-1)
