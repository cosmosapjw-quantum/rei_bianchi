"""Independent exact oracle tests. Production implementation imported only for outputs.
The oracle expands into SymPy power basis and samples exact derivative algebraic
critical values, separately checking all returned interval identities.
"""
import sys, random, json, hashlib
from fractions import Fraction as Q
from pathlib import Path
import sympy as s
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r16_nonnegative_cubic as P
x=s.Symbol('x',real=True)

def toS(v): return s.Rational(v.numerator,v.denominator)
def expr(row):
    return s.expand(sum(toS(row[i])*s.binomial(3,i)*x**i*(1-x)**(3-i) for i in range(4)))

def independent_nonnegative(row):
    f=expr(row)
    if f==0: return True
    d=s.diff(f,x)
    roots=s.solve(d,x)
    values=[f.subs(x,0),f.subs(x,1)]
    for r in roots:
        if r.is_real is True and 0<r<1: values.append(s.simplify(f.subs(x,r)))
    return all(bool(s.simplify(v>=0)) for v in values)

def oracle_partition(row):
    part=P.positive_partition(row)
    f=expr(row)
    for a,b,coef in part['leaves']:
        assert min(coef)>=0
        u=s.Symbol('u')
        g=s.expand(f.subs(x,toS(a)+(toS(b)-toS(a))*u))
        h=s.expand(sum(toS(coef[i])*s.binomial(3,i)*u**i*(1-u)**(3-i) for i in range(4)))
        assert s.simplify(g-h)==0
    return part

def power_to_B3(f):
    poly=s.Poly(f,x)
    z=[Q(poly.nth(k)) for k in range(4)]
    return (z[0],z[0]+z[1]/3,z[0]+2*z[1]/3+z[2]/3,sum(z))

def test_boundary_examples():
    exact_cases=[
        s.Integer(0),s.Integer(1),x,1-x,x**3,(1-x)**3,
        (x-s.Rational(1,2))**2,
        (x-s.Rational(1,3))**2*(x+1),
        (x-s.Rational(3,8))**2*(2-x),
        (1-x)*(1-4*x)**2,
        x*(x-s.Rational(1,4))**2,
        (x-s.Rational(1,2))**2+s.Rational(1,2**80),
        x*(1-x),x**2+(1-x)**2,
        (x-s.Rational(1,2))**2*(x+1)/300,
    ]
    for f in exact_cases:
        b=power_to_B3(f)
        assert independent_nonnegative(b)
        oracle_partition(b)
    assert P.classify_nonnegative(power_to_B3((x-s.Rational(1,2))**2))['interior_zero_knots']==[Q(1,2)]
    for f in [x*(x-1),x-s.Rational(1,2),-(x-s.Rational(1,2))**2,1-8*x+8*x*x]:
        b=power_to_B3(f)
        assert not independent_nonnegative(b)
        try: P.positive_partition(b)
        except P.DomainError: pass
        else: raise AssertionError('negative accepted')
    return len(exact_cases)+4

def test_random_exhaustive(n=1500):
    rng=random.Random(20261028)
    passed=0;positives=0;negatives=0
    for _ in range(n):
        b=tuple(Q(rng.randint(-5,5),rng.choice([1,2,3,5,7])) for j in range(4))
        exp=independent_nonnegative(b)
        try:
            result=P.positive_partition(b,depth=256,nodes=16384)
            actual=True
        except P.DomainError:actual=False
        assert actual==exp,(b,actual,exp)
        if actual:
            oracle_partition(b);positives+=1
        else:negatives+=1
        passed+=1
    return dict(random_passed=passed,positive=positives,negative=negatives)

def test_adapter():
    def data():
        b=power_to_B3((x-s.Rational(1,3))**2)
        source=[Q(0),Q(1)]
        gr=[list(b)];ge=[[Q(0),Q(0),Q(0),Q(0)]]
        bind={'source_id':'synthetic-r16','clock_id':'t-r16','clock_unit':'s',
              'full_A_family_id':'synthetic-full-A','source_locator':'synthetic:exact',
              'source_sha256':'f'*64,'whole_forcing_source_sha256':'',
              'scientific_status':'ARITHMETIC_CONTROL_PREMISE','state_order':['v0','v1'],
              'whole_forcing_hash_format':P.R15_FORCING_SCHEMA}
        h=P.canonical_r15_hash(source,gr,ge,bind)
        bind['whole_forcing_source_sha256']=h
        cert=bind.copy();cert.update({'generator':'A=K+wH;H=pi*d^T-diag(d)',
              'fixed_K_pi_d':True,'full_w_box':True,'all_start_times':True,
              'zero_mass_residual':True,'short_remainder_nonexpansive':True,
              'forcing_whole_fine_coarse_domain':True,'q':'1/2','tau':'1',
              't0':'0','T':'1','w_box':['0','1']})
        return {'states':2,'q':'1/2','tau':'1','c':'1','d':'-1',
                'initial':['0','0'],'source_knots':['0','1'],
                'observation_knots':['0','1'],
                'g_r':[[str(v) for v in b]],'g_e':[['0']*4],
                'binding':bind,'certificate':cert}
    case=data();refined,meta=P.adapt_case_for_r15(case)
    assert meta['original_cells']==1 and meta['refined_cells']>1
    assert case['binding']['whole_forcing_source_sha256']==meta['original_whole_forcing_hash']
    assert refined['binding']['whole_forcing_source_sha256']==refined['certificate']['whole_forcing_source_sha256']
    assert meta['native_source_sha256_unchanged']=='f'*64
    assert meta['mathematical_identity']=='EXACT_BERNSTEIN_AFFINE_RESTRICTION'
    assert all(all(Q(c)>=0 for c in row) for row in refined['g_r'])
    # Integration is conserved under refinement (exact Simpson/degree3 Bernstein weights).
    def area(a,b,rows):
        return sum((b[i+1]-b[i])*sum(Q(v) for v in rows[i])/4 for i in range(len(rows)))
    assert area([Q(k) for k in case['source_knots']],[Q(k) for k in case['source_knots']],case['g_r'])==area([Q(k) for k in refined['source_knots']],[Q(k) for k in refined['source_knots']],refined['g_r'])
    bad=json.loads(json.dumps(case));bad['binding']['whole_forcing_source_sha256']='0'*64
    try:P.adapt_case_for_r15(bad)
    except P.DomainError: pass
    else:raise AssertionError('corrupt hash admitted')
    try:P.adapt_case_for_r15(case,max_source_cells=1)
    except P.ResourceExceeded:pass
    else:raise AssertionError('excess source cells admitted')
    # Typed malformed input and negative polynomial cannot be silently promoted.
    for b in [(True,0,0,0),(0,0,0,0.2)]:
        try:P.positive_partition(b)
        except P.DomainError:pass
        else:raise AssertionError('malformed coefficient admitted')
    return {'adapter_cells':meta['refined_cells'],'source_digest':meta['original_whole_forcing_hash'],
            'new_digest':meta['refined_whole_forcing_hash'], 'lineage':meta}

if __name__=='__main__':
    print('boundary_count',test_boundary_examples())
    print('random',test_random_exhaustive())
    print('adapter',json.dumps(test_adapter(),sort_keys=True))
