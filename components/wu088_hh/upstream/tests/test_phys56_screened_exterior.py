from pathlib import Path

from wu088_hh.phys56_screened_exterior import (
    FROZEN_NPZ_SHA256,
    conditional_dtn_bound,
    operator_construction,
    scalar_feshbach_effective_q,
    scalar_schur_complement,
    conditional_hybrid_inverse_bound,
    schur_sign_diagnostic,
    screened_exterior_upper_bound,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
NPZ = ROOT / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_frozen_input_identity_and_exterior_decay():
    assert sha256_file(NPZ) == FROZEN_NPZ_SHA256
    assert screened_exterior_upper_bound(28.0) < screened_exterior_upper_bound(27.0)


def test_conditional_bound_marks_neumann_gate():
    valid = conditional_dtn_bound(1.0, 1.0, 1.0)
    assert valid.neumann_q_lt_one
    assert not valid.operator_constants_certified
    assert valid.upper_bound is not None
    invalid = conditional_dtn_bound(1.0, 1.0, 1.0e24)
    assert not invalid.neumann_q_lt_one
    assert invalid.upper_bound is None
    try:
        conditional_dtn_bound(float("nan"), 1.0, 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-finite norm constant must be rejected")


def test_feshbach_return_and_full_schur_are_retained():
    effective = scalar_feshbach_effective_q(0.2, 0.3, 0.4, 0.5, 0.6)
    assert effective != 0.5
    assert scalar_schur_complement(2.0, 3.0, 5.0, 11.0) == 3.5
    statement = operator_construction()
    assert "V_QP" in statement["pq_feshbach"]
    assert "Q-only" in statement["full_matching"]


def test_hybrid_inverse_formula_requires_actual_certificates():
    assert conditional_hybrid_inverse_bound(False, False)["status"] == "OPEN_MISSING_UNIFORM_TAIL_SIGN"
    assert conditional_hybrid_inverse_bound(True, False)["status"] == "OPEN_MISSING_FINITE_CURRENT_INTERVAL"
    empty = conditional_hybrid_inverse_bound(True, True)
    assert empty["bound"] == 1000.0 / 9.0
    diagnostic = schur_sign_diagnostic()
    assert diagnostic["imaginary_inverse_tail_positive"]
    assert diagnostic["imaginary_schur_negative"]
    assert diagnostic["diagnostic_bound_holds"]
