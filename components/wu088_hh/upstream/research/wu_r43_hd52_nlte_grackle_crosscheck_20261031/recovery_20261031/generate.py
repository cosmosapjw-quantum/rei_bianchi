#!/usr/bin/env python3
"""R43 recovery: source-authentic HD52 non-LTE signed photon energy / Grackle comparison.
The recovered output is a NEW reproducible artifact, not byte-identical to lost R43 archive.
No invented proton rates; only exact EMAA source temperature nodes.
"""
from __future__ import annotations
import sys, math, csv, json, hashlib
from pathlib import Path
import numpy as np
from scipy.constants import h,c,k as KB

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source_private'))
import emaa_primary as owner

RAW_HASH='b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'
PARSER_HASH='c982bdd3a1dcf61bbd734295a68b2162b536068f4f65eb9e18ff188dd774252b'
GRACKLE_SOURCE_SHA1='dfbab661e7c45981eed750baebff140849917152'
GRACKLE_COMMIT='01261db0cefc69d8d5558e76a671b0c1f6e48271'
GRID_H=(1.,1e3,1e4,1e6)
GRID_HP=(1e3,1e6)
GRID_Z=('OFF','0','30','100','300')
GRID_Z_JOINT=('OFF','30','300')
T_RAD0=2.7255
DATA=None

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_data():
    assert sha(ROOT/'source_private/HD.Rovibration.805a7aa5.radex')==RAW_HASH
    assert sha(ROOT/'source_private/emaa_primary.py')==PARSER_HASH
    data=owner.parse_radex(ROOT/'source_private/HD.Rovibration.805a7aa5.radex')
    assert len(data['levels'])==52 and len(data['radiative'])==368
    assert len(data['partners'][5]['rates'])==1326 and len(data['partners'][7]['rates'])==171
    assert sorted(set(data['partners'][5]['temps']) & set(data['partners'][7]['temps']))==[5.]
    return data

def grackle_low(T):
    """Original Grackle main rate_functions.c, HDlow_rate, erg cm^3 / s; valid 10-6000K."""
    tm=min(max(T,10.),6000.)
    x=math.log10(tm/1000.)
    logq=-23.175780+1.5035261*x+0.40871403*x**2+0.17849311*x**3-0.077291388*x**4+0.10031326*x**5
    return 10**logq

def grackle_lte(T):
    """Original Grackle HDlte_rate, associated code comments erg cm^3/s; not direct LTE per HD without units semantics."""
    tm=min(max(T,10.),3e4);l=math.log10(tm)
    logq=-55.5725+56.649*l-37.9102*l*l+12.698*l**3-2.02424*l**4+0.122393*l**5
    return 10**min(logq,0.)

def coll_matrix(d,partner,T,n,E=None):
    C=np.zeros((52,52));
    if n==0.:return C
    rates=d['partners'][partner]; temps=rates['temps'];T=float(T)
    if T not in temps:raise ValueError(f'No source-original collider {partner} at {T} K')
    it=temps.index(T);lv=d['levels']
    for (up,lo),arr in rates['rates'].items():
        gap=lv[up]['E']-lv[lo]['E']
        down=float(arr[it])*n
        up_rate=down*lv[up]['g']/lv[lo]['g']*math.exp(-owner.HCK*gap/T)
        C[lo-1,up-1]+=down
        C[up-1,lo-1]+=up_rate
    np.fill_diagonal(C,-C.sum(axis=0))
    return C

def radio_matrix(d,Trad):
    R=np.zeros((52,52)); lines=[];lv=d['levels']
    for q in d['radiative']:
        up,lo=q['up'],q['low'];gap=lv[up]['E']-lv[lo]['E'];Eph=owner.HCJ*gap
        if Trad>0:
            arg=Eph/(KB*Trad)
            occ=0. if arg>700 else 1./math.expm1(arg)
        else:occ=0.
        down=q['A']*(1+occ);upt=q['A']*(lv[up]['g']/lv[lo]['g'])*occ
        R[lo-1,up-1]+=down
        R[up-1,lo-1]+=upt
        lines.append((up-1,lo-1,Eph,down,upt,float(q['freq_GHz'])))
    np.fill_diagonal(R,-R.sum(axis=0))
    return R,lines

