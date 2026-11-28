"""New EXFOR controls; executed only in authorized primary invocation."""
from fractions import Fraction as F
from decimal import Decimal,localcontext
from math import comb
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import exfor_aperture as E

class Controls(unittest.TestCase):
    def test_exact_inputs_and_source(self):
        for x in (True,0.2,None,[],float('nan')):
            with self.assertRaises(E.ContractError):E.rational(x)
        with self.assertRaises(E.ContractError):E.sensitivity('1','-0.1')
        self.assertEqual(E.sensitivity('0.02','0.03'),(0,F('0.05')))
        with self.assertRaises(FileNotFoundError):E.parse_source(ROOT/'missing.x4')
        with self.assertRaises(E.ContractError):E.parse_source(__file__)
    def test_basis(self):
        for n in (4,8):
            for endpoint in (False,True):
                b=E.EvenBasis(n,endpoint);self.assertEqual(b.integrate(((-1,1),)),b.d)
                for x in (F(-1),F(-2,3),F(0),F(1)):
                    self.assertEqual(b.value(x),b.value(-x));self.assertTrue(all(v>=0 for v in b.value(x)))
                if endpoint:self.assertTrue(all(v==0 for v in b.value(1)))
                else:self.assertEqual(sum(b.value(F(2,7))),1)
        for args in ((6,), (4,1)):
            with self.assertRaises(E.ContractError):E.EvenBasis(*args)
        with self.assertRaises(E.ContractError):E.EvenBasis(4).value(1.0)
        with self.assertRaises(E.ContractError):E.EvenBasis(4).integrate(((1,-1),))
    def test_cosine_decimal_oracle(self):
        with localcontext() as ctx:
            ctx.prec=90
            def atan(x):
                term=x;total=x;k=1
                while abs(term)>Decimal('1e-95'):
                    term*=-(x*x);total+=term/(2*k+1);k+=1
                return total
            pi=16*atan(Decimal(1)/5)-4*atan(Decimal(1)/239)
            for theta in E.ANGLES:
                x=Decimal(theta)*pi/180;term=Decimal(1);cos=term
                for k in range(1,100):term*=-x*x/((2*k-1)*(2*k));cos+=term
                oracle=F(cos);iv=E.H.sincos_turn(F(theta,720))[1]
                self.assertLessEqual(iv.lower,oracle);self.assertLessEqual(oracle,iv.upper)
                for n in (4,8):
                    b=E.EvenBasis(n)
                    for (l,u),v in zip(b.row(theta),b.value(oracle)):self.assertTrue(0<l<=v<=u)
            for theta,expected in ((0,1),(90,0),(180,-1)):
                iv=E.H.sincos_turn(F(theta,720))[1];self.assertEqual((iv.lower,iv.upper),(expected,expected))
        for x in (-1,181,46.0):
            with self.assertRaises(E.ContractError):E.EvenBasis(4).row(x)
    def test_polytope_and_ratio(self):
        A=tuple(tuple(map(F,row)) for row in ((-1,0),(0,-1),(1,1),(-1,-1)))
        p=E.enumerate_energies(A,[(F(0),F(0),F(1),F(-1,2))])[0]
        self.assertEqual(set(p['vertices']),{(F(0),F(1,2)),(F(0),F(1)),(F(1,2),F(0)),(F(1),F(0))})
        for scale in (1,7):
            v=[tuple(scale*x for x in v) for v in p['vertices']]
            r=E.ratio_extrema(v,(F(0),F(1)),(F(0),F(1)),(F(1),F(1)))
            self.assertEqual((r['lower'],r['upper']),(0,1))
            r=E.ratio_extrema(v,(F(3),F(3)),(F(3),F(3)),(F(1),F(1)))
            self.assertEqual((r['lower'],r['upper']),(3,3))
        self.assertEqual(E.enumerate_energies(((F(1),),(F(-1),)),[(F(0),F(-1))])[0]['vertices'],[])
        self.assertEqual(E.enumerate_energies(((F(1),),(F(-1),),(F(1),)),[(F(1),F(-1),F(1))])[0]['vertices'],[(F(1),)])
        self.assertIsNone(E.inverse(((F(1),F(1)),(F(2),F(2)))))
    def test_inner_outer_constructed(self):
        rows=(((F(1),F(2)),),);bounds=((F(1),F(4)),)
        ai,bi=E.constraints(rows,bounds,'inner');ao,bo=E.constraints(rows,bounds,'outer')
        vi=E.enumerate_energies(ai,[bi])[0]['vertices'];self.assertEqual(set(vi),{(F(1),),(F(2),)})
        for v in vi:self.assertTrue(all(E.dot(a,v)<=b for a,b in zip(ao,bo)))
    def test_manufactured_integrals_and_physical_boundaries(self):
        # Exact rational manufactured map gamma=1,a=0: F(mu)=mu.
        # Apply inherited Boolean same-event sets to the NEW basis integral.
        api=E.H._Z._API;model=api.AngularMap(1,0)
        for n in (4,8):
            b=E.EvenBasis(n)
            for name,wa,wb,expected_sets in [('FULL',(-1,1),(-1,1),((F(-1),F(1)),)),('HEMISPHERES',(0,1),(-1,0),((F(-1),F(1)),)),('CAPS',(F(1,2),1),(-1,F(-1,2)),((F(-1),F(-1,2)),(F(1,2),F(1))))]:
                sa=model.preimage(wa,F(1,2**48)).sets;sb=model.preimage(wb,F(1,2**48)).sets
                coincidence=sa.intersection(sb.reflected()).union(sb.intersection(sa.reflected()))
                self.assertEqual(coincidence.inner,expected_sets);self.assertEqual(coincidence.outer,expected_sets)
                coeff=E.geometry_coefficients(b,[{'interval':(F(0),F(1)),'sets':{'coincidence':coincidence}}])
                self.assertEqual(coeff,(b.integrate(expected_sets),b.integrate(expected_sets)))
                if name in ('FULL','HEMISPHERES'):self.assertEqual(coeff,(b.d,b.d))
            self.assertEqual(b.integrate(((0,1),)),tuple(d/2 for d in b.d))
            caps=b.integrate(((-1,F(-1,2)),(F(1,2),1)))
            for j in range(len(caps)):
                expected=F(0)
                for k in {b.indices[j],n-b.indices[j]}:
                    def prim(x):return 2*sum((F(comb(n,k)*comb(n-k,r)*(-1)**r,k+r+1)*x**(k+r+1) for r in range(n-k+1)),F(0))
                    expected+=prim(F(1,4))-prim(F(0))+prim(F(1))-prim(F(3,4))
                self.assertEqual(caps[j],expected)
        for args in ((0,1,1),(1,1,0),(1,1,1)):
            with self.assertRaises(E.ContractError):E.H.PhysicalAngularMap(*args)

