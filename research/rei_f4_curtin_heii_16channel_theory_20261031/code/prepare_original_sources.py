#!/usr/bin/env python3
"""Self-contained private-master source extraction with immutable SHA guard."""
import hashlib,pathlib,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
s=root/'private_sources'
archive=s/'REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip'
heii=s/'e-HeII_XSEC_LS.zip'
assert archive.is_file() and heii.is_file(),'Private master requires BOTH original archives'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4'
assert hashlib.sha256(heii.read_bytes()).hexdigest()=='e32f7d22a3dc54e7981e93369bb98ddd38109a784cff608e59e9657b3a3558db'
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for info in z.infolist():
        dest=(s/info.filename).resolve()
        assert dest.is_relative_to(s.resolve()),info.filename
    z.extractall(s)
print('RESTORED original protected PR313 + user-supplied HeII archive, hashes verified')
