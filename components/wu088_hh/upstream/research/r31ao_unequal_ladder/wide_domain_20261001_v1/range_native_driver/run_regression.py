"""Compile/run only the analytic regression against one hash-recorded host TU."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
def identity(path):
    path=Path(path).resolve();b=path.read_bytes()
    return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--host-mode',choices=('old','range'),required=True)
    ap.add_argument('--prefix',required=True);ap.add_argument('--provenance',required=True)
    ap.add_argument('--output-dir',required=True);args=ap.parse_args()
    spec=importlib.util.spec_from_file_location('refined_synthetic_driver',HERE/'driver.py')
    driver=importlib.util.module_from_spec(spec);sys.modules[spec.name]=driver;spec.loader.exec_module(driver)
    _,gate=driver.dependencies();prefix=Path(args.prefix).resolve()
    backend=gate.verify_backend(Path(args.provenance).resolve(),prefix)
    host=HERE/'range_petras.cpp' if args.host_mode=='range' else HERE.parent/'diagnostic_native_driver/diagnostic_petras.cpp'
    out=Path(args.output_dir).resolve();out.mkdir(exist_ok=False)
    compiler=Path(shutil.which('g++')).resolve();binary=out/'synthetic'
    flags=['-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror']
    command=[str(compiler),*flags,'-DWU088_RANGE_HOST='+str(int(args.host_mode=='range')),str(host),
             '-I'+str(prefix/'include'),str(HERE/'range_regression.cpp'),
             str(driver.OLD/'validated_callback/callback.cpp'),'-L'+str(prefix/'lib'),
             '-Wl,-rpath,'+str(prefix/'lib'),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix/'lib'),
         'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
    receipt={'schema':'WU088_LOG2_ANALYTIC_EXECUTION_V1','hh_evaluations':0,'scientific_admission':False,
             'sources':[identity(host),identity(HERE/'range_regression.cpp'),identity(HERE/'range_petras.hpp'),identity(HERE/'diagnostics.hpp'),identity(driver.OLD/'validated_callback/callback.cpp')],
             'compiler':identity(compiler),'command':command,'precision_bits':128,
             'process_limits':{'address_space_bytes':512*1024*1024,'output_bytes':1024*1024,'run_wall_seconds':20}}
    def caps():
        resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(1024*1024,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    for stage,cmd,wall in [('build',command,60),('run',[str(binary)],20)]:
        if stage=='run':
            ldd=subprocess.run(['/usr/bin/ldd',str(binary)],env=env,capture_output=True,text=True,timeout=10,check=True)
            (out/'linkage.log').write_text(ldd.stdout)
            linkage=gate.verify_linkage(ldd.stdout,{n:v['binary_path'] for n,v in backend['libraries'].items()})
            for name,item in linkage['libraries'].items():
                if item['sha256']!=backend['libraries'][name]['binary_sha256']:raise ValueError('linked byte chain mismatch')
            receipt['linkage']=linkage;receipt['binary']=identity(binary)
        with (out/(stage+'.stdout')).open('xb') as so,(out/(stage+'.stderr')).open('xb') as se:
            result=subprocess.run(cmd,env=env,stdout=so,stderr=se,timeout=wall,check=False,preexec_fn=caps)
        receipt[stage]={'returncode':result.returncode,'stdout':identity(out/(stage+'.stdout')),'stderr':identity(out/(stage+'.stderr'))}
        if stage=='build' and result.returncode:break
    if 'run' in receipt:
        try:receipt['result']=json.loads((out/'run.stdout').read_text())
        except ValueError:receipt['result']={'status':'FAILED_NONJSON_OUTPUT'}
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(out),'build':receipt['build']['returncode'],'run':receipt.get('run',{}).get('returncode'),'result':receipt.get('result')}))
    return receipt.get('run',receipt['build'])['returncode']
if __name__=='__main__':raise SystemExit(main())
