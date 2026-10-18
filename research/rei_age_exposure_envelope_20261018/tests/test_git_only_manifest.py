"""A Git checkout need not carry a second copy of the frozen 153-file manifest."""
from pathlib import Path
import shutil
import pytest
from prepare_native import prepare
ROOT=Path(__file__).resolve().parents[1]

def test_git_only_restore_reconstructs_the_exact_native_input_map(tmp_path):
    root=tmp_path/'checkout';root.mkdir()
    shutil.copytree(ROOT/'donors/pr171',root/'donors/pr171')
    (root/'contracts').mkdir()
    shutil.copy2(ROOT/'contracts/DONOR_IDENTITY.json',root/'contracts/DONOR_IDENTITY.json')
    try:
        result=prepare(root,tmp_path/'native',archive=ROOT/'donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip')
    except FileNotFoundError as e:
        pytest.fail('GIT_ONLY_MANIFEST_RECONSTRUCTION_MISSING: '+str(e))
    assert result['original_input_count']==153
    assert result['native_sha']=='35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
