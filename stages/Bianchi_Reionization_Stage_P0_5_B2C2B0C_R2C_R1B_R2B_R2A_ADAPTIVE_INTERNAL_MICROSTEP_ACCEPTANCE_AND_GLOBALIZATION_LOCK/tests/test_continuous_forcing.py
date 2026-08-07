from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import numpy as np

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]


def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def test_continuous_forcing_reproduces_locked_nodes_and_integrals():
    m=_load('r2b_r2a_array_forcing',STAGE/'analysis/array_forcing.py')
    t=_load('r2b_r2a_tensorized_forcing',STAGE/'analysis/tensorized_inputs.py')
    data=t.load_tensorized_inputs(repo_root=REPO)
    forcing=m.ArrayContinuousForcing.from_repo(repo_root=REPO,inputs=data)
    for node in (0,8,16):
        point=forcing.point(interval=0,time_s=float(data.time_s[0,node]))
        for got,ref in ((point.kappa,data.kappa[0,node]),(point.current,data.absorption[0,node]),(point.external_subgrid,data.external_subgrid[0,node])):
            scale=np.maximum.reduce([np.abs(got),np.abs(ref),np.ones_like(got)])
            assert np.max(np.abs(got-ref)/scale) < 1e-15
    duration=forcing.duration_seconds(0)
    full=forcing.step(interval=0,t0_s=0.0,t1_s=duration)
    halves=(
        forcing.step(interval=0,t0_s=0.0,t1_s=duration/2),
        forcing.step(interval=0,t0_s=duration/2,t1_s=duration),
    )
    lhs=full.current*duration
    rhs=halves[0].current*(duration/2)+halves[1].current*(duration/2)
    scale=np.maximum(np.abs(lhs),1.0)
    assert np.max(np.abs(lhs-rhs)/scale) < 1e-14


def test_array_owner_point_api_matches_locked_node_api():
    t=_load('r2b_r2a_tensorized_point',STAGE/'analysis/tensorized_inputs.py')
    o=_load('r2b_r2a_array_owner_point',STAGE/'analysis/array_owner_kernel.py')
    data=t.load_tensorized_inputs(repo_root=REPO)
    kernel=o.ArrayOwnerKernel.from_repo(repo_root=REPO,inputs=data)
    ref=kernel.evaluate(interval=0,node=8,state=data.state0,lane=o.LANES[0])
    got=kernel.evaluate_values(
        kappa_total=data.kappa[0,8], current_total=data.absorption[0,8],
        external_subgrid=data.external_subgrid[0,8], z=float(data.z_mid[0,8]),
        gamma_hi=float(data.gamma_hi[0,8]), state=data.state0, lane=o.LANES[0]
    )
    for name in ('owner_kappa','owner_current','owner_fraction','node_current','node_fraction'):
        a=getattr(ref,name); b=getattr(got,name)
        scale=np.maximum.reduce([np.abs(a),np.abs(b),np.ones_like(a)])
        assert np.max(np.abs(a-b)/scale) < 1e-14
