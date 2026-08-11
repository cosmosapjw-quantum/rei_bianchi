#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
def load():
 p=HERE/'interval_discrete_map.py';s=importlib.util.spec_from_file_location('crosssite_partition_case',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--partition',type=int,required=True);ap.add_argument('--lane',default='LOCAL_NEUTRAL_HAZARD_PRIMARY');ap.add_argument('--output',required=True);a=ap.parse_args();m=load();t=time.perf_counter();r=m.run_lane(REPO,lane=a.lane,partition=a.partition)
 row={'partition':a.partition,'classification':r.classification,'certified':r.certified,'widths':r.public_widths,'table_event':r.table_event,'validated_local_error_bounds':r.diagnostics.get('validated_local_error_bounds',{}),'maximum_validated_local_error':r.diagnostics.get('maximum_validated_local_error'),'map_enclosed':r.diagnostics.get('map_enclosed',False),'elapsed_s':time.perf_counter()-t}
 Path(a.output).write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print(json.dumps(row,indent=2));raise SystemExit(0 if r.certified else 1)
