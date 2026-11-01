#!/usr/bin/env python3
"""Run the original sealed NumPy interval source via its import-only JAX stub."""
import importlib.util,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
stage=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
       "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")
file=root/"stages"/stage/"analysis"/"jax_import_guard.py"
spec=importlib.util.spec_from_file_location("physical_import_only_guard",file)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
if not m.install_if_missing():raise RuntimeError("original runtime requires JAX absent")
sys.argv=[str(Path(__file__).resolve().with_name("probe_nonlinear.py")),*sys.argv[1:]]
runpy.run_path(sys.argv[0],run_name="__main__")
