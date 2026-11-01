#!/usr/bin/env python3
"""Run source-owned interval microphysics with its original import-only JAX guard."""
import importlib.util, runpy, sys
from pathlib import Path
here=Path(__file__).resolve().parent
repo=here.parents[1]
stage=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
       "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")
file=repo/"stages"/stage/"analysis"/"jax_import_guard.py"
spec=importlib.util.spec_from_file_location("source_locked_import_guard",file)
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
assert module.install_if_missing(), "original source-only environment must have no installed JAX"
sys.argv=[str(here/"source_26events.py"),*sys.argv[1:]]
runpy.run_path(str(here/"source_26events.py"),run_name="__main__")
