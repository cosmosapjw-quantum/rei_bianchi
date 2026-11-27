"""R16 exact rational nonnegative-cubic preprocessing for an R15 B3 source.

This module is NOT a physical HD source/consumer certificate. It preserves the
source polynomial exactly, refines into nonnegative Bernstein-B3 cells, and
returns finite-budget failure rather than treating an unproved cell as positive.
No floats, least-squares, external solvers or hidden source completion.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, isqrt
import hashlib
import json
import re
from copy import deepcopy

MAX_INPUT_BITS = 256
MAX_DERIVED_BITS = 16384
DEFAULT_DEPTH = 256
DEFAULT_NODES = 16384
R15_MAX_SOURCE_CELLS = 16
R15_FORCING_SCHEMA = 'WU_R15_WHOLE_FORCING_V1'

class DomainError(ValueError):
    pass

class ResourceExceeded(RuntimeError):
    pass


def bitlen(x):
    v = Q(x)
    return max(abs(v.numerator).bit_length(), v.denominator.bit_length())


def rational(x, name='coefficient'):
    if isinstance(x, bool) or not isinstance(x, (int, str, Q)):
        raise DomainError(f'{name}: exact rational required (not float or bool)')
    if isinstance(x, str):
        if len(x)>2048 or re.fullmatch(r'[+-]?[0-9]+(?:/[+-]?[0-9]+)?',x) is None:
            raise DomainError(f'{name}: ASCII integer or p/q required')
        pair=x.split('/')
        if len(pair)==2 and int(pair[1])==0:
            raise DomainError(f'{name}: zero denominator')
        z=Q(int(pair[0]),int(pair[1])) if len(pair)==2 else Q(int(pair[0]))
    else: z=Q(x)
    if bitlen(z)>MAX_INPUT_BITS: raise DomainError(f'{name}: input >256 bits')
    return z


def bounded(v):
    z=Q(v)
    if bitlen(z)>MAX_DERIVED_BITS:
        raise ResourceExceeded('derived rational exceeds 16384 bits')
    return z


def row4(seq):
    if not isinstance(seq,(list,tuple)) or len(seq)!=4:
        raise DomainError('source row must have exactly four B3 coefficients')
    return tuple(rational(v,'B3') for v in seq)


def power3(b):
    b0,b1,b2,b3=b
    return (b0,3*(b1-b0),3*(b0-2*b1+b2),-b0+3*b1-3*b2+b3)


def evaluate(b,t):
    t=Q(t); a=list(b)
    for n in (3,2,1): a=[bounded((1-t)*a[i]+t*a[i+1]) for i in range(n)]
    return a[0]


def split(b,t):
    t=Q(t)
    if not 0<=t<=1: raise DomainError('split argument outside [0,1]')
    a=list(b);left=[a[0]];right=[a[-1]]
    while len(a)>1:
        a=[bounded((1-t)*a[i]+t*a[i+1]) for i in range(len(a)-1)]
        left.append(a[0]);right.append(a[-1])
    return tuple(left),tuple(right[::-1])


def restrict(b,left,right):
    l,r=Q(left),Q(right)
    if not 0<=l<r<=1: raise DomainError('restriction must be a nonempty [0,1] subinterval')
    suffix=b if l==0 else split(b,l)[1]
    return split(suffix,(r-l)/(1-l))[0]


def sign(x):
    return (x>0)-(x<0)


def sign_radical(a,b,d):
    """Exact sign of a+b*sqrt(d), where a,b,d are rational and d>=0."""
    a,b,d=Q(a),Q(b),Q(d)
    if d<0: raise DomainError('negative radical square')
    if b==0 or d==0: return sign(a)
    if a==0: return sign(b)
    if sign(a)==sign(b): return sign(a)
    cmp=sign(a*a-b*b*d)
    return sign(a) if cmp>0 else sign(b) if cmp<0 else 0


def sqrt_fraction_if_rational(d):
    d=Q(d)
    if d<0: return None
    a,b=isqrt(d.numerator),isqrt(d.denominator)
    return Q(a,b) if a*a==d.numerator and b*b==d.denominator else None


def stationary_data(p):
    """Return (location-if-rational-or-None, sign(value), interior, radical descriptor).
    Uses exact algebraic signs without any floating point approximation.
    """
    p0,p1,p2,p3=p
    A,B,C=3*p3,2*p2,p1
    if A==0:
        if B==0: return []
        r=-C/B
        return [(r,sign(p0+p1*r+p2*r*r), 0<r<1, None)]
    d=B*B-4*A*C
    if d<0:return []
    square=sqrt_fraction_if_rational(d)
    out=[]
    for s in (-1,1):
        if s==1 and d==0: continue
        positive_r=sign_radical(-B,Q(s),d)*sign(A)
        below_one=sign_radical(2*A+B,Q(-s),d)*sign(A)
        # P mod P' is rem0 + rem1*x, with x^2=(-Bx-C)/A.
        rem0=p0-p2*C/A+p3*B*C/(A*A)
        rem1=p1-p2*B/A+p3*(B*B/(A*A)-C/A)
        val_sign=sign_radical(rem0-rem1*B/(2*A),s*rem1/(2*A),d)
        r=(-B+s*square)/(2*A) if square is not None else None
        out.append((r,val_sign,positive_r>0 and below_one>0,(s,str(d))))
    return out


def classify_nonnegative(b):
    b=row4(b)
    p=power3(b)
    if p[0]<0 or sum(p)<0:
        raise DomainError('NEGATIVE: polynomial has a negative endpoint value')
    critical=stationary_data(p)
    if any(interior and sv<0 for _,sv,interior,_ in critical):
        raise DomainError('NEGATIVE: polynomial has a negative interior minimum')
    roots=sorted(set(r for r,sv,interior,_ in critical if interior and sv==0 and r is not None))
    # Rational cubics with an interior multiple root must have rational root.
    if any(interior and sv==0 and r is None for r,sv,interior,_ in critical):
        raise DomainError('UNRESOLVED: unexpected algebraic multiple root')
    return {'power':p,'critical':critical,'interior_zero_knots':roots}


def positive_partition(b,depth=DEFAULT_DEPTH,nodes=DEFAULT_NODES):
    b=row4(b)
    if isinstance(depth,bool) or not isinstance(depth,int) or not 0<=depth<=4096:
        raise DomainError('depth outside [0,4096]')
    if isinstance(nodes,bool) or not isinstance(nodes,int) or not 1<=nodes<=1000000:
        raise DomainError('nodes outside [1,1000000]')
    analysis=classify_nonnegative(b)
    knots=[Q(0)]+analysis['interior_zero_knots']+[Q(1)]
    stack=[(a,c,restrict(b,a,c),0) for a,c in zip(knots[:-1],knots[1:])][::-1]
    leaves=[];visits=0;splits=0;max_depth=0
    while stack:
        if visits >= nodes: raise ResourceExceeded(f'positive subdivision node budget {nodes} exhausted')
        a,c,control,k=stack.pop();visits+=1
        if min(control)>=0:
            leaves.append((a,c,control));max_depth=max(max_depth,k)
        else:
            if k>=depth: raise ResourceExceeded(f'positive subdivision depth {depth} exhausted')
            mid=(a+c)/2
            l,r=split(control,Q(1,2))
            stack.append((mid,c,r,k+1)); stack.append((a,mid,l,k+1));splits+=1
    assert len(leaves)==splits+len(knots)-1
    assert leaves[0][0]==0 and leaves[-1][1]==1
    assert all(a[1]==c[0] for a,c in zip(leaves,leaves[1:]))
    return {'leaves':leaves,'visits':visits,'splits':splits,'max_depth':max_depth,
            'exact_interior_zeros':analysis['interior_zero_knots'],
            'critical_points_checked':len(analysis['critical'])}


def _strings(xs):
    return [str(x) for x in xs]


def canonical_r15_hash(source,gr,ge,binding):
    data={'schema':R15_FORCING_SCHEMA,'source_id':binding['source_id'],
          'clock_id':binding['clock_id'],'clock_unit':binding['clock_unit'],
          'state_order':binding['state_order'],'source_knots':_strings(source),
          'g_r':[_strings(row) for row in gr],
          'g_e':[_strings(row) for row in ge]}
    return hashlib.sha256((json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()


def adapt_case_for_r15(case,depth=DEFAULT_DEPTH,nodes=DEFAULT_NODES,max_source_cells=R15_MAX_SOURCE_CELLS):
    """Convert signed-B3 but nonnegative whole-source case to R15-compatible B3.

    Requires the original binding and full-A certificate to match the original
    forcing hash. Rewrites ONLY the derived forcing representation digest in both;
    original source SHA, physical state/clock and full-A premises are not created.
    Returns new dict+lineage. Caller MUST run the unchanged R15 validate/run_case.
    """
    if not isinstance(case,dict): raise DomainError('input must be a JSON object')
    old=deepcopy(case)
    knots=[rational(x,'source_knot') for x in old['source_knots']]
    if len(knots)<2 or any(a>=b for a,b in zip(knots,knots[1:])):
        raise DomainError('source knots must increase')
    gr=[row4(row) for row in old['g_r']]
    ge=[row4(row) for row in old['g_e']]
    if len(gr)!=len(knots)-1 or len(ge)!=len(gr): raise DomainError('row/knots mismatch')
    bind=old['binding'];cert=old['certificate']
    if not isinstance(bind,dict) or not isinstance(cert,dict):
        raise DomainError('source binding and actual full-A certificate required')
    h=canonical_r15_hash(knots,gr,ge,bind)
    if bind.get('whole_forcing_hash_format')!=R15_FORCING_SCHEMA or cert.get('whole_forcing_hash_format')!=R15_FORCING_SCHEMA:
        raise DomainError('original R15 canonical hash format required')
    if bind.get('whole_forcing_source_sha256')!=h or cert.get('whole_forcing_source_sha256')!=h:
        raise DomainError('original forcing bytes/metadata not bound to canonical hash')
    if bind.get('source_sha256')!=cert.get('source_sha256'):
        raise DomainError('original native source identity differs between binding and certificate')
    refined=[knots[0]]; total_visits=0; total_splits=0
    for i,(a,c) in enumerate(zip(knots,knots[1:])):
        endpoints={a,c}
        for row in (gr[i],ge[i]):
            result=positive_partition(row,depth,nodes)
            total_visits+=result['visits'];total_splits+=result['splits']
            endpoints.update(a+(c-a)*r for l,r,_ in result['leaves'])
        for t in sorted(endpoints)[1:]:
            if t>refined[-1]: refined.append(t)
    if len(refined)-1>max_source_cells:
        raise ResourceExceeded('R15 maximum original source cells exceeded after exact refinement')
    new_gr=[];new_ge=[]
    j=0
    for a,c in zip(refined[:-1],refined[1:]):
        while knots[j+1]<=a: j+=1
        l=(a-knots[j])/(knots[j+1]-knots[j]);r=(c-knots[j])/(knots[j+1]-knots[j])
        g1=restrict(gr[j],l,r);g2=restrict(ge[j],l,r)
        if min(g1)<0 or min(g2)<0: raise AssertionError('internal positivity-equality error')
        new_gr.append(_strings(g1));new_ge.append(_strings(g2))
    old['source_knots']=_strings(refined)
    old['g_r']=new_gr;old['g_e']=new_ge
    newhash=canonical_r15_hash(refined,new_gr,new_ge,bind)
    old['binding']['whole_forcing_source_sha256']=newhash
    old['certificate']['whole_forcing_source_sha256']=newhash
    return old, {'schema':'WU_R16_EXACT_REPRESENTATION_TRANSFORM_V1',
                 'original_whole_forcing_hash':h,'refined_whole_forcing_hash':newhash,
                 'original_cells':len(knots)-1,'refined_cells':len(refined)-1,
                 'full_A_certificate_claim':'INHERITED_UNCHANGED_NOT_VERIFIED_BY_R16',
                 'mathematical_identity':'EXACT_BERNSTEIN_AFFINE_RESTRICTION',
                 'refinement_visits':total_visits,'refinement_splits':total_splits,
                 'native_source_sha256_unchanged':bind['source_sha256'],
                 'source_state_clock_binding_unchanged':True}


def _cli():
    import argparse
    from pathlib import Path
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--depth',type=int,default=DEFAULT_DEPTH)
    ap.add_argument('--nodes',type=int,default=DEFAULT_NODES)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError('create-only output already exists')
    case=json.loads(args.input.read_text())
    try:
        refined,lineage=adapt_case_for_r15(case,args.depth,args.nodes)
        result={'status':'EXACT_REPRESENTATION_PREPROCESSED_CONDITIONAL',
                'case_for_r15':refined,'lineage':lineage}
        rc=0
    except (DomainError,ResourceExceeded) as exc:
        result={'status':'REJECTED_OR_RESOURCE_LIMIT','type':type(exc).__name__,'reason':str(exc)}
        rc=2
    with args.output.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
    return rc

if __name__=='__main__': raise SystemExit(_cli())
