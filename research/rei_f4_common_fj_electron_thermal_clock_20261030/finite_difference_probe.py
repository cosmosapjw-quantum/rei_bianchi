import sys
sys.path.insert(0,'/mnt/data/rei_physical_fast_work/node/code')
import bridge, numpy as np, io
with bridge.load_archive('REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip') as z:
 net,s,rei=bridge.net_and_trajectory(z)
D={str(n):s['diagnostics'][:,i] for i,n in enumerate(s['diagnostic_names'])}
for i in [0,33,97,192]:
 y=s['Y'][i].copy(); v=np.sin(np.arange(21)+1.0);v/=np.linalg.norm(v)
 t=D['T_K'][i];u=D['uv_scale'][i]; n=D['nb_m3'][i]
 J=net.evaluate(y,t,u,n)['jac']; h=1.e-7
 fd=(net.evaluate(y+h*v,t,u,n)['dY_dt']-net.evaluate(y-h*v,t,u,n)['dY_dt'])/(2*h)
 pred=J@v
 ratio=np.linalg.norm(fd-pred)/max(np.linalg.norm(pred),1e-80)
 print(i,ratio,np.linalg.norm(pred))