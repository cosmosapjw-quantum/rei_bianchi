"""Verify this new AXBI execution only, not historical AX08 admission."""
import argparse,gzip,hashlib,json,re,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;repo=D.parents[1];home=Path.home()/'Downloads'
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(n):return json.loads((D/n).read_text())
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
r=load('RESULTS.json');l=load('LONG_AUDIT.json');donor=load('DONOR_SUMMARY.json')
assert len(r['cases'])==12 and all(c['status']=='PASS_SCOPED' and c['max_ledger_ratio']<=1 for c in r['cases'])
assert sum(c['accepted'] for c in r['cases'])==6654
assert l['status']=='PASS_SCOPED' and l['accepted']==58116 and l['history_rows']==58117 and l['terminal']['zbar']==4 and l['max_ledger_ratio']<=1
assert r['binary_sha256']==l['binary_sha256']
assert r['donor_sha256']==l['donor_sha256']==donor['full_donor_sha256']
assert sha(D/'REC_q0_long.cfg')==l['config_sha256']
for name,n in [('rei_cargo',273),('rei_examples',18)]:
    text=gzip.decompress((D/f'logs/r118c2g_{name}.log.gz').read_bytes()).decode()
    counts=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',text)
    assert counts and sum(int(x[1]) for x in counts)==n and sum(int(x[2]) for x in counts)==0
paths=['configs/rei_fastest_v1/science_scenario_v1.json','docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json']
for path in paths:
    old=subprocess.check_output(['git','-C',str(repo),'show','fef2baf960f5:'+path])
    assert hashlib.sha256(old).hexdigest()==sha(repo/path)
if a.raw:
    assert sha(home/'rec_r118c2g_boundary/normal.json')==r['donor_sha256']
    assert sha(Path(r['cases'][0]['command'][0]))==r['binary_sha256']
    root=home/'rei_r118c2g_owned_final'
    for c in r['cases']:
        assert sha(root/(c['case']+'.cfg'))==c['config_sha256']
        for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
    root=home/'rei_r118c2g_owned_long'
    for f,h in l['hashes'].items():assert sha(root/f)==h
print('PASS_SCOPED 12 short + 1 long native histories; 273 Rust + 18 example tests; exact legacy fixtures')
