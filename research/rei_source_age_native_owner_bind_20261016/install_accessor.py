"""Add only a task-local read-only node accessor to the scratch native source."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]);here=Path(__file__).resolve().parent
p=root/'rust/rei_microphysics/src/axbi_covariant_transport.rs'
marker=b'// BEGIN RESEARCH_SOURCE_AGE_NODE_ACCESSOR'
raw=p.read_bytes();base=raw.split(marker)[0]
addition=(here/'prepared_node_accessor.rs').read_bytes()
p.write_bytes(base+addition)
(root/'RESEARCH_ACCESSOR_IDENTITY.json').write_text(json.dumps(dict(base_sha256=hashlib.sha256(base).hexdigest(),accessor_sha256=hashlib.sha256(addition).hexdigest(),overlaid_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='read-only original prepared nodes; no coefficient/reconstruction/solver modification'),indent=2)+'\n')
