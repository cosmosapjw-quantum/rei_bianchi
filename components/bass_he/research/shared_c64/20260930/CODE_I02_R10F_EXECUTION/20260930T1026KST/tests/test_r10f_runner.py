import json

import numpy as np
import pytest

from r10f_runner import plan_queries, validate_exact_record, validate_fixed_gk, audit_exact_table
from bass_he.geometry import _gk15_nodes


def test_exact_split_query_counts_and_reuse():
    plan=plan_queries()
    assert len(plan['cutpoint_hex'])==18
    assert len(plan['node_hex'])==255
    assert len(plan['rows'])==1035
    assert sum(row['origin']=='R10C_EXACT_REUSE' for row in plan['rows'])==90
    assert sum(row['origin']=='R10F_NEW_EXACT' for row in plan['rows'])==945
    assert plan['ordered_pair_identity_sha256']==json.load(open(plan['precommit_path']))['ordered_pair_identity_sha256']


def test_record_checks_rho_and_nonnegative_delta():
    row={'branch':'S23','rho':0.125,'rho_hex':float(0.125).hex()}
    good={'rho':0.125,'delta':0.3,'panels':32}
    assert validate_exact_record(row,good)==0.3
    with pytest.raises(ValueError):validate_exact_record(row,{**good,'rho':np.nextafter(.125,1.)})
    with pytest.raises(ValueError):validate_exact_record(row,{**good,'delta':float('nan')})
    with pytest.raises(ValueError):validate_exact_record(row,{**good,'delta':-1.})


def test_fixed_gk_gate_requires_all_90_components_and_no_refinement():
    err=np.zeros(90);total=np.ones(90)
    assert validate_fixed_gk(total,err,evaluations=255,refinements=0)['status']=='PASS'
    err[47]=1e-2
    assert validate_fixed_gk(total,err,evaluations=255,refinements=0)['status']=='R10F_BOUNDARY_SPLIT_GK_UNRESOLVED'
    with pytest.raises(ValueError):validate_fixed_gk(total,np.zeros(90),evaluations=255,refinements=1)


def test_one_ulp_cutpoint_change_changes_exact_node_identity():
    plan=plan_queries()
    cuts=plan['cutpoints']
    i=10
    altered=np.nextafter(cuts[i],np.inf)
    assert cuts[i].hex()=='0x1.eaaaaaaaaaaabp+0'
    assert altered.hex()=='0x1.eaaaaaaaaaaacp+0'
    original=np.sqrt(_gk15_nodes(cuts[i-1]**2,cuts[i]**2))
    changed=np.sqrt(_gk15_nodes(cuts[i-1]**2,altered**2))
    assert any(float(a).hex()!=float(b).hex() for a,b in zip(original,changed))


def test_complete_table_reopens_every_content_addressed_cache_entry():
    audit=audit_exact_table()
    assert audit['status']=='EXACT_CACHE_TABLE_MANIFEST_PASS'
    assert audit['old_exact_pair_reuse']==90
    assert audit['new_exact_pair_count']==945
