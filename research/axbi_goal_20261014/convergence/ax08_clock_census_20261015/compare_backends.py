#!/usr/bin/env python3
"""Compare independently implemented Rust vs Python whole-source abundance audit."""
import argparse,hashlib,json,math,re
from pathlib import Path

CASES=("ZERO","SHEAR_HALF_PLUS")
RUST_KEYS=("species_number","history_fraction","electron_charge",
           "electron_xe","H_number","He_number","Ybaryon_sum",
           "gas_temperature","electron_history")
def read_json(p):
    d=json.loads(Path(p).read_text())
    if not isinstance(d,dict):raise ValueError("BAD_RESULT")
    return d

def check(final_python,final_rust,serial_python,output):
    py=read_json(final_python/"CLOCK_CENSUS_RESULT.json")
    old=read_json(serial_python/"CLOCK_CENSUS_RESULT.json")
    if py["nodes"]!=old["nodes"] or py["nodes"]!=4097:
        raise ValueError("GRID_CHANGED")
    assert py["source_sha256"]==old["source_sha256"]
    for name in py["observables"]:
        for key,val in py["observables"][name].items():
            if isinstance(val,(int,float)) and old["observables"][name][key]!=val:
                raise ValueError("SERIAL_PARALLEL_OBSERVABLE_MISMATCH")
    checks={}
    for case in CASES:
        rust=read_json(final_rust/(case+".json"))
        p=py["workload"][case]
        if rust["case"]!=case or rust["history_rows"]!=312238 or rust["ion_rows"]!=1873428:
            raise ValueError("RUST_FULL_SOURCE_INCOMPLETE")
        if not rust["all_pass"] or p["census"]["rows"]!=1873428:
            raise ValueError("SOURCE_CENSUS_NOT_CHECKED")
        maxima=[]
        for i,key in enumerate(RUST_KEYS):
            v=float(rust["max_abs_residuals"][i])
            q=float(p["census"]["max_abs_residuals"][key])
            if abs(v-q)>2e-15:
                raise ValueError(f"RUST_PYTHON_PHYSICS_MISMATCH:{case}:{key}:{v},{q}")
            maxima.append((key,v,q))
        if p["census"]["max_abs_residuals"]["electron_history_row"]>5e-9:
            raise ValueError("INDEPENDENT_CHARGE_REPR_FAILED")
        checks[case]=dict(rust_full_ion_rows=rust["ion_rows"],
           python_full_ion_rows=p["census"]["rows"],max_residuals=maxima,
           rust_scanned_seconds=rust["seconds"],
           python_scanned_seconds=p["census"]["duration_s"],
           matched_workload_audit_speedup=p["census"]["duration_s"]/rust["seconds"],
           numerical_identity_atol=2e-15,
           numerical_equivalence_pass=True)
    result=dict(schema="rei.axbi.full_clock_census.backend_comparison.v1",
       source_tracked_SHA=py["source_sha256"],
       original_complete_cases=list(CASES),
       count_provenance_cases=2,
       full_input_abundance_rows=2*1873428,
       parallel_history_and_ionization_wall_s=py["timing_s"],
       serial_history_and_ionization_wall_s=old["timing_s"],
       measured_whole_workflow_speedup=old["timing_s"]/py["timing_s"],
       rust_audit=checks,
       mathematical_data_sampling_unchanged=True,
       source_solver_reexecuted=False,
       scientific_claim="SAVED_OUTPUT_CENSUS_VALIDATED_CLOCK_DIAGNOSTIC_UNCERTIFIED_AX11",
       actual_native_Codex_invoked=False)
    if output.exists():raise ValueError("REFUSE_OVERWRITE")
    output.write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--python-parallel",type=Path,required=True)
    a.add_argument("--python-serial",type=Path,required=True)
    a.add_argument("--rust-results",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    z=a.parse_args()
    res=check(z.python_parallel,z.rust_results,z.python_serial,z.output)
    print(json.dumps({k:res[k] for k in ("full_input_abundance_rows",
      "measured_whole_workflow_speedup","parallel_history_and_ionization_wall_s",
      "serial_history_and_ionization_wall_s","rust_audit")},indent=2))
