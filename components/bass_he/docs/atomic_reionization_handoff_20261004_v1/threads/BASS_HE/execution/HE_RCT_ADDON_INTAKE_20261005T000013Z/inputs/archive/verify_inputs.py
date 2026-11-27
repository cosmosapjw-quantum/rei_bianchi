#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=root/'inputs/VENDOR_SHA256.json'
for name,expected in json.loads(manifest.read_text()).items():
 path=root/'vendor/rei_microphysics'/name
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
  raise SystemExit('INPUT_IDENTITY_MISMATCH: '+name)
print('Pinned vendor byte identity verified.')
