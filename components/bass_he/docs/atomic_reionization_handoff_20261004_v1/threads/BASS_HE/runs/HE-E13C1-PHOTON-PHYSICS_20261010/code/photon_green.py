"""Retarded photon number/energy integrals, independently evaluated at high precision.

This is not a native IEEE-emulator and not an atomic-fit error certificate.
Inputs converted by lift() retain their stored binary64 value exactly.
"""
import mpmath as mp

PARAMS = ((.4298,5.475e4,32.88,2.963,0.,0.,0.),
          (13.61,949.2,1.469,3.188,2.039,.4434,2.136),
          (1.720,1.369e4,32.88,2.963,0.,0.,0.))
CUTOFF=(13.6,24.59,54.42)

def lift(x):
    if isinstance(x,mp.mpf): return x
    if isinstance(x,int): return mp.mpf(x)
    n,d=float(x).as_integer_ratio()
    return mp.mpf(n)/d

def kernel(f,q,rates,h,e):
    if len(rates)!=3: raise ValueError('three absorber coefficients required')
    f,q,h,e=map(lift,(f,q,h,e)); lam=list(map(lift,rates))
    if not all(mp.isfinite(x) and x>=0 for x in (f,q,h,e,*lam)) or e<=0:
        raise ValueError('invalid photon kernel domain')
    L=sum(lam); z=L*h; eps=lift(1.602176634e-12)
    # Integral representation of 1F1 has a positive integrand on these arguments.
    def J(a): return h*mp.hyp1f1(1,2,-a*h)
    n_initial=f*mp.exp(-z); n_born=q*J(L)
    CN0=f*J(L); CNq=q*h*h*mp.hyp1f1(1,3,-z)/2
    CE0=f*J(L+1)
    if L==0:
        born_E=h*h*mp.hyp1f1(2,3,-h)/2
    elif abs(z)<mp.mpf('1e-25'):
        # Rare limiting-control lane, avoid an ill-conditioned divided difference.
        born_E=mp.quad(lambda t: mp.exp(-t)*t*mp.hyp1f1(1,2,-L*t),[0,h])
    else:
        born_E=(J(1)-J(L+1))/L
    CEq=q*born_E
    n=n_initial+n_born; C=CN0+CNq; ER=eps*e*(CE0+CEq)
    return {'n':n,'u':eps*e*mp.exp(-h)*n,
            'A':[l*C for l in lam],'B':[l*ER for l in lam],
            'red':ER,'qn':q*h,'qe':eps*e*q*J(1),
            'A_initial':[l*CN0 for l in lam],'A_born':[l*CNq for l in lam],
            'B_initial':[l*eps*e*CE0 for l in lam],
            'B_born':[l*eps*e*CEq for l in lam], 'eps':eps}

def sigma(species,e):
    e=lift(e)
    if species not in (0,1,2) or not mp.isfinite(e) or e<0 or e>50000:
        raise ValueError('Verner source domain')
    if e<lift(CUTOFF[species]): return mp.mpf(0)
    e0,s0,ya,p,yw,y0,y1=map(lift,PARAMS[species])
    x=e/e0-y0; y=mp.sqrt(x*x+y1*y1)
    return mp.exp(mp.log(s0)+mp.log((x-1)**2+yw*yw)
                  +(p/2-mp.mpf('5.5'))*mp.log(y)
                  -p*mp.log1p(mp.sqrt(y/ya))+mp.log(lift(1e-18)))

def coefficients(energy,nh,nhe,H,gas,source_rate,emin,emax,source_on):
    e,nh,nhe,H,rate,emin,emax=map(lift,(energy,nh,nhe,H,source_rate,emin,emax))
    x,y,z=map(lift,gas)
    if H<=0 or nh<=0 or nhe<0 or not(0<=x<=1 and y>=0 and z>=0 and y+z<=1):
        raise ValueError('invalid gas/background input')
    target=[nh*(1-x),nhe*(1-y-z),nhe*y]
    lambdas=[lift(2.99792458e10)*target[i]*sigma(i,e)/H for i in range(3)]
    q=rate/((1/emin-1/emax)*e*H) if source_on else mp.mpf(0)
    return lambdas,q
