#!/usr/bin/env python3
"""One bounded finite-grid-only diagnostic over hash-bound saved NCP endpoints."""
from __future__ import annotations
import hashlib, json, math, sys, time
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parent
RAW=HERE/'raw'
TASK=HERE.parents[2]
EVID=TASK/'native_optimization_20261021/evidence/ncp_time_campaign_20261021'
ANALYSIS=EVID/'ANALYSIS.json'
RECEIPT=EVID/'CAMPAIGN_RECEIPT.json'
EXPECTED={
 'time8':'519d67265330e471ef609f4de049b08c98407a7cc28a28f5b8c40ba3343bcf49',
 'time16':'7f99f0d4e02c74540ca6816e094468ca3197ec45cf72c6cab0ea3053078f21eb',
 'time32':'a0e78399b5455423420821fdd04cf7bd9160b1dea46028194398ebfe704e8a77',
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(x):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(float(x)): raise ValueError('INVALID_SCALAR')
 return Fraction.from_float(float(x))
def fstr(q): return f'{q.numerator}/{q.denominator}'
def dec(q):
 with localcontext() as c:
  c.prec=80
  return str(Decimal(q.numerator)/Decimal(q.denominator))
def endpoint(case):
 p=RAW/f'{case}_endpoint.json'
 if sha(p)!=EXPECTED[case]: raise ValueError('ENDPOINT_HASH_MISMATCH_'+case)
 return json.loads(p.read_text()),p

def main():
 start=time.monotonic()
 endpoints={}; meshes={};configs={};rawhash={}
 for case in ('time8','time16','time32'):
  e,p=endpoint(case);endpoints[case]=e;rawhash[case]=sha(p)
  mp=RAW/f'{case}_common_mesh_ln_a.json';cp=RAW/f'{case}_refinement_config.json'
  meshes[case]=json.loads(mp.read_text());configs[case]=json.loads(cp.read_text())
  rawhash[case+'_mesh']=sha(mp);rawhash[case+'_config']=sha(cp)
 base=dict(configs['time8'])
 for c in ('time16','time32'):
  x=dict(configs[c]); x.pop('time_factor');x.pop('native_steps')
  y=dict(base);y.pop('time_factor');y.pop('native_steps')
  if x!=y: raise ValueError('FROZEN_CONFIG_MISMATCH_'+c)
 factors=[configs[c]['time_factor'] for c in ('time8','time16','time32')]
 steps=[configs[c]['native_steps'] for c in ('time8','time16','time32')]
 if factors!=[8,16,32] or steps!=[968,1936,3872]: raise ValueError('UNEXPECTED_REFINEMENT_GRID')
 # Exact nested sampling check: every old mesh value appears at every second new index.
 nested={}
 for coarse,fine in [('time8','time16'),('time16','time32')]:
  a,b=meshes[coarse],meshes[fine]
  nested[coarse+'_to_'+fine]=(len(b)==2*len(a) and b[1::2]==a)
  if not nested[coarse+'_to_'+fine]: raise ValueError('MESH_NOT_EXACTLY_NESTED_'+coarse+'_'+fine)
 clocks=[endpoints[c]['proper_time_s'] for c in ('time8','time16','time32')]
 births=[endpoints[c]['birth_times_s'] for c in ('time8','time16','time32')]
 if len(set(clocks))!=1 or not (births[0]==births[1]==births[2]): raise ValueError('ENDPOINT_CLOCK_OR_BIRTH_MISMATCH')
 r=json.loads(RECEIPT.read_text()); a=json.loads(ANALYSIS.read_text())
 if r.get('overall_exit_code')!=0 or r.get('new_exit0_count')!=3 or r.get('new_failure_count')!=0: raise ValueError('CAMPAIGN_RECEIPT_NOT_COMPLETE')
 if sha(ANALYSIS)!='45d7b3f1fe346f90502e6062ed6b8b0a9f512d412124fef8589b7129b32f9f1f': raise ValueError('ANALYSIS_HASH_MISMATCH')
 if sha(RECEIPT)!='d7ed2beb165aca6e44ad3c203ed75b7705a631748a15549535d4850b9ed352a5': raise ValueError('CAMPAIGN_RECEIPT_HASH_MISMATCH')
 component_specs=[('N',lambda e:[e['N']]),('U',lambda e:[e['U']]),('temperature_K',lambda e:[e['temperature_K']]),('Gamma_s_0',lambda e:[e['Gamma_s'][0]]),('Gamma_s_1',lambda e:[e['Gamma_s'][1]]),('Gamma_s_2',lambda e:[e['Gamma_s'][2]]),('heat_0',lambda e:[e['heat_erg_per_absorber_s'][0]]),('heat_1',lambda e:[e['heat_erg_per_absorber_s'][1]]),('heat_2',lambda e:[e['heat_erg_per_absorber_s'][2]]),('photo_events_0',lambda e:[e['ledgers'][4]]),('photo_events_1',lambda e:[e['ledgers'][5]]),('photo_events_2',lambda e:[e['ledgers'][6]])]
 rows=[];statuses={};
 for name,get in component_specs:
  vals=[exact(get(endpoints[c])[0]) for c in ('time8','time16','time32')]
  d1,d2=vals[0]-vals[1],vals[1]-vals[2]
  if d1==0 and d2==0: status='DEGENERATE_ZERO_DIFFERENCE';ratio=p3=None
  elif d1==0 or d2==0: status='UNDEFINED_ORDER';ratio=p3=None
  else:
   ratio=abs(d2)/abs(d1)
   with localcontext() as ctx:
    ctx.prec=80
    p3=(-(Decimal(ratio.numerator)/Decimal(ratio.denominator)).ln()/Decimal(2).ln())
   p3=str(p3)
   status='OSCILLATORY_THREE_LEVEL_SEQUENCE' if (d1>0)!=(d2>0) else ('FINITE_DIFFERENCE_DECREASE' if ratio<1 else 'FINITE_DIFFERENCE_NONDECREASE')
  rows.append(dict(observable=name,values_binary64=[float(get(endpoints[c])[0]) for c in ('time8','time16','time32')],d8_16_exact=fstr(d1),d16_32_exact=fstr(d2),d8_16_decimal80=dec(d1),d16_32_decimal80=dec(d2),difference_signs=['+' if q>0 else '-' if q<0 else '0' for q in (d1,d2)],contraction_exact=fstr(ratio) if ratio is not None else None,contraction_decimal80=dec(ratio) if ratio is not None else None,p3_finite_grid=str(p3) if p3 is not None else None,status=status))
  statuses[name]=status
 # Preserve original target calculation and its verdict; no retargeting by p3.
 from sys import path
 path.insert(0,str(TASK/'src'))
 from compare_results import endpoint_metrics
 target={}
 for left,right,label in [('time8','time16','time8_vs_time16'),('time16','time32','time16_vs_time32')]:
  m=endpoint_metrics(endpoints[left],endpoints[right])
  selected=[m['N'],m['U'],m['temperature_K'],*m['photo_events'],*m['Gamma_s'],*m['heat_erg_per_absorber_s']]
  target[label]=dict(original_target=0.005,target_met=all(v is not None and v<=.005 for v in selected),reported_original_pair_metrics=a['pairs'][label]['metrics'],calculated_selected_component_count=len(selected))
 out=dict(schema='rei.age.native_be.finite_grid_diagnostic.v1',name='FINITE_GRID_ONLY_THREE_LEVEL_DIFFERENCE_DIAGNOSTIC',input_identity=dict(pr_head='dd24a9f89e847ae7e97c017ffededd4aa53790d8',campaign_receipt_sha256=sha(RECEIPT),analysis_sha256=sha(ANALYSIS),raw_sha256=rawhash),grid=dict(time_factors=factors,native_steps=steps,exactly_nested_mesh=nested,proper_time_s=clocks[0],same_birth_array=True,operators='NATIVE_BE for all three; saved positive DOP853 age32 excluded'),definition='d1=z8-z16; d2=z16-z32; c_delta=|d2|/|d1|; p3=-log2(c_delta), conditional finite-grid slope only',components=rows,original_target=target,claim_ceiling='Only these saved native-BE endpoints show the listed finite-grid differences; p3 is not a convergence-order theorem, solver contraction bound, continuum error estimate, or guarantee for another grid.',claim_decision=dict(native_age_time_convergence='HOLD',nonlinear_Grackle_response_bound='NOT_ESTABLISHED',PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED'),exit_code=0,elapsed_seconds=time.monotonic()-start)
 (HERE/'DIAGNOSTIC.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(dict(result='PASS_FINITE_GRID_DIAGNOSTIC',diagnostic=out['name'],component_status=statuses,original_target_met={k:v['target_met'] for k,v in target.items()},elapsed_seconds=out['elapsed_seconds']),sort_keys=True))

if __name__=='__main__':
 try: main()
 except Exception as e:
  print(json.dumps(dict(result='HOLD',error=type(e).__name__+': '+str(e))),file=sys.stderr);raise
