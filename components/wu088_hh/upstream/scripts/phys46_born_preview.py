#!/usr/bin/env python3
"""NONCERTIFYING finite-21 Coulomb Jost first-Born matrix preview.

Uses actual two-centre screened angular potential, Gauss angular/radial
quadrature, and 50-digit Coulomb H+ functions. This is independent
numerical confirmation of the PHYS46 rigorous *bound*, NOT certification
of the Born integral or production HH ionization physics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys46_volterra import finite21_volterra_certificate

NCHANNEL=21


def full_potential_angular(r:float,P:np.ndarray,mu:np.ndarray,w:np.ndarray)->np.ndarray:
    if not r>0.7:
        raise ValueError("outside spectator cusp")
    s=np.sqrt(r*r+.7**2-2*r*.7*mu)
    S=(1+1/s)*np.exp(-2*s)
    return P.T@((w*S)[:,None]*P)/2


def first_born_preview(source:Path,radial_levels=(20,31,43,55),
                       grids=(24,24,16),angular_nodes:int=192,dps:int=42)->dict:
    if tuple(sorted(radial_levels))!=tuple(radial_levels) or radial_levels[0]!=20:
        raise ValueError("ordered actual exterior integration windows")
    if len(grids)!=len(radial_levels)-1 or not all(4<=n<=128 for n in grids):
        raise ValueError("bounded physical radial quadrature")
    if not 64<=angular_nodes<=512 or not 35<=dps<=100:
        raise ValueError("bounded precision")
    t0=perf_counter()
    cert=finite21_volterra_certificate(source,candidate_T=(31,),workers=1)
    k=mp.mpf(7)/10
    eta=-1/k
    mu,w=np.polynomial.legendre.leggauss(angular_nodes)
    Leg=np.polynomial.legendre.legvander(mu,NCHANNEL-1)
    amp=np.sqrt(2*np.arange(NCHANNEL)+1)
    P=Leg*amp
    qnodes=[]
    for a,b,n in zip(radial_levels,radial_levels[1:],grids):
        nodes,weights=np.polynomial.legendre.leggauss(n)
        for x,wx in zip(nodes,weights):
            qnodes.append((float((a+b)/2+(b-a)/2*x),float((b-a)/2*wx)))
    with mp.workdps(dps):
        k=mp.mpf(7)/10
        eta=-1/k
        def coulomb_h(row,r):
            rho=k*mp.mpf(r)
            return mp.coulombg(row,eta,rho)+1j*mp.coulombf(row,eta,rho)
        hb=[coulomb_h(l,20) for l in range(NCHANNEL+1)]
        H=np.array([complex(hb[l]) for l in range(NCHANNEL)])
        Hdot=np.array([complex(k*((l+1)/(20*k)+eta/(l+1))*hb[l]-
                  k*mp.sqrt(1+(eta/mp.mpf(l+1))**2)*hb[l+1])
                  for l in range(NCHANNEL)])
        U=np.zeros((NCHANNEL,NCHANNEL),dtype=np.complex128)
        Ud=np.zeros_like(U)
        for r,wr in qnodes:
            vals=[coulomb_h(l,r) for l in range(NCHANNEL)]
            ht=np.array([complex(t) for t in vals])
            kr=(H*np.conj(ht)-np.conj(H)*ht)/(2j*float(k))
            dkr=(Hdot*np.conj(ht)-np.conj(Hdot)*ht)/(2j*float(k))
            V=full_potential_angular(r,P,mu,w)
            U+=wr*(kr[:,None]*(2*V)*ht[None,:])
            Ud+=wr*(dkr[:,None]*(2*V)*ht[None,:])
        # exact convention: U(B)=D(I+E), U'(B)=D'(I+Eprime)
        e=U/H[:,None]
        ep=Ud/Hdot[:,None]
        alpha=float(cert["selected_alpha_Jost_relative_error_upper"])
        q=float(cert["selected_q_strict_upper"])
        rel=np.linalg.solve(np.eye(NCHANNEL)+e,np.eye(NCHANNEL))
        zc=Hdot/H
        similarity_diff=zc[:,None]*((np.eye(NCHANNEL)+ep)@rel-np.eye(NCHANNEL))
        err_norm=np.linalg.norm(similarity_diff,ord=2)
        rn=np.linalg.norm(e,ord=2)
        dn=np.linalg.norm(ep,ord=2)
        eps_born=q*q/(1-q)
        return {
            "schema":"WU088_HH_PHYS46_NONCERT_FIRST_BORN_PREVIEW_V1",
            "status":"NONCERTIFYING_QUADRATURE",
            "original_source_sha256":cert["source_sha256"],
            "finite21_theorem_q_upper":cert["selected_q_strict_upper"],
            "finite21_theorem_relative_Jost_upper":cert["selected_alpha_Jost_relative_error_upper"],
            "rigorous_analytic_Born_second_order_remainder_weighted_upper":
                format(eps_born,".18g"),
            "radius_a0":[float(x) for x in radial_levels],
            "gauss_radial_nodes_each":[int(x) for x in grids],
            "gauss_angular_nodes":angular_nodes,
            "mpmath_dps":dps,
            "first_Born_normalized_U_B_matrix_spectral_norm":rn,
            "first_Born_normalized_dU_B_matrix_spectral_norm":dn,
            "first_Born_similarity_normalized_DtN_spectral_difference":float(err_norm),
            "observed_first_Born_norms_below_rigorous_full_Jost_bound":bool(max(rn,dn)<alpha),
            "Coulomb_z_reference_max_abs":float(np.max(np.abs(zc))),
            "exact_q_is_a_bound_not_numeric_result":True,
            "scientific_boundary":"not a full incoming-adjoint scattering rate and not a rigorous quadrature",
            "elapsed_s":perf_counter()-t0,
        }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--angular",type=int,default=192)
    p.add_argument("--dps",type=int,default=42)
    a=p.parse_args()
    out=first_born_preview(a.frozen,angular_nodes=a.angular,dps=a.dps)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out))
if __name__=="__main__":
    main()
