"""Bounded exact-kernel preparation timings; no old solver campaign is run."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
HERE = Path(__file__).resolve().parent


def digest_pairs(pairs):
    canonical = [[str(x) for x in pair] for pair in pairs]
    return hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()


def phase(name):
    from flint import ctx
    from wu088_hh.phys67_first_born import serialize_ball
    from wu088_hh import phys67_first_born as old
    from wu088_hh import phys68_angular as new
    selected = sorted({tuple(sorted((ell, j))) for ell in (20, 21) for j in range(29)})
    module = old if name == "prior_rows" else new
    begin = perf_counter()
    pair_hashes = {f"{ell},{p}": digest_pairs(module.angular_laurent_pairs(ell, p))
                   for ell, p in selected}
    exact_seconds = perf_counter()-begin
    begin = perf_counter()
    for ell, p in selected:
        module.angular_coefficients_ball(ell, p, 1024)
    ball_seconds = perf_counter()-begin
    result = {"phase": name, "pair_count": len(selected), "pair_hashes": pair_hashes,
              "exact_pair_preparation_seconds": exact_seconds,
              "ball_coefficient_preparation_seconds": ball_seconds,
              "coefficient_bits": 1024, "cache_at_start": "FRESH_CHILD_PROCESS"}
    if name == "optimized_rows":
        begin = perf_counter()
        witnesses = []
        for ell, p in selected:
            coefficients = new.angular_taylor_coefficients(ell, p, F(61, 2), 24)
            witnesses.append({"ell": ell, "ellprime": p,
                              "coefficient_0": serialize_ball(coefficients[0]),
                              "coefficient_24": serialize_ball(coefficients[24]),
                              "all_coefficients_finite": all(c.is_finite() for c in coefficients)})
        result["taylor57"] = {
            "center": "61/2", "degree": 24, "precision_bits": 384,
            "wall_seconds": perf_counter()-begin, "witnesses": witnesses,
            "operation": "ACTUAL_ANGULAR_TAYLOR_PREPARATION_NOT_D1_OR_D2_SOLVE"}
        begin = perf_counter()
        full = {(ell, p): new.angular_laurent_pairs(ell, p)
                for ell in range(29) for p in range(ell+1)}
        result["full435"] = {
            "pair_count": len(full),
            "exact_pair_preparation_seconds": perf_counter()-begin,
            "cache_at_start": "ROW57_CACHE_ALREADY_PREPARED",
            "operation": "EXACT_ANGULAR_COEFFICIENT_PREPARATION_ONLY",
            "all_coefficients_fraction": all(type(x) is F for v in full.values()
                                             for pair in v for x in pair),
            "sha256": hashlib.sha256(json.dumps(
                {f"{l},{p}": digest_pairs(v) for (l, p), v in full.items()},
                sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        }
        result["cache_final"] = new.angular_cache_info()
        result["context_final"] = {"prec": ctx.prec, "cap": ctx.cap}
    return result


def main():
    output = HERE / "PREPARATION_RESULT.json"
    if output.exists():
        raise SystemExit("Preserved result exists; choose a separate evidence location before a justified rerun.")
    records = []
    for name in ("prior_rows", "optimized_rows"):
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--phase", name],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60)
        (HERE / f"{name}.stdout.json").write_text(process.stdout)
        (HERE / f"{name}.stderr.txt").write_text(process.stderr)
        if process.returncode:
            raise RuntimeError(f"{name} failed with exit={process.returncode}; output retained")
        records.append(json.loads(process.stdout))
    prior, optimized = records
    result = {
        "schema": "PHYS68_ANGULAR_PREPARATION_V1",
        "status": "PASS_EXACT_REFACTOR_AND_NEW_TAYLOR_PREPARATION",
        "same57_exact_pair_hashes": prior["pair_hashes"] == optimized["pair_hashes"],
        "prior_rows_seconds": prior["exact_pair_preparation_seconds"],
        "optimized_rows_seconds": optimized["exact_pair_preparation_seconds"],
        "measured_exact_preparation_speed_ratio": (prior["exact_pair_preparation_seconds"] /
                                                     optimized["exact_pair_preparation_seconds"]),
        "timing_scope": "One observation in separate fresh child processes; both timed phases include canonical Fraction serialization and SHA256; no universal performance guarantee.",
        "new_taylor_pair_count": optimized["pair_count"],
        "new_taylor_coefficients_total": optimized["pair_count"]*25,
        "new_taylor_seconds": optimized["taylor57"]["wall_seconds"],
        "all_taylor_coefficients_finite": all(x["all_coefficients_finite"]
                                             for x in optimized["taylor57"]["witnesses"]),
        "full435": optimized["full435"],
        "versions": {"python": sys.version.split()[0],
                     "python-flint": importlib.metadata.version("python-flint")},
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (ROOT/"src/wu088_hh/phys68_angular.py",
                                       ROOT/"tests/test_phys68_angular.py",
                                       ROOT/"src/wu088_hh/phys67_first_born.py")},
        "executed": {"exact_coefficient_microbenchmarks": 2,
                     "new_angular_taylor_preparations": 57,
                     "D1_integrations": 0, "D2_integrations": 0,
                     "old_scientific_campaigns": 0, "NCP_solver": 0},
        "HH_R10": "OFF",
    }
    if not result["same57_exact_pair_hashes"] or not result["all_taylor_coefficients_finite"]:
        result["status"] = "FAIL"
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--phase":
        print(json.dumps(phase(sys.argv[2]), indent=2))
    else:
        main()
