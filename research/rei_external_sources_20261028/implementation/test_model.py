"""One targeted independent invariant/limiting-solution verification pass."""
import json
import unittest
import numpy as np
import model as m


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=m.config()
        cls.eta,cls.z,cls.y,cls.hidden,cls.density=m.load_baseline()
        print(json.dumps({'source_read':{'epochs':len(cls.eta),'nHref_shape':list(cls.density.shape),
              'nHref_cm3_endpoints':[float(cls.density[0]),float(cls.density[-1])],
              'eta_serialization_alignment_pass':True,'eta_atol':5e-15,'csv_sha256':m.digest(m.CSV_PATH),'npz_sha256':m.digest(m.NPZ_PATH)}}))

    def test_source_mapping_and_hidden_closure(self):
        self.assertEqual(m.LABELS[-1],'Li7_3')
        self.assertEqual(len(m.LABELS),17)
        self.assertEqual(self.hidden.shape,(201,4))
        self.assertTrue(np.all(self.y[:,[0,5,6]]==0))
        self.assertTrue(np.isfinite(self.y).all())
        self.assertFalse(any('Li6' in label for label in m.LABELS))

    def test_exact_integer_event_stoichiometry_and_energy(self):
        # Nonzero all-state input exercises every admitted target and beta column.
        out=m.evaluate_operator(np.ones(17),self.density[0],1,self.c)
        for event in out['events']:
            with self.subTest(event=event['name']):
                self.assertEqual(int(m.A@event['nu'])+event['external_A'],0)
                self.assertEqual(int(m.Q@event['nu'])-event['electron'],0)
                e=event['energy']
                incoming=sum(e.get(k,0.) for k in ('photon_input','cr_input','injected_kinetic'))
                allocated=sum(v for k,v in e.items() if k not in ('photon_input','cr_input','injected_kinetic'))
                self.assertLessEqual(abs(incoming-allocated),1e-12*max(1,abs(incoming))+1e-12)
        self.assertEqual(next(e for e in out['events'] if e['name']=='beta_n')['nu'][2],1)
        self.assertEqual(next(e for e in out['events'] if e['name']=='beta_T_0')['nu'][8],1)
        self.assertEqual(next(e for e in out['events'] if e['name']=='beta_T_1')['nu'][9],1)

    def test_strict_thresholds_all_charges(self):
        for _,thresholds in m.FAMILIES.values():
            for I in thresholds:
                self.assertEqual(m.atomic_sigma(I,I,self.c),0)
                self.assertEqual(m.atomic_sigma(I/2,I,self.c),0)
                self.assertGreater(m.atomic_sigma(I*1.01,I,self.c),0)
        for _,fam,_,_,Q in m.NUCLEAR:
            thresholds=m.FAMILIES[fam][1]
            for charge in range(len(thresholds)+1):
                req=-Q+sum(thresholds[charge:])
                self.assertEqual(m.nuclear_sigma(req,req,self.c),0)
                self.assertEqual(m.nuclear_sigma(req/2,req,self.c),0)
                self.assertGreater(m.nuclear_sigma(req*1.01,req,self.c),0)
        self.assertEqual(m.cr_sigma(3e7,self.c),0)
        self.assertEqual(m.cr_sigma(1e7,self.c),0)
        self.assertGreater(m.cr_sigma(1e8,self.c),0)

    def test_branching_and_limiting_regimes(self):
        for kind in ('n','T'):
            ks=self.c['ks_'+kind+'_s']; ke=self.c['ke_'+kind+'_s']; decay=self.c['lambda_'+kind+'_s']
            b,L=m.branching(ks,ke,decay)
            self.assertLess(abs(sum(b)-1),1e-14)
            np.testing.assert_allclose(m.branching(0,ke,decay)[0],[0,ke/(ke+decay),decay/(ke+decay)],rtol=1e-14,atol=0)
            np.testing.assert_allclose(m.branching(ks,0,decay)[0],[ks/(ks+decay),0,decay/(ks+decay)],rtol=1e-14,atol=0)

    def test_qss_independent_linear_solve_and_residuals(self):
        for i in (0,100,200):
            for alpha in (0,1,10):
                r=m.reservoirs(self.y[i],alpha,self.c)
                q=m.qss(self.y[i],self.density[i],alpha,self.c,r)
                matrix=np.array([[q['Ln'],0,0],[0,q['LT']+q['Gamma'],-q['rec']],[0,-q['Gamma'],q['LT']+q['rec']]])
                independent=np.linalg.solve(matrix,q['sources'])
                np.testing.assert_allclose(q['stocks'],independent,rtol=1e-12,atol=0)
                scale=max(np.max(np.abs(q['sources'])),np.max(np.abs(matrix)@q['stocks']))
                residual=matrix@q['stocks']-q['sources']
                self.assertLessEqual(float(np.max(np.abs(residual))),1e-12*scale if scale else 0)
                self.assertTrue(np.all(q['stocks']>=0))
                self.assertLessEqual(abs(sum(q['stocks'][1:])-q['Ttotal_expected']),1e-12*q['Ttotal_expected'])
                if alpha==0: self.assertTrue(np.all(q['stocks']==0))
                state=self.y[i].copy();state[[0,5,6]]=q['stocks']
                out=m.evaluate_operator(state,self.density[i],alpha,self.c,res=r)
                self.assertLessEqual(np.max(np.abs(out['dy'][[0,5,6]])),1e-12*scale if scale else 0)

    def test_external_off_and_boundary_positivity(self):
        out=m.evaluate_operator(np.ones(17),self.density[100],0,self.c,escape=False,intrinsic=False)
        self.assertTrue(np.all(out['dy']==0))
        self.assertTrue(all(v==0 for v in out['power'].values()))
        # For each zero component all its own target-proportional sinks vanish.
        for i in range(17):
            y=np.ones(17); y[i]=0
            out=m.evaluate_operator(y,self.density[100],1,self.c)
            self.assertGreaterEqual(out['dy'][i],0)
        # Frozen QSS loss matrix has nonpositive off-diagonals: generator rates >=0.
        q=m.qss(self.y[100],self.density[100],1,self.c)
        self.assertGreaterEqual(q['Gamma'],0); self.assertGreaterEqual(q['rec'],0)

    def test_independent_rate_spots_and_amplitude(self):
        for i in (0,100,200):
            out=m.evaluate_operator(self.y[i],self.density[i],1,self.c)
            expected=1e4*6.3e-18*(13.6/20)**3*self.y[i,1]
            self.assertAlmostEqual(out['rates']['photo_atom_H1_0_b0']/expected,1,places=14)
            expected_cr=.01*1e-26*(1-3e7/1e8)**2*self.y[i,10]
            self.assertAlmostEqual(out['rates']['cr_n_0']/expected_cr,1,places=14)
            q1=m.qss(self.y[i],self.density[i],1,self.c)
            q10=m.qss(self.y[i],self.density[i],10,self.c)
            self.assertAlmostEqual(q10['Gamma']/q1['Gamma'],10,places=12)
            self.assertAlmostEqual(sum(q10['stocks'][1:])/sum(q1['stocks'][1:]),10,places=12)
            self.assertAlmostEqual(q10['stocks'][0]/q1['stocks'][0],10,places=12)
        for i in range(201):
            out=m.evaluate_operator(self.y[i],self.density[i],1,self.c)
            self.assertTrue(np.isfinite(out['dy']).all())
            self.assertTrue(np.isfinite(list(out['rates'].values())).all())
            self.assertTrue(all(v>=0 for v in out['rates'].values()))


if __name__=='__main__': unittest.main()
