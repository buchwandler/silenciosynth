from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
import numpy as np

from .bundle import Bundle, ComponentSpec
from .errors import RuntimeContractError


def _ort():
    try:
        import onnxruntime as ort
    except ModuleNotFoundError as exc:
        raise RuntimeContractError(
            "ONNX Runtime is not installed. Install silenciosynth[cpu], [gpu], or [directml]."
        ) from exc
    return ort


class BundleRuntime:
    def __init__(self, bundle: Bundle, *, providers: Sequence[str] | None = None):
        ort = _ort()
        requested = list(providers) if providers else None
        self.bundle = bundle
        self.sessions: dict[str, Any] = {}
        for component in bundle.components:
            path = bundle.path_for(component)
            if not path.is_file():
                raise RuntimeContractError(f"Missing ONNX component: {path}")
            kwargs = {"providers": requested} if requested else {}
            self.sessions[component.component_id] = ort.InferenceSession(str(path), **kwargs)

    def component(self, component_id: str) -> ComponentSpec:
        for spec in self.bundle.components:
            if spec.component_id == component_id:
                return spec
        raise KeyError(component_id)

    def run_component(self, component_id: str, feeds: Mapping[str, Any]) -> dict[str, np.ndarray]:
        spec = self.component(component_id)
        missing = [name for name in spec.inputs if name not in feeds]
        if missing:
            raise RuntimeContractError(f"Missing inputs for {component_id}: {', '.join(missing)}")
        session = self.sessions[component_id]
        names = [out.name for out in session.get_outputs()]
        values = session.run(None, {name: np.asarray(feeds[name]) for name in spec.inputs})
        return dict(zip(names, values))
