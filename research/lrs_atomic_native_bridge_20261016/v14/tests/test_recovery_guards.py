"""Regression: synthetic malformed bookkeeping must not pass native analysis."""
from pathlib import Path
import csv,math
import pytest
from test_native_analysis import fixture
from analyze_v14 import analyze

def rewrite(p,fn):
    with p.open(newline='') as f:
        r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
    fn(rows)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

@pytest.mark.parametrize('column,value',[('added_N','nan'),('added_U','inf'),
    ('proper_time_weight_s','-1'),('weight_dln_a','-1'),('birth','nan')])
def test_bad_birth_value_rejected(tmp_path,column,value):
    p=fixture(tmp_path);b=Path(str(p)+'.births.csv')
    rewrite(b,lambda rows:rows[0].update({column:value}))
    with pytest.raises(ValueError):analyze(p)

def test_gl2_collapsed_to_common_midpoint_is_rejected(tmp_path):
    p=fixture(tmp_path);b=Path(str(p)+'.births.csv')
    def collapse(rows):
        for row in rows:
            if row['mode']=='physical_gl2':
                row['a']=math.exp((int(row['step'])-.5)*1e-5/8)/21.
    rewrite(b,collapse)
    with pytest.raises(ValueError):analyze(p)

def test_duplicate_birth_index_rejected(tmp_path):
    p=fixture(tmp_path);b=Path(str(p)+'.births.csv')
    def duplicate(rows):
        for row in rows:
            if row['mode']=='physical_gl2':row['birth']=0
    rewrite(b,duplicate)
    with pytest.raises(ValueError):analyze(p)

def test_source_off_nonzero_born_photons_rejected(tmp_path):
    p=fixture(tmp_path);b=Path(str(p)+'.births.csv')
    def corrupt(rows):
        for row in rows:
            if row['mode']=='source_off_gl2':row['added_N']=1e-10
    rewrite(b,corrupt)
    with pytest.raises(ValueError):analyze(p)

def test_requested_matrix_must_not_silently_shrink(tmp_path):
    from birth_record_guard import validate_matrix
    p=fixture(tmp_path)
    validate_matrix(p,8)
    with pytest.raises(ValueError,match='incomplete requested matrix'):
        validate_matrix(p,16)

def test_invalid_expected_grid(tmp_path):
    from birth_record_guard import validate_matrix
    with pytest.raises(ValueError,match='expected grid'):
        validate_matrix(fixture(tmp_path),12)
