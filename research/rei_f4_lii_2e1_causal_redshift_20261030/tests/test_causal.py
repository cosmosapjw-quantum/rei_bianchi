"""Bounded same-author hostile research tests (not independent-author R6/C9)."""
from __future__ import annotations
import csv,hashlib,json,math,pathlib,sys,unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import causal_firstflight as m

class Frozen:
    def __init__(self,r):
        self.Y_TAB=r.Y_TAB;self.A_TAB=r.A_TAB;self.PAIR_NORM=r.PAIR_NORM
        self.E_SINGLET_EV=r.E_SINGLET_EV;self.nodes_weights=r.nodes_weights
        self.CAT_GROUPS={'H_I':[0],'He_I':[],'He_II':[],'Li_I':[]}
        self._z_source=np.array([20.,20.*math.exp(-.1)])
class ToyNet:
    transition_energy_eV=np.array([0.])
    def __init__(self,lam=0):self.lam=lam
    def photo_cross_sections(self,E):return np.full((1,len(E)),self.lam/m.C),None

class CheckCausal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads((ROOT/'results/RESULT.json').read_text())
        def read(x):
            with (ROOT/'results'/x).open(newline='') as f:return list(csv.DictReader(f))
        cls.epochs=read('EMISSIONS_193.csv');cls.arrival=read('ABSORPTION_ARRIVALS_192.csv')
        cls.flights=read('FIRST_FLIGHT_KERNEL.csv');cls.joints=read('JOINT_OUTCOMES_4825.csv')

    def test_original_archive_sha(self):
        self.assertEqual(hashlib.sha256(m.PARENT.read_bytes()).hexdigest(),m.PARENT_SHA)
        with m.owner() as ref:
            self.assertEqual(ref.OWNER,m.ORIGINAL_OWNER)

    def test_counts(self):
        self.assertEqual([len(t) for t in (self.epochs,self.arrival,self.flights,self.joints)], [193,192,18528,4825])
        self.assertEqual(self.r['counts']['original_K_event_rows'],8492)

    def test_no_unauthorized_ivs(self):
        self.assertEqual(self.r['counts']['new_IVPs'],0)
        self.assertEqual(self.r['gates']['working_DAG'],'33/88')
        self.assertEqual(self.r['gates']['central_DAG'],'28/88')
        self.assertEqual(self.r['gates']['F4_DAG'],'4/7')
        self.assertEqual(self.r['gates']['canonical_physical_delta'],0)
        self.assertEqual(self.r['gates']['actual_singlet_branching'],'UNBOUND')
        self.assertTrue(self.r['gates']['NO_MORE_IVPS'])
        s=(ROOT/'code/causal_firstflight.py').read_text()
        self.assertNotIn('solve_ivp(',s)
        self.assertNotIn('odeint(',s)

    def test_emission_endpoint_no_future_path(self):
        self.assertAlmostEqual(float(self.epochs[-1]['mean_absorptions_per_pair']),0,delta=1e-14)
        self.assertAlmostEqual(float(self.epochs[-1]['survived_photons_at_z2']),2,delta=1e-12)
        self.assertAlmostEqual(float(self.epochs[-1]['cosmological_redshift_work_eV']),0,delta=1e-12)

    def test_pair_and_energy_conservation_all_saved_epochs(self):
        for r in self.epochs:
            p=sum(float(r[q]) for q in ('P0','P1','P2'))
            self.assertAlmostEqual(p,1,delta=4e-11)
            photons=float(r['survived_photons_at_z2'])+sum(float(r['absorbed_'+c]) for c in m.CAT[1:])
            self.assertAlmostEqual(photons,2,delta=3e-11)
            en=sum(float(r[q]) for q in ('absorbed_binding_eV','absorbed_primary_electron_eV','cosmological_redshift_work_eV','survivor_eV_at_z2'))
            self.assertAlmostEqual(en,60.922559447552,delta=2e-10)
            self.assertGreaterEqual(float(r['cosmological_redshift_work_eV']),0)

    def test_joint_matrix_and_marginal_number(self):
        for k in [0,20,64,96,128,160,191,192]:
            a=np.zeros((5,5))
            for row in self.joints[25*k:25*(k+1)]:
                i=m.CAT.index(row['low_outcome']);j=m.CAT.index(row['high_outcome'])
                a[i,j]=float(row['probability'])
            self.assertAlmostEqual(a.sum(),1,delta=1e-11)
            self.assertAlmostEqual(float(self.epochs[k]['P2']),a[1:,1:].sum(),delta=1e-12)
            self.assertLess(abs(a[m.CAT.index('He_II'),:]).max(),1e-14)

    def test_arrival_kernel_sums_all(self):
        r=self.r['integrated_conditional_per_baryon']
        first=sum(float(a['incoming_integrated_'+g+'_per_baryon']) for a in self.arrival for g in ['H_I','He_I','He_II','Li_I'])
        self.assertAlmostEqual(first/r['mean_absorptions_per_pair'],1,delta=1e-11)
        self.assertAlmostEqual(sum(float(a['primary_electron_eV_per_baryon']) for a in self.arrival)/r['absorbed_primary_electron_eV'],1,delta=1e-11)

    def test_global_passive_energy_ledger(self):
        e=self.r['energy_conservation']
        self.assertLess(abs(e['residual_eV_per_baryon'])/e['input_eV_per_baryon'],4e-14)
        self.assertGreater(self.r['integrated_conditional_per_baryon']['cosmological_redshift_work_eV'],0)

    def test_shared_source_cone_bounds(self):
        v=self.r['integrated_conditional_per_baryon']['mean_absorptions_per_pair']
        a=self.r['global_shape_cone_bounds']
        for fam in ['positive','monotone']:
            lo,hi=a[fam]['global_ionization_count_per_baryon']
            self.assertLessEqual(lo,v);self.assertLessEqual(v,hi)
        self.assertGreaterEqual(a['monotone']['global_ionization_count_per_baryon'][0],a['positive']['global_ionization_count_per_baryon'][0])
        self.assertLessEqual(a['monotone']['global_ionization_count_per_baryon'][1],a['positive']['global_ionization_count_per_baryon'][1])

    def test_fixed_hazard_exact_toy_and_redshift(self):
        with m.owner() as r:
            fake=Frozen(r)
            x=np.array([0,.1]);H=np.ones(2);nb=np.ones(2);Y=np.ones((2,1))
            val,rows,J,*_=m.lightcone(fake,ToyNet(lam=2.),x,H,nb,Y,0,order=4,substeps=1)
            expected=2*(1-math.exp(-.2))
            self.assertAlmostEqual(val['mean_absorptions_per_pair'],expected,delta=2e-12)
            self.assertAlmostEqual(J[0,0],math.exp(-.4),delta=2e-12)
            self.assertAlmostEqual(val['P_two_independent_marginals'],val['P2'],delta=1e-12)
            self.assertAlmostEqual(val['pair_absorption_covariance'],0,delta=1e-12)
            self.assertGreater(val['cosmological_redshift_work_eV'],0)

    def test_zero_opacity_expansion_only(self):
        with m.owner() as r:
            fake=Frozen(r);x=np.array([0,.5]);H=np.ones(2);nb=np.ones(2);Y=np.ones((2,1))
            val,rows,J,*_=m.lightcone(fake,ToyNet(lam=0.),x,H,nb,Y,0,order=4,substeps=2)
            self.assertAlmostEqual(val['mean_absorptions_per_pair'],0,delta=1e-12)
            self.assertAlmostEqual(val['survived_photons_at_z2'],2,delta=1e-12)
            E=r.E_SINGLET_EV
            self.assertAlmostEqual(val['survivor_eV_at_z2'],E*math.exp(-.5),delta=1e-12)
            self.assertAlmostEqual(val['cosmological_redshift_work_eV'],E*(1-math.exp(-.5)),delta=1e-12)

    def test_no_false_thermal_and_directional_promotion(self):
        g=self.r['gates']
        self.assertEqual(g['secondary_electron_thermal_deposition'],'UNBOUND')
        self.assertEqual(g['real_Bianchi_anisotropic_directional_redshift'],'NOT_RUN')
        self.assertEqual(g['PRODUCTION'],'HOLD')
        self.assertFalse(g['AUTO_NEXT_NODE'])

if __name__=='__main__':unittest.main()
