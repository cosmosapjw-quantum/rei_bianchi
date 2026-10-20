"""Bounded opt-in gas-server IPC benchmark, preserving exact request/reply bytes.

Measures the NEW optimized scalar protocol against its NEW batched protocol.
It does not label this an end-to-end timing of the historical binary. Inputs
are named manufactured point states; no gas/transport trajectory is solved.
"""
import argparse, datetime, gzip, hashlib, json, pathlib, statistics, subprocess, time

def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def payload(i, varying):
    variant = i % 5
    n = [0.0, 180.0-variant, 20.0, 0.0045, 0.0005, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0+variant, 3.0, 1.0]
    charge = [0,0,1,0,1,0,1,0,1,2,0,1,2]
    heavy = electrons = 0.0
    for value,z in zip(n,charge):
        heavy += value
        electrons += z*value
    temperature = 9500.0+(i*104729)%5000 if varying else 10000.0
    u = 1.5*1.380649e-23*(heavy+electrons)*temperature
    return " ".join(format(v,".17e") for v in n+[u])

def read_row(process):
    line = process.stdout.readline()
    words = line.split()
    if len(words) != 29 or words[0] != b"OK":
        raise RuntimeError("unexpected reply: "+repr(line[:300]))
    return line

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    parser.add_argument('--repetitions', type=int, default=3)
    args=parser.parse_args()
    if not 1 <= args.repetitions <= 5:
        raise SystemExit('repetitions must be 1..5')
    args.output.mkdir(parents=True,exist_ok=False)
    inputs={}
    for varying in [False,True]:
        for size in [512,4096]:
            key=('varying' if varying else 'same')+'_'+str(size)
            inputs[key]=[payload(i,varying) for i in range(size)]
    input_bytes=json.dumps(inputs,sort_keys=True,separators=(',',':')).encode()
    compressed=gzip.compress(input_bytes,mtime=0)
    (args.output/'IPC_INPUTS.json.gz').write_bytes(compressed)
    rows=[]; startup=[]; gold={}; replies={}
    started=time.perf_counter()
    for backend,workers in [('direct',1),('direct',4),('table',1),('table',4)]:
        argv=[str(args.binary),'--rates',backend,'--workers',str(workers)]
        before=time.perf_counter()
        process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            process.stdin.write(b'META\n');process.stdin.flush()
            meta_bytes=process.stdout.readline();metadata=json.loads(meta_bytes)
            startup.append({'argv':argv,'seconds_to_metadata':time.perf_counter()-before,'metadata':metadata})
            for key,payloads in inputs.items():
                scalar=[('RHS 7 29 '+p+'\n').encode() for p in payloads]
                batch=('RHS_BATCH '+str(len(payloads))+' 7 29 '+' '.join(payloads)+'\n').encode()
                for mode in (['single','batch'] if workers==1 else ['batch']):
                    seconds=[];stats=[]
                    for _ in range(args.repetitions):
                        output=[];t=time.perf_counter()
                        if mode=='single':
                            for request in scalar:
                                process.stdin.write(request);process.stdin.flush()
                                output.append(read_row(process))
                            counts=None
                        else:
                            process.stdin.write(batch);process.stdin.flush()
                            header=process.stdout.readline().split()
                            if header != [b'BATCH_OK',str(len(payloads)).encode(),b'28']:
                                raise RuntimeError('bad batch header '+repr(header))
                            for _ in payloads:output.append(read_row(process))
                            end=process.stdout.readline().split()
                            if len(end)!=4 or end[0]!=b'BATCH_END' or int(end[1])!=len(payloads):
                                raise RuntimeError('bad batch end '+repr(end))
                            counts=dict(zip(['evaluations','preparations','hits'],map(int,end[1:])))
                        seconds.append(time.perf_counter()-t);stats.append(counts)
                        # Byte comparison is outside the timed region.
                        raw=b''.join(output);gold_key=backend+'_'+key
                        if gold_key not in gold:
                            gold[gold_key]=raw;replies[gold_key]=raw.decode()
                        elif raw!=gold[gold_key]:
                            raise RuntimeError('scalar/batch/repetition byte mismatch '+gold_key)
                    rows.append({'backend':backend,'workers':workers,'input':key,'mode':mode,
                        'n':len(payloads),'seconds':seconds,'median_us_per_rhs':statistics.median(seconds)*1e6/len(payloads),
                        'stats':stats,'reply_identity':identity(gold[backend+'_'+key]),
                        'reply_bytes_equal_within_backend':True})
            process.stdin.write(b'QUIT\n');process.stdin.flush();process.stdin.close()
            process.wait(timeout=3)
            err=process.stderr.read()
            if process.returncode!=0 or err:
                raise RuntimeError('server failed '+repr(err[:500]))
        finally:
            if process.poll() is None:process.kill();process.wait()
    reply_bytes=json.dumps(replies,sort_keys=True,separators=(',',':')).encode()
    reply_gzip=gzip.compress(reply_bytes,mtime=0)
    (args.output/'IPC_REPLIES.json.gz').write_bytes(reply_gzip)
    result={'schema':'REI_RUN19_IPC_BENCH_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'binary':{'path':str(args.binary),**identity(args.binary.read_bytes())},
        'producer_argv':__import__('sys').argv,'total_wall_seconds':time.perf_counter()-started,
        'timing_scope':'new_optimized_server_write_flush_read_validate_token_count; preformatted_inputs; includes_float_formatting_in_server; float_conversion_not_timed',
        'legacy_binary_timed':False,'repetitions':args.repetitions,'startup':startup,'rows':rows,
        'inputs':{'gzip':identity(compressed),'uncompressed':identity(input_bytes)},
        'replies':{'gzip':identity(reply_gzip),'uncompressed':identity(reply_bytes)},'ivps':0}
    (args.output/'IPC_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'total_wall_seconds':result['total_wall_seconds'],
        'all_same_backend_replies_byte_identical':True,'result':str(args.output/'IPC_RESULT.json')},indent=2))

if __name__=='__main__':main()
