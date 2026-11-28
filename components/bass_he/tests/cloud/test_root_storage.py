from dataclasses import replace
import pytest
from bass_he.cloud.storage import GIB, RootStorage, admit_root_storage

def healthy(**changes):
    value=RootStorage('root_backed_host',True,'/dev/vda2','ext4',True,True,False,
                      100*GIB,50*GIB,50*GIB,.5,0)
    return replace(value,**changes)

def test_root_backed_ext4_with_headroom_passes():
    receipt=admit_root_storage(healthy())
    assert receipt['same_filesystem_as_root'] is True
    assert receipt['storage_mode']=='root_backed_host'

@pytest.mark.parametrize('changes,reason',[
    ({'filesystem_available_bytes':19*GIB},'BLOCKED_ROOT_STORAGE_HEADROOM'),
    ({'filesystem_available_fraction':.19},'BLOCKED_ROOT_STORAGE_HEADROOM'),
    ({'read_write':False},'BLOCKED_ROOT_STORAGE_READ_ONLY_OR_ERRORS'),
    ({'path_symlink':True},'BLOCKED_ROOT_STORAGE_PATH'),
    ({'storage_fstype':'xfs'},'BLOCKED_ROOT_STORAGE_IDENTITY'),
    ({'same_filesystem_as_root':False},'BLOCKED_ROOT_STORAGE_PATH'),
    ({'filesystem_errors':1},'BLOCKED_ROOT_STORAGE_READ_ONLY_OR_ERRORS'),
])
def test_root_backed_rejects_unsafe_storage(changes,reason):
    with pytest.raises(RuntimeError,match=reason):admit_root_storage(healthy(**changes))

@pytest.mark.parametrize('changes',[
    {'filesystem_available_bytes':14*GIB},
    {'filesystem_available_fraction':.14},
])
def test_runtime_soft_headroom_stops_new_dispatch(changes):
    with pytest.raises(RuntimeError,match='BLOCKED_STORAGE_HEADROOM'):
        admit_root_storage(healthy(**changes),initial=False)
    assert admit_root_storage(healthy(filesystem_available_bytes=15*GIB,filesystem_available_fraction=.15),initial=False)
