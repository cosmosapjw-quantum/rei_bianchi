"""ENERGY06D: exact binary64 read-only birth angular measure audit.

Mathematical object:
* native stored binary64 per-direction source_weights, source_n, clocks
* exact rational interpretation of saved f64 values
* analysis-only normalization of those weights; never a source-code change

No new nonlinear roots, science dispatch, source fitting, or Bianchi trajectory.
"""
from __future__ import annotations
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path
import struct

class EvidenceError(ValueError):
    pass


def qfmt(x: Q) -> str:
    return str(x)


def _read_json(path: Path):
    try:
        return json.loads(path.read_text('utf-8'))
    except (ValueError, OSError) as e:
        raise EvidenceError(f'invalid source JSON {path.name}: {e}') from e


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _finite_float(x, name: str, positive: bool = False) -> float:
    if not isinstance(x, (float, int)) or not math.isfinite(x) or (positive and x <= 0):
        raise EvidenceError(f'nonfinite or nonpositive {name}')
    return float(x)


def inspect(root: Path | str) -> dict:
    root = Path(root)
    inputs = root / 'inputs'
    index_path = inputs / 'INPUT_IDENTITY.json'
    if index_path.exists():
        idx = _read_json(index_path)
        for rel, item in idx.get('contents', {}).items():
            if '..' in Path(rel).parts or Path(rel).is_absolute():
                raise EvidenceError('unsafe input identity path')
            p = root / rel
            if not p.is_file() or len(p.read_bytes()) != item['size'] or _sha(p) != item['sha256']:
                raise EvidenceError(f'source identity failed: {rel}')
    binding = _read_json(inputs / 'FINAL_SOURCE_BINDING_V4.json')
    for name in ['paired_runtime.rs','hh_paired_extension.rs']:
        source_path = inputs / 'source' / name
        if _sha(source_path) != binding['original_owner_sources'][name]:
            raise EvidenceError(f'authoritative pinned {name} mismatched')
    source = _read_json(inputs / 'SOURCE_LAW_AND_SCHEMES.json')
    if not source['same_underlying_source_law'] or not source['distinct_full_twohalf_birth_quadratures']:
        raise EvidenceError('birth operator identity does not match source scope')
    if source['law']['SOURCE'] != 5e-15 or source['law']['BIRTH'] != 13.7:
        raise EvidenceError('source law modified')
    if source['twohalf']['dt'] != [625000000.0,625000000.0]:
        raise EvidenceError('unexpected two half timing')
    tt = source['twohalf']['times']
    if len(tt) != 2 or source['full']['end'] != tt[1] or tt[0]-source['full']['t0'] != tt[1]-tt[0]:
        raise EvidenceError('source birth times mismatch')
    txt = (inputs / 'OWNER_PREBE_FINAL_BINARY.jsonl').read_text('utf-8')
    try:
        rows = [json.loads(line) for line in txt.splitlines() if line.strip()]
    except ValueError as e:
        raise EvidenceError('actual preBE rows are not JSONL') from e
    if len(rows) != 12:
        raise EvidenceError('missing original preBE rows')
    native_ledger = _read_json(inputs / 'BIRTH_LEDGER.json')
    logged = {(r['member'],r['stage']):r for r in native_ledger['rows']}
    by_member = {}
    native_checks=0
    for row in rows:
        member = row.get('member');label=row.get('label');key=(member,label)
        if member not in range(4) or label not in ('full_preBE','half1_preBE','half2_birth_weights_only'):
            raise EvidenceError('invalid member or stage label')
        if label in by_member.get(member,{}):
            raise EvidenceError('duplicated member and stage')
        if row.get('root_dispatch') not in (None,0,False,'not_dispatched','blocked'):
            # original console uses explanatory root string; reject only an actual boolean true
            if row.get('root_dispatch') is True:
                raise EvidenceError('science dispatch found')
        # The half2 record is explicitly weights-only: it has no source_bits,
        # energy_bits or endpoint state. Never fabricate those native observations.
        if label != 'half2_birth_weights_only':
            if row.get('source_bits') != struct.pack('>d',5e-15).hex():
                raise EvidenceError('native source bits differ from source law')
            if row.get('birth_energy_bits') != struct.pack('>d',13.7).hex():
                raise EvidenceError('native photon birth energy bits differ')
        source_n=_finite_float(row['source_n'],'source_n',True)
        if source_n != (6.25e-6 if label=='full_preBE' else 3.125e-6):
            raise EvidenceError('stage photon birth magnitude incorrect')
        w=row['source_weights']
        if len(w)!=128 or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in w):
            raise EvidenceError('source weights invalid')
        if key not in logged:
            raise EvidenceError('original exact ledger entry missing')
        raw_sum = sum((Q.from_float(float(source_n*float(v))) for v in w),Q(0))
        if raw_sum != Q(logged[key]['actual_direction_product_sum_exact']):
            raise EvidenceError('native binary64 photon product count changed')
        if raw_sum-Q.from_float(source_n)!=Q(logged[key]['sum_minus_nominal_exact']):
            raise EvidenceError('original native product drift changed')
        native_checks += 1
        by_member.setdefault(member,{})[label]={'row':row,'ledger':logged[key],'raw_sum':raw_sum,'weights':[Q.from_float(float(v)) for v in w]}
    members=[]
    total_moment=Q(0)
    for member in range(4):
        table=by_member.get(member,{})
        if set(table)!= {'full_preBE','half1_preBE','half2_birth_weights_only'}:
            raise EvidenceError('missing member stage')
        full,half1,half2=[table[k] for k in ('full_preBE','half1_preBE','half2_birth_weights_only')]
        wf, w1, w2 = [r['weights'] for r in (full,half1,half2)]
        if wf!=w2:
            raise EvidenceError('full and half2 source weights differ at same endpoint')
        F = Q.from_float(full['row']['source_n'])
        H = Q.from_float(half1['row']['source_n'])
        if F != 2*H or H!=Q.from_float(half2['row']['source_n']):
            raise EvidenceError('binary64 full and two half birth counts differ')
        s1=sum(w1,Q(0));s2=sum(w2,Q(0))
        if s1<=0 or s2<=0:
            raise EvidenceError('nonpositive directional normalization')
        # Analysis-only ideal rational reweighting of the native stored f64 weights.
        diff=[H*(a/s1-b/s2) for a,b in zip(w1,w2)]
        pos=sum((v for v in diff if v>0),Q(0))
        neg=sum((v for v in diff if v<0),Q(0))
        signed=sum(diff,Q(0))
        if signed!=0 or pos!=-neg:
            raise EvidenceError('rational angular conservation failed')
        tv=(pos-neg)/2
        # Source-index readout on the 8 mu x 16 phi grid. This uses the
        # nominal dyadic mu-centres, not a reconstructed continuous quadrupole.
        p2=[]
        for d in range(128):
            imu=d//16
            mu=Q(-1,1)+Q(2,1)*(Q(imu,1)+Q(1,2))/Q(8,1)
            p2.append((3*mu*mu-1)/2)
        q2=sum((v*kernel for v,kernel in zip(diff,p2)),Q(0))
        range_k=max(p2)-min(p2)
        bound=range_k*tv
        if abs(q2)>bound:
            raise EvidenceError('P2 moment exceeds exact zero-sum TV bound')
        true_raw_count = half1['raw_sum']+half2['raw_sum']-full['raw_sum']
        # Centre at full endpoint to prevent catastrophic cancellation in clocks.
        t1=Q.from_float(half1['row']['endpoint_time']);t2=Q.from_float(full['row']['endpoint_time'])
        if (t1,t2)!=(Q.from_float(tt[0]),Q.from_float(tt[1])):
            raise EvidenceError('native birth clocks disagree')
        centered_m1=(t1-t2)*H
        total_moment+=centered_m1
        members.append({
            'member':member,'background':('FLRW' if member<2 else 'Bianchi-I'),
            'directions':128,'stages_checked':3,
            'full_half2_weights_binary64_identical':True,'native_ledger_per_stage_matches':3,
            'source_weight_f64_sums':{'half1':qfmt(s1),'full_and_half2':qfmt(s2)},
            'native_first_half_fraction':qfmt(half1['raw_sum']),
            'native_second_half_fraction':qfmt(half2['raw_sum']),
            'native_full_fraction':qfmt(full['raw_sum']),
            'native_f64_count_defect_fraction':qfmt(true_raw_count),
            'native_f64_count_defect_float':float(true_raw_count),
            'exact_normalized_count_defect_fraction':'0',
            'centered_M1_normalized_fraction':qfmt(centered_m1),
            'centered_M1_normalized_float':float(centered_m1),
            'angular_transport':{
                'signed_mass_fraction':qfmt(signed),'positive_fraction':qfmt(pos),
                'negative_fraction':qfmt(neg),'positive_fraction_float':float(pos),
                'normalized_total_variation_photons_per_H_fraction':qfmt(tv),
                'normalized_total_variation_photons_per_H':float(tv),
                'normalized_total_variation_fraction_of_total_birth':float(tv/F),
                'L1_signed_redistribution_photons_per_H':float(2*tv),
                'full_half2_normalized_total':qfmt(F),
                'P2_axis_reference':{
                    'description':'analysis-only P2(mu)=0.5(3mu^2-1) on native 8x16 grid; no BE source or sky multipole',
                    'moment_fraction':qfmt(q2),
                    'moment_float':float(q2),
                    'normalized_moment_fraction_of_total_birth':float(q2/F),
                    'exact_positive_upper_bound_fraction':qfmt(bound),
                    'strict_tv_bound_verified':True,
                    'grid_mu_centres':'mu_i=-1+2*(i+1/2)/8; each used 16 phi directions',
                },
            },
        })
    if native_checks!=12:
        raise EvidenceError('not all native rows verified')
    root_gate = _read_json(inputs/'ROOT_AND_GATE_RESULTS.json')
    c1 = _read_json(inputs/'C1_FULL_BOX_FEASIBILITY.json')
    proposal = _read_json(inputs/'TWO_CELL_NEW_SCOPE_PROPOSAL_V3.json')
    if c1['whole_physical_boxes_inclusion'] or c1['holomorphic_derivative_admission'] or c1['sign_rank_admission']:
        raise EvidenceError('C1 input falsely marked admitted')
    if proposal['authorization_record'] is not None or proposal.get('dispatch_count',-1)!=0:
        raise EvidenceError('C1 input not approved for read-only audit')
    if root_gate['actual_new_root_inclusion'] is not None or root_gate['new_coupled_root']:
        raise EvidenceError('unexpected scientific owner root mutation')
    return {
        'task':'HH_ENERGY06D_REAL_DIRECTIONAL_BIRTH_PAIRING',
        'status':'EXACT_STORED_SOURCE_ANGULAR_REDISTRIBUTION_VERIFIED__COUPLED_SCIENCE_OPEN',
        'fixed_source':{'source_f64_hex':(5e-15).hex(),'energy_f64_hex':(13.7).hex(),
                        'full_count_fraction':qfmt(Q.from_float(6.25e-6)),
                        'half_count_fraction':qfmt(Q.from_float(3.125e-6))},
        'member_count':4,'native_products_checked':native_checks,'native_products_exact_mismatches':0,
        'members':members,
        'gate_status':{'scientific_dispatch':0,'new_coupled_root':None,'full_box_analytic_certificate':None,
                       'coverage':'24/289','epsilon_C':None,'epsilon_R':None,'B22':'OPEN_UNDETERMINED',
                       'paired_root_accepted':None,'parameter_family_root':None,'continuous_error':None},
        'c1':{'whole_physical_boxes_inclusion':False,'holomorphic_derivative_admission':False,
              'sign_rank_admission':False,'authorization_record':None,
              'finite_series_scope':c1['kernel_domain'],
              'still_required':c1['proof_prerequisites']},
        'caveats':['weights are exactly normalized in a NEW analysis-only rational representation; original native weights and algorithms are not changed',
                   'the exact binary64 product drift is reported separately; it is not genuine radiation source gain/loss',
                   'angular birth reweighting is pre-BE, not coupled endpoint/observer difference',
                   'first time moment is birth measure only and ignores absorption and transported photons',
                   'no HH science dispatch, no root certificate, no C1 analytic admission'],
    }
