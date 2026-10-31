#!/usr/bin/env python3
"""Ground-HeII Curtin CCC nf<=10 first inelastic competition on frozen BASS193.

SOURCE-CONDITIONAL THEORETICAL EXPERIMENT, not a full secondary electron cascade,
self-consistent cosmological IVP, heat or photon emissivity. Never combines
summed n.1 with the same state's individually resolved nL.1S.
"""
import sys, os, pathlib, zipfile, hashlib, io, json, math, argparse
import numpy as np
import pandas as pd

ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENT_ARCHIVE=pathlib.Path(os.getenv('REI_F4_PARENT_ARCHIVE',str(ROOT/'private_sources/REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip' if (ROOT/'private_sources/REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip').exists() else '/mnt/data/REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip')))
PARENT_ROOT=pathlib.Path(os.getenv('REI_F4_PARENT_DIR',str(ROOT/'private_sources/REI_F4_CCC6_FIRST_EVENT_20261031' if (ROOT/'private_sources/REI_F4_CCC6_FIRST_EVENT_20261031').exists() else '/mnt/data/rei_f4_work/REI_F4_CCC6_FIRST_EVENT_20261031')))
CURTIN_ZIP=pathlib.Path(os.getenv('REI_F4_CURTIN_ZIP',str(ROOT/'private_sources/e-HeII_XSEC_LS.zip' if (ROOT/'private_sources/e-HeII_XSEC_LS.zip').exists() else '/mnt/data/e-HeII_XSEC_LS.zip')))
EXACT_CURTIN_UPLOAD_SHA='e32f7d22a3dc54e7981e93369bb98ddd38109a784cff608e59e9657b3a3558db'
PARENT_ORIGINAL_SHA='4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4'
PARENT_HEAD='5a70156ec6424d9d9f1adeeb1391fd66939a1318'
I_CCC=54.4232  # eV, target-ionization reference of provided Curtin numerical tables
SHELL_IDS=list('23456789:')
HEII_NAMES=[f'HeII_n{n}' for n in range(2,11)]+['HeII_ion']
A0_CM=5.29177210903e-9
A0_SQ_CM=A0_CM**2


def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def table(z,name):
    """Return incident electron energy eV and sigma a0^2. Select table by nf.ni filename."""
    lines=z.read(name).decode('utf-8').splitlines()
    data=[]
    for line in lines:
        if line.startswith('#') or not line.strip(): continue
        cells=line.split()
        if len(cells)<2:continue
        data.append((float(cells[0]),float(cells[1])))
    a=np.asarray(data,float)
    # All BASS193 primary E <= 60.923 eV; limit parser to 100 eV,
    # avoiding a duplicated/inconsistent 10290-eV terminal row in ':.1'.
    # This is scope cropping, NOT an unreported modification of raw source.
    a=a[a[:,0]<=100.]
    assert len(a)>=20 and np.all(np.diff(a[:,0])>0),name
    assert np.isfinite(a).all() and a[:,1].min()>=0,name
    return a

def load_heii(zippath=CURTIN_ZIP):
    assert sha(zippath)==EXACT_CURTIN_UPLOAD_SHA
    with zipfile.ZipFile(zippath) as z:
        assert z.testzip() is None
        desc=z.read('README').decode('utf-8')
        assert 'nf,lf' in desc and 'ni,li' in desc and '4F.2P' in desc
        arr=[table(z,s+'.1') for s in SHELL_IDS]+[table(z,'TICS.1')]
        # Cross-check direction and the aggregated n=2 file against resolved 
        # excitation channels. This would fail badly with 1S.2P (de-excitation).
        a=table(z,'2S.1S');b=table(z,'2P.1S')
        assert np.array_equal(a[:,0],b[:,0]) and np.array_equal(a[:,0],arr[0][:,0])
        assert np.max(abs(a[:,1]+b[:,1]-arr[0][:,1]))<0.00009
        assert abs(table(z,'TICS.1S')[1,1]-arr[-1][1,1])<1.e-12
    return arr

def calc_thresholds():
    return np.array([I_CCC*(1-1/n**2) for n in range(2,11)]+[I_CCC],float)

def make_grid(m,ccc,grid):
    gridparent=m.energy_nodes(m.load_source_data if hasattr(m,'load_source_data') else DATA,grid)
    pts=[gridparent,m.LOW,m.E_PAIR,calc_thresholds()]
    for a in ccc:pts.append(a[(a[:,0]>m.LOW)&(a[:,0]<m.E_PAIR),0])
    E=np.unique(np.round(np.concatenate([np.atleast_1d(x) for x in pts]),11))
    assert abs(E[0]-m.LOW)<1e-10 and abs(E[-1]-m.E_PAIR)<1.e-9
    return E

