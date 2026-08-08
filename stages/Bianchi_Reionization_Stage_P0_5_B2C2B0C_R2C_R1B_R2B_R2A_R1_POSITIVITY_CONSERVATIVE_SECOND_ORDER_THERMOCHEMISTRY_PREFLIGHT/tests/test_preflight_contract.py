from __future__ import annotations
import importlib.util,sys
from pathlib import Path

MODULE=Path(__file__).parents[1]/'analysis/run_preflight.py'

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_run',MODULE)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def test_pass_requires_every_lane_at_1024_or_2048():
    m=load()
    rows=[]
    for lane in m.LANES:
        rows.append({'lane':lane,'partition':1024,'candidate_converged':True,'local_error':1e-4,'all_gates_pass':True})
    assert m.classify(rows)['science_pass'] is True
    rows[-1]['local_error']=3e-4
    assert m.classify(rows)['science_pass'] is False


def test_partition_512_alone_cannot_promote():
    m=load()
    rows=[{'lane':lane,'partition':512,'candidate_converged':True,'local_error':1e-5,'all_gates_pass':True} for lane in m.LANES]
    assert m.classify(rows)['science_pass'] is False
