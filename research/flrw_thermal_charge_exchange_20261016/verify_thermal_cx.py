#!/usr/bin/env python3
"""Bounded new-unit verification; cached exact references are never recomputed."""
from dataclasses import asdict, replace
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import traceback

from thermal_cx import (KB_EV_K, State, Defect, RateProvider, Controls, SAVIN2002,
    ReducedSystem, integrate, heun_step, state_at_temperature)

ROOT = Path(__file__).resolve().parent
EPS128 = 128*sys.float_info.epsilon


def fixture_inputs(item, common):
    case = dict(common, **item)
    state = state_at_temperature(*(case[k] for k in ('h0','hp','d0','dp')), case['T0_K'])
    defect = Defect(case['beta']*state.thermal_eV_cm3, 'Manufactured signed beta*u0')
    observed = []
    def rates(t):
        observed.append(t)
        assert case['Tmin_K'] <= t <= case['Tmax_K'], 'out-of-domain provider invocation'
        k = case['k0_cm3_s']*t/case['T0_K']
        return k, k
    provider = RateProvider('Manufactured equal k0*T/T0', case['Tmin_K'], case['Tmax_K'], rates)
    return case, state, defect, provider, observed


def ledger(state, defect, result):
    assert result['status'] != 'INVALID_INPUT', result
    a,b,c,d = (state.h0,state.hp,state.d0,state.dp)
    n = result['four_densities']
    x = result['extent_cm3']
    values = list(n.values())+[result['thermal_eV_cm3']]
    assert all(v >= 0 and __import__('math').isfinite(v) for v in values)
    checks = {
        'hydrogen': (n['h0']+n['hp']-(a+b), max(1, a+b)),
        'deuterium': (n['d0']+n['dp']-(c+d), max(1, c+d)),
        'charge': (n['hp']+n['dp']-(b+d), max(1,b+d)),
        'baryons': (n['h0']+n['hp']+2*(n['d0']+n['dp'])-(a+b+2*(c+d)), max(1,a+b+2*(c+d))),
    }
    u0 = state.thermal_eV_cm3
    scale = max(1e-30,abs(u0),abs(defect.delta_chi_eV*x))
    checks['energy'] = (result['thermal_eV_cm3']+defect.delta_chi_eV*x-u0, scale)
    for residual, denominator in checks.values():
        assert abs(residual) <= EPS128*denominator, checks
    if result['temperature_K'] is not None:
        t0 = u0/(1.5*KB_EV_K*(a+b+c+d+b+d))
        change = abs(result['temperature_K']-t0)
        ceiling = result['temperature_amplitude_ceiling_K']
        assert change <= ceiling+EPS128*max(1,t0,change,ceiling)
    assert result['maximum_accepted_local_error_ratio'] <= 1
    return {k:{'residual':v[0], 'scale':v[1], 'scaled_absolute':abs(v[0])/v[1]} for k,v in checks.items()}


