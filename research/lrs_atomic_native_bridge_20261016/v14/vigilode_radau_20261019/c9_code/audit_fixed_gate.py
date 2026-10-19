#!/usr/bin/env python3
"""Independent read-only audit of captured native Radau fixed-geometry raw data.

No native solver/RHS is run. Binary64 values are promoted exactly to Decimal(60)
for event/endpoint sums. The source abundance is used as the physical Y; native
proper-density ratios can differ by an ulp. Reported audit columns are not inputs
to the endpoint, event, node or integrated-channel balance reconstruction.
"""
import argparse
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
CHI = [13.598434599702, 24.587389011, 54.41776]
Y = .2454 / (4 * (1 - .2454))
EV = 1.602176634e-12
KB = 1.380649e-16
SQRT6 = math.sqrt(6.)
A = [[(88-7*SQRT6)/360, (296-169*SQRT6)/1800, (-2+3*SQRT6)/225],
     [(296+169*SQRT6)/1800, (88+7*SQRT6)/360, (-2-3*SQRT6)/225],
     [(16-SQRT6)/36, (16+SQRT6)/36, 1/9]]
B = A[2]

def d(v):
    return Decimal.from_float(v) if isinstance(v, float) else Decimal(v)

def exact_sum(values):
    return sum((d(v) for v in values), Decimal(0))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def binding(s):
    x, y, z = map(d, s['fractions'])
    return d(CHI[0])*x + d(Y)*(d(CHI[1])*y+(d(CHI[1])+d(CHI[2]))*z)

def electron(s):
    x, y, z = map(d, s['fractions'])
    return x + d(Y)*(y+2*z)

def flatten_events(e):
    out = {}
    for k, v in e.items():
        if isinstance(v, list):
            out.update({f'{k}[{j}]': x for j, x in enumerate(v)})
        else:
            out[k] = v
    return out

def quadrature(stages):
    result = {k: Decimal(0) for k in flatten_events(stages[0]['events_per_h_s'])}
    for i, s in enumerate(stages):
        for key, value in flatten_events(s['events_per_h_s']).items():
            result[key] += d(s['dt_s'])*d(B[i])*d(value)
    return result

def species_event(e):
    return [e[f'p[{j}]']+e[f'c[{j}]']-e[f'r[{j}]'] for j in range(3)]

def chemical_balances(before, after, e):
    net = species_event(e)
    ce = sum((e[f'ce[{j}]'] for j in range(3)), Decimal(0))
    rrheat = sum((e[f'rr[{j}]'] for j in range(3)), Decimal(0))
    cin = sum((d(CHI[j])*e[f'c[{j}]'] for j in range(3)), Decimal(0))
    bind_photo = sum((d(CHI[j])*e[f'p[{j}]'] for j in range(3)), Decimal(0))
    bind_recomb = sum((d(CHI[j])*e[f'r[{j}]'] for j in range(3)), Decimal(0)) + d(CHI[1])*e['d']
    b_micro = bind_photo + cin - bind_recomb
    rad = ce + rrheat + e['dr'] + e['ff']
    dx = [d(after['fractions'][j])-d(before['fractions'][j]) for j in range(3)]
    dn = exact_sum(after['number'])-exact_sum(before['number'])
    du = exact_sum(after['energy_ref'])-exact_sum(before['energy_ref'])
    dw = d(after['w_ev'])-d(before['w_ev'])
    db = binding(after)-binding(before)
    return {
        'HII_event_per_H': dx[0]-net[0],
        'HeII_event_per_H': d(Y)*dx[1]-(net[1]-e['d']-net[2]),
        'HeIII_event_per_H': d(Y)*dx[2]-net[2],
        'electron_event_per_H': electron(after)-electron(before)-(net[0]+net[1]-e['d']+net[2]),
        'photo_binding_eV_per_H': e['photo_binding']-bind_photo,
        'binding_change_eV_per_H': db-b_micro,
        'escape_decomposition_eV_per_H': e['escape']-(bind_recomb+rad),
        'thermal_eV_per_H': dw-e['photo_heat']+cin+rad-e['cmb'],
        'gas_plus_binding_eV_per_H': dw+db+e['escape']-e['cmb']-e['photo_heat']-bind_photo,
        'photon_N_per_H': dn+sum((e[f'p[{j}]'] for j in range(3)), Decimal(0)),
        'photon_U_eV_per_H': du+e['photo_heat']+bind_photo,
        'full_photon_gas_binding_eV_per_H': dw+db+du+e['escape']-e['cmb'],
    }

