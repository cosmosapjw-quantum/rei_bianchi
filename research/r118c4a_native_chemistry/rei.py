"""C4A exact PR378 source-pinned local chemistry and native discrete map + physical Thomson memory."""
from pathlib import Path
import numpy as np,json,hashlib,sys,subprocess,tarfile,io,shutil
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent;R=D.parents[1];PR='b145729be3d9d103ef1379c9efe5f85687558bc6';XB='0e624af4668c7722759ccf781d91e15362b6d451';X='research/r118c3x_tangent_source/fine_2048_129_32_8';OU='research/r118c3u_positive_owner/birth_1024_32ray/history.csv';H0=2.1842852410855023e-18
def sha(x):return hashlib.sha256(x).hexdigest()
def blob(ref,p):return subprocess.check_output(['git','-C',str(R),'show',ref+':'+p])
def csv(ref,p):
 b=blob(ref,p);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=','),sha(b)
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 root=Path.home()/'r118c4a_rei_shadow';root.mkdir(exist_ok=False)
 paths=['rust/rei_microphysics','docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json','research/flrw_jacobian_columns_20261016/CONTRACT.json','research/r118c3b_ff_balance/gauntff.dat','research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json','research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md','research/flrw_covariant_transport_20261015/NATIVE_CONTRACT.md','research/flrw_covariant_transport_20261015/INACTIVE_POOL_CONTRACT.md','research/flrw_covariant_transport_20261015/HPC_CONTRACT.md','research/flrw_covariant_transport_20261015/BACKGROUND_CACHE_CONTRACT.md','research/flrw_covariant_transport_20261015/OUTPUT_ALLOCATION_005_CONTRACT.md','src/rei_bianchi/microphysics/data/savin2002_charge_exchange.csv']
 ar=subprocess.check_output(['git','-C',str(R),'archive',PR,*paths])
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(root,filter='data')
 crate=root/'rust/rei_microphysics';p=crate/'src/axbi_covariant_driver.rs';old=p.read_bytes()
 # Rebase only energy reference on a fresh zero-inventory initial state. No step/physics source modified.
 token='impl Driver {\n    pub fn new(config: DriverConfig)'
 add='''impl Driver {
    /// Research-only: change the reference initial energy after a gas-coordinate perturbation.
    pub fn c4a_rebase_initial(&mut self, s:&DriverState)->Result<(),ForwardError>{
        if s.accepted!=0 || s.a!=1./21. || s.ledgers.source_n!=0. || s.ledgers.source_u!=0. || self.photon_inventory(s)!=(0.,0.){return Err(err("C4A_INITIAL_REBASE_DOMAIN"))}
        self.initial_energy=self.total_energy(s)?;
        self.validate(s,1e-8)
    }
    pub fn new(config: DriverConfig)'''
 s=old.decode();assert s.count(token)==1;p.write_text(s.replace(token,add))
 (crate/'examples/c4a_probe.rs').write_bytes((D/'probe.rs').read_bytes())
 cfg=blob(PR,'research/r118c3i_event_ledger/table.cfg');(D/'CONFIG.cfg').write_bytes(cfg)
 a,sa=csv(XB,X+'/matter.csv');h,sh=csv(XB,X+'/history.csv');assert np.array_equal(a['a'],h['a'])
 rows=np.column_stack([a['a'],a['h'],*[a[f'F{i}{j}'] for i in range(3) for j in range(3)],h['xHII'],h['xHeII'],h['xHeIII'],h['thermal'],a['nh_m3']])
 np.savetxt(D/'ACTUAL_HISTORY.csv',rows,delimiter=',',header='a,h,F00,F01,F02,F10,F11,F12,F20,F21,F22,xHII,xHeII,xHeIII,w_eV_per_H,nh_m3',comments='',fmt='%.17e')
 info=dict(base=PR,archive_sha256=sha(ar),archive_bytes=len(ar),paths=paths,driver_original_sha256=sha(old),driver_patch_sha256=sha(p.read_bytes()),probe_sha256=sha((D/'probe.rs').read_bytes()),config_sha256=sha(cfg),matter_source_sha256=sa,gas_source_sha256=sh,scope='exact PR378 with one research initial-energy reference setter; native scalar FF mode2 and external prescribed geometry, not DG patched map')
 write('BUILD_ID.json',info);print(info,flush=True)
 with (D/'build.log').open('w') as f:r=subprocess.run(['cargo','build','--release','--offline','--example','c4a_probe'],cwd=crate,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 if r.returncode:raise RuntimeError('native build failed')
 binary=crate/'target/release/examples/c4a_probe';info['binary_sha256']=sha(binary.read_bytes());info['binary_bytes']=binary.stat().st_size;write('BUILD_ID.json',info)
 with (D/'native.log').open('w') as f:r=subprocess.run([str(binary),str(D/'CONFIG.cfg'),str(D/'ACTUAL_HISTORY.csv'),str(D/'POINT.csv'),str(D/'STEP.csv')],stdout=f,stderr=subprocess.STDOUT,timeout=200)
 if r.returncode:raise RuntimeError('native probe failed')
def analyze():
 p=np.genfromtxt(D/'POINT.csv',names=True,delimiter=',');q=np.genfromtxt(D/'STEP.csv',names=True,delimiter=',');assert np.isfinite(p.view(float)).all() and np.isfinite(q.view(float)).all()
 p0=p[(p['snapshot']==0)&(p['col']==-1)][0];scale=np.array([p0['x'],1e-4,1e-4,p0['w']])
 def values(r,keys):return np.array([r[k] for k in keys])
 def fd(rows,keys,eps,incr=False):
  base=rows[rows['col']==-1][0];f0=values(base,keys)
  def get(c,e):
   t=rows[(rows['col']==c)&np.isclose(rows['eps'],e,rtol=1e-13,atol=1e-15)]
   if len(t)>1:
    assert np.all(t==t[0]),(c,e)
   if not len(t):raise KeyError((c,e))
   z=values(t[0],keys)
   if incr:z-=values(t[0],['x0','y0','z0','w0'])
   return z
  if incr:f0-=values(base,['x0','y0','z0','w0'])
  J=[]
  for c in range(4):
   try:a=(get(c,eps)-get(c,-eps))/(2*eps)
   except KeyError:a=(-3*f0+4*get(c,eps)-get(c,2*eps))/(2*eps)
   J.append(a/scale)
  return np.array(J).T
 es=[.02,.01,.005,.0025];pts=[]
 for i in np.unique(p['snapshot']):
  v=p[p['snapshot']==i];Js=[fd(v,['fx','fy','fz','fw'],e) for e in es]
  dif=[np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-300) for a,b in zip(Js[:-1],Js[1:])]
  pts.append(dict(snapshot=int(i),J_scaled_du=Js[-1].tolist(),FD_refinement=dif,charge_max=float(np.max(abs(v['charge_res']))),energy_max=float(np.max(abs(v['energy_res'])))))
 steps=[]
 for i in np.unique(q['grid']):
  v=q[q['grid']==i];du=v['du'][0];Js=[fd(v,['x1','y1','z1','w1'],e,True)/du for e in es];base=v[v['col']==-1][0];point=np.array(pts[0]['J_scaled_du'])
  dif=[np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-300) for a,b in zip(Js[:-1],Js[1:])]
  steps.append(dict(grid=int(i),du=float(du),J_increment_per_du_scaled=Js[-1].tolist(),FD_refinement=dif,native_point_relative_difference=float(np.linalg.norm(Js[-1]-point)/np.linalg.norm(point)),max_accepted_metric=float(max(v['metric'])),max_energy_res=float(max(abs(v['energy_res']))),max_number_res=float(max(abs(v['number_res']))),rhs_max=int(max(v['rhs'])),base_photon_n=float(base['photon_n']),base_photon_u=float(base['photon_u']),perturbations=len(v)))
 out=dict(point=pts,step=steps,scale=scale.tolist(),scope='native point zero-photo on actual history; native accepted discrete conditional fixed geometry scalar FF2 with actual initial gas. Not C3X spectral DG or coupled Einstein derivative. Point and discrete map differ by finite source/geometry/ff and dt.')
 write('CHEMISTRY.json',out);print(out,flush=True)
