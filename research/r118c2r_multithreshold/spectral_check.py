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

# V6 exact native rate comparison: all active bands, all three species, independent GL.
D=Path(__file__).resolve().parent
FIT=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
BIND=np.array([13.598434599702,24.587389011,54.41776])
def cross(E,p):
    eth,e0,s0,ya,power,yw,y0,y1=p;x=np.asarray(E)/e0-y0;y=np.sqrt(x*x+y1*y1)
    return np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(power/2-5.5)*(1+np.sqrt(y/ya))**(-power)*1e-18,0.)
rows={}
for name,v in j(D/'RESULTS.json')['cases'].items():
    r=v['segments'][-1];root=Path(r['raw_path']);exp=r['hashes'];p=root/'checkpoint.txt'
    assert sha(p)==exp['checkpoint.txt'] and sha(root/'history.csv')==exp['history.csv']
    lines=p.read_text().splitlines();assert lines[0]=='AXBI_CHECKPOINT_V6'
    scale=(1/21)/float(lines[1].split()[0]);h=np.genfromtxt(root/'history.csv',names=True,delimiter=',')[-1];fac=C*h['nH_proper_cm3']
    def calc(order):
        g=np.zeros((3,3));heat=np.zeros_like(g);low=high=0.
        for row,idx in enumerate((4,15,11)):
            n,u,lo,hi=[np.fromstring(lines[k],sep=' ') for k in range(idx,idx+4)]
            for ni,ui,l,r in zip(n,u,lo,hi):
                if ni==0:continue
                E,w,m=quad(ni,ui,l,r,scale,order)
                for i,f in enumerate(FIT):
                    ss=cross(E,f);g[row,i]+=w@ss;heat[row,i]+=w@(ss*(E-BIND[i]))
                if row==2:
                    aa,bb,mm=l*scale,r*scale,m*scale
                    assert aa>=T-32*np.finfo(float).eps*T
                    ll=float(splus(mm));uu=ll if aa==bb else float(((bb-mm)*splus(aa)+(mm-aa)*splus(bb))/(bb-aa))
                    low+=ni*ll;high+=ni*uu
        return fac*g,fac*heat,fac*low,fac*high
    g32,h32,_,_=calc(32);g64,h64,lo,hi=calc(64);g=g64.sum(axis=0);heat=h64.sum(axis=0)
    native=np.array([h[k] for k in ('Gamma_HI','Gamma_HeI','Gamma_HeII')]);native_h=np.array([h[k] for k in ('heat_HI_erg','heat_HeI_erg','heat_HeII_erg')])/1.602176634e-12
    rg=float(np.max(abs(g/native-1)));rh=float(np.max(abs(heat/native_h-1)))
    gl=float(max(np.max(abs(g32.sum(axis=0)/g-1)),np.max(abs(h32.sum(axis=0)/heat-1))))
    assert rg<2e-8 and rh<2e-8 and gl<2e-8
    assert g64[0,1]<1e-12*g[1] and g64[0,2]+g64[1,2]<1e-12*g[2]
    assert lo<=g[2]*(1+2e-8) and g[2]<=hi*(1+2e-8)
    row=dict(z=float(h['zbar']),gamma=g.tolist(),heat_ev=heat.tolist(),by_band_gamma=g64.tolist(),by_band_heat=h64.tolist(),max_native_gamma_relative=rg,max_native_heat_relative=rh,max_GL_gap=gl,heii_interval=[float(lo),float(hi)],heii_width_relative=float((hi-lo)/g[2]),checkpoint_sha=exp['checkpoint.txt'])
    rows[name]=row;print(name,row,flush=True)
(D/'SPECTRAL_CHECK.json').write_text(json.dumps(dict(status='PASS_SCOPED_ALL_SPECIES_V6_ENDPOINT',scope='same represented moment closure with independent GL32/64 and exact provider fit; HeII bounds only fixed N/U/support, not history error',cases=rows),indent=2)+'\n')
