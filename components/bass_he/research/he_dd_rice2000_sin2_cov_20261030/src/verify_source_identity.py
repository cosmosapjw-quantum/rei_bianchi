"""PR125 original source bytes lock, copied verbatim (no PDF in Git)."""
from pathlib import Path
import hashlib
import subprocess
root=Path(__file__).resolve().parents[1]
expected={
    'RICE2000_TABLE_I_AUTHORITATIVE.json':'9cdec4449b22bdba2797bbdfb815e98901b85636',
    'RICE2000_TABLE_II_LEGENDRE_FITS.json':'378359462ef0c32ae6c7b5de6105bce9a8f7d8aa',
}
for name,want in expected.items():
    blob=(root/'inputs'/name).read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\x00'+blob).hexdigest()
    assert actual==want,(name,actual,want)
    print('GIT_BLOB_EXACT',name,actual,'SHA256',hashlib.sha256(blob).hexdigest())
