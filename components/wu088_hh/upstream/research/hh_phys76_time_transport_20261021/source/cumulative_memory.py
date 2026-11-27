"""All-node Simpson attribution of signed shear on an immutable saved path.

Inputs follow the PR128 ``stress_memory.py`` contract: x = ln(a),
S = sqrt(3)*s/H and P_A = sqrt(3)*(8*pi*G/c**2)*p_A/H**2 in one
orthonormal normal frame, with sigma = diag(-s,-s,2*s), A = m,r.
Time is the last axis; every other axis labels independent saved trajectories.

The final node uses the same composite Simpson quadrature as PR128 in real
arithmetic.  A local recurrence evaluates all nodes in O(number_of_samples)
work per trajectory, without constructing a globally growing integrating
factor.  At odd nodes the three-point Simpson primitive uses ONE FUTURE
SAMPLE and one negative weight.  This is offline sampled-data attribution,
not a causal time stepper, a positivity rule, or a continuum error bound.

The output retains signed species contributions.  Only after summing signed
components do we take a norm; Frobenius magnitudes are sqrt(2) times the
half-contraction magnitudes.  No input is modified and no ODE is integrated.
"""
from __future__ import annotations

import numpy as np


def _validated_arrays(x, H, S, Pm, Pr):
    if any(np.iscomplexobj(v) for v in (x, H, S, Pm, Pr)):
        raise ValueError("REAL_INPUTS_REQUIRED")
    try:
        x = np.asarray(x, dtype=np.float64)
        values = [np.asarray(v, dtype=np.float64) for v in (H, S, Pm, Pr)]
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("REAL_NUMERIC_INPUTS_REQUIRED") from exc
    if x.ndim != 1 or x.size < 3 or x.size % 2 != 1 or not np.isfinite(x).all():
        raise ValueError("GRID_REQUIRES_ODD_FINITE_1D_SAMPLES")
    with np.errstate(over="ignore", invalid="ignore"):
        steps = np.diff(x)
        h = (x[-1] - x[0]) / (x.size - 1)
    if (not np.isfinite(h) or h <= 0 or not np.isfinite(steps).all()
            or np.any(steps <= 0)
            or not np.allclose(steps, h, rtol=2e-12, atol=0)):
        raise ValueError("GRID_REQUIRES_UNIFORM_INCREASING_COORDINATE")
    shape = values[0].shape
    if not shape or shape[-1] != x.size or any(v.shape != shape for v in values):
        raise ValueError("SAME_CASE_AND_TIME_SHAPE_REQUIRED")
    if any(not np.isfinite(v).all() for v in values) or np.any(values[0] <= 0):
        raise ValueError("FINITE_INPUTS_AND_POSITIVE_H_REQUIRED")
    return x, float(h), values


