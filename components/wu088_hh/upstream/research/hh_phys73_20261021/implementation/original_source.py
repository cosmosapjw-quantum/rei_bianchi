#!/usr/bin/env python3
"""Original HH zero-Dirichlet exterior source: actual Coulomb sample preparation.

The output is a binary64 quadrature diagnostic, never an interval certificate.
PHYS72 supplies continuous inverse/Born bounds; source_budget.py separately
bounds continuous source truncation. No completed D1/D2/D3 integration is used.
"""
from __future__ import annotations
import argparse
import concurrent.futures as cf
from datetime import datetime, timezone
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
SOURCE_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
MAGIC = b'HHG73V01'
OUTPUT_MAGIC = b'HHO73V01'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def write_new(path, data):
    path = Path(path)
    payload = json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n'
    with path.open('x') as stream:
        stream.write(payload)

def guarded_source():
    observed = sha(SOURCE)
    if observed != SOURCE_SHA:
        raise ValueError('frozen source SHA256 differs')
    return observed

def validated_request(lmax, nodes, angular_nodes, outer, dps):
    for value, name, low, high in [(lmax,'lmax',0,128),(nodes,'nodes',3,4097),
                                  (angular_nodes,'angular_nodes',8,1024),(dps,'dps',40,200)]:
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f'{name} must be integer {low}..{high}')
    if nodes % 2 != 1:
        raise ValueError('odd radial node count required')
    if isinstance(outer,bool) or not math.isfinite(outer) or not 27 < outer <= 65:
        raise ValueError('27 < outer <= 65 required')
    return dict(schema='PHYS73_ORIGINAL_SOURCE_GRID_V2',lmax=lmax,nodes=nodes,
                angular_nodes=angular_nodes,outer=float(outer),dps=dps,
                B='27',k='7/10',E_Hartree='49/200',eta_C='-10/7',
                radial_rule='composite_Simpson',angular_rule='analytic_positive_Yukawa_multipoles',
                angular_nodes_role='unused_legacy_diagnostic_parameter_no_angular_quadrature',
                phi='exp(-r)/sqrt(pi)',forcing='V*(r*phi)',boundary='zero_Dirichlet',
                frozen_source_sha256=SOURCE_SHA,HH_R10='OFF')

def angular_forcing(radii, lmax, angular_nodes=None):
    """Production source: exact positive formula, evaluated in binary64.

    angular_nodes is retained for CLI compatibility and is not used. Its role
    is explicit in the request. High-j binary64 Gauss projection is unsuitable.
    """
    from analytic_screen_source import angular_forcing as analytic
    return analytic(radii,lmax)

def gauss_angular_diagnostic(radii, lmax, angular_nodes):
    """Low-mode comparison only; never supplies the production source packet."""
    import numpy as np
    mu, weights = np.polynomial.legendre.leggauss(angular_nodes)
    p = np.polynomial.legendre.legvander(mu,lmax).T
    radii = np.asarray(radii)
    distance = np.sqrt(radii[:,None]**2+.49-1.4*radii[:,None]*mu[None,:])
    screen = 2*(1+1/distance)*np.exp(-2*distance)
    result = np.sqrt(2*np.arange(lmax+1)+1)[:,None] * (p @ (screen*weights).T)
    result *= (radii*np.exp(-radii))[None,:]
    if not np.isfinite(result).all():
        raise ArithmeticError('nonfinite original screened source')
    return result