def read_parent():
    if sha(PARENT_ARCHIVE)!=PARENT_ORIGINAL_SHA:raise RuntimeError('parent master provenance mismatch')
    sys.path.insert(0,str(PARENT_ROOT/'code'))
    import run as m
    arr,chem,th,pl,coul,data,owner,meta=m.input_load()
    assert len(arr)==len(chem)==len(th)==192 and len(coul)==193
    bands=pd.read_csv(PARENT_ROOT/'results'/'BASS_CCC6_FIRST_EVENT_SOURCE_BANDS_3840.csv')
    original=pd.read_csv(PARENT_ROOT/'results'/'BASS_CCC6_FIRST_EVENT_ARRIVAL_192.csv')
    assert bands.shape[0]==3840 and original.shape[0]==192
    return m,arr,chem,th,pl,coul,data,owner,meta,bands,original

def species_densities(coul,chem,th):
    """193 rows: nHI,nHeI,nHeII,n_e in cm^-3, full original 21-charge bath."""
    dens=np.zeros((193,4),float)
    for epoch in range(193):
        j=epoch-1
        ne=float(coul.n_e_m3.iloc[epoch])*1e-6
        if epoch:
            r=chem.iloc[j]
            nH=float(coul.n_b_m3.iloc[epoch])*1e-6*float(th.nHref_over_nb.iloc[j]);nHe=nH*float(r.helium_per_H_ref)
            h=nH*(1-float(r.xHII_end)); hei=nHe*float(r.xHeI_end); heii=nHe*float(r.xHeII_end)
            heiii=nHe*float(r.xHeIII_end)
        else:
            r=chem.iloc[0]
            nH=float(coul.n_b_m3.iloc[0])*1e-6*float(th.nHref_over_nb.iloc[0]);nHe=nH*float(r.helium_per_H_ref)
            h=nH*(1-float(r.xHII_start)); heii=nHe*float(r.xHeII_start);heiii=nHe*float(r.xHeIII_start);hei=nHe-heii-heiii
        assert min(ne,h,hei,heii,heiii)>-1e-20
        assert abs(hei+heii+heiii-nHe)<2e-12*nHe
        dens[epoch]=[h,hei,heii,ne]
    return dens

def heii_sigma(E,arrays):
    th=calc_thresholds()
    out=[]
    for k,tab in enumerate(arrays):
        # At the first sample, source original may be finite (charged-ion threshold).
        # Do not invent a sub-first-knot cross section; zero-extend conservatively.
        val=np.interp(E,tab[:,0],tab[:,1],left=0,right=np.nan)
        assert np.isfinite(val).all()
        val=np.where(E<th[k],0.,val)
        out.append(val*A0_SQ_CM)
    return np.asarray(out)

