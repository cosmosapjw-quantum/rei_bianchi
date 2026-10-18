"""Code-only setup bridge. Real helper use requires future explicit owner launch.

No native helper is started on import or by the default CLI. The one current
verification uses a Python fake, immediate EOF, and synthetic protocol data.
"""
import argparse,hashlib,importlib.util,json,math,os,resource,signal,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
PREP=HERE.parent/'preparation_001/code/positive_reference.py'
PREP_SHA='87c85841e12b4265984a75fd5e82f7164a466b88800e51aa992029376bf0577a'
ELF_SHA='85d358f5223cedaa132f5e9e2d95ea0c1c7ea41d2f2c36fbd6358a20a7161d0a'
PRODUCER='6b976d00e548f84b02f51d32cd20ad265a0d9201'
BASE='35d9747a0bbedcafdb568467ce7c1e7a25f965b6';OVERLAY='553ce556d9f8662290c000ec675c7e6007c9d895'
ELF_PATH='/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/build_only_001/target/release/examples/source012_rhs'

class BridgeFailure(Exception):pass

def load_decoder():
    if hashlib.sha256(PREP.read_bytes()).hexdigest()!=PREP_SHA:raise BridgeFailure('immutable decoder SHA mismatch')
    name='source012_accepted_reference'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,PREP);module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module;spec.loader.exec_module(module)
    return sys.modules[name].decode_setup

def numeric(value):return type(value) in (float,int) and math.isfinite(value)

