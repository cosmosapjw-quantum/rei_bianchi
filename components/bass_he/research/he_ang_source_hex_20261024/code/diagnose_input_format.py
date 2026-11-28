"""Owner-approved one-shot bounded prefix inspection; not a catalogue retry."""
import json
import lzma
from pathlib import Path

PATH = Path('/workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz')
with open(PATH, 'rb') as raw:
    magic = raw.read(32)
with lzma.open(PATH, 'rb') as decoded:
    prefix = decoded.read(65536)
preview = prefix[:4096]
print(json.dumps({
    'scope': 'HE-ANG-SOURCE-HEX-INTAKE input-format diagnostic, not a catalogue',
    'source_path': str(PATH), 'compressed_file_bytes': PATH.stat().st_size,
    'original_container_first32_hex': magic.hex(), 'original_container_first32_repr': repr(magic),
    'decoded_bytes_read': len(prefix), 'decoded_byte_cap': 65536,
    'decoded_first32_hex': prefix[:32].hex(), 'first4096_repr': repr(preview),
    'leading_lines_from_first4096': [repr(line) for line in preview.splitlines()[:20]],
    'counts_in_decoded_prefix': {'semicolon': prefix.count(b';'), 'LF': prefix.count(b'\n'),
        'CR': prefix.count(b'\r'), 'single_quote': prefix.count(b"'"), 'double_quote': prefix.count(b'"'),
        'backtick': prefix.count(b'`'), 'literal_backslash_n': prefix.count(b'\\n')},
    'sql_executed': False, 'catalogue_completed': False,
    'ionf_availability_inferred': False,
}, indent=2, sort_keys=True))
