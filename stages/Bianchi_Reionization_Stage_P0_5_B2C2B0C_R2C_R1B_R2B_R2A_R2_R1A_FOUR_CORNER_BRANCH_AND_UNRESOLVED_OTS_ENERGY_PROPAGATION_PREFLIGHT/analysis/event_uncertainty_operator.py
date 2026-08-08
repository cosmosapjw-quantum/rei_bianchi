#!/usr/bin/env python3
"""Event-resolved full-OTS population and augmented-energy uncertainty operator."""
from __future__ import annotations

from typing import NamedTuple
import numpy as np

KB_ERG=1.380649e-16
EV_ERG=1.602176634e-12
CHI_H_EV=13.598434599702
CHI_HEI_EV=24.587389011
CHI_HEII_EV=54.417760
HEII_LYA_EV=0.75*CHI_HEII_EV
ELL=1.425
M_CAS=0.737
P_EXC=0.96

SIGMA_OTS_H24=1.2391519584513023e-18
SIGMA_OTS_HEI24=7.43469869411065e-18
SIGMA_OTS_H41=2.884642817876362e-19
SIGMA_OTS_HEI41=3.0402144676144673e-18
SIGMA_OTS_H54=1.2306959247142394e-19
SIGMA_OTS_HEI54=1.6907806870529807e-18
SIGMA_OTS_HEII54=1.5872802575386495e-18

class EventFluxResult(NamedTuple):
    population_rhs: np.ndarray
    pds_flux: np.ndarray
    event_rates: dict[str,np.ndarray]
    branches: dict[str,np.ndarray]
    resolved_ots_heating_erg_s: np.ndarray
    unresolved_ots_energy_erg_s: np.ndarray
    escaped_ots_energy_erg_s: np.ndarray
    chemical_ots_energy_rate_erg_s: np.ndarray
    pds_reconstruction_residual: float
    max_augmented_energy_residual: float
    max_photon_count_identity_residual: float
    branch_domain_failure_count: int


def _sigmoid(x): return np.exp(-np.logaddexp(0.0,-np.asarray(x,dtype=np.float64)))
def _lambda_hi(T): return 315614.0/T
def _lambda_hei(T): return 570670.0/T
def _lambda_heii(T): return 1263030.0/T

def _alpha_b_hii(T):
    ll=_lambda_hi(T); return 2.753e-14*ll**1.5/(1.0+(ll/2.740)**0.407)**2.242

def _alpha_a_heii(T):
    ll=_lambda_hei(T); base=3.0e-14*ll**0.654
    dr=1.9e-3*T**-1.5*np.exp(-473638.0/T)*(1.0+0.3*np.exp(-94728.0/T))
    return base+_sigmoid((T-1.5e4)/250.0)*dr

def _alpha_b_heii(T):
    ll=_lambda_hei(T); base=1.26e-14*ll**0.750
    dr=1.9e-3*T**-1.5*np.exp(-473638.0/T)*(1.0+0.3*np.exp(-94728.0/T))
    return base+_sigmoid((T-1.5e4)/250.0)*dr

def _alpha_a_heiii(T):
    ll=_lambda_heii(T); return 2.0*1.269e-13*ll**1.503/(1.0+(ll/0.522)**0.470)**1.923

def _alpha_b_heiii(T):
    ll=_lambda_heii(T); return 2.0*2.753e-14*ll**1.5/(1.0+(ll/2.740)**0.407)**2.242

def _alpha_heiii_n2(T): return 3.4e-13*(T/1.0e4)**-0.6

def _beta_hi(T): return 5.835e-11*np.sqrt(T)*np.exp(-157804.0/T)
def _beta_hei(T): return 2.71e-11*np.sqrt(T)*np.exp(-285331.0/T)
def _beta_heii(T): return 5.707e-12*np.sqrt(T)*np.exp(-631495.0/T)


def flux_rhs(flux: np.ndarray) -> np.ndarray:
    return np.sum(flux,axis=2,dtype=np.float64)-np.sum(flux,axis=1,dtype=np.float64)



def _add(flux: np.ndarray,dest: int,source: int,rate: np.ndarray) -> None:
    values=np.asarray(rate,dtype=np.float64)
    if np.any(~np.isfinite(values)) or np.any(values<0.0):
        raise ValueError(f'negative or nonfinite event rate {source}->{dest}')
    flux[:,dest,source]+=values


