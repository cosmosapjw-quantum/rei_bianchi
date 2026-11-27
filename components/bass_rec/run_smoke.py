"""Exercise matched BASS/REC and BASS/REI evolution from a single checkout."""
import argparse
import csv
import json
import math
import pathlib
import subprocess
import tempfile

BASE = pathlib.Path(__file__).resolve().parent
CRATE = BASE / "bass/_rustcore/Cargo.toml"


def run_example(name, arguments, offline):
    command = ["cargo", "run", "--locked", "--manifest-path", str(CRATE)]
    if offline:
        command.append("--offline")
    subprocess.run(command + ["--example", name, "--", *map(str, arguments)], check=True)


def read_table(path):
    with path.open() as stream:
        return [{name: float(value) for name, value in row.items()}
                for row in csv.DictReader(stream, delimiter="\t")]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def run(output, offline):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        destination = pathlib.Path(temporary) / "results"
        destination.mkdir()
        early = destination / "matched_rec"
        late = destination / "live_rei"
        fixture = BASE / "bass/research/r109_native_sky/hyrec_1100"
        source = json.loads((fixture / "source.json").read_text())
        donor = json.loads((BASE / "fixtures/REC_HMLA_Z20.json").read_text())
        initial = donor["initial"]
        run_example("homogeneous_sky", [
            "--out", early, "--family", "I", "--shear", "0.02",
            "--duration", "0.02", "--steps", "8", "--nmu", "6", "--nphi", "12",
            "--lmax", "2", "--recombination", "matched", "--feedback", "recoil",
            "--dust-fraction", "0.7554963357761493", "--dust-beta", "0,0,0",
            "--ionization", fixture / "hyrec_xe.tsv",
            "--n-h-emit-m3", source["n_h_emit_m3"], "--h-emit-s", source["h_emit_s"],
            "--t-unit-k", 2.72548 * (1 + source["z_emit"]),
        ], offline)
        run_example("rei_live_characteristics", [
            late, "19.999", "4", "0.005", "4", "8", initial["x_HII"], initial["T_m_K"],
        ], offline)
        rec = read_table(early / "recombination.tsv")
        rei = read_table(late / "history.tsv")
        check(len(rec) == 9 and len(rei) == 5, "Unexpected number of native states")
        for rows in [rec, rei]:
            check(all(math.isfinite(v) for row in rows for v in row.values()), "Nonfinite native output")
            check(all(right["eta"] > left["eta"] for left, right in zip(rows, rows[1:])),
                  "Native clock must increase")
        check(rec[0]["delta_xe"] == 0.0 and rec[-1]["delta_xe"] != 0.0, "Matched REC update was inactive")
        check(math.isclose(rec[-1]["eta"], 0.02, abs_tol=1e-15), "Incomplete matched interval")
        check(math.isclose(rei[-1]["eta"], math.log(21 / 20.999), abs_tol=1e-15), "Incomplete REI interval")
        check(math.isclose(rei[0]["x_HII"], initial["x_HII"], rel_tol=1e-14), "REC H boundary mismatch")
        check(math.isclose(rei[0]["Tm_K"], initial["T_m_K"], rel_tol=1e-14), "REC thermal boundary mismatch")
        check(rei[-1]["emitted_N"] > 0.0 and rei[-1]["absorbed_N"] > 0.0, "Native UV transport was inactive")
        max_number = max(abs(r["number_defect"]) for r in rei)
        max_energy = max(abs(r["energy_defect"]) for r in rei)
        summary = {
            "schema": "rei.unified.native-smoke.v1",
            "matched_rec": {"z_emit": 1100, "ending_eta": rec[-1]["eta"],
                            "steps": len(rec) - 1, "final_delta_xe_per_H": rec[-1]["delta_xe"]},
            "live_rei": {"z_start": 20, "z_end": 19.999, "q_ref": 0.005,
                         "steps": len(rei) - 1, "initial_donor_sha256": donor["full_donor_sha256"],
                         "final_x_HII": rei[-1]["x_HII"], "final_T_K": rei[-1]["Tm_K"],
                         "final_absorbed_photons_per_H": rei[-1]["absorbed_N"],
                         "max_number_defect": max_number, "max_energy_defect": max_energy},
            "scope": "Two finite native smoke intervals. The late run consumes the independent REC z=20 HMLA donor and evolves REI on BASS geometry. Geometry feedback from REI is disabled on this CLI.",
        }
        (destination / "SMOKE.json").write_text(json.dumps(summary, indent=2) + "\n")
        destination.rename(output)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.offline), indent=2))
