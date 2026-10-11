from pathlib import Path
import sys,json,hashlib,traceback
import numpy as np
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2];REPO=Q1B.parents[2]
for d in (HERE,Q1B,Q1B.parent/'n1',Q1B/'c11/precision'):sys.path.insert(0,str(d))
from source_precision_v2 import StableCellSource
from source_precision import _old
from provider import HistoryProvider
from grid_cells import load_grid
from source_cells import CellSource
path=Q1B/'c12/evidence/C2_FULL001/SCHEDULE.json'
schedule=json.loads(path.read_text())
source=StableCellSource(CellSource(HistoryProvider(r=0.),load_grid(Q1B/'GRID_C2.json')))
rows=[]
for event in schedule['hard_event_records']:
    if not any(label['kind']=='SOURCE_BAND_CELL_EDGE' for label in event['labels']):continue
    t=event['time_s'];record=dict(time_s=t,labels=event['labels'])
    try:
        v=source.source(t);_old._snapshot(source,t)
        record.update(status='PASS_EXACT_CONE_AND_ORIGINAL_PAIR',moment_assembly=v['moment_assembly'])
    except Exception as exc:
        record.update(status='FAIL',failure=repr(exc),traceback=traceback.format_exc())
    rows.append(record)
result=dict(schema='rei.c12.new_candidate_source_band_endpoints.v1',source_file_sha256=hashlib.sha256((HERE/'source_precision_v2.py').read_bytes()).hexdigest(),schedule_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),count=len(rows),failed=sum(r['status']=='FAIL' for r in rows),rows=rows,native_calls=0,completed_source_campaign_replays=0,scope='New candidate behavior at source-band hard endpoints only; no global source convergence campaign')
(HERE/'SOURCE_BAND_ENDPOINTS_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('count','failed','native_calls')}))
raise SystemExit(bool(result['failed']))
