import json,subprocess,sys,os
from pathlib import Path
import pytest
from bass_he_optical_sampling import cli
ROOT=Path(__file__).resolve().parents[1]

def test_build_export(tmp_path):
 p=tmp_path/'table.json'
 assert cli.main(['--root',str(ROOT),'export','--out',str(p)])==0
 x=json.loads(p.read_text());assert len(x['nodes'])==9 and x['physical_accuracy_certified'] is False

def test_evaluate_export(tmp_path):
 p=tmp_path/'q.json'
 assert cli.main(['--root',str(ROOT),'evaluate','9.125','--allow-midpoint-only','--out',str(p)])==0
 x=json.loads(p.read_text());assert x['interpolated'] is True and x['thermal_rate'] is None

@pytest.mark.parametrize('args',[
 ['evaluate','9.125'],['evaluate','10.125','--allow-midpoint-only'],
 ['evaluate','9','--allow-midpoint-only','--production'],
 ['evaluate','nan','--allow-midpoint-only']])
def test_cli_rejects_without_output(tmp_path,args):
 p=tmp_path/'no.json'
 assert cli.main(['--root',str(ROOT),*args,'--out',str(p)])==2
 assert not p.exists()

def test_existing_output_untouched(tmp_path):
 p=tmp_path/'original.json';p.write_bytes(b'original\n')
 assert cli.main(['--root',str(ROOT),'export','--out',str(p)])==2
 assert p.read_bytes()==b'original\n'

def test_input_hashes_bound(tmp_path):
 root=tmp_path/'input';(root/'data').mkdir(parents=True)
 (root/'data/OPTICAL_SAMPLES.json').write_text('[]')
 (root/'data/SAMPLING_DIAGNOSTICS.json').write_text('[]')
 assert cli.main(['--root',str(root),'export','--out',str(tmp_path/'no.json')])==2
 assert not (tmp_path/'no.json').exists()
