import json
from silenciosynth.catalog import CatalogClient


def test_local_catalog(tmp_path):
    path = tmp_path / "models.json"
    path.write_text(
        json.dumps(
            {
                "schema": 1,
                "models": {
                    "silencio-v1": {
                        "version": "1",
                        "release_tag": "silencio-v1-r1",
                        "sample_rate": 16000,
                        "runtime": {"kind": "silencio-split-v1"},
                        "bundle": {
                            "url": "https://example.invalid/a.zip",
                            "sha256": "a" * 64,
                            "size": 1,
                        },
                    }
                },
            }
        )
    )
    model = CatalogClient(path=path).model("silencio-v1")
    assert model.sample_rate == 16000
    assert model.runtime_kind == "silencio-split-v1"
