"""One actual read-only runtime/network probe after a pre-execution typo."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

out = Path(__file__).resolve().parent
receipt = {
    "schema": "rei.run18.runtime-probe.v1",
    "cwd": str(Path.cwd()), "probe_timestamp_unix": time.time(),
    "prior_probe_attempt": {
        "status": "PYTHON_PARSE_FAILED_BEFORE_ANY_EXECUTION",
        "error": "SyntaxError: closing parenthesis ')' does not match opening parenthesis '['",
        "line": "cache_roots list had one surplus parenthesis",
        "native_or_rust_commands_executed": 0,
        "network_requests_executed": 0,
        "remedy": "removed the surplus parenthesis; one actual probe follows",
    },
    "path_tools": {name: shutil.which(name) for name in
        ("rustc", "cargo", "cc", "gcc", "make", "pkg-config")},
    "retained_rust_prefix": {}, "cache_inventory": [], "network_probe": {},
    "new_installer_attachment_used": False, "native_science_calls": 0,
    "scientific_builds": 0,
}
prefix = Path('/tmp/rei_run15_salvage/recovery/toolchain/prefix')
for name in ('rustc', 'cargo'):
    path = prefix / 'bin' / name
    entry = {'path': str(path), 'exists': path.is_file()}
    if path.is_file():
        result = subprocess.run([str(path), '-Vv'], capture_output=True,
                                text=True, timeout=8)
        entry.update(exit_code=result.returncode, stdout=result.stdout,
                     stderr=result.stderr)
    receipt['retained_rust_prefix'][name] = entry
cache_roots = [
    Path('/tmp/rei_run15_salvage/recovery/toolchain/cargo'),
    Path('/tmp/rei_run15_salvage/recovery/cargo_home'),
    Path('/tmp/rei_run15_salvage/postloss_native'),
    Path(os.environ.get('CARGO_HOME', str(Path.home()/'.cargo'))),
]
for root in cache_roots:
    item = {'path': str(root), 'exists': root.exists()}
    if root.is_dir():
        item['top_level_names'] = sorted(p.name for p in root.iterdir())[:30]
        registry = root/'registry'
        item['registry_exists'] = registry.exists()
        if registry.exists():
            item['registry_top_level_names'] = sorted(p.name for p in registry.iterdir())[:20]
    receipt['cache_inventory'].append(item)
url = 'https://crates.io/api/v1/crates/num-rational'
try:
    request = urllib.request.Request(url,
        headers={'User-Agent': 'REI-RUN18-readonly-package-research/1.0'})
    with urllib.request.urlopen(request, timeout=8) as response:
        data = response.read(100000)
        receipt['network_probe'] = {'url': url, 'status': response.status,
            'read_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        with (out/'NUM_RATIONAL_API_PROBE.json').open('xb') as stream:
            stream.write(data)
except Exception as error:
    receipt['network_probe'] = {'url': url,
        'exception_type': type(error).__name__, 'message': str(error),
        'further_attempts': 0}
with (out/'RUNTIME_PROBE.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt, indent=2))
