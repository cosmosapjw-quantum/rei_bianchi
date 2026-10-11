"""Read exact rejected cell receipt; no source, SIGMA, gas, or map execution."""
from pathlib import Path
import hashlib,json,sys,shutil
import numpy as np
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2];REPO=Q1B.parents[2]
sys.path.insert(0,str(Q1B))
from reconstruction import reconstruct

def main():
    out=HERE/'evidence/EXTRACT67';out.mkdir(exist_ok=False)
    attempt=Q1B/'c12/evidence/C2_FULL003/RUN/ATTEMPTS/attempt-00000067'
    request=json.loads((attempt/'MAP_01_REQUEST.json').read_text())
    for key,digest in request['dependency_closure'].items():
        if hashlib.sha256((REPO/key.removeprefix('dependency:')).read_bytes()).hexdigest()!=digest:raise ValueError('PIN_CHANGED:'+key)
    receipt=json.loads((attempt/'MAP_01_ABSORPTION_REFINEMENTS.json').read_text())
    records=receipt['records']
    if len(records)!=1 or records[0]['status']!='REFINEMENT_FAILED_CLOSED':raise ValueError('EXPECTED_EXACT_FAILED_REFINEMENT')
    params=records[0]['parameters'];cell=reconstruct(**params)
    for name in ('MAP_01_REQUEST.json','MAP_01_INPUT.npz','MAP_01_ABSORPTION_REFINEMENTS.json'):shutil.copy2(attempt/name,out/name)
    with np.load(attempt/'MAP_01_INPUT.npz') as inp:gas=inp['gas'].tolist()
    sys.path.insert(0,str(Q1B.parent/'n1'))
    from provider import HistoryProvider
    g=HistoryProvider(r=0.).geometry(request['t1_s'])
    L=float(np.log1p((cell.b-cell.a)/cell.a))
    result=dict(schema='rei.c12.opacity.failure67.receipt.v1',parameters=params,p=cell.p,mean_q=cell.mean_q,L=L,pL=cell.p*L,threshold_q=54.42/cell.R,threshold_cdf=cell.cdf(54.42/cell.R),t0_s=request['t0_s'],t1_s=request['t1_s'],h_s=request['t1_s']-request['t0_s'],gas=gas,geometry=g,original_failures=records,dependencies_verified=len(request['dependency_closure']),source_calls=0,native_sigma_calls=0,native_gas_calls=0,whole_maps=0)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
