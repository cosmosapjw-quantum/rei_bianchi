"""Bounded addendum to the saved 99-channel subtraction-leaf audit.

Reuses the frozen first audit, weights its exact defects by the archived
stored stock and source-diagnostic sigma, and constructs a generic 100 eV
subtraction witness. It does not rerun the archived energy diagnostic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import time
from fractions import Fraction
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rat(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--first-leaf-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    start = time.monotonic()
    assert sha(args.input) == "1f462e7fa7c1d4251c5004194c42b0e471fe5c42303962f1a40d5d5062f1923d"
    assert sha(args.first_leaf_audit) == "a3ae31edda43b7f68ded303d12aeb62ccc061d463f8fc26a2a8edb26b1e7814e"
    source_input = json.loads(args.input.read_text())
    first = json.loads(args.first_leaf_audit.read_text())
    assert len(first["rows"]) == 99
    species = ["HI", "HeI", "HeII"]
    exact = Fraction.from_float
    weighted = []
    for row in first["rows"]:
        group = source_input["groups"][row["group"]]
        a = species.index(row["species"])
        sigma = exact(group["sigma_cm2_python_source_diagnostic"][a])
        stock = exact(group["stored_primary_packet_count_per_H"])
        saved = row["delta_E_exact"]
        delta = Fraction(int(saved["numerator"]), int(saved["denominator"]))
        defect = sigma * stock * delta
        assert defect == 0
        weighted.append({"group": row["group"], "species": row["species"], "N_sigma_delta_E": rat(defect)})

    constants = source_input["constants_from_identity_words"]
    chi = [constants["chi_HI_eV"], constants["chi_HeI_eV"], constants["chi_HeII_eV"]]
    witnesses = []
    for a in range(3):
        energy = 100.0
        excess = energy - chi[a]
        epsilon = exact(chi[a]) + exact(excess) - exact(energy)
        witnesses.append({
            "species": species[a],
            "energy_eV_binary64_hex": energy.hex(),
            "threshold_eV_binary64_hex": chi[a].hex(),
            "rounded_excess_eV_binary64_hex": excess.hex(),
            "epsilon_eV_exact": rat(epsilon),
            "epsilon_eV_rounded_display": float(epsilon),
            "nonzero": epsilon != 0,
        })
    assert any(w["nonzero"] for w in witnesses)
    result = {
        "schema": "WU088_HH_PHYS06_ARCHIVED_PHOTO_LEAF_ADDENDUM_V1",
        "status": "EXACT_LEAF_DIAGNOSTIC_COMPLETE",
        "input_sha256": sha(args.input),
        "first_leaf_audit_sha256": sha(args.first_leaf_audit),
        "source_commit": first["source_commit"],
        "source_sha256": first["source_sha256"],
        "source_raw_url": first["source_raw_url"],
        "script_sha256": sha(Path(__file__)),
        "scope": "Exact represented-leaf checks only; the generic witnesses are not model runs or spectra added to the archived point.",
        "archived_conclusion": "Every N*sigma*epsilon is exactly zero for the fixed 33-group archived point; thus the source heat-subtraction leaf does not change its ideal E*kappa photo-energy row.",
        "generic_conclusion": "100 eV has nonzero excess-energy rounding defects. The ideal E*kappa identity cannot be promoted to the general implemented source graph without its epsilon term or a separate exact-subtraction condition.",
        "stock_semantics": "Frozen stored primary stock; not the next endpoint preBE incoming stock.",
        "provider_semantics": "Stored Python source-diagnostic sigma values; no new native Rust/libm output attestation.",
        "separate_arithmetic_work": {
            "saved_subtraction_comparisons_reused": 99,
            "new_archived_subtraction_comparisons": 0,
            "new_exact_N_sigma_delta_weights": 99,
            "new_generic_100eV_subtraction_comparisons": 3,
            "archived_energy_run01_replays": 0,
        },
        "counts": {"native_provider": 0, "native_callbacks": 0, "native_endpoints": 0, "point_solvers": 0, "root_producers": 0, "IVP": 0, "old_suite_replays": 0},
        "authority": {"native_authorization": None, "native_budget": 0},
        "validation": {"all_99_N_sigma_delta_weights_exact_zero": True, "generic_nonzero_witnesses": sum(w["nonzero"] for w in witnesses)},
        "witnesses": witnesses,
        "weighted_archived_defects": weighted,
        "execution": {"wall_seconds": time.monotonic() - start, "max_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "max_wall_seconds": 30, "max_address_space_bytes": 268435456},
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "sha256": sha(args.output), "validation": result["validation"], "witnesses": witnesses, "execution": result["execution"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
