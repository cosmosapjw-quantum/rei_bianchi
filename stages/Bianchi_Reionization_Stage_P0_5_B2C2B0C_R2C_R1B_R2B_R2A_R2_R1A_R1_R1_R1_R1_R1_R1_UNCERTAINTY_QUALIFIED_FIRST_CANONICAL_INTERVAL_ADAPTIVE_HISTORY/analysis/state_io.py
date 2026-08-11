#!/usr/bin/env python3
"""Deterministic fail-closed adaptive-history state payloads."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,os,struct,tempfile
from pathlib import Path
from typing import Any
import numpy as np

MAGIC=b"REIADP1\0"; HEADER_LENGTH=struct.Struct("<Q")
ARRAY_ORDER=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")

@dataclass(frozen=True)
class DecodedState:
    metadata:dict[str,Any]; population_lower:np.ndarray; population_upper:np.ndarray
    log_temperature_lower:np.ndarray; log_temperature_upper:np.ndarray

def canonical_json_bytes(value:Any)->bytes:
    return json.dumps(value,allow_nan=False,ensure_ascii=True,separators=(",",":"),sort_keys=True).encode("ascii")
def sha256_bytes(payload:bytes)->str:return hashlib.sha256(payload).hexdigest()
def sha256_file(path:Path)->str:
    digest=hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""):digest.update(chunk)
    return digest.hexdigest()

def _arrays(plo,phi,tlo,thi):
    plo=np.ascontiguousarray(plo,dtype="<f8");phi=np.ascontiguousarray(phi,dtype="<f8")
    tlo=np.ascontiguousarray(tlo,dtype="<f8");thi=np.ascontiguousarray(thi,dtype="<f8")
    if plo.ndim!=2 or plo.shape[1]!=5 or phi.shape!=plo.shape:raise ValueError("population shape must be [nodes,5]")
    if tlo.shape!=(plo.shape[0],) or thi.shape!=tlo.shape:raise ValueError("temperature shape must be [nodes]")
    if any(np.any(~np.isfinite(a)) for a in (plo,phi,tlo,thi)):raise ValueError("state must be finite")
    if np.any(plo>phi) or np.any(tlo>thi):raise ValueError("lower bound exceeds upper")
    if np.any(plo<=0):raise ValueError("population lower bounds must be positive")
    return plo,phi,tlo,thi

def encode_state(metadata,plo,phi,tlo,thi)->bytes:
    if not isinstance(metadata,dict):raise TypeError("metadata must be dict")
    plo,phi,tlo,thi=_arrays(plo,phi,tlo,thi)
    header={"array_order":list(ARRAY_ORDER),"byte_order":"little","dtype":"float64","log_temperature_shape":list(tlo.shape),"metadata":metadata,"population_shape":list(plo.shape),"schema":1}
    h=canonical_json_bytes(header);body=b"".join(a.tobytes(order="C") for a in (plo,phi,tlo,thi))
    return MAGIC+HEADER_LENGTH.pack(len(h))+h+body

def decode_state(payload:bytes)->DecodedState:
    raw=bytes(payload);prefix=len(MAGIC)+HEADER_LENGTH.size
    if len(raw)<prefix or raw[:len(MAGIC)]!=MAGIC:raise ValueError("invalid state magic")
    (hlen,)=HEADER_LENGTH.unpack(raw[len(MAGIC):prefix]);end=prefix+hlen
    if end>len(raw):raise ValueError("truncated state header")
    try:header=json.loads(raw[prefix:end].decode("ascii"))
    except Exception as error:raise ValueError("invalid state header") from error
    fixed={"array_order":list(ARRAY_ORDER),"byte_order":"little","dtype":"float64","schema":1}
    if any(header.get(k)!=v for k,v in fixed.items()):raise ValueError("unsupported state header")
    try:pshape=tuple(map(int,header["population_shape"]));tshape=tuple(map(int,header["log_temperature_shape"]));metadata=header["metadata"]
    except Exception as error:raise ValueError("incomplete state header") from error
    if len(pshape)!=2 or pshape[1]!=5 or tshape!=(pshape[0],):raise ValueError("invalid state shapes")
    pc=pshape[0]*pshape[1];tc=tshape[0]
    if len(raw)-end!=(2*pc+2*tc)*8:raise ValueError("truncated arrays or trailing bytes")
    offset=end
    def take(count,shape):
        nonlocal offset
        out=np.frombuffer(raw,dtype="<f8",count=count,offset=offset).copy();offset+=count*8
        return np.ascontiguousarray(out.reshape(shape))
    plo,phi,tlo,thi=_arrays(take(pc,pshape),take(pc,pshape),take(tc,tshape),take(tc,tshape))
    if not isinstance(metadata,dict):raise ValueError("invalid state metadata")
    return DecodedState(metadata,plo,phi,tlo,thi)

def _fsync_dir(path:Path):
    fd=os.open(path,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def atomic_write_bytes(path:Path,payload:bytes):
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode="wb",prefix=f".{target.name}.tmp-",dir=target.parent,delete=False) as handle:
            temporary=Path(handle.name);handle.write(payload);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,target);temporary=None;_fsync_dir(target.parent)
    finally:
        if temporary is not None and temporary.is_file():temporary.unlink()
def write_state(path,metadata,plo,phi,tlo,thi):
    payload=encode_state(metadata,plo,phi,tlo,thi);atomic_write_bytes(Path(path),payload);return sha256_bytes(payload)
def read_state(path,*,expected_sha256=None):
    payload=Path(path).read_bytes();actual=sha256_bytes(payload)
    if expected_sha256 is not None and actual!=expected_sha256:raise ValueError(f"state SHA-256 mismatch: expected {expected_sha256}, observed {actual}")
    return decode_state(payload)
