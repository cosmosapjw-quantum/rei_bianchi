"""Same-author but separately implemented mpmath80 physics verification from raw source."""
import json
from pathlib import Path
import mpmath as mp
from src.emaa_primary import parse_radex,bath_rates,radiative_generator,stationary,energy_flux,HCK,HCJ

mp.mp.dps=80
SOURCE=Path(__file__).resolve().parents[1]/'sources/HD.Rovibration.805a7aa5.radex'
lines=[x.strip() for x in SOURCE.read_text().splitlines()]
lev={}
for i in range(lines.index('! LEVEL | ENERGY [CM-1] | WEIGHT | V_J')+1,lines.index('! NUMBER OF RADIATIVE TRANSITIONS')):
 a=lines[i].split();lev[int(a[0])]=(mp.mpf(a[1]),mp.mpf(a[2]),a[3])
rad=[]
for i in range(lines.index('! TRANS | UP  | LOW | A_ul [s-1] |   FREQ [GHz]  |  E_up [K]')+1,lines.index('! NUMBER OF COLLISION PARTNERS')):
 a=lines[i].split();u,l=int(a[1]),int(a[2]);
 if u<=19:rad.append((u,l,mp.mpf(a[3])))
assert len(rad)==63
anchor=lines.index('7 HD + H+ -- Ref: Gonzales-Lezana et al. J. Chem. Phys. 157 214302 (2022) https://doi.org/10.1063/5.0128598')
Tvals=list(map(mp.mpf,lines[anchor+6].split()))
assert len(Tvals)==25
k={}
for i in range(anchor+8,anchor+8+171):
 a=lines[i].split();k[(int(a[1]),int(a[2]))]=[mp.mpf(z) for z in a[3:]]
assert len(k)==171
# SI exact constants (2019 SI definitions)
H=mp.mpf('6.62607015e-34');C=mp.mpf('299792458');KB=mp.mpf('1.380649e-23')
HCKm=100*H*C/KB;HCJm=100*H*C

def evaluate(Tgas,density,z):
 Tg=mp.mpf(str(Tgas)); n=mp.mpf(str(density));Tr=mp.mpf('2.7255')*(1+mp.mpf(str(z)))
 ti=Tvals.index(Tg);M=mp.matrix(19);R=mp.matrix(19)
 for (u,l),ks in k.items():
  eu,gu,_=lev[u]; el,gl,_=lev[l]; down=n*ks[ti]
  up=down*(gu/gl)*mp.exp(-HCKm*(eu-el)/Tg)
  M[l-1,u-1]+=down;M[u-1,l-1]+=up
 for u,l,A in rad:
  eu,gu,_=lev[u];el,gl,_=lev[l]; N=1/mp.expm1(HCKm*(eu-el)/Tr)
  R[l-1,u-1]+=A*(1+N);R[u-1,l-1]+=A*gu/gl*N
 for G in (M,R):
  for j in range(19):G[j,j]=-sum(G[i,j] for i in range(19) if i!=j)
 G=M+R
 # Ground-normalized M-matrix solve, separate high precision algebra.
 cof=mp.matrix([G[i,0] for i in range(1,19)])
 mat=mp.matrix([[-G[i,j] for j in range(1,19)] for i in range(1,19)])
 x=mp.lu_solve(mat,cof)
 p=mp.matrix([mp.mpf(1)]+list(x));tot=sum(p);p=p/tot
 Er=mp.mpf(0); Ec=mp.mpf(0)
 for i in range(19):
  E=lev[i+1][0]*HCJm
  Er-=E*sum(R[i,j]*p[j] for j in range(19))
  Ec-=E*sum(M[i,j]*p[j] for j in range(19))
 return p,Er,Ec

if __name__=='__main__':
 d=parse_radex();sample=[(105,1e6,30),(3005,1e9,300),(55,1000,100),(505,1e9,0)]
 evidence=[]
 for T,n,z in sample:
  p,pr,pc=evaluate(T,n,z)
  Cp=bath_rates(d,T,n); Rp,_=radiative_generator(d,2.7255*(1+z));q,_=stationary(Cp+Rp)
  Pr=energy_flux(d,Rp,q)
  diff=max(abs(float(p[i])-q[i]) for i in range(19))
  abs_pr=abs(float(pr)-Pr)
  r=abs(float(pr+pc))
  evidence.append({'T_K':T,'n_cm3':n,'z':z,'max_population_abs_difference':diff,'P_rad_absolute_difference_J_s':abs_pr,'mp_energy_balance_J_s':r,'pv1_mpmath':float(sum(p[i-1] for i in range(1,20) if d['levels'][i]['v']==1))})
  assert diff<5e-13 and abs_pr<1e-32 and r<mp.mpf('1e-90')
 root=Path(__file__).resolve().parents[1]/'evidence'
 (root/'MPMATH80.json').write_text(json.dumps({'method':'separately constructed 19x19 mpmath80 source-native master equation','same_author':True,'sample_count':len(evidence),'results':evidence},indent=2)+'\n')
 print(json.dumps(evidence,indent=2))
