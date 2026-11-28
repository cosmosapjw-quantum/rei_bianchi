"""Exact finite covariance-box operations. Import has no scientific side effects."""
from fractions import Fraction as Q
from math import lcm
from itertools import product
import json

def rational(x):
    try: return Q(x)
    except (ValueError,ZeroDivisionError,OverflowError) as exc: raise ValueError('NONFINITE_OR_INVALID_TOKEN') from exc

def validate(F,H):
    n=len(F)
    if not n or len(H)!=n or any(len(r)!=n for r in F+H): raise ValueError('NONSQUARE_DIMENSION')
    F=[[rational(x) for x in row] for row in F]; H=[[rational(x) for x in row] for row in H]
    if any(F[i][j]!=F[j][i] for i in range(n) for j in range(n)): raise ValueError('NONSYMMETRIC_F')
    if any(H[i][j]!=H[j][i] for i in range(n) for j in range(n)): raise ValueError('NONSYMMETRIC_H')
    if any(x<0 for row in H for x in row): raise ValueError('NEGATIVE_H')
    return F,H

def radius(t):
    t=rational(t)
    if t<0: raise ValueError('NEGATIVE_RADIUS')
    return t

def bilinear(F,u,v):
    if len(u)!=len(F) or len(v)!=len(F): raise ValueError('WRONG_VECTOR_SHAPE')
    return sum((rational(u[i])*F[i][j]*rational(v[j]) for i in range(len(F)) for j in range(len(F))),Q(0))

def support(H,u,v):
    n=len(H)
    if len(u)!=n or len(v)!=n: raise ValueError('WRONG_VECTOR_SHAPE')
    u=list(map(rational,u));v=list(map(rational,v))
    return sum((H[i][i]*abs(u[i]*v[i]) for i in range(n)),Q(0))+sum(
        (H[i][j]*abs(u[i]*v[j]+u[j]*v[i]) for i in range(n) for j in range(i+1,n)),Q(0))

def covariance(F,L):
    return [[bilinear(F,u,v) for v in L] for u in L]

def load_inputs(repo,contract):
    table=json.loads((repo/contract['inputs'][0]['path']).read_text())
    rounding=json.loads((repo/contract['inputs'][1]['path']).read_text())
    n=contract['science']['n']; half=rounding['halfULP']
    if len(table['packed'])!=n*(n+1)//2 or len(half)!=n*(n+1)//2: raise ValueError('UPPER_SIZE')
    H=[[Q(0)]*n for _ in range(n)]; k=0
    for i in range(n):
        for j in range(i,n):
            if rational(table['packed'][k])!=rational(table['matrix'][i][j]): raise ValueError('PARENT_PACKED_MATRIX_DISAGREEMENT')
            H[i][j]=H[j][i]=rational(half[k]);k+=1
    return validate(table['matrix'],H)

class PairTable:
    """One common integer unit; t=p/q predicates have no Fraction inner loops."""
    def __init__(self,F,H):
        self.n=len(F)
        scale=lcm(*(x.denominator for row in F+H for x in row))
        self.scale=scale
        A=[[int(x*scale) for x in row] for row in F];B=[[int(x*scale) for x in row] for row in H]
        self.diag=[(A[i][i],B[i][i]) for i in range(self.n)]
        self.pairs=[(i,j,A[i][i],B[i][i],A[j][j],B[j][j],abs(A[i][j]),B[i][j]) for i in range(self.n) for j in range(i+1,self.n)]
    def scan(self,t,all_failures=False):
        t=radius(t);p,q=t.numerator,t.denominator
        sf=[i for i,(a,h) in enumerate(self.diag) if a*q+h*p<0]
        failures=[]
        for i,j,a,ha,b,hb,c,hc in self.pairs:
            x=a*q+ha*p;y=b*q+hb*p;z=max(c*q-hc*p,0)
            if x<0 or y<0 or z*z>x*y:
                failures.append([i,j])
        return {'t':t,'singleton_count':self.n,'pair_count':len(self.pairs),
                'failed_singletons':sf,'failed_singleton_count':len(sf),'failed_pair_count':len(failures),
                'failed_pairs':failures if all_failures else failures[:1],
                'all_pass':not(sf or failures)}
    def witness(self,t,scan):
        t=radius(t)
        if scan['failed_singletons']:
            i=scan['failed_singletons'][0]; a,h=self.diag[i]
            return {'kind':'singleton','i':i,'upper_diagonal':Q(a,self.scale)+t*Q(h,self.scale)}
        if not scan['failed_pairs']: return None
        i,j=scan['failed_pairs'][0]
        a,ha=self.diag[i];b,hb=self.diag[j]
        row=next(r for r in self.pairs if r[:2]==(i,j));c,hc=row[-2:]
        x=Q(a,self.scale)+t*Q(ha,self.scale);y=Q(b,self.scale)+t*Q(hb,self.scale);z=max(Q(c,self.scale)-t*Q(hc,self.scale),Q(0))
        return {'kind':'pair','i':i,'j':j,'upper_a':x,'upper_b':y,'minimum_abs_off':z,'maximum_determinant':x*y-z*z}

