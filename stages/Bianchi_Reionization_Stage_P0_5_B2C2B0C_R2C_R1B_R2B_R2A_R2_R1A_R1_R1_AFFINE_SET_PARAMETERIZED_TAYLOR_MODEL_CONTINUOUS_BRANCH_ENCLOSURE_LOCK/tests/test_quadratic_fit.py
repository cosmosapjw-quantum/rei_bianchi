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

def test_quadratic_fit_supports_tensor_outputs():
 m=load();pts=np.asarray([[-1,-1],[-1,0],[-1,1],[0,-1],[0,0],[0,1],[1,-1],[1,0],[1,1]],float)
 scalar=np.asarray([1+a+2*b+3*a*b for a,b in pts]);values=np.stack([scalar,2*scalar],axis=1)[:,:,None]
 fit=m.QuadraticEndpointFit.fit(pts,values)
 out=fit.evaluate(np.asarray([[.25,-.5]]))
 exact=1+.25+2*(-.5)+3*.25*(-.5)
 assert out.shape==(1,2,1);assert np.allclose(out[0,:,0],[exact,2*exact],atol=2e-13)

def test_exact_box_contains_dense_grid_and_is_tight_for_concave_quadratic():
 m=load();pts=np.asarray([[-1,-1],[-1,0],[-1,1],[0,-1],[0,0],[0,1],[1,-1],[1,0],[1,1]],float)
 vals=np.asarray([4-(a-.2)**2-2*(b+.3)**2+.1*a*b for a,b in pts])
 fit=m.QuadraticEndpointFit.fit(pts,vals)
 lo,hi=fit.exact_box()
 q=np.linspace(-1,1,301);aa,bb=np.meshgrid(q,q,indexing='ij');dense=fit.evaluate(np.column_stack([aa.ravel(),bb.ravel()]))
 assert float(lo)<=float(np.min(dense))+1e-12
 assert float(hi)>=float(np.max(dense))-1e-12
 assert float(hi)-float(np.max(dense))<2e-4
