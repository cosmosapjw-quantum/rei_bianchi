"""Rigorous rational/log radial moments for the frozen PHYS34 broken-bulk residual.

This C6/C8 optimization replaces *only* the radial-minimum integration envelope.
It does not complete the continuous scattering inverse or outgoing amplitude.
Mathematical input: an exact degree-10 Lagrange interpolant through stored IEEE
binary64 nodes and values. Every polynomial operation is Fraction arithmetic.
The only transcendental term is log(right/left); certified rational atanh-series
limits control its sign and total error, including catastrophic cancellation.
Parallel work is independent across six angular-radial panels and deterministic.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
from multiprocessing import get_all_start_methods, get_context
from math import comb, isqrt
from pathlib import Path
from time import perf_counter

import numpy as np

from .phys33_residual import (
    CHI_RECEIVER_EV, DEGREE, FROZEN_SUBSET_SHA256, I0_EV, KAPPA_SQUARED,
    L_MAX, PANEL_COUNT, add, ceil_sqrt_fixed, derivative, dyadic, integrate,
    interpolants, load_frozen, mul, reconstruct, scale, squared, value,
)


def _log_atanh(z: Q, terms: int) -> tuple[Q, Q]:
    """Exact positive rational endpoints enclosing log(z), 1<=z<=2."""
    if not (Q(1) <= z <= Q(2)) or terms < 1:
        raise ValueError("log argument must be in [1,2] with positive terms")
    t = (z - 1) / (z + 1)
    if t == 0:
        return Q(0), Q(0)
    t2, power = t * t, t
    summ = Q(0)
    for j in range(terms):
        summ += Q(2) * power / (2*j + 1)
        power *= t2
    remainder = Q(2) * power / ((2*terms + 1)*(1-t2))
    return summ, summ+remainder


def log_ratio_bounds(left: Q, right: Q, terms: int = 96) -> tuple[Q, Q]:
    """Certified rational bracket of log(right/left) using powers of 2."""
    if not 0 < left < right:
        raise ValueError("positive ordered endpoints required")
    z = right / left
    k = max(0, z.numerator.bit_length()-z.denominator.bit_length())
    q = z / (Q(2)**k)
    while q < 1:
        k -= 1; q *= 2
    while q >= 2:
        k += 1; q /= 2
    lo2, hi2 = _log_atanh(Q(2), terms)
    loq, hiq = _log_atanh(q, terms)
    return k*lo2+loq, k*hi2+hiq


def _unit_moment(left: Q, right: Q, exponent: int) -> tuple[Q, Q]:
    """Return A+B log(right/left) for integral of r**exponent."""
    if exponent == -1:
        return Q(0), Q(1)
    k = exponent+1
    return (right**k-left**k)/k, Q(0)


def _moment_polynomials(mid: Q, half: Q, left: Q, right: Q,
                        max_degree: int, divisor_power: int) -> list[tuple[Q, Q]]:
    """The integral dr x**k/r**p, x=(r-mid)/half, split A+B*log."""
    # Common-moment preprocessing is shared by 21 angular modes.
    moments = [_unit_moment(left, right, j-divisor_power)
               for j in range(max_degree+1)]
    out = []
    for k in range(max_degree+1):
        factor = half**(-k)
        a = sum((comb(k,j)*(-mid)**(k-j)*moments[j][0]
                 for j in range(k+1)), Q(0))*factor
        b = sum((comb(k,j)*(-mid)**(k-j)*moments[j][1]
                 for j in range(k+1)), Q(0))*factor
        out.append((a,b))
    return out


def _combine(poly: list[Q], moments: list[tuple[Q,Q]]) -> tuple[Q,Q]:
    if len(poly)>len(moments):
        raise ValueError("insufficient cached moment degree")
    return (sum((v*moments[i][0] for i,v in enumerate(poly)), Q(0)),
            sum((v*moments[i][1] for i,v in enumerate(poly)), Q(0)))


def _floor_sqrt_fixed(x: Q, digits: int) -> str:
    """Exact downward decimal rounded square root, no binary float used."""
    if x < 0 or not 0 <= digits <= 24:
        raise ValueError("invalid nonnegative rational or decimal digits")
    base = 10**digits
    n = isqrt((x.numerator*base*base)//x.denominator)
    whole, fractional = divmod(n,base)
    return str(whole) if not digits else f"{whole}.{fractional:0{digits}d}"


def _enclose(a: Q, b: Q, loglo: Q, loghi: Q) -> tuple[Q,Q]:
    l,h = (loglo,loghi) if b>=0 else (loghi,loglo)
    return a+b*l, a+b*h


def _expminus_upper(x: Q, terms: int = 64) -> Q:
    """Exact upper exp(-x) using a positive Taylor lower of exp(x)."""
    if x < 0 or terms < 1:
        raise ValueError("nonnegative x and positive terms required")
    coeff = Q(1); series = coeff
    for j in range(1,terms+1):
        coeff *= x/j
        series += coeff
    return Q(1)/series


def _panel(job: tuple[int, list, list, int, int, int]) -> dict:
    j, radial, complex_values, digits, max_terms, weight_cells = job
    lo,hi=dyadic(radial[0]),dyadic(radial[-1])
    half,mid=(hi-lo)/2,(hi+lo)/2
    nodes=[(dyadic(r)-mid)/half for r in radial]
    basis=interpolants(nodes)
    rr=[mid,half];r2=mul(rr,rr)
    m4=_moment_polynomials(mid,half,lo,hi,24,4)
    m2=_moment_polynomials(mid,half,lo,hi,20,2)
    mass=Q(0)
    total_grad_poly=[Q(0)]
    total_state_poly=[Q(0)]
    dia, dib, gra, grb=Q(0),Q(0),Q(0),Q(0)
    left_end=[];right_end=[]
    for ell in range(L_MAX+1):
        re,im=reconstruct(complex_values[ell],basis)
        if any(value(re,x)!=dyadic(z.real) or value(im,x)!=dyadic(z.imag)
               for x,z in zip(nodes,complex_values[ell])):
            raise ArithmeticError("frozen node interpolation does not reproduce bytes")
        re1,im1=scale(derivative(re),1/half),scale(derivative(im),1/half)
        re2,im2=scale(derivative(re1),1/half),scale(derivative(im1),1/half)
        pot=add(add(scale(r2,KAPPA_SQUARED),scale(rr,Q(2))),
                [-Q(ell*(ell+1))])
        sr2=squared(add(mul(r2,re2),mul(pot,re)),
                    add(mul(r2,im2),mul(pot,im)))
        sg2=squared(add(mul(rr,re1),scale(re,-1)),
                    add(mul(rr,im1),scale(im,-1)))
        su2=squared(re,im)
        mass+=half*integrate(su2,Q(-1),Q(1))
        a,b=_combine(sr2,m4);dia+=a;dib+=b
        gp=add(sg2,scale(su2,Q(ell*(ell+1))))
        total_grad_poly=add(total_grad_poly,gp)
        total_state_poly=add(total_state_poly,su2)
        ag,bg=_combine(gp,m2)
        gra+=ag;grb+=bg
        left_end.append((value(re,Q(-1)),value(im,Q(-1)),
                         value(re1,Q(-1)),value(im1,Q(-1))))
        right_end.append((value(re,Q(1)),value(im,Q(1)),
                          value(re1,Q(1)),value(im1,Q(1))))
    # |U_lambda(s)| <= lambda*exp(-s), proven by
    # exp(-s) <= (1-exp(-s))/s <=1 and 0<=lambda<=1.
    # s>=|r-R|; a radial-panel upper for exp(-2*s) is exact rational.
    R=Q(7,10)
    min_dist=max(Q(0),lo-R,R-hi)
    screened_weight_squared_upper=_expminus_upper(2*min_dist,64)
    if weight_cells==1:
        wgrad_hi=screened_weight_squared_upper*(gra+grb*log_ratio_bounds(lo,hi,96)[1]
            if grb>=0 else gra+grb*log_ratio_bounds(lo,hi,96)[0])
        wstate_hi=screened_weight_squared_upper*mass
        weight_points=[lo,hi]
    else:
        # A common aggregated polynomial across all ell is integrated once per
        # weighted radial cell. This replaces 21*weight_cells independent loops.
        weight_points=[dyadic(x) for x in np.geomspace(
            float(lo),float(hi),weight_cells+1)]
        weight_points[0],weight_points[-1]=lo,hi
        if any(a>=b for a,b in zip(weight_points,weight_points[1:])):
            raise ArithmeticError('invalid exact geometric weight partition')
        wgrad_hi,wstate_hi=Q(0),Q(0)
        state_sum=Q(0)
        for a,b in zip(weight_points,weight_points[1:]):
            lm4=_moment_polynomials(mid,half,a,b,len(total_grad_poly)-1,2)
            ga,gb=_combine(total_grad_poly,lm4)
            llo,lhi=log_ratio_bounds(a,b,128)
            g_lo,g_hi=_enclose(ga,gb,llo,lhi)
            if g_hi<0:
                raise ArithmeticError('screen-weighted gradient integral negative')
            x0,x1=(a-mid)/half,(b-mid)/half
            m_cell=half*integrate(total_state_poly,x0,x1)
            if m_cell<0:
                raise ArithmeticError('screen-weighted mass polynomial nonpositive')
            state_sum+=m_cell
            rad_dist=max(Q(0),a-R,R-b)
            weight=_expminus_upper(2*rad_dist,64)
            wgrad_hi+=weight*g_hi
            wstate_hi+=weight*m_cell
        if state_sum!=mass:
            raise ArithmeticError('weighted partition must sum to exact mass')
    chosen=48
    while chosen<=max_terms:
        ll,hh=log_ratio_bounds(lo,hi,chosen)
        d0,d1=_enclose(dia,dib,ll,hh)
        g0,g1=_enclose(gra,grb,ll,hh)
        if d1 < 0 or g1 < 0:
            raise ArithmeticError("positive weighted integral has negative upper bound")
        # After catastrophic cancellation, require a useful outward log error.
        w=(d1-d0)+(g1-g0)
        if w<=Q(1,10**(digits+6)):
            break
        chosen*=2
    if chosen>max_terms:
        raise ArithmeticError("certified logarithm failed requested interval width")
    return dict(panel=j,lo=lo,hi=hi,diag_lo=max(Q(0),d0),
                diag_hi=d1,grad_lo=max(Q(0),g0),grad_hi=g1,
                mass=mass,screened_weight_squared_upper=screened_weight_squared_upper,
                min_distance_to_spectator=min_dist,
                weighted_grad_hi=wgrad_hi,weighted_mass_hi=wstate_hi,
                weight_points=weight_points,
                log_terms=chosen,log_uncertainty_width=w,
                log_coeff_diag=dib,log_coeff_grad=grb,
                left=left_end,right=right_end)


def bound_weighted_moments(filename: str|Path, workers: int=1,
                           digits: int=12, max_log_terms: int=1536,
                           screen_cells: int=1) -> dict:
    """Certified whole-cell broken-bulk radial bound (not full PDE certification).

    No subcell approximation remains. Only finite rational/logarithmic moments
    and a rigorously bounded transcendental atanh remainder are used.
    Parallel processes do not share state and deterministic reduction is sorted.
    """
    if workers not in (1,2,3,4,6):
        raise ValueError("workers must be 1,2,3,4 or 6")
    if not 6<=digits<=18 or max_log_terms<48:
        raise ValueError("unsupported log precision configuration")
    if isinstance(screen_cells,bool) or screen_cells not in (1,2,4,8,16):
        raise ValueError("screen_cells must be 1,2,4,8,16")
    before=perf_counter()
    rr,uu,sha=load_frozen(filename,True)
    jobs=[(j,list(rr[j]),list(uu[:,j,:]),digits,max_log_terms,screen_cells)
          for j in range(PANEL_COUNT)]
    if workers==1:
        partial=[_panel(job) for job in jobs]
    else:
        # Never fork directly out of a multithreaded pytest/BLAS parent.
        # forkserver avoids Python3.12's unsafe-threaded-fork warning; spawn
        # is the portable fallback on platforms without a fork server.
        start_method = "forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context(start_method)) as pool:
            partial=list(pool.map(_panel,jobs))
    partial.sort(key=lambda item:item["panel"])
    dlow=sum((a["diag_lo"] for a in partial),Q(0))
    dhi=sum((a["diag_hi"] for a in partial),Q(0))
    glow=sum((a["grad_lo"] for a in partial),Q(0))
    ghi=sum((a["grad_hi"] for a in partial),Q(0))
    mass=sum((a["mass"] for a in partial),Q(0))
    weighted_grad2=sum((a["weighted_grad_hi"] for a in partial),Q(0))
    weighted_mass2=sum((a["weighted_mass_hi"] for a in partial),Q(0))
    if dlow>dhi or glow>ghi or mass<0:
        raise ArithmeticError("internal rational interval inconsistent")
    D=ceil_sqrt_fixed(dhi,digits)
    G=ceil_sqrt_fixed(ghi,digits)
    M=ceil_sqrt_fixed(mass,digits)
    residual_old=Q(D)+2*Q(G)+4*Q(M)+Q(149,100)
    # Exact cusp field: B= lambda E shat, |U_lambda|<=lambda E,
    # E=exp(-s), s>=|r-R|. Both new weighted norms use ∫ E^2(...).
    Wg=ceil_sqrt_fixed(weighted_grad2,digits)
    Wm=ceil_sqrt_fixed(weighted_mass2,digits)
    residual=Q(D)+2*Q(Wg)+2*Q(Wm)+Q(149,100)
    jumps=[]
    for a,b in zip(partial,partial[1:]):
        vjump=sum(((ra[0]-lb[0])**2+(ra[1]-lb[1])**2
                   for ra,lb in zip(a["right"],b["left"])),Q(0))
        djump=sum(((ra[2]-lb[2])**2+(ra[3]-lb[3])**2
                   for ra,lb in zip(a["right"],b["left"])),Q(0))
        jumps.append({"r":str(float(a["hi"])),
                      "value_jump_l2_upper":ceil_sqrt_fixed(vjump,digits),
                      "derivative_jump_l2_upper":ceil_sqrt_fixed(djump,digits)})
    return {
        "schema":"WU088_HH_PHYS35_C6_C8_SCREENED_MOMENT_V2",
        "input_sha256":sha,"workers":workers,"digits":digits,
        "screen_cells":screen_cells,
        "elapsed_s":perf_counter()-before,
        "math":"positive radial moments, certified rational log(b/a), and exact exp(-2distance) panel envelopes",
        "norm_lower_upper":{
            "coulomb_diagonal":[_floor_sqrt_fixed(dlow,digits),D],
            "gradient":[_floor_sqrt_fixed(glow,digits),G],
            "state":[_floor_sqrt_fixed(mass,digits),M],
        },
        "norm_upper":{
            "coulomb_diagonal":D,"state_gradient":G,"state":M,
            "screened_weighted_gradient":Wg,
            "screened_weighted_state":Wm,
            "unweighted_previous_broken_bulk_residual":
                ceil_sqrt_fixed(residual_old*residual_old,digits),
            "broken_transformed_bulk_residual":
                ceil_sqrt_fixed(residual*residual,digits),
        },
        "panels":[{
            "panel":a["panel"],
            "radial":[str(float(a["lo"])),str(float(a["hi"]))],
            "coulomb_diagonal_upper":ceil_sqrt_fixed(a["diag_hi"],digits),
            "gradient_upper":ceil_sqrt_fixed(a["grad_hi"],digits),
            "state_upper":ceil_sqrt_fixed(a["mass"],digits),
            "min_spectator_distance":str(a["min_distance_to_spectator"]),
            "exp_minus_2distance_upper_exact":str(a["screened_weight_squared_upper"]),
            "screen_weight_cells_exact_rational":[str(x) for x in a["weight_points"]],
            "log_series_terms":a["log_terms"],
            "certified_log_weighted_integral_width":
                ceil_sqrt_fixed(a["log_uncertainty_width"]**2,digits),
        } for a in partial],
        "interfaces":jumps,
        "checked_nodal_values":(L_MAX+1)*PANEL_COUNT*(DEGREE+1),
        "physical_input":{
            "R":"7/10 a0","kappa":"7/10 hbar/a0","lambda":"1",
            "energy_unit":"Ea=2I0","I0_eV":I0_EV,"receiver_chiH_eV":CHI_RECEIVER_EV,
        },
        "claims_excluded":[
            "distributional interface terms",
            "missing origin r<1e-4", "full screened DtN boundary residual",
            "continuous low-Schur inverse", "global scattering amplitude and rate",
            "numerical calibrated chemistry or REI production physics",
        ],
    }