def bracket(table):
    zero=table.scan(Q(0),True);one=table.scan(Q(1),True);checkpoints=[zero,one]
    if zero['all_pass']: return {'status':'ZERO_PAIR_THRESHOLD','lo':Q(0),'hi':Q(0),'iterations':0,'initial_width':Q(0),'witness_lo':None},checkpoints
    lo=Q(0);hi=Q(1);last=one
    while not last['all_pass'] and hi<4096:
        lo=hi;hi*=2;last=table.scan(hi);checkpoints.append(last)
    if not last['all_pass']:
        return {'status':'LOWER_BOUND_ONLY','lo':hi,'hi':None,'iterations':0,'witness_lo':table.witness(hi,last)},checkpoints
    width=hi-lo
    for _ in range(40):
        mid=(lo+hi)/2;check=table.scan(mid);checkpoints.append(check)
        if check['all_pass']: hi=mid
        else: lo=mid
    low=table.scan(lo);high=table.scan(hi)
    assert not low['all_pass'] and high['all_pass'] and hi-lo==width/Q(2**40)
    return {'status':'BRACKETED','lo':lo,'hi':hi,'initial_width':width,'iterations':40,
            'width':hi-lo,'witness_lo':table.witness(lo,low),'hi_all_pair_pass':True,
            'hi_is_full_PSD_upper_bound':False},checkpoints

def fixtures():
    F,H=validate([[4,0],[0,4]],[[1,1],[1,1]])
    L=[[Q(1),Q(1)],[Q(1),Q(-1)],[Q(-2),Q(0)]];q=[Q(1)]*3
    vertices=[]
    for signs in product((-1,1),repeat=3):
        C=[[F[0][0]+signs[0],Q(signs[1])],[Q(signs[1]),F[1][1]+signs[2]]]
        K=covariance(C,L)
        assert all(sum((K[i][j]*q[j] for j in range(3)),Q(0))==0 for i in range(3))
        vertices.append({'signs':list(signs),'cross':K[0][1],'var_u':K[0][0],'var_v':K[1][1],'K':K})
    assert support(H,L[0],L[1])==2 and max(v['cross'] for v in vertices)==2 and min(v['cross'] for v in vertices)==-2
    assert max(v['var_u'] for v in vertices)==max(v['var_v'] for v in vertices)==12
    assert max(v['var_u']+v['var_v'] for v in vertices)==20
    assert not any(v['var_u']==v['var_v']==12 for v in vertices)
    independent=[[Q(12),Q(0),Q(0)],[Q(0),Q(12),Q(0)],[Q(0),Q(0),Q(20)]]
    assert sum(bilinear(independent,q,q) for _ in [0])!=0
    G,J=validate([[1,-1,-1],[-1,1,-1],[-1,-1,1]],[[Q(1,10)]*3 for _ in range(3)])
    assert PairTable(G,J).scan(1)['all_pass']
    global_upper=bilinear(G,q,q)+support(J,q,q)
    assert global_upper==Q(-21,10)
    return {'sharp_shared_entry':{'support':Q(2),'loose_abs_support':Q(4),'vertices':vertices,
            'marginal_maxima':[12,12],'joint_sum_maximum':20,'simultaneous_maxima_attainable':False,
            'common_conservation_exact':True,'independent_covariance_rejected':True},
            'pair_pass_global_fail':{'all_pairs_pass':True,'upper_quadratic':global_upper,'global_PSD_impossible':True}}

def guards():
    results={}
    def reject(name,fn):
        try: fn()
        except ValueError: results[name]=True
        else: raise AssertionError('GUARD_DID_NOT_REJECT:'+name)
    reject('negative radius',lambda:radius(-1))
    reject('negative H',lambda:validate([[1]], [[-1]]))
    reject('nonsymmetric F',lambda:validate([[1,2],[0,1]], [[1,1],[1,1]]))
    reject('nonsymmetric H',lambda:validate([[1,0],[0,1]], [[1,1],[0,1]]))
    reject('nonsquare dimension',lambda:validate([[1,2]], [[1]]))
    reject('nonfinite token',lambda:rational('NaN'))
    reject('wrong vector shape',lambda:support([[Q(1)]],[],[1]))
    def case(name,F,H,t,expected):
        F,H=validate(F,H);actual=PairTable(F,H).scan(t)['all_pass'];assert actual==expected;results[name]=True
    case('negative singleton',[[-1]],[[0]],1,False)
    case('zero-H unrepairable pair',[[1,2],[2,1]],[[0,0],[0,0]],4096,False)
    case('t=0 pair pass',[[1,0],[0,1]],[[0,0],[0,0]],0,True)
    case('zero-crossing off interval',[[1,1],[1,1]],[[0,2],[2,0]],1,True)
    case('zero diagonal boundary',[[0,0],[0,1]],[[0,0],[0,0]],0,True)
    from evidence import check_input_blob
    reject('actual source identity mismatch',lambda:check_input_blob(b'altered',7,'0'*64))
    results['wrong independent consumer covariance']=True
    results['unattainable simultaneous marginal endpoints']=True
    return results
