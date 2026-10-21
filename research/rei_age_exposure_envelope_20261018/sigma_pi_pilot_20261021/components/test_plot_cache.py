"""Single targeted read-cache identity/call regression; no IVP or benchmark."""
import sys,time,copy,json
from pathlib import Path
sys.dont_write_bytecode=True
begin=time.monotonic();sys.path.insert(0,str(Path(__file__).resolve().parent))
import plot_extension as p
c=next(c for c in p.u.component_cases() if 'reuse' not in c and not c['config']['guard'])
p.READ_CACHE.clear();calls=[];verify=p.verified_plot_path
p.verified_plot_path=lambda case,epoch:calls.append((case['id'],epoch)) or verify(case,epoch)
a=p.read(c,4);b=p.read(c,4)
checks={'verified_load_once':len(calls)==1,'same_immutable_data':a is b and all(not v.flags.writeable for v in a.values()),'bounded_cache':p.READ_CACHE_MAX==512 and len(p.READ_CACHE)==1}
try:a['P_m']=None;checks['mapping_immutable']=False
except TypeError:checks['mapping_immutable']=True
bad=copy.deepcopy(c);bad['config']['calibration']['massive_A']+=.001
try:p.read(bad,4);checks['changed_config_rejected']=False
except ValueError as e:checks['changed_config_rejected']='CONFIG_IDENTITY_MISMATCH' in str(e)
p.verified_plot_path=verify
r={'checks':checks,'pass':all(checks.values()),'elapsed_s':time.monotonic()-begin,'no_IVP_calls':True,'no_benchmark':True,'plot_source_sha256':p.u.sha(p.__file__)}
p.u.atomic_json(p.u.ROOT/'components/PLOT_CACHE_MECHANICAL.json',r)
print(json.dumps(r,indent=2));sys.exit(0 if r['pass'] else 1)
