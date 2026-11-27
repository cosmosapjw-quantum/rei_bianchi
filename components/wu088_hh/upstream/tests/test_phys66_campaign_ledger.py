from wu088_hh.phys66_campaign_ledger import claim_gate

def test_analytic_bound_is_not_a_numerical_error_certificate():
    gate=claim_gate({'radial_bound':'small'})
    assert gate['total_error_certified'] is False

from pathlib import Path
import hashlib,io,json,zipfile
import pytest
from wu088_hh.phys66_campaign_ledger import inspect_archive,EXPECTED_NCP_SHA,_safe_path

@pytest.mark.parametrize('bad',['../data','/tmp/bad','a\\b'])
def test_path_escape_rejected(bad):
    with pytest.raises(ValueError):_safe_path(bad)

def test_arbitrary_external_number_cannot_certify():
    with pytest.raises(ValueError):claim_gate({},numerical_error_bound=0)

def test_bad_archive_sha_fails_before_parsing(tmp_path):
    p=tmp_path/'bad.zip';p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='SHA'):inspect_archive(p)

def test_internal_manifest_checks_are_not_replaced_by_outer_sha(tmp_path):
    p=tmp_path/'manufactured.zip'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('data','unchanged')
        z.writestr('MANIFEST.json',json.dumps({'data':'0'*64}))
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='manifest mismatch'):inspect_archive(p,h)

def test_duplicate_archive_path_rejected(tmp_path):
    import warnings
    p=tmp_path/'manufactured_dup.zip'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('data','a');z.writestr('data','b')
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='duplicate'):inspect_archive(p,h)
