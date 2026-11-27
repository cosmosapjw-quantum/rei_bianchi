"""Create immutable unweighted raw external comparison AFTER model C gate."""
from pathlib import Path
import csv, hashlib, json, math
from execute_real_support import HERE, REPO, atomic, sha


def main():
    benchmark=json.loads((HERE/'BENCHMARK_MANIFEST.json').read_text())
    contract=json.loads((HERE/'MODEL_CONTRACT.json').read_text())
    c=json.loads((HERE/'C_RESULT.json').read_text())
    if not c['converged'] or c['status']!='R10L_C_LOCAL_NUMERICAL_PASS':
        raise ValueError('No adopted comparison before C numerical gate')
    if c['query_contract_sha256']!=sha(HERE/'QUERY_CONTRACT.json'):
        raise ValueError('C execution query identity')
    if contract['benchmark_manifest_sha256']!=sha(HERE/'BENCHMARK_MANIFEST.json'):
        raise ValueError('benchmark freeze identity')
    source={}
    for name in ('A','B'):
        specification=contract['models'][name];p=REPO/specification['source_file']
        if sha(p)!=specification['sha256']:raise ValueError('stored control source identity')
        source[name]=json.loads(p.read_text())
    scale=benchmark['a0_squared_cm2']; rows=[]
    for reference in benchmark['benchmarks']:
        E,n=reference['energy_keV_u'],reference['shell_n'];energy=str(float(E));shell=str(n)
        a=source['A']['policy_metrics']['AUTHOR_REAL']['shell_a0sq'][0 if E==.5 else 1][n-1]
        b=source['B']['lanes']['SL_CPC'][energy]['Z2_shell_areas_a0sq'][shell]
        value=c['shells'][energy]['Z2_shell_areas_a0sq'][shell]
        model_values={'A':a*scale,'B':b*scale,'C':value*scale}
        low,high=reference['extraction_interval_cm2']; central=reference['value_cm2']
        cells={}
        for name,v in model_values.items():
            if not v>0:raise ValueError('positive shell output required for finite raw log')
            cells[name]={'value_cm2':v,'raw_ratio':v/central,'natural_log_ratio':math.log(v/central),
                         'ratio_extraction_interval':[v/high,v/low],
                         'within_extraction_interval':low<=v<=high}
        row={'source':reference['source'],'method':reference['method'],'energy_keV_u':E,
             'source_energy':reference['source_energy'],'source_energy_unit':reference['source_energy_unit'],
             'shell_n':n,'benchmark_cm2':central,'benchmark_extraction_interval_cm2':[low,high],
             'source_physical_uncertainty':'unquantified; extraction interval is not a physical confidence interval',
             'models':cells,'C_minus_B_cm2':model_values['C']-model_values['B'],
             'relative_support_change':value/b-1,
             'A_role':'AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION',
             'numerical_error_estimates_cm2':{
                 'A':None,
                 'B':source['B']['lanes']['SL_CPC'][energy]['Z2_shell_error_estimate_a0sq'][shell]*scale,
                 'C':c['shells'][energy]['Z2_shell_error_estimate_a0sq'][shell]*scale}}
        rows.append(row)
    raw={'schema':'bass_he.r10l.raw_external_comparison.v1','rows':rows,'no_aggregate':True,'weights':None,
         'source_identity':{'benchmark_manifest_sha256':sha(HERE/'BENCHMARK_MANIFEST.json'),
                            'model_contract_sha256':sha(HERE/'MODEL_CONTRACT.json'),
                            'C_result_sha256':sha(HERE/'C_RESULT.json')},
         'claim':'Finite shell research output external comparison; no fit, physical confidence interval or production certificate.'}
    path=HERE/'RAW_COMPARISON.json'
    if path.exists():raise ValueError('raw comparison already frozen')
    atomic(path,raw)
    csv_path=HERE/'RAW_COMPARISON.csv'
    if csv_path.exists():raise ValueError('CSV already frozen')
    csv_temp=csv_path.with_suffix('.csv.tmp')
    with csv_temp.open('x',newline='') as f:
        fields=['source','energy_keV_u','shell_n','benchmark_cm2','benchmark_low_cm2','benchmark_high_cm2']
        fields += [f'{k}_{x}' for k in ('A','B','C') for x in ('cm2','ratio','ln_ratio')]
        fields+=['relative_support_change']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:
            flat={k:row[k] for k in ('source','energy_keV_u','shell_n','benchmark_cm2','relative_support_change')}
            flat['benchmark_low_cm2'],flat['benchmark_high_cm2']=row['benchmark_extraction_interval_cm2']
            for k in ('A','B','C'):
                for key,label in [('value_cm2','cm2'),('raw_ratio','ratio'),('natural_log_ratio','ln_ratio')]:
                    flat[f'{k}_{label}']=row['models'][k][key]
            writer.writerow(flat)
        f.flush()
        import os
        os.fsync(f.fileno())
    os.replace(csv_temp,csv_path)
    fd=os.open(str(HERE),os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps({'raw_table_rows':len(rows),'raw_table_sha256':sha(path),'aggregate':'NOT_RUN'}))


if __name__=='__main__':main()
