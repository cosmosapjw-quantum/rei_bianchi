"""Review new derived products, reusing frozen four-case sample data only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'axbi_science/incremental_fifth/results_five'
OLD=ROOT/'rei_current/research/rei_axbi_owner_loop_20261115/results'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read(p):return pd.read_csv(p,float_precision='round_trip')

fullpath=ROOT/'axbi_science/private/SHEAR_PLUS_full_normalized.csv.gz'
manifest=json.loads((OUT/'FIFTH_FULL_ABUNDANCE_MANIFEST.json').read_text())
assert sha(fullpath)==manifest['sha256']
full=read(fullpath)
assert len(full)==manifest['rows']==312238
assert list(full.columns)==manifest['columns']
assert np.all(np.diff(full.time_s)>0) and set(full.case_id)=={'SHEAR_PLUS'}
ind=json.loads((ROOT/'reviews/AX08_PLUS_INDEPENDENT_NUMERICS.json').read_text())
spot_errors=[]
for spot in ind['native_normalization_spot_rows']:
    i=spot['original_row']
    for field,value in spot.items():
        if field=='original_row':continue
        difference=abs(float(full[field].iloc[i])-value)
        spot_errors.append(difference)
        assert difference==0,(i,field,difference)
five=read(OUT/'five_case_abundances.csv.gz')
old=read(OLD/'abundances.csv.gz')
assert len(five)==5005 and five.iloc[:len(old)].reset_index(drop=True).equals(old)
assert set(five['case'])=={'ZERO','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS','SHEAR_PLUS','SHEAR_MINUS'}
summary=json.loads((OUT/'FIVE_CASE_APPROXIMATION_SUMMARY.json').read_text())
oldsummary=json.loads((ROOT/'axbi_science/results/FULL_SUMMARY.json').read_text())
assert all(summary['cases'][k]==v for k,v in oldsummary['cases'].items())
assert summary['represented_rows']==1561190 and summary['rows_consumed']==312238
metrics=json.loads((OUT/'FIFTH_RESPONSE_SUMMARY.json').read_text())
response_results={}
lna=np.log(full.a.to_numpy());native_time=full.time_s.to_numpy()
fields=['x_HI','x_HII','x_HeI','x_HeII','x_HeIII','xe_per_H','temperature_K']
for mode,oldfile in [('fixed_a','comparison_zbar.csv.gz'),('fixed_t','comparison_time.csv.gz')]:
    df=read(OUT/('responses_'+mode+'.csv.gz'))
    reference=read(OLD/oldfile)
    minus=reference[reference['case']=='SHEAR_MINUS'].reset_index(drop=True)
    assert len(df)==len(minus)==1001
    if mode=='fixed_a':
        query=np.linspace(np.log(1/21),np.log(.2),1001)
        assert np.array_equal(df.candidate_zbar,df.reference_zbar)
        assert np.array_equal(df.reference_time_s,minus.reference_time_s)
        clock_error=float(np.max(abs(df.candidate_time_s-np.interp(query,lna,native_time))))
        assert clock_error==0
    else:
        assert np.array_equal(df.candidate_time_s,df.reference_time_s)
        assert np.array_equal(df.reference_zbar,minus.reference_zbar)
        query=np.interp(df.elapsed_time_s,native_time,lna)
        clock_error=float(np.max(abs(df.candidate_zbar-(np.exp(-query)-1))))
        assert clock_error==0
    field_checks={}
    for field in fields:
        expected=np.interp(query,lna,full[field].to_numpy())
        plus=df[field+'_plus'].to_numpy();negative=df[field+'_minus'].to_numpy();zero=df[field+'_zero'].to_numpy()
        assert np.array_equal(negative,minus[field+'_candidate'])
        assert np.array_equal(zero,minus[field+'_reference'])
        assert np.array_equal(plus,expected)
        for component,values in [('plus_response',plus-zero),('odd_q001',(plus-negative)/2),('even_q001',(plus+negative)/2-zero)]:
            assert np.array_equal(df[field+'_'+component],values)
            peak=int(np.argmax(abs(values)))
            report=metrics['responses'][mode][field][component]
            assert report['max_abs']==abs(values[peak]) and report['signed_at_peak']==values[peak]
        field_checks[field]={'signed_peak_response':metrics['responses'][mode][field]['plus_response']['signed_at_peak'],
            'max_abs_odd':metrics['responses'][mode][field]['odd_q001']['max_abs'],
            'declared_resolution':metrics['responses'][mode][field]['scientific_resolution']}
        assert field_checks[field]['declared_resolution']=='UNRESOLVED_AX11'
    response_results[mode]={'rows':len(df),'clock_mapping_max_error':clock_error,'field_checks':field_checks}
milestone=read(OUT/'fifth_milestones.csv').set_index('x_HII_level')
milestone_checks=[]
for item in ind['independent_milestones']:
    row=milestone.loc[item['x_HII_level']]
    assert row.status==item['status']
    for field in ['lower_row','upper_row','time_s','zbar']:assert row[field]==item[field]
    milestone_checks.append(item)
result={'status':'FULL_NORMALIZED_OUTPUT_AND_RESPONSES_VERIFIED','full_normalized_sha256':sha(fullpath),
    'full_normalized_rows':len(full),'native_spot_max_abs_difference':max(spot_errors),
    'sample_rows':len(five),'old_four_sample_rows_preserved_exactly':True,
    'old_four_diagnostic_records_preserved_exactly':True,'represented_native_rows':summary['represented_rows'],
    'responses':response_results,'milestones_match_independent_native_brackets':True,
    'new_native_histories_reduced':1,'prior_four_raw_histories_reprocessed':False,
    'AX11_resolution_claimed':False,'output_sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()}}
(ROOT/'reviews/AX08_FIFTH_PRODUCT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['responses','output_sha256']},indent=2))
