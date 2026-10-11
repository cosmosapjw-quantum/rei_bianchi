import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from events import source_entry_events,segment_active_indices,restart_boundaries


def test_exact_source_entry_on_expanding_geometry_and_dormant_support():
    # a_rel=exp(t), pureFLRW exact solutionE=q exp(-t).
    geometry=lambda t:dict(a_rel=np.exp(t),b=0.)
    q=np.array([20.,75000.,100000.]);mu=np.array([0.,-.4,.4])
    events=source_entry_events(q,mu,geometry,2.)
    assert len(events)==2
    for e in events:
        assert abs(e['time_s']-np.log(q[e['node']]/50000))<2e-15
    boundaries=restart_boundaries(events)
    active=[segment_active_indices(q,mu,geometry,2*a,2*b).tolist() for a,b in zip(boundaries[:-1],boundaries[1:])]
    assert active==[[0],[0,1],[0,1,2]]
