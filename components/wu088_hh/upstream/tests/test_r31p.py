import pytest


def test_midpoint_plan_preserves_r31j_preregistration_and_direct_only_scope():
    import wu088_hh.r31p as r31p
    plan=r31p.midpoint_plan(existing_ionic_nodes={4,12,24})
    assert plan['midpoints']==[4,12,24,40,56]
    assert plan['h_orders']==[160,192]
    assert plan['od_z']==[4,12,24,40,56]
    assert plan['jvp_z']==[4,12,24,40,56]
    assert plan['ionic_reuse']==[4,12,24]
    assert plan['ionic_compute']==[40,56]
    assert plan['interpolation_evaluated'] is False
    assert plan['trajectory_runs']==0
    assert plan['production_admitted'] is False


def test_interpolation_contract_is_frozen_before_midpoint_values():
    import wu088_hh.r31p as r31p
    c=r31p.interpolation_contract()
    assert c=={
        'method':'piecewise_linear_only_after_midpoint_validation',
        'H_midpoint_max_abs_Eh':2e-7,
        'whitened_independent_generator_relative_error':2e-12,
        'interpolated_raw_gates_must_also_pass':True,
        'adaptive_rule':'bisect_only_failing_intervals',
        'minimum_interval_width_a0':1.0,
        'on_failure':'STOP_INTERPOLATION_RESOLUTION_UNRESOLVED',
    }


def test_h_folder_uses_exact_binary64_z_encoding():
    import wu088_hh.r31p as r31p
    assert r31p.h_folder_name(192,4.0)=='B192_g80_sunit_z4010000000000000'
    assert r31p.h_folder_name(160,56.0)=='B160_g80_sunit_z404c000000000000'


def test_midpoint_plan_rejects_unregistered_or_missing_reuse_nodes():
    import wu088_hh.r31p as r31p
    with pytest.raises(ValueError,match='ionic reuse'):
        r31p.midpoint_plan(existing_ionic_nodes={4,12,24,40})


def _load_r31p_midpoint_script():
    import importlib.util
    from pathlib import Path
    script=Path(__file__).resolve().parents[1]/'scripts'/'r31p_midpoint_direct.py'
    spec=importlib.util.spec_from_file_location('r31p_midpoint_direct_under_test',script)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def test_backed_h_seal_is_reused_across_volatile_run_state_changes(tmp_path):
    import json
    mod=_load_r31p_midpoint_script()
    folder=tmp_path/'state';folder.mkdir()
    for name,data in [('IDENTITY.json',b'i'),('RESULTS.json',b'r'),('ASSEMBLED.npz',b'a'),('pair_00_00.npz',b'p')]:
        (folder/name).write_bytes(data)
    (folder/'RUN_STATE.json').write_text('first')
    seal=tmp_path/'seal.zip';first=mod.deterministic_state_seal(folder,seal)
    receipt=tmp_path/'receipt.json'
    receipt.write_text(json.dumps({'source_sha256':first[0],'source_bytes':first[1],'dual_raw_readback_verified':True,'status':'DUAL_RAW_READBACK_VERIFIED','providers':{}}))
    (folder/'RUN_STATE.json').write_text('second')
    old,identity=mod.reuse_or_restore_backed_seal(seal,receipt,folder)
    assert identity==first
    assert mod.digest(seal)==first
    assert old['status']=='DUAL_RAW_READBACK_VERIFIED'

