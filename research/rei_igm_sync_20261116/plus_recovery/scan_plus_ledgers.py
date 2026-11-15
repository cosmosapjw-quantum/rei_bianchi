"""One finite scan of the three exact +.01 ledger segments after native exit."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,math,datetime
P=Path('/home/cosmosapjw/Dropbox/bianchi/rei_ax08_plus_recovery_20261115')
O=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/runs/paired/32d11e733155')
assert json.loads((P/'RUN_TERMINAL_RECEIPT.json').read_text())['exit_code']==0
terminal_time=float((P/'SHEAR_PLUS_continuation_002/checkpoint.txt').read_text().splitlines()[1].split()[1])
cutoff=13488992847612486.0
lasttime=None;lastgroup={};stats={};segments=[];flags=[];dedup=0
def file_sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
for index,path in enumerate([O/'SHEAR_PLUS/ledgers.csv',O/'SHEAR_PLUS_continuation_001/ledgers.csv',P/'SHEAR_PLUS_continuation_002/ledgers.csv']):
 seg={'path':str(path),'sha256':file_sha(path),'bytes':path.stat().st_size,'raw_rows':0,'retained_unique_rows':0,'excluded_past_checkpoint_rows':0,'duplicate_equal_rows':0,'raw_time_range':None,'retained_time_range':None}
 with path.open() as f:
  for row in csv.DictReader(f):
   seg['raw_rows']+=1;t=float(row['time_s']);name=row['ledger_name'];status=row['status']
   assert row['case_id']=='SHEAR_PLUS'
   if seg['raw_time_range'] is None:seg['raw_time_range']=[t,t]
   seg['raw_time_range'][1]=t
   if index==1 and t>cutoff:seg['excluded_past_checkpoint_rows']+=1;continue
   if not math.isfinite(t):raise RuntimeError('NONFINITE_CLOCK')
   if lasttime is not None and t<lasttime:raise RuntimeError('NONMONOTONE_SEGMENT_CLOCK')
   if t==lasttime and name in lastgroup:
    assert row==lastgroup[name],('DUPLICATE_KEY_DIFFERENT_VALUES',index,t,name)
    seg['duplicate_equal_rows']+=1;dedup+=1;continue
   if t!=lasttime:lastgroup={};lasttime=t
   lastgroup[name]=row;seg['retained_unique_rows']+=1
   if seg['retained_time_range'] is None:seg['retained_time_range']=[t,t]
   seg['retained_time_range'][1]=t
   st=stats.setdefault(name,{'rows':0,'status_counts':Counter(),'finite_positive_tolerance_rows':0,'zero_tolerance_rows':0,'max_abs_residual_over_tolerance':None,'nonfinite_rows':0,'informational_nonnumeric_rows':0,'control_failures':0})
   st['rows']+=1;st['status_counts'][status]+=1
   if status not in ['PASS','VALUE']:
    st['control_failures']+=1
    if len(flags)<50:flags.append({'type':'CONTROL_STATUS','name':name,'time_s':t,'status':status})
   try:res=float(row['residual'])
   except ValueError:
    if status=='VALUE':st['informational_nonnumeric_rows']+=1;continue
    st['control_failures']+=1
    if len(flags)<50:flags.append({'type':'CONTROL_NONNUMERIC_RESIDUAL','name':name,'time_s':t})
    continue
   if not math.isfinite(res):
    st['nonfinite_rows']+=1
    if len(flags)<50:flags.append({'type':'NONFINITE_RESIDUAL','name':name,'time_s':t,'status':status})
   try:tol=float(row['tolerance'])
   except ValueError:tol=None
   if tol is not None and math.isfinite(tol) and tol>0 and math.isfinite(res):
    ratio=abs(res)/tol;st['finite_positive_tolerance_rows']+=1
    st['max_abs_residual_over_tolerance']=max(st['max_abs_residual_over_tolerance'] or 0.,ratio)
    if status=='PASS' and ratio>1:
     st['control_failures']+=1
     if len(flags)<50:flags.append({'type':'PASS_EXCEEDS_TOLERANCE','name':name,'time_s':t,'ratio':ratio})
   elif tol==0 and math.isfinite(res):
    st['zero_tolerance_rows']+=1
    if status=='PASS' and res!=0:
     st['control_failures']+=1
     if len(flags)<50:flags.append({'type':'ZERO_TOLERANCE_NONZERO_RESIDUAL','name':name,'time_s':t})
   elif status=='PASS':
    st['control_failures']+=1
    if len(flags)<50:flags.append({'type':'CONTROL_MISSING_VALID_TOLERANCE','name':name,'time_s':t})
 segments.append(seg)
assert lasttime==terminal_time,(lasttime,terminal_time)
fail=sum(x['control_failures'] for x in stats.values());nonfinite=sum(x['nonfinite_rows'] for x in stats.values())
result={'schema':'rei.axbi.plus_three_segment_ledger_scan.v1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'NO_CONTROL_FAILURE_OBSERVED' if fail==nonfinite==0 else 'FLAGS_REQUIRE_REVIEW','segments':segments,'cutoff_segment1_time_s':cutoff,'dedup_key':['time_s','ledger_name'],'duplicate_values_agree':True,'duplicates_removed':dedup,'last_ledger_time_s':lasttime,'terminal_checkpoint_time_s':terminal_time,'per_ledger':stats,'control_failures':fail,'nonfinite_rows':nonfinite,'flags':flags,'interpretation':'VALUE or blank-tolerance rows are informational, not presumed zero and not automatically failing; ratios reported only for finite residual and positive finite tolerance. No convergence claim.'}
(P/'PLUS_LEDGER_SCAN.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'control_failures':fail,'nonfinite_rows':nonfinite,'duplicates_removed':dedup,'segments':segments,'per_ledger':stats}))
