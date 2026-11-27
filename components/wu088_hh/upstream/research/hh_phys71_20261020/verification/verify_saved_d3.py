#!/usr/bin/env python3
"""Read-only, stdlib-only verification of the fixed completed PHYS71 result.

This consumes saved evidence, reconstructs exact rational error accounting,
and never imports FLINT, calls Coulomb functions, or integrates an old/new
physical panel. The verifier Python version need not equal the recorded
producer version. Numerical resume has a different, stricter runtime contract.

Normal output is one JSON object on stdout. No files or directories are written.
"""
import sys
sys.dont_write_bytecode = True

import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
from math import comb
from pathlib import Path
import platform
from zipfile import ZipFile


SOURCE_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
FINGERPRINT = 'a59e8275e0197970af71740cad86c2f7ff77b2a2cad6b15b37cb002af8d24325'
CERTIFICATE_SHA = '8d0d3a45196c89cecbecae70b59b0b93b72bae5ca600e24bcc3864ffab0c012f'
ORIGINAL_CAMPAIGN_SHA = 'f99cec09e922083f45a46a210e7873a2b05c573d6a9a3f152652d946de9062b2'
PRODUCER = {'python': '3.12.14', 'python_flint': '0.8.0', 'flint': '3.3.1'}
REQUEST = {'max_ell':36, 'ell':21, 'ellprime':20, 'm':0, 'boundary':'27',
           'outer':'65', 'half_width':'1/4', 'zero_free_radius':'1/2',
           'majorant_radius':'2', 'degree':80, 'precision_bits':384,
           'coefficient_bits':1024, 'absolute_goal':'1e-78', 'HH_R10':'OFF'}
BASE = Path('research/hh_phys71_20261020')
FAMILIES = {
    'PHYS68_LOW': ('research/hh_phys68_20261019/profiles/run_l28_t65_completed',
                   'run_l28_t65_completed',
                   'research/hh_phys68_20261019/profiles/PROFILE_PANEL_PAYLOADS_20261019.zip'),
    'PHYS69_BAND': ('research/hh_phys69_20261019/band/run_j29_36_t65',
                    'run_j29_36_t65', 'archives/PHYS69_BAND_PAYLOADS_20261019.zip')}
PAIRS = tuple((a,j) for a in (20,21) for j in range(37))


def require(value, reason):
    if not value:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),
                      ensure_ascii=False,allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ordinary_bytes(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'ordinary evidence file required: '+str(path))
    return path.read_bytes()


def decode(data):
    def unique(pairs):
        out = {}
        for k,v in pairs:
            require(k not in out, 'duplicate JSON key: '+k)
            out[k] = v
        return out
    def invalid(value):
        raise ValueError('nonfinite JSON number: '+value)
    value = json.loads(data,object_pairs_hook=unique,parse_constant=invalid)
    require(type(value) is dict,'JSON object required')
    return value


def read(path):
    return decode(ordinary_bytes(path))


def dyadic(record):
    require(type(record) is dict and type(record.get('mantissa')) is str and
            type(record.get('exponent2')) is int,'exact dyadic record required')
    exponent = record['exponent2']
    require(abs(exponent)<=100000,'dyadic exponent outside evidence bounds')
    return F(int(record['mantissa']))*F(2)**exponent


def interval(record):
    midpoint, radius = dyadic(record['midpoint']),dyadic(record['radius'])
    require(radius>=0,'negative rectangular radius')
    return midpoint-radius,midpoint+radius


def contains(outer,inner):
    for component in ('real','imag'):
        lo,hi = interval(outer[component]); x,y = interval(inner[component])
        if lo>x or hi<y:
            return False
    return True


def radius_l1(record):
    for component in ('real','imag'):
        interval(record[component])
    return sum((dyadic(record[c]['radius']) for c in ('real','imag')),F(0))


