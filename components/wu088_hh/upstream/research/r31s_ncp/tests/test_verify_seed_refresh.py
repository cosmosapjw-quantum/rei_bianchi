import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT/'research/r31s_ncp/verify_seed_refresh.py'


def test_prior_and_current_m2_arrays_are_byte_identical(tmp_path):
    out = tmp_path/'refresh.json'
    subprocess.run([sys.executable, str(SCRIPT), '--out', str(out)],
                   check=True, cwd=ROOT, capture_output=True, text=True)
    result = json.loads(out.read_text())
    assert result['status'] == 'ARRAYS_BIT_IDENTICAL_PRIOR_AND_CURRENT_SEED'
    assert [(row['n'], row['g']) for row in result['rows']] == [(160, 80), (192, 80), (32, 20)]
    assert all(part['byte_equal'] for row in result['rows'] for part in row['arrays'].values())
