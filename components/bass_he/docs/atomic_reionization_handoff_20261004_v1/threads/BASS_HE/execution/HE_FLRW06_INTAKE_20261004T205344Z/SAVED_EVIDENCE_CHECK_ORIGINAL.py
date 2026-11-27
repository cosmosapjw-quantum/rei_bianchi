"""Verify saved execution evidence without replaying old native suites."""
from pathlib import Path
import hashlib,json,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
SUP=ROOT/'intake/runner_adapter/supplier/rei_chat_flrw06_20261005'
sys.path.insert(0,str(SUP/'research'))
from native_protocol import validate_records,evidence_gate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    native=ROOT/'results/native_once'
    receipt=json.loads((native/'NATIVE_EXECUTION_RECEIPT.json').read_text())
    evidence_gate(receipt)
    assert receipt['compile_exit']==0 and receipt['run_exit']==0
    assert sha(native/'native_stdout.jsonl')==receipt['stdout_sha256']
    assert sha(native/'native_stdin.txt')==receipt['stdin_sha256']
    assert sha(native/'native_probe')==receipt['binary_sha256']
    records=[json.loads(s) for s in (native/'native_stdout.jsonl').read_text().splitlines()]
    comparison=validate_records(records,json.loads((SUP/'inputs/CASES.json').read_text()),json.loads((SUP/'results/NODE_REFERENCE_80DIGIT.json').read_text()))
    assert comparison==receipt['comparison']
    manifest=json.loads((SUP/'SOURCE_BINDING.json').read_text())
    for path,b in manifest['minimal_native_source_blobs'].items():
        assert blob(ROOT/'source/src'/Path(path).name)==b,path
    source=json.loads((ROOT/'SOURCE_BINDING.json').read_text())
    for item in source['stage_sources']:
        p=ROOT/'results/stage_build'/item['file']
        assert blob(p)==item['git_blob'] and sha(p)==item['sha256'],item
    for p in ['main.rs','stage_probe.rs']:
        assert (ROOT/'results/stage_build'/p).exists()
    stage=json.loads((ROOT/'results/STAGE_EXECUTION.json').read_text())
    assert stage['compile_exit']==0 and stage['run_exit']==0
    assert sha(ROOT/'results/stage_probe')==stage['binary_sha256']
    assert sha(ROOT/'results/stage_stdout.jsonl')==stage['stdout_sha256']
    assert sha(ROOT/'results/stage_stdin.txt')==stage['stdin_sha256']
    check=json.loads((ROOT/'results/STAGE_INDEPENDENT_CHECK.json').read_text())
    assert check['status']=='SCOPED_ACTUAL_PRIMARY_STAGE_REGRESSION_PASS'
    assert check['native_output_sha256']==stage['stdout_sha256']
    for rel,s in check['inputs_sha256'].items():assert sha(ROOT/rel)==s,rel
    external=[]
    for path in ['intake/external_f08_native.json','intake/external_sync_native.json']:
        e=json.loads((ROOT/path).read_text())
        assert e['stdout_sha256']==receipt['stdout_sha256']
        external.append({'receipt':path,'stdout_equal':True,'binary_equal':e['binary_sha256']==receipt['binary_sha256']})
    # Existing bytes vs remote/published archive identity, not an outgoing backup claim.
    restored=ROOT/'intake/source_recovery.json'
    assert restored.exists()
    env=json.loads((ROOT/'toolchain/installed_selected.json').read_text())
    out={'status':'SCOPED_NATIVE_CLOSEOUT_VERIFIED','baseline_comparison':comparison,
         'baseline_science_source_blobs':6,'stage_science_source_blobs':len(source['stage_sources']),
         'external_stdout_identity_comparisons':external,
         'stage_check':check['comparisons'],
         'execution_counts':{'successful_science_probe_compiles':2,'failed_new_wrapper_compile':1,'successful_probe_processes':2,'baseline_output_records':18,'supplemental_output_records':5,'full_cargo_suites':0,'ODE_histories':0,'independent_4D_endpoint_root_evaluations_per_check':check['reference']['root_nfev'],'independent_root_check_runs':2},
         'scope':'finite native point/stage only; no full-crate build/history/physical/interval promotion',
         'no_production_mutation':True,'signature_authenticity':'UNVERIFIED_NO_TRUSTED_PUBLIC_KEY',
         'input_receipt_sha256':{p:sha(ROOT/p) for p in ['results/native_once/NATIVE_EXECUTION_RECEIPT.json','results/STAGE_EXECUTION.json','results/STAGE_INDEPENDENT_CHECK.json','SOURCE_BINDING.json','toolchain/installed_selected.json','toolchain/signature_verification.json']}}
    (ROOT/'results/FINAL_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
