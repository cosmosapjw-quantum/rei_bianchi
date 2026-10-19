#!/usr/bin/env python3
"""Execute the Rust package/VigilODE adapter on frozen IEEE64 coefficients.

No native gas RHS, trajectory integration, or RUN17 numerical solve is run.
The Python reference is read for independent exact-rational comparison, not
used to generate any dense polynomial value submitted to Rust.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

sys.dont_write_bytecode = True
FIXTURE_SHA = "288dd0359c5234cf9777bf757a2a7e0174a0c60a242e81e2471d4b6893e6fa03"
REFERENCE_SHA = "533e9e3a2b75b691c3d63e630c81ceba8df82dc226ec3fc3680148c9003d70b6"


def identity(path):
    path = Path(path)
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", required=True, type=Path)
    ap.add_argument("--reference", required=True, type=Path)
    ap.add_argument("--binary", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    start = time.perf_counter()
    if identity(args.fixture)["sha256"] != FIXTURE_SHA or identity(args.reference)["sha256"] != REFERENCE_SHA:
        raise ValueError("frozen input/reference byte mismatch")
    fixture = json.loads(args.fixture.read_text())
    reference = json.loads(args.reference.read_text())
    pieces, dim = fixture["pieces"], fixture["components"]
    if (pieces,dim) != (23,257):
        raise ValueError("23 saved pieces and257 gas/depth components required")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    commands = []
    for i in range(pieces):
        for j in range(dim):
            commands.append(" ".join(["END", f"p{i:02}_c{j:03}",
                fixture["dense_t_old_bits"][i], fixture["dense_h_bits"][i],
                fixture["accepted_z_bits"][i+1], fixture["dense_y_old_bits"][i][j],
                fixture["accepted_y_bits"][i+1][j],
                *[fixture["dense_F_bits"][i][k][j] for k in range(7)]]))
    input_bytes = ("\n".join(commands)+"\n").encode("ascii")
    with (out/"EXACT_ENDPOINT_INPUT.tsv").open("xb") as stream:
        stream.write(input_bytes)
    before = time.perf_counter()
    process = subprocess.run([str(args.binary.resolve())], input=input_bytes,
                             capture_output=True, timeout=25)
    rust_endpoint_wall = time.perf_counter()-before
    with (out/"EXACT_ENDPOINT_OUTPUT.jsonl").open("xb") as stream:
        stream.write(process.stdout)
    with (out/"EXACT_ENDPOINT.stderr.txt").open("xb") as stream:
        stream.write(process.stderr)
    if process.returncode != 0:
        save(out/"FAILURE.json", {"stage":"rust_endpoints", "returncode":process.returncode,
            "stderr":process.stderr.decode(errors="replace"), "native_gas_calls":0})
        raise RuntimeError("Rust endpoint evaluation failed; raw logs preserved")
    rows = [json.loads(line) for line in process.stdout.splitlines()]
    if len(rows) != pieces*dim:
        raise ValueError("Rust row count mismatch")
    grid = [rows[i*dim:(i+1)*dim] for i in range(pieces)]
    cumulative = [Q(0) for _ in range(dim)]
    all_offsets, all_jumps, derivative_jumps, repair = [], [], [], []
    gamma = Q(0)
    jump_radius = Q(0)
    exact_comparisons = 0
    for i in range(pieces):
        all_offsets.append(cumulative.copy())
        if cumulative != list(map(Q,reference["cumulative_offsets_at_piece_start"][i])):
            raise AssertionError("Rust-derived cumulative offset/reference mismatch")
        jump = [Q(row["jump"]) for row in grid[i]]
        expected = reference["internal_value_jumps"][i] if i < pieces-1 else reference["terminal_stored_endpoint_minus_polynomial"]
        for j, row in enumerate(grid[i]):
            if row["id"] != f"p{i:02}_c{j:03}" or Q(row["x_end"]) != Q(reference["clock_scales"][i]):
                raise AssertionError("Rust identifier/clock mismatch")
            if jump[j] != Q(expected[j]) or not row["exact_value_and_derivative_included"]:
                raise AssertionError("Rust exact jump or VigilODE inclusion mismatch")
            exact_comparisons += 1
        depth_lower = min(Q(row["bernstein_min"]) for row in grid[i][5:])
        offset_norm = max(abs(c) for c in cumulative[5:])
        gamma = max(gamma,offset_norm)
        conservative = depth_lower-offset_norm
        componentwise = min(Q(grid[i][j]["bernstein_min"])-cumulative[j] for j in range(5,dim))
        ref_lower = reference["repair_positivity"][i]
        if depth_lower != Q(ref_lower["original_all_depth_lower"]) or conservative != Q(ref_lower["repair_all_depth_lower"]):
            raise AssertionError("Rust Bernstein repair bound/reference mismatch")
        if conservative < 0 or componentwise < 0:
            raise AssertionError("repaired depth positivity not established by these coefficients")
        repair.append({"piece":i, "original_depth_Bernstein_min":str(depth_lower),
            "offset_norm":str(offset_norm), "uniform_repaired_depth_lower":str(conservative),
            "componentwise_repaired_depth_lower":str(componentwise),
            "nonnegative_exactly_checked":True})
        all_jumps.append(jump)
        if i < pieces-1:
            dj = [Q(grid[i+1][j]["start_derivative"])-Q(grid[i][j]["derivative"]) for j in range(dim)]
            if dj != list(map(Q,reference["internal_derivative_jumps"][i])):
                raise AssertionError("Rust exact derivative jumps/reference mismatch")
            derivative_jumps.append(dj)
            jump_radius += max(abs(v) for v in jump[5:])
            cumulative = [c+v for c,v in zip(cumulative,jump)]
    if gamma != Q(reference["gamma_all_pieces"]):
        raise AssertionError("Gamma mismatch")
    beta_input=f"BETA repair {gamma.numerator} {gamma.denominator}\n".encode("ascii")
    with (out/"BETA_INPUT.tsv").open("xb") as stream:
        stream.write(beta_input)
    before=time.perf_counter()
    beta_process=subprocess.run([str(args.binary.resolve())],input=beta_input,
                                capture_output=True,timeout=5)
    beta_wall=time.perf_counter()-before
    with (out/"BETA_OUTPUT.json").open("xb") as stream:
        stream.write(beta_process.stdout)
    with (out/"BETA.stderr.txt").open("xb") as stream:
        stream.write(beta_process.stderr)
    if beta_process.returncode != 0:
        raise RuntimeError("Rust beta calculation failed")
    beta=json.loads(beta_process.stdout)
    if Q(beta["gamma"]) != gamma or Q(beta["beta"]) != Q(reference["beta_all_pieces"]):
        raise AssertionError("Rust beta/reference mismatch")
    groups={}
    for name,indices in [("gas_q5",range(5)),("depth252",range(5,dim))]:
        internal=[all_jumps[i][j] for i in range(pieces-1) for j in indices]
        dj=[derivative_jumps[i][j] for i in range(pieces-1) for j in indices]
        groups[name]={"internal_components":len(internal),"nonzero_internal_value_jumps":sum(v!=0 for v in internal),
            "max_abs_value_jump":str(max(abs(v) for v in internal)),
            "max_abs_derivative_jump":str(max(abs(v) for v in dj)),
            "derivative_jump_scope":"one-sided derivative discrepancy, not a first-order state-residual atom"}
    result={"schema":"rei.run18.rust-exact-vigilode-adapter.v1",
        "status":"IMPLEMENTATION_VERIFIED_EXACT_STORED_POLYNOMIAL_CHECKS",
        "source_fixture":identity(args.fixture),"independent_python_reference":identity(args.reference),
        "binary":identity(args.binary),"driver":identity(__file__),
        "pieces":pieces,"gas_components":5,"depth_components":252,
        "exact_endpoint_jump_comparisons":exact_comparisons,
        "vigilode_interval_value_inclusions":pieces*dim,
        "vigilode_interval_derivative_inclusions":pieces*dim,
        "interval_inclusion_compared_to":"BigRational exact real values, not rounded f64 approximations",
        "exact_state_and_derivative_reference_comparison":True,
        "all_clock_scales_exactly_one":all(Q(row["x_end"])==1 for row in rows),
        "groups":groups,"gamma":str(gamma),"gamma_float_for_display":float(gamma),
        "beta":beta["beta"],"beta_float_for_display":float(Q(beta["beta"])),
        "sum_internal_depth_jump_infinity_norms":str(jump_radius),
        "vigilode_repair_beta_interval_bits":beta["vigilode_interval_bits"],
        "repair_Bernstein_checks":repair,"all_repaired_depths_nonnegative":True,
        "terminal_endpoint_mismatches":sum(v!=0 for v in all_jumps[-1]),
        "state_jump_orientation":"accepted start of next piece minus previous exact polynomial endpoint",
        "repair":"tau_tilde_i = tau_i - sum(previous internal jumps), with zero initial offset",
        "bound_scope":"Only positivity and relative survivor change from this exact C0 representation repair; no gas-tube, spectral, or exact-IVP bound",
        "actual_rust_cli_processes":2,"native_gas_RHS_calls":0,"new_IVP_solves":0,
        "historical_M2_reruns":0,"quadrature_calls":0,
        "rust_endpoint_wall_seconds":rust_endpoint_wall,"rust_beta_wall_seconds":beta_wall,
        "total_wall_seconds":time.perf_counter()-start,"command_argv":sys.argv,
        "environment":{"python":sys.version,"platform":platform.platform()},
        "files":[identity(p) for p in sorted(out.iterdir()) if p.is_file()]}
    save(out/"RUST_EXACT_VIGILODE_RESULT.json",result)
    print(json.dumps({k:result[k] for k in ["status","pieces","exact_endpoint_jump_comparisons",
        "vigilode_interval_value_inclusions","groups","gamma","beta","actual_rust_cli_processes",
        "rust_endpoint_wall_seconds","total_wall_seconds"]},allow_nan=False))


if __name__ == "__main__":
    main()
