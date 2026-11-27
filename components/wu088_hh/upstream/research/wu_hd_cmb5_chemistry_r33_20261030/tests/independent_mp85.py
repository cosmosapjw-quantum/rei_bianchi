"""Independent-algorithm, SAME-AUTHOR high precision check of R33 CMB + chemistry.

Rebuilds the full source-grounded CTMC directly with mpmath. Does not call
src.cmb5.assemble/evaluate; shares verified physical input arrays only.
"""
from __future__ import annotations
import json
from pathlib import Path
import mpmath as mp
from src import cmb5 as app

mp.mp.dps=85
M=mp.mpf

def check():
 parent,old,g,centers=app.get_parent()
 cases=[];worst=M('0');maxabs=M('0')
 # 7 T × 2 policies × 3 density ratios × 5 initial levels × 2 radiation states
 for T in app.TEMPS:
  for policy in app.MODES:
   for ratio in app.RATIOS:
    for J in app.LEVELS:
     for label,z in [('OFF',None),('z100',100)]:
      n=M(str(parent.reference_density(g,T,policy)*ratio))
      trad=M(0) if z is None else M(str(app.T0))*M(1+z)
      # Build independently: no reuse of production assemble(), only source rates.
      K=mp.matrix(5,5);B=mp.matrix(10,5)
      ec=[M(str(g.energies_cm1[k]))*M(100)*M(str(app.H))*M(str(app.C)) for k in range(5)]
      for src in range(5):
       for dst in range(5):
        if src==dst:continue
        if src>dst:
         rate=n*M(str(g.down[(T,src,dst)]))
        else:
         rate=n*M(str(g.down[(T,dst,src)]))*M(2*dst+1)/M(2*src+1)*mp.exp(-(ec[dst]-ec[src])/(M(str(app.KB))*M(T)))
        K[dst,src]+=rate;K[src,src]-=rate
      rad=[]
      for j in range(1,5):
       a=M(str(g.A[j]))
       occ=M(0) if z is None else 1/mp.expm1((ec[j]-ec[j-1])/(M(str(app.KB))*trad))
       down=a*(1+occ);up=a*M(2*j+1)/M(2*j-1)*occ
       K[j-1,j]+=down;K[j,j]-=down
       K[j,j-1]+=up;K[j-1,j-1]-=up
       rad.append((j,a,a*occ,up))
      for j in range(5):
       for f in range(10):
        source=M(str(g.q[(T,j,f)]));w=M(1) if policy==app.MODES[0] else (M('0.75') if f%2 else M('0.25'))
        B[f,j]=n*source*w
        K[j,j]-=B[f,j]
      m=mp.lu_solve(-K,mp.matrix([int(i==J) for i in range(5)]))
      pp=B*m
      em=sum(a*m[j] for j,a,_,_ in rad)
      radiated=sum((ec[j]-ec[j-1])*((a+st)*m[j]-ab*m[j-1]) for j,a,st,ab in rad)
      terminal=sum(ec[j]*sum(B[f,j] for f in range(10))*m[j] for j in range(5))
      # compute bath from conservative internal-energy identity INDEPENDENTLY of rates
      bath=ec[J]-radiated-terminal
      ref,_,_=app.evaluate(parent,g,centers,T,policy,ratio,J,label,z)
      for key,v in [('spont_emissions_per_initial',em),('net_radiative_transfer_J',radiated),
                    ('pre_reaction_HD_rotational_J',terminal),('collisional_proton_bath_gain_J',bath),
                    ('restricted_H2_odd_Jprime_share',sum(pp[i] for i in range(1,10,2)))]:
       ours=M(str(ref[key]));scale=max(abs(v),abs(ours),M('1e-24') if 'J' in key else M('1e-15'))
       err=abs(v-ours)/scale
       worst=max(worst,err)
       maxabs=max(maxabs,abs(v-ours))
       if err>M('3e-10'):
        raise AssertionError((T,policy,ratio,J,label,key,mp.nstr(err,12)))
      cases.append((T,policy,ratio,J,label))
 data={'schema':'wu.r33.same_author_independent_mp85.v1',
       'method':'direct mp85 rate matrix construction and LU solution; not a distinct human reviewer',
       'cases':len(cases),'metric_comparisons':len(cases)*5,'max_scaled_error':float(worst),
       'max_abs_difference':float(maxabs),'scope':'seven native T, two policies, three densities, five J, radiation OFF and z100',
       'different_author_R6_C9':'NOT_RUN'}
 path=app.ROOT/'results/INDEPENDENT_MP85.json'
 path.write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data,indent=2));return data
if __name__=='__main__':check()
