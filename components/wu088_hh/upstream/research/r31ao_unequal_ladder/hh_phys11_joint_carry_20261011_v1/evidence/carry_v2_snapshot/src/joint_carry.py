"""PHYS11 exact mixed carry algebra over saved full seven-coordinate Jets.

The four carry slots are value,U,V,W, with no 1/2 on the mixed slot.
This is an offline enclosure algebra, not a native state or solver adapter.
"""
from fractions import Fraction as Q
from exact_weighted import E, dot, bits

Z=E.point(0)
O=E.point(1)
KEYS=('value','U','V','W')

def exact_input(obj):
    p=obj['exact']
    if set(p)!={'lo','hi'}:raise ValueError('EXACT_ENDPOINT_LAYOUT')
    z=E(Q(int(p['lo'][0]),int(p['lo'][1])),Q(int(p['hi'][0]),int(p['hi'][1])))
    s=z.serial()
    if any(s[k]!=obj[k] for k in ('lo_bits','hi_bits','sign')):raise ValueError('EXACT_DISPLAY_MISMATCH')
    if bits(float(obj['lo']))!=s['lo_bits'] or bits(float(obj['hi']))!=s['hi_bits']:raise ValueError('DISPLAY_BITS')
    return z

def jzero():return {'v':Z,'g':[Z]*7,'h':[[Z]*7 for _ in range(7)]}

def jread(obj):
    if len(obj['gradient'])!=7 or len(obj['signed_hessian'])!=7 or any(len(r)!=7 for r in obj['signed_hessian']):raise ValueError('JET_DIMENSION')
    return {'v':E.saved(obj['value']),'g':[E.saved(x) for x in obj['gradient']],
            'h':[[E.saved(x) for x in r] for r in obj['signed_hessian']]}

def jscale(j,a):return {'v':a*j['v'],'g':[a*x for x in j['g']],'h':[[a*x for x in r] for r in j['h']]}

def jadd(a,b):return {'v':a['v']+b['v'],'g':[x+y for x,y in zip(a['g'],b['g'],strict=True)],
                      'h':[[x+y for x,y in zip(r,s,strict=True)] for r,s in zip(a['h'],b['h'],strict=True)]}

def jlinear(js,cs):
    out=jzero()
    for j,c in zip(js,cs,strict=True):out=jadd(out,jscale(j,c))
    return out

def carry(value=Z,U=Z,V=Z,W=Z):return dict(zip(KEYS,(value,U,V,W),strict=True))
def cscale(c,a):return {k:a*c[k] for k in KEYS}
def cadd(a,b):return {k:a[k]+b[k] for k in KEYS}
def csub(a,b):return cadd(a,cscale(b,-O))

def cmul(a,b):
    return carry(a['value']*b['value'],a['U']*b['value']+a['value']*b['U'],
                 a['V']*b['value']+a['value']*b['V'],
                 a['W']*b['value']+a['U']*b['V']+a['V']*b['U']+a['value']*b['W'])

def cquotient(a,b):
    d=b['value']
    if d.lo<=0:raise ValueError('NONPOSITIVE_QUOTIENT_DENOMINATOR')
    d2=d*d;d3=d2*d
    return carry(a['value']/d,
                 a['U']/d-a['value']*b['U']/d2,
                 a['V']/d-a['value']*b['V']/d2,
                 a['W']/d-(a['U']*b['V']+a['V']*b['U']+a['value']*b['W'])/d2
                 +2*a['value']*b['U']*b['V']/d3)

def total(j,u,v,w):
    if any(len(a)!=4 for a in (u,v,w)):raise ValueError('GAS_CARRY_DIMENSION')
    mixed=dot(j['g'][:4],w)
    mixed+=sum((j['h'][i][k]*u[i]*v[k] for i in range(4) for k in range(4)),Z)
    mixed+=dot([j['h'][i][4] for i in range(4)],v)
    mixed+=dot([j['h'][i][5] for i in range(4)],u)+j['h'][4][5]
    return carry(j['v'],dot(j['g'][:4],u)+j['g'][4],dot(j['g'][:4],v)+j['g'][5],mixed)

def intersect(a,b):
    if not a.overlap(b):raise ValueError('EMPTY_SAME_FAMILY_INTERSECTION')
    return E(max(a.lo,b.lo),min(a.hi,b.hi))

def cintersect(a,b):return {k:intersect(a[k],b[k]) for k in KEYS}
def cserial(c):return {k:c[k].serial() for k in KEYS}
def mag(x):return max(abs(x.lo),abs(x.hi))
