import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[1]/"physical_parent_jvp.py"
spec=importlib.util.spec_from_file_location("rei_original_parent_jvp",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class PhysicalParent(unittest.TestCase):
    def test_original_source_and_gate(self):
        self.assertEqual(m.SOURCE_SHA,"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual((m.N,m.GATE,m.WIDTH),(46080,2e-4,2e-3))
    def test_exact_parent_nuclei_and_box(self):
        p=np.array([[.4,.6,.25,.4,.35],[.8,.2,.1,.5,.4]])
        for src,dst in ((0,1),(2,3)):
            d,amp=m.physical_direction(p,p-.05,p+.05,src,dst)
            for a in (-1.,-.2,0.,.5,1.):
                q=p+a*d
                self.assertTrue(np.all(q>=p-.05))
                self.assertTrue(np.all(q<=p+.05))
                np.testing.assert_allclose(q[:,:2].sum(axis=1),p[:,:2].sum(axis=1))
                np.testing.assert_allclose(q[:,2:].sum(axis=1),p[:,2:].sum(axis=1))
            self.assertTrue(np.all(amp>0))
    def test_invalid_scale(self):
        p=np.ones((2,5))
        for scale in (-1.,0.,1.,2.):
            with self.assertRaises(ValueError):m.physical_direction(p,p-.1,p+.1,0,1,scale)
    def test_photo_source_exact_first_order(self):
        n=m.N
        p=np.tile([.6,.4,.1,.2,.3],(n,1))
        d=np.zeros_like(p);d[:,0]=-1e-5;d[:,1]=1e-5
        C=np.array([[2e-5,1e-5,1e-6],[4e-6,1e-5,3e-6],[6e-6,8e-6,0],[0,0,0]],float)
        J=np.array([1e7,2e7,3e6,0.])
        E=np.array([.3,.5,.6,.5])
        S=p[:,(0,2,3)].sum(axis=0)
        dg=np.array([d[:,i].sum() for i in (0,2,3)])
        den=E+C@S
        group=np.empty((4,n,3));share=np.empty((4,3))
        for g in range(4):
            group[g]=J[g]*p[:,(0,2,3)]*(C[g]/den[g])
            share[g]=C[g]*S/den[g]
        heat=np.ones((3,4))
        direct,global_part,hdir,hglobal,_=m.photon_directional_components(group,share,C,J,den,S,d,heat)
        def r_at(alpha):
            pp=p+alpha*d
            SS=pp[:,(0,2,3)].sum(axis=0)
            return np.sum([J[g]*pp[:,(0,2,3)]*(C[g]/(E[g]+C[g]@SS)) for g in range(4)],axis=0)
        f=(r_at(1.)-r_at(-1.))/2
        self.assertLess(np.max(abs(f-direct-global_part))/max(np.max(abs(f)),1),1e-8)
        self.assertLess(np.max(abs(dg-np.array([d[:,i].sum() for i in (0,2,3)]))),1e-10)
    def test_original_matrix_column_sum(self):
        F=np.zeros((m.N,5,5));p=np.tile([3.,2.,5.,4.,1.],(m.N,1))
        F[:,1,0]=2.;F[:,3,2]=.3
        A=m.A_from_flux(F,p,.1)
        np.testing.assert_allclose(A.sum(axis=1)[:,0],np.ones(m.N))
        self.assertLess(np.max(abs(A.sum(axis=1)-1)),3e-16)
        self.assertGreater(np.min(A[:,np.arange(5),np.arange(5)]),0)
    def test_wrong_shape(self):
        with self.assertRaises(ValueError):
            m.A_from_flux(np.ones((2,5,5)),np.ones((2,5)),1)
    def test_charge(self):
        p=np.array([[1.,2.,3.,4.,5.]])
        self.assertAlmostEqual(float(m.charge(p,np.array([2]))[0]),8.)
    def test_synthetic_baseline_zero_global(self):
        group=np.zeros((4,m.N,3));shares=np.zeros((4,3))
        C=np.ones((4,3));J=np.ones(4);den=np.ones(4);S=np.ones(3)
        d=np.zeros((m.N,5));heat=np.ones((3,4))
        x=m.photon_directional_components(group,shares,C,J,den,S,d,heat)
        self.assertTrue(np.all(x[0]==0))
        self.assertTrue(np.all(x[1]==0))
if __name__=="__main__":unittest.main()
