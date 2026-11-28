"""Only new conditional angular-moment tests; no old BASS_HE suite or IVPs."""
import sys
import unittest
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
import numpy as np
from scipy.integrate import quad
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import angular_moments as a

class AngularMomentScopedTests(unittest.TestCase):
    def test_source_row_values(self):
        self.assertEqual(a.SOURCE_330[2],(F(73),F("0.07"),F("0.05")))
    def test_source_metadata_pinned(self):
        self.assertEqual(len(a.SOURCE_SHA256),64)
        self.assertEqual(a.SOURCE_GIT_BLOB,"c49433293921dbb012d7f1b0387745732a598efa")
    def test_min_l_exact(self):self.assertEqual(a.min_L(),F(1,700))
    def test_below_min_l_rejected(self):
        with self.assertRaises(ValueError):a.segments(F(1,701))
    def test_source_energy_identity_mutation_rejected(self):
        mutated=list(a.SOURCE_330)
        mutated[0]=(F(45),mutated[0][1],mutated[0][2])
        with self.assertRaises(ValueError):a.source_rows(mutated)
    def test_source_value_mutation_changes_lmin(self):
        mutated=list(a.SOURCE_330)
        mutated[2]=(F(73),F("0.01"),F(0))
        self.assertNotEqual(a.min_L(mutated),a.min_L())
    def test_negative_source_rejected(self):
        mutated=list(a.SOURCE_330)
        mutated[0]=(F(46),F(-1),F(0))
        with self.assertRaises(ValueError):a.source_rows(mutated)
    def test_float_bool_rejected(self):
        for value in (330.0, True, False):
            with self.assertRaises(TypeError):a.Q(value)
    def test_envelope_nonnegative_and_continuous(self):
        for L in (F(1,700),F(1,200),F(1,100)):
            lower=a.segments(L,"lower");upper=a.segments(L,"upper")
            self.assertEqual((lower[0][0],lower[-1][1]),(0,90))
            for parts in (lower,upper):
                for left,right in zip(parts[:-1],parts[1:]):
                    self.assertEqual(left[1],right[0])
                    self.assertEqual(left[2]+left[3]*left[1],right[2]+right[3]*right[0])
                    self.assertLessEqual(abs(left[3]),L)
                for l,h,offset,slope in parts:
                    self.assertGreaterEqual(offset+slope*l,0)
                    self.assertGreaterEqual(offset+slope*h,0)
            for k in range(361):
                theta=F(k,4)
                self.assertLessEqual(a.value_at(lower,theta),a.value_at(upper,theta))
    def test_each_source_interval_feasible(self):
        for L in (F(1,700),F(1,200)):
            lo=a.segments(L,"lower");hi=a.segments(L,"upper")
            for deg,mid,stat in a.SOURCE_330:
                for parts in (lo,hi):
                    val=a.value_at(parts,deg)
                    self.assertGreaterEqual(val,mid-stat)
                    self.assertLessEqual(val,mid+stat)
    def test_exact_delta_positive_and_k0(self):
        self.assertEqual(a.K0(330),F("153.0767609"))
        self.assertGreater(a.delta2(330),0)
    def test_threshold_at_zero(self):
        th=(4*a.m*a.m-a.M*a.M)/(2*a.M)
        self.assertEqual(a.delta2(th),0)
    def test_threshold_negative(self):
        with self.assertRaises(ValueError):a.delta2(0)
    def test_analytic_moment_integral_independent_scipy(self):
        for L in (F(1,700),F(1,200)):
            for kind in ("lower","upper"):
                with mp.workdps(55):
                    D,N=a.integrals(L,kind,55)
                segs=a.segments(L,kind)
                def numerical(moment):
                    def f(t):
                        z=t*np.pi/180
                        values=float(a.value_at(segs,F(str(t))))
                        return values*np.sin(z)*(np.cos(z)**2 if moment else 1)*np.pi/180
                    points=sorted(set(float(z) for seg in segs for z in seg[:2]))
                    return sum(quad(f,x,y,epsabs=1e-12,epsrel=1e-12)[0] for x,y in zip(points[:-1],points[1:]))
                self.assertLess(abs(float(D)-numerical(0)),2e-12)
                self.assertLess(abs(float(N)-numerical(1)),2e-12)
    def test_recovers_pr105_total_envelopes(self):
        x=a.outer_interval("1/200",52,88)
        self.assertLess(abs(float(x["I_min_nb"])-1.0068860482429433),2e-12)
        self.assertLess(abs(float(x["I_max_nb"])-2.423539172537024),2e-12)
    def test_conditional_normalized_ratio_strict_order(self):
        for L in ("1/700","1/200","1/100"):
            x=a.outer_interval(L,50,85)
            b0=float(x["b_outer_lower"]); b1=float(x["b_outer_upper"])
            s0=float(x["b_feasible_lower_envelope"])
            s1=float(x["b_feasible_upper_envelope"])
            self.assertTrue(0<=b0<=s0<=b1<=1)
            self.assertTrue(0<=b0<=s1<=b1<=1)
            self.assertIsNone(x["kappa"]);self.assertIsNone(x["R_event"])
    def test_outer_sign_bisect_invariants(self):
        with mp.workdps(50):
            for L in ("1/700","1/200","1/100"):
                x=a.outer_interval(L,50,90)
                l=mp.mpf(x["b_outer_lower"]);u=mp.mpf(x["b_outer_upper"])
                self.assertGreaterEqual(a._outer_signed(l,L,"lower",50),-mp.mpf("1e-24"))
                self.assertLessEqual(a._outer_signed(u,L,"upper",50),mp.mpf("1e-24"))
    def test_monotone_outer_family_with_lipschitz(self):
        r=[a.outer_interval(L,50,85) for L in ("1/700","1/200","1/100")]
        self.assertGreater(float(r[0]["b_outer_lower"]),float(r[1]["b_outer_lower"]))
        self.assertGreater(float(r[1]["b_outer_lower"]),float(r[2]["b_outer_lower"]))
        self.assertLess(float(r[0]["b_outer_upper"]),float(r[1]["b_outer_upper"]))
        self.assertLess(float(r[1]["b_outer_upper"]),float(r[2]["b_outer_upper"]))
    def test_quadratic_manufactured_deposition_nonisotropic(self):
        E=330;star=300;atoms=[(-1,1),(F(0),1),(F(1,2),3)]
        v=a.manufactured_quadratic_deposition(E,atoms,star)
        b=F(1+3*F(1,4),5)
        self.assertEqual(F(v["b_exact"]),b)
        with mp.workdps(48):
            k0=mp.mpf(a.K0(E).numerator)/a.K0(E).denominator
            d2=mp.mpf(a.delta2(E).numerator)/a.delta2(E).denominator
            self.assertLess(abs(mp.mpf(v["pair_manufactured_deposit_MeV"])-2*(k0*k0+d2*(mp.mpf(b.numerator)/b.denominator))/star),mp.mpf("1e-35"))
        self.assertIsNone(v["R_event"]);self.assertIsNone(v["physical_deposition_rate"])
    def test_manufactured_invalid_not_physical(self):
        with self.assertRaises(ValueError):a.manufactured_quadratic_deposition(330,[(0,1)],1)
        with self.assertRaises(ValueError):a.manufactured_quadratic_deposition(330,[(0,-1)],300)
        with self.assertRaises(ValueError):a.manufactured_quadratic_deposition(330,[],300)
    def test_angular_acceptance_is_not_global_kappa(self):
        # Multiplying f(theta) by an ANGLE-DEPENDENT detector response changes b.
        with mp.workdps(45):
            parts=a.segments("1/200","upper")
            D,N=a.integrals("1/200","upper",45)
            raw=N/D
            # independent integration of (1 + cos^2(theta)) f
            extra=mp.mpf(0)
            for seg in parts:
                val=quad(lambda th: float(a.value_at(parts,F(str(th))))*
                     (np.cos(np.pi*th/180)**4)*np.sin(np.pi*th/180)*np.pi/180,
                     float(seg[0]),float(seg[1]),epsabs=1e-13)[0]
                extra+=mp.mpf(val)
            biased=(N+extra)/(D+N)
            self.assertGreater(abs(float(biased-raw)),1e-3)

if __name__ == "__main__":
    unittest.main()