def coulomb_task(spec):
    """Independent channel; direct high-precision Coulomb values, no Riccati march."""
    import mpmath as m
    from coulomb_cache import channel_cache
    ell, radii, dps, weighted_force, cache_root = spec
    begin=time.perf_counter()
    m.mp.dps=dps
    k=m.mpf(7)/10
    eta=-m.mpf(10)/7
    diagonal=[]
    ratios=[]
    cache_binding=dict(B='27',k='7/10',eta_C='-10/7',dps=dps,mpmath=m.__version__,
                       generator_sha256=sha(__file__),cache_code_sha256=sha(Path(__file__).with_name('coulomb_cache.py')))
    new_nodes=hits=0
    with channel_cache(cache_root,cache_binding,ell,m) as (values,cache_path):
        def at(radius):
            nonlocal new_nodes,hits
            key=float(radius).hex()
            if key in values:
                hits+=1;return values[key]
            rr=m.mpf(float(radius))
            fg=[m.coulombf(ell,eta,k*rr),m.coulombg(ell,eta,k*rr)]
            values[key]=fg;new_nodes+=1
            return fg
        fb,gb=at(27);hb=gb+1j*fb;previous=None
        for radius in radii:
            ff,gg=at(radius);hh=gg+1j*ff
            # F'G-FG'=1 in rho; phi'(B)=1 in r, hence division by k.
            dd=(gb*ff-fb*gg)/k*(hh/hb)
            tt=0 if previous is None else hh/previous
            if radius == 27:dd=m.mpc(0)
            dc,tc=complex(dd),complex(tt)
            if not all(math.isfinite(v) for v in (dc.real,dc.imag,tc.real,tc.imag)):
                raise ArithmeticError(f'nonfinite Coulomb packet ell={ell}')
            diagonal.append(dc);ratios.append(tc);previous=hh
    return dict(ell=ell,d=diagonal,t=ratios,x=[complex(v) for v in weighted_force],
                seconds=time.perf_counter()-begin,new_Coulomb_nodes=new_nodes,cache_hits=hits,
                cache_path=cache_path)

def worker_limits():
    import resource
    limit=2**30
    resource.setrlimit(resource.RLIMIT_AS,(limit,limit))

def encode_packet(path, tasks):
    if not tasks or not tasks[0]['d']:
        raise ValueError('nonempty packet required')
    nodes=len(tasks[0]['d'])
    with Path(path).open('xb') as stream:
        stream.write(MAGIC+struct.pack('<QQ',len(tasks),nodes))
        for task in tasks:
            for key in ('d','t','x'):
                if len(task[key]) != nodes:
                    raise ValueError('packet shape mismatch')
                for z in task[key]:
                    stream.write(struct.pack('<dd',z.real,z.imag))

def decode_output(path):
    import numpy as np
    raw=Path(path).read_bytes()
    if len(raw)<24 or raw[:8]!=OUTPUT_MAGIC:
        raise ValueError('invalid native output header')
    tasks,nodes=struct.unpack('<QQ',raw[8:24])
    if len(raw)!=24+16*tasks*nodes or not tasks or not nodes:
        raise ValueError('native output shape mismatch')
    out=np.frombuffer(raw,dtype='<c16',offset=24).reshape(tasks,nodes)
    if not np.isfinite(out).all():
        raise ValueError('nonfinite native output')
    return out

