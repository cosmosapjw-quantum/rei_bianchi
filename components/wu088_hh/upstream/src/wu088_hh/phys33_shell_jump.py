"""Exact one-shell strong residual trace jump at the frozen radial interface.

This trace difference is NOT a distributional delta term. Distributional
defect depends on jumps in the field and its first normal derivative, not
on a jump of its second normal derivative.
"""
from fractions import Fraction as F
from pathlib import Path
from time import perf_counter

from .phys33_cusp_shell import _shell_poly, R
from .phys33_residual import load_frozen,interpolants,reconstruct,derivative,value,scale,ceil_sqrt_fixed
from .phys33_moments import _floor_sqrt_fixed
from .phys33_coupled_source import outward_decimal


def jump_certificate(filename:str|Path,n:int=96,digits:int=15)->dict:
    started=perf_counter()
    pl,el,ml=_shell_poly(filename,"left",n)
    pr,er,mr=_shell_poly(filename,"right",n)
    # Exact rational moment 2∫_0^1 x |P_right - P_left|² dx.
    poly=[[],[]]
    for j in range(2):
        a,b=pl[j],pr[j]
        poly[j]=[(b[i] if i<len(b) else 0)-(a[i] if i<len(a) else 0)
                 for i in range(max(len(a),len(b)))]
    nsq=F(0)
    for arr in poly:
        for i,ai in enumerate(arr):
            if not ai:continue
            for j,aj in enumerate(arr):
                if aj:nsq+=2*ai*aj/F(i+j+2)
    assert nsq>=0
    shell_upper=F(ceil_sqrt_fixed(nsq,digits))
    shell_lower=F(_floor_sqrt_fixed(nsq,digits))
    error=el+er
    lower=max(F(0),shell_lower-error)
    upper=shell_upper+error

    # Value and radial-first-derivative traces in the full Y_l0 basis
    # are orthonormal in angle (without additional factors 2l+1).
    radial,u,sha=load_frozen(filename,True)
    traces=[]
    for panel in (1,2):
        nodes=[F(*float(v).as_integer_ratio()) for v in radial[panel]]
        lo,hi=nodes[0],nodes[-1];mid,half=(lo+hi)/2,(hi-lo)/2
        pts=[(z-mid)/half for z in nodes];basis=interpolants(pts)
        target=(R-mid)/half
        ret=[]
        for ell in range(21):
            components=[]
            for z in (u[ell,panel].real,u[ell,panel].imag):
                arr=[F(*float(v).as_integer_ratio()) for v in z]
                re,im=None,None
                poly=[sum((val*v for val,v in zip(arr,bcol)),F(0)) for bcol in zip(*basis)]
                v=value(poly,target)
                d=value(scale(derivative(poly),1/half),target)
                components.append((v,d))
            ret.append(components)
        traces.append(ret)
    state2=F(0);first2=F(0)
    for ell in range(21):
        for component in range(2):
            vl,dl=traces[0][ell][component]
            vr,dr=traces[1][ell][component]
            jumpv=(vr-vl)/R
            jumpd=(dr-dl)/R-(vr-vl)/R**2
            state2+=jumpv*jumpv
            first2+=jumpd*jumpd
    return {
      "schema":"WU088_HH_PHYS37_ONE_SIDED_CUSP_STRONG_TRACE_JUMP_V1",
      "input_sha256":sha,"r_a0":"7/10","taylor_order":n,
      "strong_residual_jump_l2_interval":[outward_decimal(lower,digits,False),
                                         outward_decimal(upper,digits,True)],
      "radial_field_value_jump_l2_upper":ceil_sqrt_fixed(state2,digits),
      "radial_first_derivative_jump_l2_upper":ceil_sqrt_fixed(first2,digits),
      "meaning":"strong second-order residual trace discontinuity; no unproved distributional admission",
      "elapsed_s":perf_counter()-started
    }
