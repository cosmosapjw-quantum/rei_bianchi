from pathlib import Path
import pytest
import prepare_native as m
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip'

def test_prepare_entire_frozen_native_and_overlay(tmp_path):
    dest=tmp_path/'native'
    out=m.prepare(ROOT,dest,archive=ARCHIVE)
    assert out.get('native_sha')=='35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
    assert out['original_input_count']==153
    assert (dest/'rust/rei_microphysics/Cargo.toml').is_file()
    assert 'native_refine' in (dest/'rust/rei_microphysics/examples/positive_native.rs').read_text()
    assert (dest/'positive_solver_refined.py').is_file()
    for rel,digest in out['outputs'].items(): assert m.sha(dest/rel)==digest
    assert out['native_compile']=='NOT_RUN_BY_PREPARER'

def test_prepare_exact_repeat_and_changed_input(tmp_path):
    dest=tmp_path/'native'
    a=m.prepare(ROOT,dest,archive=ARCHIVE)
    b=m.prepare(ROOT,dest,archive=ARCHIVE)
    assert a==b
    assert dest.is_dir()
    (dest/'rust/rei_microphysics/src/igm_rates.rs').write_text('changed')
    with pytest.raises(ValueError,match='EXISTING'):
        m.prepare(ROOT,dest,archive=ARCHIVE)

def test_changed_archive_rejected_before_output(tmp_path):
    bad=tmp_path/'bad.zip';bad.write_bytes(b'not the donor')
    with pytest.raises(ValueError,match='ARCHIVE_SHA'):
        m.prepare(ROOT,tmp_path/'native',archive=bad)
    assert not (tmp_path/'native').exists()
