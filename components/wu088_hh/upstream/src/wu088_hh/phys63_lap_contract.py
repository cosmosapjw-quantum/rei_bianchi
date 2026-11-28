"""Source checks for the PHYS63 literature-supported exterior LAP reduction.

These arithmetic checks do NOT prove a spectral theorem. The proof is in
REPORT_KO.md and explicitly invokes AIIS Condition 1.1, Corollary 1.6,
Theorem 1.7, and Corollaries 1.9/1.10. No numerical LAP norm is supplied.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib

B = F(27)
R = F(7, 10)
K = F(7, 10)
DELTA = F(3, 10**23)  # bound for radial V=2S, not Hamiltonian S
FROZEN_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"


def source_guard(path: str | Path) -> str:
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != FROZEN_SHA:
        raise ValueError("original frozen NPZ SHA256 mismatch")
    return digest


def exp_lower(x: F, order: int = 160) -> F:
    if not isinstance(x, F) or x < 0 or type(order) is not int or not 0 <= order <= 512:
        raise ValueError("nonnegative Fraction and integer order in 0..512 required")
    total = term = F(1)
    for n in range(1, order + 1):
        term *= x / n
        total += term
    return total


def weighted_screen_bound_s1() -> F:
    """sup (1+r²)*|2S| <= (1+B²)*delta, r measured in Bohr.

    d/dr[(1+r²)e^-2(r-B)] = -2(r²-r+1)e^-2(r-B)<0.
    Therefore this bounds multiplication L2_-1 -> L2_+1.
    """
    return (1 + B*B) * DELTA


def applicability(source: str | Path) -> dict:
    digest = source_guard(source)
    expo = 2 * (B - R)
    delta_upper = 2 * (1 + 1/(B-R)) / exp_lower(expo)
    assert delta_upper < DELTA
    assert R < B and F(1,5) < K*K/2 < F(3,10)
    # AIIS delta=1/2 gives kappa=delta/(1+2delta)=1/4.
    holder = F(1,8)
    assert 0 < holder < min(F(1,4), F(1)-F(1,2))
    return {
        "schema": "WU088_HH_PHYS63_LAP_APPLICABILITY_V1",
        "source_sha256": digest,
        "domain": "R^3 minus closed radius-27 ball, Dirichlet",
        "Hamiltonian": "h=-Delta/2-1/r-S; S=(1+1/s)exp(-2s); s=|x-0.7zhat|",
        "energy_Hartree": str(K*K/2),
        "radial_spectral_parameter": str(K*K),
        "compact_energy_interval_Hartree": ["1/5", "3/10"],
        "weight_s": 1,
        "literature_condition_delta": "1/2",
        "admissible_Holder_beta": str(holder),
        "long_range_weighted_gradient_bound": str(1+1/(B*B)),
        "radial_V_sup_bound": str(DELTA),
        "radial_V_L2minus1_to_L2plus1_bound": str(weighted_screen_bound_s1()),
        "positive_point_spectrum": "EMPTY_BY_AIIS_COR1.6_PLUS_VERIFIED_UCP",
        "threshold_set": [0],
        "literature_dependencies": {
            "paper": "Adachi-Itakura-Ito-Skibsted, arXiv:1804.07874v1",
            "hypotheses": ["Condition 1.1", "Condition 1.3"],
            "results": ["Corollary 1.6(2)", "Theorem 1.7", "Corollary 1.9", "Corollary 1.10"]
        },
        "scope": "REAL_AXIS_ALL_ANGULAR_QUALITATIVE_LAP_POISSON_DTN",
        "support": ["literature-supported", "derived"],
        "numerical_LAP_norm": None,
        "quantitative_Neumann_smallness": "NOT_CERTIFIED",
        "physical_full_source_solution": "NOT_COMPUTED",
        "HH_R10": "OFF"
    }


def conditional_neumann(source: str | Path, resolvent_bound: F | None) -> dict:
    """A distinct conditional numeric contract, not implied by qualitative LAP."""
    source_guard(source)
    if resolvent_bound is None:
        return {"status": "OPEN_NUMERICAL_RESOLVENT_CONSTANT", "q": None}
    if not isinstance(resolvent_bound, F) or resolvent_bound <= 0:
        raise ValueError("positive certified resolvent Fraction required")
    q = resolvent_bound * weighted_screen_bound_s1()
    return {"status": "CONDITIONAL_NEUMANN_LT_ONE" if q < 1 else "NEUMANN_SMALLNESS_NOT_ESTABLISHED",
            "q": str(q), "assumption": "supplied bound independently certified in L2_+1 -> L2_-1"}
