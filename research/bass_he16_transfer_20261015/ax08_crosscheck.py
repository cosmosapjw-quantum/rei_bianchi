"""Source-identity reconciliation with the pre-existing AX08 signed prefix study.

No scientific certification or reanalysis of the native angular integrator.
"""
import argparse
import json
from pathlib import Path
import hashlib

CASES=("SHEAR_MINUS","SHEAR_HALF_MINUS","ZERO","SHEAR_HALF_PLUS","SHEAR_PLUS")
SOURCE_SHA="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def crosscheck(ax08,root,native_source=None):
    if ax08.get("schema")!="rei.axbi.signed_prefix_parity.v1":
        raise ValueError("Unexpected AX08 parity schema")
    if ax08.get("scientific_admission")!="NOT_ISSUED":
        raise ValueError("Unexpected AX08 admission state")
    agreed={}
    for case in CASES:
        current=json.loads((root/(case+".json")).read_text())
        legacy=ax08["cases"][case]
        if legacy["history_sha256"]!=current["history_sha256"]:
            raise ValueError(f"History input mismatch {case}")
        if legacy["source_identity_sha256"]!=SOURCE_SHA:
            raise ValueError(f"Source epoch mismatch {case}")
        agreed[case]=current["history_sha256"]
    j2=ax08["metrics"]["J2_photon_u_eV_per_H"]
    o01=j2["odd_at_q_0p01"]["endpoint"]
    o005=j2["odd_at_q_0p005"]["endpoint"]
    if o005==0:raise ValueError("Null J2 denominator")
    ratio=o01/o005
    native_identity=None
    if native_source is not None:
        data=native_source.read_text()
        if 'moments[2] += u * (3.0 * mu * mu - 1.0) / 2.0;' not in data:
            raise ValueError("Rust native J2 formula no longer matches recorded convention")
        native_identity=sha256(native_source)
    signed=json.loads((root/"SIGNED_RESPONSE.json").read_text())
    return {
       "schema":"he18.axbi.original_ax08_bridge.v1",
       "input_hashes_equal":True,
       "native_source_sha256":native_identity,
       "j2_definition":"sum photon_N_perH * energy_eV * P2(mu_current)",
       "j2_odd_q010_eV_per_H":o01,
       "j2_odd_q005_eV_per_H":o005,
       "j2_odd_ratio":ratio,
       "j2_even_q010_abs_endpoint_eV_per_H":j2["even_at_q_0p01"]["endpoint"],
       "tau_even_q010":signed["even_half_q010"][-1],
       "tau_even_q005":signed["even_half_q005"][-1],
       "tau_even_ratio":signed["even_ratio_q010_to_q005"][-1],
       "data_history_sha256":agreed,
       "interpretation":"Existing AX08 J2 result reused; novel tau/clock analysis stored separately. No CMB polarization or solver convergence claim.",
       "scientific_admission":"NOT_ISSUED"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ax08",type=Path,required=True)
    p.add_argument("--signed-report-dir",type=Path,required=True)
    p.add_argument("--native-source",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=crosscheck(json.loads(args.ax08.read_text()),args.signed_report_dir,args.native_source)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
