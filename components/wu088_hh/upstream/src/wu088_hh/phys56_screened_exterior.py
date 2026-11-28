"""PHYS56: auditable algebra for the noncentral screened exterior.

This module deliberately does not discretize or replace the physical exterior.
It records the exact resolvent/Feshbach identities used by the PHYS56 proof
obligations and evaluates only scalar bounds whose hypotheses are explicit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import exp, isfinite
from pathlib import Path


FROZEN_NPZ_SHA256 = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
BOUNDARY_RADIUS_A0 = 27.0
DISPLACEMENT_A0 = 0.7
HYBRID_COLLAR_COERCIVITY = 9.0e-3
PHYS50_TRACE_BOUND = 4849.0 / 16800.0


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256, avoiding any interpretation of NPZ data."""
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def screened_exterior_upper_bound(radius_a0: float = BOUNDARY_RADIUS_A0) -> float:
    """Supremum bound for V=2(1+1/s)exp(-2s), s >= r - 0.7.

    This is a multiplication bound only.  It is not a DtN perturbation bound.
    """
    if radius_a0 <= DISPLACEMENT_A0:
        raise ValueError("exterior radius must exceed displaced-center radius")
    s_lower = radius_a0 - DISPLACEMENT_A0
    return 2.0 * (1.0 + 1.0 / s_lower) * exp(-2.0 * s_lower)


@dataclass(frozen=True)
class ConditionalDtnBound:
    """A bound conditional on independently established operator norms."""

    delta_v: float
    c_poisson_minus: float
    c_poisson_plus: float
    c_resolvent: float
    neumann_q: float
    neumann_q_lt_one: bool
    operator_constants_certified: bool
    upper_bound: float | None


def conditional_dtn_bound(
    c_poisson_minus: float, c_poisson_plus: float, c_resolvent: float
) -> ConditionalDtnBound:
    """Evaluate the Neumann-series implication, never certify its hypotheses.

    Assuming the weighted Coulomb LAP/Poisson estimates with these constants
    and q = c_resolvent * ||V||_infinity < 1, the formal implication is
    ||W^-1/2 (Z_S-Z_C) W^-1/2|| <= C_- C_+ ||V||/(1-q).
    """
    if not all(isfinite(value) and value >= 0.0 for value in (c_poisson_minus, c_poisson_plus, c_resolvent)):
        raise ValueError("operator-norm constants must be finite and nonnegative")
    delta_v = screened_exterior_upper_bound()
    q = c_resolvent * delta_v
    valid = q < 1.0
    return ConditionalDtnBound(
        delta_v, c_poisson_minus, c_poisson_plus, c_resolvent, q, valid, False,
        c_poisson_minus * c_poisson_plus * delta_v / (1.0 - q) if valid else None,
    )


def scalar_feshbach_effective_q(
    v_pp: complex, v_pq: complex, v_qp: complex, v_qq: complex, r_p: complex
) -> complex:
    """Scalar audit model of V_QQ+V_QP(I-R_P V_PP)^-1 R_P V_PQ.

    Its purpose is to make dropping the return coupling V_QP observably wrong.
    It is not a numerical model of the infinite-dimensional operator.
    """
    denominator = 1.0 - r_p * v_pp
    if denominator == 0.0:
        raise ZeroDivisionError("P-block Feshbach inverse is singular")
    return v_qq + v_qp * (r_p / denominator) * v_pq


def scalar_schur_complement(m_pp: complex, m_pq: complex, m_qp: complex, m_qq: complex) -> complex:
    """Return M_QQ-M_QP M_PP^-1 M_PQ for an invertible scalar P block."""
    if m_pp == 0.0:
        raise ZeroDivisionError("P-block Schur inverse is singular")
    return m_qq - m_qp * m_pq / m_pp


def conditional_hybrid_inverse_bound(
    tail_sign_certified: bool,
    low_block_empty: bool,
    normalized_current_lower: float | None = None,
    collar_coercivity: float = HYBRID_COLLAR_COERCIVITY,
    trace_bound: float = PHYS50_TRACE_BOUND,
) -> dict[str, object]:
    """Evaluate the PHYS56 Schur bound only after its certified inputs exist.

    For U=W^-1/2(Lambda_D,TT-Z_C)W^-1/2, a uniform tail certificate
    Re z_l <= 0 makes U_QQ c_D-accretive.  With b=||U_PQ|| and a
    finite-block Wronskian interval j_*>0, Schur factorization gives
    ||U^-1|| <= (1+b/c_D)^2 max(1/c_D,1/j_*).
    """
    if collar_coercivity <= 0.0 or trace_bound < 0.0:
        raise ValueError("coercivity must be positive and trace bound nonnegative")
    if low_block_empty:
        if not tail_sign_certified:
            return {"status": "OPEN_MISSING_UNIFORM_TAIL_SIGN"}
        return {
            "status": "CONDITIONAL_BOUND_READY_EMPTY_LOW_BLOCK",
            "bound": 1.0 / collar_coercivity,
            "required_certificates": ["uniform Re Z_C,l <= 0 for every ell>=21"],
        }
    if not tail_sign_certified:
        return {"status": "OPEN_MISSING_UNIFORM_TAIL_SIGN"}
    if normalized_current_lower is None or not isfinite(normalized_current_lower) or normalized_current_lower <= 0.0:
        return {"status": "OPEN_MISSING_FINITE_CURRENT_INTERVAL"}
    factor = (1.0 + trace_bound / collar_coercivity) ** 2
    return {
        "status": "CONDITIONAL_BOUND_READY",
        "bound": factor * max(1.0 / collar_coercivity, 1.0 / normalized_current_lower),
        "factor": factor,
        "required_certificates": [
            "uniform Re Z_C,l <= 0 on the full tail",
            "outward interval lower bound for finite exceptional normalized Wronskian current",
        ],
    }