def run_c6(fixtures, probe):
    rows, controls = [], []
    oracles = {r['id']:r for r in probe['manufactured_oracles']}
    for item in fixtures['manufactured_cases']:
        case, state, defect, provider, observed = fixture_inputs(item, fixtures['manufactured_common'])
        before = asdict(state)
        answer = integrate(state, defect, provider, case['t_requested_s'])
        assert asdict(state) == before
        oracle = oracles[item['id']]
        error = abs(answer['extent_cm3']-float(oracle['xi_cm3']))/max(state.h0,state.hp,state.d0,state.dp)
        if oracle['oracle_status'] == 'COMPLETE':
            assert answer['full_interval_complete'] and error <= 5e-6, (item['id'], answer, error)
            crossing_difference = None
        else:
            assert answer['status'] == 'DOMAIN_BOUNDARY_APPROACH' and not answer['full_interval_complete'], answer
            assert answer['t_reached_s'] < answer['t_requested_s']
            assert answer['distance_to_boundary_cm3']/max(state.h0,state.hp,state.d0,state.dp) <= answer['event_atol_normalized']
            assert abs(answer['provider_boundary_if_approached']['extent_cm3']-float(oracle['xi_cm3'])) <= EPS128*max(1,abs(float(oracle['xi_cm3'])))
            crossing_difference = answer['t_reached_s']-float(oracle['oracle_time_s'])
        rows.append({'id':item['id'],'result':answer,'normalized_error_vs_cached_oracle':error,
            'crossing_time_difference_s_diagnostic':crossing_difference,'oracle_status':oracle['oracle_status'],
            'ledger':ledger(state,defect,answer),'provider_calls_observed':len(observed),
            'provider_temperature_range_K':[min(observed),max(observed)] if observed else None})
    case, state, defect, provider, _ = fixture_inputs(fixtures['manufactured_cases'][1], fixtures['manufactured_common'])
    def check(name, answer, expected, extra=None):
        assert answer['status'] == expected, (name, answer)
        if extra: extra(answer)
        controls.append({'id':name,'result':answer})
    check('dt0',integrate(state,defect,provider,0),'COMPLETE',lambda r: r['rhs_calls']==0 or (_ for _ in ()).throw(AssertionError()))
    empty = State(0,0,0,0,0)
    check('empty',integrate(empty,defect,provider,3),'COMPLETE_EMPTY',lambda r: r['temperature_K'] is None or (_ for _ in ()).throw(AssertionError()))
    check('empty_nonzero_thermal',integrate(replace(empty,thermal_eV_cm3=1),defect,provider,3),'INVALID_INPUT')
    nod = state_at_temperature(1,1,0,0,10)
    check('no_deuterium',integrate(nod,defect,provider,3),'COMPLETE_EQUILIBRIUM')
    zero = RateProvider('Manufactured zero',2.7,30,lambda t:(0.,0.))
    check('zero_rates',integrate(state,defect,zero,3),'COMPLETE_EQUILIBRIUM')
    outside = state_at_temperature(1,3,2,1,1)
    check('outside_domain_dt0',integrate(outside,defect,provider,0),'INVALID_INPUT')
    check('negative_density',integrate(replace(state,h0=-1),defect,provider,1),'INVALID_INPUT')
    check('nonfinite_density',integrate(replace(state,dp=float('nan')),defect,provider,1),'INVALID_INPUT')
    check('nonfinite_defect',integrate(state,Defect(float('inf'),'bad'),provider,1),'INVALID_INPUT')
    check('negative_time',integrate(state,defect,provider,-1),'INVALID_INPUT')
    check('invalid_provider_metadata',integrate(state,defect,replace(provider,minimum_K=0),1),'INVALID_INPUT')
    check('invalid_controls',integrate(state,defect,provider,1,Controls(max_attempts=0)),'INVALID_INPUT')
    limited = integrate(state,defect,provider,2,Controls(max_attempts=1))
    check('forced_work_cap',limited,'WORK_LIMIT',lambda r: not r['full_interval_complete'] and r['t_reached_s']<2 or (_ for _ in ()).throw(AssertionError()))
    ledger(state,defect,limited)
    def fails(t): raise RuntimeError('intentional provider failure')
    check('provider_exception',integrate(state,defect,replace(provider,rates=fails),1),'ARITHMETIC_FAILURE',lambda r: r['rhs_calls']==1 or (_ for _ in ()).throw(AssertionError()))
    check('provider_negative',integrate(state,defect,replace(provider,rates=lambda t:(-1,1)),1),'ARITHMETIC_FAILURE')
    check('provider_nonfinite',integrate(state,defect,replace(provider,rates=lambda t:(float('nan'),1)),1),'ARITHMETIC_FAILURE')
    check('rhs_work_cap',integrate(state,defect,provider,1,Controls(max_rhs_calls=1)),'WORK_LIMIT')
    # Exact unit conversion only; no Rust/native replay.
    system = ReducedSystem(state,defect,provider)
    g_unit = system.field(0)
    n_si = [v*1e6 for v in (state.h0,state.hp,state.d0,state.dp)]
    kf,kr = provider.rates(system.t0)
    g_si = ((kf*1e-6)*n_si[2]*n_si[1]-(kr*1e-6)*n_si[3]*n_si[0])/max(n_si)
    assert abs(g_unit-g_si) <= EPS128*max(1,abs(g_unit),abs(g_si))
    return {'manufactured':rows,'controls':controls,'conversion':{'G_unit_s-1':g_unit,'G_SI_s-1':g_si,'difference':g_unit-g_si},'all_checks_PASS':True}


