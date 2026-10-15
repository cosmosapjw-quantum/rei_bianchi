"""Streaming Thomson optical depth and exact conditional decimal bounds.

Input: elapsed proper seconds, nH and ne cm^-3, ion fractions.
Scientific status: post-processing only; no source IVP enclosure is implied.
"""
from decimal import Decimal
from fractions import Fraction
import numpy as np
from optical_depth import C_M_S, SIGMA_T_M2, electron_density_cm3


def cumulative_tau_chunked(t_s,n_h_cm3,x_hii,x_heii,x_heiii,he_to_h,chunk_size=65536):
    """Trapezoid with O(chunk_size) additional intermediate arrays, O(N) output.

    The caller owns and stores the input arrays; memmaps are supported. An overlap
    node between chunks preserves the whole-history integral and proper clock.
    """
    t=np.asarray(t_s)
    if t.ndim != 1 or t.size < 2 or chunk_size < 2:
        raise ValueError("Invalid times or chunk_size")
    arrays=[np.asarray(v) for v in (n_h_cm3,x_hii,x_heii,x_heiii)]
    if any(a.shape != t.shape for a in arrays):
        raise ValueError("Every state history must be node-aligned")
    result=np.empty(t.size,dtype=np.float64)
    result[0]=0.0
    factor=SIGMA_T_M2*C_M_S*1e6
    running=0.0
    for begin in range(0,t.size-1,chunk_size):
        end=min(begin+chunk_size,t.size-1)
        sl=slice(begin,end+1)
        tc=np.asarray(t[sl],dtype=np.float64)
        if not np.all(np.isfinite(tc)):
            raise ValueError("Nonfinite proper time")
        dt=np.diff(tc)
        if np.any(dt<=0):
            raise ValueError("Proper time must increase strictly")
        ne=electron_density_cm3(*(a[sl] for a in arrays),he_to_h)
        increments=dt*(factor*0.5)*(ne[:-1]+ne[1:])
        result[begin+1:end+1]=running+np.cumsum(increments)
        running=float(result[end])
    return result


def _exact_decimal_string(frac):
    """Terminating rational to exact base-10 expansion, no context rounding."""
    if frac==0:
        return "0"
    n,d=frac.numerator,frac.denominator
    k2=k5=0
    while d%2==0:
        k2+=1;d//=2
    while d%5==0:
        k5+=1;d//=5
    if d!=1:
        raise ValueError("Nonterminating rational cannot be decimal-exact")
    places=max(k2,k5)
    integer=abs(n)*(2**(places-k2))*(5**(places-k5))
    digits=str(integer).rjust(places+1,"0")
    body=digits if places==0 else digits[:-places]+"."+digits[-places:]
    return ("-" if n<0 else "")+body


def decimal_tau_bounds(t_strings,lo_strings,hi_strings,
                       sigma_t_m2="6.6524587321e-29",c_m_s="299792458"):
    """Exact finite-decimal sums for supplied WHOLE-CELL electron-density bounds.

    No physical uncertainty of constants, upstream ODE error, or binary64 grid
    interpretation is enclosed. All t/ne/constant inputs must be strings or Decimals.
    """
    sequences=(t_strings,lo_strings,hi_strings)
    if not all(isinstance(v,(str,Decimal)) for seq in sequences for v in seq):
        raise TypeError("Use strings or Decimal instead of binary floats")
    if not isinstance(sigma_t_m2,(str,Decimal)) or not isinstance(c_m_s,(str,Decimal)):
        raise TypeError("Constants must be decimal strings or Decimal")
    t=list(map(Decimal,t_strings))
    lo=list(map(Decimal,lo_strings))
    hi=list(map(Decimal,hi_strings))
    constants=list(map(Decimal,(sigma_t_m2,c_m_s)))
    if not all(x.is_finite() for x in t+lo+hi+constants):
        raise ValueError("Nonfinite decimal input")
    if len(t)<2 or len(lo)!=len(t)-1 or len(hi)!=len(lo):
        raise ValueError("Mismatched cell arrays")
    if any(b<=a for a,b in zip(t,t[1:])) or any(a<0 or b<a for a,b in zip(lo,hi)):
        raise ValueError("Invalid physical intervals")
    if any(v<=0 for v in constants):
        raise ValueError("Physical constants must be positive")
    factor=Fraction(constants[0])*Fraction(constants[1])*1000000
    L=Fraction(0);U=Fraction(0)
    resultL=["0"];resultU=["0"]
    for i in range(len(lo)):
        dt=Fraction(t[i+1])-Fraction(t[i])
        L+=dt*factor*Fraction(lo[i])
        U+=dt*factor*Fraction(hi[i])
        resultL.append(_exact_decimal_string(L))
        resultU.append(_exact_decimal_string(U))
    return resultL,resultU
