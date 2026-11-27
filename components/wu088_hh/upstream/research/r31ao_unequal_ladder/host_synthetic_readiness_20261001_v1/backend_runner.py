"""Offline host-only sidecar builder. Default invocation only describes a plan.

No scientific inputs are accepted. Source pinning is not execution authorization.
Linux/POSIX resource caps are per process; they are not a cgroup memory quota.
"""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import io
import json
import lzma
import math
import os
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'gap_closure_20261001_g0_g6_v1'
CONFIG = {
    'jobs': 2, 'global_wall_seconds': 10800, 'memory_mib': 4096,
    'configure_seconds': 180, 'bootstrap_seconds': 180,
    'build_seconds': 2400, 'check_seconds': 1200, 'install_seconds': 180,
    'native_build_seconds': 180, 'native_run_seconds': 180,
    'log_bytes': 8*1024*1024, 'file_bytes': 2*1024**3,
    'workspace_bytes': 16*1024**3, 'workspace_files': 200000,
}
SOURCES = {
    'gmp': {'archive':'C09.tar.xz','version':'6.3.0','root':'gmp-6.3.0',
            'size':2094196,'sha256':'a3c2b80201b89e68616f4ad30bc66aee4927c3ce50e33929ca819d5c43538898'},
    'mpfr': {'archive':'C08.tar.xz','version':'4.2.2','root':'mpfr-4.2.2',
             'size':1505596,'sha256':'b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01'},
    'flint': {'archive':'C01.tar.gz','version':'3.4.0','root':'flint-2b0788802abf62ec29d8e4a8f917993606e517e0',
              'size':8702721,'sha256':'108ab51a4dd33918ff3308f0c63a63616ae30a2c174d50c9188676e85011346f'},
}
TOOL_NAMES = {'cc':'gcc','cxx':'g++','make':'make','sh':'sh','bash':'bash',
              'pkg_config':'pkg-config','ldd':'ldd','autoreconf':'autoreconf',
              'autoconf':'autoconf','automake':'automake','libtoolize':'libtoolize',
              'm4':'m4','python3':'python3','sha256sum':'sha256sum'}


class RunnerError(ValueError):
    pass


def identity(path, maximum=512*1024*1024):
    p = Path(path).resolve(strict=True)
    if not p.is_file() or p.stat().st_size > maximum:
        raise RunnerError('file identity size/type refused: '+str(p))
    h = hashlib.sha256(); size = 0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            size += len(b)
            if size > maximum: raise RunnerError('file grew beyond identity cap')
            h.update(b)
    return {'path':str(p),'size':size,'sha256':h.hexdigest()}


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value,f,indent=2,sort_keys=True); f.write('\n')


def validate_config(config):
    if set(config) != set(CONFIG): raise RunnerError('unknown or missing configuration field')
    for k,v in config.items():
        if type(v) is not int or v <= 0: raise RunnerError('positive integer cap required: '+k)
    if config['jobs'] != 2: raise RunnerError('exactly -j2 required')
    if not 128 <= config['memory_mib'] <= 8192: raise RunnerError('memory cap outside 128..8192 MiB')
    if config['global_wall_seconds'] > 14400: raise RunnerError('global wall cap exceeds four hours')
    for k,v in config.items():
        if k.endswith('_seconds') and k != 'global_wall_seconds' and v > 3600:
            raise RunnerError('stage wall cap exceeds one hour')
        if k.endswith(('_bytes','_files')) and v > CONFIG[k]:
            raise RunnerError('resource cap exceeds fixed ceiling: '+k)
    return dict(config)


