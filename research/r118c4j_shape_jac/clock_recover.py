"""Recover completed CF4 results from the emitted rows and saved native-precision states."""
import ast,re,json,time,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
s=(D/'clock.py').read_text();g={'__file__':str(D/'clock.py'),'__name__':'recovery'}
exec(compile(s[:s.index('rows=[];vals={}')],str(D/'clock.py'),'exec'),g)
I=g['I'];rel=g['rel'];floor=g['floor'];grid=g['grid'];tau=g['tau']
raw=(D/'clock.log').read_text();assert 'Object of type longdouble is not JSON serializable' in raw
rows=[ast.literal_eval(re.sub(r'np\.float(?:64|128)\(([^()]*)\)',r'\1',x)) for x in raw.splitlines() if x.startswith("{'dim':")]
assert len(rows)==8 and {(r['dim'],r['tol']) for r in rows}=={(d,t) for d in (48,147) for t in (1e-6,1e-8,1e-10,1e-12)}
p=D/'ADAPTIVE_CF4.npz'
with np.load(p) as a:
 assert np.array_equal(a['ref'],g['ref'])
 for r in rows:
  k=0 if r['dim']==48 else 2;t=r['tol'];v=a[f'{k}_{t:g}'];assert np.all(np.isfinite(v))
  assert np.allclose(rel(v,a['ref']),r['reference_relative'],rtol=1e-12,atol=1e-20)
  if k==0:r['matched_tolerance_hierarchy_gap']=rel(v,a[f'2_{t:g}']).tolist()
  assert r['max_accepted_ratio']<=1 and r['exponential_actions']==6*r['trial_steps']
z=dict(rows=rows,clock_sha=hashlib.sha256((I/'CLOCK_CF4.npz').read_bytes()).hexdigest(),reference_steps=json.loads((I/'CLOCK_CF4.json').read_text())['reference_steps'],source_intervals=len(grid)-1,tau=float(tau[-1]),scale_floor=[float(x) for x in floor],scope='actual C4I prescribed REC opacity/BASS shear; CF4 step doubling 1/15; knot-aligned, finite reference scaling; reduced 48 vs full lmax6; no rigorous global certificate or full self-consistent REI',recovery=dict(method='all eight completed rows parsed with literal_eval; independently recalculated terminal errors and hierarchy gaps from saved NPZ; no recomputation or substitution of numerical integrations',original_log_sha256=hashlib.sha256(raw.encode()).hexdigest(),state_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(D/'ADAPTIVE_CF4.json').write_text(json.dumps(z,indent=2,allow_nan=False)+'\n')
print('RECOVERED',len(rows),'rows; saved state errors independently matched')
