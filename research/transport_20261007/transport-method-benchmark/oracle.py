"""Independent high-precision analytic characteristic oracle; no numerical-method states."""
import mpmath as mp, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
mp.mp.dps=60
EC=mp.mpf('13.6'); LO=mp.mpf('.4'); HI=mp.mpf('.9'); L=mp.log(100/EC)
def raw(x):
 z=(x-mp.mpf('.65'))/mp.mpf('.25')
 return mp.exp(-1/(1-z*z)) if abs(z)<1 else mp.mpf(0)
def integ(f,a,b):
 a=max(a,LO); b=min(b,HI)
 if b<=a:return mp.mpf(0)
 m=mp.mpf('.65')
 # Bound live abscissae: do not retain nodes from past integration intervals.
 mp.mp._tanh_sinh.clear()
 return mp.quad(f,[a,m,b] if a<m<b else [a,b])
C=1/integ(raw,LO,HI)
def q(a,b,energy=False):return C*integ(lambda x: raw(x)*(mp.exp(x) if energy else 1),a,b)
def epoch(s):
 n=q(s,HI); no=q(LO,s); u=EC*mp.exp(-s)*q(s,HI,True);eo=EC*no
 # Independent trajectory-energy-loss integral, NOT residual-defined work.
 w=EC*C*integ(lambda y:raw(y)*(mp.exp(y)-1),LO,s)+EC*(-mp.expm1(-s))*q(s,HI,True)
 return dict(s=s,N=n,U=u,Nout=no,Eout=eo,W=w,bins=[q(s+j*L/32,s+(j+1)*L/32)for j in range(32)])
epochs=[epoch(mp.mpf(s))for s in ['0','.2','.4','.5','.6','.7','.8','.9','1.']]
u0=EC*q(LO,HI,True)
checks={'Nmax':max(abs(e['N']+e['Nout']-1)for e in epochs),'Emax':max(abs(e['U']+e['Eout']+e['W']-u0)for e in epochs)}
C60=C; e60=epoch(mp.mpf('.6'))
mp.mp.dps=80
C=1/integ(raw,LO,HI);e80=epoch(mp.mpf('.6'))
checks['C60to80']=abs(C-C60);checks['selected60to80']=max(abs(e80[k]-e60[k])for k in ['N','U','Nout','Eout','W'])
assert all(v<mp.mpf('1e-50')for v in checks.values()),checks
def enc(x):
 if isinstance(x,mp.mpf):return mp.nstr(x,65)
 if isinstance(x,dict):return{k:enc(v)for k,v in x.items()}
 if isinstance(x,list):return[enc(v)for v in x]
 return x
result=enc({'normalization':C60,'N0':mp.mpf(1),'U0':u0,'epochs':epochs,'checks':checks,'dps':60,'selected_check_dps':80})
(ROOT/'oracle.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'normalization.txt').write_text(mp.nstr(C60,30)+'\n')
print(json.dumps(result['checks'],indent=2));print('C',result['normalization']);print('U0',result['U0'])
