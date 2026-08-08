from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np

MODULE=Path(__file__).parents[1]/'analysis/second_order_sdirk_trial.py'
REPO=Path(__file__).resolve().parents[3]

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_trial_sdirk',MODULE)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m


def test_sdirk_physical_microstep_closes_all_nonlocal_gates():
    m=load(); solver=m.SecondOrderSDIRKTrial.from_repo(repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY')
    parent=solver.inputs.state0.mutable_copy(); d=solver.forcing.duration_seconds(0)
    r=solver.solve(state=parent,t0=0.0,t1=d/4096,partition=4096,trial_kind='TEST')
    assert r.converged,r.certificate
    assert r.minimum_species>0.0
    assert r.hydrogen_residual<1e-11 and r.helium_residual<1e-11
    assert r.owner_residual<1e-11 and r.photon_residual<1e-8
    assert r.thermal_residual<1e-10 and r.pds_reconstruction_residual<1e-11
