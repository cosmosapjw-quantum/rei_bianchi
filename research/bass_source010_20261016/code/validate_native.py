import csv,json,math,hashlib,statistics,collections
from pathlib import Path
r=Path('/root/REI_BASS_SOURCE010_20261016_001');c=json.loads((r/'CONTRACT.json').read_text());terminal=json.loads((r/'raw/CONTROLLER_TERMINAL.json').read_text());dest=r/'compact';dest.mkdir(exist_ok=False);summ={};manifest=[]
def require(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p,role):
 digest=hashlib.sha256()
 with p.open('rb') as f:
  def lines():
   for l in f:digest.update(l);yield l.decode()
  yield from csv.DictReader(lines())
 manifest.append({'path':str(p),'role':role,'sha256':digest.hexdigest(),'bytes':p.stat().st_size})
def fields(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
for ex in terminal['executions']:
 case=ex['case'];out=r/'results'/case;t=fields(out/'RETURN.txt') if (out/'RETURN.txt').exists() else {};checks={};hist=[];headtail=collections.deque(maxlen=3);first=[];step=[];counts={};ledgers={};ledfail=[]
 for row in rows(out/'history.csv','history'):
  require(row['case_id']==case,'CASE');nums={k:float(v) for k,v in row.items() if k!='case_id'};require(all(math.isfinite(v) for v in nums.values()),'NONFINITE_HISTORY');require(nums['a']>0 and nums['nH_proper_cm3']>0,'HISTORY_DOMAIN');require(all(0<=nums[k]<=1 for k in ['x_HI','x_HII','x_HeI','x_HeII','x_HeIII']),'FRACTION_DOMAIN')
  if hist:require(nums['a']>hist[-1][0] and nums['time_s']>hist[-1][1],'CLOCK_ORDER');step.append(math.log(nums['a']/hist[-1][0]))
  hist.append((nums['a'],nums['time_s'],nums['temperature_K']));headtail.append(row)
  if len(first)<3:first.append(row)
 counts['history']=len(hist);require(hist[0][1]==0,'OWN_TIME_ORIGIN')
 idx=0;group=[];zero={k:0 for k in ['H_I','H_II','He_I','He_II','He_III','electron']}
 for row in rows(out/'abundances.csv','abundances'):
  group.append(row)
  if len(group)<6:continue
  require(idx<len(hist),'EXCESS_ABUNDANCES');require([x['species_id'] for x in group]==list(zero),'SPECIES_GROUP');require(all(x['run_id']==case and float(x['time_s'])==hist[idx][1] and float(x['Tgas_K'])==hist[idx][2] and x['normalization_registry']=='BASELINE_H_HE_CHARGE_AND_BARYON_V1' for x in group),'ABUNDANCE_ALIGNMENT')
  for x in group:
   y=float(x['Ybaryon']);require(math.isfinite(y) and y>=0,'Y_DOMAIN');zero[x['species_id']]+=y==0
  idx+=1;group=[]
 require(not group and idx==len(hist),'ABUNDANCE_COUNT');counts['abundances']=idx*6
 n=0
 for row in rows(out/'ledgers.csv','ledgers'):
  n+=1;v=float(row['residual']);require(math.isfinite(v),'NONFINITE_LEDGER');item=ledgers.setdefault(row['ledger_name'],{'status_counts':{},'max_abs':0,'max_ratio_to_own_native_tolerance':None,'last_value':None});item['status_counts'][row['status']]=item['status_counts'].get(row['status'],0)+1;item['max_abs']=max(item['max_abs'],abs(v));item['last_value']=v
  if row['status']=='PASS':
   tol=float(row['tolerance']);require(tol>=0 and math.isfinite(tol),'NATIVE_TOLERANCE');ratio=abs(v)/tol if tol else 0 if v==0 else float('inf');item['max_ratio_to_own_native_tolerance']=max(item['max_ratio_to_own_native_tolerance'] or 0,ratio)
   if abs(v)>tol:ledfail.append({'row':n,'kind':'PASS_OUTSIDE_NATIVE_TOLERANCE'})
  elif row['status']!='VALUE':ledfail.append({'row':n,'kind':row['status']})
 counts['ledgers']=n;require(not ledfail,'RECORDED_NATIVE_LEDGER_FAILURE')
 for name in ['spectra.csv','feedback.csv']:
  n=0
  for row in rows(out/name,name):
   n+=1;require(row['case_id']==case,'TABLE_CASE')
   for k,v in row.items():
    if k!='case_id':require(math.isfinite(float(v)),'NONFINITE_TABLE')
  counts[name]=n
 checks.update(history_equals_accepted_plus_initial=len(hist)==int(t['accepted'])+1 if 'accepted' in t else None,abundances_six=len(hist)*6==counts['abundances'],ledger31=len(hist)*31==counts['ledgers'],source_match=sha(out/'source_identity.txt')==c['compiled_source_sha256'],counter_caps=int(t['accepted'])<=90000 and int(t['attempts'])<=300000 and int(t['rhs_evaluations'])<=3000000 if 'accepted' in t else None,mode=t.get('inactive_hi_split')=='true' if t else None)
 cp=Path(t['last_checkpoint']) if t.get('last_checkpoint') else max((out/'checkpoints').glob('*.bass-v1'),key=lambda p:p.stat().st_mtime_ns);text=cp.read_text();h,body=text.split('\nAXBI_CHECKPOINT_V4\n',1);prefix=h.splitlines();body='AXBI_CHECKPOINT_V4\n'+body;bl=body.splitlines();state=list(map(float,bl[1].split()));counters=list(map(int,bl[2].split()));arr=[list(map(float,l.split())) for l in bl[4:10]];binding=out/'RUN_BINDING.txt'
 rb=fields(binding);expected_cfg=sha(r/'configs'/(case+'.cfg'));checks.update(run_binding_config=rb.get('config_text_sha256')==expected_cfg,run_binding_source=rb.get('source009_sha256')==c['compiled_source_sha256'],run_binding_inputs=rb.get('csv_sha256')==c['inputs'][1]['sha256'] and rb.get('producer_json_sha256')==c['inputs'][2]['sha256'],run_binding_case=rb.get('case')==case and rb.get('grid_points')=='121',run_binding_mode=rb.get('inactive_hi_split')=='true' and rb.get('resume')=='false',run_binding_epoch=rb.get('epoch')=='source010-half-target-001-'+case,cp_config_debug=prefix[5]==rb.get('config_debug_sha256'),max_newton_native=float(t['max_newton_residual'])<=1e-11 if 'max_newton_residual' in t else None,last_error_strict_ceiling=float(t['last_error'])<2e-4 if 'last_error' in t else None);checks.update(cp_source=prefix[4]==c['compiled_source_sha256'],cp_mode='inactive_hi_split=true' in prefix[2],cp_case=case in prefix[1],cp_body_hash=prefix[9]==hashlib.sha256(body.encode()).hexdigest(),cp_body_bytes=int(prefix[10])==len(body.encode()),cp_binding_sha=prefix[7]==sha(binding),cp_state=(state[0]==hist[-1][0] and state[1]==hist[-1][1]) if t else None,cp_matches_a_saved_state=any(state[0]==a and state[1]==time for a,time,temp in hist),cp_counters=(counters[0]==int(t['accepted']) and counters[1]==int(t['attempts']) and counters[4]==int(t['rhs_evaluations'])) if 'accepted' in t else None,cp_sixarrays=len(arr)==6 and len(set(map(len,arr)))==1 and all(math.isfinite(v) and v>=0 for a in arr for v in a))
 require(all(v is not False for v in checks.values()),'NATIVE_COUNT_IDENTITY_CHECK_FAILED')
 with (dest/(case+'_history_head_tail.csv')).open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=first[0]);w.writeheader();w.writerows(first+list(headtail))
 for name in ['RETURN.txt','RUN_BINDING.txt','source_identity.txt','transport_variant.txt']:(dest/(case+'_'+name)).write_bytes((out/name).read_bytes())
 dist={'count':len(step),'min':min(step),'max':max(step),'median':statistics.median(step),'mean':statistics.mean(step),'q10':sorted(step)[int(.1*(len(step)-1))],'q90':sorted(step)[int(.9*(len(step)-1))],'definition':'actual log(a[i]/a[i-1]) saved accepted intervals; controller target ratio does not fix dt ratio'}
 summ[case]={'status':'NATIVE_COMPLETE_PENDING_REVIEW' if ex['status']=='NATIVE_COMPLETE_PENDING_REVIEW' else 'PARTIAL_ONLY','execution':ex,'native_terminal':t,'missing_terminal_reason':None if t else 'NOT_RECORDED_EXTERNAL_STOP; last durable checkpoint is not a terminal receipt and its counters do not account for later charged work','counts':counts,'checks':checks,'native_ledger_observations':ledgers,'failures':ledfail,'coverage':{'first_a':hist[0][0],'last_a':hist[-1][0],'first_z':1/hist[0][0]-1,'last_z':1/hist[-1][0]-1,'first_elapsed_s':hist[0][1],'last_elapsed_s':hist[-1][1],'complete':ex['status']=='NATIVE_COMPLETE_PENDING_REVIEW'},'accepted_interval_distribution':dist,'zero_counts':zero,'checkpoint':{'path':str(cp),'sha256':sha(cp),'six_array_lengths':list(map(len,arr)),'compiled_source':prefix[4],'is_terminal':bool(t.get('last_checkpoint')),'last_durable_counters':counters,'config_debug_sha256':prefix[5],'epoch':prefix[6]},'files':list(manifest[-5:])}
 for p in out.rglob('*'):
  if p.is_file() and str(p) not in {x['path'] for x in manifest}:manifest.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
(dest/'NATIVE_SUMMARIES.json').write_text(json.dumps(summ,indent=2,allow_nan=False)+'\n');(dest/'FULL_RAW_MANIFEST.json').write_text(json.dumps({'files':manifest},indent=2)+'\n');print(json.dumps({'status':'NATIVE_VALIDATION_ONCE_COMPLETE','cases':{k:v['counts'] for k,v in summ.items()}}))
