"""Synthetic child only: prove EOF, emit supplied fabricated record unchanged."""
import sys
from pathlib import Path
if sys.argv[2:]!=['source_rhs','-0.1','8']:raise SystemExit(2)
if sys.stdin.buffer.read()!=b'':raise SystemExit(3)
sys.stderr.write('FAKE_SETUP_ONLY: EOF confirmed; zero derivative requests\n')
sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())
