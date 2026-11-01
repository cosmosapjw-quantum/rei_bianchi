#!/usr/bin/env python3
"""Frozen physical H photoionization/recombination limit, correlated error exact."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Comparison:
    dt_s:float
    independent_box_gap:float
    common_parent_gap:float
    dimensionless_kh:float

def backward_euler(x,gamma,recomb,dt):
    assert 0<=x<=1 and gamma>=0 and recomb>=0 and dt>=0
    return (x+dt*gamma)/(1+dt*(gamma+recomb))

def same_parent_defect(x,gamma,recomb,dt):
    k=gamma+recomb
    if k==0 or dt==0:return 0.0
    q=k*dt
    return (x-gamma/k)*q*q/(4*(1+q)*(1+q/2)**2)

def compare_box(xlo,xhi,gamma,recomb,dt):
    assert 0<=xlo<=xhi<=1
    f0=backward_euler(xlo,gamma,recomb,dt)
    f1=backward_euler(xhi,gamma,recomb,dt)
    h0=backward_euler(backward_euler(xlo,gamma,recomb,dt/2),gamma,recomb,dt/2)
    h1=backward_euler(backward_euler(xhi,gamma,recomb,dt/2),gamma,recomb,dt/2)
    paired=max(abs(same_parent_defect(xlo,gamma,recomb,dt)),
               abs(same_parent_defect(xhi,gamma,recomb,dt)))
    direct=max(abs(f0-h0),abs(f1-h1))
    assert math.isclose(paired,direct,abs_tol=5e-16,rel_tol=4e-12)
    return Comparison(dt,max(abs(h0-f1),abs(h1-f0)),paired,(gamma+recomb)*dt)

ORIGINAL_OBSERVED={4:2.144803577710519e-4,2:2.131269352698695e-4,
                  1:2.1245050576368385e-4}
LIMIT=2e-4
ACCEPTED_TICK=160
TOTAL_TICKS=131072

if __name__=="__main__":
    import json
    rows=[compare_box(.2,.8,1e-12,2e-13,h).__dict__
          for h in (1e11,5e10,2.5e10,1.25e10,6.25e9)]
    print(json.dumps({"source":"original reviewed Aug29 frozen failed run",
      "actual_local_errors":ORIGINAL_OBSERVED,"gate":LIMIT,
      "accepted_fraction":ACCEPTED_TICK/TOTAL_TICKS,
      "analytic_H_photo_recomb_control_only":rows,
      "full_REI_interval_completed":False,"DAG_central":"28/88"},indent=2))
