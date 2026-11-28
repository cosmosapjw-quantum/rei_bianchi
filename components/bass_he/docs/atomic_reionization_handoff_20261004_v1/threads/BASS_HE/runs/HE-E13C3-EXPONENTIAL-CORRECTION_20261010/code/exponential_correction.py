"""First coefficient-variation photon correction on sealed E13C2 inputs.

Uses exact frozen damping and one-dimensional adjoint moment kernels. This
module never calls the old continuous ODE or advances gas. The imported pinned
E13C2 module supplies only physical coefficients, frozen stock, input parsing,
and unit projection. First-variation ledger closure is not exact satisfaction
of the original full-coefficient equation: its residual is delta_Lambda * e1.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
import time
import traceback

import numpy as np

LD = np.longdouble


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.' + path.name, delete=False) as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
        tmp = f.name
    os.replace(tmp, path)


def load_model(root):
    if np.finfo(LD).nmant + 1 < 64:
        raise RuntimeError('at least 64 significand bits required; no silent fallback')
    manifest = json.loads((root / 'inputs/INPUT_MANIFEST.json').read_text())
    for item in manifest:
        path = root / item['path']
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('input identity mismatch: ' + item['path'])
    path = root / 'inputs/e13c2/code/continuous_defect.py'
    spec = importlib.util.spec_from_file_location('sealed_e13c2_coefficients', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def J(rate, width):
    """Integral of exp(-rate*u), with a cancellation-safe zero-rate limit."""
    a, h = np.broadcast_arrays(np.asarray(rate, dtype=LD), np.asarray(width, dtype=LD))
    if np.any(a < 0) or np.any(h < 0):
        raise ValueError('J requires nonnegative rate and width')
    out = np.empty_like(a)
    nz = a != 0
    out[nz] = -np.expm1(-a[nz] * h[nz]) / a[nz]
    out[~nz] = h[~nz]
    return out


def gauss_rule(order):
    """NumPy seeds refined in longdouble; no rounded physical input cache."""
    seeds, _ = np.polynomial.legendre.leggauss(order)
    x = seeds.astype(LD)
    def poly(x):
        p0 = np.ones_like(x)
        p1 = x.copy()
        for k in range(2, order + 1):
            p0, p1 = p1, ((LD(2*k-1)*x*p1) - LD(k-1)*p0)/LD(k)
        derivative = LD(order) * (x*p1-p0)/(x*x-LD(1))
        return p1, derivative
    for _ in range(8):
        p, derivative = poly(x)
        update = p / derivative
        x -= update
        if np.max(np.abs(update)) <= LD(4)*np.finfo(LD).eps:
            break
    x = (x - x[::-1])/LD(2)
    _, derivative = poly(x)
    weights = LD(1)/((LD(1)-x*x)*derivative*derivative)
    weights = (weights + weights[::-1])/LD(2)
    weights /= weights.sum()
    nodes = (x + LD(1))/LD(2)
    error = max(abs(np.sum(weights*nodes**k)-LD(1)/LD(k+1)) for k in range(2*order))
    if error > LD('1e-17') or np.any(weights <= 0):
        raise ValueError('Gauss rule moment or positivity failure')
    return nodes, weights, float(error)


def correction(batch, incoming, order):
    """Return the same 16 moment slots used in the sealed E13C2 evidence."""
    nodes, weights, rule_error = gauss_rule(order)
    ea = np.asarray(incoming, dtype=LD)
    if ea.shape != (batch.count,) or not np.all(np.isfinite(ea)):
        raise ValueError('invalid incoming correction')
    h, L, E0 = batch.h, batch.Lf, batch.e0
    end = np.zeros((16, batch.count), dtype=LD)
    end[0] = np.exp(-L*h)*ea
    I0 = J(L, h)*ea
    IE = E0*J(L+LD(1), h)*ea
    D = np.zeros(batch.count, dtype=LD)
    Br = np.zeros(batch.count, dtype=LD)
    for t, weight in zip(nodes, weights):
        lam, q, energy = batch.coeff(t)
        pf = batch.frozen_stock(t)
        dlam, dq = lam-batch.lf, q-batch.qf
        direct = dlam*pf
        dL = dlam.sum(axis=0)
        forcing = dq-direct.sum(axis=0)
        remaining = h*(LD(1)-t)
        measure = h*weight
        end[0] += measure*np.exp(-L*remaining)*forcing
        I0 += measure*J(L, remaining)*forcing
        IE += measure*energy*J(L+LD(1), remaining)*forcing
        end[1:4] += measure*direct
        end[7:10] += measure*energy*direct
        end[14] += measure*dq
        end[15] += measure*energy*dq
        D += measure*np.abs(dL)
        Br += measure*(np.abs(dq)+np.abs(dL)*pf)
    end[4:7] = batch.lf*I0
    end[10:13] = batch.lf*IE
    end[13] = IE
    pf_end = batch.frozen_stock(LD(1))
    photon_end = pf_end+end[0]
    if not np.all(np.isfinite(end)) or np.any(photon_end < 0):
        raise ValueError('nonfinite correction or negative approximate photon endpoint')
    dA = end[1:4]+end[4:7]
    dB = end[7:10]+end[10:13]
    nledger = end[0]-ea+dA.sum(axis=0)-end[14]
    eledger = E0*(np.exp(-h)*end[0]-ea)+dB.sum(axis=0)+IE-end[15]
    meta = {'order': order, 'segments': batch.count,
            'physical_coefficient_samples': order*batch.count,
            'gauss_moment_error': rule_error,
            'max_number_first_variation_ledger': float(np.max(np.abs(nledger))),
            'max_energy_first_variation_ledger_eV': float(np.max(np.abs(eledger))),
            'min_corrected_photon_endpoint': float(np.min(photon_end)),
            'max_optical_depth': float(np.max(L*h)),
            'max_quadrature_estimated_D_Lambda': float(np.max(D)),
            'max_quadrature_estimated_D_times_incoming_plus_Br': float(np.max(D*(np.abs(ea)+Br))),
            'variation_integrals_are_certified_bounds': False}
    if meta['max_number_first_variation_ledger'] > 1e-22 or meta['max_energy_first_variation_ledger_eV'] > 1e-20:
        raise ArithmeticError('first-variation ledger acceptance failed')
    return end, pf_end, meta


def scalar_packet(end, model):
    a, b = end[1:4]+end[4:7], end[7:10]+end[10:13]
    heat = b-model.CHI*a
    return {'delta_P': float(end[0]), 'delta_A': [float(x) for x in a],
            'delta_B_eV': [float(x) for x in b], 'delta_heat_eV': [float(x) for x in heat],
            'delta_total_heat_eV': float(heat.sum()),
            'direct_A': [float(x) for x in end[1:4]],
            'response_A': [float(x) for x in end[4:7]],
            'direct_B_eV': [float(x) for x in end[7:10]],
            'response_B_eV': [float(x) for x in end[10:13]],
            'delta_redshift_eV': float(end[13]),
            'delta_source_number': float(end[14]), 'delta_source_energy_eV': float(end[15])}


def local_work(root, model, order):
    original = root/'inputs/e13c2/inputs/upstream_e13c1'
    rows_by_mode, stages = {}, {}
    for mode in ('OFF', 'GM'):
        rows_by_mode[mode] = model.read_csv(original/f'evidence/capture/{mode}/SEGMENTS.csv')
        stages[mode] = model.read_csv(original/f'inputs/{mode}_STAGES.csv')
    results = []
    for mode, step, node, segment in model.SELECTED:
        row = next(x for x in rows_by_mode[mode] if (int(x['step']), int(x['node']), int(x['segment'])) == (step, node, segment))
        batch = model.SegmentBatch([row], stages[mode][step-1])
        end, _, meta = correction(batch, np.zeros(1, dtype=LD), order)
        results.append({'id': [mode, step, node, segment],
                        'initial': 'captured f0; incoming correction zero',
                        **scalar_packet(end[:, 0], model), 'meta': meta})
    return {'local_controls': results, 'physical_coefficient_samples': sum(x['meta']['physical_coefficient_samples'] for x in results)}


def path_work(root, model, order, out):
    # Conditional full-path expansion is gated by actual saved local checks.
    gate = json.loads((root/'evidence/LOCAL_ACCEPTANCE.json').read_text())
    if gate['verdict'] != 'PASS_SCOPED':
        raise ValueError('local gate has not admitted first2 expansion')
    original = root/'inputs/e13c2/inputs/upstream_e13c1'
    records, nodes_all, groups = [], [], []
    for mode in ('OFF', 'KF', 'GM'):
        rows = model.read_csv(original/f'evidence/capture/{mode}/SEGMENTS.csv')
        stages = model.read_csv(original/f'inputs/{mode}_STAGES.csv')
        previous = {}
        for step in (1, 2):
            stage = stages[step-1]
            part = [x for x in rows if int(x['step']) == step]
            sums = {int(x['node']): np.zeros(16, dtype=LD) for x in part}
            weights = {int(x['node']): model.lift(x['weight']) for x in part}
            for segment in sorted(set(int(x['segment']) for x in part)):
                group = [x for x in part if int(x['segment']) == segment]
                batch = model.SegmentBatch(group, stage)
                incoming = []
                for row in group:
                    node = int(row['node'])
                    if node in previous:
                        native_end, correction_end = previous[node]
                        incoming.append(correction_end+native_end-model.lift(row['f0']))
                    else:
                        if model.lift(row['f0']) != 0:
                            raise ValueError('missing initial photon stock')
                        incoming.append(LD(0))
                end, frozen_end, meta = correction(batch, incoming, order)
                meta.update(mode=mode, step=step, segment_level=segment)
                groups.append(meta)
                for k, row in enumerate(group):
                    node = int(row['node'])
                    native_end = model.lift(row['n'])
                    carried = end[0, k]+frozen_end[k]-native_end
                    previous[node] = (native_end, carried)
                    sums[node][0] = carried
                    sums[node][1:] += end[1:, k]
            total = np.zeros(16, dtype=LD)
            for node, values in sums.items():
                total += weights[node]*values
                nodes_all.append({'mode': mode, 'step': step, 'node': node,
                                  'weight': float(weights[node]), 'defect': [float(v) for v in values]})
            packet = scalar_packet(total, model)
            a, b = total[1:4]+total[4:7], total[7:10]+total[10:13]
            proj = model.projection(a, b, model.lift(stage['fHe']))
            base_a = np.array([model.lift(stage['A_'+species]) for species in model.SPEC])
            base_b = np.array([model.lift(stage['B_'+species])/model.EPS for species in model.SPEC])
            if np.any(base_a+a < 0) or np.any(base_b+b-model.CHI*(base_a+a) < 0):
                raise ValueError('negative corrected aggregate absorption or heat estimate')
            packet.update(mode=mode, step=step,
                          projected_photo_delta=[float(v) for v in proj],
                          projected_over_old_algebraic_TOL=[float(v) for v in proj/model.TOL],
                          absolute_moments_are_native_baseline_estimates=True)
            records.append(packet)
            print(json.dumps({'mode': mode, 'step': step, 'order': order,
                              'delta_total_heat_eV': packet['delta_total_heat_eV']}), flush=True)
    write_json(out/'NODE_CORRECTIONS.json', nodes_all)
    return {'records': records, 'segment_groups': groups,
            'physical_coefficient_samples': sum(x['physical_coefficient_samples'] for x in groups)}


def run(root, out, stage, order):
    root, out = Path(root).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    provenance = {'task': 'E13C3_EXPONENTIAL_CORRECTION', 'stage': stage, 'order': order,
                  'command': [sys.executable, *sys.argv], 'producer_sha256': digest(__file__),
                  'input_manifest_sha256': digest(root/'inputs/INPUT_MANIFEST.json'),
                  'coefficient_helper_sha256': digest(root/'inputs/e13c2/code/continuous_defect.py'),
                  'python': sys.version, 'numpy': np.__version__,
                  'longdouble_significand_bits': int(np.finfo(LD).nmant+1)}
    write_json(out/'RUN_STARTED.json', provenance)
    try:
        model = load_model(root)
        payload = local_work(root, model, order) if stage == 'local' else path_work(root, model, order, out)
        result = {**provenance, **payload, 'elapsed_seconds': time.perf_counter()-start,
                  'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'native_runs': 0, 'gas_advances': 0, 'original_continuous_recomputations': 0,
                  'old_campaign_replays': 0, 'physical': 'HOLD', 'production': 'HOLD',
                  'first_variation_ledger_is_original_model_certificate': False,
                  'execution_status': 'COMPLETED_NEW_CORRECTION_ONLY'}
        write_json(out/'RESULTS.json', result)
        print(json.dumps({'stage': stage, 'order': order, 'elapsed_seconds': result['elapsed_seconds'],
                          'physical_coefficient_samples': result['physical_coefficient_samples']}), flush=True)
        return result
    except Exception as exc:
        write_json(out/'FIRST_FAILURE.json', {**provenance, 'exception': type(exc).__name__,
                   'message': str(exc), 'classification': 'UNCLASSIFIED_REQUIRES_DIAGNOSIS',
                   'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=['local', 'paths'], required=True)
    parser.add_argument('--order', type=int, choices=[8, 12], required=True)
    args = parser.parse_args()
    run(args.root, args.output, args.stage, args.order)
