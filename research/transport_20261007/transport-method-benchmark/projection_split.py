"""Analytically propagate each declared initial representation, only as a diagnostic reference."""
import json,csv,math
from pathlib import Path
R=Path(__file__).resolve().parent
O=json.loads((R/'oracle.json').read_text());C=float(O['normalization']);truth={round(float(e['s']),12):float(e['Nout'])for e in O['epochs']};L=math.log(100/13.6)
qs=[-.9602898564975363,-.7966664774136267,-.5255324099163290,-.1834346424956498,.1834346424956498,.5255324099163290,.7966664774136267,.9602898564975363]
ws=[.1012285362903763,.2223810344533745,.3137066458778873,.3626837833783620,.3626837833783620,.3137066458778873,.2223810344533745,.1012285362903763]
def init(n):
 cells=[];nodes=[];panels=[]
 for i in range(n):
  lo=i*L/n;hi=(i+1)*L/n;el=13.6*math.exp(lo);er=13.6*math.exp(hi);N=U=0.
  for q,w in zip(qs,ws):
   x=(lo+hi)/2+(hi-lo)/2*q;z=(x-.65)/.25;g=C*math.exp(-1/(1-z*z))if abs(z)<1 else 0
   weight=(hi-lo)/2*w*g;nodes.append((x,weight));N+=weight;U+=13.6*math.exp(x)*weight
  cells.append((el,er,N/(er-el),6*(U-(el+er)/2*N)/(er-el)**2));panels.append((lo,hi,N/(hi-lo)))
 return cells,nodes,panels
# Cache only four fixed initial representations. 32+64+128+256 panels *8 =3840
# distinct stock sites. Drop each grid before constructing the next instead.
records=[]
rows=list(csv.DictReader((R/'results.csv').open()))
for n in [32,64,128,256]:
 cells,nodes,panels=init(n)
 for row in rows:
  if int(row['n'])!=n:continue
  m=row['method'];s=float(row['s']);actual=float(row['Nout']);cut=13.6*math.exp(s)
  if m=='stock':projected=sum(w for x,w in nodes if x<=s)
  elif m=='partial':projected=sum(a*max(0,min(s,r)-l)for l,r,a in panels)
  else:
   projected=0.
   for el,er,a,b in cells:
    if m=='fv':b=0.
    if m=='dg_limited':b=math.copysign(min(abs(b),a),b)
    hi=min(cut,er)
    if hi>el:
     mid=(el+er)/2
     projected+=a*(hi-el)+b*((hi-mid)**2-(el-mid)**2)/(er-el)
  exact=truth[round(s,12)];projection=projected-exact;transport=actual-projected
  assert abs((projection+transport)-(actual-exact))<1e-14
  records.append({'method':m,'n':n,'cfl':float(row['cfl']),'s':s,'exact_declared_projection_outN':projected,'initial_representation_contribution':projection,'numerical_transport_contribution':transport,'total_error':actual-exact})
 del cells,nodes,panels
summary=[]
for m,n,c in sorted({(r['method'],r['n'],r['cfl'])for r in records}):
 rs=[r for r in records if(r['method'],r['n'],r['cfl'])==(m,n,c)]
 summary.append({'method':m,'n':n,'cfl':c,'max_initial_representation_contribution':max(abs(r['initial_representation_contribution'])for r in rs),'max_numerical_transport_contribution':max(abs(r['numerical_transport_contribution'])for r in rs),'max_total_error':max(abs(r['total_error'])for r in rs)})
result={'scope':'Diagnostic analytic propagation of each own initial representation only; no evolving solver state substituted; same9epochs/26cases. Maxima of components need not sum.','max_live_initial_sites':2048,'rows':records,'summary':summary}
(R/'PROJECTION_TRANSPORT_SPLIT.json').write_text(json.dumps(result,indent=2)+'\n')
for r in summary:
 if r['n']==256:print(r)
