"""Plot admitted fast-nucleus inventories against saved time and temperature."""
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    summary = json.loads((HERE/"NUCLEAR_NETWORK_SUMMARY.json").read_text())
    with np.load(HERE/"NUCLEAR_NETWORK_HISTORIES.npz", allow_pickle=False) as data:
        names = data["case_names"].tolist()
        idx = names.index(summary["illustrative_case"])
        logs = data["log_T_n"][idx].copy()
        proper = data["elapsed_s"][idx].copy()
        temp = data["T_K"].copy()
    # Proper elapsed time since z=20, expressed using a fixed Julian year.
    gyr = (proper-proper[0])/(365.25*86400*1e9)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.2), layout="constrained",
                             sharey=True)
    for col, abscissa in enumerate((gyr, temp)):
        for j, (label, color) in enumerate((("T", "#9b2719"),
                                            ("neutron", "#245e8c"))):
            good = np.isfinite(logs[:, j])
            axes[col].plot(abscissa[good], logs[good, j]/math.log(10),
                           label=label, color=color, linewidth=2)
        axes[col].grid(alpha=.22)
        axes[col].legend()
    axes[0].set(xlabel="Proper time since z=20 (Gyr)",
                ylabel="log10 nuclei per baryon")
    axes[1].set(xlabel="Prescribed gas temperature (K)", xlim=(100, 10000))
    fig.suptitle("Conditional all-bare T and neutron inventories")
    fig.savefig(HERE/"NUCLEAR_NETWORK_TIME_TEMPERATURE.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
