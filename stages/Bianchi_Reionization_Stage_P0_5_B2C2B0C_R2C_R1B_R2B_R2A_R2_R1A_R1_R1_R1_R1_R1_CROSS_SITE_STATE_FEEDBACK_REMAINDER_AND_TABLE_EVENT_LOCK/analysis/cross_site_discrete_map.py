#!/usr/bin/env python3
"""Validated primitives for the four-site MPRK22--SDIRK2 discrete map.

This module starts with reviewable, exact-or-outward primitives.  It deliberately
separates local implicit certificates, normalized-measure bounds, table events,
and set-ledger gates from the later full-map remainder composition.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import importlib.util, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]


def _load(name:str,path:Path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


def _implicit_module():
    prior=next(REPO.glob('stages/*EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2*'))
    return _load('crosssite_parent_implicit',prior/'analysis/implicit_certificates.py')


def _parent_modules(repo_root:Path):
    repo=Path(repo_root).resolve()
    r1a=next(repo.glob('stages/*R2_R1A_FOUR_CORNER*'))
    trial=_load('crosssite_parent_trial',r1a/'analysis/uncertainty_trial.py')
    policy=_load('crosssite_parent_policy',r1a/'analysis/uncertainty_policy.py')
    return trial,policy




def sha256_bytes(payload: bytes) -> str:
    """Return a stable digest for an immutable transaction snapshot."""
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")
    return hashlib.sha256(bytes(payload)).hexdigest()


@dataclass(frozen=True)
class EventLocalization:
    certified: bool
    t_lower: float
    t_upper: float
    value_lower: float
    value_upper: float
    knot: float
    iterations: int
    direction: str
    parent_state_sha256: str
    parent_ledger_sha256: str
    parent_unchanged: bool


def localize_monotone_table_event(
    *,
    t0: float,
    t1: float,
    knot: float,
    value_at,
    parent_state_bytes: bytes,
    parent_ledger_bytes: bytes,
    time_tolerance: float,
    max_bisections: int = 128,
) -> EventLocalization:
    """Localize one monotone table crossing without mutating accepted state.

    ``value_at`` is an audit callback for a scalar continuous monotone path.
    The function is deliberately transaction-pure: the accepted parent state
    and ledger enter as immutable byte snapshots and are hashed before and after
    the rejected trial/localization sequence.
    """
    a=float(t0); b=float(t1); k=float(knot); tol=float(time_tolerance)
    if not(np.isfinite(a) and np.isfinite(b) and np.isfinite(k) and np.isfinite(tol)):
        raise ValueError("event-localization inputs must be finite")
    if not a < b or tol <= 0.0 or int(max_bisections) <= 0:
        raise ValueError("invalid localization interval or tolerance")
    state_before=sha256_bytes(parent_state_bytes)
    ledger_before=sha256_bytes(parent_ledger_bytes)
    fa=float(value_at(a)); fb=float(value_at(b))
    if not(np.isfinite(fa) and np.isfinite(fb)) or fa == fb:
        raise ValueError("event path must have finite nonzero monotone change")
    increasing=fb>fa
    if increasing:
        if not fa <= k <= fb:
            raise ValueError("increasing path does not bracket the knot")
    elif not fb <= k <= fa:
        raise ValueError("decreasing path does not bracket the knot")
    iterations=0
    while b-a > tol and iterations < int(max_bisections):
        mid=a+0.5*(b-a)
        fm=float(value_at(mid))
        if not np.isfinite(fm):
            raise ValueError("nonfinite event path")
        if increasing:
            if fm < k:
                a,fa=mid,fm
            else:
                b,fb=mid,fm
        else:
            if fm > k:
                a,fa=mid,fm
            else:
                b,fb=mid,fm
        iterations+=1
    state_after=sha256_bytes(parent_state_bytes)
    ledger_after=sha256_bytes(parent_ledger_bytes)
    certified=(b-a <= tol and ((fa <= k <= fb) if increasing else (fb <= k <= fa)))
    return EventLocalization(
        certified=bool(certified),
        t_lower=float(a),
        t_upper=float(b),
        value_lower=float(fa),
        value_upper=float(fb),
        knot=k,
        iterations=iterations,
        direction="increasing" if increasing else "decreasing",
        parent_state_sha256=state_before,
        parent_ledger_sha256=ledger_before,
        parent_unchanged=bool(state_before==state_after and ledger_before==ledger_after),
    )


@dataclass(frozen=True)
class TableEventAudit:
    any_event: bool
    node_indices: np.ndarray
    knot_indices: np.ndarray
    minimum_distance: float


def detect_table_events(log_temperature_lower,log_temperature_upper,*,ulp_guard:int=16)->TableEventAudit:
    lo=np.asarray(log_temperature_lower,dtype=np.float64)
    hi=np.asarray(log_temperature_upper,dtype=np.float64)
    if lo.shape!=hi.shape or np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo>hi):
        raise ValueError('invalid log-temperature box')
    knots=np.log(10.0**np.arange(4.0,5.0000001,0.25))
    tol=float(ulp_guard)*np.finfo(float).eps*np.maximum(1.0,np.abs(knots))
    hit=(lo[:,None] <= knots[None,:]+tol[None,:]) & (hi[:,None] >= knots[None,:]-tol[None,:])
    rows,cols=np.nonzero(hit)
    distance=np.min(np.minimum(np.abs(lo[:,None]-knots[None,:]),np.abs(hi[:,None]-knots[None,:])))
    return TableEventAudit(bool(len(rows)),np.ascontiguousarray(rows),np.ascontiguousarray(cols),float(distance))


def detect_path_table_events(*boxes, ulp_guard: int = 16) -> TableEventAudit:
    """Detect a knot touched by the hull of all discrete-map temperature sites.

    Checking each site separately is insufficient: two disjoint site boxes may
    lie on opposite sides of a source-table knot.  The componentwise path hull
    is a conservative sufficient detector for such between-site crossings.
    """
    if len(boxes) < 2:
        raise ValueError("at least two path boxes are required")
    lowers=[]; uppers=[]; shape=None
    for box in boxes:
        lo=np.asarray(box.lo,dtype=np.float64); hi=np.asarray(box.hi,dtype=np.float64)
        if shape is None:
            shape=lo.shape
        if lo.shape!=shape or hi.shape!=shape:
            raise ValueError("path boxes have inconsistent shapes")
        if np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo>hi):
            raise ValueError("invalid path box")
        lowers.append(lo); uppers.append(hi)
    hull_lo=np.nextafter(np.min(np.stack(lowers),axis=0),-np.inf)
    hull_hi=np.nextafter(np.max(np.stack(uppers),axis=0),np.inf)
    return detect_table_events(hull_lo,hull_hi,ulp_guard=ulp_guard)


@dataclass(frozen=True)
class IntervalVector:
    lo: np.ndarray
    hi: np.ndarray


def normalized_measure_interval(lower,upper)->IntervalVector:
    """Exact component bounds for ``q_i=h_i/sum_j h_j`` over a positive box."""
    lo=np.asarray(lower,dtype=np.float64);hi=np.asarray(upper,dtype=np.float64)
    if lo.ndim!=1 or lo.shape!=hi.shape or np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)):
        raise ValueError('measure bounds must be finite vectors')
    if np.any(lo<0.0) or np.any(lo>hi) or np.sum(lo)<=0.0:
        raise ValueError('invalid nonnegative measure box')
    total_hi=np.sum(hi.astype(np.longdouble),dtype=np.longdouble)
    total_lo=np.sum(lo.astype(np.longdouble),dtype=np.longdouble)
    qlo=np.empty_like(lo);qhi=np.empty_like(hi)
    for i in range(len(lo)):
        den_lo=np.longdouble(lo[i])+(total_hi-np.longdouble(hi[i]))
        den_hi=np.longdouble(hi[i])+(total_lo-np.longdouble(lo[i]))
        qlo[i]=float(np.longdouble(lo[i])/den_lo) if den_lo>0 else 0.0
        qhi[i]=float(np.longdouble(hi[i])/den_hi) if den_hi>0 else 1.0
    return IntervalVector(np.nextafter(qlo,-np.inf),np.nextafter(qhi,np.inf))


@dataclass(frozen=True)
class LinearStageBox:
    certified: bool
    lower: np.ndarray
    upper: np.ndarray
    maximum_row_sum: float


def certify_interval_linear_stage(matrices,rhs)->LinearStageBox:
    mats=np.asarray(matrices,dtype=np.float64);b=np.asarray(rhs,dtype=np.float64)
    if mats.ndim!=3 or mats.shape[1]!=mats.shape[2]:raise ValueError('matrices must be [C,S,S]')
    if b.shape!=(mats.shape[0],mats.shape[1]):raise ValueError('rhs shape mismatch')
    lo=np.nextafter(np.min(mats,axis=0),-np.inf)[None,:,:]
    hi=np.nextafter(np.max(mats,axis=0),np.inf)[None,:,:]
    blo=np.nextafter(np.min(b,axis=0),-np.inf)[None,:]
    bhi=np.nextafter(np.max(b,axis=0),np.inf)[None,:]
    cert=_implicit_module().linear_interval_krawczyk(lo,hi,blo,bhi)
    lower=np.nextafter(cert.center[0]-cert.radius[0],-np.inf)
    upper=np.nextafter(cert.center[0]+cert.radius[0],np.inf)
    return LinearStageBox(bool(cert.certified[0]),lower,upper,float(cert.row_sum_bound[0]))


@dataclass(frozen=True)
class SetLedgerAudit:
    all_include_zero: bool
    failed: tuple[str,...]


def audit_set_ledgers(intervals:dict[str,tuple[float,float]])->SetLedgerAudit:
    failed=[]
    for name,(lo,hi) in intervals.items():
        a,b=float(lo),float(hi)
        if not(np.isfinite(a) and np.isfinite(b) and a<=0.0<=b):failed.append(str(name))
    return SetLedgerAudit(not failed,tuple(failed))


def audit_point_flux_corner_containment(repo_root:Path,*,lane:str)->dict[str,object]:
    repo=Path(repo_root).resolve();trial,policy=_parent_modules(repo)
    base=trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
    solver=trial.UncertaintySecondOrderTrial(base=base,lane=lane,v_policy='CELL_LOWER_STRICT',f_value=0.1)
    state=base.inputs.state0.mutable_copy();point=base.forcing.point(interval=0,time_s=0.0)
    owner=solver._owner(state,point);photo=solver.backend.photo_fields(owner)
    volume=solver.inputs.comoving_volume_cm3/(1.0+point.z)**3
    corners=[]
    for vp in ('CELL_LOWER_STRICT','CELL_UPPER_STRICT'):
        v=policy.build_v_field_from_temperature(vp,state.temperature_K)
        for fvalue in (0.1,1.0):
            event=trial.event_mod.evaluate_event_flux(
                populations=state.values[:5].T,temperature_K=state.temperature_K,
                proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,
                photo_heii=photo.HeII,v=v,f=policy.build_f_field(fvalue,state.node_count))
            corners.append(event.pds_flux)
    stack=np.stack(corners);lo=np.nextafter(np.min(stack,axis=0),-np.inf);hi=np.nextafter(np.max(stack,axis=0),np.inf)
    outside=0.0
    for value in corners:
        outside=max(outside,float(np.max(np.maximum(lo-value,value-hi))))
    diagonal=np.diagonal(stack,axis1=2,axis2=3)
    return {
        'all_corners_contained':bool(outside<=0.0),
        'maximum_outside':max(0.0,outside),
        'structural_zero_pass':bool(np.all(diagonal==0.0)),
        'node_count':int(state.node_count),
        'corner_count':int(len(corners)),
    }


__all__=['sha256_bytes','EventLocalization','localize_monotone_table_event',
         'TableEventAudit','detect_table_events','detect_path_table_events','IntervalVector','normalized_measure_interval',
         'LinearStageBox','certify_interval_linear_stage','SetLedgerAudit','audit_set_ledgers',
         'audit_point_flux_corner_containment']