def schur_sign_diagnostic() -> dict[str, float | bool]:
    """Small two-channel check of the Schur imaginary-part sign, not physics."""
    collar_pp, collar_qq, coupling = 0.109, 0.109, 0.05
    z_p, z_q = complex(0.109, 0.02), complex(-1.0 / 27.0, 0.001)
    d = collar_qq - z_q
    s = collar_pp - z_p - coupling * coupling / d
    determinant = (collar_pp - z_p) * d - coupling * coupling
    inverse_frobenius = ((abs(d) ** 2 + 2.0 * coupling**2 + abs(collar_pp-z_p) ** 2) ** 0.5) / abs(determinant)
    bound = conditional_hybrid_inverse_bound(True, False, 0.02)["bound"]
    return {
        "imaginary_inverse_tail_positive": (1.0 / d).imag > 0.0,
        "imaginary_schur_negative": s.imag <= -0.02,
        "inverse_frobenius": inverse_frobenius,
        "coarse_schur_bound": float(bound),
        "diagnostic_bound_holds": inverse_frobenius <= float(bound),
    }


def operator_construction() -> dict[str, object]:
    """Machine-readable statement of identities and unproved analytical gates."""
    return {
        "spaces": "H_{+a}=L2(e^{+2a(r-27)}dr dOmega), H_{-a}=L2(e^{-2a(r-27)}dr dOmega), 0<a<1; trace X with W_l=l+1",
        "resolvent_identity": "u_S=(I-R_C^+ V)^(-1) P_C^+ g",
        "dtn_identity": "Z_S-Z_C=(P_C^-)^* V (I-R_C^+ V)^(-1) P_C^+; (P_C^-)^* is the unweighted-volume-pairing dual transpose H_{+a}->X*",
        "sign_check": "with A_S=A_C-V and Z=+partial_r for u=r psi, Green identity gives the displayed plus DtN-difference formula",
        "pq_feshbach": "Veff_Q=V_QQ+V_QP(I-R_P V_PP)^(-1)R_P V_PQ; (Z_S)_QQ retains V_PQ and V_QP",
        "full_matching": "The physical r=27 match needs the full P+Q boundary operator; a Q-only collar does not prove it. If M_PP is invertible, use M_QQ-M_QP M_PP^(-1)M_PQ.",
        "axisymmetry": "The displaced z-axis potential preserves m, with the usual real-potential conjugation relation between m and -m; no angular coupling is discarded.",
        "hybrid_inverse_formula": "If a uniform tail sign and finite exceptional-current intervals are certified, ||M_hyb^-1|| <= (1+C_trace/c_D)^2 max(1/c_D,1/j_*); without them no numerical bound is admitted.",
        "required_unproved_gates": [
            "weighted outgoing Coulomb limiting absorption and Dirichlet resolvent domain",
            "weighted boundary Poisson bounds and the unweighted-volume-pairing dual-transpose trace bound",
            "invertibility or Fredholm/uniqueness for I-R_C^+ V and the P/Q Schur factors",
            "full low-block boundary matching and its Schur inverse",
            "certified constants before any numerical smallness claim",
        ],
    }


def result_payload(npz_path: Path) -> dict[str, object]:
    actual_sha = sha256_file(npz_path)
    example = conditional_dtn_bound(1.0, 1.0, 1.0)
    return {
        "status": "CONDITIONAL_OPERATOR_CONSTRUCTION_ONLY",
        "frozen_npz": str(npz_path),
        "frozen_npz_sha256_expected": FROZEN_NPZ_SHA256,
        "frozen_npz_sha256_actual": actual_sha,
        "frozen_npz_sha256_match": actual_sha == FROZEN_NPZ_SHA256,
        "screened_exterior_upper_bound": screened_exterior_upper_bound(),
        "conditional_unit_constant_example": asdict(example),
        "hybrid_inverse_quantification": {
            "current_status": conditional_hybrid_inverse_bound(False, False),
            "schur_sign_diagnostic": schur_sign_diagnostic(),
        },
        "operator_construction": operator_construction(),
        "not_claimed": [
            "a proved weighted norm for Z_S-Z_C",
            "a screened-exterior DtN existence or invertibility theorem",
            "a numerical inverse norm for the PHYS55 hybrid operator",
            "driven xi=Fy-phi, sigma(E), or Maxwellian k_HH(T)",
        ],
        "hh_r10": "OFF",
    }
