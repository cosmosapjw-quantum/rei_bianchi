import argparse,json,hashlib,gzip,re
from pathlib import Path
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((D/'REFINEMENTS.json').read_text());rows=r['cases']
assert [x['case'] for x in rows]==['base','time','spectral','angular']
assert all(x['status']=='PASS_SCOPED' and max(x['gate_ratios'].values())<=1 for x in rows)
assert [x['accepted'] for x in rows]==[58116,109995,58025,58116]
assert rows[-1]['tau_relative']<1e-12
for name,n in [('rei_cargo',275),('rei_examples',18)]:
    t=gzip.decompress((D/f'logs/r118c2h_{name}.log.gz').read_bytes()).decode()
    counts=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',t)
    assert sum(int(x[1]) for x in counts)==n and sum(int(x[2]) for x in counts)==0
if a.raw:
    assert sha(D.parents[1]/'rust/rei_microphysics/target/release/examples/axbi_reionization')==r['binary_sha256']
    for c in rows:
        for f,h in c['hashes'].items():assert sha(Path(c['raw_root'])/f)==h
print('PASS_SCOPED 3 independent long refinements + preserved base; 275 Rust + 18 examples')
