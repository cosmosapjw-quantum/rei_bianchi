#!/usr/bin/env python3
"""Independent decision-review spotcheck; does not import candidate code.

Only exact-characteristic endpoint kernels on frozen neutral gas are evaluated.
No gas IVP, native runtime, production code, or old certificate is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import mpmath as mp

mp.mp.dps = 70

def binary(s):
    n, d = float(s).as_integer_ratio()
    return mp.mpf(n) / d

H = binary('1e-14')
S = (binary('1.01e-14') - binary('0.99e-14')) / 2
T = mp.mpf(1250000000)
EB = binary('13.7')
CHI = binary('13.598434599702')
C = binary('29979245800.0')
NH = binary('1e-4')
XHI = 1 - binary('0.9')

def cross_section(e):
    x = e / binary('0.4298')
    p = binary('2.963')
    return (binary('5.475e4') * (x - 1)**2 * x**(p/2 - mp.mpf('5.5'))
            * (1 + mp.sqrt(x/binary('32.88')))**(-p) * binary('1e-18'))

def values(b, q2, amp):
    def g(t):
        return mp.sqrt(q2[0]*mp.exp(-2*amp*S*t)
                       + q2[1]*mp.exp(2*amp*S*t) + q2[2])
    def energy(t):
        return EB * mp.exp(-H*(t-b)) * g(t) / g(b)
    def hazard(t):
        return C*NH*XHI*mp.exp(-3*H*t)*cross_section(energy(t))
    theta = mp.quad(hazard, [b, T], method='tanh-sinh')
    event = mp.exp(-theta) * hazard(T)
    heat = event * (energy(T)-CHI)
    jb, jt = g(b)**(-3), g(T)**(-3)
    return dict(energy_ev=energy(T), theta=theta, hazard_s=hazard(T),
                event_per_photon_s=event, heat_per_photon_ev_s=heat,
                observed_angle_event=event*jb/jt,
                observed_angle_heat=heat*jb/jt)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit('Create-only output exists')
    candidate = json.loads(a.candidate.read_text())
    rows = []
    checks = []
    for direction, b, q2 in [
        ('x_axis', mp.mpf(0), (1, 0, 0)),
        ('y_axis', mp.mpf(0), (0, 1, 0)),
        ('mixed_3_5_4_5', T/2, (mp.mpf(9)/25, mp.mpf(16)/25, 0)),
    ]:
        old = next(r for r in candidate['records']
                   if r['direction'] == direction and mp.mpf(r['birth_s']) == b)
        base, perturbed = values(b, q2, 0), values(b, q2, 1)
        changes = {k: perturbed[k]/base[k]-1 for k in base if k != 'theta'}
        differences = {k: abs(changes[k]-mp.mpf(old['actual_fractional_changes'][k]))
                       for k in changes}
        checks.extend(dict(name=direction+':'+k, pass_check=bool(err < mp.mpf('2e-18')),
                           absolute_discrepancy=str(err)) for k, err in differences.items())
        rows.append(dict(direction=direction, birth_s=str(b),
                         baseline_theta=str(base['theta']),
                         candidate_baseline_theta_relative_difference=str(
                             abs(base['theta']/mp.mpf(old['baseline']['theta'])-1)),
                         changes={k:str(v) for k,v in changes.items()},
                         differences={k:str(v) for k,v in differences.items()}))
    trace = binary('1.01e-14') + binary('0.99e-14') - 2*H
    checks.append(dict(name='binary64_trace_free_exact_inputs', pass_check=(trace == 0)))
    x = rows[0]['changes']
    signs = (mp.mpf(x['energy_ev']) < 0 < mp.mpf(x['event_per_photon_s'])
             and mp.mpf(x['heat_per_photon_ev_s']) < 0
             and mp.mpf(x['observed_angle_event']) < 0
             and mp.mpf(x['observed_angle_heat']) < 0)
    checks.append(dict(name='x_axis_rate_heat_measure_signs', pass_check=bool(signs)))
    out = dict(task='REI-PHYS20-20261010', role='independent decision reviewer spotcheck',
               method='mpmath70 tanh-sinh; independently transcribed HI formula and exact characteristic; no owner code import',
               evidence_state='numerically checked', mpmath_version=mp.__version__,
               candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               rows=rows, check_count=len(checks), failure_count=sum(not c['pass_check'] for c in checks),
               checks=checks, rigorous_enclosure=False, native_runs=0, gas_IVP_runs=0,
               physical_admission='HOLD')
    a.output.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(checks=out['check_count'], failures=out['failure_count'],
                          max_fractional_change_discrepancy=str(max(mp.mpf(v) for r in rows for v in r['differences'].values())))))
    if out['failure_count']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
