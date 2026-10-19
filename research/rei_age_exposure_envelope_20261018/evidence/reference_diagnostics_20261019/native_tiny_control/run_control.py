from pathlib import Path
import sys,os,shutil,hashlib,json,platform
root=Path('/workspace/scratch/36ed695112a9/rei_bianchi/research/rei_age_exposure_envelope_20261018')
sys.path.insert(0,str(root/'src'))
from build_refined_sources import overlay
from reference_diagnostics import transform_solver, transform_identity,COMPUTATIONAL_BASE_SHA
from run_refinement import sha,save,command,run_process,validate_outputs
import numpy,scipy
base=Path('/workspace/scratch/36ed695112a9/intake_backups/session_20261019T0933Z/B1_extracted/REI_AGE64_BLOCKMAX_NCP_20261019T084150Z/run/native')
out=root/'evidence/reference_diagnostics_20261019/native_tiny_control'
out.mkdir(parents=True,exist_ok=False)
binary=out/'positive_native.bin'
expected='89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4'
assert sha(base/'positive_native.bin')==expected
shutil.copyfile(base/'positive_native.bin',binary); binary.chmod(0o755)
assert sha(binary)==expected
_,source=overlay((root/'donors/pr171/positive_native.rs').read_bytes(),(root/'donors/pr171/positive_solver.py').read_bytes())
source=source.encode();assert hashlib.sha256(source).hexdigest()==COMPUTATIONAL_BASE_SHA
assert source==(base/'positive_solver_refined.py').read_bytes()
solvers={'off':out/'reference_solver_base.py','on':out/'reference_solver_diagnostics.py'}
solvers['off'].write_bytes(source);solvers['on'].write_bytes(transform_solver(source))
config=dict(name='tiny_observer_control',kind='reference',q=0.,birth_panels=2,n_mu=8,source_subdivisions=8,transport_cells=8,common_birth_levels=[8,16,32,64],time_factor=1,tight=False,rpc_mode='binary64',error_norm='block-max')
identity=dict(native_sha='35d9747a0bbedcafdb568467ce7c1e7a25f965b6',binary_sha=sha(binary),computational_base_solver_sha=COMPUTATIONAL_BASE_SHA,diagnostic_transform_sha=transform_identity(),executed_source_sha={k:sha(v) for k,v in solvers.items()},python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,transport_threads=1,base_binary_source=str(base/'positive_native.bin'))
save(out/'CONFIG.json',dict(config=config,identity=identity,case_wall_s=60,max_rhs=200000,authorization='ONE_NATIVE_TINY_OFF_ON_PAIR',campaign_status='NOT_ISSUED',rhs_byte_stream='NOT_RECORDED; no existing native wrapper stream capture'))
os.environ['REI_TRANSPORT_THREADS']='1'
for mode in ('off','on'):
    case=dict(config)
    if mode=='on':case['reference_diagnostics']=True
    data=out/mode/'data';data.mkdir(parents=True)
    argv=command(case,binary,solvers[mode],data,60.,200000)
    receipt=run_process(argv,out/mode,60.)
    receipt.update(mode=mode,config=case,identity=identity)
    if receipt['exit_code']==0:
        try:validate_outputs(case,data);receipt['validation']='PASS'
        except Exception as exc:receipt['validation']='FAIL';receipt['validation_error']=repr(exc)
    else:receipt['validation']='NOT_RUN_NONZERO_EXIT'
    receipt['outputs']={str(p.relative_to(out/mode)):sha(p) for p in sorted((out/mode).rglob('*')) if p.is_file() and p.name!='RECEIPT.json'}
    save(out/mode/'RECEIPT.json',receipt)
    print(json.dumps(dict(mode=mode,exit_code=receipt['exit_code'],timed_out=receipt['timed_out'],wall_s=receipt['wall_s'],validation=receipt['validation'])),flush=True)
    if receipt['exit_code']!=0 or receipt['validation']!='PASS':break
