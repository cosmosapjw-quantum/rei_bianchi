import pytest
from bass_he.cloud.backend import activate,prepare_environment,THREAD_POLICY

def test_missing_numba_is_explicit():
    with pytest.raises(RuntimeError,match='ACCELERATOR_PAYLOAD_UNAVAILABLE'):activate('numba')
def test_thread_policy_applied():
    prepare_environment()
    import os
    assert all(os.environ[k]=='1' for k in THREAD_POLICY)