def encode(state, report):
    out = [0.] * report['dimension']
    out[:3] = state['fractions']
    out[3] = state['w_ev']/report['wscale']
    for c in report['cell_coordinates']:
        k = c['cell']
        out[c['number_index']] = state['number'][k]/c['nscale']
        if c['offset_index'] is not None:
            out[c['offset_index']] = (state['energy_ref'][k]-c['lo']*state['number'][k])/((c['hi']-c['lo'])*c['nscale'])
    return out

def audit(path):
    raw = json.loads((path/'raw.json').read_text())
    outcome = json.loads((path/'outcome.json').read_text())
    inputs = json.loads((path/'inputs.json').read_text())
    assert raw['completed'] and raw['failure'] is None and outcome['exit_code'] == 0 and not outcome['truncated']
    assert raw['mode'] == 'fixed' and raw['method'] == 'radau'
    assert raw['config']['q'] == 0 and raw['config']['Xend'] == 0
    source_binding = {'archive_available': (path/'sources.tar.gz').exists()}
    if source_binding['archive_available']:
        mismatch = []
        with tarfile.open(path/'sources.tar.gz') as archive:
            for name, expected in inputs['source_sha256'].items():
                actual = hashlib.sha256(archive.extractfile(name).read()).hexdigest()
                if actual != expected:
                    mismatch.append(name)
        source_binding.update(archive_sha256=sha(path/'sources.tar.gz'),
                              archive_sha_matches=sha(path/'sources.tar.gz') == inputs['source_archive_sha256'],
                              manifest_entries=len(inputs['source_sha256']), manifest_mismatches=mismatch)
    maxima = {}
    def record(key, value):
        v = float(abs(value))
        maxima[key] = max(maxima.get(key, 0.), v)
    summed = None
    before = raw['initial']
    step_details = []
    stage_count = 0
    min_scaled_n = math.inf
    min_scaled_offset = math.inf
    min_scaled_upper_slack = math.inf
    for record_raw in raw['records']:
        after, report = record_raw['state'], record_raw['report']
        assert before['a'] == after['a'] == raw['initial']['a']
        assert len(report['stages']) == 3
        q = quadrature(report['stages'])
        if summed is None:
            summed = {key: Decimal(0) for key in q}
        for key, value in q.items():
            summed[key] += value
            record('shared_quadrature_' + key, value-d(flatten_events(report['integrated'])[key]))
        for key, value in chemical_balances(before, after, q).items():
            record(key, value)
        for s in [before, after]:
            record('electron_state_per_H', d(s['electron_per_h'])-electron(s))
            w_eos = d(1.5)*d(KB)/d(EV)*d(s['temperature_k'])*(1+d(Y)+electron(s))
            record('EOS_w_eV_per_H', d(s['w_ev'])-w_eos)
            record('pool_N_per_H', exact_sum(s['number'])-d(s['pools'][0]))
            record('pool_U_eV_per_H', exact_sum(s['energy_ref'])-d(s['pools'][1]))
            assert s['pools'][2:] == [0., 0.]
        for base, channel in [('photo','p'), ('ci','c'), ('rr','r'), ('ci_floor','ci_floor')]:
            for j in range(3):
                record('ledger_' + base, d(after['ledgers'][base][j])-d(before['ledgers'][base][j])-q[f'{channel}[{j}]'])
        for name, channel in [('dr','d'),('escaped_u','escape'),('cmb_input','cmb'),('ce_cap','ce_cap'),('excluded_dr','excluded_dr')]:
            record('ledger_'+name, d(after['ledgers'][name])-d(before['ledgers'][name])-q[channel])
        record('ledger_absorbed_N', d(after['ledgers']['absorbed_n'])-d(before['ledgers']['absorbed_n'])-sum((q[f'p[{j}]'] for j in range(3)), Decimal(0)))
        y0, y1 = encode(before, report), encode(after, report)
        atol = raw['config']['newton_atol_scaled']
        for i, stage in enumerate(report['stages']):
            stage_count += 1
            assert stage['weight'] == B[i] and stage['dt_s'] == report['dt_s']
            e = flatten_events(stage['events_per_h_s'])
            ed = {k:d(v) for k,v in e.items()}
            net = species_event(ed)
            rad = sum((ed[f'ce[{j}]']+ed[f'rr[{j}]'] for j in range(3)), Decimal(0))+ed['dr']+ed['ff']
            cin = sum((d(CHI[j])*ed[f'c[{j}]'] for j in range(3)), Decimal(0))
            gas_rhs = [net[0], (net[1]-ed['d']-net[2])/d(Y), net[2]/d(Y),
                       (ed['photo_heat']-cin-rad+ed['cmb'])/d(report['wscale'])]
            for k in range(report['dimension']):
                expected = d(y0[k])+sum((d(A[i][j])*d(report['stages'][j]['increments'][k]) for j in range(3)), Decimal(0))
                record('stage_reconstruction_scaled_coordinate', d(stage['scaled_state'][k])-expected)
            for k in range(4):
                independent_residual = d(stage['increments'][k])-d(report['dt_s'])*gas_rhs[k]
                record('gas_stage_residual_scaled_over_atol', independent_residual/d(atol))
                record('gas_stage_residual_report_disagreement_scaled', independent_residual-d(stage['scaled_residual'][k])*d(atol))
            for j in range(3):
                record('node_vs_point_P_rate', d(stage['node_photo_per_h_s'][j])-ed[f'p[{j}]'])
            record('node_vs_point_binding_rate', d(stage['node_binding_ev_per_h_s'])-ed['photo_binding'])
            record('node_vs_point_heat_rate', d(stage['node_heat_ev_per_h_s'])-ed['photo_heat'])
            for c in report['cell_coordinates']:
                n = stage['scaled_state'][c['number_index']]
                assert n > 0 and c['nscale'] > 0
                min_scaled_n = min(min_scaled_n, n)
                if c['offset_index'] is not None:
                    offset = stage['scaled_state'][c['offset_index']]
                    assert 0 <= offset <= n
                    min_scaled_offset = min(min_scaled_offset, offset)
                    min_scaled_upper_slack = min(min_scaled_upper_slack, n-offset)
        for k in range(report['dimension']):
            weighted = sum((d(B[i])*d(report['stages'][i]['increments'][k]) for i in range(3)), Decimal(0))
            record('endpoint_reconstruction_scaled_over_atol', (d(y1[k])-d(y0[k])-weighted)/d(atol))
        step_details.append({'step':record_raw['step'], 'dimension':report['dimension'],
                             'prepared_nodes':[s['nodes'] for s in report['stages']],
                             'native_rhs_attempts':report['native_rhs_calls'],
                             'balances':{k:float(v) for k,v in chemical_balances(before,after,q).items()}})
        before = after
    total = chemical_balances(raw['initial'], raw['records'][-1]['state'], summed)
    return {
        'schema':'independent_c9_fixed_raw_audit_v1',
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reviewer':'/root/dropbox_v15_intake (Astra), not adapter author',
        'raw_path':str(path/'raw.json'), 'raw_sha256':sha(path/'raw.json'),
        'scope':'Read-only reconstruction from actual raw endpoint arrays and stage event rates; no native calls or new histories.',
        'arithmetic':'Decimal60 on exact binary64 round-trips; configured Y, native binary64 tableau constants.',
        'Y':Y, 'threshold_eV':CHI, 'source_binding':source_binding,
        'stdout_hash_matches':sha(path/'stdout.txt') == outcome['stdout_sha256'],
        'stderr_hash_matches':sha(path/'stderr.txt') == outcome['stderr_sha256'],
        'outcome':outcome, 'binary_sha256':inputs.get('executables_sha256',{}),
        'unique_case':{'mode':raw['mode'],'method':raw['method'],'N':raw['N']},
        'accepted_steps':len(raw['records']), 'accepted_stages':stage_count,
        'native_rhs_attempts_total':raw['native_rhs_attempts_including_fd_replay'],
        'native_rhs_attempts_sum_reports':sum(r['report']['native_rhs_calls'] for r in raw['records']),
        'max_abs_step_audits':maxima,
        'total_signed_balances':{k:float(v) for k,v in total.items()},
        'total_quadrature':{k:float(v) for k,v in summed.items()},
        'source_seed_inventory_roundoff':{
            'N':float(exact_sum(raw['initial']['number'])-d(raw['initial']['ledgers']['source_n'])),
            'U':float(exact_sum(raw['initial']['energy_ref'])-d(raw['initial']['ledgers']['source_u']))},
        'stage_domain':{'minimum_scaled_N':min_scaled_n,'minimum_scaled_offset':min_scaled_offset,
                        'minimum_scaled_upper_support_slack':min_scaled_upper_slack},
        'steps':step_details,
        'limits':[
            'One fixed native N=4 case does not establish time order or a stiff error bound.',
            'Per-cell native RHS arrays and quadrature-node values are absent from raw; photon inventory and event totals are independently checked, not every per-cell derivative.',
            'Only negative CMB transfer, zero work/passive-boundary and the actual configured source seed are covered here.',
            'Library audit columns are not used for independent endpoint/channel balances; gas residuals are reconstructed from P/C/R/D and thermal channels.'
        ]
    }

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('receipt_dir',type=Path); ap.add_argument('output',type=Path)
    args=ap.parse_args()
    with localcontext() as context:
        context.prec=60
        result=audit(args.receipt_dir)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'total_signed_balances':result['total_signed_balances'],
                      'accepted_steps':result['accepted_steps'],'accepted_stages':result['accepted_stages'],
                      'native_rhs_attempts_total':result['native_rhs_attempts_total']},indent=2))
