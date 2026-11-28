"""Frozen 28-case canonical pilot; original solver remains byte-identical."""
import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','RAYON_NUM_THREADS'): os.environ[_name]='1'
import sys,json,hashlib,time,platform,traceback,argparse
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from lrs_boltzmann import SourceLock
from canonical_fv import CanonicalFVSpecies, CanonicalMomentumFV
import pilot as original
from coordinates import KAPPA_T
from species_stress import canonical_row
from coordinates import normalized,initial_mapping
SOURCE_IDENTITY=json.loads((ROOT/'data/source_identity.json').read_text())
FIXED=dict(mass_fraction=.1,massive_A=0.,mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3,ellmax=8,ne_source=None)
SOLVER=dict(n=101,rtol=3e-11,atol=3e-13)

class SourceBindingError(RuntimeError):
    """Reviewed source bytes differ; never silently launch replacement science."""

def verify_source_binding():
    original.verify_source_binding()
    manifest_path=ROOT/'data/split_source_manifest.json'
    try:
        manifest=json.loads(manifest_path.read_text())
        for name,expected in manifest['sha256'].items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
                raise SourceBindingError('Reviewed source binding mismatch: '+name+'; stop and review a new scientific version')
    except (OSError,ValueError,KeyError) as e:
        raise SourceBindingError('Reviewed source manifest unavailable or invalid: '+str(e)) from e

def source():
    lock=json.loads((ROOT/'vendor/REI_BACKGROUND_FAMILY_LOCK.json').read_text());c=lock['cosmology'];k=lock['clock']
    return SourceLock(c['H0_per_s'],c['Omega_m'],c['Omega_r'],c['Omega_lambda'],k['a_ref'],k['a_end'])

def case_grid():
    return [dict(case_id=f'split_s{si}_m{sm:+d}_r{sr:+d}',Sigma_F=s,Pi_m=.0003,Pi_r=(0. if sr==0 else .0006),sign_m=sm,sign_r=sr) for si,s in enumerate([0.,.03]) for sm in [-1,1] for sr in [0,-1,1]]

def split_mapping(config):
    src=source();mapping=initial_mapping(config['Sigma_F'],config['Pi_r'],config['sign_r'],src)
    M1=CanonicalMomentumFV(30.,amplitude=1.,radial_cells=24,angular_cells=12,gauss_order=3).moments(0.,0.).pi_s
    q=config['Sigma_F']/np.sqrt(6-config['Sigma_F']**2)
    Hinit=src.href*np.sqrt(1+q*q)
    Cm=KAPPA_T*np.sqrt(6)*src.rhocrit_j_m3*(src.omega_m*.1/src.aref**3)*M1/Hinit**2
    Am=config['sign_m']*config['Pi_m']/Cm
    if not -1<=Am<=2:raise ValueError('split massive amplitude outside original positivity domain')
    return mapping,dict(FIXED,massive_A=Am),dict(M1=M1,C_m=Cm,A_m=Am)

def case_identity(config):
    return hashlib.sha256(json.dumps(dict(config=config,fixed=FIXED,solver=SOLVER,sources=SOURCE_IDENTITY,coordinates='split-frobenius-v1',adapter_binding=json.loads((ROOT/'data/split_source_manifest.json').read_text())),sort_keys=True).encode()).hexdigest()

def clean(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def run_case(config):
    verify_source_binding()
    start=time.perf_counter(); result=dict(schema='he29.rei.split_canonical_case.v1',case_id=config['case_id'],identity_sha256=case_identity(config),inputs=config,fixed=FIXED,solver=SOLVER,source_identity=SOURCE_IDENTITY,environment=dict(python=sys.version,numpy=np.__version__,platform=platform.platform(),pid=os.getpid()),status='failed')
    try:
        src=source();mapping,fixed,mass_map=split_mapping(config)
        model=CanonicalFVSpecies(src,2.7255,**mapping,**fixed)
        sol,diagnostics,seconds=model.integrate(**SOLVER)
        hist=[dict(eta=float(x),a=d['a'],**canonical_row(d)) for x,d in zip(sol.t,diagnostics)]
        first=hist[0]; sigma_err=abs(first['Sigma_F']-config['Sigma_F']);pi_err=max(abs(first['v_m']-config['sign_m']*config['Pi_m']),abs(first['v_r']-config['sign_r']*config['Pi_r']))
        gates=dict(initial_mapping_abs_1e12=sigma_err<=1e-12 and pi_err<=1e-12,N0_drift_5e11=all(abs(d[k][0]-1)<=5e-11 for d in diagnostics for k in ('N_gamma','N_nu')),nonnegative_cells=all(d['massive_min_cell_population']>=0 for d in diagnostics))
        result.update(status='completed' if all(gates.values()) else 'failed',gates=gates,initial_mapping_errors=dict(Sigma_F=sigma_err,signed_v=pi_err),mapping=mapping,massive_initial_mapping=mass_map,actual_fixed=fixed,sol_t=sol.t,sol_y=sol.y,diagnostics=diagnostics,normalized_history=hist,first=first,final=hist[-1],integration_seconds=seconds,nfev=sol.nfev,constraint_note='Einstein_H2 is derived consistency, not independent Einstein certification',constraint_relative_max=max(abs(d['H']**2-d['Einstein_H2'])/d['H']**2 for d in diagnostics))
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    result['wall_seconds']=time.perf_counter()-start
    return clean(result)

def completed_result(config,path):
    verify_source_binding()
    try:
        d=json.loads(Path(path).read_text())
        return d['status']=='completed' and d['identity_sha256']==case_identity(config) and all(d['gates'].values()) and len(d['sol_t'])==101 and len(d['sol_y'])==40 and all(len(row)==101 for row in d['sol_y']) and len(d['diagnostics'])==101 and len(d['normalized_history'])==101
    except (OSError,ValueError,KeyError,TypeError):return False

def write_case(config,results_dir=None):
    directory=Path(results_dir or ROOT/'data/results/split_cases');directory.mkdir(parents=True,exist_ok=True);path=directory/(config['case_id']+'.json')
    if completed_result(config,path):
        result=json.loads(path.read_text());result['reused']=True;return result
    if path.exists():
        attempts=directory/'attempts';attempts.mkdir(exist_ok=True)
        number=1
        while True:
            archive=attempts/(config['case_id']+f'.attempt_{number:04d}.json')
            try:
                with archive.open('xb') as f:f.write(path.read_bytes())
                break
            except FileExistsError:number+=1
    result=run_case(config);tmp=path.with_suffix(f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');os.replace(tmp,path);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case-id',required=True);p.add_argument('--results-dir');a=p.parse_args();config=next(c for c in case_grid() if c['case_id']==a.case_id);r=write_case(config,a.results_dir);print(json.dumps({k:r.get(k) for k in ('case_id','status','wall_seconds','reused')}));sys.exit(0 if r['status']=='completed' else 1)
