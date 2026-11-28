from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable

import numpy as np

from .term_complex import (
    BranchPointSolution,
    continue_complex_from_real,
    solve_branch_point,
    solve_complex_term,
)


State = tuple[int,int,int]


@dataclass(frozen=True)
class StueckelbergResult:
    state_a: State
    state_b: State
    rho: float
    branch_R: complex
    branch_X: complex
    contour_integral: complex
    delta: float
    panels: int
    cf_depth: int

    @property
    def probability_exponent_coefficient(self) -> float:
        """Eq. (55): P=exp[-2 Delta/v]."""
        return 2.0*self.delta


def _choose_sqrt(z: complex, *, previous: complex | None = None,
                 preferred_imag_sign: float = 1.0) -> complex:
    r=cmath.sqrt(z)
    choices=(r,-r)
    if previous is not None:
        return min(choices,key=lambda q:abs(q-previous))
    positive_real=[q for q in choices if q.real >= 0]
    if positive_real:
        return max(positive_real,key=lambda q:preferred_imag_sign*q.imag)
    return r


def branch_x(branch_R: complex, rho: float) -> complex:
    """X_c=sqrt(R_c^2-rho^2), with the sheet chosen continuously from Re X>0."""
    if rho < 0:
        raise ValueError("rho must be non-negative")
    Rc=complex(branch_R)
    Xc=cmath.sqrt(Rc*Rc-rho*rho)
    if Xc.imag*Rc.imag < 0:
        Xc=-Xc
    if Xc.real < 0:
        Xc=-Xc
    return Xc


def stueckelberg_probability(delta: float, velocity: float) -> float:
    """CPC Eq. (55), Q-series single-pass probability."""
    if delta < 0:
        raise ValueError("delta must be non-negative")
    if velocity <= 0:
        raise ValueError("velocity must be positive")
    return math.exp(-2.0*delta/velocity)


def order_hidden_crossings(branches: Iterable[BranchPointSolution]) -> list[BranchPointSolution]:
    """Paper Eq. (50)/(52) ordering convention: increasing Re R_c."""
    return sorted(branches,key=lambda b:(b.R.real,b.R.imag,b.series,b.state_a,b.state_b))


def stueckelberg_delta(state_a: State, state_b: State, R_seed: complex, *,
                      rho: float = 0.0,
                      Z1: float = 1.0, Z2: float = 2.0,
                      panels: int = 40,
                      depth: int = 96,
                      tol: float = 1e-9) -> StueckelbergResult:
    """Numerically evaluate the first form of CPC Eq. (56).

    Delta = | Im int_{Re X_c}^{X_c} DeltaE_beta,alpha(R(X)) dX |,
    X=sqrt(R^2-rho^2).

    The integration path is the vertical segment from the real X axis to X_c.
    A quadratic endpoint clustering t=1-(1-s)^2 resolves the square-root
    coalescence of the two sheets near the branch point.

    The endpoint itself is not fed to the singular individual-sheet Newton
    problem; DeltaE(X_c)=0 is imposed by the independently solved spectral
    coalescence condition.
    """
    if rho < 0:
        raise ValueError("rho must be non-negative")
    if panels < 8:
        raise ValueError("panels must be >= 8")

    bp=solve_branch_point(
        state_a,state_b,R_seed,Z1=Z1,Z2=Z2,depth=depth,tol=tol
    )
    Rc=bp.R
    Xc=branch_x(Rc,rho)
    x0=float(Xc.real)
    R0=math.sqrt(x0*x0+rho*rho)

    a=continue_complex_from_real(
        state_a,R0+0j,Z1=Z1,Z2=Z2,depth=depth,tol=tol
    )
    b=continue_complex_from_real(
        state_b,R0+0j,Z1=Z1,Z2=Z2,depth=depth,tol=tol
    )

    Xs: list[complex]=[]
    gaps: list[complex]=[]
    previous_R=complex(R0)

    for k in range(panels):
        s=k/panels
        t=1.0-(1.0-s)**2
        X=complex(x0,Xc.imag*t)
        R=_choose_sqrt(
            X*X+rho*rho,
            previous=previous_R,
            preferred_imag_sign=1.0 if Rc.imag>=0 else -1.0,
        )

        if k>0:
            a=solve_complex_term(
                state_a,R,Z1=Z1,Z2=Z2,p0=a.p,lam0=a.separation_lambda,
                depth=depth,tol=tol,max_iterations=100
            )
            b=solve_complex_term(
                state_b,R,Z1=Z1,Z2=Z2,p0=b.p,lam0=b.separation_lambda,
                depth=depth,tol=tol,max_iterations=100
            )

        Xs.append(X)
        gaps.append(b.energy_hartree-a.energy_hartree)
        previous_R=R

    Xs.append(Xc)
    gaps.append(0.0j)

    integral=0.0j
    for xa,xb,ga,gb in zip(Xs[:-1],Xs[1:],gaps[:-1],gaps[1:]):
        integral += 0.5*(ga+gb)*(xb-xa)

    return StueckelbergResult(
        state_a,state_b,rho,Rc,Xc,integral,abs(float(integral.imag)),panels,depth
    )
