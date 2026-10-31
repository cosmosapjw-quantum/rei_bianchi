#!/usr/bin/env python3
"""Original BASS193 photoelectron source x public CCC six-channel first-collision hazards.

No secondary-electron transport or gas temperature evolution. CCC samples are an
adaptive regridding of selected source ASCII files in EXHALE; original Curtin CCC
is the primary physics authority, EXHALE Git blob the byte source for these samples.
"""
from __future__ import annotations
from pathlib import Path
import base64, hashlib, json, math, bisect
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'inputs'; RESULTS=ROOT/'results';RESULTS.mkdir(exist_ok=True)
SHA={
 'PR302_ARRIVAL_192.csv':'155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df',
 'PR303_SPECIES_192.csv':'dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09',
 'PR302_THERMAL_192.csv':'292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6',
 'PR_BASS193_ELECTRON_FEEDBACK_193.csv':'50a9a7a2728f08ac4534f0e92071cdd4fb3b7ddc9a3e9f8175458d398ad06b0f',
}
M_E_G=9.1093837139e-28
EV_ERG=1.602176634e-12
SPECIES=['H_I','He_I','He_II','Li_I']
BANDS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
EDGES=[0,10.2,13.598434599702,24.587389011,54.41776,60.922559447552]
ABS_THRESHOLDS={'H_I':13.598434599702,'He_I':24.587389011,'He_II':54.41776,'Li_I':5.390}
TARGETS=['HI_ion','HI_2p','HI_2s','HeI_ion','HeI_2p','HeI_t2s']
H_TARGETS=TARGETS[:3]
# Physical threshold can be between rounded input cross-section grid samples.
# Enforce the exact He I ionization edge before interpolating any author data.
CHANNEL_THRESHOLDS={'HI_ion':13.6058,'HI_2p':10.20435,'HI_2s':10.20435,
                    'HeI_ion':24.587389011,'HeI_2p':21.1156,'HeI_t2s':19.7179}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_ccc():
    meta=json.loads((INPUT/'ccc_adaptive_b64.json').read_text())
    assert meta['mirror_commit']=='7388232fac2c3cdadad613515006de008360f1ab'
    out={}
    for name,item in meta['data'].items():
        b=base64.b64decode(item['b64'],validate=True)
        pos=0;energy=0;rows=[]
        def unsigned_varint():
            nonlocal pos
            result=0;shift=0
            while True:
                value=b[pos];pos+=1
                result|=(value&127)<<shift
                if not(value&128):return result
                shift+=7
                assert shift<50
        while pos<len(b):
            energy+=unsigned_varint()
            cross=unsigned_varint()
            rows.append((energy/1e6,cross/1e22))
        assert len(rows)==item['n'],(name,len(rows),item['n'])
        data=np.asarray(rows,dtype=float)
        assert np.isfinite(data).all() and np.all(np.diff(data[:,0])>0) and np.min(data[:,1])>=0
        assert data[0,1]==0 and data[-1,0]>=60
        out[name]=data
    assert set(out)==set(TARGETS)
    return out,meta


def v_cm_s(E):
    return math.sqrt(2*max(E,0)*EV_ERG/M_E_G)


def sigma_interp(data,E,channel):
    """Original CCC-snapshot linear-energy sigma with true ionization threshold.

    For He I TICS, 24.50 eV has sigma=0 and 24.60 has sigma>0; the
    published actual ionization energy is 24.587389011 eV. Replace
    ONLY this small table-interpolation segment by (threshold, 0) ->
    (24.60, measured sigma). No forced nonzero sigma below threshold.
    """
    theta=CHANNEL_THRESHOLDS[channel]
    if E<=theta:return 0.
    assert E<=data[-1,0]
    if channel=='HeI_ion' and E<24.6:
        sig_246=float(np.interp(24.6,data[:,0],data[:,1]))
        return sig_246*(E-theta)/(24.6-theta)
    return float(np.interp(E,data[:,0],data[:,1]))


def model_g(data,E,channel):
    return sigma_interp(data,E,channel)*v_cm_s(E)


