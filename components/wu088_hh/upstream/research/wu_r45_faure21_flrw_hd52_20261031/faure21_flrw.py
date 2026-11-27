#!/usr/bin/env python3
"""R45: all 21 published Faure et al 2024 Table-1 fits, 12-species FLRW.
The raw coefficients are author-published; the initial conditions, Compton
thermal closure and full-time reconstructed trajectories are this work's
SOURCE-CONDITIONAL derivation, NOT reproductions of Faure's private outputs.
No chemothermal Q or molecular cooling feedback. Uses pure SI constants outside
cgs reaction rates, which are cm^3 s^-1 or s^-1 (photo).
"""
from __future__ import annotations
from dataclasses import dataclass
import csv, math, json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import G, c as C_LIGHT, sigma, m_e, physical_constants, pi

SPECIES=('H','Hp','Hm','H2','H2p','D','Dp','HD','He','Hep','HeHp','e')
IDX={s:i for i,s in enumerate(SPECIES)}
# H, D, He nucleus and ionic charge covectors: exact integers.
CONSERVED=np.array([
 [1,1,1,2,2,0,0,1,0,0,1,0],
 [0,0,0,0,0,1,1,1,0,0,0,0],
 [0,0,0,0,0,0,0,0,1,1,1,0],
 [0,1,-1,0,1,0,1,0,0,1,1,-1],
],dtype=int)
# Published parameter table from Faure et al MNRAS 531 340 (2024), Table 1.
# Label: (reaction educt stoichiometry, product stoichiometry, alpha, beta, gamma[K], T-source)
# Source types: gas (neutral/electron T) versus radiation (Planck field Tr).
PAPER='https://doi.org/10.1093/mnras/stae994'
TABLE={
'H1': ({'Hp':1,'e':1},{'H':1},3.22e-12,-.675,0.,'gas'),
'H2': ({'H':1},{'Hp':1,'e':1},1.18e7,1.,1.58e5,'rad'),
'H3': ({'Hm':1},{'H':1,'e':1},1.23e4,2.35,8750.,'rad'),
'H4': ({'H':1,'e':1},{'Hm':1},2.45e-16,.846,0.,'gas'),
'H5': ({'Hm':1,'H':1},{'H2':1,'e':1},3.57e-9,-.312,13.8,'gas'),
'H6': ({'Hm':1,'Hp':1},{'H':2},1.89e-7,-.442,0.,'gas'),
'H7': ({'H':1,'Hp':1},{'H2p':1},6.52e-19,1.75,0.,'gas'),
'H8': ({'H2p':1},{'H':1,'Hp':1},3.87e6,.570,3.29e4,'rad'),
'H9': ({'H2p':1,'H':1},{'H2':1,'Hp':1},8.93e-10,0.,0.,'gas'),
'H10':({'H2':1,'Hp':1},{'H2p':1,'H':1},2.43e-10,0.,21400.,'gas'),
'D1': ({'Dp':1,'e':1},{'D':1},3.22e-12,-.675,0.,'gas'),
'D2': ({'D':1},{'Dp':1,'e':1},1.18e7,1.,1.58e5,'rad'),
'D3': ({'Dp':1,'H':1},{'D':1,'Hp':1},2.18e-9,.355,0.,'gas'),
'D4': ({'D':1,'Hp':1},{'Dp':1,'H':1},2.18e-9,.355,43.,'gas'),
'D5': ({'Dp':1,'H2':1},{'Hp':1,'HD':1},1.50e-9,0.,0.,'gas'),
'D6': ({'HD':1,'Hp':1},{'H2':1,'Dp':1},8.57e-10,0.,405.,'gas'),
'He1':({'Hep':1,'e':1},{'He':1},9.08e-13,-.5,0.,'gas'),
'He2':({'He':1},{'Hep':1,'e':1},4.56e7,1.,2.85e5,'rad'),
'He3':({'He':1,'Hp':1},{'HeHp':1},1.45e-19,-.452,13.,'gas'),
'He4':({'HeHp':1},{'He':1,'Hp':1},4.80e4,-.767,22300.,'rad'),
'He5':({'HeHp':1,'H':1},{'He':1,'H2p':1},1.04e-9,.236,24.2,'gas'),
}
assert len(TABLE)==21
LABELS=tuple(TABLE)
EDUCT=np.array([[v[0].get(k,0) for k in SPECIES] for v in TABLE.values()],dtype=int)
PRODUCT=np.array([[v[1].get(k,0) for k in SPECIES] for v in TABLE.values()],dtype=int)
STOICH=(PRODUCT-EDUCT).T
ALPHA=np.array([v[2] for v in TABLE.values()]);BETA=np.array([v[3] for v in TABLE.values()]);GAMMA=np.array([v[4] for v in TABLE.values()]);PHOTO=np.array([v[5]=='rad' for v in TABLE.values()])
assert np.array_equal(CONSERVED@STOICH,np.zeros((4,21),dtype=int))
M_H=1.6735575e-27 # kg H atom; explicit conventional physical mass approximation
MPC=3.085677581491367e22 # metre
SIGMA_T=physical_constants['Thomson cross section'][0]
A_RAD=4*sigma/C_LIGHT # radiation constant J m^-3 K^-4
SEC_MYR=1e6*365.25*86400.

