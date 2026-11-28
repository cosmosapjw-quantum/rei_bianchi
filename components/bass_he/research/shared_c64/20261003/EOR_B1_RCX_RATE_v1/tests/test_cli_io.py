import json, os, subprocess, sys
from pathlib import Path
import pytest
from bass_he_rcx import SOURCE_ID,ContractError,parse_fit_excerpt,rate,batch
from bass_he_rcx.io import write_json_create_only
FLAGS=['--source-id',SOURCE_ID,'--distribution','MAXWELL_COMMON_T_ZERO_DRIFT','--acknowledge-source-conflict']
def cli(args, root):
    env=dict(os.environ)
    env['PYTHONPATH']=os.environ.get('B1_TEST_INSTALLED',str(root/'src'))
    return subprocess.run([sys.executable,'-B','-m','bass_he_rcx',*args],env=env,capture_output=True,text=True)

def test_cli_rate_real(root):
    a=cli(['rate','1000',*FLAGS],root)
    assert a.returncode==0 and json.loads(a.stdout)['rate_token']=='1.70E-19'

def test_cli_no_ack(root):
    a=cli(['rate','1000',*FLAGS[:-1]],root)
    assert a.returncode==2 and 'ACKNOWLEDGE' in a.stderr

def test_cli_counts_output(root,tmp_path):
    p=tmp_path/'out.json';a=cli(['counts','1000',*FLAGS,'--out',str(p)],root)
    assert a.returncode==0 and json.loads(p.read_text())['photon_number_per_event']==1

def test_cli_domain_no_output(root,tmp_path):
    p=tmp_path/'out.json';a=cli(['rate','10001',*FLAGS,'--out',str(p)],root)
    assert a.returncode==2 and not p.exists()

def test_cli_create_only(root,tmp_path):
    p=tmp_path/'out.json';p.write_bytes(b'ORIGINAL')
    a=cli(['rate','1000',*FLAGS,'--out',str(p)],root)
    assert a.returncode==2 and p.read_bytes()==b'ORIGINAL'

def test_io_actual(tmp_path):
    p=tmp_path/'out.json';write_json_create_only(p,{'a':1})
    assert p.exists() and json.loads(p.read_text())=={'a':1}

def test_io_existing(tmp_path):
    p=tmp_path/'out.json';p.write_bytes(b'A')
    with pytest.raises(FileExistsError):write_json_create_only(p,{'a':1})
    assert p.read_bytes()==b'A'

def test_io_symlink(tmp_path):
    a=tmp_path/'a';a.write_bytes(b'B');p=tmp_path/'p';p.symlink_to(a)
    with pytest.raises(FileExistsError):write_json_create_only(p,{'a':1})
    assert a.read_bytes()==b'B'

def test_io_nan_no_artifact(tmp_path):
    p=tmp_path/'out.json'
    with pytest.raises(ValueError):write_json_create_only(p,{'x':float('nan')})
    assert not p.exists()
