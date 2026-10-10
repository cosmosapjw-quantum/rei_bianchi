"""New-grid checks; reuse saved Q0 exact references, never replay Q0/old ODEs."""
from pathlib import Path
import hashlib,importlib.util,json,sys
import numpy as np
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
sys.path.insert(0,str(BASE/'n2'))
import characteristics
from fixed_grid import FixedCharacteristics

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

out=HERE/'evidence/PREFLIGHT.json'
if out.exists():raise FileExistsError(out)
n1=load('q1a_preflight_n1',BASE/'n1/provider.py')
base=load('q1a_preflight_base',BASE/'integration/run_native_history.py')
provider=n1.HistoryProvider(0.)
ref=json.loads((BASE/'recovery/Q0_SOURCE_ATTRIBUTION.json').read_text())
rows=ref['exact_source_history']
icref=ref['runs']['EVENT_COUPLED003_RECOVERED']['initial_UVB_moment_comparison']
records={}
for order in [1,2]:
    file=HERE/f'GRID_G{order}.json';ch=FixedCharacteristics(file,characteristics)
    q,mu,w=ch.make_grid(ch.record['n_energy'],2,provider.q_max_eV)
    native=n1.Native(BASE/'n1/native/target/release/rei_n1_native')
    try:
        p=base.Coupled(provider,native,ch,ch.record['n_energy'],2)
        consumed=all(np.array_equal(a,b) for a,b in zip((q,mu,w),(p.q,p.mu,p.weights)))
        initial=provider.initial_photons(q,w)
        ic={}
        for key,power,factor in [('full_number',0,1.),('full_energy',1,base.EV)]:
            exact=icref[key]['exact_declared_interpolation'];val=float(np.dot(initial,q**power)*factor)
            ic[key]=dict(value=val,exact=exact,signed_relative=(val-exact)/exact)
        geommax=0.;sources=[]
        for row in rows:
            g=provider.geometry(row['time_s']);e,m,ratio=ch.geometry_nodes(q,mu,g)
            geommax=max(geommax,float(np.max(abs(e*g['a_rel']/q-1))),float(np.max(abs(m-mu))))
            # Each energy node has the same two normalized Gauss angular weights.
            wr=w.reshape(-1,2);wm=wr/wr.sum(axis=1)[:,None]
            ratio2=ratio.reshape(-1,2)
            geommax=max(geommax,float(np.max(abs(np.sum(wm/ratio2**3,axis=1)/g['a_rel']**3-1))))
            source=ch.source_reference(q,mu,w,g,provider.tables['emissivity'])
            sources.append([float(source.sum()),float(base.EV*np.dot(source,e))])
        exact=np.array([[r['full_number_ref'],r['full_energy_ref']] for r in rows])
        discrepancy=np.max(abs(np.array(sources)-exact),axis=0)/np.max(abs(exact),axis=0)
        v=p.y0/p.scales;J=p.jac(0.,v);f=p.rhs(0.,v);checks=[]
        chosen=[]
        for energy in [15.,30.,70.,200.]:
            chosen.append(4+int(np.argmin(abs(q-energy))))
        for col in chosen:
            errs=[]
            for delta in [1e-3,1e-4,1e-5]:
                vv=v.copy();vv[col]+=delta
                fd=(p.rhs(0.,vv)-f)/delta;j=J[:,col].toarray().ravel()
                errs.append(float(np.linalg.norm(fd-j,np.inf)/max(np.linalg.norm(j,np.inf),np.finfo(float).tiny)))
            checks.append(dict(column=col,q_eV=float(q[col-4]),deltas=[1e-3,1e-4,1e-5],relative_errors=errs,pass_check=min(errs)<1e-5))
        gates=dict(exact_grid_consumed=consumed,immutable=all(not a.flags.writeable for a in (p.q,p.mu,p.weights)),
                   positive_weights=bool(np.all(w>0)),geometry=geommax<=1e-11,
                   dormant_IC_exact_zero=bool(np.all(initial[q>50000.]==0)),
                   IC_number_declared_interpolation=abs(ic['full_number']['signed_relative'])<1e-12,
                   new_grid_photon_Jacobian=all(c['pass_check'] for c in checks),
                   local_native_number=p.max_local_number<1e-12,local_native_energy=p.max_local_energy<1e-12)
        gates={key: bool(value) for key,value in gates.items()}
        records[f'G{order}']=dict(grid_sha256=sha(file),grid_arrays_sha256=ch.record['arrays_sha256'],
            n_energy=ch.record['n_energy'],n_nodes=p.n,gates=gates,geometry_max=geommax,IC=ic,
            source_reference_number_scaled=float(discrepancy[0]),source_reference_energy_scaled=float(discrepancy[1]),
            source_profile_status='DIAGNOSTIC_NEW_GRID; does not replace full coupled spectral test',
            photon_Jacobian=checks,local_native_number=p.max_local_number,local_native_energy=p.max_local_energy)
    finally:native.close()
result=dict(schema='rei.q1a.preflight.v1',status='PASS' if all(all(r['gates'].values()) for r in records.values()) else 'FAIL',
    old_science_replays=0,ODE_calls=0,new_grid_native_point_calls=True,
    oracle='Saved independently checked Q0 references reused; no source-reference re-integration',
    Q0_reference_sha256=sha(BASE/'recovery/Q0_SOURCE_ATTRIBUTION.json'),implementation_sha256=sha(__file__),
    grid_factory_sha256=sha(HERE/'fixed_grid.py'),base_sha256=sha(BASE/'integration/run_native_history.py'),
    native_sha256=sha(BASE/'n1/native/target/release/rei_n1_native'),grids=records)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['status']=='PASS' else 1)
