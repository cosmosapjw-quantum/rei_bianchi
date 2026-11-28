"""One bounded reference force evaluation at a failed scientific-gate geometry.
No new eigensolve, native evaluation, quadrature order or refinement.
"""
import hashlib,json,os,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
sys.path.insert(0,str(ROOT/'code'))
from state_io import load_pair
from coupling import torque
pair=ROOT/'evidence/PROLATE_MPI/R16_h/STATE.npz'
record=ROOT/'evidence/PROLATE_MPI/R16_h/RESULT.json'
stored=json.loads(record.read_text())
actual_sha=hashlib.sha256(pair.read_bytes()).hexdigest()
if actual_sha!=stored['state_sha256']:
    raise RuntimeError('stored state identity mismatch')
g,b=load_pair(pair)
if g.R!=16.0 or b.R!=16.0 or stored['task_id']!='R16_h':
    raise ValueError('requires frozen R16_h pair')
start=time.perf_counter()
reference=torque(g,b,order=28)
wall=time.perf_counter()-start
native=stored['operators']['torque']['28']
differences={k:abs(v-native[k]) for k,v in reference.items() if isinstance(v,float)}
result={'scope':'one reference force q28 evaluation on frozen R16_h state; stored native result reused',
 'reference':reference,'stored_native':native,'differences':differences,
 'max_abs_difference':max(differences.values()),'tolerance_abs':1e-11,
 'passed':max(differences.values())<=1e-11,'reference_seconds':wall,
 'state_sha256':actual_sha,'stored_result_sha256':hashlib.sha256(record.read_bytes()).hexdigest(),
 'reference_source_sha256':hashlib.sha256((ROOT/'reference/coupling.py').read_bytes()).hexdigest(),
 'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'native_backend_identity':stored['backend'],
 'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),
 'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),
 'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
 'interpretation':'Implementation parity only; does not change or close the failed C2 scientific force/convergence gate.'}
with (ROOT/'review/PROLATE_OPTIMIZATION_R16_FORCE_PARITY.json').open('x') as f:
    json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'passed':result['passed'],'differences':differences,'reference_seconds':wall},indent=2))
assert result['passed']
