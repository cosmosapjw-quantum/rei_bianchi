from pathlib import Path
import csv,json,math,sys
root=Path(__file__).resolve().parents[1]
a=list(csv.DictReader((root/'evidence'/'P2_CAMPAIGN.csv').open()))
b=list(csv.DictReader((root/'evidence'/'P2_CAMPAIGN_REPLAY.csv').open()))
assert len(a)==len(b)==45 and all(x.keys()==y.keys() for x,y in zip(a,b))
max_rel=0.0;bad=[]
for i,(x,y) in enumerate(zip(a,b)):
 for k in x:
  if k in ('case','owner'):
   if x[k]!=y[k]:bad.append((i,k,x[k],y[k]))
  else:
   v,w=float(x[k]),float(y[k]);assert math.isfinite(v) and math.isfinite(w)
   if k in ('energy_rel_residual','baryon_rel_residual'):
    if abs(v)>1e-11 or abs(w)>1e-11:bad.append((i,k,v,w))
   else:
    err=abs(v-w)/(max(abs(v),abs(w),1e-30));max_rel=max(max_rel,err)
    if err>2e-10:bad.append((i,k,v,w))
res={'schema':'rei.iso.p2.replay_comparison.v1','rows':45,'max_observable_relative_diff':max_rel,'excluded_from_pointwise': ['energy_rel_residual','baryon_rel_residual'], 'status':'PASS' if not bad else 'FAIL','first_errors':bad[:12]}
(root/'evidence'/'CAMPAIGN_COMPARE.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res))
if bad:sys.exit(2)
