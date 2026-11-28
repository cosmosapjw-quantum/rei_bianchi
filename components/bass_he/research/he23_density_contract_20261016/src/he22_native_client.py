"""Explicit bridge to the separately compiled original Rust HE22 point evaluator.

No guessed rates, no fallback on subprocess failure, no cross-source cache.
Native computation is not available in this ChatGPT container.
"""
from __future__ import annotations
from pathlib import Path
import subprocess, math, hashlib, json, os, time
from dataclasses import dataclass
import numpy as np
from he21_photo import Y_HE
from he22_contract import NativePoint

# Provenance only: frozen neutral HI, never native total hydrogen nuclei.
HISTORICAL_FROZEN_HI_Z20_CM3=0.0017575700008892194
OWNER_SOURCE_SHA='f7830e2f55e7a1938bc3c98f61b60651f8dae474'


def _atomic_record(path,payload):
    partial=path.with_suffix(path.suffix+'.partial')
    with partial.open('x') as f:
        json.dump(payload,f,indent=2,allow_nan=False)
        f.flush();os.fsync(f.fileno())
    os.link(partial,path)  # atomic create-only publication, fails on collision
    partial.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def record_evidence(directory, kind, payload):
    if directory is None: return
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    path=directory/f'{os.getpid()}_{time.monotonic_ns()}_{kind}.json'
    try:_atomic_record(path,payload)
    except Exception as exc:
        # Retain interrupted/invalid partial bytes separately from canonical JSON.
        _atomic_record(path.with_suffix('.failure'),dict(exception_type=type(exc).__name__,
            exception=str(exc),partial_name=path.name+'.partial'))
        raise
    return path


def native_run(argv,timeout,evidence_dir,kind,**metadata):
    try:
        p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout,check=False)
    except (subprocess.TimeoutExpired,OSError) as exc:
        def stream(value):
            return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else (value or '')
        record_evidence(evidence_dir,kind,dict(argv=argv,exception_type=type(exc).__name__,
            exception=str(exc),stdout=stream(getattr(exc,'stdout',None)),
            stderr=stream(getattr(exc,'stderr',None)),**metadata))
        raise
    record_evidence(evidence_dir,kind,dict(argv=argv,returncode=p.returncode,
        stdout=p.stdout,stderr=p.stderr,**metadata))
    return p


@dataclass(frozen=True)
class TotalNucleiDensity:
    a: float
    nh: float
    nhe: float
    source_sha: str
    binary_sha256: str


class NativeDensityProvider:
    """No rounded cache: each exact a is queried from the pinned native Driver.

    Source commit, binary content SHA and float.hex(a) identify each query.
    Caller build manifest independently binds this executable to actual owner source.
    """
    def __init__(self,binary,source_sha,evidence_dir=None):
        if source_sha!=OWNER_SOURCE_SHA:raise ValueError('HE23_OWNER_SOURCE_MISMATCH')
        self.binary=Path(binary).resolve();self.source_sha=source_sha
        self.binary_sha=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.evidence_dir=evidence_dir
    def __call__(self,a,x=None):
        if not math.isfinite(a) or not 1/21<=a<=1/5:raise ValueError('HE23_DENSITY_SCALE_DOMAIN')
        if hashlib.sha256(self.binary.read_bytes()).hexdigest()!=self.binary_sha:
            raise ValueError('HE23_BINARY_CHANGED')
        argv=[str(self.binary),'--density',format(a,'.17e')]
        p=native_run(argv,20,self.evidence_dir,'density',source_sha=self.source_sha,
            binary_sha256=self.binary_sha,a_hex=a.hex())
        if p.returncode:raise RuntimeError('HE23_DENSITY_NATIVE_ERROR: '+p.stderr)
        rows=p.stdout.strip().splitlines()
        if not rows or rows[0]!='HE23_TOTAL_NUCLEI_V1':raise ValueError('HE23_DENSITY_SCHEMA')
        fields=dict(row.split('\t') for row in rows[1:])
        if len(fields)!=4 or fields['SOURCE_COMMIT']!=self.source_sha:raise ValueError('HE23_DENSITY_SOURCE')
        ar,nh,nhe=(float(fields[k]) for k in ('A','NH_CM3','NHE_CM3'))
        if ar!=a or not all(math.isfinite(z) and z>0 for z in (nh,nhe)):
            raise ValueError('HE23_DENSITY_DOMAIN')
        if abs(nhe/nh/Y_HE-1)>1e-9:raise AssertionError('HE22_NATIVE_DENSITY_OR_HELIUM_SOURCE_MISMATCH')
        return TotalNucleiDensity(a,nh,nhe,self.source_sha,self.binary_sha)


