"""Read-only payload verification. Does not run research, native code or tests."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
manifest_path = root / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text())
checked = 0
for item in manifest["files"]:
    rel = Path(item["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("unsafe manifest path")
    path = root / rel
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing or non-regular payload: " + str(rel))
    data = path.read_bytes()
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        raise ValueError("payload identity mismatch: " + str(rel))
    checked += 1
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
expected = {x["path"] for x in manifest["files"]} | {"MANIFEST.json", "SHA256SUMS"}
if actual != expected:
    raise ValueError("unmanifested or missing files: " + repr(sorted(actual ^ expected)))
print(json.dumps({"status": "PAYLOAD_HASHES_VERIFIED", "payload_files": checked,
                  "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                  "native_authority": False, "research_executed": False}))
