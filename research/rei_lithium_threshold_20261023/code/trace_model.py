"""ANGTHERM02 reconstructed candidate; frozen conditional trace equations."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
from scipy.interpolate import CubicHermiteSpline,PchipInterpolator
from scipy.optimize import brentq
BASE=Path(__file__).resolve().parents[1]
DONOR=BASE.parent/'rei_angular_thermochemistry_20261023'
if not DONOR.exists(): DONOR=BASE/'donor/rei_angular_thermochemistry_20261023'
sys.path.insert(0,str(DONOR/'code'))
from angular_model import Reduced,Background,thermal,ATOM,CT,NN,VGRAD,C,END
G0=.05;YLI=5.0001e-10;DELTA=2e-8;SIGMA_MAX=1.66e-18;STAR_INDEX=11
CHI=np.array([5.392,75.64,122.5]);BIND=np.r_[0.,np.cumsum(CHI)];CHARGE=np.arange(4.)
DRIVER_PATH=BASE/'inputs/bath_drivers.npz'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sigma(e): return ATOM.provider.sigma('LiI',np.asarray(e))*1e-18
def energy(t,mu,b):
    mu=np.asarray(mu)
    return 10*np.exp(-t+.5*np.log1p((1-mu*mu)*np.expm1(2*b)+mu*mu*np.expm1(-4*b)))
def support(t,b):
    e0,e1=energy(t,np.array([0.,1.]),b)
    if min(e0,e1)>=CHI[0]: return 0.,1.
    if max(e0,e1)<=CHI[0]: return 0.,0.
    mu=math.sqrt((np.expm1(2*(math.log(CHI[0]/10)+t))-np.expm1(2*b))/(np.expm1(-4*b)-np.expm1(2*b)))
    return (0.,mu) if b>0 else (mu,1.)
class Rates:
    def __init__(self):
        self.bg=Background('grid044')
        self.rules={}
        for m in [4,8,16,32]:
            x,w=np.polynomial.legendre.leggauss(m);self.rules[m]=((x+1)/2,w/2)
        self.endpoint_roots=sorted(brentq(lambda t:float(energy(t,mu,self.bg.fields(t)[2])-CHI[0]),0.,END,xtol=5e-15) for mu in [0.,1.])
    def coefficients(self,t,kind='split',M=16,tau=None,segment=None):
        h,n,b,bp=self.bg.fields(t);st,sb=t,b
        if kind=='fixed' and segment is not None and t in segment:
            lo,hi=segment;toward=hi if t==lo else lo
            st=t+math.copysign(min(1e-12,(hi-lo)*1e-8),toward-t);sb=self.bg.fields(st)[2]
        x,w=self.rules[M]
        if kind=='split':
            lo,hi=support(t,b);mu=lo+(hi-lo)*x;weights=(hi-lo)*w
        else: mu,weights=x,w
        e=energy(t,mu,b);k=C*n/h*sigma(energy(st,mu,sb));counts=G0*weights
        if tau is not None: counts=counts*np.exp(-tau)
        wk=counts*k
        return float(wk.sum()),float((e*wk).sum()),k,e,wk,weights
    def fixed_crossings(self,M):
        return sorted(brentq(lambda t:float(energy(t,mu,self.bg.fields(t)[2])-CHI[0]),0.,END,xtol=5e-15) for mu in self.rules[M][0])
def build_drivers():
    model=Reduced(M=16);src=DONOR/'results/grid044_M16_tight.npz'
    with np.load(src,allow_pickle=False) as d:
        t=d['accepted_eta'].copy();Y=d['accepted_Y'].copy();rt=d['eta'].copy();rf=d['fractions'].copy()
        tau=d['Y'][model.gx,11].copy()[:16];logs=d['photon_log_counts'][16:,11].copy()
    v=VGRAD@Y[:9];T=Y[model.iu]/(CT*(NN+v))
    rhs=np.column_stack([model.rhs(float(ti),yi) for ti,yi in zip(t,Y.T)])
    vp=VGRAD@rhs[:9];ltp=rhs[model.iu]/Y[model.iu]-vp/(NN+v);lvp=vp/v
    DRIVER_PATH.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(DRIVER_PATH,eta=t,logT=np.log(T),logv=np.log(v),logTprime=ltp,logvprime=lvp,rhs=rhs,
                        report_eta=rt,report_fractions=rf,initial_li=rf[5:9,11],initial_tau=tau,tail_log_counts=logs)
    from scipy.special import logsumexp
    logtail=float(logsumexp(logs));ratio=float(np.exp(logtail-math.log(YLI)))
    m={'source_sha256':sha(src),'saved_driver_source':str(src.relative_to(DONOR)),'driver_sha256':sha(DRIVER_PATH),
       'driver_shape':list(Y.shape),'eta_star':float(rt[11]),'initial_li':rf[5:9,11].tolist(),
       'initial_tau_range':[float(tau.min()),float(tau.max())],'log_Ntail':logtail,'Ntail_per_Href_raw':float(np.exp(logtail)),
       'log_Ntail_per_Li':logtail-math.log(YLI),'Ntail_per_Li':ratio,'tail_component_bound_per_Li':ratio,
       'tail_L1_bound_per_Li':2*ratio,'donor_sources':{},'recovery':'driver RHS regenerated after two observed scratch losses; no original IVP rerun'}
    paths=[DONOR/'code/angular_model.py',DONOR/'vendor/c22/atomic_network.py',DONOR/'vendor/c22/rr_energy_moment.py',
           DONOR/'inputs/background/grid044_history.npz',DONOR/'results/grid044_M16_tight.json',*sorted((DONOR/'vendor/c22/vendor/atomic').glob('*'))]
    for p in paths:
        if p.is_file(): m['donor_sources'][str(p.relative_to(DONOR))]={'sha256':sha(p),'bytes':p.stat().st_size}
    with np.load(DRIVER_PATH,allow_pickle=False) as d: m['array_shapes']={k:list(d[k].shape) for k in d.files}
    (BASE/'inputs/driver_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m
class Bath:
    def __init__(self,secondary=False):
        with np.load(DRIVER_PATH,allow_pickle=False) as d:
            if secondary:
                self.Tfun=PchipInterpolator(d['eta'],d['logT']);self.vfun=PchipInterpolator(d['eta'],d['logv'])
            else:
                self.Tfun=CubicHermiteSpline(d['eta'],d['logT'],d['logTprime']);self.vfun=CubicHermiteSpline(d['eta'],d['logv'],d['logvprime'])
            self.star=float(d['report_eta'][11]);self.initial=d['initial_li'].copy();self.tau=d['initial_tau'].copy()
            self.report_eta=d['report_eta'].copy();self.report_f=d['report_fractions'][5:9].copy()
        self.bg=Background('grid044')
    def values(self,t):
        T=math.exp(float(self.Tfun(t)));v=math.exp(float(self.vfun(t)));h,n,b,bp=self.bg.fields(t)
        alpha,_,cap,_=thermal(T)
        return n/h*v*alpha[3:],cap[3:],T,v
class Trace:
    def __init__(self,kind='split',M=16,secondary=False,attenuated=False):
        self.kind,self.M,self.attenuated=kind,M,attenuated;self.rates,self.bath=Rates(),Bath(secondary)
        self.size=9+M if attenuated else 9;self.y0=np.zeros(self.size);self.y0[:4]=self.bath.initial
        if attenuated:self.y0[9:]=self.bath.tau
        self.segment=None;self._cache=None
    def coefficients(self,t,y):
        key=float(t),self.segment
        if self._cache is None or self._cache[0]!=key:
            a=self.rates.coefficients(t,self.kind,self.M,segment=self.segment);r,cap,T,v=self.bath.values(t)
            self._cache=key,(a,r,cap)
        a,r,cap=self._cache[1];lam,le,k,e,wk,w=a
        if self.attenuated: wk=wk*np.exp(-y[9:]);lam,le=float(wk.sum()),float((e*wk).sum())
        return lam,le,r,cap,k,e,wk
    def matrix(self,lam,r):
        a=np.zeros((4,4));a[0,0],a[1,0]=-lam,lam
        for q in range(1,4):a[q-1,q],a[q,q]=r[q-1],-r[q-1]
        return a
    def rhs(self,t,y):
        lam,le,r,cap,k,e,wk=self.coefficients(t,y);dy=np.zeros(self.size);f=y[:4];rr=r*f[1:]
        dy[:4]=self.matrix(lam,r)@f;dy[4]=lam*f[0];dy[5]=rr.sum()
        dy[6]=(le-CHI[0]*lam)*f[0]-cap@rr;dy[7]=(CHI+cap)@rr;dy[8]=le*f[0]
        if self.attenuated:dy[9:]=YLI*k*f[0]
        return dy
    def jac(self,t,y):
        lam,le,r,cap,k,e,wk=self.coefficients(t,y);a=np.zeros((self.size,self.size));a[:4,:4]=self.matrix(lam,r)
        a[4,0],a[5,1:4]=lam,r;a[6,0],a[6,1:4]=le-CHI[0]*lam,-cap*r;a[7,1:4],a[8,0]=(CHI+cap)*r,le
        if self.attenuated:
            a[0,9:],a[1,9:]=wk*y[0],-wk*y[0];a[4,9:]=-wk*y[0];a[6,9:]=-(e-CHI[0])*wk*y[0];a[8,9:]=-e*wk*y[0];a[9:,0]=YLI*k
        return a
    def splits(self):
        p=self.rates.endpoint_roots+(self.rates.fixed_crossings(self.M) if self.kind=='fixed' else [])
        return np.array(sorted({self.bath.star,END,*(q for q in p if self.bath.star<q<END)}))
class Bootstrap:
    size=2
    def __init__(self):self.rates,self.bath=Rates(),Bath();self.y0=np.zeros(2);self.segment=None;self._cache=None
    def coefficients(self,t):
        if self._cache is None or self._cache[0]!=t:
            lam=self.rates.coefficients(t,'split',32)[0];r1=self.bath.values(t)[0][0];h,n,b,bp=self.rates.bg.fields(t)
            self._cache=t,(lam,r1,YLI*SIGMA_MAX*C*n/h)
        return self._cache[1]
    def rhs(self,t,y):
        lam,r1,c=self.coefficients(t);return np.array([r1*(1-y[0])-math.exp(-DELTA)*lam*y[0],c*y[0]])
    def jac(self,t,y):
        lam,r1,c=self.coefficients(t);return np.array([[-r1-math.exp(-DELTA)*lam,0.],[c,0.]])
    def splits(self):return np.array([0.,*self.rates.endpoint_roots])

