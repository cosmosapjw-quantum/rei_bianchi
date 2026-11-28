"""One approved prefix-only old/new profile; no availability inference."""
import cProfile
import hashlib
import importlib.util
import io
import json
import lzma
from pathlib import Path
import pstats
import sys
import time
import hex_intake as new

UNIT = Path(__file__).resolve().parents[1]
old_path = UNIT/'evidence'/'execution'/'A1_before'/'pre_A2_hex_intake.py'
spec = importlib.util.spec_from_file_location('hex_pre_a2', old_path)
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)
with lzma.open('/workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz', 'rb') as stream:
    prefix = stream.read(262144)
lines = prefix.split(b'\n')[:-1]  # inspect only completed lines, no EOF assumption
rows = [line.decode('utf-8').strip() for line in lines if line.lstrip().upper().startswith(b'INSERT ')]
report = {'scope': 'A2 prefix parse cost diagnostic only; no availability inference',
          'decoded_bytes_read': len(prefix), 'decoded_cap': 262144,
          'prefix_sha256': hashlib.sha256(prefix).hexdigest(),
          'completed_lines': len(lines), 'literal_rows_profiled': len(rows), 'profiles': {}}
results = {}
for name, module in [('old', old), ('new', new)]:
    profiler = cProfile.Profile()
    started = time.process_time()
    profiler.enable()
    results[name] = [module.parse_insert(row) for row in rows]
    profiler.disable()
    cpu = time.process_time()-started
    text = io.StringIO()
    pstats.Stats(profiler, stream=text).sort_stats('cumulative').print_stats(15)
    report['profiles'][name] = {'cpu_s': cpu, 'cprofile_raw': text.getvalue(),
        'parsed_output_sha256': hashlib.sha256(json.dumps(results[name], separators=(',', ':')).encode()).hexdigest()}
report['exact_outputs_equal'] = results['old'] == results['new']
report['full_source_availability_inferred'] = False
print(json.dumps(report, indent=2, sort_keys=True))
if not report['exact_outputs_equal']:
    raise SystemExit('old/new parse outputs differ')
