"""Finite throughput campaign using the pinned native ParallelExecution pool."""
import experiment as e
import json,time,os,statistics
from pathlib import Path
start=time.monotonic();rows=[];binary=e.W/'target_baseline/release/lrs_batch';cpus=','.join(map(str,sorted(os.sched_getaffinity(0))[:4]))
for width in [1,2,4]:
 for sample in ['warm',0,1,2]:
  if time.monotonic()-start>90:raise RuntimeError('total batch campaign cap')
  name=f'batch_v3_w{width}_{sample}';parent=e.run(name,['timeout','-k','2s','90s',binary,e.CAND,e.E/name/'children',str(width),cpus],90)
  data=json.loads((parent/'children/batch.json').read_text());checks=[]
  for mode in ['fixed','birth','disabled']:
   a=json.loads((e.E/f'baseline_{mode}/raw.json').read_text());b=json.loads((parent/f'children/{mode}/raw.json').read_text());issues=e.compare(a,b);checks.append({'mode':mode,'issues':issues})
   if issues:raise RuntimeError('batch numerical mismatch')
  rows.append({'width':width,'sample':sample,'batch':data,'comparisons':checks});(e.E/'batch_samples.json').write_text(json.dumps(rows,indent=2))
summary={str(w):{'median_batch_wall_s':statistics.median(r['batch']['wall_s'] for r in rows if r['width']==w and r['sample']!='warm'),'all_batch_wall_s':[r['batch']['wall_s'] for r in rows if r['width']==w and r['sample']!='warm']} for w in [1,2,4]}
(e.E/'BATCH_SUMMARY.json').write_text(json.dumps({'jobs':3,'width4_effective_max':3,'pool':'pinned VigilODE ParallelExecution','settings':summary,'campaign_wall_s':time.monotonic()-start,'admission':'ROOT_PENDING'},indent=2));print('BATCH COMPLETE',flush=True)
