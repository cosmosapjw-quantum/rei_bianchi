#!/usr/bin/env python3
"""Independent arithmetic over new Q1A artifacts; zero ODE/native calls."""
from pathlib import Path
import argparse, datetime, hashlib, json
import numpy as np

FIELDS = ['xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','GammaHI_s','GammaHeI_s','GammaHeII_s']
MOMENTS = ['source_number_ref_cm3_s','source_energy_ref_erg_cm3_s','source_number_proper_cm3_s',
 'source_energy_proper_erg_cm3_s','cumulative_source_number_ref_cm3','cumulative_source_energy_ref_erg_cm3',
 'radiation_energy_ref_erg_cm3','radiation_energy_proper_erg_cm3','photoheat_HI_per_absorber_erg_s',
 'photoheat_HeI_per_absorber_erg_s','photoheat_HeII_per_absorber_erg_s','photoheat_HI_proper_erg_cm3_s',
 'photoheat_HeI_proper_erg_cm3_s','photoheat_HeII_proper_erg_cm3_s','total_photoheat_proper_erg_cm3_s']
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def inspect_run(path):
    result=read(path/'RESULT.json'); identity=read(path/'IDENTITY.json'); grid=read(path/'GRID.json')
    events=read(path/'EVENTS.json')
    with np.load(path/'history.npz') as a:
        u=a['u']; states=a['scaled_states']*a['scales']; q=a['q']; mu=a['mu']; weights=a['weights']
    n=len(q); rows=result['history']; checks={}
    checks['complete']=result['status']=='COMPUTED_NOT_REVIEWED' and result['failure'] is None
    checks['segments_complete']=result['completed_segments']==identity['segment_count']==len(events['boundaries'])-1
    checks['saved_shape']=states.shape==(129,n+10)
    checks['epoch_grid']=np.array_equal(u,np.linspace(0,1,129)) and len(rows)==129
    checks['z_endpoints']=abs(rows[0]['z']-15.9)<4e-15 and abs(rows[-1]['z']-4)<2e-15
    checks['finite']=bool(np.isfinite(states).all())
    checks['strict_photon_positive']=bool((states[:,4:4+n]>=0).all())
    checks['fractions_domain']=bool((states[:,0]>=0).all() and (states[:,0]<=1).all()
                                  and (states[:,1:3]>=0).all() and (states[:,1:3].sum(axis=1)<=1).all())
    checks['gas_json_exact']=all(np.array_equal(states[:,i],[r[k] for r in rows])
                                for i,k in enumerate(FIELDS[:3]))
    fhe=.24/(4*.76)
    temperature=2*states[:,3]*1.602176634e-12/(3*1.380649e-16*(1+fhe+states[:,0]+fhe*(states[:,1]+2*states[:,2])))
    checks['temperature_domain']=bool((temperature>=1).all() and (temperature<=1e6).all())
    temp_relative=float(np.max(np.abs(temperature-[r['T_K'] for r in rows]))/np.max(temperature))
    checks['temperature_agreement']=temp_relative<2e-14
    checks['grid_arrays_exact']=all(np.array_equal(x,grid[k]) for x,k in [(q,'q_eV'),(mu,'mu0'),(weights,'weights')])
    hh=hashlib.sha256()
    for arr in [q,mu,weights]:hh.update(np.asarray(arr,dtype='<f8').tobytes())
    checks['grid_hash']=hh.hexdigest()==grid['arrays_sha256']==identity['grid_arrays_sha256']
    checks['positive_weights']=bool((weights>0).all())
    checks['dormant_initial_empty']=bool((states[0,4:4+n][q>50000]==0).all())
    checks['accepted_instrumentation']=all(result['checks'][k] for k in ['accepted_positive','accepted_finite','accepted_gas_domain'])
    checks['one_sided_energy']=result['max_one_sided_relative_energy_shift']<=64*np.finfo(float).eps
    root=Path(__file__).resolve().parents[2]
    checks['actual_native_identity']=sha(root/'n1/native/target/release/rei_n1_native')==identity['native_sha']
    checks['actual_n1_identity']=sha(root/'n1/provider.py')==identity['n1_sha']
    checks['FLRW_locked']=identity['args']['shear']==grid['construction']['r']==0.0
    moments=read(path/'MOMENTS.json');geometry=moments['geometry_preflight']
    geomfile=path/geometry['relative_path']; pre=read(geomfile)
    bound=[r for r in pre['grids'].values() if r['grid_arrays_sha256']==identity['grid_arrays_sha256']]
    checks['geometry_evidence']=sha(geomfile)==geometry['sha256'] and len(bound)==1 and bound[0]['grid_sha256']==identity['grid_sha'] and bound[0]['geometry_max']<=1e-11 and geometry['passed'] is True
    for name,key in [('driver_as_run.py','driver_sha'),('base_driver_as_run.py','base_sha'),
                     ('fixed_grid_as_run.py','grid_factory_sha'),('GRID.json','grid_sha'),
                     ('characteristics_as_run.py','characteristics_sha'),('events_as_run.py','events_sha')]:
        checks['identity_'+name]=sha(path/name)==identity[key]
    energy=max(result['max_endpoint_energy_ledger'],max(abs(r['energy_ledger_scaled']) for r in rows))
    number=max(result['max_endpoint_number_ledger'],max(abs(r['number_ledger_scaled']) for r in rows))
    checks['energy_aggregation']=energy==result['max_energy_ledger']; checks['number_aggregation']=number==result['max_number_ledger']
    checks['energy_gate']=energy<=1e-9;checks['number_gate']=number<=1e-9
    checks={key:bool(value) for key,value in checks.items()}
    # Independent FLRW saved-state ledger arithmetic, no provider or native call.
    h0=70*1e5/3.0856775814913673e24
    rhob=.045*3*h0*h0/(8*np.pi*6.67430e-8);vi=(1/16.9)**3
    nh0=.76*rhob/1.67262192369e-24/vi; nhe0=.24*rhob/(4*1.67262192369e-24)/vi
    arel=16.9/(1+np.array([r['z'] for r in rows]))
    photons=states[:,4:4+n];counts=np.sum(photons*arel[:,None]/q[None,:],axis=1)
    counters=states[:,4+n:];chi=np.array([13.598434599702,24.587389011,54.41776])
    total=1.602176634e-12*(nh0*states[:,3]+nh0*states[:,0]*chi[0]+nhe0*(states[:,1]*chi[1]+states[:,2]*(chi[1]+chi[2]))+photons.sum(axis=1))
    independent_energy=(total+counters[:,0]+counters[:,1]-counters[:,2]-counters[:,5]-total[0])/total[0]
    independent_number=(counts+counters[:,3]-counters[:,4]-counts[0])/nh0
    arithmetic=dict(energy_sample_max=float(max(abs(independent_energy))),number_sample_max=float(max(abs(independent_number))),
        energy_sample_report_difference=float(max(abs(independent_energy-[r['energy_ledger_scaled'] for r in rows]))),
        number_sample_report_difference=float(max(abs(independent_number-[r['number_ledger_scaled'] for r in rows]))),
        note='Independent array summation and FLRW a_rel from saved redshift; roundoff/order may differ from serial native-driver reporting. Segment-endpoint maxima use recorded evidence.')
    return dict(run=path.name,checks=checks,all_checks=all(checks.values()),energy_max=energy,number_max=number,
                temperature_relative_disagreement=temp_relative,independent_saved_ledger_arithmetic=arithmetic,identities={x:sha(path/x) for x in
                ['RESULT.json','IDENTITY.json','GRID.json','history.npz','EVENTS.json']})

