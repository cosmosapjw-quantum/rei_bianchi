"""Source-locked, no-IVP Li6 charge-blind tangent jets on 193 saved BASS states.

Rows are proper-time source rates from original BASS native AtomicNetwork.
The 2-jet includes the time derivative of nonautonomous M(t), evaluated from
owner UV/T(x), nb(x), H(x), and native BASS F(Y). Neither a solver nor a
physical REI17/BASS21 cross-model equivalence is implemented.
"""
from __future__ import annotations
import hashlib, importlib, json, math, sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'code'))
import native_full_rate as src

LOCK={
 'source/PR275_SOURCE_FULL.zip': 'de81a869f19f8ffd0db6b12f5bac5c93109f5804b691954c7ac0eae4f22df24b',
 'source/PR121_SOURCE_FULL.zip': '19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907',
 'source/BASS_ORIGINAL_TRAJECTORY.npz':'37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086',
 'source/BASS_ATOMIC_NETWORK.py':'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80',
 'source/BASS_ATOMIC_MODEL.json':'9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614',
}
Q4=np.arange(4,dtype=float)
V=np.array([[1,0],[-2,1],[1,-2],[0,1]],dtype=float)
P_KEEP=np.array(list(range(13))+list(range(17,21)),dtype=int)


def check_sources():
 for name,expected in LOCK.items():
  path=BASE/name
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
   raise ValueError('IMMUTABLE_INPUT_MISMATCH:'+name)
 src.source_manifest_check()
 return {name:expected for name,expected in LOCK.items()}


def load_original():
 check_sources()
 with np.load(BASE/'source'/'BASS_ORIGINAL_TRAJECTORY.npz',allow_pickle=False) as a:
  obj={k:a[k].copy() for k in a.files}
 assert obj['Y'].shape==(193,21) and obj['diagnostics'].shape==(193,25)
 assert len(obj['x'])==193 and np.all(np.diff(obj['x'])>0)
 assert np.all(np.isfinite(obj['Y'])) and np.min(obj['Y'])>=0
 return obj


def recombination_T_derivative(net,T:float):
 """Analytic dGne/dT; original Verner-Ferland RR and Badnell DR tables."""
 a,b,T0,T1,c,T2=net._rr_parameters.T
 effective=b+c*np.exp(-T2/T)
 effp=c*np.exp(-T2/T)*T2/(T*T)
 u=np.sqrt(T/T0);v=np.sqrt(T/T1)
 deriv_log=-(1/(2*T))-(1-effective)*u/(2*T*(1+u))-(1+effective)*v/(2*T*(1+v))+effp*(np.log1p(u)-np.log1p(v))
 r=net.rates(T,0.0)
 rrp=np.zeros(21)
 rrp[net.recombination_indices]=r['rr_m3_s'][net.recombination_indices]*deriv_log
 drp=np.zeros(21)
 expo=np.exp(-net._dr_E/T)
 drp[net._dr_indices]=1e-6*T**-1.5*np.sum(net._dr_c*expo*(net._dr_E/T**2-1.5/T),axis=1)
 return net._transition_matrix(rrp,False)+net._transition_matrix(drp,False)


def original_bath_derivatives(z):
 """Original BASS source: UV(x)=.5[1+tanh((7-z)/.8)], z=21e^-x -1."""
 u=(7.0-z)/.8
 t=math.tanh(u)
 uv_x=.5*(1-t*t)*(1+z)/.8
 return uv_x,11900.*uv_x


