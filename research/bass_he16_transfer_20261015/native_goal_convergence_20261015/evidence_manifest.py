"""Auditable read-only SHA256 manifest for nine real native runs and remap probe."""
import argparse, csv, hashlib, json
from pathlib import Path

EXPECTED_BINARY = "32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca"
EXPECTED_SOURCE = "d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
CASES = ("ZERO", "SHEAR_HALF_MINUS", "SHEAR_HALF_PLUS")

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def verify(root, case, level, receipt):
    d = root / "runs" / case / level
    state = receipt["result"]["native_return"]
    assert receipt["status"] == "EXIT_ZERO"
    assert state["status"] == "COMPLETE_REPRESENTED_INTERVAL"
    assert state["scientific_admission"] == "NOT_ISSUED"
    assert receipt["binary_sha256"] == EXPECTED_BINARY
    assert sha(d / "source_identity.txt") == EXPECTED_SOURCE
    assert sha(d / "config.cfg") == receipt["config_sha256"]
    assert sha(d / "history.csv") == receipt["result"]["history_sha256"]
    return {"case":case,"level":level,"rows":receipt["result"]["rows"],
            "accepted":int(state["accepted"]),"history_sha256":receipt["result"]["history_sha256"]}

def main(root, out):
    s1 = json.loads((root/"experiment_001/RUN_SUMMARY.json").read_text())
    s2 = json.loads((root/"experiment_002/RUN_SUMMARY.json").read_text())
    assert s1["successful"] == 6 and s2["successes"] == 3
    r1 = {(r["case"],r["level"]):r for r in s1["records"]}
    r2 = {r["case"]:r for r in s2["receipts"]}
    runs = []
    for case in CASES:
        for level in ("baseline","refined"):
            runs.append(verify(root/"experiment_001",case,level,r1[(case,level)]))
        runs.append(verify(root/"experiment_002",case,"ultra",r2[case]))
    with (root/"REMAP_SEMIGROUP_LEDGER.csv").open(newline="") as f:
        ledger=list(csv.DictReader(f))
    assert len(ledger) == 48
    max_n = max(abs(float(r["number_ledger_residual"])) for r in ledger)
    max_e = max(abs(float(r["energy_ledger_residual"])) for r in ledger)
    assert max_n < 1e-12 and max_e < 1e-11
    files = [{"path":str(p.relative_to(root)),"bytes":p.stat().st_size,
              "sha256":sha(p)} for p in sorted(root.rglob("*")) if p.is_file()]
    res = {"schema":"he18.axbi.native_raw_sha256_manifest.v1",
           "native_runs":runs,"native_run_count":len(runs),
           "source_identity_sha256":EXPECTED_SOURCE,"binary_sha256":EXPECTED_BINARY,
           "geometry_ledger_probes":len(ledger),
           "max_abs_number_ledger_residual":max_n,
           "max_abs_energy_ledger_residual_ev_per_h":max_e,
           "file_count":len(files),"total_bytes":sum(x["bytes"] for x in files),
           "files":files,"scientific_admission":"NOT_ISSUED",
           "source_ode_error_certified":False}
    out.write_text(json.dumps(res,indent=2)+"\n")
    print(json.dumps({k:res[k] for k in
          ("native_run_count","file_count","total_bytes","geometry_ledger_probes",
           "max_abs_number_ledger_residual","max_abs_energy_ledger_residual_ev_per_h")},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    main(args.raw,args.out)
