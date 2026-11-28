#!/usr/bin/env python3
"""Read-only five-case signed AXBI PARTIAL endpoint parity, at identical a.

This is an exact-decimal diagnostic of archived display samples, not a true
solution, numerical-convergence, time-matched, or detection certificate.
The five displayed partial histories cover only their recorded common endpoint.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from decimal import Decimal,localcontext

LABELS=('ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS')
FIELDS=('x_HII','x_HeII','x_HeIII','electron','T')
SOURCE_SHA='d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'

def evaluate(root:Path):
    root=Path(root)
    manifest=json.loads((root/'SAMPLE_MANIFEST.json').read_text())
    if manifest['status']!='FIVE_ORIGINAL_PARTIAL_INPUTS_VALIDATED':
        raise ValueError('UNAPPROVED_SAMPLE_SOURCE')
    rows={};sha={}
    for name in LABELS:
        p=root/f'{name}_display_samples.csv'
        sha[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        if sha[name]!=manifest['cases'][name]['display_sample_csv_sha256']:
            raise ValueError('SAMPLE_BYTES_MISMATCH:'+name)
        if manifest['cases'][name]['source_identity_sha256']!=SOURCE_SHA:
            raise ValueError('SOURCE_MISMATCH')
        with p.open(newline='') as f:
            data=list(csv.DictReader(f))
        if len(data)!=manifest['cases'][name]['display_rows']:
            raise ValueError('SAMPLE_COUNT_MISMATCH')
        rows[name]=data[-1]
        if rows[name]['original_accepted_row']!='200000':
            raise ValueError('UNEXPECTED_TERMINAL_ROW')
        if rows[name]['a']!=str(manifest['cases'][name]['a_endpoint']):
            raise ValueError('SCALE_NOT_MATCHED')
    if len({rows[n]['a'] for n in LABELS})!=1:
        raise ValueError('NOT_IDENTICAL_SCALE_FACTOR')
    with localcontext() as c:
        c.prec=65
        he=Decimal('0.2454'); f=he/(4*(1-he)); baryon=1+4*f
        # Verify the pre-existing electron per-baryon normalization at printed precision.
        for name in LABELS:
            x,y,z=[Decimal(rows[name][k]) for k in ('x_HII','x_HeII','x_HeIII')]
            expect=(x+f*(y+2*z))/baryon
            if abs(Decimal(rows[name]['electron'])-expect)>Decimal('5e-15'):
                raise ValueError('ELECTRON_BARYON_NORMALIZATION_ERROR:'+name)
        def d(n,key):return Decimal(rows[n][key])
        result={}
        for key in FIELDS:
            base=d('ZERO',key)
            p,m,ph,mh=(d(n,key) for n in LABELS[1:])
            even=(p+m)/2-base; odd=(p-m)/2
            evenhalf=(ph+mh)/2-base; oddhalf=(ph-mh)/2
            fourth=even-4*evenhalf
            result[key]={
              'zero':str(base),'even_full_q':str(even),'odd_full_q':str(odd),
              'even_half_q':str(evenhalf),'odd_half_q':str(oddhalf),
              'even_full_over_even_half':str(even/evenhalf) if evenhalf else None,
              'deviation_from_quadratic_amplitude':str(fourth),
              'full_to_half_expected_for_even_quadratic':4,
              'true_IVP_error':None,'numeric_convergence_error':None
            }
        return {
          'schema':'rei.axbi.five_partial_fixed_a_parity_diagnostic.v1',
          'stage':'C1-scoped parallel support','source_SHA256':SOURCE_SHA,
          'sample_sha256':sha,'equal_scale_factor':rows['ZERO']['a'],
          'equal_stored_accepted_row':'200000',
          'proper_elapsed_time_seconds_by_case':{k:rows[k]['t'] for k in LABELS},
          'comparison_coordinate':'FIXED_STORED_SCALE_FACTOR_NOT_PROPER_TIME',
          'signed_shear_q_ref':{'full':'0.01','half':'0.005'},
          'physical_model':'cold IGM/MD14 AXBI normal-comoving; helium mass fraction .2454',
          'observables':result,
          'limitations':['display-sampled endpoint only','not full z20-to4 signed histories',
                 'no convergence or roundoff certificate',
                 'odd differences can be numeric noise',
                 'different model proper times at fixed scale factor',
                 'not an IVP/physics detection claim'],
          'scientific_admission':'EXPLORATORY_ONLY',
          'owner_code_or_run_changed':False
        }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--samples',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit('REFUSE_OVERWRITE')
    val=evaluate(a.samples)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(val,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'endpoint_a':val['equal_scale_factor'],
        'even_q_ratio_xHII':val['observables']['x_HII']['even_full_over_even_half'],
        'even_q_ratio_electron':val['observables']['electron']['even_full_over_even_half'],
        'odd_xHII':val['observables']['x_HII']['odd_full_q'],
        'claim':val['scientific_admission']},indent=2))
if __name__=='__main__': main()
