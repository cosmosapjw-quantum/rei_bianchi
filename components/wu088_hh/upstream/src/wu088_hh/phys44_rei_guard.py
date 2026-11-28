"""PHYS44 read-only provider-consumer check for rei_bianchi HH.

Two DIFFERENT lanes remain distinct:
(a) PHYS43 microscopic frozen spectator scattering, no physical cross section;
(b) earlier PHYS19 FT03/LCS conditional source response with an effective
    HH ionization coefficient. Do not replace k_HH by a raw raw sigma*v
    without the identical-pair coefficient convention.
This module never writes, loads, or starts a rei_bianchi production solver.
"""
from __future__ import annotations

from decimal import Decimal as D, localcontext
from pathlib import Path
import hashlib
import json
import re
import subprocess

COVERAGE_REL="rust/rei_microphysics/src/coverage.rs"
SOURCE_REL="rust/rei_microphysics/src/axbi_sources.rs"
FT03_REL="rust/rei_microphysics/src/ft03_controlled.rs"
LCS_REL=("research/r31ao_unequal_ladder/"
         "hh_phys19_parameter_curvature_theory_20261013_v1/contracts/"
         "NEXT_CONSUMER_CONTRACT.json")
FROZEN_ID="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SCHEMA="WU088_HH_PHYS44_REI_CONSUMER_GUARD_V1"


def _sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _extract_constant(src:str,name:str)->str:
    m=re.search(r'pub const '+re.escape(name)+r':\s*&str\s*=\s*"([^"]+)";',src)
    if not m:raise ValueError("missing original source identity "+name)
    return m.group(1)


def _git_head(repo:Path)->str:
    res=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],
                       capture_output=True,text=True,check=True)
    return res.stdout.strip()


def read_rei_guard(rei_repo:str|Path,wu_repo:str|Path)->dict:
    """Read ORIGINAL actual local sources only; never mutate consumer checkout."""
    rei=Path(rei_repo);wu=Path(wu_repo)
    coverage=rei/COVERAGE_REL
    axbi=rei/SOURCE_REL
    ft03=rei/FT03_REL
    contract=wu/LCS_REL
    for p in (coverage,axbi,ft03,contract):
        if not p.is_file():raise FileNotFoundError(str(p))
    covsrc=coverage.read_text()
    axsrc=axbi.read_text()
    ftsrc=ft03.read_text()
    if ('"HH_R10"' not in covsrc
            or 'NO_EXTERNAL_PHYSICAL_SOURCE_ADMITTED' not in covsrc
            or 'MissingAuthority' not in covsrc):
        raise ValueError("repo consumer missing known fail-closed HH coverage guard")
    d=json.loads(contract.read_bytes())
    if d["schema"]!="WU088_HH_PHYS20_CONSUMER_SOURCE_CONTRACT_V1":
        raise ValueError("expected actual previous conditional HH provider contract")
    if d["consumer_binding"]["status"]!="unverified":
        raise ValueError("prior consumer binding status changed; fresh science intake needed")
    srcid=_extract_constant(axsrc,"SOURCE_ID")
    modelid=_extract_constant(ftsrc,"FT03_MODEL_ID")
    # Distinguish conditionally reused FT03 benchmark from AX08 solver dynamics.
    return {
        "schema":SCHEMA,
        "local_rei_head_read_only":_git_head(rei),
        "local_wu_head_read_only":_git_head(wu),
        "consumer_source_identity":srcid,
        "separate_ft03_model_identity":modelid,
        "provider_PHYS19_contract_sha256":_sha(contract),
        "consumer_coverage_sha256":_sha(coverage),
        "consumer_axbi_source_sha256":_sha(axbi),
        "consumer_ft03_source_sha256":_sha(ft03),
        "consumer_actual_existing_HH_R10_excluded":True,
        "consumer_actual_require_physical_source_fails_closed":True,
        "selected_candidate":"AXBI signed conditional zbar20..4 (NOT a PHYS19 matching fixed-COMMON interval)",
        "provider_physics_distinct":{
            "PHYS19_LCS":"conditional named-interval thermal/electron response",
            "PHYS43_Coulomb":"source-locked annulus residual only, physical scattering rate absent",
        },
        "missing_for_FT03_HH_production":[
            "named adopted physical source interval with exact source/input identity and proper seconds",
            "admitted positive k_HH(T) with the identical-pair convention and measured thermal support",
            "verified same-frame proper n_H, state fractions, electron/thermal energy normalization",
            "source ownership avoiding double counting existing H/He collisional ionization",
            "matched source/closure/birth/geometry, H/He state and time history transfer gate",
            "PHYS43 microscopic continuum inverse+adjoint+cross section if microscopic lane is selected",
        ],
        "rate_table_status":"NOT_AVAILABLE_FROM_BOUND_SOURCES",
        "actual_HH_source_response":"NOT_EVALUATED",
        "physical_rate_admission":"HOLD",
        "rei_mutations":0,
    }


