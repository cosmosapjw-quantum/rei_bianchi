from pathlib import Path
import importlib.util,sys
import numpy as np
from scipy.interpolate import PchipInterpolator
HERE=Path(__file__).resolve().parents[1]/'analysis'
def load(name):
 p=HERE/f'{name}.py';s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def test_cubic_bernstein_bound_contains_dense_polynomial_values():
    mod=load('pchip_bounds')
    c=np.array([1.7,-2.3,0.4,5.1])
    lo,hi=mod.cubic_power_range(c,-0.3,0.8)
    x=np.linspace(-0.3,0.8,10001)
    y=((c[0]*x+c[1])*x+c[2])*x+c[3]
    assert lo <= y.min()
    assert hi >= y.max()

def test_ppoly_bound_contains_dense_pchip_values_and_is_tight_on_microinterval():
    mod=load('pchip_bounds')
    x=np.array([0.,1.,2.,4.]);y=np.array([2.,4.,1.,3.])
    p=PchipInterpolator(x,y)
    lo,hi=mod.ppoly_range(p,0.0,0.08)
    q=p(np.linspace(0,0.08,1001))
    assert lo <= q.min() and hi >= q.max()
    assert hi-lo < 0.5
