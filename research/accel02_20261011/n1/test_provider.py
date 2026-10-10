import unittest
import numpy as np
from provider import HistoryProvider,EV_ERG

class ProviderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.p=HistoryProvider()
    def test_same_source_full_domain_cold_normalized_initial_state(self):
        p=self.p
        self.assertEqual(list(p.initial_gas[:3]),[2e-4,0,0])
        self.assertAlmostEqual(p.geometry(p.end_time_s)['z'],4,places=13)
        for z in [15.9,12.,8.,4.]:
            for table in p.tables.values():
                self.assertGreaterEqual(table.moment(10,50000,z,proper_photons=True),0)
        with self.assertRaises(ValueError): p.geometry(-1)
        with self.assertRaises(ValueError): p.geometry(np.nextafter(p.end_time_s,np.inf))
    def test_uvb_ic_emissivity_source_firewall_and_late_source_coverage(self):
        p=self.p;q=np.array([20.,60000.]);weights=np.array([.2,.2]);mu=np.zeros(2)
        self.assertEqual(p.initial_photons(q,weights)[1],0)
        self.assertEqual(p.source_reference(q,mu,weights,0)[1],0)
        t=p.end_time_s;e,_,r=p.ray(q,mu,t)
        actual=p.source_reference(q,mu,weights,t)
        exact=p.tables['emissivity'].photon_emission_log(e,p.geometry(t)['z'])*weights/r**3
        exact[(e<10)|(e>50000)]=0  # Contract support, including low-energy redshift outflow.
        np.testing.assert_allclose(actual,exact,rtol=1e-14,atol=0)
        self.assertGreater(actual[1],0)
        with self.assertRaises(ValueError): p.tables['uvb'].photon_emission_log(20,8)
        with self.assertRaises(ValueError): p.tables['emissivity'].photon_number_log(20,8)
    def test_axisymmetric_q_jacobian_and_source_support(self):
        p=HistoryProvider(.1);t=p.end_time_s
        # dOmega transformation: 2pi quadrature on mu0; source proper angular average.
        mu,w=np.polynomial.legendre.leggauss(64)
        q=np.full_like(mu,20.);_,_,r=p.ray(q,mu,t)
        self.assertLess(abs(np.dot(w/2,1/r**3)/p.geometry(t)['a_rel']**3-1),2e-13)
        self.assertGreaterEqual(p.q_max_eV,50000*max(p.geometry(t)['scale_rel']))
        self.assertTrue(np.all(p.source_reference(np.array([1.,p.q_max_eV*2]),[0,0],[1,1],t)==0))
        with self.assertRaises(ValueError): p.source_reference([20],[0],[-1],t)

if __name__=='__main__':unittest.main()
