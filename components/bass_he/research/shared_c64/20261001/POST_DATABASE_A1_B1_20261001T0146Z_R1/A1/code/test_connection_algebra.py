"""Finite matrix algebra fixtures; these are not collision or eigenproblem runs."""
import unittest
import numpy as np
from scipy.linalg import expm
from connection_algebra import metric_generator, orthonormal_generator

TOL = 2e-12
HBAR_FIXTURE = 0.7  # Dimensionless algebra fixture, never a physical-unit substitution.

def dagger(a):
    return a.conj().T

def fixture(t):
    a = np.array([[np.exp(t), t+0.2j*t], [0, np.exp(-t)]], complex)
    adot = np.array([[np.exp(t), 1+0.2j], [0, -np.exp(-t)]], complex)
    h0 = np.array([[2, 1-1j], [1+1j, 3]], complex)
    s, d, h = dagger(a)@a, dagger(a)@adot, dagger(a)@h0@a
    sdot = dagger(adot)@a+dagger(a)@adot
    w = np.linalg.inv(a)
    wdot = -w@adot@w
    return a, adot, h0, s, d, h, sdot, w, wdot

class ConnectionAlgebraTests(unittest.TestCase):
    def test_static_orthonormal_limit(self):
        h=np.array([[2, 1j],[-1j,4]],complex); eye=np.eye(2); zero=np.zeros((2,2))
        k=orthonormal_generator(eye,h,zero,zero,eye,zero,HBAR_FIXTURE)
        np.testing.assert_allclose(k,h,atol=TOL,rtol=0)

    def test_metric_generator_is_not_euclidean_hermitian(self):
        _,_,_,s,d,h,sdot,_,_=fixture(0.37)
        g=metric_generator(s,h,d,sdot,HBAR_FIXTURE)
        self.assertGreater(np.linalg.norm(g-dagger(g)),0.1)
        residual=1j/HBAR_FIXTURE*(dagger(g)@s-s@g)+sdot
        np.testing.assert_allclose(residual,0,atol=TOL,rtol=0)

    def test_exact_transformed_basis_reference(self):
        for t in [0.0,0.13,0.37,0.8]:
            a,adot,h0,s,d,h,sdot,w,wdot=fixture(t)
            k=orthonormal_generator(s,h,d,sdot,w,wdot,HBAR_FIXTURE)
            y=a@w; ydot=adot@w+a@wdot
            reference=dagger(y)@h0@y-1j*HBAR_FIXTURE*dagger(y)@ydot
            np.testing.assert_allclose(k,reference,atol=TOL,rtol=0)
            np.testing.assert_allclose(k,h0,atol=TOL,rtol=0)

    def test_nonabelian_and_rephasing_covariance(self):
        t=0.37; rate=0.6; alpha=0.4; beta=-0.9
        a,adot,h0,s,d,h,sdot,w,wdot=fixture(t)
        r=np.array([[np.cos(rate*t),-np.sin(rate*t)],[np.sin(rate*t),np.cos(rate*t)]])
        rdot=rate*np.array([[-np.sin(rate*t),-np.cos(rate*t)],[np.cos(rate*t),-np.sin(rate*t)]])
        phase=np.diag(np.exp(1j*np.array([alpha,beta])*t)); pdot=np.diag(1j*np.array([alpha,beta]))@phase
        u=r@phase; udot=rdot@phase+r@pdot
        k=orthonormal_generator(s,h,d,sdot,w@u,wdot@u+w@udot,HBAR_FIXTURE)
        target=dagger(u)@h0@u-1j*HBAR_FIXTURE*dagger(u)@udot
        np.testing.assert_allclose(k,target,atol=TOL,rtol=0)
        self.assertGreater(np.linalg.norm(target-dagger(u)@h0@u),0.1)

    def test_metric_norm_exact_static_reference_evolution(self):
        c0=np.array([1,1j])/np.sqrt(2)
        for t in [0,0.13,0.37,0.8]:
            a,adot,h0,s,d,h,sdot,w,wdot=fixture(t)
            c=w@expm(-1j*h0*t/HBAR_FIXTURE)@c0
            self.assertAlmostEqual(float(np.real(np.vdot(c,s@c))),1.0,places=12)

    def test_origin_lever_and_intrinsic_translation_cancel(self):
        s=np.array([0.2,-0.4,0.7]); p=np.array([1.2,0.6,-0.5]); om=np.array([0.8,-0.1,0.3])
        v=np.array([-0.3,1.0,0.4]); ds=np.array([0.1,0.2,-0.7]); ell=np.array([0.6,0.5,0.9])
        old=-om@ell-v@p
        new=-om@(ell-np.cross(s,p))-(v+np.cross(om,s)+ds)@p+ds@p
        self.assertAlmostEqual(new,old,places=13)
        wrong=-om@(ell-np.cross(s,p))-(v+np.cross(om,s)+ds)@p
        self.assertGreater(abs(wrong-old),0.1)

    def test_common_inertial_boost_scalar_cancellation(self):
        m=1.3;v=np.array([0.3,-0.5,0.1]);p=np.array([0.6,0.2,-0.4])
        u=v; hb_gamma_dot=0.5*m*(v@v)
        difference=(u-v)@p+0.5*m*(u@u)-m*(v@u)+hb_gamma_dot
        self.assertAlmostEqual(difference,0,places=14)

    def test_r10r_bright_term_sign_and_hermiticity_fixture(self):
        theta_dot=-0.3; hbar=0.7; positive_ratio=1.4
        ell=np.array([[0,-1j*hbar*positive_ratio],[1j*hbar*positive_ratio,0]])
        k=-theta_dot*ell
        np.testing.assert_allclose(k[0,1],1j*hbar*theta_dot*positive_ratio,atol=TOL,rtol=0)
        np.testing.assert_allclose(k,dagger(k),atol=0,rtol=0)

    def test_missing_metric_derivative_fails(self):
        _,_,_,s,d,h,_,w,wdot=fixture(0.37)
        with self.assertRaisesRegex(ValueError,'metric_derivative'):
            orthonormal_generator(s,h,d,np.zeros_like(s),w,wdot,HBAR_FIXTURE)

    def test_missing_orthonormalizer_derivative_fails(self):
        _,_,_,s,d,h,sdot,w,_=fixture(0.37)
        with self.assertRaisesRegex(ValueError,'orthonormal_metric_derivative'):
            orthonormal_generator(s,h,d,sdot,w,np.zeros_like(w),HBAR_FIXTURE)

    def test_singular_or_illconditioned_metric_fails(self):
        zero=np.zeros((2,2));eye=np.eye(2)
        for s in [np.diag([1,0]),np.diag([1,1e-12])]:
            with self.assertRaisesRegex(ValueError,'metric'):
                metric_generator(s,eye,zero,zero,HBAR_FIXTURE)

    def test_nonfinite_and_nonhermitian_h_fail(self):
        eye=np.eye(2);zero=np.zeros((2,2));bad=np.array([[1,np.nan],[0,1]])
        with self.assertRaisesRegex(ValueError,'finite'):
            metric_generator(eye,bad,zero,zero,HBAR_FIXTURE)
        with self.assertRaisesRegex(ValueError,'Hamiltonian'):
            metric_generator(eye,np.array([[1,1],[0,1]]),zero,zero,HBAR_FIXTURE)

if __name__=='__main__':
    unittest.main(verbosity=2)
