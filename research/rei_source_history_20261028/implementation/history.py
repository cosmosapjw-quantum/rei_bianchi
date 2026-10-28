"""Finite saved-history reconstruction and analytic QSS error certificates.

No physical IVP or event-extents integration occurs in this module.
"""
from pathlib import Path
import importlib.util
import json
import sys
import numpy as np
from scipy.interpolate import PchipInterpolator

UNIT = Path(__file__).resolve().parents[1]
PREVIOUS = UNIT.parent / 'rei_external_sources_20261028' / 'implementation'
spec = importlib.util.spec_from_file_location('rei_previous_external_source', PREVIOUS/'model.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
SOURCE = old.NPZ_PATH.parents[1]


def clock(eta, H):
    eta, H = np.asarray(eta), np.asarray(H)
    if eta.shape != H.shape or np.any(np.diff(eta) <= 0) or np.any(H <= 0) or not np.isfinite(H).all():
        raise ValueError('invalid matched background clock')
    logh = PchipInterpolator(eta, np.log(H), extrapolate=False)
    def increments(order):
        nodes, weights = np.polynomial.legendre.leggauss(order)
        half = np.diff(eta)/2
        points = (eta[:-1]+eta[1:])[:,None]/2 + half[:,None]*nodes
        return half*(np.exp(-logh(points))@weights)
    dt8, dt16 = increments(8), increments(16)
    relative = np.abs(dt8-dt16)/dt16
    total = abs(dt8.sum()-dt16.sum())/dt16.sum()
    if np.any(relative > 1e-7) or total > 1e-8:
        raise ValueError('CLOCK_QUADRATURE_HOLD')
    return np.r_[0.,np.cumsum(dt8)], {'order':8,'comparison_order':16,
            'max_interval_relative_difference':float(relative.max()),'total_relative_difference':float(total)}


def baseline():
    eta,z,y,hidden,nref = old.load_baseline()
    with np.load(old.NPZ_PATH,allow_pickle=False) as d:
        H = d['H'].copy()
    if H.shape != (201,) or np.any(H <= 0) or not np.isfinite(H).all():
        raise ValueError('saved H schema invalid')
    t, check = clock(eta,H)
    return {'eta':eta,'z':z,'y':y,'hidden':hidden,'nref':nref,'H':H,'t':t,'clock_check':check}


def affine_reservoir(B0,S0,slope,L,dt):
    """Exact endpoint of B'=S0+slope*t-LB, used for static-limit tests only."""
    if L == 0:
        return B0+S0*dt+slope*dt*dt/2
    x=L*dt
    one=-np.expm1(-x)
    second=(x+np.expm1(-x))/(L*L) if abs(x)>1e-3 else dt*dt*(.5-x/6+x*x/24-x**3/120+x**4/720)
    return np.exp(-x)*B0+S0*one/L+slope*second


def five_fixed_point(S,kcap,c):
    lf=np.array([c['ks_'+j+'_s']+c['ke_'+j+'_s']+c['lambda_'+j+'_s']/c['gamma_'+j] for j in ('n','T')])
    B=np.asarray(S)/lf
    In,I0,I1=np.asarray(c['thermal_injection_per_Href_s'])[[0,5,6]]
    Ln=c['lambda_n_s']+kcap+c['kesc_s']
    LT=c['lambda_T_s']+c['kesc_s']
    g=sum(F*old.atomic_sigma(E,13.6,c) for E,F in c['photon_bins_eV_flux_cm2_s'])
    r=c['T_recombination_s']; determinant=LT*(LT+g+r)
    feed=I1+c['ks_T_s']*B[...,1]
    n=(In+c['ks_n_s']*B[...,0])/Ln
    t0=((LT+r)*I0+r*feed)/determinant
    t1=(g*I0+(LT+g)*feed)/determinant
    return np.stack([B[...,0],B[...,1],n,t0,t1],axis=-1)


def envelope_step(E,M,c,dt):
    return np.exp(-c*dt)*E + (-np.expm1(-c*dt))*M/c


def diagnose(data,c):
    """Exact interval slope bounds for the declared affine proper-time history."""
    t,y,nref=data['t'],data['y'],data['nref']
    S=np.array([old.reservoirs(row,1.,c)['S'] for row in y])
    cap=nref*(y[:,1]+y[:,2])*c['capture_C_cm3_s']
    fixed=five_fixed_point(S,cap,c)
    dt=np.diff(t); slopes=np.diff(S,axis=0)/dt[:,None]
    lf=np.array([c['ks_'+j+'_s']+c['ke_'+j+'_s']+c['lambda_'+j+'_s']/c['gamma_'+j] for j in ('n','T')])
    Ln=c['lambda_n_s']+cap+c['kesc_s']; LT=c['lambda_T_s']+c['kesc_s']
    Dp=np.diff(Ln)/dt
    N=c['thermal_injection_per_Href_s'][0]+c['ks_n_s']*S[:,0]/lf[0]
    Np=c['ks_n_s']*slopes[:,0]/lf[0]
    Mn=np.abs(slopes[:,0])/lf[0]+np.abs(Np*Ln[:-1]-N[:-1]*Dp)/np.minimum(Ln[:-1],Ln[1:])**2
    # Constant positive inverse T loss matrix gives same-sign thermal slopes;
    # their absolute sum is ksT/LT times |BT*'|. This is an analytic derivative
    # for the declared affine source, rather than a sampled finite difference.
    MT=np.abs(slopes[:,1])/lf[1]*(1+c['ks_T_s']/LT)
    cn=np.minimum(c['ke_n_s']+c['lambda_n_s']/c['gamma_n'],np.minimum(Ln[:-1],Ln[1:]))
    cT=min(c['ke_T_s']+c['lambda_T_s']/c['gamma_T'],LT)
    contraction=np.column_stack([cn,np.full(len(dt),cT)])
    M=np.column_stack([Mn,MT])
    norms=np.column_stack([fixed[:,[0,2]].sum(axis=1),fixed[:,[1,3,4]].sum(axis=1)])
    initial=np.zeros_like(norms); variation=np.zeros_like(norms); initial[0]=norms[0]
    for k,delta in enumerate(dt):
        decay=np.exp(-contraction[k]*delta)
        initial[k+1]=decay*initial[k]
        variation[k+1]=envelope_step(variation[k],M[k],contraction[k],delta)
    bound=initial+variation
    certified=bound<=.01*norms
    # Exact zero denominator: comparison above is true only for zero bound.
    relative=np.divide(bound,norms,out=np.zeros_like(bound),where=norms>0)
    summary={}
    for j,name in enumerate(('neutron','tritium')):
        bad=np.flatnonzero(~certified[:,j]); last=int(bad[-1]) if len(bad) else None
        first=(last+1 if last is not None and last+1<len(t) else (0 if last is None else None))
        summary[name]={'certified_saved_epochs':int(certified[:,j].sum()),'last_uncertified_index':last,
            'last_uncertified_eta':None if last is None else float(data['eta'][last]),
            'first_subsequently_all_certified_index':first,
            'first_subsequently_all_certified_elapsed_s':None if first is None else float(t[first]),
            'initial_relative_bound':float(relative[0,j]),'max_forcing_variation_bound_per_Href':float(variation[:,j].max())}
    return {'S':S,'kcap':cap,'fixed':fixed,'norms':norms,'initial':initial,'variation':variation,
            'bound':bound,'relative':relative,'certified':certified,'M':M,'contraction':contraction,
            'summary':summary,'interval_certification':'NOT_RUN'}