def compute_all(grid=2100,save=True):
    global DATA
    m,arr,chem,th,pl,coul,DATA,owner,meta,bands,original=read_parent()
    array=load_heii()
    E=make_grid(m,array,grid)
    sig_old=m.sigma_samples(DATA,owner,E)
    sig_heii=heii_sigma(E,array)
    sig=np.concatenate([sig_old,sig_heii],axis=0)
    channel_names=m.CHANNELS+HEII_NAMES
    assert sig.shape[0]==16 and (sig>=0).all()
    den=species_densities(coul,chem,th)
    target=np.hstack([den[:,0,None]*np.ones((193,3)),den[:,1,None]*np.ones((193,3)),den[:,2,None]*np.ones((193,10))])
    ne=den[:,3]
    ln=np.log(4*E[None,:]/(7.40e-11*ne[:,None]))
    assert ln.min()>1
    speed=np.sqrt(2*E*m.EV_ERG/m.ELECTRON_MASS_G)
    b=4*np.pi*m.E_SQUARED_CGS**2*ne[:,None]*ln/(m.ELECTRON_MASS_G*speed[None,:]*m.EV_ERG)
    hz=(target[:,:,None]*sig[None,:,:]*speed[None,None,:])/b[:,None,:]
    assert np.isfinite(hz).all() and hz.min()>=0
    delta=0.5*(hz[:,:,:-1]+hz[:,:,1:])*np.diff(E)[None,None,:]
    epochs,chan,n=193,16,len(E)
    P=np.zeros((epochs,chan+1,n),float)
    P[:,chan,0]=1
    G=np.zeros((epochs,n),float) # first-event kinetic-energy moment, summed across channels
    Ghe=np.zeros((epochs,n),float)
    for j in range(n-1):
        dchan=delta[:,:,j]
        d=dchan.sum(axis=1)
        decay=np.exp(-np.minimum(d,745))
        weight=-np.expm1(-np.minimum(d,745))
        q=np.divide(weight,d,out=np.ones_like(d),where=d>1e-10)
        # q=1-d/2+... for extremely small d, not a constant 1 for larger d
        small=(d<=1e-10);q[small]=1-d[small]/2+d[small]**2/6
        P[:,:chan,j+1]=P[:,:chan,j]*decay[:,None]+dchan*q[:,None]
        P[:,chan,j+1]=P[:,chan,j]*decay
        # Collision moment: finite-cell mean energy for exponentially-distributed first event.
        f=np.empty_like(d)
        small=d<0.005;large=d>45;med=~(small|large)
        f[small]=0.5-d[small]/12+d[small]**3/720-d[small]**5/30240
        f[large]=1/d[large]
        f[med]=1/d[med]-1/np.expm1(d[med])
        ebar=E[j+1]-(E[j+1]-E[j])*f
        G[:,j+1]=G[:,j]*decay + weight*ebar
        GHeAdd=np.sum(dchan[:,6:],axis=1)*q*ebar
        Ghe[:,j+1]=Ghe[:,j]*decay+GHeAdd
    # physics invariants
    assert np.max(np.abs(P.sum(axis=1)-1))<2e-12
    assert P.min()>-1e-14
    assert (np.diff(P[:,:16,:].sum(axis=1),axis=1)>-1e-12).all()
    chi=np.r_[np.array([m.THRESH[k] for k in m.CHANNELS]),calc_thresholds()]
    chi[m.CHANNELS.index('HI_ion')]=13.598434599702 # energy ledger corrected only
    Q=np.einsum('c,jck->jk',chi,P[:,:16,:])
    K=G-Q
    C=E[None,:]-G-m.LOW*P[:,16,:]
    assert K.min()>-1e-9 and C.min()>-1e-9
    for name,q in [('K',K),('C',C)]: assert np.isfinite(q).all()
    closure=np.max(np.abs(Q+K+C+m.LOW*P[:,16,:]-E[None,:]))
    assert closure<4e-13
    # Full source expectation at mean collocation and exact first moment enclosures for selected output functions.
    dfb=bands.copy()
    outrows=[];rows=[];mono=[]
    th_he=calc_thresholds()
    kernels={
        'HeII_any':P[:,6:16,:].sum(axis=1),
        'HeII_n2':P[:,6,:],
        'HeII_n3to10':P[:,7:15,:].sum(axis=1),
        'HeII_ion':P[:,15,:],
        'all_any':1-P[:,16,:],
        'HeII_binding_eV':np.einsum('c,jck->jk',th_he,P[:,6:16,:]),
        'HeII_first_event_energy_eV':Ghe,
    }
    # Prior 6-channel source mean from original source for comparison.
    total_prior=0.
    for epoch in range(193):
        for en in (13.7,30.0,41.,45.,50.,55.,60.,m.E_PAIR):
            vector=np.interp(en,E,kernels['HeII_any'][epoch]);po=np.interp(en,E,kernels['all_any'][epoch])
            mono.append(dict(epoch=epoch,z=float(coul.z.iloc[epoch]),E_eV=en,nHeII_cm3=den[epoch,2],ne_all_BASS_cm3=den[epoch,3],P_HeII_any=float(vector),P_all_16=float(po),P_HeII_n2=float(np.interp(en,E,kernels['HeII_n2'][epoch])),P_HeII_ion=float(np.interp(en,E,kernels['HeII_ion'][epoch])),P_survival=float(np.interp(en,E,P[epoch,16])),HeII_binding_eV=float(np.interp(en,E,kernels['HeII_binding_eV'][epoch])),C_pre_eV=float(np.interp(en,E,C[epoch])),K_post_eV=float(np.interp(en,E,K[epoch]))))
    result_names=list(kernels.keys())
    for j in range(192):
        epoch=j+1
        prior_subset=dfb[dfb.arrival_interval==j]
        assert len(prior_subset)==20
        totals={key:np.zeros(3,float) for key in result_names}
        channel_totals=np.zeros(16)
        Ntotal=Mtotal=0.
        for _,r in prior_subset.iterrows():
            N=float(r.source_electron_count_per_b);M=float(r.source_kinetic_eV_per_b)
            lo=float(r.source_support_min_eV);hi=float(r.source_support_max_eV);mu=float(r.source_mean_e_eV) if N>0 else lo
            Ntotal+=N;Mtotal+=M
            outr=dict(arrival_interval=j,z_low=float(r.z_low),first_absorber=r.first_absorber,energy_band=r.energy_band,source_N_per_b=N,source_M_eV_per_b=M,nHeII_cm3=float(den[epoch,2]))
            for key in result_names:
                vals=np.zeros(3)
                if N>0:
                    # Only the original first photoelectron source and the computed kernel, never fabricated spectral shape.
                    if hi<=m.LOW:vals=np.zeros(3)
                    elif key.startswith('HeII_') and hi<40.8174:vals=np.zeros(3)
                    else:
                        knots=np.unique(np.r_[lo,E[(E>lo)&(E<hi)],hi])
                        if lo<m.LOW<hi: knots=np.unique(np.r_[knots,m.LOW])
                        v=np.interp(np.maximum(knots,m.LOW),E,kernels[key][epoch])
                        v=np.where(knots<m.LOW,0,v)
                        vals=m.moment_bounds(knots,v,lo,hi,mu)
                totals[key]+=N*vals
                for k,label in enumerate(('low','mean','high')):outr[key+'_'+label+'_per_b']=float(N*vals[k])
            if N>0:
                for c in range(16):channel_totals[c]+=N*float(np.interp(max(mu,m.LOW),E,P[epoch,c])) if mu>=m.LOW else 0.
            outrows.append(outr)
        assert abs(Ntotal-float(original.photoelectron_N_per_b.iloc[j]))<2e-23
        assert abs(Mtotal-float(original.photoelectron_E_eV_per_b.iloc[j]))<3e-22
        total_prior+=float(original.six_any_mean.iloc[j])
        row=dict(arrival_interval=j,z_low=float(original.z_low.iloc[j]),z_high=float(original.z_high.iloc[j]),nHeII_cm3=float(den[epoch,2]),ne_all_BASS_cm3=float(den[epoch,3]),source_N_per_b=Ntotal,source_M_eV_per_b=Mtotal,prior_CCC6_first_mean_per_b=float(original.six_any_mean.iloc[j]))
        for key in result_names:
            for t,label in enumerate(('low','mean','high')):row[key+'_'+label+'_per_b']=float(totals[key][t])
        row['new_CCC6_first_mean_per_b']=float(channel_totals[:6].sum())
        row['HeII_any_channel_mean_per_b']=float(channel_totals[6:16].sum())
        row['HeII_ion_charge_mean_per_b']=float(channel_totals[15])
        row['HeII_excitation_mean_per_b']=float(channel_totals[6:15].sum())
        row['mean_prob_normalization_residual_per_b']=float(totals['all_any'][1]-channel_totals.sum())
        rows.append(row)
    result=pd.DataFrame(rows);src=pd.DataFrame(outrows);mono=pd.DataFrame(mono)
    totals={key:{t:float(result[key+'_'+t+'_per_b'].sum()) for t in ('low','mean','high')} for key in result_names}
    initial_N=float(result.source_N_per_b.sum());initial_E=float(result.source_M_eV_per_b.sum())
    answer=dict(schema='REI_F4_CURTIN_HEII_GROUND_16_CHANNEL_FIRST_EVENT_SOURCE_CONDITIONAL',source_uploaded_sha256=EXACT_CURTIN_UPLOAD_SHA,source_archive_bytes=CURTIN_ZIP.stat().st_size,source_archive_members=3122,owner_claim='Curtin CCC 2026 HeII format; exact byte match to remote official unverified',source_parent_sha256=PARENT_ORIGINAL_SHA,source_parent_PR315_head=PARENT_HEAD,parent_reused_CCC6='EXHALE pinned six channels, unchanged',HeII_channels=HEII_NAMES,HeII_thresholds_eV={k:float(v) for k,v in zip(HEII_NAMES,calc_thresholds())},original_193_epochs=193,source_192_arrivals=192,source_3840_bands=3840,energy_grid_nodes=int(len(E)),first_photoelectrons_per_b=initial_N,first_photoelectron_energy_eV_per_b=initial_E,prior_six_first_mean_per_b=total_prior,source_first_event_bounds=totals,new_six_first_mean_per_b=float(result.new_CCC6_first_mean_per_b.sum()),HeII_source_first_charges_per_b=float(result.HeII_ion_charge_mean_per_b.sum()),probability_normalization_max=float(np.max(abs(P.sum(axis=1)-1))),max_mono_energy_closure_eV=float(closure),fixed_background=True,source_conditional=True,full_secondary_cascade=False,production='HOLD',working_dag='33/88',central_dag='28/88',fast_dag='4/7',canonical_delta=0)
    if save:
        path=ROOT/'results';path.mkdir(exist_ok=True)
        src.to_csv(path/'HeII_16CHANNEL_SOURCE_BANDS_3840.csv',index=False,float_format='%.17g')
        result.to_csv(path/'HeII_16CHANNEL_ARRIVAL_192.csv',index=False,float_format='%.17g')
        mono.to_csv(path/'HeII_16CHANNEL_MONO_1544.csv',index=False,float_format='%.17g')
        (path/'RESULTS.json').write_text(json.dumps(answer,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    return answer

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--grid',type=int,default=2100);parser.add_argument('--no-save',action='store_true')
    a=parser.parse_args()
    d=compute_all(grid=a.grid,save=not a.no_save)
    print(json.dumps(d,indent=2,ensure_ascii=False))
