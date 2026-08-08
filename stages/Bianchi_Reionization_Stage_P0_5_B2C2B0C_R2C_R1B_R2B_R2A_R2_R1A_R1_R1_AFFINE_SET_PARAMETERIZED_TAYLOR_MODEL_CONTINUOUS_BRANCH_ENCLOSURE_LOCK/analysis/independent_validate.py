#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sympy as sp
STAGE=Path(__file__).resolve().parents[1]

def validate():
 r=json.loads((STAGE/'results.json').read_text())
 a=r['source_safe_rank_audit']
 assert r['completed'] is True
 assert r['continuous_parameter_certified'] is False
 assert r['production_history_authorized'] is False
 assert a['node_count']==46080 and a['robust_rank2_nodes']>45000
 assert a['source_safe_rank_lower_bound']==2*a['robust_rank2_nodes']+a['rank1_remainder_nodes']
 assert a['source_safe_rank_lower_bound']>90000 and a['global_parameter_rank']==2
 assert a['sparse_quadratic_storage_mib']<16.0
 assert len(r['coherent_auditor'])==3
 for lane in r['coherent_auditor']:
  assert lane['coherent_all_hard_gates_pass'] is True
  assert max(lane['coherent_empirical_widths'].values())<2e-3
  assert max(lane['withheld_max_absolute_residual'].values())<1e-8
  assert lane['claim']=='COHERENT_TWO_GLOBAL_PARAMETER_AUDITOR_ONLY'
  assert all(sum(item['outside_counts'].values())==0 for item in lane['adversarial'])
 assert r['decision']['classification']=='SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED'
 v,f,y,z,rr=sp.symbols('v f y z r');ell=sp.Rational(57,40);m=sp.Rational(737,1000);w=(ell-m)+m*y
 det=sp.expand(rr*(w-f*z)*rr*(1-v)*(1-z)-rr*(1-v)*z*rr*(m*(1-y)-f*(1-z)))
 assert sp.simplify(det-rr**2*(1-v)*(w-ell*z))==0
 return {'status':'PASS','rank_lower_bound':a['source_safe_rank_lower_bound'],'coherent_lane_count':3}
if __name__=='__main__':print(json.dumps(validate(),sort_keys=True))
