"""Independent exact-rational controls; imports no oracle from the kernel."""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys
import unittest
from ccc_exchange import (ContractError, raw_pair_diagnostics,
    phase_intensity_interval, coherent_disk_interval,
    admit_equal_sharing_record, spin_average)

UNIT = Path(__file__).resolve().parents[1]
TOL = 5e-13


def rational(p):
    return F.from_float(p['mantissa'])*(F(2)**p['exponent'])


def oracle(a, b, spin):
    ar, ai = map(F, a)
    br, bi = map(F, b)
    s = (-1)**spin
    return {'U': ar*ar+ai*ai+br*br+bi*bi,
            'C': (ar+s*br)**2+(ai+s*bi)**2,
            'D': (ar-s*br)**2+(ai-s*bi)**2}


def record(spin=0, **update):
    r = {'source_profile': 'CCC_RAW_EQUAL_SHARING', 'source_id': 'MANUFACTURED',
         'producer_family':'MANUFACTURED_CCC_PROFILE', 'kinematics_id':'POINT_1', 'preparation_id':'UNPOLARIZED_MIXTURE_1',
         'density_unit': 'manufactured_density_unit',
         'differential_measure': 'dOmega1*dOmega2*dE2',
         'outgoing_energies': {'kind': 'point_exact', 'values': ['1', '1.00'], 'unit': 'Ry'},
         'spin': spin, 'spin_weight_applied': False,
         'representation': 'raw_amplitudes', 'a': [1., 1.], 'b': [2., -1.],
         'phase_provenance': {'source_id': 'MANUFACTURED',
                              'common_convention': 'exact manufactured cartesian',
                              'relative_phase_preserved': True}}
    r.update(update)
    return r


