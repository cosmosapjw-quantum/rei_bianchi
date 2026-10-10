#!/usr/bin/env python3
"""PHYS21 second-order continuum kernel. No gas IVP or production import.

The neutral fraction is frozen at the pinned FT03 initial value. Density
dilution is retained. Physical birth angles are integrated with a research
Gauss-Legendre/azimuth rule, not the native midpoint rule. All input f64
literals are exact-real binary64 conversions; Decimal arithmetic uses 60 digits.
"""
from __future__ import annotations
import argparse
from decimal import Decimal as D, getcontext
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import numpy as np

getcontext().prec = 60


def binary(s):
    return D.from_float(float(s))


H = binary('1e-14')
SHEAR = (binary('1.01e-14') - binary('0.99e-14')) / 2
C = binary('29979245800.0')
NH0 = binary('1e-4')
XHI = D(1) - binary('0.9')
EB = binary('13.7')
CHI = binary('13.598434599702')
CUT = binary('13.60')
E0 = binary('0.4298')
SIG0 = binary('5.475e4')
YA = binary('32.88')
P = binary('2.963')
CM2 = binary('1e-18')
TEND = binary('1.25e9')
OBS = ('survival', 'absorption_event_s', 'primary_heat_ev_s', 'surviving_energy_ev')


def sigma(e):
    if e < CUT:
        return D(0)
    x = e/E0
    return SIG0*(x-1)**2*((P/2-D('5.5'))*x.ln()).exp()*(-P*(1+(x/YA).sqrt()).ln()).exp()*CM2


def spectral(e):
    """Return sigma, D sigma, D^2 sigma; D = E d/dE, above cutoff."""
    if e <= CUT:
        raise ValueError('Spectral derivatives require a threshold-separated domain.')
    x = e/E0
    v = (x/YA).sqrt()
    a = 2*x/(x-1) + P/2 - D('5.5') - P*v/(2*(1+v))
    da = -2*x/(x-1)**2 - P*v/(4*(1+v)**2)
    z = sigma(e)
    return z, z*a, z*(a*a+da)


@lru_cache(None)
def legendre(n):
    xs, ws = np.polynomial.legendre.leggauss(n)
    return tuple((binary(x), binary(w)) for x, w in zip(xs, ws))


def times(b, t, n):
    half = (t-b)/2
    return [((t+b)/2+half*x, half*w) for x, w in legendre(n)]


def angular(nmu, nphi):
    rows = []
    for mu, wm in legendre(nmu):
        for j in range(nphi):
            phi = 2*math.pi*(j+0.5)/nphi
            cp, sp = binary(math.cos(phi)), binary(math.sin(phi))
            z = (1-mu*mu)*(cp*cp+sp*sp)+mu*mu
            m2 = ((1-mu*mu)*cp*cp/z, (1-mu*mu)*sp*sp/z, mu*mu/z)
            rows.append((m2, wm/(2*nphi)))
    return rows


def ebase(s, b):
    return EB*(-H*(s-b)).exp()


def energy(s, b, eps, m2):
    v = eps*SHEAR*(s-b)
    # This representation gives R(0)=1 exactly before rounding.
    r2 = 1 + m2[0]*((-2*v).exp()-1) + m2[1]*((2*v).exp()-1)
    return ebase(s,b)*r2.sqrt()


def opacity(s, e):
    return C*NH0*XHI*(-3*H*s).exp()*sigma(e)


def exact_kernel(t, b, eps, m2, ntime):
    theta = sum((w*opacity(s,energy(s,b,eps,m2)) for s,w in times(b,t,ntime)), D(0))
    surv = (-theta).exp()
    e = energy(t,b,eps,m2)
    event = surv*opacity(t,e)
    return dict(zip(OBS,(surv,event,event*(e-CHI),surv*e)))


def baseline_data(t,b,ntime):
    theta = D(0)
    m = D(0)
    v = D(0)
    for s,w in times(b,t,ntime):
        s0,s1,s2 = spectral(ebase(s,b))
        density = C*NH0*XHI*(-3*H*s).exp()
        lam,dlam,ddlam = density*s0,density*s1,density*s2
        u = SHEAR*(s-b)
        theta += w*lam
        m += w*dlam*u
        v += w*(ddlam+3*dlam)*2*u*u
    surv = (-theta).exp()
    e = ebase(t,b)
    s0,s1,s2 = spectral(e)
    density = C*NH0*XHI*(-3*H*t).exp()
    lam,dlam,ddlam = density*s0,density*s1,density*s2
    local = {
      'survival':(D(1),D(0),D(0)),
      'absorption_event_s':(lam,dlam,ddlam),
      'primary_heat_ev_s':(lam*(e-CHI),dlam*(e-CHI)+lam*e,ddlam*(e-CHI)+2*dlam*e+lam*e),
      'surviving_energy_ev':(e,e,e)
    }
    u = SHEAR*(t-b)
    rows = {}
    for key,(l,dl,ddl) in local.items():
        pieces = {
          'local_spectral_curvature':(ddl+3*dl)*2*u*u,
          'endpoint_opacity_covariance':-4*dl*u*m,
          'survival_variance':l*2*m*m,
          'mean_second_opacity':-l*v
        }
        absolute_pieces = {k:surv*x/15 for k,x in pieces.items()}
        coefficient = sum(absolute_pieces.values(),D(0))
        rows[key] = {'baseline':surv*l,'coefficient':coefficient,
                     'relative_coefficient':coefficient/(surv*l),
                     'relative_parts':{k:x/(surv*l) for k,x in absolute_pieces.items()},
                     'local_D':dl,'local_D2':ddl,'local_C':ddl+3*dl}
    return {'theta0':theta,'energy0_ev':e,'M_diagonal':(m,-m,D(0)),'V':v,
            'alpha_sigma':dlam/lam,'D_alpha_sigma':ddlam/lam-(dlam/lam)**2,
            'C_sigma_over_sigma':(ddlam+3*dlam)/lam,'rows':rows}