def safe_extract(archive, destination, *, expected_sha256, expected_root,
                 max_file_bytes=16*1024*1024, max_total_bytes=96*1024*1024,
                 max_members=20000, max_archive_bytes=16*1024*1024,
                 max_expanded_bytes=128*1024*1024):
    """Validate hash, bounded decompression and all paths before creating output.

    Strictly reject links and special members; upstream pinned archives need none.
    Entire decompressed tar is bounded before tarfile parses PAX/long-name records.
    """
    dest = Path(destination)
    if dest.exists() or dest.is_symlink(): raise RunnerError('extraction destination already exists')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',expected_root): raise RunnerError('invalid archive root')
    item = identity(archive,max_archive_bytes)
    if item['sha256'] != expected_sha256: raise RunnerError('archive SHA256 mismatch')
    with Path(archive).open('rb') as f: magic = f.read(6)
    opener = gzip.open if magic.startswith(b'\x1f\x8b') else lzma.open if magic == b'\xfd7zXZ\x00' else None
    if opener is None: raise RunnerError('only gzip or xz tar accepted')
    expanded=io.BytesIO()
    try:
        with opener(archive,'rb') as f:
            while True:
                b=f.read(min(1024*1024,max_expanded_bytes-expanded.tell()+1))
                if not b: break
                if expanded.tell()+len(b)>max_expanded_bytes: raise RunnerError('expanded tar cap exceeded')
                expanded.write(b)
        expanded.seek(0)
        with tarfile.open(fileobj=expanded,mode='r:') as tf:
            members=[]; paths={}; total=0
            for member in tf:
                if len(members)>=max_members: raise RunnerError('member count cap exceeded')
                name=member.name.rstrip('/')
                path=PurePosixPath(name)
                if (not name or '\\' in name or '\x00' in name or path.is_absolute()
                        or any(x in ('','.','..') for x in name.split('/'))
                        or path.parts[0]!=expected_root or str(path)!=name):
                    raise RunnerError('unsafe member path')
                if name in paths: raise RunnerError('duplicate member path')
                if not (member.isfile() or member.isdir()) or member.issparse():
                    raise RunnerError('links/special/sparse members refused')
                if member.size<0 or member.size>max_file_bytes: raise RunnerError('member byte cap exceeded')
                total+=member.size
                if total>max_total_bytes: raise RunnerError('total member byte cap exceeded')
                paths[name]=member.isdir(); members.append(member)
            for name,is_dir in paths.items():
                if any(str(p) in paths and not paths[str(p)] for p in PurePosixPath(name).parents if str(p)!='.'):
                    raise RunnerError('regular-file ancestor collision')
            if not members: raise RunnerError('empty archive')
            dest.mkdir(parents=False,exist_ok=False)
            for member in members:
                target=dest/member.name.rstrip('/')
                if member.isdir(): target.mkdir(parents=True,exist_ok=True); continue
                target.parent.mkdir(parents=True,exist_ok=True)
                with tf.extractfile(member) as src, target.open('xb') as out:
                    remaining=member.size
                    while remaining:
                        b=src.read(min(1024*1024,remaining))
                        if not b: raise RunnerError('truncated member')
                        out.write(b); remaining-=len(b)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
    except (tarfile.TarError,EOFError,lzma.LZMAError,OSError) as exc:
        raise RunnerError('archive extraction refused: '+str(exc)) from exc
    finally:
        expanded.close()
    return dest/expected_root


def build_steps(root, prefix, tools, config):
    validate_config(config); root=Path(root); prefix=Path(prefix); steps=[]
    for lib,spec in SOURCES.items():
        cwd=root/'sources'/lib/spec['root']
        def add(stage,argv):
            steps.append({'id':lib+'-'+stage,'library':lib,'stage':stage,
                          'cwd':str(cwd),'argv':argv,'wall_seconds':config[stage+'_seconds']})
        if lib=='flint': add('bootstrap',[tools['sh'],'./bootstrap.sh'])
        args=[tools['sh'],'./configure','--prefix='+str(prefix),'--libdir='+str(prefix/'lib')]
        if lib in ('mpfr','flint'): args.append('--with-gmp='+str(prefix))
        if lib=='flint': args.extend(['--with-mpfr='+str(prefix),'--with-blas=no','--with-ntl=no'])
        add('configure',args)
        add('build',[tools['make'],'-j2'])
        check=[tools['make'],'-j2','check']
        if lib=='flint': check.append('MOD=arb acb acb_hypgeom acb_calc')
        add('check',check)
        add('install',[tools['make'],'-j2','install'])
    return steps


