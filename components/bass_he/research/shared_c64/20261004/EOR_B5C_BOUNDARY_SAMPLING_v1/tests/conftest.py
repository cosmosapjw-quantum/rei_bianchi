import os,sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1]
if os.getenv('B5C_INSTALLED'):
 sys.path.insert(0,os.environ['B5C_INSTALLED'])
else:
 for x in ('vendor/b5a/src','vendor/b5b/src','vendor/b5b2/src','src'):sys.path.insert(0,str(ROOT/x))
