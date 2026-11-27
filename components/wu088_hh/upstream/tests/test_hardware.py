import pytest
from wu088_hh.hardware import select_resources, partition_affinity_groups, read_linux_cpu_metadata


def topology():
    return {i:(0,i%4) for i in range(8)}


def test_affinity_and_physical_core_selection():
    r=select_resources(topology(),{1,2,5,6},None,requested_workers=12)
    assert r['cpus']==[1,2]
    assert r['workers']==2
    assert r['logical_allowed']==4


def test_fractional_quota_caps_total_workers_times_threads():
    r=select_resources(topology(),set(range(8)),2.5,requested_workers=12)
    assert r['workers']==2
    with pytest.raises(ValueError,match='budget'):
        select_resources(topology(),set(range(8)),2.5,requested_workers=2,kernel_threads=2)


def test_package_core_pair_avoids_multisocket_collision():
    r=select_resources({0:(0,0),1:(1,0)},{0,1},None,requested_workers=12)
    assert r['workers']==2


def test_subcore_quota_keeps_one_worker_and_reports_limit():
    r=select_resources(topology(),set(range(8)),0.5,requested_workers=12)
    assert r['workers']==1
    assert r['quota_cores']==0.5


def test_smt_only_when_explicit_and_no_empty_affinity():
    r=select_resources(topology(),set(range(8)),None,requested_workers=8,use_smt=True)
    assert r['workers']==8
    with pytest.raises(ValueError):
        select_resources(topology(),set(),None)


def zen3_topology():
    topo={}
    l3={}
    for core in range(12):
        ccd=0 if core<6 else 1
        for smt in range(2):
            cpu=core+12*smt
            topo[cpu]=(0,core)
            l3[cpu]=ccd
    return topo,l3


def test_two_by_six_physical_groups_follow_ccd_boundaries():
    topo,l3=zen3_topology()
    groups=partition_affinity_groups(topo,set(topo),workers=2,kernel_threads=6,use_smt=False,l3_by_cpu=l3)
    assert groups == [set(range(0,6)),set(range(6,12))]


def test_two_by_twelve_smt_groups_take_complete_ccds():
    topo,l3=zen3_topology()
    groups=partition_affinity_groups(topo,set(topo),workers=2,kernel_threads=12,use_smt=True,l3_by_cpu=l3)
    assert groups == [set(range(0,6))|set(range(12,18)), set(range(6,12))|set(range(18,24))]


def test_affinity_groups_reject_oversubscription():
    topo,l3=zen3_topology()
    with pytest.raises(ValueError,match='slots'):
        partition_affinity_groups(topo,set(topo),workers=3,kernel_threads=6,use_smt=False,l3_by_cpu=l3)


def test_linux_metadata_reads_smt_and_l3_groups(tmp_path):
    root=tmp_path/'cpu'
    # cpu0/cpu2 are SMT siblings in L3 A; cpu1/cpu3 siblings in L3 B.
    for cpu,sibs,l3 in [(0,'0,2','0,2'),(2,'0,2','0,2'),(1,'1,3','1,3'),(3,'1,3','1,3')]:
        top=root/f'cpu{cpu}'/'topology';top.mkdir(parents=True)
        (top/'thread_siblings_list').write_text(sibs)
        cache=root/f'cpu{cpu}'/'cache'/'index3';cache.mkdir(parents=True)
        (cache/'level').write_text('3')
        (cache/'type').write_text('Unified')
        (cache/'shared_cpu_list').write_text(l3)
    meta=read_linux_cpu_metadata(root,{0,1,2,3})
    assert meta['thread_siblings'][0] == [0,2]
    assert meta['l3_by_cpu'][0] == '0,2'
    assert meta['l3_groups'] == [[0,2],[1,3]]

def test_hardware_module_cli_runs(tmp_path):
    import os,subprocess,sys
    env=dict(os.environ);env['PYTHONPATH']=str(__import__('pathlib').Path(__file__).resolve().parents[1]/'src')
    r=subprocess.run([sys.executable,'-m','wu088_hh.hardware'],env=env,capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    data=__import__('json').loads(r.stdout)
    assert 'l3_groups' in data

def test_smt_worker_groups_keep_sibling_pairs_together():
    topo,l3=zen3_topology()
    groups=partition_affinity_groups(topo,set(topo),workers=4,kernel_threads=6,use_smt=True,l3_by_cpu=l3)
    for g in groups:
        cores={topo[c][1] for c in g}
        assert len(cores)==3
        for core in cores:
            siblings={cpu for cpu in g if topo[cpu][1]==core}
            assert len(siblings)==2