@dataclass(frozen=True)
class Cosmology:
    H0_km_s_Mpc:float=67.4
    Omega_b:float=.0493
    Omega_m:float=.315
    Omega_r:float=9.27e-5
    Omega_L:float=.685
    T0_K:float=2.7255
    Y_He_mass:float=.245 # DECLARED, not primary source's exact helium fraction
    D_over_H:float=2.53e-5 # Faure et al section 3
    z_initial:float=1500.
    z_final:float=30.
    proton_initial_fraction:float=.999
    helium_initial_ion_fraction:float=0.0

    @property
    def H0(self):return self.H0_km_s_Mpc*1e3/MPC
    @property
    def f_he(self):return self.Y_He_mass/(4*(1-self.Y_He_mass))
    @property
    def nH0_cm3(self):return (1-self.Y_He_mass)*self.Omega_b*3*self.H0**2/(8*pi*G)/M_H/1e6
    def Hubble(self,z):return self.H0*np.sqrt(self.Omega_r*(1+z)**4+self.Omega_m*(1+z)**3+self.Omega_L)
    def nH(self,z):return self.nH0_cm3*(1+z)**3


def rates(Tgas,Trad):
    t=np.where(PHOTO,Trad,Tgas)
    return ALPHA*(t/300.)**BETA*np.exp(-GAMMA/t)


def initial(c):
    v=np.zeros(12)
    v[IDX['Hp']]=c.proton_initial_fraction;v[IDX['H']]=1.-c.proton_initial_fraction
    v[IDX['Dp']]=c.D_over_H*c.proton_initial_fraction;v[IDX['D']]=c.D_over_H*(1-c.proton_initial_fraction)
    v[IDX['Hep']]=c.f_he*c.helium_initial_ion_fraction;v[IDX['He']]=c.f_he-v[IDX['Hep']]
    v[IDX['e']]=v[IDX['Hp']]+v[IDX['Dp']]+v[IDX['Hep']]
    return v


def source(z, T, y, cosm, network='faure'):
    nH=cosm.nH(z); k=rates(T,cosm.T0_K*(1+z))
    if network=='grackle_d5d6':
        # Only swap Faure D5/D6 to original Grackle k52/k53, keep other 19 published Faure rates.
        lg=math.log10(T)
        k[LABELS.index('D5')]=1e-9*(.417+.846*lg-.137*lg*lg) if T<=1e4 else 1.609e-9
        k[LABELS.index('D6')]=1.1e-9*math.exp(-488./T)
    elif network!='faure':raise ValueError(network)
    # Chemistry per H nucleus, physical cm^-3/s /nH, no floor/clipping of y state in main law.
    # Clip only tiny negative solver roundoff on the rate monomials to avoid negative production.
    yy=np.maximum(y,0.)
    rate=k*nH**(EDUCT.sum(axis=1)-1)*np.prod(yy[None,:]**EDUCT,axis=1)
    return STOICH@rate,rate


def evolution_rhs(lam, state, cosm, network):
    z=(1+cosm.z_initial)*math.exp(-lam)-1
    y=state[:12];T=state[12]
    H=cosm.Hubble(z);Tr=cosm.T0_K*(1+z)
    dydt,rr=source(z,T,y,cosm,network)
    # Thomson Compton coupling, fHe is helium nuclei per H nucleus.
    xe=max(y[IDX['e']],0.)
    coeff=8*SIGMA_T*A_RAD*Tr**4/(3*m_e*C_LIGHT)*xe/(1+cosm.f_he+xe)
    dT=-2*T + (coeff/H)*(Tr-T)
    return np.concatenate([dydt/H,[dT,1/(H*SEC_MYR)]])