def moment_geometry(data,low,high,channel):
    assert high>=low
    knots=np.unique(np.concatenate(([low],data[(data[:,0]>low)&(data[:,0]<high),0],
             [CHANNEL_THRESHOLDS[channel]] if low < CHANNEL_THRESHOLDS[channel] < high else [],[high])))
    g=np.asarray([model_g(data,float(v),channel) for v in knots])
    def hull(is_upper):
        index=[]
        for k in range(len(knots)):
            while len(index)>=2:
                i,j=index[-2:]
                slo=(g[j]-g[i])/(knots[j]-knots[i]);shi=(g[k]-g[j])/(knots[k]-knots[j])
                if (slo<=shi if is_upper else slo>=shi):index.pop()
                else: break
            index.append(k)
        return knots[index],g[index]
    return hull(False),hull(True),knots,g


def segment_interpolate(xs,ys,mean):
    return float(np.interp(mean,xs,ys))


def main():
    for name,d in SHA.items():assert sha(INPUT/name)==d,('SOURCE_SHA_MISMATCH',name)
    data,meta=load_ccc()
    arr=pd.read_csv(INPUT/'PR302_ARRIVAL_192.csv')
    comp=pd.read_csv(INPUT/'PR303_SPECIES_192.csv')
    thermal=pd.read_csv(INPUT/'PR302_THERMAL_192.csv')
    plasma=pd.read_csv(INPUT/'PR_BASS193_ELECTRON_FEEDBACK_193.csv')
    assert (len(arr),len(comp),len(thermal),len(plasma))==(192,192,192,193)
    assert np.array_equal(arr.arrival_interval,np.arange(192)) and np.array_equal(plasma.epoch,np.arange(193))
    assert np.max(abs(arr.z_low.to_numpy()-comp.z_end.to_numpy()))<1e-11
    assert np.max(abs(arr.z_low.to_numpy()-thermal.z_low.to_numpy()))<1e-11
    assert np.max(abs(arr.z_low.to_numpy()-plasma.z.to_numpy()[1:]))<1e-11
    assert np.isfinite(plasma.nb_m3).all() and (plasma.nb_m3>0).all()
    ratios=comp.helium_per_H_ref.to_numpy(); assert np.max(ratios)-np.min(ratios)<1e-9
    YHe=float(ratios[0]);
    # endpoint state: actual BASS species fractions, nHref/nb from original PR302 thermal
    nHcm=plasma.nb_m3.to_numpy()[1:]*1e-6*thermal.nHref_over_nb.to_numpy()
    ni_H=nHcm*(1-comp.xHII_end.to_numpy())
    ni_He=nHcm*YHe*comp.xHeI_end.to_numpy()
    ne=nHcm*(comp.xHII_end.to_numpy()+YHe*(comp.xHeII_end.to_numpy()+2*comp.xHeIII_end.to_numpy()))
    assert np.all(ni_H>=-1e-18) and np.all(ni_He>=-1e-18) and np.all(ne>=0)
    # moment hulls depend only on first absorber and energy band; target density multiplies later
    geometries={}
    for s in SPECIES:
        for k,b in enumerate(BANDS):
            low=EDGES[k];high=min(EDGES[k+1],EDGES[-1]-ABS_THRESHOLDS[s]);high=max(low,high)
            for c in TARGETS:
                geometries[(s,b,c)]=moment_geometry(data[c],low,high,c)
    rows=[];summ=[]
    max_badmean=0
    for j in range(192):
        r=arr.iloc[j]; x=comp.iloc[j]; dt=float(thermal.proper_interval_s.iloc[j])
        combined_N=0.;combined_M=0.; sum_rate=np.zeros(6);sum_low=np.zeros(6);sum_high=np.zeros(6)
        for s in SPECIES:
            for k,b in enumerate(BANDS):
                N=float(r[s+'_'+b+'_counts_per_b']);M=float(r[s+'_'+b+'_primary_e_eV_per_b']);
                assert N>=-1e-30 and M>=-1e-25
                N=max(N,0.);M=max(M,0.);mu=M/N if N>0 else 0.
                combined_N+=N;combined_M+=M
                a=EDGES[k];ub=min(EDGES[k+1],EDGES[-1]-ABS_THRESHOLDS[s]);ub=max(a,ub)
                assert N==0 or a-1e-2<=mu<=ub+1e-2,(j,s,b,mu,a,ub)
                Ebar=max(a,min(ub,mu)) if N>0 else 0.
                for cc,c in enumerate(TARGETS):
                    n_target=ni_H[j] if c.startswith('HI_') else ni_He[j]
                    geometry=geometries[s,b,c]
                    if N>0:
                        L,U,knots,g=geometry
                        min_g=segment_interpolate(*L,Ebar)
                        max_g=segment_interpolate(*U,Ebar)
                        # The moment envelope is exact for the *piecewise linear rate kernel*
                        # g=linear_interpolate(sigma_at_knots*v_at_knots). Collocation
                        # MUST use the same g, not sigma_linear(E)*sqrt(E). The
                        # latter has a different curvature and can lie outside a hull.
                        bar_g=segment_interpolate(knots,g,Ebar)
                        direct_g=model_g(data[c],Ebar,c)
                        lo=n_target*N*min_g
                        hi=n_target*N*max_g
                        ref=n_target*N*bar_g
                        rel_interp_err=abs(direct_g-bar_g)/max(max(g),1e-100)
                        max_badmean=max(max_badmean,rel_interp_err)
                        assert min_g-1e-11*max(g)<=bar_g<=max_g+1e-11*max(g),('MODEL_HULL_VIOLATION',c,s,b,j)
                    else:lo=hi=ref=0.
                    assert lo>=-1e-50 and hi>=-1e-50 and lo<=hi+max(1e-50,hi*2e-14)
                    sum_rate[cc]+=ref;sum_low[cc]+=lo;sum_high[cc]+=hi
                    rows.append(dict(arrival_interval=j,z_end=float(r.z_low),first_absorber=s,electron_band=b,
                                     electron_N_per_b=N,electron_M_eV_per_b=M,mean_electron_eV=mu,
                                     channel=c,source_sigma_blob=meta['data'][c]['blob'],
                                     n_target_cm3=n_target,rate_coeff_mean_cm3_s=bar_g if N>0 else 0,
                                     collision_nu_mean_s=ref/N if N>0 else 0,
                                     sigma_v_direct_curvature_relative_peak=rel_interp_err if N>0 else 0,
                                     source_weighted_nu_mean_per_b_s=ref,
                                     source_weighted_nu_lower_per_b_s=lo,
                                     source_weighted_nu_upper_per_b_s=hi,
                                     source_energy_end_eV=ub,within_segment_model=True))
        assert abs(combined_N-float(r.total_absorbed_ionizations_per_b))<1e-23,(j,'COUNT')
        assert abs(combined_M-float(r.total_primary_e_eV_per_b))<1e-23,(j,'ENERGY')
        summ.append(dict(arrival_interval=j,z_high=float(r.z_high),z_low=float(r.z_low),
                         proper_interval_s=dt,nb_m3=float(plasma.nb_m3.iloc[j+1]),
                         nHref_over_nb=float(thermal.nHref_over_nb.iloc[j]),nH_cm3=float(nHcm[j]),
                         nH_I_cm3=float(ni_H[j]),nHe_I_cm3=float(ni_He[j]),ne_HHe_cm3=float(ne[j]),
                         YHe_over_H=YHe,xHII_end=float(x.xHII_end),xHeII_end=float(x.xHeII_end),
                         xHeIII_end=float(x.xHeIII_end),primary_electrons_per_b=combined_N,primary_E_eV_per_b=combined_M,
                         **{c+'_source_nu_mean_per_b_s':float(sum_rate[i]) for i,c in enumerate(TARGETS)},
                         **{c+'_source_nu_min_per_b_s':float(sum_low[i]) for i,c in enumerate(TARGETS)},
                         **{c+'_source_nu_max_per_b_s':float(sum_high[i]) for i,c in enumerate(TARGETS)}))
    out=pd.DataFrame(rows);agg=pd.DataFrame(summ)
    out.to_csv(RESULTS/'CCC_FIRST_COLLISION_CHANNELS_23040.csv',index=False,float_format='%.17g')
    agg.to_csv(RESULTS/'CCC_FIRST_COLLISION_ARRIVAL_192.csv',index=False,float_format='%.17g')
    nonzero=agg.primary_electrons_per_b>0
    # Interval rates (not physical deposited yield); one-electron mean collocation averaged over source
    val=agg[[c+'_source_nu_mean_per_b_s' for c in TARGETS]].sum(axis=1)
    rate_per_electron=val[nonzero]/agg.primary_electrons_per_b[nonzero]
    neutral=agg[[c+'_source_nu_mean_per_b_s' for c in H_TARGETS]].sum(axis=1)
    he_ion=agg['HeI_ion_source_nu_mean_per_b_s']
    diagnostic=dict(
      schema='CCC_H_HE_PRIMARY_SOURCE_FIRST_COLLISION_RATE_V1', status='PHYSICAL_CCC_TABULATED_HAZARD_AT_ORIGINAL_BASS_FROZEN_BACKGROUND',
      sample_model='ADAPTIVE_PUBLIC_EXHALE_CCC_SAMPLES_0p5percent_peak_plus_moment_hull',
      BASS193_saved_plasma_states=193,real_arrival_intervals=192,
      source_first_photoelectron_channels=len(out),sources_per_arrival=20,
      species_and_processes=TARGETS,
      primary_electrons_per_b=float(agg.primary_electrons_per_b.sum()),
      primary_kinetic_eV_per_b=float(agg.primary_E_eV_per_b.sum()),
      original_BASS_nb_m3_range=[float(plasma.nb_m3.min()),float(plasma.nb_m3.max())],
      original_H_ref_cm3_range=[float(nHcm.min()),float(nHcm.max())],
      source_weighted_mean_nu_s_range=[float(rate_per_electron.min()),float(rate_per_electron.max())],
      source_weighted_mean_inelastic_collision_time_s_range=[float((1/rate_per_electron).min()),float((1/rate_per_electron).max())],
      intervals_where_first_inelastic_collocation_faster_than_proper_interval=int((rate_per_electron*agg.loc[nonzero,'proper_interval_s']>1).sum()),
      intervals_nonzero_source=int(nonzero.sum()),
      source_weighted_sum_over_snapshots_rates_per_b_s={c:float(agg[c+'_source_nu_mean_per_b_s'].sum()) for c in TARGETS},
      maximum_direct_sigma_v_vs_piecewise_linear_kernel_relative_peak=max_badmean,
      collision_operator_kind='6 partial CCC inelastic processes ONLY; missing many other CCC excitation states, HeII, elastic, and Coulomb',
      PERTINENT_CAVEAT='Summed snapshot rates across distinct epochs not integrated event counts, NOT chemistry or deposited energy',
      source_sha256=SHA, source_mirror_revision=meta['mirror_commit'],
      source_mirror_blobs={c:meta['data'][c]['blob'] for c in TARGETS},
      CCC_owner='https://atom.curtin.edu.au/CCC-WWW/index.html',
      statuses={'CCC_HHeI_source_files':'6_PUBLISHED_SNAPSHOT_BLOBS_USED','CCC_HeII_sigma':'NOT_ACQUIRED','native_nonthermal_cascade':'NOT_RUN','native_REI17_FJ':'NOT_RUN','production':'HOLD','new_IVP':0,'F4':'PARTIAL','L4_ready':False,'canonical_dag':'28/88','working_dag':'33/88','F4_fast_dag':'4/7','canonical_delta':0},
    )
    (RESULTS/'RESULTS.json').write_text(json.dumps(diagnostic,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in diagnostic.items() if k not in ['source_sha256','source_mirror_blobs']},indent=2))
    return out,agg,diagnostic

if __name__=='__main__':main()
