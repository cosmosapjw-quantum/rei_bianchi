"""Independent Decimal80 VALUES of the frozen rational absorption functional.

No analytic derivative or derivative increment is used here. Binary64 primitive
inputs are lifted exactly; perturbations and all arithmetic remain Decimal.
"""
from decimal import Decimal, localcontext
from opacity_native import C_CM_S, EV_ERG, CHEMICAL_CHI_EV

def D(value):return Decimal.from_float(float(value))

def values(q,p,R,h,sigma,g,gas,direction=None,epsilon=0.):
    with localcontext() as ctx:
        ctx.prec=80
        zero=Decimal(0);one=Decimal(1)
        y=[D(x) for x in gas]
        if direction is not None:y=[x+D(epsilon)*D(d) for x,d in zip(y,direction)]
        x,y1,y2,w=y
        if not (zero<=x<=one and y1>=zero and y2>=zero and y1+y2<=one and w>zero):
            raise ValueError('DECIMAL_GAS_TRIAL_OUTSIDE_DOMAIN')
        nh,ne=D(g['nH']),D(g['nHe']);V=D(g['a_rel'])**3
        lower=[nh*(one-x),ne*(one-y1-y2),ne*y1]
        hh,rr,cc=D(h),D(R),D(C_CM_S);chi=[D(z) for z in CHEMICAL_CHI_EV]
        n=zero;u=zero;count=[zero]*3;heat=[zero]*3;K0=[zero]*3;KE=[zero]*3
        for qi,pi,sig in zip(q,p,sigma):
            E=rr*D(qi);P=D(pi);cross=[cc*D(z) for z in sig]
            rates=[c*density for c,density in zip(cross,lower)]
            den=one+hh*sum(rates,zero);survive=P/den
            absorbed=[hh*rate*P/den for rate in rates]
            n+=survive;u+=E*survive
            for j in range(3):
                count[j]+=absorbed[j];heat[j]+=(E-chi[j])*absorbed[j]
                K0[j]+=cross[j]*survive;KE[j]+=E*cross[j]*survive
        bind=[a*b for a,b in zip(count,chi)]
        gamma=[z/V for z in K0];perheat=[(e-c*k)/V for e,c,k in zip(KE,chi,K0)]
        work=2*D(g['H'])*D(EV_ERG)*nh*V*w
        return [n,u]+count+bind+heat+K0+KE+gamma+perheat+[work,zero]

def difference(baseline,plus,other,epsilon,mode):
    with localcontext() as ctx:
        ctx.prec=80;e=D(epsilon)
        if mode=='right':return [(-3*b+4*p-o)/(2*e) for b,p,o in zip(baseline,plus,other)]
        return [(p-m)/(2*e) for p,m in zip(plus,other)]
