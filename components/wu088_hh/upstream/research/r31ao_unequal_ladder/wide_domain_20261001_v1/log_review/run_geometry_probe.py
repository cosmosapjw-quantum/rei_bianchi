"""Bounded independent pure interval diagnostic; no physical callbacks."""
from pathlib import Path
import hashlib, importlib.util, json, os, resource, subprocess, time

HERE=Path(__file__).resolve().parent
LADDER=HERE.parents[1]
PREFIX=Path('/workspace/scratch/6cf5f59cd2d1/native_execution_build/prefix')
PROVENANCE=PREFIX.parent/'BACKEND_BUILD_PROVENANCE.json'
GATE=LADDER/'host_synthetic_readiness_20261001_v1/provenance_gate.py'
FLAGS=['-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra']

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def caps():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024**2,16*1024**2))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))

def main():
    out=HERE/'geometry_runtime';out.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('log_review_backend',GATE)
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    backend=gate.verify_backend(PROVENANCE,PREFIX)
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C','LANG':'C','LD_LIBRARY_PATH':str(PREFIX/'lib'),'OMP_NUM_THREADS':'1'}
    source=HERE/'log_image_probe.cpp';binary=out/'probe'
    command=['/usr/bin/g++',*FLAGS,'-I'+str(PREFIX/'include'),str(source),'-L'+str(PREFIX/'lib'),
             '-Wl,-rpath,'+str(PREFIX/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
    record={'schema':'WU088_LOG_IMAGE_GEOMETRY_PROBE_RECEIPT_V1','source_sha256':sha(source),
            'runner_sha256':sha(__file__),'backend_provenance_sha256':sha(PROVENANCE),
            'backend_verified':backend['verification']['status'],'command':command,'flags':FLAGS,
            'compiler_sha256':sha(Path('/usr/bin/g++').resolve()),'precision_bits':[128,256],
            'memory_cap_bytes':512*1024**2,'build_wall_cap_seconds':30,'run_wall_cap_seconds':10,
            'affinity':sorted(os.sched_getaffinity(0)),'hh_callback_calls':0,'native_integral_runs':0}
    for stage,argv,wall in [('compile',command,30),('run',[str(binary)],10)]:
        start=time.monotonic_ns()
        with (out/(stage+'.stdout')).open('xb') as so,(out/(stage+'.stderr')).open('xb') as se:
            proc=subprocess.run(argv,stdout=so,stderr=se,env=env,timeout=wall,preexec_fn=caps)
        record[stage+'_exit_code']=proc.returncode;record[stage+'_nanoseconds']=time.monotonic_ns()-start
        if proc.returncode: break
        if stage=='compile':
            record['binary_sha256']=sha(binary)
            linkage=subprocess.check_output(['/usr/bin/ldd',str(binary)],env=env,text=True,timeout=10)
            (out/'linkage.log').write_text(linkage)
            record['linkage']=gate.verify_linkage(linkage,{name:item['binary_path'] for name,item in backend['libraries'].items()})
    if record.get('run_exit_code')==0: record['result']=json.loads((out/'run.stdout').read_text())
    record['source_unchanged']=record['source_sha256']==sha(source)
    record['backend_after']=gate.verify_backend(PROVENANCE,PREFIX)['verification']['status']
    with (out/'REVIEW_RUN.json').open('x') as f: json.dump(record,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(record.get('result',record),sort_keys=True))
    return record.get('run_exit_code',record['compile_exit_code'])

if __name__=='__main__': raise SystemExit(main())
