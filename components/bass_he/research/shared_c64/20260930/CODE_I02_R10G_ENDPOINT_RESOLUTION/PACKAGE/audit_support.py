"""Isolated archived audit support, with no BASS_HE contour/package import.

The event topology, state map and velocity/charge conventions are transcribed
from the pinned clean-room source and checked by archived first-panel replay.
This is supporting implementation evidence, not a full repository execution.
"""
from __future__ import annotations
import ast,hashlib,json
from functools import lru_cache
from pathlib import Path
import numpy as np
from eta_rotation import operators,velocity,eta_rotation_batch

ROOT=Path(__file__).resolve().parent
EVENTS=((2,5,True),(1,5,True),(0,2,False),(3,8,True),(2,7,True))
BLOCKS=((2,1,(2,3)),(3,1,(5,6)),(3,2,(7,8,9)))
BRANCH_NAMES=('S23','Qother','Q12','Qm1','Q23')
LANES=('SL_CPC','SL_AUTHORCUT','COUL_CPC','COUL_AUTHOR','COUL_AUTHOR_FROZEN')


def propagate(p,rot):
    p=np.asarray(p,float);rot=np.asarray(rot,float)
    if p.ndim!=2 or p.shape[1]!=5 or rot.shape!=(len(p),10,10):raise ValueError('transport shapes')
    if np.any(~np.isfinite(p)) or np.any((p<0)|(p>1)) or np.any(~np.isfinite(rot)):
        raise ValueError('invalid transition probabilities')
    if np.max(abs(rot.sum(1)-1))>2e-10 or np.min(rot)<-1e-13:raise ValueError('rotation not stochastic')
    y=np.zeros((len(p),10));y[:,2]=1.
    def event(k):
        i,j,sink=EVENTS[k];q=p[:,k];yi=y[:,i].copy();yj=y[:,j].copy()
        if sink:y[:,i]=(1-q)*yi;y[:,j]=yj+q*yi
        else:y[:,i]=(1-q)*yi+q*yj;y[:,j]=(1-q)*yj+q*yi
    for k in reversed(range(5)):event(k)
    y=np.einsum('bij,bj->bi',rot,y)
    for k in range(5):event(k)
    if np.max(abs(y.sum(1)-1))>3e-10:raise ArithmeticError('transport invariant')
    return y


@lru_cache(maxsize=1)
def original_adapter():
    # Exact original file; dependency facade replaces package imports only.
    raw=(ROOT/'fixtures/R10D_coulomb_rotation.py').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!='543ff5e5c20ff2969547f03410cd30353998348c':raise ValueError('original adapter identity')
    def angular(l):
        lx,lz,_,_=operators(l);return lx,-1j*(lz@lx-lx@lz),lz
    def basis(l):return np.arange(-l,l+1),operators(l)[2]
    def eps(N,l,Z1=1.,Z2=2.):return 6*Z1*Z2*(Z1+Z2)**2/(N**3*l*(l+1)*(2*l-1)*(2*l+1)*(2*l+3))
    import math
    namespace={'np':np,'math':math,'angular_operators':angular,'molecular_x_basis':basis,
               'epsilon_rotational':eps,'s_sigma_boundary':lambda l:((l+.5)**2-.5)/3,
               'projectile_velocity_au':lambda E:(2.*E/(27.07*1.836153))**.5}
    tree=ast.parse(raw);tree.body=[x for x in tree.body if not isinstance(x,(ast.Import,ast.ImportFrom))]
    exec(compile(tree,'PINNED_ORIGINAL_ADAPTER','exec'),namespace)
    return namespace['coulomb_rotation_batch']


def frozen_components(rhos,*,method='eta',steps=256):
    rhos=np.asarray(rhos,float);r=np.repeat(rhos,2);E=np.tile([.5,5.],len(rhos))
    P=np.broadcast_to(np.eye(10),(len(r),10,10)).copy()
    for N,l,ids in BLOCKS:
        f=eta_rotation_batch if method=='eta' else original_adapter()
        p=f(N,l,E,r,steps=steps,R_cut=(l+.5)**2/3)['P_abs']
        P[:,np.asarray(ids)[:,None],ids]=p
    rec=json.loads((ROOT/'fixtures/R10C_FROZEN_DELTA0_RECORD.json').read_text())
    if [x['branch'] for x in rec['records']]!=list(BRANCH_NAMES):raise ValueError('branch ordering')
    d=np.array([float.fromhex(x['delta0_hex']) for x in rec['records']])
    p=np.exp(-2*d/velocity(E)[:,None])
    return propagate(p,P)[:,np.arange(10)!=2].reshape(len(rhos),18)
