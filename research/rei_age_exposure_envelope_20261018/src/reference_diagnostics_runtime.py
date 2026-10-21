"""Passive runtime helpers embedded only in the opt-in reference copy."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def _diagnostic_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {k: _diagnostic_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_diagnostic_json(v) for v in value]
    return value


class ReferenceDiagnostics:
    def __init__(self, output, identity, executed_file):
        self.output = Path(output)
        self.identity = dict(identity)
        self.identity['executed_solver_sha'] = hashlib.sha256(Path(executed_file).read_bytes()).hexdigest()
        self.attempts = []
        self.jumps = []
        self.current = None

    def persist(self):
        telemetry = dict(schema='rei.reference.passive_diagnostics.v1', identity=self.identity,
                         interpretation='DESCRIPTIVE_ONLY; does not establish RMS dilution causality',
                         attempts=self.attempts)
        jumps = dict(schema='rei.reference.source_jumps.v1', identity=self.identity,
                     status='AVAILABLE' if self.jumps else 'MISSING_DATA', records=self.jumps)
        self.output.mkdir(parents=True, exist_ok=True)
        for name, value in [('reference_diagnostics.json', telemetry), ('source_jumps.json', jumps)]:
            (self.output/name).write_text(json.dumps(_diagnostic_json(value), indent=2, allow_nan=False)+'\n')

    def instrument_factory(self, original_factory, component_norm):
        owner = self

        def factory(block_sizes):
            original = original_factory(block_sizes)

            class ObservedDOP853(original):
                def _estimate_error_norm(self, K, h, scale):
                    # The existing controller is called once and its exact
                    # return value is returned unchanged to SciPy.
                    actual = super()._estimate_error_norm(K, h, scale)
                    err5 = np.dot(K.T, self.E5)/scale
                    err3 = np.dot(K.T, self.E3)/scale
                    names = ['gas'] + (['photon_logs'] if len(scale) > 18 else []) + [f'ledger_{i}' for i in range(14)]
                    values = []
                    start = 0
                    for index, size in enumerate(self.block_sizes):
                        stop = start+size
                        value = component_norm(err5[start:stop], err3[start:stop], h, (size,))
                        values.append(dict(index=index, name=names[index], start=start, stop=stop, value=value))
                        start = stop
                    maximum = max(x['value'] for x in values)
                    record = dict(t=float(self.t), h=float(h), t_new=float(self.t+h),
                                  dimension=len(scale), blocks=values,
                                  binding_indices=[x['index'] for x in values if x['value'] == maximum],
                                  binding_names=[x['name'] for x in values if x['value'] == maximum],
                                  block_max_diagnostic=maximum, error_norm_actual=float(actual),
                                  old_rms_diagnostic=component_norm(err5, err3, h, (len(scale),)),
                                  error_accept=bool(actual < 1.))
                    if owner.current is not None:
                        owner.current['estimates'].append(record)
                    return actual

            return ObservedDOP853
        return factory

    def solve(self, original_solve, event, retry, *args, **kwargs):
        start, stop = args[1]
        attempt = dict(attempt=len(self.attempts), event=event, retry=retry,
                       interval_start=float(start), interval_stop=float(stop), estimates=[],
                       status='RUNNING', discarded=True, retained=False)
        self.attempts.append(attempt)
        self.current = attempt
        try:
            solution = original_solve(*args, **kwargs)
            attempt.update(status='RETURNED_SUCCESS' if solution.success else 'RETURNED_FAILURE',
                           discarded=not bool(solution.success), retained=bool(solution.success),
                           returned_steps=len(solution.t)-1)
            return solution
        except BaseException as error:
            attempt.update(status='EXCEPTION', exception_type=type(error).__name__, exception=repr(error))
            raise
        finally:
            attempt['local_error_accepted_estimates'] = sum(x['error_accept'] for x in attempt['estimates'])
            attempt['final_trajectory_accepted_estimates'] = (
                attempt['local_error_accepted_estimates'] if attempt['retained'] else 0)
            self.current = None
            self.persist()

    @staticmethod
    def compact(physical):
        if len(physical.get('flat', [])) < 4 or len(physical.get('ledgers', [])) != 14:
            raise ValueError('SOURCE_JUMP_PHYSICAL_SHAPE')
        return dict(N=physical['N'], U=physical['U'], gas=physical['flat'][:4],
                    ledgers=list(physical['ledgers']))

    def birth(self, event, x, active_before, active_after, setup, before, after, physical_before, get_post):
        record = dict(event=event, x=float(x), active_before=active_before, active_after=active_after,
                      source_inventory=setup['source_inventory'][event], status='RUNNING')
        self.jumps.append(record)
        try:
            record['pre'] = self.compact(physical_before)
            record['post'] = self.compact(get_post())
            lo = 4+2*setup['cells']*event
            hi = lo+2*setup['cells']
            mask = np.ones(before.size, dtype=bool)
            mask[lo:hi] = False
            bits_before = np.asarray(before, dtype=np.float64).view(np.uint64)
            bits_after = np.asarray(after, dtype=np.float64).view(np.uint64)
            record.update(status='AVAILABLE',
                          unchanged_nonbirth_coordinates_bits=bool(np.array_equal(bits_before[mask], bits_after[mask])),
                          unchanged_gas_coordinate_bits=bool(np.array_equal(bits_before[:4], bits_after[:4])),
                          unchanged_ledger_coordinate_bits=bool(np.array_equal(bits_before[-setup['extra']:], bits_after[-setup['extra']:])))
        except BaseException as error:
            record.update(status='ERROR', exception_type=type(error).__name__, exception=repr(error))
            raise
        finally:
            self.persist()
