"""R10L execution adapter: existing transport/rotation/GK, support mask only.

No scientific function is replaced. --prepare pins the finite tail queries and
bounded endpoint generator BEFORE --execute may call existing contour_geometry.
Copyrighted benchmark PDFs and figures are never copied into this directory.
"""
from pathlib import Path
import argparse, hashlib, json, platform, sys, time, traceback
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
G = REPO/'research/shared_c64/20260930/CODE_I02_R10G_ENDPOINT_RESOLUTION/PACKAGE'
sys.path[:0] = [str(G), str(REPO/'src'), str(REPO)]
from execute_endpoint import atomic, sha, source_check, SOURCE_SHA
from endpoint_quadrature import nodes, reduce, integrate_endpoint
from audit_support import BRANCH_NAMES, BLOCKS, propagate
from bass_he.eq54 import BRANCHES
from bass_he.rotation import rotation_batch
from bass_he.geometry import _gk15_nodes, _gk15_reduce
from scripts.r10a_rho_freeze import _shell_summary
from eta_rotation import velocity


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def support_probabilities(delta, rhos, energies, cutoffs):
    """Retain existing factor2, zero out inactive events before transport."""
    rhos = np.asarray(rhos, float)
    delta = np.asarray(delta, float)
    energies = np.asarray(energies, float)
    if delta.shape != (len(rhos), len(cutoffs)):
        raise ValueError('delta shape')
    if np.any(~np.isfinite(delta)) or np.any(delta < 0):
        raise ValueError('finite nonnegative actions')
    p = np.exp(-2*np.repeat(delta, len(energies), axis=0)/
               velocity(np.tile(energies, len(rhos)))[:, None])
    return p*np.repeat(rhos[:, None] <= np.asarray(cutoffs), len(energies), axis=0)


def load_bank(old):
    tablepath = old/'restored/review/EXACT_NODE_TABLE.json'
    if sha(tablepath) != 'a5c2422820b56b0ae6b5cc3857b0d24508452bb274ad40e1818373facb1e8031':
        raise ValueError('old exact table identity')
    table = json.loads(tablepath.read_text())
    if table['source_sha256'] != SOURCE_SHA or table['depth'] != 96 or table['panels'] != 32:
        raise ValueError('table authority')
    bank = {(r['branch'], r['rho_hex']): (r['delta_hex'], 'R10F') for r in table['rows']}
    inputs = old/'restored/inputs'
    endpoints = {b: sha(inputs/f'R10A_EP_{b}.json') for b in BRANCH_NAMES}
    paths = sorted((old/'geometry_cache').glob('*.json'))
    if len(paths) != 300:
        raise ValueError('expected complete R10G endpoint cache')
    provenance = []
    for path in paths:
        item = json.loads(path.read_text()); key, record = item['key'], item['record']
        if hashlib.sha256(canonical(key)).hexdigest() != path.stem:
            raise ValueError('old cache key hash')
        if hashlib.sha256(canonical(record)).hexdigest() != item['record_sha256']:
            raise ValueError('old cache payload hash')
        b = key['branch']
        if (key['source'] != SOURCE_SHA or key['environment'] != ['2.3.5','3.12.3'] or
            key['depth'] != 96 or key['panels'] != 32 or key['endpoint_sha256'] != endpoints[b] or
            key['contract'] != sha(G/'CONTRACT.json') or record['branch'] != b or
            record['rho_hex'] != key['rho_hex']):
            raise ValueError('old cache transitive identity')
        pair = (b, key['rho_hex'])
        if pair in bank and bank[pair][0] != record['delta_hex']:
            raise ValueError('contradictory exact record')
        bank[pair] = (record['delta_hex'], 'R10G')
        provenance.append({'file':path.name,'sha256':sha(path)})
    return bank, endpoints, provenance


