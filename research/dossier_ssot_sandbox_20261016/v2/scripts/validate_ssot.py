#!/usr/bin/env python3
"""Check machine-readability, DAG acyclicity, actor/source bindings, and preserved gates.
This is a syntactic and contract validator, NOT physics/scientific validation.
"""
import json, csv, sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent; C=R/'contracts'
def read(n):return json.loads((C/n).read_text())
def main():
 d=read('RESEARCH_DAG.json'); nodes=d['nodes']; by={n['id']:n for n in nodes}
 assert len(nodes)==26 and len(by)==26,(len(nodes),len(by))
 assert d['source_proposal_enumerated_nodes']==21
 original={'SYNC-01','SYNC-02','RT-R9_R10','RT-C1_C3','RT-C4_C5','RT-C6_C7','RT-C8','RT-C9_C10','SA-01','SA-02','SA-03','OBS-O5','OBS-O6','LRS-V11','FLRW-CONV','BI-SIGNED','BASS-TAU','ISO-EOS','ISO-COUPLE','ISO-RUN','REL-GATE'}
 assert original<=by.keys() and len(original)==21
 from jsonschema import Draft202012Validator
 Draft202012Validator(read('SCHEMAS.dag.schema.json')).validate(d)
 states={i:0 for i in by}; schedule=[]
 def dfs(k):
  if states[k]==1:raise ValueError('DAG cycle: '+k)
  if states[k]==2:return
  states[k]=1
  for dep in by[k]['depends_on']:
   assert dep in by,(k,dep)
   dfs(dep)
  states[k]=2;schedule.append(k)
 for k in by: dfs(k)
 refs={s['id'] for s in read('SOURCE_REGISTRY.json')['sources']}
 for n in nodes:
  assert set(n['source_refs'])<=refs,n['id']
  assert n['inputs'] and n['outputs'] and n['physics_acceptance'] and n['numerical_acceptance'] and n['execution_budget'],n['id']
  assert set(n['on_pass'])<=by.keys(),n['id']
 cards=[json.loads(l) for l in (C/'TASK_CARDS.jsonl').read_text().splitlines()]
 assert {x['id'] for x in cards}==by.keys()
 state=read('STATE_VARIABLES.json');assert len(state['dossier_17'])==17
 assert sum(s['baryon_number'] for s in state['dossier_17'] if s['nuclear_isotope']=='He3')==9
 owners=read('PROCESS_OWNER_REGISTRY.json')['owners'];assert len(owners)>=8
 assert len({o['process'] for o in owners})==len(owners)
 cols=list(csv.DictReader((C/'CODE_MAP.csv').open()))
 assert len(cols)>=6
 assert d['nodes'][0]['id']=='DOSSIER-V2'
 print(json.dumps({'verdict':'PASS_CONTRACT_STRUCTURE_ONLY','nodes':len(nodes),'user_proposal':len(original),'source_registry':len(refs),'owners':len(owners),'schema_valid':True,'acyclic':True,'topological_order':schedule},ensure_ascii=False))
if __name__=='__main__':main()