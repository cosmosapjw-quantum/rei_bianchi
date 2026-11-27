"""Produce PHYS57 exact-rational infinite-high hybrid quantitative certificate."""
from pathlib import Path
from wu088_hh.phys57_coulomb_cert import hybrid_inverse_certificate,write_json
ROOT=Path(__file__).resolve().parents[1]
data=hybrid_inverse_certificate(ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz')
out=ROOT/'research/hh_phys57_20261016/results/PHYS57_CERTIFICATE.json'
write_json(out,data)
print('SOURCE_SHA',data['frozen_npz_sha256'])
print('TAIL_SIGN',data['tail_sign_certificate']['all_integer_ell_gte_cutoff_sign'])
print('FINITE_CURRENT',data['finite_exception_current_certificate']['status'])
print('UPPER_EXPONENT',data['hybrid_inverse_upper_log10_approx_DIAGNOSTIC'])
print('OUTPUT',out)
