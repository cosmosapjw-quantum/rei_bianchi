from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class TermPoint:
    N: int
    l: int
    m: int
    R: float
    Z1: float
    Z2: float
    p: float
    separation_lambda: float
    energy_hartree: float
    residual_radial: float
    residual_angular: float
    iterations: int
    cf_depth: int

    @property
    def max_residual(self) -> float:
        return max(abs(self.residual_radial), abs(self.residual_angular))


def _validate_quantum_numbers(N: int, l: int, m: int) -> None:
    if N < 1:
        raise ValueError("N must be >= 1")
    if not (0 <= l < N):
        raise ValueError("require 0 <= l < N")
    if not (0 <= m <= l):
        raise ValueError("this real-term implementation uses m=|m| with 0 <= m <= l")


def energy_from_p(p: float, R: float) -> float:
    """E = -2 p^2 / R^2 in Hartree, from the primary two-center convention."""
    if p <= 0 or R <= 0:
        raise ValueError("p and R must be positive")
    return -2.0 * p * p / (R * R)


def p_from_energy(E_hartree: float, R: float) -> float:
    if E_hartree >= 0 or R <= 0:
        raise ValueError("bound-state energy must be negative and R positive")
    return math.sqrt(-2.0 * E_hartree) * R / 2.0


def united_atom_guess(N: int, l: int, m: int, R: float, Z1: float, Z2: float) -> tuple[float, float]:
    """Hydrogenic united-atom seed.

    This is the internally consistent R->0 limit:
        E -> -(Z1+Z2)^2/(2 N^2),
        lambda -> l(l+1)
    in the Solov'ev/Komarov convention used by the recurrences below.
    """
    _validate_quantum_numbers(N,l,m)
    if R <= 0 or Z1 <= 0 or Z2 <= 0:
        raise ValueError("R,Z1,Z2 must be positive")
    E0 = -(Z1 + Z2) ** 2 / (2.0 * N * N)
    return p_from_energy(E0, R), float(l * (l + 1))


def radial_coefficients(s: int, p: float, lam: float, *, Z1: float, Z2: float, R: float, m: int):
    """Jaffe quasi-radial three-term recurrence.

    Primary-source convention:
      a=(Z1+Z2)R,
      sigma=a/(2p)-m-1,

      alpha_s=(s+1)(s+m+1)
      beta_s=2s(s+2p-sigma)-(m+sigma)(m+1)-2p sigma+lambda
      gamma_s=(s-1-sigma)(s-1-m-sigma)
    """
    if p <= 0:
        raise ValueError("p must be positive")
    a = (Z1 + Z2) * R
    sigma = a / (2.0 * p) - m - 1.0
    alpha = (s + 1.0) * (s + m + 1.0)
    beta = (
        2.0 * s * (s + 2.0 * p - sigma)
        - (m + sigma) * (m + 1.0)
        - 2.0 * p * sigma
        + lam
    )
    gamma = (s - 1.0 - sigma) * (s - 1.0 - m - sigma)
    return alpha, beta, gamma


def angular_coefficients(s: int, p: float, lam: float, *, Z1: float, Z2: float, R: float, m: int):
    """Baber-Hasse quasi-angular three-term recurrence for Z1 != Z2.

      b=(Z2-Z1)R
      rho_s=(s+2m+1)[b-2p(s+m+1)]/[2(s+m)+3]
      chi_s=(s+m)(s+m+1)-lambda
      delta_s=s[b+2p(s+m)]/[2(s+m)-1]

    lambda is the primary-source convention, lambda -> l(l+1) as R->0.
    """
    if p <= 0:
        raise ValueError("p must be positive")
    b = (Z2 - Z1) * R
    rho = (s + 2.0*m + 1.0) * (b - 2.0*p*(s + m + 1.0)) / (2.0*(s + m) + 3.0)
    chi = (s + m) * (s + m + 1.0) - lam
    delta = 0.0 if s == 0 else s * (b + 2.0*p*(s + m)) / (2.0*(s + m) - 1.0)
    return rho, chi, delta


