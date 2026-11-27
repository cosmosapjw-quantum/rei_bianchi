#!/usr/bin/env python3
"""NONCERTIFYING original screened m=0 high-l Dirichlet collar finite differences.

Impose ZERO radial traces at r=20 and 27. This is an independent
numerical model of the PHYS49 mathematically coercive high-l block,
not physical Coulomb outgoing scattering or actual frozen r>20 data.
Input low source u_ell20(r)=sin(pi(r-20)/7) is explicitly MANUFACTURED.
"""
from __future__ import annotations

import argparse,json,sys
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys49_dirichlet_collar import high_l_dirichlet_collar


def angular_basis(mu:np.ndarray,lmax:int):
    leg=np.polynomial.legendre.legvander(mu,lmax)
    leg*=np.sqrt(2*np.arange(lmax+1)+1)[None,:]
    return leg


def screened_v(r:float,mu:np.ndarray,w:np.ndarray,P:np.ndarray,low:int,high:np.ndarray):
    rr=.7
    sep=np.sqrt(r*r+rr*rr-2*r*rr*mu)
    S=(1+1/sep)*np.exp(-2*sep)
    wh=w*S/2
    hp=P[:,high]
    V=hp.T @ (wh[:,None]*hp)
    source=hp.T @ (wh*P[:,low])
    return V,source


def run(frozen:Path,nrad:int=48,nmu:int=128,last_ell:int=28,skip_eigen:bool=False):
    if not 16<=nrad<=256 or not 64<=nmu<=512 or not 21<=last_ell<=40:
        raise ValueError("bounded original collar numerical diagnostic")
    t0=perf_counter()
    cert=high_l_dirichlet_collar(frozen,Ns=(0,),rhos=(4,),workers=1)
    dr=7/(nrad+1)
    r=20+dr*np.arange(1,nrad+1,dtype=float)
    high=np.arange(21,last_ell+1)
    nhigh=len(high)
    mu,w=np.polynomial.legendre.leggauss(nmu)
    P=angular_basis(mu,last_ell)
    native=np.sin(np.pi*(r-20)/7)
    phys_blocks=[]
    fblocks=[]
    max_symmetry=0.
    for ri,ui in zip(r,native):
        V,low_to_high=screened_v(ri,mu,w,P,20,high)
        max_symmetry=max(max_symmetry,np.max(np.abs(V-V.T)))
        diagonal=high*(high+1)/ri**2-2/ri-.49
        phys_blocks.append(sp.csr_matrix(np.diag(diagonal)-2*V))
        fblocks.append(2*low_to_high*ui)
    kinetic=sp.diags(
        [-np.ones(nrad-1)/dr**2,np.ones(nrad)*2/dr**2,-np.ones(nrad-1)/dr**2],
        [-1,0,1],format="csr"
    )
    A=sp.kron(kinetic,sp.eye(nhigh,format="csr"),format="csr")+sp.block_diag(phys_blocks,format="csr")
    f=np.concatenate(fblocks)
    tsolve=perf_counter()
    sol=sla.spsolve(A,f)
    solve_s=perf_counter()-tsolve
    rel=np.linalg.norm(sol)/np.linalg.norm(native)
    lam=None
    if not skip_eigen:
        lam=float(sla.eigsh(A,k=1,which="SA",tol=1e-11,return_eigenvectors=False)[0])
    residual=np.linalg.norm(A @ sol-f)/max(np.linalg.norm(f),1e-250)
    cap=float(cert["whole_high_response_gain_to_low_u_P_upper"])
    if not rel<cap:
        raise ArithmeticError("finite-difference high source exceeds continuous theory threshold")
    return {
        "schema":"WU088_HH_PHYS49_NONCERT_FINITE_DIFFERENCE_COLLAR_V1",
        "source_sha256":cert["original_source_sha256"],
        "radial_domain_a0":[20,27],
        "dirichlet_high_traces":["u_high(20)=0","u_high(27)=0"],
        "manufactured_low_input":"ell=20, u20=sin(pi*(r-20)/7), NOT original frozen physical extension",
        "n_radial_interiors":nrad,"mu_nodes":nmu,
        "high_partial_waves":high.tolist(),
        "scoped_analytic_infinite_ell_dirichlet_gain_upper":cert["whole_high_response_gain_to_low_u_P_upper"],
        "numerical_conditional_u_high_over_u_low_L2":float(rel),
        "numerical_min_discretized_high_block_eigenvalue":lam,
        "certified_continuum_eigenvalue_floor":cert["unperturbed_high_Dirichlet_eigen_floor_exact"],
        "finite_system_relative_linear_residual":float(residual),
        "numerical_matrix_max_asymmetry":float(max_symmetry),
        "solve_wall_s":solve_s,
        "elapsed_s":perf_counter()-t0,
        "NOT_CERTIFYING":"finite-dimensional m0 and radial FD, original screened potential, manufactured low source; no physical incoming/outgoing boundary and no actual rate",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--radial",type=int,default=48)
    p.add_argument("--angular",type=int,default=128)
    p.add_argument("--last-ell",type=int,default=28)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=run(a.source,a.radial,a.angular,a.last_ell)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("n_radial_interiors","mu_nodes","high_partial_waves","numerical_min_discretized_high_block_eigenvalue","numerical_conditional_u_high_over_u_low_L2","scoped_analytic_infinite_ell_dirichlet_gain_upper","elapsed_s")}))
if __name__=="__main__":main()
