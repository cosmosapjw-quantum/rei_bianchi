#!/usr/bin/env python3
"""Independent high-precision Coulomb forbidden-action/CoulombH diagnostics.

DO NOT infer a physical tunneling probability from WKB action alone.
Coulomb H+ is the exact original CENTRAL reference and numerical only.
"""
from __future__ import annotations
import argparse,json,sys,time
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys48_barrier import source_barrier_actions


def evaluate_one(ell:int,dps:int=55)->dict:
    with mp.workdps(dps):
        k=mp.mpf(7)/10
        B=mp.mpf(20)
        L=ell*(ell+1)
        turn=(mp.sqrt(1+k*k*L)-1)/(k*k)
        if turn<=B:
            action=mp.mpf(0)
        else:
            width=turn-B
            def f(t):
                rr=B+width*(2*t-t*t)
                barrier=L/rr**2-2/rr-k*k
                # End-point cancellation can produce a sub-precision negative.
                if barrier<0 and abs(barrier)<mp.mpf(10)**(-dps+10):
                    barrier=mp.mpf(0)
                return 2*width*(1-t)*mp.sqrt(barrier)
            action=mp.re(mp.quad(f,[0,mp.mpf('0.5'),mp.mpf('0.9'),1]))
        eta=-1/k
        H=mp.coulombg(ell,eta,k*B)+1j*mp.coulombf(ell,eta,k*B)
        logamplitude=mp.log(abs(H))
        return {
            "ell":ell,
            "turn_float":mp.nstr(turn,36),
            "forbidden_action_numeric":mp.nstr(action,36),
            "log_outgoing_Hplus_B_numeric":mp.nstr(logamplitude,36),
            "ratio_logamplitude_to_action":mp.nstr(logamplitude/action,30) if action>0 else None,
            "classification":"NONCERTIFYING_REFERENCE_SAMPLES; ACTION rigorous only via separate rational mesh",
        }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--cert",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--dps",type=int,default=55)
    a=p.parse_args()
    if not 35<=a.dps<=100:raise ValueError("bounded independent precision")
    cert=json.loads(a.cert.read_text())
    model=source_barrier_actions(a.source,tuple(v["ell"] for v in cert["action_enclosures"]),
                                 n=4,grading="uniform",workers=1)
    if model["original_source_sha256"]!=cert["original_source_sha256"]:
        raise ArithmeticError("immutable frozen source mismatch")
    t=time.perf_counter()
    rows=[]
    for c in cert["action_enclosures"]:
        d=evaluate_one(c["ell"],a.dps)
        with mp.workdps(a.dps):
            atrue=mp.mpf(d["forbidden_action_numeric"])
            lo=mp.mpf(c["action_lower"]);hi=mp.mpf(c["action_upper"])
            if not lo-mp.mpf("1e-30")<=atrue<=hi+mp.mpf("1e-30"):
                raise ArithmeticError("independent numerical Coulomb action outside strict interval")
        d["action_inside_certified_rational_bracket"]=True
        d["rigorous_lower"]=c["action_lower"]
        d["rigorous_upper"]=c["action_upper"]
        rows.append(d)
    result={
      "schema":"WU088_HH_PHYS48_INDEPENDENT_COULOMB_ACTION_AND_HPLUS_NUMERIC_V1",
      "source_SHA256":cert["original_source_sha256"],
      "certificate":str(a.cert),
      "dps":a.dps,"rows":rows,
      "elapsed_s":time.perf_counter()-t,
      "all_independent_actions_inside_rational_brackets":True,
      "scope":"barrier action integral numerical parity; H+(20) values not certified, no barrier-wave amplitude inequality or physical HH rate"
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"n":len(rows),"wall_s":result["elapsed_s"],
                      "ell_log_H":[[r["ell"],r["log_outgoing_Hplus_B_numeric"]] for r in rows]}))
if __name__=="__main__":main()
