"""Bounded scientific producer; complete coefficient matrices remain in NPZ."""
from pathlib import Path
import argparse,json,time
import numpy as np
from wu088_hh.phys64_born_hierarchy import solve_orders,summary,coefficient_quadrature,series_delta
from wu088_hh.phys63_scaled_riccati import direct_fundamental_control


def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=root/'research/hh_phys64_20261018/c5c8/results')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    src=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
    cases=[(21,0,39,128,2e-11,.25),(28,0,39,128,2e-11,.25),(32,0,39,128,2e-11,.25),
           (28,0,35,128,2e-11,.25),(28,0,43,128,2e-11,.25),(28,0,39,192,2e-12,.125),
           (28,1,39,128,2e-11,.25),(28,2,39,128,2e-11,.25)]
    rows=[];arrays={}
    for i,(L,m,T,nodes,tol,step) in enumerate(cases):
        s=solve_orders(src,tuple(range(abs(m),L+1)),m,T,3,nodes,tol,step)
        row=summary(s)
        if i==1:
            row['quadrature_relative']={str(j):float(np.linalg.norm(coefficient_quadrature(s,j,80)-s['coefficients'][j-1])/np.linalg.norm(s['coefficients'][j-1])) for j in (1,2,3)}
        rows.append(row);arrays['Y_'+str(i)]=s['coefficients'];arrays['D_'+str(i)]=s['contributions']
        print('CASE',i,L,m,T,[(x['order'],x['physical_entry']) for x in row['terms']],flush=True)
    ctrl=solve_orders(src,(0,1),0,33,4,128,1e-12,.1)
    direct=direct_fundamental_control(src,ells=(0,1),outer=33,strength=1e20,rtol=1e-12)
    errors=[float(np.linalg.norm(np.diag(ctrl['central_z'])+series_delta(ctrl,1e20,j)-direct['Z'])) for j in (1,2,3,4)]
    out={'schema':'PHYS64_ORDER_RESOLVED_V1','cases':rows,
         'nonphysical_strength_1e20_control':{'partial_sum_errors':errors,'flux_error':direct['flux_error']},
         'all_angular_numeric_certificate':False,'HH_R10':'OFF','NCP':'NOT_RUN'}
    np.savez_compressed(a.out/'COEFFICIENTS.npz',**arrays)
    (a.out/'SCIENCE.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('CONTROL',errors,direct['flux_error'])

if __name__=='__main__':main()
