#!/usr/bin/env python3
"""Independent high-precision equations for the pinned static FT03+RCT model.
No Rust evaluator is called. This is an author-side numerical oracle, not an
independent scientific review, validated interval proof, or physical fit audit.
"""
from pathlib import Path
import json,hashlib,argparse,mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--input',type=Path,default=ROOT/'evidence/STEP_PROBE.jsonl')
parser.add_argument('--output',type=Path,default=ROOT/'evidence/INDEPENDENT_ENDPOINT_RESULTS.json')
args=parser.parse_args()
mp.mp.dps=90
M=lambda x: mp.mpf(float(x))  # exact lift of each printed round-trippable f64
rows=[json.loads(x) for x in args.input.read_text().splitlines()]
g=rows[0];nh,nhe,c,kb,ev=map(M,[g[x] for x in ['nh','nhe','c','kb','ev']]);f=nhe/nh
chi=list(map(M,g['chi']));eg=list(map(M,g['energy']));sigma=[list(map(M,r)) for r in g['sigma']]
Q=M(float(g['chi'][2])-float(g['chi'][0]))
initial=g['initial']
ABS_BOUND=mp.mpf('5e-14');ROOT_BOUND=mp.mpf('5e-14');EVENT_REL_BOUND=mp.mpf('2e-12')

def normalize(raw):
 a=list(map(M,raw));return mp.matrix([*a[:3],a[3]/(nh*ev),*(x/nh for x in a[4:7])])

def equations(u,k,eb):
 x,y,z,w,p0,p1,p2=u
 ne=nh*x+nhe*(y+2*z);T=2*ev*w/(3*kb*(1+f+x+f*(y+2*z)))
 if not 30000<=T<=110000: raise ValueError('FT03_TEMPERATURE_DOMAIN')
 alpha=[];ci=[];kin=[]
 for a in range(3):
  l=M([315614.,570670.,1263030.][a])/T
  if a==1:
   ar=M(3e-14)*l**M(.654);slope=-M(.654)
  else:
   u0=(l/M(.522))**M(.470)
   ar=M(2. if a==2 else 1.)*M(1.269e-13)*l**M(1.503)/(1+u0)**M(1.923)
   slope=-M(1.503)+M(1.923)*M(.470)*u0/(1+u0)
  alpha.append(ar);kin.append(M(1.380649e-16)*T*ar*(M(1.5)+slope))
  aa=M([21.11,32.38,19.95][a]);pp=M([-1.089,-1.146,-1.089][a]);cc=M([.354,.416,.553][a]);rr=M([.874,.987,.735][a]);dd=M([1.101,1.056,1.275][a])
  ci.append(aa*T**(-M(1.5))*mp.exp(-l/2)*l**pp/(1+(l/cc)**rr)**dd)
 da=M(1.54e-9)*M(11605.)**M(1.5)
 b1=M(40.49664394833662)*M(11605.);b2=M(8.099328789667)*M(11605.)
 adr=[da*T**(-M(1.5))*mp.exp(-b1/T),M(.3)*da*T**(-M(1.5))*mp.exp(-(b1+b2)/T)]
 edr=[M(1.380649e-16)*b1,M(1.380649e-16)*(b1+b2)]
 lo=[nh*(1-x),nhe*(1-y-z),nhe*y];hi=[nh*x,nhe*y,nhe*z]
 ph=[[c*lo[a]*sigma[a][j]*nh*u[4+j] for j in range(3)] for a in range(3)]
 C=[lo[a]*ne*ci[a] for a in range(3)];R=[hi[a]*ne*alpha[a] for a in range(3)];K=[hi[a]*ne*kin[a] for a in range(3)];D=[hi[1]*ne*v for v in adr]
 net=[sum(ph[a])+C[a]-R[a] for a in range(3)];net[1]-=sum(D)
 r=k*lo[0]*hi[2]
 heat=sum(ph[a][j]*(eg[j]-chi[a])*ev for a in range(3) for j in range(3))-sum(C[a]*chi[a]*ev+K[a] for a in range(3))-sum(D[j]*edr[j] for j in range(2))+(Q-eb)*ev*r
 escape=sum(R[a]*chi[a]*ev+K[a] for a in range(3))+sum(D[j]*(chi[1]*ev+edr[j]) for j in range(2))+eb*ev*r
 rhs=mp.matrix([(net[0]+r)/nh,(net[1]-net[2]+r)/nhe,(net[2]-r)/nhe,heat/(nh*ev),*[-sum(ph[a][j] for a in range(3))/nh for j in range(3)]])
 return rhs,escape,r

