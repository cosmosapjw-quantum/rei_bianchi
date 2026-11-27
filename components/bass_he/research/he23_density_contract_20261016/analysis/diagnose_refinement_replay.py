import sys,json,math
from pathlib import Path
sys.path.insert(0,'/root/BASS_HE_HE23_DENSITY_20261016/research/he23_density_contract_20261016/src')
from he22_coupled import run_coupled
from he22_native_client import parse_native_point
w=Path('/root/HE23_NCP_DENSITY_20261016');raw=w/'refinement/raw_m4_n8'
records=[json.loads(p.read_text()) for p in sorted(raw.glob('*_rhs.json'))];index=0
nh_by_a={}
for p in raw.glob('*_density.json'):
 r=json.loads(p.read_text());f=dict(x.split('\t') for x in r['stdout'].splitlines()[1:]);nh_by_a[float(f['A'])]=float(f['NH_CM3'])
def density(a,x):return nh_by_a[a]
def factory(a,x):
 def owner(g,gr,power):
  global index
  r=records[index];index+=1
  args=[format(float(v),'.17e') for v in (a,*g,*gr,*power)]
  assert args==r['argv'][1:],('replay input drift',index)
  return parse_native_point(r['stdout'],density(a,x))
 return owner
def trace(frame,event,arg):
 if event=='exception' and frame.f_code.co_name=='solve_midpoint' and str(arg[1])=='HE22_TOTAL_ENERGY_LEDGER_FAIL':
  v=frame.f_locals
  def clean(x):
   if hasattr(x,'tolist'):return x.tolist()
   if isinstance(x,(float,int,str)):return x
   return repr(x)
  keys=['gas0','g','nh','dt','err','k','calls','total_energy','physical_scale','du','db','escaped','cmb','e_after']
  data={k:clean(v[k]) for k in keys}
  data.update(acceptance_limit=max(3e-11*v['physical_scale'],2e-12*abs(v['g'][3])),scope='exact input-matched saved-native-output diagnostic replay; zero new native calls')
  (w/'REFINEMENT_FIRST_FAILURE_DIAGNOSIS.json').write_text(json.dumps(data,indent=2))
 return trace
sys.settrace(trace)
try:run_coupled(factory,m=4,steps=8,q=0.,density_provider=density)
except AssertionError as e:print('reproduced from',index,'saved RHS outputs:',e)
finally:sys.settrace(None)
print((w/'REFINEMENT_FIRST_FAILURE_DIAGNOSIS.json').read_text())
