"""Extract only rustc/rust-std components into a chosen scratch directory."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('archive');parser.add_argument('destination')
    args=parser.parse_args()
    dest=Path(args.destination);dest.mkdir(parents=True,exist_ok=True)
    files=0;bytes_out=0
    with tarfile.open(args.archive,mode='r|xz') as archive:
        for member in archive:
            parts=Path(member.name).parts
            if len(parts)<3:continue
            component=parts[1]
            if component!='rustc' and not component.startswith('rust-std-'):continue
            rel=Path(*parts[2:])
            if rel.parts[0] not in ('bin','lib'):continue
            target=dest/rel
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True,exist_ok=True)
                with archive.extractfile(member) as source,target.open('wb') as output:
                    shutil.copyfileobj(source,output)
                target.chmod(member.mode);files+=1;bytes_out+=member.size
            elif member.issym():
                target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():os.symlink(member.linkname,target)
    rustc=dest/'bin/rustc'
    version=subprocess.run([str(rustc),'--version','--verbose'],check=True,capture_output=True,text=True)
    probe=dest/'probe.rs';probe.write_text('fn main(){println!("RUST_PASS");}\n')
    compile_result=subprocess.run([str(rustc),str(probe),'--edition=2021','-C','codegen-units=1','-C','link-arg=-Wl,--threads=1','-o',str(dest/'probe')],capture_output=True,text=True)
    run=None
    if compile_result.returncode==0:
        run=subprocess.run([str(dest/'probe')],capture_output=True,text=True)
    status='RUST_PASS' if run is not None and run.returncode==0 else 'EXECUTION_FAILED'
    out={'status':status,'rustc':str(rustc),'version':version.stdout,'compile_exit':compile_result.returncode,
         'compile_stderr':compile_result.stderr,'probe_stdout':run.stdout if run else None,
         'extracted_files':files,'extracted_bytes':bytes_out,
         'scope':'scratch-only compiler and standard library; no systemwide install or old suite replay'}
    Path(__file__).with_name('TOOLCHAIN_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    if status!='RUST_PASS':raise SystemExit(1)

if __name__=='__main__':main()
