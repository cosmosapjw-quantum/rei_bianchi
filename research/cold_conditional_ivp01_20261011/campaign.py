"""One bounded native campaign and independent Decimal80 reduced oracle."""
import decimal as dec, hashlib, json, pathlib, subprocess, time, sys
P=pathlib.Path(__file__).resolve().parent
ROOT=P.parents[1]
D=dec.Decimal
dec.getcontext().prec=80
def dump(name,x): (P/'evidence'/name).write_text(json.dumps(x,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def endpoints():
 return [r['endpoint'] for f in ('baseline','refined') for r in json.loads((ROOT/'research/rec_rei_cold_intake01_20261011/inputs'/f'{f}.json').read_text())]
def H(a):
 g=D('4.48162687719e-7')*D('2.728')**4
 return D('3.2407792896393e-18')*(D('.13')*a**-3+D('.343')+g*a**-4*(1+D('.227107317660239')*D('3.04'))).sqrt()
KB=D('1.380649e-23'); CHI=D('13.598434599702')*D('1.602176634e-19')
def rates(t,nh,nhe,xe,tg):
 l=D(315614)/t
 alpha=D('1.269e-19')*l**D('1.503')/(1+(l/D('.522'))**D('.470'))**D('1.923')
 cool=D('1.778e-42')*t*l**D('1.965')/(1+(l/D('.541'))**D('.502'))**D('2.697')
 r=alpha*(nh*xe)**2;c=cool*(nh*xe)**2
 q=D('1.5')*KB*nh*xe*D('4.91466895548409e-22')*tg**4*(tg-t)
 return r,c,q
def reduced(e,n=128):
 ai,nh0,nhe0,xe0,t0,tg0=[D(str(e[k])) for k in ('a','nH_m3','nHe_m3','xe_per_H','Tm_K','Tgamma_K')]
 y=[ai,xe0,t0,D(0),D(0),D(0),D(0)];out=[y.copy()];dt=D('1e14')/n
 def rhs(z):
  a,xe,t=z[:3];nh=nh0*(ai/a)**3;nhe=nhe0*(ai/a)**3;tg=tg0*ai/a
  r,c,q=rates(t,nh,nhe,xe,tg);u=D('1.5')*KB*t*(nh+nhe+nh*xe);h=H(a)
  return [a*h,-r/nh,-2*h*t+(-c+q+D('1.5')*KB*t*r)/(D('1.5')*KB*(nh+nhe+nh*xe)),a**3*r,a**3*(CHI*r+c),-a**3*q,2*h*a**3*u]
 for i in range(n):
  k1=rhs(y);k2=rhs([v+dt*k/2 for v,k in zip(y,k1)]);k3=rhs([v+dt*k/2 for v,k in zip(y,k2)]);k4=rhs([v+dt*k for v,k in zip(y,k3)])
  y=[v+dt*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(y,k1,k2,k3,k4)]
  if (i+1)%(n//4)==0:out.append(y.copy())
 def expand(z):
  a,xe,t=z[:3];nh=nh0*(ai/a)**3;nhe=nhe0*(ai/a)**3
  n=[D(0)]*13;n[1]=nh*(1-xe);n[2]=nh*xe;n[10]=nhe
  return [a,*n,D('1.5')*KB*t*(nh+nhe+nh*xe),*z[3:]]
 return [[float(v) for v in expand(z)] for z in out]
def fields(y):
 a=y[0];nh=y[2]+y[3];nhe=y[11];xe=y[3]/nh;t=y[14]/(1.5*float(KB)*(nh+nhe+y[3]))
 return [*y,nh,xe,t,float(CHI)*y[3],nh+nhe+y[3]]
NAMES=['a']+[f'species_{i}' for i in range(13)]+['u','Rc','Eesc','Ebath','W','nH','xe','T','binding','particles']
def scales(epochs):
 f=fields(epochs[0]);end=fields(epochs[-1]);return [abs(end[i]) if 15<=i<=18 else abs(v) for i,v in enumerate(f)]
def norm(aa,bb,ss):
 m=0.
 for a,b in zip(aa,bb):
  for x,y,s in zip(fields(a),fields(b),ss):
   den=max(abs(x),abs(y),s)
   if den==0:assert x==y
   else:m=max(m,abs(x-y)/den)
 return m
def finite_checks(trajectories,refs):
 checks=[];ledgers=[]
 def identity(name,terms,tol):
  denominator=sum(abs(v) for v in terms);residual=abs(sum(terms))
  value=residual/denominator if denominator else 0.
  assert denominator or residual==0
  checks.append({'name':name,'value':value,'limit':tol,'pass':value<=tol,'denominator':denominator,'terms':terms})
  assert value<=tol,(name,value,tol)
 for r in trajectories:
  if r['control']!='physical' or r['n']!=32:continue
  id=r['id'];ys=r['epochs'];y0=ys[0];a0=y0[0]
  chem0=a0**3*y0[3];hi0=a0**3*y0[2];he0=a0**3*y0[11]
  energy0=a0**3*(y0[14]+float(CHI)*y0[3]);baryon0=a0**3*(y0[2]+y0[3]+4*y0[11])
  for j,y in enumerate(ys):
   a3=y[0]**3
   identity(f'chemistry_{id}_{j}',[-chem0,a3*y[3],y[15]],1e-10)
   identity(f'HI_identity_{id}_{j}',[-hi0,a3*y[2],-y[15]],1e-10)
   identity(f'He_identity_{id}_{j}',[-he0,a3*y[11]],1e-10)
   identity(f'energy_{id}_{j}',[-energy0,a3*(y[14]+float(CHI)*y[3]),y[16],y[17],y[18]],1e-10)
   identity(f'baryon_{id}_{j}',[-baryon0,a3*(y[2]+y[3]+4*y[11])],1e-11)
   identity(f'helium_{id}_{j}',[-he0,a3*y[11]],1e-11)
   for i,name in enumerate(('Rc','Eesc','Ebath','W'),15):
    x,z=y[i],refs[id][j][i];den=max(abs(x),abs(z));error=abs(x-z)/den if den else 0.
    assert den or x==z
    ledger={'endpoint':id,'epoch_fraction':j/4,'ledger':name,'native':x,'reference':z,'comparison_denominator':den,'relative_error':error,'exact_zero':den==0}
    ledgers.append(ledger);checks.append({'name':f'ledger_relative_{id}_{j}_{name}','value':error,'limit':1e-10,'pass':error<=1e-10});assert error<=1e-10
 return checks,ledgers
def main():
 receipt=json.loads((P/'evidence/BUILD_RECEIPT.json').read_text());binary=pathlib.Path(receipt['binary'])
 sources=receipt['sources']
 def preflight(expected):
  assert sha(binary)==expected,'STALE_BINARY_PREFLIGHT'
  for rel,h in sources.items():assert sha(ROOT/rel)==h,'SOURCE_PREFLIGHT'
  assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==receipt['source_commit']
 try:preflight('0'*64)
 except AssertionError as ex:dump('STALE_BINARY_NEGATIVE.json',{'status':'EXPECTED_REJECTION','reason':str(ex),'solver_started':False})
 else:raise AssertionError('negative preflight accepted')
 preflight(receipt['binary_sha256']);dump('PRELAUNCH.json',{'binary_sha256':sha(binary),'source_commit':receipt['source_commit'],'source_tree':receipt['source_tree'],'sources':sources})
 es=endpoints();inp=''.join(' '.join(str(e[k]) for k in ('a','H_s1','Tm_K','nH_m3','nHe_m3','xe_per_H','Tgamma_K'))+'\n' for e in es)
 (P/'evidence/NATIVE_INPUT.txt').write_text(inp)
 start=time.monotonic()
 with (P/'evidence/FIRST_CAMPAIGN.stdout').open('w') as out,(P/'evidence/FIRST_CAMPAIGN.stderr').open('w') as err:
  p=subprocess.run([str(binary)],input=inp,text=True,stdout=out,stderr=err,timeout=120)
 dump('CAMPAIGN_RECEIPT.json',{'elapsed_s':time.monotonic()-start,'returncode':p.returncode,'campaign_attempts':1})
 assert p.returncode==0,'NATIVE_FAILURE'
 rows=[json.loads(v) for v in (P/'evidence/FIRST_CAMPAIGN.stdout').read_text().splitlines()]
 refs=[reduced(e) for e in es];dump('DECIMAL80_REFERENCE.json',{'epochs':refs,'trajectories':4,'steps':512,'rhs_attempts':2048})
 trajectories=[r for r in rows if r['kind']=='trajectory'];checks=[]
 def check(name,x,tol):checks.append({'name':name,'value':x,'limit':tol,'pass':x<=tol});assert x<=tol,(name,x,tol)
 for id,e in enumerate(es):
  ts={r['n']:r['epochs'] for r in trajectories if r['id']==id and r['control']=='physical'};ss=scales(refs[id]);coarse=norm(ts[8],ts[16],ss);fine=norm(ts[16],ts[32],ss)
  check(f'decimal_{id}',norm(ts[32],refs[id],ss),1e-10);check(f'refine_{id}',fine,1e-10)
  if coarse>2e-13:check(f'order_{id}',fine,1.25*coarse)
  checks.append({'name':f'order_status_{id}','status':'ROUNDOFF_LIMITED' if coarse<=2e-13 else 'REFINEMENT_RULE_PASS','coarse':coarse,'fine':fine,'scales':dict(zip(NAMES,ss))})
  for y in ts[32]:
   assert all(y[1+i]==0 for i in range(13) if i not in (1,2,10))
 finite,ledgers=finite_checks(trajectories,refs);checks.extend(finite)
 for r in rows:
  if r['kind']!='stage':continue
  y,dy=r['y'],r['dy'];a=D(str(y[0]));nh=D(str(y[2]+y[3]));nhe=D(str(y[11]));xe=D(str(y[3]))/nh;t=D(str(y[14]))/(D('1.5')*KB*(nh+nhe+nh*xe));e=es[r['id']];tg=D(str(e['Tgamma_K']))*D(str(e['a']))/a
  rr,c,q=rates(t,nh,nhe,xe,tg);h=H(a)
  expected=[a*h,*([D(0)]*13),-5*h*D(str(y[14]))-c+q,a**3*rr,a**3*(CHI*rr+c),-a**3*q,2*h*a**3*D(str(y[14]))]
  expected[2]=-3*h*D(str(y[2]))+rr;expected[3]=-3*h*D(str(y[3]))-rr;expected[11]=-3*h*nhe
  for i,(v,w) in enumerate(zip(dy,expected)):
   if w==0:assert v==0
   else:check(f'stage_oracle_{r["id"]}_{r["n"]}_{r["tau"]}_{i}',abs(v-float(w))/abs(float(w)),3e-12)
  hi,hii,thermal,internal,escape,external=r['sources'];source_scale=sum(abs(v) for v in (thermal,internal,escape,external))
  check('stage_energy',abs(thermal+internal+escape-external)/source_scale,1e-13)
  check('stage_hydrogen_source',abs(hi+hii)/(abs(hi)+abs(hii)),1e-13)
  for v,w in zip(r['sources'],[rr,-rr,-c+q,-CHI*rr,CHI*rr+c,q]):check('source_oracle',abs(v-float(w))/abs(float(w)),3e-12)
 for r in trajectories:
  if r['control']=='physical':continue
  ys=r['epochs'];y0=ys[0];a0=y0[0];t0=fields(y0)[21]
  for y in ys:
   a=y[0];check(r['control']+'_A5u',abs(a**5*y[14]-a0**5*y0[14])/(a0**5*y0[14]),1e-11)
   check(r['control']+'_A2T',abs(a*a*fields(y)[21]-a0*a0*t0)/(a0*a0*t0),1e-11)
   for i in (2,3,11):
    if y0[i]:check(r['control']+'_A3n',abs(a**3*y[i]-a0**3*y0[i])/(a0**3*y0[i]),1e-11)
   assert y[15:18]==[0.,0.,0.]
 for r in rows:
  if r['kind']=='control_stage' and not r['free']:assert r['dy'][15:18]==[0.,0.,0.]
 dump('VALIDATION.json',{'status':'PASS','checks':checks,'native_accounting':rows[-1],'reference_rhs_attempts':2048,'structural_exact_zero':'PASS','time_tag_controls':'PASS','ledger_relative_errors':ledgers,'denominator_policy':'finite identities use epoch term absolute sums; ledger final/comparison magnitudes are comparison-only, never initial or residual scales'})
 dump('RESULTS.json',{'native':trajectories,'scope':'cold source-pinned FLRW finite conditional interval','broader_claims':'HOLD'})
if __name__=='__main__':
 try:main()
 except Exception as ex:
  dump('FIRST_FAILURE.json',{'exception':repr(ex),'status':'STOP_RETURN_TO_ASTRA'});raise
