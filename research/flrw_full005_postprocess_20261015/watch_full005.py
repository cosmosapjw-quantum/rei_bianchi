#!/usr/bin/env python3
"""One create-only completion watcher. No solver, restart, push or admission."""
import csv,datetime,hashlib,json,os,resource,shlex,subprocess,sys,tarfile,time,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent
RUN=BASE/'AUTO_FULL005_001'
REMOTE='/root/REI_FLRW_COVARIANT_20261015_005/full_campaign001'
CASES=['FLRW_FULL_Q512_001','FLRW_FULL_Q1024_001']
RECORD=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/execution/NCP_ACCESS_RECOVERY_20261014.json')
DROPBOX=Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912')
NEEDED=['history.csv','abundances.csv','ledgers.csv','config.cfg','source_identity.txt','RETURN.txt','checkpoint.txt']
CAP_MEMORY=8*1024**3
CAP_POST_S=300
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ssh_args():
    saved=json.loads(RECORD.read_text());cmd=shlex.split(saved['command']);identity=cmd[cmd.index('-i')+1]
    return ['ssh','-T','-i',identity,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ControlMaster=no','-o','ControlPath=none','-p','22',saved['user']+'@'+saved['host']]
def remote(code,timeout=40,output=None):
    command=ssh_args()+['python3 -c '+shlex.quote(code)]
    with (RUN/'SSH_PRIVATE_STDERR.log').open('ab') as err:
        if output:
            with output.open('xb') as f:
                r=subprocess.run(command,stdout=f,stderr=err,timeout=timeout)
            if r.returncode:raise RuntimeError('REMOTE_COLLECTION_NONZERO')
            return None
        r=subprocess.run(command,stdout=subprocess.PIPE,stderr=err,timeout=timeout)
    if r.returncode:raise RuntimeError('REMOTE_READONLY_PROBE_NONZERO')
    return json.loads(r.stdout)
def probe():
    code="import json,pathlib; p=pathlib.Path("+repr(REMOTE)+"); cases="+repr(CASES)+"; read=lambda x:json.loads(x.read_text()) if x.is_file() else None; print(json.dumps({'epoch':read(p/'campaign_epoch.json'),'status':read(p/'full_campaign.status.json'),'terminal':read(p/'full_campaign.receipt.json'),'case_receipts':{c:read(p/'launches'/(c+'.receipt.json')) for c in cases}}))"
    return remote(code)
def completed(receipt):
    if not receipt or receipt.get('returncode')!=0 or not receipt.get('native_completion_proof') or not receipt.get('source_config_binary_bindings_match'):return False
    n=receipt.get('native_return') or {}
    try:return n.get('status')=='COMPLETE_REPRESENTED_INTERVAL' and float(n.get('a','nan'))==.2 and n.get('result')=='Ok(())'
    except (TypeError,ValueError):return False
def measure_command(command,deadline,name):
    remaining=min(CAP_POST_S,deadline-time.monotonic())
    if remaining<=0:raise RuntimeError('POSTPROCESS_300S_CAP')
    def bound():resource.setrlimit(resource.RLIMIT_AS,(CAP_MEMORY,CAP_MEMORY))
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    start=time.monotonic()
    with (RUN/(name+'.log')).open('xb') as f:
        child=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,cwd=BASE,preexec_fn=bound,env=env)
        try:code=child.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait()
            raise RuntimeError('POSTPROCESS_300S_CAP')
    return {'command':command,'returncode':code,'wall_s':time.monotonic()-start,'address_space_limit_bytes':CAP_MEMORY,'child_peak_rss_bytes_linux_so_far':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024}
