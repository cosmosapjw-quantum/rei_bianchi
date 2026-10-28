"""Byte-only delivery preparation. Requires a controller-created explicit GO JSON.
No science imports, numerical evaluation, render or external writes occur here.
Usage: python delivery/package_checkpoint.py PHASE --go-file PATH
GO JSON: {"authorized": true, "unit_id": "...", "phase": "PHASE"}.
"""
import time
START_WALL = time.perf_counter()
import argparse
import datetime
import hashlib
import json
import pathlib
import resource
import signal
import sys
import zipfile

UNIT = pathlib.Path(__file__).resolve().parents[1]
OUT = UNIT / 'delivery'
UNIT_ID = 'REI-H1-PRIMARY-SOURCE-MEASURE-20261026'
ROOT_NAMES = {'UNIT_START.json','ADMISSION.json','GLOBAL_DAG_STATUS.json',
              'REPORT_KO.md','HANDOFF_KO.md','README.md','REPRODUCE.md'}
SCIENCE_ROOTS = {'theory','implementation','review','runtime_inputs','progress'}
CURATED_INTAKE = {'AGENTS_CURRENT.md','AUTHORITY_INTAKE.md',
                 'SOURCE_PINS.json','SURVEY_SYNTHESIS_KO.md'}
CURATED_PROVIDER = {'PROVIDER_READINESS_KO.md','PROVIDER_READINESS.json',
                    'SOURCES.json','SOURCE_PINS.json'}
DELIVERY_NAMES = {'package_checkpoint.py','PUBLICATION_PLAN.json',
                  'README_PORTABILITY.md'}
FORBIDDEN_SUFFIXES = {'.pyc','.tmp','.zip','.tar','.gz'}
BINARY_SUFFIXES = {'.npz','.npy','.png','.jpg','.jpeg','.pdf','.so','.o','.a','.rlib'}
PRIOR_CPU, PRIOR_WALL = 5.1939327, 5.209046969002007

def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def write_json(path,obj):
    path.write_bytes(encoded(obj))
def clock_check():
    if time.process_time() >= 5 or time.perf_counter()-START_WALL >= 10:
        raise RuntimeError('PACKAGING_PHASE_CAP_REACHED')
def cap_signal(signum,frame):
    raise RuntimeError('PACKAGING_PHASE_CAP_SIGNAL:'+str(signum))
def chosen(path):
    r=path.relative_to(UNIT)
    if not path.is_file() or path.is_symlink() or '__pycache__' in r.parts:
        return False
    if path.suffix in FORBIDDEN_SUFFIXES:
        return False
    return ((len(r.parts)==1 and path.name in ROOT_NAMES)
            or r.parts[0] in SCIENCE_ROOTS
            or (r.parts[0]=='intake' and len(r.parts)==2 and path.name in CURATED_INTAKE)
            or (r.parts[0]=='provider_inputs' and len(r.parts)==2 and path.name in CURATED_PROVIDER)
            or (r.parts[0]=='delivery' and len(r.parts)==2 and path.name in DELIVERY_NAMES))
def verify_inputs():
    provenance=json.loads((UNIT/'runtime_inputs/PROVENANCE.json').read_text())
    for name,row in provenance['files'].items():
        clock_check()
        path=(UNIT/name).resolve()
        assert path.is_relative_to(UNIT.resolve()),name
        raw=path.read_bytes()
        assert digest(raw)==row['sha256'],name
        if 'bytes' in row: assert len(raw)==row['bytes'],name
