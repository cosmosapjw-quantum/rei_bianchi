#!/usr/bin/env python3
"""Exact analysis of completed local evidence; no vendor/kernel imports."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
from common import *

def semantic(result):
    projection = {k: result[k] for k in ('schema', 'work', 'path_input_sha256', 'source_lock_sha256',
        'input_checks', 'new_local_enclosures', 'new_coefficient_evaluations', 'rounding_operation_counts', 'forbidden_invocations')}
    projection['track'] = {k: v for k, v in result['track'].items() if k != 'elapsed_seconds'}
    return hashlib.sha256(b'bass-he-e13c7-path-numerical-v1\n' + canonical(projection)).hexdigest()

def load_complete(root, path, index, source_lock_sha):
    receipt, result, admission = [read(path / n) for n in ('COMPLETE.json', 'RESULT.json', 'ADMISSION.json')]
    if (path / 'FAILURE.json').exists() or receipt['status'] != 'COMPLETE':
        raise ValueError('failed or incomplete local path')
    if sha(path / 'RESULT.json') != receipt['result_sha256'] or sha(path / 'ADMISSION.json') != receipt['admission_sha256']:
        raise ValueError('completed evidence byte identity mismatch')
    if semantic(result) != receipt['semantic_sha256']:
        raise ValueError('completed numerical semantic mismatch')
    w = result['work']; node = w['node']; rec = index[str(node)]
    for o in (receipt, result, admission):
        if o['source_lock_sha256'] != source_lock_sha or o['path_input_sha256'] != rec['path_input_sha256']:
            raise ValueError('completed source/input identity mismatch')
    if any(result['forbidden_invocations'].values()):
        raise ValueError('forbidden invocation reported')
    with (root / 'inputs/OFF_OLD_PATHS.jsonl').open('rb') as f:
        f.seek(rec['offset']); raw = f.read(rec['bytes'])
    if hashlib.sha256(raw).hexdigest() != rec['old_line_sha256']:
        raise ValueError('old source line mismatch')
    old = json.loads(raw)
    weight = box(old['weight'])[0]
    oldm, newm = old_metrics(old), new_metrics(result['track'], weight)
    rows = compare_metrics(oldm, newm)
    if admission['old_weighted'] != encode_metrics(oldm) or admission['new_raw_weighted'] != encode_metrics(newm) or rows != admission['comparisons']:
        raise ValueError('exact local saved definition/comparison mismatch')
    if not all(r['overlap'] for r in rows) or admission['intersection_used']:
        raise ValueError('nonoverlap or undeclared interval intersection')
    display_path = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    return {'path': display_path, 'result': result, 'receipt': receipt,
            'admission': admission, 'old': oldm, 'new': newm, 'weight': weight}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args(); root = a.package.resolve(); out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    index = read(root / 'inputs/INPUT_INDEX.json')['records']
    contract = read(root / 'RESEARCH_CONTRACT.json')
    locksha = sha(root / 'SOURCE_LOCK.json')
    records = {}
    for p in sorted((root / 'runs').rglob('COMPLETE.json')):
        if p.parent.name.startswith('node_'):
            x = load_complete(root, p.parent, index, locksha)
            w = x['result']['work']; k = (w['node'], w['N'], w['precision'])
            if k in records:
                raise ValueError('duplicate scientific work item in local runs: ' + str(k))
            records[k] = x
    expected = {(n, 512, 60) for n in contract['local_primary_nodes']}
    expected |= {(n, 1024, 60) for n in contract['local_resolution_diagnostic_nodes']}
    expected |= {(n, s, p) for n in contract['local_branch_control_nodes'] for s, p in ((32,60), (32,80), (128,60))}
    if set(records) != expected:
        raise ValueError('exact local work-unit coverage mismatch: ' + str(sorted(expected - set(records))))
    primary = [records[(n, 512, 60)] for n in contract['local_primary_nodes']]
    if not all(x['admission']['mechanically_admissible'] for x in primary):
        raise ValueError('one or more primary N512 paths is not eligible for raw replacement')
    chosen = []
    resolution = []
    for node in contract['local_primary_nodes']:
        x = records[(node,512,60)]
        if node in contract['local_resolution_diagnostic_nodes']:
            y = records[(node,1024,60)]
            rows = compare_metrics(x['new'], y['new'])
            eligible = y['admission']['mechanically_admissible'] and all(r['nested'] and r['width_nonincreasing'] for r in rows)
            resolution.append({'node': node, 'rows_N512_to_N1024': rows,
                'raw_N1024_eligible_over_N512': eligible, 'seconds_N512': x['result']['elapsed_seconds'],
                'seconds_N1024': y['result']['elapsed_seconds'],
                'observed_time_ratio': y['result']['elapsed_seconds'] / x['result']['elapsed_seconds']})
            if eligible:
                x = y
        chosen.append(x)
    # Every set is disjoint and directly summed; no interval subtraction.
    pred = read(root / 'inputs/PREDECESSOR_BUDGET.json')
    local_sum = sum_metrics(x['new'] for x in chosen)
    primary_sum = sum_metrics(x['new'] for x in primary)
    retained = sum_metrics([decode_metrics(pred['prior_six']), decode_metrics(pred['old_ncp_2331'])])
    full = sum_metrics([retained, local_sum])
    full_primary = sum_metrics([retained, primary_sum])
    old_full = decode_metrics(pred['E13C6_full'])
    if sum_metrics([retained, decode_metrics(pred['old_local_eight'])]) != old_full:
        raise ValueError('predecessor direct local/retained bridge mismatch')
    full_rows = compare_metrics(old_full, full)
    if not all(r['nested'] and r['width_nonincreasing'] for r in full_rows):
        raise ValueError('full local-refined raw interval is not nested')
    precision_rows = []
    for n in contract['local_branch_control_nodes']:
        x, y = records[(n,32,60)], records[(n,32,80)]
        for row in compare_metrics(x['new'], y['new']):
            u, v = box(row['old']), box(row['new_raw'])
            width = u[1] - u[0]
            shift = max(abs(v[0]-u[0]), abs(v[1]-u[1]))
            precision_rows.append({'node': n, 'kind': row['kind'], 'quantity': row['quantity'],
                'overlap': row['overlap'], 'max_endpoint_shift': str(shift),
                'shift_over_P60_width': str(shift/width) if width else None,
                'zero_width_equal': (u == v) if not width else None})
    if not all(r['overlap'] and (r['zero_width_equal'] is not False) for r in precision_rows):
        raise ValueError('precision diagnostic mismatch')
    same_n_rows = []
    for n in contract['local_branch_control_nodes']:
        x = records[(n,128,60)]
        same_n_rows.extend({'node':n, **r} for r in x['admission']['comparisons'])
    radius = []
    for x in primary + [records[(n,1024,60)] for n in contract['local_resolution_diagnostic_nodes']]:
        t = x['result']['track']; last = t['segments'][-1]
        total = F(t['final_photon']['radius'])
        numeric = F(t['final_photon']['numerical_and_representation_radius'])
        inc = F(last['remainder']['incoming_upper']['P1'])
        coupling = F(last['remainder']['nonlinear_upper']['P1'])
        radius.append({'node':x['result']['work']['node'], 'N':x['result']['work']['N'],
            'photon_radius':str(total), 'numeric_representation':str(numeric), 'incoming':str(inc), 'coupling':str(coupling),
            'numeric_fraction':str(numeric/total), 'incoming_fraction':str(inc/total), 'coupling_fraction':str(coupling/total)})
    resource_rows = [{**x['result']['work'], 'seconds':x['result']['elapsed_seconds'],
         'peak_RSS_KiB':x['result']['peak_RSS_KiB'], 'segments':x['result']['new_local_enclosures'],
         'coefficient_evaluations':x['result']['new_coefficient_evaluations'], 'path':x['path'],
         'semantic_sha256':x['receipt']['semantic_sha256']} for _, x in sorted(records.items())]
    accepted = {'schema':'bass-he-e13c7-local-admitted-enclosures-v1', 'decision':'PENDING_INDEPENDENT_REVIEW',
        'source_lock_sha256':locksha, 'intersection_used':False,
        'paths':[{'node':x['result']['work']['node'], 'N':x['result']['work']['N'], 'precision':60,
            'path':x['path'], 'semantic_sha256':x['receipt']['semantic_sha256'], 'result_sha256':x['receipt']['result_sha256'],
            'admission_sha256':x['receipt']['admission_sha256'], 'new_raw_weighted':encode_metrics(x['new'])} for x in chosen],
        'new_local_eight':encode_metrics(local_sum), 'retained_prior_six':pred['prior_six'],
        'still_old_ncp_2331':pred['old_ncp_2331'], 'current_full_OFF':encode_metrics(full),
        'claim_ceiling':'conditional finite fixed capture; bulk refinement NOT_RUN; physical/continuum/production/receiver HOLD'}
    analysis = {'schema':'bass-he-e13c7-local-analysis-v1', 'status':'PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW',
        'source_lock_sha256':locksha, 'full_old_E13C6':encode_metrics(old_full), 'full_after_local_eight':encode_metrics(full),
        'full_after_N512_eight_only':encode_metrics(full_primary), 'full_comparison':full_rows,
        'resolution_comparison':resolution, 'precision_comparison':precision_rows, 'same_N128_comparison':same_n_rows,
        'radius_components':radius, 'resource_rows':resource_rows,
        'actual_counts':{'scientific_path_work_items':len(records), 'fresh_local_enclosures':sum(r['segments'] for r in resource_rows),
           'coefficient_evaluations':sum(r['coefficient_evaluations'] for r in resource_rows),
           'prior_scientific_reruns':0, 'ODE_solves':0, 'gas_advances':0, 'native_runs':0, 'NCP_new_batch_paths':0},
        'new_work_items_eligible_for_primary_admission':len(chosen), 'intersection_used':False,
        'same_N128_new_formula_advantage':'NOT_ESTABLISHED', 'full_2331_refinement':'NOT_RUN'}
    save(out / 'LOCAL_ANALYSIS.json', analysis)
    save(out / 'LOCAL_ADMITTED_CANDIDATE.json', accepted)
    buf = io.StringIO(newline='')
    wr = csv.writer(buf); wr.writerow(['kind','quantity','old_width_exact','local_refined_width_exact','gain_percent','old_width_display','local_refined_width_display'])
    for r in full_rows:
        ow, nw = F(r['old_width']), F(r['new_width'])
        wr.writerow([r['kind'],r['quantity'],str(ow),str(nw),decimal_display(100*(ow-nw)/ow) if ow else 'EXACT_ZERO',decimal_display(ow),decimal_display(nw)])
    save_bytes(out / 'LOCAL_FULL_WIDTHS.csv', buf.getvalue().encode())
    identity = hashlib.sha256(b'bass-he-e13c7-local-analysis-v1\n' + canonical(analysis)).hexdigest()
    save(out / 'ANALYSIS_IDENTITY.json', {'analysis_semantic_sha256':identity,'analysis_file_sha256':sha(out/'LOCAL_ANALYSIS.json'),
         'csv_sha256':sha(out/'LOCAL_FULL_WIDTHS.csv'),'candidate_sha256':sha(out/'LOCAL_ADMITTED_CANDIDATE.json')})
    summary = {'status':analysis['status'],'counts':analysis['actual_counts'],'selected_resolutions':{str(x['node']):x['N'] for x in accepted['paths']},
        'full_photon_gain_percent':next(decimal_display(100*F(r['gain_fraction'])) for r in full_rows if r['kind']=='absolute' and r['quantity']=='P_final'),
        'full_heat_gain_percent':next(decimal_display(100*F(r['gain_fraction'])) for r in full_rows if r['kind']=='absolute' and r['quantity']=='H_total_eV'),
        'analysis_semantic_sha256':identity}
    print(json.dumps(summary,sort_keys=True))

if __name__ == '__main__':
    main()
