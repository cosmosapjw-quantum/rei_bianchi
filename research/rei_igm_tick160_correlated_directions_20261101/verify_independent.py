#!/usr/bin/env python3
"""Independent no-import archival verifier, NOT a scientific acceptance gate."""
import argparse,csv,gzip,hashlib,io,json,math,zipfile
from collections import defaultdict
from pathlib import Path

LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
CASES=('center','logT_minus','logT_plus','HII_minus','HII_plus','HeII_minus','HeII_plus','HeIII_minus','HeIII_plus')
SOURCE='a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b'
KERNEL='579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644'


def audit_zip(archive):
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, 'zip CRC failed'
        members={x: z.read(x) for x in z.namelist()}
    jfiles=[x for x in members if x.endswith('RESULT.json')]
    assert len(jfiles)==1, jfiles
    result=json.loads(members[jfiles[0]])
    lane=result['lane'];assert lane in LANES
    assert result['original_archive_sha256']==SOURCE
    assert result['original_kernel_sha256']==KERNEL
    assert result['original_accepted_tick']==160 and result['original_total_ticks']==131072
    assert result['new_canonical_nodes']==0 and result['original_gate']==.0002
    assert result['source_parent_type'] if 'source_parent_type' in result else result['scope']
    assert len(result['cases'])==9 and result['successful_candidate_points']==9
    assert set(x['name'] for x in result['cases'])==set(CASES)
    assert result['overall']=='SCOPED_POINT_SCIENCE_COMPLETE'
    paths=[x for x in members if x.endswith('.csv.gz')]
    assert len(paths)==1
    raw=members[paths[0]]
    assert hashlib.sha256(raw).hexdigest()==result['csv_sha256']
    counts=defaultdict(int);maxima=defaultdict(lambda:0.0)
    with gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb') as gz, io.TextIOWrapper(gz,encoding='utf8',newline='') as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames is not None
        for row in reader:
            c=row['case'];assert c in CASES
            n=int(row['node']);assert 0<=n<46080
            assert counts[c]<=n, ('nonmonotone index',c,n)
            counts[c]+=1
            for x in ['parent_xHII','parent_xHeII','parent_xHeIII']:
                assert 0<=float(row[x])<=1.000001
            assert float(row['parent_T_K'])>0
            for key in ('logT','xHII','xHeII','xHeIII'):
                x=float(row[f'{key}_D_absupper'])
                assert math.isfinite(x) and x>=0
                lo=float(row[f'{key}_D_lo']);hi=float(row[f'{key}_D_hi']);cent=float(row[f'{key}_D_center_est'])
                assert lo<=hi and abs(cent)<=x+1e-10
                maxima[(c,key)]=max(maxima[(c,key)],x)
    assert len(counts)==9 and all(counts[x]==46080 for x in CASES),counts
    for case in result['cases']:
        for obs,value in case['observables'].items():
            ref=value['max_independent_output_box_upper']
            got=maxima[(case['name'],obs)]
            assert abs(ref-got)<max(1e-13,abs(ref)*1e-12),(case['name'],obs,got,ref)
    return dict(lane=lane,sha256=hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
                rows=sum(counts.values()),candidate_cases=9,source_sha256=SOURCE,
                original_status='BLOCKED_MINIMUM_STEP',canonical_delta=0,
                max_logT_9_candidates=max(maxima[(case,'logT')] for case in CASES),
                direction_summary=result['directional_secants'],
                result=result)


def main():
    p=argparse.ArgumentParser();p.add_argument('artifacts',nargs=3,type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    reports=[audit_zip(z) for z in a.artifacts]
    assert set(x['lane'] for x in reports)==set(LANES)
    base=max(x['max_logT_9_candidates'] for x in reports)
    summary=dict(schema='REI_26EVENT_DIRECTIONAL_INDEPENDENT_READBACK_V1',
                 results=reports,all_three_lanes=True,total_labelled_rows=sum(x['rows'] for x in reports),
                 true_spatial_nodes=46080,nine_physical_candidate_scenarios=True,
                 max_tested_candidate_logT_box_upper=base,
                 original_strict_error_limit=2e-4,
                 all_nine_candidate_points_below_gate=base<2e-4,
                 interpretation='sampled physically positive nuclei-conserving points only; NOT whole physical parent X or shared-source rigorous Jacobian/remainder',
                 central_dag='28/88',working_dag='33/88',canonical_delta=0,tick161_admitted=False)
    a.output.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('results',)},indent=2))

if __name__=='__main__':main()
