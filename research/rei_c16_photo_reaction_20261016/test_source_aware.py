"""Independent source-aware Bianchi-I H/He photo transaction verification."""
import math
import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import source_aware as s
import numpy as np
from scipy.integrate import solve_ivp

BASE_GAS=s.Gas(.92,.08,.077,.003,0.)


def state_ref():
    return s.State((s.Node(18.,0.75,.28),s.Node(38.,-0.4,.17),
                    s.Node(72.,.3,.22),s.Node(115.,-.6,.13)),BASE_GAS)


def ode_reference(initial:s.State, dt:float,nH:float):
    nodes=initial.photons
    k=np.array([[s.C_CM_S*nH*s.MB_CM2*s.verner_mb(i,p.q_ev) for i in range(3)]
                for p in nodes])
    y0=np.array([p.n_per_h for p in nodes]+list(initial.gas.__dict__.values()),dtype=float)
    m=len(nodes)
    def rhs(t,y):
        N=y[:m]; HI,HII,HeI,HeII,HeIII=y[m:]
        stocks=np.array([HI,HeI,HeII])
        r=N[:,None]*k*stocks[None,:]
        dn=-r.sum(axis=1)
        events=r.sum(axis=0)
        return np.concatenate([dn,[-events[0],events[0],-events[1],events[1]-events[2],events[2]]])
    ans=solve_ivp(rhs,(0.,dt),y0,rtol=2.e-12,atol=2.e-14,method="DOP853")
    assert ans.success
    return ans.y[:,-1]


class VernerProvenance(unittest.TestCase):
    def test_exact_three_donor_thresholds(self):
        self.assertEqual([r[0] for r in s.VERNER_ROWS],[13.6,24.59,54.42])
        self.assertEqual(s.SPECIES,("HI","HeI","HeII"))
    def test_crosssections_nonnegative(self):
        for E in (0.,13.5,13.6,24.,24.59,40.,54.4,54.42,60.,100.,1000.):
            for i in range(3):
                self.assertGreaterEqual(s.verner_mb(i,E),0.)
                if E<s.VERNER_ROWS[i][0]:
                    self.assertEqual(s.verner_mb(i,E),0.)
    def test_positive_threshold_sigma(self):
        self.assertTrue(all(s.verner_mb(i,r[0])>0 for i,r in enumerate(s.VERNER_ROWS)))
    def test_original_range_rejection(self):
        with self.assertRaises(ValueError):s.verner_mb(2,50001.)
        with self.assertRaises(ValueError):s.verner_mb(1,-1.)


class ExactPairPhysics(unittest.TestCase):
    def test_exact_single_channel_semi_group(self):
        for n,stock,k,dt in [(.1,1.,.3,5.),(1.,.1,.3,5.),(.1,.1,.3,5.),(.3,.3,.01,20.),(1e-10,1.,1.,10.)]:
            N,S,ev=s.exact_pair(n,stock,k,dt)
            N1,S1,e1=s.exact_pair(n,stock,k,dt/2)
            N2,S2,e2=s.exact_pair(N1,S1,k,dt/2)
            self.assertAlmostEqual(N,N2,delta=3e-14)
            self.assertAlmostEqual(S,S2,delta=3e-14)
            self.assertAlmostEqual(ev,e1+e2,delta=3e-14)
            self.assertGreaterEqual(N,0)
            self.assertGreaterEqual(S,0)
            self.assertAlmostEqual((n-N),(stock-S),delta=2e-14)
    def test_pair_independent_ivp(self):
        for n,stock,k,dt in [(.51,.67,.08,9.),(.49,.49,.12,7.),(2.2,.08,.5,3.)]:
            solution=s.exact_pair(n,stock,k,dt)
            res=solve_ivp(lambda t,y:(-k*y[0]*y[1],-k*y[0]*y[1]),
                          (0,dt),(n,stock),rtol=1e-12,atol=1e-14,method="DOP853")
            self.assertTrue(res.success)
            self.assertAlmostEqual(solution[0],res.y[0,-1],delta=7e-12)
            self.assertAlmostEqual(solution[1],res.y[1,-1],delta=7e-12)
    def test_large_and_small_optical_depth(self):
        for x in (1e-15,1e-8,1.,50.,1e5):
            n,S,dn=s.exact_pair(.35,.65,x,1.)
            self.assertTrue(0<=dn<=.35)
            self.assertTrue(n>=0 and S>=0)
    def test_invalid_pair(self):
        for z in ((-.1,1.,1.,1.),(1.,-1.,1.,1.),(1.,1.,-1.,1.),(1.,1.,1.,-1.)):
            with self.assertRaises(ValueError):s.exact_pair(*z)