def equilibrium(d,Tg,nH,nHp,z,*,return_diagnostics=False):
    lv=d['levels'];E=np.array([lv[i]['E']*owner.HCJ for i in range(1,53)])
    C_H=coll_matrix(d,5,Tg,nH)
    C_P=coll_matrix(d,7,Tg,nHp) if nHp else np.zeros((52,52))
    Trad=0. if z=='OFF' else T_RAD0*(1+int(z)) if isinstance(z,str) else float(z)
    R,lines=radio_matrix(d,Trad)
    G=C_H+C_P+R
    # normalized row replacement (column generator), physical stationary solution
    scale=max(float(np.max(np.abs(G))),1e-50)
    A=G.copy()/scale; A[0,:]=1.
    y=np.zeros(52);y[0]=1.
    p=np.linalg.solve(A,y)
    if p.min()< -5e-13:raise ValueError(f'large negative population {p.min()}')
    p=np.maximum(p,0.);p/=p.sum()
    residual=float(np.max(np.abs(G@p))/scale)
    if residual>5e-12:raise AssertionError(f'stationary generator residual {residual}')
    arr=[];Lamb=0.;gross_energy=0.
    for u,l,Eph,down,upt,fGHz in lines:
        n_em=down*p[u];n_abs=upt*p[l]
        energy=Eph*(n_em-n_abs)
        Lamb+=energy
        gross_energy+=Eph*(n_em+n_abs)
        arr.append({'upper_id':u+1,'lower_id':l+1,'upper_v':lv[u+1]['v'],'upper_J':lv[u+1]['J'],
          'lower_v':lv[l+1]['v'],'lower_J':lv[l+1]['J'],'freq_GHz':f'{fGHz:.11e}',
          'photon_energy_J':f'{Eph:.17e}','down_emitted_s_inv_per_HD':f'{n_em:.17e}',
          'up_absorbed_s_inv_per_HD':f'{n_abs:.17e}',
          'net_radiative_energy_J_s_per_HD':f'{energy:.17e}'})
    heat_H=float(E@(C_H@p));heat_HP=float(E@(C_P@p));
    denom=max(abs(Lamb),abs(heat_H+heat_HP),gross_energy,1e-60)
    energy_rel=float(abs(Lamb-(heat_H+heat_HP))/denom)
    if energy_rel>4e-7:raise AssertionError(f'energy residual {energy_rel} at {Tg,nH,nHp,z}')
    out={'T_gas_K':Tg,'n_H_cm_minus3':nH,'n_Hplus_cm_minus3':nHp,'z_boundary':z,
         'T_rad_K':Trad,'net_photon_J_s_per_HD':f'{Lamb:.17e}',
         'collisional_H_heating_of_HD_J_s':f'{heat_H:.17e}',
         'collisional_Hplus_heating_of_HD_J_s':f'{heat_HP:.17e}',
         'stationarity_scaled_residual':f'{residual:.17e}',
         'energy_relative_residual':f'{energy_rel:.17e}',
         'status':'source_conditional_optically_thin_HD52_no_chemistry_no_transport',
         'sign':'cooling' if Lamb>0 else 'heating' if Lamb<0 else 'balance'}
    return out,p,arr

