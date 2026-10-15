#!/usr/bin/env python3
"""Bounded full current-C11 verification; preserve exit codes and scientific receipt."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ENV={**os.environ,"PYTHONDONTWRITEBYTECODE":"1",
     "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1",
     "CARGO_TARGET_DIR":os.getenv("CARGO_TARGET_DIR","/tmp/rei_source07_c11_cargo_target"),
     "CARGO_BUILD_JOBS":"2"}
commands={}
def record(name,args,cwd=ROOT):
    run=subprocess.run(args,cwd=cwd,env=ENV,text=True,capture_output=True)
    (HERE/(name+".log")).write_text(run.stdout+run.stderr)
    commands[name]={"exit_code":run.returncode,"command":args,"run_cwd":str(cwd)}
    print(name,"exit",run.returncode,"stdout",len(run.stdout),"stderr",len(run.stderr),flush=True)
    if run.returncode!=0:
        print((run.stdout+run.stderr)[-1400:])
        raise RuntimeError("FAILED_"+name)
    return run

def main():
    for path in HERE.glob("*.py"):
        record("PYCOMPILE_"+path.stem,[sys.executable,"-m","py_compile",str(path)])
    for folder in ("source07_c9_heii_vector_20261015",
                   "source07_c10_dynamic_20261015",
                   "source07_c11_casea_20261015"):
        name="TESTS_"+folder.replace("_20261015","")
        run=record(name,[sys.executable,"-m","unittest","discover",
                          "-s","research/"+folder,"-p","test_*.py","-v"])
        if "FAILED" in run.stderr or "OK" not in run.stderr:
            raise RuntimeError("TEST_RESULT_NOT_OK")
    record("C11_RUST",[os.environ.get("CARGO","cargo"),"check",
                        "--offline","--example","source07_c11_rates"],
           cwd=ROOT/"rust/rei_microphysics")
    record("GIT_DIFF",["git","diff","--check"])
    a=json.loads((HERE/"study_results.json").read_text())
    r=json.loads((HERE/"RATE_VALIDATION.json").read_text())
    z=json.loads((HERE/"ZERO_RATE_CONTROL.json").read_text())
    assert r["PASS"] and r["highest_relative_difference"]<2e-7
    assert 2<a["matched_benchmark"]["dense_vs_compressed_speedup"]<4
    assert a["parallel_batch"]["science_byte_float_exact_match"]
    for name,value in a["canonical_cases"].items():
        assert value["max_energy_residual_eV_per_H"]<1e-10,name
        assert value["max_electron_photon_residual_per_H"]<1e-10,name
    for k in ("bb50k","hard"):
        assert a["compression_error"][k]["Tgas_K"]["max_abs"]<0.001
        for key in ("x_HII","Tgas_K"):
            assert all(1.8<v<2.2 for v in a["time_convergence"][k]["metrics"][key]["estimated_order"])
    assert len(z["cases"])==2
    assert all(c["delta_T_sign"]=="positive" and
               c["delta_thermal_energy_sign"]=="negative" for c in z["cases"])
    assert hashlib.sha256((HERE/"owner_grackle_rates_129.csv").read_bytes()).hexdigest()==r["table_sha256"]
    assert hashlib.sha256((ROOT/"rust/rei_microphysics/src/igm_rates.rs").read_bytes()).hexdigest()==r["rust_owner_sha256"]
    data={"schema":"rei.source07.c11.local_verification.v1",
          "base_commit":"26177f10d2c3264189980af2de26b3f63a9227fc",
          "status":"PASS_SCOPED","scope":"C11 Case A stationary proper receiver only",
          "commands":commands,
          "source_sha256":r["rust_owner_sha256"],
          "rate_table_sha256":r["table_sha256"],
          "max_provider_holdout_relative_error":r["highest_relative_difference"],
          "scoped_conservation_and_convergence":True,
          "native_subagent":"NOT_RUN",
          "production_admission":"NOT_ISSUED"}
    (HERE/"VERIFICATION.json").write_text(json.dumps(data,indent=2)+"\n")
    print("LOCAL_VERIFICATION_PASS",len(commands),"commands",flush=True)


if __name__=="__main__":
    main()
