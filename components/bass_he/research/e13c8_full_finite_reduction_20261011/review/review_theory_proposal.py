#!/usr/bin/env python3
"""Freeze independent algebraic review and saved scalar-parameter checks."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import json
import time
import review_inputs as ri

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
R=ROOT/'analysis/RESIDUAL'

def show(x):
 with localcontext() as c:
  c.prec=22
  return str(Decimal(x.numerator)/Decimal(x.denominator))

def main():
 start=time.perf_counter()
 document=R/'RESIDUAL_AND_NEXT_METHOD_KO.md'
 summary=ri.read(R/'ACTUAL/SECOND_VARIATION_PARAMETERS.json')
 data=ri.read(R/'ACTUAL/SECOND_VARIATION_SEGMENT_PARAMETERS.json')
 ri.check('reviewed_document_identity',ri.h(document)=='5e2181c8d66139d85236208c395a018b4e60cbe92e8981f6220aec3a46265a23')
 ri.check('parameter_source_script_identity',ri.h(R/'second_variation_parameters.py')==summary['source_sha256'])
 rows=data['segments'];paths=data['paths']
 ri.check('parameter_rows_complete_unique',len(rows)==4694 and len({tuple(x['key']) for x in rows})==4694 and len(paths)==2345 and {p['node'] for p in paths}==set(range(2345)))
 by_node={}
 for row in rows:
  d,s,h=(F(row[k]) for k in ('D_L_upper_exact','S_upper_exact','H_h_upper_exact'))
  ri.check('saved_scalar_bounds_nonnegative',min(d,s,h,F(row['incoming_radius_exact']),F(row['frozen_Lh_upper_exact']))>=0,row['key'])
  ri.check('uniform_scalar_remainder_D_squared_S',F(row['uniform_K_squared_delta_upper_exact'])==d*d*s,row['key'])
  ri.check('endpoint_scalar_remainder_Hh_D_S',F(row['endpoint_K_squared_delta_upper_exact'])==h*d*s,row['key'])
  by_node.setdefault(row['node'],[]).append(d)
 for row in paths:
  ds=by_node[row['node']]
  ri.check('path_scalar_sums_and_maxima',F(row['sum_D_L_upper_exact'])==sum(ds) and F(row['max_segment_D_L_upper_exact'])==max(ds),row['node'])
 ds=sorted(F(x['D_L_upper_exact']) for x in rows)
 expected={'min':show(ds[0]),'median':show((ds[len(ds)//2-1]+ds[len(ds)//2])/2),'p95_order_statistic':show(ds[(95*len(ds)+99)//100-1]),'max':show(ds[-1])}
 ri.check('norm_distribution_order_statistics',summary['D_L_upper_distribution_display']==expected)
 ri.check('observed_D_less_than_one',summary['all_D_L_less_than_one']==all(x<1 for x in ds))
 for k,v in summary['formal_direct_coupling_comparison'].items():
  new=F(v['proposed_K_delta_replacement_upper_exact']);old=F(v['old_saved_direct_coupling_upper_exact'])
  ri.check('formal_direct_ratio_arithmetic',old>0 and new>=0 and v['ratio_display']==show(new/old),k)
 ri.check('no_second_candidate_claim',summary['scientific_kernel_calls']==summary['second_variation_integrals']==0 and summary['new_enclosure_admission']=='NOT_RUN')
 proof={
  'variation_of_constants':{'status':'DERIVED_AND_REVIEWED','statement':'delta=delta1+F*e-K*delta follows from delta\'=r-Lambda_f*delta-DeltaLambda*delta and delta(0)=c+e.'},
  'finite_second_correction_identity':{'status':'DERIVED_AND_REVIEWED','derivation':'delta1=(I+K)delta-F e; delta-(I-K)delta1=delta-(I-K)(I+K)delta+(I-K)F e=K^2 delta+(I-K)F e. No infinite-series convergence assumption is used.'},
  'whole_operator_norm':{'status':'DERIVED_AND_REVIEWED','derivation':'0<F<=1 gives ||K z||inf<=D||z||inf with D>=integral|DeltaLambda|. Saved D_L integrates a whole-cell interval upper bound. Endpoint-only H_h is not substituted for this uniform operator norm.'},
  'true_defect_sup_bound':{'status':'DERIVED_AND_REVIEWED','derivation':'delta\'=r-Lambda*delta, Lambda>=0 imply |delta(t)|<=|c|+eta+integral|r|<=S. This avoids an unnecessary 1/(1-D) factor and does not require D<1.'},
  'uniform_and_terminal_bounds':{'status':'DERIVED_AND_REVIEWED','uniform':'(1+D)*eta+D^2*S','terminal':'(F(h)+H_h)*eta+H_h*D*S','qualification':'Bounds concern the exact second-correction function; integration, representation and centering radii must be added by a future implementation.'},
  'species_moment_identity':{'status':'DERIVED_AND_REVIEWED','derivation':'Expand lambda_i(P_f+delta); substitute delta-delta1=F e-K delta in the lambda_fi term. Absolute integrability on the finite segment permits Fubini: -integral w lambda_fi K delta=-integral Q_i DeltaLambda delta, producing k_i=w DeltaLambda_i-Q_i DeltaLambda and the separate G_i e term.'},
  'species_second_correction_bound':{'status':'DERIVED_AND_REVIEWED','derivation':'After adding integral k_i delta1 the residual is G_i e+integral k_i(F e-K delta); |F|<=1, integral|k_i|<=T_i and ||K delta||<=D*S give (|G_i|+T_i)*eta+T_i*D*S.'},
  'special_cases_and_units':{'status':'DERIVED_AND_REVIEWED','checks':['eta term remains on later segments','DeltaLambda=0 kills photon K but need not kill separate species DeltaLambda_i moment correction','D=0 and all species variations=0 remove coupling corrections','r=c=eta=0 gives delta=0','t is the dimensionless log-scale-factor displacement, so D is dimensionless','T_i carries the weight units; H_h D S has photon-stock units','Z has no direct DeltaLambda_i term; QN/QE have no photon-coupling remainder','selected heat triangle bounds retain inherited active heat-weight positivity and fixed captured branch assumptions']},
  'implementation_status':{'status':'NOT_IMPLEMENTED','limitations':['No enclosed prefix delta1(v) or signed K delta1 integral has been computed.','Existing endpoint sums cannot reconstruct all prefixes or justify multiplying the old full interval width by D.','The displayed formal TDS/TS factors exclude propagated incoming uncertainty, midpoint quadrature, representation and centering.','No cost, whole-width improvement factor, O(N) implementation or new heavy allocation is established.']}}
 report={'schema':'bass-he-e13c8-independent-second-variation-proposal-review-v1','status':'PASS_DERIVED_PROPOSAL_ONLY_NOT_NUMERICAL_ADMISSION' if not ri.failures else 'HOLD','reviewer':'e13c8_intake','observed_utc':datetime.now(timezone.utc).isoformat(),'automated_saved_scalar_checks_passed':sum(x['passed'] for x in ri.checks.values()),'automated_saved_scalar_checks_failed':sum(x['failed'] for x in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'mathematical_review':proof,'assumptions':['Finite positive segment length and fixed captured branch.','Lambda_f>=0, Lambda>=0, nonnegative frozen P_f for the saved B_r construction.','Integrable coefficient defects and bounded E/heat weights on the finite segment.','Initial uncertainty |e|<=eta is carried; quadrature and representation errors are not silently removed.'],'candidate_modules_imported':0,'scientific_kernel_calls':0,'new_second_variation_integrals':0,'new_enclosure_admission':'NOT_RUN','new_heavy_tasks':0,'current_finite_decision_unchanged':{'path':'review/INDEPENDENT_DECISION.json','bytes':(HERE/'INDEPENDENT_DECISION.json').stat().st_size,'sha256':ri.h(HERE/'INDEPENDENT_DECISION.json')},'evidence':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':ri.h(p)} for p in [document,R/'second_variation_parameters.py',R/'ACTUAL/SECOND_VARIATION_PARAMETERS.json',R/'ACTUAL/SECOND_VARIATION_SEGMENT_PARAMETERS.json']},'elapsed_seconds':time.perf_counter()-start,'blocking_findings':[] if not ri.failures else ri.failures}
 with (HERE/'THEORY_PROPOSAL_REVIEW.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True,ensure_ascii=False);f.write('\n')
 print(json.dumps({k:report[k] for k in ('status','automated_saved_scalar_checks_passed','automated_saved_scalar_checks_failed','elapsed_seconds')}),flush=True)
 return 1 if ri.failures else 0

if __name__=='__main__':raise SystemExit(main())
