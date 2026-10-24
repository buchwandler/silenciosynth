from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from platformdirs import user_cache_dir

from .catalog import CatalogModel
from .errors import IntegrityError


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class BundleStore:
    def __init__(self, root: str | Path | None = None):
        configured = os.environ.get("SILENCIOSYNTH_HOME")
        self.root = Path(root or configured or user_cache_dir("silenciosynth")).expanduser()

    def install(self, model: CatalogModel) -> Path:
        target = self.root / "models" / model.model_id / model.version
        manifest = target / "bundle.json"
        if manifest.is_file():
            return target
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="silenciosynth-") as tmp_name:
            tmp = Path(tmp_name)
            archive = tmp / "bundle.zip"
            urllib.request.urlretrieve(model.bundle_url, archive)
            digest = sha256_file(archive)
            if digest != model.sha256:
                raise IntegrityError(
                    f"Bundle checksum mismatch for {model.model_id}: expected {model.sha256}, got {digest}"
                )
            unpacked = tmp / "unpacked"
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(unpacked)
            roots = [p for p in unpacked.iterdir() if p.is_dir()]
            source = (
                roots[0] if len(roots) == 1 and (roots[0] / "bundle.json").is_file() else unpacked
            )
            if not (source / "bundle.json").is_file():
                raise IntegrityError("Downloaded bundle does not contain bundle.json")
            stage = target.with_name(target.name + ".tmp")
            if stage.exists():
                shutil.rmtree(stage)
            shutil.copytree(source, stage)
            stage.replace(target)
        return target
