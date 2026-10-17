#!/usr/bin/env python3
"""One frozen bounded native PRIMAT execution; never edits provider source."""
import argparse, hashlib, json, math, os, pathlib, shutil, signal, subprocess, tarfile, time
ROOT = pathlib.Path(__file__).resolve().parents[2]
PIN = '4bf97d5082eee54b9df50d88f43182bb651fea80'

def verify(provider, manifest):
    checked = []
    for item in manifest['files']:
        p = provider / item['path']; content = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        sha = hashlib.sha256(content).hexdigest()
        if blob != item['git_blob_sha'] or sha != item['sha256'] or len(content) != item['bytes']:
            raise ValueError('immutable source identity mismatch: ' + item['path'])
        checked.append({'path':item['path'], 'git_blob_sha':blob, 'sha256':sha})
    if manifest['commit'] != PIN: raise ValueError('source commit mismatch')
    return checked

def command(exe, provider, cache, precision='1e-7', n=None, prefix=None):
    args = [str(exe),'--data_dir',str(provider/'primat/data'),'--network','small','--Omegabh2','0.02205','--DeltaNeff','0','--numerical_precision',precision]
    for param in ['Omegach2=0.12495','h=0.7','tau_n=878.4','std_tau_n=0.5','T_end_MeV=0.001','decay_era=False','strict_params=True','mc_rate_rescale_cap=30','show_progress=False',"cache_dir='"+str(cache)+"'"]:
        args += ['--set',param]
    args += ['--json']
    if n is not None:
        args += ['--mc',str(n),'--mc-seed','20261016','--mc-jobs','1','--output_mc_samples','--output_mc_covariance','--output_mc_correlation','--output_mc_file_prefix',str(prefix)]
    return args

def invoke(args, cwd, out, label, timeout):
    record = {'label':label,'command':args,'cwd':str(cwd),'timeout_s':timeout}
    start = time.monotonic()
    with (out/(label+'.stdout')).open('wb') as stdout, (out/(label+'.stderr')).open('wb') as stderr:
        p = subprocess.Popen(args,cwd=cwd,stdout=stdout,stderr=stderr,start_new_session=True)
        try:
            record['returncode'] = p.wait(timeout=timeout); record['timed_out']=False
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGKILL); p.wait(); record['returncode']=p.returncode; record['timed_out']=True
    record['wall_s'] = time.monotonic()-start
    return record

def selected(d):
    return [d[k] if k in d else d['Y_final'][k] for k in ['YPBBN','DoH','He3oH','Li7oH','Be7','Li7']]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--provider-root',default=os.environ.get('UNIT8_PRIMAT_PROVIDER_ROOT')); ap.add_argument('--prepare-only',action='store_true'); a=ap.parse_args()
    out=ROOT/'evidence/laneD_raw'; out.mkdir(exist_ok=True,parents=True)
    inputs=ROOT/'inputs/laneD'; inputs.mkdir(exist_ok=True,parents=True)
    manifest=json.loads((ROOT/'intake/PRIMAT_DOWNLOAD_MANIFEST.json').read_text())
    provider=pathlib.Path(a.provider_root).resolve() if a.provider_root else ROOT.parent/'u8_primat_provider'
    backup=inputs/'primat_source_4bf97d5082ee.tar.gz'
    if not provider.exists() and backup.exists():
        provider=inputs/'provider'; provider.mkdir(exist_ok=True)
        with tarfile.open(backup,'r:gz') as tf: tf.extractall(provider,filter='data')
    checked=verify(provider,manifest)
    (out/'source_verification.json').write_text(json.dumps({'commit':PIN,'verified_count':len(checked),'files':checked},indent=2)+'\n')
    shutil.copy2(ROOT/'intake/PRIMAT_DOWNLOAD_MANIFEST.json',inputs/'PRIMAT_DOWNLOAD_MANIFEST.json')
    if not backup.exists():
        with tarfile.open(backup,'w:gz') as tf:
            for item in manifest['files']: tf.add(provider/item['path'],arcname=item['path'],recursive=False)
    for name in ['COPYING','LICENCE','CITATION.cff']: shutil.copy2(provider/name,inputs/name)
    shutil.copy2(provider/'primat/data/nuclear/networks/small.txt', inputs/'small.txt')
    if a.prepare_only: print(json.dumps({'prepared':True,'verified_files':len(checked),'backup':str(backup)})); return
    receipt=out/'execution_receipt.json'
    if receipt.exists(): raise SystemExit('Frozen execution already attempted; inspect receipt, no reruns authorized.')
    records=[]; report={'commit':PIN,'provider_root':str(provider),'verified_files':len(checked),'build_budget_s':30,'numerical_budget_s':30,'seed':20261016,'jobs':1,'records':records,'status':'STARTED'}
    def save(): receipt.write_text(json.dumps(report,indent=2)+'\n')
    def fail(reason): report['status']=reason; save(); print(json.dumps(report)); return
    save()
    rec=invoke(['make','-j2'],provider/'primat-c',out,'build',30); records.append(rec); save()
    if rec['returncode'] != 0: return fail('BUILD_FAILED_RETURN_TO_AUTHORITY')
    exe=provider/'primat-c/build/primat-c'; cache=inputs/'cache_overlay'; cache.mkdir(exist_ok=True)
    used=0
    for label,precision in [('nominal','1e-7'),('tight','1e-8')]:
        rec=invoke(command(exe,provider,cache,precision),provider/'primat-c',out,label,min(5,30-used)); records.append(rec); used+=rec['wall_s']; report['numerical_wall_s']=used; save()
        if rec['returncode'] != 0: return fail(label.upper()+'_FAILED_RETURN_TO_AUTHORITY')
    nominal=selected(json.loads((out/'nominal.stdout').read_text())); tight=selected(json.loads((out/'tight.stdout').read_text()))
    rel=[abs(x-y)/abs(x) for x,y in zip(nominal,tight)]; report['central_relative_error']=rel
    if max(rel)>1e-4: return fail('CENTRAL_PRECISION_FAILED_RETURN_TO_AUTHORITY')
    rec=invoke(command(exe,provider,cache,n=8,prefix=out/'pilot'),provider/'primat-c',out,'pilot',max(.01,30-used)); records.append(rec); used+=rec['wall_s']; report['numerical_wall_s']=used; save()
    if rec['returncode'] != 0: return fail('PILOT_FAILED_RETURN_TO_AUTHORITY')
    report['valid_samples']=8; report['result_prefix']='pilot'; remaining=30-used
    candidates=[n for n in [64,32,16] if 1.5*rec['wall_s']*(n+2)/10 <= remaining-2]
    report['production_selection']={'pilot_wall_s':rec['wall_s'],'remaining_s':remaining,'candidates_fitting':candidates,'formula':'1.5*t8*(N+2)/10 <= remaining-2'}
    if candidates:
        n=candidates[0]; rec=invoke(command(exe,provider,cache,n=n,prefix=out/'production'),provider/'primat-c',out,'production',max(.01,30-used)); records.append(rec); used+=rec['wall_s']; report['numerical_wall_s']=used
        if rec['returncode']==0: report['valid_samples']=n; report['result_prefix']='production'; report['status']='EXECUTED_PENDING_ANALYSIS'
        elif rec['timed_out']: report['status']='BUDGET_LIMITED'
        else: report['status']='PRODUCTION_FAILED_RETURN_TO_AUTHORITY'
    else: report['status']='BUDGET_LIMITED'
    save(); print(json.dumps(report))
if __name__=='__main__': main()
