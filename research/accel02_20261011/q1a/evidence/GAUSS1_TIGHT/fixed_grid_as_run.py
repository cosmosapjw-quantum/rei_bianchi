"""Immutable positive composite Gauss rule in log conserved q.

Only the numerical quadrature changes. No dynamic nodes, weights, remap or
new source/cross-section law is introduced.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np


def composite_grid(panel_edges, order, n_mu):
    edges=np.asarray(panel_edges,dtype=float)
    if (edges.ndim!=1 or len(edges)<2 or not np.isfinite(edges).all()
        or np.any(edges<=0) or np.any(np.diff(edges)<=0)
        or int(order)!=order or order<1 or int(n_mu)!=n_mu or n_mu<1):
        raise ValueError('FIXED_GRID_DOMAIN')
    lx=np.log(edges);x,w=np.polynomial.legendre.leggauss(int(order))
    q=np.exp((lx[:-1,None]+lx[1:,None])/2+np.diff(lx)[:,None]*x/2).ravel()
    we=(np.diff(lx)[:,None]*w/2).ravel()
    mu,wm=np.polynomial.legendre.leggauss(int(n_mu))
    arrays=(np.repeat(q,n_mu),np.tile(mu,len(q)),np.repeat(we,n_mu)*np.tile(wm/2,len(q)))
    for a in arrays:a.setflags(write=False)
    return arrays


def arrays_sha(arrays):
    h=hashlib.sha256()
    for a in arrays:h.update(np.asarray(a,dtype='<f8').tobytes())
    return h.hexdigest()


def design_panels(provider):
    if provider.r!=0.:raise ValueError('Q1A_PROSPECTIVE_DESIGN_FLRW_ONLY')
    native=provider.tables['uvb'].energies_eV
    jumps=provider.tables['emissivity'].energies_eV
    jumps=np.unique(jumps[:-1][np.diff(jumps)==0])
    cuts=np.unique(np.r_[10.,13.60,24.59,54.42,50000.,jumps])
    edges=[10.,50000.,provider.q_max_eV]
    edges.extend(native[(native>10.)&(native<50000.)])
    for u in [0.,.25,.5,.75,1.]:
        a=provider.geometry(u*provider.end_time_s)['a_rel']
        edges.extend(float(e*a) for e in cuts if 10.<e*a<provider.q_max_eV)
    return np.unique(edges)


def build_record(provider,order,n_mu=2):
    edges=design_panels(provider);arrays=composite_grid(edges,order,n_mu)
    return dict(schema='rei.fixed_q_gauss.v1',panel_edges_eV=edges.tolist(),
        order=int(order),n_mu=int(n_mu),n_panels=len(edges)-1,
        n_energy=(len(edges)-1)*order,n_nodes=len(arrays[0]),
        q_eV=arrays[0].tolist(),mu0=arrays[1].tolist(),weights=arrays[2].tolist(),
        arrays_sha256=arrays_sha(arrays),input_identity=provider.identity,
        construction=dict(initial_knots='all unique native UVB knots in10..50000eV',
            trajectory_u=[0.,.25,.5,.75,1.],r=0.,angle_rule='Gauss Legendre dmu/2',
            qmin=10.,qmax=provider.q_max_eV,weights='dlnq times dmu/2; fixed positive'),
        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


class FixedCharacteristics:
    def __init__(self,path,original):
        self.path=Path(path);self.record=json.loads(self.path.read_text())
        r=self.record
        if r['schema']!='rei.fixed_q_gauss.v1':raise ValueError('GRID_SCHEMA')
        if r['implementation_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError('GRID_IMPLEMENTATION_IDENTITY')
        arrays=tuple(np.asarray(r[k],dtype=float) for k in ['q_eV','mu0','weights'])
        expected=composite_grid(r['panel_edges_eV'],r['order'],r['n_mu'])
        if (not all(np.array_equal(a,b) for a,b in zip(arrays,expected))
            or arrays_sha(arrays)!=r['arrays_sha256'] or len(arrays[0])!=r['n_nodes']
            or r['n_energy']*r['n_mu']!=r['n_nodes']):raise ValueError('GRID_ARRAY_IDENTITY')
        self.arrays=expected
        self.geometry_nodes=original.geometry_nodes
        self.source_reference=original.source_reference

    def make_grid(self,n_energy,n_mu,qmax):
        r=self.record
        if n_energy!=r['n_energy'] or n_mu!=r['n_mu'] or qmax!=r['construction']['qmax']:
            raise ValueError('GRID_ARGUMENT_MISMATCH')
        return self.arrays
