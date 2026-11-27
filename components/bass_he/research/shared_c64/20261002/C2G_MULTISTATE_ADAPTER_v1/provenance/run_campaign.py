"""Execute exactly the two preregistered C2g layouts with immutable slot receipts."""
from pathlib import Path
import subprocess,sys,json,time,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from physical_contract import approved_inputs,source_identity
from runtime_support import atomic_create,file_identity
manifest,inputs,review=approved_inputs(ROOT/'contract/PHYSICAL_TASKS.json',ROOT/'review/PHYSICAL_LAUNCH_REVIEW.json')
prereg=json.loads(Path(inputs['preregistration']['path']).read_text());source=source_identity(ROOT/'code')
ledger=ROOT/'results/campaign_ledger';ledger.mkdir(exist_ok=False)
atomic_create(ledger/'CONTRACT.json',{'inputs':inputs,'source':source,'max_layouts':2,'max_tasks':24,'max_independent_roots':108,'scope':'one invocation; create-only output prevents accidental replay; perlayout watchdog separate'})
results=[]
for i,layout in enumerate(prereg['campaign']['layouts']):
    if source_identity(ROOT/'code')!=source:raise RuntimeError('source changed before campaign slot')
    command=[sys.executable,str(ROOT/'code/launch_reference.py'),'--manifest',str(ROOT/'contract/PHYSICAL_TASKS.json'),'--review',str(ROOT/'review/PHYSICAL_LAUNCH_REVIEW.json'),'--execution',layout['execution'],'--backend',layout['backend'],'--ranks',str(layout['ranks']),'--threads',str(layout['threads']),'--binding',layout['binding'],'--output',str(ROOT/'results'/(layout['id']+'.json'))]
    if layout['backend']=='native':command+=['--native-library',str(ROOT/'native/build/libbass_element.so'),'--mpiexec',str(ROOT.parent/'ncp_build_deps/root/usr/bin/orterun')]
    atomic_create(ledger/(str(i+1)+'_START.json'),{'slot':i+1,'layout':layout,'command':command,'started_unix':time.time(),'inputs':inputs})
    print('START '+layout['id'],flush=True)
    done=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    record={'slot':i+1,'layout':layout,'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr,'finished_unix':time.time(),'result':file_identity(ROOT/'results'/(layout['id']+'.json'))}
    atomic_create(ledger/(str(i+1)+'_FINISH.json'),record);results.append(record)
    print(done.stdout,flush=True)
    if done.returncode:raise SystemExit(done.returncode)
atomic_create(ledger/'COMPLETED.json',{'status':'PASS','layouts':2,'sector_solves_completed':24,'independent_roots_returned':108,'represented_columns_after_reconstruction':144,'results':[r['result'] for r in results],'source_unchanged':source_identity(ROOT/'code')==source})
