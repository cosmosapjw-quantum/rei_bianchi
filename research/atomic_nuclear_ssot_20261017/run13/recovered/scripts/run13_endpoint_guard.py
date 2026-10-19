"""Admit a COMPLETE event-resolved endpoint, never a partial checkpoint.

This validates file/protocol consistency, not physical or continuum accuracy.
No input, solver tolerance or state is modified by this reader.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

def load_complete(root: Path, m: int, rtol: float) -> tuple[dict,np.ndarray]:
    root=Path(root);folder=root/'evidence'/f'joint11_sided_m{m}_{rtol:.0e}'
    packetfile=root/f'inputs/spectral11/m{m}.json'
    packet=json.loads(packetfile.read_text());sha=hashlib.sha256(packetfile.read_bytes()).hexdigest()
    events=json.loads((root/f'inputs/spectral11/m{m}_events.json').read_text())
    record=json.loads((folder/'checkpoint.json').read_text());points=np.array(events['points'])
    if record.get('status')!='COMPLETE' or record.get('next_segment')!=len(points)-1 or len(record.get('segments',[]))!=len(points)-1:
        raise ValueError('incomplete event trajectory')
    if record.get('packet_sha256')!=sha or events.get('packet_sha256')!=sha:
        raise ValueError('packet identity mismatch')
    if record.get('rtol')!=rtol:
        raise ValueError('solver control mismatch')
    if points.ndim!=1 or not np.isfinite(points).all() or points[0]!=0. or points[-1]!=1. or np.any(np.diff(points)<=0):
        raise ValueError('invalid event partition')
    segments=np.array([row[:2] for row in record['segments']])
    if not np.array_equal(segments,np.column_stack((points[:-1],points[1:]))):
        raise ValueError('event partition mismatch')
    filename=record.get('state_file','')
    if not filename or Path(filename).name!=filename:
        raise ValueError('invalid state filename')
    statefile=folder/filename
    if hashlib.sha256(statefile.read_bytes()).hexdigest()!=record.get('state_sha256'):
        raise ValueError('state hash mismatch')
    with np.load(statefile,allow_pickle=False) as data:state=data['state'].copy()
    with np.load(folder/'endpoint.npz',allow_pickle=False) as data:endpoint=data['state'].copy()
    dim=record.get('dimension');nphysical=len(packet['cohorts'])
    if dim!=events['dimension'] or dim!=nphysical//2+37 or nphysical%2 or record.get('physical_cohorts')!=nphysical:
        raise ValueError('dimension/physical support mismatch')
    if state.shape!=(dim,) or not np.isfinite(state).all() or not np.array_equal(state,endpoint):
        raise ValueError('endpoint is not the committed finite state')
    if np.any(state[:13]<0.) or state[13]<=0. or np.any(state[27:dim-10]<-1e-12):
        raise ValueError('endpoint state domain violation')
    if json.loads((folder/'result.json').read_text())!=record:
        raise ValueError('endpoint result/commit marker mismatch')
    if not all(np.isfinite(float(v)) for v in record['observable'].values()):
        raise ValueError('nonfinite observable')
    return record,state

def load_sealed_parent(root: Path,m: int,rtol: float,manifest_path: Path) -> tuple[dict,np.ndarray]:
    """Read an immutable parent endpoint sealed by its original manifest.

    Parent archives intentionally need not contain resumable checkpoint metadata.
    This is a different evidence form, never an implicit fallback for new runs.
    """
    root=Path(root);manifest={}
    for line in Path(manifest_path).read_text().splitlines():
        digest,name=line.split(maxsplit=1);manifest[name.lstrip('*')]=digest
    folder=root/'evidence'/f'joint11_sided_m{m}_{rtol:.0e}'
    paths=[folder/'result.json',folder/'endpoint.npz',root/f'inputs/spectral11/m{m}.json',root/f'inputs/spectral11/m{m}_events.json']
    for path in paths:
        key=path.relative_to(root).as_posix()
        if key not in manifest or hashlib.sha256(path.read_bytes()).hexdigest()!=manifest[key]:
            raise ValueError('sealed parent file hash mismatch: '+key)
    result=json.loads(paths[0].read_text());packet=json.loads(paths[2].read_text());events=json.loads(paths[3].read_text());points=np.asarray(events['points'])
    if result['status']!='COMPLETE' or result['next_segment']!=len(points)-1 or len(result['segments'])!=len(points)-1:
        raise ValueError('incomplete sealed parent endpoint')
    if not np.array_equal(np.asarray([v[:2] for v in result['segments']]),np.column_stack((points[:-1],points[1:]))):
        raise ValueError('sealed parent event partition mismatch')
    sha=hashlib.sha256(paths[2].read_bytes()).hexdigest()
    if result['packet_sha256']!=sha or events['packet_sha256']!=sha or result['rtol']!=rtol:
        raise ValueError('sealed parent source/control mismatch')
    with np.load(paths[1],allow_pickle=False) as data:state=data['state'].copy()
    if state.shape!=(events['dimension'],) or state.shape!=(len(packet['cohorts'])//2+37,) or not np.isfinite(state).all():
        raise ValueError('sealed parent state dimension/domain mismatch')
    return result,state
