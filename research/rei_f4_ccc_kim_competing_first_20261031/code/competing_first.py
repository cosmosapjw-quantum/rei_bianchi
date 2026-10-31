#!/usr/bin/env python3
"""CCC6 and Kim92 competing first-inelastic-event vs continuous Coulomb cooling.

Frozen BASS193 states; no post-first-event cascade, no cosmology or chemistry IVP.
Usage: python code/competing_first.py
"""
from __future__ import annotations
from pathlib import Path
import sys, math, json, hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
from ccc_snapshot_311 import load_ccc, sigma_interp, SHA as INPUT_SHA
INPUT=ROOT/'inputs'; OUTPUT=ROOT/'results';OUTPUT.mkdir(exist_ok=True)
TARGETS=['HI_ion','HI_2p','HI_2s','HeI_ion','HeI_2p','HeI_t2s']
ME_G=9.1093837139e-28
EV_ERG=1.602176634e-12
E2=7.2973525693e-3*1.054571817e-27*2.99792458e10
E_LOW=13.7
E_TOP=60.922559447552
SPECIES=['H_I','He_I','He_II','Li_I']
BANDS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
EDGES=[0.,10.2,13.598434599702,24.587389011,54.41776,E_TOP]
ABS_THRESHOLDS={'H_I':13.598434599702,'He_I':24.587389011,'He_II':54.41776,'Li_I':5.390}
KIM={'H_I':(13.61,.7576,-5.521,5.867,2.948),
     'He_I':(24.58,.7326,-5.117,3.295,2.468),
     'He_II':(54.42,.06233,-.2982,.2835,.327)}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def sigma_kim(E,coefficient):
    I,A,B,C,D=coefficient
    x=np.asarray(E,dtype=float)/I
    m=np.maximum(x,1.)
    r=1e-16*(A*np.log(m)+(B*np.log(m)+C*(m-1.))/(m+D))/m
    # Original fit is positive in domain of present analysis; zeros outside ionization threshold.
    return np.where(x<=1.,0.,r)

def sigma_ccc_1d(table,energy,channel):
    # Same physical source interpolation as PR311, including observed HeI TICS edge repair.
    e=np.asarray(energy,float)
    out=np.interp(e,table[:,0],table[:,1],left=0.,right=float(table[-1,1]))
    if channel=='HeI_ion':
        edge=24.587389011
        mid=(e>edge)&(e<24.6)
        val=np.interp(24.6,table[:,0],table[:,1])
        out[mid]=val*(e[mid]-edge)/(24.6-edge)
        out[e<=edge]=0.
    else:
        first=float(table[0,0]);out[e<=first]=0.
    return out

def event_probability_step(dtau):
    """Returns (survival, first-event probability, phi=(1-exp(-tau))/tau).

    Stable for both tiny optical depths and optically thick cells.
    """
    tau=np.asarray(dtau,float)
    surv=np.exp(-tau)
    q=-np.expm1(-tau)
    phi=np.empty_like(tau)
    small=tau<1e-5
    phi[small]=1-tau[small]/2+tau[small]**2/6-tau[small]**3/24
    phi[~small]=q[~small]/tau[~small]
    return surv,q,phi

def expected_event_distance(dx,tau):
    """Conditional starting-energy loss within constant-hazard cell."""
    tau=np.asarray(tau,float)
    out=np.empty_like(tau)
    small=tau<1e-4
    out[small]=dx*(0.5-tau[small]/12+tau[small]**3/720)
    middle=(~small)&(tau<40)
    out[middle]=dx*(1/tau[middle]-1/np.expm1(tau[middle]))
    large=tau>=40
    out[large]=dx/tau[large]
    return out