def save_csv(path,rows):
    assert rows
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def generate():
    d=load_data();lv=d['levels'];temps=d['partners'][5]['temps'];conditions=[]
    for T in temps:
        for nH in GRID_H:
            for z in GRID_Z:conditions.append((T,nH,0.,z))
    for nH in GRID_H:
        for nHp in GRID_HP:
            for z in GRID_Z_JOINT:conditions.append((5.,nH,nHp,z))
    assert len(conditions)==324
    cases=[];populations=[];photons=[];lowlte=[]
    for T,nH,nHp,z in conditions:
        case,p,ph=equilibrium(d,T,nH,nHp,z)
        cases.append(case)
        sc={x:case[x] for x in ('T_gas_K','n_H_cm_minus3','n_Hplus_cm_minus3','z_boundary')}
        for k,prob in enumerate(p):populations.append({**sc,'level_id':k+1,'v':lv[k+1]['v'],'J':lv[k+1]['J'],'E_cm_inv':f'{lv[k+1]["E"]:.11e}', 'p_HD_level':f'{prob:.17e}'})
        for row in ph:photons.append({**sc,**row})
    # Grackle comparison original H temperatures under H-only nH=1, radiation OFF. LTE coefficients shown as code reference.
    energy=np.array([lv[i]['E']*owner.HCJ for i in range(1,53)])
    g=np.array([lv[i]['g'] for i in range(1,53)])
    for T in temps:
        boltzmann=g*np.exp(-(energy-energy.min())/(KB*T));boltzmann/=boltzmann.sum()
        em_lte=sum((energy[z['up']-1]-energy[z['low']-1])*z['A']*boltzmann[z['up']-1] for z in d['radiative'])*1e7
        row=next(q for q in cases if float(q['T_gas_K'])==T and float(q['n_H_cm_minus3'])==1. and q['z_boundary']=='OFF' and float(q['n_Hplus_cm_minus3'])==0.)
        em=float(row['net_photon_J_s_per_HD'])*1e7 # J/s per HD -> erg/s per HD; nH=1
        gr=grackle_low(T)
        lowlte.append({'T_gas_K':T,'n_H_cm_minus3':1.,'EMAA_net_erg_s_per_HD':f'{em:.17e}',
           'EMAA_low_erg_cm3_s_per_HD_H':f'{em:.17e}',
           'Grackle_HDlow_erg_cm3_s':f'{gr:.17e}',
           'ratio_EMAA_over_Grackle_HDlow':f'{em/gr:.17e}',
           'EMAA_LTE_erg_s_per_HD':f'{em_lte:.17e}',
           'Grackle_HDlte_erg_s_per_HD':f'{grackle_lte(T):.17e}',
           'EMAA_LTE_over_Grackle_HDlte':f'{em_lte/grackle_lte(T):.17e}',
           'source':'Grackle_rate_functions.c_sha1_dfbab661e7c45981eed750baebff140849917152'})
    assert (len(cases),len(populations),len(photons),len(lowlte))==(324,16848,119232,15)
    OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
    save_csv(OUT/'R43_CASES_324.csv',cases)
    save_csv(OUT/'R43_POPULATIONS_16848.csv',populations)
    save_csv(OUT/'R43_SIGNED_PHOTONS_119232.csv',photons)
    save_csv(OUT/'R43_GRACKLE_REFERENCE_15.csv',lowlte)
    probes={}
    for t,n,z in [(70.,1e4,'OFF'),(70.,1e4,'30'),(100.,1e4,'30'),(200.,1e4,'30')]:
        rr=next(r for r in cases if r['T_gas_K']==t and r['n_H_cm_minus3']==n and r['z_boundary']==z and r['n_Hplus_cm_minus3']==0.)
        probes[f'T{int(t)}_nH{int(n)}_z{z}']=rr['net_photon_J_s_per_HD']
    summary={'project':'cosmosapjw-quantum/WU088_HH','unit':'R43_HD52_NLTE_EMAA_GRACKLE_RECOVERY',
        'original_parent_PR':182,'original_parent_HEAD':'30a9ce9199e199426995b7035de059ff8d21d8dc',
        'canonical_DAG':'34/49_UNCHANGED','auxiliary':'R43_RECONSTRUCTED_FROM_PRIMARY_SOURCE',
        'original_source_SHA256':RAW_HASH,'original_parser_SHA256':PARSER_HASH,'grackle_code_blob':GRACKLE_SOURCE_SHA1,
        'original_source_temperature_nodes':temps,'conditions':len(cases),
        'rows':{'cases':len(cases),'populations':len(populations),'photons':len(photons),'Grackle':len(lowlte)},
        'signs':{k:sum(r['sign']==k for r in cases) for k in ['cooling','heating','balance']},'probes':probes,
        'not_claimed':['not byte-identical to unrecovered R43 20261031 master','no high-state proton collider rates','not abundance-weighted cooling nor radiation transfer',
             'no chemical or reactive scattering source correction','not production; no DAG canonical admission','not outside source temperature grids'],
        'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','HH_R10':'OFF','L4':False,'production':'HOLD'}
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'rows':summary['rows'],'signs':summary['signs'],'probes':probes,'grackle_70_ratio':next(x['ratio_EMAA_over_Grackle_HDlow'] for x in lowlte if x['T_gas_K']==70.),'grackle_100_ratio':next(x['ratio_EMAA_over_Grackle_HDlow'] for x in lowlte if x['T_gas_K']==100.)},indent=2))
    return summary
if __name__=='__main__':generate()