def memory():
 from scipy.constants import c
 rows=[]
 for label,h,sh,ne in []:pass
 h,sh=csv(XB,OU)
 m,sm=csv(XB,X+'/matter.csv');g,sg=csv(XB,X+'/history.csv')
 for label,u,K,S,hs in [('C3U',np.log(h['a']/h['a'][0]),c*6.6524587051e-29*h['ne']*1e6/(H0*h['h']),h['S0'],sh),('C3X',np.log(g['a']/g['a'][0]),c*6.6524587051e-29*m['ne_m3']/(H0*m['h']),g['S0'],sg)]:
  assert len(u)>1 and np.all(np.diff(u)>0) and min(K)>=0
  f=PchipInterpolator(u,np.c_[K,S],axis=0);d=np.sqrt(8/3);b=.4/d;cc=.15*d
  def rhs(t,y):
   k,s=f(t);I,E=y;return [-4*s+k*(-.9*I+b*E),k*(cc*I-.4*E)]
  ref=solve_ivp(rhs,(u[0],u[-1]),[0.,0.],rtol=2e-12,atol=1e-22,max_step=np.max(np.diff(u))/4,method='DOP853',dense_output=True);assert ref.success
  mark=solve_ivp(lambda t,y:-4*f(t)[1]-.75*f(t)[0]*y,(u[0],u[-1]),[0.],rtol=2e-12,atol=1e-22,max_step=np.max(np.diff(u))/4,method='DOP853');assert mark.success
  def calc(n):
   t=np.concatenate([np.linspace(a,b,n,endpoint=False) for a,b in zip(u[:-1],u[1:])]+[u[-1:]]);dt=np.diff(t);k,s=f((t[1:]+t[:-1])/2).T
   G=np.r_[0,np.cumsum(k*dt)];I=np.zeros(len(t));E=I.copy()
   for j,(hh,kk,ss) in enumerate(zip(dt,k,s)):
    phi=np.exp(-.4*kk*hh);p=cc*(-np.expm1(-.4*kk*hh))/.8
    I[j+1]=((1-.9*kk*hh/2+b*kk*hh*p/2)*I[j]+b*kk*hh*(1+phi)*E[j]/2-4*ss*hh)/(1+.9*kk*hh/2-b*kk*hh*p/2)
    E[j+1]=phi*E[j]+p*(I[j]+I[j+1])
   direct=np.sum(np.exp(-.4*(G[-1]-G[1:]))*cc*(-np.expm1(-.4*k*dt))/.4*(I[:-1]+I[1:])/2)
   assert abs(direct-E[-1])<1e-11*max(abs(E[-1]),1e-300)
   e=np.linalg.norm(np.array([I[-1],E[-1]])-ref.y[:,-1])/max(np.linalg.norm(ref.y[:,-1]),1e-300)
   return I[-1],E[-1],direct,G[-1],e
  a,b1,z=[calc(n) for n in [2,4,8]];x=ref.y[:,-1];mk=mark.y[0,-1]
  rows.append(dict(label=label,history_sha256=hs,steps=len(u)-1,delta_u=float(u[-1]-u[0]),integrated_thomson_depth=float(z[3]),explicit_I_E=x.tolist(),memory_I_E=list(map(float,z[:2])),direct_convolution_E=float(z[2]),relative_refinement_errors=[float(a[-1]),float(b1[-1]),float(z[-1])],Markov_I=float(mk),Markov_E=float(.375*d*mk),Markov_I_relative=float(abs(mk-x[0])/max(abs(x[0]),1e-300)),Markov_E_relative=float(abs(.375*d*mk-x[1])/max(abs(x[1]),1e-300)),scope='physical rest-electron Thomson l2 collision block with actual S0 and K, zero IC; no full l-coupling streaming'))
 write('THOMSON_MEMORY.json',dict(rows=rows,kernel='.06 K(u)K(v) exp(-.4 integral K)',collision_eigenvalues=[-1,-.3],scope='exact E elimination of quadrupole collision block; supplied shear source, not full hierarchy nor plasma OU kernel'));print(rows,flush=True)
if __name__=='__main__':{'build':build,'analyze':analyze,'memory':memory}[sys.argv[1]]()

