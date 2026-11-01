#!/usr/bin/env python3
"""Independent F08 original-source 8x16 PSTF quadrupole audit, no new IVP."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ANGLE_SHA = "370abc5b57c25497d8adfb2931428d04fcc84ff29a8621a8348e01d90a9c6a54"
HISTORY_SHA = "df1acb1bf78f2fc0e6d3a852cdfacedf1bc44e0909b870bebbacf8ce1cb302c4"
CHANNELS = (
 ("HI_photoionization_rate", "characteristic_photo_rate_per_H_s", "HI_photo_rate_per_original_H_s"),
 ("HI_photoelectron_heat_rate", "characteristic_heat_rate_eV_per_H_s", "HI_photoheating_rate_eV_per_original_H_s"),
 ("HI_cumulative_absorption", "characteristic_cumulative_absorbed_per_H", "HI_cumulative_absorbed_photons_per_H"),
 ("HI_cumulative_photoelectron_heat", "characteristic_cumulative_photoheat_eV_per_H", "HI_cumulative_excess_photoheat_eV_per_H"),
)

def check_bytes(path, digest):
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if actual!=digest:
        raise RuntimeError(f"source-byte mismatch {path}: {actual} != {digest}")

def read_gz(path):
    with gzip.open(path,"rt",newline="") as file:
        return list(csv.DictReader(file))

def close(a,b,rtol=3e-12,atol=0.0):
    return abs(a-b)<=atol+rtol*max(abs(a),abs(b))

def q2(r):
    x,y,z=(float(r[c]) for c in ("q_x","q_y","q_z"))
    return (x*x,y*y,z*z,x*y,x*z,y*z)

def independent_tensor(group, column):
    n=len(group)
    if n!=128:raise RuntimeError("unexpected angular group size")
    matrices=[q2(r) for r in group]
    means=[math.fsum(v[i] for v in matrices)/n for i in range(6)]
    x=[float(r[column]) for r in group]
    total=math.fsum(x)
    if not (total>0):raise RuntimeError("nonpositive original source total")
    q=[math.fsum(x[j]*(matrices[j][i]-means[i]) for j in range(n))/total for i in range(6)]
    return total,q

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--angles",required=True)
    ap.add_argument("--history",required=True)
    ap.add_argument("--result",required=True)
    ap.add_argument("--json",required=True)
    args=ap.parse_args()
    check_bytes(args.angles,ANGLE_SHA)
    check_bytes(args.history,HISTORY_SHA)
    rows=read_gz(args.angles)
    history=read_gz(args.history)
    if len(rows)!=3840 or len(history)!=30:raise RuntimeError("original-source row count")
    groups=collections.defaultdict(list)
    for r in rows:
        key=(r["branch"],int(r["source_original_tick"]))
        groups[key].append(r)
    hist={(r["branch"],int(r["original_tick"])):r for r in history}
    if len(groups)!=30 or set(groups)!=set(hist):raise RuntimeError("source time keys")
    parsed=list(csv.DictReader(Path(args.result).open(newline="")))
    if len(parsed)!=120:raise RuntimeError(f"expected 120 Rust multipole rows; got {len(parsed)}")
    results={(r["branch"],int(r["original_tick"]),r["quantity"]):r for r in parsed}
    if len(results)!=120:raise RuntimeError("duplicate Rust output")
    max_rel_source=0.0
    max_abs_tensor=0.0
    max_flrw=0.0
    bi={}
    for (branch,tick),g in sorted(groups.items()):
        if len(g)!=128 or sorted(int(x["direction_id"]) for x in g)!=list(range(128)):
            raise RuntimeError("missing/duplicated qhat direction")
        t=float(g[0]["proper_time_s"])
        if abs(t-tick*625000000.0)>.01:raise RuntimeError("original clock mismatch")
        for quantity,src_col,hist_col in CHANNELS:
            total,q=independent_tensor(g,src_col)
            authoritative=float(hist[(branch,tick)][hist_col])
            if not close(total,authoritative):
                raise RuntimeError(f"source-history mismatch {branch} {tick} {quantity} {total} {authoritative}")
            relative=abs(total-authoritative)/max(abs(authoritative),1e-300)
            max_rel_source=max(max_rel_source,relative)
            out=results[(branch,tick,quantity)]
            got=[float(out[c]) for c in ("q_xx","q_yy","q_zz","q_xy","q_xz","q_yz")]
            if not close(float(out["source_total"]),total,rtol=3e-12):
                raise RuntimeError(f"Rust total mismatch {branch} {tick} {quantity}")
            delta=max(abs(a-b) for a,b in zip(q,got))
            max_abs_tensor=max(max_abs_tensor,delta)
            if delta>2e-12:raise RuntimeError(f"Rust/Python multipole mismatch {branch} {tick} {quantity} {delta}")
            if abs(sum(got[:3]))>2e-12:raise RuntimeError("nonzero PSTF trace")
            if not close(float(out["q_xx_minus_yy"]),got[0]-got[1],rtol=1e-11,atol=3e-15):
                raise RuntimeError("qdiff mismatch")
            if branch=="S0_FLRW":
                max_flrw=max(max_flrw,max(abs(v) for v in got))
            else:
                bi.setdefault(tick,{})[quantity]=got[0]-got[1]
    if max_flrw>2e-11:raise RuntimeError(f"FLRW nonzero quadrupole {max_flrw}")
    rate="HI_photoionization_rate"
    heat="HI_photoelectron_heat_rate"
    if not (bi[1][rate]>0 and bi[1][heat]<0 and bi[800][rate]>0
            and bi[1600][rate]<0 and bi[800][heat]<0 and bi[1600][heat]<0):
        raise RuntimeError("first-tick directional physics or sampled sign change failed")
    verdict={
      "original_angle_rows":len(rows),
      "original_history_rows":len(history),
      "derived_multipole_rows":len(parsed),
      "q_grid":"8x16_midpoint_finite_grid_centered_PSTF",
      "max_relative_history_sum_error":max_rel_source,
      "max_abs_Rust_Python_tensor_difference":max_abs_tensor,
      "max_abs_FLRW_quadrupole":max_flrw,
      "BI_selected_qxx_minus_qyy":{str(t):bi[t] for t in (1,800,1600,16000)},
      "claim":"PHYSICAL_SOURCE_CONDITIONAL_ORIGINAL_F08_FROZEN_HHE_NOT_NATIVE_FULL_IVP",
      "dag":{"central":"28/88","working":"33/88_nonadditive","physical_fast":"4/7","canonical_delta":0},
      "test":"PASS"
    }
    Path(args.json).write_text(json.dumps(verdict,indent=2)+"\n")
    print("REI_F08_SOURCE_ORIGINAL_QAUDIT_PASS")
    print(json.dumps(verdict,sort_keys=True))

if __name__=="__main__":
    main()
