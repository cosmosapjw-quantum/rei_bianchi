"""Independent angular-envelope quadrature for a threshold root, not PR105 code."""
import mpmath as mp
from fractions import Fraction as F
from pathlib import Path

p=[(F(46),F('.11')),(F(61),F('.11')),(F(73),F('.02')),(F(87),F('.14'))]

def lines(L,a,b):
    mid=(a+b)/2
    z=[(F(0),F(0))]
    for t,v in p:
        s=1 if mid>=t else -1
        z.append((v+L*s*t,-L*s))
    return z

def pieces(L):
    breaks=sorted({F(0),F(90)}|{t for t,_ in p})
    result=[]
    for a,b in zip(breaks,breaks[1:]):
        candidates=lines(L,a,b); knots={a,b}
        for i,(c,d) in enumerate(candidates):
            for e,f in candidates[i+1:]:
                if d!=f:
                    t=(e-c)/(d-f)
                    if a<t<b:knots.add(t)
        xs=sorted(knots)
        for x,y in zip(xs,xs[1:]):
            c,d=max(candidates,key=lambda cd:cd[0]+cd[1]*(x+y)/2)
            result.append((x,y,c,d))
    return result

def mpr(x):return mp.mpf(x.numerator)/x.denominator

def I_lower(L,dps=70):
    L=F(L)
    with mp.workdps(dps):
        k=mp.pi/180
        def anti(x,a,b):
            x,a,b=map(mpr,(x,a,b))
            return -(a+b*x)*mp.cos(k*x)/k+b*mp.sin(k*x)/(k*k)
        return mp.fsum(4*mp.pi*k*(anti(y,a,b)-anti(x,a,b)) for x,y,a,b in pieces(L))

if __name__=='__main__':
    with mp.workdps(75):
        lo=mp.mpf('0.0049');hi=mp.mpf('0.005')
        target=mp.mpf('1.0075')
        for i in range(140):
            mid=(lo+hi)/2
            val=I_lower(str(mid),80)
            if val>target:lo=mid
            else:hi=mid
        print('Lcrit interval',mp.nstr(lo,55),mp.nstr(hi,55))
        print('Icrit',mp.nstr(I_lower(str((lo+hi)/2),80),50))
        print('I(1/200)',mp.nstr(I_lower('0.005',80),55))