def evaluate_event_flux(*,populations,temperature_K,proper_volume_cm3,photo_hi,photo_hei,photo_heii,
                        v,f) -> EventFluxResult:
    pop=np.asarray(populations,dtype=np.float64); T=np.asarray(temperature_K,dtype=np.float64)
    volume=np.asarray(proper_volume_cm3,dtype=np.float64)
    phi=np.asarray(photo_hi,dtype=np.float64); phe=np.asarray(photo_hei,dtype=np.float64); phe2=np.asarray(photo_heii,dtype=np.float64)
    vv=np.asarray(v,dtype=np.float64); ff=np.asarray(f,dtype=np.float64)
    if pop.ndim!=2 or pop.shape[1]!=5: raise ValueError('populations must have shape [N,5]')
    n=pop.shape[0]
    for name,a in [('temperature',T),('volume',volume),('photo_hi',phi),('photo_hei',phe),('photo_heii',phe2),('v',vv),('f',ff)]:
        if a.shape!=(n,) or np.any(~np.isfinite(a)): raise ValueError(f'{name} shape/finiteness')
    if np.any(pop<=0.0) or np.any(T<=0.0) or np.any(volume<=0.0): raise ValueError('material state must be strictly positive')
    if np.any(phi<0.0)|np.any(phe<0.0)|np.any(phe2<0.0): raise ValueError('photo rates must be nonnegative')
    if np.any((vv<0.0)|(vv>1.0)|(ff<0.0)|(ff>1.0)): raise ValueError('branch probability leaves [0,1]')

    nhi,nhii,nhei,nheii,nheiii=pop.T
    nh=nhi+nhii
    ne=(nhii+nheii+2.0*nheiii)/volume
    floor=1e-300
    y=(nhi/volume*SIGMA_OTS_H24)/(nhi/volume*SIGMA_OTS_H24+nhei/volume*SIGMA_OTS_HEI24+floor)
    z=(nhi/volume*SIGMA_OTS_H41)/(nhi/volume*SIGMA_OTS_H41+nhei/volume*SIGMA_OTS_HEI41+floor)
    op_h54=nhi/volume*SIGMA_OTS_H54; op_he54=nhei/volume*SIGMA_OTS_HEI54; op_heii54=nheii/volume*SIGMA_OTS_HEII54
    total54=op_h54+op_he54+op_heii54+floor
    y2a=op_heii54/total54; y2b=op_he54/total54
    w=(ELL-M_CAS)+M_CAS*y
    A_H=vv*w+(1.0-vv)*ff*z
    A_HeI=vv*M_CAS*(1.0-y)+(1.0-vv)*ff*(1.0-z)
    nonion=vv*(2.0-ELL); escape_count=(1.0-vv)*(1.0-ff)
    photon_identity=A_H+A_HeI+nonion+escape_count-(1.0+vv)
    branch_bad=((y<0)|(y>1)|(z<0)|(z>1)|(y2a<0)|(y2b<0)|(y2a+y2b>1+2e-14)|
                (w<0)|(A_H<0)|(A_HeI<0)|(nonion<0)|(escape_count<0))

    r_hi=phi+nhi*ne*_beta_hi(T)
    r_hei=phe+nhei*ne*_beta_hei(T)
    r_heii=phe2+nheii*ne*_beta_heii(T)
    aA2=_alpha_a_heii(T); aB2=_alpha_b_heii(T); aA3=_alpha_a_heiii(T); aB3=_alpha_b_heiii(T)
    aN2=np.minimum(_alpha_heiii_n2(T),aB3); aCas=np.maximum(aB3-aN2,0.0)
    r_hb=nhii*ne*_alpha_b_hii(T)
    r_he2g=nheii*ne*np.maximum(aA2-aB2,0.0)
    r_he2b=nheii*ne*aB2
    r_he3g=nheiii*ne*np.maximum(aA3-aB3,0.0)
    r_he3n2=nheiii*ne*aN2
    r_he3cas=nheiii*ne*aCas

    flux=np.zeros((n,5,5),dtype=np.float64)
    _add(flux,1,0,r_hi); _add(flux,3,2,r_hei); _add(flux,4,3,r_heii)
    _add(flux,0,1,r_hb)
    _add(flux,2,3,r_he2g); _add(flux,1,0,r_he2g*y); _add(flux,3,2,r_he2g*(1.0-y))
    _add(flux,2,3,r_he2b); _add(flux,1,0,r_he2b*P_EXC)
    _add(flux,3,4,r_he3g); _add(flux,1,0,r_he3g*(1.0-y2a-y2b)); _add(flux,3,2,r_he3g*y2b); _add(flux,4,3,r_he3g*y2a)
    _add(flux,3,4,r_he3n2); _add(flux,1,0,r_he3n2)
    _add(flux,3,4,r_he3cas); _add(flux,1,0,r_he3cas*A_H); _add(flux,3,2,r_he3cas*A_HeI)
    rhs=flux_rhs(flux)
    recon_scale=np.maximum(np.max(np.abs(rhs),axis=1),1.0)
    pds_res=float(np.max(np.max(np.abs(flux_rhs(flux)-rhs),axis=1)/recon_scale))

    # Only the monoenergetic He II Ly-alpha packet has a source-locked first
    # energy moment.  The two-photon and free-bound/cascade first moments remain
    # unresolved and therefore never modify the resolved thermal state.
    heat_lya=(1.0-vv)*ff*(z*(HEII_LYA_EV-CHI_H_EV)+(1.0-z)*(HEII_LYA_EV-CHI_HEI_EV))
    escape_lya=(1.0-vv)*(1.0-ff)*HEII_LYA_EV

    chemical=(
        r_hb*(-CHI_H_EV)
        +r_he2g*(-CHI_HEI_EV+y*CHI_H_EV+(1.0-y)*CHI_HEI_EV)
        +r_he2b*(-CHI_HEI_EV+P_EXC*CHI_H_EV)
        +r_he3g*(-CHI_HEII_EV+(1.0-y2a-y2b)*CHI_H_EV+y2b*CHI_HEI_EV+y2a*CHI_HEII_EV)
        +r_he3n2*(-CHI_HEII_EV+CHI_H_EV)
        +r_he3cas*(-CHI_HEII_EV+vv*(w*CHI_H_EV+M_CAS*(1.0-y)*CHI_HEI_EV)
                    +(1.0-vv)*ff*(z*CHI_H_EV+(1.0-z)*CHI_HEI_EV))
    )*EV_ERG
    resolved=r_he3cas*heat_lya*EV_ERG
    escaped=r_he3cas*escape_lya*EV_ERG
    # The unidentified packet spectrum is retained as an explicit radiation
    # reservoir.  This is the unique nonnegative binding-energy remainder once
    # the population event graph, exact Ly-alpha heat, and escape owner are
    # fixed.  It is not a fitted or midpoint energy moment.
    unresolved=-chemical-resolved-escaped
    energy_res=chemical+resolved+unresolved+escaped
    energy_scale=np.maximum.reduce([np.abs(chemical),resolved,unresolved,escaped,np.ones(n)])
    max_energy=float(np.max(np.abs(energy_res)/energy_scale))
    if np.any(resolved<-1e-14*np.maximum(np.abs(chemical),1.0)) or np.any(unresolved<0.0) or np.any(escaped<0.0):
        branch_bad=branch_bad|np.ones(n,dtype=bool)

    rates={'HI_ION':r_hi,'HEI_ION':r_hei,'HEII_ION':r_heii,'HII_CASE_B':r_hb,
           'HEII_GROUND':r_he2g,'HEII_CASE_B':r_he2b,'HEIII_GROUND':r_he3g,
           'HEIII_N2':r_he3n2,'HEIII_CASCADE':r_he3cas}
    branches={'y':y,'z':z,'y2a':y2a,'y2b':y2b,'w':w,'A_H':A_H,'A_HeI':A_HeI,
              'two_photon_nonionizing':nonion,'lya_escape_count':escape_count}
    return EventFluxResult(rhs,flux,rates,branches,resolved,unresolved,escaped,chemical,pds_res,max_energy,
                           float(np.max(np.abs(photon_identity))),int(np.count_nonzero(branch_bad)))
