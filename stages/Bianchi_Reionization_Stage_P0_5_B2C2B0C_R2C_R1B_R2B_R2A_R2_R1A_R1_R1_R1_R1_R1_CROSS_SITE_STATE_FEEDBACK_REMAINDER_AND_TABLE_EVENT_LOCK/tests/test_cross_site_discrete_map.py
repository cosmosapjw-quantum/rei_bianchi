from __future__ import annotations
import importlib.util, sys
from pathlib import Path
import numpy as np

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]

def load():
    path=STAGE/'analysis/cross_site_discrete_map.py'
    spec=importlib.util.spec_from_file_location('cross_site_discrete_map_test',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def test_table_event_detector_distinguishes_safe_touch_and_crossing():
    m=load()
    knots=np.log(10.0**np.arange(4.0,5.0000001,0.25))
    safe=m.detect_table_events(
        np.array([knots[1]+1e-3]),np.array([knots[1]+2e-3]))
    assert not safe.any_event
    crossing=m.detect_table_events(
        np.array([knots[1]-1e-6]),np.array([knots[1]+2e-6]))
    assert crossing.any_event
    assert crossing.node_indices.tolist()==[0]
    assert crossing.knot_indices.tolist()==[1]

def test_owner_normalization_interval_preserves_simplex_and_contains_samples():
    m=load()
    lo=np.array([1.0,2.0,3.0]);hi=np.array([1.1,2.2,3.3])
    q=m.normalized_measure_interval(lo,hi)
    assert np.sum(q.lo)<=1.0<=np.sum(q.hi)
    rng=np.random.default_rng(20260811)
    for _ in range(1000):
        h=rng.uniform(lo,hi);v=h/h.sum()
        assert np.all(q.lo<=v) and np.all(v<=q.hi)

def test_interval_linear_stage_contains_all_corner_solves():
    m=load()
    A=np.array([
      [[1.2,-0.1],[-0.2,1.4]],
      [[1.21,-0.09],[-0.18,1.39]],
      [[1.19,-0.11],[-0.21,1.41]],
      [[1.205,-0.095],[-0.19,1.405]],
    ])
    b=np.array([[1.0,0.8],[1.01,0.79],[0.99,0.81],[1.005,0.795]])
    box=m.certify_interval_linear_stage(A,b)
    assert box.certified
    for Ai,bi in zip(A,b):
        z=np.linalg.solve(Ai,bi)
        assert np.all(box.lower<=z) and np.all(z<=box.upper)

def test_set_ledger_requires_zero_inclusion():
    m=load()
    ok=m.audit_set_ledgers({'H_nuclei':(-1e-16,2e-16),'total_energy':(-2e-12,3e-12)})
    assert ok.all_include_zero
    bad=m.audit_set_ledgers({'H_nuclei':(1e-9,2e-9)})
    assert not bad.all_include_zero
    assert bad.failed==('H_nuclei',)

def test_actual_parent_point_flux_box_contains_four_source_corners():
    m=load()
    result=m.audit_point_flux_corner_containment(REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY')
    assert result['all_corners_contained'], result
    assert result['maximum_outside']==0.0
    assert result['structural_zero_pass']

def test_path_hull_event_detector_catches_between_site_crossing():
    m=load()
    knot=float(np.log(10.0**4.25))
    left=m.IntervalVector(np.array([knot-2e-4]),np.array([knot-1e-4]))
    right=m.IntervalVector(np.array([knot+1e-4]),np.array([knot+2e-4]))
    audit=m.detect_path_table_events(left,right)
    assert audit.any_event
    assert audit.node_indices.tolist()==[0]
    assert audit.knot_indices.tolist()==[1]


def test_transactional_monotone_event_localizer_preserves_parent_bytes():
    m=load()
    knot=float(np.log(10.0**4.5))
    state=b'parent-state-v1'
    ledger=b'parent-ledger-v1'
    slope=0.4
    t_cross=0.375
    def value(t:float)->float:
        return knot+slope*(t-t_cross)
    result=m.localize_monotone_table_event(
        t0=0.0,t1=1.0,knot=knot,value_at=value,
        parent_state_bytes=state,parent_ledger_bytes=ledger,
        time_tolerance=2.0**-30,
    )
    assert result.certified
    assert result.t_lower <= t_cross <= result.t_upper
    assert result.t_upper-result.t_lower <= 2.0**-30
    assert result.parent_state_sha256==m.sha256_bytes(state)
    assert result.parent_ledger_sha256==m.sha256_bytes(ledger)
    assert result.parent_unchanged
