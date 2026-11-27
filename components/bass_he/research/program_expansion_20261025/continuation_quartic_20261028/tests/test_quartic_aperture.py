"""QUARTIC12 new controls and independent saved certificate reader."""
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import quartic_aperture as Q

class Controls(unittest.TestCase):
    def test_signed_row_perturbation(self):
        b=(F(1,2),F(-1,3),F(1,4))
        for t in Q.ANGLES:
            row=Q.angle_row(t);zl,zh=row['z'];wl,wh=row['z2'];m=Q.dot(row['midpoint'],b)
            for z in (zl,zh):
                for w in (wl,wh):self.assertLessEqual(abs(b[0]+b[1]*z+b[2]*w-m),row['epsilon'])
        for x in (46.0,-1,181,True):
            with self.assertRaises(Q.ContractError):Q.angle_row(x)
    def test_compactness_and_normalization_proof(self):
        rows=[Q.angle_row(t) for t in (46,61,87)]
        for i in range(3):
            for j in range(i):self.assertGreaterEqual(rows[j]['z'][0]-rows[i]['z'][1],F(1,5))
        self.assertEqual(F(7,50)**2/(12*Q.B),Q.DMIN)
        delta=F(7,50)/(12*Q.B);self.assertLess(rows[-1]['mu'][1]+delta,1);self.assertGreater(rows[-1]['mu'][0]-delta,-1)
        self.assertEqual((3*25,3*25*2,3*25),(75,150,75));self.assertTrue(all(v<Q.B for v in (75,150,75)))
    def test_positivity_controls_and_endpoint(self):
        b=(F(13,50),F(-1),F(1));self.assertEqual(Q.quadratic_minimum(b)['value'],F(1,100))
        self.assertLess(min(Q.dot(row,b) for row in Q.positivity_rows(1,'inner',False)),0)
        self.assertGreaterEqual(min(Q.dot(row,b) for row in Q.positivity_rows(4,'inner',False)),0)
        for v in ((F(1),F(-2)),(F(0),F(1)),(F(1),F(-1))):
            b=Q.lift(v,True)
            for z in (F(0),F(1,3),F(1)):
                self.assertEqual(b[0]+b[1]*z+b[2]*z*z,(1-z)*(v[0]+(v[0]+v[1])*z))
            self.assertEqual(Q.quadratic_minimum(b)['nonnegative'],v[0]>=0 and 2*v[0]+v[1]>=0)
        b=(F(0),F(-1),F(1))
        self.assertTrue(all(Q.dot(row,b)>=0 for row in Q.positivity_rows(1,'outer',False)))
        self.assertEqual(Q.quadratic_minimum(b)['value'],F(-1,4))
    def test_nested_cells_and_signed_known_polytopes(self):
        A=((F(1),F(0)),(F(-1),F(0)),(F(0),F(1)),(F(0),F(-1)))
        p,c=Q.enumerate_shared(A,[(F(1),F(1),F(1),F(1)),(F(-2),F(1),F(1),F(1))])
        self.assertEqual(set(p[0]['vertices']),{(F(x),F(y)) for x in (-1,1) for y in (-1,1)})
        self.assertEqual(p[1]['vertices'],[]);self.assertEqual(c['active_bases_attempted'],6);self.assertEqual(c['rhs_candidate_count'],8)
        p,c=Q.enumerate_shared(((F(1),),(F(-1),),(F(1),)),[(F(-1),F(1),F(-1))]);self.assertEqual(p[0]['vertices'],[(F(-1),)])
        b=(F(13,50),F(-1),F(1))
        for N in (4,16):self.assertTrue(all(Q.dot(row,b)>=0 for row in Q.positivity_rows(N,'inner',False)))
    def test_signed_moments_manufactured_geometry(self):
        self.assertEqual(Q.integrate_monomials(((-1,1),)),Q.D)
        expected=(F(1),F(7,12),F(31,80))
        self.assertEqual(Q.integrate_monomials(((-1,F(-1,2)),(F(1,2),1))),expected)
        api=Q.E.H._Z._API;model=api.AngularMap(1,0)
        for wa,wb,expected in [((-1,1),(-1,1),Q.D),((0,1),(-1,0),Q.D),((F(1,2),1),(-1,F(-1,2)),expected)]:
            a=model.preimage(wa,F(1,2**48)).sets;b=model.preimage(wb,F(1,2**48)).sets;c=a.intersection(b.reflected()).union(b.intersection(a.reflected()))
            moment=Q.moments([{'interval':(F(0),F(1)),'sets':{'coincidence':c}}]);self.assertEqual(moment['lower'],expected);self.assertEqual(moment['upper'],expected)
        lo,hi=Q.signed_numerator((F(1),F(-2),F(3)),(F(1),F(2),F(3)),(F(2),F(3),F(4)));self.assertEqual((lo,hi),(4,10))
    def test_concave_convex_denominator_weighting(self):
        l=(F(1,10),F(1,20),F(1,30));u=(F(1,5),F(1,10),F(1,15));a=(F(1),F(-1),F(1));b=(F(2),F(1),F(-1));t=F(2,5);v=tuple(t*x+(1-t)*y for x,y in zip(a,b))
        al,ah=Q.signed_numerator(a,l,u);bl,bh=Q.signed_numerator(b,l,u);vl,vh=Q.signed_numerator(v,l,u)
        self.assertGreaterEqual(vl,t*al+(1-t)*bl);self.assertLessEqual(vh,t*ah+(1-t)*bh)
        den=Q.dot(Q.D,v);weight=t*Q.dot(Q.D,a)/den
        self.assertGreaterEqual(vl/den,weight*al/Q.dot(Q.D,a)+(1-weight)*bl/Q.dot(Q.D,b))
        self.assertLessEqual(vh/den,weight*ah/Q.dot(Q.D,a)+(1-weight)*bh/Q.dot(Q.D,b))
        artificial={'lower':(F(1),F(0),F(0)),'upper':(F(1),F(0),F(0))};v=(F(1,5),F(-1),F(1))
        empty=Q.objective([], [v],False,artificial);self.assertEqual(empty['status'],'EMPTY_PHYSICAL_INTERSECTION');self.assertIsNone(empty['physical_range'])
        with self.assertRaises(Q.ContractError):Q.objective([v],[v],False,artificial)
        self.assertEqual(Q.folded_bernstein((F(1),F(-1),F(1))),(F(1),F(0),F(7,3)))
    def test_source_and_physical_boundaries(self):
        with self.assertRaises(Q.ContractError):Q.E.parse_source(__file__)
        with self.assertRaises(FileNotFoundError):Q.E.parse_source(ROOT/'missing.x4')
        for args in ((0,1,1),(1,1,0),(1,1,1)):
            with self.assertRaises(Q.ContractError):Q.E.H.PhysicalAngularMap(*args)
        for x in (0.0,True,None):
            with self.assertRaises(Q.ContractError):Q.rational(x)
        with self.assertRaises(Q.ContractError):Q.integrate_monomials(((1,-1),))

