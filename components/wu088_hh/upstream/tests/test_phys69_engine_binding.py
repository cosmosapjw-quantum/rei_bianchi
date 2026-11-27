"""Only the additional engine identity guard introduced after the first assembly."""
import copy
import json
from pathlib import Path

import pytest

from wu088_hh.phys69_all_angular import verify_inherited_engine, digest

ROOT = Path(__file__).resolve().parents[1]


def records():
    old = ROOT/"research/hh_phys68_20261019/profiles/run_l28_t65_completed"
    band = ROOT/"research/hh_phys69_20261019/band/run_j29_36_t65/CERTIFICATE.json"
    return (json.loads((old/"CERTIFICATE.json").read_text()),
            json.loads((old/"REQUEST.json").read_text()), json.loads(band.read_text())["engine"])


def test_actual_saved_producers_use_same_source_and_runtime():
    old, request, engine = records()
    result = verify_inherited_engine(old, request, engine)
    assert len(result["files_sha256"]) == 7
    assert result["flint"] == "3.3.1"


def test_changed_band_kernel_refused():
    old, request, engine = records()
    engine["phys68_reused_engine"]["files_sha256"]["phys68_taylor.py"] = "0"*64
    with pytest.raises(ValueError, match="unchanged PHYS68 engine"):
        verify_inherited_engine(old, request, engine)


def test_self_consistent_forged_request_still_fails_pinned_old_binding():
    old, request, engine = records()
    request["binding"]["engine"]["files_sha256"]["phys68_taylor.py"] = "0"*64
    request["fingerprint"] = digest(request["binding"])
    engine["phys68_reused_engine"] = copy.deepcopy(request["binding"]["engine"])
    with pytest.raises(ValueError, match="old certificate engine binding"):
        verify_inherited_engine(old, request, engine)
