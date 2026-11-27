"""Evaluate the joint photon constraint on the published F05 V2 dataset."""
import argparse
import csv
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
from collections import defaultdict

from rei_bianchi.microphysics.he import correlated_partition_bounds

DATA = (Path(__file__).resolve().parents[1] / 'research/rei_f05_v2_lya_local_reabsorption_20261115'
        / 'results/REI_ORIGINAL_V2_LYA_LOCAL_H_HEI_FEEDBACK_92160.csv.gz')
SHA = '6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae'
E, H, HE = map(Fraction, ('40.813320', '13.598434599702', '24.587389011'))
EV_ERG = Fraction('1.602176634e-12')


def reduce_archive(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA:
        raise ValueError('Source CSV identity mismatch')
    sums = defaultdict(lambda: [Fraction(0), Fraction(0)])
    naive_high, rows, last = Fraction(0), 0, None
    with gzip.open(path, 'rt', newline='') as f:
        for record in csv.DictReader(f):
            tick, right_tick, node = map(int, (record['left_tick'], record['right_tick'], record['source_node']))
            if (tick, right_tick, node) != (160 + rows // 46080, 161 + rows // 46080, rows % 46080):
                raise ValueError('Source intervals/order/node identifiers disagree')
            boxes = [tuple(Fraction(record[k + suffix]) for suffix in ('_lo', '_hi')) for k in
                     ('emitted', 'absorbed_H', 'absorbed_HeI', 'escaped')]
            bounds = correlated_partition_bounds(*boxes)
            for k, (low, high) in bounds.items():
                sums[k][0] += low
                sums[k][1] += high
            naive_high += sum(box[1] for box in boxes[1:]) * E * EV_ERG
            rows += 1
            last = [tick, right_tick, node]
    if rows != 92160:
        raise ValueError('Source interval count mismatch')
    h_lo, h_hi = sums['hydrogen_absorptions']; he_lo, he_hi = sums['helium_absorptions']
    h_share = [h_lo/(h_lo+he_hi), h_hi/(h_hi+he_lo)]
    heat_share = [(E - HE + (HE - H) * w) / E for w in h_share]
    true_hi = sums['emitted_energy_erg'][1]
    return {'source_commit':'b8300f57a5c36c109bf9a982769fb7ba76d250eb', 'input_sha256':SHA,
            'source':'F05 V2 local He II Ly-alpha research ticks160 through162',
            'source_rows':rows, 'last_key':last, 'new_ivps':0,
            'algorithm':'Exact rational arithmetic on the decimal CSV endpoints. Per row original lower/upper H I, He I and escape constrained by their sum lying in the emitted interval. Product of row polytopes; shared source-parameter dependencies between rows may further tighten the physical ranges.',
            'bounds_rounded_binary64':{k:list(map(float,v)) for k,v in sorted(sums.items())},
            'hydrogen_receives_fraction_of_all_local_absorptions':list(map(float,h_share)),
            'heat_fraction_of_locally_absorbed_line_energy':list(map(float,heat_share)),
            'complementary_binding_energy_fraction':[float(1-heat_share[1]),float(1-heat_share[0])],
            'local_heat_per_absorption_eV':list(map(float,(v*E for v in heat_share))),
            'unconstrained_sum_of_branchwise_upper_energies_erg':float(naive_high),
            'simultaneous_total_upper_erg':float(true_hi),
            'excess_of_marginal_sum_relative_to_joint_upper':float(naive_high/true_hi-1),
            'interpretation':'Finite original F05 source intervals and their stored outer boxes. These counts/energies are already in its population and thermal RHS. AXBI primary Case-A has no F05 OTS injection.'}

if __name__=='__main__':
    cli=argparse.ArgumentParser(); cli.add_argument('--output',type=Path,required=True)
    dest=cli.parse_args().output
    result=reduce_archive(DATA)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
