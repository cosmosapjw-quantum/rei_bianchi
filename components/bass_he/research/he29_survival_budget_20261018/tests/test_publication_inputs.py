"""Packaging checks only; no scientific execution."""
from pathlib import Path
import importlib.util
import shutil
import os
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("he29_input_restore",ROOT/"ncp/RESTORE_VERIFIED_INPUTS.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ARCHIVE=Path(os.environ.get("HE29_INPUT_ARCHIVE", "/mnt/data/BASS_HE_HE29_RESUME_COMPLETE_20261018.tar.gz"))

@pytest.mark.skipif(not ARCHIVE.is_file(),reason="archival fixture unavailable; native bootstrap validates downloaded inputs")
def test_archive_restores_exact_inputs_and_is_idempotent(tmp_path):
    shutil.copytree(ROOT/"provenance",tmp_path/"provenance")
    assert MODULE.restore(ARCHIVE,tmp_path)==22
    assert MODULE.verify(tmp_path)==22
    assert MODULE.restore(ARCHIVE,tmp_path)==22

@pytest.mark.skipif(not ARCHIVE.is_file(),reason="archival fixture unavailable")
def test_conflicting_existing_input_is_never_overwritten(tmp_path):
    shutil.copytree(ROOT/"provenance",tmp_path/"provenance")
    p=tmp_path/"inputs/SAVED_NATIVE_POINTS.json";p.parent.mkdir();p.write_text("wrong")
    with pytest.raises(ValueError,match="EXISTING_INPUT_MISMATCH"):
        MODULE.restore(ARCHIVE,tmp_path)
    assert p.read_text()=="wrong"

def test_wrong_archive_is_rejected_before_writes(tmp_path):
    shutil.copytree(ROOT/"provenance",tmp_path/"provenance")
    p=tmp_path/"bad.tar.gz";p.write_bytes(b"invalid")
    with pytest.raises(ValueError,match="ARCHIVE_SHA"):
        MODULE.restore(p,tmp_path)
    assert not (tmp_path/"inputs").exists()