def run(c=Cosmology(),network='faure',N=241,rtol=3e-8):
    if c.z_initial<=c.z_final:raise ValueError('z_initial>z_final')
    L=math.log((1+c.z_initial)/(1+c.z_final))
    y0=initial(c)
    x0=np.r_[y0,c.T0_K*(1+c.z_initial),0.]
    span=np.linspace(0,L,N)
    sol=solve_ivp(evolution_rhs,(0,L),x0,args=(c,network),method='BDF',t_eval=span,
                 rtol=rtol,atol=np.array([2e-13]*12+[5e-7,1e-9]),max_step=.04,dense_output=True)
    if not sol.success: raise RuntimeError(sol.message)
    z=(1+c.z_initial)*np.exp(-sol.t)-1
    resid=CONSERVED@sol.y[:12]-CONSERVED@y0[:,None]
    # electron charge neutrality is also checked in conserved rows.
    return z,sol.y,resid,sol


def rows(c,z,Y,network):
    rows=[];react=[]
    for i,zi in enumerate(z):
        y=Y[:12,i];T=Y[12,i];tr=c.T0_K*(1+zi); H=c.Hubble(zi);nH=c.nH(zi)
        q,rate=source(zi,T,y,c,network)
        row={'network':network,'z':float(zi),'proper_elapsed_Myr':float(Y[13,i]),
             'nH_nuclei_cm3':float(nH),'Tgas_K':float(T),'Trad_K':float(tr),'H_s_inv':float(H),
             'Compton_coeff_over_H':float(8*SIGMA_T*A_RAD*tr**4/(3*m_e*C_LIGHT)*y[IDX['e']]/(1+c.f_he+y[IDX['e']])/H),
             'x_e':float(y[IDX['e']]),'HD_formation_per_H_s':float(rate[LABELS.index('D5')]),
             'HD_destruction_per_H_s':float(rate[LABELS.index('D6')])}
        for j,s in enumerate(SPECIES):row['x_'+s]=float(y[j])
        for j in range(4):row['conserved_'+str(j)]=float(CONSERVED[j]@y)
        rows.append(row)
        for j,label in enumerate(LABELS):
            react.append({'network':network,'z':float(zi),'label':label,
                          'source_rate_coefficient':float(rates(T,tr)[j] if network=='faure' or label not in ('D5','D6') else (1e-9*(.417+.846*math.log10(T)-.137*math.log10(T)**2) if label=='D5' else 1.1e-9*math.exp(-488/T))),
                          'source_coefficient_units':'s^-1' if PHOTO[j] else 'cm3/s',
                          'net_events_per_H_per_s':float(rate[j]),'events_per_cm3_per_s':float(rate[j]*nH)})
    return rows,react


def save_csv(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,list(rows[0]),lineterminator='\n');wr.writeheader()
        for row in rows:wr.writerow({k:format(v,'.17g') if isinstance(v,float) else v for k,v in row.items()})

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];dest=root/'results';dest.mkdir(exist_ok=True)
    c=Cosmology();allrows=[];rates_rows=[];summ={}
    for network in ('faure',):
        z,y,r,s=run(c,network)
        rr,tt=rows(c,z,y,network);allrows+=rr;rates_rows+=tt
        summ[network]={'last_z':float(z[-1]),'last_T':float(y[12,-1]),'last_xHD':float(y[IDX['HD'],-1]),
                       'last_xH2':float(y[IDX['H2'],-1]),'last_xe':float(y[IDX['e'],-1]),
                       'nfev':s.nfev,'min_abundance':float(y[:12].min()),'conserved_max_error':float(np.abs(r).max())}
    save_csv(dest/'R45_FAURE21_FLRW_CHEMISTRY.csv',allrows)
    save_csv(dest/'R45_21_REACTION_EVENT_ATLAS.csv',rates_rows)
    (dest/'CHEMISTRY_SUMMARY.json').write_text(json.dumps(summ,indent=2)+'\n')
    print(json.dumps(summ,indent=2))
