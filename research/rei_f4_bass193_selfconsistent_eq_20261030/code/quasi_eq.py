"""Algebraic self-consistent instantaneous charge equilibrium of ORIGINAL BASS21.

Not an ODE, not a REI17 reconstruction, not a Thomson tau calculation.
Original 193 saved trajectory is immutable.  Prescribed BASS (T, UV, nb)
are taken at the stored points. Normal electron feedback is solved via one scalar.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.special import logsumexp
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'code'))
import native_full_rate as src
GROUPS=('H1','D','He3','He4','Li6','Li7')
EXPECTED_TRAJECTORY='37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
EXPECTED_PARENT_ZIP='de81a869f19f8ffd0db6b12f5bac5c93109f5804b691954c7ac0eae4f22df24b'

def source():
    if hashlib.sha256((HERE/'trajectory.npz').read_bytes()).hexdigest()!=EXPECTED_TRAJECTORY: raise ValueError('TRAJECTORY_SHA_MISMATCH')
    src.source_manifest_check()
    with np.load(HERE/'trajectory.npz',allow_pickle=False) as z:
        a={k:z[k].copy() for k in z.files}
    if a['Y'].shape!=(193,21) or a['diagnostics'].shape!=(193,25):raise ValueError('WRONG_SAVED_GRAIN')
    if not np.all(np.diff(a['x'])>0) or not np.all(np.diff(a['z'])<0):raise ValueError('WRONG_SAVED_CLOCK')
    if not np.all(a['Y']>=0):raise ValueError('NEGATIVE_SAVED_Y')
    return a,src.new_native_network()

def group_rates(net,rates,group):
    indices=np.asarray(net.isotope_groups[group],int)
    q=np.asarray(net.q[indices],int)
    if not np.array_equal(q,np.arange(len(indices))):raise ValueError('WRONG_CHARGE_ORDER')
    up=np.asarray(rates['photo_s'][indices[:-1]],float)
    down=np.asarray((rates['rr_m3_s']+rates['dr_m3_s'])[indices[1:]],float)
    if np.any(up<=0) or np.any(down<=0) or not np.isfinite(up).all() or not np.isfinite(down).all():
        raise ValueError('SOURCE_RATE_NONPOSITIVE_OR_OUTSIDE_POSITIVE_DOMAIN')
    return indices,up,down

def stationary(up,down,ne):
    """Exact normalized stationary law for finite birth/death chain, numerically log-stable.
    For j>=1, pi_j proportional product up_0..up_(j-1) / [ne^j product down_1..down_j].
    """
    if not (np.isfinite(ne) and ne>0):raise ValueError('POSITIVE_NE_REQUIRED')
    logs=np.r_[0.,np.cumsum(np.log(up)-np.log(down)-math.log(ne))]
    weights=np.exp(logs-logsumexp(logs))
    charges=np.arange(len(weights),dtype=float)
    mean=float(charges@weights)
    variance=float(((charges-mean)**2)@weights)
    return weights,mean,variance

def local_generator(up,down,ne):
    n=len(up)+1
    M=np.zeros((n,n),dtype=float)
    for j,v in enumerate(up):M[j,j]-=v;M[j+1,j]+=v
    for j,v in enumerate(down,start=1):M[j,j]-=ne*v;M[j-1,j]+=ne*v
    return M

def local_gap(up,down,ne):
    # Similarity via detailed balance; symmetric representation avoids complex eig artifacts.
    diag=-np.r_[up,0.]-np.r_[0.,ne*down]
    side=np.sqrt(up*(ne*down))
    S=np.diag(diag)+np.diag(side,1)+np.diag(side,-1)
    vals=np.linalg.eigvalsh(S)
    return float(max(0.,-vals[-2])),float(abs(vals[-1]))

def root_for_rates(net,rates,nb,inventory):
    if not(np.isfinite(nb) and nb>0):raise ValueError('INVALID_NB')
    params={g:group_rates(net,rates,g) for g in GROUPS}
    high=sum(float(inventory[g])*(len(v[0])-1) for g,v in params.items())
    def f(x):
        return sum(float(inventory[g])*stationary(v[1],v[2],nb*x)[1] for g,v in params.items())-x
    lo=1e-30
    if not (f(lo)>0 and f(high)<0):raise ValueError('NO_POSITIVE_BRACKET')
    x=float(brentq(f,lo,high,xtol=1e-22,rtol=4e-15,maxiter=200))
    return x,params,abs(f(x)),high

def analyze():
    a,net=source();y=a['Y'];diag={str(k):a['diagnostics'][:,i] for i,k in enumerate(a['diagnostic_names'])}
    N={g:float(np.sum(net.initial_Y[list(net.isotope_groups[g])])) for g in GROUPS}
    if not all(v>0 for v in N.values()):raise ValueError('UNEXPECTED_ZERO_ISOTOPE')
    rows=[];epochs=[]
    max_equilibrium_full_F=0.;max_jac_eq_abs=0.;max_exact_pi_resid=0.;max_source_native_resid=0.
    for i in range(len(y)):
        T=float(diag['T_K'][i]); uv=float(diag['uv_scale'][i]); nb=float(diag['nb_m3'][i]); H=float(diag['H'][i]); zz=float(a['z'][i])
        rates=net.rates(T,uv)
        xe,params,rooterr,ceiling=root_for_rates(net,rates,nb,N)
        ystar=np.zeros(21,dtype=float)
        xe_actual=float(net.q@y[i]);
        for g,(idx,up,down) in params.items():
            pi,mean,var=stationary(up,down,nb*xe)
            actual=y[i,idx];total=float(np.sum(actual))
            # Compare unit-sum normalized distributions, separate conservation errors.
            pop=actual/total
            TV=0.5*float(np.sum(np.abs(pop-pi)))
            M_eq=local_generator(up,down,nb*xe)
            gap,zeroe=local_gap(up,down,nb*xe)
            ystar[idx]=N[g]*pi
            this_res=float(np.max(np.abs(M_eq@pi)))
            max_exact_pi_resid=max(max_exact_pi_resid,this_res)
            rows.append(dict(epoch=i,z=zz,x=float(a['x'][i]),group=g,states=len(idx),N_isotope=N[g],
                xe_actual=xe_actual,xe_self_consistent=xe,charge_actual=float(net.q[idx]@actual),
                charge_eq=float(net.q[idx]@ystar[idx]),TV_distance=TV,
                L1_fraction_difference=2*TV,nonzero_local_gap_s=gap,gap_over_H=gap/H,
                local_gap_time_Myr=(1/gap)/(31557600*1e6) if gap>0 else float('inf'),
                mean_charge_eq=mean,charge_variance_eq=var,
                source_F_group_L1_per_baryon_s=float(np.sum(np.abs(local_generator(up,down,nb*xe_actual)@actual))),
                saved_isotope_total_rel_error=abs(total/N[g]-1.),
                stationary_M_pi_max_abs_s=this_res))
        full=net.evaluate(ystar,T,uv,nb)
        fullF=float(np.max(np.abs(full['dY_dt'])))
        max_equilibrium_full_F=max(max_equilibrium_full_F,fullF)
        if not np.isfinite(rooterr):raise ValueError('BAD_ROOT')
        # Analytical self-consistency derivative from conditional logistic family.
        chi=sum(N[g]*stationary(*params[g][1:],nb*xe)[2] for g in GROUPS)
        Gprime=-1.-chi/xe
        epochs.append(dict(epoch=i,x=float(a['x'][i]),z=zz,H_s=H,nb_m3=nb,T_K=T,UV=uv,
             xe_saved=xe_actual,xe_star=xe,xe_star_minus_saved=xe-xe_actual,
             relative_instantaneous_opacity_source_gap=(xe-xe_actual)/xe_actual,
             fixedpoint_residual=rooterr,charge_upper_bound=ceiling,
             Gprime=Gprime,full21_static_eq_F_max_abs_per_s=fullF))
    return rows,epochs,dict(schema='REI_F4_BASS193_SELFCONSISTENT_EQ_V1',source='original BASS21 saved193, prescribed photon T UV and native rates',
      data_kind='conditional instantaneous nonlinear chemical equilibrium, no new IVP',
      epochs=len(epochs),isotopes=GROUPS,rows=len(rows),saved_trajectory_sha256=EXPECTED_TRAJECTORY,
      maximum_native_eq_F_abs_s=max_equilibrium_full_F,maximum_pi_eigen_residual_s=max_exact_pi_resid,
      max_fixedpoint_residual=max(e['fixedpoint_residual'] for e in epochs),
      original_DAG=dict(working='33/88',central='28/88',physical_fast='4/7',delta=0),
      original_300K_ON_refined='unchanged',no_more_IVPs=True,
      first_epoch=epochs[0],last_epoch=epochs[-1])

def write():
    rows,epochs,summary=analyze()
    out=HERE/'results'
    for name,data in [('EQUILIBRIUM_193x6.csv',rows),('ELECTRON_FEEDBACK_193.csv',epochs)]:
        with (out/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary['equilibrium_mismatch_by_group']={g:dict(first=next(r['TV_distance'] for r in rows if r['group']==g),last=next(r['TV_distance'] for r in reversed(rows) if r['group']==g),max=max(r['TV_distance'] for r in rows if r['group']==g),
                 gap_over_H_first=next(r['gap_over_H'] for r in rows if r['group']==g),gap_over_H_last=next(r['gap_over_H'] for r in reversed(rows) if r['group']==g)) for g in GROUPS}
    (out/'RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return summary
if __name__=='__main__':
    print(json.dumps(write(),ensure_ascii=False,indent=2))
