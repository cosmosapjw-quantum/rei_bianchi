"""Render two diagnostics from the completed one-shot tracer NPZ, without rerun."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
with np.load(ROOT / "TRACER_HISTORIES.npz", allow_pickle=False) as d:
    data = {k: d[k].copy() for k in d.files}
report = json.loads((ROOT / "TRACER_REPORT.json").read_text())
i = list(data["case_names"]).index(report["strongest_case"])
lg = np.log(10)
x = data["x"]
z = data["z"]
fig, ax = plt.subplots(2, 1, figsize=(8.2, 8.2), sharex=True, constrained_layout=True)
ax[0].plot(z, data["T_K"], color="#a52a2a", lw=2.2)
ax[0].set(ylabel="Prescribed gas / ion T [K]", yscale="log")
ax[0].grid(alpha=.2)
ax[1].plot(z, data["log_sp"][i]/lg, label="DDp → T+p", lw=2)
ax[1].plot(z, data["log_sn"][i]/lg, label="DDn → He³+n", lw=1.6, ls="--")
ax[1].set(xlabel="Redshift z (late time to right)", ylabel="log₁₀ source [baryon⁻¹ s⁻¹]")
ax[1].invert_xaxis(); ax[1].grid(alpha=.2); ax[1].legend(frameon=False)
fig.suptitle("Conditional bare-ion DD source on a saved atomic history")
fig.savefig(ROOT / "01_DD_source.png", dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.2, 5.6), constrained_layout=True)
for key, label, style in (("log_Cp", "Cumulative direct T births", "-"),
                           ("log_Cn", "Cumulative DD neutron births", "--"),
                           ("log_YT", "Surviving direct T", "-"),
                           ("log_YT_qss", "Local T quasi-steady estimate", ":")):
    y = data[key][i]/lg
    ax.plot(z[1:], y[1:], style, lw=2 if key != "log_YT_qss" else 1.5,
            label=label)
ax.set(xlabel="Redshift z (late time to right)",
       ylabel="log₁₀ baryon-normalized inventory")
ax.invert_xaxis(); ax.grid(alpha=.2); ax.legend(frameon=False)
ax.set_title("Births are distinct from surviving tritium")
fig.savefig(ROOT / "02_births_vs_survival.png", dpi=180)
plt.close(fig)
