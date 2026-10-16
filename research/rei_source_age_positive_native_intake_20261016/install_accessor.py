from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]);here=Path(__file__).resolve().parent
src=root/'rust/rei_microphysics/src/axbi_covariant_transport.rs'
raw=src.read_bytes();marker=b'// BEGIN RESEARCH_SOURCE_AGE_NODE_ACCESSOR'
base=raw.split(marker)[0].split(b'// BEGIN RESEARCH_POSITIVE_SOURCE_AGE_ACCESSOR')[0]
old=here.parent/'rei_source_age_native_owner_bind_20261016/prepared_node_accessor.rs'
addition=old.read_bytes()+(here/'positive_accessor.rs').read_bytes()
src.write_bytes(base+addition)
(root/'POSITIVE_ACCESSOR_IDENTITY.json').write_text(json.dumps(dict(base_sha256=hashlib.sha256(base).hexdigest(),suffix_sha256=hashlib.sha256(addition).hexdigest(),modified_sha256=hashlib.sha256(src.read_bytes()).hexdigest()),indent=2)+'\n')
