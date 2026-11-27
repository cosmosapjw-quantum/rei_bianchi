"""Prepared R10G execution boundary. Default is archive/contract inventory only.

--execute performs ONLY the newly contracted first-interval computation. The
other sixteen R10F panels are immutable reused evidence. Exact source/environment
mismatch fails before any contour call. No default production code is edited.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,sys,time,traceback,zipfile
from pathlib import Path,PurePosixPath
import numpy as np
from eta_rotation import eta_rotation_batch,eta_dop853,velocity
from endpoint_quadrature import integrate_endpoint
from audit_support import BLOCKS,BRANCH_NAMES,LANES,propagate

ROOT=Path(__file__).resolve().parent
ARCHIVE_SHA='082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578'
TABLE_SHA='a5c2422820b56b0ae6b5cc3857b0d24508452bb274ad40e1818373facb1e8031'
SOURCE_SHA='496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba'
DEPENDENCIES=('src/bass_he/geometry.py','src/bass_he/spectral.py','src/bass_he/eq54.py',
 'src/bass_he/rotation.py','src/bass_he/transport.py','src/arseny_reimpl/eq50_scoped.py',
 'src/arseny_reimpl/term_complex.py','src/arseny_reimpl/term_real.py',
 'src/arseny_reimpl/correlation.py','scripts/r10a_rho_freeze.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    temp=path.with_name(path.name+'.tmp')
    with temp.open('wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.replace(temp,path)
    fd=os.open(str(path.parent),os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def restore(archive,destination):
    archive=Path(archive);destination=Path(destination)
    if sha(archive)!=ARCHIVE_SHA:raise ValueError('R10F_ARCHIVE_IDENTITY_MISMATCH')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('R10F_ZIP_CRC_FAILURE')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('duplicate ZIP entries')
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or (info.external_attr>>16)&0o170000==0o120000:
                raise ValueError('unsafe archive member')
        manifest=json.loads(z.read('MANIFEST.json'))
        for item in manifest['payloads']:
            raw=z.read(item['path'])
            if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
                raise ValueError('R10F_MANIFEST_FAILURE')
        # Only required immutable inputs; no redundant copy of 945 cache payloads.
        wanted=['review/EXACT_NODE_TABLE.json','review/FIXED_GK_DIAGNOSTIC.json',
                'review/CUTPOINT_QUERY_PRECOMMITTED.json','inputs/R10A_RUN_CONTRACT.json',
                'inputs/R10C_FROZEN_DELTA0_RECORD.json']
        wanted += ['inputs/R10A_EP_'+b+'.json' for b in BRANCH_NAMES]
        for name in wanted:
            raw=z.read(name);path=destination/name;path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=raw:raise ValueError('restored input would overwrite different bytes')
            if not path.exists():path.write_bytes(raw)
    if sha(destination/'review/EXACT_NODE_TABLE.json')!=TABLE_SHA:raise ValueError('R10F_TABLE_IDENTITY')
    return destination


def source_check(repo):
    repo=Path(repo).resolve();h=hashlib.sha256()
    for rel in DEPENDENCIES:h.update(rel.encode()+b'\0'+(repo/rel).read_bytes())
    if h.hexdigest()!=SOURCE_SHA:raise ValueError('R10G_SOURCE_IDENTITY_BLOCKED')
    if platform.python_version()!='3.12.3' or np.__version__!='2.3.5':
        raise ValueError('R10G_ENVIRONMENT_IDENTITY_BLOCKED: needs R10F Python3.12.3/NumPy2.3.5')
    return repo


def rotation_batch_checked(rhos,out,batchid):
    Es=np.tile([.5,5.],len(rhos));r=np.repeat(rhos,2)
    mats={};records=[]
    for kind in ('CPC','AUTHOR'):
        total=np.broadcast_to(np.eye(10),(len(r),10,10)).copy()
        for N,l,idx in BLOCKS:
            cut=((l+.5)**2-(.5 if kind=='CPC' else 0))/3
            coarse=eta_rotation_batch(N,l,Es,r,R_cut=cut,steps=128)
            fine=eta_rotation_batch(N,l,Es,r,R_cut=cut,steps=256)
            diffs=np.max(abs(coarse['P_abs']-fine['P_abs']),axis=(1,2))
            if max(diffs)>1e-7 or max(fine['unitarity_defect'],fine['stochasticity_defect'])>5e-13:
                atomic(out/f'rotation_gate_{batchid}.json',{'status':'FAIL','kind':kind,'N':N,'l':l,'step_max':float(max(diffs)),
                                                         'unitarity':fine['unitarity_defect'],'stochasticity':fine['stochasticity_defect']})
                raise ArithmeticError('R10G_NEW_QUERY_ROTATION_UNRESOLVED')
            for E in (.5,5.):
                active=np.flatnonzero((Es==E)&fine['entered'])
                if not len(active):continue
                k=int(active[np.argmax(diffs[active])])
                check=eta_dop853(N,l,E,float(r[k]),R_cut=cut)
                difference=float(np.max(abs(check['P_abs']-fine['P_abs'][k])))
                records.append({'N':N,'l':l,'E':E,'cutoff':kind,'rho_hex':float(r[k]).hex(),
                                'step_max':float(np.max(diffs[active])),'dop_difference':difference,'nfev':check['nfev']})
                if difference>1e-8:
                    atomic(out/f'rotation_gate_{batchid}.json',{'status':'FAIL','records':records})
                    raise ArithmeticError('R10G_DOP853_QUERY_AUDIT_FAILED')
            total[:,np.asarray(idx)[:,None],idx]=fine['P_abs']
        mats['COUL_'+kind]=total
    atomic(out/f'rotation_gate_{batchid}.json',{'status':'PASS','records':records})
    return mats


def execute(repo,archive,out,*,run=False):
    out=Path(out).resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('output must be outside immutable delivery package')
    out.mkdir(parents=True,exist_ok=True)
    contract=json.loads((ROOT/'CONTRACT.json').read_text())
    contract_sha=sha(ROOT/'CONTRACT.json')
    locked=out/'CONTRACT.lock.json'
    lock={'contract_sha256':contract_sha,'contract':contract}
    if locked.exists() and json.loads(locked.read_text())!=lock:raise ValueError('CONTRACT_RESTART_MISMATCH')
    atomic(locked,lock)
    inputs=restore(archive,out/'restored')
    diag=json.loads((inputs/'review/FIXED_GK_DIAGNOSTIC.json').read_text())
    pre=json.loads((inputs/'review/CUTPOINT_QUERY_PRECOMMITTED.json').read_text())
    B=float.fromhex(pre['cutpoint_hex'][1]);Bhex=B.hex()
    if Bhex!=contract['endpoint_B_hex']:raise ValueError('FIRST_INTERVAL_IDENTITY_MISMATCH')
    inventory={'status':'PREPARED_NOT_EXECUTED','archive_sha256':ARCHIVE_SHA,'exact_table_sha256':TABLE_SHA,
               'reused_outside_intervals':16,'old_exact_delta_rows':1035,'new_delta_calls':0,
               'max_new_query_evaluations':210,'max_new_delta_calls':1050,'B_hex':Bhex,'contract_sha256':contract_sha}
    atomic(out/'INPUT_INVENTORY.json',inventory)
    if not run:return inventory
    repo=source_check(repo)
    sys.path[:0]=[str(repo/'src'),str(repo)]
    # Late import: no scientific package at authoring/dry-run time.
    from bass_he.geometry import contour_geometry,unjsonable
    from bass_he.rotation import rotation_batch as straight_rotation
    endpoints={b:unjsonable(json.loads((inputs/f'inputs/R10A_EP_{b}.json').read_text())['ep']) for b in BRANCH_NAMES}
    for b,ep in endpoints.items():
        if ep['depth']!=96 or ep['certificate']['simple_fold'] is not True or ep['pair_membership']['passed'] is not True:
            raise ValueError('R10G_ENDPOINT_AUTHORITY_BLOCKED: '+b)
    table=json.loads((inputs/'review/EXACT_NODE_TABLE.json').read_text())
    exact={(x['branch'],x['rho_hex']):float.fromhex(x['delta_hex']) for x in table['rows']}
    frozen=json.loads((inputs/'inputs/R10C_FROZEN_DELTA0_RECORD.json').read_text())
    if [x['branch'] for x in frozen['records']]!=list(BRANCH_NAMES):raise ValueError('FROZEN_BRANCH_IDENTITY')
    d0=np.array([float.fromhex(x['delta0_hex']) for x in frozen['records']])
    tail=np.asarray(diag['interval_component_high_estimate'])[1:].sum(0)
    te=np.asarray(diag['interval_component_error_estimate'])[1:].sum(0)
    counts={'new_delta_calls':0,'r10f_exact_reuse':0,'new_cache_reuse':0,'rotation_batches':0}
    def eval_nodes(rhos):
        batchid=counts['rotation_batches'];counts['rotation_batches']+=1
        # Check representation numerics before spending geometry calls.
        mats=rotation_batch_checked(rhos,out,batchid)
        E=np.tile([.5,5.],len(rhos));r=np.repeat(rhos,2)
        for kind in ('CPC','AUTHOR'):
            total=np.broadcast_to(np.eye(10),(len(r),10,10)).copy()
            for N,l,idx in BLOCKS:
                cut=((l+.5)**2-(.5 if kind=='CPC' else 0))/3
                fine=straight_rotation(N,l,E,r,steps=64,R_cut=cut)
                audit=straight_rotation(N,l,E,r,steps=128,R_cut=cut)
                if np.max(abs(fine['P_abs']-audit['P_abs']))>1e-7:raise ArithmeticError('R10G_NEW_STRAIGHT_QUERY_UNRESOLVED')
                total[:,np.asarray(idx)[:,None],idx]=fine['P_abs']
            mats['SL_CPC' if kind=='CPC' else 'SL_AUTHORCUT']=total
        D=np.zeros((len(rhos),5))
        for i,rho in enumerate(rhos):
            hx=float(rho).hex()
            for k,b in enumerate(BRANCH_NAMES):
                key={'kind':'R10G_exact_delta','contract':contract_sha,'source':SOURCE_SHA,'environment':['2.3.5','3.12.3'],
                     'endpoint_sha256':sha(inputs/f'inputs/R10A_EP_{b}.json'),'branch':b,'rho_hex':hx,'depth':96,'panels':32}
                keyhash=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                path=out/'geometry_cache'/f'{keyhash}.json'
                if (b,hx) in exact:
                    d=exact[(b,hx)];counts['r10f_exact_reuse']+=1
                elif path.exists():
                    old=json.loads(path.read_text())
                    if old['key']!=key:raise ValueError('CACHE_KEY_IDENTITY_MISMATCH')
                    raw=json.dumps(old['record'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()
                    if hashlib.sha256(raw).hexdigest()!=old['record_sha256']:raise ValueError('CACHE_PAYLOAD_IDENTITY_MISMATCH')
                    d=float.fromhex(old['record']['delta_hex']);counts['new_cache_reuse']+=1
                else:
                    if counts['new_delta_calls']>=1050:raise RuntimeError('EXACT_GEOMETRY_BUDGET_EXHAUSTED')
                    t=time.perf_counter();rec=contour_geometry(endpoints[b],float(rho),panels=32)
                    d=float(rec['delta']);counts['new_delta_calls']+=1
                    if not np.isfinite(d) or d<0:raise ArithmeticError('INVALID_EXACT_DELTA')
                    record={'delta_hex':d.hex(),'elapsed_s':time.perf_counter()-t,'rho_hex':hx,'branch':b,'panels':32,
                            'spectral_residual':float(rec['max_spectral_residual']),
                            'sheet_gap':float(rec['minimum_normalized_sheet_gap'])}
                    raw=json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
                    atomic(path,{'key':key,'record':record,'record_sha256':hashlib.sha256(raw).hexdigest()})
                    if counts['new_delta_calls']%10==0:atomic(out/'PROGRESS.json',counts)
                D[i,k]=d
        dynamic=np.exp(-2*np.repeat(D,2,axis=0)/velocity(E)[:,None])
        static=np.exp(-2*d0/velocity(E)[:,None]);columns=[]
        for lane in LANES:
            frozen_lane=lane=='COUL_AUTHOR_FROZEN';rot=mats['COUL_AUTHOR'] if frozen_lane else mats[lane]
            y=propagate(static if frozen_lane else dynamic,rot)
            columns.append(y[:,np.arange(10)!=2].reshape(len(rhos),18))
        vals=np.concatenate(columns,axis=1)
        atomic(out/'integrands'/f'{batchid:02d}.json',{'rho_hex':[float(x).hex() for x in rhos],'components':vals.tolist()})
        return vals
    try:
        result=integrate_endpoint(eval_nodes,B=B,scale=float.fromhex(contract['q_scale_hex']),tail=tail,tail_error=te,
                                  max_leaves=8,checkpoint=lambda r:atomic(out/'ENDPOINT_PROGRESS.json',r))
        result.update({'counts':counts,'source_sha256':SOURCE_SHA,'old_tail_sha256':sha(inputs/'review/FIXED_GK_DIAGNOSTIC.json'),
                       'scientific_PROMOTE':'HOLD','Eq55_next_node_authorized':False,'Eq55':'NOT_RUN',
                       'R10F_historical_verdict':'R10F_BOUNDARY_SPLIT_GK_UNRESOLVED_PRESERVED',
                       'production_change':False,'factorial_or_appendix_admission':'NOT_AUTOMATIC'})
        atomic(out/'RETURN_REPORT.json',result)
        return result
    except Exception:
        atomic(out/'FAILURE.json',{'status':'R10G_EXECUTION_BLOCKED_OR_FAILED','counts':counts,'traceback':traceback.format_exc(),
                                  'scientific_PROMOTE':'HOLD','Eq55':'NOT_RUN'})
        raise

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,help='pinned BASS_HE checkout, required with --execute')
    parser.add_argument('--r10f-archive',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--execute',action='store_true',help='explicitly run newly contracted first-interval node')
    args=parser.parse_args()
    if args.execute and args.repo is None:parser.error('--repo required with --execute')
    import fcntl
    args.out.mkdir(parents=True,exist_ok=True)
    guard=(args.out/'PROCESS.lock').open('a')
    try:fcntl.flock(guard.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise SystemExit('R10G_OUTPUT_DIRECTORY_BUSY')
    ans=execute(args.repo,args.r10f_archive,args.out,run=args.execute)
    print(json.dumps({'status':ans['status'],'converged':ans.get('converged'),'counts':ans.get('counts')},indent=2))
    if args.execute and not ans.get('converged'):raise SystemExit(3)
