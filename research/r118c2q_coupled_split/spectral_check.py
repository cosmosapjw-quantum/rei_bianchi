"""Cell-moment ambiguity envelope for HeII absorption, independent of exponential closure.
Original fit threshold, physical E in eV, proper nH in cm^-3; sigma cm^2."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
I=D.parents[1]; B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124')
K=I/'research/r118c2k_segment'; M=I/'research/r118c2m_energy_budget'
C=2.99792458e10; T=54.42; bind=54.41776
def j(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def splus(E):
    x=np.asarray(E)/1.720
    return 1.369e4*(x-1)**2*x**(2.963/2-5.5)*(1+np.sqrt(x/32.88))**(-2.963)*1e-18
def sig(E):
    return np.where(np.asarray(E)>=T,splus(E),0.)
def bounds(a,b,m):
    assert 0<a<=m<=b and np.isfinite([a,b,m]).all()
    # exact degenerate moment forces a point measure
    if m==a or m==b:
        x=float(sig(m));p=float(m>=T);return x,x,p,p
    if b<T:return 0.,0.,0.,0.
    if a>=T:
        l=float(splus(m))
        u=float(((b-m)*splus(a)+(m-a)*splus(b))/(b-a))
        return l,u,1.,1.
    # a<T<=b, threshold discontinuity; lower infimum need not be attained.
    if m<=T:
        l=0.;u=float(splus(T)*(m-a)/(T-a))
        p0=0.;p1=(m-a)/(T-a)
    else:
        l=float(splus(b)*(m-T)/(b-T))
        u=float(((b-m)*splus(T)+(m-T)*splus(b))/(b-T))
        p0=(m-T)/(b-T);p1=1.
    return l,u,p0,p1
def mean(b):
    if b<1e-3:return .5-b/12+b**3/720-b**5/30240
    if b>700:return 1/b
    return 1/b-1/np.expm1(b)
def quad(n,u,lo,hi,scale,order):
    # Same mathematical maximum-entropy ansatz as native, different quadrature.
    m=lo+(u-lo*n)/n if u-lo*n<=hi*n-u else hi-(hi*n-u)/n
    assert lo<=m<=hi,(lo,m,hi,n,u)
    if lo==hi or m==lo or m==hi:return np.array([m*scale]),np.array([n]),m
    width=hi-lo;flip=m>(hi+lo)/2
    d=(hi-m if flip else m-lo)/width
    b=0. if d==.5 else brentq(lambda b:mean(b)-d,0,max(2.,2/d),xtol=1e-14)
    x,w=leggauss(order)
    norm=max(1.,b);end=min(norm,60.) if b>1 else 1.
    cuts=[0.,end]
    for edge in (T,1.05*T,1.2*T,2*T):
        p=((hi-edge/scale) if flip else (edge/scale-lo))/width*norm
        if 0<p<end:cuts.append(p)
    cuts.extend(map(float,np.arange(2.,end,2.)));cuts=sorted(set(cuts));yy=[];ww=[]
    for l,r in zip(cuts[:-1],cuts[1:]):
        y=(l+r)/2+(r-l)*x/2;yy.extend(y/norm);ww.extend((r-l)*w/2*np.exp(-b*y/norm))
    t=np.array(yy);w=np.array(ww);q=hi-width*t if flip else lo+width*t;w=n*w/w.sum()
    assert abs(w@q-u)<2e-12*u
    return q*scale,w,m

# V5: below-HeII support is half-open at the fit threshold; no atom may
# live at the cutoff in that pool. Above pool is closed at the threshold.
D=Path(__file__).resolve().parent
j0=j(D/'RESULTS.json')
rows={}
for name,v in j0['cases'].items():
    root=Path(v['segments'][-1]['raw_path']);exp=v['segments'][-1]['hashes']
    p=root/'checkpoint.txt';assert sha(p)==exp['checkpoint.txt'] and sha(root/'history.csv')==exp['history.csv']
    lines=p.read_text().splitlines();assert lines[0]=='AXBI_CHECKPOINT_V5'
    a=float(lines[1].split()[0]);scale=(1/21)/a
    h=np.genfromtxt(root/'history.csv',names=True,delimiter=',')[-1]
    nh=float(h['nH_proper_cm3'])
    def calculate(order):
        gamma=heat=low=high=0.;below_rate=0.;cross=0
        for idx in (4,11):
            n,u,lo,hi=[np.fromstring(lines[k],sep=' ') for k in range(idx,idx+4)]
            for ni,ui,l,r in zip(n,u,lo,hi):
                if ni==0:continue
                E,w,m=quad(ni,ui,l,r,scale,order)
                g=float(w@sig(E));ht=float(w@(sig(E)*(E-bind)))
                gamma+=g;heat+=ht
                if idx==4:
                    below_rate+=g
                else:
                    aa,bb,mm=l*scale,r*scale,m*scale
                    assert aa>=T-32*np.finfo(float).eps*T
                    if aa< T:cross+=1
                    # For physically threshold-labelled above pool, use smooth
                    # post-threshold fit. Tiny endpoint rounding is recorded.
                    ll=float(splus(mm));uu=ll if bb==aa else float(((bb-mm)*splus(aa)+(mm-aa)*splus(bb))/(bb-aa))
                    low+=ni*ll;high+=ni*uu
        fac=C*nh
        return np.array([fac*gamma,fac*heat,fac*low,fac*high,fac*below_rate]),cross
    v32,_=calculate(32);v64,cross=calculate(64)
    assert np.max(abs(v32[:2]/v64[:2]-1))<1e-8
    gamma,heat,low,high,below=v64
    rg=abs(gamma/float(h['Gamma_HeII'])-1);rh=abs(heat/(float(h['heat_HeII_erg'])/1.602176634e-12)-1)
    assert rg<2e-8 and rh<2e-8 and below<1e-12*gamma
    assert low<=gamma*(1+2e-8) and gamma<=high*(1+2e-8)
    row=dict(z=float(h['zbar']),gamma=float(gamma),heat=float(heat),gamma_lower=float(low),gamma_upper=float(high),width_relative=float((high-low)/gamma),native_gamma_relative=rg,native_heat_relative=rh,threshold_roundoff_cells=cross,checkpoint_sha=exp['checkpoint.txt'])
    rows[name]=row;print(name,row,flush=True)
(D/'SPECTRAL_CHECK.json').write_text(json.dumps(dict(status='PASS_SCOPED_V5_ENDPOINT_SPECTRUM',scope='fixed represented above-pool support and N/U; no ambiguity across pool membership; not true spectrum or history error bound',cases=rows),indent=2)+'\n')
