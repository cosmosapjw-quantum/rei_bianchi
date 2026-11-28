"""Run the accepted BASS/REI tracer and validate it against the stored native fields."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from run_smoke import BASE, check, read_table, run_example

# Use the original owner calculation on the serialized history as a separate check.
sys.path.insert(0, str(BASE.parents[1] / "src"))
from rei_bianchi.microphysics import he, hh


def same(measured, expected, name):
    check(math.isclose(measured, expected, rel_tol=3e-10, abs_tol=1e-26), name)


def inspect(folder):
    history = read_table(folder / "history.tsv")
    uv = read_table(folder / "uv_exchange.tsv")
    trace = read_table(folder / "material_trace.tsv")
    check(len(history) == 1 + len(trace) == len(uv), "Missing accepted rows")
    y = history[0]["x_HII"]
    d_error, heat_error, absorbed_error = 0., 0., 0.
    species = tuple(he.BINDING_EV)
    for i, row in enumerate(trace):
        left, right = history[i:i + 2]
        before, after = uv[i:i + 2]
        check(row["eta"] == right["eta"] == after["eta"], "Native clock mismatch")
        dt = right["time_s"] - left["time_s"]
        mean = lambda name: 0.5 * (left[name] + right[name])
        y = hh.trace_step(y, dt, mean("Tm_K"), mean("nH_m3") * 1e-6, mean("x_HII"))
        d_error = max(d_error, abs(y - row["y_DII"]))
        same(row["y_DII"], y, "Independent stored-history D evolution")
        for absorber, threshold in he.BINDING_EV.items():
            delta = right["photo_" + absorber] - left["photo_" + absorber]
            same(row[absorber + "_events_per_H"], delta, "Accepted events " + absorber)
            same(row[absorber + "_binding_eV_per_H"], threshold * delta, "Ionization work " + absorber)
        heat = math.fsum(row[s + "_heat_eV_per_H"] for s in species)
        bound = math.fsum(row[s + "_binding_eV_per_H"] for s in species)
        dh = after["heat_U"] - before["heat_U"]
        du = after["absorbed_U"] - before["absorbed_U"]
        same(heat, dh, "Per-absorber heat total")
        same(heat + bound, du, "Absorbed energy partition")
        same(row["absorbed_eV_per_H"], du, "Accepted packet energy loss")
        heat_error = max(heat_error, abs(heat - dh))
        absorbed_error = max(absorbed_error, abs(heat + bound - du))
    total_heat = {s: math.fsum(r[s+"_heat_eV_per_H"] for r in trace) for s in species}
    total_bound = {s: math.fsum(r[s+"_binding_eV_per_H"] for r in trace) for s in species}
    return {
        "elapsed_proper_s": history[-1]["time_s"], "final_H_s": history[-1]["H_s"],
        "accepted_steps": len(trace), "x_HII": history[-1]["x_HII"], "T_K": history[-1]["Tm_K"],
        "initial_y_DII": history[0]["x_HII"], "final_y_DII": trace[-1]["y_DII"],
        "heat_eV_per_H": total_heat, "binding_eV_per_H": total_bound,
        "absorbed_eV_per_H": uv[-1]["absorbed_U"],
        "max_stored_DII_difference": d_error, "max_step_heat_difference_eV_per_H": heat_error,
        "max_step_partition_difference_eV_per_H": absorbed_error,
    }


def run(output, offline):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    initial = json.loads((BASE / "fixtures/REC_HMLA_Z20.json").read_text())["initial"]
    with TemporaryDirectory(dir=output.parent) as tmp:
        dest = Path(tmp) / "results"
        dest.mkdir()
        cases, pairs, clock_controls = {}, [], []
        controls = (4, 8, 16, 32, 64)
        for steps in controls:
            q_cases = {}
            for q in (-0.005, 0.0, 0.005):
                name = f"q{q:+.3f}_n{steps}"
                where = dest / name
                args = ["19.999", str(steps), str(q), "4", "8", initial["x_HII"], initial["T_m_K"]]
                run_example("rei_live_characteristics", [where, *args, "--material-trace"], offline)
                data = inspect(where)
                cases[name] = data
                q_cases[q] = data
                if steps == 4 and q == 0.005:
                    plain = dest / "default_smoke"
                    run_example("rei_live_characteristics", [plain, *args], offline)
                    parity = {}
                    for file in sorted(plain.iterdir()):
                        if file.name == "run.txt":
                            continue
                        content = file.read_bytes()
                        check(content == (where / file.name).read_bytes(), "Passive compatibility " + file.name)
                        parity[file.name] = hashlib.sha256(content).hexdigest()
            pairs.append({
                "accepted_steps": steps,
                "even_y_DII_difference": 0.5 * (q_cases[-0.005]["final_y_DII"] + q_cases[0.005]["final_y_DII"]) - q_cases[0.0]["final_y_DII"],
                "odd_y_DII_half_difference": 0.5 * (q_cases[0.005]["final_y_DII"] - q_cases[-0.005]["final_y_DII"]),
                "even_absorbed_eV_per_H_difference": 0.5*(q_cases[-0.005]["absorbed_eV_per_H"]+q_cases[0.005]["absorbed_eV_per_H"])-q_cases[0.0]["absorbed_eV_per_H"],
            })
            if steps >= 32:
                # Compare at common proper time as well as common redshift.
                # dt/dz = -1/[(1+z)H] supplies the first endpoint correction.
                anisotropic, flrw = q_cases[0.005], q_cases[0.0]
                end_z = 19.999
                residual_s = anisotropic["elapsed_proper_s"] - flrw["elapsed_proper_s"]
                end_z += residual_s * (1.0 + end_z) * anisotropic["final_H_s"]
                where = dest / f"clock_matched_n{steps}"
                run_example("rei_live_characteristics", [
                    where, end_z, steps, 0.005, 4, 8, initial["x_HII"], initial["T_m_K"],
                    "--material-trace",
                ], offline)
                matched = inspect(where)
                matched_s = matched["elapsed_proper_s"] - flrw["elapsed_proper_s"]
                check(abs(matched_s) <= 3., "Proper-time control differs by more than 3 s")
                clock_controls.append({
                    "accepted_steps": steps, "q": 0.005, "FLRW_end_z": 19.999,
                    "adjusted_end_z": end_z, "fixed_z_time_difference_s": residual_s,
                    "matched_time_difference_s": matched_s,
                    "fixed_z_y_DII_difference": anisotropic["final_y_DII"] - flrw["final_y_DII"],
                    "matched_time_y_DII_difference": matched["final_y_DII"] - flrw["final_y_DII"],
                    "matched_time_absorbed_eV_per_H_difference": matched["absorbed_eV_per_H"] - flrw["absorbed_eV_per_H"],
                    "matched_state": matched,
                })
        summary = {
            "schema": "rei.unified.accepted-trace.v1", "z_start": 20.0, "z_end": 19.999,
            "energy_subdivisions": 4, "n_mu": 8, "cosmic_ray_source": "OFF",
            "D_feedback_on_gas": False, "additional_photo_sinks_applied": 0,
            "initialization": "y_DII=x_HII independently at the z=20 REC boundary",
            "source": "BASS live accepted LRS-I records, native REI case-A primary photoabsorption",
            "time_discretization": "Native source changes with temporal resolution. Fixed angular and spectral quadratures.",
            "cases": cases, "matched_q_comparisons": pairs, "matched_proper_time_controls": clock_controls,
            "default_vs_online_sha256": parity,
        }
        (dest / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        dest.rename(output)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    result = run(args.output, args.offline)
    print(json.dumps(result["matched_q_comparisons"], indent=2))
