from sage.all import RealIntervalField
import json
from pathlib import Path
R=RealIntervalField(200)
cases=[]
for op, pairs in [('EXP',[(-32.,-31.),(-2.,-1.),(-.01,.02),(0.,0.),(.001,.002),(1.,2.),(10.,11.)]),('LN',[(.001,.002),(.1,.3),(1.,1.),(1.,2.),(30000.,110000.),(1e-100,1e-99),(1e100,1e101)]),('POW',[(30000.,110000.),(.1,.3),(1.,2.)])]:
 for lo,hi in pairs:
  exponents=[.470,.654,1.503,-1.5] if op=='POW' else [None]
  for p in exponents:
   x=R(lo,hi);y=x.exp() if op=='EXP' else x.log() if op=='LN' else (x.log()*R(p)).exp()
   cases.append({'op':op,'lo':lo,'hi':hi,'p':p,'range_lower':str(y.lower()),'range_upper':str(y.upper())})
for lo,hi in [(30000.,30000.),(50000.,50000.),(110000.,110000.),(30000.,30001.),(50000.,50001.),(109999.,110000.)]:
 # Derived PREWORK6.1 prototype beta=A sqrt(T) exp(-B/T), not a substitute
 # for the actual HG source. This qualifies AD operations before real residual.
 samples=[]
 for t in [lo,(lo+hi)/2,hi]:
  T=R(t);A=R(5e-11);B=R(157807.);b=A*T.sqrt()*(-B/T).exp();d=b*(1/(2*T)+B/T**2);h=b*((1/(2*T)+B/T**2)**2-1/(2*T**2)-2*B/T**3)
  encode=lambda v:{'lo':str(v.lower()),'hi':str(v.upper())}
  samples.append({'t':t,'value':encode(b),'gradient':encode(d),'hessian':encode(h)})
 cases.append({'op':'JET_BETA','lo':lo,'hi':hi,'A':5e-11,'B':157807.,'samples':samples})
out={'arithmetic':'Sage MPFI200 outward intervals','cases':cases,'invalid_commands':['LN 0 1','LN -2 -1','POW -1 1 0.5','EXP 1000 1001'],'scope':'Finite scalar domain/extrema and derived Jet2 witness qualification; no actual HHe/root/fullF04 or physical admission'}
Path('.cuh/fastest-track/REI-F04-INTERVAL/oracle.json').write_text(json.dumps(out,indent=2)+'\n')
print('Frozen MPFI oracle cases',len(cases),'invalid',len(out['invalid_commands']))
