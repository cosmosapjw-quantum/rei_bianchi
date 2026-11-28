import copy
import pytest
from wu088_hh.autotune import select_best_configuration, host_profile_key, benchmark_configurations, make_tuning_profile, validate_tuning_profile, representative_pairs


def host():
    return {
        "cpu_model":"AMD Ryzen 9 5900X",
        "cpus":list(range(12)),
        "topology":{str(i):[0,i] for i in range(12)},
        "l3_groups":[list(range(6)),list(range(6,12))],
        "physical_allowed":12,
        "logical_allowed":24,
    }


def sample(p,t,wall,cross=0,exact=True,use_smt=False,rep=0):
    return {"repetition":rep,"processes":p,"kernel_threads":t,"use_smt":use_smt,
            "batch_wall_including_spawn_s":wall,"numerical_array_exact_equal":exact,
            "affinity_disjoint":True,"cross_l3_workers":cross}


def test_locality_stable_choice_wins_within_two_percent():
    rows=[]
    for rep in range(3):
        rows += [sample(3,4,1.60,cross=1,rep=rep), sample(2,6,1.62,cross=0,rep=rep)]
    best=select_best_configuration({"samples":rows},locality_tie_fraction=0.02)
    assert (best["processes"],best["kernel_threads"]) == (2,6)
    assert best["selection_reason"] == "WITHIN_TIE_BAND_PREFER_L3_LOCALITY"


def test_exactness_failure_disqualifies_configuration():
    rows=[sample(2,6,1.0,exact=False),sample(3,4,1.3,exact=True)]
    best=select_best_configuration({"samples":rows})
    assert (best["processes"],best["kernel_threads"]) == (3,4)


def test_profile_key_binds_host_and_build():
    h=host();a=host_profile_key(h,"build-a");b=host_profile_key(h,"build-b")
    assert a != b
    h2=copy.deepcopy(h);h2["cpu_model"]="different"
    assert host_profile_key(h2,"build-a") != a


def test_benchmark_configs_cover_physical_and_smt_without_oversubscription():
    cfg=benchmark_configurations(physical_budget=12,logical_budget=24,pairs=12)
    assert (2,6,False) in cfg
    assert (3,4,False) in cfg
    assert (2,12,True) in cfg
    assert (6,4,True) in cfg
    assert all(p*t <= (24 if smt else 12) for p,t,smt in cfg)
    assert all(p <= 12 for p,t,smt in cfg)


def test_tuning_profile_is_bound_to_host_build_and_exact_samples():
    h=host();rows=[]
    for rep in range(2):
        rows += [sample(2,6,1.60,cross=0,rep=rep), sample(3,4,1.80,cross=1,rep=rep)]
    report={"host":h,"build_key":"native-build","samples":rows,"schema":"pool"}
    profile=make_tuning_profile(report,report_sha256='c'*64)
    assert profile['schema']=='WU088_HOST_TUNING_PROFILE_V1'
    assert profile['selected']['processes']==2
    validate_tuning_profile(profile,h,'native-build')
    with pytest.raises(ValueError,match='host/build'):
        validate_tuning_profile(profile,h,'changed-build')


def test_representative_pairs_choose_fast_median_and_slow():
    costs={(i,0):float(i+1) for i in range(7)}
    assert representative_pairs(costs)==[(0,0),(3,0),(6,0)]
