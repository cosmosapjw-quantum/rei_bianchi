"""Minimal coherence diagnostics for an isolated symmetric double passage.

These helpers do not upgrade the scoped Eq. (50) Markov transport into a
coherent multi-channel solver. They only quantify what is lost when one
crossing with single-pass probability p is traversed twice and the relative
phase is discarded. The phase argument absorbs dynamical and Stokes contributions.
"""
from __future__ import annotations
import math


def _p(x: float) -> float:
    p=float(x)
    if not math.isfinite(p) or not (0.0 <= p <= 1.0):
        raise ValueError("probability must be finite and in [0,1]")
    return p


def markov_double_pass_probability(p: float) -> float:
    """Off-diagonal population after two identical incoherent passages."""
    p=_p(p)
    return 2.0*p*(1.0-p)


def coherent_double_pass_probability(p: float, phase: float) -> float:
    """Two-path coherent envelope, 4 p(1-p) sin^2(total phase)."""
    p=_p(p);phi=float(phase)
    if not math.isfinite(phi):
        raise ValueError("phase must be finite")
    return 4.0*p*(1.0-p)*math.sin(phi)**2


def phase_averaged_double_pass_probability(p: float) -> float:
    """Uniform total-phase average of the coherent double-passage formula."""
    return markov_double_pass_probability(p)


def coherent_double_pass_envelope(p: float) -> tuple[float,float]:
    """Minimum/maximum coherent double-passage probability over phase."""
    p=_p(p)
    return 0.0,4.0*p*(1.0-p)


def phase_uncertainty_report(p: float) -> dict:
    """Bounded isolated-crossing phase-ignorance diagnostic.

    For a nontrivial passage the coherent probability ranges from zero to twice
    the phase-averaged/Markov result. The relative half-width about that mean is
    therefore unity. This statement must not be promoted to a five-branch
    network uncertainty without coherent S matrices and inter-branch phases.
    """
    p=_p(p);mean=markov_double_pass_probability(p);lo,hi=coherent_double_pass_envelope(p)
    rel=0.0 if mean==0.0 else (hi-lo)/(2.0*mean)
    return {
        "single_pass_probability":p,
        "markov_double_pass":mean,
        "phase_average":mean,
        "coherent_min":lo,
        "coherent_max":hi,
        "relative_half_width_about_markov":rel,
        "scope":"ISOLATED_SYMMETRIC_DOUBLE_PASS_ONLY_NOT_FULL_EQ50_NETWORK",
    }



def adiabatic_topological_phase() -> float:
    """Square-root hidden-crossing topological phase in the v->0 limit.

    Janev, Pop-Jordanov & Solov'ev (J. Phys. B 30, L353, 1997) give gamma=pi/2
    for a square-root branching point in the adiabatic limit.
    """
    return math.pi/2.0


def hidden_crossing_two_pass_probability(p: float, dynamical_phase: float, topological_phase: float | None = None) -> float:
    """Source-aligned two-pass hidden-crossing interference probability.

    P=4 p(1-p) cos^2(chi+gamma), with gamma=pi/2 by default in the
    adiabatic limit. This is still an isolated two-state formula, not the
    complete multi-branch ARSENY evolution matrix.
    """
    p=_p(p);chi=float(dynamical_phase)
    gamma=adiabatic_topological_phase() if topological_phase is None else float(topological_phase)
    if not math.isfinite(chi) or not math.isfinite(gamma):
        raise ValueError("phases must be finite")
    return 4.0*p*(1.0-p)*math.cos(chi+gamma)**2
