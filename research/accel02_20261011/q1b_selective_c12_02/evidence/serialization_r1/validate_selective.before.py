"""One prescribed selective cell12 reconstruction-opacity validation."""
import argparse, ast, hashlib, importlib.util, json, math, platform, sys, time, traceback
from pathlib import Path
import numpy as np
from reconstruction_selective import Reconstruction, nodes, kernels, accounting, CHI, THRESHOLDS
RESULT={'unit':'Q1B_SELECTIVE_C12_02','failures':[],
'execution':dict.fromkeys(['native_process','SIGMA','SIGMA_energies','RATES','RHS','JAC','ODE','build','history_replay'],0),
'retained_holds':{'Q1A_number_ledger':'FAIL','Q1A_spectral_pair':'FAIL','original_candidate_reconstruction':'HOLD_INITIAL_UVB_RECONSTRUCTION_ACCURACY','global_admission':'HOLD'},
'harness':'HARNESS_UNAVAILABLE','requested_execution_model':'gpt-6.1-sol','requested_effort':'medium','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED'}
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def check(condition,outcome,detail):
    if not condition:
        RESULT['failures'].append({'outcome':outcome,'detail':detail})
        raise ValueError(outcome)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def array_sha(e):return hashlib.sha256(np.asarray(e,dtype='<f8').tobytes()).hexdigest()
def endpoint_fixtures():
    rows=[]
    for atom in (10.,20.):
        rec=Reconstruction(10.,20.,.25,1.,.25*atom)
        for threshold in (np.nextafter(.25*atom,-np.inf),.25*atom,np.nextafter(.25*atom,np.inf)):
            q,w=nodes(rec,32,float(threshold));active=threshold<=.25*atom
            check((q.tolist()==[atom] and w.tolist()==[1.]) if active else len(q)==len(w)==0,
                'HOLD_ENDPOINT_ATOM_IMPLEMENTATION',{'atom':atom,'threshold':float(threshold),'q':q.tolist(),'w':w.tolist()})
            rows.append({'atom':atom,'threshold':float(threshold),'threshold_hex':float(threshold).hex(),'included':active})
        for r in (0.,1.,2.,-3.):
            check(rec.oracle_moment(r,atom,atom)==atom**r,'HOLD_ENDPOINT_ATOM_IMPLEMENTATION','singleton oracle')
            check(rec.oracle_moment(r,np.nextafter(atom,np.inf),20.)==0.,
                'HOLD_ENDPOINT_ATOM_IMPLEMENTATION','outside oracle above atom')
            check(rec.oracle_moment(r,10.,np.nextafter(atom,-np.inf))==0.,
                'HOLD_ENDPOINT_ATOM_IMPLEMENTATION','outside oracle below atom')
    continuous=Reconstruction(10.,20.,.25,1.,.25*15.)
    q,w=nodes(continuous,32,5.)
    check(len(q)==len(w)==0 and continuous.oracle_moment(0.,20.,20.)==0.,
        'HOLD_ENDPOINT_ATOM_IMPLEMENTATION','continuous zero width')
    RESULT['endpoint_fixtures']=rows
def additivity(root,hm,source,original,grids):
    src=load('selective_source_helpers',root/'research/accel02_20261011/q1b_source_ic01/check_source_ic.py')
    q0=json.loads((root/'research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json').read_text())
    epochs=q0['exact_source_history'];check(len(epochs)==129,'HOLD_SOURCE_IC_ADDITIVITY','epoch count')
    tables=hm.load_hm12();records=[]
    a,b=original['candidate'][12:14];m=original['enriched'][25]
    quarter=grids['enriched'][(grids['enriched']>=a)&(grids['enriched']<=b)]
    check(len(quarter)==5,'HOLD_GRID_SCHEMA_OR_DOMAIN','cell12 quarters')
    for role,table,series in [('source',tables['emissivity'],epochs),('IC',tables['uvb'],[{'z':15.9,'a_rel':1.,'time_s':0.}])]:
        for i,e in enumerate(series):
            R=1./e['a_rel']
            saved=source['data']['candidate']['source_history'][i] if role=='source' else source['data']['candidate']['initial_UVB_moments']
            for band,threshold in src.BANDS.items():
                scaleN=abs(saved[band+'_number_ref']);scaleQ=abs(saved[band+'_energy_ref'])/src.EV/R;scaleU=abs(saved[band+'_energy_ref'])/src.EV
                scales=(scaleN,scaleQ,scaleU)
                def val(l,h):return np.asarray(src.cell_moments(table,float(l),float(h),e['z'],R,.5,float(threshold)))*2.
                parent=val(a,b);children=val(a,m)+val(m,b)
                oldchildren=np.array([val(a,m),val(m,b)])
                newchildren=np.array([val(l,h) for l,h in zip(quarter[:-1],quarter[1:])]).reshape(2,2,3).sum(axis=1)
                pairs=[('C12_to_C02',parent,children),('E24_to_E02',oldchildren[0],newchildren[0]),('E25_to_E02',oldchildren[1],newchildren[1])]
                for label,old,new in pairs:
                    dif=np.abs(old-new);scaled=[]
                    for d,s in zip(dif,scales):
                        ok=d/s<=1e-12 if s else d==0.
                        check(ok,'HOLD_SOURCE_IC_ADDITIVITY',{'role':role,'epoch':i,'band':band,'pair':label,'difference':float(d),'scale':s})
                        scaled.append(float(d/s) if s else 0.)
                    records.append({'role':role,'epoch':i,'original65':role=='source' and i%2==0,'band':band,'pair':label,
                        'before':old.tolist(),'after':new.tolist(),'global_reference_scales':scales,'scaled_errors':scaled})
    RESULT['source_IC_additivity']={'tolerance':1e-12,'scope':'affected original candidate cell12 and enriched cells24/25 only',
        'saved129_checked':129,'original65_checked':65,'IC_checked':True,'records':records}
