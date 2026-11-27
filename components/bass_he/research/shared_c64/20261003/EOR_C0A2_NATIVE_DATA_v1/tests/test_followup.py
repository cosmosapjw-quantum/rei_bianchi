"""Post-implementation invariants, separate from the 38 observed red/green tests."""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
import csv, io, json, subprocess, sys
import pytest
from bass_he_liu import load_dataset, parse_csv, ContractError, SourceUnavailable, DomainError
from bass_he_liu.native import strict_json
from bass_he_liu.products import write_json_create_only
ROOT=Path(__file__).resolve().parents[1]

def ds():return load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')

def test_source_raw_row_and_column_roundtrip_for_every_nonblank():
    # Independent plain-delimiter reader is applicable because these four files
    # contain neither quoting nor embedded newlines. It does not share layouts.
    n=0
    for tab in ds().tables:
        text=(ROOT/'raw'/tab.name).read_text(encoding='utf-8-sig')
        assert '"' not in text
        lines=[line.split(',') for line in text.splitlines()]
        assert tuple(tuple(x) for x in lines[1:])==tab.rows
        for c in tab.channels:
            for s in c.samples:
                line=lines[s.source_line-1]
                assert line[s.energy_column-1]==s.energy_token
                assert line[s.value_column-1]==s.value_token
                n+=1
    assert n==743

@pytest.mark.parametrize('chan,count',[
 ('NR_CX:1s:n2',28),('NR_CX:1s:n3',28),('NR_CX:2s:n3',29),('NR_CX:2s:n4',29)])
def test_every_derived_shell_sum_with_fraction_oracle(chan,count):
    d=ds();energies=d.available_energies(chan);assert len(energies)==count
    for e in energies:
        result=d.sample(chan,e,scope='payload_domain')
        oracle=sum((Fraction(Decimal(d.sample(c,e,scope='payload_domain')['value_token'])) for c in d.members(chan)),Fraction(0))
        assert Fraction(Decimal(result['value']))==oracle
        assert result['data_kind']=='DERIVED_EXACT_DISJOINT_SUM'

@pytest.mark.parametrize('unit,factor',[('cm2',Decimal(1)),('m2',Decimal('1e-4'))])
def test_every_contextual_unit_conversion(unit,factor):
    d=ds();count=0
    for cid,c in d.channels.items():
        for s in c.samples:
            a=d.sample(cid,s.energy,unit=unit,accept_contextual_unit=True,scope='payload_domain')
            assert Decimal(a['value'])==Decimal(s.value_token)*factor
            assert a['physical_certificate'] is False
            count+=1
    assert count==743

def test_zero_if_explicit_is_not_missing():
    name='H2s-Capture cross sections.csv'
    raw=(ROOT/'raw'/name).read_bytes().replace(b'1.32E-14',b'0.00E-14',1)
    t=parse_csv(name,raw)
    c=next(c for c in t.channels if c.id.endswith('total'))
    assert c.samples[0].value_token=='0.00E-14' and not c.missing

def test_duplicate_json_keys_and_nonfinite_json_rejected():
    for text in ['{"csv":[],"csv":[]}','{"a":NaN}','{"a":Infinity}']:
        with pytest.raises(ContractError):strict_json(text)

def test_all_empty_channel_rejected():
    name='H1s-Excitation cross sections.csv';rows=list(csv.reader((ROOT/'raw'/name).read_text(encoding='utf-8-sig').splitlines()))
    for r in rows[1:]:r[1]=''
    stream=io.StringIO();csv.writer(stream).writerows(rows)
    with pytest.raises(ContractError,match='EMPTY_CHANNEL'):parse_csv(name,stream.getvalue().encode())

def test_source_symlink_rejected(tmp_path):
    for p in (ROOT/'raw').glob('*.csv'):(tmp_path/p.name).symlink_to(p)
    with pytest.raises(ContractError,match='SYMLINK'):
        load_dataset(tmp_path,ROOT/'provenance/INPUT_LOCK.json')

def test_create_only_preserves_symlink_target(tmp_path):
    target=tmp_path/'target';target.write_text('keep');link=tmp_path/'link';link.symlink_to(target)
    with pytest.raises(FileExistsError):write_json_create_only(link,{'overwrite':1})
    assert target.read_text()=='keep' and link.is_symlink()

def test_quantity_and_axis_refusals_do_not_create_rates():
    d=ds()
    for unit in ['m3/s','heating_rate','electron_spectrum']:
        with pytest.raises(ContractError):d.sample('NR_CX:2s:total','100',unit=unit)
    for energy in ['NaN','-1','0',True]:
        with pytest.raises(ContractError):d.sample('NR_CX:2s:total',energy)

def test_old_gate_ids_and_requirements_preserved():
    parent=json.loads((ROOT/'provenance/parent_RESEARCH_DAG.json').read_text())
    current=json.loads((ROOT/'RESEARCH_DAG.json').read_text())
    p={x['id']:x.get('requires',[]) for x in parent['nodes']}
    c={x['id']:x.get('requires',[]) for x in current['nodes']}
    assert p==c and len(c)==16
    assert current['preserved_parent_gates']==parent['preserved_parent_gates']
