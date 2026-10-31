#!/usr/bin/env python3
"""Original PR311 CCC six-channel FIRST EVENT competition against original PR309 FS Coulomb.

Source is a fixed BASS193 background, conditional Li II 2E1 photoelectrons.
No cosmological IVP, no actual secondary cascade, no full REI17 F/J.
Source-moment exact bounds apply to a specified piecewise-linear-in-E first-event kernel.
"""
import os,sys,io,hashlib,zipfile,json,math,importlib.util,datetime
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'source'; OUTPUT=ROOT/'results';OUTPUT.mkdir(parents=True,exist_ok=True)
PR311='4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52'
COULOMB_CSV='66c60518c1fe60482aa31472f0437104f52176b6b7fef3a807318dabf3efb463'
E_PAIR=60.922559447552
LOW=13.7
ELECTRON_MASS_G=9.1093837139e-28
EV_ERG=1.602176634e-12
E_SQUARED_CGS=7.2973525693e-3*1.054571817e-27*2.99792458e10
CHANNELS=['HI_ion','HI_2p','HI_2s','HeI_ion','HeI_2p','HeI_t2s']
THRESH={'HI_ion':13.6058,'HI_2p':10.20435,'HI_2s':10.20435,'HeI_ion':24.587389011,'HeI_2p':21.1156,'HeI_t2s':19.7179}
FIRST_ABSORBERS=['H_I','He_I','He_II','Li_I']
BANDS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
EDGES=[0,10.2,13.598434599702,24.587389011,54.41776,E_PAIR]
CHI={'H_I':13.598434599702,'He_I':24.587389011,'He_II':54.41776,'Li_I':5.390}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def input_load():
    assert digest(INPUT/'PR311_CCC6_SOURCE_FULL.zip')==PR311
    assert digest(INPUT/'BASS193_COULOMB_PLASMA_193.csv')==COULOMB_CSV
    path=INPUT/'PR311_CCC6_SOURCE_FULL.zip'
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name in ['inputs/PR302_ARRIVAL_192.csv','inputs/PR303_SPECIES_192.csv','inputs/PR302_THERMAL_192.csv','inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv','inputs/ccc_adaptive_b64.json']:
            assert name in z.namelist()
        docs={k:pd.read_csv(io.BytesIO(z.read(k))) for k in ['inputs/PR302_ARRIVAL_192.csv','inputs/PR303_SPECIES_192.csv','inputs/PR302_THERMAL_192.csv','inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv']}
        raw=z.read('inputs/ccc_adaptive_b64.json'); meta=json.loads(raw)
    # Import exact original PR311 decoder / threshold semantics from read-only extracted owner.
    src=ROOT/'source311'/'code'/'compute.py'
    with zipfile.ZipFile(path) as z: source_code=z.read('code/compute.py')
    if src.exists():
        assert src.read_bytes()==source_code, 'cached CCC source-owner implementation differs'
        assert (ROOT/'source311'/'inputs'/'ccc_adaptive_b64.json').read_bytes()==raw
    else:
        (ROOT/'source311'/'code').mkdir(parents=True,exist_ok=True)
        src.write_bytes(source_code)
        (ROOT/'source311'/'inputs').mkdir(exist_ok=True)
        (ROOT/'source311'/'inputs'/'ccc_adaptive_b64.json').write_bytes(raw)
    spec=importlib.util.spec_from_file_location('original_pr311_ccc',src)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    data,owner=m.load_ccc()
    assert meta['mirror_commit']=='7388232fac2c3cdadad613515006de008360f1ab'
    assert set(data)==set(CHANNELS)
    arr=docs['inputs/PR302_ARRIVAL_192.csv'];comp=docs['inputs/PR303_SPECIES_192.csv'];thermal=docs['inputs/PR302_THERMAL_192.csv'];pl=docs['inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv']
    coul=pd.read_csv(INPUT/'BASS193_COULOMB_PLASMA_193.csv')
    assert len(arr)==len(comp)==len(thermal)==192 and len(pl)==len(coul)==193
    np.testing.assert_allclose(pl.nb_m3.values*pl.xe_saved.values,coul.n_e_m3.values,rtol=1e-12,atol=0)
    np.testing.assert_allclose(pl.z.values,coul.z.values,rtol=0,atol=1e-12)
    np.testing.assert_allclose(arr.z_low.values,comp.z_end.values,rtol=0,atol=1e-12)
    return arr,comp,thermal,pl,coul,data,m,owner

