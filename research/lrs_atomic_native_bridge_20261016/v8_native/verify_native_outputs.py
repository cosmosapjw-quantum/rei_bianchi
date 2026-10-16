#!/usr/bin/env python3
"""Numerical sanity checks on raw NCP CSV and the independent Radau comparison."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

CASES={
 "D1_X1e-5_T15000":1.,"D100_X002_T15000":100.,
 "D1000_X002_T15000":1000.,"D10000_X0003_T15000":10000.,
 "D1000_X002_T22000":1000.,"D1e6_X0001_T15000":1e6,
}
CHANNELS=("RR_HII","RR_HeII","RR_HeIII","DR_HeII")
Y=.2454/(4*(1-.2454))
E0=.075+Y*(.12+2*.03)

def verify(raw:Path, report:Path)->dict:
    result=json.loads(report.read_text())
    assert result["native_runs"]==30
    assert result["geometry_max_relative_error"]<=2e-13
    assert result["electron_ledger_max_abs_per_H"]<=5e-12
    assert result["nuclear_ledger_max_abs_per_H"]<=5e-12
    assert result["energy_ledger_max_relative"]<=5e-12
    checks=0;max_res=0.;max_ex=0.;max_ledger=0.
    for name in CASES:
        for n in (8,16,32,64,128):
            time_text=(raw/f"{name}_N{n}.time").read_text()
            stderr_text=(raw/f"{name}_N{n}.stderr").read_text()
            assert "exit=0 " in time_text and stderr_text.startswith("OK steps=")
            with (raw/f"{name}_N{n}.csv").open(newline="") as f:
                rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
            assert len(rows)==n
            for r in rows:
                assert all(math.isfinite(v) for v in r.values())
                assert 10000<=r["Tbegin_K"]<=24000 and 10000<=r["Tmid_K"]<=24000 and 10000<=r["Tend_K"]<=24000
                assert all(r[s]>=-1e-12 for s in ("HI","HII","HeI","HeII","HeIII"))
                assert abs(r["HI"]+r["HII"]-1)<=5e-12
                assert abs(r["HeI"]+r["HeII"]+r["HeIII"]-Y)<=5e-12
                assert abs(E0-r["e_per_H"]-sum(r[f"cum_events_{ch}"] for ch in CHANNELS))<=5e-12
                assert r["root_residual_K"]<=3e-7
                assert all(r[f"cum_events_{ch}"]>=0 and r[f"cum_cooling_{ch}"]>=0 and r[f"cum_binding_{ch}"]>=0 for ch in CHANNELS)
                assert all(r[f"exposure_{phase}_HeII_sum"]>=0 for phase in ("begin","mid","end"))
                assert all(abs(r[f"exposure_{phase}_HeII_sum"]-(r[f"exposure_{phase}_RR_HeII"]+r[f"exposure_{phase}_DR_HeII"]))<=1e-12*max(1,r[f"exposure_{phase}_HeII_sum"]) for phase in ("begin","mid","end"))
                max_res=max(max_res,r["root_residual_K"])
                max_ex=max(max_ex,max(r[f"exposure_{phase}_{ch}"] for phase in ("begin","mid","end") for ch in CHANNELS))
                max_ledger=max(max_ledger,abs(r["energy_residual_erg_per_H"]))
                checks+=1
    return {"native_runs_checked":30,"native_steps_checked":checks,"max_root_residual_K":max_res,"max_channel_exposure":max_ex,"max_energy_residual_erg_per_H":max_ledger,"checks":"all assertions passed"}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("raw",type=Path);ap.add_argument("comparison",type=Path);ap.add_argument("output",type=Path);a=ap.parse_args()
    out=verify(a.raw,a.comparison);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(out)
