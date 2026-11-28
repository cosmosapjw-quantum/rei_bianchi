"""R10G diagnostic: same frozen source lane, no contour calls or new dynamic Delta.
Not a final multibranch cross-section admission. Rest-of-domain high/error is reused.
"""
import json,math,time
from pathlib import Path
import numpy as np
from endpoint_lab import coulomb_rotation_batch,projectile_velocity_au,author_cutoff
from eta_prototype import eta_magnus
ROOT=Path(__file__).parent/'input';OUT=Path(__file__).parent
X=np.array([.9914553711208126,.9491079123427585,.8648644233597691,.7415311855993945,.5860872354676911,.4058451513773972,.2077849550078985,0.])
WK=np.array([.02293532201052922,.06309209262997855,.1047900103222502,.1406532597155259,.1690047266392679,.1903505780647854,.2044329400752989,.2094821410847278])
WG=np.array([.1294849661688697,.2797053914892767,.3818300505051189,.4179591836734694])
EVENTS=[(2,5,True),(1,5,True),(0,2,False),(3,8,True),(2,7,True)]
BLOCKS=[(2,1,[2,3]),(3,1,[5,6]),(3,2,[7,8,9])]
def gnodes(lo,hi):
 mid=.5*(lo+hi);half=.5*(hi-lo);ys=[]
 for x in X[:-1]:ys.extend([mid-half*x,mid+half*x])
 return np.array(ys+[mid])
def reduce(lo,hi,vals):
 hiw=sum((w*(vals[2*j]+vals[2*j+1]) for j,w in enumerate(WK[:-1])),WK[-1]*vals[-1])
 low=sum((w*(vals[2*j]+vals[2*j+1]) for w,j in zip(WG[:-1],(1,3,5))),WG[-1]*vals[-1])
 return .5*(hi-lo)*hiw,.5*(hi-lo)*abs(hiw-low)
def probabilities(rhos,kind='eta',steps=256):
 rhos=np.array(rhos);Es=np.tile([.5,5.],len(rhos));r=np.repeat(rhos,2)
 rot=np.broadcast_to(np.eye(10),(len(r),10,10)).copy()
 for N,l,idx in BLOCKS:
  if kind=='eta':p,_=eta_magnus(N,l,Es,r,author_cutoff(l),steps)
  else:p=coulomb_rotation_batch(N,l,Es,r,steps=steps,R_cut=author_cutoff(l))['P_abs']
  rot[:,np.array(idx)[:,None],idx]=p
 d=json.loads((ROOT/'inputs/R10C_FROZEN_DELTA0_RECORD.json').read_text());d0=np.array([float.fromhex(x['delta0_hex']) for x in d['records']])
 v=np.array([projectile_velocity_au(e) for e in Es]);p=np.exp(-2*d0/v[:,None]);y=np.zeros((len(r),10));y[:,2]=1.
 def update(k):
  i,j,sink=EVENTS[k];q=p[:,k];yi=y[:,i].copy();yj=y[:,j].copy()
  if sink:y[:,i]=(1-q)*yi;y[:,j]=yj+q*yi
  else:y[:,i]=(1-q)*yi+q*yj;y[:,j]=(1-q)*yj+q*yi
 for k in reversed(range(5)):update(k)
 y=np.einsum('bij,bj->bi',rot,y)
 for k in range(5):update(k)
 assert np.max(abs(y.sum(1)-1))<3e-10
 return y[:,np.arange(10)!=2].reshape(len(rhos),18)
if __name__=='__main__':
 diag=json.loads((ROOT/'review/FIXED_GK_DIAGNOSTIC.json').read_text())
 oldhi=np.asarray(diag['interval_component_high_estimate'])[:,72:90]
 olderr=np.asarray(diag['interval_component_error_estimate'])[:,72:90]
 tail=oldhi[1:].sum(0);tailerr=olderr[1:].sum(0);B=.5111982111775345
 rs=np.sqrt(gnodes(0.,B*B))
 vals=probabilities(rs,'original',1024)
 high,err=reduce(0.,B*B,np.pi*vals)
 print('ARCHIVE HIGH DIFF',np.max(abs(high-oldhi[0])),'ERR DIFF',np.max(abs(err-olderr[0])),flush=True)
 assert np.max(abs(high-oldhi[0]))<1e-12
 a=2/(.8*1836.153*projectile_velocity_au(5.)**2);qend=np.arcsinh(B/a)
 out={'scope':'FIRST_INTERVAL_FROZEN_LANE_ONLY_NEW_COORDINATE_NUMERICAL_DIAGNOSTIC','a_ref':a,'q_end':qend,'B':B,'archive_high_max_diff':float(np.max(abs(high-oldhi[0]))),'archive_error_max_diff':float(np.max(abs(err-olderr[0]))),'rows':[]}
 for transform in ('u','q'):
  for n in (1,2,4,8):
   edges=np.linspace(0.,B*B if transform=='u' else qend,n+1);nodes=np.concatenate([gnodes(x,y) for x,y in zip(edges[:-1],edges[1:])]);rho=np.sqrt(nodes) if transform=='u' else a*np.sinh(nodes)
   v=probabilities(rho,'eta',256)
   f=np.pi*v if transform=='u' else (np.pi*a*a*np.sinh(2*nodes))[:,None]*v
   hs=[];ers=[]
   for k,(x,y) in enumerate(zip(edges[:-1],edges[1:])):
    h,e=reduce(x,y,f[k*15:(k+1)*15]);hs.append(h);ers.append(e)
   h=np.sum(hs,axis=0);e=np.sum(ers,axis=0);score=(e+tailerr)/(1e-10+2e-4*abs(h+tail))
   row={'variable':transform,'local_intervals':n,'rotation_nodes':len(nodes),'max_normalized_embedded':float(max(score)),'failed_components':int(np.count_nonzero(score>1)),'first_interval_high':h.tolist(),'first_interval_error':e.tolist()}
   out['rows'].append(row);print(transform,n,'max',row['max_normalized_embedded'],'fail',row['failed_components'],flush=True)
 (OUT/'FROZEN_ENDPOINT_PILOT.json').write_text(json.dumps(out,indent=2)+'\n')
