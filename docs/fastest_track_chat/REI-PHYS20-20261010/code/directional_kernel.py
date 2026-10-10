#!/usr/bin/env python3
"""PHYS20 small directional kernel; no gas IVP and no production import.

The gas neutral fraction is frozen at the pinned FT03 initial value.  Proper
density still dilutes as exp(-3 H t).  All input Rust f64 literals are interpreted
as exact real binary64 numbers; arithmetic is Decimal at 60 digits.  Quadrature
nodes/weights are numerical Gauss-Legendre values, so this is a numerical check,
not a rigorous enclosure or a reproduction of the native solver.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
from decimal import Decimal, localcontext, getcontext
from pathlib import Path
import numpy as np

getcontext().prec = 60


def d(s):
    return Decimal.from_float(float(s))


H = d("1e-14")
SX = d("1.01e-14") - H
SY = d("0.99e-14") - H
S = (SX - SY) / 2
C = d("29979245800.0")
NH0 = d("1e-4")
XHI = Decimal(1) - d("0.9")
EB = d("13.7")
CHI = d("13.598434599702")
CUT = d("13.60")
E0 = d("0.4298")
SIG0 = d("5.475e4")
YA = d("32.88")
P = d("2.963")
CM2 = d("1e-18")
TEND = d("1.25e9")


def sigma(e):
    if e < CUT:
        return Decimal(0)
    x = e / E0
    power = P / 2 - Decimal("5.5")
    return SIG0 * (x-1)**2 * (power*x.ln()).exp() * (-P*(1+(x/YA).sqrt()).ln()).exp() * CM2


def alpha(e):
    x = e / E0
    u = (x/YA).sqrt()
    return 2*x/(x-1) + P/2 - Decimal("5.5") - (P/2)*u/(1+u)


def g_aniso(t, amp, q2):
    st = amp*S*t
    return (q2[0]*(-2*st).exp() + q2[1]*(2*st).exp() + q2[2]).sqrt()


def energy(t, birth, amp, q2):
    return EB*(-H*(t-birth)).exp()*g_aniso(t,amp,q2)/g_aniso(birth,amp,q2)


def jac(t, amp, q2):
    return 1/g_aniso(t,amp,q2)**3


def hazard(t, birth, amp, q2):
    return C*NH0*XHI*(-3*H*t).exp()*sigma(energy(t,birth,amp,q2))


def gl_integral(f, lo, hi, n):
    x,w = np.polynomial.legendre.leggauss(n)
    half=(hi-lo)/2
    mid=(hi+lo)/2
    return half*sum((Decimal.from_float(float(wi))*f(mid+half*Decimal.from_float(float(xi))) for xi,wi in zip(x,w)),Decimal(0))


def simpson(f, lo, hi, n=128):
    assert n % 2 == 0
    step=(hi-lo)/n
    return step/3*(f(lo)+f(hi)+sum(((4 if i%2 else 2)*f(lo+step*i) for i in range(1,n)),Decimal(0)))


def kernel(t,birth,amp,q2,n=24):
    e=energy(t,birth,amp,q2)
    theta=gl_integral(lambda u:hazard(u,birth,amp,q2),birth,t,n)
    survival=(-theta).exp()
    local=hazard(t,birth,amp,q2)
    event=local*survival
    heat=event*(e-CHI)
    jb,jt=jac(birth,amp,q2),jac(t,amp,q2)
    return {'energy_ev':e,'theta':theta,'survival':survival,'hazard_s':local,
            'event_per_photon_s':event,'heat_per_photon_ev_s':heat,
            'source_q_event':jb*event,'source_q_heat':jb*heat,
            'observed_angle_event':jb/jt*event,'observed_angle_heat':jb/jt*heat,
            'J_birth':jb,'J_observe':jt}


def first_variation(t,birth,q2):
    proj=q2[0]-q2[1]
    bend=S*(t-birth)*proj
    eb=energy(t,birth,Decimal(0),q2)
    at=alpha(eb)
    memory=gl_integral(lambda u:hazard(u,birth,Decimal(0),q2)*alpha(energy(u,birth,Decimal(0),q2))*S*(u-birth)*proj,birth,t,32)
    photon=-at*bend+memory
    heat=photon-eb/(eb-CHI)*bend
    return {'delta_log_energy':-bend,'delta_log_hazard':-at*bend,
            'survival_memory_delta_log':memory,'delta_log_event_per_photon':photon,
            'delta_log_heat_per_photon':heat,
            'delta_log_source_q_event':3*S*birth*proj+photon,
            'delta_log_source_q_heat':3*S*birth*proj+heat,
            'delta_log_observed_angle_event':-3*bend+photon,
            'delta_log_observed_angle_heat':-3*bend+heat,
            'alpha_sigma':at,'alpha_primary_heat':at+eb/(eb-CHI)}


def serialize(x):
    if isinstance(x,Decimal): return str(x)
    if isinstance(x,dict): return {k:serialize(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [serialize(v) for v in x]
    return x


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if args.output.exists(): raise SystemExit('Output exists; choose a new path.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with localcontext() as ctx:
        ctx.prec=60
        # Re-evaluate the shear difference at full precision; module constants
        # otherwise contain only conversions, except S which is overwritten here.
        global S
        S=((d('1.01e-14')-H)-(d('0.99e-14')-H))/2
        q2s={'x_axis':(Decimal(1),Decimal(0),Decimal(0)),
             'y_axis':(Decimal(0),Decimal(1),Decimal(0)),
             'z_axis':(Decimal(0),Decimal(0),Decimal(1)),
             'mixed_3_5_4_5':(Decimal(9)/25,Decimal(16)/25,Decimal(0))}
        records=[]
        failures=[]
        checks=[]
        eps=Decimal('0.002')
        fields={
          'energy_ev':'delta_log_energy','hazard_s':'delta_log_hazard',
          'event_per_photon_s':'delta_log_event_per_photon',
          'heat_per_photon_ev_s':'delta_log_heat_per_photon',
          'source_q_event':'delta_log_source_q_event','source_q_heat':'delta_log_source_q_heat',
          'observed_angle_event':'delta_log_observed_angle_event','observed_angle_heat':'delta_log_observed_angle_heat'}
        for birth in [Decimal(0),TEND/2]:
            for name,q2 in q2s.items():
                base=kernel(TEND,birth,Decimal(0),q2)
                physical=kernel(TEND,birth,Decimal(1),q2)
                variation=first_variation(TEND,birth,q2)
                plus=kernel(TEND,birth,eps,q2)
                minus=kernel(TEND,birth,-eps,q2)
                derivative={k:(plus[k]-minus[k])/(2*eps*base[k]) for k in fields}
                errors={k:abs(derivative[k]-variation[v]) for k,v in fields.items()}
                for k,err in errors.items():
                    ok=err<Decimal('2e-20')
                    checks.append({'name':f'derivative:{birth}:{name}:{k}','abs_error':err,'pass':ok})
                    if not ok: failures.append(checks[-1])
                t48=kernel(TEND,birth,Decimal(1),q2,n=48)['theta']
                tsim=simpson(lambda u:hazard(u,birth,Decimal(1),q2),birth,TEND,128)
                relgl=abs(t48-physical['theta'])/physical['theta']
                relsim=abs(tsim-physical['theta'])/physical['theta']
                for label,error in [('gl24_vs_gl48',relgl),('gl24_vs_simpson128',relsim)]:
                    ok=error<Decimal('2e-14')
                    checks.append({'name':f'{label}:{birth}:{name}','relative_error':error,'pass':ok})
                    if not ok: failures.append(checks[-1])
                records.append({'birth_s':birth,'direction':name,'q_squared':q2,
                                'baseline':base,'actual_shear':physical,'analytic_first_variation':variation,
                                'actual_fractional_changes':{k:physical[k]/base[k]-1 for k in fields},
                                'central_derivative':derivative,'derivative_abs_errors':errors,
                                'quad_relative_differences':{'gl24_vs_gl48':relgl,'gl24_vs_simpson128':relsim}})
        min_e=EB*(-(H+abs(S))*TEND).exp()
        margin=(min_e/CUT).ln()
        ok=margin>0
        checks.append({'name':'actual_firstmacro_no_HI_cutoff_crossing','pass':ok,'log_margin':margin})
        if not ok:failures.append(checks[-1])
        # Physical E=chi cusp is a counterexample in a separate positive-part
        # benchmark, not a change to the actual Verner threshold convention.
        out={'task':'REI-PHYS20-20261010','kind':'NUMERICALLY_CHECKED_FROZEN_GAS_DIRECTIONAL_KERNEL',
             'not_a_gas_solution':True,'new_native_runs':0,'new_gas_IVPs':0,'old_proofs_replayed':False,
             'input_commit':'718468dc75cb81fdfe0f2792aab5c8d0dbc54607',
             'constants':{'H_per_s':H,'shear_per_s':S,'binary64_trace_mismatch_per_s':d('1.01e-14')+d('0.99e-14')-2*H,
                          'c_cm_s':C,'n_H0_cm3':NH0,'frozen_xHI':XHI,'E_birth_ev':EB,'heat_chi_ev':CHI,'provider_cutoff_ev':CUT,'end_s':TEND},
             'numeric_method':{'decimal_digits':60,'main_time_rule':'Gauss-Legendre 24','quadrature_cross_checks':['Gauss-Legendre 48','composite Simpson 128'],
                               'derivative_method':'symmetric exact characteristic evaluations at +/-0.002 times actual shear, compared to analytic first variation',
                               'rigorous_error_enclosure':False},
             'environment':{'python':platform.python_version(),'numpy':np.__version__},
             'records':records,'firstmacro_min_energy_ev':min_e,'firstmacro_HI_log_margin':margin,
             'checks':checks,'check_count':len(checks),'failure_count':len(failures),'failures':failures,
             'physical_admission':'HOLD'}
        args.output.write_text(json.dumps(serialize(out),indent=2)+'\n')
        print(json.dumps({'output':str(args.output),'checks':len(checks),'failures':len(failures),
                          'max_derivative_abs_error':str(max(c.get('abs_error',Decimal(0)) for c in checks)),
                          'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},indent=2))
        if failures:raise SystemExit(1)


if __name__=='__main__': main()
