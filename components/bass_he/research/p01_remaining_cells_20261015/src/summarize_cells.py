#!/usr/bin/env python3
"""Reconstruct first-to-last source-scoped optical-depth summary and plot.

Only admitted original saved cells are included. No new photon or chemistry
source solver is executed. Diagnostic plot is not a physical EoR ionic history.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
from fractions import Fraction as Q
from pathlib import Path
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(250000)
STEP=6250000000
BASE={
    2:Path("/tmp/HE18_C3_RUN_20261015/results/TWO_CELL_VALIDATION.json"),
    3:Path("/tmp/HE18_C5_THIRD_REAL_20261015/results/THREE_CELL_VALIDATION.json"),
    4:Path("/tmp/HE18_C6_FOURTH_OPT_20261015/results/FOUR_CELL_VALIDATION.json"),
    5:Path("/tmp/HE18_C7_FIFTH_BERNSTEIN_20261015/results/FIVE_CELL_VALIDATION.json"),
    6:Path("/tmp/HE18_C8_SIXTH_CACHED_20261015/results/SIX_CELL_VALIDATION.json"),
    7:Path("/tmp/HE18_C9_SEVENTH_MEMOIZED_20261015/results/SEVEN_CELL_VALIDATION.json"),
}
WORDS={1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",
       8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",
       13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen"}
NAMES={8:"EIGHT",9:"NINE",10:"TEN",11:"ELEVEN",12:"TWELVE",
       13:"THIRTEEN",14:"FOURTEEN",15:"FIFTEEN",16:"SIXTEEN"}
def decimal(q):
    q=Q(q)
    with localcontext() as c:
        c.prec=37
        return str(Decimal(q.numerator)/Decimal(q.denominator))
def row(i, lo,hi, status):
    lo=Q(lo);hi=Q(hi)
    if not Q(0)<=lo<=hi<Q(1):raise ValueError("INVALID_CUMULATIVE_TAU")
    midpoint=float((lo+hi)/2)
    return dict(cell=i,source_end_proper_s=i*STEP,source_end_years=(i*STEP)/31557600,
                cumulative_tau_lower=decimal(lo),
                cumulative_tau_upper=decimal(hi),
                cumulative_tau_mid_display=f"{midpoint:.17e}",
                collision_probability_mid_display=f"{-math.expm1(-midpoint):.17e}",
                admitted=status)

def collect(root,maxcell):
    first=json.loads(BASE[2].read_text())
    if first["schema"]!="he18.c3.exact_rational_two_cell_review.v1":
        raise ValueError("CHANGED_ORIGINAL_TWO_CELL_SCHEMA")
    rows=[row(1,*first["first_cell_tau"],True)]
    rows.append(row(2,*first["two_cell_tau_interval_exact"],True))
    for n in range(3,min(7,maxcell)+1):
        a=json.loads(BASE[n].read_text())
        arr=a.get(f"{WORDS[n]}_cell_tau_exact")
        if arr is None and n==3:arr=a["three_cell_tau_exact"]
        if len(arr)!=2:raise ValueError("OLD_CUMULATIVE_TAU_MISSING")
        rows.append(row(n,*arr,True))
    for n in range(8,maxcell+1):
        if n==8:
            p=root/"HE18_MULTICELL_08_20261015"
            if not p.exists():p=Path("/tmp/HE18_MULTICELL_08_20261015")
        else:
            p=root/f"HE18_MULTICELL_{n:02d}_20261015"
        vr=p/"results"/f"{NAMES[n]}_CELL_VALIDATION.json"
        error=p/"results"/f"{NAMES[n]}H_ENDPOINT_MEMORY.json"  # eighth, ninth, ...
        if not vr.is_file():
            # no fabricated gaps: write an explicitly partial source-scoped chart.
            break
        a=json.loads(vr.read_text())
        if a["status"]!="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES":
            raise ValueError("CHANGED_ADMISSION_STATUS")
        arr=a[f"{WORDS[n]}_cell_tau_exact"]
        if len(arr)!=2:raise ValueError("NO_EXACT_CURRENT_TAU")
        rows.append(row(n,*arr,True))
    for i in range(1,len(rows)):
        if Q(rows[i]["cumulative_tau_lower"])<Q(rows[i-1]["cumulative_tau_lower"]):
            raise ValueError("NONMONOTONIC_PHYSICAL_DEPTH")
    return rows

def write(root,dest,maxcell):
    dest.mkdir(parents=True,exist_ok=True)
    rows=collect(root,maxcell)
    csvp=dest/"warm_P01_cumulative_tau.csv"
    if csvp.exists():raise ValueError("REFUSE_OVERWRITE_EXISTING_SUMMARY")
    with csvp.open("x",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    years=[z["source_end_years"] for z in rows]
    taus=[float(z["cumulative_tau_mid_display"]) for z in rows]
    fig,ax=plt.subplots(figsize=(8.8,5))
    ax.plot(years,taus,".-",lw=1.9,markersize=6)
    ax.set(xlabel="Proper time since frozen initial epoch [Julian yr]",
           ylabel="Cumulative passive Thomson optical depth",
           title=f"Warm P01 source-scoped history: {len(rows)}/16 saved cells")
    ax.grid(alpha=0.35)
    fig.tight_layout()
    fig.savefig(dest/"warm_P01_cumulative_tau.png",dpi=180)
    plt.close(fig)
    widths=[taus[0]]+[taus[i]-taus[i-1] for i in range(1,len(taus))]
    fig,ax=plt.subplots(figsize=(8.8,5))
    ax.plot(range(1,len(rows)+1),widths,"o-",lw=1.8,markersize=5)
    ax.set(xlabel="Saved source cell",ylabel="Cell Thomson optical depth",
           title="Per-cell opacity, frozen warm P01 finite-source model")
    ax.grid(alpha=0.35)
    fig.tight_layout();fig.savefig(dest/"warm_P01_cell_tau.png",dpi=180);plt.close(fig)
    report=dict(schema="he18.p01.source_scoped_history.v1",
       generated_from_original_saved_source=True,
       total_source_saved_cells=16,completed_saved_cells=len(rows),
       final_tau_mid_display=rows[-1]["cumulative_tau_mid_display"],
       final_tau_outward=[rows[-1]["cumulative_tau_lower"],rows[-1]["cumulative_tau_upper"]],
       first_collision_mid_display=rows[-1]["collision_probability_mid_display"],
       original_source_commit="a5c958c414dea41216b445c05f58df837f05cacb",
       original_HM12_FT03_warm_source=True,
       scientific_status="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
       not_physical_EoR_ion_abundance_history=True,
       native_binary64_rounding_or_formal_backend_proof=False,
       public_csv_sha256=hashlib.sha256(csvp.read_bytes()).hexdigest())
    (dest/"RESULT_STATUS.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--campaign",type=Path,required=True)
    pa.add_argument("--output",type=Path,required=True)
    pa.add_argument("--through",type=int,default=16)
    a=pa.parse_args()
    write(a.campaign,a.output,a.through)