def prepare(directory, request, workers=1, cache=None):
    if type(workers) is not int or not 1<=workers<=64:
        raise ValueError('workers must be in 1..64')
    if not isinstance(request,dict):
        raise ValueError('complete original-source request required')
    expected=validated_request(request.get('lmax'),request.get('nodes'),
                               request.get('angular_nodes'),request.get('outer'),request.get('dps'))
    if request!=expected:
        raise ValueError('request fields or fixed physics differ')
    guarded_source()
    import numpy as np
    import mpmath
    from analytic_screen_source import backend_metadata
    root=Path(directory)
    if root.is_symlink():raise ValueError('preparation output symlink refused')
    root=root.resolve()
    binding=dict(request=request,source_code_sha256=sha(__file__),
                 cache_code_sha256=sha(Path(__file__).with_name('coulomb_cache.py')),
                 angular_code_sha256=sha(Path(__file__).with_name('analytic_screen_source.py')),
                 angular_backend=backend_metadata(),
                 python=platform.python_version(),numpy=np.__version__,mpmath=mpmath.__version__)
    fingerprint=hashlib.sha256(canonical(binding)).hexdigest()
    if root.exists():
        if root.is_symlink() or not root.is_dir():
            raise ValueError('ordinary preparation output directory required')
        receipt_path=root/'PREPARED.json'
        if receipt_path.exists():
            receipt=json.loads(receipt_path.read_text())
            if (receipt.get('schema')!='PHYS73_SOURCE_PREPARATION_RECEIPT_V1'
                    or receipt.get('status')!='PREPARED_BINARY64_DIAGNOSTIC'
                    or receipt.get('certified') is not False
                    or receipt.get('HH_R10')!='OFF'
                    or set(receipt.get('files_sha256',{}))!={'SOURCE_GREEN.bin','GRID.npz'}
                    or receipt.get('binding')!=binding or receipt.get('fingerprint')!=fingerprint):
                raise ValueError('existing source preparation identity differs')
            for name,digest in receipt['files_sha256'].items():
                if (root/name).is_symlink() or sha(root/name)!=digest:
                    raise ValueError('saved source packet hash mismatch')
            return {**receipt,'this_invocation':'REUSED_VERIFIED_NO_EVALUATIONS'}
        if any(root.iterdir()):
            raise ValueError('incomplete preparation exists: preserve and choose new output')
    else:
        root.mkdir(parents=True)
    started=time.perf_counter()
    radii=np.linspace(27,request['outer'],request['nodes'])
    h=(request['outer']-27)/(request['nodes']-1)
    weights=np.ones(request['nodes']);weights[1:-1:2]=4;weights[2:-1:2]=2;weights*=h/3
    force=angular_forcing(radii,request['lmax'],request['angular_nodes'])
    specs=[(ell,radii.tolist(),request['dps'],(force[ell]*weights).tolist(),str(Path(cache).resolve()) if cache else None)
           for ell in range(request['lmax']+1)]
    used=min(workers,len(specs))
    if used==1:
        tasks=[coulomb_task(spec) for spec in specs]
    else:
        # Each process owns mpmath's precision; no shared mutable global context.
        with cf.ProcessPoolExecutor(max_workers=used,mp_context=mp.get_context('spawn'),initializer=worker_limits) as pool:
            tasks=list(pool.map(coulomb_task,specs))
    encode_packet(root/'SOURCE_GREEN.bin',tasks)
    np.savez(root/'GRID.npz',r=radii,weights=weights,force=force)
    receipt=dict(schema='PHYS73_SOURCE_PREPARATION_RECEIPT_V1',binding=binding,fingerprint=fingerprint,
                 status='PREPARED_BINARY64_DIAGNOSTIC',certified=False,
                 scientific_scope='original_source_zero_Dirichlet_first_Green_action',
                 files_sha256={n:sha(root/n) for n in ('SOURCE_GREEN.bin','GRID.npz')},
                 requested_workers=workers,effective_workers=used,
                 channel_seconds=[{k:t[k] for k in ('ell','seconds','new_Coulomb_nodes','cache_hits','cache_path')} for t in tasks],
                 elapsed_seconds=time.perf_counter()-started,
                 created_utc=datetime.now(timezone.utc).isoformat(),
                 Coulomb_scalar_calls=2*sum(t['new_Coulomb_nodes'] for t in tasks),
                 cached_node_hits=sum(t['cache_hits'] for t in tasks),
                 process_worker_memory_limit_bytes=2**30 if used>1 else None,
                 old_panel_integrations=0,old_profile_integrations=0,
                 interior_matching_boundary_supplied=False,HH_R10='OFF')
    write_new(root/'PREPARED.json',receipt)
    return {**receipt,'this_invocation':'NEW_PREPARATION'}

