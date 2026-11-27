"""Manufactured controls with independently specified exact expectations."""
from fractions import Fraction as F
from copy import deepcopy
from itertools import product
import endpoint14 as p
import verify_certificate as reader

def run(saved,old,saved_path,official_path,unit):
    results=[]
    def test(name,fn):
        try:fn();results.append({'id':name,'status':'PASS'})
        except Exception as exc:results.append({'id':name,'status':'FAIL','error':repr(exc)})
    def require(ok):
        if not ok:raise AssertionError('manufactured expectation')
    def identities():
        a=(F(2),F(-3),F(5));require(p.cubic(a)==(2,-5,8,-5));require(sum(p.cubic(a))==0)
        require(p.dot(p.D,a)==F(256,105))
        # d/dmu b(mu^2): bound uses coefficients 2b1,4b2,6b3.
        require(tuple((2*j)*b for j,b in enumerate(p.cubic(a)))[1:]==(-10,32,-30))
        for mu in (F(-1),F(-1,2),F(0),F(1,2),F(1)):
            require(p.fvalue(a,mu)==sum((b*mu**(2*j) for j,b in enumerate((2,-5,8,-5))),F(0)))
        # Weighted primitive derivative coefficients: -2*t^(2j)+2*t^(2j+2).
        for j in range(3):
            require(p.weighted(j,F(0))==p.D[j] and p.weighted(j,F(1))==0)
    test('factorization_normalization_derivative_identities',identities)
    def quadratic():
        require(p.minimum((F(1),F(-1),F(1)))=={'z':F(1,2),'value':F(3,4),'nonnegative':True})
        require(p.minimum((F(0),F(-1),F(1)))['value']==F(-1,4))
        require(not p.minimum((F(0),F(-1),F(1)))['nonnegative'])
        require(p.minimum((F(1),F(0),F(-2)))['value']==-1)
    test('positive_negative_coefficient_and_negative_quadratic',quadratic)
    def rows():
        manufactured={'rows':[{'angle':'46','z':['1/5','1/4']}]};r=p.rows_from_saved(manufactured)[0]
        require(r['basis_lower']==[F(3,4),F(3,20),F(3,100)] and r['basis_upper']==[F(4,5),F(1,5),F(1,20)])
        require(r['epsilon']==F(48,5))
        for a in product((F(-160),F(160)),repeat=3):
            for z in (F(1,5),F(9,40),F(1,4)):
                v=(1-z)*sum((a[j]*z**j for j in range(3)),F(0));require(abs(v-p.dot(r['midpoint'],a))<=r['epsilon'])
    test('three_basis_interval_signs',rows)
    test('threshold_moment_known_examples',lambda:require([p.weighted(j,F(1,2)) for j in range(3)]==[F(5,12),F(47,240),F(233,2240)]))
    def polytopes():
        m=[];b=[]
        for j in range(3):
            v=tuple(F(int(i==j)) for i in range(3));m.extend([v,tuple(-x for x in v)]);b.extend([F(1),F(0)])
        cube=p.enumerate_polytope(m,b);require(set(cube['vertices'])==set(product((F(0),F(1)),repeat=3)))
        simplex=p.enumerate_polytope([(-1,0,0),(0,-1,0),(0,0,-1),(1,1,1)],[0,0,0,1]);require(set(simplex['vertices'])=={(0,0,0),(1,0,0),(0,1,0),(0,0,1)})
        require(cube['singular_bases']>0 and p.solve3([(1,0,0),(2,0,0),(0,1,0)],[1,2,3]) is None)
    test('cube_simplex_vertices_and_singular_rejection',polytopes)
    def signed():
        require(p.ratio((F(1),F(-1),F(0)),{'lower':[F(0),F(1),F(0)],'upper':[F(1),F(2),F(0)]})==(F(-15,8),F(0)))
        require(p.outward(F(1,3),3)==['0.333','0.334'] and p.outward(F(-1,3),3)==['-0.334','-0.333'])
        require(p.outward(F(-1),3)==['-1.000','-1.000'])
    test('signed_ratio_and_outward_display',signed)
    def actual():reader.verify(saved,old,saved_path,official_path,unit)
    test('actual_six_certificates_nesting_witnesses_binding',actual)
    def corruption():
        for mutate in (lambda x:x['cases'][0]['polytopes']['inner']['vertices'][0].__setitem__(0,'999'),lambda x:x['rows'][0].__setitem__('epsilon','0'),lambda x:x['cases'][0]['objectives']['CAPS'].__setitem__('maximum_bracket',['0','0']),lambda x:x.__setitem__('source_sha256','wrong')):
            bad=deepcopy(saved);mutate(bad)
            try:reader.verify(bad,old)
            except (ValueError,AssertionError):continue
            raise AssertionError('corruption accepted')
    test('corrupted_certificate_rejection',corruption)
    return {'status':'PASS' if all(r['status']=='PASS' for r in results) else 'FAIL','passed':sum(r['status']=='PASS' for r in results),'failed':sum(r['status']=='FAIL' for r in results),'checks':results,'execution_scope':'one primary campaign; manufactured enumeration only in controls, one actual construction call','requested_model':'gpt-6.1-sol','observed_runtime_model':None}