def compare(left,right,kind):
    a,b=read(left/'RESULT.json'),read(right/'RESULT.json')
    ai,bi=read(left/'IDENTITY.json'),read(right/'IDENTITY.json')
    am,bm=read(left/'MOMENTS.json'),read(right/'MOMENTS.json')
    checks={'epochs_identical':[r['time_s'] for r in a['history']]==[r['time_s'] for r in b['history']]}
    for key in ['base_sha','driver_sha','events_sha','characteristics_sha','grid_factory_sha','n1_sha','native_sha','input_identity','semantics']:
        checks['same_'+key]=ai[key]==bi[key]
    for key in ['angle','shear','max_step']:
        checks['same_'+key]=ai['args'][key]==bi['args'][key]
    checks['correct_discretization_change']=(ai['grid_sha']==bi['grid_sha'] and ai['args']['rtol']>bi['args']['rtol']) if kind=='temporal' else (ai['grid_sha']!=bi['grid_sha'] and ai['args']['rtol']==bi['args']['rtol'])
    target=2e-6 if kind=='temporal' else 1e-3
    sets={}
    for count,ii in [('129',np.arange(129)),('65',np.arange(0,129,2))]:
        metrics={}
        for key in FIELDS+MOMENTS:
            l,r=(a,b) if key in FIELDS else (am,bm)
            av=np.asarray([row[key] for row in l['history']])[ii]
            bv=np.asarray([row[key] for row in r['history']])[ii]
            amplitude=float(np.max(np.abs(bv)));delta=np.abs(av-bv);imax=int(np.argmax(delta));error=float(delta[imax]/amplitude if amplitude else delta[imax])
            metrics[key]=dict(scaled_error=error,amplitude=amplitude,worst_epoch_index=int(ii[imax]),finite=bool(np.isfinite(np.r_[av,bv]).all()),
                              pass_target=error<=target if amplitude else float(delta[imax])==0,
                              formal_gate=(kind=='spectral' or key in FIELDS))
        formal=[v for v in metrics.values() if v['formal_gate']]
        sets[count]=dict(fields=metrics,formal_max=max(v['scaled_error'] for v in formal),
                        formal_pass=all(v['finite'] and v['pass_target'] for v in formal),
                        formal_failed_count=sum(not (v['finite'] and v['pass_target']) for v in formal))
    return dict(kind=kind,target=target,identity_checks=checks,identity_pass=all(checks.values()),selections=sets,
                fields_and_pair_identity_pass=all(checks.values()) and all(v['formal_pass'] for v in sets.values()),
                combined_run_admission='NOT_DECIDED_BY_FIELD_COMPARISON; requires each run checks')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--coarse',type=Path,required=True)
    parser.add_argument('--fine',type=Path,required=True);parser.add_argument('--time-fine',type=Path)
    parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    paths=[a.coarse,a.fine]+([a.time_fine] if a.time_fine else [])
    result=dict(schema='q1a_independent_saved_arithmetic_v1',timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                reviewer='/root/q1a_independent',model_identity='UNKNOWN',ODE_calls=0,native_calls=0,old_replays=0,
                runs=[inspect_run(p) for p in paths],spectral=compare(a.coarse,a.fine,'spectral'))
    if a.time_fine:result['temporal']=compare(a.coarse,a.time_fine,'temporal')
    result['combined_spectral_admission']=all(r['all_checks'] for r in result['runs'][:2]) and result['spectral']['fields_and_pair_identity_pass']
    if a.time_fine:
        result['combined_temporal_admission']=result['runs'][0]['all_checks'] and result['runs'][2]['all_checks'] and result['temporal']['fields_and_pair_identity_pass']
    result['code_sha256']=sha(Path(__file__))
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['runs','spectral','temporal']},indent=2))
if __name__=='__main__':main()
