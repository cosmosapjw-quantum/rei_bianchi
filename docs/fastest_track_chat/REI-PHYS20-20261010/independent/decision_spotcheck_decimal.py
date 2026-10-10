#!/usr/bin/env python3
"""Independent reviewer endpoint spotcheck using only standard Decimal.

No candidate code import, native execution, IVP, or old certificate replay.
The preceding optional mpmath attempt stopped at import; its record is retained.
"""
import argparse
import hashlib
import json
from pathlib import Path
from decimal import Decimal as D, getcontext

getcontext().prec = 70

def binary(s):
    n, d = float(s).as_integer_ratio()
    return D(n)/D(d)

H = binary('1e-14')
S = (binary('1.01e-14')-binary('0.99e-14'))/2
T = D(1250000000)
EB, CHI = binary('13.7'), binary('13.598434599702')
C, NH, XHI = binary('29979245800.0'), binary('1e-4'), 1-binary('0.9')
E0, YA, P, SIG0, CM2 = (binary(s) for s in ['0.4298','32.88','2.963','5.475e4','1e-18'])

def power(x, y):
    return (x.ln()*y).exp()

def cross_section(e):
    x = e/E0
    return SIG0*(x-1)**2*power(x, P/2-D('5.5'))*power(1+(x/YA).sqrt(),-P)*CM2

def integrate(f, a, b, n):
    h=(b-a)/n
    odd=sum((f(a+(2*i+1)*h) for i in range(n//2)),D(0))
    even=sum((f(a+2*i*h) for i in range(1,n//2)),D(0))
    return h*(f(a)+f(b)+4*odd+2*even)/3

def values(b,q2,amp,n):
    def g(t):
        return (q2[0]*(-2*amp*S*t).exp()+q2[1]*(2*amp*S*t).exp()+q2[2]).sqrt()
    def energy(t):
        return EB*(-H*(t-b)).exp()*g(t)/g(b)
    def hazard(t):
        return C*NH*XHI*(-3*H*t).exp()*cross_section(energy(t))
    theta=integrate(hazard,b,T,n)
    event=(-theta).exp()*hazard(T)
    heat=event*(energy(T)-CHI)
    ratio=(g(T)/g(b))**3
    return dict(energy_ev=energy(T),theta=theta,hazard_s=hazard(T),
                event_per_photon_s=event,heat_per_photon_ev_s=heat,
                observed_angle_event=event*ratio,observed_angle_heat=heat*ratio)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists(): raise SystemExit('Create-only output exists')
    candidate=json.loads(a.candidate.read_text())
    rows=[]
    checks=[]
    for direction,b,q2 in [('x_axis',D(0),(D(1),D(0),D(0))),
                           ('y_axis',D(0),(D(0),D(1),D(0))),
                           ('mixed_3_5_4_5',T/2,(D(9)/25,D(16)/25,D(0)))]:
        old=next(r for r in candidate['records'] if r['direction']==direction and D(r['birth_s'])==b)
        base,perturbed=values(b,q2,D(0),256),values(b,q2,D(1),256)
        refined=values(b,q2,D(1),512)
        changes={k:perturbed[k]/base[k]-1 for k in base if k!='theta'}
        differences={k:abs(changes[k]-D(old['actual_fractional_changes'][k])) for k in changes}
        checks.extend(dict(name=direction+':'+k,pass_check=bool(err<D('2e-18')),
                           absolute_discrepancy=str(err)) for k,err in differences.items())
        time_diff=abs(perturbed['theta']/refined['theta']-1)
        checks.append(dict(name=direction+':simpson256_vs512',pass_check=(time_diff<D('1e-20')),
                           relative_difference=str(time_diff)))
        rows.append(dict(direction=direction,birth_s=str(b),baseline_theta=str(base['theta']),
                         candidate_baseline_theta_relative_difference=str(abs(base['theta']/D(old['baseline']['theta'])-1)),
                         changes={k:str(v) for k,v in changes.items()},
                         differences={k:str(v) for k,v in differences.items()},time_refinement_relative_difference=str(time_diff)))
    trace=binary('1.01e-14')+binary('0.99e-14')-2*H
    checks.append(dict(name='binary64_trace_free_exact_inputs',pass_check=(trace==0)))
    x=rows[0]['changes']
    signs=(D(x['energy_ev'])<0<D(x['event_per_photon_s'])
           and D(x['heat_per_photon_ev_s'])<0 and D(x['observed_angle_event'])<0
           and D(x['observed_angle_heat'])<0)
    checks.append(dict(name='x_axis_rate_heat_measure_signs',pass_check=bool(signs)))
    out=dict(task='REI-PHYS20-20261010',role='independent decision reviewer spotcheck',
             method='Decimal70; independently transcribed HI formula and exact characteristic; Simpson256 checked against512; no owner code import',
             evidence_state='numerically checked',candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,
             check_count=len(checks),failure_count=sum(not c['pass_check'] for c in checks),checks=checks,
             rigorous_enclosure=False,native_runs=0,gas_IVP_runs=0,physical_admission='HOLD')
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(checks=out['check_count'],failures=out['failure_count'],
                         max_fractional_change_discrepancy=str(max(D(v) for r in rows for v in r['differences'].values())))))
    if out['failure_count']:raise SystemExit(1)

if __name__=='__main__':main()
