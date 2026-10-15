#!/usr/bin/env python3
"""Create a fresh, allowlisted NCP source bundle after controller source freeze."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.output.exists():
        raise SystemExit("fresh archive path required")
    crate = Path("rust/rei_microphysics")
    scope = Path("research/flrw_covariant_transport_20261015")
    files = {crate / "Cargo.toml", crate / "Cargo.lock",
             crate / "examples/axbi_reionization.rs", crate / "examples/eval_fixture.rs"}
    files.update(p.relative_to(repo) for p in (repo / crate / "src").rglob("*.rs"))
    files.update({crate / "tests/axbi_covariant_transport.rs", crate / "tests/axbi_covariant_driver.rs"})
    files.update({crate / "tests/axbi_covariant_partition.rs", crate / "tests/axbi_inactive_driver.rs"})
    files.update({crate / "examples/axbi_hpc_scaling.rs", crate / "tests/axbi_transport_parallel.rs"})
    driver = repo / crate / "src/axbi_driver.rs"
    identity = driver.read_text().split("pub fn compiled_identity() -> String {", 1)[1]
    identity = identity.split("fn ledger_values", 1)[0]
    for relative in re.findall(r'include_str!\(\s*"([^"]+)"\s*\)', identity):
        files.add((driver.parent / relative).resolve().relative_to(repo))
    files.update(p.relative_to(repo) for p in (repo / scope / "configs").glob("*.cfg"))
    files.update(p.relative_to(repo) for p in (repo / scope / "execution").rglob("*.py"))
    files.update({scope / "NATIVE_CONTRACT.md", scope / "NCP_PREFLIGHT.md"})
    payload = {str(p): (repo / p).read_bytes() for p in sorted(files)}
    manifest = "".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n"
                       for name, data in payload.items()).encode()
    payload["SOURCE_SHA256SUMS.txt"] = manifest
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, data in sorted(payload.items()):
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    member.mode = 0o644
                    member.mtime = 0
                    archive.addfile(member, io.BytesIO(data))
    receipt = {"archive": str(args.output.resolve()), "members": len(payload),
               "bytes": args.output.stat().st_size,
               "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
               "source_manifest_sha256": hashlib.sha256(manifest).hexdigest()}
    receipt_path = args.output.with_suffix(args.output.suffix + ".receipt.json")
    with receipt_path.open("x") as out:
        json.dump(receipt, out, indent=2)
        out.write("\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
