#!/usr/bin/env python3
"""Build reference and candidate side by side; never install into the scientific runtime."""
from pathlib import Path
import argparse,hashlib,json,platform,subprocess
ROOT=Path(__file__).resolve().parents[1]
FLAGS=['-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fopenmp']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    manifest=json.loads((ROOT/'evidence/BASELINE_SOURCE_MANIFEST.json').read_text())
    for name,h in manifest.items():
        if name.startswith('native/reference/') and sha(ROOT/name)!=h:raise ValueError(f'frozen source changed: {name}')
    compiler=subprocess.run(['g++','--version'],check=True,capture_output=True,text=True).stdout
    files={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native').rglob('*') if p.is_file()}
    identity=dict(compiler=compiler,flags=FLAGS,sources=files,platform=platform.platform())
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    folder=ROOT/'build'/key;folder.mkdir(parents=True,exist_ok=True)
    receipt=folder/'BUILD.json'
    if receipt.exists():
        r=json.loads(receipt.read_text())
        for lane,v in r['libraries'].items():
            if sha(Path(v['path']))!=v['sha256']:raise ValueError('cached binary changed')
        return r
    libs={}
    for lane in ('reference','candidate'):
        cpp=ROOT/'native'/lane/'r31a/hybrid12_wide_h_v2.cpp';so=folder/(lane+'.so')
        report=folder/(lane+'_vectorization.txt')
        cmd=['g++',*FLAGS,f'-fopt-info-vec-all={report}',str(cpp),'-o',str(so)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
        (folder/(lane+'_compile.stdout')).write_text(p.stdout);(folder/(lane+'_compile.stderr')).write_text(p.stderr)
        if p.returncode:raise RuntimeError(f'build failed: {p.stderr}')
        libs[lane]=dict(path=str(so),sha256=sha(so),command=cmd,vectorization_report=str(report))
    r=dict(identity=identity,build_key=key,libraries=libs,scientific_runtime_mutation=False)
    with receipt.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
