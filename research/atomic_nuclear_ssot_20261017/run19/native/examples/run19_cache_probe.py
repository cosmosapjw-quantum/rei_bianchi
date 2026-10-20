"""One bounded cold/save + warm/load + mismatched-source server cache probe."""
import argparse,gzip,hashlib,json,pathlib,subprocess,time
def ident(p):
    b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=pathlib.Path,required=True)
    p.add_argument('--inputs',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    values=json.loads(gzip.decompress(a.inputs.read_bytes()));key=sorted(values)[0]
    request='META\n'+''.join('RHS 7 29 '+s+'\n'for s in values[key][:4])+'QUIT\n'
    (a.output/'REQUEST.txt').write_text(request)
    cache=a.output/'cubic_default.bin';rows=[];good_reply=None;old_sha=None
    for phase in ['cold_build_save','warm_load']:
        argv=[str(a.binary),'--rates','cubic','--table-cache',str(cache)]
        t=time.perf_counter();result=subprocess.run(argv,input=request,text=True,capture_output=True,timeout=10)
        (a.output/(phase+'.stdout.txt')).write_text(result.stdout);(a.output/(phase+'.stderr.txt')).write_text(result.stderr)
        if result.returncode or result.stderr:raise RuntimeError('cache run failed '+repr(result.stderr))
        lines=result.stdout.splitlines();metadata=json.loads(lines[0]);reply='\n'.join(lines[1:])
        if len(lines)!=5 or any(len(x.split())!=29 or not x.startswith('OK ')for x in lines[1:]):raise RuntimeError('reply shape')
        digest=ident(cache)
        if metadata['table_cache_sha256']!=digest['sha256']:raise RuntimeError('META file identity mismatch')
        if phase=='cold_build_save':
            assert metadata['table_cache_action']=='BUILT_SAVED_NEW';good_reply=reply;old_sha=digest['sha256']
        else:
            assert metadata['table_cache_action']=='LOADED_EXACT_SOURCE'
            if reply!=good_reply or digest['sha256']!=old_sha:raise RuntimeError('warm/cold byte mismatch')
        rows.append({'phase':phase,'argv':argv,'wall_seconds':time.perf_counter()-t,'metadata':metadata,'cache_identity':digest,'exit_code':result.returncode})
    # Deliberately different source-ID header with an otherwise valid digest.
    bad=bytearray(cache.read_bytes());bad[24]^=1;bad[-32:]=hashlib.sha256(bad[:-32]).digest()
    wrong=a.output/'wrong_source.bin';wrong.write_bytes(bad)
    argv=[str(a.binary),'--rates','cubic','--table-cache',str(wrong)]
    r=subprocess.run(argv,input='META\nQUIT\n',text=True,capture_output=True,timeout=10)
    (a.output/'wrong_source.stdout.txt').write_text(r.stdout);(a.output/'wrong_source.stderr.txt').write_text(r.stderr)
    if r.returncode!=64 or 'CUBIC_CACHE_IDENTITY'not in r.stderr or r.stdout:
        raise RuntimeError('wrong source cache not rejected before serving')
    summary={'schema':'REI_RUN19_NATIVE_CACHE_PROBE_V1','producer_argv':__import__('sys').argv,
        'binary_identity':ident(a.binary),'retained_inputs_identity':ident(a.inputs),
        'selected_input_key':key,'selected_rows':list(range(4)),'request_identity':ident(a.output/'REQUEST.txt'),
        'runs':rows,'warm_cold_reply_bytes_identical':True,'cache_unchanged_on_load':True,
        'wrong_source':{'argv':argv,'identity':ident(wrong),'exit_code':r.returncode,'stderr':r.stderr},
        'gas_rhs_point_evaluations':8,'ivps':0,'scope':'actual source-bound cache roundtrip and rejection, not benchmark or cache-producer authentication'}
    (a.output/'CACHE_PROBE.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'phases':[{'phase':r['phase'],'seconds':r['wall_seconds']}for r in rows],
        'cache':ident(cache),'wrong_source_rejected':True,'rhs_points':8,'ivps':0},indent=2))
if __name__=='__main__':main()