def collect(deadline):
    names=[]
    for c in CASES:
        names.extend(['runs/'+c+'/'+n for n in NEEDED]);names.extend(['launches/'+c+'.binding.json','launches/'+c+'.receipt.json'])
    names+=['campaign_epoch.json','full_campaign.receipt.json','full_resource_plan.json']
    code="import pathlib,tarfile,sys; p=pathlib.Path("+repr(REMOTE)+"); names="+repr(names)+"; assert all((p/n).is_file() for n in names); t=tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz'); [(t.add(p/n,arcname=n,recursive=False)) for n in names]; t.close()"
    target=RUN/'completed_pair_declared_inputs.tar.gz'
    remote(code,timeout=max(1,deadline-time.time()),output=target)
    dest=RUN/'inputs';dest.mkdir()
    with tarfile.open(target) as t:t.extractall(dest,filter='data')
    write(RUN/'COLLECTION_RECEIPT.json',{'status':'DECLARED_COMPLETED_INPUTS_COLLECTED','archive':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'declared_members':names,'source005_mutations':0,'solver_runs':0,'cloud_backup':'NOT_CLAIMED_BY_COLLECTION'})
    return dest
def package(status):
    (RUN/'POSTPROCESS_STATUS_REPORT.md').write_text('# Completion-driven postprocessing status\n\n'+status['status']+'\n\nDiagnostic only; no scientific admission. Native source/jobs unchanged.\n')
    write(RUN/'FINAL_STATUS.json',status)
    files=[]
    for p in RUN.rglob('*'):
        if not p.is_file() or 'inputs' in p.relative_to(RUN).parts or p.name in {'completed_pair_declared_inputs.tar.gz','SSH_PRIVATE_STDERR.log'}:continue
        files.append((p,'postprocess/'+str(p.relative_to(RUN))))
    for p in [BASE/'postprocess_flrw.py',BASE/'watch_full005.py',BASE/'REUSE_PROVENANCE.json',BASE/'README_KO.md',BASE/'TASK_PACKET.json',*sorted((BASE/'vendor').glob('*.py')),*sorted((BASE/'contracts').glob('*.md'))]:
        if p.is_file():files.append((p,'runnable/'+str(p.relative_to(BASE))))
    archive=DROPBOX/'REI_FLRW_FULL005_POSTPROCESS_20261015_AUTO001.zip'
    if archive.exists():raise RuntimeError('UNIQUE_REPORT_ZIP_ALREADY_EXISTS_NO_OVERWRITE')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p,name in files:z.write(p,name)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('REPORT_ZIP_CRC_FAILURE')
    write(RUN/'REPORT_PACKAGE_RECEIPT.json',{'status':'OWNER_DROPBOX_UNIQUE_REPORT_ZIP_CREATED_READBACK_PASS_CLOUD_SYNC_NOT_INDEPENDENTLY_VERIFIED','archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'members':len(files),'scientific_admission':'NOT_ISSUED','solver_runs':0,'git_mutations':0,'source005_mutations':0})
def main():
    resource.setrlimit(resource.RLIMIT_AS,(CAP_MEMORY,CAP_MEMORY))
    RUN.mkdir(exist_ok=False)
    frozen=json.loads((BASE/'FULL005_EPOCH.json').read_text())
    hard_deadline=float(frozen['deadline_epoch'])+3600
    write(RUN/'WATCHER_PID.json',{'pid':os.getpid(),'started_utc':now(),'native_deadline_epoch':frozen['deadline_epoch'],'postprocess_hard_deadline_epoch':hard_deadline,'hard_rule':'FIRST_NATIVE_DEADLINE_PLUS_1H_NO_NATIVE_EXTENSION','native_source_identity_sha256':'1a2268e3da98ed47159cb738762a1a3d3d17bdcb6806e611cbd2bc3c0c6eaff7'})
    status={'status':'WATCHING_ACTUAL_FULL005_COMPLETION','started_utc':now(),'solver_runs':0,'scientific_admission':'NOT_ISSUED','D_cosmological_activation':'NOT_ACTIVATED_NOT_PLOTTED','native_campaign_extended':False}
    try:
        errors=0
        while time.time()<hard_deadline-15:
            try:
                state=probe()
                if state['epoch']!=frozen:raise RuntimeError('NATIVE_EPOCH_CHANGED_NO_RESET_ALLOWED')
                write(RUN/'LATEST_READONLY_STATUS.json',state)
                got=state['case_receipts']
                write(RUN/'WATCHER_STATUS.json',{**status,'observed_utc':now(),'probe_errors':errors,'completed_cases':[c for c in CASES if completed(got.get(c))],'remaining_seconds_to_hard_deadline':hard_deadline-time.time()})
                if all(completed(got.get(c)) for c in CASES):
                    status['completed_terminal_receipts']=got
                    source=collect(hard_deadline-15)
                    counts=[int(got[c]['native_return']['accepted'])+1 for c in CASES]
                    estimate=512*sum(counts)+512*1024**2
                    status['memory_planning']={'history_rows':counts,'conservative_working_estimate_bytes':estimate,'estimate_rule':'512bytes/row for both cases plus512MiB plotting/base; estimate not measuredRSS','enforced_AS_bytes':CAP_MEMORY}
                    if estimate>6*1024**3:raise RuntimeError('POSTPROCESS_HISTORY_SIZE_ESTIMATE_EXCEEDS_OWNER_HEADROOM')
                    post_deadline=time.monotonic()+min(CAP_POST_S,hard_deadline-time.time()-15)
                    command=[sys.executable,str(BASE/'postprocess_flrw.py'),'bind','--mode','FULL_PAIR','--end-zbar','4','--output',str(RUN/'full_pair_manifest.json')]
                    for c in CASES:command+=['--case',c+','+str(source/'runs'/c)+','+str(source/'launches'/(c+'.binding.json'))]
                    bind=measure_command(command,post_deadline,'bind')
                    status['bind']=bind
                    if bind['returncode']:raise RuntimeError('COMPLETED_BINDING_INPUT_CHECK_FAILED')
                    render=measure_command([sys.executable,str(BASE/'postprocess_flrw.py'),'render','--manifest',str(RUN/'full_pair_manifest.json'),'--output',str(RUN/'figures_and_diagnostics')],post_deadline,'render')
                    status['render']=render
                    receipt=RUN/'figures_and_diagnostics/POSTPROCESS_RECEIPT.json'
                    if render['returncode'] or not receipt.is_file():raise RuntimeError('POSTPROCESS_DID_NOT_COMPLETE')
                    result=json.loads(receipt.read_text())
                    if result['status']!='CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING':raise RuntimeError('POSTPROCESS_GATE_HELD '+str(result.get('wait_reason')))
                    status.update(status='COMPLETED_ACTUAL_FULL_PAIR_DIAGNOSTICS_PENDING_INDEPENDENT_REVIEW',completed_utc=now(),postprocess_receipt=str(receipt))
                    package(status);return
                if state['terminal'] is not None:
                    status.update(status='NATIVE_PAIR_FAILED_OR_INCOMPLETE_NO_FULL_PLOTS',terminal=state['terminal'],observed_utc=now());package(status);return
            except (subprocess.TimeoutExpired,subprocess.SubprocessError,RuntimeError,json.JSONDecodeError) as e:
                if isinstance(e,RuntimeError) and str(e) not in {'REMOTE_READONLY_PROBE_NONZERO'}:raise
                errors+=1;write(RUN/'PROBE_ERROR_STATUS.json',{'status':'READONLY_PROBE_UNAVAILABLE_RETRY_WITHIN_FIXED_DEADLINE','errors':errors,'utc':now(),'details':'PrivateSSHstderr retained outside report package'})
            time.sleep(min(60,max(0,hard_deadline-time.time()-15)))
        status.update(status='FIXED_WATCH_DEADLINE_REACHED_NO_COMPLETED_PAIR_NO_FULL_PLOTS',observed_utc=now());package(status)
    except Exception as e:
        # Preserve failure metadata. Never produce a successful full report from
        # incomplete native histories or a partially rendered child.
        for p in (RUN/'figures_and_diagnostics').glob('*.png') if (RUN/'figures_and_diagnostics').exists() else []:p.unlink()
        status.update(status='CONTINUATION_FAILED_NO_FULL_PLOTS_OR_ADMISSION',error=type(e).__name__+': '+str(e),observed_utc=now())
        (RUN/'POSTPROCESS_STATUS_REPORT.md').write_text('# Postprocessing status\n\n'+status['status']+'\n\n'+status['error']+'\n\nNo full plots or scientific admission. Native jobs/source were not changed.\n')
        package(status)
if __name__=='__main__':main()
