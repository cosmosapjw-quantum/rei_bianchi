import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from reference_base import prepared_sources_complete,reuse_compact


class ReferenceBaseTests(unittest.TestCase):
    def test_compact_archive_can_reuse_only_exact_prepared_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'base';prepared=root/'prepared';scratch=root/'scratch'
            base.mkdir();prepared.mkdir()
            source=b'fixture frozen source\n';(prepared/'source').write_bytes(source)
            identity=json.dumps(dict(outputs={'source':hashlib.sha256(source).hexdigest()})).encode()
            (prepared/'PREPARED_IDENTITY.json').write_bytes(identity)
            (base/'PREPARED_IDENTITY.json').write_bytes(identity)
            binary=b'fixture executable bytes';(base/'positive_native.bin').write_bytes(binary)
            build=dict(exit_code=0,prepared_identity_sha256=hashlib.sha256(identity).hexdigest(),
                       binary_sha256=hashlib.sha256(binary).hexdigest())
            (base/'BUILD_RECEIPT.json').write_text(json.dumps(build))
            self.assertFalse(prepared_sources_complete(base))
            self.assertTrue(prepared_sources_complete(prepared))
            result=reuse_compact(base,prepared,scratch)
            self.assertEqual(result['status'],'REUSED_EXACT_BUILD_BINDING')
            self.assertEqual((scratch/'positive_native.bin').read_bytes(),binary)
            self.assertEqual((prepared/'BUILD_RECEIPT.json').read_bytes(),(base/'BUILD_RECEIPT.json').read_bytes())
            (prepared/'PREPARED_IDENTITY.json').write_bytes(identity+b'\n')
            self.assertEqual(reuse_compact(base,prepared,scratch)['status'],'NOT_REUSED')
            (prepared/'PREPARED_IDENTITY.json').write_bytes(identity)
            (base/'positive_native.bin').write_bytes(b'changed')
            self.assertEqual(reuse_compact(base,prepared,scratch)['status'],'NOT_REUSED')


if __name__ == '__main__':
    unittest.main()
