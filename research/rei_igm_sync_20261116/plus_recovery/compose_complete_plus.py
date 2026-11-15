"""Admit a complete saved +0.01 history only after exact terminal/source checks.

Inputs private/plus_2.csv, plus_2_checkpoint.txt, plus_2_RETURN.txt and
private/plus_2_info.json must be retrieved after native completion, never live.
No trajectory is calculated by this script. Original raw tails are preserved.
"""
from pathlib import Path
import csv, hashlib, json, math

ROOT=Path(__file__).resolve().parent;P=ROOT/'private'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def digest_ok(p,expected):assert sha(p)==expected,(p,sha(p))

info=json.loads((P/'plus_2_info.json').read_text())
assert info['status']=='NATIVE_COMPLETE_OBSERVED'
assert info['source_identity_sha256']=='d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'
assert info['binary_sha256']=='c16932bdd7a9fdb86c20d9ea3d8b08f897663874e1f1b6e35ea39fa3f2db3263'
for n,expected in {'plus_0.csv':'1f29ed5dd6a7cc0588eceb9cc8748a3f3ab78e94c482f3758fd585f8910c1587','plus_1.csv':'dbe87394cb417ae18c700325a95f8e1ddebf1fed220375c3f4df947c992f66b3','plus_1_checkpoint.txt':'7af4071c8267f349c0a1d106759aa39d5fa47423ecbb76137692d31d1f5f82a2','plus_2.csv':info['history_sha256'],'plus_2_checkpoint.txt':info['checkpoint_sha256'],'plus_2_RETURN.txt':info['return_sha256']}.items():digest_ok(P/n,expected)
terminal=dict(l.split('=',1) for l in (P/'plus_2_RETURN.txt').read_text().splitlines() if '=' in l)
assert terminal['status']=='COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT'
assert terminal['result']=='Ok(())'
assert terminal['case_id']=='SHEAR_PLUS' and float(terminal['a'])==.2
assert int(terminal['starting_accepted'])==240480
cp=(P/'plus_2_checkpoint.txt').read_text().splitlines();v=list(map(float,cp[1].split()));c=list(map(int,cp[2].split()))
assert v[0]==.2 and c[0]==int(terminal['accepted'])
dest=P/'SHEAR_PLUS_composed_002';dest.mkdir(exist_ok=True)
out=dest/'history.csv';assert not out.exists(),'Never overwrite a previously composed history'
inputs=[];last=None;count=0;common_header=None;boundaries=[]
with out.open('wb') as target:
    for index,name in enumerate(['plus_0.csv','plus_1.csv','plus_2.csv']):
        path=P/name
        with path.open('rb') as f:
            header=f.readline();assert header
            if common_header is None:common_header=header;target.write(header)
            else:assert header==common_header
            columns=next(csv.reader([header.decode().strip()]))
            raw_rows=0;kept_rows=0;first=None
            for line in f:
                fields=next(csv.reader([line.decode().rstrip('\r\n')]))
                assert len(fields)==len(columns)
                row=dict(zip(columns,fields));raw_rows+=1
                if first is None:first=row
                assert row['case_id']=='SHEAR_PLUS' and float(row['q_ref'])==.01
                if index==1 and raw_rows>40481:continue
                if index and raw_rows==1:
                    assert row==last,('boundary',index)
                    boundaries.append({'left':index-1,'right':index,'exact_all_columns':True,'a':float(row['a'])});continue
                if last:
                    assert float(row['a'])>float(last['a']) and float(row['time_s'])>float(last['time_s'])
                else:assert float(row['zbar'])==20 and float(row['time_s'])==0
                assert all(math.isfinite(float(x)) for k,x in row.items() if k!='case_id')
                target.write(line);last=row;kept_rows+=1;count+=1
        inputs.append({'path':name,'bytes':path.stat().st_size,'sha256':sha(path),'raw_rows':raw_rows,'added_rows':kept_rows,'first_a':float(first['a'])})
assert inputs[0]['raw_rows']==200001 and inputs[1]['raw_rows']==40528
assert count==c[0]+1 and float(last['zbar'])==4 and float(last['a'])==.2
for k,z in zip(['a','time_s','b','x_HII','x_HeII','x_HeIII'],v[:6]):assert float(last[k])==z,(k,last[k],z)
output_sha=sha(out)
admission={'status':'COMPLETE_COMPOSED_HISTORY','case_id':'SHEAR_PLUS','q_ref':.01,'zbar_start':20.,'zbar_end':4.,'rows':count,'sha256':output_sha,'bytes':out.stat().st_size,'native_terminal_accepted':c[0],'boundary_checks_passed':True,'terminal_checkpoint_matches':True,'original_physics_identity_verified':True}
report={'schema':'rei.axbi.plus_complete_composition.v1','admission':admission,'inputs':inputs,'output_private_path':str(out),'boundary_checks':boundaries,'orphan47rows':'Original plus_1 rows40482..40528 preserved in immutable input but excluded after durable checkpoint240480; replay costs are charged separately.','native_evidence':info,'terminal':terminal,'checkpoint_counters':c,'composition_only':True,'AX11':'UNRESOLVED_NO_REFINEMENT_IMPLIED','scientific_admission':'BASELINE_SAVED_HISTORY_ONLY_NOT_RESOLVED_SIGNED_RESPONSE','canonical_count_delta':0}
(ROOT/'PLUS_COMPLETE_COMPOSITION_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(admission))