def clean_environment(root,prefix,tools,config):
    root=Path(root); prefix=Path(prefix)
    # Explicit allowlist: no compiler, Python, dynamic-loader or proxy injection.
    path=list(dict.fromkeys([str(Path(p).parent) for p in tools.values()]+['/usr/bin','/bin']))
    return {'PATH':os.pathsep.join(path),'WU088_BUILD_HOME':str(root/'home'),'TMPDIR':str(root/'tmp'),
            'LC_ALL':'C','LANG':'C','TZ':'UTC','CC':tools['cc'],'CXX':tools['cxx'],
            'CFLAGS':'-O2 -fno-fast-math -ffp-contract=off',
            'CXXFLAGS':'-O2 -fno-fast-math -ffp-contract=off',
            'LD_LIBRARY_PATH':str(prefix/'lib'),
            'PKG_CONFIG_PATH':str(prefix/'lib/pkgconfig'),
            'PKG_CONFIG_LIBDIR':str(prefix/'lib/pkgconfig'),
            'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','PYTHONNOUSERSITE':'1',
            'PYTHONDONTWRITEBYTECODE':'1'}


def check_input_lock(lock_path=HERE/'INPUT_LOCK.json', old=OLD):
    lock=json.loads(Path(lock_path).read_text()); old=Path(old).resolve(strict=True)
    if lock.get('old_overlay_relative_path')!='research/r31ao_unequal_ladder/gap_closure_20261001_g0_g6_v1':
        raise RunnerError('unexpected prior overlay authority')
    seen=set()
    for f in lock['files']:
        rel=PurePosixPath(f['path'])
        if rel.is_absolute() or '..' in rel.parts or str(rel) in seen: raise RunnerError('invalid lock path')
        seen.add(str(rel)); actual=identity(old/rel,4*1024*1024)
        if not Path(actual['path']).is_relative_to(old) or (actual['sha256'],actual['size'])!=(f['sha256'],f['size']):
            raise RunnerError('prior input lock mismatch: '+str(rel))
    required={'validated_callback/build_host.sh','validated_callback/verify_build_inputs.py',
              'validated_callback/callback.cpp','validated_callback/callback.hpp',
              'validated_callback/assembly.cpp','validated_callback/assembly.hpp',
              'validated_callback/native_synthetic.cpp','interior_pilot/build_petras_host.sh',
              'interior_pilot/petras_host.cpp','interior_pilot/petras_host.hpp',
              'interior_pilot/native_petras_synthetic.cpp','host_guard/run_guarded.py'}
    if not required<=seen: raise RunnerError('lock omits executed/compiled dependency')
    return {'status':'PRIOR_CODE_BYTES_VERIFIED','files':len(seen),'lock':identity(lock_path),
            'synthetic_fixture_source_locked':True,'actual_HH_input_loader_in_pipeline':False}


def preflight(source_dir,output):
    lock=check_input_lock()  # Before extraction or any subprocess, including version probes.
    output=Path(output)
    if not output.is_absolute() or not re.fullmatch(r'[A-Za-z0-9_./-]+',str(output)):
        raise RunnerError('absolute output path with simple ASCII components required')
    output=output.resolve()
    if output.exists() or not output.parent.is_dir(): raise RunnerError('output must be new, with existing parent')
    if output.is_relative_to(OLD.resolve()) or output in (Path('/'),Path('/usr'),Path('/opt'),Path('/tmp')):
        raise RunnerError('output overlaps protected source/system location')
    sources={}
    for name,spec in SOURCES.items():
        item=identity(Path(source_dir)/spec['archive'],16*1024*1024)
        if (item['size'],item['sha256'])!=(spec['size'],spec['sha256']): raise RunnerError(name+' archive pin mismatch')
        sources[name]=item
    tools={}; missing=[]; tool_identities={}
    for key,name in TOOL_NAMES.items():
        found=shutil.which(name,path='/usr/local/bin:/usr/bin:/bin')
        if found is None: missing.append(name)
        else: tools[key]=str(Path(found).absolute()); tool_identities[key]=identity(found)
    return {'status':'PREFLIGHT_BLOCKED_MISSING_TOOLS' if missing else 'PREFLIGHT_READY_HOST_EXECUTION_NOT_RUN',
            'missing_tools':missing,'tools':tools,'tool_identities':tool_identities,'sources':sources,
            'input_lock':lock,'current_sources':{p:identity(HERE/p) for p in ('backend_runner.py','provenance_gate.py')},
            'output':str(output),'native_builds':0,'actual_HH_runs':0}


