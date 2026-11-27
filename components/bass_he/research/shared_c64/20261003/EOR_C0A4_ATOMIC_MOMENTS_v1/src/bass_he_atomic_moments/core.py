"""State-internal-energy moments of existing cross sections, never a heat model.

Exact Coulomb coefficients are rational. Native decimal inputs remain exact;
opt-in interpolants and integrated functionals use the parent's binary64 lane.
No mass, per-u convention, scattering threshold or physical uncertainty is inferred.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import math
import re
import sys
from typing import Any, Sequence

from bass_he_liu import Dataset, ContractError, SourceUnavailable
from bass_he_liu.native import strict_json
from bass_he_liu_interp import Interpolator, numerical_range

MODEL_ID='COULOMB_Z1_Z2_INFINITE_NUCLEAR_MASS_V1'
SNAPSHOT_SHA256='f78518dfd842cad3e12f68b0e2ef14f2a2c539fb2d920a9444fdcc35cd10235a'
DATASET_DOI='10.57760/sciencedb.j00113.00114'
FIELDS=('internal','chemical','excitation_change','excitation_initial','excitation_final')
NAMES=frozenset(('H1s-Capture cross sections.csv','H1s-Excitation cross sections.csv',
                'H2s-Capture cross sections.csv','H2s-Excitation cross sections.csv'))


def _model(model_id: str | None) -> None:
    if model_id != MODEL_ID:
        raise ContractError('EXPLICIT_SUPPORTED_ENERGY_MODEL_REQUIRED')


def coefficients(channel_id: str, *, model_id: str | None) -> dict[str,Fraction]:
    """Return signed event coefficients in E_h. Not original finite-basis energies."""
    _model(model_id)
    if not isinstance(channel_id,str):
        raise ContractError('CHANNEL_ID_REQUIRED')
    parts=channel_id.split(':')
    if len(parts)!=3 or parts[0] not in ('NR_CX','EXC') or parts[1] not in ('1s','2s'):
        raise ContractError('UNSUPPORTED_PROCESS_OR_INITIAL_STATE')
    process,initial,final=parts
    if final=='total':
        raise SourceUnavailable('TOTAL_SIGMA_HAS_NO_UNIQUE_INTERNAL_ENERGY_MOMENT')
    match=re.fullmatch(r'([1-9][0-9]{0,2})([spdfg])',final)
    if match is None: raise ContractError('RESOLVED_NL_STATE_REQUIRED')
    nf=int(match[1]); ell='spdfg'.index(match[2]); ni=int(initial[0])
    if ell>=nf or (process=='EXC' and nf<=ni):
        raise ContractError('INVALID_OR_UNSUPPORTED_QUANTUM_STATE')
    zf=2 if process=='NR_CX' else 1
    ei=-Fraction(1,2*ni*ni); ef=-Fraction(zf*zf,2*nf*nf)
    chem=-Fraction(zf*zf,2)+Fraction(1,2)
    ini=ei+Fraction(1,2); fin=ef+Fraction(zf*zf,2)
    return dict(zip(FIELDS,(ef-ei,chem,fin-ini,ini,fin)))


def validate_provider(raw_dir: str | Path, metadata_file: str | Path) -> dict[str,Any]:
    """Bind current bytes to a recovered historical provider snapshot, not live state."""
    raw_dir=Path(raw_dir); path=Path(metadata_file)
    if path.is_symlink(): raise ContractError('METADATA_SYMLINK_FORBIDDEN')
    payload=path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=SNAPSHOT_SHA256:
        raise ContractError('PROVIDER_SNAPSHOT_SHA_MISMATCH')
    meta=strict_json(payload.decode('utf-8'))
    if meta.get('identifier')!='https://doi.org/'+DATASET_DOI:
        raise ContractError('DATASET_DOI_MISMATCH')
    distributions=meta['distribution']
    if len(distributions)!=4 or {d['name'] for d in distributions}!=NAMES:
        raise ContractError('PROVIDER_FILESET_MISMATCH')
    matches=[]
    for d in distributions:
        file=raw_dir/d['name']
        if file.is_symlink(): raise ContractError('SOURCE_SYMLINK_FORBIDDEN')
        b=file.read_bytes()
        size=int(d['contentSize'].split()[0])
        digest=hashlib.md5(b).hexdigest()
        if len(b)!=size or digest!=d['md5']:
            raise ContractError('PROVIDER_FILE_SIZE_OR_MD5_MISMATCH: '+d['name'])
        matches.append({'name':d['name'],'provider_object_id':d['@id'],'bytes':len(b),
                        'md5':digest,'md5_matches':True,'sha256':hashlib.sha256(b).hexdigest(),
                        'source_url':d['contentUrl']})
    return {'schema':'bass-he.c0a4.provider-binding.v1','provider':'Science Data Bank',
            'dataset_doi':DATASET_DOI,'version':meta['version'],'date_published':meta['datePublished'],
            'license_uri':meta['license'],'metadata_sha256':SNAPSHOT_SHA256,'files':matches,
            'verification':'ARCHIVED_PROVIDER_SNAPSHOT_AND_PRESENT_BYTES_MATCH',
            'live_provider_queried_successfully':False,'archive_observed_at':'2026-09-30',
            'isotope':None,'per_u_divisor':None,'ordinate_unit_explicit':None,
            'ordinate_unit_contextual':'cm2, requires explicit acceptance in parent API',
            'source_uncertainty':None,'physical_certificate':False}


def _as_fraction(x: Any) -> Fraction:
    if isinstance(x,bool) or not isinstance(x,(str,int,Decimal,Fraction)):
        raise ContractError('EXACT_RATIONAL_INPUT_REQUIRED')
    try: return Fraction(x)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as e:
        raise ContractError('FINITE_RATIONAL_REQUIRED') from e


def basis_weight_interval(sigma_mean: Any, basis_coefficients: Sequence[Any]) -> dict[str,Any]:
    """Convex bracket if sigma_mean really averages nonnegative basis cross sections.

    This is a coefficient sensitivity interval, not an error bar on source truth.
    The nonnegative values sigma_j need not be known individually.
    """
    s=_as_fraction(sigma_mean)
    if s<0 or isinstance(basis_coefficients,str) or not basis_coefficients:
        raise ContractError('NONNEGATIVE_MEAN_AND_NONEMPTY_COEFFICIENTS_REQUIRED')
    q=[_as_fraction(v) for v in basis_coefficients]
    return {'lower':s*min(q),'upper':s*max(q),
            'semantics':'CONDITIONAL_COEFFICIENT_ENVELOPE_NOT_SOURCE_UQ',
            'requires':'same-index nonnegative sigma_j, exact mean and supplied coefficient set',
            'physical_certificate':False}


def _record(exact: Fraction | None, value: float | None, unit: str) -> dict[str,Any]:
    if exact is not None:
        with localcontext() as ctx:
            ctx.prec=34
            display=str(Decimal(exact.numerator)/Decimal(exact.denominator))
        return {'exact_fraction':str(exact),'value':display,'unit':'E_h * '+unit,
                'arithmetic':'exact_rational_native_tokens',
                'zero_kind':'EXACT_IN_STATED_ENERGY_MODEL' if exact==0 else None}
    assert value is not None
    numerical_range(value)
    return {'exact_fraction':None,'value':value,'unit':'E_h * '+unit,'arithmetic':'binary64',
            'zero_kind':'BINARY64_SIGNED_SUM_ZERO_NOT_PROOF' if value==0 else None}


class MomentProvider:
    """Source-backed internal-state energy changes. Every energy model is opt-in."""
    def __init__(self,dataset: Dataset,*,model_id: str | None,method: str | None=None,
                 scope: str='paper_domain'):
        _model(model_id)
        if not isinstance(dataset,Dataset):raise ContractError('SOURCE_DATASET_REQUIRED')
        if scope not in ('paper_domain','payload_domain'):raise ContractError('UNKNOWN_SCOPE')
        if method not in (None,'linear_E','loglog'):raise ContractError('UNKNOWN_INTERPOLATION_METHOD')
        self.dataset=dataset;self.model_id=model_id;self.method=method;self.scope=scope
        self.interpolator=Interpolator(dataset,method=method,scope=scope) if method else None

    def _members(self,ids: Sequence[str]) -> tuple[str,...]:
        if isinstance(ids,str) or not ids:raise ContractError('NONEMPTY_CHANNEL_LIST_REQUIRED')
        flat=tuple(c for cid in ids for c in self.dataset.members(cid))
        if any(c.endswith(':total') for c in flat):
            raise SourceUnavailable('TOTAL_SIGMA_HAS_NO_UNIQUE_INTERNAL_ENERGY_MOMENT')
        if len(flat)!=len(set(flat)):raise ContractError('OVERLAPPING_CHANNEL_SELECTION')
        if len({tuple(c.split(':')[:2]) for c in flat})!=1:
            raise ContractError('INCOMPATIBLE_INITIAL_STATE_OR_PROCESS')
        return flat

    def _base(self) -> dict[str,Any]:
        return {'energy_model_id':self.model_id,
                'energy_semantics':'INTERNAL_STATE_ENERGY_NOT_HEAT_OR_STOPPING',
                'nuclear_energy_or_threshold_inferred':False,'energy_zero':'bare nuclei + free electron',
                'heat':None,'recoil':None,'photon_spectrum':None,'momentum_transfer':None,
                'source_uncertainty':None,'interpolation_error_bound':None,'physical_certificate':False,
                'inclusive_all_bound':False,'source_basis_energy_averaging_claimed':False}

    def _one(self,cid: str,e: str | int | Decimal,unit: str,accept: bool) -> dict[str,Any]:
        q=coefficients(cid,model_id=self.model_id)
        if self.interpolator:
            s=self.interpolator.evaluate(cid,e,unit=unit,accept_contextual_unit=accept)
        else:
            s=self.dataset.sample(cid,e,unit=unit,accept_contextual_unit=accept,scope=self.scope)
        interpolated=s['interpolated']
        if not interpolated:
            v=Fraction(Decimal(s['value']))
            moments={k:_record(q[k]*v,None,unit) for k in FIELDS}
        else:
            v=float(s['value']);moments={}
            for k in FIELDS:
                x=float(q[k])*v
                if q[k]!=0 and v!=0 and x==0:raise ContractError('NUMERICAL_RANGE_ERROR: moment underflow')
                moments[k]=_record(None,x,unit)
                if q[k]==0:moments[k]['zero_kind']='EXACT_IN_STATED_ENERGY_MODEL'
        return {**self._base(),'channel_id':cid,'energy_token':s['energy_token'],
                'data_kind':'STATE_ENERGY_WEIGHTED_'+s['data_kind'],'sigma':s,
                'coefficients_E_h':{k:str(v) for k,v in q.items()},'moments':moments}

    def sample(self,channel_id: str,energy: str | int | Decimal,*,unit: str='source_native',
               accept_contextual_unit: bool=False) -> dict[str,Any]:
        members=self._members([channel_id])
        if len(members)>1:return self.aggregate([channel_id],energy,unit=unit,accept_contextual_unit=accept_contextual_unit)
        return self._one(members[0],energy,unit,accept_contextual_unit)

    def aggregate(self,channel_ids: Sequence[str],energy: str | int | Decimal,*,unit: str='source_native',
                  accept_contextual_unit: bool=False) -> dict[str,Any]:
        members=self._members(channel_ids)
        parts=[self._one(c,energy,unit,accept_contextual_unit) for c in members]
        exact=all(p['moments']['internal']['exact_fraction'] is not None for p in parts)
        if exact:
            moments={k:_record(sum((Fraction(p['moments'][k]['exact_fraction']) for p in parts),Fraction(0)),None,unit) for k in FIELDS}
        else:
            moments={k:_record(None,math.fsum(float(p['moments'][k]['value']) for p in parts),unit) for k in FIELDS}
        return {**self._base(),'data_kind':'RESOLVED_SUBSET_STATE_ENERGY_SUM','members':list(members),
                'energy_token':parts[0]['energy_token'],'moments':moments,'parts':parts,
                'source_values_modified':False,'missing_channels_filled':False}

    def functional(self,channel_ids: Sequence[str],lo: str | int | Decimal,hi: str | int | Decimal,*,
                   theta_native: float,unit: str='source_native',accept_contextual_unit: bool=False,
                   require_full: bool=False) -> dict[str,Any]:
        if not isinstance(require_full,bool):raise ContractError('FULL_FLAG_BOOLEAN_REQUIRED')
        if require_full:raise SourceUnavailable('FULL_ENERGY_MOMENT_REQUIRES_MISSING_CHANNELS_AND_TAILS')
        members=self._members(channel_ids)
        if self.method not in (None,'linear_E'):raise ContractError('FINITE_FUNCTIONAL_REQUIRES_LINEAR_E')
        interp=self.interpolator or Interpolator(self.dataset,method='linear_E',scope=self.scope)
        parts=[]
        for cid in members:
            f=interp.maxwell_functional(cid,lo,hi,theta_native=theta_native,unit=unit,accept_contextual_unit=accept_contextual_unit)
            q=coefficients(cid,model_id=self.model_id)
            moments={}
            for k in FIELDS:
                value=float(q[k])*f['value']
                if q[k] and f['value'] and value==0:raise ContractError('NUMERICAL_RANGE_ERROR: moment underflow')
                numerical_range(value); moments[k]=value
            parts.append({'channel_id':cid,'sigma_functional':f,'moments':moments})
        moments={}
        for k in FIELDS:
            ts=[p['moments'][k] for p in parts]
            value=math.fsum(ts);scale=math.fsum(abs(v) for v in ts)
            numerical_range(value);numerical_range(scale)
            moments[k]={'value':value,'positive_sum':math.fsum(v for v in ts if v>0),
                        'negative_sum':math.fsum(v for v in ts if v<0),'absolute_sum':scale,
                        'cancellation_ratio':None if scale==0 else abs(value)/scale,
                        'unit':'E_h * '+unit,'arithmetic':'binary64; exact model coefficients'}
        return {**self._base(),'data_kind':'FINITE_SUPPORT_RESOLVED_INTERNAL_ENERGY_FUNCTIONAL',
                'members':list(members),'native_interval':[str(lo),str(hi)],'theta_native':theta_native,
                'moments':moments,'parts':parts,'full_functional':None,'tail_bound':None,
                'renormalized_to_support':False,'physical_rate_computed':False,
                'theta_native_is_temperature':False}