class BianchiTransactions(unittest.TestCase):
    def test_source_free_geometry_killing_work(self):
        a=state_ref()
        b,e=s.evolve(a,0.,1e-3,a_end=math.exp(.14),b_end=.08)
        self.assertEqual(a.nphot,b.nphot)
        self.assertEqual(sum(e.photo_events),0)
        self.assertAlmostEqual(a.u_phot_ev,b.u_phot_ev+e.geometric_work_ev,delta=4e-14)
        self.assertAlmostEqual(e.energy_residual_ev,0.,delta=4e-14)
    def test_geometry_reverse_exact(self):
        a=state_ref()
        b,_=s.evolve(a,0.,1e-3,a_end=1.12,b_end=.06)
        c,_=s.evolve(b,0.,1e-3,a_end=1.,b_end=0.)
        self.assertAlmostEqual(a.u_phot_ev,c.u_phot_ev,delta=3e-14)
    def test_no_photons_no_gas(self):
        a=s.State((),BASE_GAS)
        b,e=s.evolve(a,1.e11,1e-3)
        self.assertEqual(a,b)
        self.assertEqual(e.energy_residual_ev,0.)
    def test_he_i_is_he_ii_donor(self):
        gas=s.Gas(1.,0.,.08,0.,0.)
        a=s.State((s.Node(85.,0.,.6),),gas)
        b,e=s.evolve(a,1.5e10,1e-3,reaction_substeps=50)
        self.assertGreater(e.photo_events[1],0.)
        self.assertGreater(e.photo_events[2],0.)
        self.assertGreater(b.gas.he_iii,0.)
        self.assertAlmostEqual(b.gas.he_total,gas.he_total,delta=3e-14)
    def test_hydrogen_and_helium_ionization_budgets(self):
        a=state_ref()
        b,e=s.evolve(a,3e10,1e-3,reaction_substeps=32)
        self.assertGreater(sum(e.photo_events),0)
        for j in range(3):self.assertGreater(e.photo_events[j],0)
        self.assertTrue(all(p.n_per_h>=0 for p in b.photons))
        self.assertTrue(all(x>=0 for x in b.gas.__dict__.values()))
        self.assertAlmostEqual(a.gas.h_total,b.gas.h_total,delta=5e-14)
        self.assertAlmostEqual(a.gas.he_total,b.gas.he_total,delta=5e-14)
        self.assertLess(abs(e.number_residual),2e-13)
        self.assertLess(abs(e.energy_residual_ev),2e-11)
        self.assertAlmostEqual(e.absorbed_energy_ev,e.binding_energy_ev+e.photoheat_ev,delta=3e-12)
        self.assertGreater(e.photoheat_ev,0.)
        self.assertEqual(e.recoil_owner,"OPEN_NO_BARYON_EULER_UPDATE")
    def test_source_injection_single_owner(self):
        a=state_ref()
        new=s.Node(61.,.4,.003)
        b,e=s.evolve(a,0.,1e-3,source=[new],a_end=1.02,b_end=.01)
        self.assertEqual(len(b.photons),len(a.photons)+1)
        self.assertAlmostEqual(e.emitted_number,.003)
        self.assertAlmostEqual(e.emitted_energy_ev,s.physical_energy(new,1.02,.01)*.003)
        self.assertAlmostEqual(e.energy_residual_ev,0.,delta=3e-14)
    def test_signed_shear_bidirectional_opacity(self):
        # A near-cut source crosses into and out of the H I channel under
        # signed shear, without assigning a permanent subthreshold sink.
        gas=s.Gas(1.,0.,0.,0.,0.)
        original=s.State((s.Node(13.65,0.,.3),),gas)
        a,e=s.evolve(original,5e9,1e-3,b_end=.06,a_end=1.0)
        self.assertLess(a.photons[0].n_per_h,.3)
        b,e2=s.evolve(original,5e9,1e-3,b_end=-.06,a_end=1.0)
        self.assertEqual(b.photons[0].n_per_h,.3)
        self.assertEqual(e2.photo_events[0],0.)
    def test_recoil_bookkept_not_absent(self):
        a=s.State((s.Node(30.,.6,.08),),s.Gas(1.,0.,0.,0.,0.))
        _,e=s.evolve(a,4e10,1e-3)
        self.assertGreater(e.absorbed_pz_ev_over_c,0.)
        self.assertIn("OPEN",e.recoil_owner)
    def test_invalid_input_and_e_max(self):
        a=state_ref()
        for dt,dens in ((-1.,1.),(1.,-1.),(math.inf,1.)):
            with self.assertRaises(ValueError):s.evolve(a,dt,dens)
        with self.assertRaises(ValueError):s.evolve(a,1.,1.,reaction_substeps=0)
        with self.assertRaises(ValueError):s.evolve(s.State((s.Node(60000.,.1,.01),),a.gas),1.,1.)
    def test_two_moments_not_full_spectrum(self):
        gas=s.Gas(1.,0.,.05,.03,0.)
        # Both N=1, Uq=60 eV/H, distinct positive spectral shapes.
        mon=s.State((s.Node(60.,0.,1.),),gas)
        bim=s.State((s.Node(40.,0.,.5),s.Node(80.,0.,.5)),gas)
        self.assertEqual(mon.nphot,bim.nphot)
        self.assertEqual(mon.u_phot_ev,bim.u_phot_ev)
        a,x=s.evolve(mon,4.e9,1e-3)
        b,y=s.evolve(bim,4.e9,1e-3)
        self.assertGreater(abs(x.photo_events[2]-y.photo_events[2]),1e-7)
        self.assertLess(abs(x.energy_residual_ev),2e-12)
        self.assertLess(abs(y.energy_residual_ev),2e-12)
    def test_multiple_gas_rates_timestep_convergence(self):
        a=state_ref();dt=5.e10;dens=1.e-3
        ref=ode_reference(a,dt,dens)
        errors=[]
        for k in (1,2,4,8,16,32,64,128):
            b,e=s.evolve(a,dt,dens,reaction_substeps=k)
            actual=np.array([p.n_per_h for p in b.photons]+list(b.gas.__dict__.values()))
            errors.append(float(np.max(np.abs(ref-actual))))
            self.assertLess(abs(e.number_residual),3e-13)
            self.assertLess(abs(e.energy_residual_ev),2e-11)
        self.assertLess(errors[-1],errors[-2])
        self.assertLess(errors[-2],errors[-3])
        self.assertLess(errors[-3],errors[-4])
        self.assertGreater(errors[-3]/errors[-2],3.0)
        self.assertGreater(errors[-2]/errors[-1],3.0)
    def test_random_positive_stock_ledger_stress(self):
        import random
        rng=random.Random(20261016)
        for trial in range(300):
            hi=rng.random()
            he_i=.08*rng.random()
            he_ii=(.08-he_i)*rng.random()
            gas=s.Gas(hi,1.-hi,he_i,he_ii,.08-he_i-he_ii)
            energy=[rng.uniform(13.,300.) for _ in range(4)]
            src=s.State(tuple(s.Node(ee,rng.uniform(-1.,1.),rng.random()*.1)
                              for ee in energy),gas)
            b,e=s.evolve(src,10.**rng.uniform(6.,12.),
                         10.**rng.uniform(-5.,-1.),reaction_substeps=2,
                         a_end=math.exp(rng.uniform(-.25,.25)),
                         b_end=rng.uniform(-.1,.1))
            self.assertTrue(all(p.n_per_h>=0 for p in b.photons))
            self.assertTrue(all(v>=0 for v in b.gas.__dict__.values()))
            self.assertLessEqual(abs(e.number_residual),1e-13)
            self.assertLessEqual(abs(e.energy_residual_ev),4e-12)
            self.assertLessEqual(abs(e.hydrogen_residual),2e-14)
            self.assertLessEqual(abs(e.helium_residual),2e-14)

    def test_pure_he_cascade_atom_stoichiometry(self):
        g=s.Gas(1.,0.,.08,0.,0.)
        a=s.State((s.Node(90.,-.25,.1),s.Node(110.,.7,.2)),g)
        b,l=s.evolve(a,8e10,1e-2,reaction_substeps=64)
        ai,aii=l.photo_events[1],l.photo_events[2]
        self.assertAlmostEqual(b.gas.he_i,.08-ai,delta=8e-15)
        self.assertAlmostEqual(b.gas.he_ii,ai-aii,delta=8e-15)
        self.assertAlmostEqual(b.gas.he_iii,aii,delta=8e-15)
        self.assertLess(aii,ai+1e-15)

    def test_one_channel_photoionization_exact_semigroup(self):
        # H-only photon energy < HeI, no other species channels.
        gas=s.Gas(.9,.1,.08,0.,0.)
        a=s.State((s.Node(18.,0.,.5),),gas)
        x,_=s.evolve(a,1e10,.001)
        y,_=s.evolve(a,5e9,.001)
        z,_=s.evolve(y,5e9,.001)
        self.assertAlmostEqual(x.photons[0].n_per_h,z.photons[0].n_per_h,delta=2e-14)
        self.assertAlmostEqual(x.gas.h_i,z.gas.h_i,delta=2e-14)

if __name__=="__main__":
    unittest.main(verbosity=2)
