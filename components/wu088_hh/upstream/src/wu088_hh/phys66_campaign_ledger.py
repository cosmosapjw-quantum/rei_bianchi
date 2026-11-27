"""PHYS66 typed analytic ledger for byte-verified old NCP payloads.

No inherited job is rerun, no inherited result flag is changed. Missing
numerical/angular errors remain None. Source archive and every payload digest
are checked before coefficient-wise analytic radial bounds are attached.
"""
from __future__ import annotations
from pathlib import Path,PurePosixPath
from fractions import Fraction as F
import hashlib,io,json,zipfile,math
import numpy as np
from .phys66_radial_budget import (coefficient_bounds,to_jsonable,numeric_summary,
                                  SOURCE_SHA,plan_radius)
EXPECTED_NCP_SHA='d7fa0b50ed803e19dfcec8f781219c03acbd21f8f3ee47fe922754f8fdb5ea79'
SOURCE='research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def claim_gate(analytic,numerical_error_bound=None,angular_error_bound=None):
    # This implementation has no validated numerical/angular certificate reader.
    # Supplying an arbitrary number must not silently become certification.
    if numerical_error_bound is not None or angular_error_bound is not None:
        raise ValueError('external error certificates require a separately verified interface')
    return {'analytic_component':analytic,'numerical_error_bound':None,
            'excluded_angular_error_bound':None,'total_error_certified':False,
            'HH_R10':'OFF'}

def _json(raw):
    return json.loads(raw,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

def _safe_path(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('unsafe archive relative path')
    return p

def _sha(data):return hashlib.sha256(data).hexdigest()

def inspect_archive(path:str|Path,expected_sha:str=EXPECTED_NCP_SHA)->dict:
    """Read and validate completed inherited PHYS64 source/results archive."""
    p=Path(path)
    if p.stat().st_size>32*1024**2:raise ValueError('archive exceeds bounded intake32MiB')
    raw=p.read_bytes()
    if _sha(raw)!=expected_sha:raise ValueError('NCP archive SHA mismatch')
    rows=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('duplicate archive path')
        for n in names:_safe_path(n)
        if sum(i.file_size for i in z.infolist())>128*1024**2:raise ValueError('uncompressed intake too large')
        if z.testzip() is not None:raise ValueError('archive CRC failure')
        manifest=_json(z.read('MANIFEST.json'))
        if set(names)!=set(manifest)|{'MANIFEST.json'}:raise ValueError('unmanifested or missing payload')
        for n,h in manifest.items():
            if _sha(z.read(n))!=h:raise ValueError('manifest mismatch '+n)
        source_name='source/'+SOURCE
        if _sha(z.read(source_name))!=SOURCE_SHA:raise ValueError('original input changed')
        with np.load(io.BytesIO(z.read(source_name)),allow_pickle=False) as inp:
            if inp['u'].shape!=(1386,) or inp['u'].dtype!=np.complex128:
                raise ValueError('original input shape/dtype')
        campaign=_json(z.read('results/CAMPAIGN.json'))
        runtime=campaign['runtime']
        if runtime['source_sha256']!=SOURCE_SHA:raise ValueError('runtime source binding mismatch')
        for n,h in runtime['code_sha256'].items():
            if _sha(z.read('source/'+n))!=h:raise ValueError('executed source binding mismatch')
        if campaign['all_angular_or_error_certificate'] is not False:
            raise ValueError('unexpected inherited certification claim')
        for row in campaign['cases']:
            if row.get('status')!='NUMERICAL_CASE_COMPLETE' or row.get('exit_code')!=0:
                raise ValueError('incomplete inherited case')
            folder='results/cases/'+row['key']+'/'
            stored=_json(z.read(folder+'SUCCESS.json'))
            if stored!=row:raise ValueError('case success/campaign disagreement')
            key_raw=json.dumps({'spec':row['spec'],'fingerprint':runtime['fingerprint']},sort_keys=True,allow_nan=False).encode()
            if _sha(key_raw)!=row['key']:raise ValueError('case key/config mismatch')
            if len(row['payloads'])!=2:raise ValueError('expected two immutable result payloads')
            for rel,h in row['payloads'].items():
                _safe_path(rel)
                if _sha(z.read(folder+rel))!=h:raise ValueError('case payload digest mismatch')
            prefix=folder+row['attempt']+'/'
            result=_json(z.read(prefix+'RESULT.json'))
            execution=_json(z.read(prefix+'EXECUTION.json'))
            request=_json(z.read(prefix+'REQUEST.json'))
            if execution!=stored or request['fingerprint']!=runtime['fingerprint']:
                raise ValueError('execution binding disagreement')
            if request['spec']!=row['spec']:raise ValueError('request/campaign spec')
            spec=row['spec'];ells=spec['ells'];m=spec['m'];n=len(ells);orders=spec['orders']
            if type(m) is not int or ells!=list(range(abs(m),max(ells)+1)) or max(ells)>64:
                raise ValueError('full finite signed-m block required')
            if result['source_sha256']!=SOURCE_SHA or result['runtime']!=runtime:
                raise ValueError('result/runtime source mismatch')
            if result['full_nonlinear_remainder_certified'] or result['spatial_and_roundoff_error_certified']:
                raise ValueError('unexpected prior total-error certification')
            for k in ('ells','m','outer','orders','nodes','rtol','max_step'):
                if result[k]!=spec[k]:raise ValueError('result config mismatch '+k)
            with np.load(io.BytesIO(z.read(prefix+'COEFFICIENTS.npz')),allow_pickle=False) as payload:
                co=payload['coefficients'];values=payload['contributions']
                if co.shape!=(orders,n,n) or values.shape!=co.shape:raise ValueError('coefficient shape')
                if not np.isfinite(co).all() or not np.isfinite(values).all():raise ValueError('nonfinite coefficient')
                scale=np.array([(3e-23)**(j+1) for j in range(orders)])[:,None,None]
                if not np.allclose(values,co*scale,rtol=3e-15,atol=0):raise ValueError('physical coefficient scaling')
                ij=tuple(result['reported_indices']);physical=[]
                for j,t in enumerate(result['terms']):
                    v=values[(j,)+ij];q=complex(*t['physical_entry'])
                    if abs(v-q)>3e-15*max(abs(v),abs(q),1e-300):raise ValueError('JSON/NPZ reported value')
                    physical.append([float(v.real),float(v.imag)])
            analytic=coefficient_bounds(max(ells),F(str(spec['outer'])),orders)
            rows.append({'key':row['key'],'spec':spec,'physical_entries':physical,
                         'payload_SHA256':row['payloads'],'unchanged_inherited_certification':{
                         'full_nonlinear_remainder_certified':False,'spatial_and_roundoff_error_certified':False},
                         'new_components':claim_gate(analytic),'display_noncertifying':numeric_summary(analytic)})
        successes=sum(n.endswith('/SUCCESS.json') for n in names)
    return {'schema':'PHYS66_VERIFIED_INHERITED_LEDGER_V1','archive_sha256':_sha(raw),
            'manifest_payload_count':len(manifest),'inherited_total_success_count':successes,
            'extended_cases_verified':len(rows),'new_NCP_jobs_executed':0,
            'runtime_inherited':runtime,'cases':rows,'HH_R10':'OFF',
            'total_numerical_error_certified':False,
            'new_plan':plan_radius(64,{1:'1e-30',2:'1e-54',3:'1e-78'})}
