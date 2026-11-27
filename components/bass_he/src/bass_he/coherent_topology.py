"""Same-system source formulas used to audit the scoped Eq. (50) topology.

The formulas are from Janev, Pop-Jordanov & Solov'ev,
J. Phys. B 30, L353-L360 (1997), Eqs. (14)-(15), for the
He2+ + H / H+ + He+ system. They are audit helpers, not a
coherent multi-branch solver.

For Eq. (15), relative_phase means chi2' - chi1' - 2 gamma after
factoring out exp[i(chi1'+gamma)] from the two-path amplitude.
"""
from __future__ import annotations
import math


def _prob(x: float, name: str) -> float:
    y=float(x)
    if not math.isfinite(y) or not (0.0 <= y <= 1.0):
        raise ValueError(f"{name} must be finite and in [0,1]")
    return y


def janev97_eq14_2ppi_probability(p23: float, p12: float, pS23: float,
                                   p_2ppi_3dpi: float,
                                   p_rot_sigma_pi: float) -> float:
    """Source Eq. (14): forward 2p-sigma -> 2p-pi probability."""
    p23=_prob(p23,"p23");p12=_prob(p12,"p12");s=_prob(pS23,"pS23")
    pm=_prob(p_2ppi_3dpi,"p_2ppi_3dpi");r=_prob(p_rot_sigma_pi,"p_rot_sigma_pi")
    return (1.0-p23)*(1.0-p12)*(1.0-s)*(1.0-pm)*r


def janev97_eq15_2psigma_coherent_probability(p12: float, p23: float,
                                                pS23: float,
                                                p_rot_sigma_pi: float,
                                                relative_phase: float) -> float:
    """Source Eq. (15) rewritten with one total relative phase.

    The source bracket is
      exp[i(chi1'+gamma)]
      +(1-pS)*sqrt(1-p_rot)*exp[i(chi2'-gamma)].
    """
    a=_prob(p12,"p12");t=_prob(p23,"p23");s=_prob(pS23,"pS23")
    r=_prob(p_rot_sigma_pi,"p_rot_sigma_pi")
    phi=float(relative_phase)
    if not math.isfinite(phi):
        raise ValueError("relative_phase must be finite")
    A=(1.0-s)*math.sqrt(1.0-r)
    return a*(1.0-a)*(1.0-t)*(1.0+A*A+2.0*A*math.cos(phi))


def janev97_eq15_2psigma_phase_average(p12: float, p23: float,
                                        pS23: float,
                                        p_rot_sigma_pi: float) -> float:
    """Uniform relative-phase average of source Eq. (15)."""
    a=_prob(p12,"p12");t=_prob(p23,"p23");s=_prob(pS23,"pS23")
    r=_prob(p_rot_sigma_pi,"p_rot_sigma_pi")
    return a*(1.0-a)*(1.0-t)*(1.0+(1.0-s)**2*(1.0-r))
