from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
if os.environ.get('B1_TEST_INSTALLED'):
    sys.path.insert(0,os.environ['B1_TEST_INSTALLED'])
else:
    sys.path.insert(0,str(ROOT/'src'))
