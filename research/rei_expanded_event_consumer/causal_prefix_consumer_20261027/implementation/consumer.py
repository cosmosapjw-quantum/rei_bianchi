"""Exact conditional information-polytope consumer; no producer execution."""
from fractions import Fraction as Q
from math import isfinite, nextafter, inf

EV = Q(801088317, 5000000000000000000000000000)
I = Q(2721, 50)
MILLION = Q(1000000)
ZERO = Q(0)

def basis_si(f, basis):
    """Convert the original common basis once, before normalization/JVP."""
    if basis not in ('count_cm3','kinetic_eV_cm3'):
        raise ValueError('unknown common basis')
    return rational(f)*MILLION*(Q(1) if basis=='count_cm3' else EV)

def rational(x):
    if isinstance(x, bool):
        raise ValueError('bool is not a scalar')
    if isinstance(x, float):
        if not isfinite(x):
            raise ValueError('nonfinite')
        return Q.from_float(x)
    return Q(x)

def positive(x):
    x = rational(x)
    if x <= 0:
        raise ValueError('positive divisor required')
    return x

def interval(pair):
    a, b = map(rational, pair)
    if a > b:
        raise ValueError('inverted interval')
    return a, b

def closure(times, intervals, cap):
    times = tuple(map(rational, times))
    raw = tuple(map(interval, intervals))
    cap = rational(cap)
    if len(raw) != len(times) or not times or times[0] != 0:
        raise ValueError('zero origin required')
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError('unordered time')
    if raw[0] != (0, 0) or cap < 0:
        raise ValueError('zero horizon or cap')
    l, running = [], ZERO
    for a, b in raw:
        running = max(running, a)
        l.append(running)
    u = [ZERO] * len(raw)
    running = cap
    for i in range(len(raw)-1, -1, -1):
        running = min(running, raw[i][1])
        u[i] = running
    if any(a > b for a, b in zip(l, u)):
        raise ValueError('empty temporal polytope')
    return {'times': times, 'raw': raw, 'cap': cap, 'l': tuple(l), 'u': tuple(u)}

def window(p, a, b):
    if not 0 <= a < b < len(p['l']):
        raise ValueError('invalid window')
    l, u = p['l'], p['u']
    low, high = max(ZERO, l[b]-u[a]), u[b]-l[a]
    c = min(u[a], l[b])
    lower_witness = tuple(min(u[i], c) if i < a else max(l[i], c) for i in range(len(l)))
    upper_witness = tuple(l[i] if i < b else max(l[i], u[b]) for i in range(len(l)))
    return low, high, lower_witness, upper_witness

def feasible(p, f):
    return (len(f) == len(p['raw']) and f[0] == 0 and
            all(max(ZERO, a) <= x <= min(b, p['cap']) for (a,b),x in zip(p['raw'],f)) and
            all(x <= y for x,y in zip(f,f[1:])))

def endpoint_range(p, a, b, ba, bb):
    ba, bb = positive(ba), positive(bb)
    la, ua, lb, ub = p['l'][a], p['u'][a], p['l'][b], p['u'][b]
    vertices = [(x,y) for x in (la,ua) for y in (lb,ub) if x <= y]
    dl, du = max(la,lb), min(ua,ub)
    if dl <= du:
        vertices += [(dl,dl),(du,du)]
    values = [y/bb-x/ba for x,y in vertices]
    return min(values), max(values), tuple(vertices)

def outward(x):
    x = rational(x)
    f = float(x)
    if not isfinite(f):
        raise ValueError('float range exceeded')
    represented = Q.from_float(f)
    return (nextafter(f,-inf) if represented > x else f,
            nextafter(f,inf) if represented < x else f)

def quotient(f, b, s=Q(7,10), ds=Q(11,100), db=ZERO, duration=None, dduration=ZERO):
    b, s, ds, db = positive(b), rational(s), rational(ds), rational(db)
    f = rational(f)
    if s < 0:
        raise ValueError('negative scale')
    d = Q(1) if duration is None else positive(duration)
    dd = ZERO if duration is None else rational(dduration)
    value = s*f/(b*d)
    tangent = ds*f/(b*d)-s*f*db/(b*b*d)-s*f*dd/(b*d*d)
    return value, tangent

def clock_averages(f, b, dt, deta=None, ddt=ZERO, ddeta=ZERO, **direction):
    proper = quotient(f,b,duration=positive(dt),dduration=ddt,**direction)
    eta = None if deta is None else quotient(f,b,duration=positive(deta),dduration=ddeta,**direction)
    return {'proper':proper, 'eta':eta}

def endpoint(fa, fb, ba, bb, s=Q(7,10), ds=Q(11,100), dba=ZERO, dbb=ZERO):
    fa, fb, ba, bb = rational(fa), rational(fb), positive(ba), positive(bb)
    s, ds, dba, dbb = map(rational,(s,ds,dba,dbb))
    if s < 0:
        raise ValueError('negative scale')
    change = s*(fb/bb-fa/ba)
    event = s*(fb-fa)/bb
    correction = s*fa*(1/bb-1/ba)
    derivative = ds*(fb/bb-fa/ba)+s*(-fb*dbb/bb**2+fa*dba/ba**2)
    event_derivative = ds*(fb-fa)/bb-s*(fb-fa)*dbb/bb**2
    correction_derivative = ds*fa*(1/bb-1/ba)+s*fa*(-dbb/bb**2+dba/ba**2)
    return {'change':change,'event':event,'correction':correction,'jvp':derivative,
            'event_jvp':event_derivative,'correction_jvp':correction_derivative}

