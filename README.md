# silenciosynth

ONNX-first runtime package for [BlueRoseLabs/Silencio](https://huggingface.co/BlueRoseLabs/Silencio), using `kokorog2p` as the text frontend.

This repository intentionally contains the import package at the repository root (`silenciosynth/`), not under an extra `src/` directory. Versions are derived from Git tags via `setuptools_scm`.

## Repository split

- **silenciosynth**: user-facing Python runtime, G2P, bundle installation and ONNX sessions.
- **silencio-onnx-bundles**: reproducible model conversion, release assets and the public catalog.

The split mirrors `pykokoro` / `kokoro-onnx-models`, while allowing Silencio to use a multi-graph ONNX bundle.

## Install

```bash
pip install -e ".[cpu]"
```

## Frontend

```python
from silenciosynth import prepare_text

prepared = prepare_text("Hello from Silencio.")
print(prepared.phonemes)
print(prepared.input_ids)
```

`kokorog2p` owns text-to-phoneme conversion. `silenciosynth` only applies the Silencio boundary-token/max-length contract declared by the bundle.

## Catalog

By default, model metadata is loaded from:

`https://raw.githubusercontent.com/buchwandler/silencio-onnx-bundles/main/catalog/models.json`

You can use a local catalog during development:

```bash
export SILENCIOSYNTH_CATALOG_PATH=/path/to/catalog/models.json
```

## MVP runtime scope

The package already provides:

- catalog loading and validation;
- deterministic, checksum-verified bundle installation;
- `kokorog2p` frontend preparation;
- ONNX Runtime session creation for every component in `bundle.json`;
- component-level execution for exporter/runtime development.

Full end-to-end Silencio synthesis is intentionally gated by the bundle's `runtime.kind`. The first public bundle should define and test a stable `silencio-split-v1` contract before `Synthesizer.synthesize()` is considered stable. This avoids embedding guessed tensor names/shapes in the runtime.

## CLI

```bash
silenciosynth phonemize "Hello world"
silenciosynth catalog
silenciosynth install silencio-v1
silenciosynth inspect silencio-v1
```
