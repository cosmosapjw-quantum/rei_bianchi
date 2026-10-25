#!/usr/bin/env python3
"""Mechanical assembly only. Authority files are copied without scientific edits.
Config entries: path, frozen (author-confirmed), optional nodes_key.
Each authority's nodes may be a list or repository->list mapping.
"""
import argparse,copy,hashlib,json,pathlib,sys

def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def assemble(root,config):
 nodes=[];authorities=[]
 for entry in config:
  if not entry.get('frozen'):raise ValueError('authority not frozen: '+entry['path'])
  path=root/entry['path'];raw=path.read_bytes();doc=json.loads(raw);group=doc[entry.get('nodes_key','nodes')]
  authorities.append({'path':entry['path'],'sha256':hashlib.sha256(raw).hexdigest(),'document':doc})
  groups=group.items() if isinstance(group,dict) else [(entry.get('repository',doc.get('repository')),group)]
  for repo,items in groups:
   for i,n in enumerate(items):
    nodes.append({'id':n['id'],'repository':n.get('repository',n.get('repo',repo)), 'authority':entry['path'],'authority_pointer':('/'+entry.get('nodes_key','nodes')+'/'+str(repo)+'/'+str(i) if isinstance(group,dict) else '/'+entry.get('nodes_key','nodes')+'/'+str(i)),'contract':copy.deepcopy(n)})
 ids={n['id'] for n in nodes}
 for n in nodes:
  deps=n['contract'].get('depends_on',n['contract'].get('dependencies',[]))
  if not isinstance(deps,list):raise ValueError('dependencies must be a list; author clarification required: '+n['id'])
  n['plan_status']='OWNER_DELIVERY_PENDING' if n['contract'].get('status')=='science_complete_scoped_final_delivery_receipt_pending' else 'OWNER_IN_PROGRESS' if n['contract'].get('status') in {'active_owner_thread','current_unit_selected'} else 'PROPOSED'
  n['local_dependencies']=[];n['external_dependencies']=[]
  conditional=n['contract'].get('conditional_dependencies',{})
  n['conditional_dependencies']=[]
  if isinstance(conditional,dict):
   for condition,values in conditional.items():
    for value in values:n['conditional_dependencies'].append({'condition':condition,'dependency':value,'external':value not in ids})
  for d in deps:
   if isinstance(d,str) and d in ids:n['local_dependencies'].append(d)
   else:n['external_dependencies'].append(d)
 integration_path=root/'rei/INTEGRATION_EDGES.json'
 integration=json.loads(integration_path.read_text()) if integration_path.exists() else None
 if integration is not None:authorities.append({'path':'rei/INTEGRATION_EDGES.json','sha256':hashlib.sha256(integration_path.read_bytes()).hexdigest(),'document':integration})
 return {'integration':integration,'schema':'ORCHESTRATION_DAG_V1','as_of':'2026-10-23','scope':'Frozen authority contracts; mechanical graph and provenance assembly; no execution or scientific admission implied','authorities':authorities,'nodes':nodes}

def validate(dag,root):
 errors=[];nodes=dag['nodes'];ids=[n['id'] for n in nodes];index={n['id']:n for n in nodes}
 if len(ids)!=len(set(ids)):errors.append('duplicate node IDs')
 docs={}
 for a in dag['authorities']:
  p=root/a['path']
  if not p.is_file():errors.append('missing authority source '+a['path']);continue
  if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:errors.append('authority source hash mismatch '+a['path'])
  doc=json.loads(p.read_text());docs[a['path']]=doc
  if doc!=a['document']:errors.append('embedded authority differs '+a['path'])
 for n in nodes:
  doc=docs.get(n['authority'])
  if doc is None:
   errors.append('missing node authority source '+n['authority']);continue
  try:
   src=doc
   for token in n['authority_pointer'].strip('/').split('/'):
    token=token.replace('~1','/').replace('~0','~');src=src[int(token)] if isinstance(src,list) else src[token]
   if src!=n['contract']:errors.append('contract/claim leap: source differs '+n['id'])
   evidence=src.get('input',src.get('sources',src.get('source_refs',src.get('evidence',src.get('entrypoints',src.get('input_sources'))))))
   if not evidence:errors.append('missing authored source references '+n['id'])
  except (KeyError,IndexError,ValueError,TypeError):errors.append('invalid authority pointer '+n['id'])
  for dep in n['local_dependencies']:
   if dep not in index:errors.append('missing local dependency '+str(dep))
 integration=dag.get('integration')
 if integration is not None and integration!=docs.get('rei/INTEGRATION_EDGES.json'):errors.append('integration authority mismatch')
 cross={}
 for edge in (integration or {}).get('edges',[]):
  if edge['from'] not in index or edge['to'] not in index:errors.append('missing integration endpoint '+str(edge))
  cross.setdefault(edge['to'],[]).append(edge['from'])
 active=set();done=set()
 def visit(i):
  if i in active:errors.append('dependency cycle at '+i);return
  if i in done or i not in index:return
  active.add(i)
  for dep in index[i]['local_dependencies']+cross.get(i,[]):visit(dep)
  for dep in index[i].get('conditional_dependencies',[]):
   if not dep['external']:visit(dep['dependency'])
  active.remove(i);done.add(i)
 for i in ids:visit(i)
 return errors
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--config');ap.add_argument('--check');ap.add_argument('--root',default=str(pathlib.Path(__file__).resolve().parents[1]));ap.add_argument('--output',default='assembly/DAG.json');a=ap.parse_args();root=pathlib.Path(a.root)
 if a.config:
  dag=assemble(root,json.loads((root/a.config).read_text()));errors=validate(dag,root)
  if errors:sys.exit('\n'.join(errors))
  dump(root/a.output,dag)
 else:dag=json.loads((root/a.check).read_text());errors=validate(dag,root)
 print(json.dumps({'valid':not errors,'nodes':len(dag['nodes']),'errors':errors},ensure_ascii=False));sys.exit(bool(errors))