def rational(record):
    require(type(record) is dict and set(record)=={'numerator','denominator'} and
            all(type(x) is str for x in record.values()),'exact rational record required')
    return F(int(record['numerator']),int(record['denominator']))


def rational_record(value):
    return {'numerator':str(value.numerator),'denominator':str(value.denominator)}


def decimal_display(value):
    with localcontext() as context:
        context.prec = 40
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def angular_bound_independent():
    """Exact Newton-series reconstruction of the proven L36 geometric tails.

    For j>=37 the inner convolution is 10^-j times a polynomial of degree
    at most three: the low-k part is constant, the left high-k range sums
    (k+1)^2, the seven central terms are quadratic, and the right geometric
    tail is quadratic. Multiplication by C_j^2 gives degree at most five.
    Six exact values therefore determine its Newton polynomial; this is
    not a numerical fit or an angular truncation.
    """
    slope,delta,angular_c,q = F(800,189),F(3,10**23),F(1,9*10**18),F(1,100)
    def mode(j):
        return F(77) if j<=28 else slope*(j+1)
    def potential(d):
        return min(delta,angular_c*F(10)**(-d))
    def square_tail(start):
        return q**start*((start+1)**2/(1-q)+2*(start+1)*q/(1-q)**2+
                          q*(1+q)/(1-q)**3)
    def inner(j,b):
        stop = max(28,j+3,b+3)
        finite = sum((mode(k)**2*potential(abs(j-k))*potential(abs(b-k))
                      for k in range(stop+1)),F(0))
        return finite+slope**2*angular_c**2*F(10)**(j+b)*square_tail(stop+1)
    def side(a,b):
        start = 37
        def polynomial(j):
            return mode(j)**2*potential(abs(a-j))*inner(j,b)/q**j
        row = [polynomial(start+n) for n in range(6)]
        differences = []
        while row:
            differences.append(row[0])
            row = [y-x for x,y in zip(row,row[1:])]
        # Two exact structural consistency checks, without truncating the sum.
        for n in (6,7):
            require(polynomial(start+n)==sum((F(comb(n,k))*v
                    for k,v in enumerate(differences)),F(0)),
                    'angular degree-five identity mismatch')
        return q**start*sum((v*q**k/(1-q)**(k+1)
                             for k,v in enumerate(differences)),F(0))
    ab,ba = side(21,20),side(20,21)
    return F(77**2,96)*(ab+ba),ab,ba


def radial_enclosure_independent():
    """Bracket beta3 and verify the corrected PR115 upward endpoint."""
    gamma,delta = F(32400),F(3,10**23)
    a,chi = gamma*delta/2,gamma**2*delta/2
    # Positive Taylor partial sum is a rigorous lower bound for exp(76).
    term = partial = F(1)
    for n in range(1,257):
        term *= F(76,n)
        partial += term
    rigorous_upper = F(5,4)*a*chi**2/partial
    exponential_upper = partial+term*F(76,257)/(1-F(76,258))
    rigorous_lower = F(5,4)*a*chi**2/exponential_upper
    adopted = F('1.48432231489e-79')
    require(F('1.484322e-79')<rigorous_lower<=rigorous_upper<=adopted,
            'corrected radial endpoint or inward-rounding diagnosis failed')
    return adopted,rigorous_lower,rigorous_upper


def radial_bound_independent():
    adopted,_,upper = radial_enclosure_independent()
    return adopted,upper


