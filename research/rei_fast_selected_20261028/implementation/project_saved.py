"""Project receipt-pinned ANGTHERM01 saved histories; no ODE integration."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
SOURCE = UNIT / "inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023"
ARCHIVE = UNIT / "inputs/REI_ANGTHERM01_FINAL_20261023_46519489c540.zip"
ARCHIVE_SHA = "46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036"
RECEIPT_SHA = "e604e87be6dc9bb30824cd97f482dab1752bb23d484d5cfb4e294e4fed384747"
SOURCE_SHA = "6730e3091de918f693e02e40b0bdf1fefc543a5dcc4de23efd885ca098e2ed5f"
BASE_COMMIT = "73c5e00cac26b4efc782446975bd6b6762555997"
CASE_SHA = {
    "grid044_M4_tight": "6a1adec0bda0285ccaf55ee5f2e39a1e7fcedd981fe607a6a85783e53406910c",
    "grid044_M4_nominal": "ac035e9bdc6427dd66cbc3a39db92769ffc23f2ae8de7a2c1200b83fb9f20619",
}
DISPLAY = ("n", "H1_0", "H1_1", "D_0", "D_1", "T_0", "T_1",
           "He3_0", "He3_1", "He3_2", "He4_0", "He4_1", "He4_2",
           "Li7_0", "Li7_1", "Li7_2", "Li7_3")
PANEL = ("n", "H1", "D", "T", "He3", "He4", "Li7")
ROMAN = ("I", "II", "III", "IV")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_hash(path: Path, expected: str) -> None:
    observed = sha256(path)
    if observed != expected:
        raise ValueError(f"source SHA256 mismatch: {path}: {observed}")


def registry_from_pinned_source(path: Path):
    """Read only the literal isotope tuple; never import source/provider code."""
    tree = ast.parse(path.read_text())
    literals = [ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "ISOTOPES" for t in node.targets)]
    if len(literals) != 1:
        raise ValueError("missing or duplicate pinned isotope registry")
    labels, mass, scales, totals = [], [], [], {}
    for name, a, z, abundance, scale in literals[0]:
        totals[name] = abundance
        for q in range(z + 1):
            labels.append("n" if name == "n" else f"{name}_{q}")
            mass.append(a)
            scales.append(scale)
    if len(labels) != 21 or tuple(labels[:17]) != DISPLAY or labels[17:] != [
        "Li6_0", "Li6_1", "Li6_2", "Li6_3"]:
        raise ValueError("unexpected source column registry")
    baryons_per_href = float(sum(a * abundance for name, a, z, abundance, scale in literals[0]))
    return labels, np.asarray(mass), np.asarray(scales), totals, baryons_per_href


def load_projected(case: str):
    if case not in CASE_SHA:
        raise ValueError("case outside frozen saved-source selection")
    require_hash(ARCHIVE, ARCHIVE_SHA)
    receipt_path = SOURCE / "FINAL_RUN_RECEIPT.json"
    require_hash(receipt_path, RECEIPT_SHA)
    receipt = json.loads(receipt_path.read_text())
    if receipt["base_commit"] != BASE_COMMIT or case not in receipt["completed_cases"]:
        raise ValueError("receipt source identity/status mismatch")
    source_path = SOURCE / "vendor/c22/atomic_network.py"
    require_hash(source_path, SOURCE_SHA)
    labels, mass, scales, totals, baryons_per_href = registry_from_pinned_source(source_path)
    npz_path = SOURCE / "results" / (case + ".npz")
    require_hash(npz_path, CASE_SHA[case])
    receipt_files = {x["path"]: x for x in receipt["artifacts"] if "path" in x}
    rel = "results/" + case + ".npz"
    if receipt_files[rel]["sha256"] != CASE_SHA[case]:
        raise ValueError("receipt does not bind selected NPZ")
    case_json = SOURCE / "results" / (case + ".json")
    require_hash(case_json, receipt_files["results/" + case + ".json"]["sha256"])
    if json.loads(case_json.read_text())["status"] != "COMPLETED":
        raise ValueError("selected history is not completed")
    with np.load(npz_path, allow_pickle=False) as saved:
        eta = saved["eta"].copy()
        scaled = saved["atomic_scaled"].copy()
        fractions = saved["fractions"].copy()
    if eta.shape != (201,) or scaled.shape != (21, 201) or fractions.shape != (9, 201):
        raise ValueError("unexpected saved trajectory schema")
    if not np.all(np.isfinite(eta)) or not np.all(np.diff(eta) > 0):
        raise ValueError("invalid native clock")
    if eta[0] != 0 or not np.isclose(eta[-1], np.log(7), rtol=0, atol=1e-14):
        raise ValueError("unexpected saved domain")
    if not np.all(np.isfinite(scaled)) or np.any(scaled < 0):
        raise ValueError("negative/nonfinite saved population; refusing to hide it")
    if np.any(scaled[[0, 5, 6]] != 0) or totals["n"] != 0 or totals["T"] != 0:
        raise ValueError("n/T cannot be called structural zero")
    per_href = scaled * scales[:, None]
    # All 21 source populations, including hidden Li6, define the baryon reference.
    per_baryon = per_href / baryons_per_href
    baryon_sum = mass @ per_href
    z = 21 * np.exp(-eta) - 1  # matched mean-scale-factor convention
    return {
        "case": case, "labels": labels, "eta": eta, "z": z,
        "per_href": per_href, "per_baryon": per_baryon,
        "baryons_per_href": baryons_per_href,
        "max_baryon_drift_per_href": float(np.max(np.abs(baryon_sum - baryons_per_href))),
        "source_npz_sha256": CASE_SHA[case],
    }


def write_table(projected, path: Path):
    labels = projected["labels"]
    header = ["eta_ln_a_over_ai", "z_mean", *["per_Href__" + x for x in labels],
              *["per_baryon__" + x for x in labels]]
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for t in range(len(projected["eta"])):
            writer.writerow([projected["eta"][t], projected["z"][t],
                             *projected["per_href"][:, t], *projected["per_baryon"][:, t]])


def log_series(values):
    """Return a masked log series, or None when a source stage is all zero."""
    if np.any(values < 0) or not np.all(np.isfinite(values)):
        raise ValueError("negative/nonfinite population cannot be hidden on log ordinate")
    return None if np.all(values == 0) else np.ma.masked_equal(values, 0)


def write_figure(projected, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels, z, p = projected["labels"], projected["z"], projected["per_baryon"]
    fig, axs = plt.subplots(7, 1, figsize=(9, 14), sharex=True,
                            gridspec_kw={"hspace": 0.15})
    for ax, family in zip(axs, PANEL):
        ii = [i for i, name in enumerate(labels) if name == family or name.startswith(family + "_")]
        ii = [i for i in ii if labels[i] in DISPLAY]
        positives, zeros = [], []
        for i in ii:
            values = p[i]
            q = 0 if family == "n" else int(labels[i].split("_")[-1])
            label = "n" if family == "n" else f"{family} {ROMAN[q]}"
            series = log_series(values)
            if series is None:
                zeros.append(label)
                continue
            # Exact zero samples remain zero in the table and are masked only
            # on the logarithmic axis, never replaced by a fake positive floor.
            ax.plot(z, series, lw=1.8, label=label)
            positives.append(i)
        if positives:
            ax.set_yscale("log")
            ax.legend(loc="best", ncol=3, fontsize=8)
            if zeros:
                ax.text(0.99, 0.04, "; ".join(label + " = 0" for label in zeros) + " (source)",
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
        else:
            zero_label = "; ".join(label + " = 0" for label in zeros)
            ax.text(0.5, 0.5, zero_label + " (structural in this source case)", transform=ax.transAxes,
                    ha="center", va="center", fontsize=10)
            ax.set_ylim(0, 1)
            ax.set_yticks([0])
        ax.set_ylabel(family + "\n$n_i/n_b$")
        ax.grid(alpha=0.25)
    axs[-1].set_xlim(float(z[0]), float(z[-1]))
    axs[-1].set_xlabel("Mean-scale-factor redshift $z$ (20 → 2)")
    fig.suptitle("Saved ANGTHERM01 isotope charge populations — " + projected["case"], y=0.995)
    fig.text(0.5, 0.009,
             "17 displayed states; n/T source-zero; exact zero samples omitted on log axes.\n"
             "Li7 IV shown; Li6 I–IV hidden. Shared isotope electronic rates and initial charge fractions.\n"
             "Prescribed background and six-bin initial UV; no new nuclear production or Einstein feedback.",
             ha="center", fontsize=8)
    fig.subplots_adjust(top=0.965, bottom=0.07, left=0.13, right=0.97)
    fig.savefig(path, dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASE_SHA), default="grid044_M4_nominal")
    parser.add_argument("--output-dir", type=Path, default=UNIT / "outputs")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    p = load_projected(args.case)
    csv_path = out / f"{args.case}_all21_populations.csv"
    png_path = out / f"{args.case}_selected17.png"
    write_table(p, csv_path)
    write_figure(p, png_path)
    meta = {"source": "ANGTHERM01 saved history", "case": args.case,
            "base_commit": BASE_COMMIT, "archive_sha256": ARCHIVE_SHA,
            "source_npz_sha256": p["source_npz_sha256"], "n_report_points": len(p["eta"]),
            "domain_z": [float(p["z"][0]), float(p["z"][-1])],
            "baryons_per_Href": p["baryons_per_href"],
            "max_baryon_drift_per_Href": p["max_baryon_drift_per_href"],
            "columns": p["labels"], "displayed": list(DISPLAY),
            "source_zero": ["n", "T_0", "T_1"], "hidden_closure": p["labels"][17:],
            "unit": "number population per baryon (constant source n_b/n_Href reference; all 21 states)",
            "scope": "prescribed ANGTHERM01 background and initial UV; saved history projection only",
            "outputs": {str(csv_path.name): sha256(csv_path), str(png_path.name): sha256(png_path)}}
    (out / f"{args.case}_projection.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
