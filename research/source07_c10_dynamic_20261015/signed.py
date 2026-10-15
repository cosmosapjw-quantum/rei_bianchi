#!/usr/bin/env python3
"""Scalar shear-parity check with a dynamically depleting H/He photon inventory.

This is a separate C10 synthetic receiver, not a substitute for AX08 full-history
signed parity or an estimate of observational anisotropy.
"""
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic as d

METRICS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_per_H","photon_U_eV_per_H")
QS=(-.01,-.005,0.,.005,.01)


def sweep(spectrum):
    cases={q:d.one_run(q,spectrum,nsteps=64,photons_per_H=1.,interval_s=1e12)
           for q in QS}
    values={str(q):{k:cases[q]["dense"]["final"][k] for k in METRICS} for q in QS}
    parity={}
    for field in METRICS:
        parity[field]={}
        for a in (.005,.01):
            plus=cases[a]["dense"]["final"][field]
            minus=cases[-a]["dense"]["final"][field]
            zero=cases[0.]["dense"]["final"][field]
            parity[field][str(a)]={"even":(plus+minus)*.5-zero,
                                   "odd":(plus-minus)*.5}
        d1=parity[field][str(.005)]
        d2=parity[field][str(.01)]
        parity[field]["ratio_even"]=d2["even"]/d1["even"] if d1["even"] else None
        parity[field]["ratio_odd"]=d2["odd"]/d1["odd"] if d1["odd"] else None
    return {"source":spectrum,"five_q_endpoints":values,
            "signed_parity":parity,
            "conditional_scope":"fixed zbar4 source packet; fully evolving photo-only material; neglect expansion, recomb, cooling"}


def main():
    rows=[sweep(source) for source in ("bb50k","hard")]
    (HERE/"SIGNED_DYNAMIC_PARITY.json").write_text(json.dumps(rows,indent=2)+"\n")
    for row in rows:
        print(row["source"])
        for name in ("x_HII","x_HeII","x_HeIII","Tgas_K"):
            item=row["signed_parity"][name]
            print(name,"q=0.01 even",item[str(.01)]["even"],
                  "odd",item[str(.01)]["odd"],
                  "even ratio",item["ratio_even"],"odd ratio",item["ratio_odd"])


if __name__=="__main__":
    main()
