from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
if not os.environ.get('B5C2_INSTALLED'):
 sys.path.insert(0,str(ROOT/'src'))
 for n in ('b5a','b5b','b5b2','b5c'):sys.path.append(str(ROOT/'vendor'/n/'src'))
