import os,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get('B3_TEST_INSTALLED',str(ROOT/'src')))
@pytest.fixture
def request_data():
    return {
       'schema':'bass-he.atomic-request.v1',
       'source_id':'GM25_W82_RCX_CONSTANT_200_10000_K_V1',
       'temperature_K':['200','1000','10000'],
       'distribution':'MAXWELL_COMMON_T_ZERO_DRIFT',
       'isotope_basis':'SOURCE_W82_4HE_H', 'initial_state':'H1s',
       'relative_drift_m_s':'0','radiation_model':'SPONTANEOUS_SINGLE_PHOTON',
       'acknowledge_source_conflict':True,'unit':'m3 s-1',
       'quantity':'event_count_coefficients'}
@pytest.fixture
def root():return ROOT
