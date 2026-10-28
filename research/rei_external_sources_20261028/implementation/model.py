"""Frozen-contract local source operator; no trajectory integration.

All stocks are particles/Href, rates events/Href/s, powers eV/Href/s.
Separate fast stocks are part of baryon and charge accounting.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
BASE = UNIT.parent / 'rei_fast_selected_20261028'
CSV_PATH = BASE / 'outputs/grid044_M4_nominal_all21_populations.csv'
NPZ_PATH = BASE / 'inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023/results/grid044_M4_nominal.npz'
EXPECTED_CSV = '68b316ae614db15f5765cf97c8f634fb57b3efc8f6a597236a27ec6bcdc3c539'
EXPECTED_NPZ = 'ac035e9bdc6427dd66cbc3a39db92769ffc23f2ae8de7a2c1200b83fb9f20619'
LABELS = ('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2','He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
HIDDEN = ('Li6_0','Li6_1','Li6_2','Li6_3')
A = np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7,1,3], dtype=int)
Q = np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1], dtype=int)
FAMILIES = {'H1':(1,[13.6]),'D':(3,[13.6]),'T':(5,[13.6]),'He3':(7,[24.6,54.4]),'He4':(10,[24.6,54.4]),'Li7':(13,[5.4,75.6,122.4])}
NUCLEAR = [('D_n','D',[(2,1)],17,-2224600.),('He4_T','He4',[(2,1)],18,-19813900.),('He4_n','He4',[(9,1)],17,-20577600.),('Li7_T','Li7',[(12,1)],18,-2467000.)]
POWERS = ('photon_input','cr_input','injected_kinetic','nuclear_internal','atomic_internal','heat','fast_electron','neutrino','escaping_radiation','escaped_kinetic','fast_kinetic_change')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config():
    c = json.loads(Path(__file__).with_name('config.json').read_text())
    # Evaluate the declared lifetime expression instead of rounding its reciprocal.
    c['lambda_n_s'] = 1 / 878.4
    c['lambda_T_s'] = math.log(2)/(c['T_half_life_years']*c['year_days']*86400)
    return c


def load_baseline():
    if digest(CSV_PATH) != EXPECTED_CSV or digest(NPZ_PATH) != EXPECTED_NPZ:
        raise ValueError('immutable baseline identity mismatch')
    with CSV_PATH.open() as f:
        rows = list(csv.DictReader(f))
    eta = np.array([float(r['eta_ln_a_over_ai']) for r in rows])
    z = np.array([float(r['z_mean']) for r in rows])
    y = np.array([[float(r['per_Href__'+k]) for k in LABELS] for r in rows])
    hidden = np.array([[float(r['per_Href__'+k]) for k in HIDDEN] for r in rows])
    with np.load(NPZ_PATH, allow_pickle=False) as saved:
        native_eta = saved['eta'].copy()
        density = saved['nHref'].copy()
    if eta.shape != (201,) or y.shape != (201,17) or not np.allclose(eta,native_eta,rtol=0,atol=5e-15):
        raise ValueError('201-epoch baseline serialization alignment failed')
    if density.shape != (201,) or np.any(density <= 0) or not np.isfinite(density).all():
        raise ValueError('saved nHref density schema invalid')
    return eta,z,y,hidden,density


def atomic_sigma(E,I,c):
    return c['atomic_sigma0_cm2']*(I/E)**3 if E>I else 0.


def nuclear_sigma(E,required,c):
    return c['nuclear_sigma0_cm2']*(1-required/E)**2 if E>required else 0.


def cr_sigma(E,c):
    return c['cr_sigma0_cm2']*(1-c['cr_cutoff_eV']/E)**2 if E>c['cr_cutoff_eV'] else 0.


def branching(ks,ke,decay):
    L=ks+ke+decay
    if L<=0:
        raise ValueError('nonpositive fast loss denominator')
    return np.array([ks,ke,decay])/L,L


def reservoirs(y,alpha,c):
    """Direct source plus bin-by-bin nuclear/CR daughters and kinetic power."""
    S=alpha*np.asarray(c['fast_injection_per_Href_s'],float)
    P=S*c['fast_injection_kinetic_eV']
    for name,fam,stable,fast,qvalue in NUCLEAR:
        start,thresholds=FAMILIES[fam]
        for charge in range(len(thresholds)+1):
            strip=sum(thresholds[charge:]); req=-qvalue+strip
            for E,F in c['photon_bins_eV_flux_cm2_s']:
                rate=alpha*F*nuclear_sigma(E,req,c)*y[start+charge]
                S[fast-17]+=rate; P[fast-17]+=rate*(E-req)/2
    start,thresholds=FAMILIES['He4']
    for charge in range(3):
        for j,qvalue in enumerate((-20577600.,-19813900.)):
            E=c['cr_energy_eV']; rate=alpha*c['cr_flux_cm2_s']*cr_sigma(E,c)*y[start+charge]
            K=E+qvalue-sum(thresholds[charge:])
            if rate and K<0: raise ValueError('CR event admitted with negative kinetic energy')
            S[j]+=rate; P[j]+=rate*K/2
    branches=[]; losses=[]
    for j,k in enumerate(('n','T')):
        br,L=branching(c['ks_'+k+'_s'],c['ke_'+k+'_s'],c['lambda_'+k+'_s']/c['gamma_'+k])
        branches.append(br); losses.append(L)
    losses=np.array(losses)
    return {'S':S,'P':P,'B':S/losses,'U':P/losses,'fractions':np.array(branches),'L':losses}


def qss(y,nref,alpha,c,res=None,escape=True):
    res=reservoirs(y,alpha,c) if res is None else res
    esc=c['kesc_s'] if escape else 0.
    Sn=alpha*c['thermal_injection_per_Href_s'][0]+c['ks_n_s']*res['B'][0]
    cap=nref*(y[1]+y[2])*c['capture_C_cm3_s']
    Ln=c['lambda_n_s']+cap+esc
    S0=alpha*c['thermal_injection_per_Href_s'][5]
    S1=alpha*c['thermal_injection_per_Href_s'][6]+c['ks_T_s']*res['B'][1]
    Gamma=sum(alpha*F*atomic_sigma(E,13.6,c) for E,F in c['photon_bins_eV_flux_cm2_s'])
    L=c['lambda_T_s']+esc; rec=c['T_recombination_s']; D=L*(L+Gamma+rec)
    stocks=np.array([Sn/Ln,((L+rec)*S0+rec*S1)/D,(Gamma*S0+(L+Gamma)*S1)/D])
    return {'stocks':stocks,'sources':np.array([Sn,S0,S1]),'Ln':Ln,'LT':L,'Gamma':Gamma,'rec':rec,'kcap':cap,
            'tau_s':np.array([1/Ln,1/L]),'Ttotal_expected':(S0+S1)/L}


class Operator:
    def __init__(self):
        self.dy=np.zeros(19); self.rates={}; self.events=[]
        self.power=dict.fromkeys(POWERS,0.)
        self.electron=0.; self.external_A=0.; self.external_Q=0.
        self.absorbed=0.; self.escaped=0.

    def event(self,name,rate,nu,electron=0,external_A=0,external_Q=0,energy=None):
        v=np.zeros(19,dtype=int)
        for i,number in nu: v[i]+=number
        self.dy+=v*rate; self.rates[name]=float(rate)
        self.electron+=electron*rate; self.external_A+=external_A*rate; self.external_Q+=external_Q*rate
        self.events.append({'name':name,'nu':v,'electron':electron,'external_A':external_A,'external_Q':external_Q,'energy':energy or {}})
        for k,value in (energy or {}).items(): self.power[k]+=rate*value

    def result(self):
        incoming=sum(self.power[k] for k in ('photon_input','cr_input','injected_kinetic'))
        outgoing=sum(v for k,v in self.power.items() if k not in ('photon_input','cr_input','injected_kinetic'))
        return {'dy':self.dy,'rates':self.rates,'power':self.power,'events':self.events,
                'electron_rate':self.electron,'external_baryon_rate':self.external_A,'external_charge_rate':self.external_Q,
                'baryon_residual':float(A@self.dy+self.external_A),'charge_residual':float(Q@self.dy-self.electron),
                'energy_residual':incoming-outgoing,'absorbed_photon_rate':self.absorbed,'escaped_particle_rate':self.escaped}


def evaluate_operator(y,nref,alpha,c,escape=True,intrinsic=True,res=None):
    if np.any(np.asarray(y)<0): raise ValueError('negative state')
    res=reservoirs(y,alpha,c) if res is None else res
    op=Operator()
    for family,(start,thresholds) in FAMILIES.items():
        for q,I in enumerate(thresholds):
            for b,(E,F) in enumerate(c['photon_bins_eV_flux_cm2_s']):
                rate=alpha*F*atomic_sigma(E,I,c)*y[start+q]
                op.event(f'photo_atom_{family}_{q}_b{b}',rate,[(start+q,-1),(start+q+1,1)],electron=1,
                         energy={'photon_input':E,'atomic_internal':I,'fast_electron':E-I})
                op.absorbed+=rate
    for name,fam,stable,fast,qvalue in NUCLEAR:
        start,thresholds=FAMILIES[fam]
        for q in range(len(thresholds)+1):
            strip=sum(thresholds[q:]); req=-qvalue+strip
            for b,(E,F) in enumerate(c['photon_bins_eV_flux_cm2_s']):
                rate=alpha*F*nuclear_sigma(E,req,c)*y[start+q]
                # No admitted energy allocation below threshold.
                K=E-req if rate else 0.
                op.event(f'photo_nuc_{name}_{q}_b{b}',rate,[(start+q,-1),*stable,(fast,1)],electron=len(thresholds)-q,
                         energy={'photon_input':E,'nuclear_internal':-qvalue,'atomic_internal':strip,'heat':K/2,'fast_kinetic_change':K/2} if rate else {})
                op.absorbed+=rate
    start,thresholds=FAMILIES['He4']
    for q in range(3):
        for j,(name,qvalue,products) in enumerate((('n',-20577600.,[(2,1),(9,1),(17,1)]),('T',-19813900.,[(2,2),(18,1)]))):
            E=c['cr_energy_eV']; rate=alpha*c['cr_flux_cm2_s']*cr_sigma(E,c)*y[start+q]
            strip=sum(thresholds[q:]); K=E+qvalue-strip
            if rate and K<0: raise ValueError('CR energy support violated')
            op.event(f'cr_{name}_{q}',rate,[(start+q,-1),*products],electron=3-q,external_A=-1,external_Q=-1,
                     energy={'cr_input':E,'nuclear_internal':-qvalue,'atomic_internal':strip,'heat':K/2,'fast_kinetic_change':K/2} if rate else {})
    for i,value in enumerate(c['thermal_injection_per_Href_s']):
        op.event('inject_'+LABELS[i],alpha*value,[(i,1)],electron=int(Q[i]),external_A=-int(A[i]),external_Q=-int(Q[i]))
    for j,kind in enumerate(('n','T')):
        op.event('inject_fast_'+kind,alpha*c['fast_injection_per_Href_s'][j],[(17+j,1)],electron=j,external_A=-int(A[17+j]),external_Q=-j,
                 energy={'injected_kinetic':c['fast_injection_kinetic_eV'],'fast_kinetic_change':c['fast_injection_kinetic_eV']})
        mean=res['P'][j]/res['S'][j] if res['S'][j]>0 else 0.
        slow=c['ks_'+kind+'_s']*res['B'][j]
        es=c['ke_'+kind+'_s']*res['B'][j]
        beta=c['lambda_'+kind+'_s']/c['gamma_'+kind]*res['B'][j]
        op.event('slow_'+kind,slow,[(17+j,-1),(0 if j==0 else 6,1)],energy={'fast_kinetic_change':-mean,'heat':mean})
        op.event('escape_fast_'+kind,es,[(17+j,-1)],electron=-j,external_A=int(A[17+j]),external_Q=j,
                 energy={'fast_kinetic_change':-mean,'escaped_kinetic':mean})
        op.escaped+=es
        qvalue=c['beta_Q_'+kind+'_eV']; f=c['beta_electron_fraction']
        op.event('beta_fast_'+kind,beta,[(17+j,-1),(2 if j==0 else 9,1)],electron=1,
                 energy={'fast_kinetic_change':-mean,'heat':mean,'nuclear_internal':-qvalue,'fast_electron':f*qvalue,'neutrino':(1-f)*qvalue})
    if intrinsic:
        for i,target,kind in ((0,2,'n'),(5,8,'T'),(6,9,'T')):
            qvalue=c['beta_Q_'+kind+'_eV']; f=c['beta_electron_fraction']
            op.event('beta_'+LABELS[i],c['lambda_'+kind+'_s']*y[i],[(i,-1),(target,1)],electron=1,
                     energy={'nuclear_internal':-qvalue,'fast_electron':f*qvalue,'neutrino':(1-f)*qvalue})
        for h,d in ((1,3),(2,4)):
            op.event('capture_'+LABELS[h],nref*y[0]*y[h]*c['capture_C_cm3_s'],[(0,-1),(h,-1),(d,1)],
                     energy={'nuclear_internal':-c['capture_Q_eV'],'escaping_radiation':c['capture_Q_eV']})
        op.event('recombine_T',c['T_recombination_s']*y[6],[(6,-1),(5,1)],electron=-1,
                 energy={'atomic_internal':-13.6,'escaping_radiation':13.6})
    for i,label in enumerate(LABELS):
        rate=(c['kesc_s'] if escape else 0)*y[i]
        op.event('escape_'+label,rate,[(i,-1)],electron=-int(Q[i]),external_A=int(A[i]),external_Q=int(Q[i]))
        op.escaped+=rate
    return op.result()