def sigma_samples(data, original, E):
    """Same piecewise linear sigma and threshold patch as original PR311, vectorized."""
    E=np.asarray(E,float)
    sigma=[]
    for name in CHANNELS:
        d=data[name]; val=np.interp(E,d[:,0],d[:,1]);theta=THRESH[name]
        val=np.where(E<=theta,0,val)
        if name=='HeI_ion':
            s246=float(np.interp(24.6,d[:,0],d[:,1]));v=s246*np.maximum(E-theta,0)/(24.6-theta)
            val=np.where((E>theta)&(E<24.6),v,val)
        sigma.append(val)
        for q in [13.7,17.0,20.,24.58,26.,45.,55.,60.]:
            if q>=LOW and q<=E[-1]:
                i=np.searchsorted(E,q)
                if i<len(E) and abs(E[i]-q)<1e-11:
                    assert abs(val[i]-original.sigma_interp(d,q,name))<3e-29
    result=np.asarray(sigma)
    assert np.isfinite(result).all() and result.min()>=0
    return result

def energy_nodes(data,n=2100):
    pts=[LOW,E_PAIR,*[t for t in THRESH.values() if LOW<t<E_PAIR]]
    for d in data.values():pts.extend(float(t) for t in d[:,0] if LOW<t<E_PAIR)
    pts.extend(np.linspace(LOW,E_PAIR,n))
    pts=np.unique(np.round(np.asarray(pts),13));assert pts[0]==LOW
    return pts

def first_probs(E, sigmas, ne_cm3, h_cm3, he_cm3):
    """True full original BASS21 charge bath ne, *partial* CCC6 inelastic first events.
    At each energy node: P_a(E_high) = e^-delta P_a(E_low) + w_a(1-e^-delta).
    Competing hazards are integrated along Coulomb-only mean energy loss down to 13.7eV.
    """
    assert ne_cm3>0 and h_cm3>=0 and he_cm3>=0
    lnL=np.log(4*E/(7.40e-11*ne_cm3))
    if lnL.min()<=1:raise ValueError('Coulomb log invalid')
    v=np.sqrt(2*E*EV_ERG/ELECTRON_MASS_G)
    b_erg=4*np.pi*E_SQUARED_CGS**2*ne_cm3*lnL/(ELECTRON_MASS_G*v)
    b_eV_s=b_erg/EV_ERG
    density=np.array([h_cm3]*3+[he_cm3]*3)
    nu=density[:,None]*sigmas*v[None,:]
    h=nu/b_eV_s[None,:]
    dh=0.5*(h[:,:-1]+h[:,1:])*np.diff(E)[None,:]
    dtot=dh.sum(axis=0)
    out=np.zeros((7,len(E)),float)
    out[6,0]=1. # survival without any of the 6 inelastic processes
    for i,d in enumerate(dtot):
        decay=math.exp(-float(d)) if d<745 else 0.
        collision=-math.expm1(-float(d))
        out[:6,i+1]=out[:6,i]*decay + (dh[:,i]/d if d>0 else 0.)*collision
        out[6,i+1]=out[6,i]*decay
    return out,nu,h

def hull(knots, values, upper):
    xs=[];ys=[]
    for x,y in zip(knots,values):
        x=float(x);y=float(y)
        while len(xs)>=2:
            s0=(ys[-1]-ys[-2])/(xs[-1]-xs[-2]);s1=(y-ys[-1])/(x-xs[-1])
            if (s0<=s1 if upper else s0>=s1):xs.pop();ys.pop()
            else:break
        xs.append(x);ys.append(y)
    return np.asarray(xs),np.asarray(ys)

def moment_bounds(E,pvalues,low,high,mu):
    low=float(low);high=float(high);mu=float(mu)
    if high<=low:
        z=np.array([float(np.interp(low,E,pvalues))]*3)
        return z
    knots=np.unique(np.r_[low,E[(E>low)&(E<high)],high])
    vals=np.interp(knots,E,pvalues)
    LX,LY=hull(knots,vals,False);UX,UY=hull(knots,vals,True)
    return np.array([np.interp(mu,LX,LY),np.interp(mu,knots,vals),np.interp(mu,UX,UY)])