def inherited_inputs(root,binding,archive_paths):
    receipts,verified = {},[]
    families = {item['family']:item for item in binding['inherited']}
    require(set(families)==set(FAMILIES),'inherited families changed')
    for family,(run,prefix,default_archive) in FAMILIES.items():
        bound = families[family]
        request_bytes = ordinary_bytes(root/run/'REQUEST.json')
        cert_bytes = ordinary_bytes(root/run/'CERTIFICATE.json')
        require(sha(request_bytes)==bound['request_sha256'] and
                sha(cert_bytes)==bound['certificate_sha256'],'inherited request/certificate hash mismatch')
        request,certificate = decode(request_bytes),decode(cert_bytes)
        require(digest(request['binding'])==request['fingerprint']==bound['fingerprint'],
                'inherited request fingerprint mismatch')
        require(certificate['fingerprint']==bound['fingerprint'] and
                certificate['source_sha256']==SOURCE_SHA and
                certificate['scientific_execution']=='COMPLETE' and
                certificate['HH_R10']=='OFF','inherited certificate scope mismatch')
        path = archive_paths.get(family) or root/default_archive
        data = ordinary_bytes(path)
        require(sha(data)==bound['archive_sha256'],'inherited archive hash mismatch')
        by_index = certificate['panels']
        require(len(by_index)==76,'inherited complete panel list required')
        rows = []
        with ZipFile(BytesIO(data)) as archive:
            names = archive.namelist()
            require(len(names)==len(set(names)),'duplicate inherited ZIP member')
            for index,item in enumerate(by_index):
                member = prefix+'/panel_'+format(index,'04d')+'.json'
                saved = decode(archive.read(member))
                require(item['index']==saved['index']==index and
                        saved['fingerprint']==bound['fingerprint'],
                        'inherited panel identity mismatch')
                payload_hash = digest(saved['payload'])
                require(payload_hash==saved['payload_sha256']==item['payload_sha256'],
                        'inherited payload hash mismatch')
                require(saved['payload']['source_sha256']==SOURCE_SHA and
                        saved['payload']['HH_R10']=='OFF','inherited physical scope mismatch')
                rows.append(payload_hash)
            if family=='PHYS69_BAND':
                require(archive.read(prefix+'/REQUEST.json')==request_bytes and
                        archive.read(prefix+'/CERTIFICATE.json')==cert_bytes,
                        'band archived request/certificate mismatch')
        receipts[family] = rows
        verified.append({'family':family,'archive_sha256':sha(data),
                         'inherited_payloads_hash_checked':76})
    return receipts,verified


