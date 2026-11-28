#!/usr/bin/env python3
"""Public derived-witness checker; full original-source generator is in private-input-aware ZIP."""
import csv, math, pathlib, sys
P = pathlib.Path(__file__).resolve().parent
csv_path = P / 'R47_PUBLIC_WITNESS_9.csv'
if not csv_path.exists(): csv_path = P / 'results' / 'R47_PUBLIC_WITNESS_9.csv'
rows = list(csv.DictReader(csv_path.open(encoding='utf-8')))
assert len(rows) == 9
seen = {'JOINT_T_RANGE': 0, 'H_ONLY_T_RANGE': 0, 'OUTSIDE_H_T_RANGE': 0}
for row in rows:
    status = row['source_T_support']; seen[status] += 1
    lo, hi = float(row['T_K_lo']), float(row['T_K_hi'])
    if status == 'JOINT_T_RANGE':
        assert 5 <= lo <= hi <= 3005
        x = (float(row['x_HII_lo']) + float(row['x_HII_hi'])) / 2
        kH = float(row['HD_J1_to_J0_kH_cm3_s'])
        kp = float(row['HD_J1_to_J0_kp_cm3_s'])
        reconstructed = x/(1-x)*(kp/kH)
        reported = float(row['Gamma_p_over_H_mid_loglog'])
        assert math.isclose(reconstructed, reported, rel_tol=3e-13)
        assert float(row['Gamma_p_over_H_outer_lo']) <= reported <= float(row['Gamma_p_over_H_outer_hi'])
    elif status == 'H_ONLY_T_RANGE':
        assert 3005 < lo <= hi <= 5000
        assert row['Gamma_p_over_H_mid_loglog'] == ''
    else:
        assert lo > 5000
        assert row['Gamma_p_over_H_mid_loglog'] == ''
assert seen == {'JOINT_T_RANGE':3,'H_ONLY_T_RANGE':3,'OUTSIDE_H_T_RANGE':3}
print('PUBLIC_R47_WITNESS_9_OF_9_PASS')
