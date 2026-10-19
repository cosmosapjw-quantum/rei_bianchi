#!/usr/bin/env python3
"""Compile the actual candidate scalar module and compare to Decimal oracles."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile

from independent_birth_study import age_moment_decimal, evaluate, phi_decimal, rule

base=Path(__file__).resolve().parent
root=base.parent
parser=argparse.ArgumentParser()
parser.add_argument("--candidate",type=Path,default=root/"repo/research/dossier_ssot_sandbox_20261016/bass_reactive03_positive_birth_20261019/crate/fitted_birth.rs")
parser.add_argument("--toolchain",type=Path,default=root/"toolchains/rust-1.94.1-prefix")
args=parser.parse_args()
candidate=args.candidate.resolve()
toolchain=args.toolchain.resolve()
digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
environment=dict(os.environ)
environment["LD_LIBRARY_PATH"]=str(toolchain/"lib")+":"+environment.get("LD_LIBRARY_PATH","")
rustc=toolchain/"bin/rustc"
version=subprocess.run([str(rustc),"--version"],env=environment,capture_output=True,text=True,check=True).stdout.strip()
with tempfile.TemporaryDirectory(prefix="rei_birth_probe_") as temp:
    probe_dir=Path(temp)
    probe_source=probe_dir/"rust_rule_probe.rs"
    probe_source.write_text((base/"rust_rule_probe.rs").read_text().replace("__REI_FITTED_BIRTH_FILE__",str(candidate)))
    compilation=subprocess.run([str(rustc),"--edition=2024",str(probe_source),"-o",str(probe_dir/"rust_rule_probe")],env=environment,capture_output=True,text=True)
    (base/"RUST_PROBE_BUILD.log").write_text(compilation.stdout+compilation.stderr)
    compilation.check_returncode()
    execution=subprocess.run([str(probe_dir/"rust_rule_probe")],env=environment,capture_output=True,text=True,check=True)
(base/"RUST_SCALAR_GRID.csv").write_text(execution.stdout)
rows=list(csv.DictReader(io.StringIO(execution.stdout)))
worst_phi=worst_species=worst_rust_python_moment=0.
for row in rows:
    tau=float(row["tau"])
    r=int(row["refinement"])
    exact=float(phi_decimal(tau))
    phi=float(row["phi"])
    assert abs(phi-exact)<3e-14*exact
    worst_phi=max(worst_phi,abs(phi-exact)/exact)
    independent=evaluate(tau,rule(tau,r))
    for index,field in enumerate(["survivor_age_mean","survivor_age_second"],start=1):
        ref=float(age_moment_decimal(tau,index))
        independent_moment=ref*(1+independent["age_moment_relative_errors"][index-1])
        diff=abs(float(row[field])-independent_moment)/ref
        worst_rust_python_moment=max(worst_rust_python_moment,diff)
        assert diff<2e-13
    for label,share in zip(["species_h","species_he0","species_he1","species_d"],[.71,.19,.097,.003]):
        # Decimal subtraction avoids losing absorbed photons at tiny τ.
        a=float((1-phi_decimal(tau)))*share
        error=abs(float(row[label])-a)/max(a,1e-300)
        worst_species=max(worst_species,error)
        assert error<5e-14 if a else float(row[label])==0
    assert abs(float(row["number_residual"]))<3e-15
    assert abs(float(row["emission"])-1)<3e-15
    assert abs(float(row["emission_mean"])-.5)<3e-15
assert digest==hashlib.sha256(candidate.read_bytes()).hexdigest(),"candidate mutated during probe"
result={"status":"PASS_SCOPED","candidate_source_sha256":digest,"compiler":version,"candidate_source":str(candidate),"rows":len(rows),"max_phi_relative_error":worst_phi,"max_species_relative_error":worst_species,"max_rust_vs_independent_python_age_moment_relative_difference":worst_rust_python_moment,"reference":"Decimal90 analytic integral plus separately written Python quadrature","scope":"actual scalar module including frozen_inventory; no native thermochemistry or BASS history was executed in this probe"}
(base/"RUST_INDEPENDENT_COMPARISON.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
