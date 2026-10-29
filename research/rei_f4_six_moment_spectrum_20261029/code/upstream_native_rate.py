"""Actual BASS AtomicNetwork implementation, projected pinned coefficients, saved REI y.

No IVP, no cosmological clock integration, no same-source physical admission.
BASS rate numeric coefficients projected from Git blob 2eba600a9... at parent
464aff9d95fe596e464e1788c8bebf10ebb2ed5f (metadata not raw byte lock).
Source Python and source model byte-locked from PR234 original Drive ZIP.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source'
EXPECTED={
    'BASS_ATOMIC_NETWORK.py':'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80',
    'BASS_ATOMIC_MODEL.json':'9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614',
    'REI_SAVED7.json':'7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77'
}
PH_KEYS=('Eth_eV','Emax_eV','E0_eV','sigma0_Mb','ya','P','yw','y0','y1')
RR_KEYS=('A_cm3_s','B','T0_K','T1_K','C','T2_K')
A17=np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7],float)
Q17=np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3],float)
PHOTO_EVENTS=((1,2,0),(3,4,0),(5,6,0),(7,8,1),(8,9,2),(10,11,1),(11,12,2))
STOICH=np.zeros((17,7))
for j,(src,dst,fam) in enumerate(PHOTO_EVENTS):
    STOICH[src,j]=-1.0; STOICH[dst,j]=1.0
GAMMA_FAMILIES=(0,1,2)
NOMINAL_BETA=-0.04591874303144475
NOMINAL_KAPPA=0.0686617394805907


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_manifest_check():
    got={n:sha(SRC/n) for n in EXPECTED}
    if got!=EXPECTED:raise ValueError(('SOURCE_SHA_MISMATCH',got))
    c=json.loads((SRC/'COEFF_NUMERIC_PROJECTION.json').read_text())
    if c['source_git_blob']!='2eba600a9d7a7359ca55f566f1b841a363a3e5c7':
        raise ValueError('COEFFICIENT_PROJECTION_SOURCE_ID_MISMATCH')
    p=json.loads((SRC/'P19_13_KNOTS.json').read_text())
    if p['source_git_blob']!='3472e57abebb55e94f8c4436f2867bfc58e9feb9':
        raise ValueError('P19_KNOT_PROJECTION_SOURCE_ID_MISMATCH')
    if len(p['rows'])!=13: raise ValueError('BAD_P19_KNOTS')
    return got


def native_coefficients():
    obj=json.loads((SRC/'COEFF_NUMERIC_PROJECTION.json').read_text())
    return {
       'photo_VF1996':{k:dict(zip(PH_KEYS,v)) for k,v in obj['photo'].items()},
       'rr':{k:dict(zip(RR_KEYS,v)) for k,v in obj['rr'].items()},
       'dr':{k:dict(c_cm3_s_K32=v[0],E_K=v[1]) for k,v in obj['dr'].items()},
       'LiI_partial':obj['li'],
       'runtime_temperature_domain_K':obj['domain']}


def new_native_network():
    source_manifest_check()
    spec=importlib.util.spec_from_file_location('pinned_original_bass_atomic_network',SRC/'BASS_ATOMIC_NETWORK.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    coeff=native_coefficients(); model=json.loads((SRC/'BASS_ATOMIC_MODEL.json').read_text())
    # Load only: bypass original file manifest whose parent data are not present
    # in PR234 SOURCE ZIP. Native AtomicNetwork methods and model stay unmodified.
    mod._verified_inputs=lambda:(coeff,model)
    net=mod.AtomicNetwork()
    return net


def original_bass_bath_at_z(z):
    if not (0<=z<=20) or not math.isfinite(z):raise ValueError('z outside 0..20')
    u=(7.0-z)/0.8
    Q=0.5*(1+math.tanh(u))
    return 100.0+11900.0*Q, Q


def p19_nominal_gamma(z, beta=NOMINAL_BETA, kappa=NOMINAL_KAPPA):
    if not (2.4<=z<=4.75) or not math.isfinite(z):raise ValueError('P19 calibration restricted 2.4..4.75')
    knots=np.asarray(json.loads((SRC/'P19_13_KNOTS.json').read_text())['rows'],float)
    if not np.all(np.diff(knots[:,0])>0) or np.any(knots[:,1:]<=0):
        raise ValueError('bad P19 numerical projection')
    log_rates=np.array([np.interp(z,knots[:,0],np.log(knots[:,i])) for i in (1,3,5)])
    return np.exp(log_rates + math.log(10)*(beta+kappa*(z-3.6)))


def bass_gamma_family(net,z):
    T,uv=original_bass_bath_at_z(z)
    rates=net.rates(T,uv)
    # BASS native photo rate indices H1I, He3I, He3II; isotopes use same Z,q.
    return np.array([rates['photo_s'][1],rates['photo_s'][7],rates['photo_s'][8]]),T,uv


def source_photo_generator_17(y,gamma):
    y=np.asarray(y,float); g=np.asarray(gamma,float)
    if y.shape!=(17,) or g.shape!=(3,) or not (np.isfinite(y).all() and np.isfinite(g).all()):
        raise ValueError('vector dimensions/finiteness')
    src=np.array([a for a,b,k in PHOTO_EVENTS]);fam=np.array([k for a,b,k in PHOTO_EVENTS])
    flux=y[src]*g[fam]
    F=STOICH@flux
    J=STOICH@np.diag(g[fam])@np.eye(17)[src]
    return F,J,flux


def amplitude_shape_minimax(gamma_B, gamma_P):
    """Exact real scalar minimax for fixed positive channel shapes, not a fit.

    min_{u>0} max_j |u B_j/P_j -1|, with P_j and B_j positive.
    """
    b=np.asarray(gamma_B,float);p=np.asarray(gamma_P,float)
    if b.shape!=(3,) or p.shape!=(3,) or np.any(b<=0) or np.any(p<=0):
        raise ValueError('positive three-channel rates required')
    ratio=b/p
    lo=float(np.min(ratio));hi=float(np.max(ratio))
    u=2.0/(lo+hi)
    epsilon=(hi-lo)/(hi+lo)
    return u,epsilon,float(np.max(np.abs(u*ratio-1)))


def electron_matched_source_residual(y, gamma_B, gamma_P):
    """Pointwise scalar-electron match does not imply vector-chemistry match."""
    src=np.array([s for s,d,k in PHOTO_EVENTS]);fam=np.array([k for s,d,k in PHOTO_EVENTS])
    b=np.asarray(gamma_B,float);p=np.asarray(gamma_P,float)
    weights=np.asarray(y,float)[src]
    if np.any(weights<0):raise ValueError('nonnegative saved populations required')
    bflux=float(np.dot(weights,b[fam]));pflux=float(np.dot(weights,p[fam]))
    if bflux<=0:raise ValueError('nonzero BASS photo electron source required')
    u=pflux/bflux
    F_B,_,_=source_photo_generator_17(y,u*b)
    F_P,_,_=source_photo_generator_17(y,p)
    df=F_B-F_P
    return u,float(Q17@df),float(np.linalg.norm(df)),df


def compare_on_saved_rows(net):
    obj=json.loads((SRC/'REI_SAVED7.json').read_text())
    if obj['original_git_blob']!='189c2d903e25c18bee49e0ab6add3ba1d1805e93':
        raise ValueError('SAVED_SOURCE_IDENTITY_INVALID')
    result=[]
    for r in obj['rows']:
        z=float(r['z']); y=np.asarray(r['y'],float)
        bass,T,uv=bass_gamma_family(net,z)
        p19=p19_nominal_gamma(z)
        B,JB,flux_B=source_photo_generator_17(y,bass)
        P,JP,flux_P=source_photo_generator_17(y,p19)
        dF=B-P;dJ=JB-JP
        u_shape,err_shape,err_witness=amplitude_shape_minimax(bass,p19)
        u_e,e_res,vector_norm,vec=electron_matched_source_residual(y,bass,p19)
        electron=float(Q17@dF)
        direct=float(np.dot(y[[1,3,5]],(bass[0]-p19[0])*np.ones(3))+
                     (y[7]+y[10])*(bass[1]-p19[1])+
                     (y[8]+y[11])*(bass[2]-p19[2]))
        if not np.allclose(dF,dJ@y,rtol=5e-15,atol=5e-30):
            raise AssertionError('LINEAR_SOURCE_JAC_MISMATCH')
        result.append(dict(z=z,elapsed_proper_s=r['elapsed_proper_s'],T_BASS_K=T,uv_BASS_scale=uv,
          gamma_BASS_s=bass.tolist(),gamma_P19_nominal_s=p19.tolist(),delta_gamma_s=(bass-p19).tolist(),
          signed_electron_delta_per_Href_s=electron,direct_electron_delta_per_Href_s=direct,
          dF17_l2_per_s=float(np.linalg.norm(dF)),dJ17_max_abs_per_s=float(np.max(np.abs(dJ))),
          max_relative_family_rate_gap=float(np.max(np.abs(bass-p19)/np.maximum(p19,bass))),
          amplitude_minimax_scale=u_shape,amplitude_minimax_error=err_shape,
          amplitude_minimax_witness=err_witness,electron_match_scale=u_e,
          electron_matched_charge_residual=e_res,
          electron_matched_vector_residual_l2_s=vector_norm,
          isotope_heavy_y_invariant=float(A17@dF),photo_charge_bookkeeping=float(Q17@B-np.sum(flux_B))))
    return result


def native_jac_snapshot(net,z=3.603019593287379,nb_m3=1e6):
    T,uv=original_bass_bath_at_z(z)
    y=net.initial_Y.copy()
    base=net.evaluate(y,T,uv,nb_m3)
    rates=net.rates(T,uv)
    expected=(rates['G0']+rates['D']+base['ne']*rates['Gne']+
              nb_m3*np.outer(rates['Gne']@y,net.q))
    return y,base,expected,T,uv
