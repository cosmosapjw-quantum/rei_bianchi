#!/usr/bin/env python3
"""Physics: compare two authentic REI 26-event rate diagnostics with an accepted state secant.

Important: PR321 rates are independent flux-box midpoints, not a coherent path;
this is a two-snapshot consistency diagnostic, NEVER a proof of trajectory accuracy
nor the source-owned F_h - F_{h/2} o F_{h/2} nonlinear defect.

Inputs read-only: REI PR321 HEAD @9afee... verified Actions artifact #13067184595,
REI PR320 original accepted-state Actions artifact #13064333012.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PR321_SHA="44b322e2ebbd7b915b6958709136d5dc041e2468b0d71f0eb67da013f6aad535"
PR320_SHA="48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7"
SOURCE_NAME="REI_PR321_VERIFIED_HEAD_26EVENT_SOURCE.zip"
STATE_NAME="REI_PR320_ORIGINAL_TICK160_NODE_PHYSICS.zip"
N=46080
TICK=160
TOTAL=131072
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
CHANNELS={"HII":("x_HII","dx_HII_dt_mid_per_s"),"HeII":("x_HeII","dx_HeII_dt_mid_per_s"),
          "HeIII":("x_HeIII","dx_HeIII_dt_mid_per_s"),"electron":("free_electrons_per_H","dxe_dt_mid_per_s")}

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def load(source_dir=ROOT/'source'):
    p=Path(source_dir)/SOURCE_NAME;q=Path(source_dir)/STATE_NAME
    if not p.is_file() or not q.is_file():raise ValueError('MISSING_PINNED_SOURCE_ARCHIVE')
    if sha(p)!=PR321_SHA:raise ValueError('PR321_HEAD_SOURCE_SHA_MISMATCH')
    if sha(q)!=PR320_SHA:raise ValueError('PR320_STATE_SHA_MISMATCH')
    with zipfile.ZipFile(p) as z, zipfile.ZipFile(q) as orig:
        if z.testzip() is not None or orig.testzip() is not None: raise ValueError('BAD_ARCHIVE_CRC')
        meta=json.loads(z.read('ORIGINAL_26EVENT_PHYSICS.json'))
        assert meta['schema']=='REI_IGM_26EVENT_ORIGINAL_SOURCE_T0_TICK160_V1'
        assert meta['accepted_tick']==TICK and meta['first_interval_total_ticks']==TOTAL
        assert meta['original_archive_sha256']=='a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b'
        assert meta['saved_model_diagnostic_rows']==6*N
        assert len(meta['rows'])==6
        rates={}
        for row in meta['rows']:
            assert row['source']=='unmodified_original_26event_MPRK22_OTS'
            assert 'NOT a physical trajectory' in row['source_flux_meaning']
            name=row['csv_file']; raw=z.read(name)
            if hashlib.sha256(raw).hexdigest()!=row['csv_sha256']:raise ValueError('ORIGINAL_CSV_SHA_MISMATCH '+name)
            r=pd.read_csv(io.BytesIO(gzip.decompress(raw)),float_precision='round_trip')
            if len(r)!=N or not np.array_equal(r.node.to_numpy(dtype=int),np.arange(N)):raise ValueError('BAD_NODE_GRID')
            if not np.isfinite(r.select_dtypes('number')).all().all():raise ValueError('NONFINITE_SOURCES')
            rates[(row['lane'],row['snapshot'])]=r
        assert set(rates)=={(lane,time) for lane in LANES for time in ('initial','accepted_tick160')}
        # Exactly the same numeric fields across shape-lane *labels*; do not count 3 independent histories.
        for time in ('initial','accepted_tick160'):
            reference=rates[(LANES[0],time)]
            for lane in LANES[1:]:
                assert reference.equals(rates[(lane,time)]),f'LANE_NONIDENTITY: {lane}/{time}'
        orig_rates=pd.read_csv(io.BytesIO(gzip.decompress(orig.read('NODEWISE_'+LANES[0]+'_46080_PHYSICAL.csv.gz'))),float_precision='round_trip')
        assert len(orig_rates)==N
        chosen=rates[(LANES[0],'accepted_tick160')]
        state_pairs={'x_HII':'x_HII','x_HeII':'x_HeII','x_HeIII':'x_HeIII',
                     'T_K':'temperature_K','xe_per_H':'free_electrons_per_H',
                     'U_thermal_erg_per_H':'thermal_erg_per_H'}
        match={}
        for src,dst in state_pairs.items():
            midpoint=.5*(orig_rates[src+'_lo']+orig_rates[src+'_hi'])
            v=chosen[dst]
            maxrel=float(np.max(abs((midpoint-v)/np.maximum(abs(midpoint),1e-50))))
            if maxrel>1e-8: raise ValueError('SOURCE_STATE_MISMATCH: '+src)
            match[src]=maxrel
        clocks={row['time_s_from_interval_begin'] for row in meta['rows'] if row['snapshot']=='accepted_tick160'}
        if len(clocks)!=1:raise ValueError('SOURCE_TIME_MISMATCH')
        h=float(next(iter(clocks)))
        if not h>0:raise ValueError('NONPOSITIVE_DELTA_TIME')
    return rates[(LANES[0],'initial')],chosen,orig_rates,h,meta,match

def calc(a,b,orig,h,match):
    data={'node':np.arange(N,dtype=int)}
    for key in ('temperature_K','x_HII','x_HeII','x_HeIII','free_electrons_per_H'):
        data[key+'_start']=a[key].to_numpy(float)
        data[key+'_tick160']=b[key].to_numpy(float)
    w=np.log(orig.T_K_hi.to_numpy(float)/orig.T_K_lo.to_numpy(float))
    data['original_logT_parent_width']=w
    stats={}
    for c,(state,rate) in CHANNELS.items():
        y0=a[state].to_numpy(float);y1=b[state].to_numpy(float)
        f0=a[rate].to_numpy(float);f1=b[rate].to_numpy(float)
        dy=y1-y0
        samples=.5*h*(f0+f1)
        residue=dy-samples
        a0=(6*dy/h-(4*f0+2*f1))/h
        a1=(-6*dy/h+(2*f0+4*f1))/h
        # This algebraic identity holds for the unique cubic Hermite interpolant;
        # a0,a1 do NOT certify the original source's physical second derivatives.
        reconstructed=-h*h*(a1-a0)/12
        if not np.allclose(reconstructed,residue,rtol=5e-12,atol=2e-15):raise ValueError('HERMITE_IDENTITY_MISMATCH')
        dbase=max(float(np.sum(abs(dy))),1e-100)
        resrel=np.abs(residue)/np.maximum(np.maximum(abs(dy),abs(samples)),1e-30)
        # Endpoint interval from the PR320 accepted state; y0 is the PR321 source-derived t0 representative.
        original_state_column={'HII':'x_HII','HeII':'x_HeII','HeIII':'x_HeIII','electron':'xe_per_H'}[c]
        delta_low=orig[original_state_column+'_lo'].to_numpy(float)-y0
        delta_high=orig[original_state_column+'_hi'].to_numpy(float)-y0
        outside=np.maximum(np.maximum(delta_low-samples,samples-delta_high),0.0)
        data[c+'_nominal_trapezoid_outside_accepted_interval']=outside
        summary={
          'nominal_outside_original_accepted_interval_count':int(np.count_nonzero(outside)),
          'nominal_outside_original_accepted_interval_fraction':float(np.mean(outside>0)),
          'nominal_outside_excess_abs_95pct':float(np.percentile(outside,95)),
          'nominal_outside_excess_abs_max':float(np.max(outside)),
          'representative_state_change_mean':float(np.mean(dy)),
          'representative_state_change_median':float(np.median(dy)),
          'two_sample_source_estimate_mean':float(np.mean(samples)),
          'delta_minus_two_sample_mean':float(np.mean(residue)),
          'absolute_residual_95pct':float(np.percentile(abs(residue),95)),
          'absolute_residual_max':float(np.max(abs(residue))),
          'sum_abs_residual_over_sum_abs_state_change':float(np.sum(abs(residue))/dbase),
          'source_estimate_vs_actual_delta_pearson':float(np.corrcoef(samples,dy)[0,1]),
          'sign_agreement_fraction':float(np.mean(np.sign(dy)==np.sign(samples))),
          'relative_residual_95pct':float(np.percentile(resrel,95)),
          'relative_residual_max':float(np.max(resrel)),
          'source_integral_sum_over_representative_change_sum':float(np.sum(samples)/np.sum(dy)),
          'local_sample_difference_max_rate_per_s':float(np.max(abs(f1-f0))),
          'max_relative_hermite_algebra_residual':float(np.max(abs(reconstructed-residue)/np.maximum(abs(residue),1e-30))) }
        for suffix,value in [('dx',dy),('two_sample_estimate_dx',samples),('dx_difference',residue),
                             ('f0_per_s',f0),('f1_per_s',f1),('hermite_start_curvature_per_s2',a0),('hermite_end_curvature_per_s2',a1)]:
            data[c+'_'+suffix]=value
        stats[c]=summary
    v=np.column_stack([data[c+'_dx_difference'] for c in CHANNELS])
    fdelta=np.column_stack([data[c+'_dx'] for c in CHANNELS])
    he_ratio=(a.free_electrons_per_H.to_numpy(float)-a.x_HII.to_numpy(float))/(a.x_HeII.to_numpy(float)+2*a.x_HeIII.to_numpy(float))
    yHe=float(np.median(he_ratio))
    charge_change=(data['HII_dx']+yHe*(data['HeII_dx']+2*data['HeIII_dx']))-data['electron_dx']
    charge_source=(data['HII_f0_per_s']+yHe*(data['HeII_f0_per_s']+2*data['HeIII_f0_per_s']))-data['electron_f0_per_s']
    maxcharge=max(float(np.max(abs(charge_change))),float(np.max(abs(charge_source)*h)))
    if maxcharge>1e-8:raise ValueError('CHARGE_LEDGER_FAILURE')
    # Source-thermal coupling is a diagnostic, not total thermal RHS.
    Qstart=(a.photoheat_erg_per_H_s_mid+a.resolved_OTS_heat_erg_per_H_s_mid-a.escaped_OTS_erg_per_H_s_mid).to_numpy(float)
    Qend=(b.photoheat_erg_per_H_s_mid+b.resolved_OTS_heat_erg_per_H_s_mid-b.escaped_OTS_erg_per_H_s_mid).to_numpy(float)
    deltaU=(b.thermal_erg_per_H-a.thermal_erg_per_H).to_numpy(float)
    data['thermal_change_erg_per_H']=deltaU
    data['two_sample_partial_photon_erg_per_H']=h*(Qstart+Qend)/2
    data['thermal_minus_partial_photon_erg_per_H']=deltaU-data['two_sample_partial_photon_erg_per_H']
    residual_abs=abs(data['HII_dx_difference'])
    idxsrc=np.argsort(residual_abs)[-50:]
    idxwidth=np.argsort(w)[-50:]
    overlap=len(set(idxsrc.tolist())&set(idxwidth.tolist()))
    peakids=np.argsort(residual_abs)[-24:][::-1]
    witnesses=[]
    for i in peakids:
        witnesses.append({k:float(v[i]) if k!='node' else int(v[i]) for k,v in data.items() if k in ('node','temperature_K_tick160','original_logT_parent_width','HII_dx','HII_two_sample_estimate_dx','HII_dx_difference','HII_nominal_trapezoid_outside_accepted_interval','HeII_dx','HeII_dx_difference','HeII_nominal_trapezoid_outside_accepted_interval','HeIII_dx','HeIII_dx_difference','electron_dx','electron_dx_difference')})
    temp= b.temperature_K.to_numpy(float)
    edges=np.quantile(temp,np.linspace(0,1,11))
    deciles=[]
    for i in range(10):
        mask=(temp>=edges[i])&(temp<edges[i+1] if i<9 else temp<=edges[i+1])
        deciles.append({'decile':i+1,'n':int(mask.sum()),'min_temperature_K':float(np.min(temp[mask])),
                        'max_temperature_K':float(np.max(temp[mask])),
                        'median_deltaHII':float(np.median(data['HII_dx'][mask])),
                        'mean_abs_source_snapshot_gap_HII':float(np.mean(residual_abs[mask])),
                        'mean_parent_logT_width':float(np.mean(w[mask]))})
    summary={'schema':'REI_PR321_HEAD_26EVENT_SNAPSHOT_SECANT_V1',
      'semantic_contract':{
        'state_change':'difference of initial and tick160 *in-box representatives*, not one identified time-continuous physical history',
        'source_integral':'trapezoid between independent event-flux interval midpoint samples; not an exact or bounded time integral',
        'outside_interval':'falsifies using that particular two-sample proxy as an in-box accepted state; not a violation of true 26-event ODE or solver',
        'hermite_curvature':'unique cubic Hermite interpolation curvature implied by two representatives and two midpoint flux samples, not original physical second derivatives'},
      'origin_rei_pr321_head':'9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d',
      'origin_rei_pr320_head':'e5836fc4b8804d1bcdcdcbb97ab33f822703fa46',
      'input_sha256':{'PR321_VERIFIED_HEAD':PR321_SHA,'PR320_ACCEPTED_STATE':PR320_SHA},
      'original_failed_run_archive_sha256':'a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b',
      'status':'SOURCE_AUTHENTIC_TWO_SNAPSHOT_PHYSICS_DIAGNOSTIC_NOT_JOINT_ERROR_CERTIFICATE',
      'spatial_nodes':N,'snapshots':2,'unique_node_snapshot_records':2*N,'lane_labelled_source_rows_reused':6*N,
      'new_derived_node_rows':N,'new_derived_temperature_deciles':10,'new_independent_observations':0,'new_original_ivps':0,
      'time_s_from_start_to_tick160':h,'tick160':TICK,'total_first_interval_ticks':TOTAL,
      'he_to_h_number_ratio_inferred':yHe,'he_to_h_max_abs_variation':float(np.max(abs(he_ratio-yHe))),
      'max_physical_charge_change_identity_abs':maxcharge,'parent_logT_width_max':float(np.max(w)),
      'original_one_tick_crossbox_failure':2.1245050576368385e-4,'original_local_error_gate':2.0e-4,
      'top50_HII_gap_vs_top50_logT_width_overlap':overlap,
      'HII_source_snapshot_gap_vs_parent_width_correlation':float(np.corrcoef(residual_abs,w)[0,1]),
      'source_state_midpoint_max_relative_deviation':match,
      'channel_diagnostics':stats,
      'photothermal_two_snapshot_only':{
        'mean_thermal_state_change_erg_per_H':float(np.mean(deltaU)),
        'mean_partial_photon_source_estimate_erg_per_H':float(np.mean(data['two_sample_partial_photon_erg_per_H'])),
        'mean_difference_not_a_missing_heating_measurement':float(np.mean(data['thermal_minus_partial_photon_erg_per_H'])),
        'notice':'Other chemistry, Compton, adiabatic, escape owners and intra-interval source dynamics not closed; not conserved energy residual'},
      'DAG':{'central_reported':'28/88','working_reported':'33/88','physical_fast_reported':'4/7','canonical_delta':0},
      'first_interval':'BLOCKED_MINIMUM_STEP','production':'HOLD',
      'no_merge':True,'no_force_push':True,'no_more_ivps':True,'auto_next_node':False,
      'claim_limits':['PR321 independent midpoint rates not coherent single source path',
         'This is not local full-minus-two-half error, not original owner 26-event Jacobian',
         'Equal-node arithmetic only; no volume/mass weights or present-day observable',
         'No causal inference from source gap and parent width correlation']}
    return data,summary,witnesses,deciles

def export(path, data,summary,witnesses,deciles):
    path=Path(path); path.mkdir(parents=True,exist_ok=True)
    names=list(data.keys())
    # Deterministic gzip for useful byte-level reproduce checks; no timestamp or nondeterministic filename.
    with (path/'NODEWISE_SOURCE_SECANT_46080.csv.gz').open('wb') as out:
        with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=6,mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding='utf-8',newline='',write_through=True) as text:
                writer=csv.writer(text,lineterminator='\n');writer.writerow(names)
                for i in range(N):writer.writerow([i if k=='node' else format(float(data[k][i]),'.17g') for k in names])
    for filename,rows in [('WITNESS_24_NODES.csv',witnesses),('TEMP_DECILE_10.csv',deciles)]:
        with (path/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    (path/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n')

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT/'source');ap.add_argument('--out',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    a,b,p,h,meta,match=load(args.source_dir)
    data,res,witnesses,deciles=calc(a,b,p,h,match)
    export(args.out,data,res,witnesses,deciles)
    print(json.dumps({'N':N,'dt_s':h,'results':res['channel_diagnostics'],
                      'width_gap_overlap':res['top50_HII_gap_vs_top50_logT_width_overlap'],
                      'original_interval':'BLOCKED_MINIMUM_STEP','central':'28/88'},indent=2))
    return res
if __name__=='__main__':main()