def ft03_manufactured_response(
    *,nH_cm3:str,xHII:str,yHeII:str,yHeIII:str,nHe_over_nH:str,
    w_eV_per_H:str,kHHeffective_cm3_s:str,kB_eV_K:str,chiH_eV:str,
    lambda_switch:str="1",unit_test_only:bool=False
)->dict:
    """Check algebra/units on an EXPLICITLY SYNTHETIC FT03 LCS state.

    kHHeffective is the *already identical-pair convention aligned*
    effective collision coefficient in the PHYS19 source contract.
    This never measures or infers a microscopic physical rate.
    """
    if unit_test_only is not True:
        raise PermissionError("NO_ADMITTED_RATE_PROVIDER: manufactured contract only")
    with localcontext() as ctx:
        ctx.prec=75
        nH,x,y,z,fhat,w,k,kB,chi,lam=[
          D(v) for v in (nH_cm3,xHII,yHeII,yHeIII,
                          nHe_over_nH,w_eV_per_H,kHHeffective_cm3_s,
                          kB_eV_K,chiH_eV,lambda_switch)]
        if not all(c.is_finite() for c in (nH,x,y,z,fhat,w,k,kB,chi,lam)):
            raise ValueError("all model-test inputs must be finite")
        if (nH<=0 or k<0 or kB<=0 or chi<=0 or fhat<0 or w<0 or
            not (0<=x<=1 and 0<=y<=1 and 0<=z<=1 and y+z<=1)
            or not 0<=lam<=1):
            raise ValueError("invalid manufactured FT03 physical-domain factors")
        e=x+fhat*(y+2*z)
        Pi=D(1)+fhat+e
        Ct=D(2)/(D(3)*kB)
        T=Ct*w/Pi
        q=lam*nH*(1-x)**2*k
        dot_e=q
        dot_ne=nH*q
        dot_w=-chi*q
        dot_T=-(Ct*chi+T)*q/Pi
        # Independently apply the exact kinetic temperature Jacobian.
        check_T=(Ct*dot_w-T*dot_e)/Pi
        # The symbolic identity is exact, but Decimal arithmetic rounds
        # intermediate products at a finite user-selected precision.
        tol=D("1e-70")*max(D(1),abs(dot_T),abs(check_T))
        if abs(dot_T-check_T)>tol:
            raise ArithmeticError("manufactured thermal source Jacobian inconsistent")
        return {
            "schema":"WU088_HH_PHYS44_FT03_MANUFACTURED_ONLY_V1",
            "synthetic":True,"admitted":False,
            "kHH_definition":"effective PHYS19 per-H coefficient, identical-pair factor already absorbed",
            "T_K":str(T),
            "nH_cm3":str(nH),"e_electron_per_H":str(e),
            "Pi_particle_per_H":str(Pi),
            "q_HH_per_H_s":str(q),
            "dot_T_HH_K_per_s":str(dot_T),
            "dot_e_HH_per_H_s":str(dot_e),
            "dot_ne_HH_cm3_s":str(dot_ne),
            "dot_w_HH_eV_per_H_s":str(dot_w),
            "thermal_jacobian_decimal_consistency":True,
            "physical_application":"PROHIBITED_WITHOUT_NAMED_RATE_AND_ADOPTED_INTERVAL"
        }
