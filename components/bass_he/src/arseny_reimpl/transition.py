from __future__ import annotations
import math
import numpy as np

def hidden_crossing_probability(delta: float, velocity: float, exponent_factor: float = 1.0) -> float:
    """Exponential transition-probability helper.

    Paper Eq. (52) uses exp(-Delta/v) for an elementary crossing in the
    matrix formulation. Paper Eq. (55) writes a Q-series single-pass
    probability as exp(-2 Delta/v). The caller must therefore specify the
    appropriate exponent_factor from the derivation being reproduced.
    """
    if velocity <= 0:
        raise ValueError("velocity must be positive")
    if delta < 0:
        raise ValueError("delta must be non-negative")
    p = math.exp(-exponent_factor * delta / velocity)
    if not (0.0 <= p <= 1.0):
        raise ArithmeticError("transition probability left [0,1]")
    return p

def transition_block(jmax: int, i: int, j: int, p: float, *, absorbing_j: bool = False) -> np.ndarray:
    """Eq. (51)/(53)-style transition matrix, using 1-based state indices.

    For a bound-bound crossing:
        [[1-p, p],
         [p, 1-p]]

    If absorbing_j=True, the j-channel is treated as an ionization/upper-shell
    sink in the spirit of paper Eq. (53): population can flow i->j and does
    not flow back through this elementary block.
    """
    if not (1 <= i <= jmax and 1 <= j <= jmax and i != j):
        raise ValueError("invalid 1-based state indices")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0,1]")
    M = np.eye(jmax, dtype=float)
    a, b = i-1, j-1
    if not absorbing_j:
        M[a,a] = 1-p
        M[a,b] = p
        M[b,a] = p
        M[b,b] = 1-p
    else:
        M[a,a] = 1-p
        M[b,a] = p
        M[a,b] = 0.0
        M[b,b] = 1.0
    return M

def ordered_probability_matrix(jmax: int, crossings, prot=None) -> np.ndarray:
    """Compose the paper Eq. (50) ordering.

    P = P_kmax ... P_2 P_1 P_rot P_1 P_2 ... P_kmax

    `crossings` must be supplied in increasing crossing order as matrices.
    """
    I = np.eye(jmax, dtype=float)
    if prot is None:
        prot = I
    if prot.shape != (jmax,jmax):
        raise ValueError("P_rot shape mismatch")
    for M in crossings:
        if M.shape != (jmax,jmax):
            raise ValueError("crossing shape mismatch")
    left = I
    for M in reversed(crossings):
        left = left @ M
    right = I
    for M in crossings:
        right = right @ M
    return left @ prot @ right
