"""Nine fixed actual callback range queries, no integration or candidate change."""
from pathlib import Path
import hashlib,importlib.util,json,os,resource,subprocess,time
HERE=Path(__file__).resolve().parent
NEW=HERE.parents[1];BASE=NEW.parent
PREFIX=Path('/workspace/scratch/6cf5f59cd2d1/native_execution_build/prefix')
PROVENANCE=PREFIX.parent/'BACKEND_BUILD_PROVENANCE.json'
GATE=BASE/'host_synthetic_readiness_20261001_v1/provenance_gate.py'
BUILD=NEW/'runtime/build_log_cached'
FLAGS=['-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1024**2,1024**2))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
    out=HERE/'runtime';out.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('preflight_diagnostic_backend',GATE)
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    backend=gate.verify_backend(PROVENANCE,PREFIX)
    manifest=json.loads((BUILD/'BUILD.json').read_text())
    assert manifest['source']['sha256']=='faf2525e0270d38db7873380f84264a15e89f64568033727fd7724204f5e840c'
    assert sha(BUILD/'frozen107_generated.hpp')==manifest['generated_header_sha256']
    sources=[HERE/'probe.cpp',BASE/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.cpp',BASE/'gap_closure_20261001_g0_g6_v1/validated_callback/assembly.cpp']
    pins={str(BASE/p):h for p,h in manifest['source']['files'].items()}
    pins.update({str(p):sha(p) for p in [*sources,BUILD/'frozen107_generated.hpp',Path(__file__)]})
    for path,h in pins.items():assert sha(path)==h,path
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C','LANG':'C','LD_LIBRARY_PATH':str(PREFIX/'lib'),'OMP_NUM_THREADS':'1'}
    binary=out/'probe'
    command=['/usr/bin/g++',*FLAGS,'-I'+str(PREFIX/'include'),'-I'+str(BUILD),'-I'+str(BASE/'gap_closure_20261001_g0_g6_v1/validated_callback'),*[str(p) for p in sources],'-L'+str(PREFIX/'lib'),'-Wl,-rpath,'+str(PREFIX/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
    record={'schema':'WU088_ACTUAL_CALLBACK_PREFLIGHT_DIAGNOSTIC_RECEIPT_V1','sources':pins,'compiler_sha256':sha(Path('/usr/bin/g++').resolve()),'command':command,'flags':FLAGS,'build_manifest_sha256':manifest['manifest_sha256'],'backend_provenance_sha256':sha(PROVENANCE),'backend_before':backend['verification']['status'],'memory_cap_bytes':1024**3,'compile_wall_cap_seconds':60,'run_wall_cap_seconds':15,'actual_hh_integrals':0,'affinity':sorted(os.sched_getaffinity(0)),'scientific_admission':False,'production_admission':False}
    for stage,argv,wall in [('compile',command,60),('run',[str(binary)],15)]:
        start=time.monotonic_ns()
        with (out/(stage+'.stdout')).open('xb') as so,(out/(stage+'.stderr')).open('xb') as se:
            proc=subprocess.run(argv,stdout=so,stderr=se,env=env,timeout=wall,preexec_fn=limits)
        record[stage+'_exit_code']=proc.returncode;record[stage+'_elapsed_ns']=time.monotonic_ns()-start
        if proc.returncode:break
        if stage=='compile':
            record['binary_sha256']=sha(binary)
            linked=subprocess.check_output(['/usr/bin/ldd',str(binary)],env=env,text=True,timeout=10)
            (out/'linkage.log').write_text(linked)
            record['linkage']=gate.verify_linkage(linked,{k:v['binary_path'] for k,v in backend['libraries'].items()})
    if record.get('run_exit_code')==0:
        record['result']=json.loads((out/'run.stdout').read_text())
        assert record['result']['actual_hh_callback_evaluations']==9 and record['result']['actual_hh_integrals']==0
    record['log_sha256']={p.name:sha(p) for p in out.iterdir() if p.suffix in ('.stdout','.stderr','.log')}
    record['sources_unchanged']=all(sha(p)==h for p,h in pins.items())
    record['backend_after']=gate.verify_backend(PROVENANCE,PREFIX)['verification']['status']
    with (out/'REVIEW_RUN.json').open('x') as f:json.dump(record,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(record.get('result',record),sort_keys=True))
    return record.get('run_exit_code',record['compile_exit_code'])
if __name__=='__main__':raise SystemExit(main())