def cumulative_memory_budget(x, H, shear_signed, pi_m_signed, pi_r_signed):
    """Return same-trajectory matter/radiation memory at every saved node.

    All five inputs have the PR128 contract; H, shear and the two stresses
    must have identical shape ``(..., len(x))``.  x must be odd-length,
    finite, uniform and increasing.  Returned arrays have that same shape.

    With T_ij = exp(3*(x_i-x_j) + log(H_i)-log(H_j)), each adjacent pair
    advances the even-node composite Simpson integral.  The intervening odd
    node is the integral of the local quadratic interpolant through the
    pair's three samples, so it can depend on its right-hand neighbour.

    ``closure_defect`` and ``closure_scaled_defect`` compare the sampled
    reconstruction with the supplied saved shear.  They include sampling
    and upstream trajectory errors and are diagnostics only.  The function
    does not change the coupled trajectory or perform species-off runs.

    Underflow of a damped transport/contribution is permitted.  Overflow,
    invalid floating arithmetic or nonfinite output raises FloatingPointError;
    no clipping, tolerance relaxation, or silent infinity is returned.
    """
    x, h, (H, S, Pm, Pr) = _validated_arrays(
        x, H, shear_signed, pi_m_signed, pi_r_signed
    )
    # One leading species axis makes the recurrence vectorized over both
    # species and every case axis, while the time dependence remains ordered.
    sources = np.stack((Pm, Pr), axis=0)
    memory = np.zeros_like(sources)
    initial = np.empty_like(S)
    initial[..., 0] = S[..., 0]

    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            log_H = np.log(H)

            def transport(i, j):
                return np.exp(3.0 * (x[i] - x[j]) + log_H[..., i] - log_H[..., j])

            for k in range(2, x.size, 2):
                t01 = transport(k - 2, k - 1)
                t12 = transport(k - 1, k)
                t02 = transport(k - 2, k)
                t21 = transport(k, k - 1)
                initial[..., k - 1] = t01 * initial[..., k - 2]
                initial[..., k] = t12 * initial[..., k - 1]
                # Even nodes: unchanged composite Simpson quadrature.
                memory[..., k] = (
                    t02 * memory[..., k - 2]
                    + (h / 3.0) * t02 * sources[..., k - 2]
                    + (4.0 * h / 3.0) * t12 * sources[..., k - 1]
                    + (h / 3.0) * sources[..., k]
                )
                # Odd nodes: offline quadratic primitive; the last term has
                # a negative coefficient and consumes the next saved sample.
                memory[..., k - 1] = (
                    t01 * memory[..., k - 2]
                    + (5.0 * h / 12.0) * t01 * sources[..., k - 2]
                    + (8.0 * h / 12.0) * sources[..., k - 1]
                    - (h / 12.0) * t21 * sources[..., k]
                )

            matter, radiation = memory[0], memory[1]
            total_memory = matter + radiation
            predicted = initial + total_memory
            defect = S - predicted

            # Scaled ratios avoid overflow in a sum of individually finite
            # magnitudes.  Their values are the PR128 ratios in real arithmetic.
            scale_max = np.maximum.reduce((np.abs(initial), np.abs(matter),
                                           np.abs(radiation), np.abs(S)))
            scaled = [np.divide(np.abs(v), scale_max, out=np.zeros_like(S),
                                where=scale_max > 0)
                      for v in (initial, matter, radiation, S)]
            scaled_defect = np.divide(np.abs(defect), scale_max,
                                      out=np.zeros_like(S), where=scale_max > 0)
            scaled_sum = sum(scaled)
            relative = np.divide(scaled_defect, scaled_sum,
                                 out=np.zeros_like(S), where=scaled_sum > 0)

            stress_max = np.maximum(np.abs(matter), np.abs(radiation))
            m_scaled = np.divide(matter, stress_max, out=np.zeros_like(S),
                                 where=stress_max > 0)
            r_scaled = np.divide(radiation, stress_max, out=np.zeros_like(S),
                                 where=stress_max > 0)
            subtotal_scaled = np.abs(m_scaled) + np.abs(r_scaled)
            cancellation = 1.0 - np.divide(
                np.abs(m_scaled + r_scaled), subtotal_scaled,
                out=np.ones_like(S), where=subtotal_scaled > 0
            )
            root2 = np.sqrt(2.0)
            total_pi = Pm + Pr
            result = {
                "initial_memory": initial,
                "matter_memory": matter,
                "radiation_memory": radiation,
                "predicted_signed_shear": predicted,
                "observed_signed_shear": S.copy(),
                "closure_defect": defect,
                "closure_scaled_defect": relative,
                "stress_memory_cancellation": cancellation,
                "has_stress_memory": stress_max > 0,
                "Sigma_half": np.abs(S),
                "Sigma_F": root2 * np.abs(S),
                "predicted_Sigma_half": np.abs(predicted),
                "predicted_Sigma_F": root2 * np.abs(predicted),
                "Pi_m_half": np.abs(Pm),
                "Pi_r_half": np.abs(Pr),
                "Pi_total_half": np.abs(total_pi),
                "Pi_m_F": root2 * np.abs(Pm),
                "Pi_r_F": root2 * np.abs(Pr),
                "Pi_total_F": root2 * np.abs(total_pi),
                "signed_Sigma_F": root2 * S,
                "signed_Pi_m_F": root2 * Pm,
                "signed_Pi_r_F": root2 * Pr,
                "stress_memory_total_F": root2 * np.abs(total_memory),
            }
    except FloatingPointError as exc:
        raise FloatingPointError("NONFINITE_MEMORY_ARITHMETIC") from exc
    if any(not np.isfinite(value).all() for value in result.values()):
        raise FloatingPointError("NONFINITE_MEMORY_OUTPUT")
    return result
