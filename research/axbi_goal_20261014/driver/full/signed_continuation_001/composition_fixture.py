import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
p=Path('research/axbi_goal_20261014/driver/full/signed_continuation_001')
spec=importlib.util.spec_from_file_location('signed','research/axbi_goal_20261014/driver/full/compose_signed_history.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=p/'composition_fixture';root.mkdir()
c={'old_source_sha256':m.OLD,'current_source_sha256':m.NEW,'decision_sha256':m.DECISION,'review_sha256':m.REVIEW,'relation':'REVIEWED_RESOURCE_ONLY'}
m.verify_epochs(m.OLD,m.NEW,c)
rejected=[]
for old,new,changed in [(m.OLD,'0'*64,c),('0'*64,m.NEW,c),(m.OLD,m.NEW,dict(c,decision_sha256='0'*64))]:
    try:m.verify_epochs(old,new,changed)
    except m.NotReady as e:rejected.append(str(e))
    else:raise AssertionError('third epoch accepted')
counts={}
for name in m.FILES:
    prefix=root/('prefix_'+name);segment=root/('segment_'+name)
    prefix.write_text('case_id,time_s,value\nSHEAR_MINUS,0,2\nSHEAR_MINUS,1,3\n')
    segment.write_text('case_id,time_s,value\nSHEAR_MINUS,1,3\nSHEAR_MINUS,2,4\n')
    counts[name]=m.join_csv(prefix,segment,root/name,1.,'SHEAR_MINUS')
    assert counts[name]=={'original_rows':2,'segment_rows_after_boundary':1,'boundary_rows_removed':1,'composed_rows':3}
    assert len((root/name).read_text().splitlines())==4
m.check_counters({'accepted':'1','attempts':'3','rejections':'0','rhs_evaluations':'21','wall_s':'17'},{'accepted':'2','attempts':'6','rejections':'0','rhs_evaluations':'42','wall_s':'18'},counts['history.csv'])
(root/'RESULT.json').write_text(json.dumps({'status':'PASS_MANUFACTURED_STREAM_JOIN_AND_EXACT_EPOCH_CHECK_ONLY','counts':counts,'negative_cases':rejected,'scientific_admission':'NOT_ISSUED','full_compose_invocations':0},indent=2)+'\n')
print('PASS manufactured five-stream boundary join and exact two-epoch compatibility; third/mismatched epochs rejected')
