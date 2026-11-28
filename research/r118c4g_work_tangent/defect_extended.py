"""C4G complementary defect recurrence; projected polynomial error accumulated without subtracting the carrier."""
from pathlib import Path
import numpy as np,json,sys,io,time
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply
from scipy.interpolate import PchipInterpolator
D=Path(__file__).resolve().parent;F=D.parent/'r118c4f_external_stress'
old=(F/'rei.py').read_text();old=old[:old.index("g={'__file__'")];ns={'__file__':str(F/'rei.py'),'__name__':'inspect'};exec(compile(old,str(F/'rei.py'),'exec'),ns);g={'__file__':str(D/'defect_repair.py'),'__name__':'prior'};exec(compile(ns['src'],'C4F_owner','exec'),g)
raw=g['blob'](g['XBASE'],'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',');u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=g['c']*g['SIG']*h['ne']*1e6/(g['H0']*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0);ops,ident=g['operators'](6);m=49;N=3*m;I=np.eye(N,dtype=complex);C=csr_matrix(np.column_stack([g['collision'](I[:,i],m) for i in range(N)]));p0=np.r_[0,np.arange(4,9),m+np.arange(4,25),2*m+np.arange(4,25)];p1=np.sort(np.r_[p0,np.arange(16,25)]);pp=[p0,p1,np.arange(N)];cd=np.clongdouble
def obs(y):
 v=y.reshape(3,m);e=-.5*(v[1]+v[2]);b=.5j*(v[1]-v[2]);return [e[4:9],b[9:16],e[16:25]]
def relative(d,y):
 return max(float(np.linalg.norm(x)/max(np.linalg.norm(z),1e-32)) for x,z in zip(obs(d),obs(y)))
def proj(y,p):
 z=np.zeros(N,dtype=y.dtype);z[p]=y[p];return z
def err_poly(A,y,p,degree=12):
 r=proj(y,p);d=y-r;rs=r.copy();ds=d.copy()
 # exact term recurrence full - projected, including pre-existing omitted state.
 for k in range(1,degree+1):
  ar=A@r;dr=(A@d+ar-proj(ar,p))/k;r=proj(ar,p)/k;d=dr;rs+=r;ds+=d
 return rs,ds,relative(d,rs+ds)
def taylor(A,y,degree=18):
 v=y.copy();z=v.copy()
 for j in range(1,degree+1):v=A@v/j;z+=v
 return z
def evolve(A,y,p):
 v=np.zeros(N,complex);v[p]=expm_multiply(A[p][:,p],y[p]);return v
rows=[]
for kfac in [1.,1e3,1e6]:
 for sfac in [1.,10.,100.]:
  for n in [32,64]:
   t=np.linspace(0,u[-1],n+1);base=np.zeros(N,complex);base[0]=g['Y00'];ref=base.astype(cd);ad=[base.astype(cd),base.astype(cd)];cnt=[[0,0,0],[0,0,0]];tol=[1e-6,1e-8];false=[0,0];double_false=[0,0];worst=[0.,0.];audit_gap=0.;tail_max=0.;forced=[0,0]
   for i,(l,r) in enumerate(zip(t[:-1],t[1:])):
    v=f((l+r)/2);A=((r-l)*(sum(sfac*x*op for x,op in zip(v[:5],ops))+kfac*v[5]*C)).tocsr();AA=A.astype(cd);ref=taylor(AA,ref)
    for j,tt in enumerate(tol):
     yy=ad[j];y=yy.astype(cd);choice=2;est=0.
     # First cell uses full state to initialize tiny polarization modes. No exact full propagation in later decision.
     if i==0:forced[j]+=1
     else:
      for k,p in enumerate(pp[:2]):
       rs,ds,tail=err_poly(AA,y,p);est=2*(relative(ds,rs+ds)+tail)
       if est<=tt/n:choice=k;break
     p=pp[choice];z=proj(y,p);vv=z.copy()
     for kk in range(1,19):vv=proj(AA@vv,p)/kk;z+=vv
     full=taylor(AA,y);full2=taylor(AA,y,22)
     audit_gap=max(audit_gap,relative(full2-full,full2))
     if choice<2:
      # compare projected evolution in extended precision against full reference: method error separated from expm_multiply roundoff.
      p=pp[choice];zz=proj(y,p);vv=zz.copy();rr=zz.copy()
      for kk in range(1,19):vv=proj(AA@vv,p)/kk;rr+=vv
      exact=relative(rr-full2,full2);double=relative(z.astype(cd)-full2,full2)
      false[j]+=int(exact>tt/n);double_false[j]+=int(double>tt/n);worst[j]=max(worst[j],exact/max(est,1e-300))
     cnt[j][choice]+=1;ad[j]=z
   for j,tt in enumerate(tol):
    ob={name:dict(norm=float(np.linalg.norm(x)),relative=float(np.linalg.norm(y.astype(cd)-x)/max(np.linalg.norm(x),1e-32))) for name,x,y in zip(['E2','B3','E4'],obs(ref),obs(ad[j]))}
    rows.append(dict(opacity_scale=kfac,shear_scale=sfac,steps=n,local_tol=tt,chosen_counts=cnt[j],forced_initial_full=forced[j],truncation_false_accepts=false[j],double_output_false_accepts=double_false[j],max_actual_to_estimate=worst[j],mean_retained=float(np.dot(cnt[j],[48,57,147])/n),reference18_22_max_rel=audit_gap,observables=ob))
   print('defect recurrence',kfac,sfac,n,flush=True)
(D/'DEFECT_EXTENDED.json').write_text(json.dumps(dict(rows=rows,source_sha=g['sha'](raw),identity=ident,scope='cancellation-aware projected Taylor defect recurrence degree12, safety factor2 and initial full cell; extended projected Taylor18 evolution and full Taylor22 audit after decision; same prescribed scaled C3U histories; no rigorous relative bound or speedup claim'),indent=2)+'\n')
print('false accepts',sum(r['truncation_false_accepts'] for r in rows),sum(r['double_output_false_accepts'] for r in rows),flush=True)