def prepare(old):
    source_check(REPO)
    manifest = json.loads((HERE/'BENCHMARK_MANIFEST.json').read_text())
    model = json.loads((HERE/'MODEL_CONTRACT.json').read_text())
    if manifest['status'] != 'FROZEN_READY' or model['benchmark_manifest_sha256'] != sha(HERE/'BENCHMARK_MANIFEST.json'):
        raise ValueError('ordered benchmark/model gate')
    bank, endpoints, provenance = load_bank(old)
    real = [float(b.R.real) for b in BRANCHES]
    extended = [float(b.support_cutoff) for b in BRANCHES]
    oldcuts = json.loads((old/'restored/review/CUTPOINT_QUERY_PRECOMMITTED.json').read_text())['cutpoint_hex']
    # Preserve inherited union splits and add REAL boundaries; no new fitted cut.
    cuts = sorted(set([float.fromhex(h) for h in oldcuts if float.fromhex(h) < max(real)] + real))
    tail_specs = list(zip(cuts[1:-1], cuts[2:]))
    rhos = np.concatenate([np.sqrt(_gk15_nodes(a*a,b*b)) for a,b in tail_specs])
    pairs = [(b,float(r).hex()) for r in rhos for b,c in zip(BRANCH_NAMES,real) if r < c]
    missing = [p for p in pairs if tuple(p) not in bank]
    query = {'schema':'bass_he.r10l.real_query.v1', 'scientific_source_sha256':SOURCE_SHA,
             'execution_adapter_sha256':sha(__file__), 'environment':[platform.python_version(),np.__version__],
             'helper_sha256':{n:sha(G/n) for n in ('audit_support.py','eta_rotation.py','endpoint_quadrature.py')},
             'endpoint_sha256':endpoints, 'branch_order':list(BRANCH_NAMES),
             'real_support_hex':[x.hex() for x in real], 'extended_support_hex':[x.hex() for x in extended],
             'support_source':'unchanged ScopedBranch.R.real; not refined endpoint.R.real',
             'cutpoints_hex':[x.hex() for x in cuts], 'tail_rho_hex':[float(r).hex() for r in rhos],
             'tail_active_pairs':pairs, 'tail_new_pairs':missing, 'tail_reuse_count':len(pairs)-len(missing),
             'endpoint_B_hex':cuts[1].hex(), 'endpoint_q_scale_hex':json.loads((G/'CONTRACT.json').read_text())['q_scale_hex'],
             'endpoint_generator_sha256':sha(G/'endpoint_quadrature.py'),
             'endpoint_policy':'unchanged integrate_endpoint; initial2 leaves, worst-first up to8, max210rho; exact hex identities pinned on each generated batch before solve',
             'max_new_delta_calls':len(missing)+1050,'max_endpoint_rho':210,
             'depth':96,'panels':32,'rotation_steps':64,'rotation_check_steps':128,
             'rtol':2e-4,'atol':1e-10,'new_global_refinement':False,
             'tail_coordinate':'unchanged R10F u=rho^2; direct _gk15_nodes/_gk15_reduce calls',
             'model_contract_sha256':sha(HERE/'MODEL_CONTRACT.json'),
             'old_cache_inventory':provenance, 'domain_policy':'REAL subset EXTENDED, no solve at inactive/outside points'}
    path=HERE/'QUERY_CONTRACT.json'
    if path.exists() and canonical(json.loads(path.read_text())) != canonical(query):
        raise ValueError('immutable query restart mismatch')
    atomic(path,query)
    atomic(HERE/'REUSED_EXACT_BANK.json',{'rows':[{'branch':b,'rho_hex':h,'delta_hex':d,'origin':o}
           for (b,h),(d,o) in sorted(bank.items())], 'source_sha256':SOURCE_SHA})
    return query, bank


