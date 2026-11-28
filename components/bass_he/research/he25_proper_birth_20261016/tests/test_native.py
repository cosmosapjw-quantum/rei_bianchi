"""Affected HE25 persistent bridge checks against immutable HE22 owner CLI."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("he25_native", HERE / "src/native.py")
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)
SERVER = Path("/root/HE25_NCP_BIRTH_20261016/build/he25_owner_server")
ORIGINAL = Path("/root/HE23_NCP_DENSITY_20261016/build/he22_owner_point")
ORIGINAL_SHA = "981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe"


def original_point(a, gas, gamma, power):
    argv = [str(ORIGINAL), *(format(float(x), ".17e") for x in (a, *gas, *gamma, *power))]
    p = subprocess.run(argv, capture_output=True, text=True, check=True, timeout=20)
    rows = p.stdout.splitlines()
    assert rows[0] == "HE22_NATIVE_POINT_V1"
    return {k: np.array([float(x) for x in columns])
            for k, *columns in (row.split("\t") for row in rows[1:])}


@pytest.mark.parametrize("a,gas,gamma,power", [
    (1/21, [.02, .01, .002, .004], [1e-15, 2e-15, 3e-15], [1e-26, 2e-26, 3e-26]),
    (.1, [.1, .1, .1, 3.], [1e-15]*3, [1e-26]*3),
    (.2, [.4, .2, .1, 5.], [2e-14, 1e-14, 3e-14], [1e-25, 2e-25, 3e-25]),
])
def test_persistent_matches_original_point(a, gas, gamma, power, tmp_path):
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA
    evidence = tmp_path / "points.jsonl.gz"
    with native.NativeOwner(SERVER, evidence_path=evidence) as owner:
        result = owner.point(a, gas, gamma, power)
        assert owner.calls == 1
        assert owner.density(a) == (result["nh"], result["nhe"])
    legacy = original_point(a, gas, gamma, power)
    keys = {
        "nh": "NH_CM3", "nhe": "NHE_CM3", "fraction_dt": "FRACTION_DT",
        "w_dt_ev_per_h_s": "W_DT_EV_PER_H_S", "temperature_K": "TEMP_K",
        "photo_events": "PHOTO_EVENTS", "thermal_micro": "THERMAL_MICRO",
        "binding_micro": "BINDING_MICRO", "escape": "ESCAPE",
        "cmb": "CMB_TO_GAS", "photo_input": "PHOTO_INPUT",
        "ci": "CI_EVENTS", "rr": "RR_EVENTS", "dr": "DR_EVENTS",
    }
    for new, old in keys.items():
        np.testing.assert_array_equal(np.atleast_1d(result[new]), legacy[old], err_msg=new)
    assert np.all(result["ci"] > 0)
    assert np.all(result["rr"] > 0)
    if a != 1/21:
        assert result["dr"] > 0
    else:
        assert result["dr"] == 0.0  # Original low-temperature DR underflow/domain behavior.
    with gzip.open(evidence, "rt") as f:
        records = [json.loads(line) for line in f]
    assert [r["kind"] for r in records] == ["handshake", "point"]
    assert records[1]["request"] and records[1]["response"].startswith("POINT\t")


def test_error_retains_partial_evidence(tmp_path):
    evidence = tmp_path / "error.jsonl.gz"
    with pytest.raises(RuntimeError, match="HE25_OWNER_ERROR"):
        with native.NativeOwner(SERVER, evidence_path=evidence) as owner:
            owner.point(.1, [.1, .1, .1, 3.], [0., 0., 0.], [1e-26, 0., 0.])
    assert not evidence.exists()
    with gzip.open(Path(str(evidence) + ".partial"), "rt") as f:
        records = [json.loads(line) for line in f]
    assert [r["kind"] for r in records] == ["handshake", "point", "failure"]
    assert records[1]["response"].startswith("ERROR\t")


def test_timeout_retains_request_and_does_not_assume_fast_startup(tmp_path):
    fake = tmp_path / "slow.py"
    fake.write_text("#!/usr/bin/env python3\nimport time,sys\n"
                    "time.sleep(.15)\nprint('HE25_OWNER_V1\\tf7830e2f55e7a1938bc3c98f61b60651f8dae474\\t1e-7\\t8.129e-9',flush=True)\n"
                    "sys.stdin.readline()\nprint('owner diagnostic',file=sys.stderr,flush=True)\ntime.sleep(1)\n")
    fake.chmod(0o755)
    evidence = tmp_path / "slow.jsonl.gz"
    # Fake helium density must satisfy the locked Y exactly.
    fake.write_text(fake.read_text().replace("8.129e-9", format(1e-7 * native.Y_HE, ".17e")))
    with pytest.raises(TimeoutError, match="HE25_OWNER_RESPONSE_TIMEOUT"):
        with native.NativeOwner(fake, evidence_path=evidence,
                                timeout=.2, startup_timeout=2.) as owner:
            owner.point(.1, [.1, .1, .1, 3.], [0., 0., 0.], [0., 0., 0.])
    with gzip.open(Path(str(evidence) + ".partial"), "rt") as f:
        records = [json.loads(line) for line in f]
    assert records[0]["kind"] == "handshake"
    failures = [r for r in records if r["kind"] == "failure"]
    assert len(failures) == 1
    assert failures[0]["phase"] == "request"
    assert failures[0]["request"]
    assert "owner diagnostic" in failures[0]["stderr"]


@pytest.mark.parametrize("occupied", ["final", "partial"])
def test_preexisting_evidence_is_untouched_before_native_start(tmp_path, monkeypatch, occupied):
    evidence = tmp_path / "existing.jsonl.gz"
    blocked = evidence if occupied == "final" else Path(str(evidence) + ".partial")
    sentinel = b"preserve-existing-evidence"
    blocked.write_bytes(sentinel)
    monkeypatch.setattr(native.subprocess, "Popen", lambda *args, **kwargs:
                        pytest.fail("native process started before evidence collision check"))
    with pytest.raises(FileExistsError):
        with native.NativeOwner(SERVER, evidence_path=evidence):
            pass
    assert blocked.read_bytes() == sentinel
    assert not (Path(str(evidence) + ".partial") if occupied == "final" else evidence).exists()


def test_gzip_trailer_fsynced_before_create_only_publication(tmp_path, monkeypatch):
    evidence = tmp_path / "published.jsonl.gz"
    events = []
    real_fsync, real_link, real_unlink = native.os.fsync, native.os.link, native.os.unlink

    def fsync(fd):
        events.append(("fsync", Path(f"/proc/self/fd/{fd}").resolve()))
        return real_fsync(fd)

    def link(src, dst):
        events.append(("link", Path(src)))
        return real_link(src, dst)

    def unlink(path, *args, **kwargs):
        events.append(("unlink", Path(path)))
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(native.os, "fsync", fsync)
    monkeypatch.setattr(native.os, "link", link)
    monkeypatch.setattr(native.os, "unlink", unlink)
    with native.NativeOwner(SERVER, evidence_path=evidence):
        pass
    partial = Path(str(evidence) + ".partial")
    link_index = next(i for i, event in enumerate(events) if event[0] == "link")
    unlink_index = next(i for i, event in enumerate(events) if event[0] == "unlink")
    assert ("fsync", partial) in events[:link_index]
    assert events[link_index] == ("link", partial)
    assert events[unlink_index] == ("unlink", partial)
    assert ("fsync", tmp_path) in events[unlink_index+1:]
    assert evidence.exists() and not partial.exists()
    with gzip.open(evidence, "rt") as f:
        assert json.loads(next(f))["kind"] == "handshake"


def test_destination_arriving_at_publication_preserves_both_records(tmp_path, monkeypatch):
    evidence = tmp_path / "raced.jsonl.gz"
    sentinel = b"independent-final-record"
    real_link = native.os.link

    def competing_link(src, dst):
        Path(dst).write_bytes(sentinel)
        return real_link(src, dst)

    monkeypatch.setattr(native.os, "link", competing_link)
    with pytest.raises(FileExistsError):
        with native.NativeOwner(SERVER, evidence_path=evidence):
            pass
    assert evidence.read_bytes() == sentinel
    with gzip.open(Path(str(evidence) + ".partial"), "rt") as f:
        assert json.loads(next(f))["kind"] == "handshake"
