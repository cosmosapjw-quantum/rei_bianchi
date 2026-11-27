from __future__ import annotations
import csv,json,math,unittest
from pathlib import Path
import numpy as np
from src import fcs

ROOT=Path(__file__).resolve().parents[1]

def csv_rows(name):
    with (ROOT/'results'/name).open(newline='',encoding='utf-8') as x:return list(csv.DictReader(x))

class FCSPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=fcs.import_bridge()
        _,cls.branches,_,_,_=cls.b.load_inputs()
        cls.r=cls.b.load_r33()
        cls.parent,cls.old,cls.grid,cls.centers=cls.r.get_parent()

    def model(self,T=55, mode='raw_SQM', ratio=1., j=0, radT=0, vp='DB_UPWARD_V1'):
        initial,w=fcs.initial_mix(self.b,self.branches[(T,vp,j)])
        n=self.parent.reference_density(self.grid,T,mode)*ratio
        G,_,_,Q,rad=self.r.assemble(self.parent,self.grid,T,mode,n,radT)
        return G,Q,rad,initial,w

    def test_parent_integrity(self):
        self.assertEqual(fcs.hash_file(fcs.PARENT_ZIP),fcs.PARENT_SHA)
        self.b.lock_inputs()

    def test_two_state_exact_bernoulli(self):
        # In the 2-level collision-free model, the net number of signed photons
        # equals 1 iff chemistry absorbs in the lower state, otherwise 0.
        a,b,q0,q1=2.3,.8,1.4,.6
        det=a*q0+b*q1+q0*q1
        p=a*q0/det
        G=np.array([[-b-q0,a],[b,-a-q1]],float)
        Q=np.diag([q0,q1])
        # embed in 5 states with positive chemical exit, leaving 2 initial levels reachable
        F=np.diag([-1.,-1.,-1.,-1.,-1.])
        F[:2,:2]=G
        Chem=np.diag([q0,q1,1.,1.,1.])
        e=np.array([0.,1.,0.,0.,0.])
        energy=fcs.E0
        # use 1->0 radiative emission and 0->1 absorption (cm^-1=100)
        rad=[(1,100.,a,0.,b,0.)]
        m=fcs.moments(F,Chem,rad,e)
        self.assertAlmostEqual(m['mean_signed_photon_energy_J']/energy,p,places=12)
        self.assertAlmostEqual(m['variance_signed_photon_energy_J2']/energy**2,p*(1-p),places=12)
        for s in (-.02,.02):
            phi=fcs.tilted_mgf(F,Chem,rad,e,s)
            self.assertAlmostEqual(phi,1-p+p*math.exp(s),places=11)

    def test_positive_reaction_mass_and_photon_variances(self):
        for T, mode, ratio, j, radT, vp in [
            (55,'raw_SQM',1,0,0,'DB_UPWARD_V1'),
            (105,'Eq6-7_spin_effective',.1,2,2.7255*39,'DB_UPWARD_V1'),
            (255,'raw_SQM',10,4,2.7255*301,'DOWN_ONLY_COUNTERFACTUAL'),
            (1005,'raw_SQM',1,3,2.7255*101,'DB_UPWARD_V1')]:
            G,Q,rad,initial,w=self.model(T,mode,ratio,j,radT,vp)
            m=fcs.moments(G,Q,rad,initial)
            self.assertAlmostEqual(m['probability_chemical_absorption'],1,places=10)
            self.assertGreaterEqual(m['variance_signed_photon_energy_J2'],0)
            self.assertGreaterEqual(m['variance_emitted_photons'],0)
            self.assertGreaterEqual(m['variance_absorbed_photons'],0)
            self.assertAlmostEqual(m['mean_absorbed_photons'] if radT==0 else 0,0,places=11)

    def test_tilted_direct_resolvent_independent_derivative(self):
        # The tilted-resolvent uses exponentials while moments use exact matrix
        # derivatives. Small h must respect exponential moment convergence radius.
        for T, mode, ratio, j, radT, vp in [
            (55,'raw_SQM',1,0,0,'DB_UPWARD_V1'),
            (105,'Eq6-7_spin_effective',.1,2,2.7255*39,'DB_UPWARD_V1'),
            (255,'raw_SQM',10,4,2.7255*301,'DOWN_ONLY_COUNTERFACTUAL')]:
            G,Q,rad,initial,w=self.model(T,mode,ratio,j,radT,vp)
            m=fcs.moments(G,Q,rad,initial)
            h=1e-4
            a=fcs.tilted_mgf(G,Q,rad,initial,h)
            b=fcs.tilted_mgf(G,Q,rad,initial,-h)
            c=fcs.tilted_mgf(G,Q,rad,initial,0)
            d1=(a-b)/(2*h)
            d2=(a+b-2*c)/h**2
            u1=m['mean_signed_photon_energy_J']/fcs.E0
            u2=m['second_signed_photon_energy_J2']/fcs.E0**2
            self.assertLess(abs(d1-u1)/max(1.,abs(u1)),1e-5)
            self.assertLess(abs(d2-u2)/max(1.,abs(u2)),1e-4)

    def test_source_case_crosscheck(self):
        cases=csv_rows('FCS_CONDITIONAL_3528.csv')
        self.assertEqual(len(cases),3528)
        for c in (cases[0],cases[73],cases[502],cases[1543],cases[-1]):
            T=int(c['Tgas_K']);vp=c['v1_quench_policy'];j=int(c['initial_v1_J'])
            G,Q,rad,initial,w=self.model(T,c['v0_spin_policy'],float(c['n_over_ncrit_J2']),j,float(c['T_rad_K']),vp)
            m=fcs.moments(G,Q,rad,initial)
            self.assertAlmostEqual(float(c['variance_signed_photon_energy_J2'])/m['variance_signed_photon_energy_J2'],1,places=10)

    def test_source_restricted_bounds(self):
        bounds=csv_rows('SOURCE_RESTRICTED_H2_BRANCH_BOUNDS_35280.csv')
        self.assertEqual(len(bounds),35280)
        for r in bounds:
            lo=float(r['known_selected_lower_bound']); hi=float(r['conditional_upper_bound'])
            self.assertTrue(-1e-13 <= lo <= hi <=1+1e-13)
            self.assertTrue(hi-lo>=0)
            self.assertEqual(r['full_physical_network_bound'],'False')

    def test_zero_mean_nonzero_variance(self):
        roots=csv_rows('FCS_ZERO_MEAN_ROOTS_324.csv')
        self.assertEqual(len(roots),324)
        for r in roots:
            self.assertLess(abs(float(r['mean_signed_photon_energy_J'])),2e-30)
            self.assertGreater(float(r['variance_signed_photon_energy_J2']),0)

    def test_no_rad_case_only_spontaneous(self):
        off=[r for r in csv_rows('FCS_CONDITIONAL_3528.csv') if r['CMB_label']=='OFF']
        self.assertEqual(len(off),504)
        for r in off:self.assertEqual(float(r['mean_absorbed_photons']),0)

    def test_classification_and_provenance(self):
        r=json.loads((ROOT/'results/SUMMARY.json').read_text())
        self.assertEqual(r['EMAA_source'],'NOT_ACQUIRED')
        self.assertEqual(r['canonical_DAG'],'34/49_UNCHANGED')
        self.assertFalse(r['L4'])
        self.assertEqual(r['R6_distinct_author'],'NOT_RUN')
        self.assertEqual(r['C9_distinct_author'],'NOT_RUN')

if __name__=='__main__':unittest.main()
