#!/usr/bin/env python3
"""Same-author adversarial audit: independent Decimal photon optical-depth formula and original-ray join."""
import csv
import gzip
import hashlib
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
IN=ROOT/"source_inputs"
OUT=ROOT/"results"
F_D=2.5e-5
C_SIGMA=29979245800.0*6.6524587051e-25
H=1e-14
NH0=1e-4
TO=1e13
SHA_SKY="41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d"

def run():
    original=IN/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz"
    if hashlib.sha256(original.read_bytes()).hexdigest()!=SHA_SKY:
        raise AssertionError("source ray identity mismatch")
    generated=OUT/"R50_ORIGINAL_F08_S0_D_ELECTRON_THOMSON_CAP_10752.csv.gz"
    checked=0;absolute=0.0;max_ratio=0.;sample=[]
    with gzip.open(original,"rt",newline="") as fo,gzip.open(generated,"rt",newline="") as fg:
        for a,b in zip(csv.DictReader(fo),csv.DictReader(fg)):
            checked+=1
            for key in ("window_fraction","angular_nmu","angular_nphi","mu_bin","phi_bin"):
                original_value=a[key]
                new_value=b[key]
                if key=="window_fraction":
                    if float(original_value)!=float(new_value):raise AssertionError("original window mismatch")
                elif original_value!=new_value:raise AssertionError("original source ray key mismatch")
            te=float(a["emission_time_s"])
            cap=float(b["D_fullion_tau_cap"])
            delt=TO-te
            upper=F_D*C_SIGMA*NH0*math.exp(-3*H*te)*delt
            lower=F_D*C_SIGMA*NH0*math.exp(-3*H*TO)*delt
            if not lower*(1-3e-15)<=cap<=upper*(1+3e-15):
                raise AssertionError("passive D upper or lower integral bound violated")
            if abs(float(a["tau_BI"])-float(b["original_tau_BI"]))>1e-30:
                raise AssertionError("changed input source tau")
            if not 0<=cap/float(a["tau_BI"])<.000025:
                raise AssertionError("unexpected deuterium-to-electron opacity ratio")
            if abs((float(b["tau_BI_with_fullion_D"])-float(a["tau_BI"]))-cap)>3e-21:
                raise AssertionError("non-additive passive opacity")
            max_ratio=max(max_ratio,cap/float(a["tau_BI"]))
            if checked%420==1:sample.append((a,b))
    if checked!=10752:raise AssertionError("not full physical-source ray data")
    max_decimal_relative=0.0
    with localcontext() as ctx:
        ctx.prec=60
        op=Decimal("29979245800")*Decimal("6.6524587051e-25")
        eta=Decimal("2.5e-5");n0=Decimal("0.0001");h=Decimal("1e-14")
        for a,b in sample:
            t=Decimal(a["emission_time_s"])
            to=Decimal("10000000000000")
            cap_decimal=op*eta*n0*((-Decimal(3)*h*t).exp()-(-Decimal(3)*h*to).exp())/(Decimal(3)*h)
            rel=abs(float(cap_decimal)-float(b["D_fullion_tau_cap"]))/float(cap_decimal)
            max_decimal_relative=max(max_decimal_relative,rel)
            if rel>2e-14:
                raise AssertionError("independent Decimal isotope electron optical-depth mismatch")
    r=json.loads((OUT/"R50_RESULTS.json").read_text())
    if r["source_pair_id"]!="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8":
        raise AssertionError("source pair swap")
    if r["DAG"]["new_canonical_nodes"]!=0 or not r["assumptions"]["passive_deuterium"]:
        raise AssertionError("false canonical-source admission")
    report=dict(schema="WU_R50_SECOND_PASS_SAME_AUTHOR_DECIMAL_AND_SOURCE_IDENTITY_V1",
       source_rows_checked=checked,decimal_witnesses=len(sample),
       max_decimal_relative_error=max_decimal_relative,
       max_fraction_over_original_tau=max_ratio,
       original_rei_source_sha256=SHA_SKY,
       independent_author=False,second_model=False,
       science_scope="PASSIVE_D_MAX_ELECTRON_ONLY_IN_ORIGINAL_S0_F08",
       evidence="ALL_10752_RELATION_AND_DECIMAL_WITNESSES_PASS",
       limit="NO_H_D_CHEMISTRY_NO_REI_EOR_OBSERVATIONAL_ADMISSION")
    (OUT/"R50_SELF_ADVERSARIAL_AUDIT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