def joint_map(n, e, b=None):
    n,e = rational(n)*MILLION,rational(e)*MILLION*EV
    energy = {'internal':-I*EV*n,'thermal_kinetic':ZERO,'fast_kinetic':-e,
              'retained_photon':e+I*EV*n,'recoil':ZERO,'escaped':ZERO,'external':ZERO}
    density = {'He4:2':-n,'He4:1':n,'e:fast':-n,'photon':n}
    native = photon = None
    if b is not None:
        b=positive(b)
        native=[ZERO]*25
        native[11],native[12],native[21],native[22]=n/b,-n/b,-n/b,-e/b
        photon={'count':n/b,'energy':energy['retained_photon']/b}
    return {'density_m3':density,'energy_J_m3':energy,'native25':native,
            'retained_photon_per_baryon':photon,'physical_state_update':False}

def expected_maps():
    evmap = {k:(ZERO,ZERO) for k in ('internal','thermal_kinetic','fast_kinetic','retained_photon','recoil','escaped','external')}
    evmap.update(internal=(-I,ZERO),fast_kinetic=(ZERO,Q(-1)),retained_photon=(I,Q(1)))
    return {'energy_eV_cm3':evmap,
            'energy_J_m3':{k:(a*MILLION*EV,b*MILLION*EV) for k,(a,b) in evmap.items()},
            'density_m3':{'He4:2':(-MILLION,ZERO),'He4:1':(MILLION,ZERO),'e:fast':(-MILLION,ZERO),'photon':(MILLION,ZERO)}}

def read_ratio(d):
    return Q(int(d['numerator']),int(d['denominator']))

def validate_book(summary, book):
    if book['case'] != summary['case_id'] or not book['cumulative_views_not_added_to_book'] or book['actual_nb_m3'] is not None:
        raise ValueError('case/book qualification')
    rows = {x['source_id']:x for x in summary['source_rows']}
    if len(rows)!=3 or set(rows)!={'2.316','2.479','2.649'}:
        raise ValueError('source alternatives')
    seen=set(); grouped={k:[] for k in rows}; maps=expected_maps()
    conversion={'count_cm3_to_m3':MILLION,'eV_to_J_exact':EV,'energy_eV_cm3_to_J_m3':MILLION*EV,'threshold_eV_exact':I}
    for e in book['exports']:
        sid=e['source_id']; r=rows.get(sid)
        if r is None or e['case_id']!=summary['case_id'] or e['source_identity']!=r['source_identity']:
            raise ValueError('source/case/operator/bath/projection mismatch')
        if e['canonical_event_id'] in seen or e['observation_kind']!='finite_bin':
            raise ValueError('duplicate or cumulative extra event')
        seen.add(e['canonical_event_id']); grouped[sid].append(e)
        if e['frame']!='bath_frame_rest_target' or e['time_basis']!='comoving_proper_seconds':
            raise ValueError('frame/time basis')
        if e['native_nb_m3'] is not None or e['native25'] is not None or e['finite_coupled_abundance_update']:
            raise ValueError('recipient/state qualification')
        for k,v in conversion.items():
            if read_ratio(e['conversion'][k])!=v: raise ValueError('conversion')
        lm=e['linear_map']
        if lm['coefficient_representation']!='EXACT_RATIONAL': raise ValueError('map representation')
        for domain, entries in maps.items():
            if set(lm[domain])!=set(entries): raise ValueError('reservoir inventory')
            for key, expected in entries.items():
                if tuple(read_ratio(lm[domain][key][v]) for v in ('N_cm3','E_eV_cm3'))!=expected:
                    raise ValueError('source signed map')
        for k in ('N_cm3','E_eV_cm3'):
            v=e['common_basis'][k]
            if tuple(map(rational,v['interval']))!=tuple(rational(float.fromhex(h)) for h in v['endpoint_hex']):
                raise ValueError('endpoint binary64 identity')
        for rec in e['clock_metadata']['records']:
            for clock in rec['clocks'].values():
                exact=rational(float.fromhex(clock['gamma_hex']))*rational(rec['horizon_s'])/rec['m']
                if exact!=Q(clock['a_numerator'],clock['a_denominator']):
                    raise ValueError('exact gamma ratio / rounded integer metadata')
    for sid, events in grouped.items():
        if len(events)!=6: raise ValueError('six disjoint bins required')
        for i,(e,rb) in enumerate(zip(events,rows[sid]['bins'])):
            if (e['time_start_s'],e['time_end_s'],e['canonical_event_id'])!=(rb['time_start_s'],rb['time_end_s'],rb['canonical_event_id']):
                raise ValueError('overlap/order/canonical identity')
            if e['time_end_s']<=e['time_start_s'] or (i and events[i-1]['time_end_s']!=e['time_start_s']):
                raise ValueError('invalid bin width or overlap')
            if tuple(e['common_basis']['N_cm3']['interval'])!=tuple(rb['count_cm3']) or tuple(e['common_basis']['E_eV_cm3']['interval'])!=tuple(rb['kinetic_eV_cm3']):
                raise ValueError('canonical bin basis mismatch')
    return grouped
