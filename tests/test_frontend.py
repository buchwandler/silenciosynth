import numpy as np
import silenciosynth.frontend as frontend


class Result:
    phonemes = "hɛlo"
    token_ids = [10, 11, 12]
    warnings = []


def test_prepare_text_adds_boundary_tokens(monkeypatch):
    import sys, types

    fake = types.SimpleNamespace(phonemize=lambda *a, **k: Result())
    monkeypatch.setitem(sys.modules, "kokorog2p", fake)
    out = frontend.prepare_text("hello", frontend={"max_tokens": 2, "pad_id": 0})
    assert out.input_ids.dtype == np.int64
    assert out.input_ids.tolist() == [[0, 10, 11, 0]]
