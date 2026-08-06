from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]

def sha256(p):
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    return h

def test_upload_recovery_is_non_promoting_and_hash_locked():
    state=json.loads((ROOT/'STAGE_STATE.json').read_text())
    inv=json.loads((ROOT/'RECOVERY_INVENTORY.json').read_text())
    assert state['status']=='PARTIALLY_RECOVERED'
    assert state['science_promotion_authorized'] is False
    assert state['R2C_R1B_R2_authorized'] is False
    assert inv['original_git_object_recovered'] is False
    assert inv['original_bundle_bytes_recovered'] is False
    for item in inv['recovered_files']:
        p=Path(__file__).resolve().parents[3]/item['path']
        assert p.exists()
        assert sha256(p)==item['sha256']
