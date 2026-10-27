"""Byte-only blocker-loop packaging. Never imports science or writes externally.
Run only with explicit controller GO:
python delivery/package_checkpoint.py PHASE --go-file PATH
GO requires authorized,phase,unit_id,repository,allowed_path,base_tree_sha,
and files: exact {path,sha256} entries relative to this unit.
"""
import time
START_WALL=time.perf_counter()
import argparse
import datetime
import hashlib
import json
import pathlib
import resource
import signal
import sys
import zipfile
UNIT=pathlib.Path(__file__).resolve().parents[1]
OUT=UNIT/'delivery'
PRIOR_CPU=6.036257744
PRIOR_WALL=6.039164908005692
CAP_CPU=5.0
CAP_WALL=10.0
CANONICAL_ROOT='research/orchestration_expansion_20261025/'
CANONICAL_PATHS={'DAG.json','contracts/HE-EXP-SPECIES.json','contracts/REC-EXP-SPECIES.json','node_plans/HE-EXP-SPECIES.md','node_plans/REC-EXP-SPECIES.md','status/CURRENT_STATUS.json','returns/REI_SPECIES_PROJECTION_20261026.json'}

def enc(obj):
    return (json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def check():
    if time.process_time()>=CAP_CPU or time.perf_counter()-START_WALL>=CAP_WALL:
        raise RuntimeError('PACKAGING_CAP_REACHED')
def signal_cap(signum,frame):
    raise RuntimeError('PACKAGING_CAP_SIGNAL:'+str(signum))
def write(path,obj):
    path.write_bytes(enc(obj))

def build(go,phase):
    private=[];public=[];rows=[];binary=[]
    assert go['files'],'EMPTY_FROZEN_SCOPE'
    seen=set();canonical_targets=set();public_targets=set()
    for entry in go['files']:
        check()
        name=entry['path']
        rel=pathlib.PurePosixPath(name)
        assert name not in seen,'DUPLICATE_PATH'
        seen.add(name)
        assert not rel.is_absolute() and '..' not in rel.parts,'UNSAFE_PATH'
        assert rel.parts[0]!='recovery','NO_PRIVATE_RECOVERY_RAW'
        assert name!='intake/current_DAG.json','NO_LARGE_CENSUS_DUMP'
        assert not any(x in rel.parts for x in ['__pycache__','.git']),'FORBIDDEN_TREE'
        assert 'GIT_TREE_PAYLOAD' not in name,'NO_RECURSIVE_GIT_PAYLOAD'
        assert 'PACKAGE_RECEIPT' not in name or name=='delivery/CANONICAL_PACKAGE_RECEIPT.json','NO_RECURSIVE_PACKAGE_OUTPUT'
        assert not name.upper().endswith(('EXA_RAW.JSON','SCISPACE_RAW.JSON')),'NO_THIRD_PARTY_RAW'
        path=UNIT/name
        assert path.is_file() and not path.is_symlink(),'MISSING_OR_SYMLINK:'+name
        assert path.resolve().is_relative_to(UNIT.resolve()),'ESCAPED_ROOT'
        assert path.suffix not in {'.zip','.gz','.tar','.pyc','.tmp'},'NO_ARCHIVE_OR_CACHE'
        raw=path.read_bytes()
        assert sha(raw)==entry['sha256'],'FROZEN_BYTE_MISMATCH:'+name
        git_path=go['allowed_path'].rstrip('/')+'/'+name
        if rel.parts[0]=='canonical_patch':
            suffix='/'.join(rel.parts[1:])
            assert suffix in CANONICAL_PATHS,'CANONICAL_ALLOWLIST'
            assert entry.get('git_path')==CANONICAL_ROOT+suffix,'EXPLICIT_CANONICAL_TARGET_REQUIRED'
            git_path=entry['git_path'];canonical_targets.add(suffix)
        else:
            assert entry.get('git_path',git_path)==git_path,'NONCANONICAL_TARGET_OVERRIDE'
        private_only=entry.get('public',True) is False or name.startswith('stopping/source_raw/')
        row={'path':name,'bytes':len(raw),'sha256':sha(raw),'git_path':None if private_only else git_path}
        rows.append(row);private.append((name,raw))
        if private_only:
            binary.append(row);continue
        try:
            content=raw.decode('utf-8')
            assert '\x00' not in content
            assert path.suffix not in {'.npz','.npy','.png','.pdf','.so','.o'}
        except (UnicodeDecodeError,AssertionError):
            binary.append(row);continue
        assert git_path not in public_targets,'DUPLICATE_GIT_TARGET'
        public_targets.add(git_path)
        public.append({'path':git_path,
                       'mode':'100644','type':'blob','content':content})
    if canonical_targets:assert canonical_targets==CANONICAL_PATHS,'EXACT_SEVEN_CANONICAL_MAPPINGS_REQUIRED'
    manifest={'unit_id':go['unit_id'],'phase':phase,'files':rows,
              'prior_binary_companion':{'bytes':17368910,'sha256':'df62233ae9ac76a5a62aea551dc56c7c68820c36aa2ab7dc8ff98f1728700b58','included':False,'required_for_current_25_tests':False,'role':'Future H1 actual source consumption only'},
              'science_evaluations':0,'future_delivery_ACK_included':False}
    zpath=OUT/(phase+'_PRIVATE_PORTABLE.zip')
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for name,raw in private:
            check();z.writestr(UNIT.name+'/'+name,raw)
        z.writestr('MANIFEST.json',enc(manifest))
    with zipfile.ZipFile(zpath) as z:
        for row in rows:
            check()
            raw=z.read(UNIT.name+'/'+row['path'])
            assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
        assert set(z.namelist())=={UNIT.name+'/'+r['path'] for r in rows}|{'MANIFEST.json'}
        assert z.testzip() is None
    check()
    write(OUT/(phase+'_PUBLIC_MANIFEST.json'),{'files':[r for r in rows if r not in binary],
          'private_companion_only_files':binary,'prior_archive_reference':manifest['prior_binary_companion']})
    write(OUT/(phase+'_GIT_TREE_PAYLOAD.json'),{'repository_full_name':go['repository'],
          'base_tree_sha':go['base_tree_sha'],'tree_elements':public})
    return {'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath.read_bytes()),
            'members':len(rows)+1,'payload_files':len(rows),'public_text_files':len(public),
            'private_only_files':len(binary),'member_sizes_hashes_CRC':'pass_scoped'}

def main():
    global CAP_CPU,CAP_WALL
    pa=argparse.ArgumentParser();pa.add_argument('phase');pa.add_argument('--go-file',required=True)
    a=pa.parse_args();assert a.phase.replace('_','').isalnum()
    go=json.loads(pathlib.Path(a.go_file).read_text())
    assert go.get('authorized') is True and go['phase']==a.phase
    for k in ['unit_id','repository','allowed_path','base_tree_sha','files']:assert k in go
    receipt=OUT/(a.phase+'_PACKAGE_RECEIPT.json')
    assert not receipt.exists(),'PRESERVE_EXISTING_ATTEMPT'
    pc,pw=PRIOR_CPU,PRIOR_WALL
    for f in OUT.glob('*_PACKAGE_RECEIPT.json'):
        old=json.loads(f.read_text());pc+=old['incremental_CPU_s'];pw+=old['incremental_wall_s']
    CAP_CPU=min(5.0,30-pc);CAP_WALL=min(10.0,60-pw)
    assert CAP_CPU>0 and CAP_WALL>0,'CUMULATIVE_CAP_EXHAUSTED'
    signal.signal(signal.SIGXCPU,signal_cap);signal.signal(signal.SIGALRM,signal_cap)
    resource.setrlimit(resource.RLIMIT_CPU,(max(1,int(CAP_CPU)),max(2,int(CAP_CPU)+1)))
    signal.setitimer(signal.ITIMER_REAL,max(.001,CAP_WALL-(time.perf_counter()-START_WALL)))
    result=None;error=None
    try:
        result=build(go,a.phase);check()
    except BaseException as exc:error=type(exc).__name__+': '+str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        cpu=time.process_time();wall=time.perf_counter()-START_WALL
        status='failed' if error or cpu>=CAP_CPU or wall>=CAP_WALL else 'completed'
        rec={'unit_id':go['unit_id'],'phase':a.phase,'status':status,'error':error,'archive':result,
             'incremental_CPU_s':cpu,'incremental_wall_s':wall,
             'charged_prior_CPU_s':pc,'charged_prior_wall_s':pw,
             'charged_cumulative_CPU_s':pc+cpu,'charged_cumulative_wall_s':pw+wall,
             'campaign_caps':{'CPU_s':30,'wall_s':60},
             'phase_caps':{'CPU_s':CAP_CPU,'wall_s':CAP_WALL},
             'failed_attempts_charged':True,'science_evaluations':0,'external_writes':0,
             'old_archive_reuploaded':False,'old_frozen_files_changed':False,
             'backup':'PENDING_CONTROLLER_GO','unmeasured_metadata_network_overhead':'UNKNOWN_NOT_ZERO',
             'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        write(receipt,rec);print(json.dumps(rec))
    return 0 if status=='completed' else 1
if __name__=='__main__':sys.exit(main())