def audit(root,campaign,low_archive,band_archive,display=None,corrected=None,
          numerical_only=False):
    """Audit immutable numerical evidence; separately accept a corrected bound.

    numerical_only=True never adopts the original inward-rounded aggregate
    claim. It supplies verified numerical evidence to the additive finalizer.
    """
    root,campaign = Path(root),Path(campaign)
    started = datetime.now(timezone.utc).isoformat()
    request = read(campaign/'REQUEST.json')
    binding = request['binding']
    require(request['schema']=='PHYS71_CAMPAIGN_REQUEST_V1' and
            request['HH_R10']=='OFF','campaign request schema/scope mismatch')
    require(digest(binding)==request['fingerprint']==FINGERPRINT,
            'reviewed stable-error fingerprint mismatch')
    require(binding['request']==REQUEST and
            all(type(binding['request'][k]) is type(v) for k,v in REQUEST.items()),
            'fixed physical/numerical request changed')
    require(binding['source_sha256']==SOURCE_SHA and binding['HH_R10']=='OFF' and
            binding['coefficient']=="D3=Z'''(0)/6" and
            binding['angular_contraction']=='bilinear_no_conjugation',
            'physical identity or contraction changed')
    engine = binding['engine']
    require({k:engine[k] for k in PRODUCER}==PRODUCER,'producer runtime identity changed')
    files = {str(Path('src/wu088_hh')/name):value for name,value in engine['files_sha256'].items()}
    files.update(engine['campaign_files_sha256'])
    files.update(binding['inherited_proof_sha256'])
    producer_locations = {}
    for path,expected in files.items():
        current = root/path
        location = current
        if sha(ordinary_bytes(current)) != expected:
            require(path=='src/wu088_hh/phys71_campaign.py' and expected==ORIGINAL_CAMPAIGN_SHA,
                    'bound source/proof hash mismatch: '+path)
            location = root/BASE/'verification/phys71_campaign.py.ORIGINAL_PRODUCER.txt'
            require(sha(ordinary_bytes(location))==ORIGINAL_CAMPAIGN_SHA,
                    'preserved original producer campaign snapshot mismatch')
        producer_locations[path] = str(location.relative_to(root))
    inherited,archive_receipts = inherited_inputs(root,binding,
                  {'PHYS68_LOW':low_archive,'PHYS69_BAND':band_archive})

    cert_bytes = ordinary_bytes(campaign/'CERTIFICATE.json')
    require(sha(cert_bytes)==CERTIFICATE_SHA,'completed execution certificate byte hash mismatch')
    cert = decode(cert_bytes)
    checksum_body = dict(cert)
    checksum = checksum_body.pop('certificate_payload_sha256')
    require(digest(checksum_body)==checksum,'certificate canonical payload hash mismatch')
    require(cert['schema']=='PHYS71_ALL_ANGULAR_D3_CERTIFICATE_V1' and
            cert['fingerprint']==FINGERPRINT and cert['request']==REQUEST,
            'certificate request mismatch')
    require(cert['source_sha256']==SOURCE_SHA and cert['coefficient']=="D3=Z'''(0)/6" and
            cert['scientific_execution']=='COMPLETE' and cert['HH_R10']=='OFF',
            'certificate physical scope mismatch')
    for field,expected in [('panel_count_required',76),('precision_bits',384),
                           ('new_D1_or_D2_integrations',0),('inherited_profile_payloads_reused',152),
                           ('radial_cutoff_bound_reused_from_max_L',64)]:
        require(type(cert[field]) is int and cert[field]==expected,'certificate count/scope mismatch: '+field)
    require(cert['PHYS63_qualitative_existence']=='ESTABLISHED_REUSED' and
            cert['full_nonlinear_remainder_certified'] is False and
            cert['original_driven_xi_certified'] is False,'unsupported scope promotion')
    names = sorted(p.name for p in campaign.glob('panel_*.json'))
    require(names==['panel_'+format(i,'04d')+'.json' for i in range(76)],
            '76 contiguous stable-error panels required')

    zero = {'display':'0','midpoint':{'mantissa':'0','exponent2':0},
            'radius':{'mantissa':'0','exponent2':0}}
    state = {str(a)+','+str(j):{'real':zero,'imag':zero} for a,j in PAIRS}
    sums = {component:[F(0),F(0)] for component in ('real','imag')}
    summed_radii = F(0)
    panel_receipts = []
    h,rho,n = F(1,4),F(1,2),80
    for index,name in enumerate(names):
        raw = ordinary_bytes(campaign/name); saved = decode(raw); payload = saved['payload']
        require(type(saved['index']) is int and saved['index']==index and
                saved['fingerprint']==FINGERPRINT,'saved panel identity mismatch')
        require(saved['payload_sha256']==digest(payload),'saved panel payload hash mismatch')
        require(saved['left_state_sha256']==digest(state),'serialized forward predecessor hash mismatch')
        require(saved['inherited_payload_sha256']==
                {family:rows[75-index] for family,rows in inherited.items()},
                'saved inherited input references mismatch')
        require(payload['schema']=='PHYS71_D3_PANEL_V1' and
                payload['HH_R10']=='OFF' and payload['new_D1_or_D2_integrations']==0,
                'new panel scientific scope mismatch')
        require(type(payload['forward_index']) is int and payload['forward_index']==index and
                type(payload['inherited_index']) is int and payload['inherited_index']==75-index,
                'forward/inherited index mismatch')
        for key,value in [('left',F(27)+index/ F(2)),
                          ('center',F(27)+F(2*index+1,4)),
                          ('right',F(27)+F(index+1,2))]:
            require(type(payload[key]) is str and F(payload[key])==value,'panel geometry mismatch')
        require(payload['all_modes']==list(range(37)) and
                all(type(x) is int for x in payload['all_modes']),'angular coverage mismatch')
        for field,expected in [('regenerated_Coulomb_disks',37),
                               ('regenerated_q_derivative_series',73),('angular_moment_series',73)]:
            require(type(payload[field]) is int and payload[field]==expected,'panel work identity mismatch')
        numerical = radius_l1(payload['D3_increment'])
        require(numerical==rational(payload['D3_increment_error_l1']),'panel numerical radius mismatch')
        summed_radii += numerical
        for component in sums:
            lo,hi = interval(payload['D3_increment'][component])
            sums[component][0] += lo; sums[component][1] += hi
        carries = payload['source_response_carries']
        require(len(carries)==74 and
                tuple((row['external'],row['j']) for row in carries)==PAIRS,
                '74 ordered directed carries required')
        next_state = {}
        for row in carries:
            require(type(row['external']) is int and type(row['j']) is int,'exact directed mode indices required')
            key = str(row['external'])+','+str(row['j'])
            require(contains(row['P_left'],state[key]),'P_left omits serialized predecessor')
            radius_l1(row['P_center']); radius_l1(row['P_right'])
            for field in ('S_majorant','S_panel_remainder','U_disk_majorant'):
                require(interval(row[field])[0]>=0,'negative primitive majorant/remainder')
            require(interval(row['S_panel_remainder'])[0]>=
                    interval(row['S_majorant'])[1]*(h/rho)**(n+1)/(1-h/rho),
                    'primitive Cauchy remainder mismatch')
            next_state[key] = row['P_right']
        state = next_state
        majorant = interval(payload['integrand_disk_majorant'])[1]
        tail = interval(payload['integrand_panel_remainder'])[1]
        require(majorant>=0 and tail>=majorant*(h/rho)**(n+1)/(1-h/rho),
                'whole-integrand Cauchy bound mismatch')
        budget = payload['angular_error_budget']
        require(budget['schema']=='PHYS71_CENTERED_ANGULAR_ERROR_V1' and
                budget['basis_for_error_bound']=='original_orthonormal_modes_with_L1_upper_bound' and
                budget['midpoint_transform_roundoff']=='retained_in_complex_ball_polynomial',
                'centered angular error accounting changed')
        values = {}
        for field in ('midpoint_weighted_l1_a','midpoint_weighted_l1_b',
                      'coefficient_error_weighted_l1_a','coefficient_error_weighted_l1_b',
                      'multiplier_weighted_coefficient_bound','projected_integrand_coefficient_error'):
            lo,hi = interval(budget[field]); require(lo>=0,'negative coefficient budget')
            values[field] = hi
        a,b = values['midpoint_weighted_l1_a'],values['midpoint_weighted_l1_b']
        ea,eb = values['coefficient_error_weighted_l1_a'],values['coefficient_error_weighted_l1_b']
        coefficient_error = values['projected_integrand_coefficient_error']
        require(coefficient_error>=values['multiplier_weighted_coefficient_bound']*(ea*b+a*eb+ea*eb),
                'projected coefficient error misses a cross term')
        require(numerical>=4*h*(tail+coefficient_error),
                'serialized numerical box omits a Cauchy/coefficient error term')
        panel_receipts.append({'index':index,'file':name,
                 'payload_sha256':saved['payload_sha256'],'file_sha256':sha(raw)})
    require(cert['panels']==panel_receipts,'certificate panel receipts mismatch')
    cutoff = cert['D3_B_cutoff']
    for component in sums:
        lo,hi = interval(cutoff[component])
        require(lo<=sums[component][0] and hi>=sums[component][1],
                'certificate cutoff box omits exact saved increment sum')
    numerical = radius_l1(cutoff)
    require(rational(cert['numerical_error_l1'])==numerical,'original numerical radius mismatch')
    numerical_result = {
        'schema':'PHYS71_PORTABLE_INDEPENDENT_VERIFICATION_V1',
        'status':'PASS_NUMERICAL_ONLY','started_utc':started,
        'finished_utc':datetime.now(timezone.utc).isoformat(),
        'analytic_certificate_adopted':False,
        'original_aggregate_status':'REJECTED_RADIAL_INWARD_ROUNDING',
        'verifier_python':platform.python_version(),'producer_runtime':PRODUCER,
        'runtime_match_required_for_this_readonly_verifier':False,
        'producer_runtime_required_for_numerical_resume':True,
        'producer_fingerprint':FINGERPRINT,
        'numerical_certificate_sha256':sha(cert_bytes),
        'verified_source_and_proof_file_count':len(files),
        'verified_producer_source_locations':producer_locations,
        'verified_inherited_archives':archive_receipts,
        'verified_saved_new_D3_panels':76,'verified_forward_carries':76*74,
        'exact_panel_radius_sum':rational_record(summed_radii),
        'numerical_error_l1':rational_record(numerical),'D3_B_cutoff':cutoff,
        'new_numerical_callbacks':0,'Coulomb_evaluations':0,
        'new_or_old_physical_integrations':0,'read_only':True,'files_written':0,
        'HH_R10':'OFF'}
    if numerical_only:
        return numerical_result
    angular,ab,ba = angular_bound_independent()
    radial,radial_rational_lower,radial_rational_upper = radial_enclosure_independent()
    # The original bytes are retained as numerical evidence. Their inward
    # radial summary is recognized explicitly and is never adopted here.
    require(rational(binding['radial_beta3_upward_bound'])==F('1.484322e-79') and
            rational(cert['radial_cutoff_error_upper'])==F('1.484322e-79'),
            'unexpected historical aggregate; this correction is narrowly bound')
    angles = read(root/BASE/'angles/RESULTS.json')
    angular_row = next(row for row in angles['angular_rows'] if row['L']==36)
    require(angular==rational(angular_row['absolute_angular_tail_bound']) and
            ab==rational(angular_row['one_sided_ab']) and
            ba==rational(angular_row['one_sided_ba']),
            'independent angular geometric sum mismatch')
    require(rational(cert['excluded_angular_error_upper'])==angular,
            'original angular error record differs from independent exact sum')
    corrected_path = Path(corrected) if corrected is not None else campaign/'ALL_ANGULAR_CERTIFICATE.json'
    corrected_bytes = ordinary_bytes(corrected_path)
    accepted = decode(corrected_bytes)
    body = dict(accepted); payload_checksum = body.pop('certificate_payload_sha256')
    require(payload_checksum==digest(body),'corrected certificate payload hash mismatch')
    require(accepted['schema']=='PHYS71_CORRECTED_ALL_ANGULAR_D3_V1' and
            accepted['producer_fingerprint']==FINGERPRINT and
            accepted['numerical_certificate_sha256']==CERTIFICATE_SHA and
            accepted['numerical_certificate_file']=='CERTIFICATE.json' and
            accepted['original_aggregate_status']=='REJECTED_RADIAL_INWARD_ROUNDING',
            'corrected certificate numerical provenance mismatch')
    require(accepted['request']==REQUEST and accepted['source_sha256']==SOURCE_SHA and
            accepted['coefficient']=="D3=Z'''(0)/6" and accepted['D3_B_cutoff']==cutoff,
            'corrected certificate changed numerical data or physical identity')
    require(accepted['scientific_execution']=='COMPLETE_REUSED_NUMERICAL_PANELS' and
            accepted['HH_R10']=='OFF' and
            accepted['PHYS63_qualitative_existence']=='ESTABLISHED_REUSED' and
            accepted['full_nonlinear_remainder_certified'] is False and
            accepted['original_driven_xi_certified'] is False,
            'corrected certificate promoted an unsupported scientific scope')
    for field,expected in [('radial_cutoff_bound_reused_from_max_L',64),
                           ('numerical_panels_reused',76),('inherited_profile_payloads_reused',152),
                           ('new_physical_panels',0),('new_Coulomb_evaluations',0),
                           ('new_D1_or_D2_integrations',0)]:
        require(type(accepted[field]) is int and accepted[field]==expected,
                'corrected certificate execution count mismatch: '+field)
    postprocessor_paths = {'src/wu088_hh/phys71_finalize.py','scripts/phys71_finalize.py',
                          str(BASE/'verification/verify_saved_d3.py'),
                          str(BASE/'verification/phys71_campaign.py.ORIGINAL_PRODUCER.txt')}
    require(set(accepted['postprocessor_files_sha256'])==postprocessor_paths,
            'corrected postprocessor source membership mismatch')
    for path,expected in accepted['postprocessor_files_sha256'].items():
        require(sha(ordinary_bytes(root/path))==expected,'corrected postprocessor hash mismatch: '+path)
    require(accepted['postprocessor_files_sha256'][str(BASE/'verification/verify_saved_d3.py')]==
            sha(ordinary_bytes(Path(__file__))), 'executing verifier differs from recorded postprocessor')
    require(accepted['postprocessor_files_sha256'][
            str(BASE/'verification/phys71_campaign.py.ORIGINAL_PRODUCER.txt')]==ORIGINAL_CAMPAIGN_SHA,
            'original producer campaign identity was replaced')
    require(accepted['inherited_proof_sha256']==binding['inherited_proof_sha256'],
            'corrected proof provenance mismatch')
    proof = accepted['radial_proof']
    require(proof['formula']=='(5/4)*a*chi^2*exp(-76)' and
            type(proof['gamma']) is int and proof['gamma']==32400 and
            proof['delta']=='3e-23' and
            rational(proof['a'])==F(32400)*F('3e-23')/2 and
            rational(proof['chi'])==F(32400)**2*F('3e-23')/2,
            'radial proof physical constants mismatch')
    require(type(proof['positive_exp_series_last_order']) is int and
            proof['positive_exp_series_last_order']==256 and
            rational(proof['exponential_tail_ratio_upper'])==F(76,258) and
            rational(proof['beta3_lower'])==radial_rational_lower and
            rational(proof['beta3_upper'])==radial_rational_upper and
            rational(proof['adopted_upward_endpoint'])==radial,
            'independent positive exponential-series bracket mismatch')
    total = numerical+radial+angular
    for field,value in [('numerical_error_l1',numerical),('radial_cutoff_error_upper',radial),
                        ('excluded_angular_error_upper',angular),
                        ('total_error_about_cutoff_midpoint',total)]:
        require(rational(accepted[field])==value,'corrected total error mismatch: '+field)
    goal_met = total<=F(REQUEST['absolute_goal'])
    require(accepted['absolute_goal_met'] is goal_met and
            accepted['status']==('CERTIFIED_GOAL_MET' if goal_met else 'CERTIFIED_GOAL_NOT_MET'),
            'corrected certificate goal decision mismatch')
    require(goal_met,'completed coefficient does not meet the fixed absolute goal')

    display_result = None
    if display is not None:
        shown = read(display)
        require(shown['schema']=='PHYS71_DISPLAY_RESULT_V1' and shown['HH_R10']=='OFF' and
                shown['certificate_sha256']==sha(corrected_bytes),'display corrected source identity mismatch')
        require(shown['units']=='a0^-1' and shown['full_nonlinear_remainder_certified'] is False and
                shown['original_driven_xi_certified'] is False,'display units or certificate scope changed')
        require(type(shown['real']) is str and type(shown['imag']) is str and
                type(shown['absolute_error_upper']) is str,'decimal display strings required')
        printing = sum((abs(dyadic(cutoff[c]['midpoint'])-F(shown[c]))
                        for c in ('real','imag')),F(0))
        require(rational(shown['printing_error_l1'])==printing,'displayed printing error mismatch')
        for field,value in [('numerical_error_l1',numerical),('radial_cutoff_error_upper',radial),
                            ('excluded_angular_error_upper',angular),
                            ('total_error_about_cutoff_midpoint',total)]:
            require(type(shown['budget_upper_decimals'][field]) is str and
                    F(shown['budget_upper_decimals'][field])>=value,
                    'displayed budget decimal is not an upward bound: '+field)
        reported = F(shown['absolute_error_upper'])
        require(total+printing<=reported<=F(REQUEST['absolute_goal']),
                'displayed bound omits printing error or exceeds fixed goal')
        display_result = {'sha256':sha(ordinary_bytes(display)),
                          'real':shown['real'],'imag':shown['imag'],
                          'printing_error_l1':rational_record(printing),
                          'total_plus_printing':rational_record(total+printing),
                          'reported_absolute_error_upper':shown['absolute_error_upper']}
    return {'schema':'PHYS71_PORTABLE_INDEPENDENT_VERIFICATION_V1',
            'status':'PASS_CORRECTED_ALL_ANGULAR_D3_CERTIFICATE',
            'analytic_certificate_adopted':True,
            'original_aggregate_status':'REJECTED_RADIAL_INWARD_ROUNDING',
            'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
            'verifier_python':platform.python_version(),'producer_runtime':PRODUCER,
            'runtime_match_required_for_this_readonly_verifier':False,
            'producer_runtime_required_for_numerical_resume':True,
            'producer_fingerprint':FINGERPRINT,'numerical_certificate_sha256':sha(cert_bytes),
            'certificate_sha256':sha(corrected_bytes),
            'corrected_certificate_sha256':sha(corrected_bytes),
            'verified_source_and_proof_file_count':len(files),
            'verified_producer_source_locations':producer_locations,
            'verified_inherited_archives':archive_receipts,
            'verified_saved_new_D3_panels':76,'verified_forward_carries':76*74,
            'exact_panel_radius_sum':rational_record(summed_radii),
            'certificate_numerical_radius':rational_record(numerical),
            'independent_angular_tail':rational_record(angular),
            'independent_radial_upward_bound':rational_record(radial),
            'radial_bound_checked_by_positive_exp_series':rational_record(radial_rational_upper),
            'total_error':rational_record(total),'total_error_decimal_display':decimal_display(total),
            'fixed_goal':REQUEST['absolute_goal'],'absolute_goal_met':goal_met,
            'display_result':display_result,'new_numerical_callbacks':0,
            'Coulomb_evaluations':0,'new_or_old_physical_integrations':0,
            'read_only':True,'files_written':0,'HH_R10':'OFF'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--campaign',type=Path)
    parser.add_argument('--display',type=Path)
    parser.add_argument('--low-archive',type=Path)
    parser.add_argument('--band-archive',type=Path)
    parser.add_argument('--corrected',type=Path)
    parser.add_argument('--numerical-only',action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    campaign = args.campaign or root/BASE/'d3/run_l36_t65_stable_errors'
    try:
        result = audit(root,campaign,args.low_archive,args.band_archive,
                       display=args.display,corrected=args.corrected,
                       numerical_only=args.numerical_only)
        result['verifier_source_sha256'] = sha(ordinary_bytes(Path(__file__)))
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({'schema':'PHYS71_PORTABLE_INDEPENDENT_VERIFICATION_V1',
             'status':'FAIL_READONLY_VERIFICATION','error_type':type(exc).__name__,
             'reason':str(exc),'new_numerical_callbacks':0,'files_written':0,
             'read_only':True,'HH_R10':'OFF'},indent=2,sort_keys=True))
        return 1


if __name__=='__main__':
    raise SystemExit(main())
