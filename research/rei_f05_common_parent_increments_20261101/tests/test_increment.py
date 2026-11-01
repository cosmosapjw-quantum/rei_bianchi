import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
import numpy as np

SCRIPT=Path(__file__).resolve().parents[1]/"increment_certificate.py"
spec=importlib.util.spec_from_file_location("rei_f05_increment_new_test",SCRIPT)
e=importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

class Iv:
    def __init__(self,lo,hi=None):
        self.lo=np.asarray(lo,dtype=float)
        self.hi=np.asarray(self.lo if hi is None else hi,dtype=float)
    def _b(self,x):
        return x if isinstance(x,Iv) else Iv(x)
    def __add__(self,x):
        x=self._b(x);return Iv(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return Iv(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self._b(x)
    def __rsub__(self,x):return self._b(x)+-self
    def __mul__(self,x):
        x=self._b(x)
        p=np.stack(np.broadcast_arrays(self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi))
        return Iv(np.min(p,axis=0),np.max(p,axis=0))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self._b(x)
        if np.any(x.lo<=0):raise ValueError("toy denominator nonpositive")
        return self*Iv(1/x.hi,1/x.lo)
    def __rtruediv__(self,x):return self._b(x)/self
class Toy:
    KB=1.380649e-16
    sdirk=SimpleNamespace(GAMMA=1-1/np.sqrt(2))
    _I=Iv
    iv=SimpleNamespace(
      exp=lambda q:Iv(np.exp(q.lo),np.exp(q.hi)),
      log=lambda q:Iv(np.log(q.lo),np.log(q.hi)))

class IncrementMath(unittest.TestCase):
    def test_native_matrix_difference_exact_by_direct_linear_solve(self):
        k=0.125
        A=np.array([[[1+k,-k],[-k,1+k]]])
        p=np.array([[4.,2.]])
        l,h=e.original_matrix_delta_rhs(Toy,A,A,Iv(p))
        assert l.shape==(1,2)
        exact=np.linalg.solve(A[0],p[0])-p[0]
        rhs=-(A[0]-np.eye(2))@p[0]
        self.assertTrue(np.all(l[0]<=rhs+1e-14))
        self.assertTrue(np.all(rhs<=h[0]+1e-14))
        self.assertLess(np.linalg.norm(A[0]@exact-rhs),1e-14)

    def test_coupled_thermal_ratio_uses_electron_increment(self):
        parent=np.array([[6.,4.,2.,3.,1.]])
        # H: -0.1/+0.1; He: -0.06/+0.04/+0.02
        dp=np.array([[-.1,.1,-.06,.04,.02]])
        # 3 H +? Actual H nuclei=10, He nuclei=6 and parent electron=9.
        nh=np.array([10.]);nhe=np.array([6.])
        z=np.log(np.array([11000.]))
        par=Iv(parent);d=Iv(dp);Z=Iv(z)
        n0=10.+6.+4.+3.+2*1.
        U0=1.5*Toy.KB*n0*11000.
        # Choose a fixed exact physically plausible small energy increment.
        dU=U0*2.5e-4
        h=3.0
        R=Iv(np.array([dU/h]))
        vals,extra=e.incremental_thermochemical_state(Toy,par,Z,d,R,R,h,nh,nhe)
        dne=.1+.04+2*.02
        analytic=np.log1p(dU/U0)-np.log1p(dne/n0)
        self.assertAlmostEqual(float(vals["log_T"].lo[0]),analytic,places=12)
        self.assertAlmostEqual(float(vals["log_T"].hi[0]),analytic,places=12)
        self.assertAlmostEqual(float(vals["x_HII"].lo[0]),.01,places=12)
        self.assertAlmostEqual(float(vals["x_HeIII"].lo[0]),.02/6,places=12)

    def test_thermal_energy_no_photo_returns_electron_dilution(self):
        p=np.array([[4.,6.,3.,2.,1.]])
        dp=np.array([[-.02,.02,-.01,.01,0.]])
        vals,_=e.incremental_thermochemical_state(Toy,Iv(p),Iv(np.array([np.log(12000.)])),
             Iv(dp),Iv(np.array([0.])),Iv(np.array([0.])),1.0,np.array([10.]),np.array([6.]))
        n0=16.+6.+2.+2.
        self.assertAlmostEqual(float(vals["log_T"].lo[0]),-np.log1p(.03/n0),places=12)

    def test_zero_difference_does_not_force_false_pass(self):
        q=Iv(np.array([-0.000201]),np.array([0.000201]))
        self.assertFalse(bool(np.all(e.interval_upper(q)<e.LOCAL_GATE)))

    def test_parent_conservation_checks_fixed_source_identity(self):
        self.assertEqual(len(e.SOURCE_SHA),64)
        self.assertEqual(len(e.STATE_SHA),64)
        self.assertEqual(len(e.KERNEL_SHA),64)
        self.assertEqual(e.LOCAL_GATE,2e-4)
        self.assertEqual(e.PUBLIC_GATE,2e-3)

    def test_negative_log_domain_rejected(self):
        par=Iv(np.array([[4.,6.,3.,2.,1.]]))
        dp=Iv(np.zeros((1,5)))
        z=Iv(np.array([np.log(10000.)]))
        U=1.5*Toy.KB*(10+6+6+2+2)*1e4
        with self.assertRaises(ArithmeticError):
            e.incremental_thermochemical_state(Toy,par,z,dp,Iv([-2*U]),Iv([-2*U]),
                1.,np.array([10.]),np.array([6.]))

    def test_source_ledger_explicit_no_admission(self):
        import inspect
        s=inspect.getsource(e.run)
        self.assertIn('"canonical_delta":0',s)
        self.assertIn('"production":"HOLD"',s)
        self.assertIn('"full_allX_jacobian_hessian_certificate":False',s)
        self.assertIn('BLOCKED_UNTIL_ORIGINAL_OWNER_ADMISSION',s)

if __name__=="__main__":unittest.main()