def _matched_cf_residual(n0: int, coeff_fn, p: float, lam: float, *,
                         Z1: float, Z2: float, R: float, m: int,
                         depth: int = 128) -> float:
    """Match finite low-s and minimal-solution high-s continued fractions.

    The low-s recurrence imposes y_{-1}=0.  The high-s tail selects the
    minimal solution.  For recurrence

       A_s y_{s+1} + B_s y_s + C_s y_{s-1}=0,

    the state-specific matching condition is

       F_low(n0) - A_n0 C_{n0+1}/F_high(n0+1) = 0.

    This is the sign-consistent form that also reduces directly to the
    ordinary D_infinity=0 condition at n0=0.
    """
    if depth <= n0 + 4:
        raise ValueError("continued-fraction depth too small")

    def c(s):
        return coeff_fn(s,p,lam,Z1=Z1,Z2=Z2,R=R,m=m)

    # finite continued fraction from y_-1=0 up to the node-count index n0
    _, low, _ = c(0)
    tiny = 1e-300
    for s in range(1, n0 + 1):
        Aprev, _, _ = c(s-1)
        _, B, C = c(s)
        if abs(low) < tiny:
            raise FloatingPointError("finite continued fraction hit a pole")
        low = B - C * Aprev / low

    # minimal-solution tail from large s downward
    _, high, _ = c(depth)
    for s in range(depth - 1, n0, -1):
        A, B, _ = c(s)
        _, _, Cnext = c(s+1)
        if abs(high) < tiny:
            raise FloatingPointError("continued-fraction tail hit a pole")
        high = B - A * Cnext / high

    A0, _, _ = c(n0)
    _, _, Cnext = c(n0+1)
    if abs(high) < tiny:
        raise FloatingPointError("continued-fraction tail hit a pole")
    return low - A0 * Cnext / high


def term_residuals(N: int, l: int, m: int, R: float, p: float, lam: float,
                   *, Z1: float = 1.0, Z2: float = 2.0, depth: int = 128) -> np.ndarray:
    _validate_quantum_numbers(N,l,m)
    if Z1 == Z2:
        raise NotImplementedError("R2 is scoped to the asymmetric Z1 != Z2 recurrence")
    n_xi = N - l - 1
    n_eta = l - m
    return np.array([
        _matched_cf_residual(n_xi, radial_coefficients, p, lam, Z1=Z1,Z2=Z2,R=R,m=m,depth=depth),
        _matched_cf_residual(n_eta, angular_coefficients, p, lam, Z1=Z1,Z2=Z2,R=R,m=m,depth=depth),
    ], dtype=float)


def _finite_difference_jacobian(fun, x: np.ndarray) -> np.ndarray:
    J = np.empty((2,2), dtype=float)
    for j in range(2):
        h = 1e-6 * max(abs(float(x[j])), 1.0)
        xp = x.copy()
        xm = x.copy()
        xp[j] += h
        xm[j] -= h
        if j == 0 and xm[j] <= 0:
            xm[j] = max(float(x[j]) * 0.5, 1e-12)
        fp = fun(xp)
        fm = fun(xm)
        J[:,j] = (fp - fm) / (xp[j] - xm[j])
    return J


def solve_real_term(N: int, l: int, m: int, R: float, *,
                    Z1: float = 1.0, Z2: float = 2.0,
                    p0: float | None = None,
                    lam0: float | None = None,
                    depth: int = 128,
                    tol: float = 1e-10,
                    max_iterations: int = 60) -> TermPoint:
    """Solve the real-R two-center bound-state term by damped Newton iteration.

    For arbitrary R a branch-preserving initial guess is required.  When p0
    and lam0 are omitted the united-atom seed is used and is intended for
    the first, sufficiently small-R point of a continuation.
    """
    _validate_quantum_numbers(N,l,m)
    if R <= 0:
        raise ValueError("R must be positive")
    if Z1 <= 0 or Z2 <= 0:
        raise ValueError("charges must be positive")
    if Z1 == Z2:
        raise NotImplementedError("symmetric b=0 recurrence is deferred to a later node")

    if p0 is None or lam0 is None:
        gp, gl = united_atom_guess(N,l,m,R,Z1,Z2)
        p0 = gp if p0 is None else p0
        lam0 = gl if lam0 is None else lam0

    x = np.array([float(p0), float(lam0)], dtype=float)

    def fun(xx):
        return term_residuals(N,l,m,R,float(xx[0]),float(xx[1]),Z1=Z1,Z2=Z2,depth=depth)

    for it in range(1, max_iterations + 1):
        f = fun(x)
        fnorm = float(np.max(np.abs(f)))
        if not np.isfinite(fnorm):
            raise RuntimeError("non-finite TERM residual")
        if fnorm <= tol:
            return TermPoint(
                N,l,m,R,Z1,Z2,float(x[0]),float(x[1]),
                energy_from_p(float(x[0]),R),float(f[0]),float(f[1]),it,depth
            )

        J = _finite_difference_jacobian(fun, x)
        try:
            dx = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError as exc:
            raise RuntimeError("singular Newton Jacobian") from exc

        accepted = False
        alpha = 1.0
        # Paper Eq. (32) uses a descending damping sequence if the functional
        # does not improve.  This reimplementation uses geometric halving.
        for _ in range(40):
            xn = x + alpha * dx
            if xn[0] <= 0 or not np.all(np.isfinite(xn)):
                alpha *= 0.5
                continue
            try:
                fn = fun(xn)
                new_norm = float(np.max(np.abs(fn)))
            except (FloatingPointError, OverflowError, ZeroDivisionError):
                alpha *= 0.5
                continue
            if np.isfinite(new_norm) and new_norm < fnorm:
                x = xn
                accepted = True
                break
            alpha *= 0.5

        if not accepted:
            raise RuntimeError(
                f"damped Newton failed to improve TERM functional at R={R}, "
                f"state={(N,l,m)}, residual={fnorm:.3e}"
            )

    f = fun(x)
    raise RuntimeError(
        f"TERM did not converge in {max_iterations} iterations; "
        f"state={(N,l,m)}, R={R}, residual={np.max(np.abs(f)):.3e}"
    )


