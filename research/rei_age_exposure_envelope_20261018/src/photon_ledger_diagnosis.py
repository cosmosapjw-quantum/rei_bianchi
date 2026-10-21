"""Read-only diagnosis of stored photon conservation terms.

The fixed reference gate is reported unchanged. Bounds here cover only the
final addition of stored binary64 terms, never integration or native RHS error.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import argparse
import math

import numpy as np

from run_refinement import read_json, save

TARGET = 1e-8
UNIT_ROUNDOFF = 2.0**-53


def display_fraction(value):
    with localcontext() as ctx:
        ctx.prec = 80
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def fraction_record(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator))


def residual_fraction(record):
    value=record['exact_fraction']['residual']
    return Fraction(int(value['numerator']),int(value['denominator']))


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('NONFINITE_OR_NONNUMERIC_PHOTON_TERM')
    return float(value)


def budget(number, photo, sources):
    """Evaluate one stored invariant, retaining each source birth separately."""
    if len(photo) != 3:
        raise ValueError('MISSING_PHOTO_SPECIES')
    number = finite(number)
    photo = [finite(v) for v in photo]
    sources = [finite(v) for v in sources]
    terms = [number, *photo, *[-v for v in sources]]
    gross = math.fsum(abs(v) for v in terms)
    residual = math.fsum(terms)
    k = len(terms)
    gamma = k * UNIT_ROUNDOFF / (1.0 - k * UNIT_ROUNDOFF)
    exact = sum((Fraction.from_float(v) for v in terms), Fraction(0))
    exact_gross = sum((abs(Fraction.from_float(v)) for v in terms), Fraction(0))
    ratio = abs(exact) / exact_gross if exact_gross else None
    exact_pass = abs(exact) <= Fraction.from_float(TARGET)*exact_gross if exact_gross else None
    decimal_record = dict(residual=display_fraction(exact), gross=display_fraction(exact_gross),
                          normalized=display_fraction(ratio) if ratio is not None else None,
                          fixed_gate_pass=exact_pass, scope='DISPLAY_ONLY; gate uses exact Fraction')
    return dict(status='AVAILABLE' if gross else 'ZERO_GROSS_UNDEFINED',
                N=number, photo=photo, source_terms=sources, term_count=k,
                fsum=dict(residual=residual, gross=gross,
                          normalized=abs(residual)/gross if gross else None,
                          fixed_gate_pass=abs(residual) <= TARGET*gross if gross else None),
                decimal80=decimal_record,
                exact_fraction=dict(residual=fraction_record(exact),gross=fraction_record(exact_gross)),
                final_addition_roundoff_bound=gamma*gross,
                roundoff_bound_scope='FINAL_ADDITION_OF_STORED_BINARY64_TERMS_ONLY')


def missing(names):
    return dict(status='MISSING_DATA', missing=names)



def explicit_source_jumps(path, setup):
    """Prefer saved event pre/post states; legacy observation path stays intact."""
    try:
        obj = read_json(path)
        rows = obj.get('records', [])
        count = setup['birth_count']
        sources = setup['source_inventory']
        if len(rows) != count:
            raise ValueError('INCOMPLETE_SOURCE_EVENT_COUNT')
        if [r.get('event') for r in rows] != list(range(count)):
            raise ValueError('INVALID_SOURCE_EVENT_ORDER_OR_DUPLICATE')
        result = []
        for j, row in enumerate(rows):
            if (row.get('status') != 'AVAILABLE' or row.get('active_before') != j
                    or row.get('active_after') != j+1):
                raise ValueError('INVALID_SOURCE_EVENT_ACTIVE_OR_STATUS')
            if finite(row['x']) != finite(setup['births'][j]):
                raise ValueError('INVALID_SOURCE_EVENT_CLOCK')
            if row.get('source_inventory') != sources[j]:
                raise ValueError('INVALID_SOURCE_EVENT_INVENTORY')
            pre = budget(row['pre']['N'], row['pre']['ledgers'][4:7], [s[0] for s in sources[:j]])
            post = budget(row['post']['N'], row['post']['ledgers'][4:7], [s[0] for s in sources[:j+1]])
            delta = residual_fraction(post)-residual_fraction(pre)
            result.append(dict(event=j, x=row['x'], status='AVAILABLE', active_pre=j,
                               active_post=j+1, signed_residual_change_decimal80=display_fraction(delta),
                               signed_residual_change_exact_fraction=fraction_record(delta),
                               exact_stored_invariant_unchanged=delta==0))
        return dict(status='AVAILABLE', provenance='EXPLICIT_SOURCE_JUMPS_JSON', records=result)
    except (ValueError, KeyError, IndexError, TypeError) as e:
        return dict(status='INCOMPLETE' if 'INCOMPLETE' in str(e) else 'INVALID',
                    reason=str(e), provenance='EXPLICIT_SOURCE_JUMPS_JSON', records=[])


def diagnose(data: Path):
    data = Path(data)
    objects = {}
    absent = []
    for name in ('setup.json', 'endpoint.json', 'ledgers.json', 'solver_return.json'):
        path = data/name
        if path.is_file():
            objects[name] = read_json(path)
        else:
            absent.append(name)
    report = dict(schema='rei.photon_ledger.diagnosis.v1', fixed_target=TARGET,
                  state_or_ledger_modified=False, required_missing=absent,
                  status='MISSING_DATA' if absent else 'AVAILABLE',
                  history_interpretation='UNRESOLVED',
                  interpretation='UNRESOLVED',
                  scope='Stored reference data; no full simulation roundoff certificate.')
    setup = objects.get('setup.json', {})
    inventory = setup.get('source_inventory')
    birth_count = setup.get('birth_count', len(setup.get('births', [])))
    if inventory is None:
        report['endpoint'] = missing(['setup.source_inventory'])
        report['intervals'] = missing(['setup.source_inventory'])
        report['observations'] = missing(['setup.source_inventory'])
        return report
    sources = []
    for row in inventory:
        if not isinstance(row, list) or len(row) < 1:
            raise ValueError('MISSING_SOURCE_NUMBER')
        sources.append(finite(row[0]))
    if not isinstance(birth_count, int) or birth_count < 0 or birth_count != len(sources):
        raise ValueError('SOURCE_BIRTH_COUNT_MISMATCH')

    def physical_budget(physical, active):
        if not isinstance(active, int) or active < 0 or active > birth_count:
            raise ValueError('ACTIVE_SOURCE_COUNT_DOMAIN')
        if not isinstance(physical, dict) or 'N' not in physical or len(physical.get('ledgers', [])) < 7:
            return missing(['physical.N_or_photo_ledgers'])
        return budget(physical['N'], physical['ledgers'][4:7], sources[:active])

    endpoint = objects.get('endpoint.json')
    report['endpoint'] = physical_budget(endpoint, birth_count)
    ledger = objects.get('ledgers.json', {})
    if 'photon_normalized' in ledger:
        normalized = finite(ledger['photon_normalized'])
        if normalized < 0:
            raise ValueError('NEGATIVE_STORED_NORMALIZED_RESIDUAL')
        report['original_gate'] = dict(status='AVAILABLE', photon_normalized=normalized,
                                       fixed_gate_pass=normalized <= TARGET,
                                       policy='STORED_GATE_UNCHANGED')
        ep = report['endpoint']
        if ep['status'] == 'AVAILABLE' and 'photon_residual' in ledger and 'photon_gross' in ledger:
            stored_residual = finite(ledger['photon_residual'])
            stored_gross = finite(ledger['photon_gross'])
            difference = abs(Fraction.from_float(stored_residual)-residual_fraction(ep))
            exact_gross = ep['exact_fraction']['gross']
            gross_difference = abs(Fraction.from_float(stored_gross)-Fraction(int(exact_gross['numerator']),int(exact_gross['denominator'])))
            bound = Fraction.from_float(ep['final_addition_roundoff_bound'])
            original_assertion_pass=abs(stored_residual)<=TARGET*stored_gross
            report['original_gate']['stored_assertion_pass']=original_assertion_pass
            report['original_gate']['normalized_condition_pass']=normalized<=TARGET
            report['original_gate']['fixed_gate_pass']=original_assertion_pass
            report['endpoint']['stored_final_addition_comparison'] = dict(
                residual_difference_decimal80=display_fraction(difference),
                gross_difference_decimal80=display_fraction(gross_difference),
                differences_within_final_addition_bound=difference <= bound and gross_difference <= bound)
            # A failed stored gate alone cannot establish a summation cause.
            if (not original_assertion_pass and ep['decimal80']['fixed_gate_pass']
                    and difference <= bound and gross_difference <= bound
                    and stored_gross > 0 and abs(stored_residual)/stored_gross == normalized):
                report['interpretation'] = 'FINAL_SUMMATION_ONLY'
        elif ep['status'] == 'AVAILABLE':
            ep['stored_final_addition_comparison'] = missing(['ledgers.photon_residual_or_photon_gross'])
            report['original_gate']['gate_source']='HISTORICAL_NORMALIZED_RATIO_ONLY'
    else:
        report['original_gate'] = missing(['ledgers.photon_normalized'])
    report['solver_status'] = objects.get('solver_return.json', {}).get('status', 'MISSING_DATA')

    intervals = objects.get('solver_return.json', {}).get('intervals')
    extra = setup.get('extra')
    if intervals is None:
        report['intervals'] = missing(['solver_return.intervals'])
    elif not isinstance(extra, int) or extra < 7:
        report['intervals'] = missing(['setup.extra'])
    else:
        records = []
        previous = Fraction(0)
        previous_event = -1
        for record in intervals:
            event = record.get('event')
            if not isinstance(event, int) or event < 0 or event > birth_count:
                raise ValueError('INTERVAL_EVENT_DOMAIN')
            if event != previous_event+1:
                previous = None
            path = data/f'accepted_coordinates_event{event}.npy'
            if not path.is_file() or 'N' not in record:
                result = missing([path.name if not path.is_file() else 'interval.N'])
                previous = None
            else:
                state = np.load(path, allow_pickle=False)
                if state.ndim != 1 or state.size < extra:
                    raise ValueError('INTERVAL_COORDINATE_DIMENSION')
                result = budget(record['N'], state[-extra:][4:7].tolist(), sources[:event])
                current = residual_fraction(result)
                result['signed_local_delta_decimal80'] = display_fraction(current-previous) if previous is not None else None
                result['signed_local_delta_exact_fraction'] = fraction_record(current-previous) if previous is not None else None
                result['local_delta_status'] = 'AVAILABLE' if previous is not None else 'MISSING_PREVIOUS_INTERVAL'
                previous = current
            records.append(dict(event=event, active=event, budget=result))
            previous_event = event
        report['intervals'] = dict(status='AVAILABLE' if all(r['budget']['status'] != 'MISSING_DATA' for r in records) else 'MISSING_DATA', records=records)

    path = data/'observations.json'
    if not path.is_file():
        report['observations'] = missing([path.name])
        report['source_jumps'] = missing([path.name])
    else:
        records = []
        for observation in read_json(path):
            result = physical_budget(observation.get('physical'), observation.get('active'))
            records.append(dict(x=observation.get('x'), side=observation.get('side'),
                                active=observation.get('active'), budget=result))
        report['observations'] = dict(status='AVAILABLE' if all(r['budget']['status'] != 'MISSING_DATA' for r in records) else 'MISSING_DATA', records=records)
        jumps = []
        for pre in records:
            if pre['side'] != 'pre':
                continue
            for post in records:
                if post['side'] != 'post' or post['x'] != pre['x'] or pre['active'] == post['active']:
                    continue
                if pre['budget']['status'] == 'MISSING_DATA' or post['budget']['status'] == 'MISSING_DATA':
                    jumps.append(dict(x=pre['x'], **missing(['pre_or_post_budget'])))
                    continue
                delta = residual_fraction(post['budget'])-residual_fraction(pre['budget'])
                jumps.append(dict(x=pre['x'], status='AVAILABLE', active_pre=pre['active'],
                                  active_post=post['active'], signed_residual_change_decimal80=display_fraction(delta),
                                  signed_residual_change_exact_fraction=fraction_record(delta),
                                  exact_stored_invariant_unchanged=delta == 0))
        report['source_jumps'] = dict(status='AVAILABLE' if jumps else 'MISSING_DATA', records=jumps,
                                      missing=[] if jumps else ['paired_source_jump_observations'])
    explicit_path = data/'source_jumps.json'
    if explicit_path.is_file():
        report['source_jumps'] = explicit_source_jumps(explicit_path, setup)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    save(args.out, diagnose(args.data))


if __name__ == '__main__':
    main()
