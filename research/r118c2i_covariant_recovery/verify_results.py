import argparse,gzip,hashlib,json,re,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;repo=D.parents[1]
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
r=json.loads((D/'RESULTS.json').read_text());s=json.loads((D/'RESTORATION.json').read_text())
assert s['donor']=='0e25846433170d0f420c4cda44a0bedbf02cd177'
assert len(r['cases'])==6 and sum(x['status']=='PASS_SCOPED' for x in r['cases'])==5
long=next(x for x in r['cases'] if x['case']=='long_q16')
assert long['status']=='STOPPED_CHECKPOINTED_RESOURCE' and long['accepted']==73149
assert all(max(c['gate_ratios'].values())<=1 for c in r['cases'])
assert hashlib.sha256(gzip.decompress((D/'LONG_CHECKPOINT.txt.gz').read_bytes())).hexdigest()==long['hashes']['checkpoint.txt']
for v in s['files']:
 b=subprocess.check_output(['git','-C',str(repo),'show',s['donor']+':'+v['source']])
 assert hashlib.sha256(b).hexdigest()==v['source_sha256']
 assert sha(repo/v['destination'])==v['restored_sha256'],v
for n,count in [('all',319),('examples',18)]:
 l=gzip.decompress((D/f'logs/r118c2i_rei_{n}.log.gz').read_bytes()).decode()
 ms=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',l)
 assert sum(int(x[1]) for x in ms)==count and sum(int(x[2]) for x in ms)==0
if a.raw:
 root=Path(r['root'])
 assert sha(repo/'rust/rei_microphysics/target/release/examples/axbi_covariant_recovered')==r['binary_sha256']
 assert sha(Path.home()/'Downloads/rec_r118c2g_boundary/normal.json')==r['donor_sha256']
 for c in r['cases']:
  assert sha(root/(c['case']+'.cfg'))==c['config_sha256']
  for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
print('PASS_SCOPED recovered covariant lane; five complete; one checkpointed; 319+18 tests')
