from pathlib import Path
import importlib.util,sys,numpy as np
STAGE=Path(__file__).resolve().parents[1]

def load():
 p=STAGE/'analysis/field_trial.py';s=importlib.util.spec_from_file_location('affine_tm_field_trial_test',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def test_coherent_and_independent_field_maps_obey_locked_bounds():
 m=load();lo=np.asarray([0.0,0.3,0.35]);hi=np.asarray([1.0,0.325,0.375])
 v,f=m.branch_fields(lo=lo,hi=hi,alpha=0.0,beta=0.0)
 assert np.allclose(v,0.5*(lo+hi));assert np.all(f==0.55)
 sv=np.asarray([0.,1.,0.]);sf=np.asarray([1.,0.,1.])
 v2,f2=m.branch_fields(lo=lo,hi=hi,v_selector=sv,f_selector=sf)
 assert np.array_equal(v2,np.asarray([0.0,0.325,0.35]));assert np.array_equal(f2,np.asarray([1.0,0.1,1.0]))
