#!/usr/bin/env python3
"""Optional primary-PDF semantic witness. Never converts images to fake data.
The source JSON remains the frozen numeric transcription. This checker compares
its values with exact textual rows of the attached physical PDFs and SHA-256.
"""
import argparse
import hashlib
import sys
from pathlib import Path
import json
try:
    import fitz
except ImportError:
    raise SystemExit('Missing dependency PyMuPDF (fitz); source JSON can still be regenerated without this optional check')
ROOT=Path(__file__).resolve().parent.parent

def check(pdfdir):
    inp=ROOT/'sources'
    src=json.loads((inp/'RICE2000_TABLE_I_AUTHORITATIVE.json').read_text())
    prior=json.loads((inp/'RICE1998_TABLE_5_1_PRELIMINARY.json').read_text())
    pdfdir=Path(pdfdir)
    pdf=pdfdir/'PhysRevC.61.064612.pdf'
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==src['pdf_sha256'], 'published PDF SHA mismatch'
    d=fitz.open(pdf)
    assert len(d)==8
    txt=d[3].get_text(); start=txt.index('TABLE I.'); end=txt.index('FIG. 6.',start)
    table=txt[start:end]
    for i in range(6):
        a=src['observations'][i];b=src['observations'][i+6]
        expected=[f"{a['theta_lab']:.1f}°", f"{a['theta_cm']:.1f}°",f"{a['sigma']:.2f}6{a['stat_sd']:.2f}", f"{b['theta_cm']:.1f}°", f"{b['sigma']:.2f}6{b['stat_sd']:.2f}"]
        for t in expected:
            assert t in table, f'Published Table I row {i+1} missing PDF text token {t}'
    fit_txt=d[4].get_text()
    assert 'TABLE II' in fit_txt and '1.3160.07' in fit_txt and '8.3260.4060.65' in fit_txt
    d.close()
    thesis=pdfdir/'Rice_1998.pdf'
    assert hashlib.sha256(thesis.read_bytes()).hexdigest()==prior['pdf_sha256'], 'thesis PDF SHA mismatch'
    t=fitz.open(thesis)
    assert len(t)==139
    ttxt=t[114].get_text();assert 'Table 5.1' in ttxt
    for x in prior['entries']:
        for token in (f"{x['sigma']:.3f} ± {x['stat_sd']:.3f}",f"{x['yield']} ± {x['yield_sd']}"):
            assert token in ttxt, f'Missing Rice thesis preliminary token {token}'
    assert 'Table 5.2' not in t[-1].get_text()
    t.close()
    return {'Rice2000_TableI_numeric_rows_pdf_crosschecked':12,'Rice2000_TableII_discrepancy_tokens_confirmed':True,
            'Rice1998_preliminary_numeric_rows_pdf_crosschecked':6, 'Rice1998_pdf_pages':139,
            'status':'PDF_BINARY_IDENTITY_AND_SEMANTIC_TABLE_PASS'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pdf-dir',required=True);args=a.parse_args()
    print(json.dumps(check(args.pdf_dir),indent=2))
