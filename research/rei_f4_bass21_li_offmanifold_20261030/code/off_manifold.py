"""Exact source-scoped off-manifold BASS21 Li6/Li7 reduction at saved states.

NO IVP. The 17-dimensional retained state is BASS-internal, NOT the
unrelated REI saved17 state or the compact30 solver.
"""
from __future__ import annotations
import sys, json, hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source'
sys.path.insert(0,str(SRC/'rei_pr269'/'code'))
import native_full_rate as donor

RETAIN=np.array(list(range(13))+list(range(17,21)),dtype=int)
LI6=np.array([13,14,15,16],dtype=int)
LI7=np.array([17,18,19,20],dtype=int)
CHARGES=np.arange(4,dtype=float)
ORIGINAL_SHA='ba3f07a4f881ae8b02fd7b9690242ee29cfd1ae9f2b885b2601487010408508b'

def load():
    assert hashlib.sha256((SRC/'VIGILODE_PR118_SOURCE_IMMUTABLE.zip').read_bytes()).hexdigest()==ORIGINAL_SHA
    donor.source_manifest_check()
    expected=json.loads((SRC/'SOURCE_LOCK.json').read_text())
    for item in expected['selected_members']:
        path=SRC/item['path']
        if path.stat().st_size!=item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('SOURCE_MEMBER_CHANGED: '+item['path'])
    net=donor.new_native_network()
    obj=json.loads((SRC/'new_physics'/'source'/'SELECTED_BASS_ENDPOINTS.json').read_text())
    if obj['source_git_blob']!='a49aa5276b4256d6bf0ad443b6b830effe2ab738' or len(obj['cases'])!=5:
        raise ValueError('ORIGINAL_BASS_ENDPOINT_IDENTITY_LOST')
    return net,obj['cases']

def maps(gamma):
    P=np.eye(21,dtype=float)[RETAIN]
    E=P.T.copy()
    for i,j in zip(LI6,range(13,17)):
        E[i,j]=gamma
    D=np.eye(21,dtype=float)[LI6]-gamma*np.eye(21,dtype=float)[LI7]
    T=np.vstack([P,D])
    Tinv=np.column_stack([E,np.eye(21,dtype=float)[:,LI6]])
    if not np.allclose(T@Tinv,np.eye(21),atol=1e-16,rtol=0):
        raise ArithmeticError('TRANSFORM_INVALID')
    return P,E,D,T,Tinv

