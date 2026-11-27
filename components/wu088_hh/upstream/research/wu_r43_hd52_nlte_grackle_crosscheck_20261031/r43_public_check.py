#!/usr/bin/env python3
"""Source-locked R43 single-point HD52 signed cooling check.
Uses previous WU R36 archived EMAA RADEX/parser; does not invent H+ high-level rates.
"""
import argparse,sys,math,hashlib,importlib.util
from pathlib import Path
import numpy as np
from scipy.constants import h,c,k as kB
EMAA_SHA='b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'
PARSER_SHA='c982bdd3a1dcf61bbd734295a68b2162b536068f4f65eb9e18ff188dd774252b'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(T=70.,nH=1e4,z=30.,source=None,parser=None):
 root=Path(__file__).resolve().parents[2] if 'research' in Path(__file__).parts else Path(__file__).resolve().parent
 base=root/'research/wu_r36_emaa_primary_20261030'
 source=Path(source) if source else base/'sources/HD.Rovibration.805a7aa5.radex'
 parser=Path(parser) if parser else base/'src/emaa_primary.py'
 assert digest(source)==EMAA_SHA and digest(parser)==PARSER_SHA
 spec=importlib.util.spec_from_file_location('r43_source_parser',parser)
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 data=mod.parse_radex(source);assert len(data['levels'])==52 and len(data['radiative'])==368
 pp=data['partners'][5];assert pp['ncol']==1326
 if float(T) not in pp['temps']:raise ValueError('T must be an original EMAA H collision temperature')
 E=np.array([100*h*c*data['levels'][i]['E'] for i in range(1,53)])
 C=np.zeros((52,52));it=pp['temps'].index(float(T))
 for (up,low),rates in pp['rates'].items():
  u,l=up-1,low-1;v=nH*rates[it];dE=E[u]-E[l]
  C[l,u]+=v;C[u,l]+=v*data['levels'][up]['g']/data['levels'][low]['g']*math.exp(-dE/(kB*T))
 np.fill_diagonal(C,-C.sum(axis=0))
 R=np.zeros((52,52));Trad=2.7255*(1+z) if z is not None else 0.
 entries=[]
 for line in data['radiative']:
  u,l=line['up']-1,line['low']-1;dE=E[u]-E[l];A=line['A'];arg=dE/(kB*Trad) if Trad else math.inf
  occupation=1/math.expm1(arg) if arg<700 else 0.
  down=A*(1+occupation);up=A*(data['levels'][u+1]['g']/data['levels'][l+1]['g'])*occupation
  R[l,u]+=down;R[u,l]+=up;entries.append((u,l,dE,down,up))
 np.fill_diagonal(R,-R.sum(axis=0));K=C+R;norm=max(np.max(np.abs(K)),1e-90)
 x=np.linalg.solve(-K[1:,1:]/norm,K[1:,0]/norm);p=np.maximum(np.r_[1.,x],0);p=p/p.sum()
 photon=sum(dE*(down*p[u]-up*p[l]) for u,l,dE,down,up in entries)
 gas=float(E@(C@p));error=abs(photon-gas)/max(abs(photon),abs(gas),1e-60)
 assert error<2e-7 and np.max(abs(K@p))/norm<2e-11
 return {'T_gas_K':T,'n_H_cm_minus3':nH,'T_rad_K':Trad,'photon_J_s_per_HD':float(photon),'collision_J_s_per_HD':gas,'relative_energy_residual':float(error)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--T',type=float,default=70);a.add_argument('--nH',type=float,default=1e4);a.add_argument('--z',type=float,default=30);a.add_argument('--source');a.add_argument('--parser');v=a.parse_args()
 import json
 print(json.dumps(check(v.T,v.nH,v.z,v.source,v.parser),indent=2))
