"""R10F research-only exact-node boundary split execution."""
from __future__ import annotations

import hashlib
import json
import math
import platform
import time
import traceback
from pathlib import Path

import numpy as np

from bass_he.eq54 import BRANCHES
from bass_he.geometry import EvidenceCache, _canonical, _gk15_nodes, atomic_json, contour_geometry, unjsonable
from scripts.r10a_rho_freeze import _source_identity
from r10c_runner import contour_key

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
CONTRACT=REPO/'research/shared_c64/20260930/CODE_I02_R10F_ROTATION_BOUNDARY_SPLIT'
R10C=REPO/'research/shared_c64/20260929/CODE_I02_R10C_EXACT_NODE_EXECUTION/20260929T1842KST'
TABLE_SHA='21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49'
SOURCE_SHA='496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba'
ARCHIVE_SHA='2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75'


def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _blob(path):
    body=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()


def plan_queries():
    pre_path=HERE/'CUTPOINT_QUERY_PRECOMMITTED.json'
    pre=json.loads(pre_path.read_text())
    idn=json.loads((CONTRACT/'CUTPOINT_IDENTITY.json').read_text())
    analysis=json.loads((CONTRACT/'BOUNDARY_ANALYSIS.json').read_text())
    if (_blob(CONTRACT/'CUTPOINT_IDENTITY.json')!='05a54f8bd8d4c85cdf5fd6a7dcda0b4919811ebd' or
        _blob(CONTRACT/'BOUNDARY_ANALYSIS.json')!='1888441743142a5370083ff567a122aa99e9be55' or
        idn['decimal']!=analysis['union_split'] or len(idn['hex'])!=18 or
        [float(x).hex() for x in analysis['union_split']]!=idn['hex'] or
        idn['hex']!=pre['cutpoint_hex']):
        raise ValueError('R10F_CUTPOINT_IDENTITY_MISMATCH')
    expected_hash=hashlib.sha256(json.dumps(idn['hex'],separators=(',',':')).encode()).hexdigest()
    if expected_hash!=idn['sha256_of_hex_json'] or pre['cutpoint_hex_json_sha256']!=expected_hash:
        raise ValueError('R10F_CUTPOINT_HASH_MISMATCH')
    cuts=np.array(analysis['union_split'],float)
    nodes=np.concatenate([np.sqrt(_gk15_nodes(a*a,b*b)) for a,b in zip(cuts[:-1],cuts[1:])])
    if len(nodes)!=255 or len({float(x).hex() for x in nodes})!=255 or np.any(nodes<=0):
        raise ValueError('R10F_NODE_IDENTITY_MISMATCH')
    for i,(a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
        if not np.all((nodes[i*15:(i+1)*15]>a)&(nodes[i*15:(i+1)*15]<b)):
            raise ValueError('R10F_NODE_OUTSIDE_SPLIT')
    if [float(x).hex() for x in nodes]!=pre['node_hex']:
        raise ValueError('R10F_NODE_IDENTITY_MISMATCH')
    table_path=R10C/'EXACT_NODE_TABLE.json'
    manifest=json.loads((R10C/'EXACT_NODE_TABLE_MANIFEST.json').read_text())
    if _sha(table_path)!=TABLE_SHA or manifest['table_sha256']!=TABLE_SHA:
        raise ValueError('R10C_TABLE_IDENTITY_MISMATCH')
    table=json.loads(table_path.read_text())
    old={(x['branch'],x['rho_hex']):x for x in table['rows']}
    rows=[]
    for b in BRANCHES:
        for rho in nodes:
            if rho<=b.support_cutoff:
                hx=float(rho).hex()
                rows.append({'index':len(rows),'branch':b.name,'rho':float(rho),'rho_hex':hx,
                             'origin':'R10C_EXACT_REUSE' if (b.name,hx) in old else 'R10F_NEW_EXACT'})
    hash_pairs=hashlib.sha256(json.dumps([(r['branch'],r['rho_hex']) for r in rows],separators=(',',':')).encode()).hexdigest()
    if (len(rows)!=1035 or sum(r['origin']=='R10C_EXACT_REUSE' for r in rows)!=90 or
        hash_pairs!=pre['ordered_pair_identity_sha256']):
        raise ValueError('R10F_QUERY_IDENTITY_MISMATCH')
    return {'cutpoint_hex':idn['hex'],'cutpoints':cuts,'node_hex':pre['node_hex'],
            'nodes':nodes,'rows':rows,'old_rows':old,'ordered_pair_identity_sha256':hash_pairs,
            'precommit_path':str(pre_path)}


def validate_exact_record(row,rec):
    if (float(rec['rho']).hex()!=row['rho_hex'] or float(row['rho']).hex()!=row['rho_hex']
        or type(rec['panels']) is not int or rec['panels']!=32):
        raise ValueError('R10F_RECORD_IDENTITY_MISMATCH')
    d=rec['delta']
    if isinstance(d,bool) or not isinstance(d,(int,float,np.floating)) or not math.isfinite(float(d)) or d<0:
        raise ValueError('R10F_NONFINITE_OR_NEGATIVE_DELTA')
    return float(d)


def validate_fixed_gk(total,error,*,evaluations,refinements):
    total=np.asarray(total,float);error=np.asarray(error,float)
    if (total.shape!=(90,) or error.shape!=(90,) or np.any(~np.isfinite(total)) or
        np.any(~np.isfinite(error)) or np.any(error<0) or evaluations!=255 or refinements!=0):
        raise ValueError('R10F_FIXED_GK_CONTRACT_MISMATCH')
    tolerance=1e-10+2e-4*np.abs(total)
    failed=np.flatnonzero(error>tolerance)
    return {'status':'PASS' if not len(failed) else 'R10F_BOUNDARY_SPLIT_GK_UNRESOLVED',
            'failed_component_count':len(failed),'failed_component_indices_zero_based':failed.tolist(),
            'max_normalized_error':float(np.max(error/tolerance)),
            'component_error_estimate':error.tolist(),'component_tolerance':tolerance.tolist(),
            'evaluations':evaluations,'refinements':refinements}


def endpoint_authority(archive_root,archive_zip):
    archive_root=Path(archive_root);archive_zip=Path(archive_zip)
    source,deps=_source_identity(REPO)
    env=(np.__version__,platform.python_version())
    contract=json.loads((archive_root/'RUN_CONTRACT.json').read_text())
    if (source!=SOURCE_SHA or _sha(archive_zip)!=ARCHIVE_SHA or
        env!=('2.3.5','3.12.3') or contract['source_sha256']!=source or
        contract['numpy']!=env[0] or contract['python']!=env[1] or
        contract['depth']!=96 or contract['panels']!=32 or contract['dependencies']!=list(deps)):
        raise ValueError('R10F_ENDPOINT_SOURCE_IDENTITY_MISMATCH')
    old_cache=EvidenceCache(archive_root/'cache')
    endpoints={}
    for b in BRANCHES:
        key={'source':source,'environment':env,'kind':'R10A_EP',
             'branch':b.name,'state_a':b.state_a,'state_b':b.state_b,
             'R':(b.R.real.hex(),b.R.imag.hex()),'depth':96}
        ep=old_cache.get(key)
        saved=unjsonable(json.loads((archive_root/f'EP_{b.name}.json').read_text())['ep'])
        if (ep is None or _canonical(ep)!=_canonical(saved) or
            ep['certificate']['simple_fold'] is not True or
            ep['pair_membership']['passed'] is not True or ep['depth']!=96 or
            tuple(ep['state_a'])!=b.state_a or tuple(ep['state_b'])!=b.state_b):
            raise RuntimeError('R10F_ENDPOINT_AUTHORITY_BLOCKED: '+b.name)
        endpoints[b.name]=ep
    return endpoints,env,source


def run_phase_a(archive_root,archive_zip,*,max_new=945):
    """Persist each exact result; a small max_new performs the measured pilot."""
    plan=plan_queries()
    endpoints,env,source=endpoint_authority(archive_root,archive_zip)
    branch_map={b.name:b for b in BRANCHES}
    new_cache=EvidenceCache(HERE/'cache')
    counts={'old_exact_pair_reuse':0,'prior_local_exact_reuse':0,'new_exact_delta_calls':0}
    output=[]
    for row in plan['rows']:
        b=branch_map[row['branch']];rho=row['rho']
        if row['origin']=='R10C_EXACT_REUSE':
            old=plan['old_rows'][(b.name,row['rho_hex'])]
            if (old['source_sha256']!=source or old['depth']!=96 or old['panels']!=32 or
                float(old['rho']).hex()!=row['rho_hex']):
                raise ValueError('R10F_OLD_EXACT_IDENTITY_MISMATCH')
            rec={'rho':rho,'delta':float.fromhex(old['delta_hex']),'panels':32}
            origin='R10C_EXACT_REUSE';counts['old_exact_pair_reuse']+=1
        else:
            key=contour_key(b,rho,source,env,depth=96,panels=32)
            rec=new_cache.get(key)
            if rec is not None:
                origin='R10F_LOCAL_EXACT_REUSE';counts['prior_local_exact_reuse']+=1
            else:
                if counts['new_exact_delta_calls']>=max_new:
                    atomic_json(HERE/'PROGRESS.json',{'status':'PILOT_PAUSED','completed':len(output),
                                'total':len(plan['rows']),'counts':counts})
                    return {'status':'PILOT_PAUSED','completed':len(output),'counts':counts}
                try:
                    start=time.perf_counter()
                    rec=contour_geometry(endpoints[b.name],rho,panels=32)
                    rec['elapsed_s']=time.perf_counter()-start
                    validate_exact_record(row,rec)
                    new_cache.put(key,rec)
                except Exception:
                    atomic_json(HERE/'failures'/f'{row["index"]:04d}_{b.name}.json',
                                {'row':row,'traceback':traceback.format_exc()})
                    raise
                origin='R10F_NEW_32_PANEL_EXACT';counts['new_exact_delta_calls']+=1
        delta=validate_exact_record(row,rec)
        saved={**row,'delta':delta,'delta_hex':delta.hex(),'origin':origin,
               'depth':96,'panels':32,'source_sha256':source,'environment':env,
               'elapsed_s':rec.get('elapsed_s')}
        atomic_json(HERE/'rows'/f'{row["index"]:04d}.json',saved)
        output.append(saved)
        if len(output)%10==0 or counts['new_exact_delta_calls']<=3:
            atomic_json(HERE/'PROGRESS.json',{'status':'PHASE_A_IN_PROGRESS',
                        'completed':len(output),'total':len(plan['rows']),'counts':counts})
            if counts['new_exact_delta_calls']%10==0:
                print('exact',counts['new_exact_delta_calls'],'rows',len(output),flush=True)
    table={'schema':'bass_he.r10f.boundary_union_exact_table.v1','status':'COMPLETE_VALID_EXACT_NODE_TABLE',
           'source_sha256':source,'environment':env,'depth':96,'panels':32,
           'cutpoint_hex_json_sha256':json.loads((HERE/'CUTPOINT_QUERY_PRECOMMITTED.json').read_text())['cutpoint_hex_json_sha256'],
           'ordered_pair_identity_sha256':plan['ordered_pair_identity_sha256'],'counts':counts,'rows':output}
    atomic_json(HERE/'EXACT_NODE_TABLE.json',table)
    raw=(HERE/'EXACT_NODE_TABLE.json').read_bytes()
    atomic_json(HERE/'EXACT_NODE_TABLE_MANIFEST.json',{'table_sha256':hashlib.sha256(raw).hexdigest(),
                'table_bytes':len(raw),'row_count':len(output),'unique_rho_count':len(plan['nodes']),
                'counts':counts,'source_sha256':source,'depth':96,'panels':32,
                'ordered_pair_identity_sha256':plan['ordered_pair_identity_sha256']})
    atomic_json(HERE/'PROGRESS.json',{'status':'PHASE_A_COMPLETE','completed':len(output),
                'total':len(plan['rows']),'counts':counts})
    return {'status':'PHASE_A_COMPLETE','completed':len(output),'counts':counts}


def audit_exact_table():
    """Reopen every exact key and verify its stored Delta before transport."""
    plan=plan_queries()
    table_path=HERE/'EXACT_NODE_TABLE.json'
    manifest=json.loads((HERE/'EXACT_NODE_TABLE_MANIFEST.json').read_text())
    if _sha(table_path)!=manifest['table_sha256'] or manifest['row_count']!=1035:
        raise ValueError('R10F_TABLE_MANIFEST_MISMATCH')
    table=json.loads(table_path.read_text())
    if (table['status']!='COMPLETE_VALID_EXACT_NODE_TABLE' or
        table['source_sha256']!=SOURCE_SHA or tuple(table['environment'])!=('2.3.5','3.12.3') or
        len(table['rows'])!=1035 or
        [(r['branch'],r['rho_hex']) for r in table['rows']]!=
        [(r['branch'],r['rho_hex']) for r in plan['rows']]):
        raise ValueError('R10F_TABLE_QUERY_MISMATCH')
    cache=EvidenceCache(HERE/'cache')
    branches={b.name:b for b in BRANCHES}
    keys=[];new_count=0;old_count=0
    max_residual=0.;min_gap=float('inf');accepted=0;bisected=0
    for q,row in zip(plan['rows'],table['rows']):
        if q['origin']=='R10C_EXACT_REUSE':
            old=plan['old_rows'][(q['branch'],q['rho_hex'])]
            if row['delta_hex']!=old['delta_hex'] or row['origin']!='R10C_EXACT_REUSE':
                raise ValueError('R10F_OLD_EXACT_ROW_MISMATCH')
            old_count+=1
        else:
            b=branches[q['branch']]
            key=contour_key(b,q['rho'],SOURCE_SHA,('2.3.5','3.12.3'),depth=96,panels=32)
            rec=cache.get(key)
            if rec is None or validate_exact_record(q,rec).hex()!=row['delta_hex']:
                raise ValueError('R10F_LOCAL_CACHE_ROW_MISMATCH')
            keys.append(hashlib.sha256(_canonical(key)).hexdigest())
            max_residual=max(max_residual,float(rec['max_spectral_residual']))
            min_gap=min(min_gap,float(rec['minimum_normalized_sheet_gap']))
            accepted+=int(rec['accepted_continuation_steps'])
            bisected+=int(rec['bisected_continuation_steps'])
            new_count+=1
    if old_count!=90 or new_count!=945:
        raise ValueError('R10F_EXACT_REUSE_COUNT_MISMATCH')
    audit={'status':'EXACT_CACHE_TABLE_MANIFEST_PASS','table_sha256':_sha(table_path),
           'rows':1035,'old_exact_pair_reuse':old_count,'new_exact_pair_count':new_count,
           'ordered_new_cache_key_sha256':hashlib.sha256(json.dumps(keys,separators=(',',':')).encode()).hexdigest(),
           'maximum_spectral_residual':max_residual,'minimum_normalized_sheet_gap':min_gap,
           'accepted_continuation_steps_total':accepted,'bisected_continuation_steps_total':bisected,
           'new_contour_solves_during_audit':0}
    atomic_json(HERE/'CACHE_ROW_AUDIT.json',audit)
    return audit
