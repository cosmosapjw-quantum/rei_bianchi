#!/usr/bin/env python3
"""Restore exact native+VigilODE inputs and run the bounded research adapter.

Normal Git files suffice with the repository's committed SSPRK restoration chain.
Use --prepare-only to restore/hash-check without compiling or running physics.
Use --all only when the seven tests and finite nineteen-case campaign are wanted.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, os, platform, shutil, subprocess, sys, tarfile, time, urllib.request
ROOT=Path(__file__).resolve().parent
PIN=json.loads((ROOT/'VIGILODE_PIN.json').read_text())
MANIFEST=json.loads((ROOT/'VIGILODE_SOURCE_MANIFEST.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def verify(root,manifest):
 for name,expected in manifest.items():
  p=root/name
  if not p.is_file() or sha(p)!=expected:raise RuntimeError('Source byte mismatch: '+str(p))
def capture(folder,argv,env=None,timeout=60,sources=()):
 folder.mkdir(parents=True,exist_ok=False)
 files=sorted(set(p for source in sources for p in source.rglob('*') if p.is_file() and not any(x in ('target','evidence','receipts','__pycache__') for x in p.relative_to(source).parts)))
 hashes={str(p):sha(p) for p in files}
 inputs={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':[str(x) for x in argv],'timeout_s':timeout,'source_sha256':hashes,'environment':{k:env[k] for k in ('CARGO_HOME','RUSTC') if env and k in env}}
 if Path(argv[0]).is_file():inputs['executable_sha256']=sha(argv[0])
 if files:
  with tarfile.open(folder/'sources.tar.gz','w:gz') as archive:
   for index,p in enumerate(files):archive.add(p,arcname=f'source_{index:04d}/{p.name}',recursive=False)
  inputs['source_archive_sha256']=sha(folder/'sources.tar.gz')
  inputs['source_archive_member_paths']={f'source_{index:04d}/{p.name}':str(p) for index,p in enumerate(files)}
 write_json(folder/'inputs.json',inputs);start=time.monotonic();truncated=False
 with (folder/'stdout.txt').open('wb') as so,(folder/'stderr.txt').open('wb') as se:
  try:code=subprocess.run([str(x) for x in argv],env=env,stdout=so,stderr=se,timeout=timeout).returncode
  except subprocess.TimeoutExpired:code=None;truncated=True
 outcome={'exit_code':code,'truncated':truncated,'wall_s':time.monotonic()-start,'stdout_sha256':sha(folder/'stdout.txt'),'stderr_sha256':sha(folder/'stderr.txt')};write_json(folder/'outcome.json',outcome)
 if code!=0 or truncated:raise RuntimeError('Failed/truncated command; preserved evidence: '+str(folder))
 return outcome

def restore_vigilode(args,out):
 destination=out/'vigilode'
 if args.vigilode_source:
  source=args.vigilode_source.resolve();verify(source,MANIFEST);destination.mkdir()
  for name in MANIFEST:
   p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,p)
 else:
  backup=ROOT/'backup/vigilode_source.tar.gz'
  archive=args.vigilode_archive or (backup if backup.is_file() else out/'vigilode_source.tar.gz')
  if not archive.is_file():
   if args.offline:raise RuntimeError('Pinned VigilODE archive/source absent in offline mode')
   with urllib.request.urlopen(PIN['url'],timeout=60) as response,archive.open('wb') as target:shutil.copyfileobj(response,target)
  if sha(archive)!=PIN['archive_sha256']:raise RuntimeError('Pinned VigilODE archive SHA256 mismatch')
  destination.mkdir();seen=set()
  with tarfile.open(archive,'r:gz') as tf:
   for member in tf:
    parts=PurePosixPath(member.name).parts
    if not parts or parts[0]!='vigilode-'+PIN['source_sha']:continue
    rel=PurePosixPath(*parts[1:])
    if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Unsafe archive path')
    name=str(rel)
    if name not in MANIFEST:continue
    if name in seen or not member.isfile():raise RuntimeError('Duplicate/nonregular whitelisted source')
    seen.add(name);p=destination/name;p.parent.mkdir(parents=True,exist_ok=True)
    with tf.extractfile(member) as source,p.open('wb') as target:shutil.copyfileobj(source,target)
   if seen!=set(MANIFEST):raise RuntimeError('Incomplete pinned source closure')
 verify(destination,MANIFEST)
 return destination

def invocation_path(command):
 # Preserve cargo/rustc's invocation basename for rustup-style multicall links.
 # Reading bytes for sha() still follows the symlink without changing argv[0].
 return Path(shutil.which(str(command)) or command).absolute()
def record_toolchain(evidence,cargo_exe,env):
 rustc=invocation_path(env.get('RUSTC') or 'rustc')
 for label,tool in [('cargo_version',cargo_exe),('rustc_version',rustc)]:
  capture(evidence/label,[tool,'-Vv'],env,30)
 metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.uname()._asdict(),'python':sys.version,'cpu_count':os.cpu_count(),'cargo_path':str(cargo_exe),'rustc_path':str(rustc),'cargo_sha256':sha(cargo_exe),'rustc_sha256':sha(rustc),'cargo_vv':(evidence/'cargo_version/stdout.txt').read_text(),'rustc_vv':(evidence/'rustc_version/stdout.txt').read_text()}
 write_json(evidence/'HOST_TOOLCHAIN_METADATA.json',metadata)

def run_cases(evidence,command_prefix,cases,env=None,sources=(),total_budget_s=180.,case_timeout_s=40.,case_args=()):
 """Return nonzero for any failed or unrun case; always retain matrix evidence."""
 total=0.;rows=[];blocked=set();executable=Path(command_prefix[0])
 def flush():
  failed=any(row['status']!='COMPLETED' for row in rows)
  write_json(evidence/'MATRIX_RECEIPT.json',{'cases':rows,'incremental_native_wall_s':total,'total_native_budget_s':total_budget_s,'overall_status':'INCOMPLETE_OR_FAILED' if failed else 'COMPLETED','overall_exit_code':1 if failed else 0,'executable_sha256':sha(executable)})
 for mode,method,n in cases:
  if (mode,method) in blocked:
   rows.append({'mode':mode,'method':method,'N':n,'status':'NOT_RUN_FAMILY_BLOCKED'});flush();continue
  remaining=total_budget_s-total
  if remaining<=0.:
   rows.append({'mode':mode,'method':method,'N':n,'status':'NOT_RUN_TOTAL_BUDGET'});flush();continue
  folder=evidence/f'{mode}_{method}_n{n}';raw=folder/'raw.json'
  timeout=min(case_timeout_s,remaining)
  try:
   capture(folder,[*command_prefix,raw,mode,method,n,*case_args],env,timeout,sources=sources)
   data=json.loads(raw.read_text());total+=data['wall_s']
   rows.append({'mode':mode,'method':method,'N':n,'status':'COMPLETED' if data['completed'] else 'FAILED','native_rhs':data['native_rhs_attempts_including_fd_replay'],'native_wall_s':data['wall_s'],'external_timeout_s':timeout})
   if not data['completed']:blocked.add((mode,method))
  except (RuntimeError,OSError,json.JSONDecodeError) as exc:
   data={}
   if raw.is_file():
    try:data=json.loads(raw.read_text())
    except (json.JSONDecodeError,OSError):pass
   outcome=json.loads((folder/'outcome.json').read_text()) if (folder/'outcome.json').is_file() else {}
   # On truncation a partial raw report cannot account for the unfinished work.
   # Charge the measured whole subprocess wall, or the timeout if no outcome exists.
   charged_wall=outcome.get('wall_s',timeout) if outcome.get('truncated') or not data else data.get('wall_s',outcome.get('wall_s',timeout))
   total+=charged_wall
   rows.append({'mode':mode,'method':method,'N':n,'status':'FAILED_OR_TRUNCATED','reason':str(exc),'native_rhs':data.get('native_rhs_attempts_including_fd_replay'),'charged_wall_s':charged_wall,'external_timeout_s':timeout});blocked.add((mode,method))
  flush()
 flush()
 return 1 if any(row['status']!='COMPLETED' for row in rows) else 0

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--input-root',type=Path,default=ROOT.parents[1],help='Repository research/lrs_atomic_native_bridge_20261016 root')
 p.add_argument('--ssprk-restore',type=Path,default=ROOT.parent/'time_centered_ssprk2_20261019/restore_ssprk2_native.py')
 p.add_argument('--output-root',type=Path,required=True,help='Fresh output workspace; existing paths refused')
 p.add_argument('--vigilode-source',type=Path,help='Verified local immutable source closure or full source tree')
 p.add_argument('--vigilode-archive',type=Path,help='Exact SHA-bound upstream tar.gz backup')
 p.add_argument('--native-eval',choices=('legacy','cell-cache','cell-borrowed'),default='legacy',help='Native evaluation implementation; default preserves legacy behavior')
 p.add_argument('--profile',action='store_true',help='Enable native evaluation profiling')
 p.add_argument('--cargo',default='cargo');p.add_argument('--cargo-home',type=Path);p.add_argument('--offline',action='store_true')
 action=p.add_mutually_exclusive_group();action.add_argument('--prepare-only',action='store_true');action.add_argument('--all',action='store_true');action.add_argument('--case',nargs=3,metavar=('MODE','METHOD','N'))
 a=p.parse_args();out=a.output_root.resolve()
 if out.exists():raise RuntimeError('Refusing existing output workspace: '+str(out))
 if not a.ssprk_restore.is_file():raise RuntimeError('Missing committed SSPRK restore chain: '+str(a.ssprk_restore))
 restore_evidence=out.parent/(out.name+'.prepare_evidence')
 capture(restore_evidence,[sys.executable,a.ssprk_restore,'--input-root',a.input_root.resolve(),'--output-root',out],timeout=90)
 evidence=out/'evidence';evidence.mkdir();shutil.move(str(restore_evidence),str(evidence/'native_restore'))
 native=out/'native_owner/rust/rei_microphysics';base=json.loads((ROOT/'BASE_NATIVE_MANIFEST.json').read_text());verify(native,base)
 hook=(ROOT/'native_additions/transport_hook.txt').read_bytes();parent=native/'src/axbi_covariant_transport.rs';parent.write_bytes(parent.read_bytes()+hook)
 shutil.copyfile(ROOT/'native_additions/axbi_native_rhs.rs',native/'src/axbi_native_rhs.rs')
 # Verify every original byte once more, including the exact prefix of the sole appended file.
 for name,expected in base.items():
  content=(native/name).read_bytes()
  if name=='src/axbi_covariant_transport.rs':content=content[:-len(hook)]
  if hashlib.sha256(content).hexdigest()!=expected:raise RuntimeError('Preexisting bytes changed: '+name)
 vigilode=restore_vigilode(a,out)
 adapter=out/'adapter';adapter.mkdir()
 for name in ('src','tests'):shutil.copytree(ROOT/name,adapter/name)
 shutil.copyfile(ROOT/'Cargo.lock',adapter/'Cargo.lock')
 cargo=(ROOT/'Cargo.toml').read_text().replace('../../v15_work/native_owner/rust/rei_microphysics','../native_owner/rust/rei_microphysics').replace('../vigilode_intake/native_source_closure','../vigilode')
 (adapter/'Cargo.toml').write_text(cargo)
 prepared={'status':'PREPARED_VERIFIED','native_baseline_files':len(base),'vigilode_files':len(MANIFEST),'vigilode_pin':PIN,'native_append_bytes':len(hook),'adapter_source_sha256':{str(q.relative_to(adapter)):sha(q) for q in adapter.rglob('*') if q.is_file()},'native_new_module_sha256':sha(native/'src/axbi_native_rhs.rs'),'native_parent_sha256':sha(parent),'native_compile':'NOT_RUN','scientific_cases':'NOT_RUN'}
 write_json(evidence/'PREPARE_RECEIPT.json',prepared)
 print(json.dumps(prepared,indent=2))
 if a.prepare_only:return
 if not a.all and not a.case:raise RuntimeError('Preparation complete; choose --prepare-only, --case or --all explicitly')
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='1'
 if a.cargo_home:env['CARGO_HOME']=str(a.cargo_home.resolve())
 elif (ROOT/'backup/cargo_home').is_dir():env['CARGO_HOME']=str(ROOT/'backup/cargo_home')
 cargo_exe=invocation_path(a.cargo)
 if (cargo_exe.parent/'rustc').is_file():env['RUSTC']=str(cargo_exe.parent/'rustc')
 record_toolchain(evidence,cargo_exe,env)
 # Lockfile preserves the upstream yanked dependency. Online fetch, when allowed,
 # completes before a mandatory offline locked release build.
 fetch=[cargo_exe,'fetch','--locked','--manifest-path',adapter/'Cargo.toml']+(['--offline'] if a.offline else [])
 capture(evidence/'cargo_fetch',fetch,env,600)
 capture(evidence/'release_build',[cargo_exe,'build','--offline','--locked','--release','--manifest-path',adapter/'Cargo.toml'],env,1200,sources=(native,vigilode,adapter))
 if a.all:capture(evidence/'focused_tests',[cargo_exe,'test','--offline','--locked','--release','--manifest-path',adapter/'Cargo.toml','--lib','--test','focused','--','--test-threads=1','--nocapture'],env,600,sources=(native,vigilode,adapter))
 binary=adapter/'target/release/rei-vigilode-radau-research';cases=[tuple(a.case)] if a.case else [(mode,method,str(n)) for mode,methods in [('fixed',{'radau':[2,4,8,16],'ssprk':[8,16,32]}),('birth',{'radau':[4,8,16],'ssprk':[4,8,16]}),('disabled',{'radau':[4,8,16],'ssprk':[4,8,16]})] for method,levels in methods.items() for n in levels]
 return run_cases(evidence,[binary],cases,env,sources=(native,vigilode,adapter),case_args=['--native-eval',a.native_eval]+(['--profile'] if a.profile else []))
if __name__=='__main__':
 try:raise SystemExit(main() or 0)
 except Exception as e:print(str(e),file=sys.stderr);raise SystemExit(1)
