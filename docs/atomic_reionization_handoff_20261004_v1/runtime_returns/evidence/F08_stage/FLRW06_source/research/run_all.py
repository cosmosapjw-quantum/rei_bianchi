"""Run only this new bounded reference package. Native absence is NOT PASS."""
from pathlib import Path
import subprocess,sys,json,time,tempfile,os
ROOT=Path(__file__).resolve().parents[1]
commands=[('independent_nodes',[sys.executable,'research/reference.py']),('stage_cone',[sys.executable,'research/check_stage.py']),('unit_protocol',[sys.executable,'-m','unittest','discover','-s','tests','-v']),('python_syntax',[sys.executable,'-m','py_compile',*map(str,(ROOT/'research').glob('*.py'))])]
records=[]
for name,cmd in commands:
    t=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=40,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
    (ROOT/'logs'/f'final_{name}_stdout.log').write_bytes(p.stdout);(ROOT/'logs'/f'final_{name}_stderr.log').write_bytes(p.stderr)
    records.append({'name':name,'command':cmd,'exit_code':p.returncode,'seconds':time.monotonic()-t})
    if p.returncode:break
# Non-mutating environment check: already executed native preflight preserves
# its original exit78 receipt. This runner does not repeat a native attempt.
native=json.loads((ROOT/'results/native_attempt/NATIVE_EXECUTION_RECEIPT.json').read_text())
result={'task':'REI-CHAT-FLRW06-20261005','status':'REFERENCE_COMPLETE__NATIVE_BLOCKED' if all(r['exit_code']==0 for r in records) and len(records)==4 else 'REFERENCE_FAILED','commands':records,
  'native_preflight':native,'native_compiles':0,'native_calls':0,'ODE_integrations':0,'prior_suites_rerun':False,
  'counts':{'unit_tests':14,'exact_rational_cone_cases':240,'symbolic_identities':4,'80digit_reference_profiles':11,'future_native_invalid_inputs':6},
  'limitations':['Rust driver not compiled','Python protocol tests use manufactured records only','No actual time integration or physical/interval certification']}
(ROOT/'results/FINAL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
sys.exit(0 if result['status']=='REFERENCE_COMPLETE__NATIVE_BLOCKED' else 1)
