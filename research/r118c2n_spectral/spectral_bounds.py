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
def terminal(root,expected,order):
    p=root/'checkpoint.txt';assert sha(p)==expected['checkpoint.txt'] and sha(root/'history.csv')==expected['history.csv']
    lines=p.read_text().splitlines();assert lines[0]=='AXBI_CHECKPOINT_V4';v=np.fromstring(lines[1],sep=' ');scale=(1/21)/v[0]
    n,u,lo,hi=[np.fromstring(lines[i],sep=' ') for i in (4,5,6,7)]
    import subprocess
    with (root/'history.csv').open() as f:head=f.readline().strip().split(',')
    last=subprocess.check_output(['tail','-1',str(root/'history.csv')],text=True).strip().split(',');h=dict(zip(head,last));nh=float(h['nH_proper_cm3'])
    fac=C*nh;cells=[];bands=np.zeros(4);edges=[T,1.05*T,1.2*T,2*T,np.inf]
    for ni,ui,l,r in zip(n,u,lo,hi):
        if ni==0:continue
        E,w,m=quad(ni,ui,l,r,scale,order);a,b,x=l*scale,r*scale,m*scale
        lo_,hi_,p0,p1=bounds(a,b,x);rate=float(w@sig(E));heat=float(w@(sig(E)*(E-bind)))
        # Rounding and GL quadrature error near a forced delta.
        assert rate>=ni*lo_-max(1e-8*ni*hi_,1e-300) and rate<=ni*hi_+max(1e-8*ni*hi_,1e-300)
        ab=float(w[E>=T].sum());assert ni*p0-1e-9*ni<=ab<=ni*p1+1e-9*ni
        for k in range(4):bands[k]+=float(w[(E>=edges[k])&(E<edges[k+1])]@sig(E[(E>=edges[k])&(E<edges[k+1])]))
        cells.append(dict(a=float(a),b=float(b),mean=float(x),number=float(ni),gamma=fac*rate,heat=fac*heat,
            gamma_lower=fac*ni*lo_,gamma_upper=fac*ni*hi_,above=ab,above_lower=ni*p0,above_upper=ni*p1,cross=bool(a<T<=b)))
    totals={k:sum(z[k] for z in cells) for k in ('gamma','heat','gamma_lower','gamma_upper','above','above_lower','above_upper')}
    totals.update(z=float(1/v[0]-1),crossing_cells=sum(z['cross'] for z in cells),crossing_gamma=sum(z['gamma'] for z in cells if z['cross']),
        crossing_width=sum(z['gamma_upper']-z['gamma_lower'] for z in cells if z['cross']),mean_excess=totals['heat']/totals['gamma'],
        gamma_band=(fac*bands).tolist(),checkpoint_sha=expected['checkpoint.txt'])
    return totals,cells
runs={r['case']:r for r in j(K/'RUNS.json')}
r128=j(D/'Q128.json')
roots=[('q16',runs['extend16']),('q32',runs['resume32']),('q64',runs['fresh64']),('q128',r128),('q256',j(D/'Q256.json')),('tight32',j(M/'FINAL_HISTORY.json'))]
out={};cellout={}
for name,r in roots:
    root=Path(r['raw_path']);x,_=terminal(root,r['hashes'],32);y,cell=terminal(root,r['hashes'],64)
    assert abs(x['gamma']/y['gamma']-1)<1e-9 and abs(x['heat']/y['heat']-1)<1e-8
    y['GL_gap']=abs(x['gamma']/y['gamma']-1);out[name]=y;cellout[name]=cell
    print(name,y,flush=True)
# Native-rate control from original C2J checkpoint and actual raw source history.
old=next(r for r in j(I/'research/r118c2j_error_control/RUNS.json') if r['variant']=='reduced' and r['case']=='long32')
r,_=terminal(Path(old['raw_path']),old['hashes'],64)
import subprocess
p=Path(old['raw_path'])/'history.csv'
with p.open() as f:head=f.readline().strip().split(',')
h=dict(zip(head,subprocess.check_output(['tail','-1',str(p)],text=True).strip().split(',')))
native_gap=abs(r['gamma']/float(h['Gamma_HeII_per_s'])-1);assert native_gap<1e-8
# Actual source-born packet spectra from BASS (not exponential closure).
br=j(B/'research/r118c2m_energy_budget/RESULTS.json');bouts={}
for r in br['results']:
    if r['name'] not in ('base','time2','cross','time2_strict'):continue
    root=Path(br['raw'])/r['name'];p=root/'packets.tsv';assert sha(p)==r['hashes']['packets.tsv']
    h=root/'history.tsv';assert sha(h)==r['hashes']['history.tsv']
    z=np.genfromtxt(p,names=True,delimiter='\t');a=np.genfromtxt(h,names=True,delimiter='\t',usecols=['nH_m3'])
    E=z['energy_eV'];w=z['N_per_H'];fac=C*float(a['nH_m3'][-1])*1e-6
    g=float(fac*(w@sig(E)));heat=float(fac*(w@(sig(E)*(E-bind))))
    assert abs(g/r['gamma'][2]-1)<1e-12 and abs(heat/r['heat'][2]-1)<1e-12
    bouts[r['name']]=dict(gamma=g,heat=heat,mean_excess=heat/g,above=float(w[E>=T].sum()),packet_sha=sha(p))
    print('BASS',r['name'],bouts[r['name']],flush=True)
# Finite numerical check of analytic envelopes by random positive measures, deterministic seed.
rng=np.random.default_rng(118)
for i in range(10000):
    a=float(rng.uniform(13.6,150));b=a+float(rng.uniform(.001,70));E=rng.uniform(a,b,12);w=rng.random(12);w/=w.sum();m=float(w@E)
    l,u,p0,p1=bounds(a,b,m);g=float(w@sig(E));p=float(w[E>=T].sum())
    assert l-1e-30<=g<=u+1e-30 and p0-1e-14<=p<=p1+1e-14
result=dict(status='PASS_SCOPED_MOMENT_ENVELOPE',scope='sharp inf/sup of HeII fit cross-section over any positive measure with fixed physical N,U,support; independent exponential-closure GL; not history error bound',threshold_ev=T,cases=out,bass=bouts,native_control_relative=native_gap,random_measure_checks=10000)
(D/'SPECTRAL.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
(D/'SPECTRAL_CELLS.json').write_text(json.dumps(cellout,indent=2,allow_nan=False)+'\n')
print('native check',native_gap,flush=True)
