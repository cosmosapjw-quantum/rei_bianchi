from pathlib import Path
import lzma,hashlib,json
root=Path(__file__).resolve().parents[1];t=json.loads((root/'results/CAUSAL_TRANSPORT.json').read_text())
raw=(root/'results'/t['name']).read_bytes();zipraw=lzma.decompress((root/'results'/t['compressed']).read_bytes())
assert raw==zipraw, 'CONTRACT_BYTES_RESTORED'
assert hashlib.sha256(raw).hexdigest()==t['raw_sha256']
assert hashlib.sha256((root/'results'/t['compressed']).read_bytes()).hexdigest()==t['xz_sha256']
print('CAUSAL_18528_TRANSPORT=BYTE_EXACT')