def solve(first_energy,cell_tau):
    """Exact finite-cell competition for cell-averaged rates.

    first_energy strictly increasing from E_LOW. cell_tau [state,cell,channel].
    Emits first channel probabilities p, event-energy weighted moments q,
    expected prior Coulomb loss L, and survivors S.
    """
    nstates, ncell, nch=cell_tau.shape
    assert len(first_energy)==ncell+1
    P=np.zeros((nstates,ncell+1,nch),float)
    Q=np.zeros_like(P)
    L=np.zeros((nstates,ncell+1),float)
    S=np.ones((nstates,ncell+1),float)
    for k in range(ncell):
        dE=first_energy[k+1]-first_energy[k]
        tau_ch=cell_tau[:,k,:]
        tau=tau_ch.sum(axis=1)
        survival,hit,phi=event_probability_step(tau)
        weight=np.zeros_like(tau_ch)
        np.divide(tau_ch,tau[:,None],out=weight,where=tau[:,None]>0)
        event=hit[:,None]*weight
        e_event=first_energy[k+1]-expected_event_distance(dE,tau)
        P[:,k+1,:]=survival[:,None]*P[:,k,:]+event
        Q[:,k+1,:]=survival[:,None]*Q[:,k,:]+event*e_event[:,None]
        L[:,k+1]=survival*L[:,k]+dE*phi
        S[:,k+1]=survival*S[:,k]
    return P,Q,L,S

def hull(xs,ys,is_upper):
    indices=[]
    for k in range(len(xs)):
        while len(indices)>=2:
            i,j=indices[-2:]
            a=(ys[j]-ys[i])/(xs[j]-xs[i]);b=(ys[k]-ys[j])/(xs[k]-xs[j])
            if (a<=b if is_upper else a>=b):indices.pop()
            else:break
        indices.append(k)
    return np.asarray(indices,int)

def moment_bounds(grid,curve,lo,hi,mu):
    """Envelope for the *stored piecewise-linear P(E)*, not guaranteed exact
    to the underlying continuous microscopic model between energy nodes.
    """
    if lo>hi or mu<lo-1e-2 or mu>hi+1e-2:raise ValueError('INVALID_SOURCE_BAND')
    mu=max(lo,min(hi,mu))
    support=np.unique(np.r_[lo,grid[(grid>lo)&(grid<hi)],hi])
    yy=np.interp(support,grid,curve)
    if len(support)==1:return yy[0],yy[0],yy[0]
    imin=hull(support,yy,False);imax=hull(support,yy,True)
    vmin=float(np.interp(mu,support[imin],yy[imin]))
    vmax=float(np.interp(mu,support[imax],yy[imax]))
    vbar=float(np.interp(mu,support,yy))
    tol=5e-12*max(1,abs(vmin),abs(vbar),abs(vmax))
    assert vmin<=vbar+tol and vbar<=vmax+tol,(lo,hi,mu,vmin,vbar,vmax)
    return vmin,vbar,vmax

def load_physics():
    for k,d in INPUT_SHA.items():assert sha(INPUT/k)==d,('SOURCE_SHA_MISMATCH',k)
    tables,meta=load_ccc()
    a=pd.read_csv(INPUT/'PR302_ARRIVAL_192.csv')
    c=pd.read_csv(INPUT/'PR303_SPECIES_192.csv')
    t=pd.read_csv(INPUT/'PR302_THERMAL_192.csv')
    p=pd.read_csv(INPUT/'PR_BASS193_ELECTRON_FEEDBACK_193.csv')
    assert (len(a),len(c),len(t),len(p))==(192,192,192,193)
    assert np.array_equal(p.epoch,np.arange(193))
    assert np.all(p.nb_m3>0) and np.all(p.xe_saved>0)
    assert np.max(abs(p.z.to_numpy()[1:]-a.z_low.to_numpy()))<1e-11
    assert np.max(abs(c.z_end.to_numpy()-a.z_low.to_numpy()))<1e-11
    assert np.max(abs(t.z_low.to_numpy()-a.z_low.to_numpy()))<1e-11
    return tables,meta,a,c,t,p

