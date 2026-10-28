"""One-axis presentation of the saved ON_refined selected17 populations.

Only saved samples are read. No IVP, rate evaluation, resampling, or floors.
"""
from pathlib import Path
import csv
import hashlib
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter

UNIT = Path(__file__).resolve().parents[1]
ROOT = UNIT.parents[1]
SOURCE = ROOT / "research/rei_source_history_20261028/outputs"
OUT = UNIT / "outputs"
FIGURE = UNIT / "figure"
Y_MIN, Y_MAX = 1e-8, 2.0
# A single factor is shared by all charge states of an isotope.
FAMILIES = (
    ("n", (0,), ("n",), 22, "#666666"),
    ("H1", (1, 2), ("H I", "H II"), 0, "#0072B2"),
    ("D", (3, 4), ("D I", "D II"), 4, "#009EAD"),
    ("T", (5, 6), ("T I", "T II"), 18, "#CC3311"),
    ("He3", (7, 8, 9), ("³He I", "³He II", "³He III"), 4, "#228833"),
    ("He4", (10, 11, 12), ("⁴He I", "⁴He II", "⁴He III"), 1, "#EE9933"),
    ("Li7", (13, 14, 15, 16), ("⁷Li I", "⁷Li II", "⁷Li III", "⁷Li IV"), 9, "#AA3377"),
)
RAW_NAMES = ("n", "H1_0", "H1_1", "D_0", "D_1", "T_0", "T_1", "He3_0",
             "He3_1", "He3_2", "He4_0", "He4_1", "He4_2", "Li7_0", "Li7_1", "Li7_2", "Li7_3")