results=[];max_res=mp.mpf(0);max_root=mp.mpf(0);max_event=mp.mpf(0)
for index,row in enumerate(rows[1:]):
 k=M(row['k']);eb=M(row['mean_ev']);dt=M(row['dt']);start=normalize(initial)
 local=[]
 for label,old,new,h in [('full',initial,row['full'],dt),('half1',initial,row['half1'],dt/2),('half2',row['half1'],row['half2'],dt/2)]:
  u0=normalize(old);u1=normalize(new);rhs,esc,r=equations(u1,k,eb)
  scales=mp.matrix([1,1,1,max(M(old[3]),M(1e-30))/(nh*ev),*[max(M(x),M(1e-30))/nh for x in old[4:7]]])
  defects=[abs((u1[j]-u0[j]-h*rhs[j])/scales[j]) for j in range(7)]
  # Same energy scale definition, evaluated independently from raw state.
  total0=M(old[3])+ev*(nh*chi[0]*u0[0]+nhe*(chi[1]*u0[1]+(chi[1]+chi[2])*u0[2]))+sum(eg[j]*ev*M(old[4+j]) for j in range(3))+M(old[7])
  defects.append(abs((M(new[7])-M(old[7])-h*esc)/max(total0,M(1e-30))))
  value=max(defects);max_res=max(max_res,value)
  if value>ABS_BOUND: raise AssertionError((index,label,'independent residual',mp.nstr(value)))
  local.append({'site':label,'max_scaled_residual':mp.nstr(value,30)})
 # Root solve uses the original initial state, not the native answer, as initial guess.
 fun=lambda *args: tuple(mp.matrix(args)-start-dt*equations(mp.matrix(args),k,eb)[0])
 root=mp.findroot(fun,tuple(start),tol=mp.mpf('1e-75'),maxsteps=30)
 native=normalize(row['full'])
 root_def=max(abs(root[j]-native[j])/max(abs(start[j]),mp.mpf(1)) for j in range(7))
 exact_r=equations(root,k,eb)[2];exact_event=dt*exact_r
 event_rel=abs(M(row['J_full'])-exact_event)/abs(exact_event)
 if root_def>ROOT_BOUND or event_rel>EVENT_REL_BOUND: raise AssertionError((index,'root/event',mp.nstr(root_def),mp.nstr(event_rel)))
 max_root=max(max_root,root_def);max_event=max(max_event,event_rel)
 results.append({'case':index,'dt_s':row['dt'],'mean_ev':row['mean_ev'],'adaptive_status':row['status'],'sites':local,'max_root_scaled_difference':mp.nstr(root_def,30),'RCT_event_relative_difference':mp.nstr(event_rel,30)})
result={'status':'FINITE_INDEPENDENT_EQUATION_CHECK_PASS','precision_dps':90,'implicit_cases':len(results),'endpoint_sites':sum(len(x['sites']) for x in results),'independent_root_solves':len(results),'max_scaled_endpoint_residual':mp.nstr(max_res,40),'max_scaled_root_difference':mp.nstr(max_root,40),'max_RCT_event_relative_difference':mp.nstr(max_event,40),'residual_bound':str(ABS_BOUND),'root_bound':str(ROOT_BOUND),'event_relative_bound':str(EVENT_REL_BOUND),'results':results,'scope':'author-written independent equation path for same fitted mathematical model; not interval/physical/scientific-review certification','source':'pinned ft03_rates.rs  b8a85ff37de160ecc576a168e4259ed23920a499 and unchanged ft03/he_rct equations','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