def execute(old):
    query, bank = prepare(old)
    from bass_he.geometry import contour_geometry, unjsonable
    eps={b:unjsonable(json.loads((old/f'restored/inputs/R10A_EP_{b}.json').read_text())['ep']) for b in BRANCH_NAMES}
    counts={'new_delta_calls':0,'reused_R10F_pairs':0,'reused_R10G_pairs':0,'reused_R10L_cache':0,'rho_evaluations':0}
    real=np.array([float.fromhex(h) for h in query['real_support_hex']]); extended=np.array([float.fromhex(h) for h in query['extended_support_hex']])
    query_sha=sha(HERE/'QUERY_CONTRACT.json'); batch=0; pilot_done=False
    def evaluate(rhos):
        nonlocal batch, pilot_done
        batch_id=batch; batch+=1
        rhos=np.asarray(rhos,float)
        if np.any(rhos<=0) or np.any(rhos>max(real)):
            raise ValueError('bounded rho')
        pairs=[(b,float(r).hex()) for r in rhos for b,c in zip(BRANCH_NAMES,real) if r<c]
        # Actual adaptive query identities are durably pinned before any solve.
        atomic(HERE/f'queries/{batch_id:02d}.json',{'parent_contract_sha256':query_sha,'rho_hex':[float(r).hex() for r in rhos],'active_pairs':pairs})
        E=np.tile([.5,5.],len(rhos));r=np.repeat(rhos,2)
        rot=np.broadcast_to(np.eye(10),(len(r),10,10)).copy();checks=[]
        for N,l,idx in BLOCKS:
            cut=((l+.5)**2-.5)/3
            fine=rotation_batch(N,l,E,r,steps=64,R_cut=cut)
            coarse=rotation_batch(N,l,E,r,steps=128,R_cut=cut)
            difference=float(np.max(abs(fine['P_abs']-coarse['P_abs'])))
            unitarity=float(np.max(abs(fine['U_z'].conj().swapaxes(-2,-1)@fine['U_z']-np.eye(2*l+1))))
            stochasticity=float(np.max(abs(fine['P_abs'].sum(1)-1)))
            checks.append({'N':N,'l':l,'probability_difference':difference,'unitarity':unitarity,'stochasticity':stochasticity})
            if difference>1e-7 or max(unitarity,stochasticity)>5e-13:
                atomic(HERE/f'rotation/{batch_id:02d}.json',{'status':'FAIL','checks':checks})
                raise ArithmeticError('new query rotation unresolved')
            rot[:,np.asarray(idx)[:,None],idx]=fine['P_abs']
        atomic(HERE/f'rotation/{batch_id:02d}.json',{'status':'PASS','checks':checks})
        D=np.zeros((len(rhos),5))
        for i,rho in enumerate(rhos):
            hx=float(rho).hex()
            for k,b in enumerate(BRANCH_NAMES):
                if rho>=real[k]:continue
                if rho>extended[k]:raise ValueError('outside old extended domain')
                pair=(b,hx)
                if pair in bank:
                    hxdelta,origin=bank[pair];counts['reused_'+origin+'_pairs']+=1;d=float.fromhex(hxdelta)
                else:
                    key={'source':SOURCE_SHA,'environment':['2.3.5','3.12.3'],'endpoint_sha256':query['endpoint_sha256'][b],
                         'query_contract_sha256':query_sha,'branch':b,'rho_hex':hx,'depth':96,'panels':32}
                    path=HERE/'geometry_cache'/(hashlib.sha256(canonical(key)).hexdigest()+'.json')
                    if path.exists():
                        item=json.loads(path.read_text())
                        if canonical(item['key'])!=canonical(key) or hashlib.sha256(canonical(item['record'])).hexdigest()!=item['record_sha256']:
                            raise ValueError('new cache authority')
                        if item['record']['branch']!=b or item['record']['rho_hex']!=hx:
                            raise ValueError('new cache record/key identity')
                        d=float.fromhex(item['record']['delta_hex']);counts['reused_R10L_cache']+=1
                    else:
                        if counts['new_delta_calls']>=query['max_new_delta_calls']:raise RuntimeError('budget exhausted')
                        started=time.perf_counter(); rec=contour_geometry(eps[b],float(rho),panels=32);elapsed=time.perf_counter()-started
                        d=float(rec['delta'])
                        if not np.isfinite(d) or d<0:raise ArithmeticError('invalid Delta')
                        record={'branch':b,'rho_hex':hx,'delta_hex':d.hex(),'elapsed_s':elapsed,
                                'max_spectral_residual':float(rec['max_spectral_residual']),
                                'minimum_normalized_sheet_gap':float(rec['minimum_normalized_sheet_gap'])}
                        atomic(path,{'key':key,'record':record,'record_sha256':hashlib.sha256(canonical(record)).hexdigest()})
                        counts['new_delta_calls']+=1
                        if not pilot_done:
                            atomic(HERE/'PILOT.json',{'elapsed_s':elapsed,'projected_upper_delta_seconds':elapsed*query['max_new_delta_calls'],
                                   'source':'one newly pinned rho/branch, retained for full run, not repeated'})
                            pilot_done=True
                        if counts['new_delta_calls']%10==0:atomic(HERE/'PROGRESS.json',counts)
                D[i,k]=d
        p=support_probabilities(D,rhos,[.5,5.],real)
        values=propagate(p,rot)[:,np.arange(10)!=2].reshape(len(rhos),18)
        counts['rho_evaluations']+=len(rhos)
        atomic(HERE/f'integrands/{batch_id:02d}.json',{'rho_hex':[float(r).hex() for r in rhos],'components':values.tolist()})
        return values
    try:
        cuts=[float.fromhex(h) for h in query['cutpoints_hex']]; specs=list(zip(cuts[1:-1],cuts[2:]))
        rhos=np.array([float.fromhex(h) for h in query['tail_rho_hex']]);vals=evaluate(rhos)
        tail=np.zeros(18);te=np.zeros(18);intervals=[]
        for i,(a,b) in enumerate(specs):
            reduced=_gk15_reduce(a*a,b*b,vals[15*i:15*i+15])
            high,error=reduced['high'],reduced['error']
            tail+=high;te+=error;intervals.append({'a_hex':a.hex(),'b_hex':b.hex(),'high':high.tolist(),'error':error.tolist()})
        atomic(HERE/'TAIL.json',{'intervals':intervals,'integral':tail.tolist(),'error_estimate':te.tolist()})
        result=integrate_endpoint(evaluate,B=cuts[1],scale=float.fromhex(query['endpoint_q_scale_hex']),tail=tail,tail_error=te,
                                  rtol=2e-4,atol=1e-10,max_leaves=8,checkpoint=lambda r:atomic(HERE/'ENDPOINT_PROGRESS.json',r))
        result['counts']=counts;result['query_contract_sha256']=query_sha
        result['status']='R10L_C_LOCAL_NUMERICAL_PASS' if result['converged'] else 'R10L_C_NUMERICAL_UNRESOLVED'
        shells={}
        for j,E in enumerate(('0.5','5.0')):
            v=np.zeros(10);error=np.zeros(10);keep=np.arange(10)!=2
            v[keep]=np.array(result['integral']).reshape(2,9)[j];error[keep]=np.array(result['error_estimate']).reshape(2,9)[j]
            shells[E]={'Z2_shell_areas_a0sq':_shell_summary(v),'Z2_shell_error_estimate_a0sq':_shell_summary(error)}
        result['shells']=shells
        result['claim']='finite Nmax3 shell audit; empirical local error estimate, no global continuum/physical certificate'
        atomic(HERE/'C_RESULT.json',result)
        return result
    except Exception:
        atomic(HERE/'FAILURE.json',{'counts':counts,'traceback':traceback.format_exc(),'historical_results_preserved':True})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-run',type=Path,required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.execute:
        result=execute(args.old_run);print(json.dumps({'status':result['status'],'counts':result['counts']}))
        if not result['converged']:raise SystemExit(3)
    else:
        q,_=prepare(args.old_run);print(json.dumps({'status':'QUERY_PINNED_NOT_EXECUTED','tail_pairs':len(q['tail_active_pairs']),
                         'tail_new':len(q['tail_new_pairs']),'tail_reuse':q['tail_reuse_count'],'max_new_delta':q['max_new_delta_calls']}))
