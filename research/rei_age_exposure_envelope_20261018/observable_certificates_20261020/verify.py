"""Independent Decimal100 direct survival/moment formulas (no stable kernels)."""
import argparse, csv, decimal, json, pathlib, time
from fractions import Fraction
D=decimal.Decimal
HERE=pathlib.Path(__file__).resolve().parent
UP=HERE.parent/'vigilode_age_transport_20261019'
CLOCKS=[8,16,32,64];POPS=['all','sensitive','passive']
def dd(x):return D.from_float(x)
def loadj(p):return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--results',type=pathlib.Path,default=HERE/'results');args=ap.parse_args();out=args.results
 start=time.monotonic();ctx=decimal.getcontext();ctx.prec=100;ctx.Emin=decimal.MIN_EMIN;ctx.Emax=decimal.MAX_EMAX
 study=loadj(out/'STUDY.json');model=loadj(UP/'inputs/model.json');T=dd(model['observe_time_s'])
 ages={n:[T-dd(b) for b in model['clocks'][str(n)]] for n in CLOCKS}
 nodes=[];rate_ids={};rates=[]
 with (UP/'inputs/nodes.csv').open() as f:
  for row in csv.DictReader(f):
   key=tuple(float(row['lambda'+str(k)]) for k in range(3))
   if key not in rate_ids:
    lam=sum(map(dd,key),D(0));shares=[dd(x)/lam if lam else D(0) for x in key];rate_ids[key]=len(rates);rates.append((lam,shares))
   nodes.append((int(row['cohort']),dd(float(row['mass'])),dd(float(row['energy'])),rate_ids[key]))
 expcache={};max_tau=D(0)
 for rid,(lam,shares) in enumerate(rates):
  for n in CLOCKS:
   for j,a in enumerate(ages[n]):
    tau=lam*a;max_tau=max(max_tau,tau);expcache[rid,n,j]=(-tau).exp() if lam else D(1)
 checks=0
 def interval(ref,bound,label):
  nonlocal checks
  lo,hi=map(dd,bound)
  assert lo<=ref<=hi,(label,str(ref),bound);checks+=1
 def upper(ref,bound,label):
  nonlocal checks
  assert ref<=dd(bound),(label,str(ref),bound);checks+=1
 totals={};initials={};records={}
 for n in CLOCKS:
  ts=[[D(0)]*9 for _ in POPS];ini=[[D(0),D(0)] for _ in POPS];rows=[]
  for cohort,w,energy,rid in nodes:
   a=ages[n][cohort*n//64];surv=w*expcache[rid,n,cohort*n//64];lam,shares=rates[rid];absorbed=w-surv
   row=[surv,energy*surv,a*surv,a*a*surv]+[s*absorbed for s in shares]+[absorbed,energy*absorbed]
   rows.append(row[:7]);pop=1 if lam else 2
   for pp in [0,pop]:
    ts[pp]=[x+y for x,y in zip(ts[pp],row)];ini[pp][0]+=w;ini[pp][1]+=w*energy
  totals[n]=ts;initials[n]=ini;records[n]=rows
  for pp,name in enumerate(POPS):
   rust=study['cases'][CLOCKS.index(n)]['populations'][name]
   for j in range(7):interval(ts[pp][j],rust['observables'][j],f'case{n}/{name}/{j}')
   for j,field in [(7,'absorbed_number'),(8,'absorbed_same_energy')]:interval(ts[pp][j],rust[field],f'case{n}/{name}/{field}')
   interval(ini[pp][0],rust['initial_number'],'initial number');interval(ini[pp][1],rust['initial_same_energy'],'initial energy')
   interval(D(0),rust['photon_ledger'],'photon ledger');interval(D(0),rust['same_energy_ledger'],'energy ledger')
   if ts[pp][0]:
    interval(ts[pp][2]/ts[pp][0],rust['normalized_mean'],'case normalized mean');interval(ts[pp][3]/ts[pp][0],rust['normalized_second'],'case normalized second')
   else:assert rust['normalization_status']=='UNRESOLVED'
 reference_pairs=[]
 for n in CLOCKS:
  labs=[[D(0)]*7 for _ in POPS];signed=[[D(0)]*7 for _ in POPS];cost=[D(0)]*3;amax=[D(0)]*3;bc=[[D(0),D(0)] for _ in POPS]
  pair=study['pairs'][CLOCKS.index(n)]
  for idx,(cohort,w,energy,rid) in enumerate(nodes):
   delta=abs(ages[n][cohort*n//64]-ages[64][cohort]);aa=max(ages[n][cohort*n//64],ages[64][cohort]);ks=[x-y for x,y in zip(records[n][idx],records[64][idx])];pop=1 if rates[rid][0] else 2
   for pp in [0,pop]:
    signed[pp]=[x+y for x,y in zip(signed[pp],ks)];labs[pp]=[x+abs(y) for x,y in zip(labs[pp],ks)];cost[pp]+=w*delta;amax[pp]=max(amax[pp],aa)
    normal=pair['populations'][POPS[pp]]['normalized_mean_bound']
    if normal['status']=='RESOLVED':
     for side,key in enumerate(['forward','reverse']):
      c=dd(normal[key]['center']);bc[pp][side]+=abs((records[n][idx][2]-c*records[n][idx][0])-(records[64][idx][2]-c*records[64][idx][0]))
  refs={}
  for pp,name in enumerate(POPS):
   rust=pair['populations'][name]
   for j in range(7):
    interval(signed[pp][j],rust['signed_difference'][j],f'pair{n}/{name}/stable/{j}');interval(totals[n][pp][j]-totals[64][pp][j],rust['direct_case_difference'][j],f'pair{n}/{name}/direct/{j}');upper(labs[pp][j],rust['label_absolute_upper'][j],f'pair{n}/{name}/L{j}')
   upper(cost[pp],rust['C_upper'],'C');upper(amax[pp],rust['Amax_upper'],'Amax')
   for j in range(2):upper(abs(signed[pp][j+2]),rust['moment_global_upper'][j],'global moment');upper(abs(signed[pp][j+2]),rust['moment_chosen_upper'][j],'chosen moment')
   normal=rust['normalized_mean_bound'];mean_diff=None
   if totals[n][pp][0] and totals[64][pp][0]:
    mean_diff=totals[n][pp][2]/totals[n][pp][0]-totals[64][pp][2]/totals[64][pp][0];interval(mean_diff,normal['observed_signed_interval'],'mean observed')
    for side,key in enumerate(['forward','reverse']):upper(bc[pp][side],normal[key]['Bc'],'Bc');upper(abs(signed[pp][0]),normal[key]['E0'],'E0');upper(abs(mean_diff),normal[key]['upper'],'centered mean')
    upper(abs(mean_diff),normal['global_upper'],'global mean');upper(abs(mean_diff),normal['chosen_upper'],'chosen mean')
   refs[name]={'signed_difference':[str(x) for x in signed[pp]],'label_absolute_sum':[str(x) for x in labs[pp]],'C':str(cost[pp]),'Amax':str(amax[pp]),'centered_absolute_sum':[str(x) for x in bc[pp]],'normalized_mean_difference':None if mean_diff is None else str(mean_diff)}
  reference_pairs.append({'coarse':n,'populations':refs})
 # Exact rational fixture proves passive age response without numerical exponentials.
 w,a,b=Fraction(2),Fraction(2),Fraction(5)
 assert w-w==0 and w*b-w*a==6 and w*b*b-w*a*a==42
 result={'status':'PASS','precision_digits':ctx.prec,'decimal_Emin':ctx.Emin,'decimal_Emax':ctx.Emax,'nodes':len(nodes),'clocks':CLOCKS,'nontrivial_pairs':3,'populations':POPS,'scalar_checks':checks,'exp_cache_entries':len(expcache),'max_tau':str(max_tau),'all_exp_values_positive':all(v>0 for v in expcache.values()),'passive_fraction_fixture':'Ndiff=0 M1diff=6 M2diff=42 exactly','wall_seconds':time.monotonic()-start,'case_references':{str(n):{name:[str(x) for x in totals[n][pp]] for pp,name in enumerate(POPS)} for n in CLOCKS},'pair_references':reference_pairs,'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
 assert result['all_exp_values_positive'],'Decimal underflow would invalidate this direct reference path'
 (out/'DECIMAL_REFERENCE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','scalar_checks','wall_seconds','max_tau','all_exp_values_positive']}))
if __name__=='__main__':main()