def run_c7(fixtures, probe):
    savin = []
    for case in fixtures['savin_cases']:
        state = state_at_temperature(*(case[k] for k in ('h0','hp','d0','dp')),case['T0_K'])
        defect = Defect(case['delta_chi_eV'],'Conditional supplied 0.0037 eV; independent of fit exponents')
        default = integrate(state,defect,SAVIN2002,case['t_requested_s'])
        tight = integrate(state,defect,SAVIN2002,case['t_requested_s'],Controls(**fixtures['tighter_pair']))
        records = []
        for result in (default,tight):
            assert result['status'] in ('COMPLETE','COMPLETE_EQUILIBRIUM','DOMAIN_BOUNDARY_APPROACH'),result
            assert SAVIN2002.minimum_K <= result['temperature_K'] <= SAVIN2002.maximum_K
            records.append(ledger(state,defect,result))
        savin.append({'id':case['id'],'scope':'Actual Savin literature fits on synthetic isolated fixed-volume H/D state',
            'input':asdict(state),'defect':asdict(defect),'default':default,'tighter':tight,'ledger':records,
            'pair_extent_difference_cm3_diagnostic':abs(default['extent_cm3']-tight['extent_cm3']),
            'pair_temperature_difference_K_diagnostic':abs(default['temperature_K']-tight['temperature_K']),
            'pair_reached_time_difference_s_diagnostic':abs(default['t_reached_s']-tight['t_reached_s'])})
    item = next(r for r in fixtures['manufactured_cases'] if r['id']=='forward_feedback')
    case,state,defect,provider,_ = fixture_inputs(item,fixtures['manufactured_common'])
    exact = float(next(r for r in probe['manufactured_oracles'] if r['id']==item['id'])['xi_cm3'])
    refinement = []
    for steps in fixtures['fixed_heun_refinement']['steps']:
        system = ReducedSystem(state,defect,provider)
        z = 0.
        for _ in range(steps): z = heun_step(system,z,case['t_requested_s']/steps,system.field)
        x = z*system.scale
        refinement.append({'steps':steps,'step_s':case['t_requested_s']/steps,'extent_cm3':x,'absolute_error_cm3':abs(x-exact)})
    ratios = [refinement[i]['absolute_error_cm3']/refinement[i+1]['absolute_error_cm3'] for i in (0,1)]
    assert all(3<=r<=5 for r in ratios),ratios
    assert all(refinement[i+1]['absolute_error_cm3']<refinement[i]['absolute_error_cm3'] for i in (0,1))
    return {'savin':savin,'fixed_heun_refinement':refinement,'refinement_ratios':ratios,'cached_exact_extent_cm3':exact,'all_checks_PASS':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['C6','C7'],required=True)
    args=parser.parse_args()
    out=ROOT/'coding_evidence'
    start_wall,start_cpu=time.perf_counter(),time.process_time()
    fixtures=json.loads((ROOT/'FIXTURES.json').read_text())
    probe=json.loads((ROOT/'probe/RESULTS.json').read_text())
    status,code='completed',0
    try:
        results=(run_c6 if args.stage=='C6' else run_c7)(fixtures,probe)
    except Exception:
        status,code='failed',1
        results={'all_checks_PASS':False,'traceback':traceback.format_exc()}
        print(results['traceback'])
    elapsed,cpu=time.perf_counter()-start_wall,time.process_time()-start_cpu
    prior=sum(json.loads(p.read_text())['wall_seconds'] for p in out.glob('C*_execution*.json'))
    if prior+elapsed>30:
        status,code='failed',1
        results['budget_failure']='Cumulative test wall exceeded30s'
    execution={'stage':args.stage,'status':status,'exit_code':code,'command_argv':[sys.executable,*sys.argv],
        'wall_seconds':elapsed,'cpu_seconds':cpu,'cumulative_test_wall_seconds':prior+elapsed,'python':sys.version,
        'platform':platform.platform(),'requested_model':'lower-tier implementation agent','observed_model':'unknown',
        'private_model_telemetry':'not exposed','threads':1,'native_runs':0,'old_suite_runs':0,'external_reference_runs':0,
        'independent_probe_replays':0,'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['thermal_cx.py','verify_thermal_cx.py','FIXTURES.json','CONTRACT.json','probe/RESULTS.json']}}
    resultpath=out/(args.stage+'_results.json')
    execpath=out/(args.stage+'_execution.json')
    if resultpath.exists() or execpath.exists(): raise RuntimeError('Preserve prior evidence; use authorized repair-specific paths')
    resultpath.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    execpath.write_text(json.dumps(execution,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'stage':args.stage,'status':status,'wall_seconds':elapsed,'cpu_seconds':cpu,'cumulative_test_wall_seconds':prior+elapsed,'results':str(resultpath)}))
    return code

if __name__=='__main__': raise SystemExit(main())
