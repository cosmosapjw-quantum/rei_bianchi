"""Resume metadata audit after inventory; never repeat inventory or science."""
import ast
from pathlib import Path
src=Path('/tmp/wu088_r31an_preflight.py').read_text()
tree=ast.parse(src)
nodes=[]
for node in tree.body:
    if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef)):
        nodes.append(node)
    elif isinstance(node,ast.Assign) and all(isinstance(t,ast.Name) and t.id in ('ROOT','OUT','RUN','ARC','ENV') for t in node.targets):
        nodes.append(node)
ns={}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'/tmp/wu088_r31an_preflight.py','exec'),ns)
out=ns['OUT']
ns['baseline']={k:tuple(v) for k,v in ns['json'].loads((out/'RUNTIME_METADATA_BEFORE.json').read_text()).items()}
ns['authority']=ns['json'].loads((out/'SOURCE_AUTHORITY.json').read_text())['sources']
inv=ns['json'].loads((out/'LOCAL_ARCHIVE_ORDER_INVENTORY.json').read_text())
for key,a in [('target_paths','target_paths'),('metadata_hits','target_identity_metadata'),('archives','archives'),('errors','errors')]:ns[key]=inv[a]
exec(compile('prereg=json.loads('+src.split('prereg=json.loads(',1)[1],'/tmp/wu088_r31an_preflight.py:after-inventory','exec'),ns)
