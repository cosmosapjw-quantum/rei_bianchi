"""Theoretical adapter tests with a synthetic mock; not source-native execution."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from he21_photo import run as he21_run, N_H_Z20
from he22_contract import PhotoOnlyTestDouble
from he22_coupled import run_coupled


def make_double(a,x):
    import math
    return PhotoOnlyTestDouble(N_H_Z20*math.exp(-3*x))


def test_he22_photo_only_embedded_reproduces_he21():
    for q in (-.005,0.,.005):
        original=he21_run(m=4,steps=4,q=q)
        simulated=run_coupled(make_double,m=4,steps=4,q=q)
        assert abs(simulated['source_count']-original.source_count)<1e-18
        assert np.max(np.abs(np.asarray(simulated['absorbed'])-original.absorbed))<2e-11
        assert abs(simulated['gas_final'][3]-original.gas_final[3])<1e-10
        assert abs(simulated['number_defect'])<1e-16
        assert abs(simulated['energy_defect'])<1e-12
        assert simulated['max_support_crossing']==0
        assert simulated['native_evaluator_calls']>0


def test_empty_photon_state_still_requests_native_gas_evolution():
    fake=run_coupled(make_double,m=4,steps=4,photons=False)
    assert fake['source_count']==0.
    assert fake['native_evaluator_calls']>=4
    assert max(abs(v) for v in fake['absorbed'])==0
    assert abs(fake['energy_defect'])<1e-12