def trace_real_curve(N: int, l: int, m: int, R_values: Iterable[float], *,
                     Z1: float = 1.0, Z2: float = 2.0,
                     depth: int = 128, tol: float = 1e-10,
                     predictor_rtol: float = 0.05,
                     min_step: float = 1e-5,
                     max_subdivisions: int = 24) -> list[TermPoint]:
    """Trace one united-atom-labelled real adiabatic branch by predictor-corrector continuation.

    R2 originally used only `p ~ R` scaling and a frozen previous lambda as the
    next Newton seed.  R3 adversarial validation exposed a root hop on the
    (N,l,m)=(3,2,0) branch near R~11 a0.  This patched implementation uses:

    1. a secant predictor in `(p, lambda)` whenever two previous points exist;
    2. the original constant-energy predictor for the first step;
    3. a correction-distance guard;
    4. automatic interval bisection if the corrected root is too far from the
       local predictor.

    The returned list contains only the user-requested R points.  Internal
    bisection points are continuation scaffolding and are not returned.
    """
    Rs = [float(r) for r in R_values]
    if not Rs or any(r <= 0 for r in Rs):
        raise ValueError("R_values must be a non-empty positive sequence")
    if any(Rs[i+1] <= Rs[i] for i in range(len(Rs)-1)):
        raise ValueError("R_values must be strictly increasing")
    if not (0.0 < predictor_rtol < 1.0):
        raise ValueError("predictor_rtol must lie in (0,1)")
    if min_step <= 0:
        raise ValueError("min_step must be positive")

    requested_out: list[TermPoint] = []
    history: list[TermPoint] = []

    first = solve_real_term(N,l,m,Rs[0],Z1=Z1,Z2=Z2,depth=depth,tol=tol)
    history.append(first)
    requested_out.append(first)

    def predictor(Rt: float) -> tuple[float,float]:
        prev = history[-1]
        if len(history) >= 2:
            a,b = history[-2], history[-1]
            dR = b.R-a.R
            f = (Rt-b.R)/dR
            p = b.p + f*(b.p-a.p)
            lam = b.separation_lambda + f*(b.separation_lambda-a.separation_lambda)
            if not math.isfinite(p) or p <= 0:
                p = b.p*Rt/b.R
            if not math.isfinite(lam):
                lam = b.separation_lambda
            return p,lam
        return prev.p*Rt/prev.R, prev.separation_lambda

    for requested_R in Rs[1:]:
        queue=[requested_R]
        subdivisions=0
        requested_point: TermPoint|None=None

        while queue:
            Rt=queue.pop(0)
            prev=history[-1]
            p_pred,lam_pred=predictor(Rt)

            cand=solve_real_term(
                N,l,m,Rt,Z1=Z1,Z2=Z2,
                p0=p_pred,lam0=lam_pred,
                depth=depth,tol=tol,max_iterations=80,
            )

            E_pred=energy_from_p(p_pred,Rt)
            correction_metric=max(
                abs(cand.p-p_pred)/max(abs(cand.p),abs(p_pred),1e-12),
                abs(cand.separation_lambda-lam_pred)/
                    max(abs(cand.separation_lambda),abs(lam_pred),1.0),
                abs(cand.energy_hartree-E_pred)/
                    max(abs(cand.energy_hartree),abs(E_pred),0.1),
            )

            interval=Rt-prev.R
            if (correction_metric > predictor_rtol and interval > min_step
                    and subdivisions < max_subdivisions):
                mid=0.5*(prev.R+Rt)
                queue.insert(0,Rt)
                queue.insert(0,mid)
                subdivisions += 1
                continue

            if correction_metric > predictor_rtol and interval <= min_step:
                raise RuntimeError(
                    "branch-continuation guard could not resolve a large "
                    f"predictor correction at R={Rt}; metric={correction_metric:.3e}"
                )
            if subdivisions >= max_subdivisions and correction_metric > predictor_rtol:
                raise RuntimeError(
                    "maximum continuation subdivisions exceeded before branch "
                    f"identity could be stabilized at R={Rt}"
                )

            history.append(cand)
            if abs(Rt-requested_R) <= 1e-13*max(1.0,abs(requested_R)):
                requested_point=cand

        if requested_point is None:
            raise RuntimeError("internal continuation error: requested point not reached")
        requested_out.append(requested_point)

    return requested_out
