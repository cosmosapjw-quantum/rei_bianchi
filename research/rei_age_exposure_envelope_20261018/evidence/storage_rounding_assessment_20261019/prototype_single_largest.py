"""Scratch-only assessment on emitted original nodes; no native source edits."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import struct


ETA = Fraction(1, 2**1074)
MIN_NORMAL = 2**-1022
EPSILON = 2**-52


def ticks(value):
    return struct.unpack('<Q', struct.pack('<d', value))[0]


def from_ticks(value):
    return struct.unpack('<d', struct.pack('<Q', value))[0]


def original_sum(values):
    total = correction = 0.0
    for value in values:
        y = value - correction
        following = total + y
        correction = (following - total) - y
        total = following
    return total


def assess(fixture):
    rows = fixture['nodes_q_probability_number']
    masses = [row[2] for row in rows]
    count_defect = abs(original_sum(masses) - fixture['n'])
    energy_defect = abs(original_sum(q * z for q, p, z in rows) - fixture['u'])
    assert count_defect == fixture['count_defect']
    assert energy_defect == fixture['energy_defect']
    result = {
        'name': fixture['name'],
        'original_count_defect_eta': str(Fraction(count_defect) / ETA),
        'original_energy_defect_eta': str(Fraction(energy_defect) / ETA),
        'count_tolerance_eta': str(Fraction(fixture['count_tolerance']) / ETA),
        'energy_tolerance_eta': str(Fraction(fixture['energy_tolerance']) / ETA),
    }
    if count_defect <= fixture['count_tolerance'] and energy_defect <= fixture['energy_tolerance']:
        result['outcome'] = 'UNCHANGED_ORIGINAL_PASS'
        return result
    if count_defect <= fixture['count_tolerance']:
        result['outcome'] = 'REJECT_COUNT_GATE_ALREADY_PASSES'
        return result
    if not 0 < fixture['n'] < MIN_NORMAL:
        result['outcome'] = 'REJECT_N_NOT_SUBNORMAL'
        return result
    if not all(math.isfinite(z) and 0 <= z < MIN_NORMAL for z in masses):
        result['outcome'] = 'REJECT_NODE_MASS_RANGE'
        return result
    if not all(math.isfinite(q) and q > 0 and fixture['lo'] <= q <= fixture['hi'] for q, p, z in rows):
        result['outcome'] = 'REJECT_NODE_SUPPORT'
        return result
    if not abs(fixture['normalized_mean_residual']) < 8 * EPSILON:
        result['outcome'] = 'REJECT_TILT_NOT_CONVERGED'
        return result

    # These are independently checked premises of the rounding bound, not a
    # replacement for the original count or energy gates.
    assert all(math.isfinite(p) and 0 <= p <= 1 for q, p, z in rows)
    assert all(fixture['n'] * p == z for q, p, z in rows)
    count_ticks = [ticks(z) for z in masses]
    target_ticks = ticks(fixture['n'])
    signed_delta_ticks = target_ticks - sum(count_ticks)
    largest = max(range(len(count_ticks)), key=count_ticks.__getitem__)
    probability_sum = sum((Fraction(p) for q, p, z in rows), Fraction(0))
    normalization_error = Fraction(fixture['n']) * abs(probability_sum - 1)
    quantization_bound = len(rows) * ETA / 2
    measured_quantization_l1 = sum(
        (abs(Fraction(z) - Fraction(fixture['n']) * Fraction(p)) for q, p, z in rows), Fraction(0)
    )
    assert measured_quantization_l1 <= quantization_bound
    assert abs(signed_delta_ticks) * ETA <= normalization_error + quantization_bound
    result.update({
        'delta_ticks': signed_delta_ticks,
        'largest_index': largest,
        'largest_q': rows[largest][0],
        'largest_old_ticks': count_ticks[largest],
        'l1_over_n': abs(signed_delta_ticks) / target_ticks,
        'probability_sum_minus_one': float(probability_sum - 1),
        'normalization_error_bound_eta': float(normalization_error / ETA),
        'storage_quantization_l1_eta': float(measured_quantization_l1 / ETA),
        'storage_quantization_bound_eta': len(rows) / 2,
        'delta_quantization_bound_verified_exactly': True,
    })
    if count_ticks[largest] == 0:
        result['outcome'] = 'REJECT_NO_EXISTING_POSITIVE_MASS'
        return result
    replacement = count_ticks[largest] + signed_delta_ticks
    if not 0 <= replacement < 2**52:
        result['outcome'] = 'REJECT_CANDIDATE_RANGE'
        return result
    candidate_ticks = count_ticks.copy()
    candidate_ticks[largest] = replacement
    assert sum(candidate_ticks) == target_ticks
    candidate = [from_ticks(count) for count in candidate_ticks]
    candidate_count_defect = abs(original_sum(candidate) - fixture['n'])
    candidate_energy_defect = abs(original_sum(q * z for (q, p, old), z in zip(rows, candidate)) - fixture['u'])
    passes = candidate_count_defect <= fixture['count_tolerance'] and candidate_energy_defect <= fixture['energy_tolerance']
    result.update({
        'largest_new_ticks': replacement,
        'candidate_l1_ticks': sum(abs(new - old) for new, old in zip(candidate_ticks, count_ticks)),
        'candidate_count_defect_eta': str(Fraction(candidate_count_defect) / ETA),
        'candidate_energy_defect_eta': str(Fraction(candidate_energy_defect) / ETA),
        'nonnegative_masses_retained': all(z >= 0 for z in candidate),
        'all_nodes_unchanged': True,
        'outcome': 'ACCEPT_CANDIDATE_BOTH_ORIGINAL_GATES' if passes else 'REJECT_ORIGINAL_ENERGY_GATE',
        'failed_candidate_committed': False,
    })
    assert result['candidate_l1_ticks'] == abs(signed_delta_ticks)
    return result


if __name__ == '__main__':
    directory = Path(__file__).resolve().parent
    input_file = directory / 'INPUT_FIXTURES.json'
    fixtures = json.loads(input_file.read_text())['fixtures']
    result = {
        'schema': 'rei.storage_rounding.scratch_single_largest.v1',
        'input_sha256': hashlib.sha256(input_file.read_bytes()).hexdigest(),
        'prototype_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Scratch node-vector prototype only. No production source repair or full native campaign.',
        'original_gates_unchanged': True,
        'production_source_edits': False,
        'scientific_admission': 'NOT_ISSUED',
        'results': [assess(fixture) for fixture in fixtures],
    }
    (directory / 'SINGLE_LARGEST_PROTOTYPE_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'fixtures': len(fixtures), 'outcomes': [entry['outcome'] for entry in result['results']]}))
