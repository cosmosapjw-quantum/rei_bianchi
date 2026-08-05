from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from exact_symbolic_fallback import kkt_symbolic_identities
class ExactFallbackTest(unittest.TestCase):
 def test_kkt_symbolic_identities(self):
  out=kkt_symbolic_identities()
  self.assertTrue(all(out.values()),out)
if __name__=='__main__': unittest.main()