def validate_setup(record,expected_birth_count):
    """Validate raw arrays BEFORE the existing decoder's sort/dedup boundary."""
    if not isinstance(record,dict):raise BridgeFailure('setup is not an object')
    required={'protocol':'SOURCE012_RHS_ONLY_V1','native_base':BASE,'overlay':OVERLAY,
              'q':-.1,'birth_count':expected_birth_count,
              'state_order':'h,y,z,w_eV/H,cohort_N[],cohort_Uref[],...',
              'x_units':'dimensionless ln(a)','f_units':'nHe0/nH0','w_units':'eV/H',
              'kb_units':'eV/K','moment_units':'N/H,eV_reference/H',
              'source_config':'supplier_driver_q-0.1_nmu8_cells16_subdiv8_initial8000K',
              'observations_status':'NOT_RUN'}
    if expected_birth_count not in (8,16,32):raise BridgeFailure('unselected birth count')
    for key,value in required.items():
        if record.get(key)!=value:raise BridgeFailure('binding/units/state order mismatch: '+key)
    if type(record['birth_count']) is not int:raise BridgeFailure('birth count type')
    for key in ('Gamma_s','heat','prepared_nodes'):
        if key not in record or record[key] is not None:raise BridgeFailure('unexpected actual observation '+key)
    if not isinstance(record.get('config_debug'),str) or not record['config_debug']:raise BridgeFailure('missing native config identity')
    for key in ('x0','x1','width','quadrature_weight_dln_a','f','kb_eV_K','ev_erg'):
        if not numeric(record.get(key)):raise BridgeFailure('nonfinite constant '+key)
    x0,x1=record['x0'],record['x1'];n=expected_birth_count;cells=record.get('cells')
    if not (x0<x1 and record['width']==x1-x0 and record['quadrature_weight_dln_a']==record['width']/n):raise BridgeFailure('stored endpoint/weight inconsistency')
    if record['f']<=0 or record['kb_eV_K']<=0 or record['ev_erg']<=0:raise BridgeFailure('nonpositive EOS constant')
    if type(cells) is not int or cells<=0:raise BridgeFailure('invalid cells dimension')
    mesh=record.get('mesh');births=record.get('births')
    if not isinstance(mesh,list) or len(mesh)!=57 or not all(map(numeric,mesh)):
        raise BridgeFailure('shared native mesh dimension/nonfinite')
    if any(a>=b for a,b in zip(mesh,mesh[1:])):raise BridgeFailure('raw mesh order/duplicate before decode')
    if mesh[-1]!=x1 or not all(x0<x<=x1 for x in mesh):raise BridgeFailure('raw stored mesh endpoints/domain')
    if not isinstance(births,list) or len(births)!=n or not all(map(numeric,births)):
        raise BridgeFailure('birth dimension/nonfinite')
    if any(a>=b for a,b in zip(births,births[1:])) or not all(x0<b<x1 and b in mesh for b in births):raise BridgeFailure('exact birth/common mesh membership')
    initial=record.get('initial')
    if not isinstance(initial,list) or len(initial)!=4+2*cells*n or not all(map(numeric,initial)):
        raise BridgeFailure('initial state dimensions/nonfinite')
    if initial[:3]!=[.01,.01,.001] or any(initial[4:]):raise BridgeFailure('native initial fractions/unborn zeros')
    for key in ('inject','support_lo','support_hi'):
        if not isinstance(record.get(key),list) or len(record[key])!=n:raise BridgeFailure('cohort dimension '+key)
    for j in range(n):
        lo,hi,inc=record['support_lo'][j],record['support_hi'][j],record['inject'][j]
        if not all(isinstance(a,list) for a in (lo,hi,inc)) or len(lo)!=cells or len(hi)!=cells or len(inc)!=2*cells or not all(numeric(v) for a in (lo,hi,inc) for v in a):raise BridgeFailure('support/injection shape/nonfinite')
        for k in range(cells):
            number,energy=inc[k],inc[cells+k]
            if number<0 or lo[k]<0 or hi[k]<lo[k]:raise BridgeFailure('invalid injection support')
            if number==0:
                if energy!=0 or lo[k]!=0 or hi[k]!=0:raise BridgeFailure('empty native template support/moments')
            elif lo[k]<=0:raise BridgeFailure('nonempty support must have positive reference energy')
            if energy-lo[k]*number<0 or hi[k]*number-energy<0:raise BridgeFailure('injection mean outside fixed support')
            if lo[k]==hi[k] and energy!=lo[k]*number:raise BridgeFailure('degenerate exact support')
    # Native checks remain authoritative; decoder adds existing affine EOS/cones.
    try:decoded=load_decoder()(record)
    except Exception as exc:raise BridgeFailure('unchanged decoder domain rejection') from exc
    return {'status':'VALIDATED_SETUP_ONLY','birth_count':n,'cells':cells,'state_size':len(initial),
            'raw_mesh':mesh.copy(),'decoded_mesh_has_initial_x0':decoded[2]==tuple([x0]+mesh),
            'x0':x0,'x1':x1,'raw_mesh_preserved':True,'RHS_requests':0,
            'Gamma':None,'heat':None,'prepared_nodes':None}

