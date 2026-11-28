"""Prepare registered dependent work from verified completed state records."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path('/workspace/scratch/0b54847633d9/BASS_HE_C2C_SMALL_R_SCALED_20261001_v1')
sys.path.insert(0,str(ROOT/'code'))
from analyze_states import documents,state_ref,audit_states
from mpi_batch import atomic_create,json_bytes
c=json.loads((ROOT/'CONTRACT.json').read_bytes());docs=documents();audit=audit_states(docs,c)
assert audit['all_new_R_numerical_gates_pass'], audit['unresolved_R']
selected={float(k):v for k,v in audit['selected_states'].items()}
folder=ROOT/'frozen/R0p25_base';r=json.loads((folder/'RESULT.json').read_bytes())
selected[.25]={'folder':str(folder.relative_to(ROOT)),'state_sha256':r['state_sha256'],'result_sha256':hashlib.sha256((folder/'RESULT.json').read_bytes()).hexdigest()}
tasks=[]
for level in ('l72','l96'):
 pair=[next(d for d in docs if d['task_id']==f'sphere_R0p125_{level}_m{m}') for m in (0,1)]
 tasks.append({'task_id':'observe_'+level,'parameters':{'kind':'sphere_observe','label':level,'left':state_ref(pair[0]),'right':state_ref(pair[1]),'orders':c['spherical_anchor']['operator_orders']}})
for i,(left,right) in enumerate(c['continuation']['edges']):
 for m in (0,1):
  for q in c['continuation']['orders']:
   tasks.append({'task_id':f'edge{i}_m{m}_q{q}','parameters':{'kind':'overlap','left':selected[left],'right':selected[right],'sector':m,'order':q}})
for i,case in enumerate(c['parity_cases']):
 params={'kind':'parity','case':case,'index':i}
 if case['kind']=='overlap':params.update(left=selected[case['edge'][0]],right=selected[case['edge'][1]])
 else:params['state']=selected[case['R']]
 tasks.append({'task_id':f'parity_{i}','parameters':params})
manifest={'schema':1,'limits':{'per_worker_memory_gib':1.5,'task_wall_seconds':240},'tasks':tasks}
atomic_create(ROOT/'inputs/FOLLOWUP_TASKS.json',json_bytes(manifest))
print(json.dumps({'tasks':len(tasks),'selected':selected},indent=2))
