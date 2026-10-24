import json
from silenciosynth.bundle import load_bundle


def test_bundle_manifest(tmp_path):
    (tmp_path / "bundle.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "model_id": "silencio-v1",
                "version": "1",
                "sample_rate": 16000,
                "runtime": {"kind": "silencio-split-v1"},
                "frontend": {"max_tokens": 510, "pad_id": 0},
                "components": [
                    {
                        "id": "text_encoder",
                        "file": "text_encoder.onnx",
                        "inputs": ["input_ids"],
                        "outputs": ["features"],
                    }
                ],
            }
        )
    )
    bundle = load_bundle(tmp_path)
    assert bundle.model_id == "silencio-v1"
    assert bundle.components[0].component_id == "text_encoder"
