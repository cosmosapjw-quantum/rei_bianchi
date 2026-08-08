from pathlib import Path
import importlib.util,sys,numpy as np
STAGE=Path(__file__).resolve().parents[1]

def load():
 p=STAGE/'analysis/quadratic_fit.py';s=importlib.util.spec_from_file_location('affine_tm_quadfit_test',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def test_quadratic_fit_reproduces_total_degree_two_map():
 m=load();pts=np.asarray([[-1,-1],[-1,0],[-1,1],[0,-1],[0,0],[0,1],[1,-1],[1,0],[1,1]],float)
 vals=np.asarray([2+3*a-4*b+5*a*a+6*a*b-7*b*b for a,b in pts])
 fit=m.QuadraticEndpointFit.fit(pts,vals)
 test=np.asarray([[-.75,.2],[.4,-.3],[.9,.8]])
 exact=np.asarray([2+3*a-4*b+5*a*a+6*a*b-7*b*b for a,b in test])
 assert np.allclose(fit.evaluate(test),exact,rtol=0,atol=2e-13)
 assert fit.training_residual < 2e-13
