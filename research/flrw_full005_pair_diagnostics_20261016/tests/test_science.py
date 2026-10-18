from fractions import Fraction as F
import importlib.util
import json
import math
import unittest

from fixtures import UNIT, case
from pair_diagnostics import diagnose_pair
from reconstruction_support import reconstruction_norm

spec=importlib.util.spec_from_file_location('independent_probe',UNIT/'probe_reconstruction.py')
probe=importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ScientificChecks(unittest.TestCase):
    def close(self,a,b):
        self.assertTrue(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-14),(a,b))

    def test_eight_preexisting_fixtures_against_independent_oracles(self):
        recorded=json.loads((UNIT/'probe/RESULT.json').read_text())
        residuals=[]
        for fixture in recorded['fixtures']:
            with self.subTest(fixture=fixture['name']):
                r=[(float(F(x)),float(F(y))) for x,y in fixture['reference_rational']]
                c=[(float(F(x)),float(F(y))) for x,y in fixture['candidate_rational']]
                lifted=lambda points:[(F.from_float(x),F.from_float(y)) for x,y in points]
                oracle=probe.polynomial_oracle(lifted(r),lifted(c))
                result=diagnose_pair(case(*zip(*r),'R'),case(*zip(*c),'C'))
                row=result['summary'][0]
                self.assertEqual(result['union_knots'],oracle['merged_knots'])
                truth={'sup_absolute_difference':float(oracle['sup']),
                       'l1_integral':float(oracle['l1']),
                       'l2_squared_integral':float(oracle['squared_integral']),
                       'l2_norm':math.sqrt(float(oracle['squared_integral'])),
                       'rms_difference':math.sqrt(float(oracle['squared_integral']/oracle['domain_length']))}
                for field,value in truth.items():self.close(row[field],value)
                exact=reconstruction_norm(r,c,'LN_A')
                self.close(row['sup_absolute_difference'],float(exact['sup_absolute_difference']))
                residuals.append({'fixture':fixture['name'],
                                  'absolute_residuals':{field:abs(row[field]-value)
                                                        for field,value in truth.items()}})
        (UNIT/'coding_evidence/C7_oracle_residuals.json').write_text(json.dumps(
            {'scope':'Eight synthetic stored-binary64 fixtures versus independent exact lifted oracle',
             'fixtures':residuals,'maximum_absolute_residual':max(
                 value for record in residuals for value in record['absolute_residuals'].values())},
            indent=2,allow_nan=False)+'\n')

    def test_sampling_gap(self):
        r=case([0,1],[0,0]);c=case([0,.50025,.5005,.50075,1],[0,0,1,0,0])
        sampled=[probe.interpolate(list(zip(c['series']['L'],c['series']['x_HII'])),i/1000)
                 for i in range(1001)]
        self.assertEqual(max(sampled),0)
        row=diagnose_pair(r,c)['summary'][0]
        self.assertEqual(row['sup_absolute_difference'],1)
        self.close(row['l1_integral'],1/4000)
        self.close(row['l2_squared_integral'],1/6000)

    def test_swap_redundant_knots_and_inequalities(self):
        r=case([0,.2,.7,1],[1,-1,2,0],'R')
        c=case([0,.1,.65,.9,1],[-1,2,-2,1,2],'C')
        a=diagnose_pair(r,c)['summary'][0];b=diagnose_pair(c,r)['summary'][0]
        for field in ('sup_absolute_difference','l1_integral','l2_squared_integral','l2_norm','rms_difference'):
            self.assertEqual(a[field],b[field])
        for field in ('initial_difference','endpoint_difference','signed_difference_at_sup'):
            self.assertEqual(a[field],-b[field])
        self.assertLessEqual(a['mean_absolute_difference'],a['rms_difference'])
        self.assertLessEqual(a['rms_difference'],a['sup_absolute_difference'])
        self.assertLessEqual(a['l2_squared_integral'],a['sup_absolute_difference']*a['l1_integral'])
        affine=case([0,1],[2,4]);redundant=case([0,.25,.5,.75,1],[2,2.5,3,3.5,4])
        original=diagnose_pair(r,affine)['summary'][0]
        refined=diagnose_pair(r,redundant)['summary'][0]
        for field in original:
            if isinstance(original[field],(int,float)):self.close(original[field],refined[field])
            else:self.assertEqual(original[field],refined[field])

    def test_measure_scaling_units_and_nonmonotone_temperature(self):
        r=case([0,.5,1],[10,10,10],field='Tgas_K')
        c=case([0,.5,1],[10,12,10],field='Tgas_K')
        a=diagnose_pair(r,c)['summary'][0]
        r2=case([2,3,4],[10,10,10],field='Tgas_K')
        c2=case([2,3,4],[10,12,10],field='Tgas_K')
        b=diagnose_pair(r2,c2)['summary'][0]
        self.assertEqual(a['units'],'K')
        self.close(b['l1_integral'],2*a['l1_integral'])
        self.close(b['l2_squared_integral'],2*a['l2_squared_integral'])
        self.close(b['l2_norm'],math.sqrt(2)*a['l2_norm'])
        self.close(b['rms_difference'],a['rms_difference'])
        self.assertEqual(b['sup_absolute_difference'],a['sup_absolute_difference'])
        self.assertEqual(b['ln_a_at_sup'],3)


if __name__=='__main__':
    unittest.main()
