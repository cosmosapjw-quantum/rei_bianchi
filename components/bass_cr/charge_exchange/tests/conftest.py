"""Expose the byte-preserved upstream standalone package for monorepo test collection."""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