STYLES = ("-", "--", "-.", ":")
MARKERS = ("o", "s", "^", "D")
SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    png = FIGURE / "pilot17_single_axis.png"
    svg = FIGURE / "pilot17_single_axis.svg"
    table = OUT / "pilot17_single_axis_scaled.csv"
    manifest = OUT / "SINGLE_AXIS_MANIFEST.json"
    for path in (png, svg, table, manifest):
        if path.exists():
            raise FileExistsError(path)
    npz = SOURCE / "ON_refined.npz"
    raw_csv = SOURCE / "pilot17_populations.csv"
    with np.load(npz, allow_pickle=False) as data:
        t = data["t"].copy()
        raw = data["physical"][:17].copy()
        physical_shape = data["physical"].shape
    if (t.ndim != 1 or physical_shape != (23, len(t)) or raw.shape != (17, len(t))
            or not np.isfinite(t).all() or not np.isfinite(raw).all()
            or t[0] != 0 or np.any(np.diff(t) <= 0)):
        raise ValueError("Saved ON_refined schema/time/finiteness mismatch")
    with raw_csv.open(newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row["case"] == "ON_refined"]
    csv_t = np.array([float(row["elapsed_proper_s"]) for row in rows])
    csv_raw = np.array([[float(row["per_Href__" + state]) for row in rows] for state in RAW_NAMES])
    if not np.array_equal(t, csv_t) or not np.array_equal(raw, csv_raw):
        raise ValueError("NPZ and preserved raw CSV selected17 values differ")
    positive_time = t > 0
    if not positive_time.any():
        raise ValueError("No positive elapsed-time samples")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "axes.labelsize": 13, "xtick.labelsize": 11,
                         "ytick.labelsize": 11, "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(12.8, 8.6), dpi=125)
    fig.subplots_adjust(left=.085, right=.985, top=.89, bottom=.33)
    records = []
    metadata = []
    handles = []
    below_total = above_total = zero_total = signed_total = 0
    for family, indices, labels, exponent, color in FAMILIES:
        multiplier = 10.0 ** exponent
        for charge, (index, label) in enumerate(zip(indices, labels)):
            values = raw[index]
            scaled = values * multiplier
            # Mask true nonpositive values, with no substitution or epsilon floor.
            plotted = np.ma.masked_less_equal(scaled[positive_time], 0)
            legend_label = label + "  ×10" + str(exponent).translate(SUPER)
            line, = ax.plot(t[positive_time], plotted, color=color,
                            linestyle=STYLES[charge], linewidth=1.8,
                            marker=MARKERS[charge], markersize=3.7,
                            markerfacecolor="white", markeredgewidth=.8,
                            markevery=(3 + 3 * charge + index % 3, 29),
                            label=legend_label)
            handles.append(line)
            zeros = int(np.count_nonzero(positive_time & (values == 0)))
            signed = int(np.count_nonzero(positive_time & (values < 0)))
            below = int(np.count_nonzero(positive_time & (scaled > 0) & (scaled < Y_MIN)))
            above = int(np.count_nonzero(positive_time & (scaled > Y_MAX)))
            visible = int(np.count_nonzero(positive_time & (scaled >= Y_MIN) & (scaled <= Y_MAX)))
            if visible == 0:
                raise ValueError("State has no visible sample: " + label)
            zero_total += zeros
            signed_total += signed
            below_total += below
            above_total += above
            metadata.append({"state": RAW_NAMES[index], "label": label, "isotope": family,
                "multiplier": multiplier, "power_of_ten": exponent,
                "samples": len(t), "time_zero_omitted": int(np.count_nonzero(t == 0)),
                "positive_time_exact_zero_omitted": zeros, "positive_time_negative_omitted": signed,
                "positive_time_positive_below_ymin": below, "positive_time_above_ymax": above,
                "visible_saved_samples": visible, "raw_min": float(values.min()),
                "raw_max": float(values.max()), "color": color,
                "linestyle": STYLES[charge], "marker": MARKERS[charge]})
            for sample, elapsed in enumerate(t):
                if elapsed == 0: status = "time_zero_omitted_on_log_x"
                elif values[sample] == 0: status = "exact_zero_gap_on_log_y"
                elif values[sample] < 0: status = "negative_gap_on_log_y"
                elif scaled[sample] < Y_MIN: status = "positive_below_y_range"
                elif scaled[sample] > Y_MAX: status = "positive_above_y_range"
                else: status = "in_display_range"
                records.append(("ON_refined", sample, repr(float(elapsed)), RAW_NAMES[index],
                                repr(float(values[sample])), repr(multiplier),
                                repr(float(scaled[sample])), status))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(float(t[positive_time].min()) * .85, float(t.max()) * 1.08)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.xaxis.set_major_locator(LogLocator(base=10, numticks=8))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=80))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=50))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(which="major", alpha=.23, linewidth=.6)
    ax.grid(which="minor", alpha=.08, linewidth=.4)
    ax.set_xlabel("Elapsed proper time after source turn-on [s]", labelpad=8)
    ax.set_ylabel("Scaled population = (particles / Href) × legend multiplier", labelpad=10)
    fig.suptitle("All 17 particle and ion states · ON refined", fontsize=17, y=.973)
    fig.text(.5, .928, "Illustrative prescribed-bath history · isotope color; ion-stage line style and marker",
             ha="center", fontsize=11)
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, .247),
               ncol=4, fontsize=11, frameon=False, handlelength=3.2,
               columnspacing=1.6, labelspacing=.55, borderaxespad=0)
    fig.text(.5, .048,
        "Fixed isotope multipliers change vertical ordering; compare raw abundances in the CSV.\n"
        f"t = 0 omitted; positive tails below 10⁻⁸: {below_total} state-samples; above 2: {above_total}. "
        f"Exact-zero gaps: {zero_total}; negative gaps: {signed_total}.\n"
        "All saved raw values retained; no epsilon floors or new time samples. This is elapsed time, not cosmic age or the BBN era.",
        ha="center", va="center", fontsize=9.5, linespacing=1.5)
    fig.savefig(png, dpi=125, facecolor="white")
    fig.savefig(svg, facecolor="white")
    plt.close(fig)
    with table.open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("case", "saved_sample_index", "elapsed_proper_s", "state", "raw_particles_per_Href",
                         "fixed_multiplier", "scaled_population", "display_status"))
        writer.writerows(records)
    receipt = {"status": "RENDERED_SAVED_DATA_ONLY", "case": "ON_refined",
        "default_presentation_case": "ON_refined", "IVP_execution": "NONE",
        "new_time_samples": 0, "raw_data_modified": False, "abundance_floor_added": False,
        "axes_count": 1, "x_scale": "log", "x_quantity": "elapsed proper seconds after source turn-on",
        "x_is_cosmic_age": False, "y_scale": "log", "y_limits_scaled": [Y_MIN, Y_MAX],
        "y_quantity": "(particles / Href) times explicit fixed isotope multiplier",
        "raw_abundance_order_preserved_across_isotopes": False,
        "samples_per_state": len(t), "legend_entries": len(handles), "states": metadata,
        "line_interpolation": "straight segments in logarithmic plotting coordinates between saved samples; no new samples",
        "below_range_handling": "positive values retained in CSV; axes clip only; no floor",
        "nonpositive_handling": "masked gaps only; original signed and zero values retained in CSV",
        "input_npz": str(npz.relative_to(ROOT)), "input_npz_sha256": sha(npz),
        "input_raw_csv": str(raw_csv.relative_to(ROOT)), "input_raw_csv_sha256": sha(raw_csv),
        "code_sha256": sha(Path(__file__)), "outputs": {
            str(path.relative_to(UNIT)): {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in (png, svg, table)},
        "csv_metadata": "display_status reports time-zero, signed/zero gaps, and offscale values for every unchanged raw sample",
        "scope": "presentation of existing illustrative prescribed-bath numerical populations; no astrophysical calibration or new solver claim"}
    with manifest.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "axes": 1, "states": len(metadata),
                      "below_range": below_total, "outputs": list(receipt["outputs"])}, indent=2))


if __name__ == "__main__":
    main()
