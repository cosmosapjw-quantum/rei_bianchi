"""Streaming Thomson depth and exact-decimal conditional bounds.

Decimal bounds concern specified decimal constants and valid whole-cell pointwise
electron density bounds; neither source ODE nor physical constants are certified.
"""
from decimal import Decimal, localcontext
import numpy as np
from optical_depth import C_M_S, SIGMA_T_M2, electron_density_cm3


def cumulative_tau_chunked(t_s, n_h_cm3, x_hii, x_heii, x_heiii, he_to_h, chunk_size=65536):
    """Node-contiguous trapezoid with O(chunk_size) temporary integrand arrays.

    Source histories and returned cumulative optical-depth history each use O(N).
    """
    t = np.asarray(t_s)
    if t.ndim != 1 or t.size < 2 or chunk_size < 2:
        raise ValueError("Invalid times or chunk_size")
    arrays = [np.asarray(v) for v in (n_h_cm3, x_hii, x_heii, x_heiii)]
    if any(a.shape != t.shape for a in arrays):
        raise ValueError("Every state history must be node-aligned")
    if not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError("Proper time must be finite and increasing")
    result = np.empty(len(t), dtype=np.float64)
    result[0] = 0.
    factor = SIGMA_T_M2*C_M_S*1e6
    running = 0.
    for begin in range(0,len(t)-1,chunk_size):
        end = min(begin+chunk_size,len(t)-1)
        sl = slice(begin,end+1)
        ne = electron_density_cm3(*(a[sl] for a in arrays),he_to_h)
        dt = np.diff(t[sl].astype(np.float64))
        increments = dt * (factor*0.5) * (ne[:-1]+ne[1:])
        result[begin+1:end+1] = running+np.cumsum(increments)
        running = result[end]
    return result


def decimal_tau_bounds(t_strings, lo_strings, hi_strings, sigma_t_m2='6.6524587321e-29', c_m_s='299792458'):
    """High precision decimal sum conditional on valid whole-cell electron enclosures.

    Decimal inputs represent physical times in s, electron densities in cm^-3.
    Not an outward-rounding or independently source-certified interval.
    """
    if not all(isinstance(v,(str,Decimal)) for seq in (t_strings,lo_strings,hi_strings) for v in seq):
        raise TypeError("Use strings/Decimals to avoid imported binary rounding")
    t=list(map(Decimal,t_strings));lo=list(map(Decimal,lo_strings));hi=list(map(Decimal,hi_strings))
    if len(t)<2 or len(lo)!=len(t)-1 or len(hi)!=len(lo):
        raise ValueError("Mismatched cell arrays")
    allv=t+lo+hi
    if not all(a.is_finite() for a in allv) or any(b<=a for a,b in zip(t,t[1:])) or any(a<0 or b<a for a,b in zip(lo,hi)):
        raise ValueError("Invalid intervals")
    digits=max(len(a.as_tuple().digits) for a in allv)
    emin=min(a.as_tuple().exponent for a in allv)
    scale_digits=max(64,5*digits+5*len(t)+max(0,-emin)+32)
    with localcontext() as ctx:
        ctx.prec=scale_digits
        factor=Decimal(sigma_t_m2)*Decimal(c_m_s)*Decimal(1000000)
        cumlo=[Decimal(0)];cumhi=[Decimal(0)]
        for i in range(len(lo)):
            dt=t[i+1]-t[i]
            cumlo.append(cumlo[-1]+dt*factor*lo[i])
            cumhi.append(cumhi[-1]+dt*factor*hi[i])
        return [str(a) for a in cumlo],[str(a) for a in cumhi]
