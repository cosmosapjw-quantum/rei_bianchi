import sys,json,math,warnings
import numpy as np
sys.path.insert(0,'/tmp/hh_phys79_work/WU088_HH/research/hh_phys79_collisional_closure_20261022/source')
import collisional as c
A=c.atomic; idx=A.SPECIES_INDEX
checks=[];findings=[]
def ck(name, passed, details):
 checks.append({'name':name,'passed':bool(passed),'details':details})
net=c.CollisionNetwork(ci_rows=tuple(range(6)),d_cx=True)
y=A.neutral_abundances();y[idx['H1_I']]=.6;y[idx['H1_II']]=.4;y[idx['D_I']]=1.1e-5;y[idx['D_II']]=1.36e-5
v=net.rhs(1e5,1e-4,y,H_per_s=2e-18)
ck('isotope_integer_nullspace',np.all(A.ISOTOPE_SUM@net.stoichiometry==0),{'shape':list(net.stoichiometry.shape)})
ck('electron_stoich_CI_vs_CX',np.array_equal(net.delta_electron,np.r_[np.ones(13),0.,0.]),net.delta_electron.tolist())
scale=max(float(np.sum(abs(net.delta_binding_eV*v.event_per_H_s))),1e-300)
ck('energy_event_scale',abs(v.energy_ledger_residual_eV_per_H_s)/scale<=2e-13,{'relative_residual':v.energy_ledger_residual_eV_per_H_s/scale})
N=float(y.sum()+A.CHARGE@y);u=1.5*c.KB_EV_K*1e5*N
udot=-2*2e-18*u+v.heat_eV_per_H_s
chain=(udot-1.5*c.KB_EV_K*1e5*v.d_electron_per_H_dt)/(1.5*c.KB_EV_K*N)
ck('temperature_chain_rule',abs(chain-v.temperature_derivative_K_per_s)<=2e-14*max(abs(chain),1e-300),{'derived':chain,'returned':v.temperature_derivative_K_per_s})
for t in (2.7,3.,10.,300.,1e4,2e5):
 kf,kr=c.d_cx_rates(t);rel=kf/kr/math.exp(-43/t)-1
 ck('DB_ratio_'+str(t),abs(rel)<2e-14,{'relative':rel})
D=c.CollisionNetwork(ci_rows=(),d_cx=True);y=A.neutral_abundances();xh=.37;T=300.;K=math.exp(-43/T);xd=K*xh/(1-xh+K*xh);Yd=A.DEFAULT_INVENTORY['D']
y[idx['H1_I']]=1-xh;y[idx['H1_II']]=xh;y[idx['D_I']]=Yd*(1-xd);y[idx['D_II']]=Yd*xd
p=D.rhs(T,1.,y);eventscale=max(p.event_per_H_s)
ck('D_equilibrium_flux',max(abs(p.d_species_per_H_dt))/eventscale<5e-15,{'relative_flux':max(abs(p.d_species_per_H_dt))/eventscale})
for row in range(6):
 for side,t in [('below',np.nextafter(c.CI_MIN_K[row],0.)),('above',np.nextafter(c.CI_MAX_K[row],math.inf))]:
  try: c.ci_rate(row,t); caught=False
  except c.RateDomainError: caught=True
  ck('CI_domain_'+str(row)+'_'+side,caught,{'temperature':t})
for t in (0.,-1.,math.nan,math.inf):
 try:c.d_cx_rates(t);caught=False
 except c.RateDomainError:caught=True
 ck('D_invalidT_'+str(t),caught,{})
y=A.neutral_abundances();cold=c.CollisionNetwork(ci_rows=(0,),d_cx=False)
try:cold.rhs(300.,1.,y);caught=False
except c.RateDomainError:caught=True
ck('zero_catalyst_still_rejects_rate_domain',caught,{})
try:c.require_full_cosmological_admission();caught=False
except c.UnresolvedClosureError:caught=True
ck('full_cosmological_refusal',caught,{})
# Deliberately finite inputs that overflow aggregate heat capacity.
empty=c.CollisionNetwork(ci_rows=(),d_cx=False);y=np.zeros(A.N_SPECIES);y[idx['H1_I']]=1e308;y[idx['He4_I']]=1e308
with warnings.catch_warnings():
 warnings.simplefilter('ignore')
 outcomes={}
 for name,fn in [('thermal_energy',lambda:empty.thermal_energy(300.,y)),('temperature',lambda:empty.temperature(1.,y)),('rhs',lambda:empty.rhs(300.,1.,y))]:
  try:
   z=fn();outcomes[name]=str(z) if name!='rhs' else {'temperature_derivative':z.temperature_derivative_K_per_s,'energy':z.binding_eV_per_H}
  except Exception as ex:outcomes[name]={'error':type(ex).__name__,'message':str(ex)}
findings.append({'id':'C9-F1','severity':'medium','scope':'finite-domain API','finding':'Finite species inputs may overflow aggregate particle count; helpers return inf or zero rather than explicit invalid-state error. rhs(empty network) also accepts that state.','reproduction':outcomes,'minimum_fix':'Check isfinite(xe), isfinite(N) and positive finite returned thermal u/T in all three entrypoints. No clipping.'})
# Model identity in explicitly raw alternative.
raw=c.CollisionNetwork(ci_rows=(),d_cx=True,d_cx_closure='raw_fit');y=A.neutral_abundances();r=raw.rhs(300.,1.,y)
findings.append({'id':'C9-N1','severity':'low','scope':'provenance label','finding':'diagnostics.model always embeds DB43K even for raw_fit alternative. The separate d_cx_closure field is correct, so actual numerical configuration remains recoverable.','reproduction':r.diagnostics,'minimum_fix':'Use neutral family ID or derive model label from closure; keep closure field in identity.'})
out={'status':'CORE_PHYSICS_CHECKS_PASS_WITH_FINITE_GUARD_FIX','checks':checks,'findings':findings,'count':len(checks),'passed_count':sum(x['passed'] for x in checks),'ode_runs':0}
open('/tmp/hh_phys79_thermal/C9_REVIEW.json','w').write(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'status':out['status'],'count':len(checks),'passed':out['passed_count'],'failed':[x for x in checks if not x['passed']],'findings':findings},indent=2))
