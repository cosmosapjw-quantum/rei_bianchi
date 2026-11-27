"""Opt-in postprocessing of the pinned E6 endpoint-rate product.

This module does not run the gas solver, re-evaluate atomic rates, interpolate
missing epochs, or replace producer columns. SHA checks bind data snapshots,
not physical truth. The pinned lock must change in a separately reviewed intake
when new histories or a different observer are adopted.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
from typing import Literal

LOCK_SHA256 = '1f6c1fbbdf487d64dae65fe690c92b9237d5b0cb6416d7d267a299288acd9b4b'
OBSERVER = 'E6_ENDPOINT_P512_Q4'

class BindingError(ValueError):
    """Input identity, clock, field ownership, or finite-value contract failed."""

@dataclass(frozen=True)
class RateRow:
    step: int
    s: float
    gamma: tuple[float,float,float]
    observer_N: float
    observer_E: float
    # Preserve the exact published decimal tokens, including their float bits.
    tokens: tuple[str,str,str,str,str,str]

@dataclass(frozen=True)
class RateAttachment:
    mode: str
    rows: tuple[RateRow,...]
    history_sha256: str
    rates_sha256: str
    config_sha256: str
    closure_mean_ev: float | None
    observer: str = OBSERVER
    units: str = 's^-1 per absorber'
    physical_admission: bool = False
    true_error_bound: None = None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse(data: bytes, required: tuple[str,...]) -> list[dict[str,str]]:
    try:
        reader=csv.DictReader(io.StringIO(data.decode('utf-8'),newline=''))
        names=reader.fieldnames
        if not names or len(set(names))!=len(names) or any(k not in names for k in required):
            raise BindingError('MISSING_OR_DUPLICATE_COLUMNS')
        rows=list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise BindingError('RAGGED_ROWS')
        return rows
    except (UnicodeError,csv.Error) as exc:
        raise BindingError('INVALID_CSV') from exc


def _num(token: str, *, nonnegative: bool=False) -> float:
    try:
        x=float(token)
    except (ValueError,OverflowError) as exc:
        raise BindingError('NONNUMERIC_FIELD') from exc
    if not math.isfinite(x) or (nonnegative and x<0):
        raise BindingError('NONFINITE_OR_NEGATIVE_RATE')
    return x


def _bits(x: float) -> bytes:
    return struct.pack('>d',x)


def _validate_rows(history: bytes, rates: bytes, m: dict) -> tuple[RateRow,...]:
    """Semantic join checks in addition to externally pinned byte identities."""
    hs=_parse(history,('step','s','x','y','z','w','activeN','activeE'))
    rs=_parse(rates,('mode','N','P','history_order','observer_order','step','s','x','y','z','w',
                    'Gamma_HI','Gamma_HeI','Gamma_HeII','Nph','Eph','nodes','nH','nHe','H'))
    if len(hs)!=m['N']+1 or len(rs)!=len(hs):
        raise BindingError('ROW_COUNT: no interpolation or partial-history padding')
    if _num(hs[0]['activeN'])!=0 or _num(hs[0]['activeE'])!=0:
        raise BindingError('NONZERO_INITIAL_STOCK')
    out=[]; last=None
    for j,(h,r) in enumerate(zip(hs,rs)):
        try:
            ids=[int(h['step']),int(r['step'])]
            declared=[int(r['N']),int(r['P']),int(r['history_order']),int(r['observer_order'])]
            nodes=int(r['nodes'])
        except ValueError as exc:
            raise BindingError('INTEGER_METADATA') from exc
        if ids!=[j,j] or r['mode']!=m['mode'] or declared!=[m['N'],m['base'],m['history_order'],m['observer_order']]:
            raise BindingError('MODE_OR_EPOCH_METADATA')
        if not 0<nodes<=4096:
            raise BindingError('ACTIVE_NODE_CAP')
        for key in ('s','x','y','z','w'):
            if _bits(_num(h[key]))!=_bits(_num(r[key])):
                raise BindingError('CLOCK_OR_STATE_BITS_DIFFER')
        s=_num(r['s'])
        if last is not None and s<=last:
            raise BindingError('NONINCREASING_CLOCK')
        last=s
        for key in ('nH','nHe','H'):
            if _num(r[key])<=0:
                raise BindingError('INVALID_BACKGROUND_METADATA')
        keys=('s','Gamma_HI','Gamma_HeI','Gamma_HeII','Nph','Eph')
        tokens=tuple(r[k] for k in keys)
        gamma=tuple(_num(r[k],nonnegative=True) for k in keys[1:4])
        nn=_num(r['Nph'],nonnegative=True); ee=_num(r['Eph'],nonnegative=True)
        if j==0 and (gamma!=(0.,0.,0.) or nn!=0 or ee!=0):
            raise BindingError('DARK_INITIAL_OBSERVER')
        out.append(RateRow(j,s,gamma,nn,ee,tokens))
    return tuple(out)


def _member(root: Path, relative: str) -> Path:
    p=root/relative
    if not p.resolve().is_relative_to(root.resolve()):
        raise BindingError('SOURCE_PATH_ESCAPES_DATA_ROOT')
    return p


def load_attachment(data_root: Path, mode: str, *, history_path: Path|None=None,
                    config_path: Path|None=None) -> RateAttachment:
    root=Path(data_root)
    raw_lock=(root/'SOURCE_LOCK.json').read_bytes()
    if _sha(raw_lock)!=LOCK_SHA256:
        raise BindingError('LOCK_SHA: a new intake is required, not a silent relabel')
    lock=json.loads(raw_lock)
    if mode not in lock['series']:
        raise BindingError('UNDECLARED_MODE')
    m=lock['series'][mode]
    cfg=(Path(config_path) if config_path is not None else _member(root,lock['config']['path'])).read_bytes()
    if _sha(cfg)!=lock['config']['sha256']:
        raise BindingError('CONFIG_SHA')
    history=(Path(history_path) if history_path is not None else _member(root,m['history']['path'])).read_bytes()
    rates=_member(root,m['rates']['path']).read_bytes()
    if len(history)!=m['history']['bytes'] or _sha(history)!=m['history']['sha256']:
        raise BindingError('HISTORY_SHA')
    if len(rates)!=m['rates']['bytes'] or _sha(rates)!=m['rates']['sha256']:
        raise BindingError('RATE_PRODUCT_SHA')
    rows=_validate_rows(history,rates,m)
    return RateAttachment(mode,rows,_sha(history),_sha(rates),_sha(cfg),m['closure_mean_ev'])


def _write_bytes(path: Path, data: bytes) -> None:
    # Destination directory is reserved first and never reused. READY is last.
    with path.open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())


def export_for_consumer(data_root: Path, mode: str, output: Path, *,
                        readout: Literal['disabled','endpoint']='disabled',
                        history_path: Path|None=None, config_path: Path|None=None) -> dict|None:
    """Return None without any I/O by default; opt-in creates a separate product.

    No target file, rate, photon inventory, or producer ledger is overwritten.
    A consumer must require READY.json and verify the declared CSV hash. This
    is not a power-loss or distributed-writer durability certificate.
    """
    if readout=='disabled':
        return None
    if readout!='endpoint':
        raise BindingError('UNKNOWN_READOUT; no implicit fallback')
    attachment=load_attachment(data_root,mode,history_path=history_path,config_path=config_path)
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(('step','ln_a','ln_a_bits','Gamma_HI_s_inv','Gamma_HeI_s_inv','Gamma_HeII_s_inv',
                     'observer_N_photons_per_H','observer_E_erg_per_H'))
    for r in attachment.rows:
        writer.writerow((r.step,r.tokens[0],_bits(r.s).hex(),*r.tokens[1:]))
    csv_bytes=stream.getvalue().encode('utf-8')
    ready={'schema':'bass-he.e7.consumer-sidecar.v1','state':'READY','row_count':len(attachment.rows),
           'observer':OBSERVER,'mode':mode,'source_lock_sha256':LOCK_SHA256,
           'source_history_sha256':attachment.history_sha256,'source_rate_product_sha256':attachment.rates_sha256,
           'source_config_sha256':attachment.config_sha256,'sidecar_sha256':_sha(csv_bytes),
           'sidecar':'endpoint_rates.csv','selection_is_explicit':True,'closure_mean_ev':attachment.closure_mean_ev,
           'atomic_mean_photon_energy':None,'units':'Gamma: s^-1 per absorber; observer N: photons/H; observer E: erg/H',
           'producer_columns_unchanged':True,'feedback_into_solver':False,'physical_admission':False,
           'true_error_bound':None,'finite_evidence':'E6 attached-data lineage, a=1e-22/s and r=1e-6; not a true-error radius',
           'continuous_epoch_interpolation':'NOT_PROVIDED','owner_remote_adoption':False}
    output=Path(output)
    # All input/semantic checks finish before reserving an output location.
    output.mkdir(parents=False,exist_ok=False)
    _write_bytes(output/'endpoint_rates.csv',csv_bytes)
    _write_bytes(output/'READY.json',(json.dumps(ready,indent=2,sort_keys=True)+'\n').encode())
    fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return ready


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data')
    p.add_argument('--mode',choices=['OFF','KF','GM'],default='OFF')
    p.add_argument('--readout',choices=['disabled','endpoint'],default='disabled')
    p.add_argument('--history',type=Path)
    p.add_argument('--config',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=export_for_consumer(a.data,a.mode,a.output,readout=a.readout,history_path=a.history,config_path=a.config)
    print(json.dumps({'state':'DISABLED_NO_IO'} if result is None else result,indent=2))


def consume_export(output: Path, data_root: Path, mode: str, *,
                   history_path: Path|None=None, config_path: Path|None=None) -> RateAttachment:
    """Receiver-side validation; an incomplete export is never accepted.

    The expected mode must be specified by the consumer. It is not inferred
    from the manifest or from near-identical numerical states.
    """
    output=Path(output)
    try:
        ready=json.loads((output/'READY.json').read_bytes())
    except (FileNotFoundError,json.JSONDecodeError) as exc:
        raise BindingError('READY_MARKER_MISSING_OR_INVALID') from exc
    a=load_attachment(data_root,mode,history_path=history_path,config_path=config_path)
    expected={'state':'READY','schema':'bass-he.e7.consumer-sidecar.v1','observer':OBSERVER,'mode':mode,
              'row_count':len(a.rows),'source_lock_sha256':LOCK_SHA256,
              'source_history_sha256':a.history_sha256,'source_rate_product_sha256':a.rates_sha256,
              'source_config_sha256':a.config_sha256,'closure_mean_ev':a.closure_mean_ev,
              'sidecar':'endpoint_rates.csv','physical_admission':False,'true_error_bound':None,
              'feedback_into_solver':False,'atomic_mean_photon_energy':None}
    if any(k not in ready or ready[k]!=v for k,v in expected.items()):
        raise BindingError('EXPORT_BINDING_MISMATCH')
    data=(output/'endpoint_rates.csv').read_bytes()
    if _sha(data)!=ready.get('sidecar_sha256'):
        raise BindingError('SIDECAR_SHA')
    rows=_parse(data,('step','ln_a','ln_a_bits','Gamma_HI_s_inv','Gamma_HeI_s_inv','Gamma_HeII_s_inv',
                     'observer_N_photons_per_H','observer_E_erg_per_H'))
    if len(rows)!=len(a.rows):raise BindingError('SIDECAR_ROW_COUNT')
    fields=('Gamma_HI_s_inv','Gamma_HeI_s_inv','Gamma_HeII_s_inv','observer_N_photons_per_H','observer_E_erg_per_H')
    for row,ref in zip(rows,a.rows):
        if row['step']!=str(ref.step) or row['ln_a_bits']!=_bits(ref.s).hex() or _bits(_num(row['ln_a']))!=_bits(ref.s):
            raise BindingError('SIDECAR_CLOCK_MISMATCH')
        for key,x in zip(fields,(*ref.gamma,ref.observer_N,ref.observer_E)):
            if _bits(_num(row[key],nonnegative=True))!=_bits(x):
                raise BindingError('SIDECAR_VALUE_MISMATCH')
    return a

if __name__=='__main__':main()
