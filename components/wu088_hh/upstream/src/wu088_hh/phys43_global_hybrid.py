"""PHYS43: certified complete frozen annulus from signed/positive cells and PHYS38 cusp.

For the ORIGINAL fixed two-centre 21-partial-wave transformed screened PDE:
- Six actual IEEE-binary64 radial panel endpoints are represented EXACTLY.
- The two panels around r=R are cut at R-delta and R+delta; PHYS38
  independently certifies the whole intervening cusp collar, including
  the distinct actual dyadic panel switch and its extra right-side sliver.
- Outside that collar, every rational radial cell has an original-source
  positive angular Bernstein certificate (PHYS41). Selected panels also
  have a stronger candidate from PHYS42 signed joint (r,mu) interval cells.
  Taking the minimum of two *complete valid same-domain certificates*
  is sound. Neither signed nor numerical-preview samples are assumptions.
- PHYS38 five exact distributional interface jumps are then added in
  the FULL H0^1(annulus) dual, not confused with the physical h operator.

This does not certify r<r0, r>20, DtN, continuous inverse, scattering
amplitude or thermal rate. Native agents and local Codex are not used.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from math import factorial
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter
import hashlib
import json

from .phys33_residual import load_frozen,dyadic,ceil_sqrt_fixed
from .phys33_coupled_source import outward_decimal
from .phys33_full_coupled_shell import R,K2
from .phys33_panel_bernstein import radial_cuts,upper_exp_minus
from .phys33_cusp_strip import strip_certificate
from .phys42_joint_interval import (
    prepare_radial_panel,_radial_ranges,certify_cell,_alphas,
)

SCHEMA="WU088_HH_PHYS43_COMPLETE_ANNULUS_HYBRID_L2_HMINUS1_V1"
FROZEN_ID="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
PHYS38_JUMPS_ID="6760001d384dd39c7aab79a21f60ee78a96b36c0eed84402301787669a2f714d"


def positive_shell_square(radial:dict,a:F,b:F,digits:int=12)->tuple[F,F]:
    """Full angular strong PDE bound from exact radial Bernstein signed intervals.

    This is independent of the PHYS42 pointwise angular upper, valid on every
    positive radial tile, including near r=R (but caller uses PHYS38 there).
    """
    if not isinstance(a,F) or not isinstance(b,F) or not 0<a<b:
        raise ValueError("positive rational radial cell")
    if not 8<=digits<=18:raise ValueError("decimal precision 8..18")
    diag2=grad2=state2=F(0)
    for ell,(re,im) in enumerate(radial["terms"]):
        u0=re[0].absup()+im[0].absup()
        du=re[1].absup()+im[1].absup()
        nu=re[2].absup()+im[2].absup()
        L=F(ell*(ell+1))
        diag2+=(nu/a**3)**2
        grad2+=(du/a**2)**2+L*(u0/a**2)**2
        state2+=(u0/a)**2
    distance=(R-b if b<=R else a-R if a>=R else F(0))
    screen=upper_exp_minus(distance)
    p0=F(ceil_sqrt_fixed(diag2,digits))
    p1=F(ceil_sqrt_fixed(grad2,digits))
    p2=F(ceil_sqrt_fixed(state2,digits))
    # Same exact factorization and original U(s) as PHYS41.
    source_error=radial["source_error"].absup()
    source_tail=2*(1+K2)*upper_exp_minus(a+distance)
    shell=p0+source_error+2*screen*(p1+p2)+source_tail
    sq=shell**2*(b**3-a**3)/3
    return sq,shell


def original_panel_ranges(frozen:str|Path,delta:F)->tuple[list,dict]:
    if not isinstance(delta,F) or not F(0)<delta<F(1,10):
        raise ValueError("require exact positive delta smaller than 0.1 Bohr")
    rr,_,sha=load_frozen(frozen,True)
    bounds=[[dyadic(rr[j,0]),dyadic(rr[j,-1])] for j in range(6)]
    if sha!=FROZEN_ID or any(bounds[j][1]!=bounds[j+1][0] for j in range(5)):
        raise ArithmeticError("immutable frozen bytes or panel seams differ")
    left,right=R-delta,R+delta
    seam=bounds[1][1]
    if not (bounds[1][0]<left<seam<right<bounds[2][1]):
        raise ValueError("the physical cusp collar must straddle actual dyadic seam")
    clipped=[x.copy() for x in bounds]
    clipped[1][1]=left
    clipped[2][0]=right
    if any(not 0<a<b for a,b in clipped):
        raise ValueError("empty clipped panel")
    ranges=[(j,a,b) for j,(a,b) in enumerate(clipped)]
    covered=[(a,b,"panel"+str(j)) for j,a,b in ranges]
    covered.append((left,right,"PHYS38_cusp"))
    covered.sort(key=lambda t:t[0])
    if covered[0][0]!=bounds[0][0] or covered[-1][1]!=bounds[-1][1] or any(
        p[1]!=q[0] for p,q in zip(covered,covered[1:])
    ):
        raise ArithmeticError("cusp+regular exact radial coverage fails")
    info={"full_range":[str(bounds[0][0]),str(bounds[-1][1])],
          "actual_panel_edges":[[str(a),str(b)] for a,b in bounds],
          "actual_cusp_panel_seam":str(seam),
          "mathematical_cusp_R":str(R),
          "cusp_delta":str(delta),
          "cusp_range":[str(left),str(right)],
          "exact_cover":[[str(a),str(b),label] for a,b,label in covered]}
    return ranges,info


def cusp_graded_cuts(lo:F,hi:F,delta:F,near_right:bool,
                     pieces:int=8)->list[F]:
    """Union of original regular division with exact geometric cusp grading.

    The existing regular cuts are preserved. New cuts are always interior
    rationals and accumulate towards whichever edge abuts the cusp collar.
    This changes ONLY partitioning, never the original frozen radial field.
    """
    if not (0<lo<hi and delta>0 and 1<=pieces<=64):
        raise ValueError("positive rational ordered cusp tile")
    regular=radial_cuts(lo,hi,pieces,False)
    near=hi if near_right else lo
    grade=[near]
    step=delta
    for _ in range(72):
        nxt=(grade[-1]-step if near_right else grade[-1]+step)
        if not lo<nxt<hi:
            break
        grade.append(nxt)
        step*=F(3,2)
    else:
        raise ArithmeticError("unbounded cusp radial grading")
    cuts=sorted(set(regular+grade+[lo,hi]))
    if cuts[0]!=lo or cuts[-1]!=hi or any(a>=b for a,b in zip(cuts,cuts[1:])):
        raise ArithmeticError("invalid cusp radial cuts")
    return cuts


def _one_panel(job:tuple)->dict:
    filename,j,lo,hi,pieces,mu_bins,signed,digits,radial_strategy,delta=job
    start=perf_counter()
    prep=prepare_radial_panel(filename,j)
    if prep["source_sha256"]!=FROZEN_ID:
        raise ArithmeticError("worker source identity changed")
    if lo<prep["radial"][0] or hi>prep["radial"][1]:
        raise ArithmeticError("clip outside original dyadic panel")
    cuts=(cusp_graded_cuts(lo,hi,delta,near_right=(j==1),pieces=pieces)
          if radial_strategy=="cusp_graded" and j in (1,2)
          else radial_cuts(lo,hi,pieces,j==0))
    angular_cuts=tuple(-F(1)+F(2*i,mu_bins) for i in range(mu_bins+1))
    if angular_cuts[0]!=-1 or angular_cuts[-1]!=1:
        raise ArithmeticError("complete angular [-1,1] cover required")
    pos_total=signed_total=chosen_total=F(0)
    cells=[]
    for a,b in zip(cuts,cuts[1:]):
        radial=_radial_ranges(prep,a,b)
        pos_sq,shell=positive_shell_square(radial,a,b,digits)
        # Bound each squared tile outward at a fixed rational decimal BEFORE
        # aggregation. Different exact exp(-a) denominators would otherwise
        # accumulate thousands of digits across all six panels, an entirely
        # representational bottleneck, not a change in physics or tolerance.
        pos_sq=F(outward_decimal(pos_sq,24,True))
        signed_sq=None
        if signed:
            signed_sq=sum((certify_cell(prep,a,b,ma,mb,radial)["_sq_exact"]
                           for ma,mb in zip(angular_cuts,angular_cuts[1:])),F(0))
            signed_sq=F(outward_decimal(signed_sq,24,True))
        chosen_sq=min(pos_sq,signed_sq) if signed_sq is not None else pos_sq
        choice="signed" if signed_sq is not None and signed_sq<pos_sq else "positive"
        pos_total+=pos_sq
        if signed_sq is not None:signed_total+=signed_sq
        chosen_total+=chosen_sq
        cells.append({
            "radial":[str(a),str(b)],"chosen":choice,
            "positive_sq":str(pos_sq),
            "signed_sq":str(signed_sq) if signed_sq is not None else None,
            "chosen_sq":str(chosen_sq),
            "full_angular_coverage":"[-1,1] exact" if signed else "orthonormality full S2",
        })
    if cells[0]["radial"][0]!=str(lo) or cells[-1]["radial"][1]!=str(hi):
        raise ArithmeticError("panel part lost")
    if any(F(x["radial"][1])!=F(y["radial"][0])
           for x,y in zip(cells,cells[1:])):
        raise ArithmeticError("radial inner tiling gap")
    return {
        "panel":j,"clip_range":[str(lo),str(hi)],
        "source_sha256":prep["source_sha256"],
        "radial_cells":len(cells),"angular_mu_bins":mu_bins if signed else 0,
        "radial_strategy":radial_strategy,"radial_cuts_exact":[str(x) for x in cuts],
        "positive_sq_exact":str(pos_total),
        "signed_sq_exact":str(signed_total) if signed else None,
        "chosen_sq_exact":str(chosen_total),
        "chosen_L2_upper":ceil_sqrt_fixed(chosen_total,digits),
        "signed_selected_cells":sum(z["chosen"]=="signed" for z in cells),
        "cells":cells,"elapsed_s":perf_counter()-start,
    }


def global_hybrid(frozen:str|Path, cusp_parent:str|Path, interfaces:str|Path,
                  delta:F=F(1,100),pieces:tuple[int,...]=(8,16,16,8,8,8),
                  mu_bins:int=16,signed_panels:tuple[int,...]=(1,2),
                  workers:int=2,digits:int=12,
                  radial_strategy:str="uniform")->dict:
    if len(pieces)!=6 or any(type(x) is not int or not 1<=x<=64 for x in pieces):
        raise ValueError("six positive bounded regular-panel divisions required")
    if type(mu_bins) is not int or not 4<=mu_bins<=512:
        raise ValueError("bounded positive angular divisions required")
    if workers not in (1,2,3,4,6):
        raise ValueError("safe worker counts 1,2,3,4,6")
    if any(type(x) is not int or x not in range(6) for x in signed_panels):
        raise ValueError("signed panel selection must be actual integer panel IDs")
    if not 8<=digits<=18:raise ValueError("supported directed precision")
    if radial_strategy not in ("uniform","cusp_graded"):
        raise ValueError("radial strategy is uniform or cusp_graded")
    started=perf_counter()
    freeze=Path(frozen).read_bytes()
    if hashlib.sha256(freeze).hexdigest()!=FROZEN_ID:
        raise ValueError("immutable frozen source SHA mismatch")
    intervals,geo=original_panel_ranges(frozen,delta)
    cusp=strip_certificate(frozen,cusp_parent,delta,digits)
    if cusp["input_sha256"]!=FROZEN_ID or F(cusp["delta_a0"])!=delta:
        raise ArithmeticError("cusp physically wrong source or width")
    if cusp["actual_frozen_interface_rational"]!=geo["actual_cusp_panel_seam"]:
        raise ArithmeticError("PHYS38 cusp/dyadic interface mismatch")
    jumping_path=Path(interfaces)
    raw_jumps=jumping_path.read_bytes()
    if hashlib.sha256(raw_jumps).hexdigest()!=PHYS38_JUMPS_ID:
        raise ValueError("immutable PHYS38 interface certificate SHA mismatch")
    jumps=json.loads(raw_jumps)
    if jumps.get("schema")!="WU088_HH_PHYS38_ALL_INTERFACES_HMINUS1_V1":
        raise ValueError("five physical radial jump certificate required")
    if jumps.get("input_sha256")!=FROZEN_ID or len(jumps["interfaces"])!=5:
        raise ArithmeticError("wrong frozen source or missing interface distributions")
    if not all(v["field_value_jump_exact_zero"] for v in jumps["interfaces"]):
        raise ValueError("delta-prime distribution unsafe")
    original_edges=[[F(x),F(y)] for x,y in geo["actual_panel_edges"]]
    for i,row in enumerate(jumps["interfaces"],1):
        if row.get("interface")!=i or F(row["r_binary64_exact_rational"])!=original_edges[i-1][1]:
            raise ArithmeticError("original exact dyadic jump location misbound")
    jobs=[(str(frozen),j,a,b,pieces[j],mu_bins,j in signed_panels,digits,
           radial_strategy,delta)
          for j,a,b in intervals]
    if workers==1:
        panels=list(map(_one_panel,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            panels=list(pool.map(_one_panel,jobs))
    if [p["panel"] for p in panels]!=list(range(6)):
        raise ArithmeticError("lost panel or nondeterministic ordering")
    if any(p["source_sha256"]!=FROZEN_ID for p in panels):
        raise ArithmeticError("worker original source identity discrepancy")
    regular_sq=sum((F(p["chosen_sq_exact"]) for p in panels),F(0))
    cusp_up=F(cusp["total_3D_broken_strong_residual_L2_upper"])
    bulk=F(ceil_sqrt_fixed(regular_sq+cusp_up**2,digits))
    jump_up=F(jumps["full_broken_Laplacian_distribution_Hminus1_upper"])
    if jump_up<0:raise ArithmeticError("negative distributional norm")
    fullH1=outward_decimal(bulk+jump_up,digits,True)
    return {
        "schema":SCHEMA,
        "source_sha256":FROZEN_ID,
        "parent_PHYS38_cusp_sha256":hashlib.sha256(Path(cusp_parent).read_bytes()).hexdigest(),
        "parent_PHYS38_interface_sha256":hashlib.sha256(jumping_path.read_bytes()).hexdigest(),
        "radial_coverage":geo,
        "status":"CERTIFIED_TRUNCATED_ORIGINAL_ANNULUS_HMINUS1_NOT_OUTGOING",
        "test_function_space":"dual of full H0^1 annulus sqrt(L2^2+grad L2^2) with dimensionless a0",
        "original_hamiltonian":"h=-Delta/2-1/r-(1+1/s)exp(-2s), R=kappa=7/10, lambda=1",
        "frozen_trial_partial_waves":21,
        "radial_panels":panels,
        "regular_sq_exact":str(regular_sq),
        "cusp_log_strip_upper":str(cusp_up),
        "broken_strong_L2_upper":str(bulk),
        "five_interface_distribution_Hminus1_upper":str(jump_up),
        "complete_truncated_annulus_Hminus1_upper":fullH1,
        "previous_accepted_PHYS39_Hminus1_upper":"2.516921964597789440",
        "tighter_than_PHYS39":F(fullH1)<F("2.516921964597789440"),
        "settings":{"cusp_delta":str(delta),"pieces":list(pieces),
                    "mu_bins":mu_bins,"signed_panels":list(signed_panels),
                    "workers":workers,"digits":digits,
                    "radial_strategy":radial_strategy},
        "elapsed_s":perf_counter()-started,
        "not_certified":["physical origin r<r0","screened exterior r>20 DtN",
                         "continuous low Schur inverse","incoming adjoint",
                         "whole-space scattering intensity or HH thermal rate",
                         "consumer source/admission"],
    }
