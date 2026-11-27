"""New azimuth-specific tests; old suites are never imported or executed."""
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('azimuth09',ROOT/'src/azimuth.py')
a=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=a
spec.loader.exec_module(a)
SAVED={'schema':'AZIMUTH09_SAVED_VALIDATION_V1','benchmarks':[],'rotation_scan':[], 'native_rows':[], 'controls':[], 'bounds_comparison':[], 'closure':[]}
D=a.BernsteinDensity([F(1,2)])


def model(e=F(8,3)):return a.PhysicalAngularMap(3,2,e)
def det(window=(-1,1),arc=(0,1)):return a.FiniteDetector((a.DetectorPatch(window,arc),))
def response(A=None,B=None,density=D,m=None,delta=None):
    return a.azimuth_pair_response(m or model(),density,A or det(),B or det(),azimuth_law='UNIFORM_DECLARED',delta=delta)
def exact(bound,value):return bound.lower<=value<=bound.upper

def packed(bound):
    return {key:str(getattr(bound,key)) for key in ('lower','upper','width','width_bound','uncertainty_area')} | {'display_lower':float(bound.lower),'display_upper':float(bound.upper),'display_width':float(bound.width)}
def measure_row(r):return {key:packed(r[key]) for key in a.EVENTS+('inclusive_a','inclusive_b','coincidence_assignments','coincidence_daughters','pair_energy_MeV','selected_plus_energy_MeV','selected_minus_energy_MeV')}


def direct_grid(A,B,polar_endpoints=(-1,1),k=F(40,51)):
    """Independent exact cell enumeration for full/forward/backward windows.

    Analytic sign F(mu)=sign(e+G*r*mu), r=3/5, gives boundary -k.
    No production set operation, preimage, density integral or response is used.
    """
    def circle_contains(p,t):
        start,width=p.arc
        return width==1 or (t-start)%1<width
    def polar_contains(window,mu):
        if window==(-1,1):return True
        if window==(0,1):return mu>-k
        if window==(-1,0):return mu<-k
        raise AssertionError('oracle only supports analytic half/full polar windows')
    def accepts(detector,mu,t):return any(polar_contains(p.window,mu) and circle_contains(p,t) for p in detector.patches if p.active)
    ts={F(0),F(1)}
    for detector in (A,B):
        for p in detector.patches:
            for t in (p.arc[0],(p.arc[0]+p.arc[1])%1):ts.update((t,(t+F(1,2))%1))
    mus=sorted(set(map(F,polar_endpoints)))
    out={key:F(0) for key in a.EVENTS+('inclusive_a','inclusive_b','coincidence_assignments')}
    ts=sorted(ts)
    for ml,mh in zip(mus,mus[1:]):
        mu=(ml+mh)/2
        for tl,th in zip(ts,ts[1:]):
            t=(tl+th)/2
            ap,am=accepts(A,mu,t),accepts(A,-mu,(t+F(1,2))%1)
            bp,bm=accepts(B,mu,t),accepts(B,-mu,(t+F(1,2))%1)
            q1,q2=ap and bm,bp and am
            flags={'coincidence':q1 or q2,'hit_a':ap or am,'hit_b':bp or bm,'double_a':ap and am,'double_b':bp and bm,'both_detectors_hit':(ap or am) and (bp or bm),'assignment_overlap':q1 and q2,'inclusive_a':int(ap)+int(am),'inclusive_b':int(bp)+int(bm),'coincidence_assignments':int(q1)+int(q2)}
            for key,flag in flags.items():out[key]+=F(flag)*(mh-ml)*(th-tl)/2
    return out


