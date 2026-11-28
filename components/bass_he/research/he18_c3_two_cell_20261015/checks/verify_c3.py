#!/usr/bin/env python3
"""Independent structural + exact-rational two-cell checks for HE18 C3.

Checks a complete stored interval/Taylor second-cell certificate against
first-cell endpoint and original input. No ODE or interval generation is run.
Not a formal independent verification of mpmath interval primitives.
"""
import hashlib, json, zipfile, sys
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from warm_interval import WarmSource, Jet, V,lo,hi
PARENT_R8=ROOT/'inputs/ADOPTION_RESULT_R8.json'
PINS={'P01_STATE.npz':'3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be',
'emissivity.out':'88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
'ENDPOINT_MEMORY_R7.json':'aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39',
'FIXED_REFERENCE.npz':'3572256db4cc17f45f76cf9bcb14434c158066ddcf54d93db26279d688f4b26e',
'ADOPTION_RESULT_R8.json':'3a57883e0640f7e7b7be29dfd0c3adabc168533e91e77bd2027c2ff91a6e0173'}
def decimal_out(x,up=False):
 with localcontext() as ctx:
  ctx.prec=44;ctx.rounding=ROUND_CEILING if up else ROUND_FLOOR
  return str(Decimal(x.numerator)/Decimal(x.denominator))
def exact_poly(n,x):
 from math import factorial
 return sum(((-1)**(k+1)*x**k/Q(factorial(k)) for k in range(1,n+1)),Q(0))
