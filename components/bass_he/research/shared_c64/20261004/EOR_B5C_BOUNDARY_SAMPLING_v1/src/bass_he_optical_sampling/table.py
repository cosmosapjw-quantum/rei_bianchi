"""Candidate finite-interval optical input. Never an endpoint/tail certificate."""
from __future__ import annotations
import hashlib,json,math
from copy import deepcopy
from .core import ContractError,NumericalFailure,hermite,_finite

def _hash(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def build_table(samples,diagnostics):
 if [x['R_a0'] for x in samples]!=[8+i/8 for i in range(17)]:raise ContractError('complete registered grid required')
 cells=[x for x in diagnostics if x['b']-x['a']==.25]
 if len(cells)!=8 or not all(x['Hermite_midpoint_accept'] and x['log_rate_midpoint_accept'] for x in cells):
  raise ContractError('midpoint criteria not met for declared quarter-grid')
 fields=('R_a0','V_entrance_Eh','dV_dR_Eh_per_a0','A_ta_div_alpha3')
 nodes=[{k:x[k] for k in fields} for x in samples[::2]]
 if any(n['A_ta_div_alpha3']<=0 for n in nodes):raise ContractError('strictly positive transition factor required')
 body={'schema':'bass-he.b5c.optical-table.v1','nodes':nodes,'domain_a0':[8.,10.],
       'V_interpolant':'cubic_Hermite_with_finite_CF_slopes','positive_factor_interpolant':'linear_in_log',
       'validation':'registered direct midpoint comparisons only',
       'uniform_error_bound':None,'tail_model':None,'physical_accuracy_certified':False,
       'source_samples_sha256':_hash(samples),'diagnostics_sha256':_hash(cells)}
 return {'body_sha256':_hash(body),**body}

def evaluate(packet,R,*,allow_midpoint_only=False,production=False):
 if production or allow_midpoint_only is not True:raise ContractError('requires opt-in to midpoint-only reference; no production admission')
 if not isinstance(packet,dict):raise ContractError('table packet required')
 b={k:v for k,v in packet.items() if k!='body_sha256'}
 try:valid=_hash(b)==packet.get('body_sha256')
 except (ValueError,TypeError):valid=False
 if not valid or b.get('schema')!='bass-he.b5c.optical-table.v1' or b.get('physical_accuracy_certified') is not False:
  raise ContractError('packet identity/claim mismatch')
 # A recomputed checksum is not authorization to change the meaning of the packet.
 try:
  semantics=(b['domain_a0']==[8.,10.] and b['tail_model'] is None
    and b['uniform_error_bound'] is None
    and b['V_interpolant']=='cubic_Hermite_with_finite_CF_slopes'
    and b['positive_factor_interpolant']=='linear_in_log'
    and [n['R_a0'] for n in b['nodes']]==[8+i/4 for i in range(9)])
  for n in b['nodes']:
   for key in ('R_a0','V_entrance_Eh','dV_dR_Eh_per_a0','A_ta_div_alpha3'):_finite(n[key],key)
   if n['A_ta_div_alpha3']<=0:semantics=False
 except (KeyError,TypeError):semantics=False
 if not semantics:raise ContractError('declared interpolation/domain/error semantics mismatch')
 R=_finite(R,'R')
 if not 8<=R<=10:raise ContractError('no extrapolation outside R8..10')
 nodes=b['nodes'];hit=next((n for n in nodes if n['R_a0']==R),None)
 if hit:
  v=hit['V_entrance_Eh'];f=hit['A_ta_div_alpha3'];support=[R]
 else:
  i=min(int((R-8)/.25),7);a,c=nodes[i:i+2];x,y=a['R_a0'],c['R_a0'];t=(R-x)/(y-x)
  v=hermite(x,y,a['V_entrance_Eh'],c['V_entrance_Eh'],a['dV_dR_Eh_per_a0'],c['dV_dR_Eh_per_a0'],R)
  try:f=math.exp((1-t)*math.log(a['A_ta_div_alpha3'])+t*math.log(c['A_ta_div_alpha3']))
  except (ValueError,OverflowError) as e:raise NumericalFailure('positive factor range') from e
  if f<=0 or not math.isfinite(f):raise NumericalFailure('positive factor underflow/overflow')
  support=[x,y]
 return {'schema':'bass-he.b5c.optical-evaluation.v1','R_a0':R,'V_entrance_Eh':v,'A_ta_div_alpha3':f,
         'interpolated':hit is None,'support_R_a0':support,'table_body_sha256':packet['body_sha256'],
         'physical_accuracy_certified':False,'uniform_error_bound':None,'tail_bound':None,
         'cross_section':None,'thermal_rate':None,'heat':None,'recoil':None,'photon_spectrum':None}
