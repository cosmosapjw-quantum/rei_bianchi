"""Replay the unchanged oracle while measuring every live cached/active abscissa."""
import mpmath as mp, runpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rule=mp.mp._tanh_sinh
original=rule.get_nodes
previous=[]
record={'max_live_distinct_abscissae':0,'calls':0,'cap':4096,'complete':False}
def get_nodes(*args,**kwargs):
 global previous
 nodes=original(*args,**kwargs)
 sites={x._mpf_ for x,w in nodes}
 sites.update(x._mpf_ for x,w in previous)
 previous=nodes
 for collection in (rule.standard_cache,rule.transformed_cache):
  for seq in collection.values():sites.update(x._mpf_ for x,w in seq)
 record['calls']+=1;record['max_live_distinct_abscissae']=max(record['max_live_distinct_abscissae'],len(sites))
 if len(sites)>4096:
  (ROOT/'ORACLE_SITE_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n')
  raise RuntimeError('Oracle quadrature-site limit exceeded; preserve partial audit')
 return nodes
rule.get_nodes=get_nodes
runpy.run_path(str(ROOT/'oracle.py'),run_name='__main__')
record['complete']=True
(ROOT/'ORACLE_SITE_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
