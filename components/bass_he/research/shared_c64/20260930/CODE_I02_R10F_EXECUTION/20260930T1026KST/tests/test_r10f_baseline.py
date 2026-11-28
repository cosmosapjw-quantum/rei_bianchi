from r10f_lanes import classify_baseline_rows


def row(before, now, old_err=1e-5, new_err=1e-5):
    return {'r10c_value':before,'r10f_value':now,
            'absolute_difference':abs(now-before),
            'r10c_embedded_estimate':old_err,
            'r10f_embedded_estimate':new_err}


def test_baseline_small_difference_passes():
    assert classify_baseline_rows([row(100,100.1)])['status']=='PASS'


def test_baseline_material_difference_stops():
    assert classify_baseline_rows([row(100,102)])['status']=='R10F_BASELINE_REGRESSION_UNRESOLVED'


def test_baseline_tiny_absolute_difference_passes():
    assert classify_baseline_rows([row(1e-10,2e-10)])['status']=='PASS'
