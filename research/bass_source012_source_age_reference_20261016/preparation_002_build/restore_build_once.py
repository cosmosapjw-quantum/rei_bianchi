"""One authorized fresh private restore and offline build. Never execute helper."""
from pathlib import Path
import argparse,hashlib,json,os,resource,signal,subprocess,time,traceback,shutil
PUB=Path(__file__).resolve().parent
REPO=PUB.parents[2]
PRIVATE=Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016')
DEST=PRIVATE/'build_only_001'

def dump(name,value):
    with (PUB/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def sha(data):return hashlib.sha256(data).hexdigest()

def size(root):return sum(p.stat().st_size for p in root.rglob('*') if p.is_file())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--producer-commit',required=True);args=parser.parse_args()
    started=time.monotonic();epoch=time.time();deadline=started+180
    resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296))
    contract=json.loads((PUB/'CONTRACT.json').read_text());receipt={'status':'FAIL_STOP_NO_RETRY','unit_start_epoch':epoch,'producer_commit':args.producer_commit,'build_invocations':0,'helper_executions':0,'physical_RHS_calls':0,'helper':'NOT_RUN','setup':None,'Gamma':None,'heat':None,'prepared_nodes':None,'requested_model':'gpt-6.1-sol','requested_effort':'high','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED'}
    try:
        if DEST.exists():raise ValueError('fresh private destination already exists; stop')
        if len(args.producer_commit)!=40 or any(c not in '0123456789abcdef' for c in args.producer_commit):raise ValueError('exact producer commit required')
        helper=PUB.parent/'preparation_001/code'
        helpers={}
        for name,expected in contract['helper_sha256'].items():
            data=(helper/name).read_bytes()
            if sha(data)!=expected:raise ValueError('helper immutable SHA mismatch '+name)
            committed=subprocess.check_output(['git','show',args.producer_commit+':'+str((helper/name).relative_to(REPO))])
            if committed!=data:raise ValueError('helper producer commit bytes mismatch '+name)
            helpers[name]=data
        observed_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        env=dict(os.environ,CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='2',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
        versions={}
        for tool in ('cargo','rustc'):
            path=shutil.which(tool)
            if path is None:raise ValueError('missing installed tool '+tool)
            versions[tool]={'path':path,'version':subprocess.check_output([path,'--version'],text=True).strip()}
        dump('UNIT_STARTED.json',{'epoch':epoch,'producer_commit':args.producer_commit,'observed_HEAD':observed_head,'clock':'starts before restoration; wrapper creation/read-only preflight excluded, no physical execution','versions':versions,'AS_bytes':4294967296})
        DEST.mkdir() # create only after identity verification
        native=DEST/'native';crate=native/'rust/rei_microphysics';records=[]
        manifest=json.loads((PUB.parent/'intake_001/attempt_002/COLLECTION_MANIFEST.json').read_text())
        def copy(src,dst,expected,category):
            if time.monotonic()>=deadline:raise TimeoutError('entire 180s bound')
            data=src.read_bytes();digest=sha(data)
            if digest!=expected:raise ValueError('restore SHA mismatch '+str(src))
            dst.parent.mkdir(parents=True,exist_ok=True)
            if dst.exists():
                if dst.read_bytes()!=data:raise ValueError('overlapping restored bytes differ '+str(dst))
                overlap=True
            else:
                with dst.open('xb') as f:f.write(data)
                overlap=False
            records.append({'source':str(src),'destination':str(dst),'sha256':digest,'bytes':len(data),'category':category,'overlap_equal':overlap})
        for item in manifest['files']:
            cat=item['category']
            if cat=='native_base_source':copy(PRIVATE/'attempt_002/native_base'/item['path'],crate/item['path'],item['sha256'],cat)
            elif cat=='native_static_dependency':copy(PRIVATE/'attempt_002/native_static_dependencies'/item['path'],native/item['path'],item['sha256'],cat)
        supplement=json.loads((PUB.parent/'intake_002_static_supplement/repair_001/MANIFEST.json').read_text())
        entries=supplement.get('files')
        if entries is None:raise ValueError('supplement files missing')
        for item in entries:
            rel=item.get('path',item.get('source_path'))
            if rel not in ('configs/rei_fastest_v1/science_scenario_v1.json','docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json'):raise ValueError('unexpected supplement path')
            copy(PRIVATE/'static_supplement_001/repair_001'/rel,native/rel,item['copy_time_sha256'],'static_supplement')
        transport=crate/'src/axbi_covariant_transport.rs';base=transport.read_bytes()
        if sha(base)!=contract['transport_base_sha256'] or b'BEGIN RESEARCH_SOURCE_AGE_NODE_ACCESSOR' in base:raise ValueError('transport base/marker mismatch')
        accessor=(PRIVATE/'attempt_002/supplier/prepared_node_accessor.rs').read_bytes()
        if sha(accessor)!=contract['accessor_sha256']:raise ValueError('accessor mismatch')
        with transport.open('ab') as f:f.write(b'\n'+accessor)
        for name,data in helpers.items():
            dst=crate/'examples/source012_rhs'/name;dst.parent.mkdir(parents=True,exist_ok=True)
            with dst.open('xb') as f:f.write(data)
        cargo=crate/'Cargo.toml';original=cargo.read_bytes()
        with cargo.open('ab') as f:f.write(b'\n[[example]]\nname = "source012_rhs"\npath = "examples/source012_rhs/campaign.rs"\n')
        dump('RESTORATION_MANIFEST.json',{'files':records,'transport_before_sha256':sha(base),'transport_after_sha256':sha(transport.read_bytes()),'accessor_sha256':sha(accessor),'Cargo_before_sha256':sha(original),'Cargo_after_sha256':sha(cargo.read_bytes()),'helper_sha256':contract['helper_sha256'],'producer_commit':args.producer_commit,'lock_policy':'restored immutable lock unchanged','target_fresh':not(DEST/'target').exists()})
        if size(DEST)>1073741824 or size(PUB)>8388608:raise ValueError('pre-build storage cap')
        argv=[versions['cargo']['path'],'build','--release','--locked','--offline','--jobs','2','--example','source012_rhs','--target-dir',str(DEST/'target')]
        buildstart=time.monotonic();builddeadline=min(buildstart+150,deadline-1);term=False;kill=False;reason=None
        with (PUB/'raw/stdout').open('xb') as out,(PUB/'raw/stderr').open('xb') as err:
            child=subprocess.Popen(argv,cwd=crate,env=env,stdout=out,stderr=err,start_new_session=True)
            receipt['build_invocations']=1
            dump('raw/BUILD_STARTED.json',{'pid':child.pid,'argv':argv,'cwd':str(crate),'epoch':time.time(),'producer_commit':args.producer_commit,'HEAD':observed_head,'AS_bytes':4294967296,'build_cap_s':150,'unit_cap_s':180,'versions':versions,'env_overrides':{k:env[k] for k in ('CARGO_NET_OFFLINE','CARGO_BUILD_JOBS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},'environment':{k:env.get(k) for k in ('PATH','RUSTUP_TOOLCHAIN','RUSTFLAGS','CARGO_HOME','RUSTUP_HOME')}})
            print(json.dumps({'build_PID':child.pid,'argv':argv,'start_epoch':time.time()}),flush=True)
            while True:
                pid,status,usage=os.wait4(child.pid,os.WNOHANG)
                if pid:break
                now=time.monotonic();over=size(DEST)>1073741824 or size(PUB)>8388608
                if (now>=builddeadline-3 or over) and not term:
                    reason='RESOURCE_CAP' if over else 'WALL_CAP';os.killpg(child.pid,signal.SIGTERM);term=True
                if (now>=builddeadline-1 or (term and over)) and not kill:
                    os.killpg(child.pid,signal.SIGKILL);kill=True
                time.sleep(.05)
        child.returncode=os.waitstatus_to_exitcode(status)
        receipt.update(argv=argv,cwd=str(crate),exit_code=child.returncode,build_wall_seconds=time.monotonic()-buildstart,user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,peak_RSS_bytes=usage.ru_maxrss*1024,termination_reason=reason,producer_HEAD=observed_head,versions=versions)
        if child.returncode!=0 or reason is not None:raise RuntimeError('first build failure; stop')
        binary=DEST/'target/release/examples/source012_rhs';data=binary.read_bytes() # hash resulting ELF once
        elf={'path':str(binary),'bytes':len(data),'sha256':sha(data),'producer_commit':args.producer_commit,'native_base':contract['native_base'],'overlay':contract['supplier_overlay'],'helper_sha256':contract['helper_sha256'],'source_restoration_manifest':'RESTORATION_MANIFEST.json','executed':False,'hash_passes':1}
        dump('ELF_IDENTITY.json',elf)
        receipt['status']='SCOPED_BUILD_PREPARATION_PASS'
        receipt['private_bytes']=size(DEST);receipt['public_bytes_before_final_receipt']=size(PUB)
        if receipt['private_bytes']>1073741824 or receipt['public_bytes_before_final_receipt']>8388608:raise ValueError('final storage cap')
    except Exception as exc:
        receipt['status']='FAIL_STOP_NO_RETRY';receipt['error']=str(exc)
        (PUB/'raw/first_failure.txt').write_text(traceback.format_exc())
    receipt['entire_unit_wall_seconds']=time.monotonic()-started
    if receipt['entire_unit_wall_seconds']>180:receipt['status']='FAIL_STOP_NO_RETRY';receipt['whole_unit_limit_exceeded']=True
    dump('WRAPPER_RECEIPT.json',receipt)
    print(json.dumps(receipt),flush=True)
    return 0 if receipt['status']=='SCOPED_BUILD_PREPARATION_PASS' else 1
if __name__=='__main__':raise SystemExit(main())
