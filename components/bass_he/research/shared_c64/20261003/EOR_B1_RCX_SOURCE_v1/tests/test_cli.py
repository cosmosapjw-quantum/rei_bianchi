import json
import subprocess
import os
import sys
from pathlib import Path
import pytest
from bass_he_rcx import ContractError
from bass_he_rcx.cli import load_config, main

MODEL={'schema':'bass-he.declared-optical-model.v1','data_class':'MANUFACTURED_REFERENCE',
       'energy_over_E0':1.,'ell_values':[0,1,2],'edges':[0.,1.,2.],
       'potential_over_E0':[-1.,0.],'widths_over_E0':[[.1],[0.]]}

def make(tmp):
    f=tmp/'input.json';f.write_text(json.dumps(MODEL));return f

def test_cli_create_and_refuse_overwrite(tmp_path):
    p=make(tmp_path);out=tmp_path/'result.json'
    assert main(['--input',str(p),'--out',str(out)])==0
    assert out.exists()
    before=out.read_bytes(); assert main(['--input',str(p),'--out',str(out)])==2
    assert out.read_bytes()==before

def test_cli_refuses_physical_data_claim(tmp_path):
    p=make(tmp_path);out=tmp_path/'no.json'
    assert main(['--input',str(p),'--out',str(out),'--request-rct'])==2
    assert not out.exists()

@pytest.mark.parametrize('content',['{"schema":1,"schema":2}',json.dumps({**MODEL,'energy_over_E0':float('nan')}),json.dumps({**MODEL,'data_class':'PHYSICAL_RCT_TABLE'}),json.dumps({**MODEL,'unknown':1})])
def test_wrong_config_fails(tmp_path,content):
    p=tmp_path/'bad.json';p.write_text(content)
    with pytest.raises(ContractError):load_config(p)
