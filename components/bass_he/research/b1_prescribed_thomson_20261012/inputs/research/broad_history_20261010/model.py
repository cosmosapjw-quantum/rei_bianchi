"""R15/HG97-B reduced mean-volume history. Not a native CR/thermal solver."""
from __future__ import annotations
import hashlib
import importlib.util
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
BG_PATH=HERE.parent/'physical_provider_20261010'/'background.py'
BG_SHA='b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d'
if hashlib.sha256(BG_PATH.read_bytes()).hexdigest()!=BG_SHA:
    raise RuntimeError('PINNED_BACKGROUND_CHANGED')
_spec=importlib.util.spec_from_file_location('acc_pinned_background',BG_PATH)
_bg=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_bg)
C_CM_S=2.99792458e10
SIGMA_T_CM2=6.6524587321e-25
MYR_S=365.25*86400*1e6

def default_config():
    return dict(z_i=20.,z_f=4.,r=0.,T_K=20000.,clumping=3.,fesc=.2,
                q_i=0.,h=.6774,omega_m=.309,omega_b_h2=.02230,Y=.2453)

def validated_config(config):
    c=default_config()
    if set(config)-set(c): raise ValueError('UNKNOWN_CONFIG_KEY')
    c.update(config)
    if not all(math.isfinite(float(v)) for v in c.values()):
        raise ValueError('NONFINITE_CONFIG')
    if not (c['z_i']==20 and c['z_f']==4 and abs(c['r'])<=.1
            and 10000<=c['T_K']<=30000 and 0<c['clumping']<=5
            and 0<c['fesc']<=1 and 0<=c['q_i']<=1
            and c['h']==.6774 and c['omega_m']==.309
            and c['omega_b_h2']==.02230 and c['Y']==.2453):
        raise ValueError('OUTSIDE_DECLARED_CAMPAIGN_DOMAIN')
    return c

def make_background(config):
    c=validated_config(config)
    return _bg.BianchiBackground(r=c['r'],z_i=c['z_i'],Hfid_km_s_Mpc=100*c['h'],
        omega_m=c['omega_m'],omega_lambda=1-c['omega_m'],
        omega_b=c['omega_b_h2']/c['h']**2,helium_mass_fraction=c['Y'],t_max=1e17)

def alpha_b(T):
    if not math.isfinite(T) or not 1<=T<=1e9: raise ValueError('HG97_RATE_DOMAIN')
    lam=315614./T
    return 2.753e-14*lam**1.5/(1+(lam/2.740)**.407)**2.242

def sfrd(z):
    if not math.isfinite(z) or not 4<=z<=20: raise ValueError('R15_SELECTED_DOMAIN')
    return .01376*(1+z)**3.26/(1+((1+z)/2.59)**5.68)

def advance_constant(q,A,B,h):
    """Exact capped dQ/dx=A-BQ, with integrated reaction counters.

    Cap is a complementarity closure with nonnegative unassigned excess.
    A declining equilibrium below1 immediately allows recombination.
    """
    if not all(math.isfinite(v) for v in (q,A,B,h)) or not(0<=q<=1 and A>=0 and B>=0 and h>=0):
        raise ValueError('REACTION_DOMAIN')
    def free(dt):
        if B==0: return q+A*dt,q*dt+.5*A*dt*dt
        u=B*dt; exp=math.exp(-u); j=-math.expm1(-u)/B
        # Analytic phi2 series avoids cancellation at vanishing sink.
        k=(dt*dt*(.5-u/6+u*u/24-u**3/120+u**4/720)
           if abs(u)<1e-3 else (dt-j)/B)
        return q*exp+A*j,q*j+A*k
    raw,iq=free(h); excess=0.
    if raw>1. or (q==1. and A>B):
        hit=(1-q)/A if B==0 else math.log1p((1-q)*B/(A-B))/B
        if not (0<=hit<=h+2e-14*max(1,h)):raise RuntimeError('OVERLAP_ROOT_DOMAIN')
        _,iq0=free(hit); remainder=max(0.,h-hit)
        iq=iq0+remainder; raw=1.; excess=(A-B)*remainder
    return dict(q=raw,integral_q=iq,rec=B*iq,emitted=A*h,excess=excess)