class AzimuthTests(unittest.TestCase):
    def assert_exact(self,b,value):
        self.assertEqual((b.lower,b.upper),(F(value),F(value)))
    def assert_oracle(self,r,oracle):
        for key,val in oracle.items():self.assertTrue(exact(r[key],val),(key,r[key],val))

    def test_01_arc_seam_empty_full_contacts(self):
        self.assertEqual(a.turn_arc(F(7,8),F(1,4)),((F(0),F(1,8)),(F(7,8),F(1))))
        self.assertEqual(a.turn_arc(F(2,3),0),())
        self.assertEqual(a.turn_arc(F(2,3),1),((F(0),F(1)),))
        self.assertEqual(a.shifted(a.turn_arc(F(7,8),F(1,4))),a.turn_arc(F(3,8),F(1,4)))
        self.assertEqual(a.shifted(((F(0),F(1,4)),(F(1,4),F(1,2)))),((F(1,2),F(1)),))

    def test_02_opposite_quarters_exact_grid(self):
        A,B=det(arc=(0,F(1,4))),det(arc=(F(1,2),F(1,4)))
        r=response(A,B);self.assert_oracle(r,direct_grid(A,B))
        for key in ('coincidence','hit_a','hit_b','inclusive_a','inclusive_b','coincidence_assignments'):self.assert_exact(r[key],F(1,2))
        SAVED['controls'].extend([{'name':'omit_halfturn','actual':str(r['coincidence'].lower),'counterfactual':str(F(0)),'diagnostic_match':False},{'name':'independent_marginal_product','actual':str(r['coincidence'].lower),'counterfactual':str(2*F(1,4)*F(1,4)),'hit_product':str(r['hit_a'].lower*r['hit_b'].lower),'diagnostic_match':False}])

    def test_03_full_overlap_assignment_or(self):
        r=response();self.assert_exact(r['coincidence'],1)
        for key in ('coincidence_assignments','inclusive_a','inclusive_b','coincidence_daughters'):self.assert_exact(r[key],2)
        for key in ('assignment_overlap','hit_a','hit_b','double_a','double_b'):self.assert_exact(r[key],1)
        SAVED['controls'].append({'name':'sum_assignments_instead_of_OR','actual':str(r['coincidence'].lower),'counterfactual':str(r['coincidence_assignments'].lower),'diagnostic_match':False})
        SAVED['closure'].append({'case':'full_overlap',**measure_row(r)})

    def test_04_same_halfcircle_same_daughter(self):
        A=det(arc=(0,F(1,2)));r=response(A,A)
        self.assert_oracle(r,direct_grid(A,A));self.assert_exact(r['coincidence'],0);self.assert_exact(r['both_detectors_hit'],1)
        SAVED['controls'].append({'name':'hitA_intersect_hitB_as_distinct_C','actual':str(r['coincidence'].lower),'counterfactual':str(r['both_detectors_hit'].lower),'diagnostic_match':False})

    def test_05_wrapped_opposite_quarters(self):
        A,B=det(arc=(F(7,8),F(1,4))),det(arc=(F(3,8),F(1,4)))
        self.assert_oracle(response(A,B),direct_grid(A,B));self.assert_exact(response(A,B)['coincidence'],F(1,2))

    def test_06_mixed_polar_independent_analytic_oracle(self):
        A,B=det((0,1),(0,F(1,4))),det((-1,0),(F(1,2),F(1,4)))
        r=response(A,B);self.assert_oracle(r,direct_grid(A,B,(-1,-F(40,51),F(40,51),1)))
        for key,value in {'coincidence':F(11,204),'hit_a':F(91,204),'hit_b':F(11,204),'pair_energy_MeV':F(11,36),'selected_plus_energy_MeV':F(11,72),'selected_minus_energy_MeV':F(11,72)}.items():self.assertTrue(exact(r[key],value),key)
        for key,value in [('conditional_a',F(11,91)),('conditional_b',F(1))]:self.assertLessEqual(r[key]['lower'],value);self.assertGreaterEqual(r[key]['upper'],value)
        SAVED['closure'].append({'case':'mixed_polar_analytic',**measure_row(r)})

    def test_07_fullazimuth_inherited_same_manual_delta(self):
        m=model();density=a.BernsteinDensity([0,F(3,2),0]);delta=F(1,2**18)
        old=a._K.physical_pair_response(m,density,(-1,0),(0,1),delta)
        new=response(det((-1,0)),det((0,1)),density,m,delta)
        for key in ('coincidence','hit_a','hit_b','inclusive_a','inclusive_b','pair_energy_MeV'):
            self.assertEqual((old[key].lower,old[key].upper,old[key].width_bound),(new[key].lower,new[key].upper,new[key].width_bound))

    def test_08_duplicate_overlap_union_invariance(self):
        p=a.DetectorPatch((-1,1),(0,F(1,3)));q=a.DetectorPatch((-1,1),(F(1,6),F(1,3)))
        A=a.FiniteDetector((p,p,q));B=det(arc=(F(1,2),F(1,2)))
        r=response(A,B);expected=response(det(arc=(0,F(1,2))),B)
        for key in a.EVENTS+('inclusive_a','coincidence_assignments'):self.assertEqual(r[key],expected[key])
        self.assertEqual(r['unique_window_count'],1);self.assertEqual(r['patch_count'],4)

    def test_09_overlapping_polar_disjoint_sectors(self):
        A=a.FiniteDetector((a.DetectorPatch((-1,F(1,2)),(0,F(1,4))),a.DetectorPatch((0,1),(F(1,2),F(1,4)))))
        r=response(A,det());self.assertEqual(r['unique_window_count'],3)
        self.assertLessEqual(r['hit_a'].upper,1)
        self.assertTrue(exact(r['coincidence'],r['hit_a'].lower))

    def test_10_rational_rotation_scan_triangular_oracle(self):
        A=det(arc=(0,F(1,4)))
        for j in range(17):
            offset=F(j,16);B=det(arc=(offset%1,F(1,4)));r=response(A,B)
            # Two assignment bands; circular distance to the opposite sector.
            distance=min((offset-F(1,2))%1,(F(1,2)-offset)%1)
            expected=2*max(F(0),F(1,4)-distance)
            self.assert_exact(r['coincidence'],expected);self.assert_oracle(r,direct_grid(A,B))
            rotation=F(5,13)
            rotated=response(det(arc=(rotation,F(1,4))),det(arc=((offset+rotation)%1,F(1,4))))
            for key in a.EVENTS:self.assertEqual(r[key],rotated[key])
            SAVED['rotation_scan'].append({'offset':str(offset),'display_offset':float(offset),'expected':str(expected),'display_expected':float(expected),'coincidence':packed(r['coincidence'])})

    def test_11_detector_swap_and_partner_exchange(self):
        A,B=det((0,1),(F(1,7),F(1,3))),det((-1,0),(F(3,7),F(1,5)))
        r,s=response(A,B),response(B,A)
        self.assertEqual(r['coincidence'],s['coincidence']);self.assertEqual(r['hit_a'],s['hit_b'])
        self.assertEqual(r['selected_plus_energy_MeV'],r['selected_minus_energy_MeV'])
        # Label exchange maps every strip membership by mu reflection and t halfturn.
        h=response(det((0,1),((F(1,7)+F(1,2))%1,F(1,3))),det((-1,0),((F(3,7)+F(1,2))%1,F(1,5))))
        for key in a.EVENTS:self.assertEqual(r[key],h[key])

    def test_12_empty_full_singleton_zero_no_preimage(self):
        m=model()
        def forbidden(*args):raise AssertionError('preimage called on empty geometry')
        m.preimage=forbidden
        E=a.FiniteDetector((a.DetectorPatch((0,0),(0,1)),a.DetectorPatch((-1,1),(0,0))))
        r=response(E,E,m=m);self.assertEqual(r['semantic_status'],'EMPTY_GEOMETRY');self.assert_exact(r['coincidence'],0)
        self.assertEqual(r['preimages'],{});self.assertEqual(r['strip_count'],0)

    def test_13_zero_density_validates_and_shortcuts(self):
        m=model();m.preimage=lambda *args: (_ for _ in ()).throw(AssertionError('zero-density preimage'))
        r=response(density=a.BernsteinDensity([0,0,0]),m=m)
        self.assertEqual(r['semantic_status'],'ZERO_DENSITY');self.assert_exact(r['coincidence'],0)
        with self.assertRaises(a.ContractError):response(density=a.BernsteinDensity([0]),m=m,delta=0)
        with self.assertRaises(a.ContractError):a.azimuth_pair_response(m,a.BernsteinDensity([0]),det(),det(),azimuth_law='UNDECLARED')

    def test_14_invalid_arc_window_shapes_scalars(self):
        for start,width in [(-1,0),(1,1),(0,-1),(0,2),(True,0),(0,float('nan')),(float('inf'),1)]:
            with self.subTest(start=start,width=width):
                with self.assertRaises(a.ContractError):a.turn_arc(start,width)
        for window,arc in [((1,-1),(0,1)),((0,2),(0,0)),((False,1),(0,1)),((0,1),(0,)),((0,1),None)]:
            with self.assertRaises(a.ContractError):a.DetectorPatch(window,arc)
        with self.assertRaises(a.ContractError):a.FiniteDetector((object(),))

    def test_15_odd_density_law_domain_atomic_guards(self):
        with self.assertRaises(a.ContractError):response(density=a.BernsteinDensity([1,2]))
        with self.assertRaises(TypeError):a.azimuth_pair_response(model(),D,det(),det())
        for law in (None,'uniform','UNIFORM'):
            with self.assertRaises(a.ContractError):a.azimuth_pair_response(model(),D,det(),det(),azimuth_law=law)
        for args in [(0,2,3),(4,2,3),(3,2,F(7,6)),(3,2,F(1,2)),(True,2,3)]:
            with self.assertRaises(a.ContractError):a.PhysicalAngularMap(*args)
        with self.assertRaises(a.ContractError):a.PhysicalAngularMap(3,2,3,measure_kind='ATOMIC')
        with self.assertRaises(a.ContractError):response(delta=F(1,2**81))

    def test_16_patch_window_caps_and_precompute_once(self):
        p=a.DetectorPatch((-1,1),(0,1))
        with self.assertRaises(a.ContractError):a.FiniteDetector((p,)*9)
        A=a.FiniteDetector(tuple(a.DetectorPatch((F(i,20),F(i+1,20)),(0,1)) for i in range(8)))
        B=det((F(1,2),F(3,4)))
        with self.assertRaises(a.ContractError):response(A,B)
        m=model();calls=[];old=m.preimage
        def recorded(window,delta):calls.append(window);return old(window,delta)
        m.preimage=recorded;r=response(a.FiniteDetector((p,)*8),a.FiniteDetector((p,)*8),m=m)
        self.assertEqual(len(calls),1);self.assertEqual(r['patch_count'],16)

    def test_17_default_and_manual_width_guarantees(self):
        A,B=det((0,F(4,5)),(0,F(1,3))),det((-F(4,5),0),(F(1,2),F(1,3)))
        for delta in (None,F(1,16)):
            r=response(A,B,delta=delta)
            for key in a.EVENTS:
                self.assertLessEqual(r[key].width,r[key].width_bound);self.assertLessEqual(r[key].width_bound,r['event_global_width_bound'])
                if delta is None:self.assertLessEqual(r[key].width,D.sigma/F(2**40))
            for key in ('inclusive_a','inclusive_b','coincidence_assignments'):self.assertLessEqual(r[key].width_bound,2*r['event_global_width_bound'])
            self.assertEqual(r['coincidence_daughters'].width_bound,2*r['coincidence'].width_bound)
            self.assertEqual(r['pair_energy_MeV'].width_bound,model().G*r['coincidence'].width_bound)
            if delta:self.assertEqual(r['delta'],delta)
            SAVED['bounds_comparison'].append({'kind':'default' if delta is None else 'manual_1_16','delta':str(r['delta']),**measure_row(r)})

    def test_18_conditional_zero_unresolved_positive(self):
        E=a.FiniteDetector(());r=response(E,E);self.assertEqual(r['conditional_a']['status'],'UNDEFINED_ZERO_DENOMINATOR');self.assertIsNone(r['conditional_a']['lower'])
        z=a.MeasureBounds(F(0),F(1,4),F(1,2),F(1,4))
        c=a.conditional_ratio(z,z);self.assertEqual(c['status'],'UNRESOLVED_DENOMINATOR');self.assertIsNone(c['upper'])
        A=det((0,F(1,100)),(0,F(1,4)));r=response(A,det(),delta=1)
        self.assertEqual(r['conditional_a']['status'],'UNRESOLVED_DENOMINATOR')
        self.assertEqual(response()['conditional_a']['status'],'CERTIFIED_ENCLOSURE')

    def test_19_fold_stopped_and_direct_lorentz_geometry(self):
        for e,topology in [(F(6,5),'fold'),(F(5,4),'fold'),(F(3,2),'stopped')]:
            m=model(e);r=response(det((F(1,5),F(4,5)),(F(7,8),F(1,4))),det((0,1),(F(3,8),F(1,4))),m=m)
            self.assertEqual(m.topology,topology)
            for strip in r['strips']:
                t=float(strip['midpoint'])
                for mu in [F(-9,10),F(-1,3),F(0),F(2,3),F(9,10)]:
                    # Independent floating direct Lorentz momentum, away from boundaries.
                    s=float(m.s);qstar=math.sqrt(float(m.H))/2;gamma=float(m.G)/math.sqrt(s);beta=float(m.e/m.G)
                    qz=gamma*(qstar*float(mu)+beta*math.sqrt(s)/2);qt=qstar*math.sqrt(1-float(mu)**2)
                    nu=qz/math.hypot(qz,qt)
                    self.assertEqual(m.compare(mu,0),(nu>0)-(nu<0))
                    x=qt*math.cos(2*math.pi*t);y=qt*math.sin(2*math.pi*t)
                    self.assertAlmostEqual(math.remainder(math.atan2(-y,-x)-math.atan2(y,x)-math.pi,2*math.pi),0,places=12)
            if topology=='stopped':
                with self.assertRaises(a._K.StoppedDirectionError):m.compare(-1,0)
                self.assertGreaterEqual(r['coincidence'].lower,0)

    def test_20_degree8_eight_windows_max50_boundary_iterations(self):
        class Traced(a.PhysicalAngularMap):
            def _bracket(self,*args):
                before=self.operations['boundary_bisections'];out=super()._bracket(*args)
                self.steps.append(self.operations['boundary_bisections']-before);return out
        m=Traced(3,2,F(5,4));m.steps=[]
        windows=[(F(i,10),F(i+1,10)) for i in range(8)]
        A=a.FiniteDetector(tuple(a.DetectorPatch(w,(F(i,11),F(1,5))) for i,w in enumerate(windows)))
        density=a.BernsteinDensity([0,0,0,0,1,0,0,0,0]);r=response(A,det(windows[0]),density,m)
        self.assertEqual(r['unique_window_count'],8);self.assertLessEqual(max(m.steps),50)
        self.assertEqual(r['delta'],density.sigma/(80*density.maximum*2**40))
        SAVED['operation_counts']={'degree8':dict(m.operations),'root_boundary_iterations':m.steps,'max_boundary_iterations':max(m.steps),'unique_windows':8,'strips':r['strip_count']}

    def test_21_native_source_three_energy_rows(self):
        inputs=json.loads((ROOT/'INPUTS.json').read_text());entry=inputs['native_mass_source'];source=ROOT.parents[2]/entry['path']
        raw=source.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),entry['sha256'])
        text=raw.decode()
        def field(label):
            row=next(line for line in text.splitlines() if line.startswith(label))
            return F(row[60:85].replace(' ',''))
        self.assertEqual(field('alpha particle mass energy equivalent in MeV'),F(entry['alpha_rest_MeV']))
        self.assertEqual(field('deuteron mass energy equivalent in MeV'),F(entry['deuteron_rest_MeV']))
        density=a.BernsteinDensity([0,F(3,2),0])
        for e in inputs['native_incident_energies_MeV']:
            m=a.PhysicalAngularMap(entry['alpha_rest_MeV'],entry['deuteron_rest_MeV'],e)
            r=response(det((-1,F(-1,2)),(0,F(1,4))),det((F(1,2),1),(F(1,2),F(1,4))),density,m)
            self.assertEqual(r['pair_energy_MeV'].lower,m.G*r['coincidence'].lower)
            self.assertEqual(r['coincidence_daughters'].upper,2*r['coincidence'].upper)
            self.assertEqual(r['selected_plus_energy_MeV'],r['selected_minus_energy_MeV'])
            SAVED['native_rows'].append({'energy_MeV':e,'sigma':str(density.sigma),'G_MeV':str(m.G),'model_operations':m.operations,'source_sha256':entry['sha256'],**measure_row(r)})

    def test_22_saved_strip_provenance_and_count_closure(self):
        r=response(det((0,1),(0,F(2,3))),det((-1,1),(F(1,3),F(2,3))))
        self.assertEqual(sum((s['interval'][1]-s['interval'][0] for s in r['strips']),F(0)),1)
        for s in r['strips']:
            self.assertTrue(s['interval'][0]<s['midpoint']<s['interval'][1]);self.assertIn('assignment_overlap',s['sets'])
        # Integral assignment count = OR measure + overlap, with all endpoints enclosed.
        left=r['coincidence_assignments'];right=r['coincidence'].added(r['assignment_overlap'])
        self.assertLessEqual(max(left.lower,right.lower),min(left.upper,right.upper))
        SAVED['strip_provenance']=[{'interval':[str(x) for x in s['interval']],'sets':{key:{'inner':[[str(x) for x in iv] for iv in v.inner],'outer':[[str(x) for x in iv] for iv in v.outer]} for key,v in s['sets'].items()}} for s in r['strips']]
        SAVED['closure'].append({'case':'overlap_and_count',**measure_row(r)})

if __name__=='__main__':unittest.main()
