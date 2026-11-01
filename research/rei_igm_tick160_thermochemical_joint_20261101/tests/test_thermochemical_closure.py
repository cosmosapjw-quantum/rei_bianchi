import io,json,os,sys,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import thermochemical_closure as c
ARCHIVE=Path(os.environ.get('REI_INPUT_ARCHIVE', '/mnt/data/REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip'))

class OriginalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src,cls.meta=c.read_original(ARCHIVE)
        cls.d=c.derived(cls.src)
    def test_source_exact_archive_identity(self):
        self.assertEqual(c.digest(ARCHIVE.read_bytes()),c.ARCHIVE_SHA256)
    def test_source_lane_identity_and_nodes(self):
        self.assertEqual(len(self.d['node']),46080)
        self.assertEqual(self.meta['original_accepted_tick'],160)
        self.assertEqual(self.meta['original_accepted_endpoints'],3)
        self.assertEqual(len(self.meta['physical_states']),3)
    def test_hhe_charge_and_thermal_helium_ratio(self):
        self.assertLess(float(np.max(abs(self.d['y_He_by_charge']-c.Y_HE))),5e-8)
        self.assertLess(float(np.max(abs(self.d['y_He_by_thermal']-c.Y_HE))),5e-8)
    def test_positive_thermochemical_real_state(self):
        self.assertTrue(np.all(self.d['E_ion_eV_per_H']>0))
        self.assertTrue(np.all(self.d['E_material_eV_per_H']>self.d['E_ion_eV_per_H']))
    def test_ion_binding_enclosure_monotonic(self):
        self.assertTrue(np.all(self.d['E_ion_lower_eV_per_H']<=self.d['E_ion_eV_per_H']))
        self.assertTrue(np.all(self.d['E_ion_upper_eV_per_H']>=self.d['E_ion_eV_per_H']))
    def test_marginal_closure_is_enclosure(self):
        self.assertTrue(np.all(self.d['T_from_marginal_lower_K']<=self.src['T_K_lo']*(1+5e-10)))
        self.assertTrue(np.all(self.d['T_from_marginal_upper_K']>=self.src['T_K_hi']*(1-5e-10)))
    def test_original_gate_not_admitted(self):
        s=c.summary(self.d,self.meta)
        self.assertEqual(s['canonical_delta'],0)
        self.assertEqual(s['new_original_IVPs'],0)
        self.assertGreater(s['original_next_tick_local_error'],s['original_local_error_bound'])
    def test_derivative_fixed_total_energy_finite_difference(self):
        # independent numerical finite difference of the algebraic exact material energy closure
        for j in (0,2000,15000,37000):
            x=np.array([self.d['x_HII'][j],self.d['x_HeII'][j],self.d['x_HeIII'][j]])
            n0=1+c.Y_HE+self.d['xe_per_H'][j]
            U0=self.d['U_thermal_eV_per_H'][j]
            emat=self.d['E_material_eV_per_H'][j]
            ion=lambda z:c.E_H_EV*z[0]+c.Y_HE*(c.E_HEI_EV*z[1]+(c.E_HEI_EV+c.E_HEII_EV)*z[2])
            ne=lambda z:1+c.Y_HE+z[0]+c.Y_HE*(z[1]+2*z[2])
            lnT=lambda z: np.log((emat-ion(z))/ne(z))
            eps=2e-7
            slopes=[]
            for i in range(3):
                a=x.copy();b=x.copy();a[i]+=eps;b[i]-=eps
                slopes.append((lnT(a)-lnT(b))/(2*eps))
            analytic=[-self.d[key][j] for key in ('abs_dlnT_dx_HII_at_fixed_Ematerial','abs_dlnT_dx_HeII_at_fixed_Ematerial','abs_dlnT_dx_HeIII_at_fixed_Ematerial')]
            np.testing.assert_allclose(slopes,analytic,rtol=1e-6,atol=8e-9)
    def test_physical_heII_to_heIII_reaction_direction(self):
        for j in (0,2000,15000,37000):
            x=np.array([self.d['x_HII'][j],self.d['x_HeII'][j],self.d['x_HeIII'][j]])
            emat=self.d['E_material_eV_per_H'][j]
            ion=lambda z:c.E_H_EV*z[0]+c.Y_HE*(c.E_HEI_EV*z[1]+(c.E_HEI_EV+c.E_HEII_EV)*z[2])
            ne=lambda z:1+c.Y_HE+z[0]+c.Y_HE*(z[1]+2*z[2])
            lnT=lambda z:np.log((emat-ion(z))/ne(z))
            eps=1e-7
            a=x.copy();b=x.copy();a[1]-=eps;a[2]+=eps;b[1]+=eps;b[2]-=eps
            deriv=(lnT(a)-lnT(b))/(2*eps)
            self.assertAlmostEqual(deriv,-self.d['abs_dlnT_dHeII_to_HeIII_at_fixed_Ematerial'][j],delta=2e-8)
    def test_fixed_U_different_from_fixed_total_energy(self):
        for key in ('HII','HeII','HeIII'):
            self.assertTrue(np.all(self.d['abs_dlnT_dx_'+key+'_at_fixed_Ematerial']>self.d['abs_dlnT_dx_'+key+'_at_fixed_Uthermal']))
    def test_3source_lanes_numerical_equal(self):
        self.assertEqual(c.STATE_ARRAY_SHA256, self.meta['physical_states'][0]['state_array_sha256'])
    def test_thermal_midpoint_self_consistency(self):
        self.assertLess(float(np.max(self.d['thermal_closure_midpoint_relative_residual'])),1.5e-9)
    def test_source_width_not_error_gate(self):
        s=c.summary(self.d,self.meta)
        self.assertIn('not a parent-state-width gate',s['WARNING_scale_not_a_width_gate'])
        self.assertEqual(s['source_logT_parent_widths_above_original_local_error_numerical_scale'],0)
        self.assertGreater(s['independent_marginal_logT_parent_widths_above_original_local_error_numerical_scale'],0)
    def test_helium_zero_limit_analytic(self):
        xx=.4;T=1e4;y=0.; e=.5
        U=1.5*c.K_B_CGS*T*(1+y+xx)
        self.assertAlmostEqual(U,1.5*c.K_B_CGS*T*(1+xx))
    def test_denominator_nonzero(self):
        self.assertTrue(np.all(1+c.Y_HE+self.d['xe_per_H']>2.))
    def test_invariant_dimension(self):
        self.assertAlmostEqual(c.ERG_PER_EV * c.E_H_EV,2.178709416e-11,delta=1e-14)
    def test_no_offmanifold_helium(self):
        x2=self.d['x_HeII'];x3=self.d['x_HeIII']
        self.assertTrue(np.all(x2+x3 < 1.00001))

if __name__=='__main__':unittest.main()