def coefficients(x,c,bg):
    a=bg.a_i*math.exp(x); z=1/a-1
    # Roundoff at the specified endpoints is resolved by exact endpoint labels.
    if abs(z-c['z_i'])<1e-12:z=c['z_i']
    if abs(z-c['z_f'])<1e-12:z=c['z_f']
    v=a**3; H=math.sqrt(bg.D+bg.B/v+bg.C/v**2)
    nH=bg.nH_i*bg.v_i/v; nHe=bg.nHe_i*bg.v_i/v
    source=c['fesc']*10**53.14*sfrd(z)/(_bg.MPC_CM**3*bg.nH_i*bg.v_i)
    recomb=c['clumping']*alpha_b(c['T_K'])*(nH+nHe)
    return dict(z=z,H=H,nH=nH,nHe=nHe,A=source/H,B=recomb/H,
                tau_factor=C_CM_S*SIGMA_T_CM2*(nH+nHe)/H,s_over_H=bg.s0/v/H)

def history(config,nsteps):
    c=validated_config(config)
    if isinstance(nsteps,bool) or not isinstance(nsteps,int) or nsteps<16:
        raise ValueError('NSTEP_DOMAIN')
    bg=make_background(c); xmax=math.log((1+c['z_i'])/(1+c['z_f']))
    xs=np.linspace(0,xmax,nsteps+1); dx=xmax/nsteps
    # q, recombination, emission, unassigned excess, tau segment, elapsed s, b
    y=np.zeros((nsteps+1,7)); y[0,0]=c['q_i']
    for i in range(nsteps):
        k=coefficients(float((xs[i]+xs[i+1])/2),c,bg)
        o=advance_constant(float(y[i,0]),k['A'],k['B'],dx)
        y[i+1]=y[i]+[o['q']-y[i,0],o['rec'],o['emitted'],o['excess'],
                           k['tau_factor']*o['integral_q'],dx/k['H'],dx*k['s_over_H']]
    ks=[coefficients(float(x),c,bg) for x in xs]
    z=np.array([k['z'] for k in ks]); ne=np.array([(k['nH']+k['nHe'])*q for k,q in zip(ks,y[:,0])])
    ledger=y[:,0]-c['q_i']+y[:,1]+y[:,3]-y[:,2]
    out=dict(x=xs,z=z,Q=y[:,0],Nrec=y[:,1],Nemit=y[:,2],Nexcess=y[:,3],
             tau=y[:,4],t_s=y[:,5],b=y[:,6],ne_cm3=ne,
             nH_cm3=np.array([k['nH'] for k in ks]),H_s=np.array([k['H'] for k in ks]),
             ledger=ledger)
    if not all(np.all(np.isfinite(a)) for a in out.values()):raise RuntimeError('NONFINITE_HISTORY')
    if np.min(out['Q'])<0 or np.max(out['Q'])>1+2e-15:raise RuntimeError('POSITIVITY_FAILURE')
    return out

def crossing_redshift(h,target):
    indices=np.flatnonzero(h['Q']>=target)
    if not len(indices):return None
    i=int(indices[0])
    if i==0:return float(h['z'][0])
    w=(target-h['Q'][i-1])/(h['Q'][i]-h['Q'][i-1])
    x=h['x'][i-1]+w*(h['x'][i]-h['x'][i-1])
    return float(21*math.exp(-x)-1)

def summarize(h):
    return dict(z50=crossing_redshift(h,.5),z90=crossing_redshift(h,.9),
        z99=crossing_redshift(h,.99),tau_20_to_4=float(h['tau'][-1]),
        duration_Myr=float(h['t_s'][-1]/MYR_S),Q_final=float(h['Q'][-1]),
        Nemit=float(h['Nemit'][-1]),Nrec=float(h['Nrec'][-1]),Nexcess=float(h['Nexcess'][-1]),
        max_photon_ledger_abs=float(np.max(np.abs(h['ledger']))),
        nH0_cm3=float(h['nH_cm3'][0]/21**3))
