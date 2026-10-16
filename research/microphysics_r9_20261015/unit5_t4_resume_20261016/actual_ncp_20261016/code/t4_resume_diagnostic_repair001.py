#!/usr/bin/env python3
"""Unit5 cached Krylov continuation. Native run requires a new explicit allocation."""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'baseline/t4_spectral_repair001.py'
LEGACY_SHA = 'b9a14d1bfa192da17b7c2a6dfa20560964d553b3c0ba30343a45bb90ee09db7a'
spec = importlib.util.spec_from_file_location('t4_frozen_repair001', BASELINE)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.require(b.sha(BASELINE) == LEGACY_SHA, 'immutable baseline byte identity mismatch')
OPERATOR = 'Q(H-E0)Q;symmetric-integrals-repair001;V6-raw_action'
UNIT = 'R9-T4-CHECKPOINT-RESUME-v1'
HISTORY = {'terminal_actions': 'UNKNOWN', 'terminal_action_interval': [86, 160],
           'absolute_deadline_utc': '2026-10-16T01:51:37.258157Z', 'old_allowance_reset': False}
require = b.require


def identities():
    return {k: b.IDENTITIES[k] for k in ('receipt', 'data', 'v6_source')}


def remainder(V, kv, ground):
    """Cached seam: Q/MGS twice/Q; the previous-beta term is in span(V)."""
    r = b.project(kv - V[:, -1]*np.vdot(V[:, -1], kv), ground)
    for _ in range(2):
        for v in V.T:
            r -= v*np.vdot(v, r)
    return b.project(r, ground)


def residual_diagnostic(V, KV, u, W, grid=b.GRID, etas=b.ETAS):
    """Direct residual evaluation, bounded memory (one grid point at a time)."""
    C = V.conj().T @ KV
    J = (C + C.conj().T)/2
    nodes, Y = np.linalg.eigh(J)
    e1 = np.zeros(V.shape[1], dtype=J.dtype); e1[0] = 1
    d, E = u - V[:, 0], KV - V@J
    delta_row = u.conj()@V - e1.conj()
    bounds, scalars, norms, deltas = [], [], [], []
    for eta in etas:
        require(np.isfinite(eta) and eta > 0, 'eta must be positive')
        rows, ms, rs, ds = [], [], [], []
        for omega in grid:
            t = Y @ ((Y.conj().T@e1)/(omega+1j*eta-nodes))
            rn = float(np.linalg.norm(d+E@t))
            delta = float(abs(delta_row@t))
            rows.append(float(np.linalg.norm(u))*rn/eta+delta)
            ms.append(t[0]); rs.append(rn); ds.append(delta)
        bounds.append(rows); scalars.append(ms); norms.append(rs); deltas.append(ds)
    bounds = np.asarray(bounds)
    trap = getattr(np, 'trapezoid', None)
    if trap is None:
        trap = np.trapz
    return {'grid': np.asarray(grid), 'etas': np.asarray(etas), 'scalar_resolvent': np.asarray(scalars),
            'scalar_bound': bounds, 'density_bound': W*bounds/np.pi,
            'residual_norm': np.asarray(norms), 'coordinate_delta': np.asarray(deltas),
            'summary': {'classification': 'floating-point conditional residual diagnostic; not interval certification',
                'formula': 'norm(u)*norm(d+(KV-VJ)t)/eta+abs((u^dagger V-e1^dagger)t)',
                'evaluation': 'direct norms; no Gram clipping', 'changes_refinement_rule': False,
                'max_scalar_bound_per_eta': bounds.max(axis=1).tolist(),
                'max_density_bound_per_eta': (W*bounds/np.pi).max(axis=1).tolist(),
                'grid_integral_density_bound_per_eta': [float(trap(row, grid)) for row in W*bounds/np.pi]}}


def recover_corrections(metadata, milestone, m):
    values = metadata.get('reorthogonalization_correction_norms_Eh')
    origin = 'checkpoint'
    if values is None and milestone is not None:
        diag = json.loads(Path(milestone).read_text())
        require(diag.get('length') == m and diag.get('passed') is True, 'milestone correction metadata mismatch')
        if 'direct_moments' in metadata:
            require(np.allclose(diag.get('direct_moments'), metadata['direct_moments'], rtol=1e-8, atol=1e-8), 'milestone direct moments mismatch')
        values = diag.get('reorthogonalization_correction_norms_Eh')
        origin = 'matching_milestone'
    if values is None:
        return [None]*m, 'historical_unknown'
    require(isinstance(values, list) and len(values) == m, 'invalid correction list')
    require(all(x is None or (isinstance(x, (int, float)) and np.isfinite(x) and x >= 0) for x in values), 'invalid correction values')
    return values.copy(), origin


