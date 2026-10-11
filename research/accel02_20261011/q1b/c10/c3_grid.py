"""Create-only C3: one logarithmic bisection of the pinned durable C2."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
Q1B=HERE.parent
sys.path.insert(0,str(Q1B))
from grid_cells import grid_array_sha256

PINNED_C2_SHA256='409a584cc4ee863dee97cd5fba60486abfd50be63a9c0955a258aeae755bffa0'


def build_c3(c2):
    if (c2['member']!='C2' or c2['energy_cells']!=174
            or c2['angular_ordinates']!=2 or c2['total_cells']!=348):
        raise ValueError('C3_BASELINE_NOT_C2_174_BY_2')
    edges=np.asarray(c2['q_edges_eV'],float)
    mu=np.asarray(c2['initial_mu'],float)
    weights=np.asarray(c2['angular_weights'],float)
    if grid_array_sha256(edges,mu,weights)!=c2['arrays_sha256']:
        raise ValueError('C3_BASELINE_ARRAY_IDENTITY')
    if len(edges)!=175 or not np.isfinite(edges).all() or np.any(edges<=0) or np.any(np.diff(edges)<=0):
        raise ValueError('C3_BASELINE_EDGES_DOMAIN')
    refined=np.empty(2*len(edges)-1)
    refined[::2]=edges
    refined[1::2]=np.exp(.5*(np.log(edges[:-1])+np.log(edges[1:])))
    if not np.all(np.diff(refined)>0):
        raise ValueError('C3_BISECTION_PRECISION_COLLAPSE')
    result=dict(c2)
    result.update(member='C3',energy_cells=348,total_cells=696,
        q_edges_eV=refined.tolist(),arrays_sha256=grid_array_sha256(refined,mu,weights),
        construction='Exactly one logarithmic bisection of each immutable C2 energy cell; inherited two angles and all physical edges retained verbatim.',
        parent_member='C2',parent_arrays_sha256=c2['arrays_sha256'],
        frozen=True,scope='New C2/C3 local comparison only; no whole-history admission')
    return result


def freeze_c3(source=Q1B/'GRID_C2.json',output=HERE/'GRID_C3.json'):
    source,output=Path(source),Path(output)
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINNED_C2_SHA256:
        raise ValueError('C3_PINNED_C2_FILE_IDENTITY')
    result=build_c3(json.loads(raw))
    result['parent_grid_file_sha256']=PINNED_C2_SHA256
    result['grid_implementation_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with output.open('x') as handle:
        json.dump(result,handle,indent=2,allow_nan=False)
        handle.write('\n')
    return result


if __name__=='__main__':
    result=freeze_c3()
    print(json.dumps({'member':result['member'],'energy_cells':result['energy_cells'],
        'total_cells':result['total_cells'],'arrays_sha256':result['arrays_sha256']}))
