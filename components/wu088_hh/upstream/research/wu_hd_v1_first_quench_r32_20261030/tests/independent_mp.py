"""Same-author independent algorithm using MP85, independent parsed rates and row-oriented dynamics.
No calls to src.quench, numpy, or the source output CSV inside the calculation.
This is NOT distinct-author R6/C9 review.
"""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
import mpmath as mp
mp.mp.dps=85
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv'
if hashlib.sha256(source.read_bytes()).hexdigest()!='58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c':raise ValueError('source mutation')
with source.open() as f:rr=[r for r in csv.DictReader(f) if r['initial_v']=='1']
with (ROOT/'sources/CDMS2011V2_RENDERED_V0V1_LEVELS.json').open() as f:ee=json.load(f)
e0=[mp.mpf(ee['v0'][str(i)]) for i in range(11)]
e1=[mp.mpf(ee['v1'][str(i)]) for i in range(7)]
hc100=mp.mpf('6.62607015e-34')*mp.mpf('299792458')*100
kb=mp.mpf('1.380649e-23')
rows=list(csv.DictReader((ROOT/'results/ATLAS_QUENCH_126.csv').open()))
branches=list(csv.DictReader((ROOT/'results/TERMINAL_V0_BRANCHES_1386.csv').open()))
branchmap={(int(r['T_K']),r['mode'],int(r['initial_v1_J'])):[] for r in rows}
for x in branches:branchmap[(int(x['T_K']),x['mode'],int(x['initial_v1_J']))].append(mp.mpf(x['restricted_probability']))

summary={'algorithm':'independently parsed source; MP85 explicit absorbing Markov inverse, rows convention',
         'same_author':True,'distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN','test_rows':0,
         'compared_total_metrics':0,'max_scaled_difference':0.0,'max_abs_p_diff':0.0}
maxdiff=mp.mpf(0);maxp=mp.mpf(0)
for x in rows:
 T=int(x['T_K']);mode=x['mode'];j=int(x['initial_v1_J']);
 # row-oriented Q: rows are transient from-state, columns are target or absorbing v0
 gen=mp.matrix(7,7);absorb=mp.matrix(7,11)
 for a in rr:
  if int(a['T_K'])!=T:continue
  v=int(a['final_v']);fr=int(a['initial_J']);to=int(a['final_J']);rate=mp.mpf(a['rate_cm3_s'])
  if v==0:absorb[fr,to]+=rate
  else:
   gen[fr,to]+=rate
   if mode=='DB_UPWARD_V1':
    gen[to,fr]+=rate*mp.mpf(2*fr+1)/mp.mpf(2*to+1)*mp.exp(-hc100*(e1[fr]-e1[to])/(kb*T))
 for a in range(7):gen[a,a]=-sum(gen[a,k] for k in range(7))-sum(absorb[a,k] for k in range(11))
 y=mp.matrix(1,7);y[0,j]=1
 # independent solve row vector expected occupation y*(-gen)^-1
 inv=(-gen)**-1
 n=y*inv; b=n*absorb
 exposure=sum(n[0,k] for k in range(7));
 finalE=sum(b[0,k]*e0[k] for k in range(11))*hc100
 heat=e1[j]*hc100-finalE
 ref=[mp.mpf(x['mean_proton_fluence_cm-3_s']),mp.mpf(x['effective_quench_coeff_cm3_s']),mp.mpf(x['proton_bath_heat_J'])]
 curr=[exposure,1/exposure,heat]
 for v,rv in zip(curr,ref):
  sc=abs(v-rv)/max(abs(v),mp.mpf('1e-28'))
  maxdiff=max(maxdiff,sc)
  if sc>mp.mpf('2e-11'):raise ValueError(f'metric discrepancy T={T},J={j},mode={mode},gap={sc}')
 expbr=branchmap[(T,mode,j)]; assert len(expbr)==11
 for k in range(11):
  g=abs(b[0,k]-expbr[k]);maxp=max(maxp,g)
  if g>mp.mpf('5e-12'):raise ValueError(f'branch discrepancy {T},{j},{mode},{k},{g}')
 summary['test_rows']+=1
 summary['compared_total_metrics']+=14
summary.update(max_scaled_difference=float(maxdiff),max_abs_p_diff=float(maxp))
(ROOT/'results/INDEPENDENT_MP85.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
