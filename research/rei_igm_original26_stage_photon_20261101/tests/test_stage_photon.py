"""Original stage photon global moment algebra. No fake 46,080-node PASS here."""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rei_stage_original_photon",HERE/"stage_photon_audit.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class OriginalPhotonStage(unittest.TestCase):
    def test_constants_preserved(self):
        self.assertEqual((m.N,m.G,m.S),(46080,4,3))
        self.assertEqual((m.GATE,m.WIDTH),(2e-4,2e-3))
    def test_share_jacobian_analytic(self):
        p=np.array([.2,.3,.4])
        self.assertLess(np.max(abs(m.exact_three_moment_derivative(p)-
            (np.diag(p)-np.outer(p,p)))),1e-16)
    def test_share_jacobian_psd(self):
        for p in ([.1,.2,.3],[.25,.25,.25],[.3,.4,.3],[0.,.1,.2]):
            w=np.linalg.eigvalsh(m.exact_three_moment_derivative(p))
            self.assertGreaterEqual(np.min(w),-2e-16)
    def test_negative_share_rejected(self):
        for p in ([-.1,.2,.4],[1.,.1,.1]):
            with self.assertRaises(ValueError):m.exact_three_moment_derivative(p)
    def test_denominator_derivative_exact(self):
        n=m.N
        rate=np.full((n,3),.1)
        p=np.array([.2,.4,.1])
        d=-rate[:,:,None]*p[None,None,:]
        self.assertLess(m.check_unit_reaction_rates(rate,d,p),1e-15)
    def test_denominator_derivative_rejects_wrong_shape(self):
        with self.assertRaises(ValueError):
            m.check_unit_reaction_rates(np.zeros((3,3)),np.zeros((3,3,3)),np.ones(3))
    def test_schur_with_two_global_source_sites(self):
        rng=np.random.default_rng(712)
        n=16;k=6
        a=np.zeros((n,n))
        for t in range(4):
            z=rng.normal(size=(4,4));a[4*t:4*t+4,4*t:4*t+4]=z.T@z+4*np.eye(4)
        b=rng.normal(size=(n,k))*.04
        v=rng.normal(size=(n,k))*.08
        rhs=rng.normal(size=n)
        result,schur=m.woodbury(a,b,v,rhs)
        dense=np.linalg.solve(a+b@v.T,rhs)
        self.assertLess(float(np.max(abs(result-dense))),2e-14)
        self.assertEqual(schur.shape,(k,k))
    def test_schur_bad_singularity_fails(self):
        with self.assertRaises(np.linalg.LinAlgError):
            m.woodbury(np.zeros((2,2)),np.ones((2,1)),np.ones((2,1)),np.ones(2))
    def test_source_archive_identity(self):
        self.assertEqual(m.SOURCE_SHA,"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(len(m.STATE_SHA),64)
if __name__=="__main__":unittest.main()
