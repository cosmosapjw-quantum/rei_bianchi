"""Build isolated pinned backend; preserve observed stage logs and provenance."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=REPO/'research/r31ao_unequal_ladder'
SCRATCH=Path('/workspace/scratch/6cf5f59cd2d1/native_execution_build')
PINS={
 'gmp':('C09.tar.xz','gmp-6.3.0','6.3.0','a3c2b80201b89e68616f4ad30bc66aee4927c3ce50e33929ca819d5c43538898',2094196),
 'mpfr':('C08.tar.xz','mpfr-4.2.2','4.2.2','b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01',1505596),
 'flint':('C01.tar.gz','flint-2b0788802abf62ec29d8e4a8f917993606e517e0','3.4.0','108ab51a4dd33918ff3308f0c63a63616ae30a2c174d50c9188676e85011346f',8702721)}
MEMORY=1024**3
FLAGS='-O2 -fno-fast-math -ffp-contract=off'

def identity(path):
 path=Path(path).resolve(strict=True);h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return {'path':str(path),'sha256':h.hexdigest(),'size':path.stat().st_size}
def newjson(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def prepare():
 if SCRATCH.exists():return
 SCRATCH.mkdir()
 for name in ('sources','prefix','logs','tmp'): (SCRATCH/name).mkdir()
 for name,(archive,top,version,sha,size) in PINS.items():
  source=REPO/'backend_sources'/archive;actual=identity(source)
  if (actual['sha256'],actual['size'])!=(sha,size):raise RuntimeError('archive pin mismatch: '+name)
  dest=SCRATCH/'sources'/name;dest.mkdir()
  with tarfile.open(source) as tar:
   members=tar.getmembers();total=sum(m.size for m in members)
   if len(members)>20000 or total>256*1024**2:raise RuntimeError('archive budget')
   seen=set()
   for m in members:
    parts=Path(m.name).parts
    if not parts or parts[0]!=top or '..' in parts or m.name.startswith('/') or m.name in seen or not(m.isdir() or m.isfile()):raise RuntimeError('unsafe archive member')
    seen.add(m.name)
   for m in members:
    target=dest/m.name
    if m.isdir():target.mkdir(exist_ok=True,parents=True);continue
    target.parent.mkdir(exist_ok=True,parents=True)
    with tar.extractfile(m) as fi,target.open('xb') as fo:shutil.copyfileobj(fi,fo)
    target.chmod(0o755 if m.mode&0o111 else 0o644)
    os.utime(target,(m.mtime,m.mtime))
  newjson(dest/'ARCHIVE_IDENTITY.json',{**actual,'version':version,'original_source_unmodified':True})
def env(tools_prefix=None):
 prefix=SCRATCH/'prefix';paths=[]
 if tools_prefix:paths.append(str(Path(tools_prefix)/'bin'))
 paths+=['/usr/bin','/bin']
 result={'PATH':':'.join(paths),'LANG':'C','LC_ALL':'C','TZ':'UTC',
  'TMPDIR':str(SCRATCH/'tmp'),'CC':'/usr/bin/gcc','CXX':'/usr/bin/g++',
  'CFLAGS':FLAGS,'CXXFLAGS':FLAGS,'LD_LIBRARY_PATH':str(prefix/'lib'),
  'PKG_CONFIG_PATH':str(prefix/'lib/pkgconfig'),'PKG_CONFIG_LIBDIR':str(prefix/'lib/pkgconfig'),
  'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MAKEFLAGS':'-j2'}
 if tools_prefix:
  extra=json.loads((Path(tools_prefix)/'ENVIRONMENT.json').read_text());result.update(extra)
  result['LD_LIBRARY_PATH']=str(prefix/'lib')+':'+extra['LD_LIBRARY_PATH']
 return result
def group_rss(pgid):
 # /proc is mounted in the host PID namespace while Popen returns a child
 # namespace PID. Resolve only this Python process's own direct child first.
 parent=Path('/proc/self').resolve();children=(parent/'task'/parent.name/'children').read_text().split()
 roots=[]
 for child in children:
  try:
   status=(Path('/proc')/child/'status').read_text()
   nspid=next(line for line in status.splitlines() if line.startswith('NSpid:')).split()[1:]
   if int(nspid[-1])==pgid:roots.append(int(child))
  except (FileNotFoundError,StopIteration,ValueError,IndexError):pass
 total=0;seen=set();pending=roots
 while pending:
  pid=pending.pop()
  if pid in seen:continue
  seen.add(pid);folder=Path('/proc')/str(pid)
  try:
   text=(folder/'stat').read_text();fields=text[text.rfind(')')+2:].split()
   total+=int(fields[21])*os.sysconf('SC_PAGE_SIZE')
   pending.extend(int(s) for s in (folder/'task'/str(pid)/'children').read_text().split())
  except (FileNotFoundError,ProcessLookupError,PermissionError,IndexError,ValueError):pass
 return total
def stage(name,label,command,cwd,environment,wall=600):
 for old in sorted((SCRATCH/'logs').glob(name+'-'+label+'*/STAGE.json')):
  item=json.loads(old.read_text())
  if item['stage']==label and item['exit_code']==0 and item['reason']=='EXIT_RECORDED' and item['command']==command and item['environment']==environment:
   mismatch=[]
   for stream in ('stdout','stderr'):
    current=identity(item[stream]['path'])
    if current!=item[stream]:mismatch.append({'stream':stream,'recorded':item[stream],'readback':current})
   if mismatch:
    marker=old.parent/'READBACK_MISMATCH.json'
    if not marker.exists():
     newjson(marker,{'status':'PRIOR_STAGE_NOT_REUSABLE','root_cause':'UNRESOLVED','mismatches':mismatch})
     for entry in mismatch:shutil.copyfile(entry['readback']['path'],old.parent/(entry['stream']+'.mismatch_readback.log'))
    continue
   print(json.dumps({'library':name,'stage':label,'status':'SUCCESSFUL_STAGE_REUSED','receipt':str(old)}),flush=True)
   return item
 logdir=SCRATCH/'logs'/(name+'-'+label);attempt=1
 while logdir.exists():
  attempt+=1;logdir=SCRATCH/'logs'/(name+'-'+label+'_attempt'+str(attempt))
 logdir.mkdir(exist_ok=False)
 def limits():
  resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  resource.setrlimit(resource.RLIMIT_FSIZE,(512*1024**2,512*1024**2))
  os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-2:])
 start=time.monotonic();reason='EXIT_RECORDED'
 with (logdir/'stdout.log').open('xb') as out,(logdir/'stderr.log').open('xb') as err:
  p=subprocess.Popen(command,cwd=cwd,env=environment,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                     start_new_session=True,preexec_fn=limits)
  while p.poll() is None:
   if time.monotonic()-start>wall:reason='WALL_LIMIT';break
   if max(os.fstat(out.fileno()).st_size,os.fstat(err.fileno()).st_size)>32*1024**2:reason='LOG_LIMIT';break
   time.sleep(.2)
  if p.poll() is None:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.wait()
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
 record={'library':name,'stage':label,'command':command,'cwd':str(cwd),'environment':environment,
  'exit_code':p.returncode,'reason':reason,'wall_seconds':time.monotonic()-start,'wall_cap_seconds':wall,
  'children_maxrss_kib_process_lifetime':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
  'aggregate_rss_limit_enforced':False,'target_build_memory_budget_bytes':3*1024**3,
  'memory_limit_bytes_per_process':MEMORY,'max_make_jobs':2,'affinity_cpu_count':2,'attempt':attempt,
  'memory_scope':'1GiB address-space hard cap per process and 2 make jobs; ru_maxrss is maximum child usage, not aggregate or a delta. Prior /proc-derived observations are not applicable.',
  'stdout':identity(logdir/'stdout.log'),'stderr':identity(logdir/'stderr.log'),
  'actual_HH_runs':0,'scientific_admission':False,'production_admission':False}
 newjson(logdir/'STAGE.json',record)
 print(json.dumps({'library':name,'stage':label,'exit_code':p.returncode,'reason':reason,'wall_seconds':record['wall_seconds'],'max_child_rss_kib':record['children_maxrss_kib_process_lifetime']}),flush=True)
 if p.returncode or reason!='EXIT_RECORDED':raise RuntimeError('stage failed: '+name+'-'+label)
 return record
def build(name,tools_prefix=None):
 prepare();environment=env(tools_prefix);source=SCRATCH/'sources'/name/PINS[name][1];prefix=SCRATCH/'prefix'
 if name=='flint':
  required=['autoreconf','autoconf','automake','m4','libtoolize','pkg-config']
  missing=[x for x in required if not shutil.which(x,path=environment['PATH'])]
  if missing:raise RuntimeError('GENUINE_BOOTSTRAP_TOOLS_REQUIRED: '+','.join(missing))
  stage(name,'bootstrap',['/bin/sh','./bootstrap.sh'],source,environment,120)
 flags=['--prefix='+str(prefix),'--libdir='+str(prefix/'lib'),'--enable-shared','--disable-static']
 if name=='gmp':flags+=['--disable-assembly']
 if name=='mpfr':flags+=['--disable-maintainer-mode']
 if name in ('mpfr','flint'):flags+=['--with-gmp='+str(prefix)]
 if name=='flint':flags+=['--with-mpfr='+str(prefix),'--with-blas=no','--with-ntl=no']
 stage(name,'configure',['/bin/sh','./configure',*flags],source,environment,120)
 # Optional documentation is omitted from the generated Makefile only.
 # Neither source archive nor numerical source/header is patched. A command
 # line SUBDIRS override would incorrectly propagate into recursive make.
 if name in ('gmp','mpfr'):
  makefile=source/'Makefile';text=makefile.read_text();lines=text.splitlines(True)
  old=next(line for line in lines if line.startswith('SUBDIRS = '));parts=old.split()
  if 'doc' in parts:
   before=identity(makefile);replacement=' '.join(p for p in parts if p!='doc')+'\n'
   makefile.write_text(text.replace(old,replacement,1))
   note=SCRATCH/(name.upper()+'_OPTIONAL_DOCS_OMITTED.json')
   if not note.exists():newjson(note,{'before':before,'after':identity(makefile),'generated_line_before':old,
     'generated_line_after':replacement,'reason':'No makeinfo available; optional docs omitted. Numerical source and generated numerical headers are unchanged.'})
 stage(name,'build',['/usr/bin/make','-j2'],source,environment,1800)
 stage(name,'install',['/usr/bin/make','-j2','install'],source,environment,120)
 if name=='flint':provenance() # Prefix/build evidence available before optional longer tests.
 if name=='gmp':
  stage(name,'check-build',['/usr/bin/make','-j2','libtests.la'],source/'tests',environment,120)
  stage(name,'check-build-mpz',['/usr/bin/make','-j2','t-addsub','t-mul','t-tdiv'],source/'tests/mpz',environment,120)
  for test in ('t-addsub','t-mul','t-tdiv'):stage(name,'check-'+test,['./'+test],source/'tests/mpz',environment,60)
 elif name=='mpfr':
  stage(name,'check-build',['/usr/bin/make','-j2','tadd','tmul','texp','tsqrt','tconst_pi'],source/'tests',environment,180)
  for test in ('tadd','tmul','texp','tsqrt','tconst_pi'):stage(name,'check-'+test,['./'+test],source/'tests',environment,90)
 else:
  stage(name,'check',['/usr/bin/make','-j2','check','MOD=arb acb acb_hypgeom acb_calc'],source,environment,900)
 newjson(SCRATCH/(name.upper()+'_BUILD_COMPLETE.json'),{'library':name,'version':PINS[name][2],
  'binary':identity(prefix/'lib'/('lib'+name+'.so')),'scientific_admission':False,'production_admission':False})
def provenance():
 compiler={**identity('/usr/bin/gcc'),'version':subprocess.run(['/usr/bin/gcc','--version'],capture_output=True,text=True,check=True).stdout}
 record={'verified_build_provenance':True,'compatibility_assertion_only':True,'prefix':str(SCRATCH/'prefix'),
  'compiler':compiler,'libraries':{},'execution_witness':'Observed bounded build stages in this session; independent historical admission not implied.',
  'gmp_assembly_disabled':True,'native_library_builds_observed':True,'actual_HH_runs':0}
 for name,(archive,top,version,sha,size) in PINS.items():
  binary=identity(SCRATCH/'prefix/lib'/('lib'+name+'.so'));logs=[];failures=[];selected={}
  for p in sorted((SCRATCH/'logs').glob(name+'-*/STAGE.json')):
   item=json.loads(p.read_text())
   if item['exit_code'] or item['reason']!='EXIT_RECORDED' or (p.parent/'READBACK_MISMATCH.json').exists():
    failures.append({'receipt':identity(p),'exit_code':item['exit_code'],
       'reason':'READBACK_MISMATCH' if (p.parent/'READBACK_MISMATCH.json').exists() else item['reason']});continue
   label=item['stage'];attempt=item.get('attempt',1)
   candidate={'stage':label,**identity(p),'exit_code':0,'stdout':item['stdout'],'stderr':item['stderr']}
   if label in selected:
    old_attempt,old=selected[label]
    if attempt>old_attempt:
     failures.append({'receipt':old,'reason':'SUCCESSFUL_STAGE_SUPERSEDED'});selected[label]=(attempt,candidate)
    else:failures.append({'receipt':candidate,'reason':'SUCCESSFUL_STAGE_SUPERSEDED'})
   else:selected[label]=(attempt,candidate)
  logs=[v[1] for k,v in sorted(selected.items())]
  if len(logs)>20:raise RuntimeError('provenance stage cap')
  record['libraries'][name]={'version':version,'source_archive_path':str(REPO/'backend_sources'/archive),
   'source_archive_sha256':sha,'binary_path':binary['path'],'binary_sha256':binary['sha256'],
   'compiler':compiler,'flags':FLAGS.split(),'abi':{'machine':platform.machine(),'system':platform.system(),'format':'ELF'},
   'build_logs':logs,'build_log_sha256':next(l['sha256'] for l in logs if l['stage']=='build'),
   'prior_attempt_records_preserved':failures}
 out=SCRATCH/'BACKEND_BUILD_PROVENANCE.json';newjson(out,record)
 gatepath=BASE/'host_synthetic_readiness_20261001_v1/provenance_gate.py'
 spec=importlib.util.spec_from_file_location('built_backend_gate',gatepath);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
 checked=gate.verify_backend(out,SCRATCH/'prefix');newjson(SCRATCH/'BACKEND_BYTE_CHAIN_VERIFIED.json',checked['verification'])
 print(json.dumps({'status':checked['verification']['status'],'provenance':str(out)}),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','gmp','mpfr','flint','provenance']);parser.add_argument('--tools-prefix')
 parser.add_argument('--work-root',type=Path,default=SCRATCH);args=parser.parse_args()
 if not args.work_root.is_absolute() or args.work_root in (Path('/'),Path('/usr'),Path('/opt')):raise SystemExit('explicit safe absolute work root required')
 SCRATCH=args.work_root.resolve()
 try:
  if args.stage=='prepare':prepare()
  elif args.stage=='provenance':provenance()
  else:build(args.stage,args.tools_prefix)
 except Exception as exc:
  print('BUILD_REFUSED: '+str(exc),file=sys.stderr);raise SystemExit(2)
