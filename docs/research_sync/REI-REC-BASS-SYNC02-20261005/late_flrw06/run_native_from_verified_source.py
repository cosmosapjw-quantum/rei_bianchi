"""Extract pinned original source from an EXISTING repo and run one rustc probe.

No network, cargo, production modifications, original tests, or histories.
Exit 78 means environment/source prerequisite unavailable. No PASS is written.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent / "supplier/rei_chat_flrw06_20261005/research"))
from native_protocol import stdin_payload,validate_records,evidence_gate,ROOT

def digest(b):return hashlib.sha256(b).hexdigest()
def git_blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def run(cmd,timeout=40,**kw):return subprocess.run(cmd,capture_output=True,timeout=timeout,**kw)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    receipt={'task':'REI-CHAT-FLRW06-20261005','status':'PREFLIGHT','native_calls':0,'compile_exit':None,'run_exit':None,'source_blobs_verified':False}
    def save():
        (args.output/'NATIVE_EXECUTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    rustc=shutil.which('rustc')
    if rustc is None:
        receipt.update(status='BLOCKED_COMPILER_ABSENT',blocker='rustc not installed; no install/full-build fallback')
        save();print(receipt['status']);return 78
    if args.source_dir is None:
        receipt.update(status='BLOCKED_VERIFIED_SOURCE_DIR_REQUIRED');save();return 78
    manifest=json.loads((ROOT/'SOURCE_BINDING.json').read_text());receipt['source_commit']=manifest['pinned_commit']
    version=run([rustc,'--version','--verbose'],timeout=10)
    receipt['compiler_version']=version.stdout.decode(errors='replace')
    sources={}
    try:
        for path,expected in manifest['input_sha256'].items():
            if digest((ROOT/path).read_bytes())!=expected:raise ValueError('INPUT_IDENTITY_MISMATCH:'+path)
        receipt['input_files_verified']=True
        for path,sha in manifest['minimal_native_source_blobs'].items():
            source_path=args.source_dir/Path(path).relative_to('rust/rei_microphysics')
            original_bytes=source_path.read_bytes()
            if git_blob(original_bytes)!=sha:raise ValueError('SOURCE_BLOB_MISMATCH:'+path)
            sources[Path(path).name]=original_bytes
        receipt['source_acquisition']='Existing exact bytes materialized from immutable Git source; six Git blobs reverified. No fabricated repository/commit.'
        receipt['source_directory']=str(args.source_dir.resolve())
        receipt['source_blobs_verified']=True
        receipt['source_sha256']={k:digest(b) for k,b in sources.items()}
        lib=sources.pop('lib.rs').decode('utf-8')
        start=lib.index('#[derive(Debug, Clone)]\npub struct State')
        marker='impl std::error::Error for ForwardError {}'
        end=lib.index(marker,start)+len(marker)
        original_types=lib[start:end]
        header='#![forbid(unsafe_code)]\n#![allow(dead_code, unused_imports)]\nmod atomic_provider;\nmod group_rates;\nmod homogeneous_rates;\nmod hhe_events;\npub mod flrw_three_equations;\npub use atomic_provider::*;\npub use group_rates::*;\npub use homogeneous_rates::*;\npub use hhe_events::*;\n'
        root_bytes=(header+original_types+'\ninclude!("driver.rs");\n').encode()
        driver=(ROOT/'native/driver.rs').read_bytes();receipt['driver_sha256']=digest(driver);receipt['minimal_root_sha256']=digest(root_bytes)
        with tempfile.TemporaryDirectory(prefix='rei_flrw06_') as tmp:
            tmp=Path(tmp)
            for name,b in sources.items():(tmp/name).write_bytes(b)
            (tmp/'main.rs').write_bytes(root_bytes);(tmp/'driver.rs').write_bytes(driver)
            cmd=[rustc,'--edition=2021','--crate-name','rei_flrw06_native_probe',str(tmp/'main.rs'),'-o',str(tmp/'probe')]
            cp=run(cmd);receipt['compile_command']=cmd;receipt['compile_exit']=cp.returncode
            (args.output/'compile_stdout.log').write_bytes(cp.stdout);(args.output/'compile_stderr.log').write_bytes(cp.stderr)
            if cp.returncode:receipt['status']='BLOCKED_NATIVE_COMPILE';save();return 2
            data=json.loads((ROOT/'inputs/CASES.json').read_text());stdin=stdin_payload(data).encode()
            (args.output/'native_stdin.txt').write_bytes(stdin);receipt['stdin_sha256']=digest(stdin)
            receipt['binary_sha256']=digest((tmp/'probe').read_bytes())
            shutil.copyfile(tmp/'probe',args.output/'native_probe')
            receipt['retained_binary']=str((args.output/'native_probe').resolve())
            result=run([str(tmp/'probe')],input=stdin);receipt['run_exit']=result.returncode
            (args.output/'native_stdout.jsonl').write_bytes(result.stdout);(args.output/'native_stderr.log').write_bytes(result.stderr)
            receipt['stdout_sha256']=digest(result.stdout)
            if result.returncode:receipt['status']='NATIVE_RUN_FAILED';save();return 2
            records=[json.loads(line) for line in result.stdout.decode().splitlines()]
            receipt['native_calls']=len(records)
            evidence_gate(receipt)
            receipt['comparison']=validate_records(records,data,json.loads((ROOT/'results/NODE_REFERENCE_80DIGIT.json').read_text()))
            receipt['status']='NATIVE_EVENT_PHOTON_POINTWISE_REGRESSION_PASS'
            receipt['claim_ceiling']='Original public functions in a minimal crate interface; not full-crate integration, expanding history, U-consumer, physical or interval admission'
            save();print(receipt['status']);return 0
    except (ValueError,OSError,subprocess.TimeoutExpired) as e:
        receipt.update(status='BLOCKED_OR_FAILED',error=str(e));save();print(str(e),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
