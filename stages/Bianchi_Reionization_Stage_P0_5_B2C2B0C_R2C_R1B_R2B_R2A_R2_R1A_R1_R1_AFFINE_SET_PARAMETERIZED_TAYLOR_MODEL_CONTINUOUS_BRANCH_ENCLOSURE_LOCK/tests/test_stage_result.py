from pathlib import Path
import importlib.util,sys
STAGE=Path(__file__).resolve().parents[1]
def test_independent_stage_validator_passes():
 p=STAGE/'analysis/independent_validate.py';s=importlib.util.spec_from_file_location('affine_tm_independent_test',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
 out=m.validate();assert out['status']=='PASS';assert out['rank_lower_bound']>90000
