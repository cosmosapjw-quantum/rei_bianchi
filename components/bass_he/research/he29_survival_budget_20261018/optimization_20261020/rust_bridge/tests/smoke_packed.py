#!/usr/bin/env python3
"""New packed ABI comparison on an analytic triangular n=24 model.

No HE29 native owner or physical source is used. This checks the new payload
layout, scaling, cache telemetry, callback failure and partial-output contract.
"""
import argparse
import ctypes as C
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback


class Stats(C.Structure):
    _fields_ = [('abi_version', C.c_uint32), ('status', C.c_int32),
        ('dimension', C.c_size_t), ('final_u', C.c_double)] + [
        (n,C.c_size_t) for n in ('output_samples','internal_steps','output_clipped_steps',
                               'attempts','accepted_macro_steps','rejected_macro_steps')] + [
        (n,C.c_uint64) for n in ('rhs_evaluations','jvp_vectors','linear_iterations',
          'direct_factorizations','callback_rhs_calls','callback_jvp_calls',
          'callback_partial_u_calls')] + [('json_required_bytes', C.c_size_t)]


D = C.POINTER(C.c_double)
RHS = C.CFUNCTYPE(C.c_int32,C.c_void_p,C.c_double,D,C.c_size_t,D)
JVP = C.CFUNCTYPE(C.c_int32,C.c_void_p,C.c_double,D,D,C.c_size_t,D)
PREPARE = C.CFUNCTYPE(C.c_int32,C.c_void_p,C.c_double,D,C.c_size_t,D,D)
N = 24
K = 1
DT = 0.125
SCALE = [2.0**((j%5)-2) for j in range(N)]
Y0 = [0.125*(j+1) for j in range(N)]
LAM = [0.5,0.75,1.25,1.5]
ALPHA = 0.25
B = [0.125,-0.25,0.5,0.0625]
FORCING = 0.125
LEDGER_ROWS = [2,3,4,5,6,7,10]
E = [0.03125*(j+1) for j in range(19)]
A = {j: 0.0625*(p+1) for p,j in enumerate(LEDGER_ROWS)}


def physical_matrix():
    m = [[0.0]*N for _ in range(N)]
    for g in range(4):
        m[g][g] = -LAM[g]
        m[g][4] = B[g]
    m[4][4] = -ALPHA
    for j in range(19):
        m[5+j][0] = E[j]
        m[5+j][4] = A.get(j,0.0)
    return m


def analytic(t):
    ea = math.exp(-ALPHA*t)
    result = [Y0[g]*math.exp(-LAM[g]*t)
        + B[g]*Y0[4]*(ea-math.exp(-LAM[g]*t))/(LAM[g]-ALPHA)
        + (FORCING*(t/LAM[g]-(1.0-math.exp(-LAM[g]*t))/LAM[g]**2) if g==0 else 0.0)
        for g in range(4)] + [Y0[4]*ea]
    ip = Y0[4]*(-math.expm1(-ALPHA*t))/ALPHA
    l = LAM[0]
    e0 = -math.expm1(-l*t)
    iy0 = Y0[0]*e0/l + B[0]*Y0[4]*((-math.expm1(-ALPHA*t))/ALPHA-e0/l)/(l-ALPHA)
    iy0 += FORCING*(t*t/(2*l)-t/(l*l)+e0/(l*l*l))
    result += [Y0[5+j]+E[j]*iy0+A.get(j,0.0)*ip for j in range(19)]
    return result


def run_case(lib, mode, *, prepare_failure=False, max_attempts=10000, max_step=0.25):
    errors=[];calls={'rhs':0,'jvp':0,'prepare':0,'partial':0}
    matrix=physical_matrix()
    def guard(fn):
        def wrapped(*args):
            try: return fn(*args)
            except BaseException:
                errors.append(traceback.format_exc()); return 42
        return wrapped
    @RHS
    @guard
    def rhs(_,u,z,n,out):
        assert n==N;calls['rhs']+=1
        y=[z[j]*SCALE[j] for j in range(n)]
        for row in range(n):
            total=0.0
            for col in range(n):
                if matrix[row][col]!=0.0: total += matrix[row][col]*y[col]
            if row==0: total += FORCING*(DT*u)
            out[row]=(DT*total)/SCALE[row]
        return 0
    @RHS
    @guard
    def partial(_,u,z,n,out):
        assert n==N;calls['partial']+=1
        for j in range(n):out[j]=0.0
        out[0]=(DT*DT*FORCING)/SCALE[0]
        return 0
    @JVP
    @guard
    def jvp(_,u,z,v,n,out):
        assert n==N;calls['jvp']+=1
        direction=[v[j]*SCALE[j] for j in range(n)]
        for row in range(n):
            total=0.0
            for col in range(n):
                a=matrix[row][col]
                if a!=0.0:total += a*direction[col]
            out[row]=(DT*total)/SCALE[row]
        return 0
    @PREPARE
    @guard
    def prepare(_,u,z,n,gas,photon):
        assert n==N;calls['prepare']+=1
        if prepare_failure:return 73
        for row in range(n):
            for col in range(4):gas[row*4+col]=matrix[row][col]
        rows=list(range(4))+[4]+[5+j for j in LEDGER_ROWS]
        for pack,row in enumerate(rows):photon[pack]=matrix[row][4]
        return 0
    state=(C.c_double*N)(*[y/s for y,s in zip(Y0,SCALE)])
    output=(C.c_double*N)(*[math.nan]*N);scale=(C.c_double*N)(*SCALE)
    stats=Stats();buf=C.create_string_buffer(65536)
    start=time.perf_counter()
    if mode=='legacy':
        rc=lib.he29_vigilode_segment(N,state,rhs,jvp,partial,None,0.01,max_step,
                                    max_attempts,output,C.byref(stats),buf,len(buf))
    else:
        rc=lib.he29_vigilode_segment_packed(N,state,rhs,prepare,partial,None,scale,DT,1,
                 0.01,max_step,max_attempts,output,C.byref(stats),buf,len(buf))
    elapsed=time.perf_counter()-start
    telemetry=json.loads(buf.value)
    assert not errors,errors
    return {'mode':mode,'status':rc,'stats':{name:getattr(stats,name) for name,_ in stats._fields_},
            'telemetry':telemetry,'physical_output':[output[j]*SCALE[j] for j in range(N)],
            'scaled_output_bytes_hex':bytes(output).hex(),'python_callback_counts':calls,
            'wall_seconds':elapsed,'errors':errors}


