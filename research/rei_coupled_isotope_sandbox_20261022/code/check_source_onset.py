#!/usr/bin/env python3
"""Two authorized source-onset coverage checks; no baseline diagnostic replay."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import sys
sys.dont_write_bytecode=True
import hashlib,json,math,platform,time,traceback
from pathlib import Path
import numpy as np
from atomic import PreparedAtomic
from local import Coefficient,ResolvedEvent,ENERGY
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence'
wall0=time.perf_counter();cpu0=time.process_time()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def clean(value):
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,np.generic):return clean(value.item())
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [clean(v) for v in value]
    return value

def main():
    path=OUT/'TARGETED_SOURCE_ONSET.json'
    if path.exists():raise FileExistsError('Existing targeted evidence; preserve it before another execution.')
    baseline=json.loads((OUT/'EXECUTION.json').read_text())
    source_identity={'baseline_three_code_sha256_unchanged':{},'targeted_script_sha256':sha(Path(__file__).resolve())}
    for name,expected in baseline['code_sha256'].items():
        actual=sha(ROOT/name)
        if actual!=expected:raise ValueError('BASELINE_CODE_BYTES_CHANGED:'+name)
        source_identity['baseline_three_code_sha256_unchanged'][name]=actual
    p=PreparedAtomic(1000.,1.);population=np.zeros(21);population[4]=.5
    ledger={key:0. for key in ENERGY};logk=-25.;nb=1.;rows=[];exception=None
    try:
        for name,products,target in [('DII_DII_to_He3III_n',{9:1,0:1},0),('DII_DII_to_HII_TII',{2:1,6:1},6)]:
            event=ResolvedEvent(name,{4:2},products,Coefficient('POSITIVE',logk),'m^3/s',
                                'MANUFACTURED_SOURCE_ONSET; Q0 and all energy increments explicitly zero',
                                'RESOLVED_DIAGNOSTIC_CHANNEL_ONLY',ledger,p.A,p.q)
            outcome=event.evaluate(population,nb)
            expected=math.exp(logk)*nb*population[4]**2/2
            relative=abs(outcome['rate']-expected)/expected
            baryon=sum(int(a)*int(v) for a,v in zip(p.A,event.nu))
            charge=sum(int(q)*int(v) for q,v in zip(p.q,event.nu))
            passed=population[target]==0. and outcome['source'][target]>0 and outcome['status']=='POSITIVE' and math.isfinite(outcome['log_rate']) and baryon==0 and charge==0 and relative<=2e-12
            rows.append({'name':name,'status':'PASS' if passed else 'FAIL','input':{'Y':population,'target_slot':target,'target_name':p.names[target],'target_initial_exact_zero':population[target]==0,'reactants':{4:2},'products':products,'log_coefficient':logk,'coefficient_unit':'m^3/s','nb_m-3':nb,'energy_J_per_event':ledger,'energy_interpretation':'manufactured; not empirical nuclear Q'},
                         'output':outcome,'expected_polynomial_flux':expected,'flux_relative_error':relative,'flux_tolerance':2e-12,'exact_integer_baryon_residual':baryon,'exact_bare_charge_residual':charge})
    except Exception:exception=traceback.format_exc()
    failed=[r['name'] for r in rows if r['status']!='PASS'];exit_code=int(bool(failed or exception or len(rows)!=2))
    result={'schema':'rei-sandbox-targeted-source-onset-v1','status':'PASS_TARGETED_SOURCE_ONSET' if not exit_code else 'FAIL_PRESERVED','baseline_observed_checks':156,'baseline_rerun':False,'targeted_checks':len(rows),'failed_tests':failed,'tests':rows,'exception':exception,'source_identity':source_identity,
            'execution':{'command':[sys.executable,str(Path(__file__).resolve())],'exit_code':exit_code,'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'wall_s':time.perf_counter()-wall0,'CPU_s':time.process_time()-cpu0,'requested_executor':'same bounded implementation worker; Astra-authorized targeted coverage repair','observed_model_identity':'UNAVAILABLE_FROM_RUNTIME_TOOL_OUTPUT'},
            'counts':{'new_source_onset_checks':2,'full_diagnostic_reruns':0,'local_IVPs':0,'cosmological_IVPs':0},
            'authorization':'one targeted coverage repair; preserve original 156-PASS diagnostic and all three baseline code hashes'}
    path.write_text(json.dumps(clean(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'baseline_checks':156,'targeted_checks':len(rows),'failed':failed,'exception':exception,'exit_code':exit_code,'source_identity':source_identity},indent=2))
    return exit_code

if __name__=='__main__':raise SystemExit(main())
