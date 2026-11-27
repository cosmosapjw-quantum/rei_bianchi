import pytest
from bass_he.cloud.resources import HostInventory,worker_limit,render_service

def host(**changes):
    values=dict(affinity=64,quota_cpus=64,effective_memory=128*1024**3,memory_current=1024**3,data_mount=True,unknown_limits=())
    values.update(changes);return HostInventory(**values)
def test_ready_stage_caps_workers():
    assert worker_limit({'workers':64},host(),7,256*1024**2)==7
    assert worker_limit({'workers':64},host(),14,256*1024**2)==14
    assert worker_limit({'workers':64},host(),42,256*1024**2)==42
def test_nested_quota_affinity_intersection():
    assert worker_limit({'workers':64},host(affinity=32,quota_cpus=8),42,256*1024**2)==8
def test_unreadable_limit_is_unknown_not_unlimited():
    with pytest.raises(RuntimeError,match='UNKNOWN'):worker_limit({'workers':64},host(unknown_limits=('cpu.max',)),42,256*1024**2)
def test_soft_memory_pauses_dispatch():
    assert worker_limit({'workers':64},host(memory_current=int(.66*128*1024**3)),42,256*1024**2)==0
def test_missing_data_mount_fails():
    with pytest.raises(RuntimeError,match='MOUNT'):worker_limit({'workers':64},host(data_mount=False),42,256*1024**2)

def test_root_backed_service_uses_root_filesystem_without_mount_dependency():
    unit=render_service({'storage_mode':'root_backed_host','same_filesystem_as_root':True},host(data_mount=False))
    assert 'RequiresMountsFor=/srv/bass-he' not in unit
    assert 'User=bass-he' in unit
    assert 'MemoryMax=' in unit
    with pytest.raises(RuntimeError,match='MOUNT'):
        render_service({'storage_mode':'mounted_host'},host(data_mount=False))
def test_template_no_infinite_restart():
    unit=render_service({},host());assert 'Restart=no' in unit and 'KillMode=control-group' in unit and 'MemoryMax=' in unit
