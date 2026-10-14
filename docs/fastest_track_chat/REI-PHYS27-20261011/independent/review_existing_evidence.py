#!/usr/bin/env python3
"""Review retained PHYS27 data only. No scientific module is imported or run."""
from pathlib import Path
from decimal import Decimal as D, getcontext
from hashlib import sha256
from datetime import datetime, timezone
import json
import zipfile

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'independent/STATIC_REVIEW_CHECKS.json'
if OUT.exists():
    raise FileExistsError('Preserve the first review result')
def read(path):
    return json.loads((ROOT / path).read_bytes())
def ident(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': sha256(b).hexdigest()}
def verify_records(records):
    return [{'path': f['path'], 'pass': ident(ROOT/f['path']) ==
             {k:f[k] for k in ['bytes','sha256']}} for f in records]
issues = []
def require(ok, label):
    if not ok:
        issues.append(label)
    return bool(ok)

candidate = read('evidence/CANDIDATE_FROZEN.json')
identity = verify_records(candidate['files'])
require(len(identity) == 87 and all(x['pass'] for x in identity), 'candidate identities')
freeze = read('contributions/numerics/PREEXECUTION_FROZEN.json')
pre = verify_records(freeze['files'])
require(len(pre) == 13 and all(x['pass'] for x in pre), 'preexecution identities')
raw = read('contributions/numerics/FINITE_WIDTH_FIRST.json')
summary = read('report/PHYS27_RESULTS_SUMMARY.json')
execution = read('contributions/numerics/EXECUTION.json')
receipt = read('portability/REPLAY_RECEIPT.json')
protocol = read('contributions/numerics/PROTOCOL.json')
require(freeze['frozen_utc'] < execution['started_utc'], 'first freeze temporal order')
require(read('portability/PORTABILITY_PREEXECUTION_FROZEN.json')['frozen_utc'] <
        receipt['replay_execution']['started_utc'], 'replay freeze temporal order')
require(execution['finished_utc'] < candidate['frozen_utc'] and
        receipt['finished_utc'] < candidate['frozen_utc'], 'candidate after actual executions')
for path, digest in raw['identity_sha256'].items():
    require(ident(ROOT/path)['sha256'] == digest, 'raw input identity '+path)
require(raw['decimal_precision'] == protocol['arithmetic']['decimal_precision'] == 80,
        'frozen Decimal precision')
j = read('inputs/PHYS22_INITIAL_COEFFICIENTS.json')['results']['baseline_local']['J_nonphoto'][2]
require(D(j[0]) == D(raw['constants']['J_h2_x']) and
        D(j[3]) == D(raw['constants']['J_h2_w']), 'actual full serialized J entries')

laws = {}
for row in raw['physical_variance_cases']:
    for side in ['upper','lower']:
        laws[row['label']+'__'+side] = row[side]
for row in raw['mixtures_at_W19_74']:
    laws['mixture_'+row['label']] = row
rules = {row['order']: row for row in raw['quadrature_rules']}
constants = raw['constants']
count = raw['summary']['actual_counts']
def supported(law):
    return all(D(b['probability']) >= 0 and
               D('13.66') <= D(b['center_eV']) <= D('24.53') and
               D('13.61') <= D(b['band_eV'][0]) <= D(b['band_eV'][1]) <= D('24.58')
               for b in law['bands'])
def budgets(c):
    return (c['new_physical_root_searches'] == 2 and
            c['physical_variance_cases'] == 9 and
            c['independent_quadrature_centers'] == 7 and
            c['combined_kernel_evaluations'] <= 20000)
def predicate(x):
    n=x['name']
    if 'tolerance' in x:
        residual=D(x['actual'])-D(x['expected'])
        err=abs(residual)/D(x['scale'])
        require(residual == D(x['residual']), 'stored residual '+n)
        require(err == D(x['scaled_error']), 'stored scaled error '+n)
        return err <= D(x['tolerance'])
    if n.startswith('GL') and n.endswith('__distinct_supported_positive'):
        rr=rules[int(n.split('__')[0][2:])]['nodes_and_weights']
        return len({D(v['x']) for v in rr}) == len(rr) and all(
            -1 < D(v['x']) < 1 and D(v['w']) > 0 for v in rr)
    if n == 'fixed_feasible_geometry':
        return (constants['center_support_eV'] == ['13.66','24.53'] and
                D(constants['L_delta_eV']) == D('4.34') and
                D(constants['H_delta_eV']) == D('6.53') and
                D(constants['V_center_max_eV2']) == D('28.3402'))
    if 'J_h2x' in x: return D(x['J_h2x']) < 0 < D(x['J_h2w'])
    if 'kbar_at_mean_s_4' in x: return D(x['kbar_at_mean_s_4']) < 0
    if 'endpoint_response_s_4' in x: return D(x['endpoint_response_s_4']) > 0
    if 'F_values_s-4_eV' in x: return D(x['F_values_s-4_eV'][0])*D(x['F_values_s-4_eV'][1]) < 0
    if 'F_low' in x: return D(x['F_low'])*D(x['F_high']) <= 0
    if 'actual_iterations' in x: return x['actual_iterations'] <= 100
    if 'width_eV' in x: return D(x['width_eV']) <= D('1e-22')
    if 'old_Vstar' in x: return D(x['old_Vstar']) < D(x['W_star_delta']) < D(x['W_0_delta']) < D(x['old_W0'])
    if 'slope_s_4_eV_minus2' in x: return D(x['slope_s_4_eV_minus2']) > 0
    if 'scaled_errors_32_64_128' in x:
        e=list(map(D,x['scaled_errors_32_64_128'])); return e[2] < e[1] < e[0]
    if n.endswith('__nonnegative_supported_bands'): return supported(laws[n.rsplit('__',1)[0]])
    if 'lower_gap_s_4' in x: return D(x['lower_gap_s_4']) > 0 and D(x['upper_gap_s_4']) > 0
    if 'gap_s_4' in x: return D(x['gap_s_4']) > 0
    if n.endswith('__degenerate_positive_centers'):
        label=n.rsplit('__',1)[0]
        target=['18'] if label.startswith('minimum_') else ['13.66','24.53']
        return all(laws[label+'__'+s]['positive_mass_centers_eV'] == target for s in ['upper','lower'])
    if 'lower_s_4' in x: return D(x['lower_s_4']) < 0 < D(x['upper_s_4'])
    if 'alpha_upper' in x: return 0 < D(x['alpha_upper']) < 1
    if 'actual_counts' in x: return budgets(x['actual_counts'])
    raise ValueError('Unreviewed check kind: '+n)
reassessed=[]
for x in raw['checks']:
    p=bool(predicate(x)); require(p == x['pass'], 'check predicate '+x['name'])
    reassessed.append({'name':x['name'],'retained_pass':x['pass'],'reassessed_pass':p})
require(len(reassessed) == len({x['name'] for x in reassessed}) == 405, '405 unique checks')
require(sum(x['reassessed_pass'] for x in reassessed) == 405, '405 predicates pass')

# Reconstruct the retained bracket path from recorded F signs, without evaluating F.
history_review=[]
for name, root in raw['new_physical_roots'].items():
    lo,hi=map(D,root['initial_numerical_bracket']['center_eV'])
    flo,fhi=map(D,root['initial_numerical_bracket']['F_values_s-4_eV'])
    before=len(issues)
    for i,row in enumerate(root['history'],1):
        mid=(lo+hi)/2; val=D(row['F_s-4_eV'])
        require(row['iteration'] == i and D(row['center_eV']) == mid, name+' recorded midpoint '+str(i))
        require(lo < mid < hi, name+' interior midpoint '+str(i))
        if flo*val < 0: hi,fhi=mid,val
        else: lo,flo=mid,val
        require(flo*fhi <= 0, name+' maintained sign bracket '+str(i))
    require([lo,hi] == list(map(D,root['final_center_bracket_eV'])), name+' final centers')
    require([flo,fhi] == list(map(D,root['final_F_values_s-4_eV'])), name+' final F values')
    require((lo+hi)/2 == D(root['midpoint_center_eV']), name+' final midpoint')
    require(hi-lo == D(root['final_center_bracket_width_eV']), name+' final width')
    require(len(root['history']) == root['iterations'] == 80, name+' iteration count')
    span=D('4.34') if name == 'W_star_delta' else D('6.53')
    def wmap(c):
        return span*(c-D(18) if name == 'W_star_delta' else D(18)-c)+D('0.05')**2/3
    require(sorted([wmap(lo),wmap(hi)]) == list(map(D,root['final_physical_variance_bracket_eV2'])), name+' physical bracket map')
    require(wmap((lo+hi)/2) == D(root['midpoint_physical_variance_eV2']), name+' physical midpoint map')
    history_review.append({'name':name,'rows':len(root['history']),'pass':len(issues)==before,
                           'new_F_or_kernel_evaluations':0})

# Report projections must preserve original observations, including nonzero residuals.
mapping={
 'threshold_numerical_approximations':'threshold_comparison',
 'numerical_endpoint_signs':'numerical_endpoint_signs',
 'first_summary':'summary',
 'mixtures_W19_74':'mixtures_at_W19_74'}
projection=[]
for s,r in mapping.items():
    ok=summary[s] == raw[r]; require(ok,'summary projection '+s); projection.append({'field':s,'pass':ok})
for name,root in raw['new_physical_roots'].items():
    require(summary['root_diagnostics'][name] == {k:v for k,v in root.items() if k!='history'}, 'root projection '+name)
for a,b in zip(summary['nine_variance_cases'],raw['physical_variance_cases']):
    require(all(a[k] == b[k] for k in ['label','W_photon_eV2','V_center_eV2','interval_s-4']) and
            a['PHYS26_same_W_interval_s-4'] == b['PHYS26_delta_allowed_same_W_interval_s-4'], 'nine case projection '+a['label'])
require(summary['representative_W19_74'] == raw['physical_variance_cases'][4], 'W19.74 full projection')
require(summary['first_execution'] == execution, 'execution projection')
require(read('contributions/theory/THEORY_CLAIMS.json')['exact_formulas'] == summary['derived'], 'derived formula projection')
require(json.loads((ROOT/'contributions/numerics/FIRST_STDOUT.txt').read_bytes()) == raw['summary'], 'stdout summary equality')
require((ROOT/'contributions/numerics/FIRST_STDERR.txt').read_bytes() == b'', 'first stderr empty')
require(count['primary_jet_kernel_evaluations']+count['independent_scalar_kernel_evaluations'] == count['combined_kernel_evaluations'] == 3923, 'kernel count sum')
require(count['independent_scalar_kernel_evaluations'] == 7*129, 'scalar count reconciliation')
require(sum(v['iterations'] for q in raw['quadrature_rules'] for v in q['positive_node_solutions']) == 118, 'node iteration reconciliation')
require(sum(len(q['positive_node_solutions']) for q in raw['quadrature_rules']) == 20, 'node solution reconciliation')

first=(ROOT/'contributions/numerics/FINITE_WIDTH_FIRST.json').read_bytes()
replay=(ROOT/'portability/REPLAY_RESULT.json').read_bytes()
require(first == replay and json.loads(first) == json.loads(replay), 'actual replay equality')
require(receipt['comparison']['byte_equal'] and receipt['comparison']['parsed_json_equal'], 'receipt equality claims')
require(receipt['replay_execution']['exit_code'] == 0 and receipt['portability_replay_main_invocations'] == 1, 'actual one replay exit')
require(receipt['independent_physics_evidence_credit'] == 0, 'replay credit ceiling')
stage=read('portability/STAGE_MANIFEST.json')
stage_checks=[]
with zipfile.ZipFile(ROOT/'portability/PHYS27_PORTABLE_STAGE.zip') as z:
    require(set(z.namelist()) == {'MANIFEST.json',*(r['path'] for r in stage['files'])}, 'stage exact member set')
    require(z.read('MANIFEST.json') == (ROOT/'portability/STAGE_MANIFEST.json').read_bytes(), 'stage manifest bytes')
    for item in stage['files']:
        data=z.read(item['path'])
        ok=len(data)==item['bytes'] and sha256(data).hexdigest()==item['sha256']
        require(ok,'stage payload '+item['path']); stage_checks.append({'path':item['path'],'pass':ok})
require(len(stage_checks)==15,'stage payload count')
out={
 'task':'REI-PHYS27-20261011','reviewer':'/root/phys27_decision',
 'completed_utc':datetime.now(timezone.utc).isoformat(),
 'classification':'Static identity, retained-record arithmetic and projection review only; no new physics execution',
 'candidate':ident(ROOT/'evidence/CANDIDATE_FROZEN.json'),
 'candidate_payloads':identity,'preexecution_payloads':pre,
 'retained_checks_reassessed':reassessed,'root_history_review':history_review,
 'summary_projection':projection,'stage_payloads':stage_checks,
 'actual_first_vs_replay_bytes_equal':first==replay,
 'actual_first_vs_replay_parsed_equal':json.loads(first)==json.loads(replay),
 'errors':issues,'status':'PASS' if not issues else 'FAIL',
 'actual_execution':{'review_script':1,'scientific_module_imports':0,'scientific_main':0,
 'kernel_or_derivative_evaluations':0,'physical_root_searches':0,
 'old_main_or_suites':0,'portability_replays':0,'native':0,'gas_IVP':0},
 'limits':['Arithmetic on stored responses does not independently validate their kernel evaluations.',
           'Recorded sign brackets remain numerical, not certified exact-integral enclosures.',
           'The final publication archive is not the already checked 15-payload portability stage.']}
with OUT.open('x',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps({'status':out['status'],'errors':issues,'candidate_payloads':len(identity),
 'retained_checks':len(reassessed),'root_history_rows':sum(r['rows'] for r in history_review),
 'stage_payloads':len(stage_checks),'science_runs':0},ensure_ascii=False))
