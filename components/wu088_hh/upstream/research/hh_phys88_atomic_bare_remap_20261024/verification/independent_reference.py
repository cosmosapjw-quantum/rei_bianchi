#!/usr/bin/env python3
"""PHYS88 separate raw parser and SciPy kve/adaptive finite-window reference.

No production module imports. Two named conditional maps at1e8K only; no
low-T variance, empirical source equivalence, uncertainty or tails certificate.
The raw-parser construction is reused statically from the independent PHYS87
reference, not executed as an old reference campaign. New bare formulas below
are independently expressed using Eb and explicit dK/dEs rather than GL weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import resource
import signal
import sys
import time
import traceback
from decimal import Decimal
from pathlib import Path


CONTRACT_SHA256 = "8f45d6a70d7cf7ffcc556b74636f25087167a3372f781eee4078f5dd00e4154d"
RAW_SHA256 = "3024d8f0db604b074e33ed8b05027eb9f5a738614041ba44c83f048e0d0bc1af"
TABLE_SHA256 = "b14ad9b4a2379166ec2b2c04b2a77efb4c819498924682072d74a6b4e31c5014"
T_K = 100_000_000.0
EPSABS_SCALED = 1.0e-24
EPSREL = 2.0e-11
QUAD_LIMIT = 64
THREAD_ENV = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)
FIELDS = ("kappa_cm3_per_s", "mean_Kin_eV", "mean_Egamma_eV", "mean_Kd_eV")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def endf_number(field: str) -> Decimal:
    """Parse the original fixed-width numeric field, without production helpers."""
    value = field.strip()
    if not value:
        return Decimal(0)
    if "e" not in value.lower():
        value = re.sub(r"(?<=[0-9.])([+-][0-9]+)$", r"E\1", value)
    parsed = Decimal(value)
    need(parsed.is_finite(), "Nonfinite ENDF numeric field")
    return parsed


def fields(line: str) -> list[Decimal]:
    need(len(line) >= 75, "Truncated ENDF record")
    return [endf_number(line[start:start + 11]) for start in range(0, 66, 11)]


def integer(value: Decimal) -> int:
    need(value == value.to_integral_value(), "Nonintegral ENDF control field")
    return int(value)


def section(lines: list[str], mf: int, mt: int) -> list[str]:
    result = [line for line in lines if len(line) >= 75
              and int(line[70:72]) == mf and int(line[72:75]) == mt]
    need(bool(result), f"Missing MF{mf}/MT{mt}")
    need(all(int(line[66:70]) == 125 for line in result), "Unexpected material")
    return result


def values(records: list[str], start: int, count: int) -> tuple[list[Decimal], int]:
    stop = start + (count + 5) // 6
    need(stop <= len(records), "Truncated ENDF array")
    flattened = [v for line in records[start:stop] for v in fields(line)]
    need(all(v == 0 for v in flattened[count:]), "Unexpected nonzero padding")
    return flattened[:count], stop


def tab1(records: list[str], start: int) -> tuple[dict, int]:
    head = fields(records[start])
    nr, np = integer(head[4]), integer(head[5])
    interpolation, offset = values(records, start + 1, 2 * nr)
    xy, stop = values(records, offset, 2 * np)
    return {
        "head": head,
        "interpolation": [(integer(interpolation[i]), integer(interpolation[i + 1]))
                          for i in range(0, len(interpolation), 2)],
        "x": xy[0::2], "y": xy[1::2],
    }, stop


def parse_source(unit: Path) -> dict:
    raw = (unit / "source_data/n-001_H_001.endf").read_bytes()
    need(len(raw) == 671232 and sha256(raw) == RAW_SHA256, "Canonical raw identity mismatch")
    lines = raw.decode("ascii").splitlines()
    mf3 = section(lines, 3, 102)
    need(len(mf3) == 54, "Unexpected MF3 record count")
    h3 = fields(mf3[0])
    cross, end = tab1(mf3, 1)
    need(end == len(mf3), "Unconsumed MF3 records")
    need(h3[:2] == [Decimal(1001), Decimal("0.9991673")], "MF3 ZA/AWR mismatch")
    need(cross["head"][:4] == [Decimal(2224648), Decimal(2224648), Decimal(0), Decimal(0)],
         "MF3 QM/QI/LR mismatch")
    need(cross["interpolation"] == [(33, 5), (153, 2)], "MF3 interpolation mismatch")
    need(len(cross["x"]) == 153, "MF3 knot count mismatch")
    need(cross["x"][0] == Decimal("1e-5") and cross["x"][-1] == Decimal("2e7"),
         "Source window mismatch")
    need(all(a < b for a, b in zip(cross["x"], cross["x"][1:])), "Unordered source grid")
    need(all(v > 0 for v in cross["y"]), "Nonpositive cross section")

    # This independently reads MF6 to guard the scalar rotational reduction.
    # Its angular coefficients are audited, not fed into the scalar kernel.
    mf6 = section(lines, 6, 102)
    need(len(mf6) == 315, "Unexpected MF6 record count")
    h6 = fields(mf6[0])
    need(h6 == [Decimal(1001), Decimal("0.9991673"), Decimal(0), Decimal(2), Decimal(2), Decimal(0)],
         "MF6 frame or product-count mismatch")
    photon, offset = tab1(mf6, 1)
    need(photon["head"][:4] == [Decimal(0), Decimal(2223300), Decimal(0), Decimal(2)],
         "Photon LAW2/primary-energy metadata mismatch")
    need(photon["interpolation"] == [(2, 2)] and photon["x"] == [cross["x"][0], cross["x"][-1]]
         and photon["y"] == [Decimal(1), Decimal(1)], "Photon yield mismatch")
    ah = fields(mf6[offset])
    need(ah == [Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(1), Decimal(153)],
         "Angular TAB2 header mismatch")
    ai, offset = values(mf6, offset + 1, 2)
    need(ai == [Decimal(153), Decimal(2)], "Angular interpolation mismatch")
    angular = []
    for energy in cross["x"]:
        head = fields(mf6[offset])
        need(head == [Decimal(0), energy, Decimal(0), Decimal(0), Decimal(2), Decimal(2)],
             "Angular LANG/NL or grid mismatch")
        coeff, offset = values(mf6, offset + 1, 2)
        angular.append(coeff)
    recoil, offset = tab1(mf6, offset)
    need(offset == len(mf6), "Unconsumed MF6 records")
    need(recoil["head"][:4] == [Decimal(1002), Decimal("1.996256"), Decimal(0), Decimal(4)],
         "Recoil LAW4/AWP metadata mismatch")
    need(recoil["interpolation"] == [(2, 2)] and recoil["x"] == photon["x"]
         and recoil["y"] == [Decimal(1), Decimal(1)], "Recoil yield mismatch")

    # The frozen table is used only to compare the independently parsed raw data.
    table_raw = (unit / "source_data/SOURCE_TABLE.json").read_bytes()
    need(sha256(table_raw) == TABLE_SHA256, "Transcription table identity mismatch")
    table = json.loads(table_raw)
    need(table["incident_energy_frame"] == "laboratory target rest"
         and table["secondary_angle_frame"] == "center_of_mass", "Table frame mismatch")
    need(len(table["rows"]) == 153, "Table row count mismatch")
    for i, row in enumerate(table["rows"]):
        need(row["index1"] == i + 1, "Transcription index mismatch")
        actual = [cross["x"][i], cross["y"][i], *angular[i]]
        recorded = [Decimal(row[k]) for k in ("En_eV", "sigma_barn", "a1", "a2")]
        need(actual == recorded, f"Raw/table mismatch at source knot {i + 1}")
    return {"cross": cross, "AWR": h3[1], "Q": cross["head"][1],
            "audit": {"raw_sha256": RAW_SHA256, "table_sha256": TABLE_SHA256,
                      "raw_bytes": len(raw), "knots": 153, "cells": 152,
                      "MF3_interpolation": [[33, 5], [153, 2]],
                      "MF6_LCT": 2, "photon_LAW": 2, "recoil_LAW": 4,
                      "photon_yield": 1, "recoil_yield": 1,
                      "exact_raw_table_numeric_fields_compared": 612,
                      "angular_coefficients_used_in_scalar_kernel": False}}


def compute_reference(source, contract, map_token, state):
    import scipy
    from scipy.integrate import quad
    from scipy.special import kve

    need(map_token in ('LAB_ANCHORED', 'FIXED_COM_K'), 'Unsupported frozen reference map')
    tokens = contract['mass_inputs']
    a, b, d = [float(Decimal(tokens[key])) for key in ('epsilon_n', 'epsilon_p', 'epsilon_d')]
    h = float(Decimal(tokens['epsilon_n'])*source['AWR'])
    mb, ms = a+b, a+h
    qb = float(Decimal(tokens['epsilon_n'])+Decimal(tokens['epsilon_p'])-Decimal(tokens['epsilon_d']))
    need(Decimal(tokens['Q_bare']) == Decimal(tokens['epsilon_n'])+
         Decimal(tokens['epsilon_p'])-Decimal(tokens['epsilon_d']), 'Nominal bare Q mismatch')
    theta = float(Decimal('1.380649e-23')/Decimal('1.602176634e-19'))*T_K
    k2a, k2b = float(kve(2, a/theta)), float(kve(2, b/theta))
    need(all(math.isfinite(v) and v > 0 for v in (k2a, k2b)), 'Nonpositive denominator kve')
    energies = [float(v) for v in source['cross']['x']]
    sigmas = [float(v) for v in source['cross']['y']]
    counts = {'quad_calls': 0, 'callback_evaluations': 0, 'exp_underflow_zero_callbacks': 0,
              'cells': 152, 'integral_families': 4}
    cells, accum, errors = [], [[], [], [], []], [[], [], [], []]
    state.update(map=map_token, counts=counts, cell_results=cells)
    for i in range(152):
        lo, hi = energies[i:i+2]; slo, shi = sigmas[i:i+2]
        law = next(law for stop, law in source['cross']['interpolation'] if i+2 <= stop)
        power = math.log(shi/slo)/math.log(hi/lo) if law == 5 else None
        slope = (shi-slo)/(hi-lo) if law == 2 else None

        def integrand(x, component):
            counts['callback_evaluations'] += 1
            es = theta*x
            sigma = slo*math.exp(power*math.log(es/lo)) if law == 5 else slo+slope*(es-lo)
            # Independent coordinate reduction: lambda/(4a²b²)=Eb(2a+Eb)/a².
            # x=Es/theta leaves an explicit derivative dKb/dEs and no theta prefactor.
            target, native_mass = (b, mb) if map_token == 'LAB_ANCHORED' else (h, ms)
            native_w = math.sqrt(native_mass*native_mass+2*target*es)
            kinetic = 2*target*es/(native_w+native_mass)
            w = mb+kinetic
            eb = es if map_token == 'LAB_ANCHORED' else kinetic*(2*mb+kinetic)/(2*b)
            boltzmann = math.exp(-kinetic/theta)
            if boltzmann == 0:
                counts['exp_underflow_zero_callbacks'] += 1
                return 0.0
            z = w/theta
            need(z >= 1e5, 'Frozen kve z domain')
            k1 = float(kve(1, z))
            weight = sigma*(eb/a)*(2+eb/a)*(target/native_w)*k1*boltzmann
            if component == 0:
                value = weight
            else:
                k2 = float(kve(2, z))
                need(k1 > 0 and k2 > 0 and math.isfinite(k2), 'Invalid moment kve')
                gm1 = (k2-k1)/k1
                available = qb+kinetic
                recoil = available*available/(2*w)
                photon = available-recoil
                if component == 1:
                    moment = (kinetic+w*gm1)/theta
                elif component == 2:
                    moment = photon*(1+gm1)/qb
                else:
                    moment = (recoil+(w-photon)*gm1)/theta
                value = weight*moment
            need(math.isfinite(value) and value >= 0, 'Nonfinite/negative independent integrand')
            return value

        entry = {'index1': i+1, 'native_Es_lo_eV': lo, 'native_Es_hi_eV': hi, 'INT': law,
                 'scaled_integrals': [], 'quad_error_estimates': [], 'neval': []}
        cells.append(entry)
        for component in range(4):
            counts['quad_calls'] += 1
            outcome = quad(integrand, lo/theta, hi/theta, args=(component,),
                           epsabs=EPSABS_SCALED, epsrel=EPSREL, limit=QUAD_LIMIT, full_output=1)
            need(len(outcome) == 3, 'QUADPACK warning cell'+str(i+1)+':'+repr(outcome[3:]))
            value, error, info = outcome
            need(math.isfinite(value) and value >= 0 and math.isfinite(error), 'Invalid quad result')
            accum[component].append(value); errors[component].append(error)
            entry['scaled_integrals'].append(value); entry['quad_error_estimates'].append(error)
            entry['neval'].append(int(info['neval']))
    integrals = [math.fsum(v) for v in accum]
    need(integrals[0] > 0, 'Independent normalizer vanished')
    result = {'map': map_token, 'T_K': T_K,
        'kappa_cm3_per_s': 29979245800.0*1e-24*integrals[0]/(k2a*k2b),
        'mean_Kin_eV': theta*integrals[1]/integrals[0],
        'mean_Egamma_eV': qb*integrals[2]/integrals[0],
        'mean_Kd_eV': theta*integrals[3]/integrals[0],
        'counts': counts, 'cell_results': cells, 'scaled_integrals': integrals,
        'summed_quad_error_estimates': [math.fsum(v) for v in errors],
        'quad_error_interpretation': 'QUADPACK estimates; no rigorous global error bound',
        'scipy_version': scipy.__version__,
        'method': {'coordinate': 'x=original_native_Es/theta per originalcell',
                   'Bessel': 'actualscipy.special.kve', 'integrator': 'scipy.integrate.quad',
                   'epsabs_scaled': EPSABS_SCALED, 'epsrel': EPSREL, 'limit': QUAD_LIMIT,
                   'variance_computed': False, 'no_production_imports': True}}
    need(all(math.isfinite(result[k]) and result[k] > 0 for k in FIELDS), 'Invalid independent fields')
    result['energy_closure_eV'] = math.fsum([result['mean_Kin_eV'], qb,
                                            -result['mean_Egamma_eV'], -result['mean_Kd_eV']])
    return result


def wall_deadline(_signum, _frame):
    raise TimeoutError('Frozen reference wall budget60s; no automaticretry')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--unit', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--primary', type=Path, required=True)
    p.add_argument('--expected-primary-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--controller-admission-receipt', type=Path, required=True)
    args = p.parse_args()
    need(not args.output.exists(), 'Reference outputexists; completedidentitynoreplay')
    need(args.output.parent.is_dir(), 'Controller prepares outputparent')
    start_wall, start_cpu = time.monotonic(), time.process_time()
    record = {'schema': 'PHYS88_INDEPENDENT_REFERENCE_V1', 'status': 'FAIL_CLOSED',
        'contract_sha256': CONTRACT_SHA256, 'reference_code_sha256': sha256(Path(__file__).read_bytes()),
        'scientific_child_attempts': 1, 'automatic_retries': 0,
        'scope': 'Two conditional bare maps at1e8K finitewindow rate+threeenergymeans; no covariance/tail/physicalCI',
        'references': [], 'comparisons': {}, 'partial_diagnostics': [], 'production': 'NOT_ISSUED', 'HH_R10': 'OFF'}
    try:
        for key in THREAD_ENV:
            os.environ[key] = '1'
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        signal.signal(signal.SIGALRM, wall_deadline); signal.alarm(60)
        raw_contract = (args.unit/'CONTRACT.json').read_bytes()
        need(sha256(raw_contract) == CONTRACT_SHA256, 'Frozen contract mismatch')
        contract = json.loads(raw_contract)
        need(contract['budget']['reference_cpu_s'] == 30 and contract['budget']['reference_wall_s'] == 60,
             'Frozen reference caps mismatch')
        admission = args.controller_admission_receipt.read_bytes(); json.loads(admission)
        record['controller_admission_receipt_sha256'] = sha256(admission)
        record['controller_admission_note'] = 'Fresh actual lease/memory/affinity owned by outer wrapper; no authorization inferred from JSON alone'
        primary_raw = args.primary.read_bytes()
        need(sha256(primary_raw) == args.expected_primary_sha256, 'Exact completed primary bytes mismatch')
        primary = json.loads(primary_raw)
        need(primary['status'] == 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' and not primary['failures'],
             'Complete passed primary required')
        record['primary_sha256'] = args.expected_primary_sha256
        source = parse_source(args.unit); record['source_audit'] = source['audit']
        tolerance = contract['acceptance']['independent_relative_rate_means']
        need(tolerance == 1e-7, 'Frozen independent tolerance mismatch')
        for name in ('LAB_ANCHORED', 'FIXED_COM_K'):
            rows = [r for r in primary['thermal_results'] if r['map'] == name and
                    r['T_K'] == T_K and r['order'] == 32 and r['rate_only'] is False]
            need(len(rows) == 1, 'ExactlyonehighTorder32primaryrowpermaprequired')
            partial = {}; record['partial_diagnostics'].append(partial)
            reference = compute_reference(source, contract, name, partial)
            record['references'].append(reference)
            comparisons = {}
            for key in FIELDS:
                test, ref = rows[0][key], reference[key]
                need(math.isfinite(test) and test > 0, 'Primarycomparisonvalueinvalid')
                relative = abs(test-ref)/abs(ref)
                comparisons[key] = {'primary': test, 'reference': ref, 'relative_difference': relative,
                                    'tolerance': tolerance, 'pass': relative <= tolerance}
            record['comparisons'][name] = comparisons
            reference['energy_closure_pass'] = abs(reference['energy_closure_eV']) <= contract['acceptance']['owner_energy_closure_abs_eV']
        record['status'] = 'PASS_SCOPED' if all(q['pass'] for c in record['comparisons'].values()
            for q in c.values()) and all(r['energy_closure_pass'] for r in record['references']) else 'FAIL_COMPARISON'
        # Successful diagnostics occur exactly once in references; failed partials stay preserved.
        record['partial_diagnostics'] = []
    except Exception as exc:
        record['exception'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.alarm(0)
        record['wall_s'] = time.monotonic()-start_wall; record['cpu_s'] = time.process_time()-start_cpu
        record['thread_environment'] = {key: os.environ.get(key) for key in THREAD_ENV}
        record['cpu_affinity'] = sorted(os.sched_getaffinity(0))
        with args.output.open('x', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': record['status'], 'output': str(args.output),
                      'cpu_s': record['cpu_s'], 'wall_s': record['wall_s']}))
    return 0 if record['status'] == 'PASS_SCOPED' else 1


if __name__ == '__main__':
    sys.exit(main())


