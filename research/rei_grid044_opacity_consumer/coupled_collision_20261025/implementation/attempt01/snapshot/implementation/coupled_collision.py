"""Fixed selected-edge photon/target collision consumer; no integration/closure.

Coordinates N16,y21,B,K,Xext are per fixed reference; energies eV, time s,
proper nref m^-3, sigma m^2. B is redundant, counted once; K is injection,
not deposited heat. Electron abundance is algebraic q@y. No generic compiler.
"""
from pathlib import Path
import importlib.util
import json
import sys
import numpy as np

INPUTS=Path(__file__).resolve().parent.parent/'runtime_inputs'
REG=json.loads((INPUTS/'SELECTED_REGISTRY.json').read_text())
SPECIES=tuple(REG['SPECIES']); BLOCKS=tuple(tuple(b) for b in REG['BLOCKS'])
EDGES=tuple(tuple(e) for e in REG['EDGES'])
CHI=np.array([13.6,24.59,54.42,5.392,75.64,122.5])
C=299792458.; DIM=40; B=37; K=38; X=39
Q=np.array([0 if n=='n' else int(n.rsplit('_',1)[1]) for n in SPECIES],float)
EPS=np.zeros(21)
for lo,up,ch in EDGES: EPS[up]=EPS[lo]+CHI[ch]


def positive(value,shape,name,strict=False,complex_ok=False):
    a=np.asarray(value)
    if a.shape!=shape or not np.all(np.isfinite(a)) or (not complex_ok and np.iscomplexobj(a)):
        raise ValueError('INVALID_'+name+'_SHAPE_OR_FINITE_DOMAIN')
    if np.any(np.real(a)<=0 if strict else np.real(a)<0):
        raise ValueError('INVALID_'+name+'_POSITIVE_DOMAIN')
    return a


