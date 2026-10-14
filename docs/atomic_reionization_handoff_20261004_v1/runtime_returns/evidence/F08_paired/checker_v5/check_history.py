from pathlib import Path
import json,sys,time,hashlib,copy,pickle,os
import independent_radiation as rad
import independent_reporting as point
root=Path(sys.argv[1]);stream='--stream' in sys.argv[2:];start=time.monotonic();total=0;results=[]
def records(file,directory):
 while True:
  offset=file.tell();line=file.readline()
  if line.endswith('\n'):yield line;continue
  file.seek(offset)
  if not stream or (directory/'summary.json').exists():
   assert not line,'INCOMPLETE_DURABLE_RECORD';break
  time.sleep(.1)
for hp in ([root/'header.jsonl'] if (root/'header.jsonl').exists() else sorted(root.glob('*/header.jsonl'))):
 header=json.loads(hp.read_text());geometry=header['geometry'];h={'FLRW':[1e-14]*3,'BI':[1.01e-14,.99e-14,1e-14],'EPS_HALF':[1.005e-14,.995e-14,1e-14]}[geometry];s=rad.initial(header);p=point.initial(header);accepted=rejected=0;dt=header['dt_initial'];maxima={'local':0.,'width':0.,'q':0.,'point_ledger':0.}
 prefix=hp.parent/'independent_prefix.pkl';source_hashes={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [Path(__file__),Path(__file__).with_name('independent_radiation.py'),Path(__file__).with_name('independent_stage.py'),Path(__file__).with_name('independent_reporting.py')]};offset=0;hasher=hashlib.sha256()
 if prefix.exists():
  cached=pickle.loads(prefix.read_bytes());assert cached['source_hashes']==source_hashes,'PROOF_CHECKER_SOURCE_CHANGED';assert cached['header']==header,'PROOF_HEADER_CHANGED'
  offset=cached['offset'];s=cached['radiation'];p=cached['point'];accepted=cached['accepted'];rejected=cached['rejected'];dt=cached['dt'];maxima=cached['maxima'];total+=accepted
  with (hp.parent/'trials.jsonl').open('rb') as existing:
   while existing.tell()<offset:
    hasher.update(existing.read(min(1024*1024,offset-existing.tell())))
  assert hasher.hexdigest()==cached['raw_prefix_sha256'],'PROVEN_PREFIX_CHANGED'
 with (hp.parent/'trials.jsonl').open() as file:
  file.seek(offset)
  for lineno,line in enumerate(records(file,hp.parent),1):
   hasher.update(line.encode());row=json.loads(line);assert row['dt_s']==min(dt,1e13-s.time),'ADAPTIVE_SCHEDULE'
   if not row['accepted']:assert row['time_s']==s.time;dt=row['dt_s']/2;rejected+=1;continue
   accepted+=1;assert row['accepted_index']==accepted
   s,proof=rad.trial(header,h,s,row);p,ledger=point.trial(header,h,p,row);assert s.time==row['time_s']==p.time
   for k,v in {**proof,'point_ledger':ledger}.items():maxima[k]=max(maxima[k],v)
   for i,b in enumerate(row['gas_parent']):assert rad.inside(b,s.gas[i]),'REPORTED_PARENT_BINDING'
   total+=1
   if accepted%100==0:
    cached={'schema':'F08_PROVEN_PREFIX_V1','source_hashes':source_hashes,'header':header,'offset':file.tell(),'radiation':s,'point':p,'accepted':accepted,'rejected':rejected,'dt':dt,'maxima':maxima,'raw_prefix_sha256':hasher.hexdigest()};temp=prefix.with_suffix('.tmp');temp.write_bytes(pickle.dumps(cached,protocol=5));os.replace(temp,prefix)
    print(json.dumps({'validated':total,'run':hp.parent.name,'time':s.time,'maxima':maxima,'proven_prefix_saved':accepted}),flush=True)
 summary=json.loads((hp.parent/'summary.json').read_text());assert summary['accepted']==accepted and summary['rejected']==rejected;point.report(header,h,p,summary)
 offset=point.checkpoint(header,p,hp.parent/'checkpoint.dat',accepted,rejected);assert offset==(hp.parent/'trials.jsonl').stat().st_size,'CHECKPOINT_LOG_OFFSET'
 residual=point.cumulative(header,p)
 for key,v in zip(['cumulative_n_residual','cumulative_u_residual'],residual):point.close(summary[key],v,1.,key)
 if summary['status']=='COMPLETE_HISTORY_CANDIDATE':assert s.time==1e13 and max(residual)<=1e-12,'WHOLE_FINAL_LEDGER'
 else:assert summary['status']=='PILOT_ONLY'
 results.append({'run':hp.parent.name,'time_s':s.time,'accepted':accepted,'rejected':rejected,'maxima':maxima,'cumulative':residual,'raw_sha256':hashlib.sha256((hp.parent/'trials.jsonl').read_bytes()).hexdigest()})
 print(json.dumps(results[-1]),flush=True)
result={'status':'WHOLE_HISTORY_COMPONENT_INDEPENDENT_PASS' if results and all(r['time_s']==1e13 for r in results) else 'FINITE_COMPOSITE_OUTPUT_EVENT_INDEPENDENT_PASS','trials':total,'runs':results,'wall_s':time.monotonic()-start,'production_evaluator_called':False,'scientific_admission':'HOLD'};(root/'independent_history_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