def workspace_usage(root,max_files):
    total=0; count=0
    for folder,dirs,files in os.walk(root,followlinks=False):
        for name in files:
            p=Path(folder)/name
            if p.is_symlink(): continue
            try: total+=p.stat().st_size
            except FileNotFoundError: continue
            count+=1
            if count>max_files: return total,count
    return total,count


def parse_native_marker(label, stdout):
    """Match immutable fixture final JSON; preserve preceding Petras diagnostics."""
    if not isinstance(stdout,str) or len(stdout)>65536: raise RunnerError('native stdout bound/type')
    lines=stdout.strip().splitlines()
    expected=({'scope':'SYNTHETIC_ONLY','native_synthetic_passed':True} if label=='callback' else
              {'synthetic_only':True,'native_fixture_checks':10,'actual_HH_evaluations':0} if label=='petras' else None)
    if expected is None or not lines: raise RunnerError('unknown/empty native marker')
    try: payload=json.loads(lines[-1])
    except json.JSONDecodeError as exc: raise RunnerError('invalid final native JSON marker') from exc
    if (type(payload) is not dict or set(payload)!=set(expected)
            or any(type(payload[k]) is not type(v) or payload[k]!=v for k,v in expected.items())):
        raise RunnerError('native synthetic acceptance marker mismatch: '+label)
    diagnostics=lines[:-1]
    if label=='callback' and diagnostics: raise RunnerError('unexpected callback diagnostics')
    if label=='petras' and (len(diagnostics)!=2 or
            not diagnostics[0].startswith('one_dimensional_polynomial=') or
            not diagnostics[1].startswith('nested_polynomial=')):
        raise RunnerError('locked Petras diagnostic structure mismatch')
    return {'payload':payload,'diagnostic_lines':diagnostics}


def run_stage(step,root,env,config,deadline):
    """Finite argv-only Linux stage. Preserve logs on success, refusal or timeout."""
    remaining=deadline-time.monotonic()
    if remaining<=0: raise RunnerError('global wall budget exhausted')
    wall=min(step['wall_seconds'],remaining)
    logdir=root/'logs'/step['id']; logdir.mkdir(exist_ok=False)
    mem=config['memory_mib']*1024*1024
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(mem,mem))
        cpu=max(1,math.ceil(wall)); resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
        resource.setrlimit(resource.RLIMIT_FSIZE,(config['file_bytes'],config['file_bytes']))
    start=time.monotonic(); reason='CHILD_EXIT_RECORDED'; proc=None; descendants=False
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        with (logdir/'stdout.log').open('xb') as out,(logdir/'stderr.log').open('xb') as err:
            proc=subprocess.Popen(step['argv'],cwd=step['cwd'],env=env,shell=False,
                                  stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                                  start_new_session=True,preexec_fn=limits)
            disk_check=start
            while proc.poll() is None:
                now=time.monotonic()
                if now-start>=wall: reason='WALL_LIMIT'; break
                if max(os.fstat(out.fileno()).st_size,os.fstat(err.fileno()).st_size)>config['log_bytes']:
                    reason='LOG_LIMIT'; break
                if now>=disk_check:
                    size,count=workspace_usage(root,config['workspace_files']); disk_check=now+2
                    if size>config['workspace_bytes'] or count>config['workspace_files']:
                        reason='WORKSPACE_LIMIT'; break
                time.sleep(0.05)
            if proc.poll() is None:
                try: os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError: pass
            proc.wait()
            try: os.killpg(proc.pid,signal.SIGKILL); descendants=reason=='CHILD_EXIT_RECORDED'
            except ProcessLookupError: pass
        if descendants: reason='DESCENDANTS_SURVIVE_LEADER'
        if reason=='CHILD_EXIT_RECORDED':
            if max((logdir/'stdout.log').stat().st_size,(logdir/'stderr.log').stat().st_size)>config['log_bytes']:
                reason='LOG_LIMIT'
            size,count=workspace_usage(root,config['workspace_files'])
            if size>config['workspace_bytes'] or count>config['workspace_files']: reason='WORKSPACE_LIMIT'
    finally:
        if proc is not None:
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={**step,'exit_code':proc.returncode,'reason':reason,'wall_elapsed_seconds':time.monotonic()-start,
             'wall_budget_seconds':wall,'memory_bytes_per_process':mem,'aggregate_tree_memory_limit':False,
             'file_size_cap_bytes_per_file':config['file_bytes'],'stdout':identity(logdir/'stdout.log'),
             'stderr':identity(logdir/'stderr.log'),'children_user_seconds':after.ru_utime-before.ru_utime,
             'children_system_seconds':after.ru_stime-before.ru_stime,'children_maxrss_kib_observed':after.ru_maxrss,
             'workspace_and_log_caps_are_polled':True,'environment':env,'actual_HH_runs':0}
    write_json(logdir/'STAGE.json',receipt)
    if proc.returncode!=0 or reason!='CHILD_EXIT_RECORDED': raise RunnerError('stage failed: '+step['id']+' / '+reason)
    return {**receipt,'receipt':identity(logdir/'STAGE.json')}


