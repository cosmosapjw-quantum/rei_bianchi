#!/usr/bin/env python3
"""Independently isolate angular quadrature sensitivity of *signed* Bianchi parity."""
import json
import math
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic as d

FIELDS=("x_HII","x_HeII","x_HeIII","Tgas_K")
QS=(-.01,-.005,0.,.005,.01)
MUS=(12,24,48,96)
SOURCE=("bb50k","hard")

def direct(q,source,nmu):
    model=d.c9.Scenario(d.ROOT)
    from benchmark import HardSource
    spect=d.c9.Spectrum() if source=="bb50k" else HardSource()
    ages=np.geomspace(model.ar,.2,d.c9.AGE_COUNT)
    packets=d.c9.build_packets(model,spect,ages,q,n_mu=nmu,n_energy=16)
    wg=d.c9.source_age_weights(model,ages,q)
    gas=d.Gas.initial(model)
    r=d.propagate(d.to_packets(packets,wg,gas,1.),gas,nsteps=64,interval=1e12)
    return {k:r["final"][k] for k in FIELDS}

def main():
    cases=[]
    for source in SOURCE:
        values={}
        for mu in MUS:
            field={q:direct(q,source,mu) for q in QS}
            parity={}
            for k in FIELDS:
                parity[k]={}
                for a in (.005,.01):
                    p,m,z=field[a][k],field[-a][k],field[0.][k]
                    parity[k][str(a)]={"even":(p+m)/2-z,"odd":(p-m)/2}
                small,big=parity[k][str(.005)],parity[k][str(.01)]
                parity[k]["ratio_even"]=big["even"]/small["even"] if small["even"] else None
                parity[k]["ratio_odd"]=big["odd"]/small["odd"] if small["odd"] else None
            values[mu]={"parity":parity,"endpoints":{str(q):v for q,v in field.items()}}
            print(source,mu,"HeII-even-ratio",parity["x_HeII"]["ratio_even"],
                  "odd ratio",parity["x_HeII"]["ratio_odd"],flush=True)
        reference=values[MUS[-1]]["parity"]
        sensitivity={}
        for mu in MUS[:-1]:
            sensitivity[str(mu)]={field:{
                key:{z:abs(values[mu]["parity"][field][key][z] -
                          reference[field][key][z]) for z in ("even","odd")}
                for key in ("0.005","0.01")} for field in FIELDS}
        cases.append({"source":source,"mu_quadratures":values,
                      "absolute_signed_discrepancy_to_mu96":sensitivity})
    (HERE/"ANGULAR_SIGNED_CONVERGENCE.json").write_text(json.dumps(cases,indent=2)+"\n")
    for case in cases:
        print("CASE",case["source"])
        for mu in MUS:
            obj=case["mu_quadratures"][mu]["parity"]
            print(mu,"HII q.01 even",obj["x_HII"]["0.01"]["even"],
                  "HeII q.01 odd",obj["x_HeII"]["0.01"]["odd"],
                  "HeII ratio",obj["x_HeII"]["ratio_odd"])


if __name__=="__main__":
    main()
