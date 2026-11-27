"""Host-specific process/thread tuning without changing scientific arithmetic."""
from __future__ import annotations
import hashlib,json,math,statistics


def _config_key(row:dict)->tuple[int,int,bool]:
    return int(row['processes']),int(row['kernel_threads']),bool(row.get('use_smt',False))


def select_best_configuration(report: dict, *, locality_tie_fraction: float=0.02) -> dict:
    if not 0 <= locality_tie_fraction <= 0.25:
        raise ValueError('invalid locality tie fraction')
    grouped={}
    for row in report.get('samples',[]):
        key=_config_key(row); grouped.setdefault(key,[]).append(row)
    candidates=[]
    for key,rows in grouped.items():
        if not rows or not all(r.get('numerical_array_exact_equal') is True for r in rows):
            continue
        if not all(r.get('affinity_disjoint') is True for r in rows):
            continue
        walls=[float(r['batch_wall_including_spawn_s']) for r in rows]
        if not walls or any(not math.isfinite(x) or x<=0 for x in walls):
            continue
        cpus=[float(r.get('sum_pair_cpu_s',0.0)) for r in rows]
        cross=max(int(r.get('cross_l3_workers',0)) for r in rows)
        candidates.append(dict(processes=key[0],kernel_threads=key[1],use_smt=key[2],
            median_wall_s=statistics.median(walls),median_pair_cpu_s=statistics.median(cpus),
            cross_l3_workers=cross,repetitions=len(rows)))
    if not candidates:
        raise ValueError('no numerically exact, affinity-valid benchmark configuration')
    fastest=min(candidates,key=lambda r:(r['median_wall_s'],r['cross_l3_workers'],r['processes'],r['kernel_threads']))
    band=fastest['median_wall_s']*(1+locality_tie_fraction)
    tied=[r for r in candidates if r['median_wall_s']<=band]
    best=min(tied,key=lambda r:(r['cross_l3_workers'],r['median_wall_s'],r['median_pair_cpu_s'],r['processes'],r['kernel_threads']))
    best=dict(best)
    if best['median_wall_s']>fastest['median_wall_s'] and best['cross_l3_workers']<fastest['cross_l3_workers']:
        best['selection_reason']='WITHIN_TIE_BAND_PREFER_L3_LOCALITY'
    else:
        best['selection_reason']='FASTEST_MEDIAN_EXACT_CONFIGURATION'
    best['fastest_median_wall_s']=fastest['median_wall_s']
    best['locality_tie_fraction']=locality_tie_fraction
    return best


def host_profile_key(host: dict, build_key: str) -> str:
    if not build_key:
        raise ValueError('empty build key')
    payload={
        'build_key':build_key,
        'cpu_model':host.get('cpu_model'),
        'cpus':host.get('cpus'),
        'topology':host.get('topology'),
        'l3_groups':host.get('l3_groups'),
        'physical_allowed':host.get('physical_allowed'),
        'logical_allowed':host.get('logical_allowed'),
        'quota_cores':host.get('quota_cores'),
    }
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()


def benchmark_configurations(*, physical_budget:int, logical_budget:int, pairs:int=12) -> list[tuple[int,int,bool]]:
    if min(physical_budget,logical_budget,pairs)<1 or logical_budget<physical_budget:
        raise ValueError('invalid benchmark budgets')
    out=[]
    for threads in (1,2,3,4,6,8,12,24,32,48,64):
        if physical_budget%threads==0:
            procs=physical_budget//threads
            if 1<=procs<=pairs:out.append((procs,threads,False))
    if logical_budget>physical_budget:
        for threads in (2,4,6,8,12,16,24,32,48,64):
            if logical_budget%threads==0:
                procs=logical_budget//threads
                if 1<=procs<=pairs:out.append((procs,threads,True))
    return list(dict.fromkeys(out))


def make_tuning_profile(report:dict, *, report_sha256:str, locality_tie_fraction:float=0.02)->dict:
    if len(report_sha256)!=64 or any(c not in '0123456789abcdef' for c in report_sha256.lower()):
        raise ValueError('invalid report sha256')
    host=report.get('host');build_key=report.get('build_key')
    if not isinstance(host,dict) or not build_key:
        raise ValueError('benchmark report lacks host/build identity')
    selected=select_best_configuration(report,locality_tie_fraction=locality_tie_fraction)
    return {
        'schema':'WU088_HOST_TUNING_PROFILE_V1',
        'host_build_key':host_profile_key(host,str(build_key)),
        'source_report_sha256':report_sha256,
        'selected':selected,
        'numerical_contract':'EXACT_ARRAY_EQUALITY_REQUIRED_FOR_ALL_SELECTED_SAMPLES',
        'promotion_scope':'HOST_TUNING_ONLY__NATIVE_PROVIDER_NOT_AUTOMATICALLY_PROMOTED',
    }


def validate_tuning_profile(profile:dict, host:dict, build_key:str)->None:
    if profile.get('schema')!='WU088_HOST_TUNING_PROFILE_V1':
        raise ValueError('unsupported tuning profile schema')
    if profile.get('host_build_key')!=host_profile_key(host,build_key):
        raise ValueError('host/build identity mismatch')
    s=profile.get('selected',{})
    if not all(isinstance(s.get(k),int) and s[k]>0 for k in ('processes','kernel_threads')):
        raise ValueError('invalid selected configuration')
    if s.get('repetitions',0)<1:
        raise ValueError('selected configuration has no benchmark repetitions')


def representative_pairs(costs:dict[tuple[int,int],float])->list[tuple[int,int]]:
    if len(costs)<3:
        raise ValueError('need at least three pair costs')
    rows=[]
    for key,value in costs.items():
        pair=(int(key[0]),int(key[1]));value=float(value)
        if not math.isfinite(value) or value<=0:
            raise ValueError('invalid representative-pair cost')
        rows.append((value,pair))
    rows.sort(key=lambda x:(x[0],x[1]))
    idx=[0,len(rows)//2,len(rows)-1]
    return [rows[i][1] for i in idx]
