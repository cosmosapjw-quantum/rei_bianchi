"""Independent 80-digit integral oracle. Inputs are captured Rust public outputs."""
import csv,json,pathlib,mpmath as mp
D=pathlib.Path(__file__).resolve().parent;mp.mp.dps=80;eps=mp.mpf('1.602176634e-12');ec=mp.mpf('13.6');summary={'precision_digits':80,'checks':[],'approximation_gates':[]};failures=[]
# Clear quadrature caches per integral and count cached plus current/previous live nodes.
rule=mp.mp._tanh_sinh;original_get_nodes=rule.get_nodes;max_live=0;previous_node_count=0;max_quadrature_estimated_relative=mp.mpf(0)
def tracked_nodes(*args,**kwargs):
 global max_live,previous_node_count
 nodes=original_get_nodes(*args,**kwargs)
 lists={id(v):v for v in list(rule.standard_cache.values())+list(rule.transformed_cache.values())+[nodes]}
 count=sum(map(len,lists.values()))+previous_node_count
 max_live=max(max_live,count);assert count<=4096, f'Live quadrature node cap exceeded: {count}'
 previous_node_count=len(nodes);return nodes
rule.get_nodes=tracked_nodes
def quad(f,points):
 global previous_node_count,max_quadrature_estimated_relative
 rule.clear();previous_node_count=0
 value,error=mp.quad(f,points,maxdegree=7,error=True)
 relative=error/max(abs(value),mp.mpf("1e-100"));max_quadrature_estimated_relative=max(max_quadrature_estimated_relative,relative)
 assert relative<mp.mpf("1e-50"), f"Oracle quadrature unresolved: {relative}"
 return value
def gate(name,error,target,required=True):
 summary['approximation_gates'].append({'name':name,'error':str(error),'target':str(target),'pass':bool(error<=target),'required_for_selected_v2_candidate':required})
def record(name,got,want,rel=mp.mpf('3e-12')):
 got=mp.mpf(got);err=abs(got-want);allow=rel*abs(want)+mp.mpf('1e-300');ratio=err/allow
 summary['checks'].append({'name':name,'got':str(got),'reference':str(want),'absolute_error':str(err),'tolerance_ratio':str(ratio),'pass':bool(err<=allow)})
 if err>allow:failures.append(name)
for k,r in enumerate(csv.DictReader((D/'results/kernel_values.csv').open())):
 h,z,f,q,e=[mp.mpf(r[n]) for n in ['h','lambda_h','f','q','e']];lam=z/h
 def state(v):
  u=h*v
  return f*mp.exp(-lam*u)+(q*u if lam==0 else q*(-mp.expm1(-lam*u))/lam)
 # Independent integrated history, not the Rust divided differences.
 points=[mp.mpf(0),mp.mpf(1)] if z<100 else [mp.mpf(0),1/z,10/z,mp.mpf(1)]
 Nint=h*quad(lambda v:state(v),points);Eint=eps*e*h*quad(lambda v:mp.exp(-h*v)*state(v),points)
 want={'n':state(1),'u':eps*e*mp.exp(-h)*state(1),'red':Eint,'qn':q*h,'qe':eps*e*q*(-mp.expm1(-h))}
 for i,c in enumerate(['0.5','0.3','0.2']):want['a'+str(i)]=mp.mpf(c)*lam*Nint;want['b'+str(i)]=mp.mpf(c)*lam*Eint
 for name,value in want.items():record(f'kernel_{k}_{name}',r[name],value)
for k,r in enumerate(csv.DictReader((D/'results/closure_values.csv').open())):
 l,rr,n,beta=[mp.mpf(r[name]) for name in ['l','r','n','beta']];w=rr-l;front=int(r['front'])
 weight=lambda y:(1-y if front else 1)*mp.exp(beta*y)
 z=quad(weight,[0,1]);m=n*mp.exp(l)*quad(lambda y:mp.exp(w*y)*weight(y),[0,1])/z
 record(f'closure_{k}_M',r['m'],m,mp.mpf('5e-12'))
 # Authoritative inputs are exact binary64 numbers, not the pre-rounded beta.
 ll,rrr,nn,mm,bb=[mp.mpf(float(r[name])) for name in ['l','r','n','m','beta_inverse']];ww=rrr-ll
 iw=lambda y:(1-y if front else 1)*mp.exp(bb*y)
 inverse_mu=quad(lambda y:mp.expm1(ww*y)/mp.expm1(ww)*iw(y),[0,1])/quad(iw,[0,1])
 rounded_target=mp.mpf(float(r['target_scaled']));true_target=mp.expm1(mp.log(mm/nn)-ll)/mp.expm1(ww)
 record(f'closure_{k}_root_scaled',str(inverse_mu),rounded_target,mp.mpf('5e-13')/max(abs(rounded_target),mp.mpf('1e-300')))
 gate(f'closure_{k}_input_scaled_mean',abs(inverse_mu-true_target),mp.mpf('5e-13'))