def atomic_json(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--library',required=True)
    parser.add_argument('--receipt',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();output_path=Path(args.output)
    result={'schema':'he29.optimized.packed_ffi_smoke.v1','status':'RUNNING',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'library_sha256':hashlib.sha256(Path(args.library).read_bytes()).hexdigest(),
            'build_receipt_sha256':hashlib.sha256(Path(args.receipt).read_bytes()).hexdigest(),
            'scope':'new packed ABI on analytic triangular n24 model; no HE29 native owner',
            'cases':[]}
    try:
        receipt=json.loads(Path(args.receipt).read_text())
        assert receipt['status']=='PASS_SCOPED'
        assert receipt['library']['sha256']==result['library_sha256']
        lib=C.CDLL(args.library);lib.he29_vigilode_abi_version.restype=C.c_uint32
        assert lib.he29_vigilode_abi_version()==2
        tail=[C.c_double,C.c_double,C.c_size_t,D,C.POINTER(Stats),C.POINTER(C.c_char),C.c_size_t]
        lib.he29_vigilode_segment.argtypes=[C.c_size_t,D,RHS,JVP,RHS,C.c_void_p]+tail
        lib.he29_vigilode_segment_packed.argtypes=[C.c_size_t,D,RHS,PREPARE,RHS,C.c_void_p,D,C.c_double,C.c_size_t]+tail
        lib.he29_vigilode_segment.restype=C.c_int32;lib.he29_vigilode_segment_packed.restype=C.c_int32
        old=run_case(lib,'legacy');result['cases'].append(old)
        new=run_case(lib,'packed');result['cases'].append(new)
        assert old['status']==new['status']==0
        assert old['scaled_output_bytes_hex']==new['scaled_output_bytes_hex']
        assert old['stats']['attempts']==new['stats']['attempts']
        expected=analytic(DT)
        error=max(abs(a-b) for a,b in zip(new['physical_output'],expected))
        assert error<=1e-9,error
        assert new['stats']['abi_version']==2
        assert new['stats']['callback_jvp_calls']==0
        assert new['telemetry']['packed_prepare_calls']==new['python_callback_counts']['prepare']>0
        assert new['telemetry']['packed_cache_hits']>0
        assert new['telemetry']['native_jvp_calls']==new['telemetry']['native_jvp_completed']>0
        result['paired_exact_output_bits']=True;result['analytic_max_abs_error']=error
        fail=run_case(lib,'packed',prepare_failure=True);result['cases'].append(fail)
        assert fail['status']==3 and fail['telemetry']['packed_prepare_calls']==1
        assert 'STATUS=73' in fail['telemetry']['callback_error']
        assert fail['telemetry']['native_jvp_completed']==0
        partial=run_case(lib,'packed',max_attempts=1,max_step=0.01);result['cases'].append(partial)
        assert partial['status']==1 and partial['stats']['output_samples']==1
        assert partial['stats']['final_u']==0.0
        assert partial['telemetry']['dense_output_used'] is False
        result['status']='PASS_SCOPED'
    except BaseException:
        result['status']='FAILED_PRESERVED';result['failure']=traceback.format_exc()
    atomic_json(output_path,result)
    print(json.dumps({'status':result['status'],'cases':len(result['cases']),
          'analytic_max_abs_error':result.get('analytic_max_abs_error'),'failure':result.get('failure')}))
    return 0 if result['status']=='PASS_SCOPED' else 1


if __name__=='__main__':sys.exit(main())
