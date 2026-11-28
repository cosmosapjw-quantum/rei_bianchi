import sys
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get('B1_TEST_INSTALLED',str(ROOT/'src')))
import pytest
@pytest.fixture
def root(): return ROOT
