"""Root-authorized C9-01 reserve: one named test, no full-suite replay."""
import sys
import unittest
from test_ccc_exchange import Controls

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Controls('test_05_extreme_scales')]))
    sys.exit(0 if result.wasSuccessful() else 1)
