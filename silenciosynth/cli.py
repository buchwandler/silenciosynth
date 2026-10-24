from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bundle import load_bundle
from .catalog import CatalogClient
from .frontend import prepare_text
from .store import BundleStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="silenciosynth")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("phonemize")
    p.add_argument("text")
    p = sub.add_parser("catalog")
    p.add_argument("--path")
    p = sub.add_parser("install")
    p.add_argument("model_id", nargs="?", default="silencio-v1")
    p.add_argument("--catalog")
    p = sub.add_parser("inspect")
    p.add_argument("path")
    args = parser.parse_args(argv)

    if args.cmd == "phonemize":
        r = prepare_text(args.text)
        print(r.phonemes)
        print(r.input_ids.tolist())
    elif args.cmd == "catalog":
        c = CatalogClient(path=args.path) if args.path else CatalogClient()
        print(json.dumps(c.load(), indent=2, ensure_ascii=False))
    elif args.cmd == "install":
        c = CatalogClient(path=args.catalog) if args.catalog else CatalogClient()
        root = BundleStore().install(c.model(args.model_id))
        print(root)
    elif args.cmd == "inspect":
        b = load_bundle(Path(args.path))
        print(json.dumps(b.raw, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
