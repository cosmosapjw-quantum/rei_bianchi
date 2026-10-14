#!/usr/bin/env python3
"""Freeze complete candidate after owner consumption and a single observed replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def rec(p):
    b=p.read_bytes();return {'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
summary=json.loads((ROOT/'report/PHYS29_RESULTS_SUMMARY.json').read_bytes())
assert summary['first_summary']['all_pass'] and summary['replay']['byte_equal'] and summary['replay']['parsed_json_equal']
assert summary['total_execution']['new_main']==2
assert (ROOT/'evidence/OWNER_CANDIDATE_REVIEW.json').is_file()
assert not (ROOT/'independent/DECISION_REVIEW.json').exists()
target=ROOT/'evidence/CANDIDATE_FROZEN.json';assert not target.exists()
exclude={'evidence/CANDIDATE_FROZEN.json','MANIFEST.json','state/CLOSEOUT.json','state/RESEARCH_STATE.md'}
files=[rec(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.relative_to(ROOT).as_posix() not in exclude and '__pycache__' not in p.parts and p.suffix!='.pyc']
obj={'task':'REI-PHYS29-20261011','status':'FROZEN_FOR_DISTINCT_FINAL_NONBLIND_REVIEW',
 'frozen_utc':datetime.now(timezone.utc).isoformat(),'owner':'/root','file_count':len(files),'files':files,
 'science_main_total_at_freeze':2,'new_physical_roots':0,
 'future_additive_files':['independent final reviewer evidence','state/CLOSEOUT.json','state/RESEARCH_STATE.md','MANIFEST.json'],
 'policy':'All listed bytes immutable; no scientific rerun. Actual final decision not preclaimed. Detached archive/Git/delivery receipts follow after gate.'}
target.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'candidate_freeze':rec(target),'payload_count':len(files)},ensure_ascii=False))
