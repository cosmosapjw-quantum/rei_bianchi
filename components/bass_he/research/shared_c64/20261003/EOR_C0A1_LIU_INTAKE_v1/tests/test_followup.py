"""Follow-up verification; these tests were added after the first green."""
from pathlib import Path
import sys, json, subprocess, hashlib
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import liu_intake as liu
PDF=ROOT/'source/Liu_2024_Chinese_Phys._B_33_083401.pdf'

@pytest.fixture(scope='module')
def parsed():return liu.parse_pdf_tables(PDF,liu.PDF_SHA256)

@pytest.fixture(scope='module')
def text():
    import fitz
    with fitz.open(PDF) as doc:return doc[3].get_text()

def test_gto_counts_reproduce_author_counts(parsed):
    assert liu.source_audit(parsed)['spherical_gto_counts']=={'B1':215,'B2':240,'B3':265}

def test_all_percentages_compatible_with_printed_rounding(parsed):
    a=liu.source_audit(parsed)
    assert len(a['percent_checks'])==60
    assert all(x['compatible_with_display_rounding'] for x in a['percent_checks'])

@pytest.mark.parametrize('species,st,b,expected',[
 ('HI','1s','B1','-0.4999920'),('HI','4f','B3','-0.0312499'),
 ('HeII','4f','B2','-0.1249997'),('HeII','2s','B3','-0.5000014')])
def test_separated_table_rows_preserve_decimal_tokens(parsed,species,st,b,expected):
    row=next(x for x in parsed['levels'] if x['species']==species and x['state']==st)
    assert row[f'E_{b}_token']==expected

def test_source_locators(parsed):
    assert parsed['source']['pdf_page_tables']==4
    assert parsed['source']['pdf_pages']==9
    assert parsed['source']['embedded_files']==0
    assert parsed['source']['extraction']=='DIRECT_PDF_TEXT_NO_OCR'

@pytest.mark.parametrize('edit',[
 lambda t:t.replace('Table 2.','Table 99.'),
 lambda t:t.replace('\nHe+\n','\nHeI\n'),
 lambda t:t.replace('−2.0000130','NaN'),
 lambda t:t.replace('0.052%','-0.052%',1),
 lambda t:t.replace('\ns\n100\n1.3335\n17\n','\ns\n100\n1.3335\n0\n'),
 lambda t:t.replace('−0.4997333','+0.4997333',1),
 lambda t:t+'\nTable 1. duplicate caption\n'])
def test_malformed_numeric_or_species_blocks_rejected(text,edit):
    with pytest.raises(liu.SchemaError):liu.parse_text_tables(edit(text))

@pytest.mark.parametrize('ids',[
 ['NR_CX:1s:1s','NR_CX:1s:2s','NR_CX:1s:2p'],
 ['NR_CX:1s:n2','NR_CX:1s:n3'],
 ['EXC:2s:3s','EXC:2s:4f'],
 ['NR_CX:2s:total']])
def test_disjoint_selection_does_not_invent_data(ids):
    r=liu.check_selection(ids,liu.coverage_registry())
    assert r['disjoint_in_source_resolution']
    assert r['summed_cross_section'] is None
    assert not r['numeric_source_available']
    assert not r['infinite_bound_completeness']

@pytest.mark.parametrize('ids',[
 ['NR_CX:1s:1s','NR_CX:1s:1s'],
 ['EXC:1s:n4','NR_CX:1s:n4'],
 ['EXC:2s:2p'],
 ['NR_CX:1s:n1'],
 []])
def test_unavailable_or_incompatible_quantities(ids):
    with pytest.raises(liu.SourceError):liu.check_selection(ids,liu.coverage_registry())

def test_coverage_distinguishes_declared_range_and_actual_grid():
    c=liu.coverage_registry()
    assert sum(x['initial_target']=='HI:1s' for x in c)==18
    assert sum(x['initial_target']=='HI:2s' for x in c)==19
    assert all(x['actual_native_grid'] is None for x in c)
    assert all(x['source_uncertainty'] is None for x in c)
    assert all(x['per_amu_divisor_definition'] is None for x in c)
    assert {x['plot_value_unit'] for x in c if x['registry_reaction_id']=='EXC'}=={'1e-16 cm^2'}

def test_allowed_exports_keep_data_kind(parsed):
    assert len(liu.export_quantity(parsed,'electronic_energies'))==20
    assert len(liu.export_quantity(parsed,'basis_parameters'))==15
    assert all('NOT_CERTIFIED' in r['data_kind'] for r in liu.export_quantity(parsed,'electronic_energies'))

def test_cli_success_then_refuses_overwrite(tmp_path):
    out=tmp_path/'out.json'
    cmd=[sys.executable,'-B',str(ROOT/'src/liu_intake.py'),'--pdf',str(PDF),'--sha256',liu.PDF_SHA256,'--out',str(out)]
    a=subprocess.run(cmd,capture_output=True,text=True)
    assert a.returncode==0,a.stderr
    before=hashlib.sha256(out.read_bytes()).hexdigest()
    assert json.loads(out.read_text())['physical_certificate'] is False
    b=subprocess.run(cmd,capture_output=True,text=True)
    assert b.returncode==2
    assert before==hashlib.sha256(out.read_bytes()).hexdigest()

@pytest.mark.parametrize('quantity',['cross_section','heating_rate'])
def test_cli_unavailable_quantity_no_output(tmp_path,quantity):
    out=tmp_path/'bad.json'
    r=subprocess.run([sys.executable,'-B',str(ROOT/'src/liu_intake.py'),'--pdf',str(PDF),'--sha256',liu.PDF_SHA256,
                      '--out',str(out),'--quantity',quantity],capture_output=True,text=True)
    assert r.returncode==2
    assert 'SourceUnavailable' in r.stderr
    assert not out.exists()
