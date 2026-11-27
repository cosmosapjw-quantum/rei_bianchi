from pathlib import Path
from decimal import Decimal
import csv, json, os, subprocess, sys, tempfile
import pytest
from bass_he_liu import load_dataset, ContractError, SourceUnavailable
from bass_he_liu.products import audit, write_json_create_only, write_long_csv_create_only
ROOT=Path(__file__).resolve().parents[1]

def data():return load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')
def report():return audit(data(),json.loads((ROOT/'provenance/parent_CHANNEL_ENERGY_COVERAGE.json').read_text()))

def test_complete_actual_census_and_native_coverage():
    a=report()
    assert a['raw_channels']==27 and a['native_values']==743
    assert a['explicit_missing_values']==6 and a['structural_padding_pairs']==1
    assert a['beyond_paper_upper_values']==54 and a['in_paper_values']==689
    assert a['native_source_lookup_ready'] and not a['full_physical_source_ready']

def test_all_catalog_entries_kept_with_direct_derived_and_missing_status():
    a=report()
    assert len(a['catalog_coverage'])==37
    assert a['catalog_counts']=={'DIRECT_NATIVE':27,'DERIVED_EXACT_SUM':4,'NOT_SUPPLIED':6}
    missing={x['id'] for x in a['catalog_coverage'] if x['status']=='NOT_SUPPLIED'}
    assert missing=={'EXC:1s:n4','EXC:1s:n5','EXC:2s:n5','NR_CX:1s:n4','NR_CX:1s:n5','NR_CX:2s:n5'}

def test_independent_capture_axis_and_total_partial_remainders():
    a=report()
    assert len(a['h1s_capture_cross_axis_disagreement'])==17
    s=a['total_minus_supplied_audit']
    assert [x['matched_native_energies'] for x in s]==[25,29]
    assert all(x['negative_differences']==0 for x in s)
    assert s[0]['classification']=='UNASSIGNED_DIFFERENCE_NOT_IONIZATION_OR_CERTIFIED_HIGH_N'
    v=next(x for x in s[0]['rows'] if Decimal(x['energy'])==100)
    assert Decimal(v['difference'])==Decimal('1.985E-17')
    assert not s[0]['inclusive_completeness_proven']

def test_atomic_json_no_overwrite_and_no_nan(tmp_path):
    p=tmp_path/'a.json';write_json_create_only(p,{'x':1})
    before=p.read_bytes()
    with pytest.raises(FileExistsError):write_json_create_only(p,{'x':2})
    assert p.read_bytes()==before
    with pytest.raises((ValueError,ContractError)):write_json_create_only(tmp_path/'bad.json',{'bad':float('nan')})
    assert not (tmp_path/'bad.json').exists()

def test_long_csv_preserves_all_native_tokens_and_locations(tmp_path):
    d=data();p=tmp_path/'all.csv';write_long_csv_create_only(p,d)
    out=list(csv.DictReader(p.open()))
    assert len(out)==743
    lookup={(r['channel_id'],int(r['source_line'])):r for r in out}
    for c in d.channels.values():
        for s in c.samples:
            r=lookup[(c.id,s.source_line)]
            assert (r['energy_token'],r['sigma_token'])==(s.energy_token,s.value_token)
            assert (int(r['energy_column']),int(r['value_column']))==(s.energy_column,s.value_column)
            assert r['sigma_unit_self_declared']==''
    before=p.read_bytes()
    with pytest.raises(FileExistsError):write_long_csv_create_only(p,d)
    assert p.read_bytes()==before

def test_cli_real_sample_and_expected_failure(tmp_path):
    cmd=[sys.executable,'-B','-m','bass_he_liu','--root',str(ROOT),'sample','NR_CX:1s:1s','100']
    p=subprocess.run(cmd,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['value_token']=='1.15E-17'
    target=tmp_path/'must_not_exist.json'
    p=subprocess.run(cmd[:-1]+['12.25','--out',str(target)],capture_output=True,text=True)
    assert p.returncode==2
    assert 'NOT_A_NATIVE_NODE' in p.stderr
    assert not target.exists()

def test_cli_export_create_only(tmp_path):
    p=tmp_path/'output.json'
    cmd=[sys.executable,'-B','-m','bass_he_liu','--root',str(ROOT),'export','--out',str(p)]
    result=subprocess.run(cmd,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    before=p.read_bytes()
    again=subprocess.run(cmd,capture_output=True,text=True)
    assert again.returncode==2 and p.read_bytes()==before
    assert 'OUTPUT_EXISTS' in again.stderr