def density_193(comp,thermal,plasma):
    YHe=comp.helium_per_H_ref.to_numpy()
    assert np.max(YHe)-np.min(YHe)<1e-9
    yhe=float(YHe.mean())
    nhr=np.r_[thermal.nHref_over_nb.iloc[0],thermal.nHref_over_nb.to_numpy()]
    nb=plasma.nb_m3.to_numpy()*1e-6
    nH=nb*nhr
    xi_hi=np.r_[comp.xHII_start.iloc[0],comp.xHII_end.to_numpy()]
    xi_hei=np.r_[comp.xHeI_end.iloc[0],comp.xHeI_end.to_numpy()]
    # Original start HeI calculated from conserved ion fractions; initial He ion fractions are provided in PR303.
    xi_hei[0]=1.-float(comp.xHeII_start.iloc[0])-float(comp.xHeIII_start.iloc[0])
    xi_heii=np.r_[comp.xHeII_start.iloc[0],comp.xHeII_end.to_numpy()]
    nHI=nH*(1-xi_hi)
    nHeI=nH*yhe*xi_hei
    nHeII=nH*yhe*xi_heii
    ne=nb*plasma.xe_saved.to_numpy()
    assert np.all(nHI>=0) and np.all(nHeI>=0) and np.all(nHeII>=0) and np.all(ne>0)
    # Independent source consistency: H/He electron pool slightly below native 21-ion bath.
    nHHe=nH*(xi_hi+yhe*(xi_heii+2*np.r_[comp.xHeIII_start.iloc[0],comp.xHeIII_end.to_numpy()]))
    eps=(ne-nHHe)/ne
    assert eps.min()>-1e-6 and eps.max()<1e-3
    return dict(nHI=nHI,nHeI=nHeI,nHeII=nHeII,ne=ne,nb=nb,nH=nH,yhe=yhe,ne_extra_fraction=eps)

