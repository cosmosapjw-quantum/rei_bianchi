"""Verify sealed E13C3 evidence; optional recomputation is new correction only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import os


def write(path,data):
    with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False) as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno());tmp=f.name
    os.replace(tmp,path)


def main(root,out,recompute):
    root,out=root.resolve(),out.resolve()
    if out.is_relative_to(root):
        raise ValueError('output must be outside immutable package')
    out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((root/'FILE_MANIFEST.json').read_text())
    files=manifest['files']
    for item in files:
        path=root/item['path']
        if path.stat().st_size!=item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('sealed payload mismatch: '+item['path'])
    commands=[]
    def run(argv,label):
        command=[sys.executable,'-B',*map(str,argv)]
        result=subprocess.run(command,cwd=root,capture_output=True,text=True)
        (out/(label+'.stdout')).write_text(result.stdout)
        (out/(label+'.stderr')).write_text(result.stderr)
        commands.append({'command':command,'actual_exit_code':result.returncode,'label':label})
        if result.returncode:
            write(out/'FIRST_FAILURE.json',{'label':label,'command':command,'exit_code':result.returncode,
                  'classification':'UNCLASSIFIED_REQUIRES_DIAGNOSIS','old_reference_rerun':False})
            raise RuntimeError('command failed: '+label)
    run([root/'code/verify_correction.py','--root',root,'--stage','final',
         '--output',out/'SAVED_EVIDENCE_VERIFICATION.json'],'saved_evidence')
    if recompute:
        # Never call an E13C2 solve, oracle, native receiver, or gas advancement.
        for stage in ('local','paths'):
            for order in (8,12):
                run([root/'code/exponential_correction.py','--root',root,'--stage',stage,
                     '--order',order,'--output',out/f'{stage}_gl{order}'],f'{stage}_gl{order}')
        run([root/'code/kernel_checks.py','--root',root,'--output',out/'KERNEL_CHECKS.json'],'kernel_checks')
    write(out/'REPRODUCTION_RESULT.json',{'status':'PASS_SCOPED','payload_files_verified':len(files),
          'recomputed_new_primary_correction_only':recompute,'old_continuous_recomputations':0,
          'old_oracle_recomputations':0,'new_gas_steps':0,'commands':commands,
          'verdict_scope':'sealed payload identity and published saved-evidence acceptance only',
          'new_output_parity_checked':False,
          'new_output_accuracy_verdict':'NOT_EVALUATED',
          'note':'optional recomputation records execution/internal checks and retains outputs; it is not a fresh parity or accuracy decision'})
    print(json.dumps({'status':'PASS_SCOPED','verdict_scope':'saved evidence only',
                      'new_output_parity_checked':False,'payload_files_verified':len(files),'commands':len(commands)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args()
    main(args.root,args.output,args.recompute)