def run(root):
    prior=root/'research/accel02_20261011/q1b_reconstruction01'
    tree=ast.parse((prior/'validate_reconstruction.py').read_text())
    pins=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in n.targets))
    extras={
      'research/accel02_20261011/q1b_reconstruction01/reconstruction.py':'cb79c56e64b45434de7b56bce966265c9633e931320a8da1eee17f517cb21425',
      'research/accel02_20261011/q1b_reconstruction01/validate_reconstruction.py':'ed54182dcfc1f4a764dc1b0108e79b6a3c40dd7b83166fa2e3bf50749ffe1934',
      'research/accel02_20261011/q1b_reconstruction01/CONTRACT.json':'f431e4e46d254e19eaf236b217d8ee1be70f6d83e365529ab58613d13180cb32',
      'research/accel02_20261011/q1b_reconstruction01/evidence/attempt1/RESULT.json':'54b9e7841e073c8f6c7571a6f9c95507a2b7f661624710a6b6d630a8f2c5fae9',
      'research/accel02_20261011/q1b_reconstruction01/evidence/attempt1/EXECUTION_RECEIPT.json':'e70ce70bf1756685d194dbf2122d6d3360b43018cd8111d11f6d74bde2cfe54b'}
    check(len(pins)==18,'HOLD_INPUT_FILE_IDENTITY','18 inherited pins')
    pins.update(extras);observed={p:digest(root/p) for p in pins};RESULT['input_sha256']=observed
    check(observed==pins,'HOLD_INPUT_FILE_IDENTITY','all inherited+prior pins')
    prior_receipt=json.loads((prior/'evidence/attempt1/EXECUTION_RECEIPT.json').read_text())
    prior_result=json.loads((prior/'evidence/attempt1/RESULT.json').read_text())
    RESULT['prior_attempt_accounting']={'receipt':prior_receipt,'native_execution':prior_result['execution'],'outcome':prior_result['outcome']}
    source=json.loads((root/'research/accel02_20261011/q1b_source_ic01/evidence/RESULT.json').read_text())
    original={n:np.asarray(source['data'][n]['edges_eV'],float) for n in ('candidate','enriched')}
    a,b=original['candidate'][12:14];m=original['enriched'][25]
    check(a==13.6 and b==15.782732264311809 and m==14.650773317290819,'HOLD_GRID_SCHEMA_OR_DOMAIN','frozen cell12')
    added=np.sqrt(np.asarray([a*m,m*b],dtype=np.float64))
    grids={'candidate':np.sort(np.r_[original['candidate'],m]),'enriched':np.sort(np.r_[original['enriched'],added])}
    check(len(grids['candidate'])==89 and len(grids['enriched'])==177,'HOLD_GRID_SCHEMA_OR_DOMAIN','89/177')
    maps={}
    for name,e in grids.items():
        check(np.isfinite(e).all() and np.all(np.diff(e)>0) and np.all(np.isin(original[name],e)) and e[0]==10. and e[-1]==168999.99999999997,
            'HOLD_GRID_SCHEMA_OR_DOMAIN',name)
        maps[name+'_to_original']=np.searchsorted(original[name],e[:-1],side='right').astype(int).tolist()
        maps[name+'_to_original']=[i-1 for i in maps[name+'_to_original']]
    parentmap=np.searchsorted(grids['candidate'],grids['enriched'][:-1],side='right')-1
    check(np.all(np.isin(grids['candidate'],grids['enriched'])) and np.all(grids['enriched'][1:]<=grids['candidate'][parentmap+1]),
        'HOLD_GRID_SCHEMA_OR_DOMAIN','E02 parent mapping')
    maps['E02_to_C02']=parentmap.tolist()
    RESULT['grids']={n:{'edges_eV':e.tolist(),'edges_hex':[float(v).hex() for v in e],
        'sha256_lef64':array_sha(e),'cells':len(e)-1} for n,e in grids.items()}
    RESULT['new_points']={'inherited_m':float(m),'inherited_m_hex':float(m).hex(),
        'sqrt_points':added.tolist(),'sqrt_points_hex':[float(v).hex() for v in added],'sqrt_points_sha256_lef64':array_sha(added)}
    RESULT['parent_maps']=maps
    endpoint_fixtures()
    # Reuse every frozen original analytic fixture with ONLY the prescribed endpoint implementation changed.
    sys.modules['reconstruction']=sys.modules['reconstruction_selective']
    prior_mod=load('selective_frozen_fixtures',prior/'validate_reconstruction.py')
    prior_mod.RESULT=RESULT
    prior_mod.fixtures(original['candidate'])
    print('ANALYTIC_ENDPOINT_FIXTURES_PASS',flush=True)
    hm=load('q1br_hm12',root/'research/physical_provider_20261010/hm12_data.py')
    additivity(root,hm,source,original,grids)
    uv=hm.load_hm12()['uvb'];recon={}
    for name,edges in grids.items():
        rows=[]
        for l,h in zip(edges[:-1],edges[1:]):
            hi=min(float(h),50000.)
            N=uv.moment(float(l),hi,15.9,power=0,proper_photons=True) if hi>l else 0.
            Q=uv.moment(float(l),hi,15.9,power=1,proper_photons=True) if hi>l else 0.
            rec=Reconstruction(float(l),float(h),1.,N,Q)
            prior_mod.relative(rec.oracle_moment(),N,1e-12,'UVB N','HOLD_RECONSTRUCTION_INVERSION')
            prior_mod.relative(rec.oracle_moment(1),Q,1e-12,'UVB Q','HOLD_RECONSTRUCTION_INVERSION')
            rows.append(rec)
        recon[name]=rows
    # Queue all SIGMA abscissae first, so cap check occurs before starting native.
    plans={};allq=[]
    for name,rows in recon.items():
        for order in (16,32):
            entries=[]
            for i,rec in enumerate(rows):
                for absorber,threshold in enumerate(THRESHOLDS):
                    q,w=nodes(rec,order,threshold)
                    start=len(allq);allq.extend(q.tolist())
                    entries.append((i,absorber,q,w,start,len(allq)))
            plans[(name,order)]=entries
    knots=uv.energies_eV
    panels=np.unique(np.r_[10.,50000.,knots[(knots>10.)&(knots<50000.)],THRESHOLDS,
                          grids['enriched'][(grids['enriched']>10.)&(grids['enriched']<50000.)],
                          grids['candidate'][(grids['candidate']>10.)&(grids['candidate']<50000.)]])
    for order in (16,32):
        x,w=np.polynomial.legendre.leggauss(order);entries=[]
        for a,b in zip(panels[:-1],panels[1:]):
            la,lb=math.log(a),math.log(b);q=np.exp((la+lb)/2+x*(lb-la)/2)
            weights=w*(lb-la)/2*uv.photon_number_log(q,15.9)
            start=len(allq);allq.extend(q.tolist());entries.append((q,weights,start,len(allq)))
        plans[('reference',order)]=entries
    # SIGMA returns all three absorbers: reuse exactly identical abscissae.
    uniqueq,inverse=np.unique(np.asarray(allq),return_inverse=True)
    RESULT['quadrature_abscissae']={'requested_entries':len(allq),'unique_SIGMA_energies':len(uniqueq)}
    check(len(uniqueq)<=65536,'HOLD_EXECUTION_RESOURCE_OR_CAP',{'SIGMA_energies':len(uniqueq)})
    native_mod=load('q1br_native_provider',root/'research/accel02_20261011/n1/provider.py')
    native=None;sigmas=[]
    try:
        native=native_mod.Native(root/'research/accel02_20261011/n1/native/target/release/rei_n1_native')
        RESULT['execution']['native_process']=1
        for start in range(0,len(uniqueq),4096):
            batch=uniqueq[start:start+4096]
            check(RESULT['execution']['SIGMA']<16,'HOLD_EXECUTION_RESOURCE_OR_CAP','SIGMA message cap')
            RESULT['execution']['SIGMA']+=1;RESULT['execution']['SIGMA_energies']+=len(batch)
            value=native.call('SIGMA',batch)
            check(len(value)==3*len(batch) and np.all(value>=0),'HOLD_NATIVE_SIGMA_EXECUTION','ABI finite nonnegative')
            sigmas.extend(value.reshape(-1,3).tolist())
        native.close();native=None
    except Exception as exc:
        if native is not None:
            native.proc.kill();native.proc.wait()
        if not str(exc).startswith('HOLD_'):
            check(False,'HOLD_NATIVE_SIGMA_EXECUTION',str(exc))
        raise
    sigma=np.asarray(sigmas)[inverse];values={}
    for (name,order),entries in plans.items():
        if name=='reference':
            K=np.zeros((len(entries),3,3))
            for i,(q,w,start,end) in enumerate(entries):
                for ab,threshold in enumerate(THRESHOLDS):
                    active=q>=threshold
                    K[i,ab]=kernels(q[active],w[active],sigma[start:end,ab][active],1.,CHI[ab])
        else:
            K=np.zeros((len(recon[name]),3,3))
            for i,ab,q,w,start,end in entries:K[i,ab]=kernels(q,w,sigma[start:end,ab],1.,CHI[ab])
        values[(name,order)]=K
    reference=values[('reference',32)].sum(axis=0)
    RESULT['metrics']={};RESULT['native_values']={f'{name}_{order}':K.tolist() for (name,order),K in values.items()}
    outcomes=[]
    for ab in range(3):
        for j,label in enumerate(('K0','K1','H')):
            key=f'{("HI","HeI","HeII")[ab]}_{label}'
            den=float(np.sum(abs(values[('reference',32)][:,ab,j])))
            metrics={'reference_quadrature':prior_mod.metric(values[('reference',16)][:,ab,j],values[('reference',32)][:,ab,j],den)}
            for name in recon:
                metrics[name+'_quadrature']=prior_mod.metric(values[(name,16)][:,ab,j],values[(name,32)][:,ab,j])
                metrics[name+'_accuracy']=prior_mod.metric([values[(name,32)][:,ab,j].sum()],[reference[ab,j]],den)
            child=np.zeros(len(recon['candidate']))
            np.add.at(child,parentmap,values[('enriched',32)][:,ab,j])
            metrics['enriched_parent']=prior_mod.metric(child,values[('candidate',32)][:,ab,j],den)
            RESULT['metrics'][key]=metrics
            for label,v in metrics.items():
                tol=1e-8 if label.endswith('quadrature') else 1e-4
                ok=v['scaled']<=tol if v['reference_L1'] else v['exact_zero']
                if not ok:
                    outcome='HOLD_REFERENCE_QUADRATURE' if label=='reference_quadrature' else (
                        'HOLD_RECONSTRUCTION_QUADRATURE' if label.endswith('quadrature') else 'HOLD_SELECTIVE_RECONSTRUCTION_ACCURACY')
                    outcomes.append({'outcome':outcome,'detail':{'where':key+' '+label,'tolerance':tol,**v}})
    RESULT['accounting']=[]
    for name in recon:
        K=values[(name,32)].sum(axis=0)
        for V in (1.,8.):
            for densities in ((0.,0.,0.),(1.,0.,2.),(1.,2.,3.)):
                row=accounting(K,1.,V,densities)
                check(row['residual_scaled']<=1e-12,'HOLD_COMMON_PHOTO_ACCOUNTING','native accounting')
                RESULT['accounting'].append({'grid':name,'V':V,'densities':densities,**row})
    # All nine metric sets and accounting are retained before making a decision.
    RESULT['failures'].extend(outcomes)
    return outcomes[0]['outcome'] if outcomes else 'PASS_SELECTIVE_RECONSTRUCTION_OPACITY_SCOPED'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    started=time.monotonic()
    try:outcome=run(args.root)
    except Exception as exc:
        traceback.print_exc();outcome=str(exc) if str(exc).startswith('HOLD_') else 'HOLD_EXECUTION_RESOURCE_OR_CAP'
        RESULT['error_type']=type(exc).__name__;RESULT['error']=str(exc)
        if not RESULT['failures']:RESULT['failures'].append({'outcome':outcome,'detail':str(exc)})
    RESULT['outcome']=outcome;RESULT['wall_s']=time.monotonic()-started
    RESULT['environment']={'python':sys.version,'numpy':np.__version__,'platform':platform.platform()}
    RESULT['implementation_sha256']={n:digest(Path(__file__).parent/n) for n in ('reconstruction_selective.py','validate_selective.py','CONTRACT.json')}
    with args.output.open('x') as f:json.dump(RESULT,f,indent=2,allow_nan=False)
    print(outcome,flush=True);sys.exit(0 if outcome.startswith('PASS_') else 1)

