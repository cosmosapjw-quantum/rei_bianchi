"""New attempt66 source/incident extraction only. Zero gas/SIGMA evaluations."""
from pathlib import Path
import hashlib,json,sys,time,shutil
import numpy as np
HERE=Path(__file__).resolve().parent
Q1B=HERE.parents[2];REPO=Q1B.parents[2]
for path in (Q1B,Q1B.parent/'n1',HERE.parent/'source_candidate'):
    sys.path.insert(0,str(path))
from provider import HistoryProvider
from grid_cells import load_grid
from source_cells import CellSource
import source_precision_v2 as source_api
from reconstruction import reconstruct


def main():
    out=HERE/'evidence/EXTRACT66';out.mkdir(exist_ok=False)
    attempt=Q1B/'c12/evidence/C2_FULL002/RUN/ATTEMPTS/attempt-00000066'
    request=json.loads((attempt/'MAP_01_REQUEST.json').read_text())
    for key,digest in request['dependency_closure'].items():
        path=REPO/key.removeprefix('dependency:')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('PIN_CHANGED:'+key)
    shutil.copy2(attempt/'MAP_01_REQUEST.json',out/'ORIGINAL_REQUEST.json')
    shutil.copy2(attempt/'MAP_01_INPUT.npz',out/'ORIGINAL_INPUT.npz')
    shutil.copy2(Q1B/'c12/evidence/C2_FULL002/RUN/CHUNKS/chunk-00000009/RESULT.json',out/'ORIGINAL_FAILURE.json')
    asrun=out/'ASRUN';asrun.mkdir()
    for path in (Path(__file__),HERE.parent/'source_candidate/source_precision_v2.py',Q1B/'c10/positive_absorption.py',Q1B/'c11/endpoint/native_coordinate_absorption.py',Q1B/'reconstruction.py'):
        shutil.copy2(path,asrun/path.name)
    provider=HistoryProvider(r=0.);source=CellSource(provider,load_grid(Q1B/'GRID_C2.json'))
    with np.load(attempt/'MAP_01_INPUT.npz') as saved:
        N=saved['N'].copy();U=saved['U_eV'].copy();gas=saved['gas'].copy()
    t0,t1=request['t0_s'],request['t1_s'];start=time.monotonic()
    events=source_api.provider_event_times(source,t0,t1)
    integrated=source_api.integrate_source(source,t0,t1,event_times=events)
    incident=source_api.advance_source(N,U,integrated)
    _,mu,R=provider.ray(np.ones(len(source.mu)),source.mu,t1)
    a,j=0,66
    parameters=dict(N=float(incident['N'][a,j]),U=float(incident['U_eV'][a,j]),R=float(R[a]),a=float(source.edges[j]),b=min(float(source.edges[j+1]),50000./R[a]))
    cell=reconstruct(**parameters)
    split=54.42/cell.R
    geom=provider.geometry(t1)
    result=dict(schema='rei.c12.opacity.failure66.extraction.v1',source_sha256=hashlib.sha256(Path(source_api.__file__).read_bytes()).hexdigest(),request_sha256=hashlib.sha256((attempt/'MAP_01_REQUEST.json').read_bytes()).hexdigest(),source_events_s=list(events),source_diagnostics=integrated['diagnostics'],source_pairing=incident['diagnostics'],parameters=parameters,closure=dict(p=cell.p,mean_q=cell.mean_q,status=cell.status,threshold_q=split,threshold_probability=cell.cdf(split),log_width=float(np.log(cell.b/cell.a)),coordinate_indicator=32*np.spacing(cell.b)/min(cell.mean_q-cell.a,cell.b-cell.mean_q)),t0_s=t0,t1_s=t1,h_s=t1-t0,gas=gas.tolist(),geometry=geom,native_gas_calls=0,native_sigma_calls=0,elapsed_s=time.monotonic()-start)
    np.savez_compressed(out/'INCIDENT.npz',N=incident['N'],U_eV=incident['U_eV'],R=R,source_dN=integrated['dN'])
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