def test_backed_h_seal_can_be_restored_after_local_overwrite(tmp_path,monkeypatch):
    import json,shutil,types
    mod=_load_r31p_midpoint_script()
    folder=tmp_path/'state';folder.mkdir()
    for name,data in [('IDENTITY.json',b'i'),('RESULTS.json',b'r'),('ASSEMBLED.npz',b'a'),('pair_00_00.npz',b'p')]:
        (folder/name).write_bytes(data)
    remote=tmp_path/'remote.zip';expected=mod.deterministic_state_seal(folder,remote)
    receipt=tmp_path/'receipt.json'
    receipt.write_text(json.dumps({'source_sha256':expected[0],'source_bytes':expected[1],'dual_raw_readback_verified':True,'status':'DUAL_RAW_READBACK_VERIFIED','providers':{'google_drive':{'destination':'fake:seal'}}}))
    local=tmp_path/'local.zip';local.write_bytes(b'overwritten-local-seal')
    def fake_run(cmd,**kwargs):
        shutil.copy2(remote,cmd[-1]);return types.SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(mod.subprocess,'run',fake_run)
    _,identity=mod.reuse_or_restore_backed_seal(local,receipt,folder)
    assert identity==expected
    assert mod.digest(local)==expected


def test_cp4_ionic_executable_mode_repair_is_hash_bound_and_byte_preserving(tmp_path):
    import hashlib,os,stat
    import wu088_hh.r31p as r31p
    base=tmp_path/'completion'/'ionic';base.mkdir(parents=True)
    old=dict(r31p.CP4_IONIC_EXECUTABLE_SHA256)
    try:
        payloads={'duffy_polar_double':b'\x7fELFdouble','duffy_polar':b'\x7fELFlongdouble'}
        r31p.CP4_IONIC_EXECUTABLE_SHA256={k:hashlib.sha256(v).hexdigest() for k,v in payloads.items()}
        for name,data in payloads.items():
            p=base/name;p.write_bytes(data);p.chmod(0o600)
        out=r31p.ensure_cp4_ionic_executables(tmp_path)
        assert out['status']=='CP4_IONIC_EXECUTABLE_MODES_VERIFIED'
        for name,data in payloads.items():
            p=base/name
            assert hashlib.sha256(p.read_bytes()).hexdigest()==r31p.CP4_IONIC_EXECUTABLE_SHA256[name]
            assert stat.S_IMODE(p.stat().st_mode)&stat.S_IXUSR
            assert os.access(p,os.X_OK)
    finally:
        r31p.CP4_IONIC_EXECUTABLE_SHA256=old

def test_cp4_ionic_executable_mode_repair_refuses_hash_drift(tmp_path):
    import hashlib,stat
    import pytest
    import wu088_hh.r31p as r31p
    base=tmp_path/'completion'/'ionic';base.mkdir(parents=True)
    old=dict(r31p.CP4_IONIC_EXECUTABLE_SHA256)
    try:
        r31p.CP4_IONIC_EXECUTABLE_SHA256={'duffy_polar_double':'0'*64,'duffy_polar':'1'*64}
        for name in r31p.CP4_IONIC_EXECUTABLE_SHA256:
            p=base/name;p.write_bytes(b'\x7fELFwrong');p.chmod(0o600)
        with pytest.raises(ValueError,match='hash mismatch'):
            r31p.ensure_cp4_ionic_executables(tmp_path)
        assert stat.S_IMODE((base/'duffy_polar_double').stat().st_mode)==0o600
    finally:
        r31p.CP4_IONIC_EXECUTABLE_SHA256=old


def test_cp4_ionic_executable_manifest_covers_complete_runtime_call_graph():
    import wu088_hh.r31p as r31p
    assert r31p.CP4_IONIC_EXECUTABLE_SHA256 == {
        'duffy_polar_double':'16bdcd528c53193ed53bfe371e74b804644c1b3491e014ac6f088f2d3667bf75',
        'duffy_polar':'36ed3a81c76ce6fe95bb7fbde43d3931d5e817ed66951ba3ac2ff0aed8d8fb0f',
        'diagonal':'9df0b914fca2d3df26681d3476aec5d878eae199684e580eb9544177d03ff560',
        'half_hermite':'dfbc2b434beecdfe4354fb18dca28ee3172c6f8e3957050464f4809c48de99ff',
    }