class Controls(unittest.TestCase):
    def close(self, value, expected, scale=None):
        if scale is None:
            scale = max(abs(expected), F(1, 10**300))
        self.assertLessEqual(abs(float((rational(value)-expected)/scale)), TOL)

    def test_01_printed_sign_counterexample_both_spins(self):
        for spin, c, d in [(0, 9, 5), (1, 5, 9)]:
            r = raw_pair_diagnostics([1, 1], [2, -1], spin)
            for k, v in [('U', 7), ('C', c), ('D', d)]:
                self.close(r[k], F(v))
            self.assertEqual(2*rational(r['U']), rational(r['C'])+rational(r['D']))
            self.assertNotEqual(2*rational(r['U']), rational(r['C'])-rational(r['D']))
            self.assertAlmostEqual(r['eta'], d/14, delta=TOL)

    def test_02_independent_fraction_grid(self):
        for spin in (0, 1):
            for n in range(-7, 8):
                a, b = [n/8, (n+3)/4], [(2-n)/4, n/16]
                expected = oracle(a, b, spin)
                r = raw_pair_diagnostics(a, b, spin)
                for k in expected:
                    self.close(r[k], expected[k], max(expected['U'], F(1)))
                self.assertLessEqual(r['eta'], 1+TOL)
                self.assertGreaterEqual(r['eta'], 0)

    def test_03_swap_and_common_phase(self):
        a, b = [1., 2.], [3., -4.]
        for spin in (0, 1):
            r = raw_pair_diagnostics(a, b, spin)
            for aa, bb in [(b, a), ([-a[1], a[0]], [-b[1], b[0]])]:
                q = raw_pair_diagnostics(aa, bb, spin)
                for key in ('U', 'C', 'D'):
                    self.close(q[key], rational(r[key]))
                self.assertAlmostEqual(q['eta'], r['eta'], delta=TOL)

    def test_04_destructive_and_zero(self):
        for spin, b in [(0, [-1, 0]), (1, [1, 0])]:
            r = raw_pair_diagnostics([1, 0], b, spin)
            self.assertEqual(r['C']['status'], 'ZERO')
            self.assertEqual(r['eta'], 1)
        r = raw_pair_diagnostics([0, 0], [0, 0], 0)
        self.assertIsNone(r['eta'])
        self.assertEqual(r['U']['status'], 'ZERO')

    def test_05_extreme_scales(self):
        for scale, flag in [(1e308, 'OVERFLOW'), (1e-308, 'UNDERFLOW')]:
            for spin in (0, 1):
                a, b = [scale, scale], [scale, -scale]
                r = raw_pair_diagnostics(a, b, spin)
                expected = oracle(a, b, spin)
                for key in ('U', 'C', 'D'):
                    self.close(r[key], expected[key], expected['U'])
                    self.assertEqual(r[key]['status'], flag)
                    self.assertIsNone(r[key]['float'])
                self.assertAlmostEqual(r['eta'], .5, delta=TOL)
        # An unrelated huge component must not erase a tiny coherent remainder.
        r = raw_pair_diagnostics([1e308, 1e-308], [-1e308, 1e-308], 0)
        self.close(r['C'], oracle([1e308, 1e-308], [-1e308, 1e-308], 0)['C'])
        self.assertEqual(r['C']['status'], 'UNDERFLOW')

    def test_06_phase_sharp_endpoints(self):
        for a, b in [(0, 0), (0, 3), (2, 2), (3, 4), (1e154, 1e154)]:
            r = phase_intensity_interval(a*a, b*b)
            self.close(r['lower'], (F(a)-F(b))**2, max((F(a)+F(b))**2, F(1)))
            self.close(r['upper'], (F(a)+F(b))**2)
            self.assertIsNone(r['C'])

    def test_07_phase_near_equal_rationalized(self):
        from decimal import Decimal, localcontext
        A, B = 1., math.nextafter(1., 2.)
        with localcontext() as ctx:
            ctx.prec = 100
            exact = (Decimal.from_float(A).sqrt()-Decimal.from_float(B).sqrt())**2
        r = phase_intensity_interval(A, B)
        self.close(r['lower'], F(exact))
        self.assertGreater(r['lower']['mantissa'], 0)

    def test_08_disk_endpoints(self):
        for spin in (0, 1):
            # zhat=3+4i for either spin, length5, radius.5+.75=1.25.
            r = coherent_disk_interval([3, 4], [0, 0], spin, .5, .75)
            self.close(r['lower'], F(15,4)**2)
            self.close(r['upper'], F(25,4)**2)
            s = (-1)**spin
            for direction, endpoint in [(-1, 'lower'), (1, 'upper')]:
                a = [3+direction*.5*.6, 4+direction*.5*.8]
                b = [s*direction*.75*.6, s*direction*.75*.8]
                observed = raw_pair_diagnostics(a, b, spin)
                self.close(observed['C'], rational(r[endpoint]))
        r = coherent_disk_interval([0, 0], [0, 0], 0, 1e308, 1e308)
        self.assertEqual(r['lower']['status'], 'ZERO')
        self.assertEqual(r['upper']['status'], 'OVERFLOW')

    def test_09_weights_once(self):
        raw = spin_average([record(0), record(1)])
        self.close(raw['C'], F(6))
        self.close(raw['U'], F(7))
        self.close(raw['D'], F(8))
        coherent = [record(0, representation='coherent_density', density=9),
                    record(1, representation='coherent_density', density=5)]
        weighted = [record(0, representation='coherent_density', density=2.25, spin_weight_applied=True),
                    record(1, representation='coherent_density', density=3.75, spin_weight_applied=True)]
        for rs in (coherent, weighted):
            self.close(spin_average(rs)['C'], rational(raw['C']))
        one = admit_equal_sharing_record(record(representation='coherent_density', density=4))
        self.close(one['C'], F(4))
        self.assertFalse(one['physical_provider_admitted'])

    def test_10_intensity_route_never_exact(self):
        r = admit_equal_sharing_record(record(representation='incoherent_intensities', A=1, B=1))
        self.assertIsNone(r['C'])
        self.close(r['interval']['lower'], F(0), F(1))
        self.close(r['interval']['upper'], F(4))
        r = spin_average([record(0, representation='incoherent_intensities', A=1, B=1), record(1)])
        self.assertIsNone(r['C'])
        self.close(r['interval']['lower'], F(15,4))
        self.close(r['interval']['upper'], F(19,4))

    def test_11_profile_and_provenance_rejections(self):
        for changes in [dict(source_profile='OTHER'), dict(spin=True), dict(spin=2),
                        dict(spin_weight_applied=1), dict(spin_weight_applied=True),
                        dict(phase_provenance={}), dict(density_unit=''),
                        dict(representation='unknown')]:
            with self.assertRaises(ContractError):
                admit_equal_sharing_record(record(**changes))
        for values in [['1', '1.000000000000000000000000000001'], ['NaN', 'NaN'], ['-1','-1']]:
            with self.assertRaises(ContractError):
                admit_equal_sharing_record(record(outgoing_energies={'kind':'point_exact','unit':'Ry','values':values}))
        with self.assertRaises(ContractError):
            admit_equal_sharing_record(record(outgoing_energies={'kind':'finite_bin','unit':'Ry','values':['1','1']}))

    def test_12_channel_mismatch(self):
        for key, value in [('density_unit','OTHER'), ('differential_measure','dE2'), ('source_id','OTHER'), ('kinematics_id','POINT_2'), ('producer_family','OTHER'), ('preparation_id','OTHER')]:
            with self.assertRaises(ContractError):
                spin_average([record(0), record(1, **{key:value})])
        with self.assertRaises(ContractError):
            spin_average([record(0), record(1, outgoing_energies={'kind':'point_exact','unit':'Ry','values':['2','2']})])
        with self.assertRaises(ContractError):
            spin_average([record(0), record(0)])
        with self.assertRaises(ContractError):
            spin_average([record(0)])

    def test_13_nonfinite_and_negative(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ContractError): raw_pair_diagnostics([value,0], [0,0], 0)
            with self.assertRaises(ContractError): phase_intensity_interval(value, 1)
            with self.assertRaises(ContractError): coherent_disk_interval([0,0], [0,0], 0, value, 0)
        for f in (lambda: phase_intensity_interval(-1,0), lambda: coherent_disk_interval([0,0],[0,0],0,-1,0)):
            with self.assertRaises(ContractError): f()

    def test_14_real_table_normalization_noop(self):
        table = json.loads((UNIT/'source/Stelbovics1999_TableI.json').read_text())
        expected = ['0.0172','0.0145','0.0137','0.0135','0.0072','0.0081','0.0069','0.0069']
        self.assertEqual([r['published_4CCC_pi_a0_squared_per_Ryd'] for r in table['rows']], expected)
        self.assertEqual(table['normalization']['published_factor_four_already_applied'], True)
        for row in table['rows']:
            r=record(representation='coherent_density', density=float(row['published_4CCC_pi_a0_squared_per_Ryd']), density_unit='pi*a0^2/Ry', differential_measure='dE_secondary', source_id='Stelbovics1999_TP_TableI', outgoing_energies={'kind':'point_exact','values':[str(F(row['total_three_body_energy_Ryd'])/2)]*2,'unit':'Ry'})
            # Table energies2,3 Ry give outgoing1,1.5 Ry exact decimal.
            r['outgoing_energies']['values'] = ['1','1'] if row['total_three_body_energy_Ryd']=='2' else ['1.5','1.5']
            self.assertEqual(admit_equal_sharing_record(r)['C']['float'], float(row['published_4CCC_pi_a0_squared_per_Ryd']))


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    report = {'status':'PASS' if result.wasSuccessful() else 'FAIL', 'test_methods':result.testsRun,
              'failures':len(result.failures), 'errors':len(result.errors),
              'independent_oracle':'Fraction complex algebra; Decimal100 near-equal square-root reference',
              'scaled_numeric_tolerance':TOL, 'physical_provider_admitted':False,
              'old_suite_runs':0, 'machine_directed_rounding_certificate':False}
    (UNIT/'results/test_report.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
