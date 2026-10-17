"""Mechanical packaging of completed saved ready outputs; no ODE or quadrature."""
import json,csv,sys,hashlib,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/laneA'
def normalize(value):
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value).__name__)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False,default=normalize)+'\n')
def main():
    start=time.perf_counter()
    summary=json.loads((OUT/'li_thermal_summary.json').read_text());metrics=summary['metrics'];comparisons=summary['solver_comparisons'];solverdiag=summary['solver_diagnostics'];energy=json.loads((OUT/'ready_energy_checks.json').read_text())
    spots=json.loads((OUT/'independent_detailed_balance_spots.json').read_text());independent=spots['spots'];spot_failures=spots['failures']
    solutions={}
    for label in ['ground_production','ground_257','ground_half_Be','total_RR_sensitivity']:
        path=OUT/(label+'.npz')
        if path.exists():solutions[label]=(np.load(path)['populations'],None)
    with (OUT/'li_charge_history.csv').open() as file:rows=list(csv.DictReader(file))
    F=np.array([float(row['Fdecay']) for row in rows if row['model']=='ground_Milne'])
    donor=json.loads((ROOT/'inputs/laneA/donor_donor.json').read_text()) if (ROOT/'inputs/laneA/donor_donor.json').exists() else None
    manifest=json.loads((ROOT/'inputs/laneA/manifest.json').read_text())
    donor=json.loads((ROOT/manifest['donor']['copied_path']).read_text());abund=donor['result']['Y_final'];L=abund['Li7'];B=abund['Be7']
    sys.path.insert(0,str(ROOT/'tests'));from test_li_thermal_validation import validate
    tests=validate(metrics,comparisons,solverdiag,summary)
    tests['checks'].append({'name':'required_independent_BDF_comparison','observed':'FAILED_REFERENCE','limit':'successful independent comparison required','passed':False})
    for key in ['independent_DB_max_relative','independent_DB_saved_crosscheck_max_relative']:
        tests['checks'].append({'name':key,'observed':metrics[key],'limit':2e-8,'passed':metrics[key]<=2e-8 and len(independent)==18 and not spot_failures})
    tests['passed']=False
    rate_checks=[v for v in tests['checks'] if v['name'] in ['nonfinite_or_nonpositive_alpha_count','nonfinite_log_beta_count','rate64_128_max_relative','tail60_80_max_relative','identity_max_relative','W_K_Q_max_relative','Decimal_formula_max_relative','independent_quad_max_relative','rate_midpoint_direct_max_relative','independent_DB_max_relative','independent_DB_saved_crosscheck_max_relative']]
    groups={'rates':{'completed':True,'passed':all(v['passed'] for v in rate_checks) and len(independent)==18 and not spot_failures,'admitted':'PENDING_INDEPENDENT_REVIEW','checks':rate_checks},'BDF':{'completed':False,'passed':False,'admitted':False,'status':'REFERENCE_HOLD','failed_reference':solverdiag[0]},'ledger':{'completed':True,'passed':metrics['ledger_max_relative']<=1e-12,'admitted':'INTERNAL_CONSISTENCY_ONLY_PENDING_REVIEW','max_relative':metrics['ledger_max_relative']}}
    for label in ['ground_production','ground_257','ground_half_Be','total_RR_sensitivity']:
        if label not in solutions:groups[label]={'completed':False,'passed':False,'admitted':False};continue
        pp=solutions[label][0];minpop=float(pp.min());norm=max(float(np.max(abs(pp[:4].sum(axis=0)-1))),float(np.max(abs(pp[4:].sum(axis=0)-F))))
        source_res=float(np.max(abs((L*pp[:4]+B*pp[4:]).sum(axis=0)-(L+B*F))/np.maximum(np.maximum(L,B*F),1e-30)))
        group={'completed':True,'passed':minpop>=-2e-11 and norm<=2e-11 and source_res<=2e-11,'admitted':'PROVISIONAL_BDF_REFERENCE_HOLD','population_min':minpop,'per_origin_sum_abs':norm,'Li_source_sum_normalized':source_res}
        if label in comparisons:group.update(comparisons[label]);group['passed']=group['passed'] and comparisons[label]['max_absolute_per_origin']<=5e-6
        groups[label]=group
    tests['scoped_groups']=groups;tests['status']='PARTIAL_READY_BDF_REFERENCE_HOLD'
    tests['algebraic_identity_label']='shared-quadrature algebraic consistency; separate independent_DB spots provide independent numerical identity check'
    summary.update({'status':'PARTIAL_READY_BDF_REFERENCE_HOLD','full_suite_passed':False,'BDF_comparison_available':False,'scoped_groups':groups,'energy_checks':energy,'independent_detailed_balance_spots':'independent_detailed_balance_spots.json','shared_quadrature_identity_role':'algebraic consistency only','production_diagnostic_reconstruction':'PCHIP_of_saved_1025_output_states','repair_consumed':True})
    dump(OUT/'li_thermal_summary.json',summary)
    dump(OUT/'li_thermal_tests.json',tests)
    evidence=json.loads((ROOT/'evidence/LI_THERMAL_EXECUTION.json').read_text())
    evidence.update({'status':'PARTIAL_READY_BDF_REFERENCE_HOLD','tests':tests,'scoped_groups':groups,'ready_timings':summary['timings'],'ready_solver_diagnostics':solverdiag,'rate_table_quadrature_repeated':False,'production_repeated':False,'new_independent_DB_spots':18,'BDF_calls_in_ready_continuation':0,'full_suite_passed':False,'remaining_frozen_work':'All available dependency-safe outputs completed; independent BDF validation HOLD','packaging_only':True,'packaging_internal_wall_seconds':time.perf_counter()-start,'ready_final_code_sha256':hashlib.sha256((ROOT/'code/li_thermal_finish_ready.py').read_bytes()).hexdigest(),'ready_numerically_executed_code_sha256':json.loads((OUT/'ready_serialization_correction.json').read_text())['corrected_code_sha256'],'ready_corrected_execution_outcome':'Scientific blocks completed; final scalar serialization corrected by saved-output-only packaging','observed_runtime_model':'UNKNOWN'})
    dump(ROOT/'evidence/LI_THERMAL_EXECUTION.json',evidence)
    print(json.dumps({'status':summary['status'],'metrics':metrics,'comparisons':comparisons,'groups':{key:{k:v for k,v in group.items() if k!='checks' and k!='failed_reference'} for key,group in groups.items()},'RR_sensitivity':summary['RR_sensitivity']},default=normalize))
if __name__=='__main__':main()