REQUIRED=('NH_CM3','NHE_CM3','FRACTION_DT','W_DT_EV_PER_H_S','TEMP_K',
          'PHOTO_EVENTS','THERMAL_MICRO','BINDING_MICRO','ESCAPE','CMB_TO_GAS',
          'PHOTO_INPUT','CI_EVENTS','RR_EVENTS','DR_EVENTS')

def parse_native_point(text: str, expected_nh: float) -> NativePoint:
    rows=text.strip().splitlines()
    if not rows or rows[0]!='HE22_NATIVE_POINT_V1':
        raise ValueError('HE22_NATIVE_SCHEMA_MISMATCH')
    fields={}
    for line in rows[1:]:
        cols=line.split('\t')
        if len(cols)<2 or cols[0] in fields:
            raise ValueError('HE22_NATIVE_DUPLICATE_OR_EMPTY_FIELD')
        fields[cols[0]]=np.array([float(v) for v in cols[1:]])
    if not set(REQUIRED).issubset(fields):
        raise ValueError('HE22_NATIVE_FIELDS_MISSING')
    if not all(np.isfinite(v).all() for v in fields.values()):
        raise ValueError('HE22_NATIVE_NONFINITE')
    scalar=('NH_CM3','NHE_CM3','W_DT_EV_PER_H_S','TEMP_K','THERMAL_MICRO',
            'BINDING_MICRO','ESCAPE','CMB_TO_GAS','PHOTO_INPUT','DR_EVENTS')
    vector=('FRACTION_DT','PHOTO_EVENTS','CI_EVENTS','RR_EVENTS')
    if any(len(fields[k])!=1 for k in scalar) or any(len(fields[k])!=3 for k in vector):
        raise ValueError('HE22_NATIVE_BAD_FIELD_SHAPE')
    nh=fields['NH_CM3'][0]; nhe=fields['NHE_CM3'][0]
    if not (nh>0 and nhe>0 and expected_nh>0):
        raise ValueError('HE22_NATIVE_DENSITY_DOMAIN')
    if abs(nh/expected_nh-1)>1e-9 or abs(nhe/nh/Y_HE-1)>1e-9:
        raise AssertionError('HE22_NATIVE_DENSITY_OR_HELIUM_SOURCE_MISMATCH')
    if fields['TEMP_K'][0]<=0:
        raise ValueError('HE22_NATIVE_NEGATIVE_TEMPERATURE')
    f=fields
    return NativePoint(f['FRACTION_DT'],float(f['W_DT_EV_PER_H_S'][0]),
        float(f['TEMP_K'][0]),f['PHOTO_EVENTS'],
        float(f['THERMAL_MICRO'][0]),float(f['BINDING_MICRO'][0]),
        float(f['ESCAPE'][0]),float(f['CMB_TO_GAS'][0]),
        float(f['PHOTO_INPUT'][0]),f['CI_EVENTS'],f['RR_EVENTS'],float(f['DR_EVENTS'][0]))


class NativeRustPoint:
    def __init__(self, executable: str|Path, scale_factor: float,
                 expected_nh: float, timeout_s: float=20., evidence_dir=None):
        self.exe=Path(executable)
        if not self.exe.is_file(): raise FileNotFoundError(self.exe)
        if not math.isfinite(scale_factor) or not 1/21 <= scale_factor <= 1/5:
            raise ValueError('HE22_NATIVE_SCALE_DOMAIN')
        self.a=scale_factor
        self.nh=expected_nh
        self.timeout_s=timeout_s
        self.calls=0
        self.evidence_dir=evidence_dir
    def __call__(self,gas,gamma,power):
        g=np.asarray(gas,dtype=float)
        gr=np.asarray(gamma,dtype=float)
        ph=np.asarray(power,dtype=float)
        if g.shape!=(4,) or gr.shape!=(3,) or ph.shape!=(3,) or (
            not np.isfinite(g).all() or not np.isfinite(gr).all() or
            not np.isfinite(ph).all() or (gr<0).any() or (ph<0).any()):
            raise ValueError('HE22_NATIVE_CLIENT_INPUT')
        argv=[str(self.exe),*[format(float(v),'.17e')
              for v in (self.a,*g,*gr,*ph)]]
        p=native_run(argv,self.timeout_s,self.evidence_dir,'rhs',expected_nh=self.nh)
        self.calls+=1
        if p.returncode:
            raise RuntimeError('HE22_NATIVE_RUST_ERROR: '+p.stderr.strip())
        return parse_native_point(p.stdout,self.nh)
