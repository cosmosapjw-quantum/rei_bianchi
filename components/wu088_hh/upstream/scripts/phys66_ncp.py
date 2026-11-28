"""Execute PHYS66 on the current approved host, without SSH-key dependencies."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.phys66_campaign import main
if __name__=='__main__':raise SystemExit(main())
