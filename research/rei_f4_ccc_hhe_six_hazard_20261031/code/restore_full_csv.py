#!/usr/bin/env python3
"""Restore exact 23040-row physical CSV from a public XZ Git blob."""
from pathlib import Path
import hashlib,lzma
root=Path(__file__).resolve().parents[1]
p=root/'results/CCC_FIRST_COLLISION_CHANNELS_23040.csv.xz'
q=root/'results/CCC_FIRST_COLLISION_CHANNELS_23040.csv'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='c2a0b1e0274fe8fa15cb5db247eb18906b854d34fcc7e6fa234daff6f43dbb23'
data=lzma.decompress(p.read_bytes())
assert hashlib.sha256(data).hexdigest()=='519454641743710090577407b1560ee13f5a1bb90b2784ec8d11af54d77e017a'
q.write_bytes(data)
print('RESTORED',q.name,len(data),'bytes sha256 match')
