"""Repair endpoint stock wording from saved histories; never rerun 82 trajectories."""
import json
import math
import shutil
from pathlib import Path

import numpy as np

import nuclear_network as net


def _linear(item):
    state = item["absolute"]
    return item["sign"]*math.exp(state["log10"]*math.log(10)) if item["sign"] else 0.


def main():
    source = net.HERE/"NUCLEAR_NETWORK_REPORT.json"
    backup = net.HERE/"review_repair"/"before"
    backup.mkdir(parents=True, exist_ok=True)
    original = backup/source.name
    if original.exists():
        raise FileExistsError("review repair is one-shot")
    shutil.copy2(source, original)
    report = json.loads(source.read_text())
    contract = json.loads(net.CONTRACT.read_text())
    families = contract["families"]
    nbad = {"T": {"negative": 0, "zero": 0},
            "n": {"negative": 0, "zero": 0}}
    max_stock, max_gross = 0., 0.
    max_a, max_z = 0., 0.
    with np.load(net.HERE/"NUCLEAR_NETWORK_HISTORIES.npz", allow_pickle=False) as data:
        for case_idx, name in enumerate(data["case_names"].tolist()):
            previous = report["case_ledgers"][name]
            initial = np.array([row["initial"] for row in previous["changes"]])
            result = {"log_cumulative": data["log_forward_reverse_cumulative"][case_idx],
                      "log_fast": data["log_T_n"][case_idx]}
            new = net.endpoint_ledger(result, families, report["constants"]["Q_J"], initial)
            gross_a = 0.
            for j, f in enumerate(families):
                nu = np.array([f["products"].get(s, 0)-f["reactants"].get(s, 0)
                               for s in net.SPECIES])
                g = float(result["log_cumulative"][-1, j, 0])
                l = float(result["log_cumulative"][-1, j, 1])
                total = (math.exp(g) if math.isfinite(g) else 0.) + (
                    math.exp(l) if math.isfinite(l) else 0.)
                gross_a += total*float(net.A@abs(nu))
            reconstructed = np.array([
                _linear(row["event_reconstruction_net"])
                if "event_reconstruction_net" in row else
                row["net_sign"]*math.exp(row["net_abs"]["log10"]*math.log(10))
                if row["net_sign"] else 0.
                for row in new["changes"]])
            electrons = sum(math.exp(f["forward"]["log10"]*math.log(10))
                            * next(x["electrons_created"] for x in families
                                   if x["id"] == f["id"])
                            for f in new["families"] if f["id"] in ("t_beta", "n_beta"))
            a_residual = abs(float(net.A@reconstructed))/gross_a
            z_residual = abs(float(net.Z@reconstructed)-electrons)/gross_a
            max_a, max_z = max(max_a, a_residual), max(max_z, z_residual)
            diag = {}
            for isotope in ("T", "n"):
                row = next(x for x in new["changes"] if x["species"] == isotope)
                stock = row["net_abs"]["linear"]
                delta = _linear(row["event_reconstruction_net"])
                gain = row["gain"]["linear"] or 0.
                loss = row["loss"]["linear"] or 0.
                if row["event_reconstruction_net"]["sign"] < 0:
                    nbad[isotope]["negative"] += 1
                if row["event_reconstruction_net"]["sign"] == 0:
                    nbad[isotope]["zero"] += 1
                stock_scale = abs(delta-stock)/stock
                gross_scale = abs(delta-stock)/max(gain, loss)
                max_stock = max(max_stock, stock_scale)
                max_gross = max(max_gross, gross_scale)
                diag[isotope] = {"event_reconstruction_minus_fast_stock_relative_to_stock":
                                 stock_scale,
                                 "event_reconstruction_minus_fast_stock_relative_to_gross":
                                 gross_scale}
            new["reconstruction_diagnostics"] = diag
            new["event_ledger_conservation"] = {
                "A_residual_divided_by_gross_A_turnover": a_residual,
                "Z_minus_beta_electron_residual_divided_by_gross_A_turnover": z_residual}
            report["case_ledgers"][name] = new
    report["checks"].update({
        "max_fast_stock_reconstruction_relative_to_stock": max_stock,
        "max_fast_stock_reconstruction_relative_to_gross_events": max_gross,
        "max_event_A_residual_divided_by_gross_A_turnover": max_a,
        "max_event_Z_minus_beta_electron_residual_divided_by_gross_A_turnover": max_z,
        "event_reconstruction_nonpositive_counts": nbad,
        "event_ledger_conservation_rtol": contract["checks"]["ledger_relative_conservation_tolerance"]})
    report["fast_stock_authority"] = (
        "log_T_n in saved NPZ: positive 2x2 propagated inventory; T/n changes.net_abs "
        "uses that stock. changes.event_reconstruction_net is a separately reconstructed "
        "flux difference and can cancel or differ at stock scale.")
    report["review_repair"] = {"scope": "report-only endpoint stock semantics",
                                "before": "review_repair/before/NUCLEAR_NETWORK_REPORT.json",
                                "network_rerun": False}
    source.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps(report["checks"], indent=2))


if __name__ == "__main__":
    main()
