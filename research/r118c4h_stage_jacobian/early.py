"""Physical REC-clock optical depth with prescribed source-owned BASS shear jet; extended projected defect audit."""
from pathlib import Path
import json,numpy as np,sys,hashlib,time
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
D=Path(__file__).resolve().parent;P=D.parent;G=P/'r118c4g_work_tangent';B=Path.home()/'worktrees/bass-r109-native-20261124/research'
old=(G/'defect_extended.py').read_text();ns={'__file__':str(G/'defect_extended.py'),'__name__':'prior'}
exec(compile(old[:old.index('\nrows=[]')],str(G/'defect_extended.py'),'exec'),ns)
# Exact REI generator from C3Z; BASS early history in identical STF basis.
g=ns['g'];ops=ns['ops'];C=ns['C'];N=ns['N'];pp=ns['pp'];cd=ns['cd'];obs=ns['obs'];relative=ns['relative'];proj=ns['proj'];err_poly=ns['err_poly'];taylor=ns['taylor']
from pathlib import Path
b0=B/'r118c4g_discrete_quadratic/bass.py';bg={'__file__':str(b0),'__name__':'prior'};exec(compile(b0.read_text(),str(b0),'exec'),bg)
jet=B/'r118c4d_precision_jet/jet_4096.npz';z=np.load(jet);t=z['t'];S=z['S'][:,0,:]*.04
clock=B/'r118c3d_four_tracks/REC_CLOCK.csv';e=np.genfromtxt(clock,names=True,delimiter=',');a0=bg['a0'];cut=np.log(1601/1101);u=np.unique(np.r_[t[t<=cut],e['u'][(e['u']>=0)&(e['u']<=cut)],0,cut])
mom,_=bg['bg_table'](u.astype(np.longdouble),192);hh=np.sqrt(mom[:,0]+bg['OL']).astype(float);k=float(bg['K0'])*np.interp(u,e['u'],e['ne_m3'])/hh;s=np.stack([np.interp(u,t,S[:,j]) for j in range(5)],axis=1)
tau=np.r_[0.,cumulative_trapezoid(k,u)];assert tau[-1]>1
f=PchipInterpolator(u,np.c_[s,k],axis=0);inv=PchipInterpolator(tau,u);rows=[]
for target in [v for v in [1.,10.,30.] if v<tau[-1]]+[float(tau[-1])]:
 for steps_per_tau in [16,32]:
  n=max(64,int(np.ceil(target*steps_per_tau)));grid=inv(np.linspace(0,target,n+1));base=np.zeros(N,cd);base[0]=g['Y00'];ref=base.copy();ad=[base.copy(),base.copy()];cnt=[[0,0,0],[0,0,0]];tol=[1e-6,1e-8];false=[0,0];maxdiff=0.;maxA=0.;st=time.monotonic()
  for i,(l,r) in enumerate(zip(grid[:-1],grid[1:])):
   v=f((l+r)/2);A=((r-l)*(sum(x*op for x,op in zip(v[:5],ops))+v[5]*C)).tocsr().astype(cd);maxA=max(maxA,float(np.max(np.asarray(abs(A).sum(axis=1)))));ref=taylor(A,ref,22)
   for j,tt in enumerate(tol):
    y=ad[j];choice=2
    if i:
     for k0,p in enumerate(pp[:2]):
      rs,ds,tail=err_poly(A,y,p);est=2*(relative(ds,rs+ds)+tail)
      if est<=tt/n:choice=k0;break
    p=pp[choice];z=proj(y,p);v0=z.copy()
    for kk in range(1,19):v0=proj(A@v0,p)/kk;z+=v0
    full=taylor(A,y,22);check=taylor(A,y,18);maxdiff=max(maxdiff,relative(full-check,full))
    if choice<2:false[j]+=int(relative(z-full,full)>tt/n)
    cnt[j][choice]+=1;ad[j]=z
  for j,tt in enumerate(tol):
   ob={name:dict(norm=float(np.linalg.norm(x)),adaptive_rel=float(np.linalg.norm(y-x)/max(np.linalg.norm(x),1e-32))) for name,x,y in zip(['E2','B3','E4'],obs(ref),obs(ad[j]))}
   row=dict(tau=target,steps=n,z_end=float(1601*np.exp(-grid[-1])-1),steps_per_tau=steps_per_tau,local_tol=tt,chosen_counts=cnt[j],mean_retained=float(np.dot(cnt[j],[48,57,147])/n),false_accepts=false[j],max_scaled_operator_norm=maxA,reference18_22_gap=maxdiff,observables=ob,seconds=time.monotonic()-st)
   rows.append(row);print(row,flush=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'EARLY_CLOCK_CLOSURE.json').write_text(json.dumps(dict(rows=rows,tau_total=float(tau[-1]),clock_sha=sha(clock),shear_jet_sha=sha(jet),generator=ns['ident'],shear_amplitude=.04,scope='actual primordial scalar REC opacity and BASS first-order prescribed shear jet, zero initial radiation anisotropy, finite lmax6 projected propagation; not self-consistent early REI chemistry or full l hierarchy; reference finite time cells'),indent=2)+'\n')
