"""New13geometries only; independent hand Fraction and vector/interval controls."""
from fractions import Fraction as F
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
import tdcs413 as m

UNIT=Path(__file__).resolve().parents[1]


def prior_point():
    path=UNIT.parent/'he_ang_pwbe_spin_azimuth_20261024/code/pwbe.py'
    spec=importlib.util.spec_from_file_location('reused_pwbe_point',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.pwbe_point


def raw_vector_K(theta):
    # Literal transition amplitude and unpolarized mixture, no closed diagonal helper.
    k=math.sqrt(250/17);r=math.sqrt(517/17);th=math.radians(theta)
    A=(k*math.sin(th),0.,k*math.cos(th));B=(-A[0],0.,A[2]);beam=(0.,0.,r)
    q2=sum((beam[i]-A[i]-B[i])**2 for i in range(3))
    gapA=sum((beam[i]-A[i])**2 for i in range(3));gapB=sum((beam[i]-B[i])**2 for i in range(3))
    norm=8*math.sqrt(2)/(2*math.pi)**3
    D=norm/gapA*((1+q2)**-2-(1+sum(x*x for x in B))**-2)
    X=norm/gapB*((1+q2)**-2-(1+sum(x*x for x in A))**-2)
    return (2*math.pi)**4*(k*k/r)*(.25*(D+X)**2+.75*(D-X)**2)


class Contract(unittest.TestCase):
    def close(self,a,b,abs_tol=1e-10,rel_tol=1e-11):
        self.assertLessEqual(abs(a-b),max(abs_tol,rel_tol*abs(b)),(a,b))

    def test_01_exact_source_selection_and_zero(self):
        obj,rows=m.load_source();self.assertEqual(len(rows),13);self.assertEqual(len(obj['excluded_rows']),3)
        self.assertEqual([int(r['theta_deg']) for r in rows],list(m.SELECTED_ANGLES))
        self.assertEqual([(r['y'],r['s']) for r in rows],[(F(a),F(b)) for a,b in [(10,3),(11,3),(17,3),(28,4),(50,4),(76,5),(82,6),(100,6),(30,3),(15,2),(4,1),(2,1),(0,1)]])
        self.assertTrue(all(r['y'] is None and r['s'] is None for r in obj['excluded_rows']))
        self.assertEqual(rows[-1]['printed'],'0(1)')

    def test_02_source_schema_rejection(self):
        obj,_=m.load_source()
        for kind in ['theta','error','excluded']:
            a=json.loads(json.dumps(obj))
            if kind=='theta':a['rows'][0]['theta_deg']='32.1'
            elif kind=='error':a['rows'][0]['s']='0'
            else:a['excluded_rows'][0]['y']='89'
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'input.json';p.write_text(json.dumps(a))
                with self.assertRaises(ValueError):m.load_source(p)

    def test_03_exact_fraction_toy(self):
        f=[F(1),F(2),F(4)];y=[F(1),F(4),F(0)];s=[F(1)]*3
        exact=max(F(0),max((y[i]*f[j]-y[j]*f[i])/(s[i]*f[j]+s[j]*f[i]) for i in range(3) for j in range(3)))
        self.assertEqual(exact,F(8,3));a=F(2,3)
        self.assertEqual(max(abs(a*f[i]-y[i])/s[i] for i in range(3)),exact)
        got=m.minimax(f,y,s);self.close(got['a'],float(a));self.close(got['kappa'],float(exact));self.assertEqual(got['active_pair_1based'],[2,3])

    def test_04_exactly_proportional(self):
        got=m.minimax([1,2,4],[3,6,12],[1,1,1]);self.close(got['kappa'],0);self.close(got['a'],3)

    def test_05_scale_invariances(self):
        f=[1,2,4];y=[1,4,0];s=[1,1,1];a=m.minimax(f,y,s)
        b=m.minimax([7*x for x in f],y,s);c=m.minimax(f,[3*x for x in y],[3*x for x in s])
        self.close(a['kappa'],b['kappa']);self.close(a['a']/7,b['a']);self.close(a['kappa'],c['kappa']);self.close(3*a['a'],c['a'])

    def test_06_invalid_fit(self):
        for f,y,s in [([0],[1],[1]),([-1],[1],[1]),([1],[-1],[1]),([1],[0],[1]),([1],[1],[0]),([True],[1],[1]),([float('nan')],[1],[1]),([1],[float('inf')],[1]),([1,2],[1],[1])]:
            with self.assertRaises(ValueError):m.minimax(f,y,s)
        with self.assertRaises(ValueError):m.feasible_interval([1],[1],[1],-1)

    def test_07_new13_source_vector_and_prior_point(self):
        _,rows=m.load_source();point=prior_point()
        for row in rows:
            th=float(row['theta_deg']);closed=m.diagonal(th)['K'];v=raw_vector_K(th)
            q=point(float(m.E0),float(m.E),math.cos(math.radians(th)),math.cos(math.radians(th)),math.pi)
            self.close(closed,v,abs_tol=0);self.close(closed,q['K'],abs_tol=0)
            self.assertGreater(closed,0);self.close(q['spin']['triplet'],0,abs_tol=2e-15)

    def test_08_shape_reference(self):
        self.close(m.shape(44),1)
        for th in m.SELECTED_ANGLES:self.close(m.shape(th),raw_vector_K(th)/raw_vector_K(44),abs_tol=0)

    def test_09_actual_minimax_vs_bisection(self):
        _,rows=m.load_source();f=[m.shape(r['theta_deg']) for r in rows];y=[r['y'] for r in rows];s=[r['s'] for r in rows]
        a=m.minimax(f,y,s);b=m.minimax_bisection(f,y,s)
        self.close(a['kappa'],b['kappa']);self.close(a['a'],b['a']);self.close(a['objective'],a['kappa'])
        i,j=[x-1 for x in a['active_pair_1based']];self.close(a['residuals'][i],-a['kappa']);self.close(a['residuals'][j],a['kappa'])

    def test_10_peak_scope_bracket_signs(self):
        p=m.peak();self.assertTrue(-.5<p['z']<0);self.assertLess(abs(p['root_residual']),1e-11)
        self.assertTrue(32<p['theta_deg']<p['theta_q0_deg']<60)
        self.assertGreater(m.peak_N(-.5),0);self.assertLess(m.peak_N(0),0)
        self.assertTrue(-1<m.diagonal(32)['z']<-.5);self.assertTrue(0<m.diagonal(60)['z']<math.sqrt(float(m.K2)))
        # Derivative formula signs on both sides of root; theorem supplies full uniqueness.
        self.assertGreater(m.peak_N(p['z']-.001),0);self.assertLess(m.peak_N(p['z']+.001),0)

    def test_11_invalid_model_and_exact_energy_shell(self):
        self.assertEqual(m.E0,2*m.E+F(1,2))
        for th in [31,61,True,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):m.diagonal(th)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contract))
    out=UNIT/'results';out.mkdir(exist_ok=True);(out/'TEST_REPORT.json').write_text(json.dumps({'unit':'HE-ANG-TDCS413-DIAGONAL','methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'old_suite_replays':0,'new_prior_point_geometries':13},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