def summarize(prepared, output):
    import numpy as np
    prepared=Path(prepared)
    receipt=json.loads((prepared/'PREPARED.json').read_text())
    if (receipt.get('schema')!='PHYS73_SOURCE_PREPARATION_RECEIPT_V1'
            or receipt.get('status')!='PREPARED_BINARY64_DIAGNOSTIC'
            or receipt.get('certified') is not False
            or set(receipt.get('files_sha256',{}))!={'SOURCE_GREEN.bin','GRID.npz'}):
        raise ValueError('invalid preparation receipt')
    for name,digest in receipt['files_sha256'].items():
        if (prepared/name).is_symlink() or sha(prepared/name)!=digest:
            raise ValueError('preparation payload changed')
    values=decode_output(output)
    with np.load(prepared/'GRID.npz',allow_pickle=False) as grid:
        r,w=grid['r'],grid['weights']
        if values.shape!=(receipt['binding']['request']['lmax']+1,len(r)):
            raise ValueError('output/preparation shape mismatch')
        norm=float(np.sqrt(np.sum(w[None,:]*np.abs(values/r[None,:])**2)))
        boundary=float(np.max(np.abs(values[:,0])))
    if boundary!=0:raise ValueError('nonzero source Dirichlet boundary')
    checked=verify_action(prepared/'SOURCE_GREEN.bin',values)
    return dict(schema='PHYS73_ORIGINAL_SOURCE_SAMPLE_RESULT_V1',
                status='FINITE_GRID_DIAGNOSTIC',certified=False,
                output_sha256=sha(output),input_sha256=sha(prepared/'SOURCE_GREEN.bin'),
                sample_Xminus_norm=norm,Dirichlet_boundary_max_abs=boundary,
                max_sample_abs=float(np.max(np.abs(values))),
                tasks=values.shape[0],radial_nodes=values.shape[1],
                quadrature_error_certified=False,roundoff_error_certified=False,
                finite_packet_action_check=checked,
                original_source=True,physical_matched_xi=False,HH_R10='OFF')

def verify_action(packet,values):
    """Independent phi/f cumulative implementation on the same quantized packet."""
    import numpy as np
    raw=Path(packet).read_bytes()
    if len(raw)<24 or raw[:8]!=MAGIC:raise ValueError('bad input packet')
    tasks,nodes=struct.unpack('<QQ',raw[8:24])
    if len(raw)!=24+48*tasks*nodes or values.shape!=(tasks,nodes):
        raise ValueError('input/output dimensions differ')
    array=np.frombuffer(raw,dtype='<c16',offset=24).reshape(tasks,3,nodes)
    errors=[]
    for task,out in zip(array,values):
        d,t,x=task
        f=np.ones(nodes,dtype=complex);f[1:]=np.cumprod(t[1:])
        if np.any(f==0) or not np.isfinite(f).all():
            raise ValueError('reference factorization left finite nonzero domain')
        phi=d/f
        lower=np.cumsum(phi*x)
        upper=np.zeros(nodes,dtype=complex)
        upper[:-1]=np.cumsum((f*x)[:0:-1])[::-1]
        expected=f*lower+phi*upper
        relative=float(np.max(np.abs(expected-out)))/max(float(np.max(np.abs(expected))),np.finfo(float).tiny)
        errors.append(relative)
    if max(errors)>3e-12:raise ValueError('output fails independent finite packet action')
    return dict(status='PASS_FINITE_PACKET_ACTION',maximum_channel_relative_difference=max(errors),
                threshold=3e-12,continuum_error_certified=False)

def main():
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key]='1'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--lmax',type=int,default=64)
    parser.add_argument('--nodes',type=int,default=257)
    parser.add_argument('--angular-nodes',type=int,default=128,
                        help='legacy diagnostic label only; the analytic source uses no angular quadrature')
    parser.add_argument('--outer',type=float,default=44)
    parser.add_argument('--dps',type=int,default=60)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--coulomb-cache',type=Path)
    parser.add_argument('--summarize',type=Path)
    args=parser.parse_args()
    if args.summarize:
        result=summarize(args.out,args.summarize)
    else:
        request=validated_request(args.lmax,args.nodes,args.angular_nodes,args.outer,args.dps)
        result=prepare(args.out,request,args.workers,args.coulomb_cache)
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__':
    main()
