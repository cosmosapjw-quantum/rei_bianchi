#!/usr/bin/env python3
"""HE18 C2: source-bound analytic warm-P01 second-cell coupling map.

Derives *pointwise* gas-gas A, photon-to-gas B, gas-to-photon C from the
actual archived FT03/HM12 C1 RHS without changing the physical solver.
Not an interval supremum/whole-cell error certificate. No cold AXBI imports.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from fractions import Fraction
import numpy as np

RECEIVER_COMMIT = 'a5c958c414dea41216b445c05f58df837f05cacb'
PINS = {
    'P01_STATE.npz': '3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be',
    'emissivity.out': '88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
    'ENDPOINT_MEMORY_R7.json': 'aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39',
    'FIXED_REFERENCE_R4.npz': '7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be',
}
PHOTONS=2904
SCALES=np.array([1,1,1,32],dtype=np.longdouble)


def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_source(root:Path):
    root=Path(root).resolve()
    for name,digest in PINS.items():
        p=root/'inputs'/name
        if not p.is_file() or sha(p)!=digest:
            raise ValueError('SOURCE_INPUT_IDENTITY_MISMATCH:'+name)
    path=root/'src/warm_source_reference.py'
    if not path.is_file() or sha(path)!='8c434debdcb66ee499d61f7822980c73c75469bd426839a1597687042b8c78f3':
        raise ValueError('SOURCE_REFERENCE_IDENTITY_MISMATCH')
    spec=importlib.util.spec_from_file_location('frozen_he18_c1_source_reference',path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    source=obj.Source()
    if (source.y.shape[0]!=4+PHOTONS or source.times[1]!=obj.L(6250000000)
        or source.times[2]!=obj.L(12500000000)):
        raise ValueError('WARM_CELL_OR_STATE_SHAPE_MISMATCH')
    packet=json.loads((root/'inputs/ENDPOINT_MEMORY_R7.json').read_text())
    photon=np.asarray([obj.L(float(Fraction(x))) for x in packet['photon_error_end_raw_exact']],dtype=obj.L)
    gas=np.asarray([obj.L(float(Fraction(x))) for x in packet['gas_error_end_scaled']],dtype=obj.L)
    if (packet['source_interval_s']!=['0','6250000000'] or len(photon)!=PHOTONS
        or len(gas)!=4 or packet['next_cell_majorants'] is not None or np.any(photon<0)):
        raise ValueError('INCOMING_FIRST_CELL_SCOPE_MISMATCH')
    return obj,source,photon,gas


def reference_at(source,mathlib,u):
    if not 0<=u<=1:raise ValueError('SECOND_CELL_REFERENCE_COORDINATE')
    t0,t1=source.times[1:3];h=t1-t0
    left,right=source.y[:,1],source.y[:,2]
    ml=source.rhs(t0,left)[0].astype(np.float64).astype(mathlib.L)
    mr=source.rhs(t1,right)[0].astype(np.float64).astype(mathlib.L)
    y,dy=mathlib.Hval(left,right,ml,mr,h,mathlib.L(u))
    return t0+h*mathlib.L(u),y,dy


def rate_derivatives(source,T,mathlib):
    """Actual native FIT analytic derivatives, including g'(ln T) in kinetic RR."""
    L=mathlib.L
    ci,rr,kin,dr,drenergy=source.rates(T)
    lam=np.array(['315614','570670','1263030'],dtype=L)/T
    aa=np.array(['21.11','32.38','19.95'],dtype=L)
    pp=np.array(['-1.089','-1.146','-1.089'],dtype=L)
    c0=np.array(['.354','.416','.553'],dtype=L)
    powers=np.array(['.874','.987','.735'],dtype=L)
    dd=np.array(['1.101','1.056','1.275'],dtype=L)
    v=(lam/c0)**powers
    dci=ci*(-L('1.5')+lam/2-pp+dd*powers*v/(1+v))/T
    gg=np.zeros(3,dtype=L);dgg=np.zeros(3,dtype=L)
    for i in range(3):
        if i==1:gg[i]=-L('.654')
        else:
            u=(lam[i]/L('.522'))**L('.470')
            gg[i]=-L('1.503')+L('1.923')*L('.470')*u/(1+u)
            dgg[i]=-L('1.923')*L('.470')**2*u/(1+u)**2
    drr=rr*gg/T
    dkin=mathlib.KB*rr*((1+gg)*(L('1.5')+gg)+dgg)
    ddr=dr*(-L('1.5')+drenergy/mathlib.KB/T)/T
    return (ci,rr,kin,dr,drenergy),(dci,drr,dkin,ddr)


