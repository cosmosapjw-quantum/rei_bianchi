"""Recompute matched BASS/REC/REI and local material-transfer experiments from one checkout."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "components/bass_rec")]
from rei_bianchi.microphysics import cr
from rei_bianchi.microphysics.experiment import consume_live, late_cell
import run_material_trace
import run_smoke


def build_transfer(offline):
    command = ["cargo", "build", "--locked", "--manifest-path",
               str(ROOT / "rust/rei_microphysics/Cargo.toml"), "--example", "material_exchange",
               "--message-format=json"]
    if offline:
        command.append("--offline")
    run = subprocess.run(command, text=True, stdout=subprocess.PIPE, check=True)
    for line in run.stdout.splitlines():
        entry = json.loads(line)
        if entry.get("executable") and entry["target"]["name"] == "material_exchange":
            return Path(entry["executable"])
    raise RuntimeError("The Rust build returned no material_exchange executable")


def run(output, offline):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as td:
        result_dir = Path(td) / "results"
        result_dir.mkdir()
        transfer = build_transfer(offline)
        smoke = run_smoke.run(result_dir / "native", offline)
        traces = run_material_trace.run(result_dir / "matched_trace", offline)
        native = result_dir / "native/live_rei"
        reconstructed = consume_live(native / "history.tsv", native / "uv_exchange.tsv")
        cases = {}
        for name in sorted(cr.axbi_snapshots()["rows"]):
            cases[name] = {state:late_cell(transfer, name, enabled=enabled)
                           for state, enabled in (("source_on", True), ("source_off", False))}
        report = {
            "schema":"rei.unified.igm.experiment.v1",
            "native":smoke, "native_energy_and_trace":reconstructed,
            "matched_short_window":traces["matched_q_comparisons"],
            "matched_proper_time_controls":traces["matched_proper_time_controls"],
            "axbi_fixed_volume_cells":cases,
            "interpretation":"The live z=20 run uses a passive D tracer and primary H/He absorptions. The low-z calculations are separate finite-cell interventions on original AXBI samples with prescribed CR injection. These epochs have independent initial conditions."
        }
        (result_dir / "RESULTS.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        result_dir.rename(output)
    return output / "RESULTS.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new output directory")
    parser.add_argument("--offline", action="store_true", help="use an already populated Cargo cache")
    args = parser.parse_args()
    print(run(args.output, args.offline))
