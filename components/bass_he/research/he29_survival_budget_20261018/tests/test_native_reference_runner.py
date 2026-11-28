"""Runner contracts only: no fixture in this module is native science."""
from pathlib import Path
import sys,json,copy
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import reference_runner as rr


def test_saved_point_response_exact_and_zero_rules():
    assert rr.response_error([0.,1.,1e-30],[0.,1.,1e-30])==0
    with pytest.raises(ValueError):rr.response_error([1e-30],[0.])
    with pytest.raises(ValueError):rr.response_error([float('nan')],[1.])
    with pytest.raises(ValueError):rr.response_error([1.],[1.,2.])


def test_invalid_grid_never_enters_native():
    for r,nodes in [(1,512),(16,512),(2,1024),(4,256)]:
        with pytest.raises(ValueError):rr.validate_job(r,nodes)
    for r,nodes in [(2,512),(4,512),(8,512),(4,1024)]:rr.validate_job(r,nodes)


def test_parent_table_mismatch_refused_without_owner():
    with pytest.raises(ValueError,match='TABLE'):
        rr.parent_comparisons(ROOT/'inputs',2,512,'wrong',{'temperature_K':8.,'gas_final':[0.,0.,0.,1.]})


def test_valid_same_table_reads_existing_transport_not_replay():
    p=ROOT/'inputs/study/m8_r2_n64/RESULT.json';d=json.loads(p.read_text())
    out=rr.parent_comparisons(ROOT/'inputs',2,512,d['source_table_sha256'],d['results']['transport'])
    assert len(out)==2 and out[1]['temperature_error_K']==0


def test_table1024_is_not_mislabeled_transport_time_error():
    assert rr.parent_comparisons(ROOT/'inputs',4,1024,'new-table',{})==[]


def test_missing_parent_input_refused(tmp_path):
    with pytest.raises((FileNotFoundError,ValueError)):
        rr.parent_comparisons(tmp_path,2,512,'table',{})
