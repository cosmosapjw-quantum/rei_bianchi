"""Only HARMONIC10 tests. Closed-form oracles do not use production trig."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harmonic10',ROOT/'src/harmonic.py')
h=importlib.util.module_from_spec(spec);sys.modules[spec.name]=h;spec.loader.exec_module(h)
PI_LO=F('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679')
PI_HI=PI_LO+F(1,10**100)
SAVED={'schema':'HARMONIC10_SAVED_VALIDATION_V1','benchmarks':[],'rotation_scan':[],'native_rows':[],'nonseparable':[],'width_rows':[],'controls':[]}


def model(e=F(8,3)):return h.PhysicalAngularMap(3,2,e)
def det(window=(-1,1),arc=(0,1)):return h.FiniteDetector((h.DetectorPatch(window,arc),))
def law():return h.SecondHarmonicDensity([F(1,2)],[F(3,10)],[F(2,5)])
def response(A=None,B=None,density=None,m=None,delta=None):
    return h.harmonic_pair_response(m or model(),density or law(),A if A is not None else det(),B if B is not None else det(),azimuth_law='SECOND_HARMONIC_DECLARED',delta=delta)
def packed(b):
    return {k:str(getattr(b,k)) for k in ('lower','upper','width','width_bound','uncertainty_area')}|{'display_lower':float(b.lower),'display_upper':float(b.upper),'display_width':float(b.width),'display_width_bound':float(b.width_bound)}
def row(r):return {key:packed(r[key]) for key in h.EVENTS+('inclusive_a','inclusive_b','coincidence_assignments','coincidence_daughters','pair_energy_MeV','selected_plus_energy_MeV','selected_minus_energy_MeV')}

def oracle_sincos(t):
    """Independent decimal series at 115 digits; PI_LO/PI_HI input only."""
    with localcontext() as ctx:
        ctx.prec=115
        pi=Decimal(PI_LO.numerator)/Decimal(PI_LO.denominator)
        phase=(2*F(t))%1
        if phase>F(1,2):phase-=1
        x=2*pi*Decimal(phase.numerator)/Decimal(phase.denominator)
        st=x;ct=Decimal(1);ss=st;cs=ct
        for k in range(1,90):
            st*=-x*x/Decimal((2*k)*(2*k+1));ct*=-x*x/Decimal((2*k-1)*(2*k))
            ss+=st;cs+=ct
        return F(ss),F(cs)

def orientation_oracle(a,w=F(1,8),lam=F(3,5),kap=F(4,5)):
    sl,cl=oracle_sincos(a);sh,ch=oracle_sincos(a+w)
    return 2*w+(lam*(sh-sl)+kap*(cl-ch))/(PI_LO*2)


class HarmonicTests(unittest.TestCase):
    def assert_contains(self,b,x):self.assertLessEqual(b.lower,x);self.assertGreaterEqual(b.upper,x)
    def assert_exact(self,b,x):self.assertEqual((b.lower,b.upper),(F(x),F(x)))

    def test_01_coefficient_cone_boundary_and_sigma(self):
        d=law();self.assertEqual(d.sigma,1);self.assertEqual(d.maximum,1)
        self.assertEqual(d.b0[0]**2,d.bc[0]**2+d.bs[0]**2)
        self.assertEqual(d.value_components(F(2,3)),(F(1,2),F(3,10),F(2,5)))
        self.assertEqual(d.integrals(((-F(1),F(1)),)),(F(1),F(3,5),F(4,5)))

    def test_02_invalid_coefficient_inputs(self):
        cases=[('x',[0],[0]),([],[],[]),([1]*10,[0]*10,[0]*10),([1],[0,0],[0]),([True],[0],[0]),([float('nan')],[0],[0]),([-1],[0],[0]),([1],[2],[0]),([1,2],[0,0],[0,0]),([1,1],[1,0],[0,0]),([1,1],[0,0],[0,1]),([1],[1],[1]),(None,[0],[0])]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(h.ContractError):h.SecondHarmonicDensity(*args)

    def test_03_positive_polynomial_outside_certificate_cone(self):
        with self.assertRaises(h.ContractError):h.SecondHarmonicDensity([1,0,1],[0,F(1,2),0],[0,0,0])
        for mu in (F(-1),F(-1,3),F(0),F(1,3),F(1)):
            self.assertGreater((1+3*mu*mu)/4,0)
        SAVED['controls'].append({'case':'positive_polynomial_outside_sufficient_cone','certificate':'rejected','rho0_minus_abs_rhoc':'(1+3mu^2)/4'})

    def test_04_pi_interval_independent_decimal(self):
        p=h.pi_interval();self.assertLessEqual(p.lower,PI_LO);self.assertGreaterEqual(p.upper,PI_HI)
        self.assertLess(p.width,F(1,2**94));SAVED['pi']={'lower':str(p.lower),'upper':str(p.upper),'width':str(p.width),'oracle_lower':str(PI_LO),'oracle_upper':str(PI_HI)}

    def test_05_cardinal_exact_and_periodicity(self):
        for t,expected in [(0,(0,1)),(F(1,8),(1,0)),(F(1,4),(0,-1)),(F(3,8),(-1,0)),(F(1,2),(0,1)),(1,(0,1))]:
            pair=h.sincos_turn(t)
            for b,x in zip(pair,expected):self.assert_exact(b,x)
            self.assertEqual(pair,h.sincos_turn(F(t)+1))
            self.assertEqual(pair,h.sincos_turn(F(t)+F(1,2)))

    def test_06_noncardinal_trig_independent_decimal(self):
        for t in (F(1,13),F(3,17),F(7,19),F(9,11),F(-1,29),F(35,37)):
            for b,value in zip(h.sincos_turn(t),oracle_sincos(t)):
                self.assert_contains(b,value);self.assertLess(b.width,F(1,2**86))
        for lo,hi in [(0,1),(0,F(1,2)),(F(2,13),F(9,13))]:
            c,s=h.harmonic_integrals(F(lo),F(hi));self.assertLessEqual(c.width,F(1,2**84));self.assertLessEqual(s.width,F(1,2**84))
            if hi-lo in (1,F(1,2)):self.assert_exact(c,0);self.assert_exact(s,0)

    def test_07_signed_primitive_nonseparable(self):
        d=h.SecondHarmonicDensity([F(1,2)]*3,[F(1,2),F(-1,2),F(1,2)],[0]*3)
        for low,high in [(-1,1),(-F(2,3),F(1,4)),(0,F(1))]:
            low,high=F(low),F(high)
            self.assertEqual(d.integrals(((F(low),F(high)),)),((high-low)/2,(high**3-low**3)/6,F(0)))
        signed=h.SecondHarmonicDensity([1,1,1],[F(-1,2)]*3,[F(1,3)]*3)
        self.assertEqual(signed.integrals(((-F(1),F(1)),)),(F(2),F(-1),F(2,3)))

    def test_08_orientation_independent_17_point_scan(self):
        for j in range(17):
            a=F(j,16)%1
            r=response(det(arc=(a,F(1,8))),det(arc=((a+F(1,2))%1,F(1,8))))
            expected=orientation_oracle(a)
            self.assert_contains(r['coincidence'],expected)
            self.assertEqual(r['coincidence'].uncertainty_area,0)
            SAVED['rotation_scan'].append({'a_turns':str(F(j,16)),'display_a':j/16,'oracle':str(expected),'display_oracle':float(expected),'coincidence':packed(r['coincidence'])})

    def test_09_cardinal_orientation_closed_forms(self):
        corrections=[F(7,5),F(1,5),F(-7,5),F(-1,5)]
        for a,c in zip((0,F(1,8),F(1,4),F(3,8)),corrections):
            r=response(det(arc=(a,F(1,8))),det(arc=((a+F(1,2))%1,F(1,8))))
            self.assert_contains(r['coincidence'],F(1,4)+c/(2*PI_LO))

    def test_10_full_overlap_assignment_semantics(self):
        r=response();self.assert_exact(r['coincidence'],1)
        self.assert_exact(r['coincidence_assignments'],2);self.assert_exact(r['assignment_overlap'],1);self.assert_exact(r['coincidence_daughters'],2)
        self.assert_exact(r['pair_energy_MeV'],model().G);self.assert_exact(r['selected_plus_energy_MeV'],model().G/2)
        SAVED['controls'].append({'case':'full_overlap','events':row(r)})

    def test_11_same_halfcircle_distinguishes_events(self):
        A=det(arc=(0,F(1,2)));r=response(A,A)
        self.assert_exact(r['coincidence'],0);self.assert_exact(r['both_detectors_hit'],1)

    def test_12_nonseparable_fullpolar_oracle(self):
        d=h.SecondHarmonicDensity([F(1,2)]*3,[F(1,2),F(-1,2),F(1,2)],[0]*3)
        r=response(det(arc=(0,F(1,8))),det(arc=(F(1,2),F(1,8))),d)
        self.assert_contains(r['coincidence'],F(1,4)+1/(6*PI_LO))
        SAVED['nonseparable'].append({'case':'fullpolar','oracle':float(F(1,4)+1/(6*PI_LO)),'actual':packed(r['coincidence'])})

    def test_13_nonseparable_forward_backward_and_wrong_marginal(self):
        d=h.SecondHarmonicDensity([F(1,2)]*3,[F(1,2),F(-1,2),F(1,2)],[0]*3)
        r=response(det((0,1),(0,F(1,8))),det((-1,0),(F(1,2),F(1,8))),d)
        k=F(40,51);y=(1-k)/8+(1-k**3)/(12*PI_LO);ha=(1+k)/8+(1+k**3)/(12*PI_LO)
        for key,v in [('coincidence',y),('hit_a',ha),('hit_b',y)]:self.assert_contains(r[key],v)
        self.assertLessEqual(r['conditional_a']['lower'],y/ha);self.assertGreaterEqual(r['conditional_a']['upper'],y/ha)
        self.assertLessEqual(r['conditional_b']['lower'],1);self.assertEqual(r['conditional_b']['upper'],1)
        naive=(1-k)/8+(1-k)/(12*PI_LO)
        self.assertGreater(abs(y-naive),r['coincidence'].width)
        SAVED['nonseparable'].append({'case':'forward_backward','oracle':float(y),'naive_global_marginal':float(naive),'actual':packed(r['coincidence']),'hit_a_oracle':str(ha),'conditional_a_oracle':str(y/ha),'analytic_k':str(k)})

    def test_14_uniform_exact_inherited_manual_delta(self):
        d=h.SecondHarmonicDensity([0,F(3,2),0],[0,0,0],[0,0,0]);A=det((0,1),(F(1,7),F(1,3)));B=det((-1,0),(F(3,7),F(1,5)))
        delta=F(1,2**17)
        new=response(A,B,d,delta=delta)
        old=h._Z.azimuth_pair_response(model(),d.polar,A,B,azimuth_law='UNIFORM_DECLARED',delta=delta)
        for key in h.EVENTS+h.PARTS:self.assertEqual(new[key],old[key]);self.assertEqual(new['arithmetic_widths'][key],0)

    def test_15_zero_density_and_empty_geometry(self):
        m=model();m.preimage=lambda *args: (_ for _ in ()).throw(AssertionError('unnecessary polar solver'))
        z=h.SecondHarmonicDensity([0,0,0],[0,0,0],[0,0,0]);r=response(density=z,m=m)
        self.assert_exact(r['coincidence'],0);self.assertEqual(r['delta'],1);self.assertEqual(r['semantic_status'],'ZERO_DENSITY')
        E=h.FiniteDetector(());r=response(E,E,m=m);self.assert_exact(r['coincidence'],0);self.assertEqual(r['semantic_status'],'EMPTY_GEOMETRY')

    def test_16_invalid_law_types_delta_and_geometry_caps(self):
        for declared in ('UNIFORM_DECLARED','second',None):
            with self.assertRaises(h.ContractError):h.harmonic_pair_response(model(),law(),det(),det(),azimuth_law=declared)
        for delta in (0,F(1,2**81),2,True):
            with self.assertRaises(h.ContractError):response(delta=delta)
        with self.assertRaises(h.ContractError):h.harmonic_pair_response(model(),h.BernsteinDensity([1]),det(),det(),azimuth_law='SECOND_HARMONIC_DECLARED')
        with self.assertRaises(h.ContractError):response(A=object())
        patches=tuple(h.DetectorPatch((F(i,20),F(i+1,20)),(0,1)) for i in range(8))
        with self.assertRaises(h.ContractError):response(h.FiniteDetector(patches),det((F(1,2),F(3,4))))
        with self.assertRaises(h.ContractError):h.FiniteDetector((h.DetectorPatch((-1,1),(0,1)),)*9)

    def test_17_wrap_overlap_union_and_halfturn(self):
        A=det(arc=(F(15,16),F(1,8)));B=det(arc=(F(7,16),F(1,8)))
        r=response(A,B);self.assert_contains(r['coincidence'],orientation_oracle(F(15,16)))
        p=h.DetectorPatch((-1,1),(0,F(1,8)));q=h.DetectorPatch((-1,1),(F(1,16),F(1,8)))
        overlapped=response(h.FiniteDetector((p,p,q)),det(arc=(F(1,2),F(3,16))))
        merged=response(det(arc=(0,F(3,16))),det(arc=(F(1,2),F(3,16))))
        for key in h.EVENTS:
            self.assertLessEqual(max(overlapped[key].lower,merged[key].lower),min(overlapped[key].upper,merged[key].upper))
        self.assert_contains(overlapped['coincidence'],orientation_oracle(0,w=F(3,16)))
        self.assert_contains(merged['coincidence'],orientation_oracle(0,w=F(3,16)))
        shifted=response(det(arc=((A.patches[0].arc[0]+F(1,2))%1,F(1,8))),det(arc=((B.patches[0].arc[0]+F(1,2))%1,F(1,8))))
        for key in h.EVENTS:self.assertEqual(r[key],shifted[key])

    def test_18_rotation_covariance_exact_rational_transform(self):
        A=det((0,1),(0,F(1,8)));B=det((-1,0),(F(1,2),F(1,8)))
        d=law();rot=h.SecondHarmonicDensity(d.b0,d.bs,tuple(-v for v in d.bc))
        r=response(det((0,1),(F(1,8),F(1,8))),det((-1,0),(F(5,8),F(1,8))),d)
        s=response(A,B,rot)
        for key in h.EVENTS:self.assertEqual(r[key],s[key])
        # Rotate both geometry and beam law; inverse coefficient transform.
        beam=h.SecondHarmonicDensity(d.b0,tuple(-v for v in d.bs),d.bc)
        both=response(det((0,1),(F(1,8),F(1,8))),det((-1,0),(F(5,8),F(1,8))),beam)
        base=response(A,B,d)
        for key in h.EVENTS:self.assertEqual(both[key],base[key])

    def test_19_reflection_partner_exchange_energy_scaling(self):
        A=det((0,1),(0,F(1,8)));B=det((-1,0),(F(1,2),F(1,8)));r=response(A,B);s=response(B,A)
        self.assertEqual(r['coincidence'],s['coincidence']);self.assertEqual(r['hit_a'],s['hit_b'])
        self.assertEqual(r['pair_energy_MeV'],r['coincidence'].scaled(model().G))
        self.assertEqual(r['selected_plus_energy_MeV'],r['selected_minus_energy_MeV'])
        self.assertEqual(r['coincidence_daughters'],r['coincidence'].scaled(2))
        for key in ('inclusive_a','inclusive_b','coincidence_assignments'):
            self.assertLessEqual(r[key].width,r[key].width_bound)
        d=law();scaled=h.SecondHarmonicDensity(tuple(3*x for x in d.b0),tuple(3*x for x in d.bc),tuple(3*x for x in d.bs))
        rr=response(A,B,scaled,delta=r['delta'])
        for key in h.EVENTS:self.assertEqual((rr[key].lower,rr[key].upper),(3*r[key].lower,3*r[key].upper))

    def test_20_manual_and_default_width_budgets(self):
        A=det((0,F(4,5)),(0,F(1,3)));B=det((-F(4,5),0),(F(1,2),F(1,3)))
        self.assert_exact(response(A,B,delta=F(1,16))['coincidence'],0)
        A=det((0,1),(0,F(1,3)));B=det((-1,0),(F(1,2),F(1,3)))
        for delta in (None,F(1,16)):
            r=response(A,B,delta=delta)
            for key in h.EVENTS:
                self.assertLessEqual(r[key].width,r[key].width_bound);self.assertLessEqual(r[key].width_bound,r['event_global_width_bound'])
                self.assertLessEqual(r['arithmetic_widths'][key],4*r['density_sigma']*r['strip_count']*F(1,2**84))
                if delta is None:self.assertLess(r[key].width,F(1,2**40))
            SAVED['width_rows'].append({'case':'default' if delta is None else 'manual_1_16','delta':str(r['delta']),'actual_width':float(r['coincidence'].width),'polar_bound':float(r['polar_width_bounds']['coincidence']),'arithmetic_bound':float(r['arithmetic_widths']['coincidence']),'width_bound':float(r['coincidence'].width_bound),'default_epsilon':2**-40})
        self.assertGreater(SAVED['width_rows'][-1]['actual_width'],2**-40)

    def test_21_conditional_unresolved_null(self):
        z=h.MeasureBounds(F(0),F(1,4),F(1,2),F(1,4))
        self.assertEqual(h.conditional_ratio(z,z)['status'],'UNRESOLVED_DENOMINATOR')
        self.assertIsNone(h.conditional_ratio(z,z)['lower'])
        E=h.FiniteDetector(());self.assertEqual(response(E,E)['conditional_a']['status'],'UNDEFINED_ZERO_DENOMINATOR')
        r=response(det((0,F(1,100)),(0,F(1,8))),det(),delta=1)
        self.assertEqual(r['conditional_a']['status'],'UNRESOLVED_DENOMINATOR')

    def test_22_fold_stopped_increasing_geometry(self):
        for energy,topology in [(F(6,5),'fold'),(F(3,2),'stopped'),(F(8,3),'increasing')]:
            m=model(energy);r=response(det((F(1,5),F(4,5)),(F(7,8),F(1,4))),det((0,1),(F(3,8),F(1,4))),m=m)
            self.assertEqual(m.topology,topology)
            self.assertGreaterEqual(r['coincidence'].lower,0);self.assertLessEqual(r['coincidence'].upper,1)
            if topology=='stopped':
                with self.assertRaises(h._Z._K.StoppedDirectionError):m.compare(-1,0)
            SAVED['controls'].append({'case':topology,'operations':r['operation_delta'],'coincidence':packed(r['coincidence'])})

    def test_23_degree8_eight_window_stress(self):
        class Traced(h.PhysicalAngularMap):
            def _bracket(self,*args):
                before=self.operations['boundary_bisections'];out=super()._bracket(*args);self.steps.append(self.operations['boundary_bisections']-before);return out
        m=Traced(3,2,F(8,3));m.steps=[]
        patches=[h.DetectorPatch((F(-4,5)+F(i,5),F(-7,10)+F(i,5)),(F(i,64),F(1,8))) for i in range(8)]
        d=h.SecondHarmonicDensity([F(1,2)]*9,[F((-1)**i,2) for i in range(9)],[0]*9)
        self.assertEqual(d.power[1],(F(0),)*8+(F(1,2),))
        r=response(h.FiniteDetector(tuple(patches[:4])),h.FiniteDetector(tuple(patches[4:])),d,m)
        self.assertEqual(r['unique_window_count'],8);self.assertLessEqual(r['strip_count'],65)
        self.assertGreater(m.operations['boundary_bisections'],0);self.assertLessEqual(max(m.steps),52)
        self.assertGreaterEqual(r['delta'],F(1,1440*2**40))
        SAVED['stress']={'operations':dict(m.operations),'root_boundary_iterations':m.steps,'max_boundary_iterations':max(m.steps),'delta':str(r['delta']),'strip_count':r['strip_count'],'unique_windows':r['unique_window_count'],'coincidence':packed(r['coincidence'])}
        SAVED['width_rows'].append({'case':'degree8_N8','delta':str(r['delta']),'actual_width':float(r['coincidence'].width),'polar_bound':float(r['polar_width_bounds']['coincidence']),'arithmetic_bound':float(r['arithmetic_widths']['coincidence']),'width_bound':float(r['coincidence'].width_bound),'default_epsilon':float(d.sigma/2**40)})

    def test_24_native_NIST_three_energy_rows(self):
        source=ROOT.parents[0]/'continuation_photon_20261027/sources/NIST_CODATA_2022_allascii.txt'
        raw=source.read_bytes();expected='77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67'
        self.assertEqual(hashlib.sha256(raw).hexdigest(),expected)
        def field(label):return F(next(line for line in raw.decode().splitlines() if line.startswith(label))[60:85].replace(' ',''))
        A=field('alpha particle mass energy equivalent in MeV');M=field('deuteron mass energy equivalent in MeV')
        self.assertEqual(A,F('3727.3794118'));self.assertEqual(M,F('1875.61294500'))
        d=h.SecondHarmonicDensity([0,F(3,2),0],[0,F(9,10),0],[0,F(6,5),0])
        for energy in (213,258,330):
            m=h.PhysicalAngularMap(A,M,energy);r=response(det((-1,F(-1,2)),(0,F(1,8))),det((F(1,2),1),(F(1,2),F(1,8))),d,m)
            self.assertEqual(r['pair_energy_MeV'],r['coincidence'].scaled(m.G));self.assertEqual(r['coincidence_daughters'],r['coincidence'].scaled(2))
            for key in h.EVENTS:self.assertLess(r[key].width,d.sigma/2**40)
            SAVED['native_rows'].append({'energy_MeV':energy,'A_MeV':str(A),'M_MeV':str(M),'G_MeV':str(m.G),'sigma':str(d.sigma),'source_sha256':expected,'operation_delta':r['operation_delta'],**row(r)})

    def test_25_strip_provenance_and_no_component_clipping(self):
        d=h.SecondHarmonicDensity([1],[F(-3,5)],[F(4,5)])
        r=response(det(arc=(F(1,8),F(1,8))),det(arc=(F(5,8),F(1,8))),d)
        self.assert_contains(r['coincidence'],2*orientation_oracle(F(1,8),lam=F(-3,5),kap=F(4,5)))
        self.assertEqual(sum((s['interval'][1]-s['interval'][0] for s in r['strips']),F(0)),1)
        SAVED['strip_provenance']=[{'interval':list(map(str,s['interval'])),'sets':{key:{'inner':[[str(x) for x in iv] for iv in v.inner],'outer':[[str(x) for x in iv] for iv in v.outer]} for key,v in s['sets'].items()}} for s in r['strips']]

if __name__=='__main__':unittest.main()
