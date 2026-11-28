"""Distinct-author transcription check, starting from the original PDF only."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parent
PDF=Path('/workspace/scratch/5f3e9bf5a6d0/source_research/GL2022_CSIC_supplement.pdf')
SHA='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754'

def rat(x):
    return {'numerator':str(x.numerator),'denominator':str(x.denominator)}

def main():
    c0,t0=time.process_time(),time.monotonic()
    raw=PDF.read_bytes()
    assert len(raw)==273554 and hashlib.sha256(raw).hexdigest()==SHA
    text=subprocess.check_output(['pdftotext','-layout',str(PDF),'-'],text=True)
    pages=text.split('\f')
    assert len(pages)==15 and pages[-1].strip()==''
    table2=pages[5].split('Table 2:',1)[1].split('Table 3:',1)[0]
    header=re.search(r'T \[K\]([^\n]+)',table2).group(1)
    temps=[int(s) for s in header.split()]
    assert temps==[15,55,105,255,505,1005,1505,2005,2505,3005]
    rows={int(m.group(1)):m.group(2).split() for m in re.finditer(r'^\s*\(0,(\d+)\)\s+([^\n]+)$',table2,re.M)}
    assert sorted(rows)==list(range(7))
    selected=rows[2]
    # Independent human transcription from rendered page6/Table2/row(0,2).
    visual=['3.99(14)','2.92(11)','1.15(10)','2.74(10)','3.33(10)',
            '3.18(10)','2.85(10)','2.55(10)','2.30(10)','2.08(10)']
    assert selected==visual
    cells=[]
    for column,(t,token) in enumerate(zip(temps,selected),start=1):
        m=re.fullmatch(r'(\d+\.\d+)\((\d+)\)',token)
        assert m
        mantissa,x=m.groups()
        printed=F(mantissa)*F(1,10**int(x))
        cells.append({'pdf_page_1indexed':6,'printed_page':6,'table':2,
                      'row_label':'(0,2)','rate_data_row_1indexed':3,
                      'temperature_column_1indexed':column,'temperature_K':t,
                      'source_token':token,'printed_value_cm3_per_s_exact':rat(printed),
                      'printed_value_m3_per_s_exact':rat(printed/F(10**6)),
                      'value_kind':'exact rational decoding of printed SQM decimal, not exact physical rate',
                      'spin_factor_in_raw_row':False})
    coverage=[]
    for table in range(1,11):
        for pg,page in enumerate(pages,1):
            match=re.search(r'(?m)^\s*Table '+str(table)+r':',page)
            if match:
                block=page[match.end():]
                end=re.search(r'(?m)^\s*Table \d+:',block)
                if end:block=block[:end.start()]
                rs=sorted(int(m.group(1)) for m in re.finditer(r'^\s*\(0,(\d+)\)\s+[^\n]+$',block,re.M))
                assert rs==list(range(7)),(table,pg,rs)
                coverage.append({'table':table,'product_v':0,'product_j':table-1,
                                 'pdf_page_1indexed':pg,'initial_HD_v':0,
                                 'initial_HD_j_provided':rs,'initial_HD_j7_j8':'MISSING_NOT_ZERO'})
                break
        else:raise AssertionError(('missing table',table))
    result={'schema':'WU_R18_INDEPENDENT_NATIVE_SOURCE_TRANSCRIPTION_V1',
            'reviewer':'/root/r17b_independent_review','blind_to_author_extraction':True,
            'source':{'local_pdf':str(PDF),'sha256':SHA,'bytes':len(raw),'pages':14,
                      'url':'https://digital.csic.es/bitstream/10261/305186/2/h_hd_rate_supplementary_material.pdf',
                      'record':'https://digital.csic.es/handle/10261/305186',
                      'article_doi':'10.1063/5.0128598','source_identity':'institutional author deposit; bytes hash verified locally'},
            'target':'H+ + HD(v0,j2) -> D+ + H2(v0,j1)',
            'method':'SQM reactive state-to-state native printed table',
            'units':'cm^3 s^-1; m^3 s^-1 = 1e-6 times cm^3 s^-1',
            'temperatures_K':temps,'cells':cells,'native_reactive_coverage':coverage,
            'support':'ten discrete printed temperatures; no interpolation or extrapolation',
            'spin_application':{'raw_row':'unweighted state-to-state k_0j,0r',
                                'thermal_article_contribution':'p_j(T)*s_r*k_0j,0r(T)',
                                'target_r':1,'s_r':{'numerator':'3','denominator':'4'},
                                'apply_count':1,'source':'main article Eqs5-7; supplement p5 distinguishes raw tables1-10 from spin-weighted Table11'},
            'coverage_conflict':{'main_article_initial_j_max':8,
                                 'supplement_section3_initial_j_max':6,
                                 'supplement_thermal_total_initial_j_max_text':6,
                                 'Table11_caption':'refers to article Eqs5-7',
                                 'resolution':'UNRESOLVED_SOURCE_SCOPE_DIFFERENCE; no j7/8 fill or total equivalence claim'},
            'true_physical_rate_uncertainty':'UNRESOLVED_NOT_PROVIDED_BY_DECIMAL_TABLE',
            'consumer_binding':'NOT_REVIEWED_NOT_ADMITTED','HH_R10':'OFF',
            'production':'NOT_ISSUED','L4':False,
            'checks':{'pdf_hash_size':True,'pdf_pages':True,'target_cells_visual_vs_text':10,
                      'reactive_table_initial_row_coverages':10,'author_extraction_read':False},
            'cpu_seconds':time.process_time()-c0,'wall_seconds':time.monotonic()-t0,
            'exit_code':0,'verdict':'PASS_SCOPED_NATIVE_PRINTED_TARGET_ROW'}
    (ROOT/'INDEPENDENT_SOURCE_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'cells':10,'coverage_tables':10,
                      'source_sha256':SHA,'cpu_seconds':result['cpu_seconds']},indent=2))

if __name__=='__main__':main()
