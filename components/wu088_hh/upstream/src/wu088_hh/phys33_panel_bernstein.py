"""PHYS41: rigorous *entire six-panel* screened broken-bulk L2 enclosure.

The original 21 angular modes and all 1386 binary64 source values are unmodified.
For every radial rational tile, exact Lagrange interpolation is transformed to
Bernstein form.  Convex hull gives exact coefficient suprema, including at the
spectator sphere r=R, without evaluating an ill-defined direction n(s=0).

This is deliberately a whole-volume but possibly loose certificate. It does
NOT bind radial interface delta sheets, the origin below r0, the exterior,
a continuous outgoing inverse, or any HH cross section.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter
import hashlib

from .phys33_residual import (
    load_frozen, dyadic, interpolants, reconstruct, value,
    derivative, ceil_sqrt_fixed, mul, add, scale,
)
from .phys33_full_coupled_shell import R, K2, _center_exp
from .phys33_coupled_source import outward_decimal

L_MAX = 20
SCHEMA = "WU088_HH_PHYS41_FULL_SIX_PANEL_SCREENED_BULK_V1"


@lru_cache(maxsize=128)
def _bernstein_transform(x0: F, x1: F, n: int) -> tuple[tuple[F, ...], ...]:
    """Exact cached monomial-to-Bernstein matrix for one tile and degree.

    Shares a single rational transform between all 21 complex modes on the
    tile instead of redundantly rebuilding binomial/power sums.
    """
    if x0 >= x1 or n < 0:
        raise ValueError("invalid Bernstein tile")
    dx=x1-x0
    rows=[]
    for k in range(n+1):
        row=[]
        for j in range(n+1):
            row.append(sum((F(comb(j,i)*comb(k,i),comb(n,i)) *
                            x0**(j-i)*dx**i
                            for i in range(min(k,j)+1)),F(0)))
        rows.append(tuple(row))
    return tuple(rows)


def bernstein_sup(coeff: list[F], x0: F, x1: F) -> F:
    """Exact rational convex-hull bound on |sum c_j*x^j| for x in [x0,x1].

    The cached matrix directly converts any polynomial's power coefficients
    to Bernstein coefficients on the requested tile. Zero padding the
    polynomial is deliberately excluded from caching for exact degree.
    """
    if not (isinstance(x0,F) and isinstance(x1,F) and x0<x1):
        raise ValueError("strict rational interval required")
    if not coeff:
        raise ValueError("nonempty polynomial required")
    rows=_bernstein_transform(x0,x1,len(coeff)-1)
    return max(abs(sum((c*w for c,w in zip(coeff,row)),F(0)))
               for row in rows)


def radial_cuts(lo: F, hi: F, pieces: int, first: bool) -> list[F]:
    """Exact positive partition, geometrically graded next to the origin."""
    if not (F(0) < lo < hi and 1 <= pieces <= 64):
        raise ValueError("positive exact panel and 1..64 pieces required")
    if not first:
        return [lo + (hi-lo)*F(k, pieces) for k in range(pieces+1)]
    # Use a 3:2 rational growth; no floating root finding or hidden gaps.
    cuts = [lo]
    while cuts[-1] * F(3, 2) < hi:
        cuts.append(cuts[-1] * F(3, 2))
        if len(cuts) > 512:
            raise ArithmeticError("origin grading runaway")
    return cuts + [hi]


def upper_exp_minus(x: F, terms: int = 24) -> F:
    """Rigorous 0<exp(-x)<=1/sum_{k=0}^N x^k/k! for x>=0."""
    if x < 0 or terms < 1:
        raise ValueError("nonnegative x and positive polynomial degree")
    return F(1) / sum((x**k/F(factorial(k)) for k in range(terms+1)), F(0))


def source_numerator_polynomial(a: F, b: F, mid: F, half: F,
                                order: int = 24) -> tuple[list[F], F]:
    """Enclose r^3*2(1+k²)e^-r in exact power basis of panel x.

    exp(-a) has certified midpoint+error; exp(-(r-a)) is a Taylor
    polynomial with an explicitly bounded nonnegative remainder. The
    second output bounds the resulting error *after division by r^3*.
    """
    if not F(0)<a<b or order<8:
        raise ValueError("positive source tile and Taylor degree")
    c,ec=_center_exp(a,192)
    t=[mid-a,half]  # r-a as polynomial in original physical panel x
    tp=[F(1)]
    e_poly=[F(1)]
    for k in range(1,order+1):
        tp=mul(tp,t)
        e_poly=add(e_poly,scale(tp,F((-1)**k,factorial(k))))
    rp=[mid,half]
    r3=mul(mul(rp,rp),rp)
    matched=scale(mul(r3,e_poly),2*(1+K2)*c)
    w=b-a
    max_taylor=sum((w**k/F(factorial(k)) for k in range(order+1)),F(0))
    exp_error=ec*max_taylor+abs(c)*w**(order+1)/F(factorial(order+1))
    # r^3 was factored EXACTLY, so it cancels in the source error.
    # Applying a b^3/a^3 factor here is valid but needlessly inflates
    # near-origin bounds by many orders of magnitude.
    normalized_error=2*(1+K2)*exp_error
    return matched,normalized_error


def panel_certificate(filename: str | Path, j: int, pieces: int = 6,
                      digits: int = 12) -> dict:
    if j not in range(6) or not 8 <= digits <= 18:
        raise ValueError("panel 0..5 and 8..18 digits")
    started = perf_counter()
    rr, uu, digest = load_frozen(filename, pinned=True)
    radii = [dyadic(v) for v in rr[j]]
    lo, hi = radii[0], radii[-1]
    mid, half = (lo + hi)/2, (hi-lo)/2
    xs = [(r-mid)/half for r in radii]
    basis = interpolants(xs)  # build ONCE per panel, share among 42 mode components
    coeffs = []
    verified = 0
    for ell in range(L_MAX+1):
        real, imag = reconstruct(uu[ell,j], basis)
        for z,x in zip(uu[ell,j],xs):
            if value(real,x) != dyadic(z.real) or value(imag,x) != dyadic(z.imag):
                raise ArithmeticError("original frozen node reconstruction mismatch")
            verified += 1
        components = []
        rp=[mid,half]
        r2=mul(rp,rp)
        L=F(ell*(ell+1))
        potential=add(add(scale(r2,K2),scale(rp,F(2))),[-L])
        for p in (real,imag):
            first = [v/half for v in derivative(p)]
            second = [v/half for v in derivative(first)]
            # r^2 D_l u and r u' - u preserve large radial cancellations.
            nu=add(mul(r2,second),mul(potential,p))
            ru_minus_u=add(mul(rp,first),scale(p,F(-1)))
            components.append((p,ru_minus_u,nu))
        coeffs.append(components)
    cuts = radial_cuts(lo,hi,pieces,j==0)
    cells = []
    norm2 = F(0)
    for a,b in zip(cuts,cuts[1:]):
        xa,xb = (a-mid)/half,(b-mid)/half
        matched_source,source_error=source_numerator_polynomial(a,b,mid,half)
        diag_sq = grad_sq = state_sq = F(0)
        for ell, parts in enumerate(coeffs):
            # (u, r*u'-u, r²*D_l*u), each with exact real/imag coefficients.
            u0=sum((bernstein_sup(parts[c][0],xa,xb)
                    for c in (0,1)),F(0))
            ur=sum((bernstein_sup(parts[c][1],xa,xb)
                    for c in (0,1)),F(0))
            nu_re=parts[0][2]
            if ell==0:
                nu_re=add(nu_re,scale(matched_source,F(-1)))
            nu=(bernstein_sup(nu_re,xa,xb)+
                bernstein_sup(parts[1][2],xa,xb))
            L=F(ell*(ell+1))
            d=nu/a**3
            g=ur/a**2
            diag_sq+=d**2
            grad_sq+=g**2+L*(u0/a**2)**2
            state_sq+=(u0/a)**2
        # The l=0 Coulomb radial source is cancelled BEFORE taking norms.
        # G=(A-S0)-2E ∂_sB-2UB+S0(1-exp(-E)).
        # |U|<=E, |∂_sB|<=|grad B|, 1-exp(-E)<=E, E<=exp(-|r-R|).
        # The angular Legendre factors are normalized orthogonally.
        distance = R-b if b<=R else (a-R if a>=R else F(0))
        screened=upper_exp_minus(distance)
        qd=F(ceil_sqrt_fixed(diag_sq,digits))
        qg=F(ceil_sqrt_fixed(grad_sq,digits))
        qb=F(ceil_sqrt_fixed(state_sq,digits))
        correction=2*(1+K2)*upper_exp_minus(a+distance)
        q=qd+source_error+2*screened*(qg+qb)+correction
        vol=(b**3-a**3)/3  # physical r^2 dr, no 4pi for normalized Y_l0
        l2up=F(ceil_sqrt_fixed(q*q*vol,digits))
        norm2+=l2up**2
        cells.append({
            "radial_interval_a0":[str(a),str(b)],
            "angular_L2_uniform_upper":outward_decimal(q,digits,True),
            "volume_weight_exact":str(vol),
            "volume_L2_upper":str(l2up),
        })
    bound=ceil_sqrt_fixed(norm2,digits)
    return {
        "panel":j,"radial_interval_a0":[str(lo),str(hi)],
        "source_sha256":digest,"actual_input_complex_values_checked":verified,
        "Bernstein_basis_degree":10,"exact_rational_cuts":[str(x) for x in cuts],
        "cell_count":len(cells),"volume_L2_upper":bound,"cells":cells,
        "elapsed_s":perf_counter()-started,
    }


def whole_panel_certificate(filename: str | Path, pieces: int = 6,
                            workers: int = 1, digits: int = 12) -> dict:
    if workers not in (1,2,3,4,6):
        raise ValueError("supported safe 1,2,3,4,6 process counts")
    if not isinstance(pieces,int) or isinstance(pieces,bool) or not 1<=pieces<=64:
        raise ValueError("pieces must be 1..64")
    start=perf_counter()
    data=Path(filename).read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    # Each worker independently re-verifies original byte identity. Result
    # order and exact rational reduction are independent of worker schedule.
    jobs=[(str(filename),j,pieces,digits) for j in range(6)]
    if workers==1:
        panels=[panel_certificate(*job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            panels=list(pool.map(_panel_job,jobs))
    if any(p["source_sha256"]!=sha for p in panels):
        raise ArithmeticError("mixed frozen source files")
    if any(F(panels[j]["radial_interval_a0"][1]) !=
           F(panels[j+1]["radial_interval_a0"][0]) for j in range(5)):
        raise ArithmeticError("radial panel coverage has a gap")
    total=ceil_sqrt_fixed(sum((F(p["volume_L2_upper"])**2 for p in panels),F(0)),digits)
    return {
        "schema":SCHEMA,
        "input_sha256":sha,
        "physical_domain_a0":[panels[0]["radial_interval_a0"][0],
                              panels[-1]["radial_interval_a0"][1]],
        "same_original_model":"lambda=1,R=kappa=7/10,21 modes,6 panels",
        "scope":"full all-angle broken strong transformed PDE residual only",
        "certified_broken_strong_L2_upper":total,
        "certified_full_H1_dual_bulk_upper":total,
        "full_H1_test_norm":"sqrt(L2(v)^2 + L2(grad(v))^2), dimensionless a0",
        "gradient_only_Hminus1_bulk_upper":
            outward_decimal(F(1420,223)*F(total),digits,True),
        "gradient_only_dual_proof":
            "zero-extend annulus to radius-20 ball; first Dirichlet "
            "eigenvalue pi^2/400; Archimedes pi>223/71",
        "angular_bound":"orthogonality of normalized Y_l0, |E|<=1, |U|<=E, |partial_s y|<=|grad y|",
        "method":"exact dyadic Lagrange; rational Bernstein convex hull; exact radial r^2 volume",
        "input_modes":21,
        "original_input_values_checked":sum(p["actual_input_complex_values_checked"] for p in panels),
        "tiles":sum(p["cell_count"] for p in panels),
        "pieces_per_regular_panel":pieces,"workers":workers,"digits":digits,
        "elapsed_s":perf_counter()-start,
        "panels":panels,
        "not_certified":["interface delta sheets","r<r0 and r>rmax",
                         "outgoing DtN / low Schur inverse / incoming adjoint",
                         "physical ionization intensity or rate"],
    }


def _panel_job(job: tuple) -> dict:
    return panel_certificate(*job)
