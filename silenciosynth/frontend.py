from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from collections.abc import Mapping

import numpy as np


@dataclass(frozen=True, slots=True)
class PreparedText:
    text: str
    phonemes: str
    input_ids: np.ndarray
    warnings: tuple[str, ...]


def prepare_text(
    text: str,
    *,
    language: str = "en-us",
    frontend: Mapping[str, Any] | None = None,
) -> PreparedText:
    cfg = dict(frontend or {})
    max_tokens = int(cfg.get("max_tokens", 510))
    pad_id = int(cfg.get("pad_id", 0))
    target_model = cfg.get("target_model") or "kokoro"
    from kokorog2p import phonemize

    result = phonemize(
        text,
        language=language,
        return_ids=True,
        return_phonemes=True,
        target_model=str(target_model),
    )
    core = [int(x) for x in result.token_ids[:max_tokens]]
    ids = np.asarray([pad_id, *core, pad_id], dtype=np.int64)[None, :]
    return PreparedText(
        text=text, phonemes=result.phonemes, input_ids=ids, warnings=tuple(result.warnings)
    )
