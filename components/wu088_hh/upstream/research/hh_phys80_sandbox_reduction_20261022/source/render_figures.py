"""Render preserved PHYS80 results only; no model evaluations or ODE calls."""
import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"figures"
RECEIPT = ROOT/"verification/FIGURE_RENDER.json"
if RECEIPT.exists():
    raise SystemExit("CREATE_ONLY: figures already rendered; reuse saved artifacts")
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
                     "legend.fontsize": 9, "figure.dpi": 120, "savefig.dpi": 180,
                     "axes.grid": True, "grid.alpha": .20, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})

meta = {d["task_id"]: d for p in (ROOT/"results/reduced/cases").glob("*.json")
        if (d := json.loads(p.read_text()))["status"] == "COMPLETE"}
data = {k: dict(np.load(ROOT/"results/reduced"/d["npz"]["path"], allow_pickle=False))
        for k, d in meta.items()}
parents = {}
parentmeta = {}
for k, d in meta.items():
    parent_id = d["binding"]["parent_comparison_science_id"]
    parents[k] = dict(np.load(ROOT/"inputs/phys79_cases"/(parent_id+".npz"), allow_pickle=False))
    parentmeta[k] = json.loads((ROOT/"inputs/phys79_cases"/(parent_id+".json")).read_text())
warm, cold = data["C01_REDUCED_BASE"], data["C02_REDUCED_BASE"]
oldwarm, oldcold = parents["C01_REDUCED_BASE"], parents["C02_REDUCED_BASE"]
ix = {name: i for i, name in enumerate(warm["species_names"].tolist())}
colors = ["#146a9c", "#c66b20", "#7d4695", "#277a53"]
outputs = []

def save(fig, stem):
    for suffix in ("png", "pdf"):
        path = OUT/(stem+"."+suffix)
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, bbox_inches="tight")
        outputs.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
ax = axes[0, 0]
ax.plot(warm["theta"], warm["T_K"], color=colors[0], label="Reduced Radau")
ax.plot(oldwarm["theta"][::8], oldwarm["T_K"][::8], "o", ms=3,
        mfc="none", color="black", label="Stored PHYS79")
ax.set(title="C01 | closed thermal energy", xlabel=r"$\theta=n_H k_{\rm ref}t$", ylabel="Temperature [K]")
ax.legend()
ax = axes[0, 1]
for species, inventory, color in [("H1_II", 1., colors[0]), ("D_II", 2.46e-5, colors[1])]:
    ax.plot(warm["theta"], warm["Y"][:, ix[species]]/inventory, color=color, label=species)
    ax.plot(oldwarm["theta"][::8], oldwarm["Y"][::8, ix[species]]/inventory,
            "o", color=color, mfc="none", ms=3)
ax.set(title="C01 | H/D kinetics retained", xlabel=r"$\theta$", ylabel="Singly ionized fraction")
ax.legend()
ax = axes[1, 0]
for species, inventory, color in [("He4_II", .08205167916519925, colors[2]), ("Li7_II", 5.627e-10, colors[3])]:
    ax.plot(warm["theta"], warm["Y"][:, ix[species]]/inventory, color=color, label=species)
    ax.plot(oldwarm["theta"][::8], oldwarm["Y"][::8, ix[species]]/inventory,
            "o", color=color, mfc="none", ms=3)
ax.set(title="C01 | shared elemental rates", xlabel=r"$\theta$", ylabel="Singly ionized fraction", yscale="log")
ax.legend()
ax = axes[1, 1]
ax.plot(cold["theta"], cold["Y"][:, ix["D_II"]]/2.46e-5, color=colors[1], label="1D Radau")
ax.plot(oldcold["theta"][::8], oldcold["Y"][::8, ix["D_II"]]/2.46e-5,
        "o", color="black", mfc="none", ms=3, label="Stored PHYS79")
eq = meta["C02_REDUCED_BASE"]["oracle"]["equilibrium_Y_per_H"][ix["D_II"]]/2.46e-5
ax.axhline(eq, ls=":", color=colors[2], label="Independent extent equilibrium")
ax.set(title="C02 | D/H exchange, 300 K", xlabel=r"$\theta=n_H k_{\rm ref}t$", ylabel="D II / D")
ax.legend(loc="lower right")
fig.suptitle("PHYS80 | fixed-inventory exact reduction of the isolated subnetwork", fontsize=14)
save(fig, "F01_saved_trajectory_comparison")

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)
for key, label, color in [("C01_REDUCED_BASE", "Base", colors[0]),
                          ("C01_REDUCED_REFINED", "Refined", colors[2])]:
    d = data[key]
    e = np.max(abs(d["parent_scaled_state_difference"]), axis=1)
    axes[0].semilogy(d["theta"], np.ma.masked_equal(e, 0), color=color, label=label)
