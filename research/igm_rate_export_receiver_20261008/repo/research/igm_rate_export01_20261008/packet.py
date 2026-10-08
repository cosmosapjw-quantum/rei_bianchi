"""Validated singleton observation; deliberately no certified-family conversion."""
import hashlib,json,math

GAMMA_UNIT='absorber^-1 s^-1'
ENERGY_UNIT='eV absorber^-1 s^-1'
KIND='singleton_observation_not_parameter_family'

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def check(packet,expected_context_id):
    if packet['units']!={'Gamma':GAMMA_UNIT,'incident_Ecal':ENERGY_UNIT}:
        raise ValueError('PER_ABSORBER_GAMMA_AND_EV_RATE_UNITS_REQUIRED')
    if packet['family_kind']!=KIND or any(packet.get(k) is not None for k in ('generators','generator_ids','uncertainty_widths')):
        raise ValueError('OBSERVATION_NOT_CERTIFIED_PARAMETER_FAMILY')
    if any(packet.get(k)!=v for k,v in {'provider_error':'UNKNOWN','continuum_error':'UNKNOWN','family_admission':'HOLD_MISSING_EXTERNAL_FAMILY_PREMISE','physical':'HOLD','full_Wide':'HOLD'}.items()) or packet.get('history_integrated') is not False:
        raise ValueError('SINGLETON_UNKNOWN_HOLD_INVARIANTS_REQUIRED')
    if packet['context_id']!=expected_context_id or digest(packet['context'])!=expected_context_id:
        raise ValueError('SOURCE_CLOCK_STATE_PROVIDER_CONTEXT_MISMATCH')
    for key in ('Gamma','incident_Ecal'):
        a=packet[key]
        if len(a)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in a):
            raise ValueError('INSTANTANEOUS_MOMENT_DOMAIN')
    for g,e,chi in zip(packet['Gamma'],packet['incident_Ecal'],packet['context']['chi_ev']):
        if g==0 and e!=0:raise ValueError('ZERO_GAMMA_REQUIRES_ZERO_INCIDENT_ENERGY')
        if e<chi*g:raise ValueError('SUBTHRESHOLD_INCIDENT_ENERGY')
    if digest({'context_id':packet['context_id'],'Gamma':packet['Gamma'],'incident_Ecal':packet['incident_Ecal']})!=packet['observation_id']:
        raise ValueError('OBSERVATION_VALUE_IDENTITY_MISMATCH')
    return packet

def require_certified_family(packet):
    raise ValueError('INSTANTANEOUS_MOMENT_FAMILY_REQUIRED_NOT_SINGLETON_OBSERVATION')
