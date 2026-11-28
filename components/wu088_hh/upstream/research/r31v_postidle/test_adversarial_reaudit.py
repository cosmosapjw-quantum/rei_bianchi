"""Source-first hostile controls audit. Only archived JSON and synthetic mutations.

No H0Authority construction, native .so load, pool or scientific pair evaluation.
"""
import copy
import importlib
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
m = importlib.import_module('m3_postidle')
OLD = HERE.parent/'r31s_ncp/evidence/ncp_host/20260928T092409Z_18dd6940'
RUN = HERE/'evidence/ncp_host/20260928T132239Z_r31v'


def pilot():
    return json.loads((OLD/'M3_B192_PILOT.json').read_text())


def exact_bundle():
    d = json.loads((OLD/'M3_FULL_PAIR_EQUIVALENCE.json').read_text())
    c = {'h0_binary_sha256': d['h0_binary_sha256'],
         'authority_sources': d['h0_source_sha256'], 'seed_sha256': d['grid_seed_sha256']}
    b = {'build_key': d['foreign_build_key']}
    s = {160: ((3,7),(5,11),(10,11)), 192: ((3,7),(4,10),(10,11))}
    return d, c, b, s


def measurement():
    return json.loads((RUN/'m3b_132.json').read_text())['configs'][0]['repetitions'][0]


def test_actual_pilot_accepted():
    assert m._validate_pilot_receipt(pilot()) == 32454656


@pytest.mark.parametrize('bad', [None, True, [], 'invalid'])
def test_pilot_bad_top_level_is_classified(bad):
    with pytest.raises(ValueError):
        m._validate_pilot_receipt(bad)


@pytest.mark.parametrize('bad', [None, True, [], 'invalid'])
def test_pilot_bad_config_is_classified(bad):
    d = pilot(); d['configurations'] = [bad]
    with pytest.raises(ValueError):
        m._validate_pilot_receipt(d)


@pytest.mark.parametrize('field,value', [
    ('sum_pss_bytes', None), ('sum_pss_bytes', -1),
    ('sum_pss_bytes', float('nan')), ('sum_pss_bytes', True),
    ('sum_pss_bytes', '32454656'), ('sum_pss_bytes', 32454656.0)])
def test_pilot_malformed_pss_is_not_filtered_away(field, value):
    d = pilot(); d['configurations'][0]['warmup'][field] = value
    with pytest.raises(ValueError):
        m._validate_pilot_receipt(d)


def test_pilot_missing_pss_is_not_silently_accepted():
    d = pilot(); del d['configurations'][0]['warmup']['sum_pss_bytes']
    with pytest.raises(ValueError):
        m._validate_pilot_receipt(d)


@pytest.mark.parametrize('field', ['processes', 'threads_per_process'])
def test_pilot_true_is_not_one(field):
    d = pilot(); d['configurations'][0][field] = True
    with pytest.raises(ValueError):
        m._validate_pilot_receipt(d)


def test_actual_exactness_accepted():
    m._validate_exactness_receipt(*exact_bundle())


@pytest.mark.parametrize('mutation', ['component_false','component_delta','missing_components',
    'missing_component','shape','dtype','nonfinite_delta','conflicting_duplicate'])
def test_exactness_detail_cannot_contradict_top_summary(mutation):
    d,c,b,s = exact_bundle(); r=d['rows'][0]
    if mutation=='component_false': r['components']['H0']['exact']=False
    elif mutation=='component_delta': r['components']['H0']['max_abs_delta']=1.
    elif mutation=='missing_components': del r['components']
    elif mutation=='missing_component': del r['components']['foreign_sumabs']
    elif mutation=='shape': r['components']['H0']['shape']=[1]
    elif mutation=='dtype': r['components']['H0']['dtype']='complex128'
    elif mutation=='nonfinite_delta': r['components']['H0']['max_abs_delta']=float('nan')
    else:
        bad=copy.deepcopy(r); bad['all_exact']=False; d['rows'].append(bad)
    with pytest.raises(RuntimeError):
        m._validate_exactness_receipt(d,c,b,s)


@pytest.mark.parametrize('mutation', ['memory_high','memory_oom','swap','missing_events',
    'ancestor_throttle','missing_ancestors','bool_exact','str_exact','nan_wall',
    'zero_wall','nan_rate','wrong_rate','wrong_count','infinite_cpu','missing_swap'])
def test_measurement_bad_observation_rejected_and_checkpointed(mutation):
    row=measurement(); checkpoints=[]; calls=[]
    if mutation=='memory_high': row['memory_events_delta']['high']=1
    elif mutation=='memory_oom': row['memory_events_delta']['oom']=1
    elif mutation=='swap': row['swap_after']=4096
    elif mutation=='missing_events': row['memory_events_delta']=None
    elif mutation=='ancestor_throttle':
        row['ancestor_cpu_deltas']['/sys/fs/cgroup/user.slice']['nr_throttled']=1
    elif mutation=='missing_ancestors': row['ancestor_cpu_deltas']={}
    elif mutation=='bool_exact': row['all_exact']=1
    elif mutation=='str_exact': row['all_exact']='false'
    elif mutation=='nan_wall': row['batch_wall_seconds']=float('nan')
    elif mutation=='zero_wall': row['batch_wall_seconds']=0.
    elif mutation=='nan_rate': row['steady_state_pairs_per_second']=float('nan')
    elif mutation=='wrong_rate': row['steady_state_pairs_per_second']=999.
    elif mutation=='wrong_count': row['tasks_completed']=0
    elif mutation=='infinite_cpu': row['worker_cpu_parallelism']=float('inf')
    elif mutation=='missing_swap': del row['swap_after']
    def measure(): calls.append(1); return copy.deepcopy(row)
    with pytest.raises(RuntimeError):
        m.perform_measured_batches(measure,lambda:None,checkpoints.append,64)
    assert len(calls)==1 and len(checkpoints)==1
    assert checkpoints[0]['measurement_status'] != 'RESOURCE_CHECKS_PASSED_REVIEW_REQUIRED'


def test_all_twelve_archived_rows_remain_acceptable():
    raw=json.loads((RUN/'m3b_132.json').read_text())
    for cfg in raw['configs']:
        it=iter(copy.deepcopy(cfg['repetitions'])); got=[]
        assert len(m.perform_measured_batches(lambda:next(it),lambda:None,
                   got.append,cfg['processes']))==3
        assert len(got)==3


def test_nonfinite_failure_checkpoint_is_valid_json(tmp_path):
    import controls
    row=measurement(); row['batch_wall_seconds']=float('nan')
    out=tmp_path/'failure.json'
    with pytest.raises(RuntimeError):
        m.perform_measured_batches(lambda:row,lambda:None,
            lambda x:controls.atomic_json(out,x,create_only=True),64)
    saved=json.loads(out.read_text())
    assert saved['measurement_status']=='MEASUREMENT_VALIDATION_FAILED'
    assert saved['batch_wall_seconds']=={'__nonfinite_float__':'nan'}


@pytest.mark.parametrize('value', [float('inf'),float('-inf'),float('nan')])
def test_failure_encoding_never_becomes_numeric_result(value):
    row=m._failure_checkpoint({'measurement_status':'REJECTED','value':value})
    assert isinstance(row['value'],dict)
    json.dumps(row,allow_nan=False)
