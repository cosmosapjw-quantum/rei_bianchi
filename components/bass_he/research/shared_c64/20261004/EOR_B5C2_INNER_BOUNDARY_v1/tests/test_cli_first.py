import json
import pytest
from bass_he_inner_boundary.cli import main

def request():
 return {'schema':'bass-he.b5c2.local-polynomial.v1','input_kind':'DECLARED_LOCAL_MODEL',
 'ell':20,'coulomb':6000.,'potential':[-1000.],'width':[1e-22],'energy':1.,'radius':.001,'order':96}


def test_UA_cli(tmp_path):
 p=tmp_path/'a.json';r=main(['ua','--out',str(p)])
 assert r==0 and json.loads(p.read_text())['A_factor_exact']=='256/81'


def test_seed_cli(tmp_path):
 i=tmp_path/'in.json';o=tmp_path/'out.json';i.write_text(json.dumps(request()))
 assert main(['seed',str(i),'--out',str(o)])==0
 assert json.loads(o.read_text())['inner_absorption']>0


def test_overwrite_refusal(tmp_path):
 p=tmp_path/'a.json';p.write_bytes(b'preserved')
 assert main(['ua','--out',str(p)])==2 and p.read_bytes()==b'preserved'


def test_prod_refused(tmp_path):
 p=tmp_path/'a.json'
 assert main(['ua','--out',str(p),'--production'])==2 and not p.exists()

@pytest.mark.parametrize('change',[{'input_kind':'ACTUAL_HE_H_OPTICAL_CURVE'},{'schema':'wrong'},{'default_mass':1000},{'width':[-1]},{'energy':float('nan')}])
def test_malformed_source_rejected(tmp_path,change):
 r=request();r.update(change);i=tmp_path/'in.json';o=tmp_path/'out.json';i.write_text(json.dumps(r))
 assert main(['seed',str(i),'--out',str(o)])==2 and not o.exists()


def test_duplicate_keys_rejected(tmp_path):
 i=tmp_path/'in.json';o=tmp_path/'out.json';s=json.dumps(request());i.write_text(s[:-1]+',"ell":0}')
 assert main(['seed',str(i),'--out',str(o)])==2 and not o.exists()
