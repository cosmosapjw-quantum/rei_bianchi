"""New PHYS07 primitive/Jet checks; independent Decimal analytic observations.

The exact rational series argument establishes enclosure semantics; Decimal
comparisons are independent numerical error detectors, not enclosure proofs.
No existing scientific suite or native callback is imported or executed.
"""
import json
import sys
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from certified_interval import I, J, outward, pow2, PRECISION_BITS, LOG_TERMS, EXP_TERMS

count = 0
rejected = 0


def check(condition, name):
    global count
    count += 1
    if not condition:
        raise AssertionError(name)


def reject(fn, name):
    global rejected
    try:
        fn()
    except (ValueError, ZeroDivisionError):
        rejected += 1
        check(True, name)
    else:
        check(False, name)


def dec(x):
    x = F(x)
    return D(x.numerator)/D(x.denominator)


def observed_inside(iv, observation, name):
    check(dec(iv.lo) <= observation <= dec(iv.hi), name)


def analytic(x, y, p):
    # Independent log-derivative formulas; no Jet operations here.
    u = (x-y).exp()*(p*x.ln()).exp()/y
    lx, ly = 1+p/x, -1-1/y
    v = x.ln()*y*y
    d = 2+x*y
    value = u+v+1/d
    gx = u*lx+y*y/x-y/(d*d)
    gy = u*ly+2*y*x.ln()-x/(d*d)
    hxx = u*(lx*lx-p/(x*x))-y*y/(x*x)+2*y*y/(d*d*d)
    hxy = u*lx*ly+2*y/x-1/(d*d)+2*x*y/(d*d*d)
    hyy = u*(ly*ly+1/(y*y))+2*x.ln()+2*x*x/(d*d*d)
    return value, [gx, gy], [[hxx, hxy], [hxy, hyy]]


def build(x, y):
    return (x-y).exp()*x.powf(1.503)/y+x.log()*y*y+1/(2+x*y)


for q in [F(0), F(1,3), F(-1,3), F(10)**70/F(7), F(-11,2**900),
          F(2**300+1,2**170+3), F.from_float(13.5984), F.from_float(5e-324)]:
    lo, hi = outward(q), outward(q, True)
    check(lo <= q <= hi, 'directed rational rounding')
    check(lo <= hi, 'round order')
    if q:
        check((hi-lo)/abs(q) <= pow2(2-PRECISION_BITS), 'relative quantum bound')

interval_pairs = [(I(-2,3), I(F(1,3),F(7,5))),
                  (I(F(1,11),F(7,3)), I(-5,-2)),
                  (I(0,F(1,10)), I(2,4)),
                  (I(F(-1,10),F(1,10)), I(F(1,7),F(2,7)))]
for a,b in interval_pairs:
    for x in [a.lo,a.midpoint(),a.hi]:
        for y in [b.lo,b.midpoint(),b.hi]:
            check((a+b).contains(x+y), 'sum exact sample')
            check((a-b).contains(x-y), 'difference exact sample')
            check((a*b).contains(x*y), 'product exact sample')
            check((a/b).contains(x/y), 'quotient exact sample')
            check((a**2).contains(x*x), 'square exact sample')

with localcontext() as context:
    context.prec = 85
    for q in map(F, ['-30','-3','-0.125','0','0.03125','0.125','0.5','1','7','30']):
        observed_inside(I(q).exp(),dec(q).exp(),'exp Decimal85')
    for q in [F(1,10**10),F(5,7),F(1),F(7,3),F(50000),F(1263030)]:
        observed_inside(I(q).log(),dec(q).ln(),'log Decimal85')
        check(I(q).log().exp().contains(q),'exp(log(q)) rational identity')
    for q in [F(0),F(1,7),F(2),F(4),F(50000),F(10)**100]:
        s=I(q).sqrt()
        check(s.lo*s.lo <= q <= s.hi*s.hi,'sqrt exact squared bracket')
        observed_inside(s,dec(q).sqrt(),'sqrt Decimal85')
    for q,p in [(F(50000),1.2),(F(315614,50000),-1.089),(F(570670,50000),0.654),
                (F(3,2),1.503),(F(5,7),-1.5)]:
        observed_inside(I(q).powf(p),(dec(F.from_float(p))*dec(q).ln()).exp(),'power Decimal85')

    x0,y0=F(3,2),F(7,4)
    value=build(J.variable(I(x0),0,n=2),J.variable(I(y0),1,n=2))
    av,ag,ah=analytic(dec(x0),dec(y0),dec(F.from_float(1.503)))
    observed_inside(value.v,av,'point value independent formula')
    for i in range(2):
        observed_inside(value.g[i],ag[i],'point gradient independent formula')
        for j in range(2):
            observed_inside(value.h[i][j],ah[i][j],'point Hessian independent formula')

    xb,yb=I(F(7,5),F(8,5)),I(F(8,5),F(19,10))
    value=build(J.variable(xb,0,n=2),J.variable(yb,1,n=2))
    for xp in [xb.lo,xb.midpoint(),xb.hi]:
        for yp in [yb.lo,yb.midpoint(),yb.hi]:
            av,ag,ah=analytic(dec(xp),dec(yp),dec(F.from_float(1.503)))
            observed_inside(value.v,av,'box value independent observation')
            for i in range(2):
                observed_inside(value.g[i],ag[i],'box gradient independent observation')
                for j in range(2):
                    observed_inside(value.h[i][j],ah[i][j],'box Hessian independent observation')

# Analytic second derivatives at zero value, with nonzero incoming mixed carry.
x=J.variable(I(0),0,n=2)
y=J.variable(I(0),1,n=2)
z=(2+x+3*y+x*y)**3
check(z.v.contains(8),'polynomial value at zero')
check(z.g[0].contains(12) and z.g[1].contains(36),'polynomial gradients')
check(z.h[0][0].contains(12) and z.h[1][1].contains(108),'polynomial pure Hessian')
check(z.h[0][1].contains(48),'polynomial mixed Hessian including inner carry')

for fn,name in [(lambda:I(1,-1),'reversed box'),(lambda:I(float('nan')),'nonfinite'),
                (lambda:1/I(-1,1),'zero denominator'),(lambda:I(0,1).log(),'zero log'),
                (lambda:I(-1).sqrt(),'negative sqrt'),(lambda:I(1).exp()*I(1025).exp(),'exp budget'),
                (lambda:J.variable(I(1),3,n=2),'bad slot'),
                (lambda:J.constant(1,n=2)+J.constant(1,n=3),'jet shape mismatch')]:
    reject(fn,name)

print(json.dumps({'schema':'WU088_HH_PHYS07_CERTIFIED_REFERENCE_CHECKS_V1',
                  'status':'PASS','assertions':count,'intentional_rejections':rejected,
                  'precision_bits':PRECISION_BITS,'log_terms':LOG_TERMS,'exp_terms':EXP_TERMS,
                  'decimal_observation_precision':85,
                  'proof_basis':'rational directed arithmetic and explicit positive-series tails',
                  'numeric_oracle_scope':'independent Decimal observations and analytic derivative formulas; not a rigorous Decimal error bound',
                  'native_callbacks':0,'native_endpoints':0,'native_roots':0,'IVP':0,'old_suite_replays':0},indent=2))
