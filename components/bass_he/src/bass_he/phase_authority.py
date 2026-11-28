"""Source-bounded phase authority for hidden-crossing coherence work.

This module deliberately separates the *local* branch-point action used to
obtain a single-pass probability from the *complete reaction-path* real action
needed for coherent interference.  It does not turn the current Eq. (56)
Stueckelberg integral into a coherent phase by taking its real part.
"""
from __future__ import annotations
import math


def nuclear_momentum(M: float, common_term: float, electronic_term: float) -> float:
    """Janev-1997 style radial momentum for a real positive radicand."""
    M=float(M);A=float(common_term);U=float(electronic_term)
    if not all(math.isfinite(x) for x in (M,A,U)) or M<=0 or A-U<=0:
        raise ValueError("require finite M>0 and common_term-electronic_term>0")
    return math.sqrt(2.0*M*(A-U))


def exact_nuclear_momentum_difference(M: float, common_term: float,
                                      U_a: float, U_b: float) -> float:
    """Exact P_b-P_a, evaluated in a cancellation-resistant rationalized form."""
    pa=nuclear_momentum(M,common_term,U_a)
    pb=nuclear_momentum(M,common_term,U_b)
    return -2.0*float(M)*(float(U_b)-float(U_a))/(pb+pa)


def common_trajectory_linearized_difference(M: float, radial_momentum: float,
                                             delta_U: float) -> float:
    """Leading common-trajectory expansion: P_b-P_a ~= -M*DeltaU/P."""
    M=float(M);P=float(radial_momentum);dU=float(delta_U)
    if not all(math.isfinite(x) for x in (M,P,dU)) or M<=0 or P<=0:
        raise ValueError("require finite M>0 and radial_momentum>0")
    return -M*dU/P


def path_phase(real_path_action: float, net_branch_encircling: int,
               *, topological_phase: float=math.pi/2) -> float:
    """2015 path-phase convention phi + n*gamma for an amplitude exponent."""
    phi=float(real_path_action);gamma=float(topological_phase)
    if not math.isfinite(phi) or not math.isfinite(gamma):
        raise ValueError("finite phases required")
    if not isinstance(net_branch_encircling,int):
        raise ValueError("net_branch_encircling must be an integer")
    return phi+net_branch_encircling*gamma


def phase_authority_inventory() -> dict:
    """Current source-supported authority map for DR10B."""
    return {
        "local_branch_action_imaginary_part": {
            "single_pass_probability_authorized": True,
            "form": "p=exp(-2 Delta) with Delta=|Im local complex action|",
            "sources": ["Grozdanov-Solovev_PRA92_042701_2015",
                        "Janev-PopJordanov-Solovev_JPB30_L353_1997"],
        },
        "local_branch_action_real_part": {
            "full_interference_phase_authorized": False,
            "reason": "full coherent phase is defined on complete reaction paths, not the local branch segment alone",
        },
        "full_reaction_path_real_action": {
            "required_for_coherent_phase": True,
            "form": "phi^(k)=Re integral_C(k) E(t) dt (or nuclear-action equivalent)",
            "source": "Grozdanov-Solovev_PRA92_042701_2015",
        },
        "topological_phase": {
            "square_root_adiabatic_value": math.pi/2,
            "source": "Janev-PopJordanov-Solovev_JPB30_L353_1997",
            "finite_velocity_correction": "UNRESOLVED_IN_CURRENT_MODEL",
        },
        "common_trajectory_bridge": {
            "status": "DERIVED_LEADING_ORDER_ONLY",
            "identity": "P_b-P_a=-2M DeltaU/(P_b+P_a) -> -M DeltaU/P",
            "straight_line": "DeltaS ~= -(1/v) integral DeltaU dX",
            "does_not_supply_full_path_phase": True,
        },
    }
