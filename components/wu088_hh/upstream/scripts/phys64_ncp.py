"""Run PHYS64 directly on the current authorized host; no SSH required."""
import os
import sys
from pathlib import Path
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from wu088_hh.phys64_campaign import main
if __name__=='__main__':sys.exit(main())
