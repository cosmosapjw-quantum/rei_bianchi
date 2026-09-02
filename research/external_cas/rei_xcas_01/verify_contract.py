#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

BASE = "f4eb2c893ce6449f8899ab6f02c83421fc7c7019"
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

expected_blobs = {
    "src/rei_bianchi/b2b_physical_model.py": "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
    "src/rei_bianchi/monolithic_model_b2a.py": "3d806e1c1d3bb523bb3c339d1a141f67d7f10069",
    "src/rei_bianchi/primary_exact_zero_model.py": "ea2a10a60114622fd1215b692be3dd0d04ef0c6d",
    "src/rei_bianchi/multigroup_hhe_transmission.py": "5b74a4036c8cb21a2cb772dd3d373c5f96d5a36c",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    contract = json.loads((HERE / "FORMULA_CONTRACT.json").read_text())
    assert contract["exact_scientific_source"]["commit"] == BASE
    subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT, check=True)

    actual_blobs = {}
    for rel, expected in expected_blobs.items():
        actual = git("hash-object", rel)
        assert actual == expected, (rel, expected, actual)
        actual_blobs[rel] = actual

    changed = [
        line for line in git("diff", "--name-only", f"{BASE}...HEAD").splitlines()
        if line
    ]
    allowed = (
        ".github/workflows/rei-xcas-octave-jas-julia.yml",
        "research/external_cas/rei_xcas_01/",
    )
    unexpected = [p for p in changed if not any(p == a or p.startswith(a) for a in allowed)]
    assert not unexpected, unexpected

    source_text = {
        rel: (ROOT / rel).read_text(encoding="utf-8") for rel in expected_blobs
    }
    required_snippets = {
        "src/rei_bianchi/b2b_physical_model.py": [
            "return H0 * math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)",
            "lo * shape(float(lo)) / norm",
        ],
        "src/rei_bianchi/monolithic_model_b2a.py": [
            "red_out = p[\"Hubble\"] * p[\"redshift_coeff\"]",
            "state[\"xHeII\"] + 2.0 * state[\"xHeIII\"]",
            "expansion = 3.0 * p[\"Hubble\"] * pressure",
        ],
        "src/rei_bianchi/primary_exact_zero_model.py": [
            "he=jax.nn.softmax",
            "expansion=3*p['Hubble']*pressure",
        ],
        "src/rei_bianchi/multigroup_hhe_transmission.py": [
            "trans = np.exp(-np.clip(tau_total, 0.0, 745.0))",
            "absorbed_energy = -np.expm1(-np.clip(tau_total, 0.0, 745.0))",
            "allocation[thin_mask] = thin_allocation[thin_mask]",
        ],
    }
    for rel, snippets in required_snippets.items():
        for snippet in snippets:
            assert snippet in source_text[rel], (rel, snippet)

    receipt_dir = HERE / "receipts"
    receipt_dir.mkdir(exist_ok=True)
    receipt = {
        "status": "PASS",
        "base_ancestor": BASE,
        "head": git("rev-parse", "HEAD"),
        "source_blobs": actual_blobs,
        "changed_paths": changed,
        "formula_contract_sha256": hashlib.sha256(
            (HERE / "FORMULA_CONTRACT.json").read_bytes()
        ).hexdigest(),
        "claim_boundary": "SOURCE_BINDING_AND_PATH_CLOSURE_ONLY",
    }
    (receipt_dir / "contract_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
