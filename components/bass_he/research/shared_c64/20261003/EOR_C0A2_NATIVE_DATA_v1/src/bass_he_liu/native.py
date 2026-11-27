"""Source-native, non-interpolating access to the four supplied Liu CSV files.

The CSV files do not declare cross-section units. Converting their ordinates
requires explicit acceptance of the cm^2 assignment from the associated paper.
No rate coefficient, continuum probability or physical uncertainty is inferred.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class ContractError(ValueError):
    """Input semantics or provenance do not satisfy the declared contract."""


class SourceUnavailable(ContractError):
    """Requested source datum was not supplied. This is not a numerical zero."""


class DomainError(ContractError):
    """Requested energy or scope is outside the supplied contract."""


# Column indices below are zero based internally, one based in exported records.
# H1s capture has THREE energy blocks, not one energy column plus nine ordinates.
_LAYOUTS = {
    'H1s-Capture cross sections.csv': (
        'NR_CX', '1s', ('keV/u','tot capture','','1s','','2s','2p','3s','3p','3d'),
        ((0,1,'total'),(2,3,'1s'),(4,5,'2s'),(4,6,'2p'),(4,7,'3s'),(4,8,'3p'),(4,9,'3d'))),
    'H1s-Excitation cross sections.csv': (
        'EXC', '1s', ('keV/u','2s','2p','3s','3p','3d'),
        ((0,1,'2s'),(0,2,'2p'),(0,3,'3s'),(0,4,'3p'),(0,5,'3d'))),
    'H2s-Capture cross sections.csv': (
        'NR_CX', '2s', ('keV/u','tot capture','3s','3p','3d','4s','4p','4d','4f'),
        ((0,1,'total'),(0,2,'3s'),(0,3,'3p'),(0,4,'3d'),(0,5,'4s'),(0,6,'4p'),(0,7,'4d'),(0,8,'4f'))),
    'H2s-Excitation cross sections.csv': (
        'EXC', '2s', ('keV/u','3s','3p','3d','4s','4p','4d','4f'),
        ((0,1,'3s'),(0,2,'3p'),(0,3,'3d'),(0,4,'4s'),(0,5,'4p'),(0,6,'4d'),(0,7,'4f'))),
}
ENERGY_AXIS = 'projectile_keV_per_u_source'
_NUM = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?\Z')
_DERIVED = {
    'NR_CX:1s:n2': ('NR_CX:1s:2s','NR_CX:1s:2p'),
    'NR_CX:1s:n3': ('NR_CX:1s:3s','NR_CX:1s:3p','NR_CX:1s:3d'),
    'NR_CX:2s:n3': ('NR_CX:2s:3s','NR_CX:2s:3p','NR_CX:2s:3d'),
    'NR_CX:2s:n4': ('NR_CX:2s:4s','NR_CX:2s:4p','NR_CX:2s:4d','NR_CX:2s:4f'),
}
_ALIAS = {'NR_CX:1s:n1':'NR_CX:1s:1s'}


def _number(token: str, *, energy: bool = False) -> Decimal:
    if not isinstance(token,str) or len(token)>128 or not _NUM.fullmatch(token.strip()):
        raise ContractError('INVALID_NUMERIC_TOKEN')
    try:
        out=Decimal(token.strip())
    except InvalidOperation as exc:
        raise ContractError('INVALID_NUMERIC_TOKEN') from exc
    if not out.is_finite() or out<0 or (energy and out==0):
        raise ContractError('NONFINITE_OR_NEGATIVE_VALUE')
    return out


def _energy(value: str | int | Decimal) -> Decimal:
    if isinstance(value,bool) or not isinstance(value,(str,int,Decimal)):
        raise ContractError('EXACT_ENERGY_TOKEN_REQUIRED: use string, Decimal or integer')
    return _number(str(value),energy=True)


def _unique_object(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
    out={}
    for k,v in pairs:
        if k in out:
            raise ContractError('DUPLICATE_JSON_KEY: '+k)
        out[k]=v
    return out


def strict_json(payload: str) -> Any:
    def bad_constant(token: str) -> None:
        raise ContractError('NONFINITE_JSON: '+token)
    try:
        return json.loads(payload,object_pairs_hook=_unique_object,parse_constant=bad_constant)
    except (json.JSONDecodeError,UnicodeError) as exc:
        raise ContractError('INVALID_JSON') from exc


@dataclass(frozen=True)
class Sample:
    energy_token: str
    value_token: str
    source_line: int
    energy_column: int
    value_column: int

    @property
    def energy(self) -> Decimal:
        return _number(self.energy_token,energy=True)

    def as_dict(self) -> dict[str,Any]:
        return {'energy_token':self.energy_token,'value_token':self.value_token,
                'source_line':self.source_line,'energy_column':self.energy_column,
                'value_column':self.value_column}


@dataclass(frozen=True)
class Missing:
    energy_token: str
    source_line: int
    energy_column: int
    value_column: int


@dataclass(frozen=True)
class Channel:
    id: str
    source_name: str
    samples: tuple[Sample,...]
    missing: tuple[Missing,...]
    padding_lines: tuple[int,...]


@dataclass(frozen=True)
class Table:
    name: str
    sha256: str
    bytes: int
    header: tuple[str,...]
    rows: tuple[tuple[str,...],...]
    channels: tuple[Channel,...]
    bom_utf8: bool


def parse_csv(name: str, payload: bytes) -> Table:
    """Parse the *observed* layout, preserving every nonblank token and location."""
    if name not in _LAYOUTS:
        raise ContractError('UNRECOGNIZED_SOURCE_FILE')
    if not isinstance(payload,bytes):
        raise ContractError('SOURCE_BYTES_REQUIRED')
    try:
        text=payload.decode('utf-8-sig')
        rows=list(csv.reader(io.StringIO(text,newline=''),strict=True))
    except (UnicodeError,csv.Error) as exc:
        raise ContractError('INVALID_CSV') from exc
    process,initial,header,mapping=_LAYOUTS[name]
    if not rows or tuple(rows[0])!=header:
        raise ContractError('UNEXPECTED_HEADER')
    body=rows[1:]
    if not body or any(len(r)!=len(header) for r in body):
        raise ContractError('RAGGED_OR_EMPTY_CSV')
    if any('\n' in x or '\r' in x for r in rows for x in r):
        raise ContractError('MULTILINE_CELL_UNSUPPORTED')
    channels=[]
    for e_col,v_col,state in mapping:
        samples=[];missing=[];padding=[];previous=None
        for line,row in enumerate(body,2):
            et,vt=row[e_col],row[v_col]
            if not et.strip():
                if vt.strip():
                    raise ContractError(f'MISSING_ENERGY: line {line}, column {e_col+1}')
                padding.append(line)
                continue
            value_e=_number(et,energy=True)
            if previous is not None and value_e<=previous:
                raise ContractError('ENERGY_NOT_STRICTLY_INCREASING')
            previous=value_e
            if not vt.strip():
                missing.append(Missing(et,line,e_col+1,v_col+1))
                continue
            _number(vt)
            samples.append(Sample(et,vt,line,e_col+1,v_col+1))
        if not samples:
            raise ContractError('EMPTY_CHANNEL')
        channels.append(Channel(f'{process}:{initial}:{state}',name,tuple(samples),tuple(missing),tuple(padding)))
    return Table(name,hashlib.sha256(payload).hexdigest(),len(payload),header,
                 tuple(tuple(r) for r in body),tuple(channels),payload.startswith(b'\xef\xbb\xbf'))


def load_dataset(raw_dir: str | Path, input_lock: str | Path) -> 'Dataset':
    """Load only bytes matching the separately bound four-file source manifest."""
    raw_dir=Path(raw_dir)
    lock=strict_json(Path(input_lock).read_text(encoding='utf-8'))
    items=lock.get('csv',[])
    if len(items)!=4 or {r.get('name') for r in items}!=set(_LAYOUTS):
        raise ContractError('INPUT_LOCK_FILESET_MISMATCH')
    tables=[]
    for item in items:
        path=raw_dir/item['name']
        if path.is_symlink():
            raise ContractError('SOURCE_SYMLINK_FORBIDDEN')
        data=path.read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ContractError('HASH_MISMATCH: '+item['name'])
        tables.append(parse_csv(item['name'],data))
    return Dataset(tuple(tables))


class Dataset:
    """Exact native-node provider; queries never interpolate or zero-fill."""
    def __init__(self, tables: Sequence[Table]):
        self.tables=tuple(tables)
        channels={}
        for table in self.tables:
            for channel in table.channels:
                if channel.id in channels:
                    raise ContractError('DUPLICATE_CHANNEL')
                channels[channel.id]=channel
        self.channels: Mapping[str,Channel]=MappingProxyType(channels)
        self._samples={cid:{s.energy:s for s in c.samples} for cid,c in channels.items()}
        self._missing={cid:{_number(s.energy_token,energy=True):s for s in c.missing} for cid,c in channels.items()}
        self._hashes={t.name:t.sha256 for t in self.tables}

    def members(self, channel_id: str) -> tuple[str,...]:
        cid=_ALIAS.get(channel_id,channel_id)
        if cid in self.channels:
            return (cid,)
        if cid in _DERIVED and all(c in self.channels for c in _DERIVED[cid]):
            return _DERIVED[cid]
        raise SourceUnavailable('UNAVAILABLE_CHANNEL: '+channel_id)

    def available_energies(self, channel_id: str) -> tuple[Decimal,...]:
        members=self.members(channel_id)
        keys=set(self._samples[members[0]])
        for key in members[1:]:
            keys.intersection_update(self._samples[key])
        return tuple(sorted(keys))

    @staticmethod
    def _query_contract(e: Decimal, unit: str, accept: bool, scope: str, axis: str) -> Decimal:
        if axis!=ENERGY_AXIS:
            raise ContractError('ENERGY_AXIS_UNBOUND: no isotope/per-u conversion inferred')
        if scope not in ('paper_domain','payload_domain'):
            raise ContractError('UNKNOWN_SCOPE')
        if scope=='paper_domain' and not Decimal(1)<=e<=Decimal(200):
            raise DomainError('OUTSIDE_PAPER_SCOPE: raw value retained; request payload_domain explicitly')
        if unit not in ('source_native','cm2','m2'):
            raise ContractError('UNSUPPORTED_QUANTITY_OR_UNIT')
        if not isinstance(accept,bool):
            raise ContractError('UNIT_ACCEPTANCE_MUST_BE_BOOLEAN')
        if unit!='source_native' and not accept:
            raise ContractError('UNIT_BINDING_REQUIRED: CSV ordinate unit not declared')
        return Decimal('1e-4') if unit=='m2' else Decimal(1)

    def sample(self, channel_id: str, energy: str | int | Decimal, *,
               unit: str='source_native', accept_contextual_unit: bool=False,
               scope: str='paper_domain', energy_axis: str=ENERGY_AXIS) -> dict[str,Any]:
        e=_energy(energy)
        factor=self._query_contract(e,unit,accept_contextual_unit,scope,energy_axis)
        cid=_ALIAS.get(channel_id,channel_id)
        members=self.members(cid)
        if len(members)>1:
            out=self.aggregate(members,energy,unit=unit,accept_contextual_unit=accept_contextual_unit,
                               scope=scope,energy_axis=energy_axis)
            out['channel_id']=cid
            return out
        channel=self.channels[cid]
        if e in self._missing[cid]:
            raise SourceUnavailable('MISSING_VALUE: '+cid+' at '+str(energy))
        samples=self._samples[cid]
        if e not in samples:
            if e<min(samples) or e>max(samples):
                raise DomainError('OUTSIDE_CHANNEL_SUPPORT')
            raise SourceUnavailable('NOT_A_NATIVE_NODE: interpolation has not been requested or implemented')
        s=samples[e]
        with localcontext() as ctx:
            ctx.prec=80
            value=str(_number(s.value_token)*factor)
        return {**s.as_dict(),'channel_id':cid,'requested_channel_id':channel_id,
                'value':value,'unit':unit,'energy_axis':ENERGY_AXIS,
                'source_name':channel.source_name,'source_sha256':self._hashes[channel.source_name],
                'data_kind':'SOURCE_NATIVE_SAMPLE',
                'unit_binding':'CSV_ORDINATE_UNIT_UNDECLARED' if unit=='source_native' else 'PDF_CONTEXTUAL_CM2_NOT_CSV_HEADER',
                'outside_paper_stated_range':not Decimal(1)<=e<=Decimal(200),
                'per_u_divisor_definition':None,'isotope':None,'uncertainty':None,
                'interpolated':False,'physical_certificate':False,
                'inclusive_all_bound':False}

    def aggregate(self, channel_ids: Sequence[str], energy: str | int | Decimal, *,
                  unit: str='source_native', accept_contextual_unit: bool=False,
                  scope: str='paper_domain', energy_axis: str=ENERGY_AXIS) -> dict[str,Any]:
        if isinstance(channel_ids,str) or not channel_ids:
            raise ContractError('NONEMPTY_CHANNEL_LIST_REQUIRED')
        groups=[self.members(cid) for cid in channel_ids]
        flat=[x for group in groups for x in group]
        identities={tuple(cid.split(':')[:2]) for cid in flat}
        if len(identities)!=1:
            raise ContractError('INCOMPATIBLE_INITIAL_STATE_OR_PROCESS')
        if len(set(flat))!=len(flat) or (len(flat)>1 and any(x.endswith(':total') for x in flat)):
            raise ContractError('OVERLAPPING_CHANNEL_SELECTION')
        parts=[self.sample(cid,energy,unit=unit,accept_contextual_unit=accept_contextual_unit,
                           scope=scope,energy_axis=energy_axis) for cid in flat]
        with localcontext() as ctx:
            ctx.prec=80
            value=sum((Decimal(p['value']) for p in parts),Decimal(0))
        return {'requested_channels':list(channel_ids),'atomic_members':flat,
                'energy_token':str(energy),'energy_axis':ENERGY_AXIS,'unit':unit,'value':str(value),
                'data_kind':'DERIVED_EXACT_DISJOINT_SUM','source_parts':parts,
                'inclusive_all_bound':False,'interpolated':False,'physical_certificate':False,
                'unit_binding':parts[0]['unit_binding'],
                'outside_paper_stated_range':parts[0]['outside_paper_stated_range']}

    def to_dict(self) -> dict[str,Any]:
        tables=[]
        for t in self.tables:
            channels=[]
            for c in t.channels:
                channels.append({'id':c.id,'source_name':c.source_name,
                    'samples':[s.as_dict() for s in c.samples],
                    'missing':[{'energy_token':m.energy_token,'source_line':m.source_line,
                        'energy_column':m.energy_column,'value_column':m.value_column} for m in c.missing],
                    'padding_lines':list(c.padding_lines)})
            tables.append({'name':t.name,'sha256':t.sha256,'bytes':t.bytes,'header':list(t.header),
                           'rows':[list(r) for r in t.rows],'utf8_bom':t.bom_utf8,'channels':channels})
        return {'schema':'bass-he.liu2024.native-csv.v1','tables':tables,
                'energy_header':'keV/u','sigma_header_unit':None,
                'contextual_sigma_unit':'cm^2','contextual_unit_authority':'Liu2024 figures 2-10; explicit acceptance required',
                'native_source_values_available':True,'scientific_accuracy_certified':False,
                'source_uncertainty':None,'isotope':None,'per_u_divisor_definition':None,
                'remote_dataset_checksum_compared':False,'license':None,
                'source_association':'USER_SUPPLIED_ASSOCIATED_WITH_LIU2024',
                'source_interpolation':'NONE','derived_shell_members':{k:list(v) for k,v in _DERIVED.items()}}