for k,r in enumerate(csv.DictReader((D/'results/source_values.csv').open())):
 t=mp.mpf(r['t']);emin=mp.mpf('13.7');emax=mp.mpf('100');l=mp.log(emin);upper=t+mp.log(emax);cut=t+mp.log(ec)
 def f(eta,end):
  a=max(mp.mpf(0),eta-mp.log(emax));b=min(end,eta-mp.log(emin))
  return mp.mpf(0) if b<=a else mp.exp(-eta)*(mp.exp(b)-mp.exp(a))
 def integ(fun,a,b):
  if b<=a:return mp.mpf(0)
  pts=sorted(set([a,b]+[x for x in [mp.log(emax),t+mp.log(emin),cut] if a<x<b]));return quad(fun,pts)
 active_l=max(l,cut);N=integ(lambda eta:f(eta,t),active_l,upper);U=eps*integ(lambda eta:mp.exp(eta-t)*f(eta,t),active_l,upper)
 out=integ(lambda eta:f(eta,eta-mp.log(ec)),l,min(cut,upper));Qn=t*(1/emin-1/emax);Qe=eps*t*mp.log(emax/emin)
 # Redshift reference is a direct integral in eta and closed time history,
 # derived from integral E(s)f(s)ds, not an invariant repair.
 def red(eta):
  end=min(t,eta-mp.log(ec));a=max(mp.mpf(0),eta-mp.log(emax));b=min(end,eta-mp.log(emin))
  if b<=a:return mp.mpf(0)
  h=b-a;return eps*(h+mp.expm1(-h)+(1-mp.exp(-h))*(1-mp.exp(-(end-b))))
 R=integ(red,l,upper)
 for name,want in {'n':N,'u':U,'red':R,'qn':Qn,'qe':Qe,'outn':out,'oute':eps*ec*out}.items():record(f'source_{k}_{name}',r[name],want)

# Independent reference for spectrally varying initial-opacity quadrature.
l=mp.mpf(float(mp.log(ec)));r=l+1;t=mp.mpf('0.4')
def initial_abs(eta):
 lam=2*mp.exp(-3*(eta-mp.log(ec)));duration=min(t,eta-mp.log(ec));return mp.mpf('0.3')*mp.exp(2*(eta-l))*(-mp.expm1(-lam*duration))
refabs=quad(initial_abs,[l,t+mp.log(ec),r])
for_row=list(csv.DictReader((D/'results/initial_opacity_convergence.csv').open()))
for row in for_row:
  if row['parts']=='64':gate('initial_opacity_quadrature_64',abs(mp.mpf(row['absorption_N'])-refabs)/refabs,mp.mpf('1e-6'),required=False)
for row in csv.DictReader((D/'results/v2_opacity_candidates.csv').open()):
 error=abs(mp.mpf(row['absorption_N'])-refabs)/refabs
 gate('v2_initial_opacity_quadrature_'+row['parts'],error,mp.mpf('1e-6'),required=row['parts']=='512')
for row in csv.DictReader((D/'results/normalized_targets.csv').open()):
 l,r,n,m,got=[mp.mpf(float(row[name])) for name in ['l','r','n','m','got']]
 true=mp.expm1(mp.log(m/n)-l)/mp.expm1(r-l)
 gate('expanded_normalization_'+row['case'],abs(got-true),mp.mpf('5e-13'))
summary['count']=len(summary['checks']);summary['failures']=failures;summary['maximum_tolerance_ratio']=max(float(c['tolerance_ratio']) for c in summary['checks']);summary['sample_high_water_bound']=max_live;summary['maximum_quadrature_estimated_relative_error']=str(max_quadrature_estimated_relative);summary['status']='FAIL' if failures else ('PARTIAL' if any(not g['pass'] and g['required_for_selected_v2_candidate'] for g in summary['approximation_gates']) else 'PASS');(D/'results/HIGH_PRECISION_ORACLE.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='checks'}));raise SystemExit(1 if failures else (2 if summary["status"]=="PARTIAL" else 0))
