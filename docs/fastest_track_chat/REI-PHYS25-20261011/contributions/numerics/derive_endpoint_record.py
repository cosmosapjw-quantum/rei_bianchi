#!/usr/bin/env python3
"""Translate the stored primary upper root endpoint into a law.

This performs no kernel evaluation and no root search. The source numerator's
numerical sign is retained; this is not a rigorous interval certificate.
"""
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from pathlib import Path

getcontext().prec = 160
here = Path(__file__).resolve().parent
source = here / 'VARIANCE_CANDIDATE.json'
source_hash = sha256(source.read_bytes()).hexdigest()
if source_hash != 'bb89271e705eae1db014fcb6371539af9e6496747e6cc288706c94dc87c71a63':
    raise ValueError('unexpected first numerical result identity')
data = json.loads(source.read_text())
root = data['primary_anchored_root']
a, m, v = D('13.61'), D(18), D(root['final_bracket_eV'][1])
numerator = D(root['final_function_values'][1])
pa, pv = (v-m)/(v-a), (m-a)/(v-a)
variance = (m-a)*(v-m)
record = {
    'task': 'REI-PHYS25-20261011',
    'kind': 'algebraic translation of already evaluated positive root endpoint',
    'source_result_sha256': source_hash,
    'new_kernel_evaluations': 0, 'new_root_iterations': 0,
    'numerical_support_eV': [str(a), str(v)],
    'probabilities': [str(pa), str(pv)],
    'probability_mass': str(pa+pv), 'mean_energy_eV': str(pa*a+pv*v),
    'variance_eV2': str(variance), 'rms_width_eV': str(variance.sqrt()),
    'stored_endpoint_numerator_eV_s-4': str(numerator),
    'derived_response_s-4': str(numerator/(v-a)),
    'positive_stored_numerical_response': numerator > 0,
    'scope': 'Numerically feasible displayed endpoint; no interval-arithmetic certification or J uncertainty enclosure.'
}
out = here / 'NUMERICAL_FEASIBLE_ENDPOINT.json'
with out.open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps(record, indent=2))
