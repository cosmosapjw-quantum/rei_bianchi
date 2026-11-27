"""PHYS58 C5–C8 source-locked original 2S Gaunt/interval/GL producer."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, json
import numpy as np

from wu088_hh.phys58_exact_multipoles import (
 make_interval_rows,exact_neighbour_m0_lower,
 truncated_original_screen_matrix,independent_numpy_angular_matrix,
 exact_legendre_coefficient_interval)
from wu088_hh.phys58_screen_multipoles import (
 original_source_sha_guard,legendre_tail_upper)
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source',default=str(ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'))
parser.add_argument('--out',default=str(ROOT/'research/hh_phys58_20261016/c5c8/results/EXACT_COEFFICIENTS_AND_GAUNT.json'))
a=parser.parse_args()
sha=original_source_sha_guard(a.source)
rows27=make_interval_rows(a.source,ns=tuple(range(13)),r=F(27),terms=320,dps=240)
rows30=make_interval_rows(a.source,ns=(0,1,2,4,8,12),r=F(30),terms=320,dps=240)
els=(20,21,22)
checks=[]
for m in (0,1,2):
    analytic,interval_width=truncated_original_screen_matrix(els,m,F(27),degree=12,terms=320,dps=85)
    ref128=independent_numpy_angular_matrix(els,m,r=27.0,nodes=128)
    ref256=independent_numpy_angular_matrix(els,m,r=27.0,nodes=256)
    diff=max(abs(float(analytic[i,j])-ref256[i,j]) for i in range(3) for j in range(3))
    diff_ref=float(np.max(np.abs(ref128-ref256)))
    checks.append({
       'm':m,'ells':list(els),'analytic_2S_3by3_matrix_mpmath_noncertifying':[[str(analytic[i,j]) for j in range(3)] for i in range(3)],
       'numpy_Gauss_128_vs_256_max_abs':diff_ref,
       'analytic_vs_numpy_Gauss256_max_abs':diff,
       'analytic_exact_coefficient_max_interval_width':'%.8e'%float(interval_width),
       'all_angular_degree12_2S_operator_tail_upper_exact':str(2*legendre_tail_upper(12)),
       'source_r_Bohr':27,
       'numerical_status':'NONCERTIFYING_GAUNT_MATRIX_EVALUATION'},
    )
nonzero=exact_neighbour_m0_lower(F(27))
assert checks[0]['analytic_vs_numpy_Gauss256_max_abs']<5e-35
obj={'schema':'WU088_HH_PHYS58_C5_C8_GAUNT_REDUCED_EXTERIOR_V1',
 'frozen_source_SHA256':sha,
 'physical_potential':'h=-Delta/2-1/r-(1+1/s)*exp(-2s); s=|x-0.7 z|',
 'exact_interval_rows_at_r27':rows27,
 'exact_interval_rows_at_r30':rows30,
 'strict_original_P20Q21_positive_lower_at_r27':nonzero,
 'matrices':checks,
 'theoretical_benchmark':'uniform N12 far-high direct 2S upper '+str(2*legendre_tail_upper(12)),
 'status':'RIGOROUS_SOURCE_LOCKED_FINITE_COEFFICIENT_INTERVALS_PLUS_NUMERICAL_3x3_GAUNT',
 'invalid_promotion':['not screened Coulomb outgoing resolvent','not noncentral exterior DtN or microscopic cross section'],
 'HH_R10':'OFF'}
path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
for n in (0,1,4,8,12):
  print('A_n(r27)',n,rows27['rows'][n]['mpmath_noncertifying'])
for d in checks:
  print('m=',d['m'],'matrix P20Q21=',d['analytic_2S_3by3_matrix_mpmath_noncertifying'][0][1],
        'Gaunt_vs_GL256=',d['analytic_vs_numpy_Gauss256_max_abs'])
print('strict mathematical P20Q21 bound:',nonzero['physical_V_2S_P20_to_Q21_strict_gt'])
print('scientific production HH_R10=OFF; no screened outgoing DtN')
