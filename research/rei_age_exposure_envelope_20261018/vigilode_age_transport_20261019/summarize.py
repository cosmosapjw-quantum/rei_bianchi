"""Reaggregate completed intervals, including exact passive/sensitive splitting.

This script reads immutable coefficients and existing certified outputs. It never
runs native dynamics, Rust, or any exponential computation.
"""
from pathlib import Path
from fractions import Fraction
import csv
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent


def outward(value):
    candidate = float(value)
    lower = upper = candidate
    while Fraction.from_float(lower) > value:
        lower = math.nextafter(lower, -math.inf)
    while Fraction.from_float(upper) < value:
        upper = math.nextafter(upper, math.inf)
    return [lower, upper]


def interval(lower, upper):
    return [outward(lower)[0], outward(upper)[1]]


def main():
    study_path = HERE/'results/STUDY.json'
    study_bytes = study_path.read_bytes()
    result = json.loads(study_bytes)
    coefficient_bytes = (HERE/'inputs/nodes.csv').read_bytes()
    passive = Fraction(0)
    passive_nodes = 0
    with (HERE/'inputs/nodes.csv').open() as stream:
        for node in csv.DictReader(stream):
            if all(float(node['lambda'+str(k)]) == 0 for k in range(3)):
                passive += Fraction.from_float(float(node['mass']))
                passive_nodes += 1
    assert passive_nodes == 4096
    reference = result['cases'][-1]['central']
    n64 = result['cases'][-1]['N']
    sensitive64 = [Fraction.from_float(value)-passive for value in n64]
    assert sensitive64[0] > 0
    sensitive64_central = Fraction.from_float(reference['N'])-passive
    cases = []
    for case in result['cases']:
        row = {'birth_groups': case['birth_groups']}
        for name in ['N','U_ev','age_first_number_s','age_second_number_s2']:
            row[name+'_central'] = case['central'][name]
            row[name+'_lower'] = case[name][0]
            row[name+'_upper'] = case[name][1]
            row[name+'_relative_difference_vs64'] = (case['central'][name]-reference[name])/reference[name]
        assert Fraction.from_float(case['passive_surviving_mass'][0]) <= passive <= Fraction.from_float(case['passive_surviving_mass'][1])
        sensitive = [Fraction.from_float(value)-passive for value in case['N']]
        sensitive_interval = interval(*sensitive)
        sensitive_central = Fraction.from_float(case['central']['N'])-passive
        # Passive mass cancels exactly in the signed difference. The reference
        # denominator is explicitly strictly positive before any division.
        if case['birth_groups'] == 64:
            difference = [Fraction(0), Fraction(0)]
            relative = [0.0, 0.0]
        else:
            difference = [Fraction.from_float(case['N'][0])-Fraction.from_float(n64[1]),
                          Fraction.from_float(case['N'][1])-Fraction.from_float(n64[0])]
            corners = [num/den for num in difference for den in sensitive64]
            relative = interval(min(corners), max(corners))
        assert sensitive[0] >= 0
        row.update(passive_N_central=float(passive),
                   passive_N_lower=outward(passive)[0], passive_N_upper=outward(passive)[1],
                   sensitive_N_central=float(sensitive_central),
                   sensitive_N_lower=sensitive_interval[0], sensitive_N_upper=sensitive_interval[1],
                   sensitive_N_relative_difference_vs64_central=float((sensitive_central-sensitive64_central)/sensitive64_central),
                   sensitive_N_relative_difference_vs64_lower=relative[0],
                   sensitive_N_relative_difference_vs64_upper=relative[1],
                   sensitive_reference_denominator_strictly_positive=True,
                   sensitive_N_signed_difference_vs64_lower=interval(*difference)[0],
                   sensitive_N_signed_difference_vs64_upper=interval(*difference)[1],
                   positive_upper_underflow_nodes=case['central_underflow_nodes_with_positive_upper_bound'])
        cases.append(row)
    bounds = []
    for pair in result['paired_bounds']:
        sharp = pair['sharp_per_node_final_upper']
        observed = abs(pair['central_N_difference'])
        bounds.append({'birth_groups': pair['coarse'],
                       'signed_N_difference_central': pair['central_N_difference'],
                       'sharp_per_node_upper': sharp, 'affine_prefix_upper': pair['affine_prefix_final_upper'],
                       'affine_over_sharp': pair['affine_prefix_final_upper']/sharp if sharp else 0,
                       'sharp_over_observed': sharp/observed if observed else 0,
                       'event_leaves': pair['algorithm_counts']['leaves'],
                       'grouped_affine_upper': pair.get('grouped_affine',{}).get('final_upper',0),
                       'grouped_rate_groups': pair.get('grouped_affine',{}).get('groups',0),
                       'grouped_total_leaves': pair.get('grouped_affine',{}).get('total_leaves',0)})
    for name, rows in [('CASES.csv',cases),('BOUNDS.csv',bounds)]:
        with (HERE/'results'/name).open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    endpoint_path = HERE.parent/'evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data/endpoint.json'
    archived = None
    if endpoint_path.is_file():
        endpoint_bytes = endpoint_path.read_bytes()
        source_map = json.loads((HERE/'inputs/SOURCE_MAP.json').read_text())
        assert hashlib.sha256(endpoint_bytes).hexdigest() == source_map['archived_endpoint_sha256']
        archived = {'N': json.loads(endpoint_bytes)['N'],
                    'scope': 'Separate archived native evolving-history result; no trajectory-closeness certificate is asserted.'}
    analysis = {'scope': 'Declared fixed-source fixed-opacity endpoint-geometry age study',
                'study_sha256': hashlib.sha256(study_bytes).hexdigest(),
                'coefficient_csv_sha256': hashlib.sha256(coefficient_bytes).hexdigest(),
                'passive_subset_definition': 'All three imported species hazards exactly zero.',
                'passive_N_exact_dyadic': {'numerator': str(passive.numerator), 'denominator': str(passive.denominator),
                                          'nodes': passive_nodes, 'interval': outward(passive), 'central': float(passive)},
                'sensitive_subset_definition': 'The remaining original labelled nodes, with strictly positive total hazard.',
                'sensitive_N_reference64_interval': interval(*sensitive64),
                'sensitive_reference_denominator_strictly_positive': True,
                'relative_interval_definition': '(sensitive_N_case-sensitive_N_64)/sensitive_N_64, signed; all four interval corners evaluated as exact Fractions before outward conversion.',
                'case64_identity_relative_interval': 'Exactly [0,0] because numerator is the identical same-case quantity.',
                'archived_native_endpoint': archived,
                'cases': cases, 'paired_bounds': bounds,
                'meaning': 'Total surviving number is dominated by invariant passive mass; the sensitive subset exposes birth-clock sensitivity without changing the model.',
                'limitation': 'Global minimum sensitive hazard is loose; exact rate tuple groups retain the opacity spectrum for a useful affine prefix bound.',
                'reaggregation_only_no_native_or_rust_execution': True,
                'original_study_unchanged': study_path.read_bytes() == study_bytes,
                'no_nonlinear_history_admission': True, 'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    (HERE/'results/ANALYSIS.json').write_text(json.dumps(analysis,indent=2)+'\n')
    print(json.dumps({'passive_N_exact': str(passive), 'passive_N': float(passive),
                      'sensitive_reference64': analysis['sensitive_N_reference64_interval'],
                      'sensitive_cases': [{key: row[key] for key in ['birth_groups','sensitive_N_lower','sensitive_N_upper',
                          'sensitive_N_relative_difference_vs64_lower','sensitive_N_relative_difference_vs64_upper']} for row in cases],
                      'archived_native_N': archived['N'] if archived else None,
                      'study_unchanged': analysis['original_study_unchanged']}))


if __name__ == '__main__':
    main()
