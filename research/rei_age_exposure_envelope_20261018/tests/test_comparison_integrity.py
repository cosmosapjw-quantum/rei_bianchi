"""Scientific-result schema guards: missing species must never appear accurate."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
import compare_results as c

def endpoint():
    return dict(proper_time_s=10.,N=2.,U=40.,temperature_K=8000.,
        Gamma_s=[1.,2.,3.],heat_erg_per_absorber_s=[.1,.2,.3],
        ledgers=[0.]*14,flat=[.1,.2,.3,1.],
        quadrupole_U_mu2_minus_third=0.,birth_times_s=[7.,9.],
        cohorts=[[1.,20.],[1.,20.]])

@pytest.mark.parametrize('key,bad',[
    ('Gamma_s',[1.]),('heat_erg_per_absorber_s',[]),('ledgers',[0.]*6),
    ('flat',[.1,.2]),('cohorts',[[2.,40.]]),('birth_times_s',[11.,9.]),
    ('temperature_K',float('nan')),('N',-1.)])
def test_malformed_endpoint_never_yields_pass(key,bad):
    a=endpoint();a[key]=bad
    with pytest.raises(ValueError): c.endpoint_metrics(a,endpoint())

def test_valid_zero_species_result_remains_accepted():
    a=endpoint();a['Gamma_s']=[0.,0.,0.]
    assert c.endpoint_metrics(a,a)['Gamma_s']==[0.,0.,0.]

@pytest.mark.parametrize('target',['nan','inf','-0.01'])
def test_cli_rejects_invalid_accuracy_target(tmp_path,target):
    for name in ('left','right'):
        d=tmp_path/name;d.mkdir()
        (d/'endpoint.json').write_text(json.dumps(endpoint()))
        (d/'observations.json').write_text('[]')
    out=tmp_path/'comparison.json'
    r=subprocess.run([sys.executable,str(Path(c.__file__)),str(tmp_path/'left'),
        str(tmp_path/'right'),'--out',str(out),'--target',target],capture_output=True,text=True)
    assert r.returncode != 0 and not out.exists(),r.stdout

@pytest.mark.parametrize('tol',[float('nan'),-1.])
def test_observation_clock_tolerance_must_be_valid(tol):
    with pytest.raises(ValueError):c.match_observations([],[],tol)
