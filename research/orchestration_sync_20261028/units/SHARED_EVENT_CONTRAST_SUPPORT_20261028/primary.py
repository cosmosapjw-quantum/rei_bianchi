"""Exact finite support and separately typed numerical-error composition."""
from fractions import Fraction as F

def exact(x):
    if isinstance(x,bool) or not isinstance(x,(str,int,F)):raise ValueError('EXACT_STRING_OR_INTEGER_REQUIRED')
    return F(x)
def vec(x):
    if not isinstance(x,(tuple,list)) or not 1<=len(x)<=10:raise ValueError('VECTOR_DIMENSION')
    return [exact(v) for v in x]
def mat(x):
    if not isinstance(x,(tuple,list)) or not 1<=len(x)<=10:raise ValueError('MATRIX_DIMENSION')
    a=[vec(r) for r in x]
    if any(len(r)!=len(a[0]) for r in a):raise ValueError('RAGGED_MATRIX')
    return a
def dot(a,b):
    if len(a)!=len(b):raise ValueError('DIMENSION_MISMATCH')
    return sum((x*y for x,y in zip(a,b)),F(0))
def mm(a,b):
    if len(a[0])!=len(b):raise ValueError('DIMENSION_MISMATCH')
    return [[dot(r,c) for c in zip(*b)] for r in a]
def affine_support(A,B,r0,R,l,U):
    A,B,R,U=map(mat,(A,B,R,U));r0,l=map(vec,(r0,l))
    if len(B[0])>8 or len(A[0])!=len(r0) or len(B)!=len(r0) or len(R)!=len(l) or len(U)!=len(l):raise ValueError('DIMENSION_MISMATCH')
    if any(dot(l,c) for c in zip(*U)):raise ValueError('NUISANCE_NOT_ANNIHILATED')
    c=mm([l],R)[0];ab=mm(A,B);ca=mm([c],A)[0];latent=mm([c],ab)[0]
    central=dot(ca,r0);hc=sum(map(abs,latent),F(0));hb=sum((abs(ci)*sum(map(abs,row),F(0)) for ci,row in zip(c,ab)),F(0));w=[F(1 if x>0 else -1 if x<0 else 0) for x in latent]
    if hc>hb:raise AssertionError('TRIANGLE_FAILURE')
    return {'central':central,'correlated_radius':hc,'independent_box_radius':hb,'latent_coefficients':latent,'positive_witness':w,'lower':central-hc,'upper':central+hc,'c':c,'AB':ab}
def finite_support(vertices,coefficients):
    if not 1<=len(vertices)<=35:raise ValueError('VERTEX_COUNT')
    v=[vec(x) for x in vertices];c=vec(coefficients);values=[dot(c,x) for x in v]
    return {'minimum':min(values),'maximum':max(values),'values':values,'min_vertex':v[values.index(min(values))],'max_vertex':v[values.index(max(values))],'completeness':'SUPPLIED_COMPLETE_VERTEX_LIST_PREMISE'}
def covariance_projection(V,c,*,validated_psd=False):
    V=mat(V);c=vec(c)
    if len(V)!=len(c) or len(V[0])!=len(c):raise ValueError('COVARIANCE_DIMENSION')
    value=sum((c[i]*V[i][j]*c[j] for i in range(len(c)) for j in range(len(c))),F(0))
    return {'contraction':value,'role':'COVARIANCE_OF_DECLARED_VALIDATED_PSD_INPUT' if validated_psd else 'ALGEBRAIC_CONTRACTION_ONLY','hard_support_inferred':False}
def numerical_scalar_bound(k_cross,zeta,Gamma,rho,deltaJ,eta,dual_norm_upper,identity):
    vals=list(map(exact,(k_cross,zeta,Gamma,rho,deltaJ,eta,dual_norm_upper)))
    if any(v<0 for v in vals):raise ValueError('NEGATIVE_BOUND_TERM')
    if not isinstance(identity,dict) or set(identity)!= {'expected','actual'}:raise ValueError('IDENTITY_PAIR_REQUIRED')
    keys={'source','clock','metric','state','rates','weights','units'}
    if not isinstance(identity['actual'],dict) or not isinstance(identity['expected'],dict) or not keys<=set(identity['actual']) or not keys<=set(identity['expected']) or identity['actual']!=identity['expected']:raise ValueError('SOURCE_CLOCK_METRIC_STATE_RATE_WEIGHT_UNIT_MISMATCH')
    k,z,g,r,d,e,n=vals;epsilon=k*z+g*r*r+d*r+e
    return {'epsilon':epsilon,'projected_bound':n*epsilon,'identity':identity,'assumption':'Supplied dual-norm upper bound and compatible component bounds, no actual response inferred'}