def execute(pre,config):
    if pre['missing_tools']: raise RunnerError('missing host tools: '+', '.join(pre['missing_tools']))
    if sys.platform!='linux': raise RunnerError('Linux host required; no unguarded fallback')
    from provenance_gate import verify_backend,verify_linkage
    root=Path(pre['output']); root.mkdir(exist_ok=False)
    write_json(root/'PREFLIGHT.json',pre)
    start=time.monotonic(); deadline=start+config['global_wall_seconds']; stages=[]
    report={'status':'HOST_PIPELINE_STARTED','actual_HH_runs':0,'rigorous':False,'certified_epsilon':None,
            'certified_eta':None,'native_library_builds_verified':False,'native_synthetic_accepted':False}
    try:
        for d in ('sources','prefix','logs','home','tmp'): (root/d).mkdir()
        prefix=root/'prefix'; tools=pre['tools']; env=clean_environment(root,prefix,tools,config)
        for name,spec in SOURCES.items():
            safe_extract(pre['sources'][name]['path'],root/'sources'/name,expected_sha256=spec['sha256'],expected_root=spec['root'])
            if time.monotonic()>=deadline: raise RunnerError('global budget exhausted during extraction')
        def run(step,custom_env=None):
            result=run_stage(step,root,custom_env or env,config,deadline); stages.append(result); return result
        compiler_versions={}
        for key in ('cc','cxx'):
            r=run({'id':key+'-version','stage':'version','cwd':str(root),'argv':[tools[key],'--version'],'wall_seconds':10})
            compiler_versions[key]={**identity(tools[key]),'version':Path(r['stdout']['path']).read_text()[:16384]}
        for step in build_steps(root,prefix,tools,config): run(step)
        record={'verified_build_provenance':True,'compatibility_assertion_only':True,'prefix':str(prefix),
                'compiler':compiler_versions['cc'],'cxx_compiler':compiler_versions['cxx'],'libraries':{},
                'execution_witness':'This runner stage receipts; not independent historical admission.'}
        for name,spec in SOURCES.items():
            binary=identity(prefix/'lib'/('lib'+name+'.so'))
            if not Path(binary['path']).is_relative_to(prefix): raise RunnerError('installed binary escaped prefix')
            logs=[{'stage':r['stage'],'path':r['receipt']['path'],'sha256':r['receipt']['sha256'],'exit_code':0,
                   'stdout':r['stdout'],'stderr':r['stderr']}
                  for r in stages if r.get('library')==name]
            record['libraries'][name]={'version':spec['version'],'source_archive_path':pre['sources'][name]['path'],
                'source_archive_sha256':spec['sha256'],'binary_path':binary['path'],'binary_sha256':binary['sha256'],
                'compiler':compiler_versions['cc'],'flags':env['CFLAGS'].split(),
                'abi':{'machine':platform.machine(),'system':platform.system(),'binary_format':'ELF'},
                'build_logs':logs,'build_log_sha256':next(x['sha256'] for x in logs if x['stage']=='build')}
        record_path=root/'BACKEND_BUILD_PROVENANCE.json'; write_json(record_path,record)
        record=verify_backend(record_path,prefix); report['native_library_builds_verified']=True
        accepted=[]
        jobs=[('callback','validated_callback/build_host.sh','WU088_BUILD_OUT','native_synthetic'),
              ('petras','interior_pilot/build_petras_host.sh','WU088_PETRAS_BUILD_OUT','native_petras_synthetic')]
        for label,script,outvar,binary_name in jobs:
            check_input_lock()
            out=root/('native_'+label)
            native_env={**env,'WU088_BACKEND_PREFIX':str(prefix),'WU088_BUILD_PROVENANCE':str(record_path),outvar:str(out)}
            run({'id':label+'-compile','stage':'native-build','cwd':str(root),'argv':[tools['bash'],str(OLD/script)],
                 'wall_seconds':config['native_build_seconds']},native_env)
            binary=identity(out/binary_name)
            linkage=run({'id':label+'-linkage','stage':'linkage','cwd':str(root),'argv':[tools['ldd'],binary['path']],'wall_seconds':10})
            linked=verify_linkage(Path(linkage['stdout']['path']).read_text(),
                                  {n:v['binary_path'] for n,v in record['libraries'].items()})
            # Recheck binary/log/source chain and linked library bytes immediately before run.
            record=verify_backend(record_path,prefix)
            for n,item in linked['libraries'].items():
                if identity(item['path'])['sha256']!=record['libraries'][n]['binary_sha256']:
                    raise RunnerError('linked-library byte mismatch: '+n)
            if identity(binary['path'])!=binary: raise RunnerError('native executable changed before run')
            write_json(out/'LINKAGE_VERIFIED.json',linked)
            guardout=root/(label+'_guard')
            budget=min(config['native_run_seconds'],deadline-time.monotonic()-2)
            if budget<=0: raise RunnerError('global budget exhausted before native run')
            run({'id':label+'-synthetic','stage':'native-run','cwd':str(root),
                 'argv':[tools['python3'],str(OLD/'host_guard/run_guarded.py'),'--wall-seconds',str(budget),
                         '--memory-mib',str(config['memory_mib']),'--output-dir',str(guardout),'--',binary['path']],
                 'wall_seconds':budget+2})
            receipt=json.loads((guardout/'PROCESS_RECEIPT.json').read_text())
            if receipt['status']!='PROCESS_COMPLETED' or receipt['stdout_preview_truncated']:
                raise RunnerError('native synthetic acceptance marker mismatch: '+label)
            marker=parse_native_marker(label,receipt['stdout'])
            accepted.append({'fixture':label,'binary':binary,**marker,'guard_receipt':identity(guardout/'PROCESS_RECEIPT.json')})
        report.update(status='HOST_SYNTHETIC_ACCEPTED',native_synthetic_accepted=True,native_synthetic=accepted)
    except Exception as exc:
        report.update(status='HOST_PIPELINE_FAILED',error=str(exc),error_type=type(exc).__name__)
        raise
    finally:
        report.update(wall_elapsed_seconds=time.monotonic()-start,completed_stages=[s['id'] for s in stages],
                      historical_abi_admitted=False,scientific_promotion=False)
        write_json(root/'HOST_RESULT.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path,required=True,help='directory with pinned C09.tar.xz, C08.tar.xz, C01.tar.gz')
    p.add_argument('--output',type=Path,required=True,help='new absolute sidecar directory (not created in plan mode)')
    p.add_argument('--execute-host-synthetic',action='store_true',help='explicit local-host build and synthetic-only execution')
    a=p.parse_args()
    try:
        config=validate_config(CONFIG); pre=preflight(a.source_dir,a.output)
        if a.execute_host_synthetic: result=execute(pre,config)
        else:
            proposed={k:pre['tools'].get(k,'/UNAVAILABLE/'+v) for k,v in TOOL_NAMES.items()}
            result={'status':'PLAN_ONLY','preflight':pre,'config':config,'library_steps':build_steps(a.output,a.output/'prefix',proposed,config),
                    'native_steps':['locked callback build','ldd identity gate','guarded synthetic callback',
                                    'locked Petras build','ldd identity gate','guarded synthetic Petras'],
                    'library_builds_executed':0,'native_runs':0,'actual_HH_runs':0,'execution_authorized_by_hash':False}
        print(json.dumps(result,indent=2)); return 0
    except Exception as exc:
        print(json.dumps({'status':'REFUSED','reason':str(exc),'error_type':type(exc).__name__,
                          'scientific_promotion':False}),file=sys.stderr); return 2


if __name__=='__main__':
    raise SystemExit(main())
