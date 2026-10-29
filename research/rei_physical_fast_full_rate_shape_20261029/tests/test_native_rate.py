"""No-IVP tests: BASS unmodified source methods with projected pinned coefficient table."""
from __future__ import annotations
import sys,unittest,math,struct,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import native_full_rate as m
import numpy as np

class NativeSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.net=m.new_native_network()

 def test_numeric_projection_matches_live_git_source_fingerprint(self):
    d=json.loads((m.SRC/'COEFF_NUMERIC_PROJECTION.json').read_text()); numbers=[]
    for k in sorted(d['photo']): numbers+=d['photo'][k]
    for k in sorted(d['rr']): numbers+=d['rr'][k]
    for k in sorted(d['dr']): numbers+=d['dr'][k][0]+d['dr'][k][1]
    for k in ['PH1_1s','PH1_2s','PH2_2s']: numbers+=d['li'][k]
    numbers+=d['domain']
    self.assertEqual(len(numbers),129)
    h=0xcbf29ce484222325
    for f in numbers:
      for byte in struct.pack('<d',float(f)):h=((h^byte)*0x100000001b3)&((1<<64)-1)
    self.assertEqual(f'{h:016x}','b8d5383717a0f023')

 def test_p19_projection_matches_live_git_source_fingerprint(self):
    d=json.loads((m.SRC/'P19_13_KNOTS.json').read_text())
    nums=sum(d['rows'],[]);self.assertEqual(len(nums),91)
    h=0xcbf29ce484222325
    for f in nums:
      for byte in struct.pack('<d',float(f)):h=((h^byte)*0x100000001b3)&((1<<64)-1)
    self.assertEqual(f'{h:016x}','18f1eb671df4567b')

 def test_original_byte_locks(self):
    self.assertEqual(m.source_manifest_check(),m.EXPECTED)

 def test_native_rate_calibration(self):
    n=self.net
    self.assertAlmostEqual(n._photo_s[1]/1e-12,1.0,places=13)
    self.assertAlmostEqual(n._photo_s[3]/n._photo_s[1],1.,places=13) # D agrees with H1 by source Z,q
    self.assertAlmostEqual(n._photo_s[5]/n._photo_s[1],1.,places=13) # T agrees
    self.assertEqual(n.photo_indices.size,13)
    self.assertEqual(n.recombination_indices.size,13)

 def test_li_native_source_reference_cross_sections(self):
    n=self.net
    # Source coefficient file carries independent reference tests at 80 eV.
    sigma,inner=n.photo_cross_sections([80.])
    self.assertAlmostEqual(sigma[13,0]/1e-22,2.406165919296005+0.030971341445678712,places=11)
    self.assertAlmostEqual(inner[13,0]/1e-22,2.406165919296005,places=11)

 def test_full_native_21_jacobian(self):
    n=self.net
    y,r,J,T,uv=m.native_jac_snapshot(n)
    self.assertEqual(J.shape,(21,21))
    self.assertTrue(np.allclose(J,r['jac'],rtol=0,atol=0))
    self.assertTrue(np.allclose(n.A@J,0,rtol=0,atol=1e-22))
    self.assertTrue(np.allclose(n.A@r['dY_dt'],0,rtol=0,atol=1e-23))
    self.assertTrue(np.isfinite(J).all())
    self.assertGreater(float(np.linalg.norm(r['dY_dt'])),0)

 def test_source_jac_fd(self):
    n=self.net
    y,r,J,T,uv=m.native_jac_snapshot(n)
    rng=np.random.default_rng(7)
    for _ in range(8):
        direction=rng.normal(size=21)
        direction/=np.linalg.norm(direction)
        h=1e-5
        plus=n.evaluate(y+h*direction,T,uv,1e6)['dY_dt']
        minus=n.evaluate(y-h*direction,T,uv,1e6)['dY_dt']
        fd=(plus-minus)/(2*h)
        exact=J@direction
        self.assertLess(float(np.linalg.norm(fd-exact)),3e-9*max(float(np.linalg.norm(exact)),1e-24))

 def test_bass_photo_li6_lift(self):
    n=self.net
    for source,dest in [(13,17),(14,18),(15,19),(16,20)]:
        self.assertEqual(n.q[source],n.q[dest]);self.assertEqual(n.Z[source],n.Z[dest]);
    for T in [300.0,12000.0]:
        rate=n.rates(T,0.7)
        for a,b in [(13,17),(14,18),(15,19),(16,20)]:
            self.assertAlmostEqual(rate['photo_s'][a],rate['photo_s'][b],places=20)
            self.assertAlmostEqual(rate['rr_m3_s'][a],rate['rr_m3_s'][b],places=28)

 def test_photo_stoichiometry(self):
    self.assertTrue(np.array_equal(m.A17@m.STOICH,np.zeros(7)))
    self.assertTrue(np.array_equal(m.Q17@m.STOICH,np.ones(7)))
    self.assertEqual(np.linalg.matrix_rank(m.STOICH),7)

 def test_puchwein_nominal_anchor(self):
    # Original PR261 frozen nominal at z=3.6 from reported source response.
    g=m.p19_nominal_gamma(3.6)
    self.assertAlmostEqual(g[0]/7.926186875920432e-13,1.,places=12)

 def test_saved_seven_source_rate_gaps(self):
    rows=m.compare_on_saved_rows(self.net)
    self.assertEqual(len(rows),7)
    self.assertTrue(all(r['max_relative_family_rate_gap']>0 for r in rows))
    self.assertTrue(all(abs(r['signed_electron_delta_per_Href_s']-r['direct_electron_delta_per_Href_s'])<1e-25 for r in rows))
    self.assertTrue(all(abs(r['isotope_heavy_y_invariant'])<2e-25 for r in rows))
    self.assertTrue(all(abs(r['photo_charge_bookkeeping'])<2e-25 for r in rows))

 def test_shape_minimax_exact_extrema(self):
    b=np.array([1.,2.,4.]);p=np.ones(3)
    u,e,w=m.amplitude_shape_minimax(b,p)
    self.assertAlmostEqual(u,0.4,places=14)
    self.assertAlmostEqual(e,0.6,places=14)
    self.assertAlmostEqual(w,e,places=14)
    for probe in np.linspace(.01,1,100):
        self.assertGreaterEqual(np.max(np.abs(probe*b-1)),e-1e-14)

 def test_electron_matched_not_full_vector(self):
    rows=m.compare_on_saved_rows(self.net)
    self.assertEqual(len(rows),7)
    for r in rows:
        self.assertLess(abs(r['electron_matched_charge_residual']),1e-27)
        self.assertGreater(r['electron_matched_vector_residual_l2_s'],1e-20)
        self.assertGreater(r['amplitude_minimax_error'],0.0)
        self.assertLess(abs(r['amplitude_minimax_error']-r['amplitude_minimax_witness']),1e-14)

 def test_no_p19_z20_extrapolation(self):
    with self.assertRaisesRegex(ValueError,'P19 calibration'):
        m.p19_nominal_gamma(20)

if __name__=='__main__':unittest.main()
