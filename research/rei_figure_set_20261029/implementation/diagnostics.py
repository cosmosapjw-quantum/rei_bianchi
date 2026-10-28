"""Saved-array diagnostics, no IVP. Local frozen operator imported for point diagnostics."""
import csv
import json
from pathlib import Path
import numpy as np

UNIT=Path(__file__).resolve().parents[1]
ROOT=UNIT.parent
SOURCE=ROOT/'rei_source_history_20261028'/'outputs'
OUT=UNIT/'outputs'
LABELS=('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2','He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
FAMILIES=(('n',[0]),('H1',[1,2]),('D',[3,4]),('T',[5,6]),('He3',[7,8,9]),('He4',[10,11,12]),('Li7',[13,14,15,16]))
CASES=('OFF_base','ON_base','ON_refined')
A=np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7])
Q=np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3])

def rows(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def relative(a,b):
    """Signed difference relative to maxabs, zero/zero exactly zero."""
    den=np.maximum(np.abs(a),np.abs(b))
    return np.divide(a-b,den,out=np.zeros_like(a-b),where=den!=0)

def load_cases(source=SOURCE):
    cases={}
    for name in CASES:
        with np.load(source/(name+'.npz'),allow_pickle=False) as d:
            cases[name]={k:d[k].copy() for k in ('t','physical','scales','baryon_residual','charge_residual')}
        c=cases[name];t=c['t']
        if t.ndim!=1 or c['physical'].shape!=(23,len(t)) or c['scales'].shape!=(23,):raise ValueError('case shape mismatch '+name)
        if any(not np.isfinite(x).all() for x in c.values()) or np.any(np.diff(t)<=0) or t[0]!=0 or np.any(c['scales']<=0):raise ValueError('invalid case '+name)
        if any(c[k].shape!=t.shape for k in ('baryon_residual','charge_residual')):raise ValueError('ledger shape mismatch')
        if name!=CASES[0] and not np.array_equal(t,cases[CASES[0]]['t']):raise ValueError('case clock mismatch')
    if any(not np.array_equal(cases[name]['physical'][:,0],cases['OFF_base']['physical'][:,0]) for name in CASES):raise ValueError('initial case stocks mismatch')
    if not np.array_equal(cases['ON_base']['scales'],cases['ON_refined']['scales']):raise ValueError('refinement scales mismatch')
    return cases

def refinement(base,ref,scales):
    delta=ref-base;norm=np.abs(delta)/scales[:,None]
    floor=np.maximum(1e-11*scales[:,None]+1e-7*np.abs(base),2e-12*scales[:,None]+2e-8*np.abs(ref))
    den=np.maximum(abs(base),abs(ref))
    condition=np.divide(floor,den,out=np.zeros_like(floor),where=den!=0)
    return {'delta':delta,'normalized':norm,'relative':np.abs(relative(ref,base)),
            'conditioning_ratio':condition,'at_or_below_10_local_error_scale':den<=10*floor,
            'local_error_scale':floor}

def serial(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)

def saved_clock(t):
    table=rows(SOURCE/'pilot17_populations.csv'); groups={name:[r for r in table if r['case']==name] for name in CASES}
    eta=None
    for name in CASES:
        r=groups[name];tt=np.array([float(x['elapsed_proper_s']) for x in r]);ee=np.array([float(x['eta']) for x in r]);zz=np.array([float(x['z_mean']) for x in r])
        if not np.array_equal(tt,t) or np.any(np.diff(ee)<=0):raise ValueError('saved CSV clock mismatch')
        if not np.allclose(zz,21*np.exp(-ee)-1,rtol=1e-12,atol=1e-14):raise ValueError('saved z mapping mismatch')
        if eta is not None and not np.array_equal(eta,ee):raise ValueError('case eta mismatch')
        eta=ee
    return eta,groups

def tests():
    assert np.array_equal(relative(np.array([0.,2.,-1.]),np.array([0.,1.,1.])),[0.,.5,-2.])
    r=refinement(np.array([[0.,2.]]),np.array([[0.,1.]]),np.array([2.]))
    assert np.array_equal(r['normalized'],[[0.,.5]]) and r['relative'][0,0]==0
    assert np.array_equal(r['local_error_scale'],np.maximum([[2e-11,2e-11+2e-7]],[[4e-12,4e-12+2e-8]]))
    # Nonlinear eta→z and inverse clock; rounded early z need not be strict.
    t=np.array([0.,1.,3.]);eta=np.array([0.,.2,1.]);target=.5
    tick=np.interp(target,eta,t)
    assert abs(np.interp(tick,t,eta)-target)<1e-15
    return {'status':'PASS','checks':['signed_relative_zero_handling','frozen_scale_refinement','physical_local_error_scale','eta_tick_roundtrip']}

def main():
    test=tests();cases=load_cases();t=cases['ON_refined']['t'];eta,table=saved_clock(t)
    for name,c in cases.items():
        values=np.array([[float(row['per_Href__'+label]) for row in table[name]] for label in LABELS])
        if not np.array_equal(values,c['physical'][:17]):raise ValueError('CSV/NPZ populations differ '+name)
    z=21*np.exp(-eta)-1;myr=t/31557600000000
    knots=rows(SOURCE/'source_history_qss.csv');kt=np.array([float(r['elapsed_proper_s']) for r in knots])
    if not np.isin(kt,t).all():raise ValueError('missing clock knots')
    ticks_z=[20.,15.,10.,8.,6.,4.,3.,2.]
    ticks=[{'z':zz,'t_myr':float(np.interp(np.log(21/(1+zz)),eta,t)/31557600000000)} for zz in ticks_z]
    for tick in ticks:
        back=21*np.exp(-np.interp(tick['t_myr']*31557600000000,t,eta))-1
        if not np.isclose(back,tick['z'],rtol=1e-12,atol=1e-12):raise ValueError('clock tick roundtrip')
    b=cases['ON_base']['physical'][:17];r=cases['ON_refined']['physical'][:17];o=cases['OFF_base']['physical'][:17];sc=cases['ON_refined']['scales'][:17]
    refine=refinement(b,r,sc);delta=b-o
    peaks=np.maximum.reduce([c['physical'][:17].max(axis=1) for c in cases.values()])
    bands=[('peak ≥ 1e-3',peaks>=1e-3),('1e-6 ≤ peak < 1e-3',(peaks>=1e-6)&(peaks<1e-3)),('1e-12 ≤ peak < 1e-6',(peaks>=1e-12)&(peaks<1e-6)),('1e-16 ≤ peak < 1e-12',(peaks>=1e-16)&(peaks<1e-12)),('peak < 1e-16',peaks<1e-16)]
    groups=[{'name':name,'indices':np.flatnonzero(mask).tolist()} for name,mask in bands if mask.any()]
    if sorted(i for g in groups for i in g['indices'])!=list(range(17)):raise ValueError('group coverage')
    threshold=1.0820350005000101e-8
    summary={'status':'SAVED_ARRAY_DIAGNOSTICS_COMPLETE','scientific_admission':'PENDING_ASTRA','sample_count':len(t),'ivp_calls':0,
        'new_physical_samples':0,'tests':test,'endpoint_s':float(t[-1]),'species':{},'cases':{},'grouping':groups,
        'refinement_threshold':1e-5,'balance_absolute_threshold':threshold,'clock_knots':len(kt)}
    for name,c in cases.items():
        summary['cases'][name]={'minimum_scaled_stock':float((c['physical'][:21]/c['scales'][:21,None]).min()),
           'max_baryon_residual':float(abs(c['baryon_residual']).max()),'max_charge_residual':float(abs(c['charge_residual']).max()),
           'baryon_pass':bool(np.max(abs(c['baryon_residual']))<=threshold),'charge_pass':bool(np.max(abs(c['charge_residual']))<=threshold)}
    for i,label in enumerate(LABELS):
        summary['species'][label]={'peak':float(peaks[i]),'maximum_normalized_refinement':float(refine['normalized'][i].max()),
            'maximum_relative_refinement':float(refine['relative'][i].max()),'max_conditioning_ratio':float(refine['conditioning_ratio'][i].max()),
            'count_at_or_below_10_local_error_scale':int(refine['at_or_below_10_local_error_scale'][i].sum()),
            'on_off_min':float(delta[i].min()),'on_off_max':float(delta[i].max())}
    summary['refinement_pass']=bool(refine['normalized'].max()<=1e-5)
    data={'labels':LABELS,'families':[{'name':n,'indices':ii} for n,ii in FAMILIES],
         't_s':t,'t_myr':myr,'eta':eta,'z':z,'upper_ticks':ticks,'cases':cases,'groups':groups,'peaks':peaks,
         'delta_on_off':delta,'delta_on_off_normalized':delta/sc[:,None],'delta_on_off_relative':relative(b,o),
         'delta_refined_base':r-b,'signed_refinement':(b-r)/sc[:,None],'normalized_refinement':refine['normalized'],
         'relative_refinement':refine['relative'],'local_error_scale':refine['local_error_scale'],
         'conditioning_ratio':refine['conditioning_ratio'],'conservation_threshold':threshold,
         'conservation_normalized':{name:{key:c[key]/threshold for key in ('baryon_residual','charge_residual')} for name,c in cases.items()},'metrics':summary}
    extra_diagnostics(data,summary,knots)
    OUT.mkdir(exist_ok=True)
    (OUT/'plot_data.json').write_text(json.dumps(data,default=serial,allow_nan=False,separators=(',',':'))+'\n')
    (OUT/'DIAGNOSTICS.json').write_text(json.dumps(summary,default=serial,allow_nan=False,indent=2)+'\n')
    with (OUT/'signed_differences.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['elapsed_proper_s','state','ON_base_minus_OFF_base','ON_base_minus_ON_refined_over_scale','absolute_relative_refinement','local_error_scale','conditioning_ratio'])
        for k,tt in enumerate(t):
            for i,label in enumerate(LABELS):writer.writerow([tt,label,delta[i,k],(b[i,k]-r[i,k])/sc[i],refine['relative'][i,k],refine['local_error_scale'][i,k],data['conditioning_ratio'][i][k]])
    with (OUT/'raw_saved_arrays.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['case','elapsed_proper_s','elapsed_Myr','eta','z_mean',*LABELS,'Bn','BT','Un_eV','UT_eV','baryon_ledger','electron_ledger','baryon_residual','charge_residual'])
        for name,c in cases.items():
            for k,tt in enumerate(t):writer.writerow([name,tt,myr[k],eta[k],z[k],*c['physical'][:,k],c['baryon_residual'][k],c['charge_residual'][k]])
    print(json.dumps(summary,default=serial,allow_nan=False,indent=2))

def extra_diagnostics(data,summary,knots):
    import sys
    sys.path.insert(0,str(ROOT/'rei_source_history_20261028'/'implementation'))
    from coupled import Coupled,old,old_bath,compile_new
    # Reuse saved clock: no clock quadrature, QSS envelope or IVP setup.
    be,bz,by,bhidden,bnref=old.load_baseline()
    with np.load(old.NPZ_PATH,allow_pickle=False) as saved: bh=saved['H'].copy()
    kt=np.array([float(row['elapsed_proper_s']) for row in knots])
    model=Coupled.__new__(Coupled)
    model.data={'eta':be,'z':bz,'y':by,'hidden':bhidden,'nref':bnref,'H':bh,'t':kt}
    model.c=old.config();model.t=kt
    model.photo,model.rec,model.edges,model.bath_metadata=old_bath(model.data)
    model.new={mode:compile_new(model.c,mode) for mode in ('OFF','ON')}
    model.initial_baryon=float(A@by[0]+6*bhidden[0].sum())
    model.initial_charge=float(Q@by[0]+np.arange(4)@bhidden[0])
    c=model.c;t=np.asarray(data['t_s'])
    hidden=np.array([np.interp(t,kt,model.data['hidden'][:,j]) for j in range(4)])
    data['delta_refined_off']=data['cases']['ON_refined']['physical'][:17]-data['cases']['OFF_base']['physical'][:17]
    data['delta_refined_off_normalized']=data['delta_refined_off']/data['cases']['ON_refined']['scales'][:17,None]
    data['delta_refined_off_relative']=relative(data['cases']['ON_refined']['physical'][:17],data['cases']['OFF_base']['physical'][:17])
    data['thermal_diagnostics']={};summary['thermal_diagnostics']={};summary['neutral_minima']={};summary['li_chatter']={}
    for name,d in data['cases'].items():
        p=d['physical'];B=A@p[:17]+p[17]+3*p[18]+6*hidden.sum(axis=0);Qh=Q@p[:17]+p[18]+np.arange(4)@hidden
        rb=B+p[21]-model.initial_baryon;rq=Qh-p[22]-model.initial_charge
        d['total_baryons']=B;d['recomputed_baryon_residual']=rb;d['recomputed_charge_residual']=rq
        summary['cases'][name]['recomputed_baryon_pass']=bool(abs(rb).max()<=data['conservation_threshold'])
        summary['cases'][name]['recomputed_charge_pass']=bool(abs(rq).max()<=data['conservation_threshold'])
        summary['cases'][name]['scaled_positivity_pass']=bool((p[:21]/d['scales'][:21,None]).min()>=-1e-9)
        summary['cases'][name].update(recomputed_baryon_max=float(abs(rb).max()),recomputed_charge_max=float(abs(rq).max()),saved_baryon_discrepancy=float(abs(rb-d['baryon_residual']).max()),saved_charge_discrepancy=float(abs(rq-d['charge_residual']).max()),inventory_initial=float(B[0]),inventory_final=float(B[-1]))
        alpha=0 if name=='OFF_base' else 1;mode='OFF' if alpha==0 else 'ON';escape=c['kesc_s'] if alpha else 0
        nref=np.exp(np.interp(t,kt,np.log(model.data['nref'])))
        capture=nref*c['capture_C_cm3_s']*(p[1]+p[2])
        data['thermal_diagnostics'][name]={};summary['thermal_diagnostics'][name]={}
        for fam,index,fast,I,L in [('n',0,17,c['thermal_injection_per_Href_s'][0],c['lambda_n_s']+escape+capture),('T',5,18,sum(c['thermal_injection_per_Href_s'][5:7]),np.full(len(t),c['lambda_T_s']+escape))]:
            X=p[index] if fam=='n' else p[5]+p[6];P=alpha*I+c['ks_'+fam+'_s']*p[fast];fixed=P/L;F=P-L*X
            den=np.maximum(P,L*abs(X));station=np.divide(abs(F),den,out=np.zeros_like(F),where=den!=0)
            track=np.divide(abs(X-fixed),fixed,out=np.zeros_like(F),where=fixed>0)
            passed=(P>0)&(station<=.01)&(track<=.01);bad=np.flatnonzero(~passed);first_after=int(bad[-1]+1) if len(bad) and bad[-1]+1<len(t) else (0 if not len(bad) else None)
            driftden=np.maximum(P[:-1],P[1:]);drift=np.divide(abs(np.diff(P)/np.diff(t)),driftden,out=np.full(len(t)-1,np.nan),where=driftden>0)
            Sj=np.array([old.reservoirs(p[:17,k],alpha,c)['S'][0 if fam=='n' else 1] for k in range(len(t))])
            fast_loss=c['ks_'+fam+'_s']+(c['ke_'+fam+'_s'] if alpha else 0)+c['lambda_'+fam+'_s']/c['gamma_'+fam]
            fast_rhs=Sj-fast_loss*p[fast]
            retained_rhs=F+fast_rhs
            entry={'fast_production':Sj,'fast_rhs':fast_rhs,'retained_total':X+p[fast],'retained_total_rhs':retained_rhs,'relaxation_time_s':1/L,'capture_time_s':[None if vv==0 else float(1/vv) for vv in capture] if fam=='n' else None,'production':P,'loss_rate':L,'fixed_point':fixed,'rhs':F,'stationarity':station,'tracking':[None if P[k]<=0 else float(track[k]) for k in range(len(t))],'tracking_defined':P>0,'sample_pass':passed,'zero_stock_trivial':(P==0)&(X==0),'source_drift_interval':[None if not np.isfinite(v) else float(v) for v in drift],'tau_times_drift_interval':[None if not np.isfinite(v) else float(v/L[k]) for k,v in enumerate(drift)]}
            data['thermal_diagnostics'][name][fam]=entry
            point_errors=[]
            for check_k in sorted(set((0,1,len(t)//2,len(t)-1))):
                full_rhs=model.rhs_physical(t[check_k],p[:,check_k],mode)
                observed=full_rhs[0] if fam=='n' else full_rhs[5]+full_rhs[6]
                difference=abs(float(F[check_k]-observed))
                magnitude=max(abs(float(F[check_k])),abs(float(observed)),float(P[check_k]),float(L[check_k]*abs(X[check_k])))
                passed_point=difference<=1e-12*magnitude if magnitude>0 else difference==0
                point_errors.append({'index':check_k,'difference':difference,'scale':magnitude,'pass':bool(passed_point)})
            entry['frozen_operator_point_identity']=point_errors
            summary['thermal_diagnostics'][name][fam]={'passing_samples':int(passed.sum()),'zero_stock_trivial_samples':int(np.count_nonzero((P==0)&(X==0))),'first_failure_index':None if not len(bad) else int(bad[0]),'last_failure_index':None if not len(bad) else int(bad[-1]),'earliest_subsequently_all_passing_s':None if first_after is None else float(t[first_after]),'maximum_stationarity':float(station.max()),'maximum_tracking':float(track[P>0].max()) if np.any(P>0) else None,'tracking_defined_samples':int(np.count_nonzero(P>0)),'frozen_operator_point_identity':point_errors,'point_identity_pass':all(point['pass'] for point in point_errors)}
        positive=np.flatnonzero(t>0);v=p[13];slopes=np.diff(v[positive])/np.diff(np.log10(t[positive]));nonzero=np.flatnonzero(slopes!=0);ext=[]
        for a,b in zip(nonzero[:-1],nonzero[1:]):
            if slopes[a]*slopes[b]<0:
                k=int(positive[a+1]);ext.append({'index':k,'t_s':float(t[k]),'value':float(v[k]),'left_log_spacing':float(np.log10(t[k]/t[k-1])) if k>1 else None,'right_log_spacing':float(np.log10(t[k+1]/t[k])) if k+1<len(t) else None})
        summary['li_chatter'][name]={'sign_reversals':len(ext),'extrema':ext}
        minima=[]
        for index in (1,3,5,7,10,13):
            found=np.flatnonzero((p[index,1:-1]<p[index,:-2])&(p[index,1:-1]<=p[index,2:]))+1
            found=[int(k) for k in found if 1e12<=t[k]<=1e16]
            for k in found:
                j=int(np.argmin(abs(kt-t[k])));width=kt[min(j+1,len(kt)-1)]-kt[max(j-1,0)]
                lhs=None if j==0 else {'photo':((model.photo[j]-model.photo[j-1])/(kt[j]-kt[j-1])).tolist(),'rec':((model.rec[j]-model.rec[j-1])/(kt[j]-kt[j-1])).tolist()}
                rhs=None if j==len(kt)-1 else {'photo':((model.photo[j+1]-model.photo[j])/(kt[j+1]-kt[j])).tolist(),'rec':((model.rec[j+1]-model.rec[j])/(kt[j+1]-kt[j])).tolist()}
                minima.append({'state':LABELS[index],'index':k,'t_s':float(t[k]),'value':float(p[index,k]),'nearest_knot_index':j,'offset_s':float(t[k]-kt[j]),'offset_over_neighbor_width':float(abs(t[k]-kt[j])/width),'left_hazard_slopes':lhs,'right_hazard_slopes':rhs,'local_rhs':float(model.rhs_physical(t[k],p[:,k],mode)[index]),'flanks':[float(p[index,k-1]),float(p[index,k+1])]})
        summary['neutral_minima'][name]={'status':'MINIMA_FOUND' if minima else 'NO_SAVED_MINIMUM','minima':minima}
    base_ext=summary['li_chatter']['ON_base']['extrema'];ref_ext=summary['li_chatter']['ON_refined']['extrema']
    for ext in base_ext:
        i=ext['index'];ext['persists_refined_within_one_index']=any(abs(i-r['index'])<=1 for r in ref_ext);ext['local_error_scale']=float(data['local_error_scale'][13,i]);ext['conditioning_ratio']=float(data['conditioning_ratio'][13,i])
    summary['rate_scales']={}
    for fam in ('n','T'):
        lam=c['lambda_'+fam+'_s'];ks=c['ks_'+fam+'_s'];ke=c['ke_'+fam+'_s'];loss=ks+ke+lam/c['gamma_'+fam]
        summary['rate_scales'][fam]={'beta_lifetime_s':1/lam,'fast_slowing_s':1/ks,'fast_escape_s':1/ke,'thermal_escape_s':1/c['kesc_s'],'fast_total_loss_s':1/loss,'branch_slowing':ks/loss,'branch_escape':ke/loss,'branch_beta':lam/c['gamma_'+fam]/loss}
    # JSON represents undefined conditioning ratios explicitly, never as zero.
    base=data['cases']['ON_base']['physical'][:17];ref=data['cases']['ON_refined']['physical'][:17];den=np.maximum(abs(base),abs(ref))
    ratio=data['conditioning_ratio'];data['conditioning_zero_mask']=den==0
    data['conditioning_ratio']=[[None if den[i,k]==0 else float(ratio[i,k]) for k in range(len(t))] for i in range(17)]
    for i,label in enumerate(LABELS):
        mask=den[i]>10*data['local_error_scale'][i];summary['species'][label]['maximum_relative_refinement_well_conditioned']=float(data['relative_refinement'][i,mask].max()) if mask.any() else None
        summary['species'][label]['undefined_conditioning_samples']=int((den[i]==0).sum())
        summary['species'][label]['max_conditioning_ratio_defined']=float(ratio[i,den[i]>0].max()) if np.any(den[i]>0) else None
        summary['species'][label]['max_conditioning_ratio']=None if np.any(den[i]==0) else float(ratio[i].max())

if __name__=='__main__':main()
