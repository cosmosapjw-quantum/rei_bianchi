#!/usr/bin/env python3
"""BASS_HE HE17 R9: source-bound, read-only first-cell current/optical consumer.

This consumes, it does not rerun, the pinned R7/R8 certified exact-real finite
warm P01 source. No cold AXBI, new photon ODE, or full-observer probability is
silently inferred. It can optionally enclose an EXPLICIT separate foreground.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,zipfile
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction as Q
from pathlib import Path

class SourceContractError(ValueError):pass
ARCHIVE_SHA='b58f6e26ffdd4688efe32758bcee67b95c91786d1ec36c1d4eb8a4cdbe3f9ab9'
R7_ARCHIVE_SHA='f6d28d418900323aa0d1392c0a23d3d54ceb234eac3fd6f53163221887fc3ff1'
R7_RESULT_SHA='1b8124e1a45065d01854f8e79a86192a017fffcdeb3e3407f41c9661677042c5'
MEMORY_SHA='aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39'
SOURCE_REAL='HE17_WARM_P01_FT03_HM12_CASE_A'
SOURCE_COMMIT='a5c958c414dea41216b445c05f58df837f05cacb'
SOURCE_NPZ_SHA='3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be'
REFERENCE_SHA='7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be'
SIGMA=Q('6.6524587051e-29')


def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def q(v):
    if isinstance(v,bool):raise SourceContractError('NUMERIC_BOOLEAN_NOT_ALLOWED')
    try:return Q(v)
    except (ValueError,TypeError,ZeroDivisionError) as exc:raise SourceContractError('EXACT_RATIONAL_REQUIRED') from exc

def read_source_certificate(path):
    path=Path(path); data=path.read_bytes()
    if sha(data)!=ARCHIVE_SHA:raise SourceContractError('R8_ARCHIVE_BYTE_IDENTITY_MISMATCH')
    try:
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise SourceContractError('ZIP_CRC_FAILED')
            root='HE17_R8_20261014/'
            manifest=json.loads(z.read(root+'MANIFEST.json'))
            for rel,contract in manifest['files'].items():
                raw=z.read(root+rel)
                if len(raw)!=contract['bytes'] or sha(raw)!=contract['sha256']:
                    raise SourceContractError('MANIFEST_PAYLOAD_MISMATCH:'+rel)
            r7bytes=z.read(root+'inputs/R7_RESULT.json')
            mbytes=z.read(root+'inputs/ENDPOINT_MEMORY.json')
            parent=z.read(root+'inputs/R7_PARENT.zip')
            if sha(r7bytes)!=R7_RESULT_SHA or sha(mbytes)!=MEMORY_SHA or sha(parent)!=R7_ARCHIVE_SHA:
                raise SourceContractError('R7_PARENT_EVIDENCE_IDENTITY')
            with zipfile.ZipFile(__import__('io').BytesIO(parent)) as pz:
                if pz.testzip() is not None:raise SourceContractError('R7_PARENT_ZIP_CRC')
                root_r5='HE17_R7_20261014/inputs/R5/BASS_HE_HE17_R5_20261014/'
                contract=json.loads(pz.read(root_r5+'CONTRACT.json'))
                lineage=json.loads(pz.read(root_r5+'SOURCE_LINEAGE.json'))
                if (contract['source_npz_sha256']!=SOURCE_NPZ_SHA
                    or contract['selected_reference_sha256']!=REFERENCE_SHA
                    or contract['cell_s']!=['0','6250000000']
                    or lineage['receiver_commit']!=SOURCE_COMMIT
                    or lineage['input_sha256']['P01_STATE.npz']!=SOURCE_NPZ_SHA
                    or lineage['input_sha256']['FIXED_REFERENCE.npz']!=REFERENCE_SHA):
                    raise SourceContractError('R5_ORIGINAL_RECEIVER_BINDING_MISMATCH')
            r7=json.loads(r7bytes);mem=json.loads(mbytes)
            r8=json.loads(z.read(root+'results/ADOPTION_RESULT.json'))
            registry=json.loads(z.read(root+'SOURCE_REGISTRY.json'))
    except (zipfile.BadZipFile,KeyError,UnicodeDecodeError,json.JSONDecodeError) as exc:
        raise SourceContractError('MALFORMED_PINNED_CERTIFICATE') from exc
    if r8['R7_input_sha256']!=R7_RESULT_SHA or registry['sources']['R7']['archive_sha256']!=R7_ARCHIVE_SHA:
        raise SourceContractError('INCONSISTENT_PUBLISHED_LINEAGE')
    if (r8['stage']!='R8' or r7['stage']!='R7' or r7['chosen_parts']!=64
        or r8['chosen_parts']!=64 or r7['original_cell_s']!=['0','6250000000']
        or r8['source_interval_s']!=r7['original_cell_s']
        or mem['source_interval_s']!=r7['original_cell_s']
        or mem['fixed_reference_sha256']!=REFERENCE_SHA):
        raise SourceContractError('WRONG_REFERENCE_OR_TIME_SCOPE')
    photon=mem['photon_error_end_raw_exact']
    if len(photon)!=2904 or len(mem['gas_error_end_scaled'])!=4 or len(mem['compressed_hB_error_exact'])!=4:
        raise SourceContractError('CARRY_VECTOR_SHAPE_INVALID')
    if any(q(x)<0 for x in photon+mem['gas_error_end_scaled']):
        raise SourceContractError('NEGATIVE_ERROR_RADIUS')
    if mem['next_cell_majorants'] is not None or mem['not_a_second_cell_certificate'] is not True:
        raise SourceContractError('SECOND_CELL_SCOPE_INVALID')
    column=[q(x) for x in r7['column_interval_exact']]
    tau=[q(x) for x in r8['tau_interval_exact']]
    pt=[q(x) for x in r8['new_probability_interval_exact']]
    old=[q(x) for x in r8['old_probability_interval_exact']]
    if not (0<=column[0]<=column[1] and all(a*SIGMA==b for a,b in zip(column,tau))
        and r8['tau_interval_exact']==r7['tau_interval_exact']
        and q(r8['column_radius_exact'])==q(r7['chosen_radius_exact'])
        and 0<=pt[0]<=pt[1]<=1 and old[0]<=pt[0] and pt[1]<=old[1]):
        raise SourceContractError('CERTIFICATE_CROSS_FIELD_INCONSISTENCY')
    return dict(column=column,tau=tau,probability=pt,old_probability=old,
                column_radius=q(r8['column_radius_exact']),
                photon_error=tuple(q(x) for x in photon),
                gas_error=tuple(q(x) for x in mem['gas_error_end_scaled']),
                photon_digest=sha(mbytes), archive_digest=sha(data),
                verified_manifest=len(manifest['files']),
                read_only_source=SOURCE_REAL,source_commit=SOURCE_COMMIT,
                reference_sha=REFERENCE_SHA)


def poly(n:int,x:Q)->Q:
    from math import factorial
    return sum(((-1)**(k+1)*x**k/factorial(k) for k in range(1,n+1)),Q(0))


def foreground_probability(c, observer_foreground=None):
    """Observer-bin probability ONLY if the user supplies a bounded foreground T.

    0<=Tlo<=Thi<=1; exp(-T) in [1-S25(Thi), 1-S24(Tlo)]. This
    separate observer geometry/model input is not a HE17 source computation.
    """
    if observer_foreground is None:return {'status':'FOREGROUND_UNSPECIFIED','observer_probability':None}
    if not isinstance(observer_foreground,(list,tuple)) or len(observer_foreground)!=2:
        raise SourceContractError('FOREGROUND_INTERVAL_REQUIRED')
    lo,hi=map(q,observer_foreground)
    if not (0<=lo<=hi<=1):raise SourceContractError('FOREGROUND_REQUIRE_0_LE_TLO_LE_THI_LE_1')
    exp_lo=1-poly(25,hi);exp_hi=1-poly(24,lo)
    if not(0<=exp_lo<=exp_hi<=1):raise SourceContractError('INVALID_EXPONENTIAL_ENCLOSURE')
    result=[exp_lo*c['probability'][0],exp_hi*c['probability'][1]]
    return {'status':'CONDITIONAL_BOUNDED_FOREGROUND',
            'observer_probability':[str(x) for x in result],
            'foreground_T_exact':[str(lo),str(hi)],
            'qualification':'foreground interval must be supplied externally; no native full observer integration'}


def outward(x:Q,places:int=44,upper:bool=False)->str:
    # Fixed scientific display ONLY, not the exact bound stored in result.
    with localcontext() as ctx:
        ctx.prec=places;ctx.rounding=ROUND_CEILING if upper else ROUND_FLOOR
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def make_result(c, target=SOURCE_REAL, sigma=None, observer_foreground=None):
    if target!=SOURCE_REAL:raise SourceContractError('SOURCE_FAMILY_MISMATCH_COLD_OR_OTHER')
    if sigma is not None and q(sigma)!=SIGMA:raise SourceContractError('THOMSON_SIGMA_CONVENTION_CHANGED')
    fg=foreground_probability(c,observer_foreground)
    r={
       'schema':'bass-he-he17-r9-current-return-v1',
       'status':'SCOPED_FIRST_CELL_CERTIFICATE_CONSUMED',
       'source':{'scenario':SOURCE_REAL,'rei_bianchi_commit':SOURCE_COMMIT,
            'p01_npz_sha256':SOURCE_NPZ_SHA,
            'fixed_reference_sha256':REFERENCE_SHA,
            'proper_time_s':['0','6250000000'],
            'gas':'normal comoving, non-tilted LRS Bianchi I',
            'gas_thermal_coordinate':'eV per H nucleus',
            'atomic_source':'warm FT03/HM12 Case A; CR/RCT/HH OFF',
            'helium_number_ratio':'3/38',
            'electron_census':'chi_e=x_HII+(3/38)(x_HeII+2*x_HeIII)',
            'current':'J_e^a=c*nH_proper*chi_e*u^a; spatial-current term zero in this source'},
       'physical_contract':{'signature':'(-,+,+,+)','x0':'ct','u_u':-1,
           'age_gradient':'q_a=c*nabla_a(theta); u^a*q_a=1',
           'ray_D':'-u_a*k^a','age_A':'q_a*k^a>0',
           'general_column':'integral [(c*D/A)*n_e - (k_a*j_e^a)/A] dtheta',
           'current_case':'D/A=1, spatial j_e=0, sigma applied once',
           'photon_stock_units':'reference-volume cm^-3',
           'electron_density_units':'proper cm^-3 *1e6 -> proper m^-3'},
       'units':{'column':'m^-2','tau':'dimensionless','probability':'dimensionless','time':'s','sigma':'m^2'},
       'cross_section_m2':str(SIGMA),
       'column_interval_exact':[str(x) for x in c['column']],
       'column_interval_display':[outward(c['column'][0]),outward(c['column'][1],upper=True)],
       'column_radius_exact':str(c['column_radius']),
       'tau_interval_exact':[str(x) for x in c['tau']],
       'tau_interval_display':[outward(c['tau'][0]),outward(c['tau'][1],upper=True)],
       'conditional_scattering_probability_exact':[str(x) for x in c['probability']],
       'conditional_scattering_probability_display':[outward(c['probability'][0]),outward(c['probability'][1],upper=True)],
       'observer_probability':fg['observer_probability'],
       'foreground_status':fg['status'],
       'full_history_tau':None,'subsequent_cell_error':None,
       'photon_carry':{'count':len(c['photon_error']),
          'full_raw_error_values_sha256':c['photon_digest'],
          'location_in_original_R8_archive':'HE17_R8_20261014/inputs/ENDPOINT_MEMORY.json',
          'four_component_compression_valid_if_B_changes':False,
          'next_cell_majorants':None,'next_cell_physics':None,
          'gas_error_end_scaled_exact':[str(x) for x in c['gas_error']],
          'source_scope':'endpoint of first cell only; later B needs raw 2904-vector'},
       'verified_identity':{'R8_archive_sha256':c['archive_digest'],
          'manifest_bound_payloads':c['verified_manifest'],
          'nested_R7_archive_sha256':R7_ARCHIVE_SHA,
          'R7_RESULT_sha256':R7_RESULT_SHA,'ENDPOINT_MEMORY_sha256':MEMORY_SHA},
       'contract_checks':{'source_identity_bound':True,'source_time_bound':True,
          'finite_parent_records_verified':True,'column_tau_exact':True,
          'nested_readout':True,'original_R5_source_binding':True,'carry_shape_and_sign':True,
          'no_unsupported_second_cell':True,'all_pass':True},
       'science':{'claim':'first-cell exact-real finite warm P01 certificate reused',
          'scientific_error_input':'inherited R5/R7 interval evidence',
          'physical_model_calibration':'NOT_ASSESSED',
          'old_science_reexecuted':False,'native_receiver_integrated':False,
          'external_independent_review':'NOT_RUN',
          'full_observer_foreground':'UNSPECIFIED_UNLESS_EXTERNALLY_SUPPLIED'},
       'excluded_source_family':'cold AXBI Y_He=0.2454 / MD14/IGM, initial gas 8.098K; not warm FT03/HM12',
    }
    if observer_foreground is not None:r['explicit_foreground']=fg
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',required=True,type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--foreground-min',default=None)
    p.add_argument('--foreground-max',default=None)
    a=p.parse_args()
    if (a.foreground_min is None)!=(a.foreground_max is None):raise SystemExit('both foreground endpoints required')
    fg=None if a.foreground_min is None else [a.foreground_min,a.foreground_max]
    c=read_source_certificate(a.archive)
    result=make_result(c,observer_foreground=fg)
    if a.out.exists():raise SystemExit('refusing to overwrite an existing result')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':result['contract_checks'],'output':str(a.out),
      'source_ODE_RHS_calls':0,'observed_photon_carry':2904}))
if __name__=='__main__':main()