def run(n=2100):
    arr,chem,th,pl,coul,data,owner,meta=input_load()
    E=energy_nodes(data,n)
    sigmas=sigma_samples(data,owner,E)
    jindices=[0,20,40,60,80,96,112,128,160,191]
    photo_columns=[];summary=[];grids=[];mono=[]
    bands=0
    # Calculate full fixed-background 193 states (including the first zero-source epoch).
    for epoch in range(193):
        j=epoch-1
        if j>=0:
            h=float((coul.n_b_m3.iloc[epoch]*1e-6)*th.nHref_over_nb.iloc[j]*(1-chem.xHII_end.iloc[j]))
            he=float((coul.n_b_m3.iloc[epoch]*1e-6)*th.nHref_over_nb.iloc[j]*chem.helium_per_H_ref.iloc[j]*chem.xHeI_end.iloc[j])
        else:
            nref=float(coul.n_b_m3.iloc[0]*1e-6*th.nHref_over_nb.iloc[0]);h=nref*(1-chem.xHII_start.iloc[0]);he=nref*float(chem.helium_per_H_ref.iloc[0])*float(chem.xHeI_end.iloc[0])
        ne=float(coul.n_e_m3.iloc[epoch])*1e-6
        p,nu,hes=first_probs(E,sigmas,ne,h,he)
        assert np.max(np.abs(p.sum(axis=0)-1))<1.6e-13
        assert np.all(p>=-1e-15) and np.all(p<=1+1e-13)
        for en in [13.7,18,22,30,45,55,E_PAIR]:
            r=np.array([np.interp(en,E,q) for q in p]);mono.append(dict(epoch=epoch,z=float(coul.z.iloc[epoch]),initial_E_eV=en,
                          ne_all_BASS_cm3=ne,nHI_cm3=h,nHeI_cm3=he,**{name+'_P':r[k] for k,name in enumerate(CHANNELS)},P_no_six_channel=r[6],P_any_six_channel=1-r[6]))
        if epoch in jindices:
            for m in range(0,len(E),max(1,len(E)//64)):
                idx=m;grids.append(dict(epoch=epoch,z=float(coul.z.iloc[epoch]),E_eV=float(E[idx]),total_p=float(p[:6,idx].sum()),P_no=float(p[6,idx]),**{name+'_P':float(p[k,idx]) for k,name in enumerate(CHANNELS)},**{name+'_nu_s':float(nu[k,idx]) for k,name in enumerate(CHANNELS)}))
        if j<0:continue
        sumN=0.;sumM=0.; agg=np.zeros((8,3),float) # 6 P + any P + threshold energy floor
        for s in FIRST_ABSORBERS:
            for k,b in enumerate(BANDS):
                N=float(arr.iloc[j][s+'_'+b+'_counts_per_b']);M=float(arr.iloc[j][s+'_'+b+'_primary_e_eV_per_b']);
                assert N>=-1e-30 and M>=-1e-23
                N=max(0.,N);M=max(0.,M);sumN+=N;sumM+=M
                left=EDGES[k];right=max(left,min(EDGES[k+1],E_PAIR-CHI[s]));
                if N>0:
                    mu=M/N
                    assert left-.011<=mu<=right+.011,(j,s,b,mu,left,right)
                    mu=max(left,min(right,mu));
                else:mu=0
                bnds=[]
                for idx in range(8):
                    if N==0: val=np.zeros(3)
                    else:
                        if idx<6: field=p[idx]
                        elif idx==6:field=p[:6].sum(axis=0)
                        else:field=np.dot([THRESH[c] for c in CHANNELS],p[:6])
                        if right<=LOW:
                            val=np.zeros(3)
                        elif left<LOW:
                            # Preserve subthreshold source mean; below 13.7 eV this scoped first-event model has zero response.
                            ext_E=np.unique(np.r_[left,LOW,E[(E>LOW)&(E<right)],right])
                            ext_P=np.where(ext_E<=LOW,0,np.interp(ext_E,E,field))
                            val=moment_bounds(ext_E,ext_P,left,right,mu)
                        else:
                            val=moment_bounds(E,field,left,right,mu)
                    bnds.append(val)
                bnds=np.asarray(bnds)
                assert (bnds[:,0]<=bnds[:,1]+1e-10).all() and (bnds[:,1]<=bnds[:,2]+1e-10).all()
                agg+=N*bnds
                bands+=1
                row=dict(arrival_interval=j,z_low=float(arr.z_low.iloc[j]),first_absorber=s,energy_band=b,source_electron_count_per_b=N,source_kinetic_eV_per_b=M,source_mean_e_eV=mu,source_support_min_eV=left,source_support_max_eV=right)
                for idx,name in enumerate(CHANNELS+['six_any','first_event_threshold_floor_eV']):
                    row.update({name+'_'+q:float(N*bnds[idx,t]) for t,q in enumerate(['lower','mean','upper'])})
                photo_columns.append(row)
        assert abs(sumN-float(arr.total_absorbed_ionizations_per_b.iloc[j]))<1.5e-23,(j,sumN)
        assert abs(sumM-float(arr.total_primary_e_eV_per_b.iloc[j]))<1.5e-22,(j,sumM)
        sm=dict(arrival_interval=j,z_high=float(arr.z_high.iloc[j]),z_low=float(arr.z_low.iloc[j]),proper_interval_s=float(th.proper_interval_s.iloc[j]),
                ne_full_BASS_cm3=ne,nHI_cm3=h,nHeI_cm3=he,photoelectron_N_per_b=sumN,photoelectron_E_eV_per_b=sumM)
        for idx,name in enumerate(CHANNELS+['six_any','first_event_threshold_floor_eV']):
            sm.update({name+'_'+q:float(agg[idx,t]) for t,q in enumerate(['lower','mean','upper'])})
        summary.append(sm)
    s=pd.DataFrame(summary);b=pd.DataFrame(photo_columns);mono=pd.DataFrame(mono);g=pd.DataFrame(grids)
    assert s.shape[0]==192 and b.shape[0]==3840 and mono.shape[0]==193*7
    for name,df in [('BASS193_CCC6_MONO_1351.csv',mono),('BASS_CCC6_FIRST_EVENT_SOURCE_BANDS_3840.csv',b),('BASS_CCC6_FIRST_EVENT_ARRIVAL_192.csv',s),('CCC6_SELECTED_ENERGY_GRID.csv',g)]:
        df.to_csv(OUTPUT/name,index=False,float_format='%.17g')
    d=dict(schema='REI_F4_CCC6_COULOMB_FIRST_EVENT_SOURCE_CONDITIONAL_V1',original_BASS_epochs=193,source_arrival_bins=192,original_source_bands=3840,mono_energy_states=193*7,
       cc_source_owner_git='EXHALE 7388232fac2c3cdadad613515006de008360f1ab',ccc_six_blob_ids={k:v['blob'] for k,v in meta['data'].items()},
       original_parent_zip_sha=PR311,proper_clock_no_ivps=True,first_electron_count_per_b=float(s.photoelectron_N_per_b.sum()),first_electron_kinetic_eV_per_b=float(s.photoelectron_E_eV_per_b.sum()),
       probability_first_six_any_lower_per_b=float(s.six_any_lower.sum()),probability_first_six_any_mean_per_b=float(s.six_any_mean.sum()),probability_first_six_any_upper_per_b=float(s.six_any_upper.sum()),
       first_event_threshold_floor_lower_eV_per_b=float(s.first_event_threshold_floor_eV_lower.sum()),first_event_threshold_floor_mean_eV_per_b=float(s.first_event_threshold_floor_eV_mean.sum()),first_event_threshold_floor_upper_eV_per_b=float(s.first_event_threshold_floor_eV_upper.sum()),
       channel_probability_means_per_b={c:float(s[c+'_mean'].sum()) for c in CHANNELS},z20_mono_p_Emax=float(mono[(mono.epoch==0)&(abs(mono.initial_E_eV-E_PAIR)<1e-6)].P_any_six_channel.iloc[0]),
       z2_mono_p_Emax=float(mono[(mono.epoch==192)&(abs(mono.initial_E_eV-E_PAIR)<1e-6)].P_any_six_channel.iloc[0]),
       no_full_cascade=True,missing_HeII_and_other_CCC_channels=True,original_REI_F4_counts=dict(working='33/88',central='28/88',physical_fast='4/7',canonical_delta=0),
       status='SOURCE_CONDITIONAL_6_CHANNEL_COMPETING_FIRST_EVENT_ONLY')
    (OUTPUT/'RESULTS.json').write_text(json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    return d

if __name__=='__main__':
    d=run(int(sys.argv[1]) if len(sys.argv)>1 else 2100)
    print(json.dumps(d,indent=2,sort_keys=True))