def jacobian_at(src,mathlib,t,state):
    """Analytic source linearization at one reference point, not a tube bound.

    A=dG/dg (4x4), B=dG/dP (4x2904), C=d(dP/dt)/dg
    (2904x4), photon D=diag(-kappa), P in reference-volume cm^-3.
    """
    L=mathlib.L;CL=mathlib.C;EV=mathlib.EV;KB=mathlib.KB
    g=np.asarray(state[:4],dtype=L);p=np.asarray(state[4:],dtype=L)
    nh,nhe,vol,H,E,sigma,forcing=src.env(t)
    x,y,z,w=g
    electron=nh*x+nhe*(y+2*z)
    f=nhe/nh;Pi=1+f+electron/nh
    T=2*EV*w/(3*KB*Pi)
    if not (L(30000)<=T<=L(110000)):raise ValueError('THERMAL_DOMAIN')
    d_ne=np.array([nh,nhe,2*nhe,0],dtype=L)
    d_T=np.array([-T/Pi,-f*T/Pi,-2*f*T/Pi,2*EV/(3*KB*Pi)],dtype=L)
    lower=np.array([nh*(1-x),nhe*(1-y-z),nhe*y],dtype=L)
    upper=np.array([nh*x,nhe*y,nhe*z],dtype=L)
    dlower=np.array([[-nh,0,0,0],[0,-nhe,-nhe,0],[0,nhe,0,0]],dtype=L)
    dupper=np.array([[nh,0,0,0],[0,nhe,0,0],[0,0,nhe,0]],dtype=L)
    (ci,rr,kin,dr,drenergy),(dci,drr,dkin,ddr)=rate_derivatives(src,T,mathlib)

    # P_j is reference-volume photon number; gas photo-rates contain 1/vol.
    weighted=sigma@p
    photo_coeff=CL/vol*weighted
    photo_heat_coeff=CL/vol*np.sum(sigma*(E[None,:]-mathlib.CHI[:,None])*p[None,:],axis=1,dtype=L)*EV
    dphoto=dlower*photo_coeff[:,None]
    dphoto_heat=np.sum(dlower*photo_heat_coeff[:,None],axis=0,dtype=L)

    def dprod(dbase,base,rates,drates):
        return (dbase*electron+base[:,None]*d_ne[None,:])*rates[:,None]+(base*electron*drates)[:,None]*d_T[None,:]

    dCI=dprod(dlower,lower,ci,dci)
    dRR=dprod(dupper,upper,rr,drr)
    dRK=dprod(dupper,upper,kin,dkin)
    # Both helium DR channels originate from the HeII upper population.
    dDR=(dupper[1,:][None,:]*electron+upper[1]*d_ne[None,:])*dr[:,None]+(upper[1]*electron*ddr)[:,None]*d_T[None,:]
    dnet=dCI-dRR+dphoto
    dnet[1]-=np.sum(dDR,axis=0,dtype=L)
    A=np.empty((4,4),dtype=L)
    A[0]=dnet[0]/nh
    A[1]=(dnet[1]-dnet[2])/nhe
    A[2]=dnet[2]/nhe
    dheat=dphoto_heat-np.sum(dCI*mathlib.CHI[:,None]*EV,axis=0,dtype=L)-np.sum(dRK,axis=0,dtype=L)-np.sum(dDR*drenergy[:,None],axis=0,dtype=L)
    A[3]=dheat/(nh*EV)
    A[3,3]-=2*H

    # The source photoionization and captured photoheating contributions.
    B=np.empty((4,PHOTONS),dtype=L)
    B[0]=CL*(1-x)*sigma[0]/vol
    B[1]=CL*((1-y-z)*sigma[1]-y*sigma[2])/vol
    B[2]=CL*y*sigma[2]/vol
    B[3]=CL/vol*((1-x)*sigma[0]*(E-mathlib.CHI[0])
          +f*(1-y-z)*sigma[1]*(E-mathlib.CHI[1])+f*y*sigma[2]*(E-mathlib.CHI[2]))

    kappa=CL*(lower@sigma)
    dk=np.zeros((PHOTONS,4),dtype=L)
    dk[:,0]=-CL*nh*sigma[0]
    dk[:,1]=CL*nhe*(sigma[2]-sigma[1])
    dk[:,2]=-CL*nhe*sigma[1]
    # Differentiating p'=forcing-kappa(g,t)*p at fixed reference P.
    C=-p[:,None]*dk
    A_sc=np.abs(A*SCALES[None,:]/SCALES[:,None])
    B_sc=np.abs(B/SCALES[:,None])
    C_sc=np.abs(C*SCALES[None,:])
    return dict(A=A,B=B,C=C,kappa=kappa,dkappa=dk,forcing=forcing,temperature=T,
          dne=d_ne,dT=d_T,gas_scale=SCALES,
          A_scaled_abs=A_sc,B_scaled_abs=B_sc,C_scaled_abs=C_sc,
          nH_cm3=nh,nHe_cm3=nhe,volume_ref_to_proper=vol,H_s_inv=H,
          units=dict(A='s^-1 per state coordinate',B='s^-1 per reference-volume photon cm^-3',
                     C='reference-volume photon cm^-3 s^-1 per gas coordinate',
                     electron_density='proper cm^-3',photon_stock='reference-volume cm^-3'))


