"""Frozen external validator. Generates Rust root-data, then independent MPFI proof."""
import importlib.util
import json
import math
import subprocess
from pathlib import Path
from sage.all import RealIntervalField

P=Path('.cuh/fastest-track/REI-F04-CERT');R=RealIntervalField(200)
cargo='/home/cosmosapjw/.cargo/bin/cargo';manifest='rust/rei_microphysics/Cargo.toml'
subprocess.run([cargo,'test','--manifest-path',manifest,'--test','ft03_interval','--locked'],check=True)
run=subprocess.run([cargo,'run','--quiet','--manifest-path',manifest,'--example','map_certificate','--locked'],text=True,capture_output=True,check=True)
data=json.loads(run.stdout);(P/'candidate.json').write_text(json.dumps(data,indent=2)+'\n')
s=importlib.util.spec_from_file_location('independent_checker',P/'checker.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
mf=json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text());constants=json.loads((P/'model_constants.json').read_text());model=m.Model(mf,constants)
checks=0
def contains(pair,expected):
    global checks
    assert len(pair)==2 and all(math.isfinite(v) for v in pair) and pair[0]<=pair[1]
    actual=R(float(pair[0]),float(pair[1]))
    assert actual.lower()<=expected.lower() and expected.upper()<=actual.upper(),(pair,str(expected))
    checks+=1
for site in data['sites']:
    box=site['box']; jets=site['interval_rhs']; assert len(jets)==7
    # Analytic MPFI witnesses at centre and each paired diagonal box endpoint.
    # Uniform root/J/H/Taylor proof uses MPFI's own domain evaluation below,
    # not an inference from these witnesses or production AD.
    for point in [site['center'],[v[0] for v in box],[v[1] for v in box]]:
        expected=model.rhs([R(float(v)) for v in point])
        for k in range(7):
            actual=jets[k];assert len(actual['gradient'])==7 and len(actual['hessian'])==7
            contains(actual['value'],expected[k].v)
            for i in range(7):
                contains(actual['gradient'][i],expected[k].g[i])
                assert len(actual['hessian'][i])==7
                for j in range(7):contains(actual['hessian'][i][j],expected[k].h[i,j])
result=m.check(data,mf,constants);result['production_interval_witness_checks']=checks
(P/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','witness_checks':checks,'site_q':[v['q_weighted'] for v in result['sites']],'local_bounds':result['joint_full_half_local_bounds'],'max_width':max(v['public_width'] for v in result['full_observables']+result['two_half_observables']),'claim':'Actual static prescribed FT03 map numerical domain only; physical/scientific HOLD'}))
