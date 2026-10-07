"""Independent Decimal continuous integrals for the fixed transparent controls.
No candidate quadrature, panel reconstruction, or energy residual is used as oracle.
"""
from decimal import Decimal as D, getcontext
import argparse,csv,json
from pathlib import Path
getcontext().prec=160
getcontext().Emin=-999999999
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def d(x):return D.from_float(float(x))
eps=d(1.602176634e-12);ec=d(13.6)
def i0(t,x,y):return y-x if not t else ((t*y).exp()-(t*x).exp())/t
def i1(t,x,y):return (y*y-x*x)/2 if not t else (((t*y).exp()*(t*y-1))-((t*x).exp()*(t*x-1)))/(t*t)
def z(t,x,y,fam):
 if x==y:return D(0)
 if fam==0:return i0(t,x,y)
 if fam==1:return i0(t,x,y)-i1(t,x,y)
 return i1(t,x,y)
def candidate(r):
 if r['log_hi']=='-inf':return D(0)
 return (d(r['log_hi'])+d(r['log_lo'])).exp()
groups={}
for r in csv.DictReader(a.input.open()):
 key=tuple(r[k] for k in ['kind','family','l','r','beta','log_n','q','s0','s1','boundary','parts'])
 groups.setdefault(key,[]).append(r)
records=[];failures=[];worst=D(0);zeros=0;budgets=[];envelopes=[];geometry=[]
for key,rows in groups.items():
 r=rows[0];kind=r['kind'];fam=int(r['family']);l=d(r['l']);right=d(r['r']);beta=d(r['beta']);logn=d(r['log_n']);s0=d(r['s0']);s1=d(r['s1']);h=s1-s0;B=d(r['boundary']);W=right-l
 if kind=='envelope':
  N=logn.exp();ref=N*(-3*(l-s0)).exp()*z(beta-3*W,D(0),D(1),fam)/z(beta,D(0),D(1),fam)
  low,high=map(candidate,rows);passed=low<=ref<=high
  item={'family':fam,'parts':int(r['parts']),'lower':float(low),'reference':float(ref),'upper':float(high),'relative_gap':float((high-low)/ref),'pass':passed};envelopes.append(item)
  if not passed:failures.append(item)
  continue
 ref=[D(0)]*13
 if kind=='stock':
  N0=logn.exp();norm=z(beta,D(0),D(1),fam);cut=min(D(1),max(D(0),(B-l)/W))
  nout=N0*z(beta,D(0),cut,fam)/norm;nactive=N0*z(beta,cut,D(1),fam)/norm
  mout=N0*l.exp()*z(beta+W,D(0),cut,fam)/norm;mactive=N0*l.exp()*z(beta+W,cut,D(1),fam)/norm
  U0=eps*(-s0).exp()*(mout+mactive)
  ref[0]=nactive;ref[1]=eps*(-s1).exp()*mactive;ref[11]=nout;ref[12]=eps*ec*nout
  ref[8]=eps*((-s0).exp()*mactive*(1-(-h).exp())+(-s0).exp()*mout-ec*nout)
 else:
  q=d(r['q']);Dband=right-l;lc=d(__import__('math').log(13.6));w=max(D(0),B-l)
  out=q*(min(w,Dband)**2/2+Dband*max(w-Dband,D(0)))
  # Continuous birth-energy integration; logarithmic band edges are supplied inputs.
  emin=l.exp();emax=right.exp();event_ec=lc.exp();v=min(emax,max(emin,(s1+lc).exp()))
  da=(emin/event_ec).ln();dv=(v/event_ec).ln();u=(v/emin).ln()
  active_n=q*((dv*dv-da*da)/2+h*(emax/v).ln())
  active_u=q*eps*((v-emin)-event_ec*u+(1-(-h).exp())*(emax-v))
  red=q*eps*((h-1)*(v-emin)+event_ec*((1-h)*u+(dv*dv-da*da)/2)+(h-1+(-h).exp())*(emax-v))
  ref[0]=active_n;ref[1]=active_u;ref[8]=red;ref[9]=q*h*Dband;ref[10]=q*eps*(emax-emin)*h;ref[11]=out;ref[12]=eps*ec*out
  N0=U0=D(0)
  geometry.append({'h':float(h),'parts':int(r['parts']),'stored_boundary':r['boundary'],'boundary_roundoff':str(B-(s1+lc)),'topology':'exact supplied binary64 log anchors and boundary'})
 got=[candidate(x) for x in rows]
 for i,(value,expect) in enumerate(zip(got,ref)):
  if expect==0:err=D(0) if value==0 else D('Infinity');zeros+=1
  elif value==0:err=D(1)
  else:err=abs(value/expect-1)
  worst=max(worst,err);passed=err<=D('3e-12')
  item={'kind':kind,'family':fam,'s1':r['s1'],'parts':int(r['parts']),'owner':i,'relative_error':str(err),'pass':passed}
  records.append(item)
  if not passed:failures.append(item)
 # Candidate readout ledger, including explicit loss enclosure and fixed denominators.
 scalar=[d(x['readout']) for x in rows]
 lossn=d(r['loss_n']);losse=d(r['loss_e'])
 nr=abs(scalar[0]+sum(scalar[2:5])+scalar[11]-N0-scalar[9])
 er=abs(scalar[1]+sum(scalar[5:8])+scalar[8]+scalar[12]-U0-scalar[10])
 na=D('1e-10')*max(scalar[9],D('1e-10'));ea=D('1e-10')*max(scalar[10],D('1e-20'))
 nb=(nr+lossn)/na;eb=(er+losse)/ea
 passed=nb<=1 and eb<=1 and lossn<=D('1e-20') and losse<=D('1e-30')
 item={'kind':kind,'family':fam,'s1':r['s1'],'parts':int(r['parts']),'number_ratio':float(nb),'energy_ratio':float(eb),'pass':passed};budgets.append(item)
 if not passed:failures.append(item)
for fam in [0,1,2]:
 seq=[x for x in envelopes if x['family']==fam]
 if not all(b['relative_gap']<a['relative_gap'] for a,b in zip(seq,seq[1:])):failures.append({'envelope_refinement':fam})
report={'status':'PASS' if not failures else 'FAIL','scope':'transparent fixed-shape continuous stock/source sweeps and E^-3 moment envelopes; no evolving gas','owner_checks':len(records),'exact_zero_reference_owners':zeros,'max_positive_owner_relative_error':str(worst),'target':'3e-12','budget_cases':len(budgets),'max_number_budget_ratio':max(x['number_ratio'] for x in budgets),'max_energy_budget_ratio':max(x['energy_ratio'] for x in budgets),'envelopes':envelopes,'geometry_audit':geometry,'owner_results':records,'budget_results':budgets,'failures':failures}
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('envelopes','geometry_audit','owner_results','budget_results','failures')},indent=2));print('failures',len(failures))
if failures:print(json.dumps(failures[:10],indent=2));raise SystemExit(1)