def describe_at(root:Path,u:float=.5):
    mod,src,ph_error,gas_error=load_source(root)
    t,y,dy=reference_at(src,mod,u)
    J=jacobian_at(src,mod,t,y)
    actual,_=src.rhs(t,y)
    predicted=J['forcing']-J['kappa']*y[4:]
    relative_photon_rhs=float(np.sum(np.abs(actual[4:]-predicted),dtype=mod.L)
                 /max(np.sum(np.abs(actual[4:]),dtype=mod.L),mod.L('1e-100')))
    # Pointwise only, NOT an interval majorant or C3 certificate.
    incoming_phot_force=J['B_scaled_abs']@ph_error
    incoming_gas_force=J['A_scaled_abs']@gas_error
    h=src.times[2]-src.times[1]
    envelope=np.max(np.abs(J['C_scaled_abs']),axis=0)
    jmix=J['B_scaled_abs']@J['C_scaled_abs']
    kappa=J['kappa']
    out=dict(schema='bass-he18-c2-jacobian-map-v1',stage='C2',source_commit=RECEIVER_COMMIT,
             physical_model='warm P01 FT03/HM12 Case A; CR/RCT/HH OFF',
             time_s=str(t),cell_s=['6250000000','12500000000'],
             state_shape=[4,PHOTONS],incoming_nonzero=True,
             temperature_K=str(J['temperature']),
             H_s_inv=str(J['H_s_inv']),nH_proper_cm3=str(J['nH_cm3']),
             photo_damping_min_s_inv=str(np.min(kappa)),
             transparent_photon_nodes=int(np.count_nonzero(kappa==0)),
             rhs_photon_normalized_identity_error=relative_photon_rhs,
             norm_A_inf_at_point=float(np.max(np.sum(J['A_scaled_abs'],axis=1))),
             norm_B_inf_at_point=float(np.max(np.sum(J['B_scaled_abs'],axis=1))),
             norm_BC_inf_at_point=float(np.max(np.sum(jmix,axis=1))),
             incoming_photon_to_gas_scaled_force_s_inv=[str(v) for v in incoming_phot_force],
             incoming_gas_to_gas_scaled_force_s_inv=[str(v) for v in incoming_gas_force],
             demonstration_photon_to_gas_integrated_scaled=[str(v*h) for v in incoming_phot_force],
             rhs_calls_for_source_map=src.rhs_calls,
             A_B_C_analytic_pointwise=True,
             whole_cell_jacobian_enclosure=None,
             whole_cell_residual_enclosure=None,
             true_second_cell_IVP_error=None,
             provider_roundoff_bound=None,
             no_HH_CR_RCT_numeric_import=True)
    return J,out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private-c1-root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--u',type=float,default=.5)
    a=p.parse_args();J,summary=describe_at(a.private_c1_root,a.u)
    if a.out.exists():raise SystemExit('REFUSE_OVERWRITE')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
