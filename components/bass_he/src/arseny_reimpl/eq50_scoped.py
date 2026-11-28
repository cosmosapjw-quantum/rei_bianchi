"""Scoped CPC Eq. (50)-(53) assembly for the five published Nmax=3 HeH2+ branches.

PAPER_DERIVED_REIMPLEMENTATION.
NOT AUTHOR CODE.

DR7 intentionally separates two printed probability conventions:
- Eq. (52): p_k = exp[-Delta_k(rho)/v] inside the support cutoff.
- Eq. (55): P^Q = exp[-2 Delta/v] for the Q-series single-pass probability.

The paper prints both. DR7 does not silently identify them. The Eq. (50)
matrix lane follows Eq. (52) literally and also reports the Eq. (55)
diagnostic for every active branch.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from .cross_section import projectile_velocity_au
from .rotational import full_rotational_probability
from .state_index import state_index
from .stueckelberg import stueckelberg_delta
from .transition import transition_block, ordered_probability_matrix

State = tuple[int,int,int]

@dataclass(frozen=True)
class ScopedBranch:
    name: str
    state_a: State
    state_b: State
    R: complex
    itype: int
    @property
    def series(self) -> str:
        return "Q" if self.itype == 10 else "S" if self.itype == 20 else "OTHER"
    @property
    def support_cutoff(self) -> float:
        if self.R.imag < 0:
            raise ValueError("upper-half-plane branch representative required")
        return float(self.R.real + self.R.imag)

BRANCHES_NMAX3 = (
    ScopedBranch("Q12",(1,0,0),(2,1,0),complex(1.212587527786,1.363819821336),10),
    ScopedBranch("Q23",(2,1,0),(3,2,0),complex(6.067211554151,3.145266138016),10),
    ScopedBranch("Qother",(2,0,0),(3,1,0),complex(0.8059222651175,2.256231739782),10),
    ScopedBranch("Qm1",(2,1,1),(3,2,1),complex(3.404752979836,3.537601421347),10),
    ScopedBranch("S23",(2,1,0),(3,1,0),complex(0.5002386252692,0.7522845045231),20),
)

def ordered_scoped_branches() -> tuple[ScopedBranch,...]:
    return tuple(sorted(BRANCHES_NMAX3,key=lambda b:(b.R.real,b.R.imag,b.name)))

def eq52_support(branch: ScopedBranch, rho: float) -> bool:
    if rho < 0: raise ValueError("rho must be non-negative")
    return rho <= branch.support_cutoff

def branch_state_indices(branch: ScopedBranch) -> tuple[int,int]:
    return state_index(*branch.state_a), state_index(*branch.state_b)

def branch_probability_record(branch: ScopedBranch, energy_keV_per_amu: float, rho: float, *,
                              panels: int = 80, depth: int = 96, tol: float = 1e-9) -> dict:
    v=projectile_velocity_au(energy_keV_per_amu)
    active=eq52_support(branch,rho)
    out={
        "name":branch.name,"series":branch.series,
        "state_a":branch.state_a,"state_b":branch.state_b,
        "state_indices":branch_state_indices(branch),
        "R":[branch.R.real,branch.R.imag],
        "support_cutoff":branch.support_cutoff,"active":active,
        "velocity_au":v,"delta":None,
        "p_eq52_literal":0.0,"p_eq55_singlepass":0.0,"eq55_minus_eq52":0.0,
    }
    if not active: return out
    st=stueckelberg_delta(branch.state_a,branch.state_b,branch.R,
                         rho=rho,panels=panels,depth=depth,tol=tol)
    delta=float(st.delta)
    p52=math.exp(-delta/v)
    p55=math.exp(-2.0*delta/v)
    if abs(p55-p52*p52) > 5e-14:
        raise ArithmeticError("Eq55/Eq52 exponential relation lost")
    out.update(delta=delta,p_eq52_literal=p52,p_eq55_singlepass=p55,
               eq55_minus_eq52=p55-p52)
    return out

def _branch_matrix(branch: ScopedBranch, p: float, Nmax: int) -> np.ndarray:
    jmax=state_index(Nmax,Nmax-1,Nmax-1)
    i,j=branch_state_indices(branch)
    if max(branch.state_a[0],branch.state_b[0]) > Nmax:
        raise ValueError("branch outside requested basis")
    absorbing = branch.state_b[0] == Nmax
    return transition_block(jmax,i,j,p,absorbing_j=absorbing)

def assemble_scoped_eq50(Nmax: int, energy_keV_per_amu: float, rho: float, *,
                         panels: int = 80, rotation_steps: int = 512,
                         depth: int = 96, tol: float = 1e-9,
                         exponent_policy: str = "eq52_literal") -> dict:
    if Nmax != 3:
        raise NotImplementedError("DR7 scoped assembler is frozen to Nmax=3")
    if exponent_policy not in ("eq52_literal","eq55_diagnostic"):
        raise ValueError("unknown exponent policy")
    if rho < 0: raise ValueError("rho must be non-negative")
    v=projectile_velocity_au(energy_keV_per_amu)
    prot=full_rotational_probability(Nmax,energy_keV_per_amu,rho,steps=rotation_steps)
    details=[]; crossing_matrices=[]
    for branch in ordered_scoped_branches():
        rec=branch_probability_record(branch,energy_keV_per_amu,rho,panels=panels,depth=depth,tol=tol)
        p=rec["p_eq52_literal"] if exponent_policy=="eq52_literal" else rec["p_eq55_singlepass"]
        rec["p_used"]=p
        rec["absorbing_upper_shell"]=(branch.state_b[0]==Nmax)
        details.append(rec)
        crossing_matrices.append(_branch_matrix(branch,p,Nmax))
    P=ordered_probability_matrix(prot.shape[0],crossing_matrices,prot)
    col_def=float(np.max(np.abs(P.sum(axis=0)-1.0)))
    minp=float(P.min()); maxp=float(P.max())
    if col_def > 2e-11: raise ArithmeticError(f"Eq50 stochasticity failed: {col_def}")
    if minp < -2e-13 or maxp > 1+2e-12:
        raise ArithmeticError(f"Eq50 range failed: {minp},{maxp}")
    return {
        "Nmax":Nmax,"energy_keV_per_amu":float(energy_keV_per_amu),
        "velocity_au":v,"rho":float(rho),"panels":int(panels),
        "rotation_steps":int(rotation_steps),"exponent_policy":exponent_policy,
        "claim":("SCOPED_PRINTED_EQ50_EQ52_LITERAL_ASSEMBLY_NOT_AUTHOR_CR_SECTION_IDENTITY"
                 if exponent_policy=="eq52_literal"
                 else "SOURCE_FACTOR_TWO_DIAGNOSTIC_ONLY_NOT_AUTHOR_ASSEMBLY"),
        "branch_order":[d["name"] for d in details],
        "active_branches":[d["name"] for d in details if d["active"]],
        "branch_details":details,"P_rot":prot,"P_total":P,
        "column_stochastic_defect":col_def,"min_probability":minp,"max_probability":maxp,
    }
