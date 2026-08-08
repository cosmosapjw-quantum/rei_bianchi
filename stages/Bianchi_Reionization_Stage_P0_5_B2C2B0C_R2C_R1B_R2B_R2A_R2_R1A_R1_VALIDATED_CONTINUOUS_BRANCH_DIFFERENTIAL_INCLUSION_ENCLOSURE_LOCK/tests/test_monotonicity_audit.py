from pathlib import Path
import importlib.util, sys

HERE = Path(__file__).resolve().parents[1] / "analysis"


def load(name):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_canonical_jacobian_has_robust_sign_reversal_excluding_constant_orthant():
    mod = load("monotonicity_audit")
    result = mod.run_audit(Path(__file__).resolve().parents[3])
    assert result["constant_diagonal_orthant_excluded"] is True
    witness = result["witness"]
    assert witness["input_coordinate"] == "x_HII"
    assert witness["output_coordinate"] == "log_T"
    assert witness["low_node"]["temperature_K"] < 3000.0
    assert witness["high_node"]["temperature_K"] > 50000.0
    assert witness["low_node"]["derivative"] < -1.0e-14
    assert witness["high_node"]["derivative"] > 1.0e-12
    assert witness["low_node"]["relative_eps_consistency"] < 1.0e-5
    assert witness["high_node"]["relative_eps_consistency"] < 1.0e-5
