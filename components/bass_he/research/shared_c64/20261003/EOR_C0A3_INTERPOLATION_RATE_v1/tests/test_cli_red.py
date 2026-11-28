from pathlib import Path
import sys, subprocess, json
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.run([sys.executable,'-B','-m','bass_he_liu_interp','--root',str(ROOT),*args],capture_output=True,text=True)
def test_cli_interpolation_not_native_node():
    p=run('interpolate','EXC:1s:2p','95','--method','linear_E')
    assert p.returncode==0,p.stderr
    d=json.loads(p.stdout); assert d['interpolated'] and not d['physical_certificate']
def test_cli_partial_functional():
    p=run('functional','EXC:1s:2p','10','100','--theta-native','20')
    assert p.returncode==0,p.stderr
    d=json.loads(p.stdout);assert d['full_functional'] is None and d['value']>0
def test_cli_create_only(tmp_path):
    target=tmp_path/'value.json'
    p=run('interpolate','EXC:1s:2p','95','--method','linear_E','--out',str(target))
    assert p.returncode==0,p.stderr
    b=target.read_bytes();p=run('interpolate','EXC:1s:2p','95','--method','linear_E','--out',str(target))
    assert p.returncode==2 and target.read_bytes()==b and 'OUTPUT_EXISTS' in p.stderr
def test_cli_rate_explicit_mapping(tmp_path):
    f=tmp_path/'binding.json';f.write_text(json.dumps({'energy_scale_J_per_native':1e-16,'reduced_mass_kg':1e-27,'authority':'MANUFACTURED_MAPPING_NOT_LIU'}))
    p=run('partial-rate','EXC:1s:2p','10','100','--theta-J','1e-15','--binding',str(f),'--accept-contextual-unit')
    assert p.returncode==0,p.stderr
    d=json.loads(p.stdout); assert d['full_rate_m3_s'] is None and d['binding_status']=='CONDITIONAL_USER_MAPPING'
