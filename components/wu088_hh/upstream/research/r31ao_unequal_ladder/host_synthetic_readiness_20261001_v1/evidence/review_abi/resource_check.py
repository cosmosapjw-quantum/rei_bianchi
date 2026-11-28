"""Small refusal checks; no scientific or NumPy input bytes are supplied."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import abi_witness as w


def refuses(call):
    try:
        call()
    except w.Refusal:
        return
    raise AssertionError('expected bounded refusal')


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    small = root / 'four_bytes'
    small.write_bytes(b'1234')
    refuses(lambda: w.Budget(max_total_bytes=3).identity(small, 'synthetic'))
    refuses(lambda: w.Budget(max_files=0).identity(small, 'synthetic'))
    text = w.CappedText(3)
    assert text.write('\u00e9') == 1
    refuses(lambda: text.write('\u00e9'))
    with patch.object(w, 'MAX_OUTPUT_BYTES', 1):
        refuses(lambda: w.collect(root / 'bounded_output'))
    assert list((root / 'bounded_output').iterdir()) == []
print(json.dumps({'status': 'PASS', 'cases': 4, 'checks': [
    'aggregate_identity_bytes', 'identity_file_count', 'utf8_bytes_not_characters',
    'total_output_cap_includes_final_report'], 'actual_HH_payloads_read': 0}))
