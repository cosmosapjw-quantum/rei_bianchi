from wu088_hh.r31r import first_discriminator_plan,h_folder_name,next_after_z2

def test_first_discriminator_is_only_z2_and_direct_only():
    p=first_discriminator_plan()
    assert p['parent_failed_interval']==[0.0,8.0]
    assert p['child_interval_under_test']==[0.0,4.0]
    assert p['direct_node']==2.0
    assert p['sibling_node_deferred']==6.0
    assert p['h_orders']==[160,192]
    assert p['od_z']==[2.0] and p['jvp_z']==[2.0]
    assert p['ionic_reuse_cp4']==[2.0]
    assert p['interpolation_evaluated'] is False
    assert p['trajectory_runs']==0

def test_generic_h_folder_uses_binary64_identity():
    assert h_folder_name(192,2.0)=='B192_g80_sunit_z4000000000000000'

def test_depth_first_next_action_is_decision_dependent():
    fail=next_after_z2(z2_interval_pass=False)
    assert fail['preferred_next_direct_node']==1.0
    assert fail['next_allowed_direct_nodes']==[1.0,3.0]
    passed=next_after_z2(z2_interval_pass=True)
    assert passed['next_direct_node']==6.0
