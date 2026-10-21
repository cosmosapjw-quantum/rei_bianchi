"""Changed-risk static checks only; deliberately no IVP calls."""
import sys,time,json,hashlib
from pathlib import Path
begin=time.monotonic()
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
import numpy as np
checks={}
cases=u.component_cases();checks['175_plus_3']=len(cases)==178
checks['reuse_35']=sum('reuse' in c for c in cases)==35
checks['missing_143']=sum('reuse' not in c for c in cases)==143
checks['old_child_debit']=u.OLD_CHILD==8.778983763986616
checks['old_controller_debit']=u.OLD_CONTROLLER==2.720931695002946
for guard in (False,True):
    c=u.ad.config(0.,.0003,-.0003,guard);obj=u.ad.model(c)
    sol=u.SimpleNamespace(t=np.array([0.]),y=obj.initial_state()[:,None])
    out=u.ad.observables(obj,sol)
    checks['axes_'+str(guard)]=bool(abs(out['P_m'][0]-.0003)<=5e-12 and abs(out['P_r'][0]+.0003)<=5e-12)
    checks['cancel_not_isotropy_'+str(guard)]=not c['true_isotropy_control'] and c['initial_total_stress_cancelled']
    checks['tensor_cross_'+str(guard)]=bool(abs(out['Pi_total'][0]**2-out['Pi_m'][0]**2-out['Pi_r'][0]**2-2*out['normalized_cross'][0])<=1e-15)
try:u.ad.config(0.,1.,0.);checks['forbidden_amplitude']=False
except ValueError:checks['forbidden_amplitude']=True
# Original code/raw bytes have exact recovered identities.
source=u.ROOT.parents[4]/'recovery_backups/laneB_recovered/package'
# Resolve source through workspace to avoid reliance on publication path depth.
source=next(p for p in u.ROOT.parents if (p/'recovery_backups/laneB_recovered/package').exists())/'recovery_backups/laneB_recovered/package'
checks['immutable_originals']=all(u.sha(f)==u.sha(u.ROOT/f.relative_to(source)) for f in source.rglob('*') if f.is_file())
r={'checks':checks,'elapsed_s':time.monotonic()-begin,'prior_mechanical_s':.205,'no_IVP_calls':True,'pass':all(checks.values())}
u.atomic_json(u.ROOT/'components/MECHANICAL_TEST.json',r)
print(json.dumps(r,indent=2));sys.exit(0 if r['pass'] else 1)
