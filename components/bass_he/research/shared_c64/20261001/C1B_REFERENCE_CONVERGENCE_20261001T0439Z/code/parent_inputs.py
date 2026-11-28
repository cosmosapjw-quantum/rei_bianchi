"""Bind sibling or bundled parent inputs to immutable C1 byte identities."""
from pathlib import Path
import hashlib
EXPECTED={
'evidence/C1_SINGLE_POINT_PILOT.json':'71153e5770848716694a790453a7f814e04ed92cbe076e0694bdae9e619e14ce',
'code/partialwave.py':'0253d072d3c1a4e359949ad0112828baa9246ded5885d4a6aefdbb30b01a61f8'}
def resolve_parent(root):
    parent=Path(root).parent/'BASS_HE_C1_ELECTRONIC_ARCHITECTURE_20261001_v1'
    if not parent.exists():parent=Path(root)/'private_dependencies/C1_PARENT_PUBLIC_SNAPSHOT'
    for rel,expected in EXPECTED.items():
        path=parent/rel
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('parent input byte identity mismatch: '+rel)
    return parent
