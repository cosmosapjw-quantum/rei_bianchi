"""Intake boundary for the delivered HE-F3 domain gate; no rate evaluation."""


def intersection(*windows):
    lower = max(window[0] for window in windows)
    upper = min(window[1] for window in windows)
    return None if lower > upper else [lower, upper]


def validate_gate(gate):
    """Validate this pinned contract, leaving changed models for a new intake."""
    expected = {
        "schema": "bass-he.he-f3.domain-gate.v1",
        "status": "WAIT_REI_F09_RESULT",
        "active_FT03_model": "REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1",
        "KF96_domain_K": [1000, 10000000],
        "GM25_domain_K": [200, 10000],
        "active_FT03_domain_K": [30000, 110000],
        "null_intersection_means": "empty set, not missing data",
    }
    for key, value in expected.items():
        if key not in gate or type(gate[key]) is not type(value) or gate[key] != value:
            raise ValueError(f"changed or missing contract: {key}")
        if isinstance(value, list) and any(type(x) is not int for x in gate[key]):
            raise ValueError(f"noninteger temperature window: {key}")
    kf, gm, ft03 = (gate[k] for k in ("KF96_domain_K", "GM25_domain_K", "active_FT03_domain_K"))
    derived = {
        "pair_common_domain_K": intersection(kf, gm),
        "intersection_FT03_KF96_K": intersection(ft03, kf),
        "intersection_FT03_GM25_K": intersection(ft03, gm),
        "intersection_FT03_pair_K": intersection(ft03, kf, gm),
    }
    for key, value in derived.items():
        if key not in gate or type(gate[key]) is not type(value) or gate[key] != value:
            raise ValueError(f"intersection mismatch: {key}")
    return {"status": "WAIT_REI_F09_RESULT", "paired_domain": derived["intersection_FT03_pair_K"],
            "physical_admission": False, "current_FT03_paired_campaign_admissible": False,
            "reason": "empty common source/model domain; OFF/KF96 is not a paired-source result"}
