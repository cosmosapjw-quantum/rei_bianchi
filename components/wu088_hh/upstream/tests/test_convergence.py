import numpy as np
import pytest
from wu088_hh.convergence import compare_h


def test_convergence_rejects_nonfinite_not_zero_failures():
    a=np.zeros((47,2),np.clongdouble);b=a.copy();b[1,0]=np.nan
    with pytest.raises(ValueError,match='finite'):compare_h(a,b)


def test_complete_94_entry_comparison_and_failure():
    a=np.zeros((47,2),np.clongdouble);b=a.copy();b[7,1]=3e-7j
    r=compare_h(a,b)
    assert r['entries']==94 and r['failure_count']==1
    assert r['worst_index']==[7,1]
    assert r['status']=='FAIL_H_ORDER_COMPARISON'


def test_max_of_matrix_norms_is_not_entrywise_comparison():
    a=np.zeros((47,2),np.clongdouble);b=a.copy();a[0,0]=1;b[0,1]=1
    r=compare_h(a,b)
    assert r['failure_count']==2


def test_no_broadcasting_or_dtype_downcast():
    with pytest.raises(ValueError,match='47'):compare_h(np.zeros(47),np.zeros((47,2)))
