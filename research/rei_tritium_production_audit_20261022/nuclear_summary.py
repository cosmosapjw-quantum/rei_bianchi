"""Small reusable result summary and figures from saved network evidence."""
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import nuclear_network as net


def main():
    report = json.loads((net.HERE/"NUCLEAR_NETWORK_REPORT.json").read_text())
    families = json.loads(net.CONTRACT.read_text())["families"]
    with np.load(net.HERE/"NUCLEAR_NETWORK_HISTORIES.npz", allow_pickle=False) as data:
        names = data["case_names"].tolist()
        logt = data["log_T_n"][:, :, 0].copy()
        logn = data["log_T_n"][:, :, 1].copy()
        x = data["x"].copy()
    index = int(np.argmax(logt[:, -1]))
    representative = names[index]
    births = []
    for name in names:
        by_route = {}
        logs = []
        for f, e in zip(families, report["case_ledgers"][name]["families"]):
            nu = f["products"].get("T", 0)-f["reactants"].get("T", 0)
            for direction, key in ((1, "forward"), (-1, "reverse")):
                if direction*nu > 0 and e[key]["log10"] is not None:
                    val = e[key]["log10"]*math.log(10)+math.log(direction*nu)
                    by_route[f["id"]+"_"+key] = val/math.log(10)
                    logs.append(val)
        births.append({"case": name,
                       "total_log10": float(np.logaddexp.reduce(logs)/math.log(10)),
                       "routes_log10": by_route})
    strongest_birth = max(births, key=lambda b: b["total_log10"])
    summary = {"scope": report["mode"], "cases": len(names),
               "case_rank_warning": "Endpoint T/n surviving inventories differ only at roundoff scale; exact endpoint argmax is not a physical ranking. Cumulative event yields may vary with proper-time history.",
               "max_surviving_T_log10": float(np.max(logt[:, -1])/math.log(10)),
               "min_surviving_T_log10": float(np.min(logt[:, -1])/math.log(10)),
               "surviving_T_log10_spread_dex": float(np.ptp(logt[:, -1])/math.log(10)),
               "max_surviving_n_log10": float(np.max(logn[:, -1])/math.log(10)),
               "max_all_T_births_log10": strongest_birth["total_log10"],
               "max_all_T_births_routes_log10": strongest_birth["routes_log10"],
               "illustrative_case": representative,
               "implementation_status": report["status"],
               "refinement_max_dex": report["checks"]["max_1x_to_2x_event_difference_dex"],
               "gross_bulk_change_max": report["checks"]["max_relative_bulk_gross_change"]}
    (net.HERE/"NUCLEAR_NETWORK_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False)+"\n")

    z = 21*np.exp(-x)-1
    fig, ax = plt.subplots(figsize=(7, 4.4), layout="constrained")
    for values, label, color in ((logt[index], "T", "#9b2719"),
                                 (logn[index], "neutron", "#245e8c")):
        finite = np.isfinite(values)
        ax.plot(z[finite], values[finite]/math.log(10), label=label,
                color=color, linewidth=2)
    ax.invert_xaxis()
    ax.set(xlabel="Redshift z", ylabel="log10 nuclei per baryon",
           title="Conditional all-bare T and neutron inventories")
    ax.legend()
    ax.grid(alpha=.22)
    fig.savefig(net.HERE/"NUCLEAR_NETWORK_POPULATIONS.png", dpi=170)
    plt.close(fig)

    routes = [(key, val) for key, val in strongest_birth["routes_log10"].items()
              if val > -400]
    routes.sort(key=lambda item: item[1])
    fig, ax = plt.subplots(figsize=(7.3, 4.1), layout="constrained")
    pretty = {"d_d_p_forward": "D + D → T + p",
              "n_he3_p_forward": "He3 + n → T + p",
              "d_n_gamma_forward": "D + n → T + γ",
              "n_li6_alpha_forward": "Li6 + n → T + α"}
    labels = [pretty.get(a, a) for a, _ in routes]
    values = [b for _, b in routes]
    yy = np.arange(len(values))
    ax.hlines(yy, min(values)-4, values, color="#9b2719", linewidth=2)
    ax.scatter(values, yy, color="#9b2719", s=52)
    ax.set_yticks(yy, labels)
    ax.set_xlim(min(values)-5, max(values)+5)
    ax.set(xlabel="log10 cumulative T nuclei born per baryon",
           title="Representable T-producing paths (conditional model)")
    ax.grid(axis="x", alpha=.22)
    fig.savefig(net.HERE/"NUCLEAR_NETWORK_T_BIRTHS.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
