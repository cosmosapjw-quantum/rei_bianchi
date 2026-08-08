from pathlib import Path
import importlib.util,sys
STAGE=Path(__file__).resolve().parents[1]

def load():
 p=STAGE/'analysis/decision.py';s=importlib.util.spec_from_file_location('affine_tm_decision_test',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def test_coherent_auditor_cannot_authorize_source_safe_family_when_rank_and_witness_fail():
 m=load()
 out=m.classify(source_safe_rank_lower_bound=91809,global_parameter_rank=2,adversarial_outside_count=1,coherent_width_max=1e-4,coherent_empirical_residual=1e-10)
 assert out['production_authorized'] is False
 assert out['classification']=='SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED'
 assert out['next_stage']=='SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK'