def verify_saved(data):
    """Independent exact reader; no enumeration/ratio/integration calls."""
    checked=0
    for case in data['cases']:
        d=list(map(F,case['d']))
        for kind,p in case['polytopes'].items():
            A=[list(map(F,row)) for row in p['matrix']];rhs=list(map(F,p['rhs']));vertices=[list(map(F,v)) for v in p['vertices']]
            assert p['unique_vertices']==len(vertices)
            assert p['bases_attempted']>=p['singular_bases']+p['feasible_bases']
            for v in vertices:
                assert all(sum(x*y for x,y in zip(row,v))<=z for row,z in zip(A,rhs))
                assert sum(x*y for x,y in zip(d,v))>0;checked+=1
                if kind=='inner':
                    outer=case['polytopes']['outer']
                    assert all(sum(F(x)*y for x,y in zip(row,v))<=F(z) for row,z in zip(outer['matrix'],outer['rhs']))
            for name,obj in case['objectives'].items():
                lo=list(map(F,obj['c_lower']));hi=list(map(F,obj['c_upper']));r=obj[kind]
                assert all(0<=l<=u<=z for l,u,z in zip(lo,hi,d))
                if not vertices:assert r['status']=='EMPTY';continue
                ratios=[]
                for c in (lo,hi):ratios.append([sum(x*y for x,y in zip(c,v))/sum(x*y for x,y in zip(d,v)) for v in vertices])
                assert F(r['lower'])==min(ratios[0]);assert F(r['upper'])==max(ratios[1])
                for label,c in (('lower',lo),('upper',hi)):
                    v=list(map(F,r[label+'_witness']));assert v in vertices
                    assert sum(x*y for x,y in zip(c,v))/sum(x*y for x,y in zip(d,v))==F(r[label])
                if name=='FULL':assert F(r['lower'])==F(r['upper'])==1
    assert len(data['cases'])==12 and len(data['dcs'])==12 and len(data['totals'])==6
    return checked
