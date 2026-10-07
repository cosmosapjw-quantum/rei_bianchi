import json, hashlib
from pathlib import Path
import mpmath as m
m.mp.dps=90
J=lambda k,h: h if k==0 else -m.expm1(-k*h)/k
worst=dict(number_identity=m.mpf(0),energy_identity=m.mpf(0),count_integral=m.mpf(0),energy_integral=m.mpf(0))
cases=0; heat_ok=True
for hh in ['1e-6','0.07','2']:
 h=m.mpf(hh)
 for zz in ['0','1e-30','1e-8','1','100','1000']:
  z=m.mpf(zz); lam=z/h
  for f0,q in [(m.mpf('0.3'),m.mpf('0.2')),(m.mpf(0),m.mpf('0.2')),(m.mpf('0.3'),m.mpf(0))]:
   E0=60*m.exp(h)
   jf=J(lam,h); je=J(lam+1,h)
   A=f0*jf+q*(h*h/2 if not lam else (h-jf)/lam)
   D=1-(1+h)*m.exp(-h) if not lam else (J(1,h)-je)/lam
   R=E0*(f0*je+q*D)
   f1=f0*m.exp(-z)+q*jf
   scaleN=f0+q*h; scaleE=E0*(f0+q*J(1,h))
   worst['number_identity']=max(worst['number_identity'],abs(f1+lam*A-scaleN)/scaleN)
   worst['energy_identity']=max(worst['energy_identity'],abs(E0*m.exp(-h)*f1+(lam+1)*R-scaleE)/scaleE)
   fn=lambda t:f0*m.exp(-lam*t)+q*J(lam,t)
   cuts=[m.mpf(0),h]
   if lam*h>1: cuts=sorted({m.mpf(0),h,*[min(h,v/lam) for v in [m.mpf('.01'),m.mpf('.1'),m.mpf(1),m.mpf(10),m.mpf(100)]]})
   aq=m.quad(fn,cuts); rq=E0*m.quad(lambda t:m.exp(-t)*fn(t),cuts)
   worst['count_integral']=max(worst['count_integral'],abs(A-aq)/max(aq,m.mpf('1e-100')))
   worst['energy_integral']=max(worst['energy_integral'],abs(R-rq)/max(rq,m.mpf('1e-100')))
   for weight,chi in zip(['.2','.3','.5'],['13.598434599702','24.587389011','54.41776']):
    ri=lam*m.mpf(weight)
    heat_ok &= ri*(R-m.mpf(chi)*A)>=0
   cases+=1
# Direct source density K*exp(-eta); test each actual overlap, never normalize a sum.
source_error=m.mpf(0)
for L,R in [('0','1'),('2.6','2.600000001'),('-3','.5')]:
 l,r=m.mpf(L),m.mpf(R); K=m.mpf('2.31')
 qn=K*(m.exp(-l)-m.exp(-r)); qm=K*(r-l)
 source_error=max(source_error,abs(qn-m.quad(lambda eta:K*m.exp(-eta),[l,r]))/qn,abs(qm-m.quad(lambda eta:K,[l,r]))/qm)
# Demonstrate why common quadrature weights are not moment exact by themselves.
l=m.mpf(0); r=m.mpf(1); beta=m.mpf(2)
N=J(-beta,1); M=J(-beta-1,1)
qN=(m.exp(beta*(m.mpf('.5')-1/(2*m.sqrt(3))))+m.exp(beta*(m.mpf('.5')+1/(2*m.sqrt(3)))))/2
qM=(m.exp((beta+1)*(m.mpf('.5')-1/(2*m.sqrt(3))))+m.exp((beta+1)*(m.mpf('.5')+1/(2*m.sqrt(3)))))/2
report={'kernel_cases':cases,'precision_decimal_digits':m.mp.dps,'max_relative_errors':{k:str(v) for k,v in worst.items()},'all_supported_channel_heat_nonnegative':bool(heat_ok),'source_moment_max_relative_error':str(source_error),'ordinary_gauss2_not_moment_exact_relative_errors':{'N':str(abs(qN-N)/N),'M':str(abs(qM-M)/M)},'scope':'Small algebraic/quadrature controls only; no production code or history solves.'}
print(json.dumps(report,indent=2))
out=Path(__file__).resolve().with_name('REVIEW_ARITHMETIC.json'); out.write_text(json.dumps(report,indent=2)+'\n')
