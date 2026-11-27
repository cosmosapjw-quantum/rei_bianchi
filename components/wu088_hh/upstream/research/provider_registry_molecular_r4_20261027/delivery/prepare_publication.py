"""Create an exact Git-tree payload from the reviewed staged R4 diff."""
import argparse,base64,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--expected-parent',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def git(*v):return subprocess.check_output(['git',*v])
head=git('rev-parse','HEAD').decode().strip();assert head==a.expected_parent
base=git('rev-parse','HEAD^{tree}').decode().strip();tree=git('write-tree').decode().strip()
paths=[x for x in git('diff','--cached','--name-only','-z').decode().split('\0') if x]
assert paths and all(x=='AGENTS.md' or x.startswith('research/provider_registry_molecular_r4_20261027/') for x in paths)
entries=[];blobs=[];records=[]
for name in paths:
 data=git('show',':'+name);mode,blob,stage=git('ls-files','-s','--',name).decode().split('\t')[0].split();assert stage=='0'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob
 item={'path':name,'mode':mode,'type':'blob'}
 try:content=data.decode('utf-8')
 except UnicodeDecodeError:blobs.append({'path':name,'sha':blob,'encoding':'base64','content':base64.b64encode(data).decode()});item['sha']=blob
 else:
  if len(data)>200000:blobs.append({'path':name,'sha':blob,'encoding':'utf-8','content':content});item['sha']=blob
  else:item['content']=content
 entries.append(item);records.append({'path':name,'mode':mode,'git_blob_sha1':blob,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
obj={'repository_full_name':'cosmosapjw-quantum/WU088_HH','branch_name':'research/provider-registry-20261025','expected_parent':head,'base_tree_sha':base,'expected_tree_sha':tree,'tree_elements':entries,'blobs_to_create':blobs,'files':records}
a.output.parent.mkdir(exist_ok=True);a.output.write_text(json.dumps(obj,ensure_ascii=False))
print(json.dumps({'parent':head,'base_tree':base,'expected_tree':tree,'files':len(records),'new_blob_objects':len(blobs),'payload_bytes':a.output.stat().st_size,'payload':str(a.output)}))
