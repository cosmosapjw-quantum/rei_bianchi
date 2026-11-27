"""Only a new tail extension; C1 inner basis and angular knots are preserved."""
from pathlib import Path
import time,json,resource
import numpy as np
from spheroidal_tail import solve,SpheroidalConfig
from coupling import direct,torque,invariants
from evidence_io import atomic_json,sha256
ROOT=Path(__file__).resolve().parents[1]
from parent_inputs import resolve_parent
PARENT=resolve_parent(ROOT)
out=ROOT/'evidence/PROLATE_TAIL_ONLY.json'
if out.exists():raise FileExistsError(out)
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
base_edges=1+30*np.linspace(0,1,49)**2
edges=np.r_[base_edges,np.linspace(31,41,11)[1:]]
cfg=SpheroidalConfig(radial_elements=48,angular_elements=20,radial_extent=40)
# New input-boundary failure seam, without executing an eigensolve.
try:solve(2,config=cfg,radial_edges=[1,2,1])
except ValueError:pass
else:raise AssertionError('invalid explicit grid accepted')
start=time.perf_counter();g=solve(2,m=0,config=cfg,radial_edges=edges);b=solve(2,m=1,config=cfg,radial_edges=edges)
d=direct(g,b,12);t=torque(g,b,24)
old=json.loads((PARENT/'evidence/C1_SINGLE_POINT_PILOT.json').read_text())['spheroidal'][-1]
x={'g':g.metadata(),'b':b.metadata(),'direct':d,'torque':t,'invariants':invariants(g,b,d,t),
   'tail_delta':{'energies':[abs(s.energy-old[k]['energy']) for s,k in zip((g,b),('g','b'))],'L_O_abs':abs(d['L_O_bar']-old['direct']['L_O_bar'])},
   'inner_knots_preserved_exact':bool(np.array_equal(edges[:len(base_edges)],base_edges)),
   'parent_extent':30,'new_extent':40,'elapsed_seconds':time.perf_counter()-start,
   'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
   'code_sha256':{n:sha256(Path(__file__).parent/n) for n in ('spheroidal_tail.py','coupling.py','run_prolate_tail.py')},
   'basis_tail_only_scope':True,'continuum_certificate':False}
atomic_json(out,x);print(json.dumps(x),flush=True)