def source_point(net,data,i):
 """Exact source algebra at one archived state; no temporal advance or new IVP."""
 y=data['Y'][i].copy()
 gamma=float(net.isotope_inventory['Li6']/net.isotope_inventory['Li7'])
 # Mathematically exact invariant reference in the *same* BASS model:
 y[13:17]=gamma*y[17:21]
 d=data['diagnostics'][i]
 di={str(k):j for j,k in enumerate(data['diagnostic_names'])}
 T=float(d[di['T_K']]);uv=float(d[di['uv_scale']]);nb=float(d[di['nb_m3']]);H=float(d[di['H']]);z=float(data['z'][i]);x=float(data['x'][i]);
 if not (100<=T<=1e6 and 0<=uv<=1 and nb>0 and H>0):raise ValueError('outside source domain')
 rr=net.rates(T,uv);full=net.evaluate(y,T,uv,nb);ne=full['ne']
 M=rr['G0'][13:17,13:17]+ne*rr['Gne'][13:17,13:17]
 up_x,T_x=original_bath_derivatives(z)
 # native original nb(x) proportional to e^(-3x); F=dY/dproper-time
 ne_x=-3*ne+(nb/H)*float(net.q@full['dY_dt'])
 GneT=recombination_T_derivative(net,T)[13:17,13:17]
 Mdot=H*(up_x*net._Gphoto[13:17,13:17]+ne_x*rr['Gne'][13:17,13:17]+ne*T_x*GneT)
 row1=Q4@M@V
 row2_frozen=Q4@M@M@V
 row2_time=Q4@(M@M+Mdot)@V
 s=np.max(np.abs(M))
 if not np.isfinite(s) or s<=0:raise ValueError('bad rate scale')
 obs_frozen=np.vstack((row1/s,row2_frozen/s**2))
 obs_time=np.vstack((row1/s,row2_time/s**2))
 det_frozen=float(np.linalg.det(obs_frozen));det_time=float(np.linalg.det(obs_time))
 # In initial Li6 all charge q=1; in middle/late q=2 has finite occupancy.
 li6=data['Y'][i,13:17]
 eps=.4*float(li6[2])
 perturb=eps*V[:,1]
 assert np.all(li6+perturb>=-1e-40) and abs(perturb.sum())<=max(1e-40,2e-15*eps) and abs(Q4@perturb)<=max(1e-40,2e-15*eps)
 electron_source_change_per_baryon=float(Q4@M@perturb)
 retained_second_t=float(nb*electron_source_change_per_baryon*np.linalg.norm((rr['Gne']@y)[P_KEEP],ord=1))
 # Source J applied to an electron-invisible Li-only variation equals M delta.
 d21=np.zeros(21);d21[13:17]=perturb
 j_diff=full['jac']@d21
 local_linear_error=float(np.max(np.abs(j_diff[13:17]-M@perturb)))
 bBath,uvBath=src.original_bass_bath_at_z(z)
 return dict(epoch=i,x=x,z=z,T_K=T,UV=uv,H_s=H,nb_m3=nb,ne_m3=ne,
     M_max_rate_s=s,det_frozen=det_frozen,det_nonautonomous=det_time,
     jet1_v1_s=float(row1[0]),jet1_v2_s=float(row1[1]),jet2_v1_s2=float(row2_time[0]),jet2_v2_s2=float(row2_time[1]),
     derivative_bath_consistency=float(max(abs(T-bBath),abs(uv-uvBath))),
     perturb_epsilon_per_baryon=eps,perturb_charge_sum=float(Q4@perturb),
     delta_electron_source_per_baryon_s=electron_source_change_per_baryon,
     delta_retained_second_l1_per_baryon_s2=abs(retained_second_t),
     jac_hidden_error_s2=local_linear_error,
     li6_isotope_initial_charge_fractions=(li6/max(float(li6.sum()),1e-40)).tolist()), (M,Mdot,full,rr,y,perturb)


def sign_brackets(rows,key):
 ans=[]
 for i in range(len(rows)-1):
  a=rows[i][key]; b=rows[i+1][key]
  if a*b<0:ans.append(dict(i0=i,i1=i+1,z_low=rows[i+1]['z'],z_high=rows[i]['z'],det_left=a,det_right=b))
 return ans


def calculate():
 data=load_original();net=src.new_native_network()
 rows=[]
 for i in range(193):
  r,aux=source_point(net,data,i);rows.append(r)
 return dict(schema='REI_F4_BASS193_CHARGE_BLIND_JETS_V1',scope='same-BASS BASS21 193 saved source, frozen plus nonautonomous source-linearized charge jets, no IVP',
   original_working='33/88',central='28/88',physical_fast='4/7',original_delta=0,new_ivp=0,
   source_sha=LOCK,
   rate_derivative='Mdot=H[UV_x Gphoto+ne_x Gne+ne*T_x*dGne_dT], ne_x=-3ne+nb qF/H',
   hidden_basis=V.T.tolist(),
   sign_brackets=dict(frozen=sign_brackets(rows,'det_frozen'),nonautonomous=sign_brackets(rows,'det_nonautonomous')),
   minmax=dict(frozen=[min(r['det_frozen'] for r in rows),max(r['det_frozen'] for r in rows)],nonautonomous=[min(r['det_nonautonomous'] for r in rows),max(r['det_nonautonomous'] for r in rows)]),
   saved_193=rows)

if __name__=='__main__':
 import csv
 a=calculate(); out=BASE/'results';out.mkdir(exist_ok=True)
 (out/'RESULT.json').write_text(json.dumps({k:v for k,v in a.items() if k!='saved_193'},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
 with (out/'NATIVE_193_LI_CHARGE_JET_ROWS.csv').open('w',newline='') as f:
  d=[{k:v for k,v in r.items() if k!='li6_isotope_initial_charge_fractions'} for r in a['saved_193']];w=csv.DictWriter(f,fieldnames=list(d[0]));w.writeheader();w.writerows(d)
 print(json.dumps({'rows':len(a['saved_193']),'brackets':a['sign_brackets'],'minmax':a['minmax'],'central':a['saved_193'][150]},ensure_ascii=False,indent=2))