def package(phase, plan):
    required=ROOT_NAMES-{'README.md','REPRODUCE.md'}
    for name in required:
        assert (UNIT/name).is_file(),'MISSING_FINAL_ROOT:'+name
    assert (UNIT/'implementation/primary_electron.py').is_file()
    assert (UNIT/'implementation/TEST_BUDGET_LEDGER.json').is_file(),'MISSING_ACTUAL_LEDGER'
    assert list((UNIT/'implementation').rglob('*.npz')),'MISSING_ACTUAL_ATOMS_NPZ'
    verify_inputs()
    candidates=[p for p in sorted(UNIT.rglob('*')) if chosen(p)]
    rows=[]; public=[]; private=[]; binaries=[]
    for p in candidates:
        clock_check()
        raw=p.read_bytes(); rel=p.relative_to(UNIT).as_posix()
        row={'path':rel,'bytes':len(raw),'sha256':digest(raw)}
        private.append((rel,raw)); rows.append(row)
        if p.suffix in BINARY_SUFFIXES:
            binaries.append(row); continue
        try: content=raw.decode('utf-8')
        except UnicodeDecodeError:
            binaries.append(row); continue
        if '\x00' in content:
            binaries.append(row); continue
        public.append({'path':plan['allowed_path']+'/'+rel,'mode':'100644',
                       'type':'blob','content':content})
    assert any(r['path']=='runtime_inputs/endpoint/grid044_history.npz' for r in binaries)
    manifest={'unit_id':UNIT_ID,'phase':phase,'files':rows,
              'binary_companion_required_for_git_only_checkout':True,
              'scientific_evaluations':0,'restore_archives_included':False,
              'third_party_article_or_API_raw_included':False}
    staging=OUT/(phase+'_PUBLIC_MANIFEST.json')
    write_json(staging,{'unit_id':UNIT_ID,'files':[r for r in rows if r not in binaries],
                        'binary_companion_files':binaries,'publication':plan})
    write_json(OUT/(phase+'_GIT_TREE_PAYLOAD.json'),{
        'repository_full_name':plan['repository'],
        'tree_elements':public,
        'base_tree_sha':'CONTROLLER_MUST_SET_AFTER_FRESH_HEAD_READ'})
    zpath=OUT/(phase+'_PRIVATE_PORTABLE.zip')
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for rel,raw in private:
            clock_check(); z.writestr(UNIT.name+'/'+rel,raw)
        z.writestr('MANIFEST.json',encoded(manifest))
    with zipfile.ZipFile(zpath) as z:
        for row in rows:
            clock_check()
            assert digest(z.read(UNIT.name+'/'+row['path']))==row['sha256']
        assert set(z.namelist())=={UNIT.name+'/'+r['path'] for r in rows}|{'MANIFEST.json'}
        assert z.testzip() is None
    clock_check()
    return {'path':str(zpath),'bytes':zpath.stat().st_size,
            'sha256':digest(zpath.read_bytes()),'payload_members':len(rows),
            'archive_members':len(rows)+1,'member_hash_size_and_CRC':'pass_scoped',
            'public_text_files':len(public),'binary_companion_files':len(binaries)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('phase'); parser.add_argument('--go-file',required=True)
    a=parser.parse_args()
    assert a.phase.replace('_','').isalnum()
    go=json.loads(pathlib.Path(a.go_file).read_text())
    assert go.get('authorized') is True and go.get('unit_id')==UNIT_ID and go.get('phase')==a.phase
    path=OUT/(a.phase+'_PACKAGE_RECEIPT.json')
    assert not path.exists(),'PRESERVE_EXISTING_ATTEMPT'
    pc,pw=PRIOR_CPU,PRIOR_WALL
    for p in OUT.glob('*_PACKAGE_RECEIPT.json'):
        old=json.loads(p.read_text()); pc+=old['incremental_CPU_s']; pw+=old['incremental_wall_s']
    assert pc<30 and pw<60,'CUMULATIVE_PACKAGING_CAP'
    signal.signal(signal.SIGXCPU,cap_signal); signal.signal(signal.SIGALRM,cap_signal)
    resource.setrlimit(resource.RLIMIT_CPU,(5,6))
    signal.setitimer(signal.ITIMER_REAL,max(0.001,10-(time.perf_counter()-START_WALL)))
    result=None; error=None
    try:
        plan=json.loads((OUT/'PUBLICATION_PLAN.json').read_text())
        result=package(a.phase,plan)
        clock_check()
    except BaseException as exc:
        error=type(exc).__name__+': '+str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        cpu=time.process_time(); wall=time.perf_counter()-START_WALL
        status='failed' if error or cpu>=5 or wall>=10 or pc+cpu>=30 or pw+wall>=60 else 'completed'
        r={'unit_id':UNIT_ID,'phase':a.phase,'status':status,'error':error,'archive':result,
           'incremental_CPU_s':cpu,'incremental_wall_s':wall,
           'charged_prior_CPU_s':pc,'charged_prior_wall_s':pw,
           'charged_cumulative_CPU_s':pc+cpu,'charged_cumulative_wall_s':pw+wall,
           'campaign_caps':{'CPU_s':30,'wall_s':60},
           'phase_caps':{'CPU_s':5,'wall_s':10},'failed_attempts_charged':True,
           'CPU_accounting':'process CPU from interpreter startup including imports',
           'wall_accounting':'from earliest script clock; external launcher/network overhead UNKNOWN',
           'scientific_evaluations':0,'external_writes':0,'backup':'PENDING',
           'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        write_json(path,r); print(json.dumps(r))
    return 0 if status=='completed' else 1
if __name__=='__main__':
    sys.exit(main())

