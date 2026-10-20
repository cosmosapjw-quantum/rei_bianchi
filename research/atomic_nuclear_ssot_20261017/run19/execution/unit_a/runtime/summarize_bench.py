"""Read recorded RUN19 timings/replies only; no binary execution."""
import argparse,gzip,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--evidence',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
core_path=a.evidence/'unit_a_core_measure01/stdout.txt'
ipc_path=a.evidence/'unit_a_ipc_measure01/IPC_RESULT.json'
reply_path=a.evidence/'unit_a_ipc_measure01/IPC_REPLIES.json.gz'
core=json.loads(core_path.read_text());ipc=json.loads(ipc_path.read_text())
replies=json.loads(gzip.decompress(reply_path.read_bytes()))
differences=[]
for j in range(28):
    maxabs=maxrel=0.0;at_abs=at_rel=None;zeros=0
    for key in ['same_512','same_4096','varying_512','varying_4096']:
        direct=replies['direct_'+key].splitlines();table=replies['table_'+key].splitlines()
        assert len(direct)==len(table)
        for i,(ar,br) in enumerate(zip(direct,table)):
            av=float(ar.split()[j+1]);bv=float(br.split()[j+1]);delta=abs(bv-av)
            if delta>maxabs:maxabs=delta;at_abs=[key,i,av,bv]
            if av!=0 and delta/abs(av)>maxrel:maxrel=delta/abs(av);at_rel=[key,i,av,bv]
            if av==0 and bv!=0:zeros+=1
    differences.append({'channel':j,'maximum_absolute_difference':maxabs,
        'maximum_relative_difference_where_direct_nonzero':maxrel,'at_absolute':at_abs,
        'at_relative':at_rel,'direct_zero_table_nonzero_count':zeros})
summary={'schema':'REI_RUN19_BENCH_ANALYSIS_V1','native_executions_in_analysis':0,'ivps':0,
    'input_identities':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in [core_path,ipc_path,reply_path]],'core_comparisons':[],'ipc_comparisons':[]}
for row in core['rows']:
    base=next(r for r in core['rows'] if r['n']==row['n'] and r['pattern']==row['pattern']
        and r['mode']=='original' and r['backend']=='direct')
    summary['core_comparisons'].append({'pattern':row['pattern'],'n':row['n'],'backend':row['backend'],
        'mode':row['mode'],'median_ns_per_rhs':row['median_ns_per_rhs'],
        'min_ns_per_rhs':min(row['seconds'])*1e9/row['evaluations_per_repetition'],
        'max_ns_per_rhs':max(row['seconds'])*1e9/row['evaluations_per_repetition'],
        'observed_speed_ratio_vs_original':base['median_ns_per_rhs']/row['median_ns_per_rhs']})
for row in ipc['rows']:
    base=next(r for r in ipc['rows'] if r['input']==row['input'] and r['backend']==row['backend'] and r['mode']=='single')
    summary['ipc_comparisons'].append({'input':row['input'],'backend':row['backend'],
        'mode':row['mode'],'workers':row['workers'],'median_us_per_rhs':row['median_us_per_rhs'],
        'min_us_per_rhs':min(row['seconds'])*1e6/row['n'],'max_us_per_rhs':max(row['seconds'])*1e6/row['n'],
        'observed_speed_ratio_vs_new_single':base['median_us_per_rhs']/row['median_us_per_rhs']})
summary['sampled_table_gas_differences']={'point_rows':9216,'channels':differences,
    'scope':'manufactured IPC points only; net cancellation can amplify relative difference; not a continuous table/trajectory bound'}
(a.output/'BENCH_ANALYSIS.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'core_rows':len(summary['core_comparisons']),'ipc_rows':len(summary['ipc_comparisons']),
    'max_net_species_relative':max(x['maximum_relative_difference_where_direct_nonzero'] for x in differences[:13]),
    'heat_relative':differences[13]['maximum_relative_difference_where_direct_nonzero'],
    'ci_rr_relative':max(x['maximum_relative_difference_where_direct_nonzero'] for x in differences[16:24]),
    'chemical_relative':differences[27]['maximum_relative_difference_where_direct_nonzero']},indent=2))
