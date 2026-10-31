#!/usr/bin/env python3
"""Independent minimal original-BASS193 Kim92+Coulomb first-ionization replay.
Usage: python reproduce_minimal.py PR309_FULL.zip out.csv
Source conditional, no CCC data, no time integration / secondary cascades.
"""
import csv,hashlib,io,math,sys,zipfile
import numpy as np
from scipy.integrate import cumulative_trapezoid
SHA='f4afbef4475dc8e0320a4c5d22792b5da6ad6a8d4be19f427af949a4dfd59233'
K={'H_I':(13.61,.7576,-5.521,5.867,2.948),
   'He_I':(24.58,.7326,-5.117,3.295,2.468),
   'He_II':(54.42,.06233,-.2982,.2835,.327)}
EV=1.602176634e-12;ME=9.1093837139e-28
E2=.0072973525693*1.054571817e-27*2.99792458e10
LOW=13.7;TOP=60.922559447552

def sigma(E,coef):
    I,A,B,C,D=coef; x=np.asarray(E)/I
    return np.where(x>1,1e-16*(A*np.log(np.maximum(x,1))+
      (B*np.log(np.maximum(x,1))+C*(x-1))/(x+D))/np.maximum(x,1),0.)

def probability(E,ne,targets):
    if E<=LOW:return 0.
    breakpoints=[LOW,K['He_I'][0],K['He_II'][0],TOP]
    energies=np.unique(np.r_[*[np.linspace(a,b,512,endpoint=False)
                      for a,b in zip(breakpoints[:-1],breakpoints[1:])],TOP])
    log=np.log(4*energies/(7.40e-11*ne))
    if np.min(log)<=1:raise ValueError('outside Coulomb domain')
    erg=energies*EV;v=np.sqrt(2*erg/ME)
    loss=4*np.pi*E2**2*ne*log/(ME*v)
    haz=sum(n*sigma(energies,K[s])*v*EV/loss for s,n in targets.items())
    tau=cumulative_trapezoid(haz,energies,initial=0.)
    return float(-np.expm1(-np.interp(E,energies,tau)))

def run(path,outpath):
    if hashlib.sha256(open(path,'rb').read()).hexdigest()!=SHA:raise ValueError('PR309 SHA')
    with zipfile.ZipFile(path) as z:
      b=z.read('REI_F4_BASS_COULOMB_TIMES_20261031/input/REI_F4_CAUSAL_MEMORY_20261031_FULL.zip')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
      with np.load(io.BytesIO(z.read('REI_F4_CAUSAL_MEMORY_20261031/source_bass/trajectory.npz')),allow_pickle=False) as f:
        Y=f['Y'];q=f['q'];zred=f['z']; names=list(f['species_names']);diag=f['diagnostics'];cols=list(f['diagnostic_names'])
        nb=diag[:,cols.index('nb_m3')];ne=diag[:,cols.index('ne_m3')]*1e-6
      bands=list(csv.DictReader(io.StringIO(z.read('REI_F4_CAUSAL_MEMORY_20261031/input/FS2010_BANDS_3840.csv').decode())))
    assert Y.shape==(193,21) and len(bands)==3840
    assert np.max(np.abs(nb*(Y@q)/(ne*1e6)-1))<3e-14
    rows=[];lo=hi=0.
    for i in range(193):
      ns={'H_I':sum(Y[i,names.index(s)] for s in ('H1I','DI','TI')),
          'He_I':sum(Y[i,names.index(s)] for s in ('He3I','He4I')),
          'He_II':sum(Y[i,names.index(s)] for s in ('He3II','He4II'))}
      ns={s:n*nb[i]*1e-6 for s,n in ns.items()}
      rows.append((i,float(zred[i]),float(ne[i]),probability(TOP,ne[i],ns)))
      if i==0:continue
      for b in bands[(i-1)*20:i*20]:
        N=float(b['electron_count_per_b']);Emin=float(b['E_min_eV']);Emax=float(b['E_max_eV'])
        lo+=N*probability(max(Emin,LOW),ne[i],ns)
        hi+=N*probability(min(Emax,TOP),ne[i],ns)
    with open(outpath,'w',newline='') as f:
      w=csv.writer(f);w.writerow(['epoch','z','ne_cm3','p_first_ion_before_Coulomb_13p7']);w.writerows(rows)
    return {'epochs':len(rows),'source_lower':lo,'source_upper':hi,'z20':rows[0][-1],'z2':rows[-1][-1]}

if __name__=='__main__':
    print(run(sys.argv[1],sys.argv[2]))
