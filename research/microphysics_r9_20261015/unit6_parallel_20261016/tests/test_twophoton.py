"""Focused acceptance checks, independent scipy.quad references, no reruns."""
import csv
import ctypes as ct
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest
import scipy
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('twophoton_driver',ROOT/'code/twophoton_driver.py')
driver=importlib.util.module_from_spec(spec); spec.loader.exec_module(driver)
OUT=ROOT/'results/laneB'; RAW={}

def rows(name):
    return driver.read_csv(OUT/name)

def close(test,a,b,relative=1e-8,floor=1e-14):
    test.assertLessEqual(abs(a-b),max(floor,relative*abs(b)),(a,b))

def python_g(y):
    w=y*(1-y)
    return w*(1-(4*w)**.8)+.88*4**.8*w**2.33

def python_sigma(e):
    x=e/3.107
    return 1e-22*62.45*(x-1)**2*x**(4.895/2-5.5)*(1+math.sqrt(x/15.01))**(-4.895)

class TwoPhotonAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k=driver.load_kernel(); cls.summary=json.loads((OUT/'twophoton_summary.json').read_text())
        cls.contract=json.loads((ROOT/'spec/TWOPHOTON_CONTRACT.json').read_text())
        cls.mixtures=json.loads((ROOT/'inputs/laneB/cascade_mixture.json').read_text())['mixture_moments']

    def test_shape(self):
        k=self.k; I=.08144613055216544
        close(self,k.tp_normalizer(),I,1e-11,0)
        raw,error=quad(python_g,0,1,epsabs=1e-13,epsrel=1e-12)
        mean,meanerr=quad(lambda y:y*python_g(y)/I,0,1,epsabs=1e-13,epsrel=1e-12)
        RAW['independent_shape_quad']={'g_integral':raw,'g_error':error,'mean_y':mean,'mean_error':meanerr}
        close(self,raw/I,1); close(self,mean,.5)
        for i in range(1001):
            y=i/1000; self.assertGreaterEqual(k.tp_f(y),0)
            self.assertLessEqual(abs(k.tp_f(y)-k.tp_f(1-y)),2e-13)
        self.assertEqual(k.tp_f(-.1),0); self.assertEqual(k.tp_f(1.1),0)
        self.assertEqual(k.tp_f(0),0); self.assertEqual(k.tp_f(1),0)
        for r in self.summary['quadrature']:
            if r['nodes']==256:
                close(self,r['f_normalization'],1); close(self,r['f_mean_y'],.5)
        q={r['nodes']:r for r in self.summary['quadrature']}
        for key in ['f_normalization','f_mean_y']: close(self,q[128][key],q[256][key])

    def test_actual_inputs_and_32_mixture_closure(self):
        for info in self.summary['input_manifest'].values():
            self.assertEqual(hashlib.sha256((ROOT/info['file']).read_bytes()).hexdigest(),info['sha256'])
        moments=rows('twophoton_moments.csv'); self.assertEqual(len(moments),32)
        self.assertEqual(len(self.summary['species']),8)
        original={(r['species'],r['n']):r for r in self.mixtures}
        lines=rows('twophoton_E1_lines.csv')
        for r in moments:
            s=r['species']; n=int(r['n']); o=original[s,n]
            p=float(r['P_2s_saved']); d=float(r['Delta_eV'])
            self.assertLessEqual(abs(p-float(r['P_2s_cascade'])),1e-12)
            self.assertLessEqual(abs(o['terminal_1s_probability']+p-1),1e-12)
            close(self,float(r['reservoir_energy_eV']),p*d,1e-11)
            close(self,float(r['N2_infinity']),2*p)
            close(self,float(r['U2_infinity_eV']),p*d)
            close(self,float(r['E1_energy_eV'])+float(r['U2_infinity_eV']),o['initial_excitation_eV'])
            subset=[l for l in lines if l['species']==s and int(l['n'])==n]
            close(self,sum(float(l['photon_count']) for l in subset),o['E1_photon_count'],1e-11)
            close(self,sum(float(l['energy_eV']) for l in subset),o['E1_energy_eV'],1e-11)
        # Every retained bin/band/response compares 128 against final 256.
        for file,keys,fields in [
            ('twophoton_continuum.csv',['species','n','E_lo_eV','E_hi_eV'],['photon_count','energy_eV']),
            ('twophoton_bands.csv',['species','n','band'],['photon_count','energy_eV']),
            ('twophoton_LiI_response.csv',['species','n','band'],['Gamma_over_J_m2','H_over_J_J_m2','Abs_over_J_J_m2'])]:
            data=rows(file); final={tuple(r[k] for k in keys):r for r in data if r['quadrature_nodes']=='256'}
            for r in data:
                if r['quadrature_nodes']!='128': continue
                ref=final[tuple(r[k] for k in keys)]
                for f in fields:
                    floor=1e-35 if f=='Gamma_over_J_m2' else 1e-53 if f.endswith('_J_m2') else 1e-14
                    close(self,float(r[f]),float(ref[f]),1e-8,floor)
        for r in rows('twophoton_bands.csv'):
            if r['quadrature_nodes']=='256' and r['band']=='photo_uncovered':
                self.assertEqual(float(r['photon_count'])>0,r['species']=='LiIII_infinite_mass')

    def test_exact_time_closure(self):
        original={(r['species'],r['n']):r for r in self.mixtures}
        sp={r['species']:r for r in self.summary['species']}
        data=rows('twophoton_time.csv'); self.assertEqual(len(data),160)
        for r in data:
            o=original[r['species'],int(r['n'])]; p=o['terminal_2s_probability']
            d=sp[r['species']]['Delta_eV']; a=sp[r['species']]['A_s_inverse']
            remain=float(r['remaining_2s_probability']); decay=float(r['decayed_probability'])
            close(self,remain+decay,p,1e-11)
            close(self,o['E1_energy_eV']+float(r['U2_eV'])+float(r['remaining_energy_eV']),o['initial_excitation_eV'],1e-11)
            close(self,float(r['N2']),2*decay,1e-11)
            close(self,float(r['instantaneous_photon_rate_s_inverse']),2*a*remain,1e-11)
            close(self,float(r['instantaneous_energy_rate_eV_s']),d*a*remain,1e-11)
            if r['asymptotic']=='True':
                self.assertEqual(r['elapsed_seconds'],''); self.assertEqual(r['x'],'')
                self.assertEqual(remain,0); close(self,float(r['ground_probability']),1,0,1e-12)
            else:
                x=float(r['x']); close(self,a*float(r['elapsed_seconds']),x,1e-11)
                close(self,remain,p*math.exp(-x),1e-11)
                close(self,decay,p*(-math.expm1(-x)),1e-11)

    def test_Li_coverage_independent_response(self):
        self.assertEqual(self.k.tp_sigma(5),0)
        self.assertGreater(self.k.tp_sigma(5.392),0)
        self.assertTrue(math.isnan(self.k.tp_sigma(64.4)))
        self.assertTrue(math.isnan(self.k.tp_integrate(5.392,65,92,1,2,256)))
        data=rows('twophoton_LiI_response.csv'); refs={}
        for sp in self.summary['species']:
            delta=sp['Delta_eV']; hi=min(delta,64.39); result={}
            # One independent quadrature per covered response moment/species.
            for kind,unit in [(2,'Gamma_over_J_m2'),(3,'H_over_J_J_m2'),(4,'Abs_over_J_J_m2')]:
                def fun(e):
                    v=2*python_g(e/delta)/.08144613055216544/delta*python_sigma(e)
                    if kind==3: v*=driver.EV_J*(e-5.392)
                    if kind==4: v*=driver.EV_J*e
                    return v
                scale=1e-22 if kind==2 else 1e-40
                value,error=quad(lambda e:fun(e)/scale,5.392,hi,epsabs=1e-12,epsrel=1e-12)
                result[unit]={'per_P':value*scale,'quad_error':error*scale}
            refs[sp['species']]=result
        RAW['independent_Li_covered_quad']=refs
        original={(r['species'],r['n']):r for r in self.mixtures}
        for r in data:
            if r['quadrature_nodes']!='256': continue
            g=float(r['Gamma_over_J_m2']); h=float(r['H_over_J_J_m2']); a=float(r['Abs_over_J_J_m2'])
            self.assertGreater(g,0); self.assertGreater(h,0)
            close(self,a,5.392*driver.EV_J*g+h,1e-11,1e-53)
            if r['band']=='covered_total':
                p=original[r['species'],int(r['n'])]['terminal_2s_probability']
                for f in ['Gamma_over_J_m2','H_over_J_J_m2','Abs_over_J_J_m2']:
                    close(self,float(r[f]),p*refs[r['species']][f]['per_P'],1e-8,1e-35 if f=='Gamma_over_J_m2' else 1e-53)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TwoPhotonAcceptance)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    RAW.update(scipy_version=scipy.__version__,tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful())
    (OUT/'twophoton_test_results.json').write_text(json.dumps(RAW,indent=2,allow_nan=False)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
