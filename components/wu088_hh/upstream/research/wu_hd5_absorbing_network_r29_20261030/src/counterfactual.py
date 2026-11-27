"""R29 explicit *counterfactual* suppress-upward model for interpreting the source-derived result.

This is NOT a physical-source alternative: omitting upward collisions at fixed thermal
T violates complete detailed balance. It only isolates the added upward mechanism.
"""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
from .network import BASE, TEMPS, POLICIES,load_grid,reference_density,assemble,run_case

def downward_only(grid,T,policy,start=2):
    n=reference_density(grid,T,policy)
    _,_,_,chem=assemble(grid,T,policy,n)
    G=np.zeros((5,5));F=np.zeros((5,5))
    for j in range(5):
        G[j,j]-=chem[j];F[j,j]-=chem[j]
        if j>=1:
            G[j,j]-=grid.A[j];G[j-1,j]+=grid.A[j]
            F[j,j]-=grid.A[j]
            for i in range(j):
                d=n*grid.down[(T,j,i)]
                G[j,j]-=d;G[i,j]+=d
                F[j,j]-=d;F[i,j]+=d
    e=np.zeros(5);e[start]=1.
    m=np.linalg.solve(-G,e);mf=np.linalg.solve(-F,e)
    return float(sum(grid.A[j]*mf[j] for j in range(1,5))),float(sum(grid.A[j]*m[j] for j in range(1,5)))

def compare(out):
    grid=load_grid();rows=[]
    for T in TEMPS:
        for policy in POLICIES:
            full=run_case(grid,T,policy,1.,2)
            down_p,down_count=downward_only(grid,T,policy)
            rows.append(dict(T_K=T,policy=policy,J_initial=2,
                p_any_photon_detailed_balance=full['probability_one_or_more_photons_before_exchange'],
                p_any_photon_counterfactual_no_up=down_p,
                expected_photons_detailed_balance=full['expected_photons_before_exchange'],
                expected_photons_counterfactual_no_up=down_count,
                comparison='counterfactual physical interpretation ONLY; down-only is NOT a thermal detailed-balance network'))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'UPWARD_SENSITIVITY_14.json').write_text(json.dumps({'schema':'wu.r29.upward_collision_counterfactual.v1','rows':rows},indent=2)+'\n')
    with (out/'UPWARD_SENSITIVITY_14.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows
if __name__=='__main__':compare(BASE/'results')