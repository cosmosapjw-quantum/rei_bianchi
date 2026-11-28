#!/usr/bin/env python3
"""Positive photon endpoint error carry after whole-cell HE18 C3 enclosure.

D_N,j(t2) <= incoming_j + h sum_k C^+_{jk} D_g,k(scaled)
                        + integral_0^1 |R_N,j(u)|du.
For later cells, a new B must consume the entire 2904-entry vector.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def run():
 cert=json.loads((ROOT/'results/CERTIFICATE.json').read_text())
 detail=json.loads((ROOT/'results/RESIDUAL_COUPLING.json').read_text())
 original=(ROOT/'inputs/ENDPOINT_MEMORY_R7.json').read_bytes()
 if hashlib.sha256(original).hexdigest()!='aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39':
  raise ValueError('WRONG_FIRST_CELL_CARRY')
 packet=json.loads(original)
 ep=[Q(x) for x in packet['photon_error_end_raw_exact']]
 scales=[Q(1),Q(1),Q(1),Q(32)]
 eg=[Q(x['rational'])/scales[k] for k,x in enumerate(cert['gas_error_components'])]
 h=Q(6250000000)
 assert len(ep)==len(detail['C_scaled'])==len(detail['photon'])==2904
 result=[];total_prior=Q(0);total_add_coupling=Q(0);total_r=Q(0)
 for j in range(2904):
  coupling=h*sum((Q(detail['C_scaled'][j][k])*eg[k] for k in range(4)),Q(0))
  res=Q(detail['photon'][j]['integral'])
  assert coupling>=0 and res>=0
  result.append(ep[j]+coupling+res)
  total_prior+=ep[j];total_add_coupling+=coupling;total_r+=res
 if not all(x>=0 for x in result):raise ValueError('NEGATIVE_ENDPOINT_RADIUS')
 return dict(schema='he18.c3.second_cell_outgoing_photon_errors.v1',
             source_commit='a5c958c414dea41216b445c05f58df837f05cacb',
             source_interval_s=['6250000000','12500000000'],
             reference='SECOND_CELL_FIXED_HERMITE_EXACT_DYADIC',
             incoming_first_cell_hash=hashlib.sha256(original).hexdigest(),
             incoming_nonzero_count=sum(x>0 for x in ep),
             outgoing_photon_error_end_raw_exact=[str(x) for x in result],
             scaled_gas_error_end_exact=list(map(str,eg)),
             error_sum_incoming=str(total_prior),
             error_sum_added_coupling=str(total_add_coupling),
             error_sum_added_local_residual=str(total_r),
             nonzero_count=sum(x>0 for x in result),
             next_cell_majorants=None,physical_input_evolution_error=None,
             provider_roundoff_budget=None,source_ODE_invoked=False,
             statement='second saved cell error packet only; third cell needs its own reference and B')
if __name__=='__main__':
 target=ROOT/'results/SECOND_ENDPOINT_MEMORY.json'
 if target.exists():raise SystemExit('REFUSE_OVERWRITE')
 obj=run();target.write_text(json.dumps(obj,indent=2)+'\n');print('saved',target,'count',len(obj['outgoing_photon_error_end_raw_exact']))
 print('photon sum incoming',float(Q(obj['error_sum_incoming'])), 'coupling add',float(Q(obj['error_sum_added_coupling'])),'residual add',float(Q(obj['error_sum_added_local_residual'])))
