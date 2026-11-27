from pathlib import Path
from decimal import Decimal
import csv, io, json, shutil
import pytest
from bass_he_liu import parse_csv, load_dataset, ContractError, SourceUnavailable, DomainError

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'raw'
LOCK=ROOT/'provenance/INPUT_LOCK.json'

def dataset():
    return load_dataset(RAW,LOCK)

@pytest.mark.parametrize('name,channels,values,rows',[
 ('H1s-Capture cross sections.csv',7,195,28),
 ('H1s-Excitation cross sections.csv',5,134,28),
 ('H2s-Capture cross sections.csv',8,232,29),
 ('H2s-Excitation cross sections.csv',7,182,26),
])
def test_real_files_keep_every_value(name,channels,values,rows):
    tab=parse_csv(name,(RAW/name).read_bytes())
    assert len(tab.channels)==channels
    assert sum(len(c.samples) for c in tab.channels)==values
    assert len(tab.rows)==rows

def test_own_capture_axis_not_main_row_axis():
    d=dataset()
    s=d.sample('NR_CX:1s:1s','11.56')
    assert s['value_token']=='2.96E-18'
    assert (s['source_line'],s['energy_column'],s['value_column'])==(6,3,4)
    assert d.sample('NR_CX:1s:total','12.25')['value_token']=='1.37E-15'
    with pytest.raises(SourceUnavailable,match='NOT_A_NATIVE_NODE'):
        d.sample('NR_CX:1s:1s','12.25')

def test_shifted_rows_do_not_shift_high_energy_capture():
    d=dataset()
    assert d.sample('NR_CX:1s:1s','100')['value_token']=='1.15E-17'
    assert d.sample('NR_CX:1s:1s','47.61')['value_token']=='2.34E-17'
    assert d.sample('NR_CX:1s:1s','225',scope='payload_domain')['value_token']=='1.53E-18'

@pytest.mark.parametrize('chan',['2s','2p','3p'])
@pytest.mark.parametrize('energy',['2.25','4'])
def test_explicit_blanks_are_not_zero(chan,energy):
    with pytest.raises(SourceUnavailable,match='MISSING_VALUE'):
        dataset().sample('EXC:1s:'+chan,energy)

def test_structural_padding_not_missing_at_225():
    c=dataset().channels['NR_CX:1s:1s']
    assert len(c.samples)==27 and not c.missing
    assert c.padding_lines==(29,)

def test_extended_raw_support_is_separate_from_paper_scope():
    d=dataset()
    with pytest.raises(DomainError,match='OUTSIDE_PAPER_SCOPE'):
        d.sample('NR_CX:2s:total','225')
    s=d.sample('NR_CX:2s:total','225',scope='payload_domain')
    assert s['outside_paper_stated_range'] and s['value_token']=='5.62E-19'
    with pytest.raises(DomainError,match='OUTSIDE_CHANNEL_SUPPORT'):
        d.sample('NR_CX:2s:total','230',scope='payload_domain')

def test_native_only_no_interpolation_at_200():
    with pytest.raises(SourceUnavailable,match='NOT_A_NATIVE_NODE'):
        dataset().sample('EXC:2s:3s','200')

def test_explicit_context_required_for_sigma_si_conversion():
    d=dataset()
    with pytest.raises(ContractError,match='UNIT_BINDING_REQUIRED'):
        d.sample('EXC:1s:2p','100',unit='m2')
    s=d.sample('EXC:1s:2p','100',unit='m2',accept_contextual_unit=True)
    assert Decimal(s['value'])==Decimal('1.77E-20')
    assert s['unit_binding']=='PDF_CONTEXTUAL_CM2_NOT_CSV_HEADER'
    assert s['value_token']=='1.77E-16'
    assert not s['physical_certificate']

def test_exact_disjoint_sum_not_a_source_total():
    out=dataset().aggregate(['NR_CX:1s:2s','NR_CX:1s:2p'],'100')
    assert Decimal(out['value'])==Decimal('1.946E-17')
    assert out['data_kind']=='DERIVED_EXACT_DISJOINT_SUM'
    assert out['inclusive_all_bound'] is False

@pytest.mark.parametrize('ids',[
 ['NR_CX:1s:total','NR_CX:1s:2s'],
 ['NR_CX:1s:2s','NR_CX:1s:n2'],
 ['NR_CX:1s:1s','NR_CX:1s:n1'],
])
def test_overlap_total_shell_alias_rejected(ids):
    with pytest.raises(ContractError,match='OVERLAPPING'):
        dataset().aggregate(ids,'100')

@pytest.mark.parametrize('ids',[
 ['NR_CX:1s:2s','NR_CX:2s:3s'],
 ['NR_CX:1s:2s','EXC:1s:2s'],
])
def test_incompatible_initial_state_or_process_rejected(ids):
    with pytest.raises(ContractError,match='INCOMPATIBLE'):
        dataset().aggregate(ids,'100')

def test_source_lock_detects_one_changed_byte(tmp_path):
    for f in RAW.glob('*.csv'):shutil.copyfile(f,tmp_path/f.name)
    p=tmp_path/'H2s-Capture cross sections.csv';p.write_bytes(p.read_bytes().replace(b'1.32E-14',b'1.33E-14',1))
    with pytest.raises(ContractError,match='HASH_MISMATCH'):
        load_dataset(tmp_path,LOCK)

@pytest.mark.parametrize('mutation', ['nan','negative','duplicate_energy','wrong_header','ragged'])
def test_csv_semantic_failures(mutation):
    name='H2s-Capture cross sections.csv'
    rows=list(csv.reader((RAW/name).read_text(encoding='utf-8-sig').splitlines()))
    if mutation=='nan':rows[1][1]='NaN'
    elif mutation=='negative':rows[1][1]='-1e-14'
    elif mutation=='duplicate_energy':rows[2][0]=rows[1][0]
    elif mutation=='wrong_header':rows[0][1]='capture_total'
    else:rows[1].pop()
    s=io.StringIO();csv.writer(s).writerows(rows)
    with pytest.raises(ContractError):parse_csv(name,s.getvalue().encode())

def test_missing_energy_with_a_value_rejected():
    p=(RAW/'H1s-Capture cross sections.csv').read_bytes().replace(b'12.25,1.37E-15,11.56,2.96E-18',b'12.25,1.37E-15,,2.96E-18',1)
    with pytest.raises(ContractError,match='MISSING_ENERGY'):
        parse_csv('H1s-Capture cross sections.csv',p)

def test_missing_channel_not_generated_from_residual():
    with pytest.raises(SourceUnavailable,match='UNAVAILABLE_CHANNEL'):
        dataset().sample('ION:1s:total','100')

def test_no_physical_energy_conversion_or_implicit_float_key():
    d=dataset()
    with pytest.raises(ContractError,match='EXACT_ENERGY_TOKEN_REQUIRED'):
        d.sample('NR_CX:1s:1s',100.0)
    with pytest.raises(ContractError,match='ENERGY_AXIS_UNBOUND'):
        d.sample('NR_CX:1s:1s','100',energy_axis='E_cm_eV')
