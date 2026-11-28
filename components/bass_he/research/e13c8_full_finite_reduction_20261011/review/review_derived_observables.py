#!/usr/bin/env python3
"""Independent derived-observable check using node endpoints, not candidate imports."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import ast
import csv
import json
import time
import review_inputs as ri

HERE=Path(__file__).resolve().parent
ROOT8=HERE.parent
ROOT7=Path('/workspace/scratch/7fd51143e473/e13c7_research_20261011/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1')

def add(*pairs):return tuple(sum((p[i] for p in pairs),F(0)) for i in (0,1))
def neg(p):return -p[1],-p[0]
def mul(p,k):return p[0]*k,p[1]*k
def show(x):
 with localcontext() as c:
  c.prec=24
  return str(Decimal(x.numerator)/Decimal(x.denominator))
def verify_report(saved,p,detail):
 width=p[1]-p[0];middle=(p[0]+p[1])/2
 ri.check('derived_exact_endpoints',ri.pair(saved)==p,detail)
 ri.check('derived_exact_width',F(saved['width'])==width,detail)
 expected={'lo_display':show(p[0]),'hi_display':show(p[1]),'midpoint_display':show(middle),'width_display':show(width),'relative_full_width_display':show(width/abs(middle)) if middle else None,'relative_half_width_display':show(width/(2*abs(middle))) if middle else None}
 for k,v in expected.items():ri.check('derived_display_consistency',saved[k]==v,(detail,k))

def main():
 start=time.perf_counter()
 observed_path=ROOT8/'analysis/FINITE_OBSERVABLES.json'
 observed=ri.read(observed_path)
 sums=ri.read(HERE/'INDEPENDENT_FULL_SUMS.json')
 intervals=ri.decode(sums['full_raw_candidate'])
 m=intervals['absolute'];corr=intervals['correction']
 sources=ROOT7/'inputs/source'
 nodes_path=sources/'OFF_NODES.csv';segments_path=sources/'OFF_SEGMENTS.csv'
 source_lock=ri.read(ROOT7/'SOURCE_LOCK.json')
 for p in (nodes_path,segments_path):
  rel=str(p.relative_to(ROOT7));pin=source_lock['files'][rel]
  ri.check('actual_source_identity',ri.h(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],rel)
 with nodes_path.open() as f:node_rows=list(csv.DictReader(f))
 end=[r for r in node_rows if int(r['step'])==2]
 ri.check('independent_node_endpoint_coverage',len(end)==2440 and {int(r['node']) for r in end}==set(range(2440)) and all(r['mode']=='OFF' for r in end))
 with segments_path.open() as f:seg_rows=list(csv.DictReader(f))
 last={}
 for r in seg_rows:
  if int(r['step'])==2:
   node=int(r['node'])
   if node not in last or int(r['segment'])>int(last[node]['segment']):last[node]=r
 for r in end:
  last_row=last[int(r['node'])]
  ri.check('node_capture_matches_last_segment_energy_and_weight',ri.cap(r['u'])==ri.cap(last_row['u']) and ri.cap(r['weight'])==ri.cap(last_row['weight']),(r['node']))
 first=[r for r in seg_rows if int(r['step'])==1 and int(r['segment'])==0]
 ri.check('all_initial_photon_stocks_zero',len(first)==2440 and all(ri.cap(r['f0'])==0 for r in first))
 eps=F.from_float(1.602176634e-12)
 captured=sum((ri.cap(r['u'])*ri.cap(r['weight'])/eps for r in end),F(0))
 energy=add((captured,captured),corr['energy_eV'])
 tree=ast.parse((ROOT7/'code/vendor/local_enclosure.py').read_bytes())
 chi_raw=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHI' for t in n.targets))
 ri.check('inherited_chi_distinct_from_masks',chi_raw==(13.598434599702,24.587389011,54.41776))
 chi=dict(zip(('HI','HeI','HeII'),map(F.from_float,chi_raw)))
 threshold=add(*(mul(m['A_'+sp],v) for sp,v in chi.items()))
 ledgers={
  'number_P_plus_A_minus_QN':add(m['P_final'],m['A_total'],neg(m['QN'])),
  'energy_final_plus_B_plus_Z_minus_QE_minus_anchor':add(energy,m['B_total_eV'],m['Z_eV'],neg(m['QE_eV']),neg(m['anchor'])),
  'heat_H_minus_B_plus_threshold_energy':add(m['H_total_eV'],neg(m['B_total_eV']),threshold)}
 for k,p in m.items():verify_report(observed['observables'][k],p,('observables',k))
 verify_report(observed['derived_final_energy_stock_eV'],energy,'final_energy')
 verify_report(observed['derived_threshold_energy_eV'],threshold,'threshold_energy')
 for k,p in ledgers.items():
  verify_report(observed['ledger_intervals'][k],p,('ledger',k))
  ri.check('derived_ledger_contains_zero',p[0]<=0<=p[1] and observed['ledger_intervals'][k]['contains_zero'] is True,k)
 ratio_definitions={
  'remaining_photons_per_injected_photon':(m['P_final'],m['QN']),
  'absorptions_per_injected_photon':(m['A_total'],m['QN']),
  'absorbed_energy_per_injected_energy':(m['B_total_eV'],m['QE_eV']),
  'heat_per_injected_energy':(m['H_total_eV'],m['QE_eV']),
  'threshold_energy_per_injected_energy':(threshold,m['QE_eV'])}
 for k,(a,b) in ratio_definitions.items():
  ri.check('positive_ratio_domain',a[0]>=0 and b[0]>0,k)
  p=min(x/y for x in a for y in b),max(x/y for x in a for y in b)
  verify_report(observed['ratios'][k],p,('ratio',k))
 ri.check('derived_input_binding',observed['source_reduction_sha256']==ri.h(ROOT8/'analysis/FULL_RETURN_REDUCTION/REDUCTION.json') and observed['source_segments_sha256']==ri.h(segments_path))
 ri.check('derived_status_and_scope',observed['status']=='PASS_EXACT_DERIVED_FINITE_ANALYSIS' and observed['kernel_invocations']==0 and observed['interval_intersection_used'] is False and observed['full_width_is_not_physical_error'] is True)
 report={'schema':'bass-he-e13c8-independent-derived-observable-review-v1','status':'PASS_EXACT_FINITE_DERIVED_OBSERVABLES' if not ri.failures else 'HOLD','reviewer':'e13c8_intake','observed_utc':datetime.now(timezone.utc).isoformat(),'checks_passed':sum(v['passed'] for v in ri.checks.values()),'checks_failed':sum(v['failed'] for v in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'candidate_modules_imported':0,'scientific_kernel_invocations':0,'independent_endpoint_source':'OFF_NODES.csv step2 u and weight; all2440 match last-segment source capture','captured_final_energy_exact_eV':str(captured),'source_and_conversion_conventions':'exact binary64 lift; weight once; one division by binary64-lift erg/eV; signed energy seam subtracted; CHI distinct from source masks','derived_observable_file':{'path':'analysis/FINITE_OBSERVABLES.json','bytes':observed_path.stat().st_size,'sha256':ri.h(observed_path)},'candidate_script':{'path':'code/analyze_finite_observables.py','bytes':(ROOT8/'code/analyze_finite_observables.py').stat().st_size,'sha256':ri.h(ROOT8/'code/analyze_finite_observables.py')},'ledger_bound_displays':{k:{'lo':show(p[0]),'hi':show(p[1]),'contains_zero':p[0]<=0<=p[1]} for k,p in ledgers.items()},'elapsed_seconds':time.perf_counter()-start,'nonblocking_presentation_note':'Ledger relative widths divided by near-zero midpoint are algebraic ratios, not meaningful relative accuracy measures. Report absolute ledger endpoints and zero inclusion.','claim_ceiling':'Finite fixed capture derived quantities and conservative positive-interval ratios; not continuum efficiencies or physical-error bounds.'}
 with (HERE/'DERIVED_OBSERVABLE_REVIEW.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({k:report[k] for k in ('status','checks_passed','checks_failed','elapsed_seconds')}),flush=True)
 return 1 if ri.failures else 0

if __name__=='__main__':raise SystemExit(main())
