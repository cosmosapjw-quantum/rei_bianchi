"""Restore generated RUN15 JSON packets losslessly from their Git gzip files."""
from pathlib import Path
import gzip
import hashlib
import json
from build_packet import write_new_or_equal

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for identity_path in sorted((ROOT / "inputs").glob("optical_n*.identity.json")):
        rec = json.loads(identity_path.read_text())
        name = rec["packet"]
        if Path(name).name != name:
            raise ValueError("unsafe packet filename")
        compressed = (ROOT / "inputs" / (name + ".gz")).read_bytes()
        if hashlib.sha256(compressed).hexdigest() != rec["compressed_sha256"]:
            raise ValueError("compressed packet identity mismatch")
        data = gzip.decompress(compressed)
        if len(data) != rec["packet_bytes"] or hashlib.sha256(data).hexdigest() != rec["packet_sha256"]:
            raise ValueError("restored packet identity mismatch")
        write_new_or_equal(ROOT / "inputs" / name, data)
        records.append({"packet": name, "sha256": rec["packet_sha256"], "status": "RESTORED_EXACT"})
    if not records:
        raise ValueError("no packet identity records")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
