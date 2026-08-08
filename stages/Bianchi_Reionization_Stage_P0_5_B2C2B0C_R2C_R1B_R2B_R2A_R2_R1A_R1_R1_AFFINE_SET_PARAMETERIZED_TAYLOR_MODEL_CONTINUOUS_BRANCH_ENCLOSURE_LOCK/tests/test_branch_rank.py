from pathlib import Path
import importlib.util, sys

STAGE = Path(__file__).resolve().parents[1]

def load():
    path=STAGE/'analysis/branch_rank.py'
    spec=importlib.util.spec_from_file_location('affine_tm_branch_rank_test',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def test_symbolic_local_determinant_identity():
    m=load()
    residual=m.symbolic_determinant_residual()
    assert residual == 0

def test_source_safe_rank_lower_bound_exceeds_global_two_parameter_model():
    m=load()
    result=m.audit_source_safe_rank(Path(__file__).resolve().parents[3])
    assert result.node_count == 46080
    assert result.robust_rank2_nodes > 45000
    assert result.source_safe_rank_lower_bound > 90000
    assert result.global_parameter_rank == 2
    assert result.rank_deficiency > 90000
    assert result.sparse_quadratic_storage_mib < 16.0
