#!/usr/bin/env python3
"""Binary64 four-variable chemical-stage linearized diagnostics; no producer run."""
import argparse
import hashlib
import json
import math
import numbers
import os
from pathlib import Path
import platform
import sys
import tempfile
import time

ORDER = ['x_HII', 'x_HeII', 'x_HeIII', 'w_eV_per_H']
DRIVER_BLOB = '23f0d9a40b8fb8b595d0f73dd6b279067ccadf88'
NEWTON_THRESHOLD = 1e-11
LOCAL_TARGET = 1e-5


class _Hold(ValueError):
    pass


def _require(condition, reason):
    if not condition:
        raise _Hold(reason)


def _finite(value):
    try:
        _require(math.isfinite(value), 'HOLD_NONFINITE_ARITHMETIC')
    except (OverflowError, TypeError):
        raise _Hold('HOLD_NONFINITE_ARITHMETIC') from None
    return value


def _number(value):
    _require(not isinstance(value, bool) and isinstance(value, numbers.Real),
             'HOLD_MALFORMED_NUMERIC_INPUT')
    return _finite(float(value))


def _vector(value):
    _require(isinstance(value, (list, tuple)) and len(value) == 4, 'HOLD_INVALID_VECTOR_SHAPE')
    return [_number(x) for x in value]


def _matrix(value):
    _require(isinstance(value, (list, tuple)) and len(value) == 4, 'HOLD_INVALID_MATRIX_SHAPE')
    return [_vector(row) for row in value]


def _sum(values):
    return _finite(math.fsum(values))


def _inf(vector):
    return max(abs(x) for x in vector)


def _matrix_inf(matrix):
    return max(_sum(abs(x) for x in row) for row in matrix)


def _failure(exc, **fields):
    reason = str(exc) if isinstance(exc, _Hold) else 'HOLD_NONFINITE_ARITHMETIC'
    return dict(status='HOLD', reason=reason, metrics=None, **fields)


def solve_scaled(residual, jacobian, residual_scales, state_scales):
    """Solve A*z=-b and estimate condition/backward error; exact-zero pivots only."""
    try:
        r, j = _vector(residual), _matrix(jacobian)
        sr, sy = _vector(residual_scales), _vector(state_scales)
        _require(all(x > 0 for x in sr + sy), 'HOLD_NONPOSITIVE_SCALE')
        a = [[_finite(j[i][k] * sy[k] / sr[i]) for k in range(4)] for i in range(4)]
        b = [_finite(r[i] / sr[i]) for i in range(4)]
        rows = [a[i][:] + [-b[i]] + [float(i == k) for k in range(4)] for i in range(4)]
        for col in range(4):
            pivot = max(range(col, 4), key=lambda i: abs(rows[i][col]))
            _require(rows[pivot][col] != 0.0, 'HOLD_SINGULAR_JACOBIAN')
            rows[col], rows[pivot] = rows[pivot], rows[col]
            divisor = rows[col][col]
            rows[col] = [_finite(x / divisor) for x in rows[col]]
            for i in range(4):
                if i != col:
                    factor = rows[i][col]
                    rows[i] = [_finite(x - factor*y) for x, y in zip(rows[i], rows[col])]
        z = [row[4] for row in rows]
        inverse = [row[5:] for row in rows]
        delta = [_finite(s*y) for s, y in zip(sy, z)]
        equation = [_sum([*(_finite(x*y) for x, y in zip(row, z)), bi])
                    for row, bi in zip(a, b)]
        anorm, znorm, bnorm = _matrix_inf(a), _inf(z), _inf(b)
        condition = _finite(anorm * _matrix_inf(inverse))
        denominator = _finite(anorm * znorm + bnorm)
        backward = _finite(_inf(equation) / denominator) if denominator else 0.0
        metrics = dict(A=a, b=b, residual_scales=sr, state_scales=sy,
                       scaled_correction=z, delta=delta, native_scaled_residual_inf=bnorm,
                       scaled_correction_inf=znorm, kappa_inf=condition,
                       linear_equation_residual=equation, linear_backward_error=backward)
        return dict(status='LINEAR_SYSTEM_DIAGNOSTIC', metrics=metrics)
    except (_Hold, OverflowError, ZeroDivisionError, ValueError) as exc:
        return _failure(exc)


def _field(packet, name):
    _require(name in packet and packet[name] is not None, 'HOLD_MISSING_STAGE_DATA')
    return packet[name]


def _text(value):
    _require(isinstance(value, str) and bool(value.strip()), 'HOLD_MISSING_STAGE_DATA')
    return value


def _physical(state):
    x, he2, he3, w = state
    return 0 <= x <= 1 and he2 >= 0 and he3 >= 0 and he2 + he3 <= 1 and w > 0


