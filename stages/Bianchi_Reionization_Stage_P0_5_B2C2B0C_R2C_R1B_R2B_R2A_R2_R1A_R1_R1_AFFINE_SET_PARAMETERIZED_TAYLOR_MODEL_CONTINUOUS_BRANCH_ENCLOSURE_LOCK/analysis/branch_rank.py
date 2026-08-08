"""Exact node-block sensitivity-rank audit for the source-safe branch family."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import importlib.util,sys
from pathlib import Path
import numpy as np

ELL=1.425
M_CAS=0.737


def _load(name:str,path:Path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


def symbolic_determinant_residual():
    import sympy as sp
    v,f,y,z,r=sp.symbols('v f y z r')
    w=(sp.Rational(57,40)-sp.Rational(737,1000))+sp.Rational(737,1000)*y
    ahv=r*(w-f*z); ahf=r*(1-v)*z
    aev=r*(sp.Rational(737,1000)*(1-y)-f*(1-z)); aef=r*(1-v)*(1-z)
    expected=r**2*(1-v)*(w-sp.Rational(57,40)*z)
    return sp.simplify(ahv*aef-ahf*aev-expected)


@dataclass(frozen=True)
class BranchRankAudit:
    node_count:int
    v_active_nodes:int
    f_active_nodes:int
    robust_rank2_nodes:int
    rank1_remainder_nodes:int
    source_safe_rank_lower_bound:int
    global_parameter_rank:int
    rank_deficiency:int
    determinant_relative_threshold:float
    determinant_relative_min:float
    determinant_relative_median:float
    determinant_relative_max:float
    v_interval_nonzero_nodes:int
    below_table_nodes:int
    sparse_linear_storage_mib:float
    sparse_quadratic_storage_mib:float
    dense_generator_matrix_tib:float

    def to_dict(self):return asdict(self)


def audit_source_safe_rank(repo_root:Path,*,relative_threshold:float=1.0e-12)->BranchRankAudit:
    repo=Path(repo_root).resolve()
    prior=next(repo.glob('stages/*R2_R1A_R1_VALIDATED_CONTINUOUS*'))
    rim=_load('affine_tm_rank_interval_model',prior/'analysis/reduced_interval_rhs.py')
    model=rim.ReducedIntervalModel.from_repo(repo)
    coordinates=model.initial_coordinates();state=model.coordinates_to_state(coordinates)
    point=model.solver.forcing.point(interval=0,time_s=0.0)
    owner=model.solver._owner(state,point);photo=model.solver.backend.photo_fields(owner)
    volume=model.inputs.comoving_volume_cm3/(1.0+point.z)**3
    vlo=np.asarray(model.policy.build_v_field_from_temperature('CELL_LOWER_STRICT',state.temperature_K),float)
    vhi=np.asarray(model.policy.build_v_field_from_temperature('CELL_UPPER_STRICT',state.temperature_K),float)
    v=0.5*(vlo+vhi);f=np.full(state.node_count,0.55)
    event=model.event.evaluate_event_flux(
        populations=state.values[:5].T,temperature_K=state.temperature_K,
        proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,
        photo_heii=photo.HeII,v=v,f=f)
    y=np.asarray(event.branches['y']);z=np.asarray(event.branches['z']);w=np.asarray(event.branches['w'])
    rate=np.asarray(event.event_rates['HEIII_CASCADE'])
    dAHv=rate*(w-f*z);dAHf=rate*(1.0-v)*z
    dAEv=rate*(M_CAS*(1.0-y)-f*(1.0-z));dAEf=rate*(1.0-v)*(1.0-z)
    determinant=dAHv*dAEf-dAHf*dAEv
    scale=np.maximum(np.abs(dAHv*dAEf)+np.abs(dAHf*dAEv),np.nextafter(0.0,1.0))
    relative=np.abs(determinant)/scale
    robust=relative>float(relative_threshold)
    vactive=(np.abs(dAHv)+np.abs(dAEv))>0.0
    factive=(np.abs(dAHf)+np.abs(dAEf))>0.0
    # Each node block has disjoint output support. Robust nonzero determinant
    # gives rank two; all remaining nodes retain at least the positive f column.
    rank2=int(np.count_nonzero(robust))
    rank1=int(state.node_count-rank2)
    lower=2*rank2+rank1
    n=state.node_count
    linear_bytes=n*2*4*8
    quadratic_bytes=linear_bytes+n*4*8  # one local v*f block per four reduced coordinates
    dense_bytes=(4*n)*(2*n)*8
    return BranchRankAudit(
        node_count=n,v_active_nodes=int(np.count_nonzero(vactive)),f_active_nodes=int(np.count_nonzero(factive)),
        robust_rank2_nodes=rank2,rank1_remainder_nodes=rank1,
        source_safe_rank_lower_bound=lower,global_parameter_rank=2,rank_deficiency=lower-2,
        determinant_relative_threshold=float(relative_threshold),
        determinant_relative_min=float(np.min(relative)),determinant_relative_median=float(np.median(relative)),
        determinant_relative_max=float(np.max(relative)),v_interval_nonzero_nodes=int(np.count_nonzero(vhi>vlo)),
        below_table_nodes=int(np.count_nonzero(state.temperature_K<1.0e4)),
        sparse_linear_storage_mib=float(linear_bytes/2**20),sparse_quadratic_storage_mib=float(quadratic_bytes/2**20),
        dense_generator_matrix_tib=float(dense_bytes/2**40))


def adversarial_selectors(repo_root:Path):
    repo=Path(repo_root).resolve();prior=next(repo.glob('stages/*R2_R1A_R1_VALIDATED_CONTINUOUS*'))
    rim=_load('affine_tm_rank_selector_model',prior/'analysis/reduced_interval_rhs.py')
    model=rim.ReducedIntervalModel.from_repo(repo);c=model.initial_coordinates();state=model.coordinates_to_state(c)
    point=model.solver.forcing.point(interval=0,time_s=0.0);owner=model.solver._owner(state,point);photo=model.solver.backend.photo_fields(owner)
    volume=model.inputs.comoving_volume_cm3/(1+point.z)**3
    vlo=model.policy.build_v_field_from_temperature('CELL_LOWER_STRICT',state.temperature_K);vhi=model.policy.build_v_field_from_temperature('CELL_UPPER_STRICT',state.temperature_K)
    v=0.5*(vlo+vhi);f=np.full(state.node_count,0.55)
    event=model.event.evaluate_event_flux(populations=state.values[:5].T,temperature_K=state.temperature_K,proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,photo_heii=photo.HeII,v=v,f=f)
    y=event.branches['y'];z=event.branches['z'];rate=event.event_rates['HEIII_CASCADE']
    d_heii_dv=rate*(M_CAS*(1-y)-f*(1-z))
    return np.ascontiguousarray((d_heii_dv>0).astype(float)),np.ones(state.node_count,dtype=float)

__all__=['BranchRankAudit','audit_source_safe_rank','adversarial_selectors','symbolic_determinant_residual']