axes[0].axhline(1e-6, ls=":", color="black", label="Declared gate")
axes[0].set(title="C01 | difference from stored parent", xlabel=r"$\theta$", ylabel="Max scaled state difference")
axes[0].legend()
e = np.max(abs(cold["parent_scaled_state_difference"]), axis=1)
axes[1].semilogy(cold["theta"], np.ma.masked_equal(e, 0), color=colors[1])
axes[1].axhline(1e-6, ls=":", color="black")
axes[1].set(title="C02 | difference from stored parent", xlabel=r"$\theta$", ylabel="Max scaled state difference")
keys = ["C01_REDUCED_BASE", "C02_REDUCED_BASE", "C01_REDUCED_REFINED"]
x = np.arange(3)
oldcounts = np.array([parentmeta[k]["solver"]["nfev"] for k in keys])
newcounts = np.array([meta[k]["solver"]["nfev"] for k in keys])
axes[2].bar(x-.18, oldcounts, .36, label="Stored 22D DOP853", color="#9aa7af")
axes[2].bar(x+.18, newcounts, .36, label="Reduced Radau", color=colors[0])
for i, oldc, newc in zip(x, oldcounts, newcounts):
    axes[2].text(i, oldc*1.15, f"{oldc/newc:.2f}x fewer", ha="center", fontsize=9)
axes[2].set(yscale="log", ylim=(200, 130000), xticks=x,
            xticklabels=["C01 base", "C02 base", "C01 refined"],
            title="RHS evaluation counts", ylabel="Evaluations")
axes[2].legend(loc="upper left", fontsize=8)
fig.suptitle("Scoped numerical comparison | same stored physical inputs; new algorithm identities", fontsize=14)
fig.supxlabel("Historical evaluation counts are workload evidence; this is not a paired wall-time benchmark. Exact zero differences omitted on log axes.", fontsize=9)
save(fig, "F02_accuracy_and_work")

receipt = json.loads((ROOT/"source/maxwellian/BELL_KERNEL_VERIFY_RECEIPT.json").read_text())
grid = receipt["grid"]
u = np.array([r["u"] for r in grid])
lograte = np.array([r["assessment"]["order64"]["log_rate_cm3_s"] for r in grid])/np.log(10)
mean = np.array([r["assessment"]["order64"]["mean_excess_energy_eV"] for r in grid])
theta = np.array([r["assessment"]["order64"]["mean_incident_energy_eV"]-r["assessment"]["order64"]["mean_excess_energy_eV"] for r in grid])/u
under = np.array([r["assessment"]["order64"]["rate_underflow"] for r in grid])
fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), constrained_layout=True)
axes[0].semilogx(u, lograte, "o-", color=colors[0], label="Finite log rate")
axes[0].scatter(u[under], lograte[under], marker="x", s=80, color=colors[1], label="Float rate underflow")
axes[0].set(title="Pure-log synthetic cross section", xlabel=r"$U=I/(k_B T)$", ylabel=r"$\log_{10}[K/({\rm cm^3\,s^{-1}})]$")
axes[0].legend()
axes[1].semilogx(u, mean/theta, "o-", color=colors[2])
axes[1].axhline(2, ls=":", color="black")
axes[1].set(title="Incoming excess energy", xlabel=r"$U$", ylabel=r"$\langle E-I\rangle/(k_B T)$")
for order, color in [(32, colors[0]), (64, colors[1])]:
    error = np.array([next(c["relative_rate_error"] for c in r["comparisons"] if c["order"] == order) for r in grid])
    axes[2].loglog(u, np.ma.masked_equal(error, 0), "o-", color=color, label=f"Order {order}")
axes[2].set(title=r"Rate comparison with $E_1$ oracle", xlabel=r"$U$", ylabel="Relative difference")
axes[2].legend()
fig.suptitle("Generic Maxwellian kernel | explicit coefficients; no H/He/Li physical admission", fontsize=14)
fig.supxlabel("Saved 9-witness verification only. Quadrature agreement and node positivity are not a global error bound or a source validation.", fontsize=9)
save(fig, "F03_maxwellian_numeric_contract")

RECEIPT.write_text(json.dumps({
    "utc": datetime.now(timezone.utc).isoformat(), "status": "COMPLETED",
    "command": "python source/render_figures.py", "figures": 3, "PNG": 3, "PDF": 3,
    "new_ODE": 0, "new_model_evaluations": 0,
    "inputs": ["results/reduced/cases", "inputs/phys79_cases",
               "source/maxwellian/BELL_KERNEL_VERIFY_RECEIPT.json"],
    "outputs": outputs, "visual_QA": "PENDING"
}, indent=2)+"\n")
print(json.dumps({"outputs": outputs, "new_ODE": 0}, indent=2))
