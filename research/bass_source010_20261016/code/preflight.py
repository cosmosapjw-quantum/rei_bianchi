import os,time,json,hashlib,subprocess,resource
from pathlib import Path
r=Path('/root/REI_BASS_SOURCE010_20261016_001');c=json.loads((r/'CONTRACT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for i in c['inputs']:
 p=r/'inputs'/('bass_adaptive_trial' if i['kind']=='binary' else Path(i['local_path']).name);assert sha(p)==i['sha256'],i['kind']
assert os.statvfs(r).f_bavail*os.statvfs(r).f_frsize>=10*2**30,'PRELAUNCH_DISK_LT_10GIB'
def sample():
 return {int(l.split()[0][3:]):list(map(int,l.split()[1:])) for l in Path('/proc/stat').read_text().splitlines() if l.startswith('cpu') and l.split()[0][3:].isdigit()}
a=sample();time.sleep(1);b=sample();loads=[]
for cpu in os.sched_getaffinity(0):
 delta=[y-x for x,y in zip(a[cpu],b[cpu])];loads.append((1-(delta[3]+delta[4])/max(1,sum(delta)),cpu))
loads.sort();binary=r/'inputs/bass_adaptive_trial';binary.chmod(0o755)
x=subprocess.run([str(binary)],capture_output=True,text=True,timeout=10)
assert x.returncode in [1,2] and ('usage' in (x.stdout+x.stderr).lower()),'ABI_PREFLIGHT_FAILED'
rec={'status':'ABI_AND_RESOURCE_PREFLIGHT_PASS','epoch':time.time(),'disk_free_bytes':os.statvfs(r).f_bavail*os.statvfs(r).f_frsize,'selected_cpus':[x[1] for x in loads[:2]],'sampled_cpu_busy_fractions':loads,'ABI':{'argv':[str(binary)],'exit':x.returncode,'stdout':x.stdout,'stderr':x.stderr,'physical_arguments':False},'R9':subprocess.check_output(['ps','-p','414739,414741','-o','pid,ppid,etime,pcpu,args'],text=True),'R9_latest_checkpoints':subprocess.getoutput("find /root/REI_R9_T4_SPECTRAL_20261016T001338Z_REPAIR001 -maxdepth 2 -type f -name '*checkpoint*' -printf '%T@ %p\\n' | sort -nr | head -3"),'affinity':sorted(os.sched_getaffinity(0)),'cpu_exclusivity_claim':False}
(r/'raw/PREFLIGHT.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