def load_checkpoint(path, ground, u, W, expected=None, milestone=None):
    expected = identities() if expected is None else expected
    with np.load(path, allow_pickle=False) as f:
        required = ('V', 'KV', 'ground', 'u', 'next_vector', 'metadata_json')
        require(all(k in f.files for k in required), 'missing checkpoint arrays')
        a = {k: f[k].copy() for k in required}
    require(a['metadata_json'].shape == (), 'metadata_json must be scalar')
    md = json.loads(str(a.pop('metadata_json').item()))
    require(isinstance(md, dict), 'metadata must be object')
    V, KV = a['V'], a['KV']
    m = md.get('length')
    require(type(m) is int and 1 <= m <= 128, 'invalid checkpoint length')
    require(V.ndim == 2 and V.shape == KV.shape and V.shape == (len(u), m), 'checkpoint shape mismatch')
    require(np.asarray(ground).shape == np.asarray(u).shape == (V.shape[0],), 'working vector shape mismatch')
    for key, value in a.items():
        require(np.issubdtype(value.dtype, np.number) and np.all(np.isfinite(value)), 'nonfinite or nonnumeric checkpoint: '+key)
        if key not in ('V', 'KV'):
            require(value.shape == u.shape, 'checkpoint vector shape mismatch: '+key)
    ids = md.get('identities')
    require(isinstance(ids, dict) and all(ids.get(k) == v for k, v in expected.items()), 'immutable input identity mismatch')
    runner = ids.get('runner')
    # The sole legacy mapping binds the pinned runner's implicit operator convention.
    current = b.sha(__file__)
    require(runner in (LEGACY_SHA, current), 'unmapped runner BYTE_IDENTITY_MISMATCH')
    require(md.get('operator', OPERATOR if runner == LEGACY_SHA else None) == OPERATOR, 'operator convention mismatch')
    require(md.get('unit') in (b.UNIT, UNIT), 'checkpoint unit mismatch')
    beta = md.get('next_beta')
    require(isinstance(beta, (int, float)) and not isinstance(beta, bool) and np.isfinite(beta) and beta >= 0, 'invalid next_beta')
    require(np.linalg.norm(a['ground']-ground) <= 1e-10 and np.linalg.norm(a['u']-u) <= 1e-10, 'working g/u mismatch')
    require(np.linalg.norm(V[:, 0]-u) <= 1e-10, 'initial-coordinate mismatch')
    direct = [W, W*float(np.vdot(u, KV[:, 0]).real), W*float(np.vdot(KV[:, 0], KV[:, 0]).real)]
    if 'direct_moments' in md:
        old = np.asarray(md['direct_moments'])
        require(old.shape == (3,) and np.all(np.isfinite(old)) and np.all(abs(old-direct) <= 1e-8*np.maximum(1, abs(np.asarray(direct)))), 'recorded direct moments mismatch')
    corrections, correction_origin = recover_corrections(md, milestone, m)
    r = remainder(V, KV[:, -1], ground)
    scale = max(1., float(np.linalg.norm(KV[:, -1])))
    happy = beta <= 1e-12*scale
    if happy:
        require(np.linalg.norm(a['next_vector']) <= 1e-10, 'breakdown next_vector must be zero')
    else:
        nv = a['next_vector']
        require(abs(np.linalg.norm(nv)-1) <= 1e-9 and np.max(abs(V.conj().T@nv)) <= 1e-9 and abs(np.vdot(ground, nv)) <= 1e-9, 'next_vector orthogonality/norm mismatch')
    seam = float(np.linalg.norm(r-beta*a['next_vector']))
    require(seam <= 1e-9*scale, 'cached recurrence seam mismatch')
    records, prior, prior_m, spectral = [], None, None, None
    for n in sorted(set([x for x in b.MILESTONES if x <= m]+[m])):
        rn = remainder(V[:, :n], KV[:, n-1], ground)
        bn = float(np.linalg.norm(rn)); hn = bn <= 1e-12*max(1., float(np.linalg.norm(KV[:, n-1])))
        diag, spectral, broad = b.compressed_measure(V[:, :n], KV[:, :n], ground, W, direct, bn, corrections[:n], hn)
        require(diag['passed'], 'cached compressed gates failed at '+str(n))
        diag.update(refinement=b.refinement(prior, broad, W) if prior is not None else None,
                    refinement_pair=[prior_m, n] if prior_m else None, reconstructed_from_cache=True)
        records.append(diag); prior, prior_m = broad, n
    last = records[-1]
    stop = ('negative_node_requires_Astra_interpretation' if last['negative_node_interpretation_flag'] else
            'certified_invariant_subspace' if happy else
            'declared_broadening_refinement_met' if m in (64, 128) and last['refinement_pair'] == [m//2, m] and last['refinement']['passed'] else None)
    return {**a, 'metadata': md, 'length': m, 'direct': direct, 'corrections': corrections,
            'correction_origin': correction_origin, 'records': records, 'prior_broad': prior,
            'spectral': spectral, 'stop': stop, 'next_beta': float(beta),
            'validation': {'cached_seam_l2': seam, 'cached_seam_scaled': seam/scale,
                'legacy_runner_sha256': runner, 'resume_runner_sha256': current,
                'semantic_mapping': 'explicit repair001 mapping' if runner == LEGACY_SHA else 'same resume implementation',
                'operator': OPERATOR, 'recompression_H_actions': 0}}


def cache_seam_checks(action, state):
    V, KV = state['V'], state['KV']; m = V.shape[1]
    c = (-1.)**np.arange(m)*(np.arange(m)+1); c /= np.linalg.norm(c)
    checks = []
    for name, x, cached in [('first', V[:, 0], KV[:, 0]), ('last', V[:, -1], KV[:, -1]), ('combination', V@c, KV@c)]:
        fresh = action(x)
        err = float(np.linalg.norm(fresh-cached)); scale = max(1., float(np.linalg.norm(fresh)), float(np.linalg.norm(cached)))
        checks.append({'name': name, 'absolute': err, 'scaled': err/scale, 'limit_scaled': 1e-9, 'pass': err <= 1e-9*scale})
    return {'passed': all(x['pass'] for x in checks), 'gates': checks, 'actions': 3, 'claim': 'deterministic sample; not proof of all cached columns'}


def write_checkpoint(out, V, KV, ground, u, residual, beta, happy, direct, corrections, source_ids, budget):
    md = {'unit': UNIT, 'identities': {**source_ids, 'runner': b.sha(__file__)}, 'operator': OPERATOR,
          'length': V.shape[1], 'next_beta': beta, 'direct_moments': direct,
          'reorthogonalization_correction_norms_Eh': corrections,
          'new_Hamiltonian_actions': budget.actions if budget else None,
          'history': HISTORY, 'saved_utc': b.utc()}
    b.save_npz(out/'checkpoint.npz', V=V, KV=KV, ground=ground, u=u,
               next_vector=np.zeros_like(residual) if happy else residual/beta,
               metadata_json=np.asarray(json.dumps(md, sort_keys=True)))


def resume_chain(action, state, ground, u, W, max_length=128, budget=None, out=None, source_ids=None):
    m = state['length']; require(m <= max_length <= 128, 'invalid resume cap')
    if out is not None:
        out = Path(out); require(out.is_dir(), 'output directory missing')
        require(not (out/'checkpoint.npz').exists(), 'refuse existing output checkpoint')
    V = np.empty((len(u), max_length), dtype=np.result_type(state['V'], state['KV']), order='F')
    KV = np.empty_like(V); V[:, :m] = state['V']; KV[:, :m] = state['KV']
    records = list(state['records']); prior = state['prior_broad']; prior_m = m
    corrections = state['corrections'].copy(); direct = state['direct']; spectral = state['spectral']
    v = state['next_vector'].copy(); previous_beta = state['next_beta']
    termination = state['stop'] or 'maximum_length'; length = m
    if not state['stop']:
        for j in range(m, max_length):
            if budget: budget.check()
            V[:, j] = v; kv = action(v); KV[:, j] = kv
            raw = kv - v*np.vdot(v, kv) - previous_beta*V[:, j-1]
            residual = b.project(raw, ground)
            for _ in range(2):
                for index in range(j+1):
                    residual -= V[:, index]*np.vdot(V[:, index], residual)
            residual = b.project(residual, ground)
            corrections.append(float(np.linalg.norm(raw-residual)))
            beta = float(np.linalg.norm(residual)); threshold = 1e-12*max(1., float(np.linalg.norm(kv)))
            happy = beta <= threshold; length = j+1
            if length in b.MILESTONES or happy or length == max_length:
                diag, spectral, broad = b.compressed_measure(V[:, :length], KV[:, :length], ground, W, direct, beta, corrections.copy(), happy)
                diag.update(breakdown_threshold_Eh=threshold, refinement=b.refinement(prior, broad, W), refinement_pair=[prior_m, length])
                require(diag['passed'], 'resumed numerical gate failed at '+str(length))
                records.append(diag)
                if out:
                    b.dump(out/('milestone_%03d.json'%length), diag)
                    b.save_npz(out/('milestone_%03d.npz'%length), **spectral)
                    write_checkpoint(out, V[:, :length], KV[:, :length], ground, u, residual, beta, happy, direct, corrections, source_ids or identities(), budget)
                if diag['negative_node_interpretation_flag']: termination = 'negative_node_requires_Astra_interpretation'; break
                if happy: termination = 'certified_invariant_subspace'; break
                if length in (64, 128) and prior_m == length//2 and diag['refinement']['passed']:
                    termination = 'declared_broadening_refinement_met'; break
                prior, prior_m = broad, length
            v, previous_beta = residual/beta, beta
    return {'milestones': records, 'last_length': length, 'restored_length': m, 'first_new_index_zero_based': m,
            'added_columns': length-m, 'termination': termination, 'direct_moments': direct,
            'refinement_met': termination == 'declared_broadening_refinement_met',
            'invariant_subspace': termination == 'certified_invariant_subspace',
            'historical_corrections': state['correction_origin'], 'scope': b.SCOPE}, spectral, V[:, :length], KV[:, :length]


def validate_allocation(a, now=None):
    require(a.get('authorized') is True, 'separately explicit new allocation authorization required')
    require(isinstance(a.get('allocation_id'), str) and a['allocation_id'].strip(), 'allocation_id required')
    require(a.get('maximum_new_Hamiltonian_actions') == 70 and a.get('wall_s') == 7200 and a.get('memory_gib') == 24 and a.get('omp_threads') == 12 and a.get('blas_threads') == 1, 'new allocation resource contract mismatch')
    issued = dt.datetime.fromisoformat(a['issued_utc'].replace('Z', '+00:00'))
    end = dt.datetime.fromisoformat(a['absolute_deadline_utc'].replace('Z', '+00:00'))
    require(issued.tzinfo is not None and end.tzinfo is not None and 0 < (end-issued).total_seconds() <= 7200, 'invalid new allocation time interval')
    epoch = time.time() if now is None else now
    require(issued.timestamp() <= epoch < end.timestamp(), 'new allocation expired or not issued')
    require(a['absolute_deadline_utc'] != HISTORY['absolute_deadline_utc'], 'old allocation cannot be reset')
    return min(7200., end.timestamp()-epoch)


def native_worker(config_path):
    c = json.loads(Path(config_path).read_text()); out = Path(c['out']); a = c['allocation']
    resource.setrlimit(resource.RLIMIT_AS, (24*1024**3, 24*1024**3))
    budget = b.ActionBudget(time.monotonic()+validate_allocation(a), maximum=70)
    receipt = {'unit': UNIT, 'status': 'failure', 'numerical_passed': False, 'history': HISTORY,
               'new_allocation': a, 'runtime': b.runtime(), 'actual_checkpoint_compatibility': 'attempted', 'started_utc': b.utc()}
    try:
        r, arrays, i, g, u, info = b.load_saved(c['receipt'], c['data'])
        require(b.sha(c['checkpoint']) == json.loads((ROOT/'intake/SOURCE_PIN.json').read_text())['actual_checkpoint_sha256'], 'actual checkpoint byte identity mismatch')
        state = load_checkpoint(c['checkpoint'], g, u, info['W'], milestone=c.get('milestone'))
        b.dump(out/'restore.json', state['validation'])
        # Honor a restored stopping decision before reconstruction consumes H actions.
        if state['stop']:
            result, spectral, V, KV = resume_chain(None, state, g, u, info['W'], out=out)
        else:
            checks, K = b.reconstruct(r, arrays, i, g, u, info, c['v6_source'], budget)
            b.dump(out/'reconstruction.json', checks); require(checks['passed'], 'reconstruction gates failed')
            seam = cache_seam_checks(K, state); b.dump(out/'operator_seam.json', seam)
            require(seam['passed'], 'fresh operator cache seam failed')
            result, spectral, V, KV = resume_chain(K, state, g, u, info['W'], budget=budget, out=out)
        b.dump(out/'chain.json', result); b.save_npz(out/'spectra.npz', **spectral)
        diagnostic = residual_diagnostic(V, KV, u, info['W'])
        b.dump(out/'residual_summary.json', diagnostic.pop('summary')); b.save_npz(out/'residual.npz', **diagnostic)
        success = result['refinement_met'] or result['invariant_subspace']
        receipt.update(status='success' if success else 'partial', numerical_passed=success, last_length=result['last_length'], termination=result['termination'])
    except b.Deferred as e:
        receipt.update(status='partial' if (out/'checkpoint.npz').exists() else 'deferred', reason=str(e))
    except Exception as e:
        receipt.update(reason=str(e), traceback=traceback.format_exc()); print(receipt['traceback'], file=sys.stderr)
    receipt.update(new_Hamiltonian_actions=budget.actions,
                   campaign_action_interval=[86+budget.actions, 160+budget.actions],
                   terminal_historical_actions='UNKNOWN', completed_utc=b.utc())
    b.dump(out/'receipt.json', receipt)
    return 0 if receipt['status'] in ('success', 'partial') else 3 if receipt['status'] == 'deferred' else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='mode', required=True)
    q = sub.add_parser('prepare'); q.add_argument('--out', type=Path, required=True)
    q = sub.add_parser('run')
    for name in ('receipt', 'data', 'v6-source', 'checkpoint', 'allocation', 'out'):
        q.add_argument('--'+name, type=Path, required=True)
    q.add_argument('--milestone', type=Path)
    q = sub.add_parser('__worker'); q.add_argument('--config', type=Path, required=True)
    args = p.parse_args(argv)
    if args.mode == '__worker': return native_worker(args.config)
    try:
        if args.mode == 'prepare':
            args.out.mkdir(parents=True, exist_ok=False)
            b.dump(args.out/'allocation_template.json', {'authorized': False, 'execution': 'NOT_RUN', 'allocation_id': None,
                'issued_utc': None, 'absolute_deadline_utc': None, 'wall_s': 7200, 'memory_gib': 24,
                'omp_threads': 12, 'blas_threads': 1, 'maximum_new_Hamiltonian_actions': 70, 'max_length': 128,
                'historical_allocation': HISTORY})
            return 0
        a = json.loads(args.allocation.read_text()); remaining = validate_allocation(a)
        require(os.cpu_count() >= 12, 'fewer than 12 host CPUs')
        require(b.sha(args.v6_source) == b.IDENTITIES['v6_source'], 'immutable V6 source mismatch')
        args.out.mkdir(parents=True, exist_ok=False)
        config = {key: str(getattr(args, key).resolve()) for key in ('receipt', 'data', 'v6_source', 'checkpoint', 'out')}
        if args.milestone: config['milestone'] = str(args.milestone.resolve())
        config['allocation'] = a; b.dump(args.out/'worker_config.json', config)
        env = os.environ | {'OMP_NUM_THREADS': '12', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'}
        command = [sys.executable, str(Path(__file__).resolve()), '__worker', '--config', str((args.out/'worker_config.json').resolve())]
        result = b.supervise(command, args.out, remaining, 24., env=env)
        # A killed worker's exact terminal count is unknown; never manufacture zero.
        if 'new_Hamiltonian_actions' not in result:
            result.update(new_Hamiltonian_actions='UNKNOWN', new_action_interval=[0, 70],
                          campaign_action_interval=[86, 230], history=HISTORY)
        b.dump(args.out/'receipt.json', result); print(json.dumps(result, indent=2))
        return 0 if result['status'] in ('success', 'partial') else 3 if result['status'] == 'deferred' else 1
    except Exception as e:
        print(str(e), file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