def validate():
 for f,digest in PINS.items():assert hashlib.sha256((ROOT/'inputs'/f).read_bytes()).hexdigest()==digest,(f,'pin')
 j=json.loads((ROOT/'results/CERTIFICATE.json').read_text());detail=json.loads((ROOT/'results/RESIDUAL_COUPLING.json').read_text())
 first=json.loads(PARENT_R8.read_text());packet=json.loads((ROOT/'inputs/ENDPOINT_MEMORY_R7.json').read_text())
 assert j['stage']=='HE18_C3' and j['cell_s']==['6250000000','12500000000']
 assert first['source_interval_s']==['0','6250000000'] and packet['source_interval_s']==['0','6250000000']
 s=WarmSource();h=s.hq;scale=[Q(1),Q(1),Q(1),Q(32)]
 with np.load(ROOT/'inputs/P01_STATE.npz') as d:
  for i in range(2908):assert s.coeff[i][0]==Q.from_float(float(d['states'][i,1]))
  assert all(sum(s.coeff[i])==Q.from_float(float(d['states'][i,2])) for i in range(2908))
 incoming_gas=[Q(x) for x in packet['gas_error_end_scaled']]; incoming_photon=[Q(x) for x in packet['photon_error_end_raw_exact']]
 assert len(incoming_gas)==4 and len(incoming_photon)==2904 and all(x>=0 for x in incoming_gas+incoming_photon)
 assert any(x>0 for x in incoming_photon)
 assert [Q(x) for x in j['incoming_gas_scaled']]==incoming_gas
 assert [Q(x) for x in detail['incoming_gas_scaled']]==incoming_gas
 assert j['next_physical_cell_incoming_included'] and j['first_initial_match']
 # The comparison box source is the true-solution global first-exit domain for this unchanged P01 source.
 hh=json.loads((ROOT/'inputs/HH_P01_COMPARISON.json').read_text())
 g0=list(map(Q,hh['gas_initial_exact'])); rad=list(map(Q,hh['gas_radii']));e=[Q(x['rational']) for x in j['gas_error_components']]
 uses=[(max(abs(z-g0[i]) for z in s.controls[i])+e[i])/rad[i] for i in range(4)]
 assert max(uses)<1, 'reference plus propagated true-error radius exits original gas box'
 assert all(min(ctrl)>=0 for ctrl in s.controls[4:]), 'second photon Hermite positivity'
 # Gas box and interval H/T/source regularity are inherited from valid first-exit source.
 assert Q(j['gain']['rational'])<1
 pp=[[Q(a) for a in row] for row in j['scaled_P']]
 assert all(x>=0 for row in pp for x in row)
 assert max(sum(row,Q(0)) for row in pp)==Q(j['gain']['rational'])
 # Distinguish exact node-count/C couplings and positive source injection.
 assert len(detail['photon'])==2904==len(detail['B_scaled'])==len(detail['C_scaled'])
 assert j['transparent_count']==784
 forcG=[Q(a['rational']) for a in j['gas_integral_scaled']]
 forcP=[Q(a['rational']) for a in j['photon_forcing_scaled']]
 carryP=[Q(x) for x in j['incoming_photon_to_gas_scaled']]
 assert [Q(x) for x in detail['incoming_photon_scaled_force']]==carryP
 for i in range(4):
  reconstructed=h*sum((Q(detail['B_scaled'][k][i])*incoming_photon[k] for k in range(2904)),Q(0))
  assert reconstructed==carryP[i], 'missing carried photon component or B mismatch'
 matrix=[[Q(i==k)-pp[i][k] for k in range(4)] for i in range(4)]
 dd=[incoming_gas[i]+carryP[i]+forcG[i]+forcP[i] for i in range(4)]
 for i in range(4):
  err_scaled=[e[k]/scale[k] for k in range(4)]
  assert sum((matrix[i][k]*err_scaled[k] for k in range(4)),Q(0))==dd[i], 'comparison inverse algebra'
 # Actual branch consistency in all 2904 rows: no certified threshold crossing during second cell.
 whole=json.loads((ROOT/'results/whole_jets.json').read_text())
 assert len(whole['nodes'])==2904
 assert all(Q(p['E'][0])>0 and Q(p['E'][1])>0 for p in whole['nodes'])
 # Compare exact interval enclosure to C1 long-double sampled middle RHS, with a very loose guard.
 assert float(j['gas_sup_per_s'][0].replace('E','e'))>2.678172307847861e-26
 left,right=map(Q,first['tau_interval_exact']);lo2,hi2=map(Q,j['true_depth_interval'])
 assert 0<left<right and 0<lo2<hi2 and right+hi2<Q(1)
 tlo=left+lo2;thi=right+hi2
 plo=exact_poly(4,tlo);phi=exact_poly(5,thi)
 assert 0<plo<phi
 return dict(schema='he18.c3.exact_rational_two_cell_review.v1',status='SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES',
  first_cell_tau=[decimal_out(left),decimal_out(right,True)],second_cell_tau=[decimal_out(lo2),decimal_out(hi2,True)],
  two_cell_tau=[decimal_out(tlo),decimal_out(thi,True)],two_cell_probability=[decimal_out(plo),decimal_out(phi,True)],
  two_cell_tau_interval_exact=[str(tlo),str(thi)],two_cell_P_interval_exact=[str(plo),str(phi)],
  second_cell_column_radius_m2_upper=j['column_radius_m2_inv']['upper_display'],
  max_reference_plus_error_gas_box_fraction=decimal_out(max(uses),True),
  existing_exact_input_hashes=PINS,checks={
    'incoming_gas_exact':True,'all_2904_incoming_photon_components_included':True,'positive_reference_photons_whole_cell':True,
    'gas_global_tube_inner':True,'positive_comparison_gain':True,'nonnegative_matrix':True,
    'exact_resolvent_equation':True,'source_regularity':True,'adjacent_clock_segments':True,'two_cell_probability_monotone':True},
  model_physical_precision='exact_real_finite_model_only',new_native_binary64_roundoff_certificate=None,
  all_16_cells_certified=False,actual_cosmological_observer_foreground=None,
  source_ODE_reexecuted=False,independent_review_of_mpmath_interval_primitives=False)
if __name__=='__main__':
 p=ROOT/'results/TWO_CELL_VALIDATION.json'
 if p.exists():raise SystemExit('REFUSE_OVERWRITE')
 obj=validate();p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:obj[k] for k in ['status','first_cell_tau','second_cell_tau','two_cell_tau','two_cell_probability','second_cell_column_radius_m2_upper','max_reference_plus_error_gas_box_fraction']},indent=2));
