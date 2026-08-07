from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

STAGE=Path(__file__).resolve().parents[1]

def _load():
 p=STAGE/'analysis/benchmark.py'; spec=importlib.util.spec_from_file_location('r2b_r2a_benchmark',p); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m

def test_five_x_speedup_promotes_parity_backend():
 m=_load(); d=m.decide_backend(legacy_seconds=10,candidate_seconds=1.9,legacy_peak_bytes=100,candidate_peak_bytes=90,parity_pass=True)
 assert d.promoted and d.reason=='SPEEDUP_AT_LEAST_5X'

def test_three_x_plus_half_memory_promotes():
 m=_load(); d=m.decide_backend(legacy_seconds=10,candidate_seconds=3,legacy_peak_bytes=100,candidate_peak_bytes=49,parity_pass=True)
 assert d.promoted and d.reason=='SPEEDUP_3X_AND_MEMORY_50_PERCENT'

def test_fast_backend_without_parity_is_never_promoted():
 m=_load(); d=m.decide_backend(legacy_seconds=10,candidate_seconds=.1,legacy_peak_bytes=100,candidate_peak_bytes=1,parity_pass=False)
 assert not d.promoted and d.reason=='PARITY_FAILED'

def test_performance_failure_does_not_change_science_status():
 m=_load(); d=m.decide_backend(legacy_seconds=10,candidate_seconds=6,legacy_peak_bytes=100,candidate_peak_bytes=80,parity_pass=True)
 assert not d.promoted
 assert d.science_authorization_changed is False
