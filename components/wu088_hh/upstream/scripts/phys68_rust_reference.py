#!/usr/bin/env python3
"""Build and run the independent PHYS68 Rust binary64 reference.

With --seed a prepared SEED_INPUT.txt is reused and python-flint is not
needed.  New seeds use the unchanged PHYS67 Arb Coulomb initializer at
512 bits.  The Rust integration itself uses no Python or external crates.
This driver is create-only and never runs an old PHYS66 campaign.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SOURCE_DEFAULT = ROOT / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
RUST_SOURCE = Path(__file__).with_suffix(".rs")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_guard(path: Path) -> str:
    value = digest(path)
    if value != SOURCE_SHA256:
        raise ValueError("original frozen source SHA256 mismatch")
    return value


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def validate_seed_text(path: Path, expected_l: int = 28) -> dict:
    """Validate exactly what Rust will parse, including the dyadic f64 values."""
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 5 or int(fields[0]) != len(rows):
            raise ValueError("seed must have consecutive ell plus four numbers")
        values = [float(x) for x in fields[1:]]
        if not all(map(math.isfinite, values)) or complex(*values[:2]) == 0:
            raise ValueError("seed must be finite with nonzero F")
        rows.append({"ell":len(rows),"binary64_hex":[x.hex() for x in values]})
    if len(rows) != expected_l+1 or not 21 <= expected_l <= 64:
        raise ValueError("seed channel count does not match target L in 21..64")
    return {"L":expected_l,"rows":rows,"sha256":digest(path)}


def create_seed(source: Path, destination: Path, lmax: int = 28,
                precision_bits: int = 512) -> tuple[Path, Path]:
    source_guard(source)
    if not 21 <= lmax <= 64 or type(lmax) is not int:
        raise ValueError("L must be an integer in 21..64")
    if precision_bits != 512:
        raise ValueError("this fixed seed contract requires 512 bits")
    if str(ROOT/"src") not in sys.path:
        sys.path.insert(0,str(ROOT/"src"))
    import flint
    from flint import acb, ctx
    from wu088_hh.phys67_coulomb_certificate import (
        complex_ball_record,coulomb_point,outgoing_h_acb,
    )
    started = time.perf_counter()
    rows, lines = [], ["# PHYS68 original atomic seed: B=27 T=65 k=7/10 eta_C=-10/7",
                       "# ell Re(F_T) Im(F_T) Re(d_r_F_T) Im(d_r_F_T); binary64 diagnostics"]
    with ctx.workprec(precision_bits):
        for ell in range(lmax+1):
            point = coulomb_point(ell,65,precision_bits)
            hb = outgoing_h_acb(ell,acb(27))
            if not hb.is_finite() or hb.contains(0):
                raise ArithmeticError("unresolved normalizer in seed generation")
            f,g = point.h_plus/hb,point.h_prime_r/hb
            values = [float(x.mid()) for x in (f.real,f.imag,g.real,g.imag)]
            if not all(map(math.isfinite,values)):
                raise ArithmeticError("nonfinite binary64 seed conversion")
            lines.append(str(ell)+" "+" ".join(format(x,".17e") for x in values))
            rows.append({"ell":ell,"normalized_h_T":complex_ball_record(f),
                         "normalized_d_r_h_T":complex_ball_record(g),
                         "binary64_hex":[x.hex() for x in values]})
    text_path = destination/"SEED_INPUT.txt"
    ball_path = destination/"SEED_BALLS.json"
    text_path.write_text("\n".join(lines)+"\n")
    seed_identity = validate_seed_text(text_path,lmax)
    dump(ball_path,{
        "schema":"PHYS68_RUST_SEED_V1","source_sha256":SOURCE_SHA256,
        "L":lmax,"B":"27","T":"65","k":"7/10","eta_C":"-10/7",
        "precision_bits":precision_bits,"python_flint":flint.__version__,
        "FLINT":flint.__FLINT_VERSION__,"rows":rows,
        "input_text_sha256":seed_identity["sha256"],
        "elapsed_seconds":time.perf_counter()-started,
        "initializer_scope":"Shared PHYS67 Arb Coulomb initializer; Rust angular/ODE/integration is independent.",
        "binary64_conversion_scope":"Recorded midpoint conversions are numerical seeds, not exported interval certificates.",
        "HH_R10":"OFF",
    })
    return text_path,ball_path


def execute(command: list[str], cwd: Path, out: Path, name: str,
            timeout: int = 60) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(command,cwd=cwd,capture_output=True,text=True,
                                   timeout=timeout,check=False)
        stdout,stderr,exit_code = completed.stdout,completed.stderr,completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout,bytes): stdout=stdout.decode(errors="replace")
        if isinstance(stderr,bytes): stderr=stderr.decode(errors="replace")
        exit_code,timed_out = None,True
    (out/f"{name}.stdout.txt").write_text(stdout)
    (out/f"{name}.stderr.txt").write_text(stderr)
    record = {"command":command,"cwd":str(cwd),"exit_code":exit_code,
              "timed_out":timed_out,"elapsed_seconds":time.perf_counter()-started,
              "stdout":f"{name}.stdout.txt","stderr":f"{name}.stderr.txt"}
    dump(out/f"{name}.EXECUTION.json",record)
    if exit_code != 0 or timed_out:
        raise RuntimeError(f"{name} failed; preserved {name}.EXECUTION.json")
    return record


def complex_field(result: dict, key: str) -> complex:
    values = result[key]
    parts = [values["real"],values["imag"]]
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in parts):
        raise ValueError("result components must be finite JSON numbers")
    return complex(*parts)


def compare_refinement(coarse: dict, fine: dict, goal: float = 1e-6) -> dict:
    if fine["steps"] != 2*coarse["steps"]:
        raise ValueError("refinement contract requires exactly doubled steps")
    if (coarse["L"],coarse["m"],coarse["target"],coarse["B"],coarse["T"]) != \
       (fine["L"],fine["m"],fine["target"],fine["B"],fine["T"]):
        raise ValueError("refinement inputs differ")
    c,f = complex_field(coarse,"d2"),complex_field(fine,"d2")
    if f == 0:
        raise ValueError("zero reference needs an explicit absolute-error goal")
    difference = abs(f-c)
    relative = difference/abs(f)
    return {"status":"NUMERICALLY_CHECKED" if relative < goal else "REFINEMENT_GOAL_NOT_MET",
            "coarse_steps":coarse["steps"],"fine_steps":fine["steps"],
            "absolute_difference":difference,"relative_difference":relative,
            "relative_goal":goal,"goal_met":relative < goal,
            "certified_error_bound":False,
            "external_validated_ball_comparison":"PENDING_PARENT_CERTIFICATE"}


def run_reference(source: Path, out: Path, rustc: str,
                  seed: Path | None = None, steps: tuple[int,int] = (2432,4864)) -> dict:
    source_guard(source)
    if len(steps) != 2 or steps[0] < 1 or steps[1] != 2*steps[0]:
        raise ValueError("exactly two positive doubled resolutions required")
    out.mkdir(parents=True,exist_ok=False)
    if seed is None:
        seed_path,ball_path = create_seed(source,out)
    else:
        validate_seed_text(seed,28)
        seed_path = out/"SEED_INPUT.txt"
        shutil.copyfile(seed,seed_path)
        ball_path = None
    rust_file = RUST_SOURCE.resolve()
    commands = []
    commands.append(execute([rustc,"--version"],ROOT,out,"RUST_VERSION"))
    test_binary = out/"phys68_rust_reference_tests"
    binary = out/"phys68_rust_reference"
    commands.append(execute([rustc,"--edition=2021","--test","-O",str(rust_file),"-o",str(test_binary)],ROOT,out,"COMPILE_TESTS"))
    commands.append(execute([str(test_binary)],ROOT,out,"RUST_TESTS"))
    commands.append(execute([rustc,"--edition=2021","-O",str(rust_file),"-o",str(binary)],ROOT,out,"COMPILE_REFERENCE"))
    results = []
    for resolution in steps:
        name = f"RK4_{resolution}"
        commands.append(execute([str(binary),str(resolution),str(seed_path)],ROOT,out,name))
        result = json.loads((out/f"{name}.stdout.txt").read_text())
        complex_field(result,"d2")
        if result["status"] != "COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE":
            raise ValueError("unexpected Rust result status")
        dump(out/f"{name}.json",result)
        results.append(result)
    comparison = compare_refinement(*results)
    dump(out/"REFINEMENT.json",comparison)
    record = {
        "schema":"PHYS68_RUST_REFERENCE_EXECUTION_V1",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "status":"COMPLETED_REFERENCE_WITH_REFINEMENT_CHECK",
        "source_sha256":SOURCE_SHA256,"rust_source_sha256":digest(rust_file),
        "driver_sha256":digest(Path(__file__)),"seed_sha256":digest(seed_path),
        "seed_ball_receipt":str(ball_path.name) if ball_path else None,
        "seed_provenance":"Shared PHYS67 Coulomb initializer; original parameters fixed.",
        "independent_components":["Rust standard-library complex arithmetic","Gauss-Legendre 96 nodes and normalized m=0 basis","backward RK4 Coulomb ODE","all j=0..28 first- and second-Born integrals"],
        "commands":commands,"refinement":comparison,
        "results":[f"RK4_{n}.json" for n in steps],
        "ncp_launches":0,"old_campaign_reruns":0,"HH_R10":"OFF",
        "numeric_reference_is_interval_certificate":False,
    }
    dump(out/"EXECUTION_RECORD.json",record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=SOURCE_DEFAULT)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--rustc",default="rustc")
    parser.add_argument("--seed",type=Path)
    parser.add_argument("--coarse-steps",type=int,default=2432)
    args = parser.parse_args()
    result = run_reference(args.source.resolve(),args.out.resolve(),args.rustc,
                           args.seed.resolve() if args.seed else None,
                           (args.coarse_steps,2*args.coarse_steps))
    print(json.dumps({"status":result["status"],"refinement":result["refinement"]},indent=2))


if __name__ == "__main__":
    main()
