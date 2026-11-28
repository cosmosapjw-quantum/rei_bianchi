"""Behavioral acceptance tests use synthetic records, never native evidence."""
from pathlib import Path
import sys,copy,json,shutil
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import reference_contract as c
import analyze_return as ar


def result(T=8.,error=0.):
    return dict(temperature_K=T,gas_final=[1e-5,2e-5,1e-12,.001],
      number_defect=error,energy_defect_ev=error,species_defect=[0.,0.,0.],
      min_photon=0.,gas_positive=True)


def test_same_model_methods_are_empirical_not_rigorous_radius():
    x=c.admit_pair(result(),result(8.+1e-12))
    assert x['reference_stable'] is True
    assert x['error_radius_certified'] is False

@pytest.mark.parametrize('key,bad',[('number_defect',1e-10),('energy_defect_ev',1e-5),
 ('min_photon',-1e-30),('temperature_K',float('nan')),('gas_positive',False)])
def test_invalid_result_refused(key,bad):
    r=result();r[key]=bad
    with pytest.raises(ValueError):c.admit_pair(r,result())


def test_disagreeing_methods_refused():
    with pytest.raises(ValueError,match='UNSTABLE'):c.admit_pair(result(),result(8.+1e-5))


def test_partial_state_not_accepted():
    r=result();r['gas_final']=[1e-5]
    with pytest.raises(ValueError):c.admit_pair(r,result())


def test_comparison_requires_same_table_and_exposure_model():
    p={'m':8,'angles':4,'q':0.,'strips':4,'source_table_nodes':512,'table':'abc'}
    c.same_model(p,dict(p))
    for field,value in [('table','x'),('source_table_nodes',1024),('strips',8),('q',.005)]:
        q=dict(p);q[field]=value
        with pytest.raises(ValueError):c.same_model(p,q)


def test_zero_reference_component_uses_absolute_difference():
    a=result();b=result();a['gas_final'][2]=0.;b['gas_final'][2]=1e-14
    r=c.admit_pair(a,b)
    assert r['absolute_fraction_difference']==1e-14
    assert 'relative_fraction_error' not in r


def test_parent_r8_time_comparison_checks_table_identity(tmp_path):
    source=Path(__file__).resolve().parents[1]/'inputs'
    target=tmp_path/'inputs';shutil.copytree(source,target)
    p=target/'study/m8_r8_n64/RESULT.json';d=json.loads(p.read_text())
    d['source_table_sha256']='different-table';p.write_text(json.dumps(d))
    with pytest.raises(ValueError,match='TABLE_CHANGED'):ar.audit(target)
