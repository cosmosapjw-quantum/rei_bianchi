from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from rate_interval_model import (  # noqa: E402
    MYR_S,
    RateInterval,
    alpha_b_hii,
    beta_hi,
    derive_positive_interval,
    family_attenuation_inverse,
    hydrogen_cooling_coefficients,
    macro_process_evidence,
)


def test_atomic_rate_functions_match_canonical_reference() -> None:
    assert math.isclose(alpha_b_hii(14500.0), 1.891474204735125e-13, rel_tol=2e-15)
    assert math.isclose(beta_hi(14500.0), 1.3191161555118136e-13, rel_tol=2e-15)
    coeff = hydrogen_cooling_coefficients(14500.0)
    assert math.isclose(coeff["excitation"], 1.5497171645045767e-22, rel_tol=2e-15)


def test_interval_uses_positive_evidence_without_arbitrary_expansion() -> None:
    interval = derive_positive_interval(
        family="M",
        estimates_myr_inv={"secant": 0.02, "start": 0.01, "end": 0.04},
        endpoint_changed=True,
        dt_myr=10.0,
        identifiability="PHYSICAL",
    )
    assert interval.k_min_myr_inv == 0.01
    assert interval.k_max_myr_inv == 0.04
    assert interval.status == "IDENTIFIED_INTERVAL"


def test_changing_endpoint_without_positive_rate_fails_identifiability() -> None:
    interval = derive_positive_interval(
        family="J_G1",
        estimates_myr_inv={"secant": 0.0, "absorption": 0.0},
        endpoint_changed=True,
        dt_myr=10.0,
        identifiability="NUISANCE",
    )
    assert interval.status == "UNIDENTIFIABLE_REQUIRED_RATE"
    assert not interval.usable


def test_constant_endpoint_can_use_dynamically_irrelevant_reference() -> None:
    interval = derive_positive_interval(
        family="U",
        estimates_myr_inv={"secant": 0.0},
        endpoint_changed=False,
        dt_myr=8.0,
        identifiability="PHYSICAL",
    )
    assert interval.status == "DYNAMICALLY_IRRELEVANT"
    assert interval.k_min_myr_inv == interval.k_max_myr_inv == 0.125


def test_attenuation_inverse_decreases_with_rate() -> None:
    slow = family_attenuation_inverse(0.01, 10.0)
    fast = family_attenuation_inverse(0.1, 10.0)
    assert slow > fast > 1.0


def test_macro_process_evidence_is_dimensionally_consistent() -> None:
    mass = np.array([2.0e64, 3.0e64])
    x = np.array([0.8, 0.9])
    t = np.array([1.0e4, 1.5e4])
    nh = np.array([1.0e-3, 2.0e-3])
    capacity = np.array([2.0e48, 4.0e48])
    current = np.array([[4.0e47, 2.0e47], [6.0e47, 3.0e47]])
    phi = np.array([1.0e52, 5.0e51])
    transfer_pos = np.array([1.0e46, 2.0e46])
    transfer_neg = np.zeros(2)
    evidence = macro_process_evidence(
        mass=mass,
        x_hii=x,
        temperature_k=t,
        n_h_cm3=nh,
        capacity=capacity,
        current=current,
        phi=phi,
        transfer_positive=transfer_pos,
        transfer_negative=transfer_neg,
        z=5.9,
        transfer_x_hii=1.0,
        transfer_temperature_k=1.3e4,
    )
    for key in ("M", "I", "U", "C", "J_G1", "J_G2a"):
        assert math.isfinite(evidence[key])
        assert evidence[key] >= 0.0
    assert math.isclose(evidence["M"], (3.0e46 / 5.0e64) * MYR_S, rel_tol=2e-15)