def analyze_stage(packet):
    """Validate a declared same-state/context packet, without reading its producer."""
    kind = packet.get('input_kind') if isinstance(packet, dict) else None
    constants = dict(input_kind=kind, nonlinear_error_certificate=None,
                     scientific_admission='NOT_ISSUED', correction_scope='CHEMICAL_STAGE_ONLY_NO_STATE_COMMIT')
    try:
        _require(isinstance(packet, dict), 'HOLD_MISSING_STAGE_DATA')
        get = lambda name: _field(packet, name)
        get('input_kind')
        _require(get('schema_version') == 1 and not isinstance(get('schema_version'), bool),
                 'HOLD_PACKET_SCHEMA')
        _require(kind in ('ACTUAL_STAGE', 'SYNTHETIC_FIXTURE'), 'HOLD_PACKET_KIND')
        _require(get('state_order') == ORDER and get('energy_unit') == 'eV_per_H'
                 and get('method') == 'BACKWARD_EULER_PREPARED_ABSORPTION', 'HOLD_PACKET_CONVENTION')
        y, old = _vector(get('state')), _vector(get('old_state'))
        _require(_physical(y) and _physical(old), 'HOLD_INPUT_STATE_DOMAIN')
        r, j = _vector(get('residual')), _matrix(get('jacobian'))
        context = _text(get('context_id'))
        _require(_vector(get('residual_evaluation_state')) == y
                 and _vector(get('jacobian_evaluation_state')) == y
                 and get('residual_context_id') == context
                 and get('jacobian_context_id') == context, 'HOLD_STALE_OR_MISMATCHED_STAGE')
        _require(_number(get('a')) > 0 and _number(get('dt_s')) > 0, 'HOLD_STAGE_DOMAIN')
        f, k = _number(get('f_He')), _number(get('k_B_eV_per_K'))
        _require(f >= 0 and k > 0, 'HOLD_THERMAL_CONSTANT_DOMAIN')
        _require(get('jacobian_kind') in ('ANALYTIC', 'FINITE_DIFFERENCE'), 'HOLD_JACOBIAN_KIND')
        provenance = {}
        if kind == 'ACTUAL_STAGE':
            _require(get('iterate_status') == 'ACCEPTED_CHEMICAL_STAGE', 'HOLD_ITERATE_STATUS')
            _require(get('driver_blob_sha') == DRIVER_BLOB, 'HOLD_SOURCE_BINDING_MISMATCH')
            for name in ('source_commit', 'stage_id', 'execution_receipt', 'cost_owner'):
                provenance[name] = _text(get(name))
            cost = get('added_rhs_evaluations')
            _require(isinstance(cost, int) and not isinstance(cost, bool) and cost >= 0,
                     'HOLD_ADDED_RHS_COST')
            provenance.update(added_rhs_evaluations=cost, driver_blob_sha=DRIVER_BLOB)
        sr = [1.0, 1.0, 1.0, max(abs(old[3]), abs(y[3]), 1e-6)]
        sy = [max(abs(x), 1e-5) for x in y[:3]] + [max(abs(y[3]), 1e-6)]
        core = solve_scaled(r, j, sr, sy)
        if core['status'] == 'HOLD':
            return dict(core, **constants)
        metrics = core['metrics']
        passed = metrics['native_scaled_residual_inf'] <= NEWTON_THRESHOLD
        _require(kind != 'ACTUAL_STAGE' or passed, 'HOLD_ACCEPTED_STAGE_RESIDUAL_MISMATCH')
        delta = metrics['delta']
        d = _finite(1 + f + y[0] + f * (y[1] + 2*y[2]))
        dd = _finite(delta[0] + f * (delta[1] + 2*delta[2]))
        temperature = _finite(2*y[3] / _finite(3*k*d))
        linear = _finite(temperature * _finite(delta[3] / y[3] - dd / d))
        corrected = [_finite(x+dx) for x, dx in zip(y, delta)]
        valid = _physical(corrected)
        exact = _finite(linear / _finite(1 + dd / d)) if valid else None
        after = _finite(temperature + exact) if valid else None
        metrics.update(correction_to_local_target=_finite(metrics['scaled_correction_inf'] / LOCAL_TARGET),
                       passes_frozen_newton_inequality=passed,
                       thermal=dict(temperature_before=temperature, delta_temperature_linear=linear,
                           delta_temperature_exact_map=exact, temperature_corrected=after,
                           corrected_state=corrected, corrected_domain='VALID' if valid else 'INVALID',
                           exact_map_hold_reason=None if valid else 'CORRECTED_FRACTION_OR_ENERGY_DOMAIN'))
        return dict(status=('ACTUAL_STAGE_LINEARIZED_DIAGNOSTIC' if kind == 'ACTUAL_STAGE'
                            else 'SYNTHETIC_LINEARIZED_DIAGNOSTIC'), metrics=metrics,
                    provenance=provenance, **constants)
    except (_Hold, OverflowError, ZeroDivisionError, ValueError) as exc:
        return _failure(exc, **constants)


def atomic_json(path, value):
    """Same-directory durable replacement; parent fsync when supported."""
    descriptor, temporary = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            directory = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
    finally:
        Path(temporary).unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        print('HOLD_FRESH_OUTPUT_REQUIRED', file=sys.stderr)
        return 2
    args.output.mkdir(parents=True)
    wall, cpu = time.perf_counter(), time.process_time()
    input_hash = None
    try:
        raw = args.input.read_bytes()
        input_hash = hashlib.sha256(raw).hexdigest()
        result = analyze_stage(json.loads(raw))
    except OSError:
        result = dict(status='HOLD', reason='HOLD_MISSING_STAGE_DATA', metrics=None)
    except (ValueError, TypeError):
        result = dict(status='HOLD', reason='HOLD_MALFORMED_STAGE_DATA', metrics=None)
    code = 2 if result['status'] == 'HOLD' else 0
    atomic_json(args.output/'NONLINEAR_BUDGET_RESULT.json', result)
    receipt = dict(schema_version=1, status=result['status'], reason=result.get('reason'), exit_code=code,
                   input_path=str(args.input.resolve()), input_sha256=input_hash,
                   module_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   argv=[sys.executable, *sys.argv] if argv is None else [sys.executable, __file__, *argv],
                   python=platform.python_version(), wall_seconds=time.perf_counter()-wall,
                   cpu_seconds=time.process_time()-cpu, native_solver_runs=0, NCP_runs=0,
                   scientific_admission='NOT_ISSUED')
    atomic_json(args.output/'EXECUTION_RECEIPT.json', receipt)
    print(json.dumps(dict(status=result['status'], output=str(args.output)), allow_nan=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
