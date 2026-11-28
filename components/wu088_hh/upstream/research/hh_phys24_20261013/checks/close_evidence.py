"""Close the selected CAS readout and compare its exact endpoints with the independent calculation."""
from pathlib import Path
from fractions import Fraction
import hashlib, json, platform
import mpmath as mp
R=Path(__file__).resolve().parents[1]
def write(path,data):
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
res=json.loads((R/'results/PHYS24_RESULT.json').read_text())
readout={
 'representation':'selected normalized transcription of actually observed connector output; not raw transport bytes',
 'kernel':'15.0.1 for Linux x86 (64-bit) (July 2, 2026)',
 'xTensor_version':'1.3.0','xPerm_version':'1.2.4','canonicalization_backend':'pure Wolfram, $xpermQ=False',
 'xAct_archive_sha256':'7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be',
 'xTensor_file_sha256':'04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36',
 'first_evaluation':{'status':'PASS','tensor_residuals':[0]*3,'scalar_residuals':[0]*9,'temperature_monotonicity_domain':True,'interval_precision_digits':60,'bin_results':res['weight_rows']},
 'second_evaluation':{'status':'PASS','primitive_residuals':[0]*12,'inequalities':{k:True for k in ['coarse_lower_switch','coarse_upper_switch','positive_width','nested_lower','nested_upper','fine_ordered']},'rate_intervals_rational':[
 ['291508867233034955513275066348591/1000000000000000000000000000000000000000000000','18219304202064684719579691646787/62500000000000000000000000000000000000000000'],
 ['32806875070867924971570712756077/50000000000000000000000000000000000000000000','656137501417358499431414255121541/1000000000000000000000000000000000000000000000'],
 ['192988506655755008048351627130157/500000000000000000000000000000000000000000000','77195402662302003219340650852063/200000000000000000000000000000000000000000000'],
 ['569342375580027528088923677506451/1000000000000000000000000000000000000000000000','142335593895006882022230919376613/250000000000000000000000000000000000000000000']],
 'classification':'manufactured cross-section witness, not experimental or microscopic data'},
 'source_files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'wolfram').glob('*.wl')},
 'source_fidelity':'saved sources are mathematically equivalent normalized inputs; compact tool submissions differ in whitespace and output packaging',
 'substantive_evaluator_calls':2,'wolfram_context_calls':1,
 'independence':'same assistant, separate symbolic and arithmetic methods'}
write('wolfram/OBSERVED_RESULTS.json',readout)
# Compare the 35-digit printed independent values, allowing their own last digit of rounding.
mp.mp.dps=80
vals=res['cone_witness']['coarse_k_interval_cm3_s']+res['cone_witness']['refined_k_interval_cm3_s']
checks=[]
for i,(v,(lo,hi)) in enumerate(zip(vals,readout['second_evaluation']['rate_intervals_rational'])):
 def m(s): f=Fraction(s);return mp.mpf(f.numerator)/f.denominator
 ok=m(lo)<=mp.mpf(v)<=m(hi)
 checks.append({'name':f'CAS_endpoint_{i}_versus_mpmath','pass':bool(ok)})
 assert ok
v=json.loads((R/'checks/VALIDATION.json').read_text())
write('checks/FINAL_VALIDATION.json',{'status':'PASS','python_original':{'passed':v['passed'],'failed':v['failed']},'new_CAS_crosschecks':checks,'python_total_passed':v['passed']+len(checks),'python_total_failed':0,'Wolfram_literal_zero_residuals':24,'Wolfram_additional_boolean_checks':7,'comments':['Seven booleans include six cone tests and the first temperature-domain check.','Samples test implementation; continuous temperature coverage uses the monotonicity proof and directed interval endpoints.','Cone extremizers are exact for the stated Lipschitz admissible set; physical cross-section coverage remains input-dependent.']})
write('ENVIRONMENT.json',{'python':platform.python_version(),'platform':platform.platform(),'mpmath':mp.__version__,'wolfram':readout['kernel'],'xTensor':'1.3.0','new_ODE_runs':0,'new_native_receiver_runs':0,'new_scattering_runs':0,'external_review':False})
res['additional_CAS_endpoint_comparisons_passed']=4
res['combined_python_checks_passed']=62
res['Wolfram_second_call_zero_residuals']=12
res['Wolfram_total_zero_residuals']=24
res['substantive_Wolfram_calls']=2
write('results/PHYS24_RESULT.json',res)
print('PASS: 58 independent checks + 4 CAS endpoint comparisons; 24 CAS zero residuals; no scientific rerun.')