def source_fixture():
    """Actual unchanged source formula at z=2, split GL2, saved normalizers."""
    config=json.loads((INPUTS/'MODEL_CONFIG.json').read_text())
    norm=np.asarray(json.loads((INPUTS/'NORMALIZER_PAYLOAD.json').read_text())['source_normalizers'])
    cuts=np.asarray(config['spectral_split_eV']); nodes=np.array([-1/np.sqrt(3),1/np.sqrt(3)])
    E=((cuts[:-1,None]+cuts[1:,None])/2+(cuts[1:,None]-cuts[:-1,None])*nodes/2).ravel()
    W=np.repeat(np.diff(cuts)/2,2); templates=[]; rates=[]
    for source,normalizer in zip(config['sources'],norm):
        if source['name']=='stellar':
            kt=source['temperature_K']*1.380649e-23/1.602176634e-19
            raw=E**2/np.expm1(E/kt)
        else:
            raw=source['pivot_energy_eV']**2*np.exp(-E/source['cutoff_energy_eV'])/E**2
        rate=source['amplitude_per_Href_s']*source['escape_fraction']*(1+np.tanh((source['z_on']-2.)/source['delta_z']))/2
        templates.append(rate*W*raw/normalizer);rates.append(rate)
    spec=importlib.util.spec_from_file_location('coupled_pinned_atomic',INPUTS/'provider/atomic_network.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    provider=module._load_provider()
    sigma=np.array([provider.sigma(name,E)*1e-22 for name in module.CHANNEL_NAMES])
    previous=json.loads((INPUTS/'OPACITY_PAYLOAD.json').read_text())
    y=np.asarray(previous['target_fixture']['y_per_Href'])
    z=np.zeros(DIM);S=np.asarray(templates);z[:16]=S.sum(axis=0)*1. # one second local operator fixture
    z[16:37]=y;z[B]=EPS@y;z[K]=1e-20;z[X]=1e-20
    return E,S,sigma,z,np.asarray(rates),provider


class Collision:
    """Complete local Jacobian at independent fixed nref,E,S and affine Lambda.

    nref partial holds normalized state and per-reference source templates fixed.
    No chain rule for algebraic nref(z) or fixed-volume source is implied.
    """
    def __init__(self,E,S,sigma,nref):
        self.E=positive(E,(16,),'ENERGY',strict=True).copy()
        if np.any(self.E>5e4):raise ValueError('ENERGY_OUTSIDE_PINNED_PROVIDER_DOMAIN')
        self.S=positive(S,(2,16),'SOURCE').copy()
        self.sigma=positive(sigma,(6,16),'SIGMA').copy()
        self.nref=float(positive(nref,(),'NREF',strict=True))
        if np.any(self.sigma[self.E[None,:]<CHI[:,None]]!=0):raise ValueError('NONZERO_SUBTHRESHOLD_SIGMA')
        self.a=C*self.nref*self.sigma

    def evaluate(self,z,alpha=(1.,1.),Lambda0=0.,gradient=None,anchor=None):
        z=positive(z,(DIM,),'STATE',complex_ok=True)
        alpha=positive(alpha,(2,),'AMPLITUDE',complex_ok=True)
        L0=np.asarray(Lambda0)
        if L0.shape!=() or not np.all(np.isfinite(L0)) or np.iscomplexobj(L0):raise ValueError('INVALID_LAMBDA')
        g=np.zeros(DIM) if gradient is None else np.asarray(gradient)
        if g.shape!=(DIM,) or not np.all(np.isfinite(g)) or np.iscomplexobj(g):raise ValueError('INVALID_LAMBDA_GRADIENT')
        anchor=np.zeros(DIM) if anchor is None and gradient is None else np.asarray(anchor)
        if anchor.shape!=(DIM,) or not np.all(np.isfinite(anchor)) or np.iscomplexobj(anchor):raise ValueError('INVALID_LAMBDA_ANCHOR')
        L=L0+g@(z-anchor)
        dtype=np.result_type(z,alpha,float);f=np.zeros(DIM,dtype=dtype);J=np.zeros((DIM,DIM),dtype=dtype)
        N=z[:16];y=z[16:37];events=[]
        for lo,up,ch in EDGES:
            dN=self.a[ch]*y[lo];dy=self.a[ch]*N;event=dN*N;total=event.sum();events.append(event)
            f[:16]-=event;f[16+lo]-=total;f[16+up]+=total
            f[B]+=CHI[ch]*total;f[K]+=(self.E-CHI[ch])@event
            J[:16,:16]-=np.diag(dN);J[:16,16+lo]-=dy
            for row,weight in ((16+lo,-1.),(16+up,1.),(B,CHI[ch])):
                J[row,:16]+=weight*dN;J[row,16+lo]+=weight*dy.sum()
            J[K,:16]+=(self.E-CHI[ch])*dN;J[K,16+lo]+=(self.E-CHI[ch])@dy
        collision=f.copy();injection=alpha@self.S
        f[:16]+=injection;f[X]+=self.E@injection
        sourceJ=np.zeros((DIM,2));sourceJ[:16]=self.S.T;sourceJ[X]=self.S@self.E
        f-=L*z;J-=L*np.eye(DIM)+np.outer(z,g)
        return f,J,sourceJ,collision/self.nref,np.asarray(events),L

    def energy_derivative(self,z,F,E_dot=None):
        """Bookkeeping derivative with explicitly supplied packet geometry work."""
        z=positive(z,(DIM,),'STATE',complex_ok=True)
        F=np.asarray(F)
        if F.shape!=(DIM,) or not np.all(np.isfinite(F)):raise ValueError('INVALID_RHS')
        drift=np.zeros(16) if E_dot is None else np.asarray(E_dot)
        if drift.shape!=(16,) or not np.all(np.isfinite(drift)) or np.iscomplexobj(drift):raise ValueError('INVALID_EXPLICIT_ENERGY_DRIFT')
        return self.E@F[:16]+F[B]+F[K]-F[X]+drift@z[:16]
