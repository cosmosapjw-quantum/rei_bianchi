"""Independent standard-library checks of emitted raw bytes, labels, and ledgers.

No Rust source is translated here. This checks the exported binary equality and
reconstructs linear number/energy/age moments independently using math.fsum.
Timing summaries describe these sessions; they are not confidence/gating claims.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]

def analyze(directory):
    contract = json.loads((directory / "CONTRACT.json").read_text())
    blobs = [(directory / f"PATH_BITS_{mode}.bin").read_bytes()
             for mode in ["baseline", "cached", "parallel"]]
    assert blobs[0] == blobs[1] == blobs[2]
    assert len(blobs[0]) == contract["unique_paths"] * 41 * 8
    ledger_raw = None
    if (directory/"LEDGER_BITS_baseline.bin").exists():
        ledger_blobs=[(directory/f"LEDGER_BITS_{mode}.bin").read_bytes()
                      for mode in ["baseline","cached","parallel"]]
        assert ledger_blobs[0] == ledger_blobs[1] == ledger_blobs[2]
        assert len(ledger_blobs[0]) == 33*8
        ledger_raw=hashlib.sha256(ledger_blobs[0]).hexdigest()
    rows = list(csv.DictReader((directory / "BIRTH_PATHS.csv").open()))
    assert len(rows) == contract["births"]
    assert len({(int(r["template"]), int(r["node"])) for r in rows}) == len(rows)
    assert [(int(r["template"]), int(r["node"])) for r in rows] == sorted(
        (int(r["template"]), int(r["node"])) for r in rows)
    assert len({int(r["template"]) for r in rows}) == contract["templates"]
    assert all(int(r["spectral"]) == int(r["template"]) // 8 for r in rows)
    assert all(int(r["angular"]) == int(r["template"]) % 8 for r in rows)
    original_prefix_checked = 0
    if (contract["case"] == "SIGNED_MINUS" and contract["birth_refinement"] == 1
            and contract["path_slabs"] == 2 and contract["opacity_degree"] == 2
            and contract["event_degree"] == 4):
        original = list(csv.DictReader((ROOT/"evidence/test_original_run/BIRTHS.csv").open()))
        matched = {(int(r["template"]),int(r["node"])):r for r in rows}
        names = {"target_age":"target_age", "emission_weight":"emission_weight",
                 "birth_time_s":"birth_time_s", "birth_energy_ev":"energy_ev",
                 "born_com3":"born", "survival":"survival", "spectral":"spectral",
                 "angular":"angular"}
        for j in [1,2,3]:
            names.update({f"birth_a{j}":f"a{j}",f"birth_H{j}":f"H{j}",
                          f"birth_n{j}":f"n{j}",f"K{j}":f"K{j}"})
        for old in original:
            new=matched[(int(old["template"]),int(old["node"]))]
            for old_key,new_key in names.items():
                assert float(old[old_key]).hex() == float(new[new_key]).hex(), (old_key,new_key)
            original_prefix_checked+=1
    max_number = 0.0
    max_k_relative = 0.0
    number_terms = []
    energy_terms = []
    for row in rows:
        f = {key: float(value) for key, value in row.items()
             if key not in {"template", "node", "spectral", "angular", "path_fingerprint"}}
        assert all(math.isfinite(value) for value in f.values())
        assert f["born"] >= 0.0 and 0.0 <= f["survival"] <= 1.0
        assert all(f[sp] >= 0.0 for sp in ["HI", "HeI", "HeII", "DI"])
        assert 0.0 <= f["birth_time_s"] < 5e11
        assert abs((5e11-f["birth_time_s"])/5e11 - f["target_age"]) < 3e-16
        total = math.fsum([f["survival"],f["HI"],f["HeI"],f["HeII"],f["DI"]]) - 1.0
        max_number = max(max_number, abs(total))
        assert abs(total - f["number_residual"]) < 2e-15
        number_terms.append(f["born"] * total)
        energy_residual = math.fsum([f["surviving_energy_ev"],f["absorbed_energy_ev"],
                                    -f["energy_ev"],-f["work_independent_ev"]])
        assert abs(energy_residual-f["energy_residual_ev"]) <= 2e-12 * f["energy_ev"]
        energy_terms.append(f["born"] * energy_residual * 1.602176634e-19)
        norm = math.hypot(math.hypot(f["n1"], f["n2"]), f["n3"])
        assert abs(norm-1.0) < 1e-12
        for index in [1,2,3]:
            expected = f[f"a{index}"]*f["energy_ev"]*(f[f"n{index}"]/norm)
            actual = f[f"K{index}"]
            if expected == 0.0:
                assert actual == 0.0
            else:
                relative = abs(actual/expected - 1.0)
                max_k_relative = max(max_k_relative, relative)
                assert relative < 3e-15
    survivor = math.fsum(float(r["born"])*float(r["survival"]) for r in rows)
    born = math.fsum(float(r["born"]) for r in rows)
    age = math.fsum(float(r["born"])*float(r["survival"])*(5e11-float(r["birth_time_s"])) for r in rows)
    age2 = math.fsum(float(r["born"])*float(r["survival"])*(5e11-float(r["birth_time_s"]))**2 for r in rows)
    timing = list(csv.DictReader((directory/"TIMINGS.csv").open()))
    assert len({r["checksum"] for r in timing}) == 1
    assert len({r["paths"] for r in timing}) == 1
    assert len({r["samples"] for r in timing}) == 1
    pairs = sorted({int(r["pair"]) for r in timing if r["stage"] == "paired"})
    measures = {}
    for mode in ["cached","parallel"]:
        ratios=[]
        base_seconds=[]
        candidate_seconds=[]
        for pair in pairs:
            selected={int(r["position"]):r for r in timing if r["stage"] == "paired" and int(r["pair"])==pair}
            if mode == "cached":
                a,b=(0,1) if pair%2==0 else (3,2)
            else:
                a,b=(2,3) if pair%2==0 else (1,0)
            assert selected[a]["mode"] == "baseline" and selected[b]["mode"] == mode
            base=float(selected[a]["seconds"]); candidate=float(selected[b]["seconds"])
            base_seconds.append(base); candidate_seconds.append(candidate); ratios.append(base/candidate)
        measures[mode]={"pairs":len(ratios),"median_log_speedup_exp":math.exp(statistics.median(map(math.log,ratios))),
                        "min_pair_speedup":min(ratios),"max_pair_speedup":max(ratios),
                        "baseline_median_seconds":statistics.median(base_seconds),
                        "candidate_median_seconds":statistics.median(candidate_seconds)}
    aa=[]
    for pair in sorted({int(r["pair"]) for r in timing if r["stage"] == "aa"}):
        selected=sorted((r for r in timing if r["stage"] == "aa" and int(r["pair"])==pair),key=lambda r:int(r["position"]))
        aa.append(float(selected[0]["seconds"])/float(selected[1]["seconds"]))
    return {"case": contract["case"],"templates":contract["templates"],"births":len(rows),
            "unique_paths":contract["unique_paths"],"path_raw_bytes_sha256":hashlib.sha256(blobs[0]).hexdigest(),
            "raw_byte_parity":True,"label_order_completeness":True,"independent_ledger_checks":True,
            "ledger_raw_bytes_sha256":ledger_raw,
            "original_BR06_prefix_birth_rows_bitwise_equal":original_prefix_checked,
            "max_number_residual_per_path":max_number,"number_residual_fsum":math.fsum(number_terms),
            "energy_residual_j_fsum":math.fsum(energy_terms),"max_K_relative_reconstruction_error":max_k_relative,
            "born_fsum":born,"surviving_fsum":survivor,"survival_age_sum_s":age,"survival_age2_sum_s2":age2,
            "timing":measures,"aa_ratios":aa,"aa_median":statistics.median(aa),
            "independent_processes":len({r["session"] for r in timing}),
            "timing_admission":"EXPLORATORY; no six-session paired-timing confirmatory gate"}

if __name__ == "__main__":
    directories = [Path(name) for name in sys.argv[1:]] if len(sys.argv)>1 else sorted((ROOT/"evidence").glob("bench_*"))
    results=[]
    for directory in directories:
        if not (directory/"CONTRACT.json").exists():
            continue
        result=analyze(directory)
        (directory/"PYTHON_VERIFICATION.json").write_text(json.dumps(result,indent=2)+"\n")
        results.append(result)
    assert results
    (ROOT/"evidence/RESULTS.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))
