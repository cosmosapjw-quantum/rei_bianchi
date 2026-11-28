#!/usr/bin/env python3
"""WU R48: original EMAA HD19 collision operator on original REI tick160 states.

Source-owned WU contribution: no modification/IVP of REI, BASS, REC, main.
All derived 19-state transitions are conditional on source-original REI (H, H+) fractions,
two-source-temperature interpolation, no actual HD abundance/level populations.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, math, pathlib, zipfile
import numpy as np
from scipy.constants import h, c, k as k_B
import wu_r47_source_adapter as r47

REI_SHA = r47.REI_SHA
EMAA_SHA = r47.EMAA_SHA
R47_ADAPTER_SHA = '61bf5c8789f4a095bbe10f8aa222138db24c6b811accfff5989affc27603eb02'
NODES = 46080
NLEVELS = 19
NPAIRS = 171


def sha256_file(path):
    dig=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(1<<20), b''):
            dig.update(part)
    return dig.hexdigest()


def source_read(emaa_zip):
    with zipfile.ZipFile(emaa_zip) as z:
        if z.testzip() is not None: raise ValueError('EMAA ZIP CRC')
        raw=z.read(r47.SOURCE_PREFIX)
    if r47.sha256(raw)!=EMAA_SHA: raise ValueError('EMAA source not exact')
    lines=raw.decode('utf8').splitlines()
    # These are the 52 EMAA HD levels in the original RADEX file, not inferred levels.
    if '52' not in lines[5]: raise ValueError('52-level original header')
    energ=[]; degen=[]; labels=[]
    for i in range(52):
        fields=lines[7+i].split()
        if int(fields[0])!=i+1: raise ValueError('Original level IDs changed')
        energ.append(float(fields[1])*100*h*c)
        degen.append(float(fields[2]))
        labels.append(fields[3])
    energ=np.asarray(energ,dtype=np.float64); degen=np.asarray(degen,dtype=np.float64)
    if not(np.all(np.diff(energ)>0) and np.all(degen>0)):raise ValueError('Original HD energy ordering')
    coll={}
    for i,s in enumerate(lines):
        if s.strip()!='! COLLISIONS BETWEEN':continue
        who='HPLUS' if 'HD + H+' in lines[i+1] else 'H' if 'HD + H ' in lines[i+1] else None
        if who is None:raise ValueError('Unexpected collider')
        n=int(lines[i+3]); t=np.array([float(v) for v in lines[i+7].split()])
        if not np.all(np.diff(t)>0):raise ValueError('source T monotonic')
        rows=[lines[j].split() for j in range(i+9,i+9+n)]
        pairs=np.array([[int(r[1])-1,int(r[2])-1] for r in rows],dtype=int)
        rates=np.array([[float(x) for x in r[3:]] for r in rows],dtype=np.float64)
        if rates.shape!=(n,len(t)) or np.any(~np.isfinite(rates)) or np.any(rates<=0):
            raise ValueError('source rate cells invalid')
        if len(set(map(tuple,pairs)))!=n or not np.all(pairs[:,0]>pairs[:,1]):
            raise ValueError('original pair labels incomplete')
        coll[who]={'T':t,'pairs':pairs,'rates':rates}
    if set(coll)!={'H','HPLUS'} or len(coll['H']['pairs'])!=1326 or len(coll['HPLUS']['pairs'])!=171:
        raise ValueError('original collider sizes')
    protons=coll['HPLUS']['pairs']
    expected={(u,l) for u in range(NLEVELS) for l in range(u)}
    if set(map(tuple,protons))!=expected:raise ValueError('not exact complete first 19 source transitions')
    h_dict={tuple(pair):i for i,pair in enumerate(coll['H']['pairs'])}
    if not all(tuple(pair) in h_dict for pair in protons):raise ValueError('neutral H transition mismatch')
    coll['H']['rates19']=coll['H']['rates'][[h_dict[tuple(pair)] for pair in protons]]
    return energ,degen,labels,coll


def interp_native(temps,native_T,raw_rates,mode='loglog'):
    """Return Nnode x Ntransition rate coefficients. No extrapolation, ever."""
    temps=np.asarray(temps,dtype=np.float64)
    if np.any(~np.isfinite(temps)) or np.any(temps<native_T[0]) or np.any(temps>native_T[-1]):
        raise ValueError('source-native interpolation range violation')
    ix=np.clip(np.searchsorted(native_T,temps,side='right')-1,0,len(native_T)-2)
    if mode=='loglog':
        u=np.log(temps/native_T[ix])/np.log(native_T[ix+1]/native_T[ix])
        return np.exp((1-u[:,None])*np.log(raw_rates[:,ix].T)+u[:,None]*np.log(raw_rates[:,ix+1].T))
    if mode=='linear':
        u=(temps-native_T[ix])/(native_T[ix+1]-native_T[ix])
        return (1-u[:,None])*raw_rates[:,ix].T+u[:,None]*raw_rates[:,ix+1].T
    raise ValueError('unsupported interpolation mode')


def boltzmann_tail(T,E,deg):
    T=np.asarray(T,dtype=np.float64)
    q=np.exp(-E[None,:]/(k_B*T[:,None]))*deg[None,:]
    q52=np.sum(q,axis=1)
    q19=np.sum(q[:,:NLEVELS],axis=1)
    return (q52-q19)/q52


def quantile(x):
    a=np.asarray(x,dtype=np.float64)
    return {key:float(val) for key,val in zip(('min','q05','median','q95','max'),np.quantile(a,[0,.05,.5,.95,1]))}


def shared_source_interval(Tlo,Thi,xlo,xhi,H,P,calc_method='loglog'):
    if not (np.all(xlo>=0) and np.all(xhi<1) and np.all(xlo<=xhi)):
        raise ValueError('x_HII original source range incorrect')
    def factor(T):
        return interp_native(T,P['T'],P['rates'],calc_method)/interp_native(T,H['T'],H['rates19'],calc_method)
    ratelo=factor(Tlo); ratehi=factor(Thi)
    low=np.minimum(ratelo,ratehi); upper=np.maximum(ratelo,ratehi)
    # Within each pair of original source temperature knots, log kp/kh is affine in log T.
    # Its extrema therefore occur at an endpoint or a source table knot.
    count_crossing=0
    for knot in sorted(set(H['T']).union(P['T'])):
        where=(Tlo<knot)&(knot<Thi)
        if np.any(where):
            count_crossing+=int(np.count_nonzero(where))
            at=factor(np.full(int(np.count_nonzero(where)),float(knot)))
            low[where]=np.minimum(low[where],at)
            upper[where]=np.maximum(upper[where],at)
    return (xlo/(1-xlo))[:,None]*low,(xhi/(1-xhi))[:,None]*upper,count_crossing


def symmetric_from_pairs(rate_down,DB,pairs):
    n=len(rate_down)
    S=np.zeros((n,NLEVELS,NLEVELS),dtype=np.float64)
    up,lo=pairs.T
    e=np.sqrt(DB)*rate_down
    # direct sum-of-exits on the diagonal, no unphysical density dimension inserted
    for j,(u,l) in enumerate(pairs):
        S[:,u,l]=e[:,j]
        S[:,l,u]=e[:,j]
        S[:,u,u]-=rate_down[:,j]
        S[:,l,l]-=rate_down[:,j]*DB[:,j]
    return S


def write_csv_gz(path,fields,rows):
    with open(path,'wb') as f:
        with gzip.GzipFile(fileobj=f,filename='',mode='wb',mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding='utf8',newline='') as tx:
                w=csv.writer(tx,lineterminator='\n')
                w.writerow(fields)
                for row in rows:w.writerow(row)
                tx.flush()


def analyze(emaa_zip,rei_zip,out,*,full=True):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    if sha256_file(rei_zip)!=REI_SHA:raise ValueError('REI ZIP source SHA mismatched')
    if sha256_file(pathlib.Path(__file__).with_name('wu_r47_source_adapter.py'))!=R47_ADAPTER_SHA:
        raise ValueError('WU R47 inherited parser byte identity')
    E,G,labels,c=source_read(emaa_zip)
    source,lh=r47.read_states(pathlib.Path(rei_zip).read_bytes())
    if len(source)!=NODES or len(set(lh.values()))!=1:raise ValueError('source states lane identity')
    joint=[]
    for r in source:
        a,b=map(float,(r['T_K_lo'],r['T_K_hi']))
        if 5<=a<=b<=3005:
            joint.append(r)
    if len(joint)!=5616:raise ValueError('frozen REI R47 exact joint T support count changed')
    node=np.array([int(r['node']) for r in joint],dtype=np.int64)
    Tlo=np.array([float(r['T_K_lo']) for r in joint]);Thi=np.array([float(r['T_K_hi']) for r in joint]);Tmid=(Tlo+Thi)/2
    xlo=np.array([float(r['x_HII_lo']) for r in joint]);xhi=np.array([float(r['x_HII_hi']) for r in joint]);xmid=(xlo+xhi)/2
    pair=c['HPLUS']['pairs'];up,lo=pair.T
    H=c['H'];P=c['HPLUS'];kH=interp_native(Tmid,H['T'],H['rates19']);kP=interp_native(Tmid,P['T'],P['rates'])
    ratio=xmid[:,None]*kP/((1-xmid[:,None])*kH)
    rlo,rhi,nk=shared_source_interval(Tlo,Thi,xlo,xhi,H,P)
    if not np.all(np.isfinite(ratio)) or not np.all(ratio>=rlo*(1-2e-13)) or not np.all(ratio<=rhi*(1+2e-13)):
        raise ValueError('ratio outer bounds invalid')
    # Positive finite-temperature state-resolved detailed balance with original HD term energies.
    dbfac=(G[up]/G[lo])[None,:]*np.exp(-(E[up]-E[lo])[None,:]/(k_B*Tmid[:,None]))
    if np.any(dbfac<=0) or np.any(~np.isfinite(dbfac)):raise ValueError('detailed balance source')
    aH=(1-xmid[:,None])*kH
    aP=xmid[:,None]*kP
    SH=symmetric_from_pairs(aH,dbfac,pair)
    SP=symmetric_from_pairs(aP,dbfac,pair)
    # Spectral gaps of the reversible generators: physically conditional 19 levels only.
    # Eigenvalues are sorted ascending; one zero eigenvalue is the largest.
    evH=np.linalg.eigvalsh(SH)
    evP=np.linalg.eigvalsh(SP)
    gapH=-evH[:,-2];gapP=-evP[:,-2];gapR=gapP/gapH
    if np.any(gapH<=0) or np.any(gapP<=0) or np.any(evH[:,-1]>5e-21) or np.any(evP[:,-1]>5e-21):
        raise ValueError('reversible generator spectral invariants')
    gammin=np.min(rlo,axis=1)
    if np.any(gapR<gammin*(1-4e-7)):
        raise ValueError('spectral-gap Dirichlet domination theorem violated')
    outlow=boltzmann_tail(Tlo,E,G)
    outmid=boltzmann_tail(Tmid,E,G)
    outhigh=boltzmann_tail(Thi,E,G)
    if np.any(outlow>outmid*(1+1e-14)) or np.any(outmid>outhigh*(1+1e-14)):
        raise ValueError('energy sorted LTE tail monotonicity')
    # Every up/down transition in original 19-state support is Boltzmann detailed-balanced
    # within each collider, so proton/H down ratio is also the ratio for reverse up.
    if np.any(rlo<=1):raise ValueError('claimed proton dominance is not universal under rectangular original source intervals')
    exit_h=np.zeros((len(node),NLEVELS));exit_p=np.zeros_like(exit_h)
    for j,(u,l) in enumerate(pair):
        exit_h[:,u]+=aH[:,j];exit_h[:,l]+=aH[:,j]*dbfac[:,j]
        exit_p[:,u]+=aP[:,j];exit_p[:,l]+=aP[:,j]*dbfac[:,j]
    exit_r=exit_p/exit_h
    if np.any(exit_r<=1):raise ValueError('exit-rate dominance failed')
    if full:
        def rows_trans():
            for i,n in enumerate(node):
                for j,(u,l) in enumerate(pair):
                    yield (int(n),int(u+1),int(l+1),labels[u],labels[l],format(Tmid[i],'.17g'),format(xmid[i],'.17g'),
                        format((E[u]-E[l]),'.17g'),format(kH[i,j],'.17g'),format(kP[i,j],'.17g'),
                        format(ratio[i,j],'.17g'),format(rlo[i,j],'.17g'),format(rhi[i,j],'.17g'))
        write_csv_gz(out/'R48_ORIGINAL_19STATE_TRANSITION_RATIO_960336.csv.gz',
            ['node','upper_original_level','lower_original_level','upper_v_j','lower_v_j','T_gas_K_mid','x_HII_mid',
            'delta_E_J','kH_down_cm3_s','kHplus_down_cm3_s','Gamma_Hplus_over_H_mid',
            'ratio_rect_outer_lower','ratio_rect_outer_upper'],rows_trans())
        def rows_exit():
            for i,n in enumerate(node):
                for j in range(NLEVELS):
                    yield (int(n),j+1,labels[j],format(Tmid[i],'.17g'),format(xmid[i],'.17g'),
                      format(exit_h[i,j],'.17g'),format(exit_p[i,j],'.17g'),format(exit_r[i,j],'.17g'))
        write_csv_gz(out/'R48_REI_HD19_LEVEL_EXITS_106704.csv.gz',
           ['node','original_level','v_j','T_gas_K_mid','x_HII_mid','H_exit_per_nHnuc_cm3_s',
            'Hplus_exit_per_nHnuc_cm3_s','Hplus_over_H_level_exit'],rows_exit())
        pair_by=[]
        for j,(u,l) in enumerate(pair):
            pair_by.append({'upper_id':int(u+1),'lower_id':int(l+1),'upper_v_j':labels[u],'lower_v_j':labels[l],
             'min_rate_ratio_mid':float(ratio[:,j].min()),'median_rate_ratio_mid':float(np.median(ratio[:,j])),
             'max_rate_ratio_mid':float(ratio[:,j].max()),
             'min_allnode_outer_lower':float(rlo[:,j].min()),
             'all_5616_nodes_proton_dominant':bool(np.all(rlo[:,j]>1))})
        with (out/'R48_TRANSITION_SUMMARY_171.csv').open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=pair_by[0]);w.writeheader();w.writerows(pair_by)
        with (out/'R48_REI_NODE_SUMMARY_5616.csv').open('w',newline='',encoding='utf8') as f:
            fields=['node','T_K_lo','T_K_hi','xHII_lo','xHII_hi','ratio_min_171_mid','ratio_min_171_outer_lower',
              'ratio_median_171_mid','ratio_max_171_mid','ratio_min_level_exit','ratio_gap_Hplus_over_H',
              'gap_H_cm3_s_per_nHnuc','gap_Hplus_cm3_s_per_nHnuc','LTE_Q52_outside_Hplus19_lo',
              'LTE_Q52_outside_Hplus19_mid','LTE_Q52_outside_Hplus19_hi']
            w=csv.writer(f,lineterminator='\n');w.writerow(fields)
            for i,n in enumerate(node):
                v=[n,Tlo[i],Thi[i],xlo[i],xhi[i],np.min(ratio[i]),gammin[i],np.median(ratio[i]),
                 np.max(ratio[i]),np.min(exit_r[i]),gapR[i],gapH[i],gapP[i],outlow[i],outmid[i],outhigh[i]]
                w.writerow([int(q) if j==0 else format(float(q),'.17g') for j,q in enumerate(v)])
        # independent source witness rows: min-ratio pair + 2/1 R47 anchor + 19th upper
        indices=[int(np.argmin(rlo)),int(np.argmax(ratio)),0,86,170]
        with (out/'R48_PHYSICAL_5_WITNESS_TRANSITIONS.csv').open('w',newline='',encoding='utf8') as f:
            w=csv.writer(f);w.writerow(['node','upper_original_level','lower_original_level','T_mid_K','xHII_mid',
               'kH_cm3_s','kHplus_cm3_s','ratio_mid','ratio_outer_lo','ratio_outer_hi'])
            for flat in indices:
                i,j=divmod(flat,NPAIRS);u,l=pair[j]
                w.writerow([int(node[i]),int(u+1),int(l+1),*[format(float(z),'.17g') for z in
                  (Tmid[i],xmid[i],kH[i,j],kP[i,j],ratio[i,j],rlo[i,j],rhi[i,j])]])
    stats={
       'schema':'WU_R48_EMAA_HD19_REI_26EVENT_TICK160_COLLISION_OPERATOR_V1',
       'origin':{'project':'cosmosapjw-quantum/WU088_HH','source':'EMAA_HD_ROVIBRATION_805A7AA5',
          'emaa_radex_sha256':EMAA_SHA,'emaa_recovery_zip_sha256':sha256_file(emaa_zip),
          'rei_original_accepted_state_zip_sha256':REI_SHA,'r47_source_adapter_sha256':R47_ADAPTER_SHA,
          'three_lane_numeric_sha256':lh,'parent_WU_PR':186,'parent_WU_head':'77062bd123352dc5044dd976cf0ac6439e15ce5f'},
       'domain':{'original_REI_unique_spatial_states':NODES,'joint_native_T_supported_nodes':len(node),
        'original_H_plus_Hplus_collisions_source_level_span':NLEVELS,'original_source_transitions':NPAIRS,
        'derived_original_node_transition_rows':int(len(node)*NPAIRS),
        'derived_level_exit_rows':int(len(node)*NLEVELS),
        'actual_T_mid_K':quantile(Tmid),'actual_xHII_mid':quantile(xmid),
        'original_T_branches_crossed':int(nk),
        'source_interpolation':'piecewise log-log; not original measured source values'},
       'physical_results':{
         'proton_dominant_transition_pairs_per_node':int(NPAIRS),
         'proton_dominant_all_pairs_all_nodes':bool(np.all(rlo>1)),
         'min_proton_to_H_derived_ratio_mid_all_pairs_nodes':float(np.min(ratio)),
         'max_proton_to_H_derived_ratio_mid_all_pairs_nodes':float(np.max(ratio)),
         'median_proton_to_H_derived_ratio_mid_all_pairs_nodes':float(np.median(ratio)),
         'minimum_rectangular_source_temperature_ionization_ratio_bound':float(np.min(rlo)),
         'percent_transitions_with_universal_joint_source_dominance':100.0,
         'per_node_minimum_rate_ratio':quantile(np.min(ratio,axis=1)),
         'per_node_minimum_19state_exit_ratio':quantile(np.min(exit_r,axis=1)),
         'nineteen_state_Hplus_over_H_spectral_gap_ratio':quantile(gapR),
         'minimum_proton_vs_H_spectral_gap_ratio':float(np.min(gapR)),
         'minimum_source_interval_rate_ratio_all_pairs':float(np.min(rlo)),
         'minimum_gap_ratio_minus_interval_pair_bound':float(np.min(gapR-gammin)),
         'LTE_truncation_Q52_fraction_outside_19_at_REI_T':quantile(outmid),
         'max_LTE_tail_upper_in_original_T_parent_interval':float(np.max(outhigh)),
         'full_52_level_actual_nonLTE_error_bound':None},
       'semantics':{'spectral_gap_unit':'cm^3 s^-1 per total H-nucleus density of 1 cm^-3; physical rate scales with actual n_H,nuc in cm^-3',
        'proton_to_H_ratios_include':'H+ and H fractions from original REI accepted H/He-only state at tick160',
        'source_level19':'first 19 energies in original 52-level EMAA file, not a 19-state independent dataset',
        'reversibility':'both H and H+ upward coefficients derived by common gas-T detailed balance',
        'ratio_bounds':'outer rectangular margins in T and xHII; do not assert physically independent original parent coordinates',
        'LTE_tail':'diagnostic of omitted ORIGINAL EMAA 52-level LTE weight, NOT a rigorous nonLTE population or cooling-error bound',
        'no_nHD':'no real HD molecular abundance in original H/He source; collision-only per-nucleus operator, not measured volumetric cooling',
        'not_claimed':['HD52 proton rates above level19','HD total collision+photon stationary populations',
          'full REI cosmological molecular heating or gas Q','new REI 26-event IVP','F05 full first interval acceptance',
          'new Bianchi vs FLRW observer history','original dataset novelty','new central DAG admission']},
       'DAG':{'WU_canonical_before':'34/49','WU_canonical_after':'34/49',
        'REI_central_before':'28/88','REI_central_after':'28/88',
        'REI_working':'33/88','canonical_science_completed_delta':0},
       'policy':{'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','no_production':True,
            'no_main_merge':True,'no_new_REI_IVP':True,'auto_next_node':False}
    }
    (out/'R48_RESULTS.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    return stats


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--emaa-zip',type=pathlib.Path,required=True)
    ap.add_argument('--rei-zip',type=pathlib.Path,required=True)
    ap.add_argument('--out',type=pathlib.Path,required=True)
    ap.add_argument('--summary-only',action='store_true')
    args=ap.parse_args()
    z=analyze(args.emaa_zip,args.rei_zip,args.out,full=not args.summary_only)
    print(json.dumps({'physical_results':z['physical_results'], 'source_node_count':z['domain']['joint_native_T_supported_nodes'],
      'DAG':z['DAG']},indent=2))
if __name__=='__main__':main()
