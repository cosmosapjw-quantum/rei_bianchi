"""Download small author-maintained atomic data files; no source evaluation."""
from pathlib import Path
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
TARGETS = {
    "verner_ferland_table1.dat": "https://www.pa.uky.edu/~verner/dima/rec/table1.dat",
    "verner_ferland_table_description.txt": "https://www.pa.uky.edu/~verner/dima/rec/table.txt",
    "verner_recombination_index.html": "https://www.pa.uky.edu/~verner/rec.html",
}

def main():
    out = ROOT / "primary_sources"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, url in TARGETS.items():
        request = urllib.request.Request(url, headers={"User-Agent": "REI-RUN19-research-source-recovery/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
            metadata = {"status": response.status, "final_url": response.url,
                        "content_type": response.headers.get("Content-Type")}
        target = out / name
        if target.exists() and target.read_bytes() != data:
            raise RuntimeError(f"Refusing to overwrite changed source: {target}")
        target.write_bytes(data)
        rows.append({"path": str(target.relative_to(ROOT)), "requested_url": url,
                     "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), **metadata})
    receipt = {"unit": "RUN19_PRIMARY_ATOMIC_SOURCE_FETCH", "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "sources": rows,
               "scientific_evaluations": 0}
    target = ROOT / "PRIMARY_FETCH_RECEIPT.json"
    target.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
