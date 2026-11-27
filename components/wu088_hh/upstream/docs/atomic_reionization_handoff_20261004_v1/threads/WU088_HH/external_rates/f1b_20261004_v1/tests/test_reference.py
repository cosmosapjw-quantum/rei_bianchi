import sys,unittest,json,tempfile,subprocess,hashlib
from pathlib import Path
from fractions import Fraction as F
from decimal import localcontext,Decimal as D
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from hh_f03_binding import evaluate,direction,ProviderError
from test_red_green import MODEL,state,contains

class Reference(unittest.TestCase):
    def test_neutral_electron_free_gas_does_not_disable_HH(self):
        r=evaluate(MODEL,state(h='0',he1='0',he2='0'),'LCS91')
        self.assertGreater(F(r['event_rate_cm3_s'][0]),0)
    def test_absent_hydrogen_remains_zero_without_division(self):
        m=dict(MODEL,n_h_cm3='0');r=evaluate(m,['.2','.1','.1','20000','0','0','0'],'LCS91')
        self.assertEqual(r['rhs'],[['0','0']]*7)
        self.assertEqual(r['scalar_gradient'],[['0','0']]*7)
    def test_pure_H_has_zero_helium_derivatives(self):
        r=evaluate(dict(MODEL,n_he_cm3='0'),state(),'LCS91')
        self.assertEqual(r['scalar_gradient'][1:3],[['0','0']]*2)
    def test_unknown_provider_rejected_even_with_zero_H(self):
        with self.assertRaises(ProviderError):evaluate(dict(MODEL,n_h_cm3='0'),state(),'missing')
    def test_invalid_states(self):
        for s in (['2','0','0','1','0','0','0'],['0','.8','.8','1','0','0','0'],['0','0','0','0','0','0','0'],['0','0','0','1','-1','0','0']):
            with self.subTest(s=s),self.assertRaises(ProviderError):evaluate(MODEL,s,'LCS91')
    def test_missing_or_extra_model_fields_rejected(self):
        for m in ({},dict(MODEL,source_is_admitted=True),dict(MODEL,kb_erg_k='0')):
            with self.subTest(m=m),self.assertRaises(ProviderError):evaluate(m,state(),'LCS91')
    def test_float_boolean_inputs_rejected(self):
        for x in (True,.2,float('nan')):
            s=state();s[0]=x
            with self.subTest(x=x),self.assertRaises(ProviderError):evaluate(MODEL,s,'LCS91')
    def test_exact_rational_temperature_boundary_ownership(self):
        with localcontext() as c:
            c.prec=140
            for d,expected in [('-1e-90','ARTIFICIAL_FLOOR_INTERIOR'),('1e-90','ANALYTIC')]:
                T=str(D(3000)+D(d));r=evaluate(MODEL,state(T=T),'LCS91')
                self.assertEqual(r['branch'],expected)
    def test_KS_has_no_3000_event(self):
        r=evaluate(MODEL,state(T='3000'),'KS92_corrected_Glover15')
        self.assertEqual(r['branch'],'ANALYTIC');self.assertIsNotNone(r['scalar_gradient'])
    def test_caller_decimal_context_does_not_change_result(self):
        r=evaluate(MODEL,state(),'LCS91');s=state()
        with localcontext() as c:
            c.prec=6
            self.assertEqual(evaluate(MODEL,s,'LCS91'),r)
    def test_all_photon_derivatives_zero(self):
        r=evaluate(MODEL,state(),'LCS91')
        for j in range(4,7):
            self.assertEqual(r['scalar_gradient'][j],['0','0'])
            self.assertTrue(all(x==['0','0'] for x in r['scalar_hessian'][j]))
    def test_hessian_exact_shape_symmetry(self):
        r=evaluate(MODEL,state(),'LCS91');h=r['hessian_shape_exact']
        self.assertEqual(h,[list(x) for x in zip(*h)])
    def test_floor_only_density_hessian(self):
        r=evaluate(MODEL,state(T='2000'),'LCS91');h=r['scalar_hessian']
        self.assertTrue(contains(h[0][0],'2e-20'))
        self.assertTrue(all(h[i][j]==['0','0'] for i in range(7) for j in range(7) if (i,j)!=(0,0)))
    def test_energy_J_and_H_null_contract_exact(self):
        m=dict(MODEL,chi_erg='13.2');r=evaluate(m,state(),'LCS91');c=list(map(F,r['rhs_factor_exact']))
        self.assertEqual(F(m['chi_erg'])*F(m['n_h_cm3'])*c[0]+c[3],0)
        for g in map(F,r['gradient_shape_exact']):self.assertEqual((F(m['chi_erg'])*c[0]+c[3])*g,0)
    def test_BE_increment_sign_dt_and_determinant(self):
        r=direction(MODEL,state(),'LCS91',['1','0','0','0','0','0','0'],'7')
        self.assertLess(F(r['BE_residual_addition'][0][1]),0)
        self.assertGreater(F(r['BE_residual_addition'][3][0]),0)
        self.assertGreaterEqual(F(r['HH_only_BE_determinant'][0]),1)
        self.assertFalse(r['full_BE_invertibility_claim'])
    def test_BE_boundary_and_negative_dt_rejected(self):
        with self.assertRaises(ProviderError):direction(MODEL,state(T='3000'),'LCS91',['0']*7)
        with self.assertRaises(ProviderError):direction(MODEL,state(),'LCS91',['0']*7,'-1')
    def test_Jv_independent_exact_shape_contraction(self):
        s=state();base=evaluate(MODEL,s,'LCS91');v=['.1','.2','-.1','3','0','0','0'];d=direction(MODEL,s,'LCS91',v)
        coeff=sum((F(a)*F(b) for a,b in zip(base['gradient_shape_exact'],v)),F(0))
        lo,hi=map(F,base['rate_cm3_s']);expected=sorted([lo*coeff,hi*coeff])
        self.assertLessEqual(F(d['Jv'][0][0]),expected[0]);self.assertGreaterEqual(F(d['Jv'][0][1]),expected[1])
    def test_original_provider_hash(self):
        self.assertEqual(hashlib.sha256((ROOT/'src/hh_external.py').read_bytes()).hexdigest(),'8c02df302adc895be1327cb2e55bae03ebed8ec06ee7496ff4eeda20fdcdc197')
    def test_cli_wont_overwrite_results(self):
        with tempfile.TemporaryDirectory() as t:
            inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'model':MODEL,'state':state(),'provider':'LCS91'}))
            cmd=[sys.executable,'-B',str(ROOT/'src/hh_f03_binding.py'),'--input',str(inp),'--output',str(out)]
            r=subprocess.run(cmd,capture_output=True);self.assertEqual(r.returncode,0,r.stderr)
            b=out.read_bytes();r=subprocess.run(cmd,capture_output=True);self.assertNotEqual(r.returncode,0);self.assertEqual(out.read_bytes(),b)

if __name__=='__main__':unittest.main()
