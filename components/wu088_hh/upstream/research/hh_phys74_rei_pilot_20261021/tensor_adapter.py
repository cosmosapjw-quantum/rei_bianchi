"""Vectorized normal-orthonormal-frame diagnostics, with explicit stress convention.

H and sigma: proper-time s^-1. Every stress tensor: energy density J/m^3.
kappa_time = c^2 kappa_Einstein = 8*pi*G/c^2. No model or closure is inferred.
"""
import numpy as np

def _frobenius(a):
    scale=np.max(np.abs(a),axis=(-2,-1))
    safe=np.where(scale==0,1.,scale)
    return scale*np.sqrt(np.sum((a/safe[...,None,None])**2,axis=(-2,-1)))

def tensor_norms(H,sigma,stress_components,*,kappa_time):
    h=np.asarray(H,dtype=float);s=np.asarray(sigma,dtype=float);ps=np.asarray(stress_components,dtype=float)
    if s.shape[-2:]!=(3,3) or ps.ndim<3 or ps.shape[-2:]!=(3,3) or ps.shape[-3]<1:raise ValueError('3x3 tensors and a nonempty species axis are required')
    if not np.isfinite(kappa_time) or kappa_time<=0 or np.any(h<=0) or not all(np.isfinite(a).all() for a in (h,s,ps)):raise ValueError('finite tensors and positive H,kappa_time required')
    for a in (s,ps):
        scale=np.maximum(np.max(np.abs(a),axis=(-2,-1)),np.finfo(float).tiny)
        if np.any(np.max(np.abs(a-np.swapaxes(a,-1,-2)),axis=(-2,-1))>1e-11*scale) or np.any(np.abs(np.trace(a,axis1=-2,axis2=-1))>1e-11*scale):raise ValueError('symmetric trace-free tensors required in one orthonormal frame')
    p=ps.sum(axis=-3)  # signed tensors summed before taking a norm
    sn=_frobenius(s);pn=_frobenius(p)
    sf=sn/h;pf=kappa_time*pn/h**2
    unit_s=s/np.where(sn==0,1.,sn)[...,None,None]
    unit_p=p/np.where(pn==0,1.,pn)[...,None,None]
    alignment=np.sum(unit_s*unit_p,axis=(-2,-1))
    valid=(sn>0)&(pn>0)
    # No fabricated alignment at a vanishing norm. validity accompanies NaN.
    return dict(Sigma_F=sf,Pi_F=pf,work=sf*pf*alignment,
                alignment=np.where(valid,alignment,np.nan),alignment_defined=valid,
                shear_energy_fraction=sf**2/6)

def lrs_tensors(s,components,*,stress_representation):
    """components shape (...,species), representation is pi_s=DeltaP/3 or delta_p."""
    shear=np.asarray(s,dtype=float);p=np.asarray(components,dtype=float)
    if stress_representation=='delta_p':p=p/3.
    elif stress_representation!='pi_s':raise ValueError('declare pi_s or delta_p; never infer from a field name')
    pattern=np.diag([-1.,-1.,2.])
    return shear[...,None,None]*pattern,p[...,None,None]*pattern
