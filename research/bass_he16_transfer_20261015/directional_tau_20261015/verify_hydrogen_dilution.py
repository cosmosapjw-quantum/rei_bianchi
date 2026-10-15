"""Read-only five-case hydrogen-number dilution check for the goal budget."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import math
from pathlib import Path
import time

CASES=("SHEAR_MINUS","SHEAR_HALF_MINUS","ZERO","SHEAR_HALF_PLUS","SHEAR_PLUS")
EXPECTED_SOURCE="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
EXPECTED_NH_REF=0.0017579215852062606

def check(root,case,declared_sha):
    hist=root/("flrw" if case=="ZERO" else "paired")/"32d11e733155"/case/"history.csv"
    if not hist.is_file():raise ValueError("Missing source history")
    sh=hashlib.sha256()
    with hist.open("rb") as infile:
        for block in iter(lambda:infile.read(2**20),b""):
            sh.update(block)
    sha=sh.hexdigest()
    if sha!=declared_sha:raise ValueError("History source hash mismatch for "+case)
    it=0;dev=0.0;first=None
    with hist.open(newline="") as f:
        rd=csv.DictReader(f)
        for r in rd:
            if not r:continue
            if r["case_id"]!=case:raise ValueError("Case identity mismatch")
            a=float(r["a"]);nh=float(r["nH_proper_cm3"])
            if not math.isfinite(a) or not math.isfinite(nh) or a<=0 or nh<=0:
                raise ValueError("Unphysical hydrogen state")
            if first is None:
                first=nh*a**3
                if abs(nh-EXPECTED_NH_REF)>5e-18:
                    raise ValueError("Cold nH reference mismatch")
            dev=max(dev,abs(nh*a**3/first-1))
            it+=1
    if it!=200001:raise ValueError("Unexpected prefix source row count")
    return {"case":case,"input_sha256":sha,"rows":it,
            "reference_nH_proper_cm3":EXPECTED_NH_REF,
            "max_rel_nH_a3_dilution_error":dev}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--source-manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(args.source_manifest.read_text())
    ts=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        result=list(pool.map(lambda case:check(args.source_root,case,
                        data["cases"][case]["history_sha256"]), CASES))
    output={"schema":"he18.axbi.hydrogen_dilution_five_case.v1",
            "status":"READ_ONLY_SOURCE_SCOPED_IDENTITY_AND_DILUTION_CHECK",
            "results":result,
            "max_abs_normalized_deviation":max(x["max_rel_nH_a3_dilution_error"] for x in result),
            "elapsed_s":time.perf_counter()-ts}
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
if __name__=="__main__":main()
