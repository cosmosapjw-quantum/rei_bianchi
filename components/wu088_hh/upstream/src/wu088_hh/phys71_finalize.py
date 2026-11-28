"""Exact analytic correction of saved PHYS71 numerical evidence; stdlib only.

The original 76 numerical panels remain immutable. Their producer aggregate
used an inward rounded radial decimal. This creates a separately identified
analytic certificate after a full independent numerical-evidence audit.
No numerical engine, Coulomb function, or integral is called.
"""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

UNIT = Path('research/hh_phys71_20261020')
RADIAL_UPPER = F('1.48432231489e-79')
OLD_CERTIFICATE_SHA = '8d0d3a45196c89cecbecae70b59b0b93b72bae5ca600e24bcc3864ffab0c012f'
OLD_FINGERPRINT = 'a59e8275e0197970af71740cad86c2f7ff77b2a2cad6b15b37cb002af8d24325'


def rational(value):
    return F(int(value['numerator']), int(value['denominator']))


def record(value):
    value = F(value)
    return {'numerator':str(value.numerator), 'denominator':str(value.denominator)}


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()


def radial_enclosure():
    """Positive rational exponential series and its geometric tail bound."""
    a = F(32400)*F('3e-23')/2
    chi = 4*a*F(32400,4)
    prefactor = F(5,4)*a*chi*chi
    term, partial = F(1), F(1)
    for n in range(1,257):
        term *= F(76,n)
        partial += term
    exponential_upper = partial + (term*F(76,257))/(1-F(76,258))
    lower, upper = prefactor/exponential_upper, prefactor/partial
    if not F('1.484322e-79') < lower <= upper <= RADIAL_UPPER:
        raise ArithmeticError('analytic radial enclosure or corrected endpoint failed')
    return {'formula':'(5/4)*a*chi^2*exp(-76)', 'gamma':32400,
            'delta':'3e-23','a':record(a),'chi':record(chi),
            'positive_exp_series_last_order':256,
            'exponential_tail_ratio_upper':record(F(76,258)),
            'beta3_lower':record(lower),'beta3_upper':record(upper),
            'adopted_upward_endpoint':record(RADIAL_UPPER)}


def load_auditor(root):
    path = Path(root)/UNIT/'verification/verify_saved_d3.py'
    spec = importlib.util.spec_from_file_location('phys71_independent_saved_auditor', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finalize(root, campaign, low_archive, band_archive):
    root, campaign = Path(root).resolve(), Path(campaign).resolve()
    auditor = load_auditor(root)
    out = campaign/'ALL_ANGULAR_CERTIFICATE.json'
    if out.exists():
        checked = auditor.audit(root,campaign,low_archive,band_archive,corrected=out)
        return {'status':'EXISTING_CORRECTED_CERTIFICATE_VERIFIED',
                'read_only':True,'files_written':0,'new_physical_panels':0,
                'certificate_sha256':digest_bytes(out.read_bytes()),'audit':checked,'HH_R10':'OFF'}
    checked = auditor.audit(root,campaign,low_archive,band_archive,numerical_only=True)
    if checked['status'] != 'PASS_NUMERICAL_ONLY' or checked['analytic_certificate_adopted'] is not False:
        raise ValueError('independently verified numerical evidence is required')
    raw = (campaign/'CERTIFICATE.json').read_bytes()
    if digest_bytes(raw) != OLD_CERTIFICATE_SHA:
        raise ValueError('this correction is bound to one original producer certificate')
    original = json.loads(raw)
    if original['fingerprint'] != OLD_FINGERPRINT:
        raise ValueError('unexpected producer fingerprint')
    numerical = rational(checked['numerical_error_l1'])
    # Independent audit recomputes this infinite tail by Newton differences;
    # the correction uses its exact accepted value, not a decimal summary.
    angular = auditor.angular_bound_independent()[0]
    radial_proof = radial_enclosure()
    total = numerical+RADIAL_UPPER+angular
    paths = ['src/wu088_hh/phys71_finalize.py','scripts/phys71_finalize.py',
             str(UNIT/'verification/verify_saved_d3.py'),
             str(UNIT/'verification/phys71_campaign.py.ORIGINAL_PRODUCER.txt')]
    result = {'schema':'PHYS71_CORRECTED_ALL_ANGULAR_D3_V1',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'producer_fingerprint':OLD_FINGERPRINT,
        'numerical_certificate_file':'CERTIFICATE.json',
        'numerical_certificate_sha256':OLD_CERTIFICATE_SHA,
        'original_aggregate_status':'REJECTED_RADIAL_INWARD_ROUNDING',
        'source_sha256':original['source_sha256'],'coefficient':original['coefficient'],
        'request':original['request'],'D3_B_cutoff':checked['D3_B_cutoff'],
        'numerical_error_l1':record(numerical),
        'radial_cutoff_error_upper':record(RADIAL_UPPER),
        'radial_cutoff_bound_reused_from_max_L':64,
        'excluded_angular_error_upper':record(angular),
        'total_error_about_cutoff_midpoint':record(total),
        'absolute_goal_met':total <= F('1e-78'),
        'status':'CERTIFIED_GOAL_MET' if total <= F('1e-78') else 'CERTIFIED_GOAL_NOT_MET',
        'scientific_execution':'COMPLETE_REUSED_NUMERICAL_PANELS',
        'numerical_panels_reused':76,'inherited_profile_payloads_reused':152,
        'new_physical_panels':0,'new_Coulomb_evaluations':0,'new_D1_or_D2_integrations':0,
        'radial_proof':radial_proof,
        'correction':'Replace the inward summary decimal by the upward PR115 endpoint; preserve every numerical panel and original producer identity.',
        'postprocessor_files_sha256':{p:digest_bytes((root/p).read_bytes()) for p in paths},
        'inherited_proof_sha256':json.loads((campaign/'REQUEST.json').read_text())['binding']['inherited_proof_sha256'],
        'full_nonlinear_remainder_certified':False,'original_driven_xi_certified':False,
        'PHYS63_qualitative_existence':'ESTABLISHED_REUSED','HH_R10':'OFF'}
    result['certificate_payload_sha256'] = digest_bytes(canonical(result))
    raw = (json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
    fd,name = tempfile.mkstemp(prefix='.analytic-certificate-',suffix='.tmp',dir=campaign)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.link(name,out)
    finally:
        Path(name).unlink(missing_ok=True)
    return {'status':'CORRECTED_ANALYTIC_CERTIFICATE_CREATED_PENDING_INDEPENDENT_FULL_AUDIT',
            'read_only':False,'files_written':1,'new_physical_panels':0,
            'certificate_sha256':digest_bytes(raw),'numerical_audit':checked,'HH_R10':'OFF'}