def parse_stdout(raw,expected_birth_count):
    # One original line/object only; never select a convenient line from noise.
    lines=raw.decode('utf-8',errors='strict').splitlines()
    if len(lines)!=1 or not lines[0]:raise BridgeFailure('malformed or multiple setup output lines')
    try:record=json.loads(lines[0],parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite JSON '+value)))
    except Exception as exc:raise BridgeFailure('malformed JSON') from exc
    return record,validate_setup(record,expected_birth_count)

def collect(argv,outdir,expected_birth_count,*,wall_cap=10,output_cap=16777216,unit_deadline=None):
    """Capture first, reap, then parse; stdin DEVNULL ensures zero requests."""
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();deadline=min(start+wall_cap,unit_deadline if unit_deadline is not None else math.inf)
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
        resource.setrlimit(resource.RLIMIT_FSIZE,(output_cap,output_cap))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    with (outdir/'stdout').open('xb') as out,(outdir/'stderr').open('xb') as err:
        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,preexec_fn=limits,start_new_session=True)
        started={'argv':argv,'pid':child.pid,'start_epoch':time.time(),'stdin':'DEVNULL','AS_bytes':1073741824,'wall_cap_s':wall_cap,'output_cap_bytes':output_cap,'derivative_requests':0}
        (outdir/'STARTED.json').write_text(json.dumps(started,indent=2)+'\n')
        reason=None;term=False;kill=False
        while True:
            pid,status,usage=os.wait4(child.pid,os.WNOHANG)
            if pid:break
            now=time.monotonic();size=sum(p.stat().st_size for p in outdir.iterdir() if p.is_file())
            if (now>=deadline-2 or size>=output_cap) and not term:
                reason='OUTPUT_CAP' if size>=output_cap else 'WALL_CAP';os.killpg(child.pid,signal.SIGTERM);term=True
            if now>=deadline-1 and not kill:os.killpg(child.pid,signal.SIGKILL);kill=True
            time.sleep(.005)
    child.returncode=os.waitstatus_to_exitcode(status)
    receipt={'argv':argv,'exit_code':child.returncode,'wall_seconds':time.monotonic()-start,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'peak_RSS_bytes':usage.ru_maxrss*1024,'termination_reason':reason,'stdin':'DEVNULL','derivative_requests':0}
    (outdir/'PROCESS_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if child.returncode!=0 or reason is not None:raise BridgeFailure('first helper process failure/cap')
    if sum(p.stat().st_size for p in outdir.iterdir() if p.is_file())>output_cap:
        raise BridgeFailure('aggregate process output cap')
    try:
        record,validation=parse_stdout((outdir/'stdout').read_bytes(),expected_birth_count)
    except Exception as exc:
        (outdir/'VALIDATION_FAILURE.json').write_text(json.dumps({'status':'FAIL_STOP_NO_RETRY','error':str(exc),'raw_preserved':True,'derivative_requests':0},indent=2)+'\n')
        raise
    (outdir/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    return record,validation,receipt

def plan(output_root):
    return {'scope':'PROPOSED_NOT_AUTHORIZED_REAL_SETUP','helper_candidate_sha256':ELF_SHA,'helper_bytes':908120,'producer_commit':PRODUCER,
            'build_receipt':str(HERE.parent/'preparation_002_build/WRAPPER_RECEIPT.json'),
            'commands':[{'argv':[ELF_PATH,'source_rhs','-0.1',str(n)],'stdin':'DEVNULL','output':str(Path(output_root)/('birth_'+str(n))),'wall_cap_s_including_termination':10} for n in (8,16,32)],
            'sequential':True,'total_wall_s':30,'AS_bytes':1073741824,'aggregate_output_bytes':16777216,'derivative_requests':0,'Gamma':None,'heat':None,'prepared_nodes':None,
            'requires':'independently accepted build and bridge + explicit owner authorization; not granted by preparation'}

def run_owner_approved(output_root):
    """Future owner-authorized use ONLY. Never called by preparation tests."""
    root=Path(output_root)
    if root.exists():raise BridgeFailure('future setup output root must be fresh')
    # Revalidate actual launch candidate once; never substitute captured old ELF.
    identity=json.loads((HERE.parent/'preparation_002_build/ELF_IDENTITY.json').read_text())
    if identity['sha256']!=ELF_SHA or identity['bytes']!=908120 or identity['producer_commit']!=PRODUCER or identity['path']!=ELF_PATH:raise BridgeFailure('producer/ELF receipt mismatch')
    raw=Path(ELF_PATH).read_bytes()
    if len(raw)!=908120 or hashlib.sha256(raw).hexdigest()!=ELF_SHA:raise BridgeFailure('actual launch ELF mismatch')
    root.mkdir();start=time.monotonic();results=[]
    for n in (8,16,32):
        used=sum(f.stat().st_size for f in root.rglob('*') if f.is_file());remaining=16777216-used
        if remaining<=0:raise BridgeFailure('aggregate output cap')
        results.append(collect([ELF_PATH,'source_rhs','-0.1',str(n)],root/('birth_'+str(n)),n,output_cap=remaining,unit_deadline=start+30))
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',required=True);parser.add_argument('--execute-owner-approved',action='store_true')
    args=parser.parse_args()
    if args.execute_owner_approved:run_owner_approved(args.output_root)
    else:print(json.dumps(plan(args.output_root),indent=2))
