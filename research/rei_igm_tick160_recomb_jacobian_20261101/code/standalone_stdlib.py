#!/usr/bin/env python3
"""Minimal executable read-only REI tick160 HII source moment, no external packages.

Usage: python standalone_stdlib.py path/to/REI_PR320_ORIGINAL_TICK160_NODE_PHYSICS.zip
Source: original public REI PR320 Actions artifact sha256 48ad5c6f...120a7.
Hui-Gnedin 1997 HII Case A/B fits are an external conditional diagnostic, not
an implementation of the original 26-event REI source or the first-interval IVP.
"""
import csv, gzip, hashlib, io, json, math, pathlib, statistics, sys, zipfile
ORIGINAL_SHA='48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7'
STATE_SHA='cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01'
LANE='LOCAL_NEUTRAL_HAZARD_PRIMARY'
N=46080

def alpha(T,case):
    lam=315614./T
    if case=='A':return 1.269e-13*lam**1.503/(1+(lam/.522)**.470)**1.923
    if case=='B':return 2.753e-14*lam**1.5/(1+(lam/2.740)**.407)**2.242
    raise ValueError(case)

def compute(filename):
    path=pathlib.Path(filename)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ORIGINAL_SHA:raise ValueError('original GitHub ZIP SHA mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError('ZIP CRC failure')
        meta=json.loads(z.read('ORIGINAL_H_HE_T_ENERGY.json'))
        assert meta['original_accepted_tick']==160 and meta['original_total_ticks']==131072
        assert len(meta['physical_states'])==3 and all(s['state_array_sha256']==STATE_SHA for s in meta['physical_states'])
        fn='NODEWISE_'+LANE+'_46080_PHYSICAL.csv.gz'
        with gzip.open(io.BytesIO(z.read(fn)),'rt',encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
    if len(rows)!=N:raise ValueError('original node count changed')
    data={k:[] for k in ['T','H','E','U']}
    bounds={k:[] for k in ['A_lo','A_hi','B_lo','B_hi']}
    measures={'A':[],'B':[]}
    for i,r in enumerate(rows):
        if int(r['node'])!=i or r['lane']!=LANE:raise ValueError('node order or lane mismatch')
        pairs=[tuple(map(float,(r[f'{col}_lo'],r[f'{col}_hi'])))
                for col in ['T_K','x_HII','xe_per_H','U_thermal_erg_per_H']]
        if any(not math.isfinite(x) or not math.isfinite(y) or x<=0 or x>y for x,y in pairs):
            raise ValueError('invalid original interval')
        (tlo,thi),(hlo,hhi),(elo,ehi),(ulo,uhi)=pairs
        t,h,e,u=[(x+y)/2 for x,y in pairs]
        for name,val in zip(data,(t,h,e,u)):data[name].append(val)
        for case in ('A','B'):
            measures[case].append(alpha(t,case)*e*h)
            bounds[case+'_lo'].append(alpha(thi,case)*elo*hlo)
            bounds[case+'_hi'].append(alpha(tlo,case)*ehi*hhi)
    ave={x:statistics.fmean(y) for x,y in data.items()}
    cases={}
    for case in ('A','B'):
        m=statistics.fmean(measures[case])
        ml=statistics.fmean(bounds[case+'_lo']);mu=statistics.fmean(bounds[case+'_hi'])
        mf=alpha(ave['T'],case)*ave['H']*ave['E']
        cases[case]={'moment_cm3_s':m,'meanfield_cm3_s':mf,'ratio':m/mf,
                     'moment_interval_cm3_s':[ml,mu]}
    out={'source_artifact_sha256':ORIGINAL_SHA,'physical_nodes':N,'HII_mean':ave['H'],
         'electron_per_H_mean':ave['E'],'T_mean_K':ave['T'],'cases':cases,
         'central_DAG':'28/88_REPORTED','canonical_delta':0,'new_IVP':0,
         'scope':'equal-node source-conditional diagnostic, not original nonlinear 26-event or a cosmological averaged recombination rate'}
    assert abs(out['cases']['A']['ratio']-1.9375156502404693)<2e-12
    assert abs(out['cases']['B']['ratio']-2.256565410424417)<2e-12
    return out

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python standalone_stdlib.py original_PR320_artifact.zip')
    print(json.dumps(compute(sys.argv[1]),indent=2,sort_keys=True))
