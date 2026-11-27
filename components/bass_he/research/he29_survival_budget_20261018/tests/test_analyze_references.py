"""Synthetic result records test reporting only, not native physics."""
from pathlib import Path
import sys,json
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analyze_references import analyze
from reference_contract import JOBS,THREADS,OWNER


def install(tmp_path):
    for j,(r,nodes) in enumerate(JOBS):
        f=tmp_path/f'm8_r{r}_table{nodes}';f.mkdir()
        i=dict(m=8,r=r,q=0.,angles=4,table_nodes=nodes,owner_source=OWNER,
          binary_sha256='synthetic',source_files={},parent_sources={},input_sources={},numerical_thread_environment=THREADS)
        a=dict(temperature_K=8.+j*1e-8,gas_final=[1e-5,2e-5,1e-13,.001],
               number_defect=0.,energy_defect_ev=0.,species_defect=[0.,0.,0.],gas_positive=True,min_photon=0.)
        b=dict(a);b['temperature_K']+=1e-12
        d=dict(status='REFERENCE_COMPLETED_SCOPED',table_sha256=f't{j}',point_qualification={'points':6},results={'Radau':a,'DOP853':b})
        for n,x in [('IDENTITY.json',i),('RESULT.json',d),('TABLE.json',{'source_table_sha256':f't{j}'})]:
            (f/n).write_text(json.dumps(x))


def test_missing_is_not_success(tmp_path):
    r=analyze(tmp_path);assert r['completed']==0 and not r['complete'] and len(r['missing'])==4


def test_four_pairs_report_finite_changes_not_convergence(tmp_path):
    install(tmp_path);r=analyze(tmp_path)
    assert r['complete'] and len(r['contrasts'])==3 and r['new_solver_calls']==0
    assert r['continuous_spectral_convergence']=='HOLD'
    assert all(x['error_radius_certified'] is False for x in r['references'])

@pytest.mark.parametrize('name,key,value',[
 ('IDENTITY.json','binary_sha256','other'),
 ('IDENTITY.json','q',.005),
 ('TABLE.json','source_table_sha256','wrong'),
 ('RESULT.json','status','FAILED')])
def test_mixed_or_failed_records_refused(tmp_path,name,key,value):
    install(tmp_path);p=tmp_path/'m8_r4_table512'/name;d=json.loads(p.read_text());d[key]=value;p.write_text(json.dumps(d))
    with pytest.raises(ValueError):analyze(tmp_path)
