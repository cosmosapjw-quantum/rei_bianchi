"""No IVP, no callable native BASS donor import or guessed physical rate tables."""
import sys, pathlib, unittest, numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'code'))
import feedback as f


def fixture(seed=0):
    rng=np.random.default_rng(seed)
    # Declared SYNTHETIC finite positive reaction coefficients: NOT the BASS table.
    gp=np.zeros((21,21)); gr=np.zeros((21,21)); D=np.zeros((21,21))
    for group in f.GROUPS[1:]:
        for src,dst in zip(group[:-1],group[1:]):
            a=float(rng.uniform(1e-4,1e-3))
            r=float(rng.uniform(1e-8,1e-7))
            gp[dst,src]+=a; gp[src,src]-=a
            gr[src,dst]+=r; gr[dst,dst]-=r
    for src,dst,r in ((0,2,.004),(5,8,.00002),(6,9,.00002)):
        D[src,src]-=r;D[dst,src]+=r
    Y=rng.uniform(.0001,.1,21)
    Y=Y/(f.A@Y)
    nb=1e3
    return Y,gp,gr,D,nb


class PhysicalFastFeedback(unittest.TestCase):
    def test_01_exact_native_indices(self):
        self.assertEqual(f.A.tolist(),[1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7])
        self.assertEqual(f.Q.tolist(),[0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3])
        self.assertEqual(sum(map(len,f.GROUPS)),21)
    def test_02_analytic_fd(self):
        for seed in range(7):
            Y,g,r,d,nb=fixture(seed);v=np.random.default_rng(seed+80).normal(size=21)
            c=f.physical_rhs_jac(Y,g,r,d,nb)
            h=1e-6
            fd=(f.physical_rhs_jac(Y+h*v,g,r,d,nb)['rhs']-f.physical_rhs_jac(Y-h*v,g,r,d,nb)['rhs'])/(2*h)
            np.testing.assert_allclose(fd,c['jac']@v,rtol=2e-8,atol=2e-12)
    def test_03_rankone_and_baryon(self):
        for seed in range(8):
            Y,g,r,d,nb=fixture(seed)
            c=f.physical_rhs_jac(Y,g,r,d,nb)
            np.testing.assert_allclose(c['jac'],c['frozen']+np.outer(c['u'],f.Q),atol=0,rtol=0)
            self.assertLess(abs(f.A@c['rhs']),1e-15)
            self.assertLess(max(abs(f.A@c['jac'])),1e-15)
    def test_04_solve_direct(self):
        for seed in range(17):
            Y,g,r,d,nb=fixture(seed);rng=np.random.default_rng(seed+150)
            c=f.physical_rhs_jac(Y,g,r,d,nb)
            dt=.1; M=np.eye(21)-dt*c['frozen']; b=rng.normal(size=21)
            out=f.rank_one_solve(M,c['u'],f.Q,dt,b)
            direct=np.linalg.solve(np.eye(21)-dt*c['jac'],b)
            np.testing.assert_allclose(out.solution,direct,rtol=3e-13,atol=3e-13)
            self.assertLess(out.relative_residual,5e-15)
            self.assertLess(out.residual_identity_defect,1e-13)
    def test_05_inexact_residual_identity(self):
        Y,g,r,d,nb=fixture(5);c=f.physical_rhs_jac(Y,g,r,d,nb)
        dt=.2;M=np.eye(21)-dt*c['frozen'];b=np.linspace(.1,1,21)
        z=np.linalg.solve(M,b)+np.linspace(-1,1,21)*1e-6
        w=np.linalg.solve(M,dt*c['u'])+np.linspace(1,-1,21)*1e-7
        alpha=(f.Q@z)/(1-f.Q@w)
        x=z+alpha*w
        res=b-(M-dt*np.outer(c['u'],f.Q))@x
        er=(b-M@z)+alpha*(dt*c['u']-M@w)
        np.testing.assert_allclose(res,er,rtol=1e-7,atol=5e-15)
    def test_06_log_clock_scaled_chain(self):
        Y,g,r,d,nb=fixture(7);scales=np.geomspace(1e-3,1,21);H=.02
        c=f.physical_rhs_jac(Y,g,r,d,nb)
        p=f.log_clock_scaled_block(Y,g,r,d,nb,H,scales)
        target=c['jac']*scales[None,:]/scales[:,None]/H
        np.testing.assert_allclose(p['jac'],target,rtol=5e-15,atol=1e-14)
        b=np.arange(21,dtype=float)/20.;dx=.0007
        sol=f.rank_one_solve(np.eye(21)-dx*p['frozen'],p['u'],p['q'],dx,b)
        exact=np.linalg.solve(np.eye(21)-dx*p['jac'],b)
        np.testing.assert_allclose(sol.solution,exact,rtol=2e-12,atol=3e-12)
    def test_07_denominator_guard(self):
        M=np.eye(21);b=np.ones(21);u=np.zeros(21);q=np.zeros(21)
        q[0]=1;u[0]=1
        with self.assertRaisesRegex(np.linalg.LinAlgError,'denominator'):
            f.rank_one_solve(M,u,q,1,b)
    def test_08_invalid_or_missing_physics(self):
        Y,g,r,d,nb=fixture()
        with self.assertRaisesRegex(ValueError,'full21'):
            f.physical_rhs_jac(Y[:17],g,r,d,nb)
        with self.assertRaisesRegex(ValueError,'nonnegative'):
            f.physical_rhs_jac(Y,g,r,d,-2)
        with self.assertRaisesRegex(ValueError,'H'):
            f.log_clock_scaled_block(Y,g,r,d,nb,0,np.ones(21))
        with self.assertRaisesRegex(ValueError,'scales'):
            f.log_clock_scaled_block(Y,g,r,d,nb,2,np.zeros(21))
    def test_09_zero_density_limit(self):
        Y,g,r,d,_=fixture(3)
        c=f.physical_rhs_jac(Y,g,r,d,0)
        np.testing.assert_array_equal(c['jac'],g+d)
        np.testing.assert_array_equal(c['u'],np.zeros(21))
    def test_10_actual_source_structural_charge(self):
        # This is only stoichiometric and local: nonnegative q does not grant physical rates.
        Y,g,r,d,nb=fixture(2)
        c=f.physical_rhs_jac(Y,g,r,d,nb)
        self.assertGreater(c['ne'],0)
        self.assertLess(abs(f.A@c['rhs']),1e-15)
        self.assertTrue(np.all(np.diag(g)<=0))
        self.assertTrue(np.all(np.diag(r)<=0))

if __name__=='__main__':unittest.main()
