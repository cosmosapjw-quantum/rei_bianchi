"""Independent mp implementation of source-defined finite-state Markov energy transfer.
It reads source rates from original immutable upstream, but assembles generator
and observables separately from R31 code and from R30 assemble.
Same-author high-precision check, NOT distinct-author R6/C9.
"""
import json
from pathlib import Path
import mpmath as mp
from src import energy_ledger as src

def run():
    mp.mp.dps=75
    mod=src.restore_parent(); p=mod.load_r29(); old=p.load_grid(); g=mod.get_grid(old)
    cases,_,_,_=src.build_atlas()
    hc=mp.mpf('6.62607015e-34')*mp.mpf('299792458')*100
    kb=mp.mpf('1.380649e-23')
    energy=[mp.mpf(str(g.energies_cm1[j]))*hc for j in range(5)]
    max_scaled=mp.mpf('0');max_abs=mp.mpf('0');results=[]
    for case in cases:
      T=case['T_K'];policy=case['policy'];ratio=case['n_over_ncrit_J2'];i0=case['initial_HD_J']
      n=mp.mpf(str(p.reference_density(old,T,policy)))*mp.mpf(str(ratio))
      G=mp.matrix(5); r=[mp.mpf('0') for _ in range(5)]
      for j in range(1,5):
       for i in range(j):
        down=n*mp.mpf(str(g.down[(T,j,i)]))
        up=down*mp.mpf(2*j+1)/mp.mpf(2*i+1)*mp.exp(-(energy[j]-energy[i])/(kb*T))
        G[i,j]+=down;G[j,j]-=down;G[j,i]+=up;G[i,i]-=up
      for j in range(1,5):
        A=mp.mpf(str(g.A[j]));G[j-1,j]+=A;G[j,j]-=A
      for j in range(5):
        weights=[mp.mpf('1') if policy=='raw_SQM' else (mp.mpf('0.75') if h2%2 else mp.mpf('0.25')) for h2 in range(10)]
        r[j]=n*sum(mp.mpf(str(g.q[(T,j,h2)]))*weights[h2] for h2 in range(10))
        G[j,j]-=r[j]
      e=mp.matrix(5,1);e[i0]=1
      m=mp.lu_solve(-G,e)
      coll=mp.mpf('0')
      for j in range(1,5):
       for i in range(j):
        dE=energy[j]-energy[i]
        down=n*mp.mpf(str(g.down[(T,j,i)]))
        up=down*(2*j+1)/(2*i+1)*mp.exp(-dE/(kb*T))
        coll+=dE*(down*m[j]-up*m[i])
      photon=sum((energy[j]-energy[j-1])*mp.mpf(str(g.A[j]))*m[j] for j in range(1,5))
      terminal=sum(energy[j]*r[j]*m[j] for j in range(5))
      tol=max(abs(energy[i0]),max(energy),abs(coll),abs(photon),abs(terminal))
      residual=abs(energy[i0]-(coll+photon+terminal))
      if residual>tol*mp.mpf('1e-60'):raise RuntimeError('MP energy identity failed')
      for col,ref in [('integrated_proton_bath_energy_gain_J',coll),('integrated_photon_energy_J',photon),('terminal_HD_rotational_energy_J',terminal)]:
       err=abs(mp.mpf(str(case[col]))-ref)
       err_scaled=err/max(abs(ref),max(energy)*mp.mpf('1e-6'))
       max_scaled=max(max_scaled,err_scaled);max_abs=max(max_abs,err)
       if err_scaled>mp.mpf('3e-9'):raise RuntimeError('MP vs source double mismatch: '+col+' '+str(err_scaled))
      if T==105 and policy=='Eq6-7_spin_effective' and ratio==1 and i0==2:
       results.append({'case':'105K_initialJ2_spin_ncrit','bath_J':mp.nstr(coll,25),'photon_J':mp.nstr(photon,25),'terminal_J':mp.nstr(terminal,25),'balance_residual_J':mp.nstr(residual,6)})
    out={'schema':'wu.r31.independent_source_assembled_mpmath75.v1','same_author_independent_implementation':True,
         'distinct_author_R6_C9':'NOT_RUN','n_cases':len(cases),'metrics_checked':len(cases)*3,
         'max_scaled_difference':mp.nstr(max_scaled,18),'max_abs_difference_J':mp.nstr(max_abs,18),
         'representative':results}
    path=src.ROOT/'results'/'INDEPENDENT_MP75.json';path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