def main(nuniform=600):
    tables,meta,arr,comp,thermal,plasma=load_physics()
    densities=density_193(comp,thermal,plasma)
    # Include all reduced CCC knots, threshold changes, and uniform Gaussian-lab energy nodes.
    energy=np.unique(np.r_[E_LOW,E_TOP,np.linspace(E_LOW,E_TOP,nuniform+1),
       *[t[(t[:,0]>E_LOW)&(t[:,0]<E_TOP),0] for t in tables.values()],
       24.58,24.587389011,24.6,54.42])
    energy=energy[(energy>=E_LOW)&(energy<=E_TOP)]
    mid=(energy[1:]+energy[:-1])/2
    ne=densities['ne'];nHI=densities['nHI'];nHeI=densities['nHeI'];nHeII=densities['nHeII']
    def hazards(ee):
        E=np.asarray(ee,float)
        v=np.sqrt(2*E*EV_ERG/ME_G)
        lnL=np.log(4*E[None,:]/(7.40e-11*ne[:,None]))
        assert np.min(lnL)>1,('COULOMB_LOG_DOMAIN',np.min(lnL))
        loss_ev_s=4*np.pi*E2**2*ne[:,None]*lnL/(ME_G*v[None,:]*EV_ERG)
        sig6=np.vstack([sigma_ccc_1d(tables[k],E,k) for k in TARGETS])
        assert np.all(sig6>=0)
        target6=np.vstack([nHI,nHI,nHI,nHeI,nHeI,nHeI]).T
        cc=target6[:,:,None]*sig6[None,:,:]*v[None,None,:]/loss_ev_s[:,None,:]
        kim=np.vstack([sigma_kim(E,KIM[k]) for k in KIM])
        assert np.min(kim)>=-1e-24
        targetkim=np.vstack([nHI,nHeI,nHeII]).T
        kk=targetkim[:,:,None]*kim[None,:,:]*v[None,None,:]/loss_ev_s[:,None,:]
        return np.moveaxis(cc,-1,1),np.moveaxis(kk,-1,1)
    cc0,kk0=hazards(energy);ccm,kkm=hazards(mid)
    dE=np.diff(energy)[None,:,None]
    cc_cell=dE*(cc0[:,:-1,:]+4*ccm+cc0[:,1:,:])/6
    kk_cell=dE*(kk0[:,:-1,:]+4*kkm+kk0[:,1:,:])/6
    assert cc_cell.min()>=0 and kk_cell.min()>=0
    p6,q6,L,S=solve(energy,cc_cell)
    pccc2,_,_,Sccc2=solve(energy,cc_cell[:,:,[0,3]])
    pk2,_,_,Sk2=solve(energy,kk_cell[:,:,:2])
    pk3,_,_,Sk3=solve(energy,kk_cell)
    assert np.max(abs(p6.sum(2)+S-1))<3e-13
    assert np.max(abs(pccc2.sum(2)+Sccc2-1))<3e-13
    assert np.max(abs(pk3.sum(2)+Sk3-1))<3e-13
    assert np.max(abs(energy[None,:] - (L+q6.sum(axis=2)+E_LOW*S)))<5e-11
    # No collisions under E_LOW are modelled. Extend with event=0 and stopping=0.
    Eeval=np.r_[0.,10.2,13.598434599702,E_LOW,energy[1:]]
    def extend(xx):return np.concatenate((np.zeros((len(ne),3)+xx.shape[2:]),xx),axis=1)
    def ext_scalar(xx):return np.concatenate((np.zeros((len(ne),3)),xx),axis=1)
    curves={
      'CCC6_first_total':extend(p6.sum(axis=2)[:,:,None])[:,:,0],
      'CCC6_first_HI_ion':extend(p6[:,:,0,None])[:,:,0],
      'CCC6_first_HeI_ion':extend(p6[:,:,3,None])[:,:,0],
      'CCC6_first_HI_exc_n2':extend((p6[:,:,1]+p6[:,:,2])[:,:,None])[:,:,0],
      'CCC6_first_HeI_exc':extend((p6[:,:,4]+p6[:,:,5])[:,:,None])[:,:,0],
      'CCC6_Coulomb_loss_before_first_eV':ext_scalar(L),
      'CCC6_first_event_energy_eV':ext_scalar(q6.sum(axis=2)),
      'CCC2_first_ion_total':extend(pccc2.sum(axis=2)[:,:,None])[:,:,0],
      'Kim2_first_ion_total':extend(pk2.sum(axis=2)[:,:,None])[:,:,0],
      'Kim3_first_ion_total':extend(pk3.sum(axis=2)[:,:,None])[:,:,0],
    }
    source=[];arrival=[]
    for j in range(192):
        i=j+1
        r=arr.iloc[j]
        entries={k:{'lower':0.,'mean':0.,'upper':0.} for k in curves}
        ncount=0.;ecount=0.
        for a in SPECIES:
            for b,band in enumerate(BANDS):
                N=float(r[f'{a}_{band}_counts_per_b']);M=float(r[f'{a}_{band}_primary_e_eV_per_b']);
                assert N>=-1e-30 and M>=-1e-25
                N=max(N,0.);M=max(M,0.);ncount+=N;ecount+=M
                lo=EDGES[b];hi=min(EDGES[b+1],E_TOP-ABS_THRESHOLDS[a]);hi=max(lo,hi)
                mean=M/N if N>0 else 0.
                d=dict(arrival_interval=j,epoch=i,z=float(r.z_low),first_absorber=a,energy_band=band,primary_electron_N_per_b=N,primary_electron_M_eV_per_b=M,mean_initial_E_eV=mean,physical_band_E_min_eV=lo,physical_band_E_max_eV=hi)
                for k,curve in curves.items():
                    if N==0:
                        lower=ref=upper=0.
                    else:
                        assert lo-1e-2<=mean<=hi+1e-2,(j,a,b,mean,lo,hi)
                        lower,ref,upper=moment_bounds(Eeval,curve[i],lo,hi,mean)
                        lower*=N;ref*=N;upper*=N
                    d[k+'_lower_per_b']=lower
                    d[k+'_mean_per_b']=ref
                    d[k+'_upper_per_b']=upper
                    entries[k]['lower']+=lower;entries[k]['mean']+=ref;entries[k]['upper']+=upper
                source.append(d)
        assert abs(ncount-float(r.total_absorbed_ionizations_per_b))<1e-23
        assert abs(ecount-float(r.total_primary_e_eV_per_b))<1e-23
        row=dict(arrival_interval=j,epoch=i,z=float(r.z_low),proper_interval_s=float(thermal.proper_interval_s.iloc[j]),source_photoelectron_N_per_b=ncount,source_photoelectron_M_eV_per_b=ecount,nHI_cm3=nHI[i],nHeI_cm3=nHeI[i],nHeII_cm3=nHeII[i],ne_native_cm3=ne[i],ne_HHe_extra_fraction=densities['ne_extra_fraction'][i])
        row.update({k+'_'+b+'_per_b':val[b] for k,val in entries.items() for b in ('lower','mean','upper')})
        arrival.append(row)
    df=pd.DataFrame(source);agg=pd.DataFrame(arrival)
    df.to_csv(OUTPUT/'FIRST_EVENT_SOURCE_BANDS_3840.csv',index=False,float_format='%.17g')
    agg.to_csv(OUTPUT/'FIRST_EVENT_ARRIVAL_192.csv',index=False,float_format='%.17g')
    # Actual 193 BASS epochs x 81 initial electron energies, including full native Coulomb and species densities.
    sampled_energies=np.unique(np.r_[13.7,20,25,30,40,54.42,60.922559447552,np.linspace(E_LOW,E_TOP,81)])
    rows=[]
    for i in range(193):
        for e in sampled_energies:
            d=dict(epoch=i,z=float(plasma.z.iloc[i]),initial_E_eV=float(e),nHI_cm3=float(nHI[i]),nHeI_cm3=float(nHeI[i]),nHeII_cm3=float(nHeII[i]),ne_native_cm3=float(ne[i]))
            for name,curve in curves.items():d[name]=float(np.interp(e,Eeval,curve[i]))
            d['CCC6_survivor_to_13p7']=1-d['CCC6_first_total']
            d['CCC6_energy_ledger_residual_eV']=float(e-(d['CCC6_Coulomb_loss_before_first_eV']+d['CCC6_first_event_energy_eV']+E_LOW*d['CCC6_survivor_to_13p7']))
            rows.append(d)
    pd.DataFrame(rows).to_csv(OUTPUT/'ORIGINAL_BASS193_FIRST_EVENT_SPECTRUM.csv',index=False,float_format='%.17g')
    summaries={}
    for key in curves:
        summaries[key]={t:float(agg[key+'_'+t+'_per_b'].sum()) for t in ('lower','mean','upper')}
    max_ledger=float(np.max(abs(energy[None,:]-(L+q6.sum(axis=2)+E_LOW*S))))
    stats=dict(
        status='SOURCE_CONDITIONAL_FROZEN_CCC6_VS_KIM92_COULOMB_FIRST_EVENT',
        n_states=193,n_arrival=192,n_source_bands=len(df),n_energy_samples=len(rows),
        original_CCC_reduced_snapshot_commit=meta['mirror_commit'],source_sha256=INPUT_SHA,
        first_photoelectron_N_per_b=float(agg.source_photoelectron_N_per_b.sum()),
        first_photoelectron_E_eV_per_b=float(agg.source_photoelectron_M_eV_per_b.sum()),
        energy_floor_eV=E_LOW, energy_top_eV=E_TOP,
        event_prob_normalization_max_abs=float(np.max(abs(p6.sum(2)+S-1))),
        first_event_energy_ledger_max_abs_eV=max_ledger,
        max_native_extra_ne_fraction=float(densities['ne_extra_fraction'].max()),
        source_event_aggregates=summaries,
        event_probability_examples={str(i):{'z':float(plasma.z.iloc[i]),'CCC6_total':float(p6[i,-1].sum()),'CCC6_HI_ion':float(p6[i,-1,0]),'CCC6_HeI_ion':float(p6[i,-1,3]),'CCC6_HI_exc':float(p6[i,-1,1]+p6[i,-1,2]),'Kim2_total':float(pk2[i,-1].sum()),'Kim3_total':float(pk3[i,-1].sum()),'CCC2_ion_total':float(pccc2[i,-1].sum()),'survivor':float(S[i,-1]),'Coulomb_loss_eV':float(L[i,-1])} for i in [0,64,96,128,192]},
        model_scope=['All first collisions start with original frozen BASS193 source, source amplitude conditional LiII singlet maximum.',
              'Only 6 CCC H I/He I inelastic channels in CCC6, no He II collision or other excitations/elastic; Kim2/Kim3 are independent first-ionization-only alternatives.',
              'Coulomb energy loss is Furlanetto-Stoever 2010 E>13.7eV electron-electron stopping, first event only, no postcollision secondary cascade.',
              'Band bounds exact for tabulated piecewise-linear first-event probability curves under N and M moments, not physical uncertainty bands.',
              'Coulomb energy expectation before first discrete collision is modeled partial heating only, not evolved temperature, no photon source added.'],
        dag={'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0,'F4':'PARTIAL','L4_READY':False,'production':'HOLD'},
        new_cosmology_ivps=0)
    (OUTPUT/'RESULTS.json').write_text(json.dumps(stats,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in stats.items() if k not in ('model_scope','source_sha256')},indent=2))
    return stats

if __name__=='__main__':main()
