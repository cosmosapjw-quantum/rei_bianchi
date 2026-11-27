import json
import os
from pathlib import Path
import subprocess
import sys
import pytest


def run(root, *args):
    env=os.environ.copy()
    env['PYTHONPATH']=env.get('B3_TEST_INSTALLED',str(root/'src'))
    return subprocess.run([sys.executable,'-B','-m','bass_he_atomic_export',*map(str,args)],
                          env=env,capture_output=True,text=True,timeout=20)


def test_registry_cli(root):
    r=run(root,'sources')
    assert r.returncode==0,r.stderr
    assert json.loads(r.stdout)['default_source_id'] is None


def test_valid_export_and_validate(root,request_data,tmp_path):
    inp=tmp_path/'request.json'; inp.write_text(json.dumps(request_data))
    out=tmp_path/'packet.json'
    r=run(root,'export',inp,'--out',out)
    assert r.returncode==0,r.stderr
    p=json.loads(out.read_text());assert len(p['records'])==3
    r=run(root,'validate',out)
    assert r.returncode==0,r.stderr
    assert json.loads(r.stdout)['physical_accuracy_certified'] is False


@pytest.mark.parametrize('mutation',[
    {'temperature_K':['1000','10001']},
    {'acknowledge_source_conflict':False},
    {'quantity':'heat'},
    {'source_id':'WEST82_OPTICAL_REFERENCE_V2'},
])
def test_invalid_batch_creates_no_file(root,request_data,tmp_path,mutation):
    request_data.update(mutation)
    inp=tmp_path/'in.json';inp.write_text(json.dumps(request_data));out=tmp_path/'out.json'
    r=run(root,'export',inp,'--out',out)
    assert r.returncode==2 and 'SOURCE' in r.stderr.upper() or r.returncode==2 and 'DOMAIN' in r.stderr.upper(),r.stderr
    assert not out.exists() and list(tmp_path.glob('.out*'))==[]


def test_existing_output_preserved(root,request_data,tmp_path):
    inp=tmp_path/'in.json';inp.write_text(json.dumps(request_data));out=tmp_path/'out.json'
    out.write_bytes(b'old immutable result')
    r=run(root,'export',inp,'--out',out)
    assert r.returncode==2 and 'OUTPUT_EXISTS' in r.stderr,r.stderr
    assert out.read_bytes()==b'old immutable result'
    assert list(tmp_path.glob('.out*'))==[]


def test_duplicate_json_rejected(root,tmp_path):
    inp=tmp_path/'in.json';inp.write_text('{"a":1,"a":2}')
    r=run(root,'export',inp,'--out',tmp_path/'out.json')
    assert r.returncode==2 and 'DUPLICATE_JSON' in r.stderr,r.stderr


def test_validate_tamper(root,request_data,tmp_path):
    from bass_he_atomic_export import export_packet
    p=export_packet(request_data);p['records'][0]['heat_moment']=0
    inp=tmp_path/'bad.json';inp.write_text(json.dumps(p))
    r=run(root,'validate',inp)
    assert r.returncode==2 and 'MISMATCH' in r.stderr,r.stderr


def test_request_file_missing(root,tmp_path):
    r=run(root,'export',tmp_path/'absent','--out',tmp_path/'out.json')
    assert r.returncode==2 and not (tmp_path/'out.json').exists(),r.stderr
