#!/usr/bin/env python3
"""Independent exact saved-evidence audit; never import a scientific kernel.

The reviewer reconstructs interval arithmetic and admission from Decimal text
as exact Fractions. This does not reevaluate captured coefficients, manufacture
new controls, or invoke any old/new path integrator. Mathematical/source review
is a separate human-readable part of the independent decision.
"""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import time
import traceback

SP = ('HI', 'HeI', 'HeII')
CHI = tuple(F.from_float(x) for x in (13.598434599702, 24.587389011, 54.41776))
MOM = ['Z_eV', 'QN', 'QE_eV'] + [p+'_'+s+('_eV' if p!='A' else '') for p in ('A','B','H') for s in SP]


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def write(path, x):
    with Path(path).open('x') as f:
        json.dump(x, f, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
        f.write('\n')


def point(x):
    y = F(x)
    return y, y


def box(x):
    a, b = F(x['lo']), F(x['hi'])
    if a > b:
        raise ValueError('invalid saved interval')
    return a, b


def enc(x):
    return {'lo': str(x[0]), 'hi': str(x[1])}


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[1], -a[0]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    x = [v*w for v in a for w in b]
    return min(x), max(x)


def scale(a, x):
    return mul(a, point(x))


def sum_boxes(seq):
    a = point(0)
    for b in seq:
        a = add(a, b)
    return a


def contains(a, b):
    return a[0] <= b[0] <= b[1] <= a[1]


def width(a):
    return a[1]-a[0]


def abs_upper(a):
    return max(abs(a[0]), abs(a[1]))


def sym(x):
    x = F(x)
    if x < 0:
        raise ValueError('negative radius')
    return -x, x


def capture(x):
    y = float(x)
    if not math.isfinite(y):
        raise ValueError('nonfinite captured binary64')
    return F.from_float(y)


def display(x, precision=30):
    with localcontext() as c:
        c.prec = precision
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def metrics(track, weight):
    absolute = {k: scale(box(track['true_moment_enclosures'][k]), weight) for k in MOM}
    absolute['P_final'] = scale(box(track['final_photon']['true_absolute_interval']), weight)
    absolute['anchor'] = scale(box(track['summed_true_anchor_eV']), weight)
    correction = {k: scale(box(track['cumulative_moment_corrections'][k]['interval']), weight) for k in MOM}
    correction['P_final'] = scale(box(track['final_photon']['true_minus_captured_interval']), weight)
    correction['energy_eV'] = scale(box(track['final_energy_stock_eV']['true_minus_captured_interval']), weight)
    for collection in (absolute, correction):
        for p in ('A','B','H'):
            suffix = '_eV' if p != 'A' else ''
            collection[p+'_total'+suffix] = sum_boxes(collection[p+'_'+s+suffix] for s in SP)
    return {'absolute': absolute, 'correction': correction}


def compare(old, new):
    rows = []
    for kind in sorted(old):
        if set(old[kind]) != set(new[kind]):
            raise ValueError('metric set mismatch')
        for k in sorted(old[kind]):
            a, b = old[kind][k], new[kind][k]
            wa, wb = width(a), width(b)
            rows.append({'kind':kind, 'quantity':k, 'old':enc(a), 'new_raw':enc(b),
                'nested':contains(a,b), 'width_nonincreasing':wb<=wa,
                'overlap':max(a[0],b[0])<=min(a[1],b[1]),
                'old_width':str(wa), 'new_width':str(wb),
                'gain_fraction':str((wa-wb)/wa) if wa else None})
    return rows


class Audit:
    def __init__(self):
        self.counts = {}
        self.failures = []

    def check(self, group, name, value):
        self.counts[group] = self.counts.get(group, 0)+1
        if not value:
            self.failures.append({'group':group, 'check':name})
            raise AssertionError(group+': '+name)

    def enclosure(self, group, name, saved, exact):
        self.check(group, name, contains(box(saved), exact))


def check_pin(audit, base, relative, pin, group='byte_identity'):
    p = (base/relative).resolve()
    audit.check(group, relative+'/path', p.is_relative_to(base.resolve()) and p.is_file())
    audit.check(group, relative+'/bytes', p.stat().st_size == pin['bytes'])
    audit.check(group, relative+'/sha256', sha(p) == pin['sha256'])
    return p


def load_controls(root7, nodes, audit):
    stages = {int(r['step']):r for r in csv.DictReader((root7/'inputs/source/OFF_STAGES.csv').open())}
    node_rows = {(int(r['step']),int(r['node'])):r for r in csv.DictReader((root7/'inputs/source/OFF_NODES.csv').open())}
    controls = {n:[] for n in nodes}
    for r in csv.DictReader((root7/'inputs/source/OFF_SEGMENTS.csv').open()):
        n, step = int(r['node']), int(r['step'])
        if n in controls and step in (1,2):
            controls[n].append({'key':['OFF',step,n,int(r['segment'])], 'row':r,
                'stage':stages[step], 'node_row':node_rows[step,n],
                'mask':{s:float(r['e_mid'])>=cut for s,cut in zip(SP,(13.6,24.59,54.42))},
                'source_on':float(r['source_on']) == 1.0})
    index = read(root7/'inputs/INPUT_INDEX.json')['records']
    for node, seq in controls.items():
        seq.sort(key=lambda c:tuple(c['key']))
        ix = index[str(node)]
        with (root7/'inputs/OFF_OLD_PATHS.jsonl').open('rb') as f:
            f.seek(ix['offset']); raw = f.read(ix['bytes'])
        audit.check('input_identity', str(node)+'/old_path_line', len(raw)==ix['bytes'] and hashlib.sha256(raw).hexdigest()==ix['old_line_sha256'])
        old = json.loads(raw)
        val = hashlib.sha256(b'bass-he-e13c7-path-input-v1\n'+canonical({'controls':seq,'old_path':old})).hexdigest()
        audit.check('input_identity', str(node)+'/semantic_path', val == ix['path_input_sha256'])
        audit.check('input_identity', str(node)+'/ordered_keys', [c['key'] for c in seq]==ix['keys'])
        audit.check('input_identity', str(node)+'/initial_zero', capture(seq[0]['row']['f0'])==0)
        w = capture(seq[0]['row']['weight'])
        audit.check('input_identity', str(node)+'/positive_exact_weight', w>0 and box(old['weight'])==(w,w))
        for c in seq:
            r = c['row']
            audit.check('input_identity', str(c['key'])+'/time_width', capture(r['a'])+capture(r['h'])==capture(r['b']) and capture(r['h'])>0)
            audit.check('input_identity', str(c['key'])+'/weight_once', capture(r['weight'])==w)
    return controls, index


def audit_controls(root, audit):
    completed = []
    initial_rows = read(root/'tests/MANUFACTURED/EXEC01/CONTROL_RESULTS.json')['rows']
    initial_by_name_N = {(r['case']['name'],r['N_first']):r for r in initial_rows}
    for receipt_path in sorted((root/'tests/MANUFACTURED').glob('*/RECEIPT.json')):
        receipt, folder = read(receipt_path), receipt_path.parent
        results = read(folder/'CONTROL_RESULTS.json')
        if folder.name=='EXEC01':
            source_root=root/'evidence/SOURCE_REVISIONS/INITIAL_N32'; script_name='run_first_integral_controls.py'; script_pin=receipt['control_script_sha256']
        elif folder.name=='EXEC02_CACHED':
            source_root=root/'evidence/SOURCE_REVISIONS/SAME_N_UNREFINED'; script_name='run_cached_midpoint_controls.py'; script_pin=receipt['script_sha256']
        elif folder.name=='EXEC03_HALF_CELL':
            source_root=root; script_name='run_half_cell_controls.py'; script_pin=receipt['script_sha256']
        else:
            raise ValueError('undeclared manufactured control stage')
        audit.check('manufactured_saved',folder.name+'/source_and_contract_identity',sha(source_root/'code/first_midpoint.py')==receipt['candidate_sha256'] and sha(source_root/'SCIENTIFIC_CONTRACT.md')==receipt['contract_sha256'])
        audit.check('manufactured_saved',folder.name+'/script_identity',sha(root/'tests/MANUFACTURED'/script_name)==script_pin)
        audit.check('manufactured_saved', folder.name+'/results_identity', sha(folder/'CONTROL_RESULTS.json')==receipt['results_sha256'])
        audit.check('manufactured_saved', folder.name+'/reported_checks', all(c['pass'] for c in results['checks']) and receipt['checks_failed']==0 and len(results['checks'])==receipt['checks_passed'])
        for i, row in enumerate(results['rows']):
            # Both original and amended controls retain these source-only targets.
            for key, saved in row['signed_candidate'].items():
                audit.enclosure('manufactured_saved', f'{folder.name}/{i}/signed/{key}', saved, box(row['signed_oracle'][key]))
            for name, saved in row.get('ledger_enclosures',{}).items():
                audit.enclosure('manufactured_saved', f'{folder.name}/{i}/ledger/{name}', saved, point(0))
            for target in row.get('incoming_oracle', []):
                for key, saved in row['incoming_candidate'].items():
                    audit.enclosure('manufactured_saved', f'{folder.name}/{i}/incoming/{key}', saved, box(target['oracle'][key]))
            if receipt.get('cached_branch_only'):
                original=initial_by_name_N[(row['case']['name'],row['N_first'])]
                audit.check('manufactured_saved',f'{folder.name}/{i}/cache_identity',row['case']==original['case'] and row['midpoint_retained']==original['midpoint_candidate'])
                audit.check('manufactured_saved',f'{folder.name}/{i}/cache_hash',hashlib.sha256(canonical(row['midpoint_retained'])).hexdigest()==row['midpoint_cache_sha256'])
                audit.check('manufactured_saved',f'{folder.name}/{i}/same_uncached_result',row['signed_candidate']==original['signed_candidate'] and row['curvature_correction']==original['curvature_correction_candidate'])
                audit.check('manufactured_saved',f'{folder.name}/{i}/cache_counts',row['new_whole_cell_calls']==row['N_first']==8 and row['new_midpoint_calls']==0)
            if 'branch' in row:
                original=initial_by_name_N[(row['case']['name'],row['N_first'])]
                audit.check('manufactured_saved',f'{folder.name}/{i}/midpoint_cache_hash',hashlib.sha256(canonical(original['midpoint_candidate'])).hexdigest()==row['midpoint_cache_sha256'])
                for target in original['incoming_oracle']:
                    for key,saved in row['incoming_candidate'].items():
                        audit.enclosure('manufactured_saved',f'{folder.name}/{i}/same_target_incoming/{key}',saved,box(target['oracle'][key]))
                expected_whole=8 if row['branch']=='FRESH_PARENT_REFINED' else 0
                audit.check('manufactured_saved',f'{folder.name}/{i}/refined_call_counts',row['actual_new_whole_cell_calls']==expected_whole and row['actual_new_left_half_calls']==8 and row['actual_new_point_calls']==0)
                h=F(row['case']['h']); n=row['N_first']
                for j,cell in enumerate(row['cells']):
                    for key in row['signed_candidate']:
                        expected=scale(add(box(cell['second_derivative'][key]),box(cell['left_half_second_derivative'][key])),h/F(48*n**3))
                        audit.enclosure('manufactured_saved',f'{folder.name}/{i}/cell{j}/{key}/half_mass',cell['curvature_correction'][key],expected)
                if row['branch']=='CACHED_PARENT_REFINED':
                    fresh=next(x for x in results['rows'] if x['case']==row['case'] and x['branch']=='FRESH_PARENT_REFINED')
                    audit.check('manufactured_saved',f'{folder.name}/{i}/cached_parent_identity',row['signed_candidate']==fresh['signed_candidate'] and row['curvature_correction']==fresh['curvature_correction'] and all(c['second_derivative']==d['second_derivative'] for c,d in zip(row['cells'],fresh['cells'])))
        completed.append({'path':str(folder.relative_to(root)), 'receipt_sha256':sha(receipt_path),
            'results_sha256':receipt['results_sha256'], 'reported_checks':receipt['checks_passed'],
            'executions':receipt['executions_completed'], 'status':receipt['status']})
    audit.check('manufactured_saved','all_three_control_stages_present', {x['status'] for x in completed}=={'PASS_MANUFACTURED_FIRST_INTEGRAL_CONTROLS','PASS_CACHED_MIDPOINT_BRANCH_CONTROLS','PASS_HALF_CELL_FRESH_AND_CACHED_PARENT_CONTROLS'})
    toy = read(root/'theory/EXACT_POLYNOMIAL_CONTROLS.json')
    audit.check('theory_saved', 'polynomial_script_identity', sha(root/'theory/exact_polynomial_controls.py')==toy['source_sha256'])
    audit.check('theory_saved', 'reported_checks', toy['check_count']==len(toy['checks']) and all(r['passed'] for r in toy['checks']) and not toy['failures'])
    for i, row in enumerate(toy['rows']):
        for method in ('signed','symmetric','simpson_C2'):
            a = tuple(F(x) for x in row[method])
            audit.check('theory_saved', f'{i}/{method}/exact_integral', contains(a, point(row['exact_integral'])))
        audit.check('theory_saved', f'{i}/same_grid_nesting', contains(tuple(F(x) for x in row['symmetric']),tuple(F(x) for x in row['signed'])))
    counter = toy['cross_resolution_counterexample']
    audit.check('theory_saved', 'cross_resolution_counterexample', not contains(tuple(F(x) for x in counter['symmetric_N512']),tuple(F(x) for x in counter['signed_N32'])))
    return completed


def audit_track(audit, result, baseline, prior, controls, parent=None):
    track, oldtrack, previous = result['track'], baseline['track'], prior['track']
    node, n, m = result['work']['node'], result['work']['N_first'], result['work']['M_second']
    audit.check('path_structure', f'{node}/keys', [s['key'] for s in track['segments']]==[c['key'] for c in controls])
    audit.check('path_structure', f'{node}/segment_count', len(track['segments'])==len(oldtrack['segments'])==len(previous['segments']))
    audit.check('path_structure', f'{node}/seam_count', len(track['seams'])==len(controls)-1)
    cumulative = {k:point(0) for k in track['cumulative_moment_corrections']}
    captured = {k:point(0) for k in cumulative}
    first_count = second_count = 0
    for i, (seg, old, past, control) in enumerate(zip(track['segments'],oldtrack['segments'],previous['segments'],controls)):
        label = f'{node}/segment{i}'
        local, h = seg['local'], capture(control['row']['h'])
        keys = set(local['signed'])
        audit.check('path_structure', label+'/17_keys', len(keys)==17 and keys==set(old['local']['signed']))
        audit.check('cache_identity', label+'/N_and_P', n==baseline['work']['N'] and local['N_first']==n and local['precision_digits']==60)
        audit.check('cache_identity', label+'/midpoint', local['midpoint']==old['local']['midpoint'])
        audit.check('cache_identity', label+'/bounds', local['bounds']==old['local']['bounds'])
        audit.check('cache_identity', label+'/frozen_gains_capture', all(seg[k]==past[k] for k in ('frozen','gains','captured','endpoint_energy_eV','initial_energy_eV','native_energy_stock_minus_Eh_n_eV')))
        audit.check('cache_identity', label+'/no_new_midpoints', local['cell_coverage']['midpoint_evaluations']==0 and local['midpoint_origin']=='REUSED_IDENTITY_BOUND_AGGREGATE')
        audit.check('cache_identity', label+'/no_raw_intersection_or_fallback', local['raw_intersections']==0 and local['old_interval_fallbacks']==0)
        expected_whole=0 if parent is not None else n
        expected_first=expected_whole+n
        audit.check('cell_coverage', label+'/count', len(local['cells'])==n and local['cell_coverage']['whole_cell_derivative_evaluations']==expected_whole and local['cell_coverage']['left_half_derivative_evaluations']==n)
        audit.check('cell_coverage',label+'/refined_method',local['method']=='positive_peano_kernel_left_half_refined_v2' and local['refine_left'] is True)
        audit.check('cache_identity',label+'/parent_count',local['cell_coverage']['reused_parent_curvature_cells']==(n if parent is not None else 0))
        curvature, radii = {k:point(0) for k in keys}, {k:F(0) for k in keys}
        for j, cell in enumerate(local['cells']):
            cell_label=label+'/cell'+str(j)
            audit.check('cell_coverage', cell_label+'/partition', cell['cell']==j and box(cell['x_left'])==point(F(j,n)) and box(cell['x_right'])==point(F(j+1,n)) and box(cell['x_midpoint'])==point(F(2*j+1,2*n)))
            audit.check('cache_identity', cell_label+'/no_midpoint_evaluation', not cell['midpoint_value'] and not cell['midpoint_term'])
            for key in keys:
                derivative = box(cell['second_derivative'][key])
                left_derivative=box(cell['left_half_second_derivative'][key])
                audit.check('signed_curvature_cells',cell_label+'/'+key+'/left_domain_inclusion',contains(derivative,left_derivative))
                if parent is not None:
                    parent_cell=parent['track']['segments'][i]['local']['cells'][j]
                    audit.check('cache_identity',cell_label+'/'+key+'/whole_parent_identity',cell['second_derivative'][key]==parent_cell['second_derivative'][key])
                exact = scale(add(derivative,left_derivative), h/F(48*n**3))
                audit.enclosure('signed_curvature_cells', cell_label+'/'+key, cell['curvature_correction'][key], exact)
                curvature[key] = add(curvature[key], box(cell['curvature_correction'][key]))
                radii[key] += h*abs_upper(derivative)/F(24*n**3)
        incoming = seg['incoming']; c, eta = F(incoming['center']), F(incoming['radius'])
        audit.enclosure('new_carry', label+'/incoming_interval', incoming['interval'], add(point(c),sym(eta)))
        if i==0:
            audit.check('new_carry', label+'/initial_zero', c==eta==0)
        else:
            audit.check('new_carry', label+'/current_seam', incoming==track['seams'][i-1]['next_incoming'])
        second, remainder = seg['second_correction'], seg['remainder']
        audit.check('new_carry', label+'/prefix_initial', box(second['prefix_initial'])==point(c))
        audit.check('new_carry', label+'/uncertainty_excluded_from_prefix', second['incoming_uncertainty_in_prefix'] is False)
        audit.check('cell_coverage', label+'/second_count', len(second['cells'])==m and second['rectangle_cells']==m and second['prefix_midpoint_cells']==m)
        for j, cell in enumerate(second['cells']):
            audit.check('new_carry', label+'/prefix_chain'+str(j), box(cell['prefix_left'])==(point(c) if j==0 else box(second['cells'][j-1]['prefix_right'])))
        audit.check('new_carry', label+'/prefix_endpoint', second['prefix_endpoint']==second['cells'][-1]['prefix_right'])
        audit.check('new_carry', label+'/prefix_first_overlap', max(box(second['prefix_endpoint'])[0],box(seg['firstvariation_with_candidate_incoming']['P1'])[0])<=min(box(second['prefix_endpoint'])[1],box(seg['firstvariation_with_candidate_incoming']['P1'])[1]))
        norm = box(local['bounds']['D_L'])[1]
        s_exact = abs(c)+eta+box(local['bounds']['B_r'])[1]
        audit.check('finite_remainder', label+'/D_identity', F(remainder['D_upper'])==norm>=0)
        audit.check('finite_remainder', label+'/S_current', F(remainder['S_upper'])>=s_exact)
        audit.check('finite_remainder', label+'/T_input_independent', remainder['T_upper']==past['remainder']['T_upper'])
        for key in keys:
            audit.enclosure('signed_curvature_sums', label+'/'+key, local['curvature_correction'][key],curvature[key])
            audit.check('signed_curvature_sums', label+'/'+key+'/symmetric_radius', F(local['same_new_grid_symmetric_radius_diagnostic'][key])>=radii[key])
            audit.enclosure('first_integral_assembly',label+'/'+key,local['signed'][key],add(box(local['midpoint'][key]),box(local['curvature_correction'][key])))
            audit.check('first_integral_assembly',label+'/'+key+'/same_N_diagnostic_nesting',contains(box(local['same_new_grid_symmetric_diagnostic'][key]),box(local['signed'][key])))
            audit.check('first_integral_assembly',label+'/'+key+'/original_first_nesting',contains(box(old['local']['signed'][key]),box(local['signed'][key])))
            first = add(box(local['signed'][key]),scale(box(seg['gains'][key]),c))
            audit.enclosure('new_carry',label+'/'+key+'/gain_applied',seg['firstvariation_with_candidate_incoming'][key],first)
            gain_norm = abs_upper(box(seg['gains'][key])); t = F(remainder['T_upper'][key])
            audit.check('finite_remainder',label+'/'+key+'/incoming_gain',F(remainder['incoming_upper'][key])>=gain_norm*eta)
            audit.check('finite_remainder',label+'/'+key+'/incoming_coupling',F(remainder['incoming_coupling_upper'][key])>=t*eta)
            audit.check('finite_remainder',label+'/'+key+'/tail',F(remainder['second_volterra_remainder_upper'][key])>=t*norm*F(remainder['S_upper']))
            rr = sum(F(remainder[k][key]) for k in ('incoming_upper','incoming_coupling_upper','second_volterra_remainder_upper'))
            audit.check('finite_remainder',label+'/'+key+'/total',F(remainder['total_before_numerical_upper'][key])>=rr)
            represented = add(add(box(seg['firstvariation_with_candidate_incoming'][key]),box(second['signed'][key])),sub(box(seg['frozen'][key]),box(seg['captured'][key])))
            out = seg['outputs'][key]
            audit.enclosure('output_assembly',label+'/'+key+'/represented',out['centered_secondvariation_plus_representation_interval'],represented)
            val = box(out['centered_secondvariation_plus_representation_interval']); center = F(out['candidate'])
            audit.check('output_assembly',label+'/'+key+'/numerical_radius',F(out['numerical_and_representation_radius'])>=abs_upper(sub(val,point(center))))
            audit.check('output_assembly',label+'/'+key+'/radius',F(out['radius'])>=F(out['numerical_and_representation_radius'])+F(remainder['total_before_numerical_upper'][key]))
            audit.enclosure('output_assembly',label+'/'+key+'/correction',out['true_minus_captured_interval'],add(point(center),sym(out['radius'])))
            audit.enclosure('output_assembly',label+'/'+key+'/absolute',out['true_absolute_interval'],add(box(seg['captured'][key]),box(out['true_minus_captured_interval'])))
        for key in ('P1','H_total_eV'):
            cell_key = 'photon_signed_cell_integral' if key=='P1' else 'heat_total_signed_cell_integral_eV'
            audit.enclosure('second_correction_sums',label+'/'+key,second['signed'][key],sum_boxes(box(cell[cell_key]) for cell in second['cells']))
        # Independently form the differential and species identities from saved
        # output terms, not merely from the candidate's Boolean ledger flags.
        for field, category in [('frozen','frozen'),('firstvariation_with_candidate_incoming','firstvariation'),('signed','secondvariation')]:
            data = second[field] if field=='signed' else seg[field]
            initial_n = capture(control['row']['f0']) if field=='frozen' else (c if field!='signed' else F(0))
            initial_e = capture(control['row']['e0'])*initial_n
            number = sub(add(box(data['P1']),box(data['A_total'])),add(point(initial_n),box(data.get('QN',{'lo':'0','hi':'0'}))))
            energy = sub(add(add(box(data['P1_energy_eV']),box(data['B_total_eV'])),box(data['Z_eV'])),add(point(initial_e),box(data.get('QE_eV',{'lo':'0','hi':'0'}))))
            audit.check('reconstructed_ledgers',label+'/'+category+'/number',contains(number,point(0)))
            audit.check('reconstructed_ledgers',label+'/'+category+'/energy',contains(energy,point(0)))
            for species, chi in zip(SP,CHI):
                heat = add(sub(box(data['H_'+species+'_eV']),box(data['B_'+species+'_eV'])),scale(box(data['A_'+species]),chi))
                audit.check('reconstructed_ledgers',label+'/'+category+'/heat_'+species,contains(heat,point(0)))
        for key, saved in seg['ledger_enclosures'].items():
            audit.enclosure('saved_ledgers',label+'/'+key,saved,point(0))
        for key in cumulative:
            # The valid centered representation is exact center +/- radius.
            # Saved display endpoints may have an extra outward decimal ulp;
            # those formatting expansions need not be accumulated as errors.
            outgoing=seg['outputs'][key]
            cumulative[key] = add(cumulative[key],add(point(outgoing['candidate']),sym(outgoing['radius'])))
            captured[key] = add(captured[key],box(seg['captured'][key]))
            audit.enclosure('path_accumulation',label+'/'+key+'/correction',seg['cumulative_moment_corrections'][key]['interval'],cumulative[key])
            audit.enclosure('path_accumulation',label+'/'+key+'/captured',seg['cumulative_captured_moments'][key],captured[key])
        if i<len(controls)-1:
            seam = track['seams'][i]
            audit.check('seams',label+'/fixed_events',all(seam[k]==previous['seams'][i][k] for k in ('left','right','event','DeltaE_eV','captured_photon_stitch_residual')))
            photon = seg['outputs']['P1']; gap = box(seam['captured_photon_stitch_residual'])
            raw = add(point(photon['candidate']),gap); nc = F(seam['next_incoming']['center'])
            audit.check('seams',label+'/incoming_radius',F(seam['next_incoming']['radius'])>=F(photon['radius'])+abs_upper(sub(raw,point(nc))))
            audit.check('seams',label+'/current_anchor_input',seam['incoming_correction_to_anchor']==photon['true_minus_captured_interval'])
            anchor = mul(box(seam['DeltaE_eV']),add(box(seg['captured']['P1']),box(photon['true_minus_captured_interval'])))
            audit.enclosure('seams',label+'/anchor',seam['true_anchor_eV'],anchor)
        first_count += local['new_coefficient_evaluations']
        second_count += second['new_coefficient_evaluations']
        audit.check('execution_counts',label+'/first_calls',local['new_coefficient_evaluations']==expected_first)
        audit.check('execution_counts',label+'/second_calls',second['new_coefficient_evaluations']==2*m)
        audit.check('execution_counts',label+'/domain_calls',seg['new_coefficient_domain']['gas_checked_evaluations']==expected_first+2*m and seg['new_coefficient_domain']['positive_rate_evaluations']==expected_first+2*m)
    for key in cumulative:
        audit.enclosure('path_accumulation',f'{node}/{key}/final_correction',track['cumulative_moment_corrections'][key]['interval'],cumulative[key])
        audit.enclosure('path_accumulation',f'{node}/{key}/final_absolute',track['true_moment_enclosures'][key],add(box(track['cumulative_captured_moments'][key]),box(track['cumulative_moment_corrections'][key]['interval'])))
    audit.enclosure('seams',f'{node}/summed_anchor',track['summed_true_anchor_eV'],sum_boxes(box(s['true_anchor_eV']) for s in track['seams']))
    final = track['segments'][-1]['outputs']
    audit.check('path_structure',f'{node}/final_stock_identity',track['final_photon']==final['P1'] and track['final_energy_stock_eV']==final['P1_energy_eV'])
    moments = track['true_moment_enclosures']
    n0, e0 = capture(controls[0]['row']['f0']), capture(controls[0]['row']['e0'])
    number = sub(add(box(track['final_photon']['true_absolute_interval']),box(moments['A_total'])),add(point(n0),box(moments['QN'])))
    energy = sub(add(add(box(track['final_energy_stock_eV']['true_absolute_interval']),box(moments['B_total_eV'])),box(moments['Z_eV'])),add(add(point(e0*n0),box(moments['QE_eV'])),box(track['summed_true_anchor_eV'])))
    audit.check('reconstructed_ledgers',f'{node}/global_number',contains(number,point(0)))
    audit.check('reconstructed_ledgers',f'{node}/global_energy',contains(energy,point(0)))
    for species, chi in zip(SP,CHI):
        heat=add(sub(box(moments['H_'+species+'_eV']),box(moments['B_'+species+'_eV'])),scale(box(moments['A_'+species]),chi))
        audit.check('reconstructed_ledgers',f'{node}/global_heat_'+species,contains(heat,point(0)))
    for key, saved in track['global_ledger_enclosures'].items():
        audit.enclosure('saved_ledgers',f'{node}/global_'+key,saved,point(0))
    audit.check('execution_counts',f'{node}/first_total',result['new_first_integral_coefficient_evaluations']==first_count)
    audit.check('execution_counts',f'{node}/second_total',result['new_second_correction_coefficient_evaluations']==second_count)
    audit.check('execution_counts',f'{node}/combined',result['new_coefficient_evaluations']==first_count+second_count)
    audit.check('execution_counts',f'{node}/second_recomputed',result['second_corrections_recomputed_with_new_carry']==len(controls))
    audit.check('execution_counts',f'{node}/no_forbidden',all(v==0 for v in result['forbidden_invocations'].values()))
    return {'node':node,'N_first':n,'M_second':m,'segments':len(controls),
        'new_first_coefficient_evaluations':first_count,'new_second_coefficient_evaluations':second_count}


def reconstruct_allocation(track, weight):
    categories=('first_curvature_range','first_midpoint_rounding','signed_rectangle','finite_volterra_tail','other_rounding')
    def zero(): return {k:F(0) for k in categories}
    incoming=zero(); accumulated={sp:zero() for sp in SP}
    for i,seg in enumerate(track['segments']):
        if sum(incoming.values())!=F(seg['incoming']['radius']):
            raise AssertionError('independent incoming allocation mismatch')
        current={}
        for q in ['P1']+['H_'+s+'_eV' for s in SP]:
            gain=abs_upper(box(seg['gains'][q]))+F(seg['remainder']['T_upper'][q])
            parts={k:gain*v for k,v in incoming.items()}
            parts['first_curvature_range']+=width(box(seg['local']['curvature_correction'][q]))/2
            parts['first_midpoint_rounding']+=width(box(seg['local']['midpoint'][q]))/2
            parts['signed_rectangle']+=width(box(seg['second_correction']['signed'][q]))/2
            parts['finite_volterra_tail']+=F(seg['remainder']['second_volterra_remainder_upper'][q])
            residual=F(seg['outputs'][q]['radius'])-sum(parts.values())
            if residual<0: raise AssertionError('negative independent direct allocation')
            parts['other_rounding']+=residual; current[q]=parts
        for sp in SP:
            q='H_'+sp+'_eV'
            accumulated[sp]={k:accumulated[sp][k]+current[q][k] for k in categories}
            residual=F(seg['cumulative_moment_corrections'][q]['radius'])-sum(accumulated[sp].values())
            if residual<0: raise AssertionError('negative independent accumulation allocation')
            accumulated[sp]['other_rounding']+=residual
        incoming=dict(current['P1'])
        if i<len(track['seams']):
            residual=F(track['seams'][i]['next_incoming']['radius'])-sum(incoming.values())
            if residual<0: raise AssertionError('negative independent seam allocation')
            incoming['other_rounding']+=residual
    p={k:v*weight for k,v in current['P1'].items()}
    h={k:sum(accumulated[s][k] for s in SP)*weight for k in categories}
    absolute=metrics(track,weight)['absolute']; out={}
    for q,parts in [('P_final',p),('H_total_eV',h)]:
        hw=width(absolute[q])/2; residual=hw-sum(parts.values())
        if residual<0: raise AssertionError('negative independent terminal allocation')
        parts['other_rounding']+=residual
        out[q]={'halfwidth':hw,'components':parts}
    return out


def audit_owner_analysis(root, analysis_dir, paths, own_aggregate, controls, audit):
    analysis=read(analysis_dir/'LOCAL_ANALYSIS.json')
    allocation=read(analysis_dir/'BOUND_ALLOCATION.json')
    receipt=read(analysis_dir/'EXECUTION_RECEIPT.json')
    audit.check('owner_analysis','analysis_code_identity',sha(root/'code/analyze_local.py')==receipt['code_sha256'])
    audit.check('owner_analysis','analysis_result_identity',sha(analysis_dir/'LOCAL_ANALYSIS.json')==receipt['analysis_sha256'])
    audit.check('owner_analysis','selected_count',analysis['selected_path_count']==5 and analysis['selected_segment_count']==12)
    audit.check('owner_analysis','raw_acceptance',analysis['nested_count']==analysis['nonincreasing_count']==analysis['required_count']==170 and analysis['mechanical_acceptance'] is True)
    audit.check('owner_analysis','scope_limits',analysis['prior_admissions_changed'] is False and analysis['raw_intersections']==analysis['old_interval_fallbacks']==0 and analysis['physical_continuum_production_receiver']=='HOLD')
    for q,own in own_aggregate.items():
        saved=analysis['selected_aggregate_summary'][q]
        audit.check('owner_analysis',q+'/aggregate_exact',F(saved['baseline_width'])==F(own['old_width_exact']) and F(saved['candidate_width'])==F(own['new_width_exact']) and F(saved['gain_fraction'])==F(own['gain_fraction_exact']))
    contributions={}; totals={}
    for path in paths:
        node=path['node']; result=read(root/path['result_relative_path']); weight=capture(controls[node][0]['row']['weight'])
        own=reconstruct_allocation(result['track'],weight)
        saved=next(x['quantities'] for x in allocation['paths'] if x['node']==node)
        for q,parts in own.items():
            audit.check('bound_allocation',f'{node}/{q}/nonnegative_reconstruction',sum(parts['components'].values())==parts['halfwidth'] and all(v>=0 for v in parts['components'].values()))
            audit.check('bound_allocation',f'{node}/{q}/saved_exact',F(saved[q]['halfwidth'])==parts['halfwidth'] and {k:F(v) for k,v in saved[q]['components'].items()}==parts['components'])
            if q not in totals: totals[q]={'halfwidth':F(0),'components':{k:F(0) for k in parts['components']}}
            totals[q]['halfwidth']+=parts['halfwidth']
            for k,v in parts['components'].items(): totals[q]['components'][k]+=v
        contributions[str(node)]={q:{'halfwidth_exact':str(x['halfwidth']),'components':{k:str(v) for k,v in x['components'].items()}} for q,x in own.items()}
    for q,parts in totals.items():
        saved=analysis['selected_bound_halfwidth_allocation'][q]
        audit.check('bound_allocation',q+'/aggregate_exact',F(saved['halfwidth'])==parts['halfwidth'] and {k:F(v) for k,v in saved['components'].items()}==parts['components'])
    records=[read(p) for p in sorted((root/'runs').glob('*/node_*/COMPLETE.json'))]
    resource_claim=analysis['resources']
    audit.check('resources','actual_path_count',len(records)==resource_claim['completed_path_invocations_including_diagnostics'])
    for destination,source in [('new_first_integral_coefficient_evaluations','new_first_integral_coefficient_evaluations'),('second_correction_coefficient_evaluations_during_new_path_assembly','new_second_correction_coefficient_evaluations'),('total_coefficient_evaluations','new_coefficient_evaluations'),('sum_per_path_elapsed_seconds_not_wall','elapsed_seconds'),('sum_per_path_process_cpu_seconds','cpu_seconds')]:
        audit.check('resources',destination,sum(r[source] for r in records)==resource_claim[destination])
    audit.check('resources','max_elapsed',max(r['elapsed_seconds'] for r in records)==resource_claim['max_per_path_elapsed_seconds'])
    audit.check('resources','individual_RSS',max(r['peak_RSS_KiB'] for r in records)==resource_claim['peak_individual_process_RSS_KiB'])
    audit.check('resources','claim_ceiling',resource_claim['NCP_launches']==0 and resource_claim['E13C10_full_population']=='NOT_RUN' and resource_claim['same_work_speedup']=='NOT_ESTABLISHED' and resource_claim['CPU_utilization']=='NOT_MEASURED' and resource_claim['provider_attestation']=='NOT_ASSERTED')
    return {'analysis_sha256':sha(analysis_dir/'LOCAL_ANALYSIS.json'),'allocation_sha256':sha(analysis_dir/'BOUND_ALLOCATION.json'),
        'source_sha256':receipt['code_sha256'],'resources':resource_claim,
        'aggregate_bound_allocation':{q:{'halfwidth_exact':str(x['halfwidth']),'components':{k:str(v) for k,v in x['components'].items()},'percent':{k:display(v/x['halfwidth']*100) for k,v in x['components'].items()}} for q,x in totals.items()}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,required=True)
    ap.add_argument('--restored-e13c9',type=Path,required=True)
    ap.add_argument('--selected-dir',type=Path,required=True)
    ap.add_argument('--analysis-dir',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    root, restored, selected_dir, out=(p.resolve() for p in (args.package,args.restored_e13c9,args.selected_dir,args.output_dir))
    out.mkdir(parents=True,exist_ok=False)
    started, cpu_started=time.perf_counter(),time.process_time()
    audit=Audit()
    state={'schema':'bass-he-e13c10-independent-saved-arithmetic-review-v1',
        'reviewer_role':'FINAL_INDEPENDENT_DECISION_REVIEWER_NO_CANDIDATE_OR_CONTROL_DESIGN',
        'started_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),
        'source_lock_sha256':sha(root/'SOURCE_LOCK.json'),'host':platform.node(),
        'captured_coefficient_evaluations':0,'scientific_kernel_imports':0,
        'scientific_path_invocations':0,'old_scientific_work_replays':0,'NCP_launches':0,
        'method':'Exact Fraction reconstruction of saved outward intervals and raw metrics; separate manual source/mathematical review required.',
        'selected_dir':str(selected_dir.relative_to(root))}
    write(out/'START.json',state)
    try:
        root9=restored/'package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1'
        root8=restored/'runtime/E13C8'
        root7=root8/'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
        lock=read(root/'SOURCE_LOCK.json')
        for rel,pin in lock['files'].items(): check_pin(audit,root,rel,pin)
        for rel,pin in lock['E13C9_dependencies'].items(): check_pin(audit,root9,rel,pin)
        audit.check('byte_identity','closed_form_oracle',sha(root9/'tests/MANUFACTURED/run_manufactured_controls.py')=='15806e4758038a788312dfe075f10a364682e3655a0ca35ed0ca602166ea091f')
        audit.check('scope','actual_prior_independent_admission',read(root9/'CURRENT_STATE.json')['decision']==read(root9/'review/independent/INDEPENDENT_DECISION.json')['decision']=='PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA')
        audit.check('byte_identity','original_source_lock',sha(root7/'SOURCE_LOCK.json')=='386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f')
        lock7=read(root7/'SOURCE_LOCK.json')
        audit.check('byte_identity','original_17_members',len(lock7['files'])==17)
        for rel,pin in lock7['files'].items(): check_pin(audit,root7,rel,pin)
        selected=read(root/'evidence/SELECTED_INPUTS.json')['selected_paths']
        nodes=[x['node'] for x in selected]
        audit.check('scope','selected_nodes',nodes==[1,1162,1976,1620,2344])
        plan=read(root/'WORK_PLAN.json')
        audit.check('scope','same_N_amendment',plan['revision']=='LEFT_HALF_REFINED_WITH_PARENT_CACHE' and plan['peano_left_half_refinement'] is True)
        audit.check('scope','local_limits',plan['max_workers']==3 and plan['per_path_wall_seconds']==120 and plan['per_process_address_space_bytes']==1073741824 and plan['new_NCP_jobs']==0)
        controls,index=load_controls(root7,nodes,audit)
        state['manufactured_receipts']=audit_controls(root,audit)
        paths=[]; sums={kind:{} for kind in ('old','new')}
        for rec in selected:
            node=rec['node']; folder=selected_dir/f'node_{node:06d}'
            result, complete, comparison=read(folder/'RESULT.json'),read(folder/'COMPLETE.json'),read(folder/'COMPARISON.json')
            baseline_path=check_pin(audit,root8,rec['baseline_result']['path_relative_to_restore'],rec['baseline_result'])
            prior_pin=rec['admitted_e13c9']['result']; prior_path=check_pin(audit,root9,prior_pin['relative_path'],prior_pin)
            baseline,prior=read(baseline_path),read(prior_path)
            audit.check('byte_identity',str(node)+'/result_receipt',sha(folder/'RESULT.json')==complete['result_sha256'] and sha(folder/'COMPARISON.json')==complete['comparison_sha256'])
            audit.check('byte_identity',str(node)+'/current_source',result['source_lock_sha256']==state['source_lock_sha256']==complete['source_lock_sha256'])
            audit.check('input_identity',str(node)+'/same_input',result['path_input_sha256']==baseline['path_input_sha256']==prior['path_input_sha256']==index[str(node)]['path_input_sha256'])
            audit.check('input_identity',str(node)+'/worker_checks',all(x['pass'] for x in result['input_checks']))
            unit=next(u for u in plan['units'] if u['node']==node)
            parent=None
            if 'parent_curvature_result' in unit:
                pin=unit['parent_curvature_result']
                parent_path=check_pin(audit,root,pin['relative_path'],pin,'cache_identity')
                parent=read(parent_path)
                audit.check('cache_identity',str(node)+'/parent_source_input_N_P',parent['source_lock_sha256']==unit['parent_curvature_source_lock_sha256'] and parent['original_source_lock_sha256']==result['original_source_lock_sha256'] and parent['path_input_sha256']==result['path_input_sha256'] and parent['work']['N_first']==result['work']['N_first'] and parent['work']['precision']==60)
                audit.check('cache_identity',str(node)+'/recorded_parent',result['parent_curvature_result']==pin)
            else:
                audit.check('cache_identity',str(node)+'/no_undeclared_parent',result['parent_curvature_result'] is None)
            path=audit_track(audit,result,baseline,prior,controls[node],parent)
            w=capture(controls[node][0]['row']['weight'])
            previous,current=metrics(prior['track'],w),metrics(result['track'],w)
            rows=compare(previous,current)
            audit.check('raw_admission',str(node)+'/34_metrics',len(rows)==34)
            saved={(r['kind'],r['quantity']):r for r in comparison['comparisons']}
            for row in rows:
                label=f"{node}/{row['kind']}/{row['quantity']}"
                audit.check('raw_admission',label+'/saved_comparison',row==saved[(row['kind'],row['quantity'])])
                audit.check('raw_admission',label+'/nested_nonincreasing',row['nested'] and row['width_nonincreasing'])
            for title,vals in [('old',previous),('new',current)]:
                for key in ('P_final','H_total_eV'):
                    sums[title][key]=add(sums[title].get(key,point(0)),vals['absolute'][key])
            audit.check('execution_counts',str(node)+'/wall_limit',0<result['elapsed_seconds']<120)
            path.update({'result_relative_path':str((folder/'RESULT.json').relative_to(root)),
                'result_sha256':complete['result_sha256'],'rows':rows,
                'elapsed_seconds':result['elapsed_seconds'],'cpu_seconds':result['cpu_seconds'],
                'peak_RSS_KiB':result['peak_RSS_KiB']})
            paths.append(path)
        state['selected_paths']=paths
        state['aggregate_metrics']={}
        for key in ('P_final','H_total_eV'):
            wa,wb=width(sums['old'][key]),width(sums['new'][key]); gain=(wa-wb)/wa
            audit.check('aggregate_admission',key+'/50_percent_gain',gain>=F(1,2))
            state['aggregate_metrics'][key]={'old_interval':enc(sums['old'][key]),'new_interval':enc(sums['new'][key]),
                'old_width_exact':str(wa),'new_width_exact':str(wb),'gain_fraction_exact':str(gain),
                'old_width_display':display(wa),'new_width_display':display(wb),'gain_percent_display':display(gain*100)}
        state['owner_analysis_independent_validation']=audit_owner_analysis(root,args.analysis_dir.resolve(),paths,state['aggregate_metrics'],controls,audit)
        audit.check('scope','twelve_segments',sum(r['segments'] for r in paths)==12)
        audit.check('scope','170_metrics',sum(len(r['rows']) for r in paths)==170)
        first=read(root/'evidence/FIRST_N32_RAW_ADMISSION_FINDING.json')
        audit.check('first_failure_preserved','N32_two_failures',[(r['node'],r['nested']) for r in first['paths']]==[(1,12),(1976,0)])
        for r in first['paths']:
            audit.check('first_failure_preserved',str(r['node'])+'/raw_result_identity',sha(root/f"runs/N32/node_{r['node']:06d}/RESULT.json")==r['result_sha256'])
        initial_root=root/'evidence/SOURCE_REVISIONS/INITIAL_N32'; initial_lock=read(initial_root/'SOURCE_LOCK.json')
        for rel,pin in initial_lock['files'].items(): check_pin(audit,initial_root,rel,pin,'first_failure_preserved')
        same_root=root/'evidence/SOURCE_REVISIONS/SAME_N_UNREFINED'; same_lock=read(same_root/'SOURCE_LOCK.json')
        for rel,pin in same_lock['files'].items(): check_pin(audit,same_root,rel,pin,'first_failure_preserved')
        for node,expected in ((1,33),(1976,26)):
            completed=read(root/f'runs/SAME_N/node_{node:06d}/COMPLETE.json')
            audit.check('first_failure_preserved',str(node)+'/unrefined_same_N_failed',completed['nested_count']==expected and completed['nonincreasing_count']==34 and completed['mechanically_admissible'] is False)
        for rel,pin in lock['files'].items(): check_pin(audit,root,rel,pin,'source_still_unchanged')
        audit.check('source_still_unchanged','lock',sha(root/'SOURCE_LOCK.json')==state['source_lock_sha256'])
        state.update({'status':'PASS_INDEPENDENT_SAVED_ARITHMETIC','checks_passed':sum(audit.counts.values()),
            'check_groups':audit.counts,'checks_failed':0,'failures':[],
            'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu_started,
            'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'claim_ceiling':'Five selected captured OFF finite paths only; E13C10 full population NOT_RUN; physical/continuum/production/receiver HOLD.'})
        write(out/'REVIEW_RESULTS.json',state)
        print(json.dumps({k:state[k] for k in ('status','checks_passed','checks_failed','wall_seconds','cpu_seconds','aggregate_metrics')},sort_keys=True))
    except BaseException as exc:
        state.update({'status':'REVIEW_FAILURE_PRESERVED','checks_passed':sum(audit.counts.values())-len(audit.failures),
            'check_groups':audit.counts,'checks_failed':len(audit.failures),'failures':audit.failures,
            'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),
            'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu_started})
        write(out/'FIRST_FAILURE.json',state)
        raise


if __name__=='__main__':
    main()
