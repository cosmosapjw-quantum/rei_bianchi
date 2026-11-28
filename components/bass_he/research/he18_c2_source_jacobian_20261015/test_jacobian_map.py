"""One scoped scientific contract test on the actually recovered warm P01 source."""
import os
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from jacobian_map import load_source, reference_at, jacobian_at, describe_at, rate_derivatives

DATA=Path(os.environ.get('HE18_C1_DATA_ROOT','/mnt/data/HE18_C1_20261014'))

class WarmCellJacobian(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.math,cls.src,cls.ep,cls.eg=load_source(DATA)
        cls.t,cls.y,cls.dy=reference_at(cls.src,cls.math,.5)
        cls.J=jacobian_at(cls.src,cls.math,cls.t,cls.y)

    def test_original_source_arity_and_nonzero_error(self):
        self.assertEqual(self.src.y.shape[0],2908)
        self.assertEqual(self.J['A'].shape,(4,4))
        self.assertEqual(self.J['B'].shape,(4,2904))
        self.assertEqual(self.J['C'].shape,(2904,4))
        self.assertEqual(self.ep.shape,(2904,))
        self.assertEqual(self.eg.shape,(4,))
        self.assertGreater(int(np.count_nonzero(self.ep)),0)

    def test_photon_factorization_and_transparency(self):
        actual,_=self.src.rhs(self.t,self.y)
        pred=self.J['forcing']-self.J['kappa']*self.y[4:]
        self.assertLess(float(np.sum(abs(actual[4:]-pred))),1e-25)
        self.assertEqual(int(np.count_nonzero(self.J['kappa']==0)),784)
        self.assertTrue(np.all(self.J['B'][:,self.J['kappa']==0]==0))
        self.assertTrue(np.all(self.J['C'][self.J['kappa']==0,:]==0))

    def test_temperature_total_derivative(self):
        m=self.math;g=self.y[:4];f=m.L(3)/38
        ne=g[0]+f*(g[1]+2*g[2]);Pi=1+f+ne
        T=2*m.EV*g[3]/(3*m.KB*Pi)
        self.assertLess(abs((T-self.J['temperature'])/T),m.L('2e-15'))
        for i,h in enumerate([m.L('1e-6')]*3+[m.L('1e-3')]):
            def calc(g):return 2*m.EV*g[3]/(3*m.KB*(1+f+g[0]+f*(g[1]+2*g[2])))
            x=g.copy();y=g.copy();x[i]+=h;y[i]-=h
            fd=(calc(x)-calc(y))/(2*h)
            self.assertLess(float(abs(fd-self.J['dT'][i])/max(abs(self.J['dT'][i]),m.L('1e-50'))),1e-6)

    def test_gas_analytic_jacobian_against_real_rhs(self):
        m=self.math
        for j,h in enumerate([m.L('1e-5')]*3+[m.L('1e-3')]):
            lo=self.y.copy();hi=self.y.copy();lo[j]-=h;hi[j]+=h
            fd=(self.src.rhs(self.t,hi)[0][:4]-self.src.rhs(self.t,lo)[0][:4])/(2*h)
            rel=np.abs(fd-self.J['A'][:,j])/np.maximum(np.abs(self.J['A'][:,j]),m.L('1e-30'))
            self.assertLess(float(np.max(rel)),2e-6)

    def test_photon_to_gas_analytic_columns(self):
        m=self.math
        for k in (0,1760,2000):
            h=m.L('1e-5');lo=self.y.copy();hi=self.y.copy();lo[k+4]-=h;hi[k+4]+=h
            fd=(self.src.rhs(self.t,hi)[0][:4]-self.src.rhs(self.t,lo)[0][:4])/(2*h)
            self.assertTrue(np.allclose(np.asarray(fd,dtype=float),np.asarray(self.J['B'][:,k],dtype=float),rtol=1e-6,atol=1e-24))

    def test_gas_to_photon_analytic_columns(self):
        m=self.math
        for j,h in enumerate([m.L('1e-5')]*3):
            lo=self.y.copy();hi=self.y.copy();lo[j]-=h;hi[j]+=h
            fd=(self.src.rhs(self.t,hi)[0][4:]-self.src.rhs(self.t,lo)[0][4:])/(2*h)
            rel=np.abs(fd-self.J['C'][:,j])/np.maximum(np.abs(self.J['C'][:,j]),m.L('1e-45'))
            self.assertLess(float(np.max(rel)),2e-6)
        self.assertTrue(np.all(self.J['C'][:,3]==0))

    def test_kinetic_recombination_second_log_temperature_derivative(self):
        m=self.math;T=self.J['temperature'];h=m.L('1e-3')
        vals,ds=rate_derivatives(self.src,T,m)
        for index in (0,1,2,3):
            fd=(self.src.rates(T+h)[index]-self.src.rates(T-h)[index])/(2*h)
            rel=np.max(np.abs(fd-ds[index])/np.maximum(abs(ds[index]),m.L('1e-80')))
            self.assertLess(float(rel),2e-6)

    def test_nonzero_raw_photon_carry_and_nonpromotion(self):
        J,s=describe_at(DATA,.5)
        self.assertTrue(s['incoming_nonzero'])
        self.assertGreater(float(s['norm_A_inf_at_point']),0)
        self.assertGreater(float(s['norm_BC_inf_at_point']),0)
        self.assertTrue(any(float(v)>0 for v in s['incoming_photon_to_gas_scaled_force_s_inv']))
        self.assertIsNone(s['whole_cell_jacobian_enclosure'])
        self.assertIsNone(s['true_second_cell_IVP_error'])
        self.assertIsNone(s['provider_roundoff_bound'])
        self.assertLess(s['rhs_photon_normalized_identity_error'],1e-10)

if __name__=='__main__':unittest.main()
