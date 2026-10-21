"""One bounded interleaved batch-throughput diagnostic; no scientific admission."""
import json,os,time,statistics
import experiment as e
binary=e.W/'target_baseline/release/lrs_batch'
cpus=','.join(map(str,sorted(os.sched_getaffinity(0))[:4]))
order=[1,2,4,4,1,2,2,4,1]
start=time.monotonic();deadline=start+40.;runs=[]
identity={'batch_binary_sha256':e.sha(binary),'case_binary_sha256':e.sha(e.CAND),'cpu_slots':cpus,'width_order':order,'total_cap_s':40,'warmups':'reuse prior successful width warmups','comparisons':'deferred until all timed batches finish'}
(e.E/'INTERLEAVED_BATCH_IDENTITY.json').write_text(json.dumps(identity,indent=2))
for index,width in enumerate(order):
 remaining=deadline-time.monotonic()
 if remaining<2.:raise RuntimeError('interleaved total budget exhausted')
 cap=min(30.,remaining-1.)
 name=f'batch_interleaved_{index}_w{width}'
 parent=e.run(name,['timeout','-k','0.5s',f'{cap:.3f}s',binary,e.CAND,e.E/name/'children',str(width),cpus],min(remaining,cap+0.75))
 # The batch process writes its own observed whole-batch wall. Do not parse large raw outputs here.
 runs.append({'index':index,'width':width,'directory':str(parent)})
measured_campaign_wall=time.monotonic()-start
for row in runs:
 parent=e.E/f"batch_interleaved_{row['index']}_w{row['width']}"
 row['batch']=json.loads((parent/'children/batch.json').read_text())
 row['comparisons']=[]
 for mode in ['fixed','birth','disabled']:
  reference=json.loads((e.E/f'baseline_{mode}/raw.json').read_text())
  actual=json.loads((parent/f'children/{mode}/raw.json').read_text())
  issues=e.compare(reference,actual)
  row['comparisons'].append({'mode':mode,'issues':issues})
  if issues:
   (e.E/'interleaved_batch_samples.json').write_text(json.dumps(runs,indent=2))
   raise RuntimeError('interleaved numerical mismatch')
(e.E/'interleaved_batch_samples.json').write_text(json.dumps(runs,indent=2))
summary={}
for width in [1,2,4]:
 xs=[r['batch']['wall_s'] for r in runs if r['width']==width]
 summary[str(width)]={'samples_s':xs,'median_s':statistics.median(xs),'range_s':[min(xs),max(xs)]}
median1=summary['1']['median_s']
result={'identity':identity,'settings':summary,'median_ratio_1_over_2':median1/summary['2']['median_s'],'median_ratio_1_over_4':median1/summary['4']['median_s'],'jobs':3,'width4_effective_max':3,'measured_campaign_wall_s':measured_campaign_wall,'all27_children_completed_and_numerically_equal':True,'scientific_admission':'ROOT_PENDING','stopping_rule':'one interleaved diagnostic; no further repeats'}
(e.E/'INTERLEAVED_BATCH_SUMMARY.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
