"""Future one-shot two-panel plot and packaging; NOT_RUN; separate approval required.

From unit root: python -B figures/plot_saved.py --execute-authorized
Reads only saved new control output; never imports implementation or tests.
"""
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.argv[1:] != ["--execute-authorized"]:
        raise SystemExit("Pending explicit presentation allowance")
    marker = ROOT/"figures/presentation_attempt_01"
    marker.mkdir(exist_ok=False)
    start = time.perf_counter()
    cpu_start = time.process_time()
    raw = (ROOT/"execution/attempt_01/STDOUT.json").read_bytes()
    saved = json.loads(raw)
    if saved.get("successful") is not True:
        raise SystemExit("Successful saved new controls required")
    # Figure conversion only; all mathematical values came from the saved check.
    def display(w):
        return int(w["num"])/int(w["den"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a, b = saved["controls"]["A"], saved["controls"]["B"]
    rows = b["directional_map"]
    errors = a["difference_errors"]
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4), constrained_layout=True)
    axes[0].plot([display(r["v"]) for r in rows], [display(r["dT"]) for r in rows], "o-", label="knot right directional map")
    axes[0].scatter([1], [display(b["false_centered_slope"])], marker="x", s=80,
                    color="crimson", label="false centered candidate at v=1")
    axes[0].set(xlabel="energy direction v [J/(V0 epsilon)]", ylabel="dT [K/epsilon]",
                title="B: unequal-slope knot")
    h = [display(r["h"]) for r in errors]
    axes[1].loglog(h, [abs(display(r["forward_error"])) for r in errors], "o-", label="forward error |2h/[3(1+h)]|")
    axes[1].loglog(h, [abs(display(r["central_error"])) for r in errors], "s-", label="central error |−2h²/[3(1−h²)]|")
    axes[1].set(xlabel="parameter step h", ylabel="absolute derivative error [K/epsilon]",
                title="A: smooth moving-segment difference errors")
    for ax in axes:
        ax.grid(True, alpha=.25)
        ax.legend(fontsize=8)
    fig.suptitle("Manufactured supplied caloric knots — no physical EOS or uncertainty claim")
    png = marker/"DIRECTIONAL_CONTROLS.png"
    svg = marker/"DIRECTIONAL_CONTROLS.svg"
    fig.savefig(png, dpi=160)
    fig.savefig(svg)
    plt.close(fig)
    archive = marker/"FIGURE_AND_SAVED_CONTROLS.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in [png, svg, ROOT/"execution/attempt_01/STDOUT.json", ROOT/"execution/attempt_01/PROCESS.json"]:
            z.write(p, arcname=p.name)
    receipt = {"input_sha256": hashlib.sha256(raw).hexdigest(),
               "outputs": [{"name": p.name, "bytes": p.stat().st_size,
                            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (png, svg, archive)],
               "CPU_prefix_s": time.process_time()-cpu_start, "wall_prefix_s": time.perf_counter()-start,
               "scope": "plot/import/conversion/packaging prefix; final receipt serialization and exit excluded",
               "maxrss_KiB_Linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "visual_inspection": "PENDING_ACTUAL_IMAGE_READ", "stage_admission": "NOT_ISSUED",
               "other_cost": "UNKNOWN_NOT_ZERO", "old_reservations_reopened": False}
    (marker/"PROCESS.json").write_text(json.dumps(receipt, indent=2)+"\n")


if __name__ == "__main__":
    main()
