#!/usr/bin/env python3
"""Review-gated 24-field diagnostics for an explicitly resumed G2 trajectory.

No science ODE/native call. No normal comparator status is forced or changed.
"""
from __future__ import annotations
import argparse,importlib.util,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import checkpoint as cp
import postprocess_continuation as continued
spec=importlib.util.spec_from_file_location('q1a_original_compare',HERE.parent/'compare.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
read,sha,metric,pair_identities=original.read,original.sha,original.metric,original.pair_identities
FIELDS,MOMENTS,REQUIRED_CHECKS=original.FIELDS,original.MOMENTS,original.REQUIRED_CHECKS

def load_continuation_run(run, review):
    chain, manifest = continued.verify_chain(run)
    cp.require(review.get('schema') == 'rei.q1a.actual_continuation_review.v1' and review.get('decision') == 'ALLOW_DIAGNOSTIC_COMPARISON', 'ACTUAL_CHAIN_REVIEW_REQUIRED')
    cp.require(review.get('chain_sha256') == sha(run/'CONTINUATION.json') and review.get('result_sha256') == sha(run/'RESULT.json') and review.get('continuation_driver_sha256') == chain['resume_driver_sha256'], 'ACTUAL_REVIEW_BINDING')
    result = read(run/'RESULT.json')
    identity = read(run/'IDENTITY.json')
    moments = read(run/'CONTINUATION_MOMENTS.json')
    cp.require(moments['continuation']['wrapper_sha256'] == sha(HERE/'postprocess_continuation.py'), 'CONTINUATION_POSTPROCESS_CHANGED')
    grid = read(run/'GRID.json')
    if result['status'] != 'COMPUTED_NOT_REVIEWED' or moments['status'] != 'POSTPROCESSED_CONTINUATION_PENDING_CHAIN_REVIEW':
        raise ValueError('INCOMPLETE_RUN_OR_UNBOUND_MOMENTS:'+str(run))
    if not moments['identity_checks'] or not all(v is True for v in moments['identity_checks'].values()):
        raise ValueError('MOMENT_IDENTITY_FAILURE:'+str(run))
    required_files = {'IDENTITY.json', 'RESULT.json', 'history.npz', 'EVENTS.json',
        'driver_as_run.py', 'base_driver_as_run.py', 'fixed_grid_as_run.py',
        'characteristics_as_run.py', 'events_as_run.py', 'GRID.json'}
    required_files.update(['CONTINUATION_START.json','CONTINUATION.json','CONTINUATION_MANIFEST.json','resume_driver_as_run.py','resume_checkpoint_as_run.py', *['predecessor/'+k for k in chain['original_files_sha256']]])
    if not required_files.issubset(moments['saved_file_sha256']):
        raise ValueError('INCOMPLETE_MOMENT_FILE_BINDING:'+str(run))
    for name, expected in moments['saved_file_sha256'].items():
        if sha(run/name) != expected:
            raise ValueError('STALE_MOMENT_INPUT:'+str(run/name))
    if sha(HERE.parent/'postprocess.py') != moments['implementation_sha256']:
        raise ValueError('POSTPROCESS_IMPLEMENTATION_CHANGED:'+str(run))
    geometry = moments['geometry_preflight']
    preflight_path = run/geometry['relative_path']
    if sha(preflight_path) != geometry['sha256']:
        raise ValueError('GEOMETRY_PREFLIGHT_CHANGED:'+str(run))
    preflight = read(preflight_path)
    geometry_rows = [r for r in preflight['grids'].values()
                     if r['grid_arrays_sha256'] == identity['grid_arrays_sha256']]
    if (len(geometry_rows) != 1 or geometry['grid_arrays_sha256'] != identity['grid_arrays_sha256']
        or geometry['grid_sha256'] != identity['grid_sha']
        or geometry_rows[0]['grid_sha256'] != identity['grid_sha']
        or geometry_rows[0]['geometry_max'] != geometry['geometry_max']):
        raise ValueError('GEOMETRY_GRID_BINDING:'+str(run))
    if len(result['history']) != 129 or len(moments['history']) != 129:
        raise ValueError('REQUIRES_129_EPOCHS:'+str(run))
    tr = np.array([r['time_s'] for r in result['history']])
    tm = np.array([r['time_s'] for r in moments['history']])
    zr = np.array([r['z'] for r in result['history']])
    zm = np.array([r['z'] for r in moments['history']])
    if not np.array_equal(tr, tm) or not np.array_equal(zr, zm):
        raise ValueError('RESULT_MOMENT_EPOCH_MISMATCH:'+str(run))
    checks = {key: result['checks'].get(key) is True for key in REQUIRED_CHECKS}
    energy = max(result['max_endpoint_energy_ledger'], max(abs(r['energy_ledger_scaled']) for r in result['history']))
    number = max(result['max_endpoint_number_ledger'], max(abs(r['number_ledger_scaled']) for r in result['history']))
    checks['combined_energy_ledger'] = bool(np.isfinite(energy) and energy <= 1e-9)
    checks['combined_number_ledger'] = bool(np.isfinite(number) and number <= 1e-9)
    checks['combined_energy_report_exact'] = energy == result['max_energy_ledger']
    checks['combined_number_report_exact'] = number == result['max_number_ledger']
    checks['accepted_gas_moment_report'] = moments['accepted_gas_domain'] is True
    checks['geometry_preflight'] = bool(geometry['passed'] is True and geometry['frozen_budget'] == 1e-11
        and np.isfinite(geometry['geometry_max']) and geometry['geometry_max'] <= 1e-11
        and geometry_rows[0]['gates']['geometry'] is True)
    return result, identity, moments, grid, checks, dict(energy=energy, number=number)


def diagnostic_compare(coarse, fine, review):
    kind = 'spectral'
    ar, ai, am, ag, ac, al = original.load_bound_run(coarse)
    br, bi, bm, bg, bc, bl = load_continuation_run(fine, review)
    identities = pair_identities(ai, bi, ag, bg, kind)
    times = np.array([r['time_s'] for r in ar['history']])
    tf = np.array([r['time_s'] for r in br['history']])
    if not np.isfinite(times).all() or not np.array_equal(times, tf):
        raise ValueError('SHARED_EPOCH_MISMATCH')
    if not np.array_equal([r['z'] for r in ar['history']], [r['z'] for r in br['history']]):
        raise ValueError('SHARED_REDSHIFT_MISMATCH')
    budget = 1e-3 if kind == 'spectral' else 2e-6
    comparisons = {}
    for count, epochs in [('129', np.arange(129)), ('65', np.arange(0, 129, 2))]:
        rows = {}
        for fields, left, right in [(FIELDS, ar, br), (MOMENTS, am, bm)]:
            for key in fields:
                value = metric([r[key] for r in left['history']], [r[key] for r in right['history']], epochs, budget)
                value.update(worst_time_s=float(times[value['worst_epoch_index']]),
                    worst_z=float(br['history'][value['worst_epoch_index']]['z']),
                    required_for_gate=kind == 'spectral' or key in FIELDS)
                rows[key] = value
        required = {key: value for key, value in rows.items() if value['required_for_gate']}
        comparisons[count] = dict(fields=rows,
            pass_required_fields=all(value['pass_budget'] for value in required.values()),
            pass_all_reported_fields=all(value['pass_budget'] for value in rows.values()),
            max_required_scaled_error=max(value['scaled_error'] for value in required.values()),
            max_all_scaled_error=max(value['scaled_error'] for value in rows.values()))
    checks = {'coarse': ac, 'fine': bc}
    passed = all(identities.values()) and all(all(v.values()) for v in checks.values()) and all(v['pass_required_fields'] for v in comparisons.values())
    prefix = 'SPECTRAL' if kind == 'spectral' else 'TIME'
    return dict(status='CONTINUED_TRAJECTORY_DIAGNOSTIC_NOT_ADMITTED',
        kind=kind, all_recorded_field_and_conservation_checks_pass=passed,
        scientific_admission=False, time_convergence_inherited=False,
        executed_control_source_equal=False, extra_BDF_initializations_in_fine=1,
        continuation_chain_sha256=sha(fine/'CONTINUATION.json'),
        actual_chain_review=review,
        interpretation='Operator identity is chain-verified; extra BDF initialization differs. These are unchanged field diagnostics, not a standard comparator PASS or time certificate.',
        method='max_abs(coarse-fine) / max_abs(fine), each selected whole-history epoch set using its own fine amplitude; 65 retains original sampling and129 is additional. Exact zero fine amplitude requires exact zero difference.',
        frozen_field_budget=budget, required_fields=FIELDS+MOMENTS if kind == 'spectral' else FIELDS,
        diagnostic_only_fields=[] if kind == 'spectral' else MOMENTS,
        identity_checks=identities, native_checks=checks, combined_ledgers={'coarse': al, 'fine': bl},
        comparisons=comparisons,
        geometry_preflight={'coarse': am['geometry_preflight'], 'fine': bm['geometry_preflight']},
        coarse_all_accepted_gas_domain=ar['checks'].get('accepted_gas_domain', 'NOT_MEASURED'),
        fine_all_accepted_gas_domain=br['checks'].get('accepted_gas_domain', 'NOT_MEASURED'),
        angular_status='NOT_EVALUATED', continuum_error_bound='NOT_ESTABLISHED',
        scientific_ceiling='Conditional FLRW source-band-limited primary-only CaseA gas+photon history, isotropic CMB bath; no CR/RCT, Bianchi signal or observer visibility admission.',
        files={str(x): sha(x) for d in (coarse, fine) for x in [d/'RESULT.json', d/'IDENTITY.json', d/'history.npz', d/('MOMENTS.json' if d==coarse else 'CONTINUATION_MOMENTS.json'), d/'GRID.json']},
        postprocess_code_sha256=sha(HERE.parent/'postprocess.py'), comparison_code_sha256=sha(__file__))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('coarse',type=Path);parser.add_argument('continued_fine',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--actual-chain-review',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    value=diagnostic_compare(args.coarse,args.continued_fine,read(args.actual_chain_review))
    value['actual_chain_review_file_sha256']=sha(args.actual_chain_review)
    value['original_comparator_sha256']=sha(HERE.parent/'compare.py')
    with args.output.open('x') as h:json.dump(value,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ('comparisons','files','geometry_preflight','actual_chain_review')},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