def central_coefficients(t,b,h,nmu,nphi,ntime):
    result = {k:D(0) for k in OBS}
    base = exact_kernel(t,b,D(0),(D(1),D(0),D(0)),ntime)
    for m2,w in angular(nmu,nphi):
        plus = exact_kernel(t,b,h,m2,ntime)
        minus = exact_kernel(t,b,-h,m2,ntime)
        for key in OBS:
            result[key] += w*(plus[key]+minus[key]-2*base[key])/(2*h*h)
    return result


def serial(obj):
    if isinstance(obj,D): return str(obj)
    if isinstance(obj,dict): return {k:serial(v) for k,v in obj.items()}
    if isinstance(obj,(tuple,list)): return [serial(v) for v in obj]
    return obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists(): raise SystemExit('Output exists; choose a new path.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    checks, records = [], []

    def check(name,ok,**evidence):
        checks.append({'name':name,'pass':bool(ok),**evidence})

    for b in (D(0),TEND/2):
        analytic = baseline_data(TEND,b,16)
        refined = baseline_data(TEND,b,32)
        probes = {}
        for label,h,nmu,nphi in [('h_1',D(1),4,8),('h_1_16',D(1)/16,4,8),('h_1_32_refined_angle',D(1)/32,6,12)]:
            vals = central_coefficients(TEND,b,h,nmu,nphi,16)
            rows = {}
            for key,value in vals.items():
                expected = analytic['rows'][key]['coefficient']
                err = abs(value/expected-1)
                rows[key] = {'coefficient':value,'relative_coefficient':value/analytic['rows'][key]['baseline'],
                             'relative_difference_vs_analytic':err}
                check(f'{b}:{label}:{key}:second_order',err<D('5e-11'),relative_difference=err)
            probes[label] = {'epsilon':h,'angle_rule':f'GL{nmu} x midpoint-phi{nphi}','rows':rows}
        for key in OBS:
            err=abs(refined['rows'][key]['coefficient']/analytic['rows'][key]['coefficient']-1)
            check(f'{b}:{key}:time_GL16_vs32',err<D('2e-13'),relative_difference=err)
        # Independent finite-log-energy differences check newly used spectral D2.
        e=analytic['energy0_ev'];s0,s1,s2=spectral(e)
        estimates=[]
        for h in (D('0.00001'),D('0.000005')):
            plus,minus=sigma(e*h.exp()),sigma(e*(-h).exp())
            estimates.append(((plus-minus)/(2*h),(plus+minus-2*s0)/(h*h)))
        for j,label,exact in [(0,'D_sigma',s1),(1,'D2_sigma',s2)]:
            extrap=(4*estimates[1][j]-estimates[0][j])/3
            err=abs(extrap/exact-1)
            check(f'{b}:{label}:log_energy_difference',err<D('5e-19'),relative_difference=err)
        check(f'{b}:scalar_signs',analytic['rows']['survival']['coefficient']>0
              and analytic['rows']['absorption_event_s']['coefficient']<0
              and analytic['rows']['primary_heat_ev_s']['coefficient']<0
              and analytic['rows']['surviving_energy_ev']['coefficient']>0)
        records.append({'birth_s':b,'end_s':TEND,'analytic':analytic,'numeric_probes':probes})
    min_e=EB*(-(H+abs(SHEAR))*TEND).exp()
    check('threshold_separation_for_abs_epsilon_le_1',min_e>CUT,min_energy_ev=min_e,cutoff_ev=CUT)
    output={'task':'REI-PHYS21-20261010','evidence_state':'numerically checked','coefficient_convention':'[epsilon^2], half of second derivative',
            'input_commit':'faec51259ed26f660cf14568bcaa3d288e54bf9a','scientific_src_tree':'cb69b4736dd046e4675557577eb8e0ead037d1f3',
            'scope':'Continuum cohort kernel with frozen initial neutral fraction and retained density dilution; not evolving gas, a full source history, or native angular implementation.',
            'constants':{'H_per_s':H,'shear_per_s':SHEAR,'nH0_cm3':NH0,'xHI_frozen':XHI,'birth_ev':EB,'heat_chi_ev':CHI,'cutoff_ev':CUT,'c_cm_s':C},
            'method':{'decimal_digits':60,'time_rule':'Gauss-Legendre16, checked against32','angular_rules':['GL4 x phi8','GL6 x phi12'],
                      'central_combination':'sum_angle w*(K(+h)+K(-h)-2*K0)/(2*h^2); cancellation performed in Decimal before sum','rigorous_enclosure':False},
            'environment':{'python':platform.python_version(),'numpy':np.__version__},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'records':records,'checks':checks,'check_count':len(checks),'failure_count':sum(not c['pass'] for c in checks),
            'native_runs':0,'gas_IVP_runs':0,'old_proof_replays':0,'physical_admission':'HOLD'}
    args.output.write_text(json.dumps(serial(output),indent=2)+'\n')
    print(json.dumps({'checks':output['check_count'],'failures':output['failure_count'],'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'b0_relative_coefficients':serial({k:v['relative_coefficient'] for k,v in records[0]['analytic']['rows'].items()})},indent=2))
    if output['failure_count']:raise SystemExit(1)


if __name__=='__main__':main()
