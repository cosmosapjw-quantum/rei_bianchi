"""Replay retained Unit A POINT requests through native backend comparison.

This is neither an IVP nor another full IPC performance benchmark. The measured
error denominators are native sums of elementary absolute flux/power terms.
"""
import argparse,gzip,hashlib,json,pathlib,struct,subprocess,time
def identity(p):
    data=p.read_bytes();return {'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def same_bits(a,b):return len(a)==len(b)and all(struct.pack('>d',x)==struct.pack('>d',y)for x,y in zip(a,b))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=pathlib.Path,required=True)
    p.add_argument('--inputs',type=pathlib.Path,required=True);p.add_argument('--unit-a-replies',type=pathlib.Path,required=True)
    p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    inputs=json.loads(gzip.decompress(a.inputs.read_bytes()));prior=json.loads(gzip.decompress(a.unit_a_replies.read_bytes()))
    maxima={name:[{'channel':j,'max_absolute_error':0.0,'max_relative_error':0.0,'max_error_over_sum_abs_flux':0.0,
        'absolute_location':None,'relative_location':None,'scaled_location':None,'direct_zero_nonzero_error_count':0}
        for j in range(28)]for name in ['loglinear','cubic']}
    max_condition=[{'value':0.0,'location':None}for _ in range(28)]
    ledgers={name:{'max_absolute':0.0,'max_scaled':0.0}for name in ['direct','loglinear','cubic']}
    count=0;bit_counts={'direct':0,'loglinear':0};t=time.perf_counter()
    proc=subprocess.Popen([str(a.binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    raw_path=a.output/'GAS_POINT_ROWS.jsonl.gz'
    try:
        header=proc.stdout.readline();metadata=json.loads(header)
        with raw_path.open('xb')as file,gzip.GzipFile(fileobj=file,mode='wb',mtime=0)as raw:
            raw.write(header)
            for key in sorted(inputs):
                old_direct=prior['direct_'+key].splitlines();old_table=prior['table_'+key].splitlines()
                assert len(inputs[key])==len(old_direct)==len(old_table)
                for index,payload in enumerate(inputs[key]):
                    proc.stdin.write(('RHS 7 29 '+payload+'\n').encode());proc.stdin.flush()
                    line=proc.stdout.readline()
                    if not line:raise RuntimeError('native comparison ended early')
                    record=json.loads(line);record['input_key']=key;record['input_index']=index
                    raw.write((json.dumps(record,separators=(',',':'))+'\n').encode())
                    for name,old in [('direct',old_direct[index]),('loglinear',old_table[index])]:
                        expected=[float(s)for s in old.split()[1:]]
                        if not same_bits(record[name],expected):raise RuntimeError('Unit A bit mismatch '+name+' '+key+' '+str(index))
                        bit_counts[name]+=len(expected)
                    direct=record['direct'];denom=record['sum_abs_flux'];loc=[key,index,record['temperature_k']]
                    for j,(value,scale)in enumerate(zip(direct,denom)):
                        if abs(value)>scale*(1+3e-14):raise RuntimeError('elementary denominator missed a term')
                        if value!=0 and scale/abs(value)>max_condition[j]['value']:
                            max_condition[j]={'value':scale/abs(value),'location':loc,'direct':value,'sum_abs_flux':scale}
                    for name in ['direct','loglinear','cubic']:
                        q=record[name]
                        if any(q[j]<0 for j in list(range(16,25))+[26]):raise RuntimeError('negative positive event channel')
                        residual=abs(record['ledger_residuals'][['direct','loglinear','cubic'].index(name)])
                        scale=sum(abs(q[j])for j in [13,14,15,27]);ratio=residual/scale if scale else 0.0
                        if residual and not scale or ratio>3e-14:raise RuntimeError('ledger gate')
                        ledgers[name]['max_absolute']=max(ledgers[name]['max_absolute'],residual)
                        ledgers[name]['max_scaled']=max(ledgers[name]['max_scaled'],ratio)
                    for name in ['loglinear','cubic']:
                        for j,(ref,v,scale)in enumerate(zip(direct,record[name],denom)):
                            delta=abs(v-ref);row=maxima[name][j]
                            if delta>row['max_absolute_error']:row.update(max_absolute_error=delta,absolute_location=loc+[ref,v,scale])
                            if ref!=0 and delta/abs(ref)>row['max_relative_error']:row.update(max_relative_error=delta/abs(ref),relative_location=loc+[ref,v,scale])
                            if scale and delta/scale>row['max_error_over_sum_abs_flux']:row.update(max_error_over_sum_abs_flux=delta/scale,scaled_location=loc+[ref,v,scale])
                            if ref==0 and delta:row['direct_zero_nonzero_error_count']+=1
                    count+=1
            proc.stdin.write(b'QUIT\n');proc.stdin.flush();proc.stdin.close();proc.wait(timeout=3)
            stderr=proc.stderr.read()
            (a.output/'native.stderr.txt').write_bytes(stderr)
            if proc.returncode or stderr:raise RuntimeError('native comparison failed '+repr(stderr[:300]))
    finally:
        if proc.poll()is None:proc.kill();proc.wait()
    result={'schema':'REI_RUN19_UNIT_B_GAS_COMPARISON_V1','metadata':metadata,
        'input_identities':[identity(a.inputs),identity(a.unit_a_replies)],'binary_identity':identity(a.binary),
        'raw_point_result':identity(raw_path),'producer_argv':__import__('sys').argv,'wall_seconds':time.perf_counter()-t,
        'point_inputs':count,'native_gas_evaluations':3*count,'extra_direct_d_evaluations_for_denominators':count,
        'unit_a_output_float_bits_equal':bit_counts,'positive_event_channel_checks_passed':True,
        'ledger_gate_passed':True,'ledgers':ledgers,'maxima':maxima,'max_flux_cancellation_condition':max_condition,
        'scope':'finite retained manufactured states; denominators are f64 point diagnostics; no continuous table/Jacobian/trajectory bound',
        'ivps':0,'full_ipc_benchmarks':0}
    (a.output/'GAS_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'point_inputs':count,'wall_seconds':result['wall_seconds'],'bit_counts':bit_counts,
        'cubic_max_net_species_relative':max(x['max_relative_error']for x in maxima['cubic'][:13]),
        'cubic_max_species_error_over_flux':max(x['max_error_over_sum_abs_flux']for x in maxima['cubic'][:13]),
        'cubic_max_ci_rr_relative':max(x['max_relative_error']for x in maxima['cubic'][16:24]),'ledgers':ledgers},indent=2))
if __name__=='__main__':main()