# Below deliberately does not call optimizer, module positivity, objective or
# monomial functions; it reads and checks saved exact arithmetic independently.
def verify_saved(data):
    D=(F(2),F(2,3),F(2,5));floor=F(49,4800000);B=F(160);count=0;by_case={}
    def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
    def lift(v,end):return (v[0],v[1],-v[0]-v[1]) if end else tuple(v)
    def qmin(b):
        values=[b[0],sum(b)]
        if b[2]>0 and 0<-b[1]/(2*b[2])<1:values.append(b[0]-b[1]**2/(4*b[2]))
        return min(values)
    def ratio(v,end,m):
        b=lift(v,end);den=dot(D,b);kl=list(map(F,m['lower']));ku=list(map(F,m['upper']))
        return (sum(x*(l if x>=0 else u) for x,l,u in zip(b,kl,ku))/den,sum(x*(u if x>=0 else l) for x,l,u in zip(b,kl,ku))/den)
    assert F(data['Dmin'])==floor and F(data['B'])==B
    assert len(data['cases'])==12 and len(data['dcs'])==12 and len(data['totals'])==6
    for c in data['cases']:
        e=c['energy'];end=c['endpoint_zero'];by_case[(e,c['case'])]=c;parsed={}
        for kind,p in c['polytopes'].items():
            A=[list(map(F,r)) for r in p['matrix']];rhs=list(map(F,p['rhs']));verts=[tuple(map(F,v)) for v in p['vertices']];parsed[kind]=verts
            assert len(verts)==p['unique_vertices']==len(set(verts))
            assert p['feasible_bases']<=p['bases_attempted']-p['singular_bases']
            for vi,v in enumerate(verts):
                b=lift(v,end);assert all(abs(x)<=B for x in b);assert dot(D,b)>=floor
                assert all(dot(row,v)<=r for row,r in zip(A,rhs));count+=1
                if kind=='inner':
                    stored=p['quadratic_positivity'][vi];z=F(stored['z']);assert 0<=z<=1 and b[0]+b[1]*z+b[2]*z*z==qmin(b)==F(stored['value']) and stored['nonnegative'] is True
                    assert qmin(b)>=0
                    if end:assert sum(b)==0 and b[0]>=0 and 2*b[0]+b[1]>=0
                    outer=c['polytopes']['outer'];assert all(dot(list(map(F,row)),v)<=F(r) for row,r in zip(outer['matrix'],outer['rhs']))
                    bounds=[(max(F(0),F(row[2])-F(row[3])),F(row[2])+F(row[3])) for row in data['dcs'] if F(row[0])==e]
                    for row,(L,U) in zip(data['rows'],bounds):
                        y=dot(list(map(F,row['midpoint'])),b);eps=F(row['epsilon']);assert L<=y-eps<=y+eps<=U
        for name,obj in c['objectives'].items():
            m=data['moments_by_energy'][str(e)][name];assert all(0<=F(l)<=F(u)<=d for l,u,d in zip(m['lower'],m['upper'],D))
            outer=[ratio(v,end,m) for v in parsed['outer']];inner=[ratio(v,end,m) for v in parsed['inner']]
            if not outer:
                assert obj['status']=='EMPTY_OUTER' and all(obj[k] is None for k in ('raw_outer_ratio_range','physical_range','minimum_bracket','maximum_bracket','outer_lower_witness','outer_upper_witness','inner_minimum_witness','inner_maximum_witness'));continue
            for wk,kind in [('outer_lower_witness','outer'),('outer_upper_witness','outer'),('inner_minimum_witness','inner'),('inner_maximum_witness','inner')]:
                w=obj[wk]
                if w is None:assert kind=='inner' and not inner;continue
                v=tuple(map(F,w['parameters']));assert v in parsed[kind];b=lift(v,end);assert tuple(map(F,w['coefficients']))==b and F(w['denominator'])==dot(D,b)
                assert (F(w['lower']),F(w['upper']))==ratio(v,end,m)
            raw=(min(x[0] for x in outer),max(x[1] for x in outer));physical=(max(F(0),raw[0]),min(F(1),raw[1]));assert tuple(map(F,obj['raw_outer_ratio_range']))==raw
            if physical[0]>physical[1]:
                assert obj['status']=='EMPTY_PHYSICAL_INTERSECTION' and obj['physical_range'] is None and not inner
                assert obj['minimum_bracket'] is None and obj['maximum_bracket'] is None
                continue
            assert tuple(map(F,obj['physical_range']))==physical
            minimum=(physical[0],min(x[1] for x in inner) if inner else None);maximum=(max(x[0] for x in inner) if inner else None,physical[1])
            for key,expected in (('minimum_bracket',minimum),('maximum_bracket',maximum)):assert tuple(None if x is None else F(x) for x in obj[key])==expected
            for key,kind,which,expected in [('outer_lower_witness','outer',0,raw[0]),('outer_upper_witness','outer',1,raw[1]),('inner_minimum_witness','inner',1,minimum[1]),('inner_maximum_witness','inner',0,maximum[0])]:
                w=obj[key]
                if expected is None:assert w is None;continue
                v=tuple(map(F,w['parameters']));assert v in parsed[kind];assert ratio(v,end,m)[which]==expected
            if name=='FULL':assert raw==(F(1),F(1))
        w=c['inner_witness']
        if parsed['inner']:
            b=tuple(map(F,w['coefficients']));parameters=tuple(map(F,w['parameters']));assert parameters in parsed['inner'] and b==lift(parameters,end);assert qmin(b)==F(w['qminimum']['value'])>=0
            assert F(w['denominator'])==dot(D,b)
            for saved,row in zip(w['data'],data['rows']):
                y=dot(list(map(F,row['midpoint'])),b);eps=F(row['epsilon']);assert F(saved['angle'])==F(row['angle']) and F(saved['midpoint_value'])==y and tuple(map(F,saved['value_enclosure']))==(y-eps,y+eps)
                match=next(r for r in data['dcs'] if F(r[0])==e and F(r[1])==F(row['angle']));assert tuple(map(F,saved['sensitivity']))==(max(F(0),F(match[2])-F(match[3])),F(match[2])+F(match[3]))
            old=(sum(b),b[0]-b[2],b[0]+b[2]-b[1]/3);assert tuple(map(F,w['old_folded_bernstein']))==old;assert w['outside_old_sufficient_cone']==any(x<0 for x in old)
        else:assert w is None
    # Verify the finite nested inclusions directly on all saved vertices.
    for e in (213,258,330):
        for low,high in (('free_N1','free_N4'),('free_N4','free_N16')):
            for kind,src,dst in [('inner',low,high),('outer',high,low)]:
                p=by_case[(e,src)]['polytopes'][kind];target=by_case[(e,dst)]['polytopes'][kind]
                for v in p['vertices']:
                    vv=list(map(F,v));assert all(sum(F(a)*b for a,b in zip(row,vv))<=F(r) for row,r in zip(target['matrix'],target['rhs']))
    return {'vertices_checked':count,'nested_case_inclusions_checked':12,'method':'independent exact saved certificate reader; not a second optimizer'}
