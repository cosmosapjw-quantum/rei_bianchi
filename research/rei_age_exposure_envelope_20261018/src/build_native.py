"""Compile only the prepared research example; never invoke a physical campaign."""
from pathlib import Path
import argparse,os,shutil,subprocess,time
from run_refinement import read_json,sha,save,run_process

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',required=True,type=Path)
    p.add_argument('--wall-s',type=float,default=300.)
    a=p.parse_args();root=a.prepared.resolve();identity=read_json(root/'PREPARED_IDENTITY.json')
    for n,h in identity['outputs'].items():
        if sha(root/n)!=h: raise ValueError('PREPARED_SOURCE_CHANGED: '+n)
    binary=root/'rust/rei_microphysics/target/release/examples/positive_native'
    receipt=root/'BUILD_RECEIPT.json'
    if receipt.exists():
        old=read_json(receipt)
        if old.get('exit_code')==0 and binary.is_file() and old['binary_sha256']==sha(binary) and old['prepared_identity_sha256']==sha(root/'PREPARED_IDENTITY.json'):
            print('VERIFIED_BUILD_REUSED');return
        raise RuntimeError('PRIOR_BUILD_NOT_REUSABLE: preserve it; prepare a new scratch')
    cargo=shutil.which('cargo')
    if cargo is None:
        c=Path.home()/'.cargo/bin/cargo'
        if c.is_file():cargo=str(c)
    if cargo is None:raise FileNotFoundError('CARGO_UNAVAILABLE')
    os.environ['CARGO_BUILD_JOBS']='2'
    result=run_process([cargo,'build','--offline','--release','--manifest-path',str(root/'rust/rei_microphysics/Cargo.toml'),'--example','positive_native','-j','2'],root/'build_logs',a.wall_s)
    result['prepared_identity_sha256']=sha(root/'PREPARED_IDENTITY.json')
    result['cargo_version']=subprocess.check_output([cargo,'--version'],text=True).strip()
    result['binary_sha256']=sha(binary) if result['exit_code']==0 else None
    changed=[n for n,h in identity['outputs'].items() if sha(root/n)!=h]
    result['changed_prepared_sources']=changed
    save(receipt,result)
    if result['exit_code'] or changed:raise RuntimeError('BUILD_FAILED_OR_SOURCE_CHANGED; raw logs retained')
    print('NATIVE_EXAMPLE_COMPILED; PHYSICS_NOT_RUN')
if __name__=='__main__':main()
