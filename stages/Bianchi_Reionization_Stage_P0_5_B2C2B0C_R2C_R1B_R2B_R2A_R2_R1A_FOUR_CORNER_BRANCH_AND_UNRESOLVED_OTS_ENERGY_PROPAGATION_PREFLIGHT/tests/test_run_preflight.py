from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def load_module():
    spec=importlib.util.spec_from_file_location('run_preflight',STAGE/'analysis/run_preflight.py')
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


class State:
    def __init__(self,values,temperature): self.values=np.asarray(values,float);self.temperature_K=np.asarray(temperature,float)


def test_block_errors_are_fraction_and_log_temperature_errors():
    m=load_module()
    a=np.array([[8.,4.],[2.,6.],[7.,6.],[2.,3.],[1.,1.],[1.,1.]])
    b=a.copy();b[1,0]+=0.1;b[0,0]-=0.1;b[3,1]+=0.05;b[2,1]-=0.05
    e=m.block_errors(State(a,[100.,200.]),State(b,[101.,198.]))
    assert e['x_HII']>0 and e['x_HeII']>0 and e['x_HeIII']==0
    assert e['log_T']==max(abs(np.log(100/101)),abs(np.log(200/198)))


def test_execution_registry_has_24_rows_and_12_load_bearing():
    m=load_module();rows=m.execution_registry_rows()
    assert len(rows)==24
    assert sum(bool(r['load_bearing']) for r in rows)==12
    assert {r['shape_lane'] for r in rows}==set(m.LANES)
    assert len({(r['shape_lane'],r['policy_id']) for r in rows})==24
