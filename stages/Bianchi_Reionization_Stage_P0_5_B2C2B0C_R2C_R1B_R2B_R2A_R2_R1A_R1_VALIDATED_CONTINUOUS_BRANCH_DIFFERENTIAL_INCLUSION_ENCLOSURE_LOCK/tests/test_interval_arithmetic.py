from pathlib import Path
import importlib.util, sys
import numpy as np

HERE=Path(__file__).resolve().parents[1]/'analysis'
def load(name):
 p=HERE/f'{name}.py'; s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def test_basic_interval_operations_enclose_dense_samples():
    iv=load('interval_arithmetic')
    a=iv.Interval(np.array([-2.0,0.5]),np.array([3.0,2.0]))
    b=iv.Interval(np.array([1.0,2.0]),np.array([4.0,5.0]))
    rng=np.random.default_rng(1201)
    for _ in range(500):
        x=a.lo+(a.hi-a.lo)*rng.random(2)
        y=b.lo+(b.hi-b.lo)*rng.random(2)
        for result,value in [
            (a+b,x+y),(a-b,x-y),(a*b,x*y),(a/b,x/y),
        ]:
            assert np.all(result.lo <= value)
            assert np.all(value <= result.hi)

def test_positive_transcendentals_and_sum_are_outward():
    iv=load('interval_arithmetic')
    x=iv.Interval(np.array([0.2,2.0]),np.array([0.8,3.0]))
    for result,lo,hi in [
        (iv.exp(x),np.exp(x.lo),np.exp(x.hi)),
        (iv.log(x),np.log(x.lo),np.log(x.hi)),
        (iv.sqrt(x),np.sqrt(x.lo),np.sqrt(x.hi)),
        (iv.pow_const(x,1.7),x.lo**1.7,x.hi**1.7),
    ]:
        assert np.all(result.lo <= lo)
        assert np.all(result.hi >= hi)
    s=iv.sum_interval(x)
    assert s.lo <= np.sum(x.lo,dtype=np.longdouble)
    assert s.hi >= np.sum(x.hi,dtype=np.longdouble)
