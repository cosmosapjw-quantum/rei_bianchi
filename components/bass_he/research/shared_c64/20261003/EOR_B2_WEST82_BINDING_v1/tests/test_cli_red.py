import json
import pytest
from bass_he_west82.cli import main

@pytest.fixture
def model(tmp_path):
    f=tmp_path/'model.json'
    f.write_text(json.dumps({'data_class':'MANUFACTURED_REFERENCE','energy_over_E0':1.,'ell_values':[33,48],'edges':[0.,51.],'potential_over_E0':[0.],'widths_over_E0':[[1e-22]]}))
    return f

def test_cli_high_l_output(model,tmp_path):
    o=tmp_path/'out.json'
    assert main(['solve','--input',str(model),'--out',str(o)])==0
    r=json.loads(o.read_text())
    assert len(r['partial_waves'])==2 and r['physical_RCT_prediction'] is False
    assert r['partial_sum']['full_cross_section'] is None

def test_table_cli_binding(root,tmp_path):
    o=tmp_path/'table.json'
    assert main(['table','--root',str(root),'--out',str(o)])==0
    assert len(json.loads(o.read_text())['rows'])==25

def test_cli_refuse_overwrite(model,tmp_path):
    o=tmp_path/'out.json';o.write_text('prior evidence')
    assert main(['solve','--input',str(model),'--out',str(o)])==2
    assert o.read_text()=='prior evidence'

def test_cli_refuse_physical_claim(model,tmp_path):
    o=tmp_path/'out.json'
    assert main(['solve','--input',str(model),'--out',str(o),'--physical-rct'])==2
    assert not o.exists()

@pytest.mark.parametrize('data',[
    '{"data_class":1,"data_class":2}',
    '{"energy_over_E0":NaN}',
    '{"data_class":"PHYSICAL_WEST_DATA"}',
])
def test_invalid_configuration_no_output(data,tmp_path):
    f=tmp_path/'bad.json';f.write_text(data);o=tmp_path/'out.json'
    assert main(['solve','--input',str(f),'--out',str(o)])==2
    assert not o.exists()