def evaluate_case(net,case):
    Y=np.asarray(case['Y'],dtype=float); nb=float(case['nb_m3']);t=float(case['T_K']);uv=float(case['uv']);
    if Y.shape!=(21,) or np.any(Y<0) or nb<=0:raise ValueError('BAD_SAVED_ENDPOINT')
    gamma=net.isotope_inventory['Li6']/net.isotope_inventory['Li7']
    P,E,D,T,Tinv=maps(gamma)
    y=P@Y;delta=D@Y; lifted=E@y
    native=net.evaluate(Y,t,uv,nb); projected=net.evaluate(lifted,t,uv,nb)
    rates=net.rates(t,uv)
    n_e=native['ne'];ne_eff=projected['ne']
    M=rates['G0'][np.ix_(LI6,LI6)]+n_e*rates['Gne'][np.ix_(LI6,LI6)]
    R=P@rates['Gne']@E
    g=nb*float(CHARGES@delta)*(R@y)
    # The exact nonlinear source decomposition holds even when Y is off E's image.
    observed_ret=P@native['dY_dt']-P@projected['dY_dt']
    observed_delta=D@native['dY_dt']
    # Exact local derivative around the invariant lift E y.
    Jlift=projected['jac'];Jred=P@Jlift@E
    upper=P@Jlift@Tinv[:,17:]
    bottom=D@Jlift@E
    lower=D@Jlift@Tinv[:,17:]
    upper_expected=nb*np.outer(R@y,CHARGES)
    M_lift=rates['G0'][np.ix_(LI6,LI6)]+ne_eff*rates['Gne'][np.ix_(LI6,LI6)]
    conv=np.diag(M)
    off=M.copy();np.fill_diagonal(off,0.0)
    lognorm_l1=np.max(np.diag(M)+np.sum(abs(off),axis=0))
    up=np.array([M[j+1,j] for j in range(3)])
    down=np.array([M[j,j+1] for j in range(3)])
    if np.any(up<=0) or np.any(down<=0):
        raise ValueError('POSITIVE_FROZEN_LI_RATE_PREMISE_NOT_MET')
    pi=np.r_[1.,np.cumprod(up/down)];pi/=pi.sum()
    sym=M*np.sqrt(pi[None,:]/pi[:,None])
    if not np.allclose(sym,sym.T,rtol=1e-12,atol=1e-29):
        raise ArithmeticError('LITHIUM_REVERSIBILITY_RESIDUAL')
    spectrum=np.linalg.eigvalsh((sym+sym.T)*0.5)
    if not (spectrum[-2]<0 and abs(spectrum[-1])<1e-26):
        raise ArithmeticError('LITHIUM_TRANSVERSE_GAP_NOT_CERTIFIED')
    gap=float(-spectrum[-2])
    # Pointwise tau_x reconstruction uses BASS original stored positive H, not a new history.
    K=(2.99792458e10*6.6524587051e-25)/1e6 # source-side prior convention as in PR118
    H=K*n_e/float(case['gamma_T_per_H'])
    tau_gap_naive=K*(n_e-ne_eff)/H  # may catastrophically cancel below float eps
    tau_gap_formula=K*nb*float(CHARGES@delta)/H
    return {'id':case['id'],'z':case['z'],'gamma_li6_li7':gamma,
        'nb_m3':nb,'H_per_s_from_stored_gamma':H,
        'Li6_scaled_defect_l1':float(np.linalg.norm(delta,1)/net.isotope_inventory['Li6']),
        'Li6_scaled_defect_linf':float(np.max(abs(delta))/net.isotope_inventory['Li6']),
        'delta_l1':float(np.linalg.norm(delta,1)),
        'delta_charge':float(CHARGES@delta),
        'retained_forcing_l1_per_s':float(np.linalg.norm(g,1)),
        'retained_forcing_l1_upper_per_s':float(3*nb*np.linalg.norm(delta,1)*np.linalg.norm(R@y,1)),
        'retained_source_defect_max_abs':float(np.max(abs(observed_ret-g))),
        'delta_source_defect_max_abs':float(np.max(abs(observed_delta-M@delta))),
        'Jred_source_shape':list(Jred.shape),
        'upper_block_diff_max_abs':float(np.max(abs(upper-upper_expected))),
        'lowerleft_block_max_abs':float(np.max(abs(bottom))),
        'lowerright_block_max_abs':float(np.max(abs(lower-M_lift))),
        'L_l1_log_norm_per_s':float(lognorm_l1),
        'L_static_eigenvalues_per_s':spectrum.tolist(),
        'L_static_gap_per_s':gap,
        'L_static_relaxation_years':float(1.0/gap/31557600.0),
        'L_detailed_balance_max_abs_per_s':float(np.max(abs(sym-sym.T))),
        'L_colsum_max_abs_per_s':float(np.max(abs(M.sum(axis=0)))),
        'L_min_offdiag_per_s':float(np.min(off)),
        'pointwise_tau_x_gap_stable':float(tau_gap_formula),
        'pointwise_tau_x_gap_naive_fp':float(tau_gap_naive),
        'pointwise_tau_x_fp_cancellation_abs':float(abs(tau_gap_naive-tau_gap_formula)),
        'pointwise_tau_x_gap_bound':float(3*K*nb*np.linalg.norm(delta,1)/H),
        'n_e_projected_m3':float(ne_eff),'n_e_saved_m3':float(n_e)}

def run():
    net,rows=load();out=[evaluate_case(net,r) for r in rows]
    return {'schema':'REI_F4_BASS21_OFF_MANIFOLD_EXACT_SOURCE_V1','donor_pr':118,
        'source':'five actual original BASS saved endpoints; native rates & proper H reconstructed from stored gamma_T_per_H',
        'claim':'BASS21 internal Li6/Li7 dynamic lift and off-manifold forcing, not REI17 equivalence',
        'new_ivps':0,'working':'33/88','central':'28/88','physical_fast':'4/7',
        'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','cases':out}

if __name__=='__main__':print(json.dumps(run(),indent=2))
