import sys
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if os.environ.get('C0A4_TEST_INSTALLED'):
    sys.path.insert(0,os.environ['C0A4_TEST_INSTALLED'])
else:
    sys.path.insert(0,str(ROOT/'vendor/c0a3/src'))
    sys.path.insert(0,str(ROOT/'src'))
import pytest
from bass_he_liu import load_dataset
@pytest.fixture(scope='session')
def root():return ROOT
@pytest.fixture(scope='session')
def data():return load_dataset(ROOT/'raw',ROOT/'vendor/c0a3/provenance/INPUT_LOCK.json')
