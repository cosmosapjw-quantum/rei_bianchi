"""Exact-rational finite-source photon competition enclosure.

A_j=(C_HI S_HI,C_HeI S_HeI,C_HeII S_HeII,E_external),
p_j=A_j/sum(A).  Derivatives and finite remainders are evaluated for the
SAME four source variables, never independent full/half output images.

The returned enclosures apply to the indicated A-box in represented exact-
rational inputs.  They do NOT enclose the entire multi-stage 26-event step map.
"""
from fractions import Fraction
import math


def f(value):
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite rational input")
        return Fraction(value)
    raise TypeError(f"cannot convert {type(value)}")


def finite_source_certificate(a0, alo, ahi):
    """Exact rational bounds for an arbitrary nonnegative 4-channel source box.

    For a_j'=a_j+da_j, D=sum a_j, p_j=a_j/D, let
    eta=sum da_j / D, v_j=da_j/D - p_j eta.
    Then p_j'-p_j=v_j/(1+eta), and the exact first-order remainder
    relative to v_j is R_j=-v_j eta/(1+eta).
    """
    a0, alo, ahi = [[f(v) for v in data] for data in (a0, alo, ahi)]
    if not all(len(a) == 4 for a in (a0, alo, ahi)):
        raise ValueError("need 3 neutral species and external sink")
    if any(not (0 <= lo <= x <= hi) for x, lo, hi in zip(a0, alo, ahi)):
        raise ValueError("point not enclosed in positive source box")
    D = sum(a0)
    if D <= 0 or sum(alo) <= 0:
        raise ValueError("positive denominator not certified")
    p = [x / D for x in a0]
    dl = [(lo - x) / D for x,lo in zip(a0,alo)]
    dh = [(hi - x) / D for x,hi in zip(a0,ahi)]
    etalo = sum(dl)
    etahi = sum(dh)
    assert 1 + etalo == sum(alo) / D
    assert 1 + etahi == sum(ahi) / D
    eta_abs = max(abs(etalo), abs(etahi))
    rows = []
    for j in range(4):
        Llo = (1-p[j])*dl[j] - p[j]*sum(dh[k] for k in range(4) if k!=j)
        Lhi = (1-p[j])*dh[j] - p[j]*sum(dl[k] for k in range(4) if k!=j)
        Linf = max(abs(Llo), abs(Lhi))
        # EXACT mean-value / first-order finite remainder bounds over the whole box.
        deltap = Linf / (1+etalo)
        rem = Linf * eta_abs / (1+etalo)
        # Exact monotone fraction interval using all numerator/denominator correlations.
        denmin = alo[j]+sum(ahi[k] for k in range(4) if k!=j)
        denmax = ahi[j]+sum(alo[k] for k in range(4) if k!=j)
        if denmin <= 0 or denmax <= 0: raise ValueError("zero source denominator")
        pmin = alo[j]/denmin
        pmax = ahi[j]/denmax
        rows.append({"p0":p[j],"pmin":pmin,"pmax":pmax,
                     "linear_lo":Llo,"linear_hi":Lhi,
                     "delta_abs_bound":deltap,"remainder_abs_bound":rem})
    return {"rows":rows,"eta_min":etalo,"eta_max":etahi,
            "eta_abs_bound":eta_abs,"D0":D,"p0_sum":sum(p),"pmin_sum":sum(x['pmin'] for x in rows)}


def exact_delta(a0, a1):
    a0, a1 = [[f(v) for v in x] for x in (a0, a1)]
    if len(a0)!=4 or len(a1)!=4 or sum(a0)<=0 or sum(a1)<=0:
        raise ValueError("bad source")
    return [b/sum(a1)-a/sum(a0) for a,b in zip(a0,a1)]


def exact_remainder(a0, a1):
    a0,a1=[[f(v) for v in x] for x in (a0,a1)]
    D=sum(a0);delta=[(b-a)/D for a,b in zip(a0,a1)]
    eta=sum(delta)
    if D<=0 or 1+eta<=0:raise ValueError("bad denominator")
    p=[a/D for a in a0]
    L=[delta[i]-p[i]*eta for i in range(4)]
    return [-li*eta/(1+eta) for li in L]


def fl(x):
    return float(x)
