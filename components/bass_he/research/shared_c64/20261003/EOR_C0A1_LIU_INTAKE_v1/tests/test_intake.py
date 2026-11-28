from pathlib import Path
import sys, json
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from liu_intake import *
PDF=ROOT/'source/Liu_2024_Chinese_Phys._B_33_083401.pdf'

def test_original_pdf_extracts_15_basis_rows_and_20_levels():
    d=parse_pdf_tables(PDF,PDF_SHA256)
    assert len(d['basis'])==15
    assert len(d['levels'])==20
    row=next(r for r in d['levels'] if r['species']=='HeII' and r['state']=='1s')
    assert row['E_B3_token']=='-2.0000130'
    assert row['E_ref_token']=='-1.9998160'

def test_preserves_basis_tokens_not_float_rounding():
    d=parse_pdf_tables(PDF,PDF_SHA256)
    assert len(d['basis'])==15
    row=next(r for r in d['basis'] if r['basis']=='B3' and r['l']=='g')
    assert (row['alpha_token'],row['beta_token'],row['count'])==('0.01','1.4677',7)

def test_wrong_file_identity_is_rejected():
    with pytest.raises(SourceError,match='SHA256'):
        parse_pdf_tables(PDF,'0'*64)

def test_missing_table_rejected():
    with pytest.raises(SchemaError):parse_text_tables('Table 1. Missing everything')

def test_printed_ground_lower_bound_conflict_is_reported_not_fixed():
    d=parse_pdf_tables(PDF,PDF_SHA256)
    audit=source_audit(d)
    assert len(audit['ground_state_lower_bound_conflicts'])==1
    item=audit['ground_state_lower_bound_conflicts'][0]
    assert (item['species'],item['basis'],item['printed_energy_au'])==('HeII','B3','-2.0000130')
    assert item['deficit_below_bound_au']=='0.0000130'

def test_coverage_37_nonduplicated_quantities():
    c=coverage_registry()
    assert len(c)==37
    assert len({r['id'] for r in c})==37
    assert all(r['numeric_rows']==0 for r in c)

def test_ground_excited_inputs_not_mixable():
    with pytest.raises(SchemaError,match='initial'):
        check_selection(['NR_CX:1s:1s','NR_CX:2s:3s'],coverage_registry())

def test_total_and_partial_double_count_is_rejected():
    with pytest.raises(SchemaError,match='overlap'):
        check_selection(['NR_CX:1s:total','NR_CX:1s:2s'],coverage_registry())

def test_shell_and_subshell_double_count_is_rejected():
    with pytest.raises(SchemaError,match='overlap'):
        check_selection(['NR_CX:1s:n2','NR_CX:1s:2p'],coverage_registry())

def test_missing_channel_is_not_zero():
    with pytest.raises(SourceUnavailable):
        check_selection(['ION:1s:total'],coverage_registry())

def test_energy_table_cannot_export_as_cross_section():
    with pytest.raises(SourceUnavailable):
        export_quantity(parse_pdf_tables(PDF,PDF_SHA256),'cross_section')

def test_unknown_quantity_not_accepted():
    with pytest.raises(SourceUnavailable):
        export_quantity({},'heating_rate')

def test_create_only_output_writes_and_roundtrips(tmp_path):
    p=tmp_path/'data.json';write_json_create_only(p,{'value':'-2.0000130'})
    assert p.is_file()
    assert json.loads(p.read_text())=={'value':'-2.0000130'}

def test_create_only_output_preserves_existing_bytes(tmp_path):
    p=tmp_path/'data.json';p.write_bytes(b'ORIGINAL')
    with pytest.raises(FileExistsError):write_json_create_only(p,{'bad':1})
    assert p.read_bytes()==b'ORIGINAL'

def test_nonfinite_json_is_rejected_without_partial_output(tmp_path):
    p=tmp_path/'bad.json'
    with pytest.raises(ValueError):write_json_create_only(p,{'bad':float('nan')})
    assert not p.exists()
