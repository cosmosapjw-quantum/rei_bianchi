#!/usr/bin/env python3
"""NONCERTIFYING finite m=0 high-ell nonzero trace screened DtN experiment.

Finite-difference independent test of the PHYS50 continuous all-ell
variational Dirichlet trace theorem. Uses true original screened S(s)
but manufactured prescribed boundary data, never original physical
outgoing or frozen exterior data.
"""
from __future__ import annotations
import argparse,json,time,sys,hashlib
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys50_trace_dtn import verified_high_trace_lifting,C_TRACE
from phys49_dirichlet_preview import angular_basis


def evaluate(frozen:Path,nrad:int=64,nmu:int=128,last_ell:int=28,repeats:int=24)->dict:
    if not 20<=nrad<=256 or not 64<=nmu<=512 or not 21<=last_ell<=40 or not 3<=repeats<=100:
        raise ValueError("bounded numeric original source problem")
    source=verified_high_trace_lifting(frozen)
    start=time.perf_counter()
    modes=np.arange(21,last_ell+1)
    nh=len(modes)
    dr=7/(nrad+1)
    radius=20+dr*np.arange(1,nrad+1)
    mu,w=np.polynomial.legendre.leggauss(nmu)
    P=angular_basis(mu,last_ell)
    P_H=P[:,21:last_ell+1]
    blocks=[]
    for r in radius:
        dist=np.sqrt(r*r+.7**2-2*.7*r*mu)
        screened=(1+1/dist)*np.exp(-2*dist)
        V=P_H.T @ ((w*screened/2)[:,None]*P_H)
        cent=modes*(modes+1)/r**2-2/r-.49
        blocks.append(sp.csr_matrix(np.diag(cent)-2*V))
    kinetic=sp.diags(
        [-np.ones(nrad-1)/dr**2,2*np.ones(nrad)/dr**2,
         -np.ones(nrad-1)/dr**2],[-1,0,1],format="csr"
    )
    A=sp.kron(kinetic,sp.eye(nh,format="csr"),format="csr") +sp.block_diag(blocks,format="csr")
    lu=spla.splu(A.tocsc())
    rhs=np.zeros((nrad*nh,2*nh))
    rhs[:nh,:nh]=np.eye(nh)/dr**2
    rhs[-nh:,nh:]=np.eye(nh)/dr**2
    x=lu.solve(rhs)
    flux=np.vstack([np.c_[np.eye(nh),np.zeros((nh,nh))],
                    np.c_[np.zeros((nh,nh)),np.eye(nh)]])/dr -np.vstack([x[:nh],x[-nh:]])/dr
    weights=np.r_[modes+1,modes+1].astype(float)
    weighted_flux=flux/np.sqrt(weights[:,None]*weights[None,:])
    evals=np.linalg.eigvalsh(weighted_flux)
    if np.min(evals)<=0 or np.max(evals)>float(C_TRACE):
        raise ArithmeticError("discretized DtN positivity or rigorous trace limit violated")
    if np.max(np.abs(flux-flux.T))>1e-10:
        raise ArithmeticError("original symmetric screened potential yields nonsymmetric DtN")
    b=np.zeros(2*nh)
    b[0]=1.
    b[nh]=.30
    b[5]=.15 if nh>5 else 0.
    if nh>5:b[nh+5]=-.05
    xg=x@b
    full=np.vstack([b[:nh],xg.reshape(nrad,nh),b[nh:]])
    egrad=np.sum(np.diff(full,axis=0)**2)/dr
    epot=dr*sum(np.dot(z,blocks[i]@z) for i,z in enumerate(full[1:-1]))
    e1=egrad+epot
    e2=b@flux@b
    gnorm2=weights@b**2
    if abs(e1-e2)>max(1e-12*abs(e2),1e-13):
        raise ArithmeticError("boundary flux/energy Green identity violated")
    if not 0<=e1<=float(C_TRACE)*gnorm2:
        raise ArithmeticError("positive measured DtN energy exceeds exact trace cap")
    l2norm=np.sqrt(dr*(xg@xg))
    gamma=float(source["trace_to_high_homogeneous_L2_gain_upper"])
    if l2norm>gamma*np.sqrt(gnorm2):
        raise ArithmeticError("nonzero trace numerical response exceeds source theorem")
    # Factorization reused, compare batched RHS to true scalar one-column solves.
    t=time.perf_counter()
    for _ in range(repeats):
        y=lu.solve(rhs)
    tb=(time.perf_counter()-t)/repeats
    t=time.perf_counter()
    for _ in range(repeats):
        zz=np.column_stack([lu.solve(rhs[:,i]) for i in range(2*nh)])
    ts=(time.perf_counter()-t)/repeats
    diff=np.max(np.abs(y-zz))
    if diff>1e-12:
        raise ArithmeticError("matched batch and sequential LU responses mismatch")
    return {
      "schema":"WU088_HH_PHYS50_NONCERTIFYING_ORIGINAL_SCREENED_FINITE_COLLAR_DTN_V1",
      "source_sha256":hashlib.sha256(frozen.read_bytes()).hexdigest(),
      "radial_grid_interiors":nrad,"angular_Gauss_nodes":nmu,"m":0,
      "ell_high_modes":modes.tolist(),
      "prescribed_B_T_g":"manufactured nonzero ell21 B=1 T=.3, ell26 B=.15 T=-.05",
      "radial_zero_Dirichlet_not_imposed":True,
      "weighted_trace_norm_sq":float(gnorm2),
      "discrete_DtN_eigen_min":float(evals[0]),
      "discrete_DtN_eigen_max":float(evals[-1]),
      "rigorous_all_ell_DtN_weighted_upper":str(C_TRACE),
      "measured_DtN_form":float(e2),
      "independent_radial_energy_form":float(e1),
      "energy_boundary_identity_abs_residual":float(abs(e1-e2)),
      "measured_high_L2":float(l2norm),
      "rigorous_trace_to_high_L2_upper_for_prescribed_g":float(gamma*np.sqrt(gnorm2)),
      "lu_batched_all_rhs_wall_s":tb,
      "lu_columnwise_all_rhs_wall_s":ts,
      "lu_batch_speedup":ts/tb,
      "matched_lu_rhs_max_difference":float(diff),
      "elapsed_s":time.perf_counter()-start,
      "status":"NUMERIC_NONCERTIFYING_TRACE_DTN_PREVIEW_ONLY_NO_OUTGOING_RATE"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--radial",type=int,default=64)
    p.add_argument("--angular",type=int,default=128)
    p.add_argument("--last-ell",type=int,default=28)
    p.add_argument("--repeats",type=int,default=24)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    v=evaluate(a.source,a.radial,a.angular,a.last_ell,a.repeats)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(v,indent=2)+"\n")
    print(json.dumps({k:v[k] for k in ("radial_grid_interiors",
      "discrete_DtN_eigen_max","rigorous_all_ell_DtN_weighted_upper",
      "measured_DtN_form","measured_high_L2","lu_batch_speedup","elapsed_s")}))
if __name__=="__main__":
    main()
