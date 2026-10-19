#!/usr/bin/env python3
"""Create a new build copy using an explicitly supplied original native crate.

The checked-in template uses the canonical run15/postloss_native location.
This helper changes only the dependency path in the new copy's Cargo.toml.
It never edits the template, the recovered literal source, or the owner crate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path, help="Original rei_bass_coupled crate, containing Cargo.toml")
    parser.add_argument("--output-root", required=True, type=Path, help="New materialized crate directory")
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True)
    template = Path(__file__).resolve().parent
    target = args.output_root.absolute()
    if not (source / "Cargo.toml").is_file() or not (source / "src/spectral_edge_support.rs").is_file():
        raise ValueError("source-root is not the preserved native crate")
    if target.exists() or target.is_symlink():
        raise ValueError("output-root must be new")
    if target == template or template in target.parents or source == target or source in target.parents:
        raise ValueError("output-root must be separate from the template and original owner")
    target.mkdir(parents=True)
    rows = []
    names = ["Cargo.toml", "src/lib.rs", "src/main.rs"]
    if (template / "Cargo.lock").is_file():
        names.append("Cargo.lock")
    canonical = 'path = "../../run13/recovered/code/rei_bass_coupled"'
    dependency = 'path = ' + json.dumps(os.path.relpath(source, target))
    for name in names:
        original = (template / name).read_bytes()
        changed = original
        if name == "Cargo.toml":
            text = original.decode("utf-8")
            if text.count(canonical) != 1:
                raise ValueError("template dependency marker changed")
            changed = text.replace(canonical, dependency).encode("utf-8")
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as stream:
            stream.write(changed)
        rows.append({"path": name, "template_sha256": digest(original), "materialized_sha256": digest(changed),
                     "bytes": len(changed), "unchanged": original == changed})
    receipt = {"status": "MATERIALIZED_NEW_COPY", "template": str(template), "original_owner_crate": str(source),
               "output_root": str(target), "dependency_path": os.path.relpath(source, target),
               "original_owner_manifest_sha256": digest((source / "Cargo.toml").read_bytes()), "files": rows,
               "builds": 0, "tests": 0, "ivps": 0}
    with (target / "MATERIALIZATION.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
